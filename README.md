# AEGIS Astronaut Monitor

AEGIS is a proof-of-concept dashboard for exploring astronaut health and spacecraft habitat monitoring. It brings simulated crew biometrics, mission context, and environmental readings together in an interactive interface.

The project explores how combining crew and habitat data could help identify emerging risks and support timely decisions during spaceflight. The current application is a demonstration: it uses simulated data and does not provide live monitoring or medical recommendations.

## Live demo and presentation

- **Streamlit demo:** [Open the AEGIS dashboard](https://aegis-nasa-app.streamlit.app/)
- **Presentation:** [View the project slides](https://docs.google.com/presentation/d/1u8sIta_hp4IRyADeibsV-ATyMZHyrOxvSUegoEt61qI)

## Dashboard features

- **Crew health overview:** View readiness indicators, compare crew members, and inspect individual profiles, alerts, and suggested actions.
- **Mission scenarios:** Switch between pre-launch, orbit, and re-entry; adjust the mission day; and trigger a simulated camera event.
- **Telemetry visualizations:** Explore biometric and crew comparison charts, status summaries, and a generated 24-hour trend for a selected astronaut.
- **Crew network:** Select a crew member to view their profile, and explore the interactive network of astronauts and assigned habitat modules.
- **Habitat monitoring:** Review module conditions, crew-wide correlation alerts, and an overview of station environmental readings.
- **Exercise simulator:** Trigger demo exercise feedback in the dashboard.

## Run locally

The application is implemented in Python with Streamlit. From the project directory, create a virtual environment, install the dependencies, and start the dashboard:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run astronaut_monitor_ez.py
```

Open the local URL printed by Streamlit, typically [http://localhost:8501](http://localhost:8501). Running Streamlit through the virtual environment's Python keeps the application and its dependencies in the same environment.

## Scope and limitations

Crew profiles, habitat readings, mission events, and hourly history are simulated. The application does not connect to NASA systems, live sensors, or a Neo4j database. Emergency and exercise controls only show demonstration feedback; they do not send messages or perform medical actions. AEGIS is not a medical or operational tool.

## References

- [NASA: Five Hazards of Human Spaceflight](https://www.nasa.gov/hrp/hazards/)
- [NASA: Risks of Human Spaceflight](https://www.nasa.gov/hrp/risks/)
- [Canadian Space Agency: Monitoring radiation for astronaut health](https://www.asc-csa.gc.ca/eng/news/articles/2026/2026-02-26-monitoring-radiation-astronaut-health.asp)
