#!/usr/bin/env python3
"""Weekly sitemap snapshot + diff for the mhr-digest Content Watch step.

For each competitor in config/targets.yaml with a `sitemap_url`, fetches
its sitemap (recursing into a sitemap index), compares the URL set
against last week's stored snapshot in data/sitemap_snapshots/, and
reports added/removed/updated (lastmod-changed) pages. Overwrites the
snapshot with the current state either way, so next week's run diffs
against this one.

A competitor whose sitemap can't be fetched (bot-protected, e.g.
Cloudflare's JS challenge) is reported as such and should fall back to
the WebSearch-based content watch for that run - see SKILL.md.

Usage: python3 scripts/sitemap_diff.py [--json]
Requires: pyyaml (pip install pyyaml)
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from xml.etree import ElementTree as ET

import yaml

UA = "Mozilla/5.0 (compatible; MHR-Pulse-Monitor/1.0; +internal competitive intelligence tool for MHR)"
ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_DIR = ROOT / "data" / "sitemap_snapshots"
CONFIG_PATH = ROOT / "config" / "targets.yaml"
MAX_SITEMAP_DEPTH = 3


def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def localname(tag):
    """Strip the namespace off an ElementTree tag - vendors vary between
    http:// and https:// sitemap namespace URIs, so matching by local
    name only is far more robust than a hardcoded namespace map."""
    return tag.split("}")[-1] if "}" in tag else tag


def safe_parse_xml(xml_bytes):
    """Some vendors mislabel the XML declaration's encoding (e.g. claim
    utf-16 while actually serving utf-8 bytes), which ElementTree
    rejects outright. Retry as plain text with the declaration stripped
    before giving up."""
    try:
        return ET.fromstring(xml_bytes)
    except ET.ParseError:
        try:
            text = xml_bytes.decode("utf-8", errors="replace")
            text = re.sub(r"^\s*<\?xml[^>]*\?>", "", text, count=1)
            return ET.fromstring(text)
        except ET.ParseError:
            return None


def parse_sitemap(xml_bytes, seen=None, depth=0):
    """Returns {url: lastmod_or_None}, recursing into a sitemap index."""
    if seen is None:
        seen = set()
    urls = {}
    root = safe_parse_xml(xml_bytes)
    if root is None:
        return urls
    tag = localname(root.tag)
    if tag == "sitemapindex":
        if depth >= MAX_SITEMAP_DEPTH:
            return urls
        for sm in root:
            if localname(sm.tag) != "sitemap":
                continue
            loc = next((c.text.strip() for c in sm if localname(c.tag) == "loc" and c.text), None)
            if not loc or loc in seen:
                continue
            seen.add(loc)
            try:
                urls.update(parse_sitemap(fetch(loc), seen, depth + 1))
            except Exception as e:
                print(f"    ! sub-sitemap fetch failed: {loc} ({e})", file=sys.stderr)
    elif tag == "urlset":
        for u in root:
            if localname(u.tag) != "url":
                continue
            loc = None
            lastmod = None
            for c in u:
                ln = localname(c.tag)
                if ln == "loc" and c.text:
                    loc = c.text.strip()
                elif ln == "lastmod" and c.text:
                    lastmod = c.text.strip()
            if loc:
                urls[loc] = lastmod
    return urls


def slugify(name):
    return "".join(c if c.isalnum() else "-" for c in name.lower()).strip("-")


def run():
    config = yaml.safe_load(CONFIG_PATH.read_text())
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    report = []
    for comp in config.get("competitors", []):
        name = comp.get("name")
        sitemap_url = comp.get("sitemap_url")
        if not sitemap_url:
            report.append({"competitor": name, "status": "no_sitemap_configured"})
            continue

        slug = slugify(name)
        snap_path = SNAPSHOT_DIR / f"{slug}.json"
        try:
            current = parse_sitemap(fetch(sitemap_url))
        except Exception as e:
            report.append({"competitor": name, "status": "fetch_failed", "error": str(e)})
            continue
        if not current:
            report.append({"competitor": name, "status": "empty_or_blocked"})
            continue

        first_run = not snap_path.exists()
        previous = json.loads(snap_path.read_text()) if not first_run else {}
        added = sorted(set(current) - set(previous))
        removed = sorted(set(previous) - set(current))
        updated = sorted(
            u for u in (set(current) & set(previous))
            if current[u] and previous.get(u) and current[u] != previous[u]
        )
        snap_path.write_text(json.dumps(current, indent=2, sort_keys=True))
        report.append({
            "competitor": name,
            "status": "first_snapshot" if first_run else "diffed",
            "total_pages": len(current),
            "added": added,
            "removed": removed,
            "updated": updated,
        })
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="raw JSON output")
    args = parser.parse_args()
    result = run()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for r in result:
            print(f"\n== {r['competitor']} ==")
            status = r["status"]
            if status == "no_sitemap_configured":
                print("  no sitemap_url configured — use WebSearch content watch")
            elif status == "fetch_failed":
                print(f"  fetch failed: {r['error']} — likely bot-protected, use WebSearch content watch")
            elif status == "empty_or_blocked":
                print("  sitemap returned but empty/unparsable — use WebSearch content watch")
            elif status == "first_snapshot":
                print(f"  first snapshot recorded: {r['total_pages']} pages. Nothing to diff until next run.")
            else:
                print(f"  {r['total_pages']} pages tracked")
                print(f"  + {len(r['added'])} added" + (f": {r['added'][:10]}" if r["added"] else ""))
                print(f"  - {len(r['removed'])} removed" + (f": {r['removed'][:10]}" if r["removed"] else ""))
                print(f"  ~ {len(r['updated'])} updated" + (f": {r['updated'][:10]}" if r["updated"] else ""))
