import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime

# ------------------------ AUTHENTICATION ------------------------ #
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(username, password):
    users = st.secrets["users"]
    return username in users and hash_password(password) == hash_password(users[username])

def log_action(user, action):
    with open("user_activity_log.txt", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} | {user} | {action}\n")

# ------------------------ MAIN APP ------------------------ #
st.set_page_config(page_title="BYS Dashboard", layout="wide")
st.markdown("<style>body{background-color: #f4f4f4;}</style>", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔒 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if check_password(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            log_action(username, "Logged in")
            st.rerun()
        else:
            st.error("Invalid username or password")
else:
    username = st.session_state.username
    st.sidebar.title(f"👤 Welcome, {username}")
    log_action(username, "Accessed Dashboard")

    st.subheader("📁 Data Source")
    uploaded_file = st.file_uploader("Upload Excel file (Desktop Users)", type=["xlsx"])
    df = None

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.success("Excel file uploaded successfully.")
    else:
        st.info("No file uploaded. Attempting to read from Google Drive for mobile users...")
        try:
            google_drive_file_id = "10eQneyaEyzXa1qfCotYFAH5O76Cew0-q/view?usp=sharing"  # Replace with your actual ID
            gsheet_url = f"https://drive.google.com/uc?export=download&id={google_drive_file_id}"
            df = pd.read_csv(gsheet_url)
            st.success("Loaded data from Google Drive.")
        except Exception as e:
            st.warning("Unable to load data from Google Drive. Please upload the file manually.")
            st.stop()

    if df is not None:
        date_cols = ["Batch Start Date", "Batch End Date", "Assessment Date"]
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

        st.success("✅ Data loaded and ready to use. (Continue building dashboards below)")
