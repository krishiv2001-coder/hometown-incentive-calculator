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

st.title("📜 Upload History")

if not st.session_state.uploads:
    st.info("No uploads found yet. Go to the Upload page to get started!")
    st.page_link("pages/1_📤_Upload.py", label="Upload File", icon="📤")
else:
    # Summary stats
    total_incentives = sum(u['total_incentives'] for u in st.session_state.uploads)
    total_transactions = sum(u['total_transactions'] for u in st.session_state.uploads)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Uploads", len(st.session_state.uploads))
    col2.metric("Total Transactions", f"{total_transactions:,}")
    col3.metric("Total Incentives", f"₹{total_incentives:,.2f}")
    col4.metric("Latest Upload", st.session_state.uploads[-1]['timestamp'].strftime('%Y-%m-%d %H:%M'))

    st.divider()

    # History table/cards
    st.subheader("All Uploads")

    for idx, upload in enumerate(reversed(st.session_state.uploads)):
        with st.expander(
            f"📄 {upload['filename']} - {upload['timestamp'].strftime('%Y-%m-%d %H:%M')}",
            expanded=(idx == 0)
        ):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.write(f"**Upload ID**: {upload['id']}")
                st.write(f"**Upload Time**: {upload['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
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
    This page shows all uploads from your current session.

    **Actions:**
    - Download processed Excel files
    - View results in Dashboard
    - Compare multiple uploads

    **Note:** History is stored in your browser session and will be cleared when you close the browser.
    """)

    if st.session_state.uploads:
        st.divider()
        if st.button("🗑️ Clear All History", use_container_width=True):
            st.session_state.uploads = []
            st.rerun()
