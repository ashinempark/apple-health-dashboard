import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
from io import StringIO

st.set_page_config(page_title="Apple Health Dashboard", layout="wide")
st.title("📊 Apple Health Dashboard")
st.markdown("Upload your `export.xml` file from Apple Health to see your metrics.")

# --------- FILE UPLOADER ---------
uploaded_file = st.file_uploader("📁 Upload your export.xml file", type="xml")

if uploaded_file is not None:
    try:
        # Parse uploaded XML
        tree = ET.parse(uploaded_file)
        root = tree.getroot()

        # Extract step and heart rate data
        steps = []
        heart_rates = []

        for record in root.findall("Record"):
            rtype = record.attrib.get("type")
            start = record.attrib.get("startDate")
            value = record.attrib.get("value")

            if rtype == "HKQuantityTypeIdentifierStepCount":
                steps.append({"datetime": pd.to_datetime(start), "value": float(value)})

            elif rtype == "HKQuantityTypeIdentifierHeartRate":
                heart_rates.append({"datetime": pd.to_datetime(start), "value": float(value)})

        # Build DataFrames
        steps_df = pd.DataFrame(steps)
        heart_df = pd.DataFrame(heart_rates)

        if not steps_df.empty:
            steps_df["date"] = steps_df["datetime"].dt.date
            daily_steps = steps_df.groupby("date")["value"].sum().reset_index()
            daily_steps.columns = ["Date", "Steps"]

            st.subheader("🚶‍♂️ Daily Step Count")
            st.line_chart(daily_steps.set_index("Date"))
        else:
            st.info("No step count data found.")

        if not heart_df.empty:
            heart_df["date"] = heart_df["datetime"].dt.date
            daily_hr = heart_df.groupby("date")["value"].mean().reset_index()
            daily_hr.columns = ["Date", "Avg Heart Rate"]

            st.subheader("❤️ Average Heart Rate")
            st.line_chart(daily_hr.set_index("Date"))
        else:
            st.info("No heart rate data found.")

    except Exception as e:
        st.error(f"Error parsing XML: {e}")
else:
    st.info("Please upload your Apple Health export.xml file.")
