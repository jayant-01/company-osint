import asyncio
from ai.pipeline import enrich
from rich.pretty import data

from crawler.search import search_company
from crawler.downloader import fetch
from crawler.intelligence import analyze_site
from crawler.throttle import Throttle

throttle = Throttle(rate=5)


async def process(company):

    print("\n", "=" * 80)
    print("Company:", company)

    websites = search_company(company)

    if not websites:

        return

    website = websites[0]

    print("Website:", website)

    page = await throttle.run(fetch(website))

    if not page:

        return

    data = analyze_site(page["url"], page["html"])
    print("\n=== JOB INTELLIGENCE ===\n")
    print("Careers pages:", len(data["careers_pages"]))
    print("ATS:", data["ats_detected"])
    print("Jobs found:", len(data["jobs_found"]))
    for job in data["jobs_found"][:5]:
        print("-", job["title"])
        print(" ", job.get("url"))

def output_results(company_data, jobs):

    ranked = enrich(company_data, jobs, USER_PROFILE)

    print("\n🔥 TOP AI-GENERATED JOBS:\n")

    for job in ranked[:5]:

        job = enrich_with_ai_outputs(job, USER_PROFILE)

        print("=" * 60)
        print(job.title)
        print("Score:", job.final_score)

        print("\n--- Resume Bullets ---")
        print(job.resume_bullets)

        print("\n--- Cover Letter ---")
        print(job.cover_letter)

        print("\n--- Outreach Message ---")
        print(job.recruiter_message)

async def main():

    companies = [
        "J P Morgan",
        "CoinSwitch",
        "Binance",
        "Stripe",
        "Zomato",
        "Razorpay"
    ]
    await asyncio.gather(*[process(c) for c in companies])


asyncio.run(main())