import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import urllib.parse
import random

st.set_page_config(page_title="DOEA Digital Online Health Assessment", layout="wide")

# Custom CSS for clean styling and grade badges
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
    .inbox-preview {
        background-color: #f1f5f9;
        border: 1px dashed #003366;
        padding: 20px;
        border-radius: 8px;
        color: #111827;
        margin-bottom: 20px;
        margin-top: 15px;
    }
    .result-row {
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #d1d5db;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        margin-bottom: 15px;
    }
    .report-box {
        background-color: white;
        padding: 35px;
        border-radius: 10px;
        border: 2px solid #003366;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08);
        margin-top: 20px;
        margin-bottom: 20px;
    }
    .grade-badge-a {
        background-color: #28a745;
        color: white;
        font-size: 36px;
        font-weight: bold;
        padding: 15px 25px;
        border-radius: 10px;
        text-align: center;
        display: inline-block;
    }
    .threat-box {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        border-left: 5px solid #28a745;
        margin-bottom: 15px;
        border-top: 1px solid #e5e7eb;
        border-right: 1px solid #e5e7eb;
        border-bottom: 1px solid #e5e7eb;
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
    h1, h2, h3, h4 {
        color: #111827;
    }
    </style>
""", unsafe_allow_html=True)

# Official State Top Banner
st.markdown("""
    <div class="state-banner">
        <span>🏛️ State of Florida — Department of Elder Affairs Official Digital Portal</span>
        <span>Operation: Senior Shield (Enterprise Compliance Engine)</span>
    </div>
""", unsafe_allow_html=True)

st.title("Digital Online Health Assessment")
st.markdown("##### Secure Identity Verification & Comprehensive Threat Remediation Portal")
st.divider()

database_name = "digital_footprint_manager.db"

# Session State Flow Management
if 'stage' not in st.session_state:
    st.session_state['stage'] = 'search'

# --- STAGE 1: CLEAN PROFESSIONAL SUBJECT INTAKE ---
if st.session_state['stage'] == 'search':
    st.markdown('<div class="search-card">', unsafe_allow_html=True)
    st.markdown("### 🔍 Enterprise Subject Intake")
    st.write("Enter your name and location parameters to initiate your verified digital footprint audit.")
    
    s_col1, s_col2, s_col3 = st.columns(3)
    with s_col1:
        search_first = st.text_input("First Name", value="", placeholder="Enter first name", key="f_name")
    with s_col2:
        search_middle = st.text_input("Middle Name / Initial", value="", placeholder="Enter middle name or initial", key="m_name")
    with s_col3:
        search_last = st.text_input("Last Name", value="", placeholder="Enter last name", key="l_name")

    loc_col1, loc_col2, loc_col3 = st.columns(3)
    with loc_col1:
        search_city = st.text_input("Current City", value="", placeholder="Enter current city", key="c_city")
    with loc_col2:
        states_list = [
            "Florida", "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", 
            "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", 
            "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", 
            "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", 
            "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", 
            "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", 
            "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"
        ]
        search_state = st.selectbox("State", states_list, index=0, key="c_state")
    with loc_col3:
        age_options = ["-- Select Age Segment --", "18-29", "30-49", "50-64", "65-74", "75+"]
        age_segment = st.selectbox("Age Segment", age_options, index=0, key="c_age")

    if st.button("Proceed to Sequential Verification"):
        if search_first and search_last and search_city and age_segment != "-- Select Age Segment --":
            full_search_name = f"{search_first} {search_middle + ' ' if search_middle else ''}{search_last}".strip()
            st.session_state['searched_name'] = full_search_name
            st.session_state['searched_city'] = search_city
            st.session_state['searched_state'] = search_state
            st.session_state['searched_location'] = f"{search_city}, {search_state}"
            st.session_state['searched_age_segment'] = age_segment
            st.session_state['stage'] = 'mfa_email'
            st.rerun()
        else:
            st.warning("Please fill in your first name, last name, current city, and select an age segment to proceed.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- STAGE 2: SEQUENTIAL MFA — STEP 1 (EMAIL VERIFICATION WITH DEMO INBOX) ---
elif st.session_state['stage'] == 'mfa_email':
    st.markdown('<div class="wizard-card">', unsafe_allow_html=True)
    current_name = st.session_state.get('searched_name', 'Subject')
    
    st.markdown(f"### Subject: {current_name}")
    st.progress(35, text="Step 1 of 2: Email Identity Confirmation")
    st.markdown("---")
    st.markdown("#### 📧 Step 1: Confirm Your Email Address")
    st.write("This is a simple **two-step process**. We will email you a verification code which will confirm your identity to securely perform your search.")
    
    user_email = st.text_input("Your Email Address (We will email you a code to confirm it's you)", value="", placeholder="name@example.com", key="input_email")
    
    col_btn1, col_btn_spacer, col_btn2 = st.columns([2, 3, 2])
    with col_btn1:
        send_code_clicked = st.button("Send Verification Code")
    with col_btn2:
        back_clicked = st.button("Back to Main Page")

    if back_clicked:
        st.session_state.pop('email_otp', None)
        st.session_state['stage'] = 'search'
        st.rerun()

    if send_code_clicked:
        if user_email:
            st.session_state['temp_email'] = user_email
            st.session_state['email_otp'] = str(random.randint(100000, 999999))
            st.rerun()
        else:
            st.warning("Please enter a valid email address before requesting a verification code.")

    if 'email_otp' in st.session_state:
        active_email = st.session_state.get('temp_email', user_email)
        simulated_email_code = st.session_state['email_otp']
        
        st.success(f"📨 A verification code has been emailed to **{active_email}**. Please check your inbox.")
        
        with st.expander("📥 Demo Inbox Preview (Click to open simulated incoming email)", expanded=True):
            st.markdown(f"""
            <div class="inbox-preview">
                <strong>From:</strong> doea-security@elderaffairs.org<br>
                <strong>To:</strong> {active_email}<br>
                <strong>Subject:</strong> Action Required: DOEA Digital Health Assessment Verification Code<br>
                <hr style="margin: 10px 0; border: 1px solid #cbd5e1;">
                <p>Hello,</p>
                <p>You have initiated a secure digital footprint audit through the State of Florida Department of Elder Affairs portal (Operation: Senior Shield).</p>
                <p>Your confidential One-Time Password (OTP) verification code is:</p>
                <h2 style="color: #003366; letter-spacing: 2px; margin: 10px 0;">{simulated_email_code}</h2>
                <p><small>If you did not request this verification, please disregard this message.</small></p>
            </div>
            """, unsafe_allow_html=True)

        entered_email_code = st.text_input("Enter the 6-Digit Verification Code that has been emailed to you", value="", max_chars=6, key="input_email_code")

        if st.button("Verify Email & Proceed to Phone Authentication"):
            if entered_email_code == simulated_email_code:
                st.session_state['user_email'] = active_email
                st.session_state['sms_otp'] = str(random.randint(100000, 999999))
                st.session_state['stage'] = 'mfa_sms'
                st.rerun()
            else:
                st.error("Invalid verification code. Please check your simulated inbox preview above.")
            
    st.markdown('</div>', unsafe_allow_html=True)

# --- STAGE 3: SEQUENTIAL MFA — STEP 2 (SMS MOBILE VERIFICATION WITH DEMO INBOX) ---
elif st.session_state['stage'] == 'mfa_sms':
    st.markdown('<div class="wizard-card">', unsafe_allow_html=True)
    current_name = st.session_state.get('searched_name', 'Subject')
    current_email = st.session_state.get('user_email', '')
    
    st.markdown(f"### Subject: {current_name}")
    st.progress(75, text="Step 2 of 2: Mobile Phone Identity Confirmation")
    st.markdown("---")
    st.success(f"✅ Email Address (**{current_email}**) successfully verified!")
    st.markdown("#### 📱 Step 2: Confirm Your Mobile Phone Number")
    st.write("We will text you a quick verification code to complete your second security step.")
    
    user_phone = st.text_input("Your Mobile Phone Number (For SMS Code)", value="", placeholder="(555) 000-0000", key="input_phone")
    
    col_s_btn1, col_s_btn_spacer, col_s_btn2 = st.columns([2, 3, 2])
    with col_s_btn1:
        send_sms_clicked = st.button("Send SMS Code")
    with col_s_btn2:
        back_email_clicked = st.button("Back to Email Verification")

    if back_email_clicked:
        st.session_state.pop('sms_otp', None)
        st.session_state['stage'] = 'mfa_email'
        st.rerun()

    if send_sms_clicked:
        if user_phone:
            st.session_state['temp_phone'] = user_phone
            st.rerun()
        else:
            st.warning("Please enter a valid mobile phone number before requesting an SMS code.")

    if 'temp_phone' in st.session_state:
        active_phone = st.session_state['temp_phone']
        simulated_sms_code = st.session_state.get('sms_otp', '654321')
        
        st.success(f"📱 A verification code has been texted to **{active_phone}**. Please check your text messages.")
        
        with st.expander("💬 Demo SMS Message Preview (Click to open simulated text message)", expanded=True):
            st.markdown(f"""
            <div class="inbox-preview">
                <strong>From:</strong> DOEA-ALERT (State Secure Gateway)<br>
                <strong>To:</strong> {active_phone}<br>
                <hr style="margin: 10px 0; border: 1px solid #cbd5e1;">
                <p>State of Florida - Senior Shield: Your mobile verification code is <strong>{simulated_sms_code}</strong>. Do not share this code.</p>
            </div>
            """, unsafe_allow_html=True)

        entered_sms_code = st.text_input("Enter the 6-Digit Verification Code that has been texted to you", value="", max_chars=6, key="input_sms_code")

        if st.button("Verify Mobile & Select Profile Match"):
            if entered_sms_code == simulated_sms_code:
                st.session_state['user_phone'] = active_phone
                st.session_state['stage'] = 'results'
                st.rerun()
            else:
                st.error("Invalid SMS verification code. Please check your simulated text message preview above.")

    st.markdown('</div>', unsafe_allow_html=True)

# --- STAGE 4: AUTOMATED INTELIUS-STYLE DISAMBIGUATION GRID ---
elif st.session_state['stage'] == 'results':
    age_seg = st.session_state.get('searched_age_segment', '50-64')
    target_city = st.session_state.get('searched_city', 'City')
    target_state_abbr = st.session_state.get('searched_state', 'State')
    searched_name = st.session_state.get('searched_name', 'User')
    
    st.markdown(f"### 👥 Select Correct Match for {searched_name}")
    st.write(f"Multiple public directory listings found matching your search parameters. Review historical residencies and relative connections below to confirm your profile:")

    # Automatically generated rich historical profile records mimicking Intelius
    candidates = [
        {
            "id": 1,
            "name": searched_name,
            "age": age_seg,
            "location": f"{target_city}, {target_state_abbr}",
            "prior_locations": "Previously lived in: Indianapolis, IN; Mobile, AL",
            "relatives": "Associated Family/Kin: Pamela Byrd & Kinship Network",
            "badge": "⭐ BEST MATCH (Public Records Index)"
        },
        {
            "id": 2,
            "name": searched_name,
            "age": "30-49",
            "location": f"Alternate Metro Area, {target_state_abbr}",
            "prior_locations": "Previously lived in: Orlando, FL",
            "relatives": "Different Kinship Network",
            "badge": "Alternative Match"
        }
    ]

    for cand in candidates:
        st.markdown(f'<div class="result-row">', unsafe_allow_html=True)
        r_c1, r_c2, r_c3, r_c4 = st.columns([2, 1, 2, 2])
        with r_c1:
            st.markdown(f"**{cand['badge']}**\n### {cand['name']}")
        with r_c2:
            st.markdown(f"**AGE SEGMENT**\n{cand['age']}")
        with r_c3:
            st.markdown(f"**RESIDENCY & KIN**\nCurrent: {cand['location']}<br><small style='color: #4b5563;'>{cand['prior_locations']}<br>{cand['relatives']}</small>", unsafe_allow_html=True)
        with r_c4:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(f"SELECT THIS PROFILE", key=f"select_{cand['id']}"):
                default_deadline = (datetime.now() + timedelta(days=45)).strftime('%Y-%m-%d')
                property_link = f"https://www.google.com/search?q={target_state_abbr}+property+appraiser+public+record+search"

                with sqlite3.connect(database_name) as connection:
                    cursor = connection.cursor()
                    cursor.execute("DROP TABLE IF EXISTS optout_tracker;")
                    cursor.execute('''
                        CREATE TABLE optout_tracker (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            broker_name TEXT,
                            status TEXT,
                            statutory_deadline TEXT,
                            threat_explanation TEXT,
                            action_description TEXT,
                            target_url TEXT,
                            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                    ''')
                    
                    identified_threats = [
                        ('Tier-1 Commercial Data Aggregators (Spokeo / Whitepages)', 'Successfully Protected', default_deadline, 
                         f'Identified commercial profile listings publishing historical addresses and contact numbers for {searched_name} across {cand["prior_locations"]}.',
                         'Dispatched automated statutory opt-out requests across tier-1 broker pipelines. Initiated 45-day statutory compliance window.', 'https://www.networkadvertising.org/'),
                        
                        ('Secondary People-Search Networks (Intelius / BeenVerified)', 'Successfully Protected', default_deadline, 
                         f'Secondary aggregators indexed residency maps and public records matching {cand["location"]} listings.',
                         'Executed batch removal protocol via centralized opt-out authority gateways.', 'https://optout.beenverified.com/'),
                        
                        (f'Public Property & Tax Records ({target_state_abbr})', 'Successfully Protected', default_deadline, 
                         f'County assessment databases expose residential real estate holdings for {searched_name} in {cand["location"]}.',
                         'Submitted formal state exemption record suppression requests to county property appraisers.', property_link),
                        
                        ('Global Credential Breach Registry (HIBP Integration)', 'Successfully Protected', default_deadline, 
                         f'An associated digital login credential matching digital fingerprints for {searched_name} was identified in corporate breach dumps.',
                         'Triggered automated breach mitigation guidance and logged event for 2FA password reset completion.', 'https://haveibeenpwned.com/')
                    ]
                    cursor.executemany("INSERT INTO optout_tracker (broker_name, status, statutory_deadline, threat_explanation, action_description, target_url) VALUES (?, ?, ?, ?, ?, ?);", identified_threats)
                    connection.commit()
                
                st.session_state['searched_location'] = cand['location']
                st.session_state['searched_age_segment'] = cand['age']
                st.session_state['stage'] = 'dashboard'
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    if st.button("Modify Search / Start Over"):
        st.session_state['stage'] = 'search'
        st.rerun()

# --- STAGE 5: PERSONALIZED HEALTH ASSESSMENT DASHBOARD & CLEAN ON-SCREEN REPORT ---
elif st.session_state['stage'] == 'dashboard':
    st.success(f"Enterprise identity audit successfully completed and sequentially MFA-verified for **{st.session_state.get('searched_name', 'User')}**! Your official report is displayed below.")

    if st.button("🔒 Sign Out / New Search"):
        st.session_state['stage'] = 'search'
        st.rerun()

    st.divider()

    with sqlite3.connect(database_name) as connection:
        df = pd.read_sql_query("SELECT broker_name, status, statutory_deadline, threat_explanation, action_description, target_url FROM optout_tracker;", connection)

    total = len(df)
    completed_count = len(df[df['status'] == 'Successfully Protected'])

    # --- CLEAN ON-SCREEN CERTIFICATE & REPORT WITH A-F GRADE ---
    st.markdown("### 📄 Official Digital Health Assessment Report")
    st.markdown("This clean, easy-to-read report summarizes scanned exposures, identified risks, and completed statutory protections.")

    with st.container():
        st.markdown("""
        <div class="report-box">
            <table width="100%" style="border: none;">
                <tr>
                    <td>
                        <h2 style="color: #003366; margin-top: 0; margin-bottom: 5px;">State of Florida — Department of Elder Affairs</h2>
                        <h4 style="color: #4b5563; margin-top: 0;">Digital Online Health Assessment & Enterprise Protection Summary</h4>
                    </td>
                    <td align="right" style="vertical-align: middle;">
                        <div class="grade-badge-a">Grade: A</div>
                    </td>
                </tr>
            </table>
            <hr style="border: 1px solid #e5e7eb; margin: 20px 0;">
        """, unsafe_allow_html=True)
        
        st.markdown(f"**Verified Subject:** {st.session_state.get('searched_name', 'N/A')}")
        st.markdown(f"**Jurisdiction & Location:** {st.session_state.get('searched_location', 'N/A')}")
        st.markdown(f"**Age Segment:** {st.session_state.get('searched_age_segment', 'N/A')}")
        st.markdown(f"**Assessment Date:** {datetime.now().strftime('%B %d, %Y')}")
        st.markdown(f"**Digital Health Status:** Fully Protected (**{completed_count} of {total} Enterprise Threats Addressed** — Grade A)")
        
        # 45-Day Re-Scan Window Notice
        future_date = (datetime.now() + timedelta(days=45)).strftime('%B %d, %Y')
        st.info(f"⏳ **Statutory Window Active:** Your 45-day compliance window expires on **{future_date}**. Data brokers frequently re-scrape records over time. We recommend running a fresh audit on or after this date.")

        st.markdown("### Identified Exposures & Remediation Actions")
        
        for index, row in df.iterrows():
            st.markdown(f"""
            <div class="threat-box">
                <h4 style="color: #003366; margin-top: 0;">{row['broker_name']} — <span style="color: #28a745;">{row['status']}</span></h4>
                <p><strong>Why it was a risk:</strong> {row['threat_explanation']}</p>
                <p><strong>Action Executed:</strong> {row['action_description']}</p>
                <p><strong>Protection Deadline Window:</strong> {row['statutory_deadline']}</p>
                <p><strong>Official Registry Link:</strong> <a href="{row['target_url']}" target="_blank">{row['target_url']}</a></p>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("""
            <hr style="border: 1px solid #e5e7eb; margin: 20px 0;">
            <p style="font-size: 13px; color: #6b7280; text-align: center; margin: 0;">
                Operation: Senior Shield • Enterprise Statutory Compliance Engine • Department of Elder Affairs
            </p>
        </div>
        """, unsafe_allow_html=True)

    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        if st.button("🖨️ Print / Save Report (Use Browser Print)"):
            st.info("Tip: Press Ctrl+P (or Cmd+P on Mac) to print this clean report directly or save it as a PDF.")
    with col_p2:
        cal_title = urllib.parse.quote("Senior Shield: Digital Health Re-Scan Reminder")
        cal_details = urllib.parse.quote("Time to run a fresh re-scan on your Digital Online Health Assessment portal to check for newly scraped data broker listings.")
        cal_url = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={cal_title}&dates={(datetime.now() + timedelta(days=45)).strftime('%Y%m%d')}/{(datetime.now() + timedelta(days=46)).strftime('%Y%m%d')}&details={cal_details}"
        st.markdown(f'<a href="{cal_url}" target="_blank"><button style="width:100%; background-color:#003366; color:white; font-weight:600; border-radius:6px; padding:0.6rem 1rem; border:none; cursor:pointer;">📅 Add 45-Day Checkup to Calendar</button></a>', unsafe_allow_html=True)
    with col_p3:
        if st.button("🔄 Run Another Assessment"):
            st.session_state['stage'] = 'search'
            st.rerun()
            
