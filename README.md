# 🏨 Georgetown Inn Revenue Management Dashboard

An interactive, data-driven revenue management portal built with Python and Streamlit. This dashboard provides real-time performance tracking, competitor benchmarking, and AI-driven pricing recommendations for the Georgetown Inn.

## 🚀 Features

* **KPI Performance Tracking:** Real-time monitoring of ADR, Occupancy, RevPAR, and RGI (Revenue Generation Index).
* **Market Benchmarking:** Visual comparisons of Market Penetration Index (MPI) and competitor rate trends.
* **Geospatial Insights:** * **Competitive Landscape:** Interactive map showing the location of the hotel relative to sets like the Four Seasons and Rosewood.
    * **Guest Origin Heatmap:** Visualization of guest demographics and origin density.
* **🤖 AI Pricing Engine:** Automated logic that suggests optimal ADR based on current occupancy and historical performance.
* **Dynamic Filtering:** Filter all visualizations and metrics by custom date ranges.

## 🛠️ Tech Stack

* **Framework:** [Streamlit](https://streamlit.io/)
* **Data Analysis:** [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
* **Visualizations:** [Plotly Express](https://plotly.com/python/)
* **Mapping:** [Folium](https://python-visualization.github.io/folium/), [Streamlit-Folium](https://github.com/randyzwitch/streamlit-folium)
* **Image Handling:** [Pillow (PIL)](https://python-pillow.org/)

## 📂 Project Structure

```text
├── app.py                      # Main Streamlit application script
├── requirements.txt            # Python dependencies
├── georgetown_inn_data.csv     # Historical performance and guest origin data
├── competitor_rates.csv        # Market rate intelligence data
├── GTINN.jpeg                  # Branding and profile assets
└── README.md                   # Project documentation
