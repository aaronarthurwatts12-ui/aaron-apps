# MHR Market Intel

A weekly public-sector market intelligence digest for MHR's marketing team:
competitor activity, competitor content, relevant industry news, people
moves, and new job openings across the four target verticals — Education,
Government (local priority), Non-profit, and Emergency Services.

Each item comes with a one-line "so what for MHR" note, and every digest
closes with a short list of specific, actionable marketing moves — this
is meant to drive action, not just aggregate links.

## How it works

1. **`config/targets.yaml`** — the single source of truth: competitors,
   named target accounts, the four sectors, job titles to watch for
   people-moves/hiring signals, and news keywords. Everything in it
   marked `TODO`/`EXAMPLE` is a placeholder and should be replaced with
   your real lists.
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

- Real competitor list (the ones in the config now are a generic
  starting guess — confirm or replace)
- Named target accounts per sector, ideally with a priority tier
- Confirmation of the job titles worth tracking (list in config is a
  first pass)
- Any preferred trade press / sources to prioritize or exclude

## Known limitations (v1)

- **People moves** is best-effort — there's no LinkedIn API access here,
  so this relies on what's publicly indexed (press releases, council/trust
  news pages, indexed posts). It will usually be the thinnest section.
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
