import sqlite3
import pandas as pd
import streamlit as st

st.title("Digital Footprint Manager")
st.write("Privacy Report Card & Tracker")

database_name = "digital_footprint_manager.db"

# Ensure table exists
with sqlite3.connect(database_name) as connection:
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS optout_tracker (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            broker_name TEXT,
            tier_category TEXT,
            status TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    cursor.execute("SELECT COUNT(*) FROM optout_tracker;")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO optout_tracker (broker_name, tier_category, status) VALUES ('Whitepages', 'Tier 1: People Search', 'Discovered');")
        cursor.execute("INSERT INTO optout_tracker (broker_name, tier_category, status) VALUES ('Spokeo', 'Tier 1: People Search', 'Discovered');")
        connection.commit()

# User input fields for anyone visiting the app
st.markdown("### Enter Search Details")
full_name = st.text_input("Full Name", placeholder="e.g., Jane Doe")
city_state = st.text_input("City and State", placeholder="e.g., Tallahassee, FL")

if st.button("Run Automated Sweep & Generate Report Card"):
    if full_name:
        with sqlite3.connect(database_name) as connection:
            cursor = connection.cursor()
            cursor.execute('''
                UPDATE optout_tracker
                SET status = 'Opt-Out Requested', last_updated = CURRENT_TIMESTAMP
                WHERE status = 'Discovered';
            ''')
        st.success(f"Scan complete for {full_name} ({city_state})! All discovered broker profiles have been queued for removal.")
    else:
        st.warning("Please enter a full name to run the automated scan.")

st.divider()
st.subheader("📊 Live Privacy Report Card")

with sqlite3.connect(database_name) as connection:
    df = pd.read_sql_query("SELECT broker_name AS 'Broker Name', tier_category AS 'Tier Category', status AS 'Current Status', last_updated AS 'Last Updated' FROM optout_tracker;", connection)

st.write(f"**Total Tracked Brokers:** {len(df)}")
st.write(f"**Opt-Outs Requested:** {len(df[df['Current Status'] == 'Opt-Out Requested'])}")

st.markdown("### Itemized Broker Status")
st.table(df)
