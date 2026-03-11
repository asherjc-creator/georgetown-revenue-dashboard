import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium

# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="Georgetown Inn Revenue Portal",
    layout="wide"
)

# -----------------------------
# Styling
# -----------------------------
st.markdown("""
<style>
.main {
    background-color:#f5f7f9;
}
.stMetric {
    background-color:white;
    padding:15px;
    border-radius:10px;
}
</style>
""", unsafe_allow_html=True)

st.title("🏨 Georgetown Inn | Revenue Management Dashboard")
st.subheader("Performance vs Georgetown Competitive Set")

# -----------------------------
# Load Data
# -----------------------------
df = pd.read_csv("georgetown_inn_data.csv")
df["Date"] = pd.to_datetime(df["Date"])

# -----------------------------
# Calculations
# -----------------------------
df["ADR"] = df["Room_Revenue"] / df["Rooms_Sold"]
df["Occupancy"] = df["Rooms_Sold"] / df["Total_Rooms"]
df["RevPAR"] = df["Room_Revenue"] / df["Total_Rooms"]

# Market benchmarking
df["MPI"] = (df["Occupancy"] / df["Market_Occ"]) * 100
df["RGI"] = (df["RevPAR"] / (df["Market_ADR"] * df["Market_Occ"])) * 100

# -----------------------------
# Sidebar filters
# -----------------------------
st.sidebar.header("Control Panel")

start_date, end_date = st.sidebar.date_input(
    "Select Date Range",
    [df["Date"].min(), df["Date"].max()]
)

filtered = df[(df["Date"] >= pd.to_datetime(start_date)) &
              (df["Date"] <= pd.to_datetime(end_date))]

# -----------------------------
# KPI Metrics
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Average ADR", f"${filtered['ADR'].mean():.2f}")
col2.metric("Occupancy", f"{filtered['Occupancy'].mean()*100:.1f}%")
col3.metric("RevPAR", f"${filtered['RevPAR'].mean():.2f}")
col4.metric("Revenue Generation Index", f"{filtered['RGI'].mean():.1f}")

# -----------------------------
# Charts
# -----------------------------
c1, c2 = st.columns(2)

with c1:
    st.write("### Revenue & RevPAR Trend")
    fig = px.line(
        filtered,
        x="Date",
        y=["Room_Revenue","RevPAR"],
        title="Daily Performance"
    )
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.write("### Market Penetration Index (MPI)")
    fig2 = px.bar(
        filtered,
        x="Date",
        y="MPI",
        color="MPI",
        color_continuous_scale="RdYlGn",
        title="Market Share Performance"
    )
    st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# Map Section
# -----------------------------
st.write("### Georgetown Competitive Landscape")

m = folium.Map(location=[38.9055,-77.0620], zoom_start=15)

# Georgetown Inn
folium.Marker(
    [38.9055,-77.0620],
    popup="Georgetown Inn",
    icon=folium.Icon(color="blue")
).add_to(m)

# Competitors
competitors = [
    {"name":"Four Seasons DC","loc":[38.9052,-77.0581]},
    {"name":"Rosewood Washington DC","loc":[38.9045,-77.0625]},
    {"name":"Ritz Carlton Georgetown","loc":[38.9031,-77.0615]}
]

for comp in competitors:
    folium.CircleMarker(
        location=comp["loc"],
        radius=8,
        popup=comp["name"],
        color="red",
        fill=True
    ).add_to(m)

st_folium(m,width=1100,height=400)

# -----------------------------
# Pricing Engine
# -----------------------------
st.write("### 🤖 Dynamic Pricing Recommendation")

latest_occ = filtered["Occupancy"].iloc[-1]

if latest_occ > 0.90:
    st.success("High demand detected → Increase BAR by 15%")
elif latest_occ > 0.75:
    st.info("Healthy demand → Maintain rate and monitor competitors")
else:
    st.warning("Low demand → Increase OTA visibility or offer packages")