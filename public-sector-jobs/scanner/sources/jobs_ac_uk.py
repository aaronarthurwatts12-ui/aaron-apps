"""jobs.ac.uk - universities, FE colleges and research bodies."""
import re
from datetime import date, datetime
from bs4 import BeautifulSoup
from ..http import get
from ..models import Job

BASE = "https://www.jobs.ac.uk"
QUERIES = ["director", "chief", "head of", "HR", "human resources", "people", "payroll",
           "transformation", "digital", "IT", "procurement", "finance", "vice-chancellor", "principal"]


def _date(txt, today):
    txt = " ".join(txt.split())
    try:
        d = datetime.strptime(f"{txt} {today.year}", "%d %b %Y").date()
    except ValueError:
        return ""
    if d > today:
        d = d.replace(year=today.year - 1)
    return d.isoformat()


def fetch(since, max_pages=6):
    today = date.today()
    jobs = {}
    for q in QUERIES:
        for page in range(max_pages):
            r = get(f"{BASE}/search/", params={"keywords": q, "sortOrder": 1, "pageSize": 100,
                                              "startIndex": 1 + page * 100})
            soup = BeautifulSoup(r.text, "html.parser")
            items = soup.select("div.j-search-result__result")
            if not items:
                break
            stop = False
            for it in items:
                a = it.select_one(".j-search-result__text > a")
                if not a:
                    continue
                emp = it.select_one(".j-search-result__employer")
                placed = it.find("strong", string=re.compile("Date Placed"))
                posted = _date(placed.next_sibling, today) if placed else ""
                if posted and posted < since:
                    stop = True
                    continue
                loc = it.find("div", string=re.compile("Location:"))
                sal = it.select_one(".j-search-result__info")
                close = it.select_one(".j-search-result__date--blue")
                url = BASE + a["href"]
                jobs[url] = Job("jobs.ac.uk", " ".join(a.get_text().split()),
                                emp.get_text(strip=True) if emp else "", url,
                                " ".join(loc.get_text().replace("Location:", "").split()) if loc else "",
                                " ".join(sal.get_text().replace("Salary:", "").split()) if sal else "",
                                posted, close.get_text(strip=True) if close else "")
            if stop or len(items) < 100:
                break
    return list(jobs.values())
