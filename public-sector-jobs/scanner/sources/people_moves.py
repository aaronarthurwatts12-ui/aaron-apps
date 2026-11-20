"""People moves: senior HR / finance / digital appointments in public sector & charities.

Sources are public news feeds (GOV.UK search API and trade press RSS). An item is
kept when its headline/summary reads like an appointment AND mentions a relevant role.
"""
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree as ET
from html import unescape
from ..http import get
from ..models import PeopleMove

RSS = {
    "Personnel Today": "https://www.personneltoday.com/feed/",
    "HTN (Health Tech News)": "https://htn.co.uk/feed/",
    "Personnel Today (appointments search)": "https://www.personneltoday.com/?s=appointed&feed=rss2",
    "UKAuthority": "https://www.ukauthority.com/rss",
    "FE News": "https://www.fenews.co.uk/feed/",
    "LGC": "https://www.lgcplus.com/rss",
    "LocalGov": "https://www.localgov.co.uk/rss",
    "Wonkhe": "https://wonkhe.com/feed/",
}
GOVUK_QUERIES = ["appoints chief executive", "appointed director of people", "appointed chief people officer",
                 "appoints finance director", "appointed chief digital officer", "appointed chief operating officer",
                 "new permanent secretary", "appointed director general"]

APPOINT = re.compile(r"\b(appoint(s|ed|ment)?|named|names?d?|hires?d?|joins?|recruits?|new (chief|director|head|ceo|cfo|cpo|cio|cdo|cto)|to (lead|head)|promoted|steps up|moves to|takes (up|over)|confirmed as)\b", re.I)
ROLE = re.compile(r"\b(chief (executive|people|operating|financial|finance|digital|information|technology|transformation)( officer)?|ceo|cfo|cpo|coo|cio|cdo|cto|hr director|director of (hr|people|human resources|workforce|finance|digital|transformation|resources|corporate services)|people director|finance director|digital director|head of (hr|people|payroll|digital|transformation)|director general|permanent secretary|vice[- ]chancellor)\b", re.I)
NOISE = re.compile(r"\b(non-executive|reappointed|ambassador|judge|magistrate|trustee|honours|lord-lieutenant|high sheriff)\b", re.I)


def _keep(text):
    return APPOINT.search(text) and ROLE.search(text) and not NOISE.search(text)


def _strip(html):
    return " ".join(unescape(re.sub(r"<[^>]+>", " ", html or "")).split())


def fetch(since):
    out, seen = [], set()
    for name, url in RSS.items():
        try:
            root = ET.fromstring(get(url, pause=0.5).content)
        except Exception as e:  # one dead feed shouldn't stop the run
            print(f"  people_moves: {name} failed: {e}")
            continue
        for it in root.iter("item"):
            title = _strip(it.findtext("title"))
            link = (it.findtext("link") or "").strip()
            desc = _strip(it.findtext("description"))[:400]
            try:
                pub = parsedate_to_datetime(it.findtext("pubDate")).date().isoformat()
            except Exception:
                pub = ""
            if pub and pub < since:
                continue
            if _keep(f"{title} {desc}") and link not in seen:
                seen.add(link)
                out.append(PeopleMove(name, title, link, pub, desc))
    for q in GOVUK_QUERIES:
        try:
            d = get("https://www.gov.uk/api/search.json", pause=0.3, params={
                "q": q, "filter_content_store_document_type": "news_story",
                "filter_public_timestamp": f"from:{since}",
                "count": 20, "fields": "title,link,public_timestamp,description"}).json()
        except Exception as e:
            print(f"  people_moves: GOV.UK failed: {e}")
            continue
        for r in d.get("results", []):
            pub = (r.get("public_timestamp") or "")[:10]
            link = "https://www.gov.uk" + r["link"]
            if pub < since or link in seen:
                continue
            if _keep(f"{r['title']} {r.get('description', '')}"):
                seen.add(link)
                out.append(PeopleMove("GOV.UK", r["title"], link, pub, (r.get("description") or "")[:400]))
    return out
