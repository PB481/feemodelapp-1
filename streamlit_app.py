import streamlit as st
import pandas as pd
from io import BytesIO

# --- Configuration ---
st.set_page_config(layout="wide", page_title="Reporting Service Pricing Model")

# --- Helper Function for HTML Report ---
def generate_html_report(data_dict, forecast_df):
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <title>Reporting Service Pricing Report</title>
    <style>
        body {{ font-family: sans-serif; margin: 20px; }}
        h1 {{ color: #2C3E50; }}
        h2 {{ color: #34495E; border-bottom: 2px solid #34495E; padding-bottom: 5px; margin-top: 30px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; color: #333; }}
        .metric-card {{
            background-color: #ECF0F1;
            border-left: 5px solid #2980B9;
            padding: 15px;
            margin-bottom: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .metric-value {{ font-size: 1.2em; font-weight: bold; color: #2980B9; }}
        .metric-label {{ font-size: 0.9em; color: #555; }}
        .highlight-green {{ color: #27AE60; font-weight: bold; }}
        .highlight-red {{ color: #C0392B; font-weight: bold; }}
    </style>
    </head>
    <body>
        <h1>Reporting Service Pricing Model Report</h1>

        <h2>Input Parameters</h2>
        <table>
            <tr><th>Parameter</th><th>Value</th></tr>
            <tr><td>Annual Vendor Cost</td><td>${data_dict['vendor_cost_usd']:,}</td></tr>
            <tr><td>Number of Resources</td><td>{int(data_dict['num_resources'])}</td></tr>
            <tr><td>Cost Per Resource</td><td>${data_dict['cost_per_resource_usd']:,}</td></tr>
            <tr><td>Number of Funds</td><td>{int(data_dict['num_funds'])}</td></tr>
            <tr><td>Desired Margin</td><td>{data_dict['margin_percent']:.2f}%</td></tr>
            <tr><td>USD to EUR Rate</td><td>{data_dict['usd_to_eur_rate']:.4f}</td></tr>
            <tr><td>USD to GBP Rate</td><td>{data_dict['usd_to_gbp_rate']:.4f}</td></tr>
        </table>

        <h2>Cost Breakdown (USD)</h2>
        <table>
            <tr><th>Category</th><th>Annual Cost (USD)</th></tr>
            <tr><td>Total Annual Cost</td><td>${data_dict['total_annual_cost_usd']:,}</td></tr>
            <tr><td>Cost Per Fund (Annual)</td><td>${data_dict['cost_per_fund_annual_usd']:,}</td></tr>
            <tr><td>Cost Per Fund (Quarterly)</td><td>${data_dict['cost_per_fund_quarterly_usd']:,}</td></tr>
            <tr><td>Cost Per Fund (Monthly)</td><td>${data_dict['cost_per_fund_monthly_usd']:,}</td></tr>
        </table>

        <h2>Pricing Model & Revenue</h2>
        <table>
            <tr><th>Metric</th><th>USD</th><th>EUR</th><th>GBP</th></tr>
            <tr><td>Selling Price Per Fund (Annual)</td><td>${data_dict['selling_price_per_fund_annual_usd']:,}</td><td>€{data_dict['selling_price_per_fund_annual_eur']:,}</td><td>£{data_dict['selling_price_per_fund_annual_gbp']:,}</td></tr>
            <tr><td>Selling Price Per Fund (Quarterly)</td><td>${data_dict['selling_price_per_fund_quarterly_usd']:,}</td><td>€{data_dict['selling_price_per_fund_quarterly_eur']:,}</td><td>£{data_dict['selling_price_per_fund_quarterly_gbp']:,}</td></tr>
            <tr><td>Selling Price Per Fund (Monthly)</td><td>${data_dict['selling_price_per_fund_monthly_usd']:,}</td><td>€{data_dict['selling_price_per_fund_monthly_eur']:,}</td><td>£{data_dict['selling_price_per_fund_monthly_gbp']:,}</td></tr>
            <tr><td>Total Potential Annual Revenue</td><td>${data_dict['total_annual_revenue_usd']:,}</td><td>€{data_dict['total_annual_revenue_eur']:,}</td><td>£{data_dict['total_annual_revenue_gbp']:,}</td></tr>
        </table>

        <h2>Key Performance Indicators (KPIs)</h2>
        <div class="metric-card">
            <div class="metric-label">Gross Profit Margin</div>
            <div class="metric-value">
                {data_dict['gross_profit_margin_percent']:.2f}%
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Return on Investment (ROI)</div>
            <div class="metric-value">
                {data_dict['roi_percent']:.2f}%
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Break-Even Point (Funds)</div>
            <div class="metric-value">
                {data_dict['break_even_funds']:.0f} funds
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Revenue Per Fund</div>
            <div class="metric-value">
                ${data_dict['revenue_per_fund_usd']:.2f}
            </div>
        </div>

        <h2>5-Year Forecast (USD)</h2>
        <table>
            <thead>
                <tr>
                    <th>Year</th>
                    <th>Cost Reduction (%)</th>
                    <th>Comment</th>
                    <th>Adjusted Annual Cost ($)</th>
                    <th>Forecasted Annual Revenue ($)</th>
                    <th>Forecasted Profit ($)</th>
                </tr>
            </thead>
            <tbody>
                """ + "".join([
                    f"""
                    <tr>
                        <td>{int(row['Year'])}</td>
                        <td>{row['Cost Reduction (%)']:.2f}%</td>
                        <td>{row['Comment']}</td>
                        <td>${row['Adjusted Annual Cost ($)']:,}</td>
                        <td>${row['Forecasted Annual Revenue ($)']:,}</td>
                        <td>${row['Forecasted Profit ($)']:,}</td>
                    </tr>
                    """ for index, row in forecast_df.iterrows()
                ]) + """
            </tbody>
        </table>

    </body>
    </html>
    """
    return html_content

# --- Streamlit App ---
st.title("💰 Reporting Service Pricing Model")
st.markdown("Calculate costs, set pricing, and forecast revenue for your reporting service.")

st.sidebar.header("Cost & Unit Inputs")
vendor_cost_usd = st.sidebar.number_input("Annual Vendor Cost (USD)", min_value=0.0, value=50000.0, step=1000.0)
num_resources = st.sidebar.number_input("Number of Resources", min_value=0, value=2, step=1)
cost_per_resource_usd = st.sidebar.number_input("Cost Per Resource (USD)", min_value=0.0, value=75000.0, step=1000.0)
num_funds = st.sidebar.number_input("Number of Funds", min_value=1, value=100, step=10)

st.sidebar.header("Pricing & FX Inputs")
margin_percent = st.sidebar.slider("Desired Profit Margin (%)", min_value=0.0, max_value=200.0, value=30.0, step=0.5)
usd_to_eur_rate = st.sidebar.number_input("USD to EUR Exchange Rate", min_value=0.5, value=0.92, step=0.01)
usd_to_gbp_rate = st.sidebar.number_input("USD to GBP Exchange Rate", min_value=0.5, value=0.79, step=0.01)

# --- Calculations ---
total_annual_cost_usd = vendor_cost_usd + (num_resources * cost_per_resource_usd)
st.subheader("📊 Annual Cost Breakdown (USD)")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Annual Cost", f"${total_annual_cost_usd:,.2f}")
with col2:
    st.metric("Vendor Cost", f"${vendor_cost_usd:,.2f}")
with col3:
    st.metric("Resource Cost", f"${num_resources * cost_per_resource_usd:,.2f}")

if num_funds > 0:
    cost_per_fund_annual_usd = total_annual_cost_usd / num_funds
    cost_per_fund_quarterly_usd = cost_per_fund_annual_usd / 4
    cost_per_fund_monthly_usd = cost_per_fund_annual_usd / 12

    st.subheader("💸 Cost Per Fund (USD)")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Annual", f"${cost_per_fund_annual_usd:,.2f}")
    with col2:
        st.metric("Quarterly", f"${cost_per_fund_quarterly_usd:,.2f}")
    with col3:
        st.metric("Monthly", f"${cost_per_fund_monthly_usd:,.2f}")

    st.subheader("💲 Pricing Model & Revenue Forecast")
    selling_price_per_fund_annual_usd = cost_per_fund_annual_usd * (1 + margin_percent / 100)
    selling_price_per_fund_quarterly_usd = selling_price_per_fund_annual_usd / 4
    selling_price_per_fund_monthly_usd = selling_price_per_fund_annual_usd / 12

    total_annual_revenue_usd = selling_price_per_fund_annual_usd * num_funds

    st.markdown("### Selling Price Per Fund (USD)")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Annual", f"${selling_price_per_fund_annual_usd:,.2f}")
    with col2:
        st.metric("Quarterly", f"${selling_price_per_fund_quarterly_usd:,.2f}")
    with col3:
        st.metric("Monthly", f"${selling_price_per_fund_monthly_usd:,.2f}")

    st.markdown("### Total Potential Annual Revenue (USD)")
    st.metric("Total Revenue", f"${total_annual_revenue_usd:,.2f}")

    st.subheader("🌍 Currency Conversion")
    st.markdown("Convert prices and revenue to EUR and GBP.")

    col_usd, col_eur, col_gbp = st.columns(3)

    with col_usd:
        st.metric("Annual Price Per Fund (USD)", f"${selling_price_per_fund_annual_usd:,.2f}")
        st.metric("Total Annual Revenue (USD)", f"${total_annual_revenue_usd:,.2f}")

    with col_eur:
        selling_price_per_fund_annual_eur = selling_price_per_fund_annual_usd * usd_to_eur_rate
        total_annual_revenue_eur = total_annual_revenue_usd * usd_to_eur_rate
        st.metric("Annual Price Per Fund (EUR)", f"€{selling_price_per_fund_annual_eur:,.2f}")
        st.metric("Total Annual Revenue (EUR)", f"€{total_annual_revenue_eur:,.2f}")

    with col_gbp:
        selling_price_per_fund_annual_gbp = selling_price_per_fund_annual_usd * usd_to_gbp_rate
        total_annual_revenue_gbp = total_annual_revenue_usd * usd_to_gbp_rate
        st.metric("Annual Price Per Fund (GBP)", f"£{selling_price_per_fund_annual_gbp:,.2f}")
        st.metric("Total Annual Revenue (GBP)", f"£{total_annual_revenue_gbp:,.2f}")

    st.subheader("📈 Key Performance Indicators (KPIs)")
    gross_profit_margin_percent = ((total_annual_revenue_usd - total_annual_cost_usd) / total_annual_revenue_usd) * 100 if total_annual_revenue_usd > 0 else 0
    roi_percent = gross_profit_margin_percent # Simple ROI as (Profit/Cost)*100, can be refined
    break_even_funds = total_annual_cost_usd / selling_price_per_fund_annual_usd if selling_price_per_fund_annual_usd > 0 else 0
    revenue_per_fund_usd = total_annual_revenue_usd / num_funds if num_funds > 0 else 0

    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    with col_kpi1:
        st.metric("Gross Profit Margin", f"{gross_profit_margin_percent:,.2f}%", help="((Total Revenue - Total Cost) / Total Revenue) * 100")
    with col_kpi2:
        st.metric("Return on Investment (ROI)", f"{roi_percent:,.2f}%", help="(Profit / Total Cost) * 100")
    with col_kpi3:
        st.metric("Break-Even Point (Funds)", f"{break_even_funds:,.0f} funds", help="Number of funds needed to cover total costs")
    with col_kpi4:
        st.metric("Revenue Per Fund", f"${revenue_per_fund_usd:,.2f}")

    st.subheader("🗓️ 5-Year Forecast with Cost Reductions")
    st.write("Model how cost reductions impact your revenue over a 5-year period.")

    forecast_data = []
    current_annual_cost = total_annual_cost_usd
    current_annual_revenue = total_annual_revenue_usd

    for year in range(1, 6):
        st.markdown(f"**Year {year}**")
        col_red, col_comm = st.columns([0.3, 0.7])
        cost_reduction_percent = col_red.number_input(f"Cost Reduction Year {year} (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1, key=f"red_{year}")
        reduction_comment = col_comm.text_input(f"Comment for Year {year} Reduction", key=f"com_{year}")

        adjusted_cost_this_year = current_annual_cost * (1 - cost_reduction_percent / 100)
        # Revenue remains based on the initial margin applied to the *current year's* adjusted cost
        # This assumes the pricing strategy (margin) stays constant relative to the costs
        forecasted_revenue_this_year = adjusted_cost_this_year * (1 + margin_percent / 100)
        forecasted_profit_this_year = forecasted_revenue_this_year - adjusted_cost_this_year

        forecast_data.append({
            "Year": year,
            "Cost Reduction (%)": cost_reduction_percent,
            "Comment": reduction_comment,
            "Adjusted Annual Cost ($)": adjusted_cost_this_year,
            "Forecasted Annual Revenue ($)": forecasted_revenue_this_year,
            "Forecasted Profit ($)": forecasted_profit_this_year
        })
        current_annual_cost = adjusted_cost_this_year # Update cost for next year's calculation

    forecast_df = pd.DataFrame(forecast_data)
    st.dataframe(forecast_df.style.format({
        "Adjusted Annual Cost ($)": "${:,.2f}",
        "Forecasted Annual Revenue ($)": "${:,.2f}",
        "Forecasted Profit ($)": "${:,.2f}",
        "Cost Reduction (%)": "{:.2f}%"
    }))

    st.subheader("📄 Report Generation")
    st.write("Download a detailed report of your pricing model.")

    report_data = {
        'vendor_cost_usd': vendor_cost_usd,
        'num_resources': num_resources,
        'cost_per_resource_usd': cost_per_resource_usd,
        'num_funds': num_funds,
        'margin_percent': margin_percent,
        'usd_to_eur_rate': usd_to_eur_rate,
        'usd_to_gbp_rate': usd_to_gbp_rate,
        'total_annual_cost_usd': total_annual_cost_usd,
        'cost_per_fund_annual_usd': cost_per_fund_annual_usd,
        'cost_per_fund_quarterly_usd': cost_per_fund_quarterly_usd,
        'cost_per_fund_monthly_usd': cost_per_fund_monthly_usd,
        'selling_price_per_fund_annual_usd': selling_price_per_fund_annual_usd,
        'selling_price_per_fund_quarterly_usd': selling_price_per_fund_quarterly_usd,
        'selling_price_per_fund_monthly_usd': selling_price_per_fund_monthly_usd,
        'total_annual_revenue_usd': total_annual_revenue_usd,
        'selling_price_per_fund_annual_eur': selling_price_per_fund_annual_eur,
        'selling_price_per_fund_annual_gbp': selling_price_per_fund_annual_gbp,
        'total_annual_revenue_eur': total_annual_revenue_eur,
        'total_annual_revenue_gbp': total_annual_revenue_gbp,
        'gross_profit_margin_percent': gross_profit_margin_percent,
        'roi_percent': roi_percent,
        'break_even_funds': break_even_funds,
        'revenue_per_fund_usd': revenue_per_fund_usd
    }

    # Generate HTML report
    html_report = generate_html_report(report_data, forecast_df)
    st.download_button(
        label="Download HTML Report",
        data=html_report,
        file_name="pricing_report.html",
        mime="text/html"
    )

    # Generate Excel report
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Main Calculations Sheet
        summary_data = {
            "Metric": [
                "Annual Vendor Cost (USD)", "Number of Resources", "Cost Per Resource (USD)",
                "Number of Funds", "Desired Profit Margin (%)", "USD to EUR Rate", "USD to GBP Rate",
                "---",
                "Total Annual Cost (USD)",
                "Cost Per Fund (Annual USD)", "Cost Per Fund (Quarterly USD)", "Cost Per Fund (Monthly USD)",
                "---",
                "Selling Price Per Fund (Annual USD)", "Selling Price Per Fund (Quarterly USD)", "Selling Price Per Fund (Monthly USD)",
                "Total Potential Annual Revenue (USD)",
                "---",
                "Selling Price Per Fund (Annual EUR)", "Total Potential Annual Revenue (EUR)",
                "Selling Price Per Fund (Annual GBP)", "Total Potential Annual Revenue (GBP)",
                "---",
                "Gross Profit Margin (%)", "Return on Investment (ROI) (%)", "Break-Even Point (Funds)", "Revenue Per Fund (USD)"
            ],
            "Value": [
                vendor_cost_usd, num_resources, cost_per_resource_usd,
                num_funds, margin_percent, usd_to_eur_rate, usd_to_gbp_rate,
                "---",
                total_annual_cost_usd,
                cost_per_fund_annual_usd, cost_per_fund_quarterly_usd, cost_per_fund_monthly_usd,
                "---",
                selling_price_per_fund_annual_usd, selling_price_per_fund_quarterly_usd, selling_price_per_fund_monthly_usd,
                total_annual_revenue_usd,
                "---",
                selling_price_per_fund_annual_eur, total_annual_revenue_eur,
                selling_price_per_fund_annual_gbp, total_annual_revenue_gbp,
                "---",
                gross_profit_margin_percent, roi_percent, break_even_funds, revenue_per_fund_usd
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)

        # 5-Year Forecast Sheet
        forecast_df.to_excel(writer, sheet_name='5-Year Forecast', index=False)

    st.download_button(
        label="Download Excel Report",
        data=output.getvalue(),
        file_name="pricing_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.warning("Please enter a number of funds greater than zero to perform calculations.")
