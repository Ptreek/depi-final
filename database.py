# database.py
import sqlite3
from datetime import datetime

conn = sqlite3.connect("hospital.db")
c = conn.cursor()

c.executescript("""
DROP TABLE IF EXISTS alerts;
DROP TABLE IF EXISTS predictions;
DROP TABLE IF EXISTS vitals;
DROP TABLE IF EXISTS patients;

CREATE TABLE patients (
    patient_id TEXT PRIMARY KEY,
    full_name TEXT,
    dob TEXT,
    sex TEXT,
    location TEXT,
    chronic_disease TEXT,
    medication TEXT,
    severity TEXT,
    notes TEXT
);

CREATE TABLE vitals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp_utc TEXT,
    patient_id TEXT,
    device_id TEXT,
    heart_rate_bpm INTEGER,
    temperature_c REAL,
    spo2_percent INTEGER,
    systolic_bp INTEGER,
    diastolic_bp INTEGER,
    rr INTEGER,
    raw_payload TEXT,
    health_status TEXT
);

CREATE TABLE predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp_utc TEXT,
    patient_id TEXT,
    model_name TEXT,
    prediction_json TEXT,
    predicted_label TEXT,
    confidence REAL,
    vitals_id INTEGER
);

CREATE TABLE alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp_utc TEXT,
    patient_id TEXT,
    alert_type TEXT,
    alert_message TEXT,
    vitals_id INTEGER,
    handled INTEGER DEFAULT 0
);
""")

patients = [
    ('P001', 'Ahmed Mostafa', '1985-04-15', 'Male', 'Cairo', 'Hypertension', 'Lisinopril 10mg', 'Moderate', ''),
    ('P002', 'Sara Ali', '1990-09-10', 'Female', 'Alexandria', 'Diabetes', 'Metformin 500mg', 'Mild', ''),
    ('P003', 'Mahmoud Hassan', '1978-06-20', 'Male', 'Giza', 'Asthma', 'Salbutamol', 'Mild', ''),
    ('P004', 'Fatma Youssef', '1965-12-01', 'Female', 'Tanta', 'Heart Disease', 'Aspirin', 'Severe', ''),
    ('P005', 'Omar Khaled', '1995-07-08', 'Male', 'Mansoura', 'Obesity', 'Diet', 'Mild', ''),
    ('P006', 'Nour Adel', '1988-03-27', 'Female', 'Suez', 'None', 'None', 'Healthy', ''),
    ('P007', 'Hassan Ibrahim', '1970-11-11', 'Male', 'Aswan', 'COPD', 'Inhaler', 'Moderate', ''),
]
c.executemany("INSERT INTO patients VALUES (?,?,?,?,?,?,?,?,?)", patients)

now = datetime.utcnow().isoformat()
vitals_sample = [
    (now, 'P001', 'DEV1', 82, 36.9, 97, 125, 85, 16, '{}', 'Stable'),
    (now, 'P002', 'DEV2', 90, 37.2, 95, 130, 88, 18, '{}', 'Warning'),
]
c.executemany("INSERT INTO vitals VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?)", vitals_sample)

conn.commit()
conn.close()
print("hospital.db created with 7 real patients")
