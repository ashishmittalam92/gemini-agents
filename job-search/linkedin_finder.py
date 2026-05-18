# linkedin_finder.py
import urllib.parse
import urllib.request
import json
import re
import time

def find_linkedin_targets(company: str, keywords: str) -> list:
    """
    Deterministically generates a native LinkedIn People Search URL 
    strictly filtered to target professionals located in India.
    """
    # Clean up common corporate suffixes cleanly
    clean_company = company.replace(", LLC", "").replace("Inc.", "").replace("LLC", "")
    clean_company = clean_company.split("Global")[0].strip()
    
    # Target relevant internal decision-makers
    search_keywords = f'"{clean_company}" AND ("Talent Acquisition" OR "Recruiter" OR "Engineering Manager")'
    encoded_keywords = urllib.parse.quote(search_keywords)
    
    # Construct deep link with geoUrn facet set explicitly to 102713980 (LinkedIn's internal code for India)
    india_linkedin_search_url = (
        f"https://www.linkedin.com/search/results/people/?"
        f"facetGeoRegion=%5B%22in%3A0%22%5D&"  # Regional legacy filter fallback
        f"geoUrn=%5B%22102713980%22%5D&"       # Explicit India Country Code
        f"keywords={encoded_keywords}&"
        f"origin=GLOBAL_SEARCH_HEADER"
    )
    
    return [india_linkedin_search_url]

def find_linkedin_targets_2(company: str, keywords: str) -> list:
    """Queries DuckDuckGo API with explicit timeout safety configurations."""
    raw_query = f'site:linkedin.com/in/ "{company}" ("Talent Acquisition" OR "Engineering Manager" OR "{keywords}")'
    encoded_query = urllib.parse.quote_plus(raw_query)
    api_url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1"
    
    # Mirroring a completely realistic modern browser header configuration
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    
    connections = []
    
    # 1. Primary Structured API Attempt
    try:
        req = urllib.request.Request(api_url, headers=headers)
        # Drop the timeout to 5 seconds so it fails fast instead of hanging your entire terminal loop
        with urllib.request.urlopen(req, timeout=5) as response:
            payload = json.loads(response.read().decode())
            
            for topics in [payload.get("RelatedTopics", []), payload.get("Results", [])]:
                for item in topics:
                    first_url = item.get("FirstURL", "")
                    if "linkedin.com/in/" in first_url:
                        connections.append(first_url)
    except Exception as e:
        # Don't print massive stack traces for expected rate-limits
        print(f"   ℹ️ Primary API endpoint skipped (Throttling/Timeout)")

    # 2. Resilient Fallback Attempt
    if not connections:
        try:
            # Give the remote server a brief moment to breathe before trying fallback
            time.sleep(2)
            
            fallback_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            req = urllib.request.Request(fallback_url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=6) as response:
                html_content = response.read().decode('utf-8', errors='ignore')
                found_profiles = re.findall(r'linkedin\.com/in/[A-Za-z0-9_-]+', html_content)
                for profile in found_profiles:
                    connections.append(f"https://www.{profile}")
        except Exception as e:
            print(f"   ℹ️ Sourcing index busy, saving job card without outreach links.")

    # Deduplicate and scrub links cleanly
    clean_connections = []
    for url in connections:
        base_url = url.split('&')[0].split('?')[0].rstrip('/')
        if base_url not in clean_connections:
            clean_connections.append(base_url)

    return clean_connections[:3]
