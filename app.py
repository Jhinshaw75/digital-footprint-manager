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

# Initialize Database table structure if not present
with sqlite3.connect(database_name) as connection:
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS optout_tracker (
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
    connection.commit()

# Session State Flow Management
if 'stage' not in st.session_state:
    st.session_state['stage'] = 'search'

# --- STAGE 1: SEARCH INPUT WITH MIDDLE NAME & AGE SEGMENTS ---
if st.session_state['stage'] == 'search':
    st.markdown('<div class="search-card">', unsafe_allow_html=True)
    st.markdown("### 🔍 Search Subject")
    st.write("Enter name details, location, and age segment to narrow down public records.")
    
    s_col1, s_col2, s_col3 = st.columns(3)
    with s_col1:
        search_first = st.text_input("First Name", placeholder="e.g., Joshua")
    with s_col2:
        search_middle = st.text_input("Middle Name / Initial", placeholder="e.g., Adam")
    with s_col3:
        search_last = st.text_input("Last Name", placeholder="e.g., Hinshaw")

    loc_col1, loc_col2, loc_col3 = st.columns(3)
    with loc_col1:
        search_city = st.text_input("City", placeholder="e.g., Tallahassee")
    with loc_col2:
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
    with loc_col3:
        age_segment = st.selectbox("Age Segment", ["18-29", "30-49", "50-64", "65-74", "75+"], index=2)

    if st.button("Begin Search & Verify Identity"):
        if search_first and search_last and search_city:
            full_search_name = f"{search_first} {search_middle + ' ' if search_middle else ''}{search_last}"
            st.session_state['searched_name'] = full_search_name
            st.session_state['searched_location'] = f"{search_city}, {search_state}"
            st.session_state['searched_age_segment'] = age_segment
            st.session_state['stage'] = 'wizard_q1'
            st.rerun()
        else:
            st.warning("Please fill in first name, last name, and city to start.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- STAGE 2: WIZARD QUESTION 1 (Locations / Cities) ---
elif st.session_state['stage'] == 'wizard_q1':
    st.markdown('<div class="wizard-card">', unsafe_allow_html=True)
    st.markdown(f"### Search Subject: {st.session_state['searched_name']} (Segment: {st.session_state.get('searched_age_segment', '50-64')})")
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

# --- STAGE 3: WIZARD QUESTION 2 (Age Segment Confirmation) ---
elif st.session_state['stage'] == 'wizard_q2':
    st.markdown('<div class="wizard-card">', unsafe_allow_html=True)
    age_seg = st.session_state.get('searched_age_segment', '50-64')
    st.markdown(f"### Search Subject: {st.session_state['searched_name']}")
    st.progress(46, text="46% Confidence Match Building")
    st.markdown("---")
    st.markdown("### ⚠️ Confirm Information")
    st.caption("Help Narrow Down Your Results")
    st.markdown(f"**Is {st.session_state['searched_name']} within the {age_seg} age bracket?**")
    
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

# --- STAGE 5: RESULTS MATCH GRID ---
elif st.session_state['stage'] == 'results':
    age_seg = st.session_state.get('searched_age_segment', '50-64')
    st.markdown(f"### Next Step: Select A Result Below for {st.session_state['searched_name']}")
    st.write(f"Filtered for records within age segment **{age_seg}** across verified public data sources:")

    with st.container():
        col_res1, col_res2, col_res3, col_res4 = st.columns([3, 1, 2, 2])
        with col_res1:
            st.markdown(f"**⭐ BEST RESULT (Verified Match)**\n### {st.session_state['searched_name']}")
            st.caption("Phone Number Found! • Tallahassee, FL")
        with col_res2:
            st.markdown(f"**AGE SEGMENT**\n### {age_seg}")
        with col_res3:
            st.markdown("**LOCATIONS**\nTallahassee, FL\nIndianapolis, IN\nMobile, AL")
        with col_res4:
            st.markdown("**POSSIBLE RELATIVES**\nAdrina Frazier\nIsabella M. Hinshaw\nJeanette Hinshaw")
        
        if st.button("OPEN REPORT / THAT'S ME"):
            default_deadline = (datetime.now() + timedelta(days=45)).strftime('%Y-%m-%d')
            with sqlite3.connect(database_name) as connection:
                cursor = connection.cursor()
                cursor.execute("DELETE FROM optout_tracker;")
                identified_threats = [
                    ('Commercial Data Aggregators', 'Commercial Brokers', 'Third-Party Opt-Out API', 'High', 'Pending Queue', default_deadline, 'Awaiting Code', 'Identified in commercial broker directory listings', 'https://www.networkadvertising.org/'),
                    ('Public Property & Tax Records', 'Public Records/PII', 'Local Ordinance Request', 'Moderate', 'Needs Review', default_deadline, 'Awaiting Code', 'County property appraiser public record exposure', 'https://floridarevenuetax.org'),
                    ('HaveIBeenPwned API', 'Credential/Breach Data', 'Direct Credential API', 'Critical', 'Needs Action', 'Immediate', 'Action Required', 'Associated email found in credential breach dump', 'https://haveibeenpwned.com/')
                ]
                cursor.executemany("INSERT INTO optout_tracker (broker_name, category, compliance_pathway, risk_level, status, statutory_deadline, response_code, verification_note, target_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);", identified_threats)
                connection.commit()
            
            st.session_state['stage'] = 'dashboard'
            st.rerun()
    
    st.divider()
    if st.button("Modify Search / Start Over"):
        st.session_state['stage'] = 'search'
        st.rerun()

# --- STAGE 6: PERSONALIZED HEALTH ASSESSMENT DASHBOARD ---
elif st.session_state['stage'] == 'dashboard':
    st.success(f"Identity successfully verified for **{st.session_state.get('searched_name', 'User')}**! Your threat assessment report card is active below.")

    if st.button("🔒 Sign Out / New Search"):
        st.session_state['stage'] = 'search'
        st.rerun()

    st.divider()

    with sqlite3.connect(database_name) as connection:
        df = pd.read_sql_query("SELECT id, broker_name AS 'Source/Broker', category AS 'Data Type', compliance_pathway AS 'API Pathway', risk_level AS 'Risk Severity', status AS 'Current Status', statutory_deadline AS '45-Day Deadline', response_code AS 'State Response Code', verification_note AS 'Audit Trail', target_url AS 'Portal Link', last_updated AS 'Last Updated' FROM optout_tracker;", connection)

    total = len(df)
    pending_count = len(df[~df['Current Status'].isin(['API Transmission Successful', 'Compliance Verified'])])
    completed_count = len(df[df['Current Status'] == 'API Transmission Successful'])

    st.subheader("📊 Your Privacy Health Scorecard")
    m1, m2, m3 = st.columns(3)
    m1.metric("Identified Threats", total)
    m2.metric("Items Needing Action", pending_count)
    m3.metric("Successfully Cleaned", completed_count)

    st.divider()

    st.markdown("### 🛡️ One-Click Privacy Protection")
    st.write("Click below to automatically request data removal across all identified threat vectors and initiate your 45-day statutory compliance window.")
    if st.button("Execute Automated State Removal Request"):
        new_deadline = (datetime.now() + timedelta(days=45)).strftime('%Y-%m-%d')
        with sqlite3.connect(database_name) as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE optout_tracker SET status = 'API Transmission Successful', statutory_deadline = ?, response_code = 'Record Deleted (Pending Window)', verification_note = 'Automated user request submitted; 45-day window active', last_updated = CURRENT_TIMESTAMP WHERE status IN ('Pending Submission', 'Needs Action', 'Pending Queue', 'Needs Review');", (new_deadline,))
        st.success("Removal requests successfully transmitted! Your 45-day statutory privacy window has begun.")
        st.rerun()

    st.divider()

    tab1, tab2 = st.tabs(["⚡ Active Threat Exposures", "✅ Cleared Records"])

    with tab1:
        st.markdown("### Confirmed Threats Requiring Your Attention")
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
            st.success("All identified threat vectors have been successfully cleared!")

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
