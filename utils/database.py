"""
Database utility for PostgreSQL operations
"""
import streamlit as st
import pandas as pd
import json
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

def get_database_url():
    """Get database URL from Streamlit secrets"""
    try:
        return st.secrets["database"]["url"]
    except Exception as e:
        st.error("⚠️ Database connection not configured. Please add database URL to secrets.")
        st.stop()

def get_db_connection():
    """Create database engine"""
    try:
        engine = create_engine(
            get_database_url(),
            poolclass=NullPool,
            connect_args={
                "connect_timeout": 10,
            }
        )
        return engine
    except Exception as e:
        st.error(f"Failed to connect to database: {e}")
        st.stop()

def init_database():
    """Initialize database tables if they don't exist"""
    engine = get_db_connection()

    with engine.connect() as conn:
        # Create uploads table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS uploads (
                id SERIAL PRIMARY KEY,
                filename TEXT NOT NULL,
                upload_timestamp TIMESTAMP NOT NULL,
                month TEXT NOT NULL,
                data_as_of_date DATE NOT NULL,
                is_final BOOLEAN DEFAULT FALSE,
                total_transactions INTEGER,
                total_incentives NUMERIC,
                employees_count INTEGER,
                stores_count INTEGER,
                transactions_data JSONB,
                summary_data JSONB,
                qualifier_data JSONB,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """))

        # Create targets table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS targets (
                id SERIAL PRIMARY KEY,
                month TEXT NOT NULL,
                store_name TEXT NOT NULL,
                lob TEXT NOT NULL,
                target_aov NUMERIC NOT NULL,
                target_bills INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                UNIQUE(month, store_name, lob)
            )
        """))

        conn.commit()

def save_upload(upload_data):
    """Save upload to database"""
    engine = get_db_connection()

    # Convert DataFrames to JSON
    transactions_json = upload_data['transactions_df'].to_json(orient='records')
    summary_json = upload_data['summary_df'].to_json(orient='records')
    qualifier_json = upload_data['qualifier_df'].to_json(orient='records')

    with engine.connect() as conn:
        result = conn.execute(text("""
            INSERT INTO uploads (
                filename, upload_timestamp, month, data_as_of_date, is_final,
                total_transactions, total_incentives, employees_count, stores_count,
                transactions_data, summary_data, qualifier_data
            ) VALUES (
                :filename, :upload_timestamp, :month, :data_as_of_date, :is_final,
                :total_transactions, :total_incentives, :employees_count, :stores_count,
                CAST(:transactions_data AS jsonb), CAST(:summary_data AS jsonb), CAST(:qualifier_data AS jsonb)
            ) RETURNING id
        """), {
            'filename': upload_data['filename'],
            'upload_timestamp': upload_data['timestamp'],
            'month': upload_data['month'],
            'data_as_of_date': upload_data['data_as_of_date'],
            'is_final': upload_data['is_final'],
            'total_transactions': upload_data['total_transactions'],
            'total_incentives': float(upload_data['total_incentives']),
            'employees_count': upload_data['employees_count'],
            'stores_count': upload_data['stores_count'],
            'transactions_data': transactions_json,
            'summary_data': summary_json,
            'qualifier_data': qualifier_json
        })
        conn.commit()
        return result.fetchone()[0]

def load_uploads():
    """Load all uploads from database"""
    engine = get_db_connection()

    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT
                id, filename, upload_timestamp, month, data_as_of_date, is_final,
                total_transactions, total_incentives, employees_count, stores_count,
                transactions_data, summary_data, qualifier_data
            FROM uploads
            ORDER BY upload_timestamp DESC
        """))

        uploads = []
        for row in result:
            try:
                # Convert JSONB (dict/list) back to DataFrames
                # PostgreSQL JSONB returns Python dict/list, not JSON string
                transactions_data = row[10]
                summary_data = row[11]
                qualifier_data = row[12]

                # If data is already a dict/list, convert directly to DataFrame
                # If it's a string, parse it first
                if isinstance(transactions_data, str):
                    transactions_df = pd.read_json(transactions_data, orient='records')
                else:
                    transactions_df = pd.DataFrame(transactions_data)

                if isinstance(summary_data, str):
                    summary_df = pd.read_json(summary_data, orient='records')
                else:
                    summary_df = pd.DataFrame(summary_data)

                if isinstance(qualifier_data, str):
                    qualifier_df = pd.read_json(qualifier_data, orient='records')
                else:
                    qualifier_df = pd.DataFrame(qualifier_data)

                uploads.append({
                    'id': row[0],
                    'filename': row[1],
                    'timestamp': row[2],
                    'month': row[3],
                    'data_as_of_date': row[4],
                    'is_final': row[5],
                    'total_transactions': row[6],
                    'total_incentives': float(row[7]),
                    'employees_count': row[8],
                    'stores_count': row[9],
                    'transactions_df': transactions_df,
                    'summary_df': summary_df,
                    'qualifier_df': qualifier_df
                })
            except Exception as e:
                # Log error but continue with other uploads
                print(f"Error loading upload {row[0]}: {e}")
                continue

        return uploads

def save_targets(month, store_name, lob, target_aov, target_bills):
    """Save or update target in database"""
    engine = get_db_connection()

    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO targets (month, store_name, lob, target_aov, target_bills, updated_at)
            VALUES (:month, :store_name, :lob, :target_aov, :target_bills, NOW())
            ON CONFLICT (month, store_name, lob)
            DO UPDATE SET
                target_aov = EXCLUDED.target_aov,
                target_bills = EXCLUDED.target_bills,
                updated_at = NOW()
        """), {
            'month': month,
            'store_name': store_name,
            'lob': lob,
            'target_aov': target_aov,
            'target_bills': target_bills
        })
        conn.commit()

def load_targets():
    """Load all targets from database"""
    engine = get_db_connection()

    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT month, store_name, lob, target_aov, target_bills
            FROM targets
        """))

        # Convert to nested dictionary structure: targets[month][store][lob] = {aov, bills}
        targets = {}
        for row in result:
            month = row[0]
            store_name = row[1]
            lob = row[2]
            target_aov = float(row[3])
            target_bills = int(row[4])

            if month not in targets:
                targets[month] = {}
            if store_name not in targets[month]:
                targets[month][store_name] = {}

            targets[month][store_name][lob] = {
                'aov': target_aov,
                'bills': target_bills
            }

        return targets

def delete_upload(upload_id):
    """Delete an upload from database"""
    engine = get_db_connection()

    with engine.connect() as conn:
        conn.execute(text("DELETE FROM uploads WHERE id = :id"), {'id': upload_id})
        conn.commit()
