"""
Dashboard Page - Analytics and visualizations
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.api_client import APIClient
from components.charts import (
    create_store_performance_chart,
    create_lob_breakdown_chart,
    create_top_performers_chart,
    create_qualifier_status_chart,
    create_role_distribution_chart
)
from config import API_BASE_URL

# Page config
st.set_page_config(page_title="Dashboard - Hometown", page_icon="📊", layout="wide")

# Initialize API client
if 'api_client' not in st.session_state:
    st.session_state.api_client = APIClient(API_BASE_URL)

api_client = st.session_state.api_client

st.title("📊 Analytics Dashboard")

# Get upload history for job selection
try:
    history = api_client.get_history(limit=20)

    if not history:
        st.warning("⚠️ No uploads found. Please upload a file first.")
        st.page_link("pages/1_📤_Upload.py", label="Go to Upload Page", icon="📤")
    else:
        # Job selector
        job_options = {
            f"{h['filename']} - {h['upload_time'][:19]}": h['job_id']
            for h in history if h['status'] == 'completed'
        }

        if not job_options:
            st.warning("⚠️ No completed jobs found. Please complete a file upload first.")
            st.page_link("pages/1_📤_Upload.py", label="Go to Upload Page", icon="📤")
        else:
            # Use latest job by default or from session state
            default_job = list(job_options.keys())[0]
            if 'latest_job_id' in st.session_state:
                for label, jid in job_options.items():
                    if jid == st.session_state.latest_job_id:
                        default_job = label
                        break

            selected_label = st.selectbox(
                "Select Upload to Analyze",
                options=list(job_options.keys()),
                index=list(job_options.keys()).index(default_job)
            )
            selected_job_id = job_options[selected_label]

            # Fetch data
            with st.spinner("Loading data..."):
                try:
                    stats = api_client.get_statistics(selected_job_id)
                    summary_df = api_client.get_summary(selected_job_id)
                    tracker_df = api_client.get_tracker(selected_job_id)

                    # KPI Cards
                    st.subheader("Overview")
                    col1, col2, col3, col4, col5 = st.columns(5)
                    col1.metric("Total Sales", f"₹{stats['total_sales']:,.0f}")
                    col2.metric("Total Incentives", f"₹{stats['total_incentives']:,.2f}")
                    col3.metric("Transactions", f"{stats['total_transactions']:,}")
                    col4.metric("Employees", stats['employees_count'])
                    col5.metric("Stores", stats['stores_count'])

                    st.divider()

                    # Filters
                    with st.sidebar:
                        st.header("Filters")
                        selected_stores = st.multiselect(
                            "Store",
                            options=stats['stores'],
                            default=[]
                        )
                        selected_role = st.multiselect(
                            "Role",
                            options=['PE', 'SM', 'DM'],
                            default=[]
                        )

                    # Apply filters
                    filtered_summary = summary_df.copy()
                    if selected_stores:
                        filtered_summary = filtered_summary[filtered_summary['store_name'].isin(selected_stores)]
                    if selected_role:
                        filtered_summary = filtered_summary[filtered_summary['role'].isin(selected_role)]

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

                        # Qualifier Status
                        if len(tracker_df) > 0:
                            st.divider()
                            col1, col2 = st.columns([1, 1])
                            with col1:
                                fig4 = create_qualifier_status_chart(tracker_df)
                                st.plotly_chart(fig4, use_container_width=True)

                        st.divider()

                        # Qualifier Tracker Table
                        if len(tracker_df) > 0:
                            st.subheader("Qualifier Tracker")

                            # Map status for display
                            status_map = {
                                'met_both': '✅ Met Both',
                                'aov_met': '⚠️ AOV Met',
                                'bills_met': '⚠️ Bills Met',
                                'both_short': '❌ Both Short'
                            }
                            tracker_df['status_display'] = tracker_df['status'].map(status_map)

                            st.dataframe(
                                tracker_df[['store_name', 'lob', 'actual_aov', 'target_aov', 'aov_achievement',
                                          'actual_bills', 'target_bills', 'bills_achievement', 'status_display']],
                                use_container_width=True,
                                column_config={
                                    "store_name": "Store",
                                    "lob": "LOB",
                                    "actual_aov": st.column_config.NumberColumn("Actual AOV", format="₹%d"),
                                    "target_aov": st.column_config.NumberColumn("Target AOV", format="₹%d"),
                                    "aov_achievement": st.column_config.ProgressColumn("AOV %", min_value=0, max_value=200, format="%.1f%%"),
                                    "actual_bills": "Actual Bills",
                                    "target_bills": "Target Bills",
                                    "bills_achievement": st.column_config.ProgressColumn("Bills %", min_value=0, max_value=200, format="%.1f%%"),
                                    "status_display": "Status"
                                },
                                hide_index=True
                            )

                        # Employee Summary Table
                        st.subheader("Employee Summary")
                        st.dataframe(
                            filtered_summary,
                            use_container_width=True,
                            column_config={
                                "store_code": "Store Code",
                                "store_name": "Store Name",
                                "employee": "Employee",
                                "role": "Role",
                                "furniture_points": st.column_config.NumberColumn("Furniture", format="₹%.2f"),
                                "homeware_points": st.column_config.NumberColumn("Homeware", format="₹%.2f"),
                                "total_points": st.column_config.NumberColumn("Total", format="₹%.2f")
                            },
                            hide_index=True
                        )
                    else:
                        st.warning("No data matches the selected filters.")

                except Exception as e:
                    st.error(f"❌ Error loading data: {str(e)}")

except Exception as e:
    st.error(f"❌ Error connecting to API: {str(e)}")
    st.info("Make sure the backend server is running.")
