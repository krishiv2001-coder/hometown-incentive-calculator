"""
Calculation utilities
"""
import pandas as pd
from datetime import datetime

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

def process_file(uploaded_file, sheet_name=None):
    """Process uploaded Excel file"""
    # Read file - use first sheet if no sheet name specified
    if sheet_name is None:
        df = pd.read_excel(uploaded_file, sheet_name=0, header=0)  # Use first sheet
    else:
        df = pd.read_excel(uploaded_file, sheet_name=sheet_name, header=0)

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
