import requests

BASE_URL = "http://127.0.0.1:8000"

# Book
print("Booking without doctor...")
res = requests.post(f"{BASE_URL}/appointments", json={
    "patient_name": "Jane Doe",
    "department": "Cardiology",
    "reason": "Chest pain",
    "date": "2023-11-10",
    "doctor": None
})
print(res.status_code, res.text)

# Reschedule
print("Rescheduling without doctor...")
res = requests.put(f"{BASE_URL}/appointments", json={
    "patient_name": "Jane Doe",
    "doctor": "", # frontend sends empty string
    "old_date": "2023-11-10",
    "new_date": "2023-11-12"
})
print(res.status_code, res.text)
