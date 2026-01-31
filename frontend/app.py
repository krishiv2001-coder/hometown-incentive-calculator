"""
Main Streamlit Application - Home Page
"""
import streamlit as st
from services.api_client import APIClient
from config import API_BASE_URL, PAGE_TITLE, PAGE_ICON

# Page configuration
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize API client
if 'api_client' not in st.session_state:
    st.session_state.api_client = APIClient(API_BASE_URL)

api_client = st.session_state.api_client

# Main content
st.title(f"{PAGE_ICON} {PAGE_TITLE}")

st.markdown("""
Welcome to the **Hometown Sales Incentive Automation System**.

This tool automates the calculation of employee incentives from raw sales data.

### Quick Start
1. **📤 Upload**: Upload your sales data Excel file
2. **📊 Dashboard**: View analytics and performance metrics
3. **📜 History**: Browse past uploads and download results

---
""")

# Check API connection
with st.spinner("Checking API connection..."):
    if api_client.health_check():
        st.success("✅ Connected to backend API")

        # Show latest upload stats if any
        try:
            history = api_client.get_history(limit=1)
            if history:
                latest = history[0]
                st.subheader("Latest Upload")

                col1, col2, col3 = st.columns(3)
                col1.metric("Filename", latest['filename'])
                col2.metric("Upload Time", latest['upload_time'][:19])
                col3.metric("Status", latest['status'].upper())

                if latest['status'] == 'completed':
                    st.subheader("Summary")
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Total Incentives", f"₹{latest['total_incentives']:,.2f}")
                    col2.metric("Transactions", f"{latest['total_transactions']:,}")
                    col3.metric("Employees", latest['employees_count'])
                    col4.metric("Stores", latest['stores_count'])
        except:
            pass
    else:
        st.error("""
        ❌ **Cannot connect to backend API**

        Please ensure the backend server is running:
        ```
        python -m uvicorn backend.main:app --reload
        ```

        Or use the provided batch file:
        ```
        run_backend.bat
        ```
        """)

# Sidebar
with st.sidebar:
    st.header("About")
    st.markdown("""
    **Hometown Incentive Calculator**

    Version: 1.0.0

    This system calculates employee incentives based on:
    - Sales slabs (Furniture/Homeware)
    - Employee roles (PE/SM/DM)
    - Target achievements (AOV & Bills)

    ---

    **Need Help?**
    - Check the Upload page for instructions
    - View the implementation documentation
    """)

    st.divider()

    st.markdown("**System Status**")
    if api_client.health_check():
        st.success("API: Online")
    else:
        st.error("API: Offline")
