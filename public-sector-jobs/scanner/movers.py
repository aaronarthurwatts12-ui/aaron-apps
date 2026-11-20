"""Turn appointment news items into people: name, new role, organisation, previous role.

Uses Claude when ANTHROPIC_API_KEY is set (much more accurate); otherwise a
pattern-based fallback that handles the common "X appointed as Y" headlines.
Each person gets a LinkedIn link: a LinkedIn people search for their name and
organisation (we don't scrape LinkedIn, so this opens the search in your own
logged-in browser - the right profile is normally the top result).
"""
import json
import os
import re
from urllib.parse import quote

MODEL = os.environ.get("CLASSIFIER_MODEL", "claude-sonnet-5-5")
NAME = r"((?:Dr|Professor|Prof|Sir|Dame|Cllr)\.?\s+)?[A-Z][a-z'’-]+(?:\s+[A-Z][a-z'’-]+){1,2}"

PROMPT = """Below are UK news items about senior appointments. For each item, extract every person who is
moving into a new senior role in a UK public sector or not-for-profit organisation. Ignore board/non-executive/
trustee appointments and private-sector-only moves.

Return ONLY a JSON list; each element:
{{"item": <item number>, "name": "...", "new_role": "...", "organisation": "...",
  "previous_role": "... (role and organisation, or empty if not stated)", "sector": "NFP|Education|Gov|Other"}}

Items:
{items}
"""


def linkedin_search(name, org=""):
    q = f"{name} {org}".strip()
    return f"https://www.linkedin.com/search/results/people/?keywords={quote(q)}"


ROLE_WORDS = {"General", "Director", "Chief", "Officer", "Innovation", "Secretary", "Permanent", "Executive",
              "Head", "New", "The", "NHS", "Department", "Home", "Council", "Board", "Trust", "University"}


def _clean_role(r):
    r = re.sub(r"^(?:the |its |new |first |current )+", "", r.strip(), flags=re.I)
    return re.sub(r"\s+role$", "", r).strip()


def _fallback(m):
    people = []
    for text in (m["headline"], m.get("summary", "")):
        pats = [
            rf"(?P<name>{NAME}) (?:has been |is )?(?i:appointed|named|confirmed) (?:as )?(?P<role>[^.,;]+)",
            rf"(?i:appoints?) (?P<role>[^.,;]+?),? (?P<name>{NAME})\b",
            rf"(?P<name>{NAME}) (?:joins|takes up|to (?:lead|head|join))\s+(?P<role>[^.,;]+)",
        ]
        for p in pats:
            for mm in re.finditer(p, text):
                name = mm.group("name").strip()
                if set(name.split()) & ROLE_WORDS or any(x["name"] == name for x in people):
                    continue
                people.append({"name": name, "new_role": _clean_role(mm.group("role")), "organisation": "",
                               "previous_role": ""})
    org = re.match(r"^([A-Z][\w&’' -]+?) (?:appoints|names|confirms|welcomes)", m["headline"])
    for x in people:
        role = x["new_role"]
        x["organisation"] = org.group(1) if org else ""
        # "Department for Education Permanent Secretary" -> split organisation off the front
        mm = re.match(r"^((?:Department|Ministry|Office|Cabinet Office|HM \w+)[\w ,&]*?) (Permanent Secretary|Director General.*|Chief .*|Director .*)$", role)
        if mm and not x["organisation"]:
            x["organisation"], x["new_role"] = mm.group(1), mm.group(2)
    return people


def extract(moves):
    """moves: list of PeopleMove dicts -> list of person dicts (with source news link)."""
    if not moves:
        return []
    people = []
    if os.environ.get("ANTHROPIC_API_KEY"):
        import anthropic
        items = "\n".join(f"{i}. {m['headline']} - {m.get('summary', '')}" for i, m in enumerate(moves))
        msg = anthropic.Anthropic().messages.create(
            model=MODEL, max_tokens=6000, messages=[{"role": "user", "content": PROMPT.format(items=items)}])
        text = "".join(b.text for b in msg.content if b.type == "text")
        try:
            for p in json.loads(text[text.find("["): text.rfind("]") + 1]):
                m = moves[int(p["item"])]
                people.append({**p, "news_url": m["url"], "news_source": m["source"], "published": m["published"]})
        except (ValueError, KeyError, IndexError):
            people = []
    if not people:
        for m in moves:
            for p in _fallback(m):
                people.append({**p, "news_url": m["url"], "news_source": m["source"], "published": m["published"]})
    for p in people:
        p["linkedin"] = linkedin_search(p["name"], p.get("organisation", ""))
    return people
