import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime

# ------------------------ AUTHENTICATION ------------------------ #
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(username, password):
    if "users" not in st.secrets:
        st.error("User credentials not configured in `.streamlit/secrets.toml`.")
        st.stop()
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
    st.title("\U0001F512 Login")
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
    st.sidebar.title(f"\U0001F464 Welcome, {username}")
    log_action(username, "Accessed Dashboard")

    # ------------------------ DATA LOADING ------------------------ #
    df = None
    try:
        file_id = "10eQneyaEyzXa1qfCotYFAH5O76Cew0-q"
        gsheet_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        df = pd.read_csv(gsheet_url)
        df.columns = df.columns.str.strip().str.replace("'", "").str.replace('"', '').str.title()
        df.rename(columns={"Spoc": "SPOC"}, inplace=True)
    except Exception:
        st.warning("Google Drive load failed. Please upload the Excel file.")
        uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])
        if uploaded_file:
            df = pd.read_excel(uploaded_file)
            df.columns = df.columns.str.strip().str.replace("'", "").str.replace('"', '').str.title()
            df.rename(columns={"Spoc": "SPOC"}, inplace=True)
            st.success("Loaded data from uploaded file.")
        else:
            st.stop()

    date_cols = ["Batch Start Date", "Batch End Date", "Assessment Date", "Payment Date"]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    tabs = ["\ud83d\udccc Active Batches Dashboard"]
    if username == "admin":
        tabs = ["\ud83d\udcc1 Project Dashboard", "\ud83d\udccc Active Batches Dashboard", "\ud83d\udcb0 SPOC Payout"]

    selected_tab = st.sidebar.radio("Select a tab", tabs)
    log_action(username, f"Opened tab: {selected_tab}")

    if selected_tab == "\ud83d\udcc1 Project Dashboard":
        st.title("\ud83d\udcc1 Project Dashboard")
        project_df = df.copy()

        col1, col2, col3 = st.columns(3)
        with col1:
            spoc_filter = st.selectbox("Select SPOC", ["All"] + sorted(project_df["SPOC"].dropna().unique().tolist()))
        with col2:
            project_filter = st.selectbox("Select Project", ["All"] + sorted(project_df["Project Name"].dropna().unique().tolist()))
        with col3:
            batch_type_filter = st.selectbox("Select Batch Type", ["All"] + sorted(project_df["Batch Type"].dropna().unique().tolist()))

        date_range = st.date_input("Select Date Range", [])

        if spoc_filter != "All":
            project_df = project_df[project_df["SPOC"] == spoc_filter]
        if project_filter != "All":
            project_df = project_df[project_df["Project Name"] == project_filter]
        if batch_type_filter != "All":
            project_df = project_df[project_df["Batch Type"] == batch_type_filter]
        if len(date_range) == 2:
            start_date, end_date = date_range
            project_df = project_df[
                (project_df["Batch Start Date"] >= pd.to_datetime(start_date)) &
                (project_df["Batch End Date"] <= pd.to_datetime(end_date))
            ]

        col_metrics1, col_metrics2 = st.columns(2)
        with col_metrics1:
            st.metric("Assessed", int(project_df["Assessed"].sum()))
            st.metric("Placed", int(project_df["Placed"].sum()))
        with col_metrics2:
            st.metric("Trained Candidates", int(project_df["Trained Candidates"].sum()))
            st.metric("Certified", int(project_df["Certified"].sum()))

        st.subheader("Training Centers")
        st.write(project_df["Training Center"].dropna().unique())

    elif selected_tab == "\ud83d\udcb0 SPOC Payout":
        st.title("\ud83d\udcb0 SPOC Payout")
        payout_df = df.copy()
        payout_df["Payout Amount"] = payout_df["Certified"] * 4500

        col1, col2, col3 = st.columns(3)
        with col1:
            selected_spoc = st.selectbox("Select SPOC", ["All"] + sorted(payout_df["SPOC"].dropna().unique().tolist()))
        with col2:
            selected_project = st.selectbox("Select Project", ["All"] + sorted(payout_df["Project Name"].dropna().unique().tolist()))
        with col3:
            selected_batch_type = st.selectbox("Select Batch Type", ["All"] + sorted(payout_df["Batch Type"].dropna().unique().tolist()))

        date_range = st.date_input("Select Batch Start-End Date Range", [])

        if selected_spoc != "All":
            payout_df = payout_df[payout_df["SPOC"] == selected_spoc]
        if selected_project != "All":
            payout_df = payout_df[payout_df["Project Name"] == selected_project]
        if selected_batch_type != "All":
            payout_df = payout_df[payout_df["Batch Type"] == selected_batch_type]
        if len(date_range) == 2:
            start_date, end_date = date_range
            payout_df = payout_df[
                (payout_df["Batch Start Date"] >= pd.to_datetime(start_date)) &
                (payout_df["Batch End Date"] <= pd.to_datetime(end_date))
            ]

        st.subheader("SPOC-wise Payout Summary")
        spoc_summary = payout_df.groupby("SPOC")[["Certified", "Payout Amount", "Payment Amount"]].sum().reset_index()
        spoc_summary["Remaining Amount"] = spoc_summary["Payout Amount"] - spoc_summary["Payment Amount"]
        st.dataframe(spoc_summary)

        st.subheader("Project-wise Payout Summary")
        project_summary = payout_df.groupby("Project Name")[["Certified", "Payout Amount", "Payment Amount"]].sum().reset_index()
        project_summary["Remaining Amount"] = project_summary["Payout Amount"] - project_summary["Payment Amount"]
        st.dataframe(project_summary)
