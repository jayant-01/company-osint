# company-osint

Personal OSINT tool. Reads company names from a text file, finds each company's
website, crawls it for careers pages, ATS providers, job listings, contact
details and social links, and writes the results to CSV. The core (no-AI) crawl
also pulls a company description, firmographics from embedded schema.org data
(founding year, HQ location, headcount, logo), a tech-stack fingerprint, phone
numbers, and a per-company hiring breakdown by department. Optional local AI
enrichment can classify & score jobs against your profile and draft resume
bullets / cover letters / outreach messages.

## Install

Core (required):

    pip install -r requirements.txt

Optional AI (only for `--ai` / `--generate`):

    pip install -r requirements-ai.txt

## Usage

Edit `companies.txt` (one company name per line), then:

    python main.py                 # OSINT crawl only (fast, no heavy models)
    python main.py --ai            # + job classification & semantic scoring
    python main.py --generate 3    # + draft docs for top 3 jobs/company (implies --ai)

Options:

    -i / --input         input text file          (default: companies.txt)
    -o / --output-dir    output directory          (default: output/)
    --ai                 enable classification + scoring
    --profile            profile text file for AI  (default: profile.txt)
    --generate N         draft docs for top N jobs per company (implies --ai)
    -c / --concurrency   max companies at once      (default: 5)

## Output

    output/companies.csv   one row per company: website, description, founded,
                           hq_location, employee_count, tech_stack, ats, num_jobs,
                           hiring_breakdown, emails, phones, security_contact,
                           socials, rss_feed, logo, ...
    output/jobs.csv        one row per job: title, location, department,
                           employment_type, remote, posted, url (+ AI scores with --ai)
    output/generated/      resume/cover/outreach markdown (only with --generate)

## Notes

- Personal use only. Respect each site's robots.txt / terms of service and keep
  request volume low (tune `--concurrency`).
- The AI models run locally via HuggingFace and are downloaded on first use.
- Fetched pages are cached in `.cache/cache.db` to avoid re-downloading.
