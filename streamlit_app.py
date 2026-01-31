"""
Hometown Incentive Calculator - Main Page
Full-featured cloud version
"""
import streamlit as st

# Page config - MUST be first Streamlit command
st.set_page_config(
    page_title="Hometown Incentive Calculator",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for storing uploads
if 'uploads' not in st.session_state:
    st.session_state.uploads = []

# Main page
st.title("🏠 Hometown Incentive Calculator")

st.markdown("""
Welcome to the **Hometown Sales Incentive Automation System**.

This tool automates the calculation of employee incentives from raw sales data.

### Quick Start
1. **📤 Upload**: Upload your sales data Excel file
2. **📊 Dashboard**: View analytics and performance metrics
3. **📜 History**: Browse past uploads and download results

---
""")

# Show latest upload stats if any
if st.session_state.uploads:
    latest = st.session_state.uploads[-1]
    st.subheader("Latest Upload")

    col1, col2, col3 = st.columns(3)
    col1.metric("Filename", latest['filename'])
    col2.metric("Upload Time", latest['timestamp'].strftime('%Y-%m-%d %H:%M'))
    col3.metric("Status", "✅ Completed")

    st.subheader("Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Incentives", f"₹{latest['total_incentives']:,.2f}")
    col2.metric("Transactions", f"{latest['total_transactions']:,}")
    col3.metric("Employees", latest['employees_count'])
    col4.metric("Stores", latest['stores_count'])

    st.info("👉 Go to **Dashboard** to view detailed analytics or **History** to see all uploads")
else:
    st.info("👆 No uploads yet. Go to the **Upload** page to get started!")

# Sidebar
with st.sidebar:
    st.header("About")
    st.markdown("""
    **Hometown Incentive Calculator**

    Version: 2.0.0 (Cloud Edition)

    This system calculates employee incentives based on:
    - Sales slabs (Furniture/Homeware)
    - Employee roles (PE/SM/DM)
    - Performance metrics

    ---

    **Features:**
    - 📤 Upload Excel files
    - 📊 Interactive dashboards
    - 📜 Upload history
    - 📥 Download results

    ---

    **Total Uploads**: {len(st.session_state.uploads)}
    """)

    if st.session_state.uploads:
        total_incentives = sum(u['total_incentives'] for u in st.session_state.uploads)
        st.metric("Total Incentives Calculated", f"₹{total_incentives:,.2f}")
