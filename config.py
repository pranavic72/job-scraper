# ============================================================
#  config.py — Edit this file to customise your job search
# ============================================================

# Search queries the script will loop through
# Add or remove entries freely — one search per line
SEARCH_QUERIES = [
    "Working Student AI",
    "Working Student Machine Learning",
    "Working Student Software Development",
    "Working Student Frontend",
    "Working Student Backend",
    "Werkstudent Softwareentwicklung",
    "Werkstudent Frontend",
    "Werkstudent Backend",
    "Werkstudent KI",
]

# Location filter applied to every search
LOCATION = "Germany"

# How far back to look (LinkedIn filter options)
# Options: "past_24_hours" | "past_week" | "past_month"
DATE_FILTER = "past_24_hours"

# Seconds to wait between page loads (random value between these two)
# Keep these at 2–4 to mimic human browsing speed
MIN_DELAY = 2
MAX_DELAY = 4

# Max job cards to collect per search query
# LinkedIn shows ~25 per page; increase if you want to scroll further
MAX_JOBS_PER_QUERY = 25
