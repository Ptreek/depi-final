# api.py - FINAL VERSION THAT WORKS IMMEDIATELY
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import uvicorn

app = FastAPI(title="Al-Salam Hospital API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    conn = sqlite3.connect("hospital.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/patients")
def get_patients():
    conn = get_db()
    c = conn.cursor()
    
    # THIS QUERY IS THE FIX — always returns latest vital + prediction for each patient
    c.execute("""
        SELECT 
            p.patient_id,
            p.full_name,
            p.sex,
            v.heart_rate_bpm,
            v.temperature_c,
            v.spo2_percent,
            COALESCE(v.health_status, 'NORMAL') as health_status,
            COALESCE(pr.predicted_label, 'Low Risk') as risk_level,
            COALESCE(pr.confidence, 0.0) as confidence
        FROM patients p
        LEFT JOIN (
            SELECT *, ROW_NUMBER() OVER (PARTITION BY patient_id ORDER BY id DESC) as rn
            FROM vitals
        ) v ON p.patient_id = v.patient_id AND v.rn = 1
        LEFT JOIN (
            SELECT *, ROW_NUMBER() OVER (PARTITION BY patient_id ORDER BY id DESC) as rn
            FROM predictions
        ) pr ON p.patient_id = pr.patient_id AND pr.rn = 1
    """)
    
    rows = c.fetchall()
    conn.close()
    
    result = []
    for row in rows:
        result.append({
            "patient_id": row["patient_id"],
            "full_name": row["full_name"],
            "sex": row["sex"],
            "heart_rate_bpm": row["heart_rate_bpm"] or 0,
            "temperature_c": round(row["temperature_c"], 1) if row["temperature_c"] else 0.0,
            "spo2_percent": row["spo2_percent"] or 0,
            "health_status": row["health_status"],
            "risk_level": row["risk_level"],
            "confidence": float(row["confidence"])
        })
    return result

@app.get("/alerts")
def get_alerts():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT a.*, p.full_name
        FROM alerts a
        JOIN patients p ON a.patient_id = p.patient_id
        ORDER BY a.id DESC LIMIT 20
    """)
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

if __name__ == "__main__":
    print("API Server → http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)