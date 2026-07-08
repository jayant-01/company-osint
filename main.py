import argparse
import asyncio
import sys
from pathlib import Path

from rich.console import Console

from config import OUTPUT_DIR
from crawler.throttle import Throttle
from io_utils import (
    read_companies,
    load_profile,
    write_companies_csv,
    write_jobs_csv,
    write_generated_docs,
)
from pipeline import process_company

# aiohttp is happier on the selector event loop on Windows.
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

console = Console()


async def _run(companies, use_ai, profile, generate_top, concurrency):
    throttle = Throttle(rate=concurrency)
    tasks = [
        throttle.run(process_company(c, use_ai, profile, generate_top))
        for c in companies
    ]
    return await asyncio.gather(*tasks)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Company OSINT: company names (txt) -> CSV.",
    )
    parser.add_argument(
        "-i", "--input", default="companies.txt",
        help="Text file with one company name per line (default: companies.txt)",
    )
    parser.add_argument(
        "-o", "--output-dir", default=str(OUTPUT_DIR),
        help="Directory to write CSV output into (default: output/)",
    )
    parser.add_argument(
        "--ai", action="store_true",
        help="Enable AI job classification + scoring (needs requirements-ai.txt)",
    )
    parser.add_argument(
        "--profile", default="profile.txt",
        help="Profile text file used for AI scoring/generation (default: profile.txt)",
    )
    parser.add_argument(
        "--generate", type=int, default=0, metavar="N",
        help="Generate resume/cover/outreach docs for the top N jobs per company (implies --ai)",
    )
    parser.add_argument(
        "-c", "--concurrency", type=int, default=5,
        help="Max companies processed concurrently (default: 5)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    use_ai = args.ai or args.generate > 0

    companies = read_companies(args.input)
    if not companies:
        console.print(f"[red]No companies found in {args.input}[/red]")
        return

    profile = load_profile(args.profile) if use_ai else None

    console.print(
        f"[bold]Processing {len(companies)} companies[/bold] "
        f"(ai={'on' if use_ai else 'off'}, concurrency={args.concurrency})"
    )

    results = asyncio.run(
        _run(companies, use_ai, profile, args.generate, args.concurrency)
    )

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    companies_csv = out_dir / "companies.csv"
    jobs_csv = out_dir / "jobs.csv"

    n_companies = write_companies_csv(companies_csv, results)
    n_jobs = write_jobs_csv(jobs_csv, results)

    console.print(f"[green]Wrote[/green] {companies_csv} ({n_companies} companies)")
    console.print(f"[green]Wrote[/green] {jobs_csv} ({n_jobs} jobs)")

    if args.generate > 0:
        gen_dir = out_dir / "generated"
        n_docs = write_generated_docs(gen_dir, results)
        console.print(f"[green]Wrote[/green] {n_docs} generated docs -> {gen_dir}")


if __name__ == "__main__":
    main()
