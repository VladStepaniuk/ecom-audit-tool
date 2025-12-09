import streamlit as st
import time
from scanner import scan_site

# --- PAGE CONFIGURATION (Force Dark Mode in settings if possible, but CSS will handle it) ---
st.set_page_config(
    page_title="Compliance Shield 2025",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- MODERN DARK THEME CSS ---
st.markdown("""
    <style>
    /* Force Dark Background */
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input {
        background-color: #262730;
        color: white;
        border: 1px solid #4b4b4b;
        border-radius: 8px;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #00D26A; /* Success Green */
        color: #000000;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        padding: 0.75rem 1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #00b359;
        box-shadow: 0 4px 15px rgba(0, 210, 106, 0.4);
    }
    
    /* Cards */
    .audit-card {
        background-color: #1f2937;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #374151;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Score Circle */
    .score-container {
        text-align: center;
        padding: 20px;
        background: #111827;
        border-radius: 15px;
        border: 2px solid #374151;
    }
    
    h1, h2, h3 {
        color: #ffffff !important;
    }
    p, li {
        color: #d1d5db !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR (Trust Signals) ---
with st.sidebar:
    st.write("### 🔒 Security Audit")
    st.info("Scanner Version: v2.4.0")
    st.write("Checks updated for:")
    st.caption("✅ Google Merchant Center")
    st.caption("✅ EU GPSR Directive (2025)")
    st.caption("✅ Shopify Trust Signals")

# --- MAIN HERO SECTION ---
col1, col2 = st.columns([2, 1])

with col1:
    st.title("🛡️ E-Com Compliance Shield")
    st.markdown("""
    <div style='background-color: #2e1065; padding: 15px; border-radius: 10px; border-left: 5px solid #8b5cf6;'>
        <strong style='color: #c4b5fd'>NEW 2025 ENFORCEMENT:</strong> 
        Stores missing the <b>GPSR 'Responsible Person'</b> address are now being banned by Google and blocked from EU customs.
    </div>
    """, unsafe_allow_html=True)

# --- SCANNER INPUT ---
st.markdown("###") # Spacer
url = st.text_input("ENTER STORE URL", placeholder="https://yourstore.com", help="We scan the public HTML for compliance tags.")

if st.button("🚀 RUN COMPLIANCE DIAGNOSTIC", use_container_width=True):
    if not url:
        st.toast("⚠️ Please enter a URL first!", icon="⚠️")
    else:
        # FAKE LOADING ANIMATION (Builds value)
        progress_text = "Establishing secure connection..."
        my_bar = st.progress(0, text=progress_text)
        
        steps = [
            (20, "Scanning HTML DOM structure..."),
            (40, "Checking Google Merchant Center policies..."),
            (60, "Verifying GPSR Responsible Person data..."),
            (80, "Calculating Trust Score..."),
            (100, "Finalizing Report...")
        ]
        
        for percent, text in steps:
            time.sleep(0.3) # Make it feel like it's "thinking"
            my_bar.progress(percent, text=text)
        
        my_bar.empty()

        # --- LOGIC ---
        results = scan_site(url)
        
        if "error" in results:
            st.error(f"Could not connect to site. Reason: {results['error']}")
        else:
            score = results.get("score", 0)
            checks = results.get("checks", {})
            
            # --- RESULTS DASHBOARD ---
            st.divider()
            
            # TOP ROW: SCORE & STATUS
            c1, c2, c3 = st.columns([1, 1, 2])
            
            with c1:
                # Score Color Logic
                score_color = "#ef4444" if score < 50 else "#f59e0b" if score < 80 else "#10b981"
                st.markdown(f"""
                <div class="score-container">
                    <h4 style="margin:0; color:#9ca3af;">TRUST SCORE</h4>
                    <h1 style="font-size: 64px; margin:0; color: {score_color};">{score}</h1>
                </div>
                """, unsafe_allow_html=True)
                
            with c2:
                st.markdown(f"""
                <div class="audit-card" style="height: 100%; display: flex; flex-direction: column; justify-content: center;">
                    <h4 style="margin:0;">STATUS</h4>
                    <h2 style="color: {score_color};">{'CRITICAL RISK' if score < 80 else 'COMPLIANT'}</h2>
                    <p style="margin:0;">{len(results.get('details', []))} Issues Found</p>
                </div>
                """, unsafe_allow_html=True)
                
            with c3:
                 if checks.get("is_shopify", False):
                     st.info("✅ Platform: Shopify Detected")
                 else:
                     st.warning("⚠️ Platform: Could not verify Shopify")
            
            # MIDDLE ROW: DETAILED CHECKS
            st.subheader("🛑 Violation Breakdown")
            
            row1_col1, row1_col2 = st.columns(2)
            
            with row1_col1:
                st.markdown('<div class="audit-card"><h3>🛒 Google Merchant Center</h3>', unsafe_allow_html=True)
                
                items = [
                    ("Physical Address", checks.get("physical_address")),
                    ("Refund Policy", checks.get("refund_policy")),
                    ("Terms of Service", checks.get("terms_of_service"))
                ]
                
                for label, passed in items:
                    icon = "✅" if passed else "❌"
                    color = "#4ade80" if passed else "#f87171"
                    st.markdown(f"<div style='display:flex; justify-content:space-between; margin-bottom:10px; border-bottom:1px solid #374151; padding-bottom:5px;'><span>{label}</span><span style='color:{color}; font-weight:bold;'>{icon} {'PASS' if passed else 'FAIL'}</span></div>", unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)

            with row1_col2:
                st.markdown('<div class="audit-card"><h3>🇪🇺 GPSR & Legal (2025)</h3>', unsafe_allow_html=True)
                
                items = [
                    ("Responsible Person (EU)", checks.get("responsible_person")),
                    ("Contact Method", checks.get("contact_email")),
                    ("Shipping Policy", checks.get("shipping_policy"))
                ]
                
                for label, passed in items:
                    icon = "✅" if passed else "❌"
                    color = "#4ade80" if passed else "#f87171"
                    st.markdown(f"<div style='display:flex; justify-content:space-between; margin-bottom:10px; border-bottom:1px solid #374151; padding-bottom:5px;'><span>{label}</span><span style='color:{color}; font-weight:bold;'>{icon} {'PASS' if passed else 'FAIL'}</span></div>", unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)

            # BOTTOM ROW: THE UPSELL
            if score < 100:
                st.markdown("###")
                st.error("🚨 ACTION REQUIRED: Your store is liable for fines.")
                
                col_cta1, col_cta2 = st.columns([2, 1])
                
                with col_cta1:
                    st.markdown("""
                    **We generated a "Fix-It Kit" specifically for these errors.**
                    
                    * 📄 **Legal Template:** GPSR "Responsible Person" Widget
                    * 📄 **Policy Template:** Google-Approved Refund Policy
                    * 📋 **Checklist:** 12 Hidden Ban Triggers to delete
                    """)
                
                with col_cta2:
                    # REPLACE LINK WITH YOUR STRIPE LINK
                    st.link_button("📥 DOWNLOAD FIX-IT KIT ($69)", "https://buy.stripe.com/YOUR_LINK_HERE", use_container_width=True)
            else:
                st.balloons()
                st.success("Perfect! Your store looks safe.")