"""
Monthly Summary Page - Final payouts after qualifier logic
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from utils.calculator import apply_qualifier_logic
except ImportError:
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.calculator import apply_qualifier_logic

# Page config
st.set_page_config(page_title="Monthly Summary - Hometown", page_icon="📊", layout="wide")

# Initialize session state
if 'uploads' not in st.session_state:
    st.session_state.uploads = []
if 'selected_month' not in st.session_state:
    st.session_state.selected_month = datetime.now().strftime("%Y-%m")
if 'targets' not in st.session_state:
    st.session_state.targets = {}

st.title("📊 Monthly Summary & Final Payouts")

# Filter uploads by selected month
month_uploads = [u for u in st.session_state.uploads if u['month'] == st.session_state.selected_month]

if not month_uploads:
    month_name = datetime.strptime(st.session_state.selected_month, "%Y-%m").strftime("%B %Y")
    st.warning(f"⚠️ No uploads found for {month_name}. Please upload data or select a different month.")
    st.info("👉 Go to the **📤 Upload** page from the sidebar to upload data.")
else:
    month_name = datetime.strptime(st.session_state.selected_month, "%Y-%m").strftime("%B %Y")
    st.info(f"📅 Summary for: **{month_name}**")

    # Filter for FINAL uploads only
    final_uploads = [u for u in month_uploads if u.get('is_final', False)]

    if not final_uploads:
        st.error("🔒 **No Final/Month-End Upload Found**")
        st.warning(f"""
        This page calculates actual payouts based on **Final/Month-End data only**.

        You have {len(month_uploads)} upload(s) for {month_name}, but none are marked as Final.

        **To set final payouts:**
        1. Go to the **📤 Upload** page
        2. Upload the month-end data
        3. Check the "✅ Mark as Final/Month-End Upload" box
        4. Process the file

        💡 Use the **📊 Dashboard** page to view progress snapshots.
        """)
        st.stop()

    # Use the latest final upload if multiple exist
    final_upload = sorted(final_uploads, key=lambda x: x['timestamp'])[-1]

    if len(final_uploads) > 1:
        st.info(f"ℹ️ Multiple final uploads found. Using the latest one (uploaded {final_upload['timestamp'].strftime('%Y-%m-%d %H:%M')})")

    st.success(f"🔒 **Using Final Upload** - Data as of {final_upload['data_as_of_date'].strftime('%B %d, %Y') if 'data_as_of_date' in final_upload else 'N/A'}")

    # Use only the final upload data (no aggregation)
    st.subheader("Month-End Overview")

    all_transactions = final_upload['transactions_df']
    monthly_summary = final_upload['summary_df'].copy()
    monthly_qualifiers = final_upload['qualifier_df'].copy()

    # Show stats from final upload
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Final Upload Date", final_upload['data_as_of_date'].strftime('%b %d') if 'data_as_of_date' in final_upload else 'N/A')
    col2.metric("Total Transactions", f"{len(all_transactions):,}")
    col3.metric("Accrued Points", f"₹{monthly_summary['Total Points'].sum():,.2f}")
    col4.metric("Unique Employees", len(monthly_summary))

    st.divider()

    # Apply qualifier logic
    st.subheader("🎯 Qualifier Status & Final Payouts")

    # Get targets for current month
    month_targets = st.session_state.targets.get(st.session_state.selected_month, {})

    if month_targets:
        # Show qualifier status
        qualifier_data = []
        for _, row in monthly_qualifiers.iterrows():
            store = row['Store Name']
            lob = row['LOB']
            actual_aov = row['Actual AOV']
            actual_bills = row['Actual Bills']

            if store in month_targets and lob in month_targets[store]:
                target_aov = month_targets[store][lob]['aov']
                target_bills = month_targets[store][lob]['bills']

                aov_met = actual_aov >= target_aov
                bills_met = actual_bills >= target_bills
                qualified = aov_met and bills_met

                if qualified:
                    status = "✅ Qualified"
                elif aov_met:
                    status = "⚠️ AOV Met, Bills Short"
                elif bills_met:
                    status = "⚠️ Bills Met, AOV Short"
                else:
                    status = "❌ Not Qualified"

                aov_achievement = (actual_aov / target_aov * 100) if target_aov > 0 else 0
                bills_achievement = (actual_bills / target_bills * 100) if target_bills > 0 else 0

                qualifier_data.append({
                    'Store': store,
                    'LOB': lob,
                    'Actual AOV': f"₹{actual_aov:,.0f}",
                    'Target AOV': f"₹{target_aov:,.0f}",
                    'AOV %': f"{aov_achievement:.1f}%",
                    'Actual Bills': int(actual_bills),
                    'Target Bills': int(target_bills),
                    'Bills %': f"{bills_achievement:.1f}%",
                    'Status': status,
                    'Qualified': qualified
                })

        if qualifier_data:
            qualifier_status_df = pd.DataFrame(qualifier_data)

            st.dataframe(
                qualifier_status_df.drop(columns=['Qualified']),
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            # Calculate final payables
            st.subheader("💰 Final Payables")

            final_summary = apply_qualifier_logic(monthly_summary, monthly_qualifiers, month_targets)

            # Exclude "No Name" from final summary display
            final_summary_display = final_summary[final_summary['Employee'] != 'No Name'].copy()

            # Show comparison
            col1, col2, col3 = st.columns(3)
            col1.metric("Accrued (Furniture)", f"₹{monthly_summary['Furniture Points'].sum():,.2f}")
            col2.metric("Accrued (Homeware)", f"₹{monthly_summary['Homeware Points'].sum():,.2f}")
            col3.metric("Accrued (Total)", f"₹{monthly_summary['Total Points'].sum():,.2f}")

            st.write("")

            col1, col2, col3 = st.columns(3)
            col1.metric("Payable (Furniture)", f"₹{final_summary_display['Final Payable Furniture'].sum():,.2f}",
                       delta=f"{final_summary_display['Final Payable Furniture'].sum() - monthly_summary['Furniture Points'].sum():,.2f}")
            col2.metric("Payable (Homeware)", f"₹{final_summary_display['Final Payable Homeware'].sum():,.2f}",
                       delta=f"{final_summary_display['Final Payable Homeware'].sum() - monthly_summary['Homeware Points'].sum():,.2f}")
            col3.metric("Payable (Total)", f"₹{final_summary_display['Final Payable Total'].sum():,.2f}",
                       delta=f"{final_summary_display['Final Payable Total'].sum() - monthly_summary['Total Points'].sum():,.2f}")

            st.divider()

            # Detailed table
            st.subheader("📋 Employee-wise Final Payouts")

            final_display = final_summary_display[[
                'Store Name', 'Employee', 'Role',
                'Furniture Points', 'Final Payable Furniture',
                'Homeware Points', 'Final Payable Homeware',
                'Total Points', 'Final Payable Total'
            ]].copy()

            st.dataframe(
                final_display,
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
                    "Final Payable Total": st.column_config.NumberColumn("Total Payable", format="₹%.2f", help="Final amount to be paid after qualifier logic")
                },
                hide_index=True
            )

            # Download button
            st.divider()
            st.subheader("📥 Download Monthly Summary")

            import io
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                final_display.to_excel(writer, sheet_name='Final Payouts', index=False)
                qualifier_status_df.to_excel(writer, sheet_name='Qualifier Status', index=False)
                monthly_summary.to_excel(writer, sheet_name='Accrued Points', index=False)
            output.seek(0)

            st.download_button(
                label="📥 Download Monthly Summary Excel",
                data=output,
                file_name=f"Monthly_Summary_{st.session_state.selected_month}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )

        else:
            st.warning("No qualifier data available. Please ensure targets are set for all stores.")
    else:
        st.warning("⚠️ No targets set. Please go to the **🎯 Targets** page from the sidebar to set AOV and Bills targets before calculating final payouts.")

# Sidebar
with st.sidebar:
    st.header("About Monthly Summary")
    st.markdown("""
    This page shows the **final payouts** for the selected month after applying qualifier logic.

    **What it shows:**
    - Aggregated data from all uploads in the month
    - Qualifier status (AOV & Bills targets)
    - Accrued points vs Final payable amounts
    - Employee-wise breakdown

    **Important:**
    - Both AOV and Bills targets must be met for payout
    - Furniture and Homeware are evaluated independently
    - "No Name" entries are excluded from final payouts
    """)
