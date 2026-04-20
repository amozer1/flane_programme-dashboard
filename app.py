import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier

st.set_page_config(page_title="CL32 ML Dashboard", layout="wide")

st.title("📊 CL32 Programme Intelligence Dashboard")

# ---------------------------
# LOAD DATA
# ---------------------------
file = st.file_uploader("Upload CL32 Excel File", type=["xlsx"])

if file:
    df = pd.read_excel(file)

    # ---------------------------
    # CLEANING
    # ---------------------------
    df["Start"] = pd.to_datetime(df["Start"], errors="coerce")
    df["Finish"] = pd.to_datetime(df["Finish"], errors="coerce")
    df["BL Project Finish"] = pd.to_datetime(df["BL Project Finish"], errors="coerce")
    df["BL Project Start"] = pd.to_datetime(df["BL Project Start"], errors="coerce")

    df["Remaining Duration"] = df["Remaining Duration"].str.replace("d","").astype(float)
    df["Total Float"] = pd.to_numeric(df["Total Float"], errors="coerce")

    # ---------------------------
    # FEATURE ENGINEERING
    # ---------------------------
    df["schedule_slip"] = (df["Finish"] - df["BL Project Finish"]).dt.days
    df["start_variance"] = (df["Start"] - df["BL Project Start"]).dt.days
    df["float_stress"] = df["Remaining Duration"] / (df["Total Float"].abs() + 1)

    # Risk classification
    df["risk_class"] = df["schedule_slip"].apply(
        lambda x: 0 if x <= 0 else (1 if x <= 10 else 2)
    )

    # ---------------------------
    # SIDEBAR FILTERS
    # ---------------------------
    st.sidebar.header("Filters")

    activity_type = st.sidebar.multiselect(
        "Activity Type",
        df["Activity ID"].str.extract(r"([A-Z]+-[A-Z]+)")[0].unique()
    )

    if activity_type:
        df = df[df["Activity ID"].str.contains("|".join(activity_type))]

    # ---------------------------
    # KPI SECTION
    # ---------------------------
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Activities", len(df))
    col2.metric("Avg Slip (days)", round(df["schedule_slip"].mean(), 1))
    col3.metric("At Risk Activities", int((df["risk_class"] > 0).sum()))
    col4.metric("Avg Float Stress", round(df["float_stress"].mean(), 2))

    st.divider()

    # ---------------------------
    # TABLE VIEW
    # ---------------------------
    st.subheader("📋 Programme Data")
    st.dataframe(df)

    # ---------------------------
    # VISUAL 1: SLIP DISTRIBUTION
    # ---------------------------
    st.subheader("📉 Schedule Slip Distribution")
    fig1 = px.histogram(df, x="schedule_slip", nbins=20)
    st.plotly_chart(fig1, use_container_width=True)

    # ---------------------------
    # VISUAL 2: RISK BY TYPE
    # ---------------------------
    st.subheader("⚠️ Risk by Activity Type")

    df["type"] = df["Activity ID"].str.extract(r"([A-Z]+-[A-Z]+)")
    fig2 = px.bar(df.groupby("type")["risk_class"].mean().reset_index(),
                  x="type", y="risk_class")
    st.plotly_chart(fig2, use_container_width=True)

    # ---------------------------
    # ML MODEL (simple but functional)
    # ---------------------------
    st.subheader("🤖 ML Risk Prediction Model")

    features = df[["Remaining Duration","start_variance","Total Float","float_stress"]].fillna(0)
    target = df["risk_class"]

    model = RandomForestClassifier(n_estimators=100)
    model.fit(features, target)

    df["predicted_risk"] = model.predict(features)

    st.write("Predicted Risk Output")
    st.dataframe(df[["Activity ID","risk_class","predicted_risk"]])

    # ---------------------------
    # RISK HEATMAP
    # ---------------------------
    st.subheader("🔥 Risk Heatmap")

    fig3 = px.scatter(
        df,
        x="Total Float",
        y="schedule_slip",
        color="risk_class",
        hover_data=["Activity ID"]
    )

    st.plotly_chart(fig3, use_container_width=True)

else:
    st.info("Upload CL32 Excel file to begin analysis")