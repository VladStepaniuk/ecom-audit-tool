import requests
from bs4 import BeautifulSoup
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
        # --- CONNECTIVITY CHECK ---
        try:
            response = requests.get(url, headers=headers, timeout=10)
        except Exception:
            return {"error": "Could not connect to site. Please check the URL and try again."}

        soup = BeautifulSoup(response.text, 'html.parser')
        text_lower = soup.get_text().lower()
        
        # --- PLATFORM DETECTION ---
        if "/products.json" in response.text or "shopify" in response.text.lower():
            results["meta"]["platform"] = "Shopify"
        elif "wp-content" in response.text:
            results["meta"]["platform"] = "WooCommerce"
        elif "wix.com" in response.text:
            results["meta"]["platform"] = "Wix"

        # --- CHECK 1: PROFESSIONAL EMAIL ---
        # Look for emails. If they use @gmail, @yahoo etc, it's amateur.
        email_pattern = r'[\w\.-]+@[\w\.-]+'
        emails_found = re.findall(email_pattern, response.text)
        
        has_pro_email = False
        amateur_domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com", "icloud.com"]
        
        if emails_found:
            for email in emails_found:
                domain = email.split('@')[-1].lower()
                if domain not in amateur_domains:
                    has_pro_email = True
                    break
        
        results["checks"]["pro_email"] = has_pro_email
        if not has_pro_email:
            results["score"] -= 10
            results["details"].append("⚠️ Amateur Support Email detected (e.g. Gmail/Yahoo).")

        # --- CHECK 2: CUSTOM FAVICON ---
        # Check for browser icon. Scammers usually leave the default.
        icons = soup.find_all("link", rel=lambda x: x and 'icon' in x.lower())
        has_favicon = False
        for icon in icons:
            href = icon.get('href', '')
            # A very basic check: if it points to a CDN, it's likely uploaded.
            if "cdn" in href or "upload" in href: 
                has_favicon = True
                
        results["meta"]["favicon"] = has_favicon
        if not has_favicon:
            # We don't deduct big points, but we note it
            results["details"].append("ℹ️ Default or Missing Favicon.")

        # --- CHECK 3: FAKE SCARCITY ---
        # Google bans "Misrepresentation" for fake countdowns/urgency.
        scarcity_words = ["hurry", "only 2 left", "selling out", "high demand", "limited time only", "timer"]
        has_scarcity = any(w in text_lower for w in scarcity_words)
        results["checks"]["fake_scarcity"] = has_scarcity
        if has_scarcity:
            results["score"] -= 5
            results["details"].append("⚠️ Aggressive 'Scarcity' language found (Google dislikes 'Fake Urgency').")

        # --- CHECK 4: PHYSICAL ADDRESS (Google Mandatory) ---
        address_keywords = ["street", "road", "ave", "avenue", "suite", "gmbh", "ltd", "floor", "box"]
        has_address = any(k in text_lower for k in address_keywords)
        results["checks"]["physical_address"] = has_address
        if not has_address: 
            results["score"] -= 20
            results["details"].append("❌ Critical: No physical address found in footer.")

        # --- CHECK 5: POLICY LINKS ---
        links = [l.get('href', '').lower() for l in soup.find_all('a', href=True)]
        
        has_refund = any("refund" in l or "return" in l for l in links)
        has_terms = any("term" in l or "condition" in l for l in links)
        has_shipping = any("shipping" in l or "delivery" in l for l in links)
        
        results["checks"]["refund_policy"] = has_refund
        results["checks"]["terms_service"] = has_terms
        results["checks"]["shipping_policy"] = has_shipping
        
        if not has_refund: results["score"] -= 15
        if not has_terms: results["score"] -= 10

        # --- CHECK 6: TEMPLATE TEXT ---
        template_phrases = ["lorem ipsum", "insert text here", "powered by shopify", "my store"]
        has_template_text = any(p in text_lower for p in template_phrases)
        results["checks"]["template_text"] = has_template_text
        if has_template_text:
            results["score"] -= 5

        # --- CHECK 7: GPSR / LEGAL (2025) ---
        # EU Law requires 'Responsible Person'
        gpsr_keywords = ["responsible person", "authorised representative", "eu address", "importer", "economic operator"]
        is_gpsr = any(k in text_lower for k in gpsr_keywords)
        
        results["checks"]["gpsr_check"] = is_gpsr
        if not is_gpsr:
            results["score"] -= 25
            results["details"].append("🚨 CRITICAL: Missing GPSR 'Responsible Person' address.")

        return results

    except Exception as e:
        return {"error": str(e)}