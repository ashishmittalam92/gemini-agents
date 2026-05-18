# 1. Install libraries
pip install -r installation.txt

**Note:** If above command failed then run following command

### Create and Activate a Virtual Environment

### 1. Create a local hidden virtual environment folder named '.venv'
python3 -m venv .venv

### 2. Activate the virtual environment
source .venv/bin/activate
**Note:** Once activated, you will see (.venv) prepend your terminal prompt line, confirming you are safely isolated.

### 3. Upgrade pip inside your virtual environment first
pip install --upgrade pip

### 4. Install libraries
pip install -r installation.txt

## Finalize the playwright headless browser installation inside the venv
playwright install chromium

# 2. Set Up Your Gemini API Key
To use the AI engine for free, you need an API key from Google AI Studio.

Go to Google AI Studio and sign in with your Google account.

Click Get API key and create a key in a new or existing project.

Set it as an environment variable in your terminal so the script can read it automatically:

**Windows (Command Prompt):** set GEMINI_API_KEY=your_api_key_here

**Windows (PowerShell):** $env:GEMINI_API_KEY="your_api_key_here"

**Mac/Linux:** export GEMINI_API_KEY="your_api_key_here"

# 3. Configuration & Personalization (config.py)
## 1. Define Your Candidate Profile (USER_PROFILE)
Update the placeholders inside the multi-line string block to accurately represent your background and career goals.

Total Experience: Enter your total professional engineering years.

Current Role: Your current company and level

Target Roles: The levels you are aiming for (e.g., Senior, Lead, Staff, Principal, or Architect).

Tech Stack Mastery: List your main technical pillars (e.g., Java, Distributed Systems, High-Scale Architectures, Go).

**💡 Pro-Tip:** The cleaner and more detailed your tech stack description is, the more accurate Gemini's strict score_out_of_10 metric will be.

## 2. Add Target Job Board Search URLs (TARGET_URLS)
Paste the pre-filtered URLs you want the pipeline to scrape inside the TARGET_URLS array. You can pull these directly from your browser's address bar after setting up your search filters on LinkedIn and Indeed.

Python
TARGET_URLS = [ 
        // LinkedIn url
        // Indeed url
]

**LinkedIn Tip:** Ensure you apply your desired filters (e.g., Past 24 hours / Under 20 applicants) before copying the link.

**Indeed Tip:** Use the date filter (e.g., &fromage=1 for the past day) to keep your results fresh.

**Note:** You can use any genAI to provide TARGET_URLS and USER_PROFILE based on your resume, linkedIn profile and additional information you provide to them.
