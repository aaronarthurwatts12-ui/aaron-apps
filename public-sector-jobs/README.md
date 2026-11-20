# Public sector HR & payroll buyer roles

A weekly scan of UK public sector and not-for-profit job boards for roles involved in buying HR and payroll software (HR/People, Payroll, Digital/IT, Transformation, Finance, Procurement and CEO). It emails a report grouped by **NFP / Education / Gov / Other (incl. NHS)**, with a link to each post, plus a **People moves** section built from appointment news.

## How it works
1. **Scrape** (`scanner/sources/`): NHS Jobs, jobs.ac.uk, Teaching Vacancies (DfE API), myjobscotland, goodmoves, WM Jobs, Inside Housing Jobs, THE Jobs, plus Indeed, Totaljobs and LinkedIn job-alert emails read from a Gmail inbox.
2. **Match titles** against `config/roles.yaml`. Each organisation size band has its own seniority rule:
   - 100–400 staff: any role in the function list
   - 400–1,500: Head of / Director / Lead level
   - 1,500+: C-suite and Director level, plus heads of HR, payroll, digital, procurement and transformation
3. **Classify organisations** by sector and size using `data/org_cache.json`. Edit this file to correct any organisation. Organisations not in the cache are classified by Claude and saved there. Organisations under 100 staff, private companies and non-UK employers are dropped.
4. **Dedupe** against `data/seen.json`, so each role is only reported once.
5. **Email** the HTML report.

## Run locally
```
pip install -r requirements.txt
python -m scanner.main --dry-run        # writes output/report.html
```

## GitHub secrets (Settings → Secrets → Actions)
| Secret | What |
|---|---|
| `ANTHROPIC_API_KEY` | classifies new organisations |
| `SMTP_USER` / `SMTP_PASSWORD` | Gmail address + app password that sends the email |
| `REPORT_TO` | recipient(s), comma-separated |
| `ALERTS_IMAP_USER` / `ALERTS_IMAP_PASSWORD` | Gmail inbox that receives the Indeed / Totaljobs / LinkedIn alerts (app password) |

The schedule in `.github/workflows/public-sector-jobs.yml` is switched off until the report is approved.
