# config.py

# Ensure your user profile text block is declared cleanly above
USER_PROFILE = """
- Total Experience: ...
- Current Role: ...
- Target Roles: ...
- Tech Stack Mastery: ...
- Market Focus: India (Bangalore, Hyderabad, Pune, Gurgaon, or Remote)

- EVALUATION & SCORING CRITERIA:
  * Grade the 'score_out_of_10' purely on technical fit and seniority scale.
  * High Scores (8-10/10): Target robust backend architectural roles, distributed systems design, tech lead positions.
  * Low Scores (1-5/10): Penalize entry-level (SDE 1), frontend-heavy, or non-technical management roles.

- COMPENSATION ESTIMATION INSTRUCTIONS:
  * For the 'estimated_total_comp' and 'comp_breakdown' fields, utilize your internal market knowledge of the Indian tech sector to predict the compensation package based on company tier and seniority level.
  * Do NOT let a low or uncertain compensation estimate lower the technical 'score_out_of_10'. Treat the compensation breakdown strictly as a descriptive informational field.
"""

# Add your target corporate career boards here!
# Pre-filtered aggregate search streams for Senior/Staff roles in India
TARGET_URLS = [
    ...
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
                        "description": "The exact date the job was published in YYYY-MM-DD format. If the listing states a relative time (e.g., '2 days ago'), calculate the explicit date relative to the current date (May 2026) and return that string."
                    },
                    "location": {"type": "STRING"},
                    "workplace_policy": {
                        "type": "STRING", 
                        "description": "Must be exactly one of these classifications: 'Remote', 'Hybrid', 'WFO (Office)', or 'Not Specified'"
                    },
                    "job_url": {
                        "type": "STRING",
                        "description": "The specific URL link to apply for this job, or N/A if not explicitly visible."
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
