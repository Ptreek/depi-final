import sqlite3

DB_PATH = "hospital.db"
KEEP_ID = "P001"

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Delete everything for other patients from predictions & alerts first
c.execute("DELETE FROM predictions WHERE patient_id != ?", (KEEP_ID,))
c.execute("DELETE FROM alerts WHERE patient_id != ?", (KEEP_ID,))

# Delete vitals of other patients
c.execute("DELETE FROM vitals WHERE patient_id != ?", (KEEP_ID,))

# Delete other patients themselves
c.execute("DELETE FROM patients WHERE patient_id != ?", (KEEP_ID,))

conn.commit()
conn.close()

print("✅ Cleaned database: only P001 remains in patients, vitals, predictions, and alerts.")
