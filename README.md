# AEGIS Astronaut Monitor (EZ)

`astronaut_monitor_ez.py` is a Streamlit dashboard that demonstrates astronaut health monitoring alongside habitat conditions. It combines simulated biometric profiles, mission context, and station telemetry in one interactive interface.

## Features

- **Crew health dashboard:** readiness status, crew comparisons, and an individual health profile with alerts and suggested actions.
- **Mission controls:** switch between orbit, re-entry, and pre-launch scenarios; adjust the mission day and simulate an emergency camera event.
- **Telemetry visualizations:** biometric radar, crew comparison and status charts, plus a generated 24-hour trend for the selected astronaut.
- **Interactive crew network:** click an astronaut node to inspect their profile; drag nodes, pan, and zoom. Astronaut nodes connect to their assigned habitat modules.
- **Habitat monitoring:** module conditions, crew-wide correlation alerts, and a station environment matrix.
- **Exercise simulator:** buttons demonstrate exercise-session feedback in the dashboard.

## Setup and run

From this directory, in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run astronaut_monitor_ez.py
```

Open the local URL printed by Streamlit, usually `http://localhost:8501`. Using the virtual environment's Python ensures Streamlit and the graph component are loaded from the same environment.

## Data and limitations

Astronaut profiles, habitat readings, mission events, and hourly history are simulated in the app; it does not connect to NASA systems, live sensors, or a Neo4j database. Emergency and exercise controls only display demo feedback—they do not send messages or perform real medical actions. This dashboard is for demonstration and is not a medical or operational tool.
