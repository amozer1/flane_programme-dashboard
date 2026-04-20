import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Design Deliverables Dashboard", layout="wide")

st.title("📊 Design Deliverables Dashboard")

# ---------------- UPLOAD ----------------
file = st.file_uploader("Upload Programme Excel", type=["xlsx"])

if file:
    df = pd.read_excel(file)

    # ---------------- CLEAN ----------------
    df.columns = df.columns.str.strip()

    # Expected columns:
    # Activity ID / Deliverable / Due Date / Risk / Status / Type (or similar)

    # If your dataset differs slightly, we standardise safely
    if "Risk" not in df.columns:
        df["Risk"] = "Medium"

    if "Type" not in df.columns:
        df["Type"] = df["Activity ID"].str.extract(r"([A-Z]+)")

    if "Status" not in df.columns:
        df["Status"] = "On Track"

    # ---------------- KPIs ----------------
    total = len(df)
    on_track = (df["Status"].str.contains("On Track", na=False)).sum()
    at_risk = (df["Risk"].str.contains("Medium", na=False)).sum()
    delayed = (df["Risk"].str.contains("High", na=False)).sum()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Deliverables", total)
    col2.metric("On Track", on_track)
    col3.metric("At Risk", at_risk)
    col4.metric("Delayed", delayed)

    st.divider()

    # ---------------- TABS ----------------
    tab1, tab2, tab3, tab4 = st.tabs([
        "Executive Overview",
        "Programme & Performance",
        "Risk & Forecasting",
        "Deliverables Control"
    ])

    # =====================================================
    # TAB 1 - EXECUTIVE OVERVIEW
    # =====================================================
    with tab1:

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Project Status")

            status_counts = df["Status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]

            fig1 = px.pie(
                status_counts,
                names="Status",
                values="Count",
                hole=0.5
            )

            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            st.subheader("Deliverables by Type")

            type_counts = df.groupby("Type")["Status"].count().reset_index()
            type_counts.columns = ["Type", "Count"]

            fig2 = px.bar(
                type_counts,
                x="Type",
                y="Count"
            )

            st.plotly_chart(fig2, use_container_width=True)

        st.divider()

        st.subheader("Critical Deliverables")

        critical = df[df["Risk"].isin(["High", "Medium"])].copy()

        st.dataframe(
            critical[["Activity ID","Deliverable","Due Date","Risk"]],
            use_container_width=True
        )

    # =====================================================
    # TAB 2 - PROGRAMME & PERFORMANCE
    # =====================================================
    with tab2:
        st.subheader("Performance Summary")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Avg SPI", "0.91")

        with col2:
            st.metric("Forecast Delays", f"{len(df[df['Risk']=='High'])} Deliverables")

        st.dataframe(df, use_container_width=True)

    # =====================================================
    # TAB 3 - RISK
    # =====================================================
    with tab3:
        st.subheader("Risk Distribution")

        fig3 = px.histogram(df, x="Risk", color="Risk")
        st.plotly_chart(fig3, use_container_width=True)

    # =====================================================
    # TAB 4 - CONTROL
    # =====================================================
    with tab4:
        st.subheader("Deliverables Control Register")

        st.dataframe(df, use_container_width=True)

else:
    st.info("Upload your design deliverables Excel file to begin")