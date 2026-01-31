"""
Chart utilities using Plotly
"""
import plotly.express as px
import plotly.graph_objects as go

def create_store_performance_chart(summary_df):
    """Bar chart of total incentives by store"""
    store_totals = summary_df.groupby('Store Name')['Total Points'].sum().reset_index()
    store_totals = store_totals.sort_values('Total Points', ascending=True)

    fig = px.bar(
        store_totals,
        x='Total Points',
        y='Store Name',
        orientation='h',
        title='Total Incentives by Store',
        labels={'Total Points': 'Incentives (₹)', 'Store Name': 'Store'},
        color='Total Points',
        color_continuous_scale='Blues'
    )
    fig.update_layout(showlegend=False, height=500)
    return fig

def create_lob_breakdown_chart(summary_df):
    """Pie chart of Furniture vs Homeware incentives"""
    furniture_total = summary_df['Furniture Points'].sum()
    homeware_total = summary_df['Homeware Points'].sum()

    fig = px.pie(
        values=[furniture_total, homeware_total],
        names=['Furniture', 'Homeware'],
        title='Incentive Split by Line of Business',
        hole=0.4,
        color_discrete_sequence=['#1f77b4', '#ff7f0e']
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    return fig

def create_top_performers_chart(summary_df, top_n=10):
    """Horizontal bar chart of top performers"""
    top_df = summary_df.nlargest(top_n, 'Total Points')

    fig = px.bar(
        top_df,
        x='Total Points',
        y='Employee',
        color='Role',
        orientation='h',
        title=f'Top {top_n} Performers',
        labels={'Total Points': 'Incentives (₹)', 'Employee': 'Employee', 'Role': 'Role'},
        color_discrete_map={'PE': '#2ca02c', 'SM': '#ff7f0e', 'DM': '#d62728'}
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=500)
    return fig

def create_role_distribution_chart(summary_df):
    """Pie chart of incentives by role"""
    role_totals = summary_df.groupby('Role')['Total Points'].sum().reset_index()

    fig = px.pie(
        role_totals,
        values='Total Points',
        names='Role',
        title='Incentive Distribution by Role',
        color='Role',
        color_discrete_map={'PE': '#2ca02c', 'SM': '#ff7f0e', 'DM': '#d62728'}
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    return fig

def create_store_comparison_chart(summary_df):
    """Grouped bar chart showing Furniture vs Homeware by store"""
    store_data = summary_df.groupby('Store Name')[['Furniture Points', 'Homeware Points']].sum().reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Furniture',
        x=store_data['Store Name'],
        y=store_data['Furniture Points'],
        marker_color='#1f77b4'
    ))
    fig.add_trace(go.Bar(
        name='Homeware',
        x=store_data['Store Name'],
        y=store_data['Homeware Points'],
        marker_color='#ff7f0e'
    ))

    fig.update_layout(
        title='Furniture vs Homeware Incentives by Store',
        xaxis_title='Store',
        yaxis_title='Incentives (₹)',
        barmode='group',
        height=500
    )
    return fig
