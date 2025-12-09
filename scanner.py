import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re

def scan_site(url):
    # 1. Universal URL Cleaner
    if not url.startswith("http"):
        url = "https://" + url
    
    results = {
        "score": 100,
        "meta": {"url": url, "platform": "Unknown", "favicon": False},
        "checks": {},
        "details": []
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        text_lower = soup.get_text().lower()
        
        # --- PLATFORM DETECTION ---
        if "/products.json" in response.text or "shopify" in response.text.lower():
            results["meta"]["platform"] = "Shopify"
        elif "wp-content" in response.text:
            results["meta"]["platform"] = "WooCommerce"
        elif "wix.com" in response.text:
            results["meta"]["platform"] = "Wix"

        # --- CHECK 1: PROFESSIONAL EMAIL (New!) ---
        # Find emails in text or mailto links
        email_pattern = r'[\w\.-]+@[\w\.-]+'
        emails_found = re.findall(email_pattern, response.text)
        
        has_pro_email = False
        amateur_domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com"]
        
        if emails_found:
            # Check if ANY email is professional (not in amateur list)
            for email in emails_found:
                domain = email.split('@')[-1].lower()
                if domain not in amateur_domains:
                    has_pro_email = True
                    break
        
        results["checks"]["pro_email"] = has_pro_email
        if not has_pro_email:
            results["score"] -= 10
            results["details"].append("⚠️ Unprofessional Email detected (Using Gmail/Yahoo instead of branded domain).")

        # --- CHECK 2: CUSTOM FAVICON (New!) ---
        # Look for <link rel="icon" ...>
        icons = soup.find_all("link", rel=lambda x: x and 'icon' in x.lower())
        has_favicon = False
        for icon in icons:
            href = icon.get('href', '')
            if "shopify" not in href and "cdn" in href: # Crude check for custom uploaded icon
                has_favicon = True
                
        results["meta"]["favicon"] = has_favicon
        if not has_favicon:
            # We don't deduct points heavily, but we note it
            results["details"].append("⚠️ Default or Missing Favicon (Trust signal missing).")

        # --- CHECK 3: FAKE SCARCITY (New!) ---
        scarcity_words = ["hurry", "only 2 left", "selling out", "high demand", "limited time only"]
        has_scarcity = any(w in text_lower for w in scarcity_words)
        results["checks"]["fake_scarcity"] = has_scarcity
        if has_scarcity:
            results["score"] -= 5
            results["details"].append("⚠️ Aggressive 'Scarcity' language found (Google dislikes 'Fake Urgency').")

        # --- EXISTING CHECKS (Keep these) ---
        # Physical Address
        address_keywords = ["street", "road", "ave", "suite", "gmbh", "ltd"]
        has_address = any(k in text_lower for k in address_keywords)
        results["checks"]["physical_address"] = has_address
        if not has_address: results["score"] -= 20

        # Policies
        links = [l['href'].lower() for l in soup.find_all('a', href=True)]
        results["checks"]["refund_policy"] = any("refund" in l or "return" in l for l in links)
        if not results["checks"]["refund_policy"]: results["score"] -= 15

        # GPSR
        gpsr_keywords = ["responsible person", "authorised representative", "eu address"]
        results["checks"]["gpsr_check"] = any(k in text_lower for k in gpsr_keywords)
        if not results["checks"]["gpsr_check"]: 
            results["score"] -= 25
            results["details"].append("🚨 CRITICAL: Missing GPSR 'Responsible Person' address.")

        return results

    except Exception as e:
        return {"error": str(e)}