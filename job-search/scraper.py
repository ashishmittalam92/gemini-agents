# scraper.py
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def scrape_target_url(url: str) -> str:
    """
    Spins up a headless browser to pull raw text layout structures from target job boards.
    Bypasses infinite tracking analytics via DOMContentLoaded strategies and compresses tokens using BS4.
    """
    # Initialize the return variable at the very top to prevent NameErrors if execution fails early
    final_payload = ""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        try:
            print(f"\n📥 Scraping current listings from: {url}")
            print("⏳ Loading network streams...")
            
            # Proceed instantly once the structural document layout is loaded
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            # Allow elements 3 seconds to complete rendering
            page.wait_for_timeout(3000)
            
            full_html = page.content()
            
            if not full_html or len(full_html.strip()) < 500:
                print("⚠️ Warning: Received low content density footprint from page layout.")
                return ""
                
            print("🧹 Sanitizing HTML token footprint...")
            # Use BeautifulSoup to strip out code blocks that inflate tokens
            soup = BeautifulSoup(full_html, "html.parser")
            for element in soup(["script", "style", "noscript", "meta", "header", "footer", "svg", "nav"]):
                element.decompose()
            
            # Extract plain text strings and strip structural whitespace redundancy
            clean_text = soup.get_text(separator=" ")
            compressed_lines = [line.strip() for line in clean_text.splitlines() if line.strip()]
            final_payload = " ".join(compressed_lines)
            
        except Exception as e:
            print(f"⚠️ Scraping exception caught: {e}")
            # fallback to empty string on failure
            final_payload = ""
        finally:
            context.close()
            browser.close()
            
    return final_payload
