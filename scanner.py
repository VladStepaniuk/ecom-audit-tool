import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def scan_site(url):
    # 1. Universal URL Cleaner
    if not url.startswith("http"):
        url = "https://" + url
    
    # Store results in a clean structure
    results = {
        "score": 100,
        "meta": {"url": url, "platform": "Unknown"},
        "checks": {},
        "details": []
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        # --- LAYER 1: CONNECTIVITY ---
        try:
            response = requests.get(url, headers=headers, timeout=8)
        except Exception:
            return {"error": "Could not connect. Check URL or try 'https://'"}
            
        soup = BeautifulSoup(response.text, 'html.parser')
        text_lower = soup.get_text().lower()
        
        # Detect Platform (Shopify / WooCommerce / Wix)
        if "/products.json" in response.text or "shopify" in response.text.lower():
            results["meta"]["platform"] = "Shopify"
        elif "wp-content" in response.text:
            results["meta"]["platform"] = "WooCommerce/WordPress"
        elif "wix.com" in response.text:
            results["meta"]["platform"] = "Wix"

        # --- CHECK 1: GOOGLE TRUST SIGNALS ---
        # Physical Address
        address_keywords = ["street", "road", "ave", "avenue", "lane", "suite", "gmbh", "ltd", "inc"]
        has_address = any(k in text_lower for k in address_keywords)
        results["checks"]["physical_address"] = has_address
        if not has_address: results["score"] -= 20

        # Policies (Looking for links)
        links = soup.find_all('a', href=True)
        link_hrefs = [l['href'].lower() for l in links]
        
        has_refund = any("refund" in l for l in link_hrefs) or any("return" in l for l in link_hrefs)
        has_terms = any("term" in l for l in link_hrefs) or any("condition" in l for l in link_hrefs)
        
        results["checks"]["refund_policy"] = has_refund
        results["checks"]["terms_service"] = has_terms
        
        if not has_refund: results["score"] -= 15
        if not has_terms: results["score"] -= 10

        # --- CHECK 2: SOCIAL INTEGRITY (New Feature!) ---
        # Detecting if they link to "facebook.com" without a username (common template error)
        social_domains = ["facebook.com", "instagram.com", "tiktok.com", "twitter.com"]
        broken_socials = False
        
        for l in link_hrefs:
            for d in social_domains:
                # If link is JUST "facebook.com" or "facebook.com/" it is broken
                if d in l and len(l) < len(d) + 2: 
                    broken_socials = True
        
        results["checks"]["broken_socials"] = broken_socials
        if broken_socials:
            results["score"] -= 10
            results["details"].append("⚠️ Broken Social Links detected (Links point to homepage, not profile).")

        # --- CHECK 3: LAZY TEMPLATE TEXT (New Feature!) ---
        # Detecting "Lorem Ipsum" or "Insert text here"
        template_phrases = ["lorem ipsum", "insert text here", "add your address", "powered by shopify"]
        has_template_text = any(p in text_lower for p in template_phrases)
        
        results["checks"]["template_text"] = has_template_text
        if has_template_text:
            results["score"] -= 10
            results["details"].append("⚠️ Template placeholder text found (e.g., 'Lorem Ipsum').")

        # --- CHECK 4: GPSR / LEGAL (2025) ---
        gpsr_keywords = ["responsible person", "authorised representative", "eu address", "importer"]
        is_gpsr = any(k in text_lower for k in gpsr_keywords)
        
        results["checks"]["gpsr_check"] = is_gpsr
        if not is_gpsr:
            results["score"] -= 30
            results["details"].append("🚨 CRITICAL: Missing 'Responsible Person' (GPSR) declaration.")

        return results

    except Exception as e:
        return {"error": str(e)}