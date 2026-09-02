# MHR Market Intel

A weekly public-sector market intelligence digest for MHR's marketing team:
competitor activity, content (watch + gap analysis + topic suggestions),
legislation changes, relevant industry news, people moves, and new job
openings across the four target verticals — Education, Local Government
(priority), Non-profit, and Emergency Services.

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

- **Contract end dates + employee-count bands for `target_accounts.csv`.**
  The CRM export you sent (`config/target_accounts.csv`, 1,576 rows) has
  Account Owner, Account Name, Country and Record Type (all "Prospect")
  — **no contract-end-date or employee-count field**, so the sales-cycle
  timing rule you described (3-6mo / 6-12mo / 12-24mo engagement windows
  by org size) can't compute anything yet. If Salesforce has those two
  fields on the Account object, a re-export including them would let the
  digest start surfacing real "start engaging by" dates instead of just
  a static account list.
- **A Sector/Industry field on that same export, if one exists in
  Salesforce.** Right now `sector_guess` in the CSV is classified by
  matching keywords in the account name (university/college/academy →
  Education, council/borough → Local government, etc.) — it got ~75% of
  1,576 accounts (mostly Education-heavy, matching the account mix),
  leaving ~390 "Unclassified" and an unknown number of mis-guesses (e.g.
  academy trusts named just "X Learning Trust" with no obvious keyword).
  A real CRM field would replace guesswork with fact.
- MHR's own content hub/blog URL(s) so the content-gap analysis compares
  against what's actually been published, not an assumption.
- Confirmation the competitor/job-title list (sourced from your
  spreadsheet) is complete — SAP and Oracle are tagged as lower-frequency
  "larger ERP" tracking; say if that's wrong.
- Any preferred trade press / sources to prioritize or exclude.

## Target accounts

`config/target_accounts.csv` holds the real prospect list — treat it as a
floor, not a ceiling: the digest's competitor/legislation/industry
findings apply to a sector even when no specific account here is named in
the source, per your brief. `config/targets.yaml`'s `sales_cycle_timing`
section encodes the engagement-window rule (org size → typical sales
cycle → work backwards from contract end date) so it's ready to compute
real dates the moment the two missing CSV fields above are filled in.

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

Once the config is populated and the format is approved, this can run on
a schedule (e.g. a weekly Routine that fires `/mhr-digest` into a session)
so the digest lands automatically rather than being run by hand. Ask for
this to be set up once you're happy with the output.
