"""
History Page - View past uploads and download results
"""
import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.api_client import APIClient
from config import API_BASE_URL

# Page config
st.set_page_config(page_title="History - Hometown", page_icon="📜", layout="wide")

# Initialize API client
if 'api_client' not in st.session_state:
    st.session_state.api_client = APIClient(API_BASE_URL)

api_client = st.session_state.api_client

st.title("📜 Upload History")

# Fetch upload history
try:
    with st.spinner("Loading history..."):
        history = api_client.get_history(limit=50)

    if not history:
        st.info("No uploads found yet. Go to the Upload page to get started!")
        st.page_link("pages/1_📤_Upload.py", label="Upload File", icon="📤")
    else:
        # Summary stats
        completed_count = sum(1 for h in history if h['status'] == 'completed')
        total_incentives = sum(h.get('total_incentives', 0) or 0 for h in history if h['status'] == 'completed')

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Uploads", len(history))
        col2.metric("Completed", completed_count)
        col3.metric("Total Incentives Paid", f"₹{total_incentives:,.2f}")
        col4.metric("Latest Upload", history[0]['upload_time'][:10] if history else "N/A")

        st.divider()

        # History table/cards
        st.subheader("All Uploads")

        for idx, upload in enumerate(history):
            with st.expander(
                f"{upload['filename']} - {upload['upload_time'][:19]} - {upload['status'].upper()}",
                expanded=(idx == 0)
            ):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.write(f"**Job ID**: `{upload['job_id'][:16]}...`")
                    st.write(f"**Status**: {upload['status'].upper()}")
                    st.write(f"**Upload Time**: {upload['upload_time'][:19]}")

                    if upload.get('file_size'):
                        st.write(f"**File Size**: {upload['file_size'] / 1024:.1f} KB")

                    if upload['status'] == 'completed':
                        st.divider()
                        st.write("**Results:**")
                        col_a, col_b, col_c, col_d = st.columns(4)
                        col_a.metric("Incentives", f"₹{upload['total_incentives']:,.2f}")
                        col_b.metric("Transactions", f"{upload['total_transactions']:,}")
                        col_c.metric("Employees", upload['employees_count'])
                        col_d.metric("Stores", upload['stores_count'])

                with col2:
                    if upload['status'] == 'completed':
                        # Download button
                        if st.button(f"📥 Download", key=f"dl_{upload['job_id']}", use_container_width=True):
                            try:
                                output_data = api_client.download(upload['job_id'])
                                st.download_button(
                                    label="💾 Save File",
                                    data=output_data,
                                    file_name=f"Hometown_Incentives_{upload['job_id'][:8]}.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    key=f"save_{upload['job_id']}",
                                    use_container_width=True
                                )
                            except Exception as e:
                                st.error(f"Error downloading: {e}")

                        # View dashboard button
                        if st.button(f"📊 View Dashboard", key=f"view_{upload['job_id']}", use_container_width=True):
                            st.session_state.latest_job_id = upload['job_id']
                            st.switch_page("pages/2_📊_Dashboard.py")

                    elif upload['status'] == 'processing':
                        st.info("⏳ Processing...")

                    elif upload['status'] == 'failed':
                        st.error("❌ Failed")

                st.divider()

except Exception as e:
    st.error(f"❌ Error loading history: {str(e)}")
    st.info("Make sure the backend server is running.")

# Sidebar
with st.sidebar:
    st.header("About History")
    st.markdown("""
    This page shows all past uploads and their processing results.

    **Actions:**
    - Download processed Excel files
    - View results in Dashboard
    - Track processing status

    **Note:** All uploads are stored permanently in the database.
    """)
