import time
from collections import deque
 
from pymavlink import mavutil
import matplotlib.pyplot as plt
 
# If QGC is connected to PX4 SITL, you can often listen on 14550.
# If you're routing MAVLink differently, adjust accordingly.
master = mavutil.mavlink_connection("udpin:0.0.0.0:14540")
master.wait_heartbeat()
print("Heartbeat received")
 
# store last N points
N = 2000
lats = deque(maxlen=N)
lons = deque(maxlen=N)
 
plt.ion()
fig, ax = plt.subplots()
line, = ax.plot([], [], marker=".", linestyle="-")
ax.set_xlabel("Longitude (deg)")
ax.set_ylabel("Latitude (deg)")
ax.set_title("Live GPS_RAW_INT track")
 
def redraw():
    if len(lats) < 2:
        return
    line.set_data(list(lons), list(lats))
    ax.relim()
    ax.autoscale_view()
    fig.canvas.draw()
    fig.canvas.flush_events()
 
last_draw = 0.0
 
while True:
    msg = master.recv_match(type="GPS_RAW_INT", blocking=True, timeout=1.0)
    if msg is None:
        continue
 
    # MAVLink uses 1e7 scaling for lat/lon
    lat = msg.lat / 1e7
    lon = msg.lon / 1e7
 
    # vel is cm/s in GPS_RAW_INT (per MAVLink message definition)
    speed_mps = (msg.vel / 100.0) if msg.vel is not None else None
 
    lats.append(lat)
    lons.append(lon)
 
    if speed_mps is not None:
        print(f"lat={lat:.7f}, lon={lon:.7f}, speed={speed_mps:.2f} m/s, sats={msg.satellites_visible}")
 
    now = time.time()
    if now - last_draw > 0.2:  # ~5 Hz plot refresh
        redraw()
        last_draw = now