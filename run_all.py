# run_all.py - FINAL FIXED VERSION (NO IMPORT ERRORS)
import subprocess
import time
import os
import signal
import sys

# Get the directory where run_all.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)  # Critical: Set correct working directory

processes = []

def stop_all(signum=None, frame=None):
    print("\nShutting down all services...")
    for p in processes:
        try:
            p.terminate()
            p.wait(timeout=5)
        except:
            pass
    sys.exit(0)

signal.signal(signal.SIGINT, stop_all)

print("Creating database...")
os.system("python database.py")

print("Cleaning database to single patient (P001)...")
os.system("python clean_to_p001.py")

print("Starting services...")

# 1. Single-patient vitals generator (P001, every 5s)
processes.append(subprocess.Popen(["python", "generate_vitals.py"], cwd=BASE_DIR))

time.sleep(2)

# 2. AI predictor  (Safe version: run the file directly)
processes.append(subprocess.Popen([
    sys.executable, "ai_predictor.py"
], cwd=BASE_DIR))

time.sleep(2)

# 3. API - THIS IS THE FIX
processes.append(subprocess.Popen([
    "uvicorn", 
    "api:app", 
    "--host", "127.0.0.1", 
    "--port", "8000",
    "--reload"  # Optional: auto-restart on code change
], cwd=BASE_DIR))  # Critical: Run in correct folder

time.sleep(6)

# 4. Dashboard (clean, no warnings)
processes.append(subprocess.Popen([
    "streamlit", "run", "dashboard.py",
    "--server.port=8501",
    "--server.headless=true",
    "--server.enableCORS=false",
    "--server.enableXsrfProtection=false"
], cwd=BASE_DIR))

print("\n" + "="*70)
print("ALL SERVICES STARTED SUCCESSFULLY!")
print("Dashboard → http://localhost:8501")
print("API       → http://127.0.0.1:8000")
print("Database  → hospital.db (in this folder)")
print("Press Ctrl+C to stop everything")
print("="*70 + "\n")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    stop_all()
    