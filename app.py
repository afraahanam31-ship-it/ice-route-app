import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="AI-ICE ROUTE Dashboard", layout="wide")

st.title("🧊 AI-ICE ROUTE: Antarctic Maritime Navigation")
st.subheader("Time-Series Sea-Ice Drift & Route Optimization")

# Sidebar Controls
st.sidebar.header("Telemetry Controls")
vessel_speed = st.sidebar.slider("Vessel Speed (knots)", 5, 20, 12)

# Time Slider for Movement Simulation
st.sidebar.subheader("🕒 Satellite Time Progression")
time_hour = st.sidebar.slider("Simulate Hours Elapsed (0h to 24h)", 0, 24, 0, step=2)

# Dynamic Ice Coordinates based on Time
ice_drift_lat = -64.2 + (time_hour * 0.015)
ice_drift_lon = -62.5 + (time_hour * 0.035)

# Calibrated Vessel Position (Interpolates directly along the route points)
fraction = time_hour / 24.0
vessel_lat = -65.0 + fraction * (-63.8 - (-65.0))
vessel_lon = -64.0 + fraction * (-61.5 - (-64.0))

# Proximity Check (Simulated proximity between ship and ice field)
near_ice = 8 <= time_hour <= 16

# Top Warning System
if near_ice:
    st.error("⚠️ **ICE HAZARD ALERT:** Vessel entering high-density iceberg drift zone! AI rerouting active.")
else:
    st.success("✅ **ROUTE CLEAR:** Safe distance maintained from primary iceberg fields.")

# Display Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Current Time Window", f"+{time_hour} Hours")
col2.metric("Vessel Coordinates", f"{round(vessel_lat, 2)}°S, {round(vessel_lon, 2)}°W")
col3.metric("Ice Drift Velocity", "1.2 knots NE")
col4.metric("Risk Assessment", "HIGH (ICE BERGS)" if near_ice else "LOW")

# Base Map Setup
m = folium.Map(location=[-64.5, -63.0], zoom_start=7, tiles="OpenStreetMap")

# 1. Fixed Start Location
folium.Marker(
    location=[-65.0, -64.0],
    popup="Start: Departure Port",
    icon=folium.Icon(color="gray", icon="play", prefix="fa")
).add_to(m)

# 2. Fixed Final Destination
folium.Marker(
    location=[-63.8, -61.5],
    popup="Destination: Rothera Research Station",
    icon=folium.Icon(color="red", icon="flag", prefix="fa")
).add_to(m)

# 3. Dynamic Moving Vessel Marker
folium.Marker(
    location=[vessel_lat, vessel_lon],
    popup=f"Vessel Position (+{time_hour}h)",
    icon=folium.Icon(color="blue", icon="ship", prefix="fa")
).add_to(m)

# 4. Iceberg Hazard Zone (Cyan Polygon with Red Warning Border)
ice_polygon = [
    [ice_drift_lat, ice_drift_lon],
    [ice_drift_lat + 0.3, ice_drift_lon + 0.2],
    [ice_drift_lat + 0.2, ice_drift_lon + 0.5],
    [ice_drift_lat - 0.1, ice_drift_lon + 0.3]
]
folium.Polygon(
    locations=ice_polygon,
    color="red",
    weight=2,
    fill=True,
    fill_color="cyan",
    fill_opacity=0.5,
    popup=f"⚠️ DANGER: Iceberg Concentration Zone (+{time_hour}h)"
).add_to(m)

# 5. Dynamic AI Safe Route Corridor
safe_route = [
    [-65.0, -64.0],
    [-64.5, -63.5],
    [ice_drift_lat - 0.3, ice_drift_lon - 0.2],
    [-63.8, -61.5]
]
folium.PolyLine(safe_route, color="green", weight=5, opacity=0.8, popup="AI Safe Corridor").add_to(m)

# Render Map
st_folium(m, width="100%", height=500)
