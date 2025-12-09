import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse

def get_domain(url):
    parsed = urlparse(url)
    return parsed.netloc or parsed.path

def scan_site(url):
    # 1. Input Sanitization
    if not url.startswith("http"):
        url = "https://" + url
    
    results = {
        "score": 100,
        "is_shopify": False,
        "gpsr_compliant": False,
        "checks": {
            "physical_address": False,
            "refund_policy": False,
            "shipping_policy": False,
            "terms_of_service": False,
            "responsible_person": False,
            "contact_email": False
        },
        "details": []
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        # --- LAYER 1: PLATFORM DETECTION ---
        # Shopify stores expose a specific JSON endpoint. 
        # If this works, we know it's Shopify (and we look smart).
        try:
            shopify_check = requests.get(f"{url}/products.json", headers=headers, timeout=5)
            if shopify_check.status_code == 200:
                results["is_shopify"] = True
                results["details"].append("✅ Platform identified: Shopify")
        except:
            pass # Not critical if this fails

        # --- LAYER 2: SCRAPING THE HOME PAGE ---
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Convert all text to lower case for case-insensitive searching
        page_text = soup.get_text().lower()
        
        # Get all links to check for policy pages
        links = [a.get('href', '').lower() for a in soup.find_all('a', href=True)]
        link_texts = [a.get_text().lower() for a in soup.find_all('a', href=True)]

        # --- CHECK 1: PHYSICAL ADDRESS (Google Merchant Center Requirement) ---
        # Google bans stores that don't have a verified address in the footer.
        # We look for common address keywords near the bottom of the page or in text.
        address_keywords = [
            "street", "road", "ave", "avenue", "lane", "suite", 
            "floor", "box", "gmbh", "ltd", "inc", "plc"
        ]
        # We verify if any address keyword appears in the footer-like text or general text
        # (A simple heuristic: usually address is in the last 20% of text, but global search is safer for MVP)
        has_address = any(keyword in page_text for keyword in address_keywords)
        
        # Refined check: PO BOX is often banned by Google
        if "po box" in page_text:
            results["details"].append("⚠️ Warning: 'PO Box' detected. Google often rejects PO Boxes.")
            results["score"] -= 10
        
        if has_address:
            results["checks"]["physical_address"] = True
        else:
            results["score"] -= 20
            results["details"].append("❌ Critical: No physical address detected on home page.")

        # --- CHECK 2: POLICY PAGES (Trust Signals) ---
        # We look for links containing specific words
        
        # Refund Policy
        if any("refund" in l for l in links) or any("return" in l for l in links):
            results["checks"]["refund_policy"] = True
        else:
            results["score"] -= 15
            results["details"].append("❌ Missing 'Refund Policy' link.")

        # Shipping Policy
        if any("shipping" in l for l in links) or any("delivery" in l for l in links):
            results["checks"]["shipping_policy"] = True
        else:
            results["score"] -= 10
            results["details"].append("⚠️ Missing 'Shipping Policy' link.")

        # Terms
        if any("term" in l for l in links):
            results["checks"]["terms_of_service"] = True
        else:
            results["score"] -= 10
            results["details"].append("⚠️ Missing 'Terms of Service' link.")

        # --- CHECK 3: CONTACT INFO ---
        # Look for explicit email (mailto) or "contact us"
        if any("mailto:" in l for l in links) or "contact" in page_text:
            results["checks"]["contact_email"] = True
        else:
            results["score"] -= 10
            results["details"].append("❌ No clear contact method found.")

        # --- CHECK 4: GPSR COMPLIANCE (The 2025 "Panic" Feature) ---
        # EU/UK Law requires a "Responsible Person" or "Authorised Representative"
        gpsr_keywords = [
            "responsible person", 
            "authorised representative", 
            "authorized representative", 
            "economic operator", 
            "eu address",
            "uk address",
            "importer"
        ]
        
        # We check if ANY of these legal terms exist in the text
        is_gpsr = any(k in page_text for k in gpsr_keywords)
        
        if is_gpsr:
            results["gpsr_compliant"] = True
            results["checks"]["responsible_person"] = True
            results["details"].append("✅ GPSR Legal Keywords found.")
        else:
            results["checks"]["responsible_person"] = False
            results["score"] -= 35  # Major penalty
            results["details"].append("🚨 URGENT: GPSR 'Responsible Person' disclosure missing. (Illegal for EU sales)")

        return results

    except Exception as e:
        return {"error": str(e)}

# --- QUICK TEST BLOCK ---
if __name__ == "__main__":
    # Test it on a site immediately
    test_url = input("Enter a URL to test (e.g. gymshark.com): ")
    print(f"Scanning {test_url}...")
    data = scan_site(test_url)
    print("\n--- RESULTS ---")
    print(f"Score: {data.get('score')}")
    print(f"Is Shopify: {data.get('is_shopify')}")
    print(f"GPSR Compliant: {data.get('gpsr_compliant')}")
    print("\nDetails:")
    for d in data.get('details', []):
        print(d)