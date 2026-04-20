import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier

# ---------------- CONFIG ----------------
st.set_page_config(page_title="CL32 Dashboard", layout="wide")
st.title("📊 CL32 Programme Intelligence Dashboard")

# ---------------- UPLOAD ----------------
file = st.file_uploader("Upload CL32 Excel File", type=["xlsx"])

if file:

    df = pd.read_excel(file)

    # ---------------- CLEANING ----------------
    df["Start"] = pd.to_datetime(df["Start"], errors="coerce")
    df["Finish"] = pd.to_datetime(df["Finish"], errors="coerce")
    df["BL Project Start"] = pd.to_datetime(df["BL Project Start"], errors="coerce")
    df["BL Project Finish"] = pd.to_datetime(df["BL Project Finish"], errors="coerce")

    df["Remaining Duration"] = df["Remaining Duration"].astype(str).str.replace("d","")
    df["Remaining Duration"] = pd.to_numeric(df["Remaining Duration"], errors="coerce")

    df["Total Float"] = pd.to_numeric(df["Total Float"], errors="coerce")

    # ---------------- FEATURES ----------------
    df["schedule_slip"] = (df["Finish"] - df["BL Project Finish"]).dt.days
    df["start_variance"] = (df["Start"] - df["BL Project Start"]).dt.days
    df["float_stress"] = df["Remaining Duration"] / (df["Total Float"].abs() + 1)

    df["risk_class"] = df["schedule_slip"].apply(
        lambda x: 0 if x <= 0 else (1 if x <= 10 else 2)
    )

    df["type"] = df["Activity ID"].str.extract(r"([A-Z]+-[A-Z]+)")

    # ---------------- TABS ----------------
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview",
        "📉 Analytics",
        "🤖 ML Risk",
        "🔥 Deep Dive"
    ])

    # ================= TAB 1 =================
    with tab1:
        st.subheader("Programme KPIs")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Total Activities", len(df))
        c2.metric("Avg Delay", round(df["schedule_slip"].mean(), 1))
        c3.metric("At Risk", int((df["risk_class"] > 0).sum()))
        c4.metric("Avg Float Stress", round(df["float_stress"].mean(), 2))

        st.divider()

        st.dataframe(df.head(20), use_container_width=True)

    # ================= TAB 2 =================
    with tab2:
        st.subheader("Schedule & Risk Analytics")

        c1, c2 = st.columns(2)

        with c1:
            fig1 = px.histogram(df, x="schedule_slip", nbins=20)
            st.plotly_chart(fig1, use_container_width=True)

        with c2:
            fig2 = px.bar(
                df.groupby("type")["risk_class"].mean().reset_index(),
                x="type", y="risk_class"
            )
            st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Risk Heatmap")

        fig3 = px.scatter(
            df,
            x="Total Float",
            y="schedule_slip",
            color="risk_class",
            hover_data=["Activity ID"]
        )

        st.plotly_chart(fig3, use_container_width=True)

    # ================= TAB 3 =================
    with tab3:
        st.subheader("ML Risk Prediction Model")

        features = df[[
            "Remaining Duration",
            "start_variance",
            "Total Float",
            "float_stress"
        ]].fillna(0)

        target = df["risk_class"]

        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(features, target)

        df["predicted_risk"] = model.predict(features)

        st.dataframe(
            df[["Activity ID", "risk_class", "predicted_risk"]],
            use_container_width=True
        )

    # ================= TAB 4 =================
    with tab4:
        st.subheader("Full Programme Data")

        st.dataframe(df, use_container_width=True)

else:
    st.info("Upload CL32 Excel file to begin analysis")