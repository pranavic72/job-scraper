# ============================================================
#  fetch_jobs.py — Run this script to fetch LinkedIn jobs
# ============================================================
#
#  Usage:
#    python fetch_jobs.py
#
#  Output: linkedin_jobs.xlsx in this folder
# ============================================================

from scraper import scrape_linkedin
from sheets import write_jobs_to_excel
from config import SEARCH_QUERIES, LOCATION, DATE_FILTER


def main():
    print("\n🚀  LinkedIn Job Agent")
    print(f"    Queries  : {len(SEARCH_QUERIES)}")
    print(f"    Location : {LOCATION}")
    print(f"    Filter   : {DATE_FILTER}\n")

    jobs = scrape_linkedin(
        queries=SEARCH_QUERIES,
        location=LOCATION,
        date_filter=DATE_FILTER,
    )

    if not jobs:
        print("\n📭  No jobs found. Try adjusting your search queries in config.py")
        return

    print(f"\n📊  {len(jobs)} unique job(s) collected. Writing to Excel...\n")
    write_jobs_to_excel(jobs)
    print("\n🎉  Done! Open linkedin_jobs.xlsx to see your results.")


if __name__ == "__main__":
    main()
