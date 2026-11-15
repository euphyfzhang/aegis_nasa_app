import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import math
from streamlit_agraph import agraph, Config, Edge, Node
from datetime import datetime, timedelta

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION & STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AEGIS | Astronaut Biometric & Habitat Monitor",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .metric-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
    }
    .alert-critical {
        background-color: #3d1214;
        border-left: 5px solid #ff4b4b;
        padding: 12px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .alert-warning {
        background-color: #3b2e10;
        border-left: 5px solid #ffa726;
        color: #f8fafc;
        padding: 12px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .alert-normal {
        background-color: #112d1c;
        border-left: 5px solid #00c853;
        padding: 12px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# DATA ENGINE: HOURLY TELEMETRY, BASELINES & HABITAT SENSORS
# -----------------------------------------------------------------------------
MODULES = ["Destiny Lab", "Harmony Node", "Columbus Module", "Tranquility (Gym)"]

ASTRONAUT_PROFILES = [
    {
        "id": "AST-01",
        "name": "Cmdr. Elena Vance",
        "baseline_condition": "Mild Hypotension (90/60)",
        "module": "Destiny Lab",
        "sys_bp": 92,
        "dia_bp": 61,
        "skin_index": 88,       # 0-100 (100 = optimal)
        "blood_sugar": 94,      # mg/dL
        "rbc_density": 4.3,     # million cells/mcL
        "immune_score": 84,     # 0-100
        "cardio_score": 86,     # 0-100
        "daily_exercise_hrs": 2.1,
        "ai_vision_status": "Normal Activity"
    },
    {
        "id": "AST-02",
        "name": "Dr. Marcus Chen",
        "baseline_condition": "Mild Polycythemia (High RBC Buffer)",
        "module": "Columbus Module",
        "sys_bp": 118,
        "dia_bp": 76,
        "skin_index": 62,       # Lowered due to simulated module humidity/air issue
        "blood_sugar": 102,
        "rbc_density": 5.1,     # Elevated on Earth, buffered into normal in 0G
        "immune_score": 65,
        "cardio_score": 89,
        "daily_exercise_hrs": 2.4,
        "ai_vision_status": "Normal Activity"
    },
    {
        "id": "AST-03",
        "name": "Maj. Tariq Al-Mansoor",
        "baseline_condition": "Mild Mitral Valve Regurgitation",
        "module": "Columbus Module",
        "sys_bp": 112,
        "dia_bp": 72,
        "skin_index": 60,       # Shares anomaly with AST-02 in Columbus Module
        "blood_sugar": 98,
        "rbc_density": 4.1,     # Experiencing space anemia dip
        "immune_score": 64,
        "cardio_score": 78,
        "daily_exercise_hrs": 1.4, # Under daily 2-2.5 hr target
        "ai_vision_status": "Mild Lethargy Detected"
    },
    {
        "id": "AST-04",
        "name": "Dr. Soren Lindqvist",
        "baseline_condition": "Lumbar Disc Compression (Earth)",
        "module": "Tranquility (Gym)",
        "sys_bp": 121,
        "dia_bp": 79,
        "skin_index": 92,
        "blood_sugar": 89,
        "rbc_density": 4.5,
        "immune_score": 91,
        "cardio_score": 94,
        "daily_exercise_hrs": 2.5,
        "ai_vision_status": "Active Strength Training"
    }
]

HABITAT_TELEMETRY = {
    "Destiny Lab": {"O2_pct": 21.0, "CO2_mmHg": 2.1, "Humidity_pct": 45, "Status": "Optimal"},
    "Harmony Node": {"O2_pct": 20.9, "CO2_mmHg": 2.3, "Humidity_pct": 47, "Status": "Optimal"},
    "Columbus Module": {"O2_pct": 20.5, "CO2_mmHg": 4.8, "Humidity_pct": 74, "Status": "Warning (High Humidity / CO2)"},
    "Tranquility (Gym)": {"O2_pct": 21.1, "CO2_mmHg": 2.6, "Humidity_pct": 50, "Status": "Optimal"},
}

def generate_hourly_history(astro):
    """Generates 24 hours of simulated smart-vest telemetry."""
    np.random.seed(sum(ord(c) for c in astro["id"]))
    hours = [(datetime.now() - timedelta(hours=23 - i)).strftime("%H:00") for i in range(24)]
    return pd.DataFrame({
        "Hour": hours,
        "Skin Condition": np.clip(astro["skin_index"] + np.random.normal(0, 2, 24), 40, 100),
        "Blood Sugar (mg/dL)": np.clip(astro["blood_sugar"] + np.random.normal(0, 5, 24), 70, 150),
        "RBC Density (M/mcL)": np.clip(astro["rbc_density"] + np.random.normal(0, 0.08, 24), 3.5, 6.0),
        "Immune Index": np.clip(astro["immune_score"] + np.random.normal(0, 2.5, 24), 40, 100),
        "Cardio Index": np.clip(astro["cardio_score"] + np.random.normal(0, 2, 24), 50, 100),
    })

# -----------------------------------------------------------------------------
# CLINICAL & CONTEXTUAL EVALUATION ENGINE
# -----------------------------------------------------------------------------
def evaluate_astronaut_health(astro, mission_phase, days_remaining, emergency_sim_id):
    """
    Evaluates individual health taking into account:
    1. Location/Gravity phase (suppressing false positives in 0G)
    2. Re-entry countdown priorities
    3. AI Vision behavioral alerts
    """
    alerts = []
    actions = []
    status_color = "Green"  # Green = Optimal, Yellow = Caution, Red = Critical

    # 1. Check AI Camera Emergency Override (e.g., Syncope / Passing Out)
    if emergency_sim_id == astro["id"] or astro["ai_vision_status"] == "CRITICAL: Syncope / Unresponsive":
        status_color = "Red"
        alerts.append(("CRITICAL", f"🚨 AI CAMERA ALERT: {astro['name']} unresponsive / possible syncope in {astro['module']}!"))
        actions.append("DISPATCH CREW IMMEDIATELY to module. Notify Earth Mission Control Flight Surgeon. Initiate emergency medical protocol.")
        return status_color, alerts, actions

    # 2. Microgravity False-Positive Suppression Logic
    if mission_phase == "Orbit (0G)":
        if "Hypotension" in astro["baseline_condition"] and astro["sys_bp"] < 95:
            alerts.append(("NORMAL", f"✅ False-Positive Suppressed: Resting BP {astro['sys_bp']}/{astro['dia_bp']} mmHg is normal in 0G (even fluid distribution)."))
        if "Polycythemia" in astro["baseline_condition"] and astro["rbc_density"] >= 4.8:
            alerts.append(("NORMAL", f"✅ False-Positive Suppressed: Elevated baseline RBC ({astro['rbc_density']} M/mcL) acts as a healthy buffer against 54% 0G hemolysis."))
        if "Regurgitation" in astro["baseline_condition"]:
            alerts.append(("NORMAL", "✅ False-Positive Suppressed: Reduced 0G cardiac afterload relieves mild mitral valve stress."))
        if "Lumbar" in astro["baseline_condition"]:
            alerts.append(("NORMAL", "✅ Spinal decompression in 0G relieving Earth baseline disc compression."))
    else:
        # Earth / Launch / Re-entry Re-calibration
        if "Hypotension" in astro["baseline_condition"] and astro["sys_bp"] < 95:
            status_color = "Red"
            alerts.append(("CRITICAL", f"⚠️ GRAVITY TRANSITION RISK: Baseline hypotension ({astro['sys_bp']}/{astro['dia_bp']} mmHg) poses high fainting risk under {mission_phase} G-forces!"))
            actions.append("Execute pre-entry salt/fluid loading protocol and don lower-body compression garments immediately.")

    # 3. RBC Density & 54% Destruction Countermeasure
    if astro["rbc_density"] < 4.2:
        if status_color != "Red":
            status_color = "Yellow"
        alerts.append(("WARNING", f"🩸 Space Anemia Warning: RBC density at {astro['rbc_density']} M/mcL (0G accelerates RBC destruction by ~54%)."))
        actions.append("Launch 'ARED Velocity Challenge' (interactive resistive game) to spike muscle oxygen demand and stimulate bone marrow RBC production.")

    # 4. Cardiovascular & Core Exercise Check (2 - 2.5 hrs daily)
    if astro["daily_exercise_hrs"] < 2.0 or astro["cardio_score"] < 80:
        if status_color != "Red":
            status_color = "Yellow"
        alerts.append(("WARNING", f"❤️ Cardiac Workload Alert: Only {astro['daily_exercise_hrs']} hrs logged today (Target: 2.0–2.5 hrs). Heart workload drops in 0G, risking atrophy."))
        actions.append("Report to Tranquility (Gym) for 45 mins on T2 Harness Treadmill + CEVIS interval cardio.")

    # 5. Re-Entry Countdown Emphasis
    if days_remaining <= 14:
        actions.append(f"⏳ RE-ENTRY COUNTDOWN ({days_remaining} days left): Prioritize orthostatic tolerance drills, heavy lower-body resistive loads, and Lower Body Negative Pressure (LBNP) conditioning.")

    # 6. AI Behavioral Check
    if "Lethargy" in astro["ai_vision_status"]:
        if status_color == "Green":
            status_color = "Yellow"
        alerts.append(("WARNING", f"👁️ AI Vision Note: {astro['ai_vision_status']} observed in {astro['module']}."))
        actions.append("Perform cognitive reaction check and verify hydration/blood glucose levels.")

    if not actions:
        actions.append("Maintain standard hourly smart-vest telemetry sync and scheduled 2.2 hr daily exercise block.")

    return status_color, alerts, actions

def detect_crew_wide_environmental_issues(df_crew):
    """
    Compares individual health anomalies against shared station modules.
    If >= 2 astronauts in the same module share skin/immune drops, flags habitat issue.
    """
    env_alerts = []
    for module, group in df_crew.groupby("module"):
        if len(group) >= 2:
            low_skin = group[group["skin_index"] < 70]
            low_immune = group[group["immune_score"] < 70]
            if len(low_skin) >= 2 or len(low_immune) >= 2:
                names = ", ".join(group["name"].tolist())
                hab = HABITAT_TELEMETRY[module]
                env_alerts.append(
                    f"🏭 **CREW-WIDE HABITAT CORRELATION ({module}):** Multiple astronauts ({names}) show simultaneous skin irritation and immune dips. "
                    f"Module sensors confirm **{hab['Status']}** (Humidity: {hab['Humidity_pct']}%, CO2: {hab['CO2_mmHg']} mmHg). "
                    f"**Action:** Dispatch environmental maintenance to scrub air/dehumidify {module} rather than treating crew for isolated illness."
                )
    return env_alerts

def create_crew_network(crew_records):
    status_colors = {"Green": "#00c853", "Yellow": "#ffa726", "Red": "#ff4b4b"}
    module_positions = {
        "Destiny Lab": (260, 130),
        "Harmony Node": (900, 130),
        "Columbus Module": (900, 370),
        "Tranquility (Gym)": (260, 370),
    }
    crew_by_module = {module: [] for module in module_positions}
    for astronaut in crew_records:
        crew_by_module[astronaut["module"]].append(astronaut)

    nodes = []
    edges = []

    for module, telemetry in HABITAT_TELEMETRY.items():
        module_id = f"module:{module}"
        is_warning = "Warning" in telemetry["Status"]
        module_x, module_y = module_positions[module]
        nodes.append(Node(
            id=module_id,
            label=module,
            title=(
                f"{module}<br>Status: {telemetry['Status']}"
                f"<br>O2: {telemetry['O2_pct']}% | CO2: {telemetry['CO2_mmHg']} mmHg"
                f"<br>Humidity: {telemetry['Humidity_pct']}%"
            ),
            shape="diamond",
            size=32,
            color={"background": "#ffa726" if is_warning else "#38bdf8", "border": "#e6edf3"},
            x=module_x,
            y=module_y,
        ))

    for module, astronauts in crew_by_module.items():
        module_x, module_y = module_positions[module]
        for index, astronaut in enumerate(astronauts):
            angle = 2 * math.pi * index / max(len(astronauts), 1) - math.pi / 2
            nodes.append(Node(
                id=astronaut["id"],
                label=astronaut["id"],
                title=(
                    f"{astronaut['name']}<br>Status: {astronaut['status_color']}"
                    f"<br>Blood sugar: {astronaut['blood_sugar']} mg/dL"
                    f"<br>Skin index: {astronaut['skin_index']}"
                    f"<br>Active alerts: {len(astronaut['alerts'])}"
                ),
                size=30,
                color={
                    "background": status_colors[astronaut["status_color"]],
                    "border": "#e6edf3",
                },
                x=module_x + 145 * math.cos(angle),
                y=module_y + 65 * math.sin(angle),
            ))
            edges.append(Edge(
                source=astronaut["id"],
                target=f"module:{module}",
                color="#526174",
                width=2,
            ))

    config = Config(
        width=1200,
        height=520,
        directed=False,
        physics=False,
        hierarchical=False,
        interaction={"dragNodes": True, "dragView": True, "zoomView": True, "hover": True},
        nodes={"font": {"color": "#f8fafc", "size": 15}, "borderWidth": 2},
    )
    return agraph(nodes=nodes, edges=edges, config=config)

# -----------------------------------------------------------------------------
# SIDEBAR: MISSION CONTROLS & SIMULATION
# -----------------------------------------------------------------------------
st.sidebar.title("🛰️ AEGIS Mission Control")
st.sidebar.markdown("Hourly Smart-Vest & Station Telemetry")

mission_phase = st.sidebar.selectbox(
    "Current Gravity / Mission Phase",
    ["Orbit (0G)", "Re-entry / Landing (3G–4G)", "Earth Pre-Launch (1G)"],
    index=0
)

total_mission_days = 180
days_elapsed = st.sidebar.slider("Mission Day", 1, total_mission_days, 168)
days_remaining = total_mission_days - days_elapsed

st.sidebar.metric("Countdown to Earth Return", f"{days_remaining} Days", delta=f"Day {days_elapsed} of {total_mission_days}")

st.sidebar.markdown("---")
st.sidebar.subheader("🎥 AI Vision & Emergency Simulator")
emergency_trigger = st.sidebar.selectbox(
    "Simulate AI Camera Event",
    ["None (Nominal Monitoring)", "AST-03: Syncope / Passing Out in Columbus Module"]
)
emergency_sim_id = "AST-03" if "AST-03" in emergency_trigger else None

astronauts_by_id = {astronaut["id"]: astronaut for astronaut in ASTRONAUT_PROFILES}
graph_selection = st.session_state.get("_crew_graph_selection")
last_graph_selection = st.session_state.get("_last_crew_graph_selection")
if graph_selection in astronauts_by_id and graph_selection != last_graph_selection:
    st.session_state["selected_astro_name"] = astronauts_by_id[graph_selection]["name"]
    st.session_state["_last_crew_graph_selection"] = graph_selection

def preserve_sidebar_selection():
    st.session_state["_last_crew_graph_selection"] = st.session_state.get("_crew_graph_selection")

selected_astro_name = st.sidebar.selectbox(
    "Inspect Individual Astronaut",
    [a["name"] for a in ASTRONAUT_PROFILES],
    key="selected_astro_name",
    on_change=preserve_sidebar_selection,
)

st.sidebar.markdown("---")
st.sidebar.markdown("Euphemia Zhang | Iryna Ivanova")

# -----------------------------------------------------------------------------
# MAIN DASHBOARD
# -----------------------------------------------------------------------------
st.title("🛰️ Astronaut Biometric & Habitat Health Monitor")
st.caption(f"Last Hourly Smart-Vest Sync: {datetime.now().strftime('%Y-%m-%d %H:00 UTC')} | Environment Mode: **{mission_phase}**")

# Process all astronauts
crew_records = []
all_alerts = []

for astro in ASTRONAUT_PROFILES:
    color, alerts, actions = evaluate_astronaut_health(astro, mission_phase, days_remaining, emergency_sim_id)
    crew_records.append({
        **astro,
        "status_color": color,
        "alerts": alerts,
        "actions": actions
    })
    for severity, msg in alerts:
        all_alerts.append((severity, astro["name"], msg))

df_crew = pd.DataFrame(crew_records)

# --- TOP BANNER: EMERGENCY & CREW-WIDE ENVIRONMENTAL ALERTS ---
if emergency_sim_id:
    st.markdown(f"""
    <div class="alert-critical">
        <strong>🚨 EMERGENCY PUSH NOTIFICATION SENT TO ALL CREW & EARTH MISSION CONTROL:</strong><br>
        AI Optical Sensor detected sudden loss of posture / syncope for <strong>Maj. Tariq Al-Mansoor</strong> in <strong>Columbus Module</strong>.
        Automated medical bay unlock initiated. Nearest crew member (Dr. Marcus Chen) directed to assist.
    </div>
    """, unsafe_allow_html=True)

env_correlations = detect_crew_wide_environmental_issues(df_crew)
for env_msg in env_correlations:
    st.markdown(f"""
    <div class="alert-warning">
        {env_msg}
    </div>
    """, unsafe_allow_html=True)

# --- ROW 1: DYNAMIC CHARTS (WEB/RADAR, BAR, PIE) ---
st.subheader("📊 Crew-Wide & Individual Health Analytics")
col1, col2, col3 = st.columns([1.2, 1.3, 1.0])

selected_record = next(r for r in crew_records if r["name"] == selected_astro_name)
indicator_scores = {
    "Skin Condition": selected_record["skin_index"],
    "Blood Sugar Stability": max(0, 100 - abs(selected_record["blood_sugar"] - 95)),
    "RBC Density": min(100, (selected_record["rbc_density"] / 5.0) * 100),
    "Immune Resilience": selected_record["immune_score"],
    "Cardiovascular": selected_record["cardio_score"],
}

# 1. WEB (RADAR) CHART: Color-coded 5-indicator snapshot
with col1:
    categories = ["Skin Condition", "Blood Sugar Stability", "RBC Density", "Immune Resilience", "Cardiovascular"]
    # Normalize metrics to 0-100 scale for radar chart
    bs_score = max(0, 100 - abs(selected_record["blood_sugar"] - 95))
    rbc_score = min(100, (selected_record["rbc_density"] / 5.0) * 100)
    values = [
        selected_record["skin_index"],
        bs_score,
        rbc_score,
        selected_record["immune_score"],
        selected_record["cardio_score"]
    ]

    radar_color = "#00c853" if selected_record["status_color"] == "Green" else ("#ffa726" if selected_record["status_color"] == "Yellow" else "#ff4b4b")

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor=radar_color,
        opacity=0.45,
        line=dict(color=radar_color, width=3),
        name=selected_record["name"]
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        title=f"5-Axis Health Web: {selected_record['name'].split()[1]}",
        height=350,
        margin=dict(l=40, r=40, t=50, b=30)
    )
    st.plotly_chart(fig_radar, use_container_width=True)

# 2. BAR CHART: Selected astronaut's health indicators
with col2:
    bar_df = pd.DataFrame({
        "Indicator": list(indicator_scores.keys()),
        "Score": list(indicator_scores.values()),
    })
    fig_bar = px.bar(
        bar_df,
        x="Indicator",
        y="Score",
        color="Indicator",
        title=f"Health Indicators: {selected_record['name']}",
        color_discrete_sequence=["#38bdf8", "#a78bfa", "#34d399", "#f87171", "#fbbf24"]
    )
    fig_bar.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=50, b=30),
        yaxis_range=[0, 110],
        showlegend=False,
        xaxis_title=None,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# 3. PIE CHART: Selected astronaut's indicator status distribution
with col3:
    indicator_status = pd.Series(indicator_scores).map(
        lambda score: "Optimal" if score >= 85 else ("Caution" if score >= 65 else "Critical")
    )
    status_counts = (
        indicator_status.value_counts()
        .reindex(["Optimal", "Caution", "Critical"], fill_value=0)
        .rename_axis("Status")
        .reset_index(name="Count")
    )
    label_map = {"Optimal": "Optimal (Green)", "Caution": "Caution (Amber)", "Critical": "Critical (Red)"}
    color_map = {"Optimal (Green)": "#00c853", "Caution (Amber)": "#ffa726", "Critical (Red)": "#ff4b4b"}
    status_counts["Label"] = status_counts["Status"].map(label_map)

    fig_pie = px.pie(
        status_counts,
        names="Label",
        values="Count",
        hole=0.45,
        color="Label",
        color_discrete_map=color_map,
        title=f"Indicator Status: {selected_record['name']}"
    )
    fig_pie.update_layout(height=350, margin=dict(l=20, r=20, t=50, b=30))
    st.plotly_chart(fig_pie, use_container_width=True)

# --- ROW 2: INDIVIDUAL DEEP-DIVE, LOCATION-AWARE DIAGNOSTICS & GAMIFIED EXERCISE ---
st.markdown("---")
st.subheader(f"🧑‍🚀 Detailed Diagnostics & Action Plan: {selected_record['name']}")

d_col1, d_col2 = st.columns([1.1, 1.2])

with d_col1:
    st.markdown(f"**Current Station Location:** 📍 `{selected_record['module']}`")
    st.markdown(f"**Earth Medical Baseline:** `{selected_record['baseline_condition']}`")
    st.markdown(f"**AI Optical Behavior Feed:** 🎥 `{selected_record['ai_vision_status']}`")
    st.markdown(f"**Daily Exercise Logged:** 🏋️ `{selected_record['daily_exercise_hrs']} hrs` / `2.5 hrs target`")

    st.markdown("#### 🔍 Context-Aware Diagnostic Alerts")
    for severity, msg in selected_record["alerts"]:
        css_class = "alert-critical" if severity == "CRITICAL" else ("alert-warning" if severity == "WARNING" else "alert-normal")
        st.markdown(f'<div class="{css_class}">{msg}</div>', unsafe_allow_html=True)

    st.markdown("#### 📋 Prescribed Astronaut Actions")
    for idx, act in enumerate(selected_record["actions"], 1):
        st.info(f"**Action {idx}:** {act}")

with d_col2:
    st.markdown("#### 📈 24-Hour Smart-Vest Telemetry Trend")
    hist_df = generate_hourly_history(selected_record)
    metric_choice = st.selectbox(
        "Select Hourly Telemetry Stream",
        ["RBC Density (M/mcL)", "Cardio Index", "Skin Condition", "Immune Index", "Blood Sugar (mg/dL)"]
    )
    fig_line = px.line(
        hist_df,
        x="Hour",
        y=metric_choice,
        markers=True,
        title=f"Hourly {metric_choice} — {selected_record['name']}"
    )
    fig_line.update_traces(line_color="#38bdf8", line_width=3)
    fig_line.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_line, use_container_width=True)

    # Interactive Gamified Exercise Module for RBC & Cardio Protection
    with st.expander("🎮 Interactive Muscle & Cardio Training Module (Counter 54% RBC Loss)", expanded=True):
        st.write(
            "Microgravity accelerates red blood cell destruction by **54%** and reduces cardiac workload. "
            "Complete high-intensity resistive games to spike muscle oxygen demand and stimulate bone marrow."
        )
        g_col1, g_col2 = st.columns(2)
        with g_col1:
            if st.button("🏋️ Start ARED Resistive Gravity Game (+0.3 hr)"):
                st.success("Session logged! Muscle oxygen demand spiked—erythropoietin (EPO) bone marrow stimulus active.")
        with g_col2:
            if st.button("🏃 Start T2 Harness Sprint Interval (+0.5 hr)"):
                st.success("Cardio interval complete! Cardiac output and vascular elasticity reinforced.")

# --- CREW & HABITAT NETWORK ---
st.markdown("---")
st.subheader("🕸️ Crew & Habitat Network")
st.caption("Click an astronaut node to inspect them. Drag nodes to rearrange the network; scroll to zoom and drag empty space to pan. Node colors show health status.")
graph_selection = create_crew_network(crew_records)
if graph_selection in astronauts_by_id and graph_selection != st.session_state.get("_crew_graph_selection"):
    st.session_state["_crew_graph_selection"] = graph_selection
    st.rerun()

# --- ROW 3: STATION HABITAT MODULE OVERVIEW ---
st.markdown("---")
st.subheader("🛸 Station Module Location & Environmental Matrix")
hab_rows = []
for mod, data in HABITAT_TELEMETRY.items():
    occupants = [r["name"] for r in crew_records if r["module"] == mod]
    hab_rows.append({
        "Module": mod,
        "Occupants": ", ".join(occupants) if occupants else "Unoccupied",
        "O2 (%)": data["O2_pct"],
        "CO2 (mmHg)": data["CO2_mmHg"],
        "Humidity (%)": data["Humidity_pct"],
        "Environment Status": data["Status"]
    })
st.dataframe(pd.DataFrame(hab_rows), use_container_width=True, hide_index=True)