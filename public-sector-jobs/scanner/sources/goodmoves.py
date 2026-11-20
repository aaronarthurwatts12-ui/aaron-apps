"""goodmoves - Scotland's main charity / third sector jobs board."""
import re
from bs4 import BeautifulSoup
from ..filters import functions_for
from ..http import get
from ..models import Job

BASE = "https://goodmoves.org"
QUERIES = ["director", "chief executive", "head of", "HR", "people", "payroll", "finance",
           "digital", "transformation", "IT"]


def fetch(since, max_pages=3):
    jobs = {}
    for q in QUERIES:
        for page in range(1, max_pages + 1):
            r = get(f"{BASE}/search", params={"keywords": q, "page": page})
            r.encoding = "utf-8"
            soup = BeautifulSoup(r.text, "html.parser")
            cards = soup.select("div.search-result[data-vacancy-id]")
            if not cards:
                break
            for c in cards:
                a = c.select_one("h2 a")
                t = c.select_one("h2 .hover-underline")
                org = c.select_one("ul.organisation a")
                sal = c.select_one(".mdc-card__info--content-primary-salary")
                close = c.find(attrs={"title": "Closing date"})
                close_txt = close.find_parent("li").get_text(" ", strip=True) if close else ""
                url = BASE + a["href"].split("?")[0]
                jobs[url] = Job("goodmoves", t.get_text(strip=True) if t else a.get_text(strip=True),
                                org.get_text(strip=True) if org else "", url, "Scotland",
                                " ".join(sal.get_text().split()) if sal else "", "",
                                close_txt.replace("Closing", "").strip())
            if len(cards) < 10:
                break
    # The search page shows no posted date, so read it from each relevant job's own page.
    out = []
    for j in jobs.values():
        if not functions_for(j.title):
            continue
        try:
            m = re.search(r'"datePosted"\s*:\s*"(\d{4}-\d{2}-\d{2})', get(j.url, pause=0.5).text)
            j.posted = m.group(1) if m else ""
        except Exception:
            pass
        if j.posted and j.posted < since:
            continue
        out.append(j)
    return out
