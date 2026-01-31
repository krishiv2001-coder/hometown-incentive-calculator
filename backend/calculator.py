"""
HOMETOWN INCENTIVE CALCULATOR - BACKEND MODULE
Refactored for FastAPI integration

Core calculation logic (preserved 100% accuracy)
"""

import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# INCENTIVE CALCULATION
# ============================================================================

def calculate_incentives(row):
    """
    Calculate incentive columns J, M, N, O

    Logic:
    - Slab check: Column H (WITH GST)
    - Calculation: Column I (WITHOUT GST)
    - DM check: If DM = "-", use 70-30 split, else 60-15-25
    """
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

# ============================================================================
# DATA LOADING
# ============================================================================

def load_sales_data(filepath, sheet_name='Sales Report - Hometown (2)'):
    """Load raw sales data from BI export"""
    df = pd.read_excel(filepath, sheet_name=sheet_name, header=0)

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

    return df

def process_calculations(df):
    """Calculate incentives for all transactions"""
    incentive_cols = df.apply(calculate_incentives, axis=1)
    df['Ince Amt'] = incentive_cols['Ince Amt']
    df['PE Inc amt'] = incentive_cols['PE Inc amt']
    df['SM Inc Amt'] = incentive_cols['SM Inc Amt']
    df['DM Inc Amt'] = incentive_cols['DM Inc Amt']

    return df

# ============================================================================
# EMPLOYEE SUMMARY
# ============================================================================

def create_employee_summary(df):
    """Aggregate incentives by employee"""
    employees = {}

    # Process each role
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

    return summary_df[['Store Code', 'Store Name', 'Employee', 'Role',
                       'Furniture Points', 'Homeware Points', 'Total Points']]

# ============================================================================
# QUALIFIER TRACKER
# ============================================================================

def create_dummy_targets(stores):
    """Create dummy targets (update with real values)"""
    return pd.DataFrame([{
        'Store Code': None,
        'Store Name': store,
        'Month': datetime.now().strftime('%b %Y'),
        'Furniture AOV Target': 25000,
        'Furniture Bills Target': 50,
        'Homeware AOV Target': 8000,
        'Homeware Bills Target': 100
    } for store in stores])

def create_qualifier_tracker(df, targets_df):
    """Calculate store performance vs targets"""
    store_perf = df.groupby(['Store Code', 'Name', 'LOB']).agg({
        'Bill No': 'nunique',
        'Sum of Sales value Without GST': 'sum'
    }).reset_index()

    store_perf['AOV'] = (store_perf['Sum of Sales value Without GST'] / store_perf['Bill No']).round(0)
    store_perf.rename(columns={'Bill No': 'Actual Bills', 'Name': 'Store Name'}, inplace=True)

    tracker = []
    for _, row in store_perf.iterrows():
        target_row = targets_df[targets_df['Store Name'] == row['Store Name']]

        if len(target_row) > 0:
            target = target_row.iloc[0]
            lob = row['LOB']

            if lob == 'Furniture':
                aov_target = target['Furniture AOV Target']
                bills_target = target['Furniture Bills Target']
            else:
                aov_target = target['Homeware AOV Target']
                bills_target = target['Homeware Bills Target']

            aov_pct = (row['AOV'] / aov_target * 100).round(1)
            bills_pct = (row['Actual Bills'] / bills_target * 100).round(1)

            if row['AOV'] >= aov_target and row['Actual Bills'] >= bills_target:
                status = 'met_both'
            elif row['AOV'] >= aov_target:
                status = 'aov_met'
            elif row['Actual Bills'] >= bills_target:
                status = 'bills_met'
            else:
                status = 'both_short'

            tracker.append({
                'Store Code': row['Store Code'],
                'Store Name': row['Store Name'],
                'LOB': lob,
                'Actual AOV': int(row['AOV']),
                'Target AOV': int(aov_target),
                'AOV Achievement %': aov_pct,
                'Actual Bills': int(row['Actual Bills']),
                'Target Bills': int(bills_target),
                'Bills Achievement %': bills_pct,
                'Qualifier Status': status
            })

    tracker_df = pd.DataFrame(tracker)
    if len(tracker_df) > 0:
        tracker_df = tracker_df.sort_values(['Store Name', 'LOB'])

    return tracker_df

# ============================================================================
# MAIN PROCESSING FUNCTION
# ============================================================================

def process_incentives(input_file, output_file=None, sheet_name='Sales Report - Hometown (2)'):
    """
    Main processing function for API integration
    Returns: (df, summary_df, tracker_df, targets_df)
    """
    # Process
    df = load_sales_data(input_file, sheet_name)
    df = process_calculations(df)
    summary_df = create_employee_summary(df)
    targets_df = create_dummy_targets(sorted(df['Name'].unique()))
    tracker_df = create_qualifier_tracker(df, targets_df)

    # Optionally save output
    if output_file:
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Detailed Transactions', index=False)
            summary_df.to_excel(writer, sheet_name='Employee Points Summary', index=False)
            tracker_df.to_excel(writer, sheet_name='Daily Qualifier Tracker', index=False)
            targets_df.to_excel(writer, sheet_name='Monthly Targets', index=False)

    return df, summary_df, tracker_df, targets_df
