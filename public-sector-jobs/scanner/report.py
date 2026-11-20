"""Builds the weekly HTML email (inline styles so it renders in Outlook/Gmail)."""
from collections import defaultdict
from datetime import date
from html import escape

SECTION_ORDER = [
    ("NFP", "Not-for-profit", "Charities, hospices, housing associations, social enterprises"),
    ("Education", "Education", "Universities, colleges, schools and academy trusts"),
    ("Gov", "Government", "Central government, agencies, councils, devolved bodies"),
    ("Other", "Other public sector (incl. NHS)", "NHS trusts, ICBs and other public bodies"),
    ("Unclassified", "Unclassified", "Organisations not yet sized or classified - check manually"),
]
BAND_LABEL = {"small": "100-400", "medium": "400-1,500", "large": "1,500+", "?": "size unknown"}
FUNC_LABEL = {"hr": "HR", "people": "People", "payroll": "Payroll", "transformation": "Transformation",
              "digital_it": "Digital / IT", "finance": "Finance / Ops", "procurement": "Procurement",
              "leadership": "CEO / Leadership"}
BLUE, INK, MUTED, LINE, BG = "#1f4e79", "#1a1a1a", "#666666", "#e3e6ea", "#f5f7fa"


def _job_row(j):
    tags = " · ".join(FUNC_LABEL.get(f, f) for f in j["functions"])
    meta = [x for x in [j.get("location"), j.get("salary")] if x]
    dates = []
    if j.get("posted"):
        dates.append(f"Posted {j['posted']}")
    if j.get("closing"):
        dates.append(f"Closes {j['closing']}")
    return f"""
    <tr><td style="padding:10px 0;border-bottom:1px solid {LINE};">
      <a href="{escape(j['url'])}" style="font-size:15px;font-weight:600;color:{BLUE};text-decoration:none;">{escape(j['title'])}</a>
      <div style="font-size:12px;color:{MUTED};margin-top:3px;">{escape(' | '.join(meta))}</div>
      <div style="font-size:12px;color:{MUTED};margin-top:2px;">{escape(' | '.join(dates))} &nbsp;·&nbsp; {escape(j['source'])} &nbsp;·&nbsp; <span style="color:{INK};">{escape(tags)}</span></div>
    </td></tr>"""


def build(jobs, moves, period_label, notes=None):
    by_sector = defaultdict(lambda: defaultdict(list))
    meta = {}
    for j in jobs:
        by_sector[j["sector"]][j["org"]].append(j)
        meta[j["org"]] = (j["band"], j.get("org_type", ""))

    counts = {k: sum(len(v) for v in by_sector[k].values()) for k, *_ in SECTION_ORDER}
    summary = " &nbsp;|&nbsp; ".join(f"<b>{label}</b>: {counts[k]}" for k, label, _ in SECTION_ORDER if counts[k])

    body = []
    for key, label, desc in SECTION_ORDER:
        orgs = by_sector.get(key)
        if not orgs:
            continue
        body.append(f"""
        <tr><td style="padding:26px 0 4px 0;">
          <div style="font-size:19px;font-weight:700;color:{INK};border-bottom:3px solid {BLUE};padding-bottom:6px;">{label}
            <span style="font-size:13px;font-weight:400;color:{MUTED};">&nbsp; {counts[key]} role{'s' if counts[key] != 1 else ''} · {len(orgs)} organisation{'s' if len(orgs) != 1 else ''}</span></div>
          <div style="font-size:12px;color:{MUTED};margin-top:4px;">{desc}</div>
        </td></tr>""")
        # biggest organisations first, then alphabetical
        rank = {"large": 0, "medium": 1, "small": 2, "?": 3}
        for org in sorted(orgs, key=lambda o: (rank.get(meta[o][0], 9), o.lower())):
            band, otype = meta[org]
            sub = " · ".join(x for x in [otype, f"{BAND_LABEL.get(band, band)} employees" if band != "?" else BAND_LABEL["?"]] if x)
            body.append(f"""
        <tr><td style="padding:14px 0 0 0;">
          <div style="font-size:15px;font-weight:700;color:{INK};">{escape(org)}</div>
          <div style="font-size:12px;color:{MUTED};">{escape(sub)}</div>
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0">{''.join(_job_row(j) for j in orgs[org])}</table>
        </td></tr>""")

    if moves:
        rows = "".join(f"""
          <tr><td style="padding:8px 0;border-bottom:1px solid {LINE};">
            <a href="{escape(m['url'])}" style="font-size:14px;font-weight:600;color:{BLUE};text-decoration:none;">{escape(m['headline'])}</a>
            <div style="font-size:12px;color:{MUTED};margin-top:2px;">{escape(m['published'])} · {escape(m['source'])}</div>
            {f'<div style="font-size:12px;color:{INK};margin-top:3px;">{escape(m["summary"][:220])}</div>' if m.get('summary') else ''}
          </td></tr>""" for m in moves)
    else:
        rows = f'<tr><td style="padding:8px 0;font-size:13px;color:{MUTED};">No relevant senior appointments found in the news sources this period.</td></tr>'
    body.append(f"""
        <tr><td style="padding:30px 0 4px 0;">
          <div style="font-size:19px;font-weight:700;color:{INK};border-bottom:3px solid {BLUE};padding-bottom:6px;">People moves</div>
          <div style="font-size:12px;color:{MUTED};margin-top:4px;">Senior HR, finance, digital and leadership appointments reported in GOV.UK and trade press news.</div>
        </td></tr>
        <tr><td><table role="presentation" width="100%" cellpadding="0" cellspacing="0">{rows}</table></td></tr>""")

    note_html = ""
    if notes:
        note_html = "".join(f"<li>{escape(n)}</li>" for n in notes)
        note_html = f'<tr><td style="padding:26px 0 0 0;font-size:12px;color:{MUTED};"><b>Notes</b><ul style="padding-left:18px;margin:6px 0;">{note_html}</ul></td></tr>'

    return f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:{BG};font-family:Segoe UI,Helvetica,Arial,sans-serif;color:{INK};">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{BG};"><tr><td align="center" style="padding:20px 12px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:720px;background:#ffffff;border:1px solid {LINE};">
  <tr><td style="background:{BLUE};padding:20px 24px;color:#ffffff;">
    <div style="font-size:12px;letter-spacing:1px;text-transform:uppercase;opacity:.85;">Weekly public sector signals</div>
    <div style="font-size:22px;font-weight:700;margin-top:4px;">HR &amp; payroll buyer roles</div>
    <div style="font-size:13px;margin-top:6px;opacity:.9;">{escape(period_label)} · {len(jobs)} roles across {len(meta)} organisations</div>
  </td></tr>
  <tr><td style="padding:12px 24px;background:#eef3f8;font-size:13px;">{summary}</td></tr>
  <tr><td style="padding:0 24px 24px 24px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0">
    {''.join(body)}
    {note_html}
  </table></td></tr>
</table></td></tr></table></body></html>"""
