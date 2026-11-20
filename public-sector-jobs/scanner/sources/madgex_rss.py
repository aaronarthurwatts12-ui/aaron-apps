"""Job boards running on the Madgex platform, which publish keyword RSS feeds.

  - WM Jobs: West Midlands councils and public bodies
  - Inside Housing Jobs: housing associations and council housing teams
  - Times Higher Education Jobs: universities
Each feed returns the 20 newest matches, so we run one query per keyword.
"""
import re
from email.utils import parsedate_to_datetime
from html import unescape
from xml.etree import ElementTree as ET
from ..http import get
from ..models import Job

BOARDS = {
    "WM Jobs": "https://www.wmjobs.co.uk/jobsrss/",
    "Inside Housing Jobs": "https://jobs.insidehousing.co.uk/jobsrss/",
    "THE Jobs": "https://jobs.timeshighereducation.com/jobsrss/",
}
QUERIES = ["director", "chief executive", "chief", "head of", "HR", "human resources", "people",
           "payroll", "transformation", "digital", "ICT", "procurement", "finance"]


def fetch(since):
    jobs = {}
    for board, base in BOARDS.items():
        for q in QUERIES:
            try:
                root = ET.fromstring(get(base, params={"keywords": q, "countrycode": "GB"}, pause=0.5).content)
            except Exception as e:
                print(f"  {board} '{q}' failed: {e}")
                continue
            for it in root.iter("item"):
                t = unescape(it.findtext("title") or "")
                org, _, title = t.partition(": ") if ": " in t else ("", "", t)
                desc = unescape(it.findtext("description") or "").strip().splitlines()
                desc = [d.strip() for d in desc if d.strip()]
                try:
                    posted = parsedate_to_datetime(it.findtext("pubDate")).date().isoformat()
                except Exception:
                    posted = ""
                if posted and posted < since:
                    continue
                url = re.sub(r"\?.*$", "", it.findtext("link") or "")
                jobs[url] = Job(board, title.strip(), org.strip(), url,
                                desc[-1] if len(desc) > 2 else "",
                                desc[0].rstrip(":") if desc else "", posted, "")
    return list(jobs.values())
