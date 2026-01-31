"""
Upload Page - File upload and processing
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path
import time
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.api_client import APIClient
from config import API_BASE_URL

# Page config
st.set_page_config(page_title="Upload - Hometown", page_icon="📤", layout="wide")

# Initialize API client
if 'api_client' not in st.session_state:
    st.session_state.api_client = APIClient(API_BASE_URL)

api_client = st.session_state.api_client

st.title("📤 Upload Sales Data")

st.markdown("""
Upload your Excel file containing sales data to calculate incentives.

**Required Sheet**: `Sales Report - Hometown (2)`

**Required Columns**:
- Store Code, Name, Sales_Doc, Sales Date
- LOB, Bill No, Salesman
- Sum of NET SALES VALUE, Sum of Sales value Without GST
- SM, DM
""")

st.divider()

# File uploader
uploaded_file = st.file_uploader(
    "Choose an Excel file (.xlsx)",
    type=['xlsx'],
    help="Upload the BI export with 'Sales Report - Hometown (2)' sheet"
)

if uploaded_file:
    # Show file info
    st.info(f"📄 **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")

    # Validate file
    try:
        with st.spinner("Validating file..."):
            preview = pd.read_excel(uploaded_file, sheet_name='Sales Report - Hometown (2)', nrows=5)

            required_cols = [
                'Store Code', 'Name', 'Sales_Doc', 'Sales Date', 'LOB', 'Bill No', 'Salesman',
                'Sum of NET SALES VALUE', 'Sum of Sales value Without GST', 'SM', 'DM'
            ]

            missing_cols = [col for col in required_cols if col not in preview.columns]

            if missing_cols:
                st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
            else:
                st.success("✅ File validated successfully!")

                # Preview table
                with st.expander("Preview (first 5 rows)", expanded=True):
                    st.dataframe(preview, use_container_width=True)

                st.divider()

                # Process button
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    process_button = st.button("🚀 Process File", type="primary", use_container_width=True)

                if process_button:
                    try:
                        # Reset file pointer
                        uploaded_file.seek(0)

                        # Step 1: Upload
                        with st.spinner("Uploading file..."):
                            file_id = api_client.upload(uploaded_file)
                            st.success(f"✅ File uploaded (ID: {file_id[:8]}...)")

                        # Step 2: Trigger processing
                        with st.spinner("Starting processing..."):
                            job_id = api_client.process(file_id)
                            st.success(f"✅ Processing started (Job ID: {job_id[:8]}...)")

                        # Step 3: Poll status
                        progress_bar = st.progress(0)
                        status_text = st.empty()

                        while True:
                            status = api_client.get_status(job_id)
                            progress_bar.progress(status['progress'])
                            status_text.text(f"Status: {status['status']} ({status['progress']}%)")

                            if status['status'] == 'completed':
                                progress_bar.progress(100)
                                st.success("✅ Processing completed!")

                                # Show summary
                                st.subheader("Results Summary")
                                col1, col2, col3, col4 = st.columns(4)
                                col1.metric("Transactions", f"{status['result']['total_transactions']:,}")
                                col2.metric("Total Incentives", f"₹{status['result']['total_incentives']:,.2f}")
                                col3.metric("Employees", status['result']['employees_count'])
                                col4.metric("Stores", status['result']['stores_count'])

                                # Download button
                                st.divider()
                                col1, col2 = st.columns([1, 2])
                                with col1:
                                    output_data = api_client.download(job_id)
                                    st.download_button(
                                        label="📥 Download Results",
                                        data=output_data,
                                        file_name=f"Hometown_Incentives_{datetime.now():%Y%m%d_%H%M%S}.xlsx",
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                        type="primary",
                                        use_container_width=True
                                    )

                                # Link to dashboard
                                st.info("👉 View detailed analytics in the **Dashboard** page")
                                st.session_state.latest_job_id = job_id
                                break

                            elif status['status'] == 'failed':
                                st.error(f"❌ Processing failed: {status.get('error', 'Unknown error')}")
                                break

                            time.sleep(1)

                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

    except Exception as e:
        st.error(f"❌ Error reading file: {str(e)}")
        st.info("💡 Make sure the file has a sheet named 'Sales Report - Hometown (2)'")

else:
    st.info("👆 Please upload an Excel file to get started")

# Sidebar
with st.sidebar:
    st.header("Instructions")
    st.markdown("""
    **Steps:**
    1. Upload the BI export Excel file
    2. Validate that all required columns are present
    3. Click "Process File" to calculate incentives
    4. Download the results when complete

    **Note:** Processing may take 10-30 seconds depending on file size.
    """)
