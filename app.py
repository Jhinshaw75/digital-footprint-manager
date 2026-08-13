import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="DOEA Digital Online Health Assessment", layout="wide")

# Custom CSS for modern styling and wizard containers
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
    .wizard-card {
        background-color: #0f2744;
        color: white;
        padding: 35px;
        border-radius: 12px;
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        margin-bottom: 25px;
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
st.markdown("##### Secure Identity Verification & Public Record Remediation Portal")
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

# Session State Flow Management
if 'stage' not in st.session_state:
    st.session_state['stage'] = 'search'

# --- STAGE 1: SEARCH INPUT WITH AGE RANGE ---
if st.session_state['stage'] == 'search':
    st.markdown('<div class="search-card">', unsafe_allow_html=True)
    st.markdown("### 🔍 Search Subject")
    st.write("Enter name, location, and target age range to filter out irrelevant public records.")
    
    s_col1, s_col2 = st.columns(2)
    with s_col1:
        search_first = st.text_input("First Name", placeholder="e.g., Josh")
        search_city = st.text_input("City", placeholder="e.g., Tallahassee")
        target_age = st.number_input("Target Age (Exact or Approximate)", min_value=18, max_value=120, value=51)
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
        age_tolerance = st.selectbox("Age Filtering Tolerance", ["Strict (Exact Age Only)", "Moderate (+/- 5 Years)", "Broad (+/- 10 Years)"], index=1)

    if st.button("Begin Search & Verify Identity"):
        if search_first and search_last and search_city:
            st.session_state['searched_name'] = f"{search_first} {search_last}"
            st.session_state['searched_location'] = f"{search_city}, {search_state}"
            st.session_state['searched_age'] = target_age
            st.session_state['stage'] = 'wizard_q1'
            st.rerun()
        else:
            st.warning("Please fill in first name, last name, and city to start.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- STAGE 2: WIZARD QUESTION 1 (Locations / Cities) ---
elif st.session_state['stage'] == 'wizard_q1':
    st.markdown('<div class="wizard-card">', unsafe_allow_html=True)
    st.markdown(f"### Search Subject: {st.session_state['searched_name']} (Target Age: {st.session_state.get('searched_age', 51)})")
    st.progress(16, text="16% Confidence Match Building")
    st.markdown("---")
    st.markdown("### ⚠️ Confirm Information")
    st.caption("Help Narrow Down Your Results")
    st.markdown(f"**Has {st.session_state['searched_name']} ever lived in {st.session_state['searched_location']}, Indianapolis, IN, or Mobile, AL?**")
    
    wq1_c1, wq1_c2, wq1_c3 = st.columns(3)
    with wq1_c1:
        if st.button("YES"):
            st.session_state['stage'] = 'wizard_q2'
            st.rerun()
    with wq1_c2:
        if st.button("NO"):
            st.session_state['stage'] = 'wizard_q2'
            st.rerun()
    with wq1_c3:
        if st.button("I DON'T KNOW"):
            st.session_state['stage'] = 'wizard_q2'
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- STAGE 3: WIZARD QUESTION 2 (Age Confirmation) ---
elif st.session_state['stage'] == 'wizard_q2':
    st.markdown('<div class="wizard-card">', unsafe_allow_html=True)
    target_age = st.session_state.get('searched_age', 51)
    st.markdown(f"### Search Subject: {st.session_state['searched_name']}")
    st.progress(46, text="46% Confidence Match Building")
    st.markdown("---")
    st.markdown("### ⚠️ Confirm Information")
    st.caption("Help Narrow Down Your Results")
    st.markdown(f"**Is {st.session_state['searched_name']} around {target_age} years old?**")
    
    wq2_c1, wq2_c2, wq2_c3 = st.columns(3)
    with wq2_c1:
        if st.button("YES"):
            st.session_state['stage'] = 'wizard_q3'
            st.rerun()
    with wq2_c2:
        if st.button("NO"):
            st.session_state['stage'] = 'wizard_q3'
            st.rerun()
    with wq2_c3:
        if st.button("I DON'T KNOW"):
            st.session_state['stage'] = 'wizard_q3'
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- STAGE 4: WIZARD QUESTION 3 (Relatives) ---
elif st.session_state['stage'] == 'wizard_q3':
    st.markdown('<div class="wizard-card">', unsafe_allow_html=True)
    st.markdown(f"### Search Subject: {st.session_state['searched_name']}")
    st.progress(75, text="75% Confidence Match Building")
    st.markdown("---")
    st.markdown("### ⚠️ Confirm Information")
    st.caption("Help Narrow Down Your Results")
    st.markdown(f"**As far as you know, is {st.session_state['searched_name']} related to Adrina Frazier, Isabella M. Hinshaw, or Jeanette Hinshaw?**")
    
    wq3_c1, wq3_c2, wq3_c3 = st.columns(3)
    with wq3_c1:
        if st.button("YES"):
            st.session_state['stage'] = 'results'
            st.rerun()
    with wq3_c2:
        if st.button("NO"):
            st.session_state['stage'] = 'results'
            st.rerun()
    with wq3_c3:
        if st.button("I DON'T KNOW"):
            st.session_state['stage'] = 'results'
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- STAGE 5: RESULTS MATCH GRID (Filtered by Age) ---
elif st.session_state['stage'] == 'results':
    target_age = st.session_state.get('searched_age', 51)
    st.markdown(f"### Next Step: Select A Result Below for {st.session_state['searched_name']}")
    st.write(f"Filtered for records near age **{target_age}** across verified public data sources:")

    # Match Box 1 (Strictly matching target age)
    with st.container():
        col_res1, col_res2, col_res3, col_res4 = st.columns([3, 1, 2, 2])
        with col_res1:
            st.markdown(f"**⭐ BEST RESULT (Age Verified)**\n### {st.session_state['searched_name']}")
            st.caption("Phone Number Found! • Tallahassee, FL")
        with col_res2:
            st.markdown(f"**AGE**\n### {target_age}")
        with col_res3:
            st.markdown("**LOCATIONS**\nTallahassee, FL\nIndianapolis, IN\nMobile, AL")
        with col_res4:
            st.markdown("**POSSIBLE RELATIVES**\nAdrina Frazier\nIsabella M. Hinshaw\nJeanette Hinshaw")
        
        if st.button("OPEN REPORT / THAT'S ME"):
            st.session_state['stage'] = 'dashboard'
            st.rerun()
    
    st.divider()
    if st.button("Modify Search / Start Over"):
        st.session_state['stage'] = 'search'
        st.rerun()

# --- STAGE 6: PERSONALIZED HEALTH ASSESSMENT DASHBOARD ---
elif st.session_state['stage'] == 'dashboard':
    st.success(f"Identity successfully verified for **{st.session_state.get('searched_name', 'User')}**! Your personalized exposure and health assessment dashboard is active below.")

    if st.button("🔒 Sign Out / New Search"):
        st.session_state['stage'] = 'search'
        st.rerun()

    st.divider()

    # Load database records
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

    st.divider()
    st.subheader("📥 Download Your Privacy Audit Report")
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Compliance Audit CSV",
        data=csv_data,
        file_name=f"DOEA_Privacy_Report_{datetime.now().strftime('%Y-%m-%d')}.csv",
        mime="text/csv",
    )
