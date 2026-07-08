---
name: company-osint
description: Architecture reference and guardrails for the company-osint project (read company names from companies.txt -> OSINT crawl -> companies.csv + jobs.csv, with optional local AI enrichment). Use this whenever working anywhere in this repo to stay aligned with the intended pipeline, module map, and conventions, and to avoid scope drift.
---

# company-osint — working guide

Personal OSINT tool. **Input:** company names from a text file. **Output:** CSV.
Keep every change serving that single sentence.

## The one true data contract

- Input: `companies.txt` — one company name per line, `#` comments, blanks ignored.
- Output:
  - `output/companies.csv` — **one row per company**.
  - `output/jobs.csv` — **one row per job found**.
  - `output/generated/*.md` — only when `--generate N` is passed.
- Profile for AI: `profile.txt` (whole file = the profile; `#` lines dropped).

Do not change the input format or the two-CSV output shape without the user asking.

## Pipeline flow (per company)

`main.py` -> `pipeline.process_company()`:

1. `crawler.search.search_company(name)` — DuckDuckGo, returns candidate URLs
   (filtered by `crawler.constants.BLACKLIST_DOMAINS`). Takes `websites[0]`.
2. `crawler.downloader.fetch(url)` — async aiohttp GET, SQLite-cached
   (`crawler.cache`). Returns `{"url", "html"}` or `None`.
3. `crawler.intelligence.analyze_site(url, html)` — extracts links, ATS
   (`crawler.ats`), emails (`crawler.email`), socials (`crawler.social`),
   careers/intern/blog links, and jobs (`crawler.ats_router` ->
   `crawler.job_extractor` greenhouse/lever APIs). Returns a dict.
4. `pipeline` builds a `models.company.Company` + list of `models.job.Job`.
5. If `--ai`: `ai.pipeline.score_jobs()` fills role_type/confidence, match_score,
   company_score, final_score and sorts. If `--generate N`:
   `ai.pipeline.generate_documents()` for the top N jobs.
6. `io_utils` writes the CSVs (+ generated docs).

## Invariants — do not break these

- **AI is optional and off by default.** The core crawler must run with only
  `requirements.txt` installed (no torch/transformers). Enforce this by:
  - importing `ai.*` **lazily**, inside `if use_ai:` branches only;
  - keeping model loads lazy inside `ai/hf_client.py`, `ai/scoring.py`,
    `ai/llm.py` (module-level import must never touch transformers/torch/
    sentence-transformers). Never add a top-level `from ai...` to a `crawler/`
    module (that is the bug that used to force torch on the core path).
- **Concurrency:** synchronous work (`search_company`, `analyze_site`,
  `score_jobs`, `generate_documents`) runs via `asyncio.to_thread`; companies
  are throttled with `crawler.throttle.Throttle` (rate = `--concurrency`).
- **Failure is non-fatal per company:** search/fetch return `[]`/`None` on error;
  one bad company must not crash the run.
- **CSV schema is fixed** (`io_utils.COMPANY_COLUMNS` / `JOB_COLUMNS`). AI columns
  stay blank when scoring did not run. Use the stdlib `csv` module (quoting).

## Models

- `models.company.Company` — name, website, career_page, ats, github, linkedin,
  engineering_blog, internships, emails, socials, job_pages.
- `models.job.Job` — title, company, location, url, description, role_type,
  role_confidence, match_score, company_score, final_score.

## AI model choices (already fixed — keep them)

- Classification: `zero-shot-classification`, `facebook/bart-large-mnli`.
- Scoring: sentence-transformers `all-MiniLM-L6-v2`, cosine similarity * 100.
- Generation: `text2text-generation`, `google/flan-t5-base` (flan-t5 is seq2seq).

## Testing

Do **not** run/test in this environment. The user tests on a separate Windows
machine. Write code; do not execute the pipeline here. Keep the Windows selector
event-loop guard in `main.py`.

## Scope discipline (avoid drift)

In scope: reliable crawl, clean CSVs, optional local AI enrichment, small quality
fixes on the existing modules. Out of scope unless asked: new data sources,
databases, web UI, external/paid APIs, proxies, or anti-bot evasion. It is a
personal tool — respect robots.txt / ToS and keep request volume low.
