"""NHS Jobs (jobs.nhs.uk) - NHS trusts, ICBs, hospices and other health employers."""
import re
from datetime import datetime
from bs4 import BeautifulSoup
from ..http import get
from ..models import Job

BASE = "https://www.jobs.nhs.uk"
QUERIES = ["director", "chief", "head of", "HR", "human resources", "people", "payroll",
           "workforce", "transformation", "digital", "IT", "procurement", "finance"]


def _date(txt):
    try:
        return datetime.strptime(txt.strip(), "%d %B %Y").date().isoformat()
    except ValueError:
        return ""


def fetch(since, max_pages=15):
    jobs = {}
    for q in QUERIES:
        for page in range(1, max_pages + 1):
            r = get(f"{BASE}/candidate/search/results",
                    params={"keyword": q, "sort": "publicationDateDesc", "page": page, "language": "en"})
            soup = BeautifulSoup(r.text, "html.parser")
            items = soup.select('li[data-test="search-result"]')
            if not items:
                break
            stop = False
            for li in items:
                a = li.select_one('a[data-test="search-result-job-title"]')
                loc = li.select_one('[data-test="search-result-location"] h3')
                org = loc.find(string=True, recursive=False).strip() if loc else ""
                place = loc.select_one(".location-font-size").get_text(" ", strip=True) if loc and loc.select_one(".location-font-size") else ""
                pub = li.select_one('[data-test="search-result-publicationDate"] strong')
                close = li.select_one('[data-test="search-result-closingDate"] strong')
                sal = li.select_one('[data-test="search-result-salary"] strong')
                posted = _date(pub.get_text()) if pub else ""
                if posted and posted < since:
                    stop = True
                    continue
                url = BASE + a["href"].split("?")[0]
                jobs[url] = Job("NHS Jobs", a.get_text(strip=True), org, url, place,
                                " ".join(sal.get_text().split()) if sal else "", posted,
                                close.get_text(strip=True) if close else "")
            if stop:
                break
    return list(jobs.values())
