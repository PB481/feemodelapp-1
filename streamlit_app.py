import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Fortress Deal Commander",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- THE "FORTRESS" CSS THEME ---
st.markdown("""
<style>
    /* MAIN BACKGROUND */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* CARD STYLING */
    .css-1r6slb0, .css-12oz5g7 {
        background-color: #262730;
        border: 1px solid #464B5C;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* METRICS BOXES */
    div[data-testid="stMetric"] {
        background-color: #1F2937;
        border: 1px solid #374151;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
    }
    div[data-testid="stMetricLabel"] {
        color: #9CA3AF !important;
        font-size: 14px !important;
    }
    div[data-testid="stMetricValue"] {
        color: #F3F4F6 !important;
        font-size: 28px !important;
        font-weight: 700 !important;
    }

    /* HEADERS */
    h1, h2, h3 {
        color: #F3F4F6 !important;
        font-family: 'Helvetica Neue', sans-serif;
    }
    h1 { font-weight: 800; letter-spacing: -1px; }
    
    /* CUSTOM ALERTS */
    .success-box {
        padding: 15px;
        border-radius: 8px;
        background-color: #064E3B;
        border-left: 5px solid #10B981;
        color: #D1FAE5;
        margin-bottom: 10px;
    }
    .warning-box {
        padding: 15px;
        border-radius: 8px;
        background-color: #78350F;
        border-left: 5px solid #F59E0B;
        color: #FEF3C7;
        margin-bottom: 10px;
    }
    .error-box {
        padding: 15px;
        border-radius: 8px;
        background-color: #7F1D1D;
        border-left: 5px solid #EF4444;
        color: #FEE2E2;
        margin-bottom: 10px;
    }

    /* BUTTONS */
    .stButton>button {
        width: 100%;
        background-color: #2563EB;
        color: white;
        border: none;
        padding: 10px;
        font-weight: bold;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #1D4ED8;
    }
    
    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #374151;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR: NAVIGATION & GLOBAL ASSUMPTIONS ---
with st.sidebar:
    st.title("🛡️ FORTRESS COMMANDER")
    st.caption("Deal Desk Analytics v2.0")
    st.markdown("---")
    navigation = st.radio("TOOLKIT", ["Deal Scorer", "Decision Trees", "Negotiation Playbook"])
    
    st.markdown("---")
    st.markdown("### ⚙️ SYSTEM PARAMS")
    
    # Cost Drivers
    with st.expander("Back-Office Costs", expanded=False):
        base_cost = st.number_input("Base Cost/Fund ($)", value=25000, step=1000)
        overhead_load = st.slider("Overhead Load (%)", 0, 50, 20) / 100
    
    # Revenue Yields
    with st.expander("Yield Assumptions", expanded=False):
        fx_spread_bps = st.number_input("Avg FX Spread (bps)", value=8.0, step=0.5)
        cash_spread_bps = st.number_input("Cash NII Spread (bps)", value=150.0, step=10.0)
    
    # Margin Hurdle
    hurdle_rate = st.slider("TARGET MARGIN (%)", 20, 60, 40)

# --- FUNCTION: GAUGE CHART ---
def create_gauge(value, title, threshold):
    # Dynamic Color Logic
    if value >= threshold:
        bar_color = "#10B981" # Green
    elif value < 0:
        bar_color = "#EF4444" # Red
    else:
        bar_color = "#F59E0B" # Yellow/Amber

    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        title = {'text': title, 'font': {'size': 20, 'color': '#9CA3AF'}},
        number = {'font': {'size': 40, 'color': bar_color}, 'suffix': "%"},
        gauge = {
            'axis': {'range': [-20, 100], 'tickwidth': 1, 'tickcolor': "#4B5563"},
            'bar': {'color': bar_color},
            'bgcolor': "#1F2937",
            'borderwidth': 2,
            'bordercolor': "#374151",
            'steps': [
                {'range': [-20, 0], 'color': '#374151'},
                {'range': [0, threshold], 'color': '#374151'}
            ],
            'threshold': {
                'line': {'color': "#F59E0B", 'width': 4},
                'thickness': 0.75,
                'value': threshold
            }
        }
    ))
    fig.update_layout(
        paper_bgcolor = "#0E1117", 
        font = {'color': "#F3F4F6", 'family': "Arial"},
        height=280, 
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig

# --- TAB 1: DEAL SCORER (CALCULATOR) ---
if navigation == "Deal Scorer":
    st.markdown("## 📊 Deal Profitability Scorer")
    
    # --- INPUT SECTION (CARD STYLE) ---
    with st.container():
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 1. Asset Profile")
            aum = st.number_input("Launch AUM ($M)", value=50.0, step=10.0) * 1_000_000
            complexity = st.selectbox("Fund Complexity", ["Low (Vanilla)", "Medium (Hedge)", "High (Private Credit)"])
            comp_map = {"Low (Vanilla)": 1.0, "Medium (Hedge)": 1.5, "High (Private Credit)": 2.5}
            comp_factor = comp_map[complexity]

        with col2:
            st.markdown("### 2. Fee Proposal")
            admin_bps = st.number_input("Admin Fee (bps)", value=8.0, step=0.1)
            mmf = st.number_input("Min. Monthly Fee ($)", value=5000, step=500)
            
        with col3:
            st.markdown("### 3. The Bundle")
            est_fx_vol = st.number_input("Est. Annual FX Vol ($M)", value=10.0, step=5.0) * 1_000_000
            est_cash = st.number_input("Avg. Cash Balances ($M)", value=2.0, step=0.5) * 1_000_000

    st.markdown("---")

    # --- CALCULATIONS ---
    admin_rev_bps = aum * (admin_bps / 10000)
    admin_rev_mmf = mmf * 12
    admin_revenue = max(admin_rev_bps, admin_rev_mmf)
    
    fx_revenue = est_fx_vol * (fx_spread_bps / 10000)
    cash_revenue = est_cash * (cash_spread_bps / 10000)
    total_revenue = admin_revenue + fx_revenue + cash_revenue
    
    total_cost = (base_cost * comp_factor) * (1 + overhead_load)
    profit = total_revenue - total_cost
    margin_percent = (profit / total_revenue) * 100 if total_revenue > 0 else 0

    # --- SCOREBOARD DASHBOARD ---
    c1, c2, c3 = st.columns([1, 1, 1.5])
    
    with c1:
        st.metric("Total Relationship Value (TRV)", f"${total_revenue:,.0f}", delta=f"{admin_bps} bps")
        st.caption(f"Admin: ${admin_revenue:,.0f} | FX/Cash: ${(fx_revenue + cash_revenue):,.0f}")
        
    with c2:
        st.metric("Cost to Serve (CTS)", f"${total_cost:,.0f}", delta=f"{comp_factor}x Complexity", delta_color="inverse")
        st.caption(f"Base: ${base_cost:,.0f} | Load: {overhead_load*100}%")
        
    with c3:
        st.plotly_chart(create_gauge(margin_percent, "Net Margin %", hurdle_rate), use_container_width=True)

    # --- THE VERDICT (Dynamic Alerts) ---
    st.subheader("📝 The Verdict")
    
    if margin_percent >= hurdle_rate:
        st.markdown(f"""
        <div class="success-box">
            <strong>✅ APPROVED:</strong> This deal exceeds the <strong>{hurdle_rate}%</strong> hurdle. Proceed to contract.
        </div>
        """, unsafe_allow_html=True)
    elif margin_percent < 0:
        st.markdown(f"""
        <div class="error-box">
            <strong>🛑 REJECT:</strong> This deal is a <strong>LOSS MAKER</strong> ($-{abs(profit):,.0f}/yr). Do not sign.
        </div>
        """, unsafe_allow_html=True)
        st.write(f"**Required Action:** You need to find **${abs(profit):,.0f}** in additional revenue just to break even.")
    else:
        st.markdown("""
        <div class="warning-box">
            <strong>⚠️ REFERRAL REQUIRED:</strong> Deal is profitable but below target hurdle. Apply 'Give-Gets' below.
        </div>
        """, unsafe_allow_html=True)

        # --- THE SOLVER ---
        with st.expander("🔧 Margin Fixer (Solve for X)", expanded=True):
            target_profit = total_revenue * (hurdle_rate / 100)
            gap = (total_cost / (1 - (hurdle_rate/100))) - total_revenue
            
            if gap > 0:
                st.write(f"To reach **{hurdle_rate}% Margin**, you need **${gap:,.0f}** in additional revenue.")
                req_fx = gap / (fx_spread_bps / 10000)
                req_admin_bps = (gap / aum) * 10000
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.info(f"**Option A (FX Flow):**\nGet client to commit to **${req_fx/1_000_000:,.1f}M** more in FX Flow.")
                with col_b:
                    st.info(f"**Option B (Fee Bump):**\nRaise Admin Fee by **{req_admin_bps:.2f} bps** (New total: {admin_bps + req_admin_bps:.2f} bps).")

# --- TAB 2: DECISION TREES ---
elif navigation == "Decision Trees":
    st.markdown("## 🌳 Negotiation Decision Trees")
    
    tab1, tab2 = st.tabs(["The 'Rate Card' Challenge", "The 'Small Launch' Trap"])
    
    with tab1:
        st.markdown("#### Scenario: Competitor is Cheaper")
        st.info("Sales: 'Competitor X is 2bps cheaper. We need to match.'")
        
        q1 = st.radio("Is the deal margin (at proposed price) above 40%?", ["Select...", "Yes", "No"], index=0)
        
        if q1 == "Yes":
            st.markdown("⬇️")
            q2 = st.radio("Is this a 'Vanilla' Fund or 'Exotic'?", ["Select...", "Vanilla (Long Only)", "Exotic (Derivatives/Private)"], index=0)
            
            if q2 == "Vanilla (Long Only)":
                st.success("✅ **MATCH FEE** but mandate **Full STP** (No manual uploads).")
            elif q2 == "Exotic (Derivatives/Private)":
                st.markdown("⬇️")
                q3 = st.radio("Can we capture the Wallet Share (Custody + FX)?", ["Select...", "Yes", "No"], index=0)
                if q3 == "Yes":
                    st.success("✅ **MATCH FEE** on Admin, but lock in FX exclusivity.")
                elif q3 == "No":
                    st.error("🛑 **DO NOT MATCH.** Sell our Valuation Team expertise.")
        
        elif q1 == "No":
            st.error("🛑 **STOP.** Do not lower price. Pivot to a 'Ramp-Up' model.")

    with tab2:
        st.markdown("#### Scenario: The Small Launch ($20M AUM)")
        st.info("Sales: 'They will be $500M in two years! Give them a break now.'")
        
        sq1 = st.radio("Does the Minimum Monthly Fee (MMF) cover fixed costs?", ["Select...", "Yes", "No"], index=0, key="sq1")
        
        if sq1 == "No":
            st.error("🛑 **STOP.** Raise the MMF. We cannot subsidize their startup costs.")
        elif sq1 == "Yes":
            st.markdown("⬇️")
            sq2 = st.radio("Does the deal structure include tiered breakpoints?", ["Select...", "Yes", "No"], index=0, key="sq2")
            
            if sq2 == "No":
                st.warning("⚠️ **Counter-Propose:** Offer 10bps on first $50M, 6bps on next $50M.")
            elif sq2 == "Yes":
                st.success("✅ **PROCEED.** Ensure Implementation Fees are paid upfront.")

# --- TAB 3: NEGOTIATION PLAYBOOK ---
elif navigation == "Negotiation Playbook":
    st.markdown("## 🛡️ The 'Give-Get' Playbook")
    st.caption("Never concede on price without extracting value elsewhere.")
    
    col_x, col_y = st.columns(2)
    
    with col_x:
        with st.expander("1. IF they want Lower Admin Bps...", expanded=True):
            st.markdown("""
            **You ask for:** Longer Contract Term (3-5 Years).
            > *"I can get to that number, but that is a 'Partner Price,' not a 'Vendor Price.' I need a 3-year term to amortize the setup costs."*
            """)
        
        with st.expander("2. IF they want Waived Setup Fees..."):
            st.markdown("""
            **You ask for:** Higher Minimum Monthly Fee (MMF).
            > *"I can waive the setup fee to help your Day 1 cash flow, but I need to keep the MMF steady to cover the ongoing compliance costs."*
            """)

    with col_y:
        with st.expander("3. IF they want Lower Custody Fees..."):
            st.markdown("""
            **You ask for:** Exclusivity on FX & Cash.
            > *"The real cost to you isn't the custody bp, it's the operational drag of unbundled FX. If you give us the FX flow, I can suppress the custody fee."*
            """)

        with st.expander("4. IF they want Custom Reporting..."):
            st.markdown("""
            **You ask for:** Standard/Hard-coded Pricing for 'Extra' Reports.
            > *"Happy to build that, but bespoke work falls outside the standard SLA. We bill customization at a per-hour rate."*
            """)

    st.markdown("### 🚫 The Red Lines (Non-Negotiables)")
    st.error("""
    1.  **Liability Caps:** Never unlimited. Cap at 12-24 months fees.
    2.  **CPI / COLA:** Contracts must have inflation adjustment clauses.
    3.  **Pass-Throughs:** Tech, Legal, and SWIFT costs are billable to client.
    """)
