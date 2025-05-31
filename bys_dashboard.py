import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime

# ------------------------ MAIN APP ------------------------ #
st.set_page_config(page_title="BYS Dashboard", layout="wide")
st.markdown("<style>body{background-color: #f4f4f4;}</style>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
        else:
            st.error("Invalid username or password")
else:
    username = st.session_state.username
    st.sidebar.title(f"👤 Welcome, {username}")
    log_action(username, "Accessed Dashboard")

    # ------------------------ DATA LOADING ------------------------ #
    file_path = "Master Data for App_updated.xlsx"
    df = pd.read_excel(file_path)

    date_cols = ["Batch Start Date", "Batch End Date", "Assessment Date"]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    tabs = ["📌 Active Batches Dashboard"]
    if username == "admin":
        tabs = ["📁 Project Dashboard", "📌 Active Batches Dashboard", "💰 SPOC Payout"]

    selected_tab = st.sidebar.radio("Select a tab", tabs)
    log_action(username, f"Opened tab: {selected_tab}")

    # ------------------------ TAB 1: PROJECT DASHBOARD ------------------------ #
    if selected_tab == "📁 Project Dashboard":
        st.title("📁 Project Dashboard")

        spoc_filter = st.selectbox("Select SPOC", ["All"] + sorted(df["SPOC"].dropna().unique().tolist()))
        project_filter = st.selectbox("Select Project", ["All"] + sorted(df["Project Name"].dropna().unique().tolist()))
        batch_type_filter = st.selectbox("Select Batch Type", ["All"] + sorted(df["Batch Type"].dropna().unique().tolist()))
        date_range = st.date_input("Select Date Range", [])

        filtered_df = df.copy()
        if spoc_filter != "All":
            filtered_df = filtered_df[filtered_df["SPOC"] == spoc_filter]
        if project_filter != "All":
            filtered_df = filtered_df[filtered_df["Project Name"] == project_filter]
        if batch_type_filter != "All":
            filtered_df = filtered_df[filtered_df["Batch Type"] == batch_type_filter]
        if len(date_range) == 2:
            start_date, end_date = date_range
            filtered_df = filtered_df[
                (filtered_df["Batch Start Date"] >= pd.to_datetime(start_date)) &
                (filtered_df["Batch End Date"] <= pd.to_datetime(end_date))
            ]

        st.metric("Total Students", int(filtered_df["Total Students"].sum()))
        st.metric("Trained Candidates", int(filtered_df["Trained Candidates"].sum()))
        st.metric("Dropouts", int(filtered_df["Dropout"].sum()))
        st.metric("Assessed", int(filtered_df["Assessed"].sum()))
        st.metric("Certified", int(filtered_df["Certified"].sum()))
        st.metric("Placed", int(filtered_df["Placed"].sum()))
        st.metric("Fail", int(filtered_df["Fail"].sum()))

        st.subheader("Training Centers")
        st.write(filtered_df["Training Center"].dropna().unique())

    # ------------------------ TAB 2: ACTIVE BATCHES ------------------------ #
    elif selected_tab == "📌 Active Batches Dashboard":
        st.title("📌 Active Batches Dashboard")

        active_df = df[df["Batch Status"] == "Active"]

        spoc_filter = st.selectbox("Select SPOC", ["All"] + sorted(active_df["SPOC"].dropna().unique().tolist()))
        project_filter = st.selectbox("Select Project", ["All"] + sorted(active_df["Project Name"].dropna().unique().tolist()))
        batch_type_filter = st.selectbox("Select Batch Type", ["All"] + sorted(active_df["Batch Type"].dropna().unique().tolist()))
        course_filter = st.selectbox("Select Course", ["All"] + sorted(active_df["Course"].dropna().unique().tolist()))
        date_range = st.date_input("Select Batch Start-End Date Range", [])

        filtered_df = active_df.copy()
        if spoc_filter != "All":
            filtered_df = filtered_df[filtered_df["SPOC"] == spoc_filter]
        if project_filter != "All":
            filtered_df = filtered_df[filtered_df["Project Name"] == project_filter]
        if batch_type_filter != "All":
            filtered_df = filtered_df[filtered_df["Batch Type"] == batch_type_filter]
        if course_filter != "All":
            filtered_df = filtered_df[filtered_df["Course"] == course_filter]
        if len(date_range) == 2:
            start_date, end_date = date_range
            filtered_df = filtered_df[
                (filtered_df["Batch Start Date"] >= pd.to_datetime(start_date)) &
                (filtered_df["Batch End Date"] <= pd.to_datetime(end_date))
            ]

        st.metric("Active Batches", len(filtered_df))

        st.subheader("SPOC-wise Active Batch Summary")
        summary_df = filtered_df.groupby("SPOC")[["Total Students", "Certified", "Placed"]].sum().reset_index()
        st.dataframe(summary_df)

        st.subheader("Project-wise Breakdown")
        st.dataframe(filtered_df.groupby("Project Name")[["Total Students", "Certified", "Placed"]].sum().reset_index())

    # ------------------------ TAB 3: SPOC PAYOUT ------------------------ #
    elif selected_tab == "💰 SPOC Payout":
        st.title("💰 SPOC Payout")

        payout_df = df.copy()
        payout_df["Payout Amount"] = payout_df["Certified"] * 4500

        spoc_options = ["All"] + sorted(payout_df["SPOC"].dropna().unique().tolist())
        selected_spoc = st.selectbox("Select SPOC", spoc_options)
        date_range = st.date_input("Select Batch Start-End Date Range", [])

        if selected_spoc != "All":
            payout_df = payout_df[payout_df["SPOC"] == selected_spoc]
        if len(date_range) == 2:
            start_date, end_date = date_range
            payout_df = payout_df[
                (payout_df["Batch Start Date"] >= pd.to_datetime(start_date)) &
                (payout_df["Batch End Date"] <= pd.to_datetime(end_date))
            ]

        payout_summary = payout_df.groupby("SPOC")[["Certified", "Payout Amount", "Payment Amount"]].sum().reset_index()
        payout_summary["Remaining Amount"] = payout_summary["Payout Amount"] - payout_summary["Payment Amount"]

        st.subheader("SPOC-wise Payout Summary")
        st.dataframe(payout_summary)

        st.metric("Total Certified", int(payout_summary["Certified"].sum()))
        st.metric("Total Payout Amount (₹)", int(payout_summary["Payout Amount"].sum()))
        st.metric("Total Payment Done (₹)", int(payout_summary["Payment Amount"].sum()))
        st.metric("Total Remaining Amount (₹)", int(payout_summary["Remaining Amount"].sum()))
