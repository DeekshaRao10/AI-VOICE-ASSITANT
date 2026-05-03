import requests
import json

def test_webhook():
    url = "http://127.0.0.1:8000/webhook"
    
    payload = {
        "message": {
            "type": "end-of-call-report",
            "call": {
                "id": "test-call-123",
                "customer": {"number": "+919876543210"}
            },
            "summary": "Patient booked an appointment for Cardiology on May 5th.",
            "transcript": "Hello, I want to book an appointment... OK confirmed."
        }
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_webhook()
