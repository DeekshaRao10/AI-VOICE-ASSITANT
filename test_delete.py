import requests

BASE_URL = "http://127.0.0.1:8000"

def test_delete():
    print("Booking an appointment to delete...")
    payload = {
        "patient_name": "Delete Me",
        "department": "General",
        "reason": "Test delete",
        "date": "2026-01-01"
    }
    requests.post(f"{BASE_URL}/appointments", json=payload)
    
    print("Deleting the appointment...")
    params = {
        "patient_name": "Delete Me",
        "date": "2026-01-01"
    }
    res = requests.delete(f"{BASE_URL}/appointments", params=params)
    print(f"Delete response: {res.status_code}, {res.json()}")

if __name__ == "__main__":
    test_delete()
