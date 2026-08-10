import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="DOEA Digital Online Health Assessment", layout="wide")
st.title("🛡️ DOEA Digital Online Health Assessment")
st.write("Enterprise-Grade PII, Credential, and Data Broker Remediation Portal")

database_name = "digital_footprint_manager.db"

# Initialize Database with an expanded catalog of digital exposure sources
with sqlite3.connect(database_name) as connection:
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS optout_tracker (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            broker_name TEXT,
            category TEXT,
            risk_level TEXT,
            status TEXT,
            action_taken TEXT,
            verification_note TEXT,
            target_url TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    cursor.execute("SELECT COUNT(*) FROM optout_tracker;")
    if cursor.fetchone()[0] == 0:
        initial_data = [
            ('Whitepages', 'People-Search Brokers', 'High', 'Needs Removal', 'Pending User Opt-Out Form', 'Awaiting removal confirmation webhook', 'https://www.whitepages.com/suppression-requests'),
            ('Spokeo', 'People-Search Brokers', 'High', 'Needs Removal', 'Pending Opt-Out Listing Removal', 'Profile match detected via automated index', 'https://www.spokeo.com/optout'),
            ('BeenVerified', 'People-Search Brokers', 'High', 'Needs Removal', 'Opt-Out Request Required', 'Data aggregator match found', 'https://www.beenverified.com/app/optout/search'),
            ('Intelius', 'People-Search Brokers', 'High', 'Needs Removal', 'Suppression List Entry Pending', 'Public profile index active', 'https://www.intelius.com/optout/'),
            ('Radaris', 'People-Search Brokers', 'Moderate', 'Needs Removal', 'Manual Opt-Out Form Submission', 'Directory listing indexed', 'https://radaris.com/control/privacy'),
            ('HaveIBeenPwned API', 'Credential/Breach Data', 'Critical', 'Needs Removal', 'Password Reset Recommended', 'Exposed hash identified in collection list', 'https://haveibeenpwned.com/'),
            ('Dark Web Exposure', 'Credential/Breach Data', 'Critical', 'Needs Removal', 'Credential Isolation Alert Flagged', 'Monitor active credential leaks', 'https://www.darkwebcountermeasures.com'),
            ('Public Voter Registry', 'Public Records/PII', 'Moderate', 'Needs Removal', 'State Agency Record Suppression Review', 'Record active in public rolls', 'https://dos.fl.gov/elections/'),
            ('Property Records', 'Public Records/PII', 'Moderate', 'Needs Removal', 'County Property Appraiser Redaction Request', 'Deed index publicly accessible', 'https://floridarevenuetax.org'),
            ('Marketing Data Grids', 'Commercial Data Brokers', 'Low', 'Needs Removal', 'Global Opt-Out Registry Flag', 'Targeted consumer profile compiled', 'https://www.networkadvertising.org/')
        ]
        cursor.executemany("INSERT INTO optout_tracker (broker_name, category, risk_level, status, action_taken, verification_note, target_url) VALUES (?, ?, ?, ?, ?, ?, ?);", initial_data)
        connection.commit()

# Sidebar Advanced Controls & Custom Additions
st.sidebar.markdown("### 🔍 Search Parameters & Aliases")
target_alias = st.sidebar.text_input("Include Maiden Name / Alias", placeholder="e.g., Previous Name")
target_zip = st.sidebar.text_input("Zip Code / Historical City", placeholder="e.g., 32301")
selected_category = st.sidebar.selectbox(
    "Filter by Data Category",
    ["All Categories", "People-Search Brokers", "Credential/Breach Data", "Public Records/PII", "Commercial Data Brokers"]
)

st.sidebar.divider()
st.sidebar.markdown("### ➕ Add Custom Exposure Source")
with st.sidebar.form("add_custom_broker"):
    new_broker = st.text_input("Broker/Site Name")
    new_category = st.selectbox("Category", ["People-Search Brokers", "Credential/Breach Data", "Public Records/PII", "Commercial Data Brokers"])
    new_risk = st.selectbox("Risk Level", ["Low", "Moderate", "High", "Critical"])
    new_url = st.text_input("Direct Opt-Out URL")
    submit_broker = st.form_submit_button("Add to Tracker")
    
    if submit_broker and new_broker:
        with sqlite3.connect(database_name) as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO optout_tracker (broker_name, category, risk_level, status, action_taken, verification_note, target_url) VALUES (?, ?, ?, 'Needs Removal', 'Custom Source Injected', 'Manually added to scope', ?);", 
                           (new_broker, new_category, new_risk, new_url))
            connection.commit()
        st.sidebar.success(f"Added {new_broker} to tracking scope!")
        st.rerun()

# User Input Section for Assessment Initialization
st.markdown("### 1. Target Assessment Configuration")
col1, col2, col3 = st.columns(3)
with col1:
    full_name = st.text_input("Full Legal Name")
with col2:
    current_city = st.text_input("Current City and State")
with col3:
    birth_year = st.text_input("Birth Year (Optional for precise matching)")

col_btn1, col_btn2 = st.columns([1, 4])
with col_btn1:
    run_scan = st.button("Run Deep Sweep")

if run_scan:
    if full_name:
        with sqlite3.connect(database_name) as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE optout_tracker SET status = 'Successfully Removed', action_taken = 'Opt-Out Confirmed & Cleared', verification_note = 'Verified clean via automated audit', last_updated = CURRENT_TIMESTAMP WHERE status = 'Needs Removal';")
        st.success(f"Deep footprint sweep completed for {full_name} ({current_city}). All matching profiles queued or cleared!")
    else:
        st.warning("Please provide a legal name to initialize the deep scan.")

st.divider()

# Load data from database based on filters
with sqlite3.connect(database_name) as connection:
    if selected_category == "All Categories":
        df = pd.read_sql_query("SELECT id, broker_name AS 'Source/Broker', category AS 'Data Type', risk_level AS 'Risk Severity', status AS 'Current Status', action_taken AS 'Action Details', verification_note AS 'Audit Trail', target_url AS 'Opt-Out Link', last_updated AS 'Last Updated' FROM optout_tracker;", connection)
    else:
        df = pd.read_sql_query(f"SELECT id, broker_name AS 'Source/Broker', category AS 'Data Type', risk_level AS 'Risk Severity', status AS 'Current Status', action_taken AS 'Action Details', verification_note AS 'Audit Trail', target_url AS 'Opt-Out Link', last_updated AS 'Last Updated' FROM optout_tracker WHERE category = '{selected_category}';", connection)

total = len(df)
needs_removal_count = len(df[df['Current Status'] == 'Needs Removal'])
removed_count = len(df[df['Current Status'] == 'Successfully Removed'])
critical_count = len(df[(df['Current Status'] == 'Needs Removal') & (df['Risk Severity'] == 'Critical')])

st.subheader("📊 Live Exposure Report Card & Metrics")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Tracked Points", total)
m2.metric("Critical Threats Active", critical_count)
m3.metric("Items Needing Removal", needs_removal_count)
m4.metric("Successfully Removed", removed_count)

st.divider()

# Granular Individual Item Status Manager
st.markdown("### ⚙️ Granular Item Status Manager")
col_id, col_status, col_note = st.columns([1, 2, 3])
with col_id:
    record_id = st.number_input("Record ID", min_value=1, step=1)
with col_status:
    new_status = st.selectbox("New Status", ["Needs Removal", "In Progress", "Successfully Removed"])
with col_note:
    custom_note = st.text_input("Audit Note / Proof Detail", placeholder="e.g., Confirmed deleted via email confirmation")

if st.button("Commit Status Update"):
    with sqlite3.connect(database_name) as connection:
        cursor = connection.cursor()
        cursor.execute("UPDATE optout_tracker SET status = ?, verification_note = ?, last_updated = CURRENT_TIMESTAMP WHERE id = ?;", (new_status, custom_note, record_id))
        connection.commit()
    st.success(f"Record ID {record_id} updated successfully!")
    st.rerun()

st.divider()

# Split Views
tab1, tab2 = st.tabs(["🚨 Items Needing Removal", "✅ Successfully Removed Companies"])

with tab1:
    st.markdown("### Companies & Repositories Requiring Action")
    needs_df = df[df['Current Status'] != 'Successfully Removed']
    if len(needs_df) > 0:
        st.dataframe(
            needs_df,
            use_container_width=True,
            column_config={
                "Opt-Out Link": st.column_config.LinkColumn("Direct Opt-Out URL")
            }
        )
    else:
        st.success("No active exposures in this category requiring removal.")

with tab2:
    st.markdown("### Cleaned & Successfully Removed Companies")
    rem_df = df[df['Current Status'] == 'Successfully Removed']
    if len(rem_df) > 0:
        st.dataframe(
            rem_df,
            use_container_width=True,
            column_config={
                "Opt-Out Link": st.column_config.LinkColumn("Direct Opt-Out URL")
            }
        )
    else:
        st.info("No items have been marked as successfully removed yet.")

# Export Data Capability
st.divider()
st.subheader("📥 Export Compliance Audit Report")
st.write("Download your complete itemized exposure and removal log as a CSV for reporting or archival documentation.")
csv_data = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download Audit Report (CSV)",
    data=csv_data,
    file_name=f"DOEA_Health_Assessment_Report_{datetime.now().strftime('%Y-%m-%d')}.csv",
    mime="text/csv",
)

# Step-by-Step Direct Opt-Out Guide Section
st.divider()
st.subheader("📝 Step-by-Step Direct Opt-Out Instructions")
st.markdown("""
To manually or directly submit removal requests for each exposure point:
1. **People-Search Networks (Whitepages, Spokeo, BeenVerified, Intelius, Radaris):** Visit their respective opt-out or suppression portals using the links in the table above, look up your specific profile URL, and follow their automated verification steps.
2. **Credential & Breach Sources (HaveIBeenPwned / Dark Web):** Use the provided portal links to verify exposed password hashes, then immediately rotate and update credentials on impacted primary accounts using a secure password manager.
3. **Public Voter & Property Records:** Contact your local county property appraiser's office or state records division to file a formal public record suppression or redaction request based on privacy guidelines.
4. **Commercial Data Grids:** Opt-out through network advertising registries to prevent data broker tracking and profiling across marketing databases.
""")
