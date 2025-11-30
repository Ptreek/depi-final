# data_simulator.py - FINAL VERSION THAT ACTUALLY UPDATES DATA
import time
import random
from datetime import datetime, timezone
import sqlite3

print("LIVE VITALS GENERATOR STARTED → 3-second updates")

# Keep connection open forever → NO LOCKS!
conn = sqlite3.connect("hospital.db", check_same_thread=False)
c = conn.cursor()
c.execute("SELECT patient_id FROM patients")
patients = [row[0] for row in c.fetchall()]

while True:
    for pid in patients:
        # 18% chance of critical (you'll see it often!)
        if random.random() < 0.18:
            hr = random.randint(128, 178)
            temp = round(random.uniform(38.9, 41.5), 1)
            spo2 = random.randint(65, 89)
            status = "CRITICAL"
        else:
            hr = random.randint(58, 108)
            temp = round(random.uniform(36.2, 37.8), 1)
            spo2 = random.randint(93, 100)
            status = "NORMAL"

        c.execute("""INSERT INTO vitals 
            (timestamp_utc, patient_id, heart_rate_bpm, temperature_c, spo2_percent, health_status)
            VALUES (?,?,?,?,?,?)""",
            (datetime.now(timezone.utc).isoformat(), pid, hr, temp, spo2, status))

    conn.commit()  # Only commit once per cycle
    print(f"New vitals generated @ {time.strftime('%H:%M:%S')} | Critical: {sum(1 for _ in c.execute('SELECT * FROM vitals WHERE health_status=? ORDER BY id DESC LIMIT 7', ('CRITICAL',)).fetchall())}")
    time.sleep(3)