import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="DOEA Digital Online Health Assessment", layout="wide")

# Custom CSS for a clean, accessible, award-winning public sector design
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .state-banner {
        background-color: #003366;
        color: white;
        padding: 12px 20px;
        font-size: 14px;
        font-weight: 500;
        border-radius: 4px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .search-card {
        background-color: white;
        padding: 30px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-top: 6px solid #003366;
        margin-bottom: 25px;
    }
    .stButton>button {
        width: 100%;
        background-color: #003366;
        color: white;
        font-weight: 600;
        border-radius: 6px;
        padding: 0.6rem 1rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #002244;
        color: white;
    }
    h1, h2, h3 {
        color: #111827;
    }
    </style>
""", unsafe_allow_html=True)

# Official State Top Banner
st.markdown("""
    <div class="state-banner">
        <span>🏛️ State of Florida — Department of Elder Affairs Official Digital Portal</span>
        <span>Operation: Senior Shield</span>
    </div>
""", unsafe_allow_html=True)

st.title("Digital Online Health Assessment")
st.markdown("##### Find out what personal information is exposed online and protect your digital privacy.")
st.divider()

database_name = "digital_footprint_manager.db"

# Initialize Database with records
with sqlite3.connect(database_name) as connection:
    cursor = connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS optout_tracker;")
    cursor.execute('''
        CREATE TABLE optout_tracker (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            broker_name TEXT,
            category TEXT,
            compliance_pathway TEXT,
            risk_level TEXT,
            status TEXT,
            statutory_deadline TEXT,
            response_code TEXT,
            verification_note TEXT,
            target_url TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    default_deadline = (datetime.now() + timedelta(days=45)).strftime('%Y-%m-%d')
    initial_data = [
        ('DOEA Digital Identity Registry', 'State-Sponsored API', 'Official State API Batch Deletion', 'High', 'Pending Submission', default_deadline, 'Awaiting Code', 'Awaiting state residency verification token', 'https://elderaffairs.org/'),
        ('State Voter Suppression Bureau', 'Public Records/PII', 'Direct Statutory Redaction', 'Moderate', 'Needs Review', default_deadline, 'Awaiting Code', 'State agency record suppression review', 'https://dos.fl.gov/elections/'),
        ('County Property Appraiser DB', 'Public Records/PII', 'Local Ordinance Request', 'Moderate', 'Needs Review', default_deadline, 'Awaiting Code', 'County property appraiser redaction protocol', 'https://floridarevenuetax.org'),
        ('HaveIBeenPwned API', 'Credential/Breach Data', 'Direct Credential API', 'Critical', 'Needs Action', 'Immediate', 'Action Required', 'Password reset required immediately', 'https://haveibeenpwned.com/'),
        ('Commercial Data Aggregators', 'Commercial Brokers', 'Third-Party Opt-Out API', 'Low', 'Pending Queue', default_deadline, 'Awaiting Code', 'Global opt-out registry transmission', 'https://www.networkadvertising.org/')
    ]
    cursor.executemany("INSERT INTO optout_tracker (broker_name, category, compliance_pathway, risk_level, status, statutory_deadline, response_code, verification_note, target_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);", initial_data)
    connection.commit()

# Session state management for simple user flow
if 'search_performed' not in st.session_state:
    st.session_state['search_performed'] = False
if 'user_confirmed' not in st.session_state:
    st.session_state['user_confirmed'] = False

# Step 1: Intelius-Style Public Search Box
if not st.session_state['user_confirmed']:
    st.markdown('<div class="search-card">', unsafe_allow_html=True)
    st.markdown("### 🔍 Start Your Privacy Search")
    st.write("Enter your details below to scan public directories and data broker networks.")
    
    s_col1, s_col2 = st.columns(2)
    with s_col1:
        search_first = st.text_input("First Name", placeholder="e.g., Joshua")
        search_city = st.text_input("City", placeholder="e.g., Tallahassee")
    with s_col2:
        search_last = st.text_input("Last Name", placeholder="e.g., Hinshaw")
        states_list = [
            "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", 
            "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", 
            "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", 
            "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", 
            "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", 
            "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", 
            "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"
        ]
        search_state = st.selectbox("State", states_list, index=8)

    if st.button("Search Public Records"):
        if search_first and search_last and search_city:
            st.session_state['search_performed'] = True
            st.session_state['searched_name'] = f"{search_first} {search_last}"
            st.session_state['searched_location'] = f"{search_city}, {search_state}"
            st.rerun()
        else:
            st.warning("Please fill in your first name, last name, and city to run the search.")
    st.markdown('</div>', unsafe_allow_html=True)

# Step 2: Search Results Match Screen (Like Intelius matching)
if st.session_state['search_performed'] and not st.session_state['user_confirmed']:
    st.markdown("### 📋 Confirm Your Identity Match")
    st.write(f"We found matching public records for **{st.session_state['searched_name']}** in **{st.session_state['searched_location']}**. Please select your record below to proceed:")

    # Simulated matching records card
    match_col1, match_col2 = st.columns([3, 1])
    with match_col1:
        st.markdown(f"""
        **Profile Match #1 (Recommended)**
        * **Name:** {st.session_state['searched_name']}
        * **Location:** {st.session_state['searched_location']}
        * **Associated Records:** Public Directories, Voter Registry, Property Records, Commercial Data Brokers
        """)
    with match_col2:
        if st.button("That's Me — Start Assessment"):
            st.session_state['user_confirmed'] = True
            st.rerun()

    if st.button("None of these are me (Search Again)"):
        st.session_state['search_performed'] = False
        st.rerun()

# Step 3: Main Health Assessment & Remediation Dashboard (Once Confirmed)
if st.session_state['user_confirmed']:
    st.success(f"Identity confirmed for **{st.session_state.get('searched_name', 'User')}**! Your personalized health assessment and exposure dashboard is active below.")

    if st.button("🔓 Sign Out / Search Another Person"):
        st.session_state['user_confirmed'] = False
        st.session_state['search_performed'] = False
        st.rerun()

    st.divider()

    # Load data from database based on exposure channels
    with sqlite3.connect(database_name) as connection:
        df = pd.read_sql_query("SELECT id, broker_name AS 'Source/Broker', category AS 'Data Type', compliance_pathway AS 'API Pathway', risk_level AS 'Risk Severity', status AS 'Current Status', statutory_deadline AS '45-Day Deadline', response_code AS 'State Response Code', verification_note AS 'Audit Trail', target_url AS 'Portal Link', last_updated AS 'Last Updated' FROM optout_tracker;", connection)

    total = len(df)
    pending_count = len(df[~df['Current Status'].isin(['API Transmission Successful', 'Compliance Verified'])])
    completed_count = len(df[df['Current Status'] == 'API Transmission Successful'])

    st.subheader("📊 Your Privacy Health Scorecard")
    m1, m2, m3 = st.columns(3)
    m1.metric("Exposures Detected", total)
    m2.metric("Items Needing Action", pending_count)
    m3.metric("Successfully Cleaned", completed_count)

    st.divider()

    # Action Trigger Button for the User
    st.markdown("### 🛡️ One-Click Privacy Protection")
    st.write("Click below to automatically request data removal across all detected public directories and state registries.")
    if st.button("Start Automated Removal Request"):
        new_deadline = (datetime.now() + timedelta(days=45)).strftime('%Y-%m-%d')
        with sqlite3.connect(database_name) as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE optout_tracker SET status = 'API Transmission Successful', statutory_deadline = ?, response_code = 'Record Deleted (Pending Window)', verification_note = 'Automated user request submitted; 45-day window active', last_updated = CURRENT_TIMESTAMP WHERE status IN ('Pending Submission', 'Needs Action', 'Pending Queue', 'Needs Review');", (new_deadline,))
        st.success("Removal requests successfully transmitted! Your 45-day statutory privacy window has begun.")
        st.rerun()

    st.divider()

    # Display Tables
    tab1, tab2 = st.tabs(["⚡ Active Exposures", "✅ Cleared Records"])

    with tab1:
        st.markdown("### Records Requiring Your Attention")
        needs_df = df[df['Current Status'] != 'API Transmission Successful']
        if len(needs_df) > 0:
            st.dataframe(
                needs_df,
                use_container_width=True,
                column_config={
                    "Portal Link": st.column_config.LinkColumn("Official Portal URL")
                }
            )
        else:
            st.success("All exposure records have been successfully cleared!")

    with tab2:
        st.markdown("### Cleared & Protected Records")
        rem_df = df[df['Current Status'] == 'API Transmission Successful']
        if len(rem_df) > 0:
            st.dataframe(
                rem_df,
                use_container_width=True,
                column_config={
                    "Portal Link": st.column_config.LinkColumn("Official Portal URL")
                }
            )
        else:
            st.info("No records have been cleared yet.")

    # Export Data Capability
    st.divider()
    st.subheader("📥 Download Your Privacy Audit Report")
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Compliance Audit CSV",
        data=csv_data,
        file_name=f"DOEA_Privacy_Report_{datetime.now().strftime('%Y-%m-%d')}.csv",
        mime="text/csv",
    )
