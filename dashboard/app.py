import streamlit as st
from pathlib import Path
import pandas as pd
import plotly.express as px

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/"output"

st.set_page_config(page_title="Device Inventory Intelligence", layout="wide")
st.title("Device Inventory Intelligence & Utilization Analytics")

try:
    devices = pd.read_csv(OUT/"device_utilization.csv")
    types = pd.read_csv(OUT/"device_type_summary.csv")
    employees = pd.read_csv(OUT/"employee_usage.csv")
except FileNotFoundError:
    st.warning("Run `python -m analytics.generate_report` first.")
    st.stop()

c1,c2,c3,c4 = st.columns(4)
c1.metric("Devices", f"{len(devices):,}")
c2.metric("Total Checkouts", f"{devices.checkout_count.sum():,}")
c3.metric("Avg Utilization", f"{devices.utilization_rate.mean():.1%}")
c4.metric("Underutilized", int((devices.utilization_segment=="Underutilized").sum()))

st.subheader("Device Demand")
st.plotly_chart(px.bar(types, x="device_type", y="total_checkouts", title="Checkouts by Device Type"), use_container_width=True)

st.subheader("Utilization")
st.plotly_chart(px.box(devices, x="device_type", y="utilization_rate", title="Utilization Distribution"), use_container_width=True)

st.subheader("Inventory Explorer")
st.dataframe(devices.sort_values("utilization_rate", ascending=False), use_container_width=True)

st.subheader("Employee Usage")
st.dataframe(employees.head(25), use_container_width=True)
