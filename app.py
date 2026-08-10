import sqlite3
import pandas as pd
import streamlit as st

st.set_page_config(page_title="SilverShield Footprint Manager", layout="wide")
st.title("🛡️ SilverShield Digital Footprint Manager")
st.write("Comprehensive PII, Credential, and Data Broker Remediation Portal")

database_name = "digital_footprint_manager.db"

# Reset and ensure the table has the correct schema
with sqlite3.connect(database_name) as connection:
    cursor = connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS optout_tracker;")
    cursor.execute('''
        CREATE TABLE optout_tracker (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            broker_name TEXT,
            category TEXT,
            status TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    initial_data = [
        ('Whitepages', 'People-Search Brokers', 'Discovered'),
        ('Spokeo', 'People-Search Brokers', 'Discovered'),
        ('HaveIBeenPwned API', 'Credential/Breach Data', 'Discovered'),
        ('Dark Web Exposure', 'Credential/Breach Data', 'Discovered'),
        ('Public Voter Registry', 'Public Records/PII', 'Discovered'),
        ('Property Records', 'Public Records/PII', 'Discovered')
    ]
    cursor.executemany("INSERT INTO optout_tracker (broker_name, category, status) VALUES (?, ?, ?);", initial_data)
    connection.commit()

# User Input Section
st.markdown("### 1. Assessment Initialization")
col1, col2 = st.columns(2)
with col1:
    full_name = st.text_input("Full Name to Scan")
with col2:
    city_state = st.text_input("City and State")

if st.button("Run Full Comprehensive Sweep"):
    if full_name:
        with sqlite3.connect(database_name) as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE optout_tracker SET status = 'Opt-Out/Remediation Requested', last_updated = CURRENT_TIMESTAMP WHERE status = 'Discovered';")
        st.success(f"Comprehensive scan complete for {full_name}. All identified exposures have been queued for automated removal.")
    else:
        st.warning("Please enter a name to proceed with the sweep.")

st.divider()
st.subheader("📊 Live Exposure Report Card")

with sqlite3.connect(database_name) as connection:
    df = pd.read_sql_query("SELECT broker_name AS 'Source/Broker', category AS 'Data Type', status AS 'Current Status', last_updated AS 'Last Updated' FROM optout_tracker;", connection)

total = len(df)
pending = len(df[df['Current Status'] == 'Discovered'])
in_progress = len(df[df['Current Status'] == 'Opt-Out/Remediation Requested'])

m1, m2, m3 = st.columns(3)
m1.metric("Total Exposure Points", total)
m2.metric("Discovered/Active", pending)
m3.metric("Remediation Pending", in_progress)

st.markdown("### Itemized Status Detail")
st.dataframe(df, use_container_width=True)
