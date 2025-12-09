import streamlit as st
import time
import plotly.graph_objects as go
from scanner import scan_site

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Compliance Shield 2025",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- MODERN CSS (Clean & Professional) ---
st.markdown("""
    <style>
    .stApp {background-color: #0E1117;}
    .report-card {background-color: #1F2937; padding: 20px; border-radius: 10px; border: 1px solid #374151; margin-bottom: 15px;}
    .success-text {color: #10B981; font-weight: bold;}
    .error-text {color: #EF4444; font-weight: bold;}
    .warning-text {color: #F59E0B; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🛡️ E-Com Compliance Shield")
    st.markdown("**Version 2.0 (Universal Scanner)** | Scans Google, GPSR & Trust Signals.")
with col2:
    st.markdown("### ") 
    st.markdown("`Status: ONLINE`")

# --- INPUT SECTION ---
url = st.text_input("ENTER STORE URL", placeholder="e.g., https://uk.gymshark.com/")

if st.button("RUN DEEP SCAN", type="primary", use_container_width=True):
    if not url:
        st.warning("Please enter a valid URL.")
    else:
        # PROGRESS ANIMATION
        with st.spinner('Accessing site nodes...'):
            time.sleep(1)
            results = scan_site(url)

        if "error" in results:
            st.error(results["error"])
        else:
            score = results["score"]
            meta = results["meta"]
            checks = results["checks"]

            # --- HERO RESULT SECTION ---
            st.divider()
            
           # 1. GAUGE CHART (Visual Impact)
            # Determine Color based on score
            if score < 50:
                bar_color = "#EF4444"  # Red
            elif score < 80:
                bar_color = "#F59E0B"  # Yellow/Orange
            else:
                bar_color = "#10B981"  # Green

            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = score,
                title = {'text': "Trust Score"},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': bar_color}, # USE THE NEW DYNAMIC COLOR
                    'steps': [
                        {'range': [0, 50], 'color': "#374151"},
                        {'range': [50, 80], 'color': "#4B5563"},
                        {'range': [80, 100], 'color': "#065F46"}
                    ]
                }
            ))
            fig.update_layout(height=250, margin={'t':0,'b':0,'l':0,'r':0}, paper_bgcolor="#0E1117", font={'color': "white"})
            
            c1, c2 = st.columns([1, 2])
            with c1:
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                st.markdown(f"### Detected Platform: **{meta['platform']}**")
                if score < 100:
                    st.error("🚨 CRITICAL COMPLIANCE FAILURES DETECTED")
                    st.write("Your store is at risk of Google Merchant Center suspension and EU border fines.")
                else:
                    st.success("✅ SITE IS COMPLIANT")
                    st.write("Good job. No obvious errors found.")

            # --- DETAILED TABS (Clean UX) ---
            tab1, tab2, tab3 = st.tabs(["⚠️ Critical Errors", "🌍 GPSR/Legal", "⚙️ Tech & Trust"])

            with tab1:
                st.markdown("#### Suspension Triggers")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("**Physical Address in Footer**")
                    if checks.get("physical_address"):
                        st.markdown('<p class="success-text">✅ PASSED</p>', unsafe_allow_html=True)
                    else:
                        st.markdown('<p class="error-text">❌ FAILED (Google Mandatory)</p>', unsafe_allow_html=True)
                with col_b:
                    st.markdown("**Refund Policy**")
                    if checks.get("refund_policy"):
                        st.markdown('<p class="success-text">✅ PASSED</p>', unsafe_allow_html=True)
                    else:
                        st.markdown('<p class="error-text">❌ FAILED (Google Mandatory)</p>', unsafe_allow_html=True)

            with tab2:
                st.markdown("#### 2025 EU/UK Regulations")
                st.info("Requirement: Stores selling to EU must list a 'Responsible Person'.")
                if checks.get("gpsr_check"):
                    st.success("✅ GPSR COMPLIANT: 'Responsible Person' found.")
                else:
                    st.error("❌ NON-COMPLIANT: No 'Responsible Person' or EU address found.")
                    st.caption("This is now illegal for EU sales.")

            with tab3:
                st.markdown("#### Professionalism Check")
                if checks.get("template_text"):
                    st.warning("⚠️ Template Text Found (e.g. 'Lorem Ipsum').")
                else:
                    st.write("✅ No placeholder text found.")
                    
                if checks.get("broken_socials"):
                    st.warning("⚠️ Social Links are broken (Point to empty profiles).")
                else:
                    st.write("✅ Social media links look valid.")

            # --- ACTION PLAN (The Upsell) ---
            if score < 95:
                st.divider()
                st.markdown("### 🛠️ Fix These Errors Now")
                
                c_up1, c_up2 = st.columns([2,1])
                with c_up1:
                    st.write("Don't risk your business. We have pre-written legal templates that fix all the errors above.")
                    st.write("Includes: **GPSR Widget**, **Anti-Ban Refund Policy**, and **Google Checklist**.")
                with c_up2:
                    # REPLACE THIS WITH YOUR STRIPE LINK
                    st.link_button("📥 DOWNLOAD FIX-IT KIT ($69)", "https://buy.stripe.com/14A4gzcQGb8P3aNbUid3i00", type="primary", use_container_width=True)