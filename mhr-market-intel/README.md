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

- **Named target accounts** per sector, ideally with a priority tier —
  the biggest remaining gap. Without these, "people moves" and
  account-level signals stay generic rather than targeted.
- MHR's own content hub/blog URL(s) so the gap analysis compares against
  what's actually been published, not an assumption.
- Confirmation the competitor/job-title list (now sourced from your
  spreadsheet) is complete — SAP and Oracle are tagged as lower-frequency
  "larger ERP" tracking; say if that's wrong.
- Any preferred trade press / sources to prioritize or exclude.

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
