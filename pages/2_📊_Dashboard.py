"""
Dashboard Page - Analytics and visualizations
"""
import streamlit as st
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

st.title("📊 Analytics Dashboard")

# Check if there are any uploads
if not st.session_state.uploads:
    st.warning("⚠️ No uploads found. Please upload a file first.")
    st.page_link("pages/1_📤_Upload.py", label="Go to Upload Page", icon="📤")
else:
    # Select upload
    upload_options = {
        f"{u['filename']} - {u['timestamp'].strftime('%Y-%m-%d %H:%M')}": u
        for u in st.session_state.uploads
    }

    selected_label = st.selectbox(
        "Select Upload to Analyze",
        options=list(upload_options.keys()),
        index=len(upload_options) - 1  # Default to latest
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

        # Top Performers Table
        st.subheader("🏆 Top 10 Performers")
        top_10 = filtered_summary.nlargest(10, 'Total Points')[
            ['Employee', 'Store Name', 'Role', 'Furniture Points', 'Homeware Points', 'Total Points']
        ]
        st.dataframe(
            top_10,
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
    if st.session_state.uploads:
        st.divider()
        st.subheader("Session Stats")
        st.metric("Total Uploads", len(st.session_state.uploads))
        total_all = sum(u['total_incentives'] for u in st.session_state.uploads)
        st.metric("Total Incentives (All)", f"₹{total_all:,.2f}")
