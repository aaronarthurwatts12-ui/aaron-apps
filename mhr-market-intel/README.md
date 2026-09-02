# MHR Market Intel

A weekly public-sector market intelligence digest for MHR's marketing team:
competitor activity, content (watch + gap analysis + topic suggestions),
legislation changes, relevant industry news, people moves, and new job
openings — plus account-specific renewal-timing flags — across seven
public-sector verticals: Education, Local Government, Central Government,
Emergency Services & Military, Charity, Housing Associations, and
Healthcare (the last two weren't in the original brief; see "What's
needed from you").

Each item comes with a one-line "so what for MHR" note, and every digest
closes with a **Suggested Actions For This Week** section — specific,
tied to that week's findings (e.g. "create X content", "flag this job
opening/role change to sales") — not generic advice.

## How it works

1. **`config/targets.yaml`** — the single source of truth: competitors,
   named target accounts, sectors and sub-segments, job titles to watch
   for people-moves/hiring signals, news keywords, legislation topics to
   track, and content-strategy inputs (MHR's own content sources, topic
   clusters for gap analysis). Everything in it marked `TODO`/`EXAMPLE`
   is a placeholder and should be replaced with your real lists.
2. **`.claude/skills/mhr-digest/SKILL.md`** — the process a Claude Code
   session follows to turn that config into a digest: targeted web
   searches per category, relevance filtering, then a written report.
3. **`templates/digest_template.md`** — the output shape.
4. **`reports/`** — where plain-markdown digests land if
   `delivery.format: markdown` is set; the default (`artifact`) instead
   publishes a styled report you get a link to.

## Running it

In a Claude Code session on this repo, run:

```
/mhr-digest
```

Or ask in plain language ("run the MHR market intel digest").

## What's needed from you to make it real

- **Confirm Healthcare and Housing Associations should stay in scope.**
  They weren't in the original 4-vertical brief but appear as real
  Industry values in the CRM export (8 and 5 accounts respectively) —
  currently tracked; say if either should be dropped.
- **Confirm the ~200 accounts with only a past renewal date on file.**
  `has_past_renewal_date_on_file` is true for accounts where every
  renewal date in the export is already behind us — could be stale CRM
  data (last signed date rather than next renewal) or a genuinely lapsed
  record. These aren't currently surfaced as actions; say if there's a
  standard contract length to project forward from instead.
- MHR's own content hub/blog URL(s) so the content-gap analysis compares
  against what's actually been published, not an assumption.
- Confirmation the competitor list is complete — Sage, Frontier, IRIS,
  Civica and Cintra were added because they show up as the *incumbent*
  supplier at real target accounts (see below); TechOne hasn't appeared
  as an incumbent anywhere in the account data yet.
- Any preferred trade press / sources to prioritize or exclude.

## Target accounts

`config/target_accounts.csv` is the primary list — 315 real accounts
across all 7 sectors, each with Employees, current HR/Payroll
product+supplier, and computed `contract_end_date` /
`start_engagement_by` (per the `sales_cycle_timing` rule in
`targets.yaml`: org size → typical sales cycle → work backwards from
contract end date). Of the 315: **120 have a computed future
contract_end_date**, and of those, **61 are already past their
start-engagement-by date** (overdue — flag immediately) and **25 more
enter their engagement window in the next 6 months**.

The current-supplier field is also a live competitive-intelligence
signal in its own right: Zellis (44 accounts — includes 15 originally
recorded as "Northgate," which is Zellis under its pre-2019 name, not a
separate competitor; see `notes` on the Zellis entry in
`config/targets.yaml`), Access Group (24), Oracle (17), Sage (15),
Frontier (14), IRIS (13), SAP (12), and Core International (12) are the
largest incumbents across these 315 accounts.

`config/target_accounts_education_prospects.csv` is a larger (1,576-row),
Education-only, mostly-undated pool from an earlier export — kept as a
broader top-of-funnel list for Education content/people-moves targeting,
not for renewal-timing actions. Both lists are a floor, not a ceiling:
the digest's competitor/legislation/industry findings apply to a sector
even when no specific account is named in the source, per your brief.

## Content watch: sitemap diffing

`scripts/sitemap_diff.py` fetches each competitor's `sitemap_url` (set
in `config/targets.yaml`), compares it against last week's snapshot in
`data/sitemap_snapshots/`, and reports pages added, removed, or updated
— a genuine "is this actually new" signal instead of guessing from
search-result freshness. Confirmed working (2 Sep 2026) for Zellis, IRIS,
and Access Group; Unit4 and Civica are both behind a Cloudflare
JS-challenge and can't be fetched this way (by design — not something
this pipeline tries to route around) and fall back to search-based
content watch. SAP, Oracle, Sage, Frontier, TechOne and Cintra don't
have a confirmed `sitemap_url` yet — untested, not necessarily blocked.

This only works because the environment's network policy was opened to
general outbound access on 2 Sep 2026 — before that, all external
fetches (`WebFetch` and Bash `curl` alike) were blocked entirely by a
blanket egress policy, not a domain-specific one. If sitemap fetches
start failing across the board again, check that policy before assuming
something else broke.

## Known limitations (v1)

- **People moves** is best-effort. **A personal LinkedIn API connection
  would not fix this**: LinkedIn's OAuth only grants access to the
  authenticated user's own profile data, not the ability to search or
  monitor other people's job changes — that requires either LinkedIn's
  restricted Marketing/Talent Solutions partner APIs (not self-serve),
  manual LinkedIn workflows (Sales Navigator saved searches/alerts,
  checked by hand), or a compliant third-party B2B data provider (e.g.
  Cognism, ZoomInfo, Lusha) with a real API and UK public-sector
  coverage. Scraping LinkedIn directly would violate its Terms of
  Service and isn't something this pipeline will do. Realistically this
  stays the thinnest section until either real named target accounts
  narrow the search, or a data-provider subscription is added — worth
  revisiting as a v2 spend decision once the rest of the digest proves
  its value.
- **Job openings** uses public job boards and target accounts' own careers
  pages; a structured jobs API (e.g. Adzuna) would make this more reliable
  and is a reasonable v2 upgrade if this section proves valuable.
- No paid SEO/ad-intel data sources (SEMrush, ad libraries, etc.) yet —
  content/competitor tracking is search-driven, not a paid feed.

## Automating the cadence

Already running: a weekly Routine fires `/mhr-digest` every Monday
06:00 UTC into this session (self-bound, so it keeps the Gmail connector
access set up here), publishing the artifact and emailing the branded
digest to `delivery.email.recipient`.
