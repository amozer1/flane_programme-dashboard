import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="CL32 Programme Dashboard", layout="wide")

# ---------------- CUSTOM CSS (CARDS + STYLE) ----------------
st.markdown("""
<style>
.card {
    padding: 20px;
    border-radius: 12px;
    background-color: #111827;
    color: white;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
    text-align: center;
}
.card h2 {
    margin: 0;
    font-size: 28px;
}
.card p {
    margin: 0;
    opacity: 0.7;
}
.small {
    font-size: 14px;
    opacity: 0.7;
}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.title("📊 CL32 Programme Intelligence Dashboard")

# ---------------- UPLOAD ----------------
file = st.file_uploader("Upload CL32 Excel File", type=["xlsx"])

if file:

    # ---------------- LOAD ----------------
    df = pd.read_excel(file)

    # ---------------- CLEAN ----------------
    df["Start"] = pd.to_datetime(df["Start"], errors="coerce")
    df["Finish"] = pd.to_datetime(df["Finish"], errors="coerce")
    df["BL Project Start"] = pd.to_datetime(df["BL Project Start"], errors="coerce")
    df["BL Project Finish"] = pd.to_datetime(df["BL Project Finish"], errors="coerce")

    df["Remaining Duration"] = df["Remaining Duration"].astype(str).str.replace("d","")
    df["Remaining Duration"] = pd.to_numeric(df["Remaining Duration"], errors="coerce")
    df["Total Float"] = pd.to_numeric(df["Total Float"], errors="coerce")

    # ---------------- ENGINEERING METRICS ----------------
    df["schedule_slip"] = (df["Finish"] - df["BL Project Finish"]).dt.days
    df["start_variance"] = (df["Start"] - df["BL Project Start"]).dt.days
    df["float_stress"] = df["Remaining Duration"] / (df["Total Float"].abs() + 1)

    # ---------------- RISK CLASS (RAG SYSTEM) ----------------
    def risk(x):
        if x <= 0:
            return "🟢 On Track"
        elif x <= 10:
            return "🟠 At Risk"
        else:
            return "🔴 Critical"

    df["risk"] = df["schedule_slip"].apply(risk)

    # ---------------- ML MODEL ----------------
    features = df[["Remaining Duration","start_variance","Total Float","float_stress"]].fillna(0)
    target = df["schedule_slip"].apply(lambda x: 0 if x<=0 else (1 if x<=10 else 2))

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(features, target)

    df["predicted_risk"] = model.predict(features)

    # ---------------- KPI CARDS ----------------
    col1, col2, col3, col4 = st.columns(4)

    col1.markdown(f"""
    <div class="card">
        <h2>{len(df)}</h2>
        <p>Total Activities</p>
    </div>
    """, unsafe_allow_html=True)

    col2.markdown(f"""
    <div class="card">
        <h2>{round(df['schedule_slip'].mean(),1)}</h2>
        <p>Avg Schedule Slip (days)</p>
    </div>
    """, unsafe_allow_html=True)

    col3.markdown(f"""
    <div class="card">
        <h2>{(df['risk']=="🔴 Critical").sum()}</h2>
        <p>Critical Activities</p>
    </div>
    """, unsafe_allow_html=True)

    col4.markdown(f"""
    <div class="card">
        <h2>{round(df['float_stress'].mean(),2)}</h2>
        <p>Avg Float Stress</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ---------------- DATA TABLE ----------------
    with st.expander("📋 Programme Data"):
        st.dataframe(df, use_container_width=True)

    st.divider()

    # ---------------- CHARTS ----------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Schedule Slip Distribution")
        fig1 = px.histogram(df, x="schedule_slip", nbins=20, color_discrete_sequence=["#636EFA"])
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("Risk Distribution")
        fig2 = px.histogram(df, x="risk", color="risk")
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # ---------------- RISK HEATMAP ----------------
    st.subheader("🔥 Programme Risk Heatmap")

    fig3 = px.scatter(
        df,
        x="Total Float",
        y="schedule_slip",
        color="risk",
        hover_data=["Activity ID"],
        color_discrete_map={
            "🟢 On Track":"green",
            "🟠 At Risk":"orange",
            "🔴 Critical":"red"
        }
    )

    st.plotly_chart(fig3, use_container_width=True)

    st.divider()

    # ---------------- ML OUTPUT ----------------
    st.subheader("🤖 ML Risk Prediction Output")

    st.dataframe(df[["Activity ID","risk","predicted_risk"]])

else:
    st.info("Upload your CL32 Excel file to begin analysis")