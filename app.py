import streamlit as st
import pandas as pd
import pydeck as pdk
from datetime import datetime

# --- 1. SYSTEM CORE & UI ENGINE ---
st.set_page_config(page_title="USSD Security Framework", layout="wide", initial_sidebar_state="expanded")

# Critical CSS for Visual Fidelity
st.markdown("""
    <style>
    /* USSD Phone UI Simulation */
    .ussd-box {
        background-color: #000000;
        color: #FFFFFF;
        padding: 40px;
        border-radius: 30px;
        border: 4px solid #333333;
        max-width: 420px;
        margin: auto;
        font-family: 'Courier New', Courier, monospace;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.5);
    }
    /* Institutional Maroon Branding */
    .stButton>button {
        background-color: #800000;
        color: white;
        border-radius: 5px;
        width: 100%;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #800000;
    }
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [aria-selected="true"] {
        background-color: #800000 !important;
        color: white !important;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GLOBAL STATE MANAGEMENT ---
# These act as the system's "RAM" for the demo
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=["Incident", "Location", "Weight", "Time"])
if 'audit_log' not in st.session_state:
    st.session_state.audit_log = pd.DataFrame(columns=["Timestamp", "User", "Action", "Role"])
if 'auth_status' not in st.session_state:
    st.session_state.auth_status = False

# Geographic Grounding for Logic-Based Landmarks
LANDMARKS = {
    "Market Area": [6.5244, 3.3792],
    "School Zone": [6.4550, 3.3841],
    "Residential Area": [6.5000, 3.3670]
}

# --- 3. SECURITY GATEWAY (Authentication) ---
st.sidebar.title("🛡️ Secure Access Terminal")

if not st.session_state.auth_status:
    with st.sidebar.form("auth_gate"):
        user_id = st.text_input("Personnel/User ID", placeholder="e.g., Beeai Morrison")
        access_role = st.selectbox("Assign Portal", ["Common Citizen", "Security Operator", "Policymaker"])
        secret_key = st.text_input("Access Key", type="password")
        
        if st.form_submit_button("Verify Identity"):
            if secret_key == "thesis2026": # Protocol key for demo
                st.session_state.auth_status = True
                st.session_state.current_user = user_id
                st.session_state.current_role = access_role
                
                # Log entry for Policymaker Oversight
                log_entry = {
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "User": user_id,
                    "Action": "System Access Granted",
                    "Role": access_role
                }
                st.session_state.audit_log = pd.concat([st.session_state.audit_log, pd.DataFrame([log_entry])], ignore_index=True)
                st.rerun()
            else:
                st.sidebar.error("Authentication Failed: Invalid Key")
else:
    st.sidebar.markdown(f"**Current Session:** {st.session_state.current_user}")
    st.sidebar.markdown(f"**Clearance:** {st.session_state.current_role}")
    if st.sidebar.button("Terminate Session"):
        st.session_state.auth_status = False
        st.rerun()

# --- 4. FUNCTIONAL PORTALS ---
if not st.session_state.auth_status:
    st.title("🛰️ Hybrid USSD Security Mapping Framework")
    st.subheader("M.Sc. Dissertation System Simulation")
    st.info("System Locked. Please authenticate via the Secure Access Terminal to proceed.")
    st.image("https://img.icons8.com/color/480/shield.png", width=150)

else:
    # --- PORTAL I: THE SENSING LAYER (Common Citizen) ---
    if st.session_state.current_role == "Common Citizen":
        st.markdown('<div class="ussd-box">', unsafe_allow_html=True)
        st.markdown("## USSD Security Simulation")
        st.markdown("### Dialing *123# ...")
        st.markdown("---")
        st.markdown("**Select Incident Type:**")
        st.markdown("1. Robbery")
        st.markdown("2. Kidnapping")
        st.markdown("3. Suspicious Activity")
        
        with st.form("ussd_interface", clear_on_submit=True):
            user_choice = st.text_input("Enter option", key="input_field")
            location_ref = st.selectbox("Confirm Landmark Location", list(LANDMARKS.keys()))
            
            if st.form_submit_button("SEND SIGNAL"):
                mapping = {"1": "Robbery", "2": "Kidnapping", "3": "Suspicious Activity"}
                intensity = {"Robbery": 10, "Kidnapping": 15, "Suspicious Activity": 5}
                
                if user_choice in mapping:
                    report = {
                        "Incident": mapping[user_choice],
                        "Location": location_ref,
                        "Weight": intensity[mapping[user_choice]],
                        "Time": datetime.now().strftime("%H:%M:%S")
                    }
                    st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([report])], ignore_index=True)
                    st.success("✔ Emergency Signal Received at Headquarters")
                else:
                    st.error("Invalid USSD Input")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- PORTAL II: THE RESPONSE LAYER (Security Operator) ---
    elif st.session_state.current_role == "Security Operator":
        st.title(f"👮 Operator Dashboard: {st.session_state.current_user}")
        st.write("Real-time Tactical Situational Awareness")
        
        if not st.session_state.db.empty:
            # Aggregate Data for Map
            map_data = st.session_state.db.groupby("Location").agg(Total_Int=('Weight', 'sum')).reset_index()
            map_data['lat'] = map_data['Location'].map(lambda x: LANDMARKS[x][0])
            map_data['lon'] = map_data['Location'].map(lambda x: LANDMARKS[x][1])
            
            # 3D Intensity Visualization
            st.pydeck_chart(pdk.Deck(
                map_style='mapbox://styles/mapbox/dark-v10',
                initial_view_state=pdk.ViewState(latitude=6.5, longitude=3.37, zoom=10, pitch=45),
                layers=[pdk.Layer(
                    'ColumnLayer', data=map_data, get_position='[lon, lat]',
                    get_elevation='Total_Int * 120', radius=400,
                    get_fill_color='[128, 0, 0, 180]', # Institutional Maroon
                    pickable=True, auto_highlight=True
                )]
            ))
            
            if st.button("Query Detailed Incident Logs"):
                # AUDIT TRIGGER: Log who is looking at the details
                audit = {"Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                         "User": st.session_state.current_user, "Action": "Accessed Incident DB", "Role": "Operator"}
                st.session_state.audit_log = pd.concat([st.session_state.audit_log, pd.DataFrame([audit])], ignore_index=True)
                st.dataframe(st.session_state.db.iloc[::-1], use_container_width=True)
        else:
            st.info("System Ready. No active threat signals detected in the sectors.")

    # --- PORTAL III: THE GOVERNANCE LAYER (Policymaker) ---
    elif st.session_state.current_role == "Policymaker":
        st.title("🏛️ Strategic Intelligence & Accountability Portal")
        
        metric_col1, metric_col2 = st.columns(2)
        metric_col1.metric("National Threat Records", len(st.session_state.db))
        metric_col2.metric("Administrative Audit Logs", len(st.session_state.audit_log))
        
        st.divider()
        st.subheader("Personnel Activity & Accountability Log")
        st.write("This table proves system integrity by tracking every action taken by personnel.")
        st.table(st.session_state.audit_log.iloc[::-1]) # Latest actions at the top

