# dashboard.py - AUTO REFRESH + LIVE DATA
import streamlit as st
import requests
import time

st.set_page_config(page_title="Al-Salam ICU", layout="wide", page_icon="🏥")

REFRESH_SECONDS = 5  # how often to refresh the dashboard

# track previous # of critical patients so we can trigger alarm when it increases
if "last_critical" not in st.session_state:
    st.session_state.last_critical = 0

# everything on the page will live inside this placeholder and be redrawn
placeholder = st.empty()

while True:
    with placeholder.container():
        # -------- TITLE --------
        st.markdown(
            """
            <h1 style='text-align: center; color: #e74c3c;'>Al-Salam International Hospital</h1>
            <h3 style='text-align: center;'>LIVE ICU MONITORING • Updates Every 5 Seconds</h3>
            <hr>
            """,
            unsafe_allow_html=True,
        )

        # -------- LOAD DATA FROM FASTAPI --------
        try:
            patients = requests.get(
                "http://127.0.0.1:8000/patients", timeout=10
            ).json()
            alerts = requests.get(
                "http://127.0.0.1:8000/alerts", timeout=10
            ).json()
        except Exception:
            st.error("Backend not ready yet... (FastAPI API not responding)")
            time.sleep(REFRESH_SECONDS)
            continue

        critical = sum(1 for p in patients if p["health_status"] == "CRITICAL")

        # -------- TOP METRICS --------
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Patients", len(patients))
        col2.metric("Stable", len(patients) - critical)
        col3.metric("CRITICAL", critical if critical else 0)
        col4.metric("Time", time.strftime("%H:%M:%S"))

        # -------- ALARM WHEN NEW CRITICAL PATIENT APPEARS --------
        if critical > st.session_state.last_critical:
            st.session_state.last_critical = critical
            st.markdown(
                """
                <audio autoplay loop>
                    <source src="https://assets.mixkit.co/sfx/preview/mixkit-alarm-digital-clock-beep-989.mp3" type="audio/mp3">
                </audio>
                """,
                unsafe_allow_html=True,
            )

        if critical:
            st.error(f"CRITICAL PATIENTS: {critical}")

        # -------- PATIENT CARDS --------
        for p in patients:
            color = "#e74c3c" if p["health_status"] == "CRITICAL" else "#2ecc71"
            st.markdown(
                f"""
                <div style="background:#1a1a1a; color:white; padding:20px;
                            border-radius:15px; margin:15px 0;
                            border-left:8px solid {color};">
                    <h2>{p['full_name']} • {p['patient_id']}</h2>
                    <h1 style="color:{color}">{p['health_status']} • {p['risk_level']}</h1>
                    <h3>
                        HR: {p['heart_rate_bpm']} |
                        Temp: {p['temperature_c']}°C |
                        SpO2: {p['spo2_percent']}%
                    </h3>
                    <p><b>AI Risk: {p['confidence']:.1%}</b></p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # -------- LATEST AI ALERTS --------
        if alerts:
            st.markdown("### Latest AI Alerts")
            for a in alerts[:5]:
                st.warning(f"**{a['full_name']}** → {a['alert_message']}")

    # wait a bit, then redraw the whole page with fresh data
    time.sleep(REFRESH_SECONDS)
