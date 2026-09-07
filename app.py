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

# 1. Dynamic Ice Drift (Drifts east/northeast at a realistic pace)
ice_drift_lat = -64.0 + (time_hour * 0.01)
ice_drift_lon = -62.0 + (time_hour * 0.02)

# 2. Ice Hazard Polygon Definition
ice_polygon = [
    [ice_drift_lat, ice_drift_lon],
    [ice_drift_lat + 0.3, ice_drift_lon + 0.2],
    [ice_drift_lat + 0.2, ice_drift_lon + 0.5],
    [ice_drift_lat - 0.1, ice_drift_lon + 0.3]
]

# 3. Safe Corridor Waypoints (Clear detour around the ice polygon west side)
detour_lat = ice_drift_lat - 0.2
detour_lon = ice_drift_lon - 0.6

start_pos = [-65.0, -64.0]
waypoint_1 = [-64.5, -63.5]
waypoint_2 = [detour_lat, detour_lon]
destination_pos = [-63.8, -61.5]

safe_route = [start_pos, waypoint_1, waypoint_2, destination_pos]

# 4. Calibrated Vessel Interpolation along the Safe Corridor
fraction = time_hour / 24.0
if fraction <= 0.33:
    sub_f = fraction / 0.33
    vessel_lat = start_pos[0] + sub_f * (waypoint_1[0] - start_pos[0])
    vessel_lon = start_pos[1] + sub_f * (waypoint_1[1] - start_pos[1])
elif fraction <= 0.66:
    sub_f = (fraction - 0.33) / 0.33
    vessel_lat = waypoint_1[0] + sub_f * (waypoint_2[0] - waypoint_1[0])
    vessel_lon = waypoint_1[1] + sub_f * (waypoint_2[1] - waypoint_1[1])
else:
    sub_f = (fraction - 0.66) / 0.34
    vessel_lat = waypoint_2[0] + sub_f * (destination_pos[0] - waypoint_2[0])
    vessel_lon = waypoint_2[1] + sub_f * (destination_pos[1] - waypoint_2[1])

# Proximity Check
near_ice = 8 <= time_hour <= 18

# Alert Banner
if near_ice:
    st.error("⚠️ **ICE HAZARD ALERT:** Iceberg field ahead. AI active detour route enforced.")
else:
    st.success("✅ **ROUTE CLEAR:** Safe clearance distance maintained from ice zone.")

# Top Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Current Time Window", f"+{time_hour} Hours")
col2.metric("Vessel Coordinates", f"{round(vessel_lat, 2)}°S, {round(vessel_lon, 2)}°W")
col3.metric("Ice Drift Velocity", "1.2 knots NE")
col4.metric("Risk Assessment", "MODERATE DETOUR" if near_ice else "LOW")

# Map Setup
m = folium.Map(location=[-64.3, -63.0], zoom_start=7, tiles="OpenStreetMap")

# Start Marker
folium.Marker(
    location=start_pos,
    popup="Start: Departure Port",
    icon=folium.Icon(color="gray", icon="play", prefix="fa")
).add_to(m)

# Destination Marker
folium.Marker(
    location=destination_pos,
    popup="Destination: Rothera Research Station",
    icon=folium.Icon(color="red", icon="flag", prefix="fa")
).add_to(m)

# Ice Polygon
folium.Polygon(
    locations=ice_polygon,
    color="red",
    weight=2,
    fill=True,
    fill_color="cyan",
    fill_opacity=0.5,
    popup=f"⚠️ DANGER: Iceberg Concentration Zone (+{time_hour}h)"
).add_to(m)

# Green Safe Route Line
folium.PolyLine(safe_route, color="green", weight=5, opacity=0.8, popup="AI Safe Corridor").add_to(m)

# Moving Ship Marker
folium.Marker(
    location=[vessel_lat, vessel_lon],
    popup=f"Vessel Position (+{time_hour}h)",
    icon=folium.Icon(color="blue", icon="ship", prefix="fa")
).add_to(m)

# Render Map
st_folium(m, width="100%", height=500)
