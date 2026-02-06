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

# Initialize selected month (defaults to current month or most recent upload month)
if 'selected_month' not in st.session_state:
    from datetime import datetime
    st.session_state.selected_month = datetime.now().strftime("%Y-%m")

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

# Show stats for selected month
if st.session_state.uploads:
    # Filter uploads by selected month
    month_uploads = [u for u in st.session_state.uploads if u['month'] == st.session_state.selected_month]

    if month_uploads:
        from datetime import datetime
        month_name = datetime.strptime(st.session_state.selected_month, "%Y-%m").strftime("%B %Y")
        st.subheader(f"📊 {month_name} Summary")

        # Show latest upload in this month
        latest = month_uploads[-1]
        col1, col2, col3 = st.columns(3)
        col1.metric("Latest File", latest['filename'])
        col2.metric("Upload Time", latest['timestamp'].strftime('%Y-%m-%d %H:%M'))
        col3.metric("Total Uploads", len(month_uploads))

        # Aggregate stats for the month
        total_incentives = sum(u['total_incentives'] for u in month_uploads)
        total_transactions = sum(u['total_transactions'] for u in month_uploads)
        unique_employees = len(set(emp for u in month_uploads for emp in u['summary_df']['Employee'].values))
        unique_stores = len(set(store for u in month_uploads for store in u['transactions_df']['Name'].values))

        st.subheader("Month Aggregates")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Incentives", f"₹{total_incentives:,.2f}")
        col2.metric("Transactions", f"{total_transactions:,}")
        col3.metric("Employees", unique_employees)
        col4.metric("Stores", unique_stores)

        st.info("👉 Go to **Dashboard** to view detailed analytics or **History** to see all uploads")
    else:
        st.info(f"No uploads for {st.session_state.selected_month} yet. Switch months or upload data.")
else:
    st.info("👆 No uploads yet. Go to the **Upload** page to get started!")

# Sidebar
with st.sidebar:
    # Monthly Navigation
    st.header("📅 Month Filter")

    # Generate constant month list (past 12 months + current + next 3 months)
    from datetime import datetime

    def add_months(date, months):
        """Add or subtract months from a date"""
        month = date.month - 1 + months
        year = date.year + month // 12
        month = month % 12 + 1
        return datetime(year, month, 1)

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

    # Month selector
    month_display = {month: datetime.strptime(month, "%Y-%m").strftime("%B %Y") for month in available_months}

    # Mark months with uploads
    months_with_uploads = set(upload['month'] for upload in st.session_state.uploads) if st.session_state.uploads else set()
    month_display_with_indicator = {
        month: f"{month_display[month]} {'📁' if month in months_with_uploads else ''}"
        for month in available_months
    }

    # Debug: Show month count
    st.caption(f"Available months: {len(available_months)}")

    # Always show month selector
    selected = st.selectbox(
        "View Data For:",
        options=available_months,
        format_func=lambda x: month_display_with_indicator[x],
        index=available_months.index(st.session_state.selected_month) if st.session_state.selected_month in available_months else available_months.index(current_date.strftime("%Y-%m")),
        key='month_selector',
        help="Filter all pages by selected month (📁 = has data)"
    )

    # Update selected month in session state
    st.session_state.selected_month = selected

    # Show stats for selected month if uploads exist
    if st.session_state.uploads:
        month_uploads = [u for u in st.session_state.uploads if u['month'] == selected]
        st.metric("Uploads This Month", len(month_uploads))
    else:
        st.info("No uploads yet")

    st.divider()

    st.header("About")
    st.markdown("""
    **Hometown Incentive Calculator**

    Version: 2.1.0 (AOV Fix Applied)

    **Latest:** AOV now correctly uses NET SALES VALUE (with GST)

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
