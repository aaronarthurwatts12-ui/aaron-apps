---
name: mhr-digest
description: Generate MHR's weekly public-sector market intelligence digest — competitor activity, content gaps/suggestions, legislation changes, industry news, people moves, and job openings across Education, Local Government (priority), Non-profit, and Emergency Services target accounts. Use when the user asks to run, build, or refresh the MHR market intel / competitor digest.
---

# MHR Market Intelligence Digest

Produces a weekly roundup for MHR's public-sector marketing team: what
competitors are doing, what's moving in the industry, what's changing in
legislation, and who's changing roles or hiring at target accounts — each
item translated into a "why it matters for MHR" note, not just aggregated
links. Closes with a concrete actions list.

## 1. Load config

Read `mhr-market-intel/config/targets.yaml`. It defines: `sectors`
(each with `sub_segments`), `competitors`, `target_accounts`, `job_titles`,
`keywords.include`/`exclude`, `legislation.topics`/`sources`, and
`content_strategy` (`mhr_content_sources`, `topic_clusters`).

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

**A. Competitor activity** — per competitor in the config:
- `"<competitor>" public sector` and `"<competitor>" (council OR NHS OR university OR "fire and rescue")`
- `"<competitor>" announcement OR partnership OR contract win`
- Treat `tier: larger ERP` competitors (SAP, Oracle) as lower-frequency —
  only surface hits with a clear public-sector angle, not generic product news.

**B. Content — watch, gaps, and suggestions.** This section does three
distinct jobs, not just link aggregation:
  1. *Content watch*: what competitors and industry sources have actually
     published recently (`"<competitor>" blog OR case study OR webinar`,
     plus general searches per sector/topic cluster).
  2. *Gap analysis*: for each `content_strategy.topic_clusters` entry,
     check what's been found in (1) against `content_strategy
     .mhr_content_sources` (fetch those pages/feeds if provided) —
     surface clusters where competitors/industry are publishing and MHR
     visibly isn't. If `mhr_content_sources` is still a placeholder, say
     so and treat every cluster as an assumed gap rather than a confirmed
     one.
  3. *Emerging topics*: flag anything appearing across multiple sources
     this run that looks like it's about to become a bigger theme (a new
     policy consultation, a funding announcement, an early-adopter case
     study of a new approach) — these are "get ahead of it" prompts, not
     gaps in past coverage.

**C. Legislation watch** — for each `legislation.topics` entry, search
recent UK coverage (e.g. `"National Living Wage" 2026 rate change`,
`"Employment Rights Bill" update`, `NJC pay award 2026`,
`"Agenda for Change" pay 2026`). Prioritize `legislation.sources`. Only
include items with a real compliance or budget impact on public-sector
HR/payroll — not general political commentary. This is the one section
where "nothing new this week" is a valid, worth-stating outcome.

**D. Industry news** — combine `keywords.include` terms with sector names
from the config. Drop anything matching `keywords.exclude`. Prefer UK
public-sector-relevant trade press (LocalGov, Public Sector Executive,
UKAuthority, Civil Service World, Personnel Today, HR magazine) and
gov.uk/target-account press releases over generic HR-tech news.

**E. People moves** — for each job title in the config (including the
open-ended "any digital transformation title" entry — read it broadly),
combine with sector/account terms, e.g. `"appointed" "HR Director"
council 2026`. Note: there is no LinkedIn API access here — personal
OAuth only exposes the authenticated user's own profile, not other
people's job changes, and third-party scraping violates LinkedIn's ToS.
This category relies on what search engines surface (press releases,
council/trust news pages, publicly indexed posts) and will always be the
thinnest without either real named target accounts to search against or
a compliant B2B data provider (see README "Known limitations").

**F. New job openings** — search official public-sector job boards
directly for the configured job titles: LGjobs (local government),
NHS Jobs, Civil Service Jobs (gov.uk), charity job boards, and each
target account's own careers page. A posting for one of the configured
titles is itself a signal (budget + appetite for change).

## 3. Filter for relevance

Drop anything that isn't clearly tied to: a configured competitor, a
configured target account, one of the four sectors, a configured
keyword/job title, or a legislation topic. When in doubt, cut it — a
short high-signal digest beats a long noisy one.

## 4. Write the digest

Use `mhr-market-intel/templates/digest_template.md` as the section
structure: Competitor Activity → Content → Legislation Watch → Industry
News → People Moves → New Job Openings → **Suggested Actions For This
Week** (last section, not first). For every item give: a one-line
summary, the source link, and a one-line "so what for MHR" note.

The closing actions section is the payoff — pull it from specific items
above, not generic advice. Cover at least these action types where the
week's findings support them:
- **Content to create** — a specific topic/format tied to a gap or
  emerging-topic item from the Content section.
- **Flag to sales** — a specific job opening, role change, or account
  signal from People Moves / Job Openings worth an account-team touch.
- **Competitive response** — something worth countering or matching from
  Competitor Activity.
- **Compliance/enablement** — anything from Legislation Watch that sales
  or customer success should know before customer conversations.

## 5. Deliver

Check `delivery.format` in the config:
- `artifact` (default): load the `artifact-design` skill, then publish
  the digest as a styled HTML Artifact (title it "MHR Market Intel — Week
  of <date>"). Favicon: 📡.
- `markdown`: write to `mhr-market-intel/reports/YYYY-MM-DD-digest.md`.

Always tell the user which lookback window was used and which categories
came back thin, so they know where the config needs more input (more
named accounts, MHR content sources, better competitor RSS feeds, etc.)
rather than assuming the pipeline is broken.
