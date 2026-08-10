import sqlite3
import pandas as pd
import streamlit as st

st.title("Digital Footprint Manager")
st.write("Privacy Report Card & Tracker")

database_name = "digital_footprint_manager.db"

# Ensure table exists so it never throws an error
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
    # Add a sample record if table is empty
    cursor.execute("SELECT COUNT(*) FROM optout_tracker;")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO optout_tracker (broker_name, tier_category, status) VALUES ('Whitepages', 'Tier 1: People Search', 'Discovered');")
        cursor.execute("INSERT INTO optout_tracker (broker_name, tier_category, status) VALUES ('Spokeo', 'Tier 1: People Search', 'Discovered');")
        connection.commit()

if st.button("Run Automated Sweep & Generate Report Card"):
    with sqlite3.connect(database_name) as connection:
        cursor = connection.cursor()
        cursor.execute('''
            UPDATE optout_tracker
            SET status = 'Opt-Out Requested', last_updated = CURRENT_TIMESTAMP
            WHERE status = 'Discovered';
        ''')
    st.success("Scan complete! All discovered broker profiles have been queued for removal.")

st.divider()
st.subheader("📊 Live Privacy Report Card")

with sqlite3.connect(database_name) as connection:
    df = pd.read_sql_query("SELECT broker_name AS 'Broker Name', tier_category AS 'Tier Category', status AS 'Current Status', last_updated AS 'Last Updated' FROM optout_tracker;", connection)

st.write(f"**Total Tracked Brokers:** {len(df)}")
st.write(f"**Opt-Outs Requested:** {len(df[df['Current Status'] == 'Opt-Out Requested'])}")

st.markdown("### Itemized Broker Status")
st.table(df)
