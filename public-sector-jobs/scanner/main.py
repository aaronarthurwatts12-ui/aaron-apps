"""Weekly run: scrape -> match roles -> classify orgs -> dedupe -> email.

  python -m scanner.main                 # full run, sends email
  python -m scanner.main --dry-run       # writes output/report.html, no email
  python -m scanner.main --days 14       # look back further
"""
import argparse
import json
import os
from datetime import date, timedelta
from pathlib import Path

from . import classify, filters, movers, report
from .sources import (alert_emails, goodmoves, jobs_ac_uk, madgex_rss, myjobscotland, nhs_jobs,
                      people_moves, teaching_vacancies)

ROOT = Path(__file__).parent.parent
SEEN = ROOT / "data" / "seen.json"
OUT = ROOT / "output"
JOB_SOURCES = [nhs_jobs, jobs_ac_uk, myjobscotland, teaching_vacancies, goodmoves, madgex_rss, alert_emails]


def scrape(since):
    raw = []
    for mod in JOB_SOURCES:
        name = mod.__name__.split(".")[-1]
        try:
            found = mod.fetch(since)
            print(f"{name}: {len(found)} postings")
            raw += [j.to_dict() for j in found]
        except Exception as e:  # keep going if one board is down
            print(f"{name}: FAILED ({e!r})")
    return raw


def select(raw, cache):
    """Dedupe, title-match and attach sector/band. Returns list of report rows."""
    seen_urls, candidates = set(), []
    for j in raw:
        key = j["url"].split("?")[0]
        if key in seen_urls:
            continue
        seen_urls.add(key)
        if filters.functions_for(j["title"]):
            candidates.append(j)
    classify.classify_unknown({j["organisation"]: (j["title"], j["source"]) for j in candidates}, cache)

    rows, dup = [], set()
    for j in candidates:
        info = cache.get(j["organisation"])
        if info:
            if info["sector"] == "Exclude" or info["band"] == "micro":
                continue
            band, sector = info["band"], info["sector"]
            org = info.get("canonical") or j["organisation"]
        else:
            band, sector, org = "?", "Unclassified", j["organisation"] or "(employer not stated)"
            info = {}
        funcs = filters.matches(j["title"], band if band != "?" else "small")
        if not funcs:
            continue
        sig = (org.lower(), j["title"].lower())
        if sig in dup:  # same role re-posted across boards / member schools
            continue
        dup.add(sig)
        rows.append({**j, "first_seen": date.today().isoformat(), "org": org, "sector": sector, "band": band,
                     "org_type": info.get("type", ""), "functions": funcs})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--moves-days", type=int, default=30)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--raw", help="reuse a saved raw postings JSON instead of scraping")
    ap.add_argument("--ignore-seen", action="store_true", help="include roles already sent before")
    a = ap.parse_args()

    today = date.today()
    since = (today - timedelta(days=a.days)).isoformat()
    OUT.mkdir(exist_ok=True)
    raw = json.loads(Path(a.raw).read_text()) if a.raw else scrape(since)
    (OUT / "raw.json").write_text(json.dumps(raw, indent=1, ensure_ascii=False))

    cache = classify.load_cache()
    rows = select(raw, cache)
    seen = json.loads(SEEN.read_text()) if SEEN.exists() else {}
    if not a.ignore_seen:
        rows = [r for r in rows if r["url"].split("?")[0] not in seen]

    moves_since = (today - timedelta(days=a.moves_days)).isoformat()
    try:
        news = [m.to_dict() for m in people_moves.fetch(moves_since)]
        if not a.ignore_seen:
            news = [m for m in news if "move:" + m["url"] not in seen]
        moves = movers.extract(news)
    except Exception as e:
        print(f"people_moves FAILED: {e!r}")
        news, moves = [], []

    label = f"{date.fromisoformat(since).strftime('%d %b')} - {today.strftime('%d %b %Y')}"
    html = report.build(rows, moves, label, notes=[
        "Size bands decide which titles are included: 100-400 staff = any HR/people/payroll/digital/finance-lead/CEO role; "
        "400-1,500 = Head of / Director / Lead level; 1,500+ = C-suite and Director level plus heads of HR, payroll, digital, procurement and transformation.",
        "Organisations under 100 staff, private companies and non-UK employers are left out.",
        "Each role shows the month it was posted (from the job board). Where a board gives no posted date, it shows the month the scanner first saw it.",
        "Sources: NHS Jobs, jobs.ac.uk, Teaching Vacancies (DfE), myjobscotland, goodmoves, WM Jobs, Inside Housing Jobs, THE Jobs, plus Indeed / Totaljobs / LinkedIn alert emails when connected.",
    ])
    (OUT / "report.html").write_text(html)
    print(f"{len(rows)} roles, {len(moves)} people moves -> {OUT / 'report.html'}")

    if not a.dry_run:
        from . import emailer
        to = os.environ.get("REPORT_TO", "aaron.watts@mhr.co.uk")
        emailer.send(f"Public sector HR & payroll buyer roles - w/c {date.fromisoformat(since).strftime('%d %b %Y')}", html, to)
        for r in rows:
            seen[r["url"].split("?")[0]] = today.isoformat()
        for n in news:
            seen["move:" + n["url"]] = today.isoformat()
        cutoff = (today - timedelta(days=120)).isoformat()
        SEEN.write_text(json.dumps({k: v for k, v in seen.items() if v >= cutoff}, indent=0))
        print(f"emailed {to}")


if __name__ == "__main__":
    main()
