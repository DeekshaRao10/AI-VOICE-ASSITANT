import requests
import sqlite3
import time

BASE_URL = "http://127.0.0.1:8000"

def test_endpoints():
    print("Testing /appointments (POST)...")
    payload_app = {
        "patient_name": "Test Patient",
        "department": "Cardiology",
        "reason": "Chest pain",
        "date": "2026-06-01",
        "doctor": "Dr. Test"
    }
    try:
        res = requests.post(f"{BASE_URL}/appointments", json=payload_app)
        print(f"Response: {res.status_code}, {res.json()}")
    except Exception as e:
        print(f"Error calling /appointments: {e}")

    print("\nTesting /conversations (POST)...")
    payload_conv = {
        "patient_name": "Test Patient",
        "transcript": "Hello, I want to book an appointment for chest pain."
    }
    try:
        res = requests.post(f"{BASE_URL}/conversations", json=payload_conv)
        print(f"Response: {res.status_code}, {res.json()}")
    except Exception as e:
        print(f"Error calling /conversations: {e}")

    print("\nTesting /appointments (PUT)...")
    payload_resched = {
        "patient_name": "Test Patient",
        "doctor": "Dr. Test",
        "old_date": "2026-06-01",
        "new_date": "2026-06-02"
    }
    try:
        res = requests.put(f"{BASE_URL}/appointments", json=payload_resched)
        print(f"Response: {res.status_code}, {res.json()}")
    except Exception as e:
        print(f"Error calling /appointments (PUT): {e}")

    print("\nChecking database...")
    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM appointments WHERE patient_name='Test Patient'")
    apps = cursor.fetchall()
    print(f"Appointments for Test Patient: {apps}")
    
    cursor.execute("SELECT * FROM conversations WHERE patient_name='Test Patient'")
    convs = cursor.fetchall()
    print(f"Conversations for Test Patient: {convs}")
    
    conn.close()

if __name__ == "__main__":
    test_endpoints()
