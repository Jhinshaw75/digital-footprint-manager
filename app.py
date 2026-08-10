import sqlite3
import pandas as pd
import streamlit as st

st.title("Digital Footprint Manager")
st.write("Privacy Report Card & Tracker")

database_name = "digital_footprint_manager.db"

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

try:
    with sqlite3.connect(database_name) as connection:
        df = pd.read_sql_query("SELECT broker_name AS 'Broker Name', tier_category AS 'Tier Category', status AS 'Current Status', last_updated AS 'Last Updated' FROM optout_tracker;", connection)
    
    st.write(f"**Total Tracked Brokers:** {len(df)}")
    st.write(f"**Opt-Outs Requested:** {len(df[df['Current Status'] == 'Opt-Out Requested'])}")
    
    st.markdown("### Itemized Broker Status")
    st.table(df)
except Exception as e:
    st.info("Initializing tracker database. Click the button above to run your first sweep!")
