import streamlit as st
import time
import plotly.graph_objects as go
from scanner import scan_site

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Compliance Shield AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS STYLING (Dark Mode & Professional Header) ---
st.markdown("""
    <style>
    /* Global Styles */
    .stApp {background-color: #0f172a;}
    h1, h2, h3, p, div, span {font-family: 'Inter', sans-serif;}
    
    /* Navbar Container */
    .navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%);
        padding: 1.2rem 2rem;
        border-radius: 12px;
        border: 1px solid #334155;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        margin-bottom: 2rem;
    }
    
    /* Navbar Branding */
    .nav-brand { display: flex; align-items: center; gap: 15px; }
    .nav-logo { font-size: 2rem; }
    .nav-title h1 {
        font-size: 22px; margin: 0; font-weight: 700; color: #fff;
    }
    .nav-title span { font-size: 13px; color: #94a3b8; font-weight: 500; }

    /* Animated Status Badge */
    .status-container {
        display: flex; align-items: center; gap: 10px;
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 6px 14px; border-radius: 50px;
    }
    .status-dot {
        width: 8px; height: 8px; background-color: #10b981;
        border-radius: 50%; box-shadow: 0 0 10px #10b981;
        animation: pulse 2s infinite;
    }
    .status-text { color: #10b981; font-size: 11px; font-weight: 700; letter-spacing: 1px; }

    @keyframes pulse {
        0% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(0.9); }
        100% { opacity: 1; transform: scale(1); }
    }
    
    /* Custom Elements */
    .pro-badge { background-color: #8B5CF6; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.7em; font-weight: bold; margin-left: 8px;}
    </style>

    <div class="navbar">
        <div class="nav-brand">
            <div class="nav-logo">🛡️</div>
            <div class="nav-title">
                <h1>Compliance Shield <span style="color: #8b5cf6;">AI</span></h1>
                <span>Universal Merchant Auditor v3.1</span>
            </div>
        </div>
        <div class="status-container">
            <div class="status-dot"></div>
            <span class="status-text">SYSTEM ONLINE</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- SALES HERO TEXT ---
st.markdown("""
<div style="text-align: center; margin-bottom: 30px;">
    <h3 style="color: #f8fafc; font-weight: 500;">
        Is your store at risk of a <span style="color: #ef4444; text-decoration: underline;">Google Suspension?</span>
    </h3>
    <p style="color: #cbd5e1; font-size: 16px; opacity: 0.8;">
        Scan for <b>Misrepresentation</b>, <b>GPSR (2025)</b>, and <b>Trust Signals</b> instantly.
    </p>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR (Subscription Upsell) ---
with st.sidebar:
    st.markdown("### 🕵️ Watchdog Pro")
    st.info("Weekly Monitoring Active")
    st.markdown("---")
    st.markdown("**Unlock Pro Features:**")
    st.markdown("✅ Deep Site Crawl (All Pages)")
    st.markdown("✅ Broken Link Detector")
    st.markdown("✅ Weekly Auto-Audit")
    # REPLACE LINK
    st.link_button("👉 Start Free Trial ($29/mo)", "YOUR_RECURRING_STRIPE_LINK_HERE", type="primary")

# --- INPUT SECTION ---
url = st.text_input("ENTER STORE URL", placeholder="e.g., gymshark.com", label_visibility="collapsed")

if st.button("🚀 RUN DEEP DIAGNOSTIC", type="primary", use_container_width=True):
    if not url:
        st.warning("Please enter a URL first.")
    else:
        # FAKE LOADING ANIMATION
        progress_text = "Establishing connection..."
        my_bar = st.progress(0, text=progress_text)
        
        steps = [
            (20, "Scanning HTML DOM structure..."),
            (50, "Checking Google Merchant Center policies..."),
            (70, "Verifying GPSR Responsible Person data..."),
            (90, "Calculating Trust Score..."),
            (100, "Finalizing Report...")
        ]
        
        for percent, text in steps:
            time.sleep(0.2)
            my_bar.progress(percent, text=text)
        my_bar.empty()

        # --- RUN SCAN ---
        results = scan_site(url)

        if "error" in results:
            st.error(results["error"])
        else:
            score = results["score"]
            meta = results["meta"]
            checks = results["checks"]
            
            st.divider()
            
            # --- DASHBOARD: GAUGE CHART ---
            # Dynamic Color Logic
            if score < 50: bar_color = "#EF4444" # Red
            elif score < 80: bar_color = "#F59E0B" # Yellow
            else: bar_color = "#10B981" # Green

            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = score,
                title = {'text': "Trust Score"},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': bar_color},
                    'steps': [
                        {'range': [0, 50], 'color': "#334155"},
                        {'range': [50, 80], 'color': "#475569"},
                        {'range': [80, 100], 'color': "#0f172a"}
                    ]
                }
            ))
            fig.update_layout(height=250, margin={'t':0,'b':0,'l':0,'r':0}, paper_bgcolor="#0f172a", font={'color': "white"})
            
            c1, c2 = st.columns([1, 2])
            with c1:
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                st.markdown(f"### Detected Platform: **{meta['platform']}**")
                
                if score < 50:
                    st.error("🚨 CRITICAL COMPLIANCE FAILURES")
                    st.write("Risk of immediate ban. Fix mandatory errors below.")
                elif score < 80:
                    st.warning("⚠️ MODERATE RISK DETECTED")
                    st.write("Your store is usable but has visible trust issues.")
                else:
                    st.success("✅ SITE IS COMPLIANT")
                    st.write("Good job. No obvious errors found.")

            # --- DETAILED TABS ---
            st.markdown("### 📋 Audit Breakdown")
            tab1, tab2, tab3 = st.tabs(["⚠️ Critical Errors", "🏗️ Brand & Trust", "🔒 Deep Scan (Pro)"])

            with tab1:
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("**Google Merchant Center**")
                    st.write(f"{'✅' if checks.get('physical_address') else '❌'} Physical Address")
                    st.write(f"{'✅' if checks.get('refund_policy') else '❌'} Refund Policy")
                    st.write(f"{'✅' if checks.get('terms_service') else '❌'} Terms of Service")
                with col_b:
                    st.markdown("**Legal / GPSR (2025)**")
                    if checks.get("gpsr_check"):
                        st.success("✅ GPSR Compliant")
                    else:
                        st.error("❌ 'Responsible Person' Missing")
                        st.caption("Illegal for EU Sales.")

            with tab2:
                col_c, col_d = st.columns(2)
                with col_c:
                    st.markdown("**Professionalism**")
                    if checks.get("pro_email"):
                        st.success("✅ Pro Email Domain")
                    else:
                        st.warning("⚠️ Amateur Email (Gmail/Yahoo)")
                    
                    if meta.get("favicon"):
                        st.success("✅ Custom Favicon")
                    else:
                        st.info("ℹ️ Missing Browser Icon")
                
                with col_d:
                    st.markdown("**Language & Trust**")
                    if checks.get("fake_scarcity"):
                        st.error("⚠️ 'Fake Scarcity' Detected")
                        st.caption("Words like 'Hurry' or 'Timer' trigger Google bans.")
                    else:
                        st.success("✅ Clean Sales Language")

            with tab3:
                # BLURRED UPSELL SECTION
                st.markdown("""
                <div style="background-color: #1e293b; padding: 20px; border-radius: 10px; text-align: center; border: 1px dashed #475569;">
                    <h3 style="color: #94a3b8;">🔒 Pro Insights Locked</h3>
                    <p style="color: #cbd5e1;">We found <b>12+ Internal Pages</b> but cannot scan them in Free Mode.</p>
                    <div style="filter: blur(4px); opacity: 0.5; text-align: left; margin-top: 15px;">
                        <p>❌ <b>Product Page Analysis:</b> Missing Return Info on /products/t-shirt...</p>
                        <p>❌ <b>Broken Links:</b> 3 links on /about returning 404 Error...</p>
                        <p>❌ <b>Speed Check:</b> Mobile load time > 3s...</p>
                    </div>
                    <br>
                    <p style="color: #F59E0B; font-weight: bold;">Unlock Deep Scan + Weekly Monitoring for $29/mo</p>
                </div>
                """, unsafe_allow_html=True)
                # RECURRING LINK
                st.link_button("🔓 Unlock Full Report ($29)", "YOUR_RECURRING_STRIPE_LINK_HERE", use_container_width=True)

            # --- BOTTOM UPSELL (One-Time) ---
            if score < 95:
                st.divider()
                st.markdown("### 🛠️ Need a quick fix?")
                c_up1, c_up2 = st.columns([2,1])
                with c_up1:
                    st.write("Don't want a subscription? Get the **Fix-It Templates** (One-time purchase).")
                    st.write("Includes: **GPSR Widget**, **Anti-Ban Refund Policy**, and **Google Checklist**.")
                with c_up2:
                    # ONE-TIME LINK
                    st.link_button("📥 Download Templates Only ($69)", "YOUR_ONE_TIME_STRIPE_LINK_HERE", type="primary", use_container_width=True)