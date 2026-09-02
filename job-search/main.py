# main.py
import sys
import os
import json
import config
import urllib.parse

from scraper import scrape_target_url
from agent_engine import JobAgent
from linkedin_finder import find_linkedin_targets
from local_excel_manager import append_to_local_sheet
from gemini_client import get_gemini_client, generate_content_with_retry
from google.genai import types

from config import TARGET_URLS

def job_search_linkedin():
    print("🚀 Initializing Local Job Hunt Agent Pipeline...")
    
    if not os.environ.get("GEMINI_API_KEY"):
        print("❌ Error: GEMINI_API_KEY environment variable not found.")
        print("Please export it in your terminal: export GEMINI_API_KEY='your_key'")
        sys.exit(1)
        
    agent = JobAgent()
    
    for url in TARGET_URLS:
        # 1. Fetch sanitized, token-compressed plain text via your modular scraper
        clean_text_payload = scrape_target_url(url)
        
        if not clean_text_payload:
            print("⚠️ No readable text captured. Skipping source target.")
            continue
            
        print("🧠 Evaluating data matches with Gemini Engine...")
        
        try:
            # 2. Evaluate using the profile-injected Gemini LLM layer
            agent_response = agent.evaluate_scraped_data(clean_text_payload)
            
            if not agent_response or not agent_response.text:
                print("⚠️ Received empty analysis block from Gemini. Skipping entry array.")
                continue
                
            cleaned_json_string = agent_response.text.strip()
            cleaned_json_string = cleaned_json_string.replace("```json", "").replace("```", "").strip()
                
            parsed_payload = json.loads(cleaned_json_string)

            # Extract the nested 'jobs' array from your new schema blueprint safely
            jobs_found = parsed_payload.get("jobs", [])
            
            if not jobs_found or len(jobs_found) == 0:
                print("ℹ️ No matched vacancies extracted matching target stack properties.")
                continue
                
            print(f"📋 Extracted {len(jobs_found)} potential roles. Committing to sorted database structure...")
            for job in jobs_found:
                if not job.get("company") or not job.get("job_title"):
                    continue
                    
                print(f"   🎯 Processing: {job['job_title']} at {job['company']} (Score: {job.get('score_out_of_10', 0)}/10)")
                
                # Extract your updated search keywords or fallback gracefully
                search_keywords = job.get("linkedin_search_keywords", '"Talent Acquisition" OR "Recruiter"')
                outreach_links = find_linkedin_targets(job["company"], search_keywords)
                
                # Update, pass along extra schema values, and sort the Excel workbook structure on disk
                append_to_local_sheet(job, outreach_links)
                
        except Exception as pipeline_error:
            print(f"❌ Fatal operational layer execution failure: {pipeline_error}")
            continue

    print("\n✅ Pipeline complete. Job_Search_Tracker.xlsx updated and perfectly sorted.")

def test_run():
    agent = JobAgent()
    print("🚀 Running Verification Test with explicit Mock Data...")
    
    # Simulating a pristine raw text match that exactly targets your profile
    mock_scraped_text = """
    Google Careers. 
    Role: Staff Software Engineer, Core Distributed Systems.
    Location: Bangalore, Karnataka, India.
    Requirements: 10+ years of professional software development experience. High proficiency in Java. 
    Deep architectural background building high-availability frameworks, low-latency microservices, 
    and multi-tenant distributed storage engines. Experience leading engineering teams at scale.
    Apply here: https://www.google.com/about/careers/applications/jobs/results/staff-backend-java
    """
    
    print("🧠 Evaluating with Gemini...")
    evaluation_results = agent.evaluate_scraped_data(mock_scraped_text)
    
    for job in evaluation_results.get("jobs", []):
        if job["score_out_of_10"] >= 7: 
            print(f"🎯 Match Found: {job['job_title']} (Score: {job['score_out_of_10']}/10)")
            connections = find_linkedin_targets(job["company"], job["linkedin_search_keywords"])
            append_to_local_sheet(job, connections)
            print("💾 Saved row locally to Job_Search_Tracker.xlsx")

def run_job_search():
    client = get_gemini_client()

    # Build search context
    urls_list = "\n".join([f"- {url}" for url in getattr(config, 'TARGET_URLS', [])])
    queries_list = "\n".join([f"- {query}" for query in getattr(config, 'SEARCH_QUERIES', [])])

    print("Step 1: Running Google Search Grounding...")
    
    search_prompt = f"""
    Find software engineering jobs in India published within the LAST 24 HOURS matching this profile:

    USER PROFILE:
    {config.USER_PROFILE}

    TARGET DIRECT URLS:
    {urls_list}

    SEARCH QUERIES:
    {queries_list}

    Instructions:
    1. Perform web searches to find newly listed job postings in India matching the profile.
    2. Strictly exclude any job posted more than 24 hours ago relative to {config.CURRENT_DATE_STR}.
    3. Include company names, job titles, exact dates posted, locations, application URLs, and details for compensation estimation.
    """

    # STEP 1: Search the web without JSON schema (text output only)
    step1_response = generate_content_with_retry(
        client=client,
        prompt=search_prompt,
        primary_model="gemini-2.5-flash",
        fallback_model="gemini-2.0-flash"
    )

    raw_search_results = step1_response.text
    print("Step 1 Complete. Parsing results into structured JSON...")

    # STEP 2: Convert search results to structured JSON matching RESPONSE_SCHEMA
    structure_prompt = f"""
    Extract and structure the following raw job search findings into the required JSON Schema.

    USER EVALUATION & SCORING RULES:
    {config.USER_PROFILE}

    RAW SEARCH FINDINGS:
    {raw_search_results}
    """

    step2_response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=structure_prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=config.RESPONSE_SCHEMA,
            temperature=0.1,
        )
    )

    # STEP 3: Write payload to Job_Search_Tracker.xlsx
    try:
        data = json.loads(step2_response.text)
        print(f"\nSuccessfully parsed {len(data.get('jobs', []))} jobs.")

        # Commit to Excel via your custom local_excel_manager module
        write_results_to_excel(data)

        print("\n✅ Pipeline complete. Job_Search_Tracker.xlsx updated successfully.")

        return data
    except Exception as e:
        print("Raw Gemini Output:", step2_response.text)
        print("❌ JSON Parsing / Output Error:", e)

def clean_job_url(job):
    url = job.get("job_url", "")
    company = job.get("company", "")
    title = job.get("job_title", "")

    # Check if URL is invalid, placeholder, or truncated
    if not url or url == "N/A" or "example.com" in url or len(url) < 15:
        # Construct a targeted search URL that opens the exact listing on Google/LinkedIn
        query = f'"{company}" "{title}" job apply India'
        encoded_query = urllib.parse.quote(query)
        return f"https://www.google.com/search?q={encoded_query}"
    
    return url        

def write_results_to_excel(payload):
    jobs_found = payload.get("jobs", [])
    
    if not jobs_found or len(jobs_found) == 0:
        print("ℹ️ No matched vacancies extracted matching target stack properties.")
        return
        
    print(f"\n📋 Extracted {len(jobs_found)} potential roles. Committing to Excel...")
    for job in jobs_found:
        if not job.get("company") or not job.get("job_title"):
            continue
            
        # Clean and validate the job URL before writing to Excel
        job["job_url"] = clean_job_url(job)
        
        print(f"   🎯 Processing: {job['job_title']} at {job['company']} (Score: {job.get('score_out_of_10', 0)}/10)")
        
        # Search for recruiter outreach targets on LinkedIn
        search_keywords = job.get("linkedin_search_keywords", '"Talent Acquisition" OR "Recruiter"')
        outreach_links = find_linkedin_targets(job["company"], search_keywords)
        
        # Append data row and update Job_Search_Tracker.xlsx
        append_to_local_sheet(job, outreach_links)

if __name__ == "__main__":
    run_job_search()
    job_search_linkedin()
