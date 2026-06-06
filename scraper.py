# ============================================================
#  scraper.py — LinkedIn scraping logic using Selenium
# ============================================================
#
#  ⚠️  SELECTOR NOTICE
#  If LinkedIn updates its HTML, job cards may stop being found.
#  All CSS selectors are marked with # <-- SELECTOR so you can
#  quickly find and update them if needed.
# ============================================================

import time
import random
import urllib.parse
import os
from dataclasses import dataclass, field
from datetime import date

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    StaleElementReferenceException,
)
from webdriver_manager.chrome import ChromeDriverManager

from config import MIN_DELAY, MAX_DELAY, MAX_JOBS_PER_QUERY

load_dotenv()


# ── Data model ───────────────────────────────────────────────

@dataclass
class Job:
    company: str
    role: str
    location: str
    link: str
    date_found: str = field(default_factory=lambda: date.today().strftime("%d.%m.%Y"))

    def __eq__(self, other):
        return isinstance(other, Job) and self.link == other.link

    def __hash__(self):
        return hash(self.link)


# ── LinkedIn URL builder ─────────────────────────────────────

DATE_FILTER_MAP = {
    "past_24_hours": "r86400",
    "past_week":     "r604800",
    "past_month":    "r2592000",
}

def build_search_url(query: str, location: str, date_filter: str) -> str:
    f_TPR = DATE_FILTER_MAP.get(date_filter, "r86400")
    params = {
        "keywords": query,
        "location": location,
        "f_TPR":    f_TPR,
        "f_JT":     "P",
    }
    base = "https://www.linkedin.com/jobs/search/?"
    return base + urllib.parse.urlencode(params)


# ── Browser setup ────────────────────────────────────────────

def create_driver() -> webdriver.Chrome:
    profile_dir = os.path.join(
        os.path.expanduser("~"),
        "AppData", "Local", "selenium-linkedin-profile"
    )
    os.makedirs(profile_dir, exist_ok=True)

    options = Options()
    options.add_argument(f"--user-data-dir={profile_dir}")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--window-size=1280,900")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"},
    )

    return driver


# ── Login ────────────────────────────────────────────────────

def login_to_linkedin(driver):
    email    = os.getenv("LINKEDIN_EMAIL")
    password = os.getenv("LINKEDIN_PASSWORD")

    if not email or not password:
        raise ValueError(
            "LINKEDIN_EMAIL and LINKEDIN_PASSWORD must be set in your .env file"
        )

    print("🔐  Logging into LinkedIn...")
    driver.get("https://www.linkedin.com/login")
    time.sleep(3)

    # Type email
    email_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "username"))  # <-- SELECTOR
    )
    email_field.clear()
    for char in email:
        email_field.send_keys(char)
        time.sleep(random.uniform(0.05, 0.15))

    time.sleep(1)

    # Type password
    password_field = driver.find_element(By.ID, "password")  # <-- SELECTOR
    password_field.clear()
    for char in password:
        password_field.send_keys(char)
        time.sleep(random.uniform(0.05, 0.15))

    time.sleep(1)

    # Click sign in
    password_field.send_keys(Keys.RETURN)

    # Wait for login to complete
    time.sleep(5)

    current = driver.current_url
    if "login" in current or "authwall" in current or "checkpoint" in current:
        print("\n⛔  Login may have failed or LinkedIn is asking for verification.")
        print("    Please complete any verification in the browser window,")
        print("    then press ENTER here to continue.")
        input()
    else:
        print("✅  Logged in successfully.\n")


# ── Helpers ──────────────────────────────────────────────────

def human_delay():
    time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))


def scroll_to_bottom(driver, pause: float = 1.5):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollBy(0, 600);")
        time.sleep(pause)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


# ── Job extraction ───────────────────────────────────────────

def extract_jobs_from_page(driver) -> list[Job]:
    jobs = []

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "ul.jobs-search__results-list li")  # <-- SELECTOR
            )
        )
    except TimeoutException:
        print("    ⚠️  No job cards found on this page (timeout). Skipping.")
        return jobs

    scroll_to_bottom(driver)

    cards = driver.find_elements(
        By.CSS_SELECTOR, "ul.jobs-search__results-list li"  # <-- SELECTOR
    )

    print(f"    Found {len(cards)} card(s) on page.")

    for card in cards[:MAX_JOBS_PER_QUERY]:
        try:
            role = card.find_element(
                By.CSS_SELECTOR, "h3.base-search-card__title"  # <-- SELECTOR
            ).text.strip()

            company = card.find_element(
                By.CSS_SELECTOR, "h4.base-search-card__subtitle"  # <-- SELECTOR
            ).text.strip()

            location = card.find_element(
                By.CSS_SELECTOR, "span.job-search-card__location"  # <-- SELECTOR
            ).text.strip()

            raw_link = card.find_element(
                By.CSS_SELECTOR, "a.base-card__full-link"  # <-- SELECTOR
            ).get_attribute("href")
            link = raw_link.split("?")[0]

            if role and company and link:
                jobs.append(Job(company=company, role=role, location=location, link=link))

        except (NoSuchElementException, StaleElementReferenceException):
            continue

    return jobs


# ── Main scrape function ─────────────────────────────────────

def scrape_linkedin(
    queries: list[str],
    location: str,
    date_filter: str,
    chrome_profile_path: str = None,
) -> list[Job]:
    driver = create_driver()
    all_jobs: list[Job] = []
    seen_links: set[str] = set()

    try:
        # Check if already logged in
        driver.get("https://www.linkedin.com/jobs")
        time.sleep(3)

        print(f"   Current URL: {driver.current_url}")
        if "authwall" in driver.current_url or "login" in driver.current_url or "checkpoint" in driver.current_url:
            login_to_linkedin(driver)

        print("Starting job search...\n")

        for query in queries:
            url = build_search_url(query, location, date_filter)
            print(f"\n🔍 Searching: '{query}' in {location}")

            driver.get(url)
            human_delay()

            if "authwall" in driver.current_url or "login" in driver.current_url:
                print("\n⛔  Redirected to login unexpectedly. Stopping.")
                break

            jobs = extract_jobs_from_page(driver)

            new_count = 0
            for job in jobs:
                if job.link not in seen_links:
                    seen_links.add(job.link)
                    all_jobs.append(job)
                    new_count += 1

            print(f"   ✅  {new_count} new job(s) collected (query total: {len(jobs)})")
            human_delay()

    finally:
        driver.quit()

    return all_jobs