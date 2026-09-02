# gemini_client.py
import time
import config
from google import genai
from google.genai import types
from google.genai.errors import ServerError

def get_gemini_client() -> genai.Client:
    """Instantiates and configures the Gemini client with global HTTP retry policies."""
    return genai.Client(
        http_options=types.HttpOptions(
            retry_options=types.HttpRetryOptions(
                attempts=5,
                initial_delay=2.0,
                http_status_codes=[429, 500, 502, 503, 504]
            )
        )
    )

def generate_content_with_retry(
    client: genai.Client,
    prompt: str,
    primary_model: str = "gemini-2.5-flash",
    fallback_model: str = "gemini-2.0-flash",
    max_retries: int = 4,
    gen_config: types.GenerateContentConfig = None
):
    """Executes model generation with exponential backoff and automatic model fallback on 503 errors."""
    current_model = primary_model
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"🔄 Executing Model Call (Attempt {attempt}/{max_retries} using {current_model})...")
            
            kwargs = {"model": current_model, "contents": prompt}
            if gen_config:
                kwargs["config"] = gen_config

            response = client.models.generate_content(**kwargs)
            return response
            
        except ServerError as e:
            if e.code == 503:
                wait_time = 2 ** attempt
                print(f"⚠️ 503 Server Unavailable ({e.message}). Retrying in {wait_time}s...")
                
                if attempt >= 2 and current_model == primary_model:
                    print(f"🔀 Switching to fallback model: {fallback_model}")
                    current_model = fallback_model
                
                time.sleep(wait_time)
            else:
                raise e
                
    raise RuntimeError("❌ Request failed after maximum retries due to model unavailability.")
