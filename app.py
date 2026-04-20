import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ---------------- PAGE SETUP ----------------
st.set_page_config(page_title="Design Deliverables Dashboard", layout="wide")

# ---------------- HEADER ----------------
st.markdown("""
# 📊 Design Deliverables Dashboard
""")

st.markdown("---")

# ---------------- LOAD DATA ----------------
file = st.file_uploader("Upload Deliverables Excel File", type=["xlsx"])

if file:

    df = pd.read_excel(file)

    # ---------------- CLEAN / SIMULATE IF NEEDED ----------------
    if "Status" not in df.columns:
        np.random.seed(42)
        df["Status"] = np.random.choice(
            ["On Track", "At Risk", "Delayed"],
            size=len(df),
            p=[0.6, 0.25, 0.15]
        )

    if "Type" not in df.columns:
        df["Type"] = np.random.choice(["Clause 31", "Clause 32", "Changes"], size=len(df))

    # ---------------- KPI CALCULATION ----------------
    total = len(df)
    on_track = (df["Status"] == "On Track").sum()
    at_risk = (df["Status"] == "At Risk").sum()
    delayed = (df["Status"] == "Delayed").sum()

    spi = round(on_track / total, 2)

    # ---------------- KPI ROW ----------------
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Deliverables", total)
    col2.metric("On Track", on_track)
    col3.metric("At Risk", at_risk)
    col4.metric("Delayed", delayed)

    st.markdown("---")

    # ---------------- TOP CHARTS ----------------
    col1, col2 = st.columns([1, 1])

    with col1:

        st.subheader("Project Status")

        fig1 = px.pie(
            df,
            names="Status",
            hole=0.5,
            color="Status",
            color_discrete_map={
                "On Track": "#2ecc71",
                "At Risk": "#f1c40f",
                "Delayed": "#e74c3c"
            }
        )

        st.plotly_chart(fig1, use_container_width=True)

    with col2:

        st.subheader("Deliverables by Type")

        fig2 = px.bar(
            df.groupby(["Type", "Status"]).size().reset_index(name="Count"),
            x="Type",
            y="Count",
            color="Status",
            barmode="group"
        )

        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ---------------- MAIN TABLE ----------------
    col1, col2 = st.columns([2, 1])

    with col1:

        st.subheader("Critical Deliverables")

        if "Due Date" not in df.columns:
            df["Due Date"] = pd.date_range("2024-01-01", periods=len(df))

        critical = df[df["Status"] != "On Track"].head(10)

        st.dataframe(
            critical[["Status", "Type", "Due Date"]],
            use_container_width=True
        )

    # ---------------- PERFORMANCE PANEL ----------------
    with col2:

        st.subheader("Performance Summary")

        st.metric("Avg SPI", spi)
        st.metric("Forecast Delays", int(delayed + at_risk))

        st.markdown("### Contractor Performance")
        st.info("ABC Ltd — 72% On Time")

else:
    st.info("Upload your deliverables file to begin")