"""
Dashboard Page - Analytics and visualizations
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.charts import (
    create_store_performance_chart,
    create_lob_breakdown_chart,
    create_top_performers_chart,
    create_role_distribution_chart,
    create_store_comparison_chart
)

# Page config
st.set_page_config(page_title="Dashboard - Hometown", page_icon="📊", layout="wide")

# Initialize session state
if 'uploads' not in st.session_state:
    st.session_state.uploads = []
if 'selected_month' not in st.session_state:
    from datetime import datetime
    st.session_state.selected_month = datetime.now().strftime("%Y-%m")
if 'targets' not in st.session_state:
    st.session_state.targets = {}

st.title("📊 Analytics Dashboard")

# Filter uploads by selected month
month_uploads = [u for u in st.session_state.uploads if u['month'] == st.session_state.selected_month]

# Check if there are any uploads for this month
if not month_uploads:
    from datetime import datetime
    month_name = datetime.strptime(st.session_state.selected_month, "%Y-%m").strftime("%B %Y")
    st.warning(f"⚠️ No uploads found for {month_name}. Please upload a file or select a different month.")
    st.info("👉 Go to the **📤 Upload** page from the sidebar to upload data.")
else:
    # Show selected month
    from datetime import datetime
    month_name = datetime.strptime(st.session_state.selected_month, "%Y-%m").strftime("%B %Y")
    st.info(f"📅 Viewing data for: **{month_name}**")

    # Progress Tracker Notice
    st.warning("📊 **Progress Tracker** - This shows snapshot data for tracking purposes only. Actual payouts are calculated from Final/Month-End uploads on the Monthly Summary page.")

    # Select upload snapshot to view
    upload_options = {}
    for u in month_uploads:
        # Create display label with data_as_of_date and final indicator
        data_as_of_str = u['data_as_of_date'].strftime('%b %d, %Y') if 'data_as_of_date' in u else u['timestamp'].strftime('%b %d, %Y')
        final_indicator = " 🔒 FINAL" if u.get('is_final', False) else ""
        label = f"Data as of {data_as_of_str}{final_indicator}"
        upload_options[label] = u

    selected_label = st.selectbox(
        "Select Data Snapshot",
        options=list(upload_options.keys()),
        index=len(upload_options) - 1,  # Default to latest
        help="View different snapshots of data to track progress over time"
    )
    selected_upload = upload_options[selected_label]

    summary_df = selected_upload['summary_df']
    df = selected_upload['transactions_df']

    # KPI Cards
    st.subheader("Overview")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Sales", f"₹{df['Sum of Sales value Without GST'].sum():,.0f}")
    col2.metric("Total Incentives", f"₹{selected_upload['total_incentives']:,.2f}")
    col3.metric("Transactions", f"{selected_upload['total_transactions']:,}")
    col4.metric("Employees", selected_upload['employees_count'])
    col5.metric("Stores", selected_upload['stores_count'])

    st.divider()

    # Qualifier Status & Target Progress (Rolling Basis)
    st.subheader("🎯 Target Progress & Qualification Status")
    st.caption("Based on current snapshot - Actual payouts calculated from Final/Month-End upload only")

    # Get targets for this month
    month_targets = st.session_state.targets.get(st.session_state.selected_month, {})

    if month_targets and 'qualifier_df' in selected_upload:
        qualifier_df = selected_upload['qualifier_df']

        # Create qualifier status table
        qualifier_status = []
        for _, row in qualifier_df.iterrows():
            store = row['Store Name']
            lob = row['LOB']
            actual_aov = row['Actual AOV']
            actual_bills = row['Actual Bills']

            # Get targets for this store and LOB
            if store in month_targets and lob in month_targets[store]:
                target_aov = month_targets[store][lob].get('aov', 0)
                target_bills = month_targets[store][lob].get('bills', 0)

                # Calculate progress percentages
                aov_progress = (actual_aov / target_aov * 100) if target_aov > 0 else 0
                bills_progress = (actual_bills / target_bills * 100) if target_bills > 0 else 0

                # Check if both targets are met
                aov_met = actual_aov >= target_aov
                bills_met = actual_bills >= target_bills
                both_met = aov_met and bills_met

                qualifier_status.append({
                    'Store': store,
                    'LOB': lob,
                    'Target AOV': f"₹{target_aov:,.0f}",
                    'Actual AOV': f"₹{actual_aov:,.0f}",
                    'AOV Progress': f"{aov_progress:.1f}%",
                    'AOV Status': '✅' if aov_met else '❌',
                    'Target Bills': target_bills,
                    'Actual Bills': actual_bills,
                    'Bills Progress': f"{bills_progress:.1f}%",
                    'Bills Status': '✅' if bills_met else '❌',
                    'Qualified': '✅ YES' if both_met else '❌ NO'
                })

        if qualifier_status:
            qualifier_status_df = pd.DataFrame(qualifier_status)
            st.dataframe(
                qualifier_status_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Store": "Store",
                    "LOB": "LOB",
                    "Target AOV": "Target AOV",
                    "Actual AOV": "Current AOV",
                    "AOV Progress": "AOV %",
                    "AOV Status": "AOV",
                    "Target Bills": "Target Bills",
                    "Actual Bills": "Current Bills",
                    "Bills Progress": "Bills %",
                    "Bills Status": "Bills",
                    "Qualified": "Payout Eligible"
                }
            )

            # Show potential payout if qualified
            from utils.calculator import apply_qualifier_logic

            # Apply qualifier logic to current snapshot
            current_summary_with_payout = apply_qualifier_logic(
                summary_df.copy(),
                qualifier_df,
                month_targets
            )

            # Calculate potential payout
            total_accrued = summary_df['Total Points'].sum()
            potential_payout = current_summary_with_payout['Total Points'].sum()
            disqualified_amount = total_accrued - potential_payout

            col1, col2, col3 = st.columns(3)
            col1.metric("💰 Total Points Accrued", f"₹{total_accrued:,.2f}")
            col2.metric("✅ Potential Payout (if qualified)", f"₹{potential_payout:,.2f}", delta=f"-₹{disqualified_amount:,.2f}" if disqualified_amount > 0 else None)
            col3.metric("❌ Disqualified Points", f"₹{disqualified_amount:,.2f}")

            st.info("💡 **Note:** This shows potential payouts based on current data. Only employees whose Store × LOB meets BOTH AOV and Bills targets are eligible. Actual payouts calculated from Final/Month-End upload.")
        else:
            st.info("No matching targets found for the stores and LOBs in this upload.")
    else:
        st.warning("⚠️ No targets set for this month. Go to the **🎯 Targets** page to set targets.")

    st.divider()

    # Filters
    with st.sidebar:
        st.header("Filters")
        stores = ['All'] + sorted(summary_df['Store Name'].unique().tolist())
        selected_stores = st.multiselect(
            "Store",
            options=stores[1:],  # Exclude 'All'
            default=[]
        )
        selected_roles = st.multiselect(
            "Role",
            options=['PE', 'SM', 'DM'],
            default=[]
        )

    # Apply filters
    filtered_summary = summary_df.copy()
    if selected_stores:
        filtered_summary = filtered_summary[filtered_summary['Store Name'].isin(selected_stores)]
    if selected_roles:
        filtered_summary = filtered_summary[filtered_summary['Role'].isin(selected_roles)]

    # Charts
    st.subheader("Performance Analysis")

    if len(filtered_summary) > 0:
        col1, col2 = st.columns(2)

        with col1:
            # Store Performance
            fig1 = create_store_performance_chart(filtered_summary)
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            # LOB Breakdown
            fig2 = create_lob_breakdown_chart(filtered_summary)
            st.plotly_chart(fig2, use_container_width=True)

        col3, col4 = st.columns(2)

        with col3:
            # Top Performers
            fig3 = create_top_performers_chart(filtered_summary, top_n=10)
            st.plotly_chart(fig3, use_container_width=True)

        with col4:
            # Role Distribution
            fig5 = create_role_distribution_chart(filtered_summary)
            st.plotly_chart(fig5, use_container_width=True)

        # Full-width chart
        st.subheader("Store Comparison: Furniture vs Homeware")
        fig6 = create_store_comparison_chart(filtered_summary)
        st.plotly_chart(fig6, use_container_width=True)

        st.divider()

        # Top Performers Table (exclude "No Name")
        st.subheader("🏆 Top 10 Performers")

        # Create stable dataframe to prevent shaking
        if len(filtered_summary) > 0:
            # Filter and sort in one go
            top_10_df = (
                filtered_summary[filtered_summary['Employee'] != 'No Name']
                .nlargest(10, 'Total Points', keep='first')
                [['Employee', 'Store Name', 'Role', 'Furniture Points', 'Homeware Points', 'Total Points']]
                .copy()
            )
            top_10_df = top_10_df.reset_index(drop=True)

            # Use container to stabilize rendering
            top_performers_container = st.container()
            with top_performers_container:
                st.dataframe(
                    top_10_df,
                    use_container_width=True,
                    column_config={
                        "Employee": "Employee",
                        "Store Name": "Store",
                        "Role": "Role",
                        "Furniture Points": st.column_config.NumberColumn("Furniture", format="₹%.2f"),
                        "Homeware Points": st.column_config.NumberColumn("Homeware", format="₹%.2f"),
                        "Total Points": st.column_config.NumberColumn("Total", format="₹%.2f")
                    },
                    hide_index=True
                )
        else:
            st.info("No performers to display after filtering.")

        st.divider()

        # Employee Summary Table
        st.subheader("👥 Employee Summary")
        st.dataframe(
            filtered_summary,
            use_container_width=True,
            column_config={
                "Store Code": "Code",
                "Store Name": "Store",
                "Employee": "Employee",
                "Role": "Role",
                "Furniture Points": st.column_config.NumberColumn("Furniture", format="₹%.2f"),
                "Homeware Points": st.column_config.NumberColumn("Homeware", format="₹%.2f"),
                "Total Points": st.column_config.NumberColumn("Total", format="₹%.2f")
            },
            hide_index=True
        )
    else:
        st.warning("No data matches the selected filters.")

# Sidebar stats
with st.sidebar:
    if month_uploads:
        st.divider()
        st.subheader("Month Stats")
        st.metric("Uploads This Month", len(month_uploads))
        total_month = sum(u['total_incentives'] for u in month_uploads)
        st.metric("Total Incentives", f"₹{total_month:,.2f}")
