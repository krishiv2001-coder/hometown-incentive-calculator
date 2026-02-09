"""
History Page - View past uploads and download results
"""
import streamlit as st
import io
import pandas as pd
from datetime import datetime

# Page config
st.set_page_config(page_title="History - Hometown", page_icon="📜", layout="wide")

# Initialize session state
if 'uploads' not in st.session_state:
    st.session_state.uploads = []
if 'selected_month' not in st.session_state:
    from datetime import datetime
    st.session_state.selected_month = datetime.now().strftime("%Y-%m")

st.title("📜 Upload History")

# Filter uploads by selected month
month_uploads = [u for u in st.session_state.uploads if u['month'] == st.session_state.selected_month]

if not month_uploads:
    from datetime import datetime
    month_name = datetime.strptime(st.session_state.selected_month, "%Y-%m").strftime("%B %Y")
    st.info(f"No uploads found for {month_name}. Go to the **📤 Upload** page from the sidebar to upload data or select a different month!")
else:
    # Show selected month
    from datetime import datetime
    month_name = datetime.strptime(st.session_state.selected_month, "%Y-%m").strftime("%B %Y")
    st.info(f"📅 Viewing history for: **{month_name}**")

    # Summary stats for selected month
    total_incentives = sum(u['total_incentives'] for u in month_uploads)
    total_transactions = sum(u['total_transactions'] for u in month_uploads)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Uploads This Month", len(month_uploads))
    col2.metric("Total Transactions", f"{total_transactions:,}")
    col3.metric("Total Incentives", f"₹{total_incentives:,.2f}")
    col4.metric("Latest Upload", month_uploads[-1]['timestamp'].strftime('%Y-%m-%d %H:%M'))

    st.divider()

    # History table/cards
    st.subheader(f"Uploads for {month_name}")

    for idx, upload in enumerate(reversed(month_uploads)):
        # Create expander title with data_as_of_date and final indicator
        data_as_of_str = upload['data_as_of_date'].strftime('%b %d, %Y') if 'data_as_of_date' in upload else upload['timestamp'].strftime('%b %d, %Y')
        final_badge = " 🔒 FINAL" if upload.get('is_final', False) else " 📊"
        expander_title = f"{final_badge} Data as of {data_as_of_str} - {upload['filename']}"

        with st.expander(expander_title, expanded=(idx == 0)):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.write(f"**Upload ID**: {upload['id']}")
                st.write(f"**Upload Time**: {upload['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                st.write(f"**Data As Of**: {data_as_of_str}")
                st.write(f"**Type**: {'🔒 **Final/Month-End** (used for payout calculations)' if upload.get('is_final', False) else '📊 Progress Tracker'}")
                st.write(f"**Status**: ✅ Completed")

                st.divider()
                st.write("**Results:**")
                col_a, col_b, col_c, col_d = st.columns(4)
                col_a.metric("Incentives", f"₹{upload['total_incentives']:,.2f}")
                col_b.metric("Transactions", f"{upload['total_transactions']:,}")
                col_c.metric("Employees", upload['employees_count'])
                col_d.metric("Stores", upload['stores_count'])

            with col2:
                # Download button
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    upload['transactions_df'].to_excel(writer, sheet_name='Detailed Transactions', index=False)
                    upload['summary_df'].to_excel(writer, sheet_name='Employee Points Summary', index=False)
                output.seek(0)

                st.download_button(
                    label="📥 Download Excel",
                    data=output,
                    file_name=f"Hometown_Incentives_{upload['id']}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"dl_{upload['id']}",
                    use_container_width=True
                )

                # View dashboard button
                if st.button(f"📊 View in Dashboard", key=f"view_{upload['id']}", use_container_width=True):
                    st.session_state.current_upload = upload
                    st.switch_page("pages/2_📊_Dashboard.py")

            st.divider()

# Sidebar
with st.sidebar:
    st.header("About History")
    st.markdown("""
    This page shows uploads organized by month.

    **Actions:**
    - Download processed Excel files
    - View results in Dashboard
    - Compare uploads within a month

    **Note:** Use the month filter at the top of the sidebar to view different months.
    """)

    if st.session_state.uploads:
        st.divider()
        total_uploads = len(st.session_state.uploads)
        final_uploads = len([u for u in st.session_state.uploads if u.get('is_final', False)])
        progress_uploads = total_uploads - final_uploads

        st.metric("Total Uploads (All Months)", total_uploads)
        col_a, col_b = st.columns(2)
        col_a.metric("🔒 Final", final_uploads)
        col_b.metric("📊 Progress", progress_uploads)

        # Group uploads by month
        from collections import defaultdict
        uploads_by_month = defaultdict(int)
        for u in st.session_state.uploads:
            uploads_by_month[u['month']] += 1

        st.write("**By Month:**")
        for month in sorted(uploads_by_month.keys(), reverse=True):
            month_display = datetime.strptime(month, "%Y-%m").strftime("%b %Y")
            st.write(f"- {month_display}: {uploads_by_month[month]} uploads")

        st.divider()
        if st.button("🗑️ Clear All History", use_container_width=True):
            st.session_state.uploads = []
            st.rerun()
