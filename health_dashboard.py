import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime
import os

# --------- SETTINGS ---------
XML_PATH = "export.xml"  # Update this if you move your file
st.set_page_config(page_title="Apple Health Dashboard", layout="wide")

# --------- HELPER FUNCTIONS ---------
@st.cache_data
def parse_health_data(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

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

    steps_df = pd.DataFrame(steps)
    heart_df = pd.DataFrame(heart_rates)

    steps_df["date"] = steps_df["datetime"].dt.date
    heart_df["date"] = heart_df["datetime"].dt.date

    daily_steps = steps_df.groupby("date")["value"].sum().reset_index()
    daily_hr = heart_df.groupby("date")["value"].mean().reset_index()

    daily_steps.columns = ["Date", "Steps"]
    daily_hr.columns = ["Date", "Avg Heart Rate"]

    return daily_steps, daily_hr

# --------- MAIN DASHBOARD ---------
st.title("📊 Apple Health Dashboard")
st.markdown("Visualize your Apple Health data interactively. Data source: `export.xml`")

if not os.path.exists(XML_PATH):
    st.error(f"Please place your `export.xml` file in this folder. File not found: `{XML_PATH}`")
else:
    steps_df, hr_df = parse_health_data(XML_PATH)

    st.subheader("🚶‍♂️ Daily Step Count")
    st.line_chart(steps_df.set_index("Date"))

    st.subheader("❤️ Average Heart Rate")
    st.line_chart(hr_df.set_index("Date"))

    st.success("Data loaded and visualized successfully!")
