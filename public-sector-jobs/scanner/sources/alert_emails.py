"""Jobs from Indeed, Totaljobs and LinkedIn job-alert emails.

None of these sites allow automated searching, but all of them will email you
job alerts. Point those alerts at a Gmail inbox and this module reads them over
IMAP (Gmail app password) and pulls out each job link.

Env: ALERTS_IMAP_USER, ALERTS_IMAP_PASSWORD (Gmail app password),
     ALERTS_IMAP_HOST (default imap.gmail.com)
"""
import email
import imaplib
import os
import re
from datetime import datetime, timedelta
from email.header import decode_header, make_header
from html import unescape
from bs4 import BeautifulSoup
from ..models import Job

SENDERS = {
    "Indeed": ["indeed.com"],
    "Totaljobs": ["totaljobs.com"],
    "LinkedIn": ["linkedin.com"],
}
JOB_LINK = {
    "Indeed": re.compile(r"indeed\.(com|co\.uk)/(rc/clk|viewjob|pagead/clk|m/viewjob)|jk=", re.I),
    "Totaljobs": re.compile(r"totaljobs\.com/(job/|jobs?/)|/job/\d+", re.I),
    "LinkedIn": re.compile(r"linkedin\.com/(comm/)?jobs/view/", re.I),
}


def _html(msg):
    for part in msg.walk():
        if part.get_content_type() == "text/html":
            return part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", "replace")
    return ""


def _clean_url(board, url):
    if board == "LinkedIn":
        m = re.search(r"jobs/view/(\d+)", url)
        if m:
            return f"https://www.linkedin.com/jobs/view/{m.group(1)}/"
    return url


def _parse(board, html):
    soup = BeautifulSoup(html, "html.parser")
    jobs = {}
    for a in soup.find_all("a", href=True):
        href = unescape(a["href"])
        title = " ".join(a.get_text(" ").split())
        if not JOB_LINK[board].search(href) or len(title) < 4 or len(title) > 140:
            continue
        if title.lower() in ("view job", "apply now", "see all jobs", "view all jobs", "apply"):
            continue
        # employer / location are usually the next couple of text lines after the title link
        cell = a.find_parent(["td", "div", "tr"]) or a.parent
        lines = [l for l in (" ".join(x.split()) for x in cell.get_text("\n").split("\n")) if l and l != title]
        org = lines[0] if lines else ""
        loc = lines[1] if len(lines) > 1 else ""
        url = _clean_url(board, href)
        jobs.setdefault(url, Job(board, title, org, url, loc))
    return list(jobs.values())


def fetch(since):
    user, pw = os.environ.get("ALERTS_IMAP_USER"), os.environ.get("ALERTS_IMAP_PASSWORD")
    if not (user and pw):
        print("  alert_emails: ALERTS_IMAP_USER/PASSWORD not set - skipping Indeed/Totaljobs/LinkedIn alerts")
        return []
    imap = imaplib.IMAP4_SSL(os.environ.get("ALERTS_IMAP_HOST", "imap.gmail.com"))
    imap.login(user, pw)
    imap.select("INBOX", readonly=True)
    since_imap = datetime.fromisoformat(since).strftime("%d-%b-%Y")
    out = []
    for board, domains in SENDERS.items():
        for d in domains:
            typ, data = imap.search(None, f'(SINCE "{since_imap}" FROM "{d}")')
            for num in (data[0].split() if typ == "OK" else []):
                typ, raw = imap.fetch(num, "(RFC822)")
                msg = email.message_from_bytes(raw[0][1])
                subj = str(make_header(decode_header(msg.get("Subject", ""))))
                if board == "LinkedIn" and "job" not in subj.lower():
                    continue
                posted = email.utils.parsedate_to_datetime(msg["Date"]).date().isoformat()
                for j in _parse(board, _html(msg)):
                    j.posted = posted
                    out.append(j)
    imap.logout()
    return out
