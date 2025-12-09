import streamlit as st
import time
from scanner import scan_site  # This imports the script you just ran

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="GPSR & Google Compliance Scanner",
    page_icon="🛡️",
    layout="centered"
)

# --- CUSTOM CSS (To make it look pro) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #f0f2f6;
    }
    div[data-testid="stMetricValue"] {
        font-size: 50px;
    }
    .css-1v0mbdj.e115fcil1 {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 20px;
        background-color: white;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        height: 3em;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("🛡️ E-Com Compliance Scanner")
st.markdown("### 🚨 New 2025 Law Enforced: Are you GPSR Compliant?")
st.markdown("Scan your store for **Google Misrepresentation** bans and **EU/UK Legal Violations**.")

# --- INPUT ---
url = st.text_input("Enter Shopify Store URL", placeholder="e.g. yourstore.com")

if st.button("RUN AUDIT NOW"):
    if not url:
        st.warning("Please paste a URL first.")
    else:
        # Progress Bar (Fake processing time to build anticipation)
        progress_text = "Connecting to store..."
        my_bar = st.progress(0, text=progress_text)
        
        for percent_complete in range(100):
            time.sleep(0.01) # fast scan
            if percent_complete == 30:
                my_bar.progress(percent_complete + 1, text="Scanning HTML structure...")
            elif percent_complete == 60:
                my_bar.progress(percent_complete + 1, text="Checking GPSR legal keywords...")
            else:
                my_bar.progress(percent_complete + 1)
        
        my_bar.empty()

        # --- RUN SCANNER ---
        results = scan_site(url)

        if "error" in results:
            st.error(f"Could not access site: {results['error']}")
        else:
            score = results.get("score", 0)
            
            # --- DISPLAY SCORE ---
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                if score < 50:
                    st.metric(label="RISK LEVEL", value=f"{score}/100", delta="- CRITICAL RISK", delta_color="inverse")
                elif score < 80:
                    st.metric(label="RISK LEVEL", value=f"{score}/100", delta="- MODERATE RISK", delta_color="inverse")
                else:
                    st.metric(label="RISK LEVEL", value=f"{score}/100", delta="SAFE", delta_color="normal")

            st.write("---")

            # --- DETAILED REPORT ---
            st.subheader("📋 Audit Report")
            
            c1, c2 = st.columns(2)
            
            checks = results.get("checks", {})
            
            with c1:
                st.markdown("**Google Merchant Center:**")
                if checks.get("physical_address"):
                    st.success("✅ Address Found")
                else:
                    st.error("❌ No Address (Ban Trigger)")
                
                if checks.get("refund_policy"):
                    st.success("✅ Refund Policy")
                else:
                    st.error("❌ No Refund Policy")

            with c2:
                st.markdown("**Legal & GPSR (2025):**")
                if checks.get("responsible_person"):
                    st.success("✅ GPSR Contact")
                else:
                    st.error("❌ GPSR Missing (Illegal)")
                
                if checks.get("contact_email"):
                    st.success("✅ Contact Method")
                else:
                    st.warning("⚠️ No Contact Info")

            # --- THE "MONEY" SECTION (Upsell) ---
            if score < 100:
                st.write("---")
                container = st.container()
                container.error(f"🚨 We found critical errors on {url}.")
                container.write("Your store is at risk of being banned by Google or fined by EU authorities.")
                
                # THIS IS WHERE YOU PUT YOUR STRIPE LINK
                container.link_button("👉 Download the Fix-It Kit ($69)", "https://stripe.com")