import os
import time
import threading
from collections import deque

from pymavlink import mavutil

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.io as pio

# ---------- CONFIG ----------
CONN_STR = os.getenv("MAVLINK_CONN", "udpin:0.0.0.0:14540")  # try 14550 if needed
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN", "")
pio.mapbox_token = MAPBOX_TOKEN

# how many points to keep in the trail
MAX_POINTS = 3000

# store shared telemetry (thread-safe enough for simple append/read patterns)
gps_points = deque(maxlen=MAX_POINTS)      # list of (lat, lon)
est_points = deque(maxlen=MAX_POINTS)      # optional overlay (lat, lon)
latest = {"lat": None, "lon": None, "speed_mps": None, "sats": None, "fix": None}
# latest = {"lat": 40.00871, "lon": -105.24793, "speed_mps": None, "sats": None, "fix": None}


# ---------- MAVLink listener thread ----------
def mavlink_worker():
    master = mavutil.mavlink_connection(CONN_STR)
    master.wait_heartbeat()
    print(f"Heartbeat received on {CONN_STR}")

    while True:
        msg = master.recv_match(blocking=True, timeout=1.0)
        if msg is None:
            continue

        mtype = msg.get_type()

        # Raw GPS sensor data:
        if mtype == "GPS_RAW_INT":
            lat = msg.lat / 1e7
            lon = msg.lon / 1e7
            # vel is cm/s (ground speed)
            speed_mps = (msg.vel / 100.0) if msg.vel is not None else None

            gps_points.append((lat, lon))
            latest.update({
                "lat": lat,
                "lon": lon,
                "speed_mps": speed_mps,
                "sats": getattr(msg, "satellites_visible", None),
                "fix": getattr(msg, "fix_type", None),
            })

        # Estimated position overlay
        # PX4 often sends GLOBAL_POSITION_INT (EKF fused)
        elif mtype == "GLOBAL_POSITION_INT":
            est_lat = msg.lat / 1e7
            est_lon = msg.lon / 1e7
            est_points.append((est_lat, est_lon))


# start listener
threading.Thread(target=mavlink_worker, daemon=True).start()


# # Fake trail for UI testing — remove when using real MAVLink
# import math
# BASE_LAT, BASE_LON = 40.00871, -105.24793
# for i in range(100):
#     angle = i * 0.1
#     gps_points.append((
#         BASE_LAT + 0.0002 * math.sin(angle),
#         BASE_LON + 0.0002 * math.cos(angle),
#     ))


# ---------- Dash app ----------
app = dash.Dash(__name__)
app.title = "PX4 Live GPS"

app.layout = html.Div(
    style={"fontFamily": "system-ui", "margin": "12px"},
    children=[
        html.H3("PX4 Live GPS (Raw) + Speed"),
        html.Div(id="status", style={"marginBottom": "8px"}),
        dcc.Graph(id="map", style={"height": "80vh"}),
        dcc.Interval(id="tick", interval=500, n_intervals=0),  # 2 Hz UI refresh
        html.Div(
            "Tip: If you see no data, try MAVLINK_CONN=udpin:0.0.0.0:14550",
            style={"marginTop": "8px", "opacity": 0.7},
        )
    ],
)


def make_figure():
    # Default center if no data yet
    center_lat, center_lon = (0.0, 0.0)
    zoom = 2

    if latest["lat"] is not None and latest["lon"] is not None:
        center_lat, center_lon = latest["lat"], latest["lon"]
        zoom = 17  # close zoom for GPS tracking

    fig = go.Figure()

    # Raw GPS trail
    if len(gps_points) >= 2:
        lats = [p[0] for p in gps_points]
        lons = [p[1] for p in gps_points]
        fig.add_trace(go.Scattermap(
            lat=lats, lon=lons,
            mode="lines",
            name="GPS_RAW_INT trail",
            line={"width": 4},
            hoverinfo="skip"
        ))
        # Latest raw GPS point
        fig.add_trace(go.Scattermap(
            lat=[lats[-1]], lon=[lons[-1]],
            mode="markers",
            name="GPS_RAW_INT current",
            marker={"size": 12},
        ))

    # Estimated overlay (optional)
    if len(est_points) >= 2:
        elats = [p[0] for p in est_points]
        elons = [p[1] for p in est_points]
        fig.add_trace(go.Scattermap(
            lat=elats, lon=elons,
            mode="lines",
            name="GLOBAL_POSITION_INT (est)",
            line={"width": 3, "dash": "dot"},
            hoverinfo="skip"
        ))
        fig.add_trace(go.Scattermap(
            lat=[elats[-1]], lon=[elons[-1]],
            mode="markers",
            name="Est current",
            marker={"size": 10, "symbol": "circle"},
        ))

    # Mapbox layout (satellite)
    fig.update_layout(
        # uirevision="locked", 
        margin=dict(l=0, r=0, t=0, b=0),
        map=dict(
            # accesstoken=MAPBOX_TOKEN if MAPBOX_TOKEN else None,
            style="satellite",  # or "satellite-streets" if you want labels
            center=dict(lat=center_lat, lon=center_lon),
            zoom=zoom,
        ),
        legend=dict(orientation="h", yanchor="bottom", y=0.01, xanchor="left", x=0.01),
    )

    return fig


@app.callback(
    Output("map", "figure"),
    Output("status", "children"),
    Input("tick", "n_intervals")
)
def update(_n):
    fig = make_figure()

    if latest["lat"] is None:
        status = "Waiting for GPS_RAW_INT..."
    else:
        sp = latest["speed_mps"]
        sats = latest["sats"]
        fix = latest["fix"]
        sp_txt = f"{sp:.2f} m/s" if sp is not None else "N/A"
        status = f"lat={latest['lat']:.6f}, lon={latest['lon']:.6f} | speed={sp_txt} | sats={sats} | fix={fix}"

    # If no token, warn why satellite might not load
    if not MAPBOX_TOKEN:
        status += "  |  (MAPBOX_TOKEN not set — satellite tiles may not render)"

    return fig, status


if __name__ == "__main__":
    app.run(debug=True)
