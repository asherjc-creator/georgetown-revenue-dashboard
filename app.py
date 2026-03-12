import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import base64
from io import BytesIO
from PIL import Image
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

# -----------------------------
# 1. Scraping & Utility Functions
# -----------------------------
def get_image_base64(image_path):
    """Loads an image and converts it to a base64 string for HTML embed."""
    try:
        img = Image.open(image_path)
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    except Exception:
        return ""

def scrape_booking_rate(hotel_name):
    """
    Fetches live price for a hotel from Booking.com. 
    Note: Selectors may change based on Booking.com's site updates.
    """
    search_query = f"{hotel_name} Washington DC"
    url = f"https://www.booking.com/searchresults.html?ss={search_query.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        # Standard price tag selector as of 2026
        price_element = soup.find("span", {"data-testid": "price-and-discounted-price"})
        return price_element.text if price_element else "Rate Hidden/Unavailable"
    except Exception:
        return "Connection Error"

# -----------------------------
# 2. Data Loading & Cleaning
# -----------------------------
@st.cache_data(ttl=600)  # Auto-refresh every 10 mins if CSVs change
def load_all_dashboard_data():
    # 1. Load Competitor Rates
    comp = pd.read_csv("competitor_rates.csv")
    comp = comp[comp["Date"] != "Date"]  # Clean duplicate headers
    comp["Date"] = pd.to_datetime(comp["Date"], errors='coerce')
    comp["Rate"] = pd.to_numeric(comp["Rate"], errors='coerce')
    comp = comp.dropna(subset=["Date", "Rate"])
    
    # 2. Load/Generate Internal Performance Data
    try:
        df = pd.read_csv("georgetown_inn_data.csv")
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
        for col in ["Room_Revenue", "Rooms_Sold", "Total_Rooms", "Market_Occ", "Market_ADR"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna(subset=["Date"])
    except FileNotFoundError:
        # FIX: Generate dummy data matching the FULL CSV RANGE (e.g., March to July 2026)
        date_range = pd.date_range(start=comp["Date"].min(), end=comp["Date"].max())
        df = pd.DataFrame({
            "Date": date_range,
            "Room_Revenue": np.random.randint(5000, 9000, len(date_range)),
            "Rooms_Sold": np.random.randint(18, 28, len(date_range)),
            "Total_Rooms": [30]*len(date_range),
            "Market_Occ": np.random.uniform(0.65, 0.85, len(date_range)),
            "Market_ADR": np.random.uniform(450, 600, len(date_range)),
            "Lat": [38.9055]*len(date_range),
            "Lon": [-77.0620]*len(date_range)
        })

    # Calculations
    df["ADR"] = df["Room_Revenue"] / df["Rooms_Sold"]
    df["Occupancy"] = df["Rooms_Sold"] / df["Total_Rooms"]
    df["RevPAR"] = df["Room_Revenue"] / df["Total_Rooms"]
    df["MPI"] = (df["Occupancy"] / df["Market_Occ"]) * 100
    df["RGI"] = (df["RevPAR"] / (df["Market_ADR"] * df["Market_Occ"])) * 100
    
    # 3. Load Events (with DC.Events mock-up)
    try:
        events = pd.read_csv("events_dc.csv")
        events["Date"] = pd.to_datetime(events["Date"])
    except FileNotFoundError:
        events = pd.DataFrame([
            {"Date": "2026-03-20", "Event": "Cherry Blossom Peak", "Impact_Level": "High"},
            {"Date": "2026-04-12", "Event": "Easter Weekend", "Impact_Level": "Medium"},
            {"Date": "2026-07-04", "Event": "Independence Day", "Impact_Level": "High"}
        ])
        events["Date"] = pd.to_datetime(events["Date"])

    return df, comp, events

# Initialize Data
df, comp, events = load_all_dashboard_data()

# -----------------------------
# 3. Page Setup & Sidebar
# -----------------------------
st.set_page_config(page_title="Georgetown Inn Revenue Portal", layout="wide", page_icon="🏨")

# Custom Styling
st.markdown("""
<style>
.stMetric { background-color:white; padding:15px; border-radius:10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
.event-card { padding: 12px; border-radius: 8px; margin-bottom: 10px; border-left: 5px solid #007bff; background: #ffffff; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.image("https://via.placeholder.com/150", caption="Asher Jannu - Revenue Analyst") # Replace with your local image
    st.header("Global Controls")
    
    # DATE FILTER - Fixed to reflect actual CSV data boundaries
    min_date, max_date = df["Date"].min().date(), df["Date"].max().date()
    date_selection = st.date_input("Analysis Period", [min_date, max_date], min_value=min_date, max_value=max_date)
    
    st.markdown("---")
    st.header("Live Rate Scraper")
    target_hotel = st.selectbox("Select Competitor", ["Four Seasons DC", "Rosewood DC", "Ritz Carlton Georgetown"])
    if st.button("Get Live Price"):
        with st.spinner("Scraping Booking.com..."):
            live_price = scrape_booking_rate(target_hotel)
            st.success(f"Current Live Rate: {live_price}")

# Filter data based on sidebar selection
if len(date_selection) == 2:
    start_dt, end_dt = pd.to_datetime(date_selection[0]), pd.to_datetime(date_selection[1])
    filtered_df = df[(df["Date"] >= start_dt) & (df["Date"] <= end_dt)]
    filtered_comp = comp[(comp["Date"] >= start_dt) & (comp["Date"] <= end_dt)]
else:
    filtered_df, filtered_comp = df, comp

# -----------------------------
# 4. Dashboard Visuals
# -----------------------------
st.title("🏨 Georgetown Inn Revenue Dashboard")

# KPI Row
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Average ADR", f"${filtered_df['ADR'].mean():.2f}")
kpi2.metric("Occupancy", f"{filtered_df['Occupancy'].mean()*100:.1f}%")
kpi3.metric("RevPAR", f"${filtered_df['RevPAR'].mean():.2f}")
kpi4.metric("Market Share (RGI)", f"{filtered_df['RGI'].mean():.1f}")

# Main Performance Charts
col_a, col_b = st.columns(2)
with col_a:
    st.subheader("Revenue & RevPAR Trend")
    fig1 = px.line(filtered_df, x="Date", y=["Room_Revenue", "RevPAR"], color_discrete_sequence=['#1f77b4', '#ff7f0e'])
    st.plotly_chart(fig1, use_container_width=True)

with col_b:
    st.subheader("Competitor Rate Benchmarking")
    fig2 = px.line(filtered_comp, x="Date", y="Rate", color="Hotel", title="Direct Competitor Pricing")
    st.plotly_chart(fig2, use_container_width=True)

# Forecast and Events
st.write("---")
col_c, col_d = st.columns([2, 1])

with col_c:
    st.subheader("📈 90-Day Predictive Analysis")
    # Simplified forecast logic for visualization
    last_date = df["Date"].max()
    future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=90)
    forecast_df = pd.DataFrame({
        "Date": future_dates,
        "Predicted_Rate": np.interp(future_dates.view(np.int64), df["Date"].view(np.int64), df["ADR"]) * 1.05
    })
    fig_forecast = px.line(forecast_df, x="Date", y="Predicted_Rate", title="AI Suggested Pricing")
    st.plotly_chart(fig_forecast, use_container_width=True)

with col_d:
    st.subheader("🚩 Upcoming DC Events")
    upcoming = events[events["Date"] >= pd.to_datetime(datetime.now())].sort_values("Date").head(5)
    if upcoming.empty:
        st.write("No major events listed.")
    else:
        for _, row in upcoming.iterrows():
            st.markdown(f"""
            <div class="event-card">
                <strong>{row['Date'].strftime('%b %d, %Y')}</strong><br>
                {row['Event']} (Impact: {row['Impact_Level']})
            </div>
            """, unsafe_allow_html=True)

# Map Section
st.subheader("📍 Guest Origin Intensity")
m = folium.Map(location=[38.9055, -77.0620], zoom_start=4)
HeatMap(filtered_df[["Lat", "Lon"]].dropna().values.tolist()).add_to(m)
st_folium(m, width="100%", height=400)
