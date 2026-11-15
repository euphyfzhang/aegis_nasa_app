# AEGIS Astronaut Monitor
1. What exactly does it do?
Aegis-1 is an autonomous biometric and habitat intelligence system that safeguards astronauts in orbit—and isolated populations on Earth. It continuously fuses hourly smart-vest biometric telemetry (tracking skin condition, blood sugar, red blood cell density, immunity, and heart rhythm) with real-time habitat environmental sensors (air quality, CO₂ scrubbers, humidity, and cumulative space radiation). It provides proactive tracking, instant threshold alerts, location-aware diagnostics, and automated countermeasure prescriptions.

2. How does it work?
Dual-Stream Telemetry Ingestion: Smart-garment sensors feed hourly physiological streams into the system, while habitat sensors simultaneously track environmental life support metrics.

Adaptive Baseline & False-Positive Intelligence: It adjusts normal medical thresholds for microgravity (0G). For example, it prevents false alarms by recognizing that mild baseline hypotension or a leaky heart valve stabilizes differently in orbit, and that high baseline red blood cells act as a natural buffer against space anemia.

Crew-Wide & Environmental Correlation: By cross-referencing multi-crew vest data with module locations, it distinguishes individual illnesses from shared cabin hazards (such as cabin CO₂ spikes or radiation surges).

AI Vision & Automated Closed-Loop Actions: It leverages AI video behavior to detect confinement fatigue, restricts complex tasks during metabolic or autonomic stress, adjusts cabin ventilation fans, vibrates vests to pace breathing, and triggers emergency medical triage when necessary.

3. What benefits does it have?
Proactive Rather Than Reactive Safety: Shifts from passive health tracking to real-time, threshold-based interventions that keep crew members mission-ready before minor physiological drifts escalate.

Elimination of False Alarms: Saves crew time and reduces panic by understanding how the human body naturally adapts (and safely changes) in microgravity.

Holistic Guidance: Seamlessly bridges medical monitoring, targeted nutrition, resistance workouts (ARED), skincare, and environmental management.   

Reliable Emergency Safety Net: Ensures that whether astronauts face mild fatigue, radiation exposure, or acute syncope, they have an automated safety net connected to both onboard crew and Earth Flight Surgeons.

4. What do you hope to achieve?
To protect human life across hostile enclosed worlds (microgravity, radiation, isolation, distance).   

To close the loop between astronaut biology and habitat engineering.

To scale this closed-loop intelligence beyond deep space and bring it back to Earth to safeguard vulnerable enclosed populations—such as immunocompromised children in hospital bubble rooms, deep-sea submarine crews, and commercial aviation passengers.   

5. What tools, coding languages, hardware, or software did you use to develop your project?
(Note: While specific code files or libraries aren't explicitly detailed in the final slide deck text, the project architecture and presentation were built for the NASA App Hackathon (Nov 14, 2026) utilizing modern data-streaming architecture, interactive visual dashboards like web/bar/pie charts, smart-garment biometric sensors, and AI computer vision behavioral tracking).   

--------
### Application

## Streamlit POC : https://aegis-nasa-app.streamlit.app/
## Presentation Slide : https://docs.google.com/presentation/d/1u8sIta_hp4IRyADeibsV-ATyMZHyrOxvSUegoEt61qI

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

### Reference and Resources
- 5 Hazards of Human Spaceflight:  https://www.nasa.gov/hrp/hazards/
- Risks of Human Spaceflight : https://www.nasa.gov/hrp/risks/
- Monitoring radiation for astronaut health : https://www.asc-csa.gc.ca/eng/news/articles/2026/2026-02-26-monitoring-radiation-astronaut-health.asp