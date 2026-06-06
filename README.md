# LinkedIn Job Agent 🔍

Automatically fetches Working Student job posts from LinkedIn (last 24h, Germany) and saves them to a local Excel file with a status tracker.

---

## Features

- Searches multiple queries in one run (AI, Frontend, Backend, Werkstudent, etc.)
- Filters by Germany and last 24 hours
- Saves results to `linkedin_jobs.xlsx` with clickable links
- Status dropdown per job: Submitted / Rejected / Interviewing
- Duplicate detection — re-running never adds the same job twice

---

## Project Structure

```
job-scraper/
├── fetch_jobs.py       ← run this
├── scraper.py          ← LinkedIn scraping logic (Selenium)
├── sheets.py           ← Excel output logic
├── config.py           ← edit search queries here
├── requirements.txt    ← Python dependencies
├── .env                ← your LinkedIn credentials (never commit this)
└── .gitignore          ← keeps credentials out of GitHub
```

---

## Setup (one time)

### 1. Clone the repo

```bash
git clone https://github.com/your-username/job-scraper.git
cd job-scraper
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create a `.env` file

Create a file called `.env` in the project folder:

```
LINKEDIN_EMAIL=your_email@gmail.com
LINKEDIN_PASSWORD=your_password
```

> ⚠️ Never commit this file. It is already listed in `.gitignore`.

---

## Running

```bash
python fetch_jobs.py
```

Chrome will open, log into LinkedIn automatically, run through all search queries, and save results to `linkedin_jobs.xlsx` in the project folder.

---

## Output

| Company | Role | Link | Status | Date Found | Location |
|---------|------|------|--------|------------|----------|
| Siemens | Working Student AI | linkedin.com/... | _(dropdown)_ | 06.06.2026 | Munich |

The **Status** column has a dropdown — click any cell in that column to mark a job as **Submitted**, **Rejected**, or **Interviewing**.

---

## Customising Searches

Edit `config.py` to add or remove search queries:

```python
SEARCH_QUERIES = [
    "Working Student AI",
    "Working Student Frontend",
    "Werkstudent Backend",
    # add more here...
]
```

Change the date filter:

```python
DATE_FILTER = "past_24_hours"  # or "past_week" / "past_month"
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| LinkedIn login fails | Check your `.env` credentials. If LinkedIn shows a captcha, complete it manually in the browser window. |
| No jobs found | LinkedIn may have updated its HTML. Find `# <-- SELECTOR` comments in `scraper.py` and update the CSS selectors. |
| ChromeDriver error | Run `pip install --upgrade webdriver-manager` |
| Dropdown not visible in Excel | Click a cell in the Status column — the arrow appears on selection. |

---

## Pushing Updates to GitHub

```bash
git add .
git commit -m "your message here"
git push
```

---

## .gitignore

Make sure your repo has a `.gitignore` that includes:

```
.env
linkedin_jobs.xlsx
__pycache__/
*.pyc
```
