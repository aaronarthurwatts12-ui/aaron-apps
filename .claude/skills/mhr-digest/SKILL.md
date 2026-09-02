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
(each with `sub_segments`), `competitors`, `target_accounts_source`,
`job_titles`, `keywords.include`/`exclude`, `legislation.topics`/`sources`,
`content_strategy` (`mhr_content_sources`, `topic_clusters`), and
`sales_cycle_timing` (bands + the start-engagement-by rule).

Also read `mhr-market-intel/config/target_accounts.csv` (named by
`target_accounts_source`) — 315 real accounts across all 7 sectors, with
real Industry, Employees, current HR/Payroll product+supplier, and
pre-computed `contract_end_date`/`start_engagement_by`/
`employee_count_band`. This is the primary source for account-specific
actions. `config/target_accounts_education_prospects.csv` (named by
`target_accounts_extended_source`) is a much larger (1,576-row),
Education-only, mostly-undated pool — use it for broader Education
content/people-moves targeting, not for renewal-timing actions.

Both lists are a floor, not a ceiling — don't limit findings to only
named accounts in them; a competitor or legislation item relevant to a
sector still belongs in the digest even when no specific account is
named in the source.

For every row in `target_accounts.csv` with a `start_engagement_by`
date, surface it as a "Flag to sales" action in one of two tiers:
- **Overdue** (`start_engagement_by` already in the past) — the
  highest-urgency tier; list every one, sorted by soonest
  `contract_end_date` first.
- **Upcoming** (`start_engagement_by` within the next ~6 months) —
  next tier down.
Rows with `has_past_renewal_date_on_file` true but no computed
`contract_end_date` (i.e. every renewal date on file is in the past) are
informational only — the CRM data may be stale rather than the contract
having lapsed; don't treat these as an action without saying so.

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
  1. *Content watch* — run the sitemap diff FIRST, then fill gaps with
     search:
     - **Primary source: `python3 scripts/sitemap_diff.py --json`** (run
       from the `mhr-market-intel/` directory; needs `pyyaml` — `pip
       install pyyaml` if the import fails). It fetches every
       competitor's `sitemap_url` from `config/targets.yaml`, diffs the
       URL set against last week's stored snapshot in
       `data/sitemap_snapshots/`, and overwrites the snapshot either
       way. Its `added` URLs are genuinely new pages — no currency
       guesswork needed, unlike search results. `status:
       "first_snapshot"` means there's nothing to diff yet this run
       (report the page count, not fabricated "new" content). A
       competitor with `status: "no_sitemap_configured"`,
       `"fetch_failed"`, or `"empty_or_blocked"` has no working sitemap
       (commonly a Cloudflare/Akamai bot challenge — confirmed for
       Civica and Unit4 as of Sep 2026; don't try to work around a real
       bot-protection challenge, that's evading a deliberate access
       control) — fall back to search for that competitor only.
     - **Fallback (competitors without a working sitemap, or to catch
       non-blog content the sitemap wouldn't distinguish as "new," like
       an updated existing page)**: `"<competitor>" blog OR case study
       OR webinar`, plus general searches per sector/topic cluster. Run
       this for every competitor lacking sitemap coverage, not just the
       one or two with the most obvious hits. Include a competitor only
       when a real, distinct piece of content with an actual URL was
       found for it that run; say nothing for a competitor with no fresh
       content rather than padding the section.
       **Currency check:** a page ranking in search isn't necessarily
       new — blogs and evergreen resource pages stay indexed for years.
       Before presenting something as "content watch" (implicitly this
       week's activity), check for a visible publish/updated date (on
       the page itself, in the search snippet, or via `WebFetch`/`curl`
       if neither shows one) and confirm it falls within roughly the
       last 4-6 weeks. An older but genuinely relevant page can still be
       worth flagging — but say so explicitly (e.g. "an existing page,
       not new this week") rather than implying it's fresh. This
       environment's network policy was opened to general outbound
       access on 2 Sep 2026 (previously all of `WebFetch` and Bash
       `curl` were blocked for external domains) — if fetches are
       failing again, that policy may have reverted; fall back to the
       "currently live content" phrasing from before rather than
       assuming a domain-specific block.
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

**E. People moves** — not limited to named `target_accounts.csv` rows:
per `config/targets.yaml`'s `icp` block, any organisation in one of the
seven sectors with roughly `icp.min_employees`+ employees is in scope,
named account or not (a district council or small trust rarely clears
that bar; a county council, NHS trust, police force or multi-academy
trust usually does). For each job title in the config (including the
open-ended "any digital transformation title" entry — read it broadly),
combine with sector terms as well as account terms, e.g. `"appointed"
"HR Director" council 2026` alongside `"appointed" "HR Director" NHS
trust 2026`. Note: there is no LinkedIn API access here — personal OAuth
only exposes the authenticated user's own profile, not other people's
job changes, and third-party scraping violates LinkedIn's ToS. This
category relies on what search engines surface (press releases,
council/trust news pages, publicly indexed posts) and will always be
thin without a compliant B2B data provider (see README "Known
limitations") — but broadening past the named list should still surface
more than searching only 315 accounts by name.

**F. New job openings** — same broadened scope as People Moves: search
official public-sector job boards directly for the configured job
titles across LGjobs (local government), NHS Jobs, Civil Service Jobs
(gov.uk), charity job boards, and sector-wide searches (e.g. `"Head of
Payroll" NHS trust`) — not just each named target account's own careers
page. A posting for one of the configured titles at any ICP-fitting org
is itself a signal (budget + appetite for change), whether or not that
org is on the named list — name the organisation plainly in the listing
(no separate note on named-vs-not; the org name is enough for sales to
check against the CRM themselves).

**Currency check — mandatory before including any job listing.** A
search result's presence doesn't mean the vacancy is still open; job
board pages stay indexed and searchable long after they close. For
every candidate listing:
- Note the closing date if the listing states one, and drop it if that
  date is before the digest's run date (today). A "starts"/"started"
  date instead of a closing date means the role has already been
  filled — that's a people-move signal at best, never a job opening.
- If a search snippet doesn't show a closing date, `WebFetch` the
  listing page itself and check for it or for explicit "this vacancy
  has closed"/"applications no longer accepted" text before including
  it. If the page is unreachable and status can't be confirmed, leave
  the listing out rather than guess it's still open.
- Only search results that are themselves fresh (posted within roughly
  the last 4-6 weeks, or with an explicit future closing date) belong
  in this section — don't reuse a listing from a prior week's run
  without re-checking it, since it may have closed since.

## 3. Filter for relevance

Drop anything that isn't clearly tied to: a configured competitor, a
configured target account, one of the four sectors, a configured
keyword/job title, or a legislation topic. When in doubt, cut it — a
short high-signal digest beats a long noisy one.

## 4. Write the digest

Use `mhr-market-intel/templates/digest_template.md` as the section
structure: Industry News → Competitor Activity → Content → Legislation
Watch → People Moves → New Job Openings → **Suggested Actions For This
Week** (last section, not first). For every item give: a one-line
summary, a real clickable link to its source (the actual article/listing/
document URL turned up by the search or fetch — never just the bare
domain name as text), and a one-line "so what for MHR" note. This
applies in both delivery formats below — the artifact's prior issues
under-did this (source domain shown as plain text, not a link); don't
repeat that.

Don't include any commentary about the digest's own production in the
digest itself — no "corrected this run," "N listings removed since last
issue," "previously reported as X," "thin this run," "widened this run
to...," notes on why a section is short, or caveats about this
environment's network/fetch access. None of that is something happening
in the market this week; it describes the process, not the findings, and
doesn't belong in front of the reader in any form — not as a standalone
note, not folded inline into an entry's body or "so what." Apply
currency checks, drop stale items, fix data errors, and widen or narrow
search scope silently; report each item on its own merits as if it were
the only version of the digest that ever existed. If something about
this run genuinely needs to reach Aaron (a real data correction, a
section that came back thin, a network/access problem), say it in your
chat reply after generating the digest — never inside the digest content
itself.

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

Check `delivery.formats` in the config — do all of the ones listed:
- `artifact`: load the `artifact-design` skill, then publish the digest
  as a styled HTML Artifact titled "Public Sector Pulse — Week of <date
  range>". Favicon: 📡. Design system: paper/teal/warm-flag palette,
  Fraunces/Public Sans/IBM Plex Mono type, sector chips for
  Education/Local & Central Gov/Charity & Housing/Emergency &
  Military/Healthcare — match prior issues rather than reinventing it
  each week.
- `markdown`: write to `mhr-market-intel/reports/YYYY-MM-DD-digest.md`.
- `email`: read `delivery.email` for the recipient, subject template, and
  the `template`/`brand` file paths (`mhr-market-intel/templates
  /email_template.html`, `mhr-market-intel/config/brand.yaml`). Build the
  HTML email by reusing that template's shell (header band, gradient
  accent bars, footer) and repeating its block patterns (section header,
  entry, so-what callout, neutral note, data table, action item) for
  that week's actual content — do not literally find/replace into the
  template file, its placeholder text is illustrative of the pattern,
  not real markup to fill in. Keep every style inline (no `<style>`
  block for layout) since this renders in email clients. Send via
  `mcp__Gmail__send_message` (load its schema via ToolSearch if not
  already available) with `to` = `delivery.email.recipient`, `subject` =
  the subject template with `{date}` filled in (e.g. "Public Sector
  Weekly Digest 7 September 2026"), `htmlBody` = the branded HTML, and
  `body` = a short plain-text fallback summarizing the top findings and
  the Suggested Actions list. If the Gmail connector isn't available in
  the firing session, say so clearly rather than silently skipping the
  email.

Always tell the user which lookback window was used and which categories
came back thin, so they know where the config needs more input (more
named accounts, MHR content sources, better competitor RSS feeds, etc.)
rather than assuming the pipeline is broken.
