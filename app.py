import streamlit as st
import folium
from streamlit_folium import st_folium

# Page configuration
st.set_page_config(page_title="AI-ICE ROUTE Dashboard", layout="wide")

st.title("🚢 AI-ICE ROUTE: Antarctic Navigation Support System")
st.caption("AI/ML-enabled Antarctic sea-ice forecasting & safe route planning")

# Sidebar - Controls & Environmental Inputs
st.sidebar.header("🕹️ Vessel & Ocean Controls")
vessel_speed = st.sidebar.slider("Vessel Speed (knots)", 5, 20, 12)
ice_density = st.sidebar.select_slider("Sea Ice Concentration Risk", options=["Low", "Medium", "High"], value="Medium")
weather_alert = st.sidebar.checkbox("Simulate Sudden Storm / Ice Shift", value=False)

# Metrics Display
col1, col2, col3, col4 = st.columns(4)
col1.metric("Recommended Route Risk", "LOW" if not weather_alert else "MODERATE", delta="-12% Fuel" if not weather_alert else "+5% Risk")
col2.metric("Estimated Time of Arrival (ETA)", "14h 20m" if not weather_alert else "16h 45m")
col3.metric("Fuel Index Efficiency", "Optimized (-12%)", delta_color="normal")
col4.metric("Iceberg Clearance Distance", "> 15 km", delta="Safe Margin")

st.divider()

# Coordinate definitions (Antarctic region simulation)
start_coords = [-64.8, -63.5]   # Vessel Starting Point
end_coords = [-65.2, -64.2]     # Destination Research Station

# Map Initialization
m = folium.Map(location=[-65.0, -63.8], zoom_start=8, tiles="CartoDB positron")

# 1. Base Vessel & Target Markers
folium.Marker(start_coords, popup="Research Vessel Location", icon=folium.Icon(color="blue", icon="ship", prefix="fa")).add_to(m)
folium.Marker(end_coords, popup="Target Station", icon=folium.Icon(color="red", icon="flag")).add_to(m)

# 2. Simulated Sea-Ice Probability Zones (Polygons)
ice_zone_1 = [[-64.9, -63.8], [-65.0, -63.7], [-64.95, -63.5], [-64.85, -63.6]]
ice_zone_2 = [[-65.1, -64.1], [-65.15, -63.9], [-65.05, -63.8], [-65.0, -64.0]]

folium.Polygon(locations=ice_zone_1, color="cyan", fill=True, fill_color="cyan", fill_opacity=0.4, popup="Medium Ice Density Zone").add_to(m)
folium.Polygon(locations=ice_zone_2, color="blue", fill=True, fill_color="blue", fill_opacity=0.6, popup="High Ice Density Zone").add_to(m)

# 3. Simulated Iceberg Trajectory
iceberg_loc = [-65.0, -63.6]
folium.CircleMarker(location=iceberg_loc, radius=10, color="darkblue", fill=True, fill_color="cyan", popup="Drifting Iceberg A-76").add_to(m)

# 4. Route Calculation Engine Logic
# Primary Safe Route (Green)
safe_route = [start_coords, [-64.85, -63.9], [-65.05, -64.3], end_coords]

# High Risk Route (Red - Direct path through ice)
direct_risk_route = [start_coords, [-65.0, -63.8], end_coords]

# Dynamic re-routing if storm simulation is toggled
if weather_alert:
    safe_route = [start_coords, [-64.75, -64.0], [-65.1, -64.4], end_coords]
    st.warning("⚠️ Ice drift detected! Route dynamically updated to avoid high-density shift zone.")

# Draw Routes on Map
folium.PolyLine(safe_route, color="green", weight=5, opacity=0.8, popup="RECOMMENDED CORRIDOR (Safe + Efficient)").add_to(m)
folium.PolyLine(direct_risk_route, color="red", weight=3, opacity=0.5, dash_array="5, 10", popup="Direct Route (High Ice Risk)").add_to(m)

# Render Map in Streamlit Dashboard
st.subheader("🗺️ Live Navigation & Decision Loop")
st_folium(m, width=1100, height=500)

# Dashboard Summary Section
st.subheader("📋 Decision Summary for Captain")
st.write("""
- **Green Route (Recommended):** Avoids predicted iceberg drift corridors and dense ice fields while optimizing fuel efficiency.
- **Red Dashed Line:** Shortest path, but crosses high probability sea-ice concentration zones.
- **Re-Plan Trigger:** Automatically recalculates alternative safe corridors as new satellite observation layers arrive.
""")
