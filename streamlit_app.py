"""
Hometown Incentive Calculator - Standalone Streamlit App
Cloud-deployable version (no backend required)
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import io
import warnings
warnings.filterwarnings('ignore')

# Page config
st.set_page_config(
    page_title="Hometown Incentive Calculator",
    page_icon="🏠",
    layout="wide"
)

# ============================================================================
# CALCULATOR FUNCTIONS (from backend/calculator.py)
# ============================================================================

def calculate_incentives(row):
    """Calculate incentive for a single transaction"""
    sales_with_gst = row['Sum of NET SALES VALUE']
    sales_without_gst = row['Sum of Sales value Without GST']
    lob = row['LOB']
    dm_value = str(row.get('DM', '')).strip()
    has_dm = (dm_value != '-' and dm_value != '')

    # Determine commission rate
    if lob == 'Furniture':
        if sales_with_gst < 20000:
            commission_rate = 0
        elif sales_with_gst <= 40000:
            commission_rate = 0.002
        elif sales_with_gst <= 80000:
            commission_rate = 0.006
        else:
            commission_rate = 0.01
    elif lob == 'Homeware':
        if sales_with_gst <= 5000:
            commission_rate = 0.005
        elif sales_with_gst <= 10000:
            commission_rate = 0.008
        else:
            commission_rate = 0.01
    else:
        commission_rate = 0

    # Calculate total incentive
    total_incentive = sales_without_gst * commission_rate

    # Split based on DM presence
    if not has_dm:
        pe_incentive = total_incentive * 0.7
        sm_incentive = total_incentive * 0.3
        dm_incentive = 0
    else:
        pe_incentive = total_incentive * 0.6
        sm_incentive = total_incentive * 0.15
        dm_incentive = total_incentive * 0.25

    return pd.Series({
        'Ince Amt': total_incentive,
        'PE Inc amt': pe_incentive,
        'SM Inc Amt': sm_incentive,
        'DM Inc Amt': dm_incentive
    })

def process_file(uploaded_file):
    """Process uploaded Excel file"""
    # Read file
    df = pd.read_excel(uploaded_file, sheet_name='Sales Report - Hometown (2)', header=0)

    required_cols = [
        'Store Code', 'Name', 'Sales_Doc', 'Sales Date', 'LOB', 'Bill No', 'Salesman',
        'Sum of NET SALES VALUE', 'Sum of Sales value Without GST', 'SM', 'DM'
    ]

    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns: {missing_cols}")

    df = df[required_cols].copy()
    df['Sum of NET SALES VALUE'] = pd.to_numeric(df['Sum of NET SALES VALUE'], errors='coerce').fillna(0)
    df['Sum of Sales value Without GST'] = pd.to_numeric(df['Sum of Sales value Without GST'], errors='coerce').fillna(0)

    for col in ['Salesman', 'SM', 'DM']:
        df[col] = df[col].fillna('-')

    # Calculate incentives
    incentive_cols = df.apply(calculate_incentives, axis=1)
    df['Ince Amt'] = incentive_cols['Ince Amt']
    df['PE Inc amt'] = incentive_cols['PE Inc amt']
    df['SM Inc Amt'] = incentive_cols['SM Inc Amt']
    df['DM Inc Amt'] = incentive_cols['DM Inc Amt']

    return df

def create_employee_summary(df):
    """Create employee summary"""
    employees = {}

    for role, col in [('PE', 'Salesman'), ('SM', 'SM'), ('DM', 'DM')]:
        inc_col = 'PE Inc amt' if role == 'PE' else f'{role} Inc Amt'
        data = df.groupby(['Store Code', 'Name', col, 'LOB'])[inc_col].sum().reset_index()

        for _, row in data.iterrows():
            emp = row[col]
            if emp != '-' and row[inc_col] > 0:
                key = (row['Store Code'], row['Name'], emp, role)
                if key not in employees:
                    employees[key] = {
                        'Store Code': row['Store Code'],
                        'Store Name': row['Name'],
                        'Employee': emp,
                        'Role': role,
                        'Furniture Points': 0,
                        'Homeware Points': 0
                    }
                if row['LOB'] == 'Furniture':
                    employees[key]['Furniture Points'] += row[inc_col]
                else:
                    employees[key]['Homeware Points'] += row[inc_col]

    summary_df = pd.DataFrame(list(employees.values()))

    if len(summary_df) > 0:
        summary_df['Total Points'] = summary_df['Furniture Points'] + summary_df['Homeware Points']
        summary_df = summary_df.round(2)
        summary_df = summary_df.sort_values(['Store Name', 'Total Points'], ascending=[True, False])

    return summary_df

def create_output_excel(df, summary_df):
    """Create downloadable Excel file"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Detailed Transactions', index=False)
        summary_df.to_excel(writer, sheet_name='Employee Points Summary', index=False)
    output.seek(0)
    return output

# ============================================================================
# STREAMLIT APP
# ============================================================================

st.title("🏠 Hometown Incentive Calculator")

st.markdown("""
Upload your sales data Excel file to automatically calculate employee incentives.

**Required Sheet**: `Sales Report - Hometown (2)`
""")

# File uploader
uploaded_file = st.file_uploader(
    "Choose an Excel file (.xlsx)",
    type=['xlsx'],
    help="Upload the BI export with 'Sales Report - Hometown (2)' sheet"
)

if uploaded_file:
    try:
        with st.spinner("Processing file..."):
            # Process file
            df = process_file(uploaded_file)
            summary_df = create_employee_summary(df)

            # Success message
            st.success("✅ Processing completed!")

            # Results
            st.divider()
            st.subheader("📊 Summary")

            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Total Sales", f"₹{df['Sum of Sales value Without GST'].sum():,.0f}")
            col2.metric("Total Incentives", f"₹{df['Ince Amt'].sum():,.2f}")
            col3.metric("Transactions", f"{len(df):,}")
            col4.metric("Employees", len(summary_df))
            col5.metric("Stores", df['Name'].nunique())

            st.divider()

            # Breakdown by role
            st.subheader("💰 Incentive Breakdown by Role")
            col1, col2, col3 = st.columns(3)
            col1.metric("PE Total", f"₹{df['PE Inc amt'].sum():,.2f}")
            col2.metric("SM Total", f"₹{df['SM Inc Amt'].sum():,.2f}")
            col3.metric("DM Total", f"₹{df['DM Inc Amt'].sum():,.2f}")

            st.divider()

            # Charts
            st.subheader("📈 Performance Analysis")

            col1, col2 = st.columns(2)

            with col1:
                # Store totals
                store_totals = summary_df.groupby('Store Name')['Total Points'].sum().sort_values(ascending=False)
                st.bar_chart(store_totals)
                st.caption("Total Incentives by Store")

            with col2:
                # LOB breakdown
                lob_data = {
                    'Furniture': summary_df['Furniture Points'].sum(),
                    'Homeware': summary_df['Homeware Points'].sum()
                }
                st.bar_chart(lob_data)
                st.caption("Incentives by Line of Business")

            st.divider()

            # Top performers
            st.subheader("🏆 Top 10 Performers")
            top_10 = summary_df.nlargest(10, 'Total Points')[['Employee', 'Store Name', 'Role', 'Total Points']]
            st.dataframe(
                top_10,
                use_container_width=True,
                column_config={
                    "Employee": "Employee",
                    "Store Name": "Store",
                    "Role": "Role",
                    "Total Points": st.column_config.NumberColumn("Incentive", format="₹%.2f")
                },
                hide_index=True
            )

            st.divider()

            # Employee Summary Table
            st.subheader("👥 Employee Summary")
            st.dataframe(
                summary_df,
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

            st.divider()

            # Download button
            st.subheader("📥 Download Results")
            excel_file = create_output_excel(df, summary_df)
            st.download_button(
                label="📥 Download Excel File",
                data=excel_file,
                file_name=f"Hometown_Incentives_{datetime.now():%Y%m%d_%H%M%S}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )

    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.info("💡 Make sure the file has a sheet named 'Sales Report - Hometown (2)' with all required columns.")

else:
    st.info("👆 Please upload an Excel file to get started")

    # Show example
    with st.expander("ℹ️ Required Columns"):
        st.markdown("""
        Your Excel file must contain these columns:
        - Store Code
        - Name (Store Name)
        - Sales_Doc
        - Sales Date
        - LOB (Line of Business)
        - Bill No
        - Salesman
        - Sum of NET SALES VALUE
        - Sum of Sales value Without GST
        - SM (Store Manager)
        - DM (Department Manager)
        """)

    with st.expander("📋 Incentive Calculation Logic"):
        st.markdown("""
        **Furniture Slabs:**
        - < ₹20,000: 0%
        - ₹20,000 - ₹40,000: 0.2%
        - ₹40,000 - ₹80,000: 0.6%
        - > ₹80,000: 1.0%

        **Homeware Slabs:**
        - ≤ ₹5,000: 0.5%
        - ₹5,000 - ₹10,000: 0.8%
        - > ₹10,000: 1.0%

        **Role Distribution:**
        - With DM: PE=60%, SM=15%, DM=25%
        - Without DM: PE=70%, SM=30%
        """)

# Sidebar
with st.sidebar:
    st.header("About")
    st.markdown("""
    **Hometown Incentive Calculator**

    Version: 1.0.0 (Cloud Edition)

    This tool calculates employee incentives based on sales data.

    Simply upload your Excel file and get instant results!
    """)

    st.divider()

    st.markdown("**How it works:**")
    st.markdown("""
    1. Upload Excel file
    2. Automatic validation
    3. Instant calculation
    4. Download results
    """)
