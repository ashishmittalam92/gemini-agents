# agent_engine.py
import time
import re
from google import genai  # Correct modern SDK import pattern
from google.genai import errors
from config import RESPONSE_SCHEMA, USER_PROFILE 

class JobAgent:
    def __init__(self, model_name="gemini-2.5-flash"):
        # Explicitly initialize the client. It automatically picks up GEMINI_API_KEY from env.
        self.client = genai.Client()
        self.model = model_name

    def evaluate_scraped_data(self, raw_html_text: str):
        """
        Evaluates scraped job details by explicitly comparing them 
        against the user's professional profile.
        """
        # Ensure we don't proceed if there's no data to process
        if not raw_html_text or len(raw_html_text.strip()) < 100:
            print("⚠️ Insufficient text data passed to evaluation engine. Skipping request.")
            return None

        prompt = f"""
You are an expert executive career agent matching job listings to a candidate's profile.

CANDIDATE PROFESSIONAL PROFILE:
{USER_PROFILE}

INBOUND SCRAPED JOB DATA:
{raw_html_text}

TASK:
1. Compare the Scraped Job Data against the Candidate Professional Profile.
2. Determine if the role matches target seniority tiers (Senior/Staff/Principal/Architect).
3. Compute a strict 'score_out_of_10' based purely on technical system scale fit.
4. Extract required fields precisely mapped to the response schema.
"""
        
        config = {
            "response_mime_type": "application/json",
            "response_schema": RESPONSE_SCHEMA, 
            "temperature": 0.2
        }
        
        max_retries = 5
        base_delay = 20
        
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=config
                )
                return response
                
            except errors.ClientError as e:
                # FIXED: Change e.status_code to e.code for the new GenAI SDK
                if e.code == 429:
                    error_msg = str(e)
                    print(f"\n⚠️ [Rate Limit Hit] Gemini Free Tier quota exhausted.")
                    
                    retry_match = re.search(r'retry in (\d+\.\d+|\d+)s', error_msg)
                    if retry_match:
                        sleep_duration = float(retry_match.group(1)) + 2.0
                    else:
                        sleep_duration = base_delay * (2 ** attempt)
                        
                    print(f"⏳ Cooling down pipeline. Sleeping for {sleep_duration:.2f}s...")
                    time.sleep(sleep_duration)
                    print("🚀 Resuming execution evaluation...")
                else:
                    # Bubble up other API errors (like 400 or 403) cleanly
                    raise e
                    
            except AttributeError as e:
                print(f"❌ Structural class configuration error: {e}")
                raise e
            except Exception as e:
                print(f"⚠️ Unexpected network glitch: {e}. Retrying...")
                time.sleep(5)
                
        raise RuntimeError("❌ Agent pipeline stopped: Gemini API rate limit could not be cleared.")
