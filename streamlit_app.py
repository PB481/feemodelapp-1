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

# --- CUSTOM CSS FOR STYLING ---
st.markdown("""
<style>
    .big-font { font-size:20px !important; font-weight: bold; }
    .metric-box { border: 1px solid #e0e0e0; padding: 20px; border-radius: 10px; background-color: #f9f9f9; }
    .stAlert { padding: 10px; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR: NAVIGATION & GLOBAL ASSUMPTIONS ---
with st.sidebar:
    st.title("🛡️ Fortress Commander")
    st.markdown("---")
    navigation = st.radio("Select Tool:", ["Deal Scorer (Calculator)", "Decision Trees", "Negotiation Cheat Sheet"])
    
    st.markdown("---")
    st.markdown("### ⚙️ Backend Assumptions")
    st.info("These are 'Fortress' costs/yields. Edit only if Finance approves.")
    
    # Cost Drivers (Hidden from standard sales view usually, but editable here for the model)
    base_cost = st.number_input("Base Cost per Fund ($)", value=25000, step=1000)
    overhead_load = st.slider("Overhead Load (%)", 0, 50, 20) / 100
    
    # Revenue Yields
    fx_spread_bps = st.number_input("Avg FX Spread (bps)", value=8.0, step=0.5)
    cash_spread_bps = st.number_input("Cash NII Spread (bps)", value=150.0, step=10.0)
    
    # Margin Hurdle
    hurdle_rate = st.slider("Target Margin Hurdle (%)", 20, 60, 40)

# --- FUNCTION: GAUGE CHART ---
def create_gauge(value, title, threshold):
    color = "green" if value >= threshold else "red"
    if value < 0: color = "black"
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        title = {'text': title},
        gauge = {
            'axis': {'range': [-20, 100]},
            'bar': {'color': color},
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': threshold
            }
        }
    ))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
    return fig

# --- TAB 1: DEAL SCORER (CALCULATOR) ---
if navigation == "Deal Scorer (Calculator)":
    st.header("🧮 Deal Profitability Scorer")
    st.markdown("Input proposed terms to calculate **Total Relationship Value (TRV)** and **Margin**.")

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("1. Asset Profile")
        aum = st.number_input("Launch AUM ($M)", value=50.0, step=10.0) * 1_000_000
        complexity = st.selectbox("Fund Complexity", ["Low (Vanilla)", "Medium (Hedge)", "High (Private Credit/Crypto)"])
        
        # Complexity Multiplier
        comp_map = {"Low (Vanilla)": 1.0, "Medium (Hedge)": 1.5, "High (Private Credit/Crypto)": 2.5}
        comp_factor = comp_map[complexity]

    with col2:
        st.subheader("2. Fee Proposal")
        admin_bps = st.number_input("Admin Fee (bps)", value=8.0, step=0.1)
        mmf = st.number_input("Min. Monthly Fee ($)", value=5000, step=500)
        
    with col3:
        st.subheader("3. The Bundle (Give-Get)")
        est_fx_vol = st.number_input("Est. Annual FX Vol ($M)", value=10.0, step=5.0) * 1_000_000
        est_cash = st.number_input("Avg. Cash Balances ($M)", value=2.0, step=0.5) * 1_000_000

    st.markdown("---")

    # --- CALCULATIONS ---
    # Revenue
    admin_rev_bps = aum * (admin_bps / 10000)
    admin_rev_mmf = mmf * 12
    admin_revenue = max(admin_rev_bps, admin_rev_mmf)
    
    fx_revenue = est_fx_vol * (fx_spread_bps / 10000)
    cash_revenue = est_cash * (cash_spread_bps / 10000)
    
    total_revenue = admin_revenue + fx_revenue + cash_revenue
    
    # Costs
    # Logic: Base Cost * Complexity Factor * (1 + Overhead)
    # Note: In a real model, volume-based costs would be added here.
    total_cost = (base_cost * comp_factor) * (1 + overhead_load)
    
    # Margin
    profit = total_revenue - total_cost
    margin_percent = (profit / total_revenue) * 100 if total_revenue > 0 else 0

    # --- OUTPUT DASHBOARD ---
    c1, c2, c3 = st.columns([1, 1, 1.5])
    
    with c1:
        st.metric("Total Revenue (TRV)", f"${total_revenue:,.0f}")
        st.caption(f"Admin: ${admin_revenue:,.0f} | FX/Cash: ${(fx_revenue + cash_revenue):,.0f}")
        
    with c2:
        st.metric("Cost to Serve (CTS)", f"${total_cost:,.0f}")
        st.caption(f"Complexity Factor: {comp_factor}x")
        
    with c3:
        # Gauge Chart
        st.plotly_chart(create_gauge(margin_percent, "Net Margin %", hurdle_rate), use_container_width=True)

    # --- ANALYSIS & VERDICT ---
    st.subheader("📝 The Verdict")
    
    if margin_percent >= hurdle_rate:
        st.success(f"✅ **APPROVED:** This deal exceeds the {hurdle_rate}% hurdle. Proceed to contract.")
    elif margin_percent < 0:
        st.error("🛑 **REJECT:** This deal is a loss-maker. Do not sign.")
        st.write(f"**Required Action:** You need to find **${abs(profit):,.0f}** in additional revenue just to break even.")
    else:
        st.warning("⚠️ **REFERRAL REQUIRED:** Deal is profitable but below target hurdle. Apply 'Give-Gets' below.")

        # --- THE SOLVER (WHAT IF) ---
        with st.expander("🔧 Margin Fixer (Solve for X)", expanded=True):
            target_profit = total_revenue * (hurdle_rate / 100) # This is approximate for the solver
            gap = (total_cost / (1 - (hurdle_rate/100))) - total_revenue
            
            if gap > 0:
                st.write(f"To reach **{hurdle_rate}% Margin**, you need **${gap:,.0f}** in additional revenue.")
                st.markdown("### Options to close the gap:")
                
                req_fx = gap / (fx_spread_bps / 10000)
                req_admin = gap / (aum / 10000)
                
                st.markdown(f"""
                * **Option A (FX):** Get client to commit to **${req_fx/1_000_000:,.1f}M** more in FX Flow.
                * **Option B (Fees):** Raise Admin Fee by **{req_admin:.2f} bps**.
                * **Option C (Hard Limits):** Implement a hard cap on manual trades/reports.
                """)

# --- TAB 2: DECISION TREES ---
elif navigation == "Decision Trees":
    st.header("🌳 Negotiation Decision Trees")
    
    tab1, tab2 = st.tabs(["The 'Rate Card' Challenge", "The 'Small Launch' Trap"])
    
    with tab1:
        st.subheader("Scenario: Competitor is Cheaper")
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
                    st.error("🛑 **DO NOT MATCH.** Sell our Valuation Team expertise. High complexity requires high fees.")
        
        elif q1 == "No":
            st.error("🛑 **STOP.** Do not lower price. Pivot to a 'Ramp-Up' model (discount Year 1 only).")

    with tab2:
        st.subheader("Scenario: The Small Launch ($20M AUM)")
        st.info("Sales: 'They will be $500M in two years! Give them a break now.'")
        
        sq1 = st.radio("Does the Minimum Monthly Fee (MMF) cover fixed costs?", ["Select...", "Yes", "No"], index=0, key="sq1")
        
        if sq1 == "No":
            st.error("🛑 **STOP.** Raise the MMF. We cannot subsidize their startup costs.")
        elif sq1 == "Yes":
            st.markdown("⬇️")
            sq2 = st.radio("Does the deal structure include tiered breakpoints?", ["Select...", "Yes", "No"], index=0, key="sq2")
            
            if sq2 == "No":
                st.warning("⚠️ **Counter-Propose:** Offer 10bps on first $50M, 6bps on next $50M. Incentivize growth.")
            elif sq2 == "Yes":
                st.success("✅ **PROCEED.** Ensure Implementation Fees are paid upfront.")

# --- TAB 3: CHEAT SHEET ---
elif navigation == "Negotiation Cheat Sheet":
    st.header("🛡️ The 'Give-Get' Cheat Sheet")
    st.markdown("Never concede on price without extracting value elsewhere.")
    
    with st.expander("1. IF they want Lower Admin Bps...", expanded=True):
        st.markdown("""
        **You ask for:** Longer Contract Term (3-5 Years).
        * **The Script:** *"I can get to that number, but that is a 'Partner Price,' not a 'Vendor Price.' I need a 3-year term to amortize the setup costs."*
        """)
        
    with st.expander("2. IF they want Waived Implementation Fees..."):
        st.markdown("""
        **You ask for:** Higher Minimum Monthly Fee (MMF).
        * **The Script:** *"I can waive the setup fee to help your Day 1 cash flow, but I need to keep the MMF steady to cover the ongoing compliance costs."*
        """)
        
    with st.expander("3. IF they want Lower Custody Fees..."):
        st.markdown("""
        **You ask for:** Exclusivity on FX & Cash.
        * **The Script:** *"The real cost to you isn't the custody bp, it's the operational drag of unbundled FX. If you give us the FX flow, I can suppress the custody fee."*
        """)

    with st.expander("4. IF they want Custom Reporting..."):
        st.markdown("""
        **You ask for:** Standard/Hard-coded Pricing for 'Extra' Reports.
        * **The Script:** *"Happy to build that, but bespoke work falls outside the standard SLA. We bill customization at a per-hour rate."*
        """)

    st.markdown("### 🚫 The Red Lines (Non-Negotiables)")
    st.error("""
    1.  **Liability Caps:** Never unlimited. Cap at 12-24 months fees.
    2.  **CPI / COLA:** Contracts must have inflation adjustment clauses.
    3.  **Pass-Throughs:** Tech, Legal, and SWIFT costs are billable to client.
    """)
