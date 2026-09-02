# config.py
import datetime

CURRENT_DATE_STR = datetime.datetime.now().strftime("%Y-%m-%d")

# Ensure your user profile text block is declared cleanly above
USER_PROFILE = """
- Today's System Date: {CURRENT_DATE_STR}
- Total Experience: 11+ years in Software Engineering
- Current Role: SDE 2 / Backend Architect at a top-tier tech firm
- Target Roles: Senior Software Engineer (SDE 3), Staff Engineer, Tech Lead, Principal Engineer (L6/L7 equivalent)
- Tech Stack Mastery: Java, Core Distributed Systems, High-Availability Frameworks, Microservices, Kafka
- Market Focus: India (Bangalore, Hyderabad, Pune, Gurgaon, or Remote)

- EVALUATION & SCORING CRITERIA:
  * Grade the 'score_out_of_10' purely on technical fit and seniority scale.
  * High Scores (8-10/10): Target robust backend architectural roles, distributed systems design, tech lead positions, or SDE-3+ scopes.
  * Low Scores (1-5/10): Penalize entry-level (SDE 1), frontend-heavy, or non-technical management roles.

- STRICT TIME FILTERING:
  * Only include jobs published within the last 24 hours relative to {CURRENT_DATE_STR}.
  * Reject any job posted 2+ days ago or missing publication timeframe.

- COMPENSATION ESTIMATION INSTRUCTIONS:
  * For the 'estimated_total_comp' and 'comp_breakdown' fields, utilize internal market knowledge of the Indian tech sector to predict the compensation package based on company tier and seniority level.
  * Do NOT let a low or uncertain compensation estimate lower the technical 'score_out_of_10'.
"""

# Direct Board URLs (for scrapers like Playwright / Selenium with active sessions)
# Add your target corporate career boards here!
# Pre-filtered aggregate search streams for Senior/Staff roles in India
TARGET_URLS = [
    # LinkedIn: 24h filter (f_TPR=r86400) sorted by most recent (sortBy=DD)
    # 1. LinkedIn Jobs: Java + Distributed Systems, India, Senior/Staff Level (Filtered over the last 24 hours)
    "https://www.linkedin.com/jobs/search/?keywords=Java%20Distributed%20Systems&location=India&f_TPR=r86400&sortBy=DD",

    # 2. LinkedIn Jobs: Software Architect / Tech Lead, India (Filtered over the last 24 hours)
    "https://www.linkedin.com/jobs/search/?keywords=Software%20Architect%20Java&location=India&f_TPR=r86400&sortBy=DD",

    # Indeed India: 1 day filter (fromage=1) sorted by date (sort=date)
    # 3. Indeed India: Senior Software Engineer / Staff Engineer queries
    "https://in.indeed.com/jobs?q=Senior+Software+Engineer+Java+Distributed&l=India&fromage=1&sort=date"
]

# Search Engine Queries (for Google Grounding or Google Custom Search API)
SEARCH_QUERIES = [
    'site:linkedin.com/jobs "Java" "Distributed Systems" "India"',
    'site:linkedin.com/jobs "Software Architect" "Java" "India"',
    'site:in.indeed.com/viewjob "Senior Software Engineer" "Java" "India"',
    'site:naukri.com "Staff Software Engineer" "Java" "India"'
]

# The corrected Schema layout assignment block
RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "jobs": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "company": {"type": "STRING"},
                    "job_title": {"type": "STRING"},
                    "score_out_of_10": {"type": "INTEGER"},
                    "posted_date": {
                        "type": "STRING",
                        "description": "The exact date the job was published in YYYY-MM-DD format. If the listing states a relative time (e.g., '2 days ago'), calculate the explicit date relative to the current date and return that string."
                    },
                    "location": {"type": "STRING"},
                    "workplace_policy": {
                        "type": "STRING", 
                        "description": "Must be exactly one of these classifications: 'Remote', 'Hybrid', 'WFO (Office)', or 'Not Specified'"
                    },
                    "job_url": {
                        "type": "STRING",
                        "description": "The EXACT source URL if present in the text. If not explicitly present or if it is a relative link, construct a Google search URL in this format: 'https://www.google.com/search?q=COMPANY+JOB_TITLE+careers'."
                    },
                    "estimated_total_comp": {
                        "type": "STRING",
                        "description": "Predicted total annual compensation package range for India (e.g., '₹1.3 - ₹1.6 CR'). Based on company tier and role seniority."
                    },
                    "comp_breakdown": {
                        "type": "STRING",
                        "description": "Estimated distribution of the compensation package. Example: 'Base: ₹55-65L | RSUs/Equity: ₹60-80L | Bonus: ₹10L'"
                    },
                    "justification": {"type": "STRING"},
                    "linkedin_search_keywords": {"type": "STRING"}
                },
                "required": [
                    "company", "job_title", "score_out_of_10", "posted_date", "location",
                    "workplace_policy", "job_url", "estimated_total_comp", "comp_breakdown", "justification", "linkedin_search_keywords"
                ]
            }
        }
    }
}
