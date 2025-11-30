import sqlite3
import time
import random
from datetime import datetime, timezone
import json

DB_PATH = "hospital.db"
PATIENT_ID = "P001"
DEVICE_ID = "DEV_P001"

def get_connection():
    # keep simple single-thread connection
    return sqlite3.connect(DB_PATH)

def generate_vitals_sample():
    """
    Generate mostly stable vitals for P001 with
    occasional 'episode' spikes so AI can still detect risk.
    """

    # 90% of the time → normal stable readings
    if random.random() < 0.9:
        heart_rate = random.randint(78, 90)                 # bpm
        temperature = round(random.uniform(36.7, 37.3), 1)  # °C
        spo2 = random.randint(95, 99)                       # %
        systolic_bp = random.randint(115, 130)              # mmHg
        diastolic_bp = random.randint(75, 85)               # mmHg
        rr = random.randint(14, 18)                         # breaths/min
    else:
        # 10% of the time → simulated worsening episode
        heart_rate = random.randint(120, 160)
        temperature = round(random.uniform(38.5, 40.2), 1)
        spo2 = random.randint(82, 92)
        systolic_bp = random.randint(130, 160)
        diastolic_bp = random.randint(85, 100)
        rr = random.randint(22, 32)

    return {
        "heart_rate_bpm": heart_rate,
        "temperature_c": temperature,
        "spo2_percent": spo2,
        "systolic_bp": systolic_bp,
        "diastolic_bp": diastolic_bp,
        "rr": rr,
    }

def classify_status(v):
    """
    Simple rule-based label used by your system (NORMAL / WARNING / CRITICAL).
    """
    hr = v["heart_rate_bpm"]
    temp = v["temperature_c"]
    spo2 = v["spo2_percent"]

    if hr > 130 or temp >= 39.0 or spo2 < 90:
        return "CRITICAL"
    elif hr > 110 or temp >= 38.0 or spo2 < 94:
        return "WARNING"
    else:
        return "NORMAL"

def insert_one_reading(conn):
    c = conn.cursor()
    vitals = generate_vitals_sample()
    status = classify_status(vitals)
    ts = datetime.now(timezone.utc).isoformat()

    raw_payload = json.dumps(vitals)

    c.execute("""
        INSERT INTO vitals (
            timestamp_utc,
            patient_id,
            device_id,
            heart_rate_bpm,
            temperature_c,
            spo2_percent,
            systolic_bp,
            diastolic_bp,
            rr,
            raw_payload,
            health_status
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, (
        ts,
        PATIENT_ID,
        DEVICE_ID,
        vitals["heart_rate_bpm"],
        vitals["temperature_c"],
        vitals["spo2_percent"],
        vitals["systolic_bp"],
        vitals["diastolic_bp"],
        vitals["rr"],
        raw_payload,
        status
    ))

    conn.commit()
    print(f"[{ts}] P001 → {vitals} | Status: {status}")

def main():
    print("✅ Single-patient vitals generator started (P001, every 5 seconds)...")
    conn = get_connection()

    try:
        while True:
            insert_one_reading(conn)
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n⏹ Stopped by user.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
