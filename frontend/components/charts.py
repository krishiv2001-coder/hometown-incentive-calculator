"""
Chart components using Plotly
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def create_store_performance_chart(summary_df: pd.DataFrame):
    """Bar chart of total incentives by store"""
    store_totals = summary_df.groupby('store_name')['total_points'].sum().reset_index()
    store_totals = store_totals.sort_values('total_points', ascending=True)

    fig = px.bar(
        store_totals,
        x='total_points',
        y='store_name',
        orientation='h',
        title='Total Incentives by Store',
        labels={'total_points': 'Incentives (₹)', 'store_name': 'Store'},
        color='total_points',
        color_continuous_scale='Blues'
    )
    fig.update_layout(showlegend=False)
    return fig

def create_lob_breakdown_chart(summary_df: pd.DataFrame):
    """Pie chart of Furniture vs Homeware incentives"""
    furniture_total = summary_df['furniture_points'].sum()
    homeware_total = summary_df['homeware_points'].sum()

    fig = px.pie(
        values=[furniture_total, homeware_total],
        names=['Furniture', 'Homeware'],
        title='Incentive Split by Line of Business',
        hole=0.4,
        color_discrete_sequence=['#1f77b4', '#ff7f0e']
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def create_top_performers_chart(summary_df: pd.DataFrame, top_n: int = 10):
    """Horizontal bar chart of top performers"""
    top_df = summary_df.nlargest(top_n, 'total_points')

    fig = px.bar(
        top_df,
        x='total_points',
        y='employee',
        color='role',
        orientation='h',
        title=f'Top {top_n} Performers',
        labels={'total_points': 'Incentives (₹)', 'employee': 'Employee', 'role': 'Role'},
        color_discrete_map={'PE': '#2ca02c', 'SM': '#ff7f0e', 'DM': '#d62728'}
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    return fig

def create_qualifier_status_chart(tracker_df: pd.DataFrame):
    """Bar chart of qualifier status counts"""
    status_map = {
        'met_both': '✅ Met Both',
        'aov_met': '⚠️ AOV Met',
        'bills_met': '⚠️ Bills Met',
        'both_short': '❌ Both Short'
    }

    tracker_df['status_display'] = tracker_df['status'].map(status_map)
    status_counts = tracker_df['status_display'].value_counts().reset_index()
    status_counts.columns = ['status', 'count']

    fig = px.bar(
        status_counts,
        x='status',
        y='count',
        title='Qualifier Achievement Status',
        labels={'status': 'Status', 'count': 'Number of Stores'},
        color='status',
        color_discrete_map={
            '✅ Met Both': '#2ca02c',
            '⚠️ AOV Met': '#ff7f0e',
            '⚠️ Bills Met': '#ff7f0e',
            '❌ Both Short': '#d62728'
        }
    )
    fig.update_layout(showlegend=False)
    return fig

def create_role_distribution_chart(summary_df: pd.DataFrame):
    """Pie chart of incentives by role"""
    role_totals = summary_df.groupby('role')['total_points'].sum().reset_index()

    fig = px.pie(
        role_totals,
        values='total_points',
        names='role',
        title='Incentive Distribution by Role',
        color_discrete_map={'PE': '#2ca02c', 'SM': '#ff7f0e', 'DM': '#d62728'}
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig
