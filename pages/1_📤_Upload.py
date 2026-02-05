"""
Upload Page - File upload and processing
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import io
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.calculator import process_file, create_employee_summary, calculate_qualifier_metrics

# Page config
st.set_page_config(page_title="Upload - Hometown", page_icon="📤", layout="wide")

# Initialize session state
if 'uploads' not in st.session_state:
    st.session_state.uploads = []

st.title("📤 Upload Sales Data")

st.markdown("""
Upload your Excel file containing sales data to calculate incentives.

**Note**: The first sheet in your Excel file will be processed automatically.

**Required Columns**:
- Store Code, Name, Sales_Doc, Sales Date
- LOB, Bill No, Salesman
- Sum of NET SALES VALUE, Sum of Sales value Without GST
- SM, DM
""")

st.divider()

# File uploader
uploaded_file = st.file_uploader(
    "Choose an Excel file (.xlsx)",
    type=['xlsx'],
    help="Upload your sales data Excel file - the first sheet will be used"
)

if uploaded_file:
    # Show file info
    st.info(f"📄 **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")

    # Validate and process
    try:
        with st.spinner("Validating file..."):
            # Quick validation - use first sheet
            preview = pd.read_excel(uploaded_file, sheet_name=0, nrows=5)

            required_cols = [
                'Store Code', 'Name', 'Sales_Doc', 'Sales Date', 'LOB', 'Bill No', 'Salesman',
                'Sum of NET SALES VALUE', 'Sum of Sales value Without GST', 'SM', 'DM'
            ]

            missing_cols = [col for col in required_cols if col not in preview.columns]

            if missing_cols:
                st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
            else:
                st.success("✅ File validated successfully!")

                # Preview table
                with st.expander("Preview (first 5 rows)", expanded=True):
                    st.dataframe(preview, use_container_width=True)

                st.divider()

                # Process button
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    process_button = st.button("🚀 Process File", type="primary", use_container_width=True)

                if process_button:
                    try:
                        # Reset file pointer
                        uploaded_file.seek(0)

                        # Process file
                        with st.spinner("Processing file..."):
                            df = process_file(uploaded_file)
                            summary_df = create_employee_summary(df)
                            qualifier_df = calculate_qualifier_metrics(df)

                        st.success("✅ Processing completed!")

                        # Store in session state
                        upload_data = {
                            'id': len(st.session_state.uploads),
                            'filename': uploaded_file.name,
                            'timestamp': datetime.now(),
                            'transactions_df': df,
                            'summary_df': summary_df,
                            'qualifier_df': qualifier_df,
                            'total_transactions': len(df),
                            'total_incentives': float(df['Ince Amt'].sum()),
                            'employees_count': len(summary_df),
                            'stores_count': int(df['Name'].nunique())
                        }
                        st.session_state.uploads.append(upload_data)
                        st.session_state.current_upload = upload_data

                        # Show summary
                        st.divider()
                        st.subheader("Results Summary")
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("Transactions", f"{upload_data['total_transactions']:,}")
                        col2.metric("Total Incentives", f"₹{upload_data['total_incentives']:,.2f}")
                        col3.metric("Employees", upload_data['employees_count'])
                        col4.metric("Stores", upload_data['stores_count'])

                        # Breakdown by role
                        st.divider()
                        st.subheader("Incentive Breakdown by Role")
                        col1, col2, col3 = st.columns(3)
                        col1.metric("PE Total", f"₹{df['PE Inc amt'].sum():,.2f}")
                        col2.metric("SM Total", f"₹{df['SM Inc Amt'].sum():,.2f}")
                        col3.metric("DM Total", f"₹{df['DM Inc Amt'].sum():,.2f}")

                        # Download button
                        st.divider()
                        st.subheader("📥 Download Results")

                        # Create Excel file
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            df.to_excel(writer, sheet_name='Detailed Transactions', index=False)
                            summary_df.to_excel(writer, sheet_name='Employee Points Summary', index=False)
                        output.seek(0)

                        col1, col2 = st.columns([1, 2])
                        with col1:
                            st.download_button(
                                label="📥 Download Excel File",
                                data=output,
                                file_name=f"Hometown_Incentives_{datetime.now():%Y%m%d_%H%M%S}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                type="primary",
                                use_container_width=True
                            )

                        # Link to dashboard
                        st.info("👉 View detailed analytics in the **Dashboard** page")

                    except Exception as e:
                        st.error(f"❌ Error processing file: {str(e)}")

    except Exception as e:
        st.error(f"❌ Error reading file: {str(e)}")
        st.info("💡 Make sure your Excel file has the required columns in the first sheet")

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
    st.header("Instructions")
    st.markdown("""
    **Steps:**
    1. Upload the BI export Excel file
    2. Validate that all required columns are present
    3. Click "Process File" to calculate incentives
    4. Download the results when complete

    **Note:** Processing takes 5-15 seconds depending on file size.
    """)

    if st.session_state.uploads:
        st.divider()
        st.metric("Total Uploads", len(st.session_state.uploads))
