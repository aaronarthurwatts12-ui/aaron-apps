---
name: mhr-digest
description: Generate MHR's weekly public-sector market intelligence digest — competitor activity, content, industry news, people moves, and job openings across Education, Government (local priority), Non-profit, and Emergency Services target accounts. Use when the user asks to run, build, or refresh the MHR market intel / competitor digest.
---

# MHR Market Intelligence Digest

Produces a weekly roundup for MHR's public-sector marketing team: what
competitors are doing, what's moving in the industry, and who's changing
roles or hiring at target accounts — each item translated into a "why it
matters for MHR" note, not just aggregated links.

## 1. Load config

Read `mhr-market-intel/config/targets.yaml`. It defines: `sectors`,
`competitors`, `target_accounts`, `job_titles`, `keywords.include` /
`keywords.exclude`.

If `target_accounts` still only contains the `EXAMPLE` placeholder, tell
the user this run is illustrative only (their real account list hasn't
been supplied yet) — still produce the digest, but label it clearly as a
sample.

Default lookback window: **7 days** (last 14 if a category comes back
thin — note when you've widened it).

## 2. Gather each category

Run these as targeted `WebSearch` calls (a handful per category, not one
mega-query — narrow queries return more usable results than broad ones).
Use `WebFetch` on a specific article/newsroom page when a search result
needs more detail to summarize accurately.

**A. Competitor activity & content** — per competitor in the config:
- `"<competitor>" public sector` and `"<competitor>" (council OR NHS OR university OR "fire and rescue")`
- `"<competitor>" announcement OR partnership OR contract win`
- `"<competitor>" blog OR case study OR webinar` (content watch — what
  they're publishing, not just news)

**B. Industry news** — combine `keywords.include` terms with sector
names from the config, e.g. `"HR transformation" local government UK`,
`payroll transformation NHS OR council`. Drop anything matching
`keywords.exclude`. Prefer UK public-sector-relevant sources (trade press
like LocalGov, Public Sector Executive, UKAuthority, Civil Service World,
Personnel Today, HR magazine; also gov.uk and target-account press
releases). Discard generic/US HR-tech news with no public-sector angle.

**C. People moves** — for each job title in the config, combine with
sector/account terms, e.g. `"appointed" "HR Director" council 2026`,
`"new role" "Head of HR Transformation" NHS`. Note: this cannot scrape
LinkedIn directly — rely on what search engines surface (press releases,
council/trust news pages, publicly indexed LinkedIn posts). Treat this
category as best-effort and say so; it will always be the thinnest one
without a paid people-data source.

**D. New job openings** — search official public-sector job boards
directly for the configured job titles: LGjobs (local government),
NHS Jobs, Civil Service Jobs (gov.uk), charity job boards, and each
target account's own careers page. A posting for one of the configured
titles is itself a signal (budget + appetite for change), independent of
whether MHR would ever apply.

## 3. Filter for relevance

Drop anything that isn't clearly tied to: a configured competitor, a
configured target account, one of the four sectors, or a configured
keyword/job title. When in doubt, cut it — a short high-signal digest
beats a long noisy one.

## 4. Write the digest

Use `mhr-market-intel/templates/digest_template.md` as the section
structure. For every item give: a one-line summary, the source link, and
a one-line "so what for MHR" note. Close with a short **This Week's
Actions** section — 2-4 concrete, specific marketing actions suggested by
what was found (not generic advice — tie each one to a specific item
above).

## 5. Deliver

Check `delivery.format` in the config:
- `artifact` (default): load the `artifact-design` skill, then publish
  the digest as a styled HTML Artifact (title it "MHR Market Intel — Week
  of <date>"). Favicon: 📡.
- `markdown`: write to `mhr-market-intel/reports/YYYY-MM-DD-digest.md`.

Always tell the user which lookback window was used and which categories
came back thin, so they know where the config needs more input (more
named accounts, better competitor RSS feeds, etc.) rather than assuming
the pipeline is broken.
