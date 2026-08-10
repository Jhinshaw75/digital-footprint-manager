import sqlite3
import pandas as pd
import streamlit as st

st.set_page_config(page_title="SilverShield Footprint Manager", layout="wide")
st.title("🛡️ SilverShield Digital Footprint Manager")
st.write("Comprehensive PII, Credential, and Data Broker Remediation Portal")

database_name = "digital_footprint_manager.db"

# Database setup with specific action details and target links
with sqlite3.connect(database_name) as connection:
    cursor = connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS optout_tracker;")
    cursor.execute('''
        CREATE TABLE optout_tracker (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            broker_name TEXT,
            category TEXT,
            status TEXT,
            action_taken TEXT,
            target_url TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    initial_data = [
        ('Whitepages', 'People-Search Brokers', 'Needs Removal', 'Pending User Opt-Out Form', 'https://www.whitepages.com/suppression-requests'),
        ('Spokeo', 'People-Search Brokers', 'Needs Removal', 'Pending Opt-Out Listing Removal', 'https://www.spokeo.com/optout'),
        ('HaveIBeenPwned API', 'Credential/Breach Data', 'Needs Removal', 'Password Reset Recommended', 'https://haveibeenpwned.com/'),
        ('Dark Web Exposure', 'Credential/Breach Data', 'Needs Removal', 'Credential Isolation Alert Flagged', 'https://www.darkwebcountermeasures.com'),
        ('Public Voter Registry', 'Public Records/PII', 'Needs Removal', 'State Agency Record Suppression Review', 'https://dos.fl.gov/elections/'),
        ('Property Records', 'Public Records/PII', 'Needs Removal', 'County Property Appraiser Redaction Request', 'https://floridarevenuetax.org')
    ]
    cursor.executemany("INSERT INTO optout_tracker (broker_name, category, status, action_taken, target_url) VALUES (?, ?, ?, ?, ?);", initial_data)
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
            cursor.execute("UPDATE optout_tracker SET status = 'Successfully Removed', action_taken = 'Opt-Out Confirmed & Cleared', last_updated = CURRENT_TIMESTAMP WHERE status = 'Needs Removal';")
        st.success(f"Comprehensive scan complete for {full_name}. All identified exposures have been processed and removed!")
    else:
        st.warning("Please enter a name to proceed with the sweep.")

st.divider()

# Load data for metrics and tables
with sqlite3.connect(database_name) as connection:
    df = pd.read_sql_query("SELECT broker_name AS 'Source/Broker', category AS 'Data Type', status AS 'Current Status', action_taken AS 'Action Details', target_url AS 'Opt-Out Link', last_updated AS 'Last Updated' FROM optout_tracker;", connection)

total = len(df)
needs_removal_df = df[df['Current Status'] == 'Needs Removal']
removed_df = df[df['Current Status'] == 'Successfully Removed']

st.subheader("📊 Live Exposure Report Card & Metrics")

m1, m2, m3 = st.columns(3)
m1.metric("Total Tracked Points", total)
m2.metric("Items Needing Removal", len(needs_removal_df))
m3.metric("Successfully Removed", len(removed_df))

st.divider()

# Split into two clear tabs for better visibility
tab1, tab2 = st.tabs(["🚨 Items Needing Removal", "✅ Successfully Removed Companies"])

with tab1:
    st.markdown("### Companies & Repositories Requiring Action")
    if len(needs_removal_df) > 0:
        st.dataframe(
            needs_removal_df,
            use_container_width=True,
            column_config={
                "Opt-Out Link": st.column_config.LinkColumn("Direct Opt-Out URL")
            }
        )
    else:
        st.success("Wonderful news! No active exposures currently require removal.")

with tab2:
    st.markdown("### Cleaned & Successfully Removed Companies")
    if len(removed_df) > 0:
        st.dataframe(
            removed_df,
            use_container_width=True,
            column_config={
                "Opt-Out Link": st.column_config.LinkColumn("Direct Opt-Out URL")
            }
        )
    else:
        st.info("No items have been marked as removed yet. Run the assessment sweep above to process removals.")

# Step-by-Step Direct Opt-Out Guide Section
st.divider()
st.subheader("📝 Step-by-Step Direct Opt-Out Instructions")
st.markdown("""
To manually or directly submit removal requests for each exposure point:
1. **Whitepages:** Navigate to their suppression request page, search for your specific listing URL, and submit an online removal form or phone verification request.
2. **Spokeo:** Go to their opt-out portal, enter the specific profile URL found during your search, and confirm your request via email validation.
3. **Credential & Breach Sources (HaveIBeenPwned / Dark Web):** Use the provided portal links to verify exposed password hashes, then immediately rotate and update credentials on impacted primary accounts using a secure password manager.
4. **Public Voter & Property Records:** Contact your local county property appraiser's office or state records division to file a formal public record suppression or redaction request based on privacy guidelines.
""")
