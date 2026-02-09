"""
Targets & Qualifier Tracker Page
Manage targets and view qualification status
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent))

# Try multiple import methods for compatibility
try:
    from utils.calculator import apply_qualifier_logic
except ImportError:
    # For Streamlit Cloud
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.calculator import apply_qualifier_logic

# Page config
st.set_page_config(page_title="Targets - Hometown", page_icon="🎯", layout="wide")

# Initialize session state
if 'uploads' not in st.session_state:
    st.session_state.uploads = []

if 'targets' not in st.session_state:
    st.session_state.targets = {}  # Structure: targets[month][store][lob] = {aov, bills}

if 'selected_month' not in st.session_state:
    from datetime import datetime
    st.session_state.selected_month = datetime.now().strftime("%Y-%m")

st.title("🎯 Targets & Qualifier Tracker")

# Initialize target month selection if not exists
if 'target_month' not in st.session_state:
    st.session_state.target_month = st.session_state.selected_month

# Month selector for setting targets
from datetime import datetime
st.subheader("📅 Select Month for Target Entry")

# Helper function to add/subtract months
def add_months(date, months):
    """Add or subtract months from a date"""
    month = date.month - 1 + months
    year = date.year + month // 12
    month = month % 12 + 1
    return datetime(year, month, 1)

# Generate constant 16-month list (past 12 + current + next 3)
current_date = datetime.now()
available_months = []

# Add past 12 months
for i in range(12, 0, -1):
    past_month = add_months(current_date, -i)
    available_months.append(past_month.strftime("%Y-%m"))

# Add current month
available_months.append(current_date.strftime("%Y-%m"))

# Add next 3 months
for i in range(1, 4):
    future_month = add_months(current_date, i)
    available_months.append(future_month.strftime("%Y-%m"))

# Reverse to show newest first
available_months = list(reversed(available_months))

# Create month display with upload indicators
months_with_uploads = set(upload['month'] for upload in st.session_state.uploads) if st.session_state.uploads else set()
month_display_dict = {
    month: f"{datetime.strptime(month, '%Y-%m').strftime('%B %Y')} {'📁' if month in months_with_uploads else ''}"
    for month in available_months
}

selected_target_month = st.selectbox(
    "Enter/Edit targets for:",
    options=available_months,
    format_func=lambda x: month_display_dict[x],
    index=available_months.index(st.session_state.target_month) if st.session_state.target_month in available_months else 0,
    key='target_month_selector',
    help="Select which month you want to set targets for (including future months)"
)

st.session_state.target_month = selected_target_month

st.divider()

# Filter uploads by selected month for viewing achievement
month_uploads = [u for u in st.session_state.uploads if u['month'] == st.session_state.selected_month]

# Check if there are any uploads for the viewing month
if not month_uploads:
    view_month_name = datetime.strptime(st.session_state.selected_month, "%Y-%m").strftime("%B %Y")
    st.info(f"ℹ️ No uploads found for **{view_month_name}** (current filter). Targets can still be set for any month.")

    # Show a simplified targets form without achievement data
    # Get store list from any available upload or create default
    if st.session_state.uploads:
        # Get stores from most recent upload
        recent_upload = st.session_state.uploads[-1]
        qualifier_df = recent_upload['qualifier_df']
    else:
        # No uploads yet, create minimal interface
        st.warning("Upload data first to see store-specific target forms.")
        st.stop()

    # Select upload from this month
    upload_options = None
else:
    view_month_name = datetime.strptime(st.session_state.selected_month, "%Y-%m").strftime("%B %Y")
    st.info(f"📊 Viewing achievement for: **{view_month_name}**")

    # Select upload from this month
    upload_options = {
        f"{u['filename']} - {u['timestamp'].strftime('%Y-%m-%d %H:%M')}": u
        for u in month_uploads
    }

    selected_label = st.selectbox(
        "Select Upload",
        options=list(upload_options.keys()),
        index=len(upload_options) - 1  # Default to latest
    )
    selected_upload = upload_options[selected_label]

    qualifier_df = selected_upload['qualifier_df']
    summary_df = selected_upload['summary_df']

    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["📋 Set Targets", "📊 Qualifier Status", "💰 Final Payables"])

    # ==================== TAB 1: SET TARGETS ====================
    with tab1:
        st.subheader("Set Targets for Each Store × LOB")

        st.markdown("""
        Set the **Target AOV** and **Target Bills** for each store and line of business.
        Both targets must be met for incentives to be paid out.
        """)

        st.divider()

        # Get unique stores and LOBs from qualifier data
        stores = sorted(qualifier_df['Store Name'].unique())

        # Initialize targets for the target month if not exists
        if st.session_state.target_month not in st.session_state.targets:
            st.session_state.targets[st.session_state.target_month] = {}

        # Create a form for each store
        for store in stores:
            with st.expander(f"🏪 {store}", expanded=False):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Furniture Targets**")
                    furniture_aov = st.number_input(
                        "Target AOV (₹)",
                        min_value=0,
                        value=st.session_state.targets[st.session_state.target_month].get(store, {}).get('Furniture', {}).get('aov', 25000),
                        step=1000,
                        key=f"{store}_{st.session_state.target_month}_furniture_aov"
                    )
                    furniture_bills = st.number_input(
                        "Target Bills",
                        min_value=0,
                        value=st.session_state.targets[st.session_state.target_month].get(store, {}).get('Furniture', {}).get('bills', 50),
                        step=5,
                        key=f"{store}_{st.session_state.target_month}_furniture_bills"
                    )

                with col2:
                    st.markdown("**Homeware Targets**")
                    homeware_aov = st.number_input(
                        "Target AOV (₹)",
                        min_value=0,
                        value=st.session_state.targets[st.session_state.target_month].get(store, {}).get('Homeware', {}).get('aov', 8000),
                        step=1000,
                        key=f"{store}_{st.session_state.target_month}_homeware_aov"
                    )
                    homeware_bills = st.number_input(
                        "Target Bills",
                        min_value=0,
                        value=st.session_state.targets[st.session_state.target_month].get(store, {}).get('Homeware', {}).get('bills', 100),
                        step=5,
                        key=f"{store}_{st.session_state.target_month}_homeware_bills"
                    )

                # Store in session state for the target month
                if store not in st.session_state.targets[st.session_state.target_month]:
                    st.session_state.targets[st.session_state.target_month][store] = {}

                st.session_state.targets[st.session_state.target_month][store]['Furniture'] = {
                    'aov': furniture_aov,
                    'bills': furniture_bills
                }
                st.session_state.targets[st.session_state.target_month][store]['Homeware'] = {
                    'aov': homeware_aov,
                    'bills': homeware_bills
                }

        if st.button("💾 Save All Targets", type="primary"):
            try:
                from utils.database import save_targets

                # Save all targets for the selected target month to database
                month_targets = st.session_state.targets.get(st.session_state.target_month, {})
                saved_count = 0

                for store_name, lobs in month_targets.items():
                    for lob, values in lobs.items():
                        save_targets(
                            st.session_state.target_month,
                            store_name,
                            lob,
                            values['aov'],
                            values['bills']
                        )
                        saved_count += 1

                st.success(f"✅ {saved_count} targets saved to database!")
                st.balloons()
            except Exception as e:
                st.error(f"⚠️ Failed to save targets to database: {e}")
                st.info("Targets are still available in this session, but won't persist after refresh.")

    # ==================== TAB 2: QUALIFIER STATUS ====================
    with tab2:
        st.subheader("Qualifier Achievement Status")

        # Calculate qualifier status for each store × LOB
        qualifier_results = []

        # Get targets for current month
        month_targets = st.session_state.targets.get(st.session_state.selected_month, {})

        for _, row in qualifier_df.iterrows():
            store = row['Store Name']
            lob = row['LOB']

            if store in month_targets and lob in month_targets[store]:
                target_aov = month_targets[store][lob]['aov']
                target_bills = month_targets[store][lob]['bills']

                actual_aov = row['Actual AOV']
                actual_bills = row['Actual Bills']

                aov_achievement = (actual_aov / target_aov * 100) if target_aov > 0 else 0
                bills_achievement = (actual_bills / target_bills * 100) if target_bills > 0 else 0

                aov_met = actual_aov >= target_aov
                bills_met = actual_bills >= target_bills
                both_met = aov_met and bills_met

                if both_met:
                    status = "✅ BOTH MET"
                    status_color = "🟢"
                elif aov_met:
                    status = "⚠️ AOV Met, Bills Short"
                    status_color = "🟡"
                elif bills_met:
                    status = "⚠️ Bills Met, AOV Short"
                    status_color = "🟡"
                else:
                    status = "❌ BOTH SHORT"
                    status_color = "🔴"

                qualifier_results.append({
                    'Store Name': store,
                    'LOB': lob,
                    'Actual AOV': f"₹{actual_aov:,.0f}",
                    'Target AOV': f"₹{target_aov:,.0f}",
                    'AOV %': f"{aov_achievement:.1f}%",
                    'Actual Bills': actual_bills,
                    'Target Bills': target_bills,
                    'Bills %': f"{bills_achievement:.1f}%",
                    'Status': f"{status_color} {status}",
                    'Qualified': both_met
                })

        if qualifier_results:
            results_df = pd.DataFrame(qualifier_results)

            # Summary metrics
            col1, col2, col3 = st.columns(3)
            total_combinations = len(results_df)
            qualified_count = results_df['Qualified'].sum()
            qualification_rate = (qualified_count / total_combinations * 100) if total_combinations > 0 else 0

            col1.metric("Total Store × LOB", total_combinations)
            col2.metric("Qualified", qualified_count)
            col3.metric("Qualification Rate", f"{qualification_rate:.1f}%")

            st.divider()

            # Display table
            st.dataframe(
                results_df.drop('Qualified', axis=1),
                use_container_width=True,
                hide_index=True
            )

            # Detailed view
            st.divider()
            st.subheader("Detailed Breakdown by Store")

            for store in results_df['Store Name'].unique():
                store_data = results_df[results_df['Store Name'] == store]

                with st.expander(f"🏪 {store}", expanded=False):
                    for _, row in store_data.iterrows():
                        col1, col2 = st.columns([1, 1])

                        with col1:
                            st.markdown(f"### {row['LOB']}")
                            st.markdown(f"**Status:** {row['Status']}")

                        with col2:
                            st.markdown("#### Metrics")
                            st.write(f"AOV: {row['Actual AOV']} / {row['Target AOV']} ({row['AOV %']})")
                            st.write(f"Bills: {row['Actual Bills']} / {row['Target Bills']} ({row['Bills %']})")

                        st.divider()
        else:
            st.info("Set targets in the 'Set Targets' tab to see qualifier status.")

    # ==================== TAB 3: FINAL PAYABLES ====================
    with tab3:
        st.subheader("Final Payable Incentives")

        st.markdown("""
        **Accrued Points** = Incentive points earned (before qualifiers)
        **Final Payable** = Actual incentives to be paid (after applying qualifiers)
        """)

        st.divider()

        # Apply qualifier logic using targets for current month
        month_targets = st.session_state.targets.get(st.session_state.selected_month, {})
        if month_targets:
            summary_with_payables = apply_qualifier_logic(
                summary_df,
                qualifier_df,
                month_targets
            )

            # Overall summary
            col1, col2, col3 = st.columns(3)
            total_accrued = summary_with_payables['Total Points'].sum()
            total_payable = summary_with_payables['Final Payable Total'].sum()
            payout_rate = (total_payable / total_accrued * 100) if total_accrued > 0 else 0

            col1.metric("Total Accrued Points", f"₹{total_accrued:,.2f}")
            col2.metric("Total Final Payable", f"₹{total_payable:,.2f}", f"{payout_rate:.1f}%")
            col3.metric("Difference", f"₹{total_accrued - total_payable:,.2f}")

            st.divider()

            # Summary by LOB
            st.subheader("Summary by Line of Business")
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### Furniture")
                furn_accrued = summary_with_payables['Furniture Points'].sum()
                furn_payable = summary_with_payables['Final Payable Furniture'].sum()
                st.metric("Accrued", f"₹{furn_accrued:,.2f}")
                st.metric("Payable", f"₹{furn_payable:,.2f}")
                st.metric("Lost", f"₹{furn_accrued - furn_payable:,.2f}")

            with col2:
                st.markdown("### Homeware")
                home_accrued = summary_with_payables['Homeware Points'].sum()
                home_payable = summary_with_payables['Final Payable Homeware'].sum()
                st.metric("Accrued", f"₹{home_accrued:,.2f}")
                st.metric("Payable", f"₹{home_payable:,.2f}")
                st.metric("Lost", f"₹{home_accrued - home_payable:,.2f}")

            st.divider()

            # Employee-level breakdown
            st.subheader("Employee-Level Breakdown")

            # Add comparison columns
            display_df = summary_with_payables[[
                'Store Name', 'Employee', 'Role',
                'Furniture Points', 'Final Payable Furniture',
                'Homeware Points', 'Final Payable Homeware',
                'Total Points', 'Final Payable Total'
            ]].copy()

            st.dataframe(
                display_df,
                use_container_width=True,
                column_config={
                    "Store Name": "Store",
                    "Employee": "Employee",
                    "Role": "Role",
                    "Furniture Points": st.column_config.NumberColumn("Furniture Accrued", format="₹%.2f"),
                    "Final Payable Furniture": st.column_config.NumberColumn("Furniture Payable", format="₹%.2f"),
                    "Homeware Points": st.column_config.NumberColumn("Homeware Accrued", format="₹%.2f"),
                    "Final Payable Homeware": st.column_config.NumberColumn("Homeware Payable", format="₹%.2f"),
                    "Total Points": st.column_config.NumberColumn("Total Accrued", format="₹%.2f"),
                    "Final Payable Total": st.column_config.NumberColumn("Total Payable", format="₹%.2f")
                },
                hide_index=True
            )

            # Download button
            st.divider()
            import io
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                display_df.to_excel(writer, sheet_name='Final Payables', index=False)
                results_df.drop('Qualified', axis=1).to_excel(writer, sheet_name='Qualifier Status', index=False)
            output.seek(0)

            st.download_button(
                label="📥 Download Final Payables Report",
                data=output,
                file_name=f"Final_Payables_{selected_upload['timestamp'].strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )

        else:
            st.info("Please set targets in the 'Set Targets' tab first.")

# Sidebar
with st.sidebar:
    st.header("About Qualifiers")
    st.markdown("""
    **Qualifier Rules:**
    - Both AOV and Bills targets must be met
    - Evaluated separately per Store × LOB
    - Furniture and Homeware independent

    **Payout Logic:**
    - ✅ Both met → Full payout
    - ❌ Either/both not met → Zero payout

    **Example:**
    - Store meets Furniture targets → Furniture incentives paid
    - Store fails Homeware targets → Homeware incentives = ₹0
    """)

    if st.session_state.uploads:
        st.divider()
        st.metric("Total Uploads", len(st.session_state.uploads))
        if st.session_state.targets:
            st.metric("Stores with Targets", len(st.session_state.targets))
