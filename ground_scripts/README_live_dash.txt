LIVE_GPS_DASH guide:

*** INTERNET REQUIRED ***
live_gps_dash shows the RAW GPS location downlinked to the GCS through MAVLINK. 
Perform the following steps to setup the live plot. 

Setup Map Token: (once)

Mac OS / Linux
- export MAPBOX_TOKEN="token_here"
    *** This will only persist for current terminal session ***
    *** To make the token persistent: ***
- echo 'export MAPBOX_TOKEN="token_here"' >> ~/.zshrc
    *** then restart terminal or run ***
    - source ~/.zshrc
    
Windows CMD Prompt
- setx MAPBOX_TOKEN "token_here"


Check Map Token:

Mac OS / Linux (terminal)
- echo $MAPBOX_TOKEN

Windows CMD Prompt
- echo %MAPBOX_TOKEN%
    - Should output token value
    - If blank try token set again

Packages:
- Pymavlink
- Dash
- Plotly 

Mac OS / Linux (terminal)
- pip3 install pymavlink dash plotly

Windows:
- pip install pymavlink dash plotly


Run:

Mac OS / Linux (terminal)
- python3 live_gps_dash.py

Windows: Command Prompt
- python live_gps_dash.py


View:
Web browser - http://127.0.0.1:8050/
- Or ctrl + click in terminal

Shutdown:
- ctrl + C

Debug:
MAVLINK connection fails, try port 14550
L15 - CONN_STR = os.getenv("MAVLINK_CONN", "udpin:0.0.0.0:14550")

