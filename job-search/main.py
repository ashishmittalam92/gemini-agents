# main.py
import sys
import os
import json

from scraper import scrape_target_url
from agent_engine import JobAgent
from linkedin_finder import find_linkedin_targets
from local_excel_manager import append_to_local_sheet
from config import TARGET_URLS

def main():
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

if __name__ == "__main__":
    main()
