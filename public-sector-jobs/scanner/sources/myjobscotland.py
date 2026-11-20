"""myjobscotland - all 32 Scottish councils plus associated public bodies."""
from datetime import date, datetime
from bs4 import BeautifulSoup
from ..http import get
from ..models import Job

BASE = "https://myjobscotland.gov.uk"
QUERIES = ["director", "chief", "head of", "HR", "human resources", "people", "payroll",
           "transformation", "digital", "ICT", "procurement", "finance"]


def fetch(since, max_pages=5):
    jobs = {}
    for q in QUERIES:
        for page in range(1, max_pages + 1):
            r = get(f"{BASE}/search-jobs", params={"keyword": q, "page": page})
            soup = BeautifulSoup(r.text, "html.parser")
            cards = soup.select("div.mjs-card")
            if not cards:
                break
            new = 0
            for c in cards:
                a = c.select_one(".mjs-card__title a")
                if not a:
                    continue
                pub = c.select_one(".mjs-card__title").find_next("span", class_="label")
                org = pub.get_text(" ", strip=True).replace("Published by", "").strip() if pub else ""
                added = c.select_one("[data-date]")
                posted = added["data-date"][:10] if added else ""
                if posted and posted < since:
                    continue
                desc = c.select_one(".mjs-card__description")
                tag = c.select_one(".mjs-card__tags[title]")
                closing = tag["title"].split(" - ")[-1] if tag else ""
                url = a["href"] if a["href"].startswith("http") else BASE + a["href"]
                if url not in jobs:
                    new += 1
                jobs[url] = Job("myjobscotland", a.get_text(strip=True), org, url,
                                desc.get_text(" ", strip=True) if desc else "", "", posted, closing)
            if new == 0:
                break
    return list(jobs.values())
