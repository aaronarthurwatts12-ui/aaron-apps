"""Organisation -> sector + size band.

Looks up data/org_cache.json first (hand-editable). Unknown organisations are
classified by Claude (if ANTHROPIC_API_KEY is set) and written back to the cache,
so each organisation is only ever classified once.
"""
import json
import os
from pathlib import Path

CACHE_PATH = Path(__file__).parent.parent / "data" / "org_cache.json"
SECTORS = ["NFP", "Education", "Gov", "Other", "Exclude"]
BANDS = ["micro", "small", "medium", "large"]
MODEL = os.environ.get("CLASSIFIER_MODEL", "claude-sonnet-5-5")

PROMPT = """You classify UK employers for a B2B software sales team selling HR and payroll software to the public and not-for-profit sectors.

For each organisation name below (with an example job title and the job board it came from), return:
- sector: one of
  "NFP" (registered charities, hospices, housing associations, social enterprises/CICs, faith organisations, trade unions, membership bodies),
  "Education" (universities, FE/sixth-form colleges, schools, multi-academy trusts, independent schools),
  "Gov" (central government departments and agencies, non-departmental public bodies, local authorities/councils, police, fire, devolved government bodies),
  "Other" (NHS trusts, ICBs and other NHS/health bodies, plus any other public sector body not above),
  "Exclude" (private companies, recruitment agencies, GP partnerships run as private businesses, non-UK employers, or anything not public/NFP).
- band: approximate total UK headcount: "micro" (<100), "small" (100-400), "medium" (400-1500), "large" (1500+). Use your best knowledge; individual primary schools are usually micro, secondary schools small, most NHS trusts, councils and universities large.
- type: a short description, e.g. "NHS trust", "District council", "Hospice charity".
- canonical (optional): if the posting is clearly on behalf of a parent body (e.g. a school posting a trust-wide CFO role), the parent's name.

Respond with ONLY a JSON object mapping each organisation name exactly as given to {{"sector":..., "band":..., "type":..., "canonical":...}}.

Organisations:
{items}
"""


def load_cache():
    return json.loads(CACHE_PATH.read_text()) if CACHE_PATH.exists() else {}


def save_cache(cache):
    CACHE_PATH.write_text(json.dumps(cache, indent=1, ensure_ascii=False, sort_keys=False) + "\n")


def classify_unknown(orgs, cache):
    """orgs: dict name -> (example title, source). Mutates and returns cache."""
    todo = {o: v for o, v in orgs.items() if o and o not in cache}
    if not todo:
        return cache
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(f"  {len(todo)} organisations unclassified (no ANTHROPIC_API_KEY) - shown under 'Unclassified'")
        return cache
    import anthropic
    client = anthropic.Anthropic()
    names = list(todo)
    for i in range(0, len(names), 40):
        chunk = names[i:i + 40]
        items = "\n".join(f"- {n} | e.g. '{todo[n][0]}' | {todo[n][1]}" for n in chunk)
        msg = client.messages.create(model=MODEL, max_tokens=8000,
                                     messages=[{"role": "user", "content": PROMPT.format(items=items)}])
        text = "".join(b.text for b in msg.content if b.type == "text").strip()
        text = text[text.find("{"): text.rfind("}") + 1]
        try:
            result = json.loads(text)
        except json.JSONDecodeError:
            print("  classifier returned unparseable output; skipping chunk")
            continue
        for name, v in result.items():
            if name in todo and v.get("sector") in SECTORS and v.get("band") in BANDS:
                cache[name] = {k: v[k] for k in ("sector", "band", "type", "canonical") if v.get(k)}
                cache[name]["auto"] = True
    save_cache(cache)
    return cache
