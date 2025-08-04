# bys_dashboard.py

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
    st.title("🔐 Login")
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
    st.sidebar.title(f"🕤 Welcome, {username}")
    log_action(username, "Accessed Dashboard")

    # ------------------------ DATA LOADING ------------------------ #
    df = None
    try:
        file_id = "10eQneyaEyzXa1qfCotYFAH5O76Cew0-q"
        gsheet_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        df = pd.read_csv(gsheet_url)
    except Exception:
        st.warning("Google Drive load failed. Please upload the Excel file.")
        uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])
        if uploaded_file:
            df = pd.read_excel(uploaded_file)
            st.success("Loaded data from uploaded file.")
        else:
            st.stop()

    # Clean and normalize column names
    df.columns = df.columns.str.strip().str.replace("'", "").str.replace('"', '').str.title()
    df.rename(columns={"Spoc": "SPOC"}, inplace=True)

    date_cols = ["Batch Start Date", "Batch End Date", "Assessment Date", "Payment Date"]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # ------------------------ DASHBOARDS ------------------------ #
    tabs = ["📌 Active Batches Dashboard"]
    if username == "admin":
        tabs = ["📁 Project Dashboard", "📌 Active Batches Dashboard", "💰 SPOC Payout"]

    selected_tab = st.sidebar.radio("Select a tab", tabs)
    log_action(username, f"Opened tab: {selected_tab}")

    if selected_tab == "💰 SPOC Payout":
        st.title("💰 SPOC Payout")
        payout_df = df.copy()
        payout_df.columns = payout_df.columns.str.strip().str.replace("'", "").str.replace('"', '').str.title()

        if "Payment Amount" in payout_df.columns and "Payment Date" in payout_df.columns:
            payout_df["Payment Date"] = pd.to_datetime(payout_df["Payment Date"], errors="coerce")
            payout_df["Payout Amount"] = payout_df["Certified"] * 4500

            missing_payment_dates = payout_df[
                (payout_df["Payment Amount"] > 0) & (payout_df["Payment Date"].isna())
            ]
            if not missing_payment_dates.empty:
                st.warning("⚠️ Some rows have 'Payment Amount' > 0 but missing 'Payment Date'.")
                st.dataframe(missing_payment_dates)

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

            payout_summary = payout_df.groupby(["SPOC", "Project Name"])[["Certified", "Payout Amount", "Payment Amount"]].sum().reset_index()
            payout_summary["Balance"] = payout_summary["Payout Amount"] - payout_summary["Payment Amount"]

            st.subheader("SPOC & Project-wise Payout Summary")
            st.dataframe(payout_summary)

            st.subheader("💸 Detailed Payment History by SPOC")
            spoc_payment_history = payout_df[["SPOC", "Project Name", "Payment Amount", "Payment Date"]].dropna()
            st.dataframe(spoc_payment_history.sort_values(by=["SPOC", "Payment Date"]))
            st.download_button("⬇️ Download Payment History", spoc_payment_history.to_csv(index=False).encode(), file_name="spoc_payment_history.csv", mime="text/csv")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Certified", int(payout_summary["Certified"].sum()))
            with col2:
                st.metric("Total Payout Amount (₹)", int(payout_summary["Payout Amount"].sum()))
            with col3:
                st.metric("Total Paid (₹)", int(payout_summary["Payment Amount"].sum()))
            with col4:
                st.metric("Total Balance (₹)", int(payout_summary["Balance"].sum()))

        else:
            st.error("❗ Required column(s) 'Payment Amount' or 'Payment Date' not found.")
            st.write("Available columns:", payout_df.columns.tolist())
            st.stop()
