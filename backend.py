# ✅ Step 1: Import DB
from database import init_db, Appointment, Conversation, get_db
init_db()

# ✅ Step 2: Imports
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import BaseModel

# ✅ Step 3: App
app = FastAPI(title="D.O.R.A AI Backend")


# =========================
# 🧠 TRIAGE LOGIC
# =========================
def detect_priority(reason: str):
    urgent_keywords = ["chest pain", "breathing", "bleeding", "accident"]
    for word in urgent_keywords:
        if word in reason.lower():
            return "HIGH"
    return "NORMAL"


# =========================
# 📦 SCHEMAS
# =========================

# BOOK
class BookAppointmentRequest(BaseModel):
    patient_name: str
    department: str
    reason: str
    date: str
    doctor: str | None = None


# LOG
class LogRequest(BaseModel):
    patient_name: str
    transcript: str


# RESCHEDULE
class RescheduleRequest(BaseModel):
    patient_name: str
    doctor: str
    old_date: str
    new_date: str


# =========================
# 🚀 APIs
# =========================

# ✅ 1. BOOK APPOINTMENT
@app.post("/appointments")
def book_appointment(request: BookAppointmentRequest, db: Session = Depends(get_db)):
    priority = detect_priority(request.reason)

    doctor = request.doctor if request.doctor else "Auto-assigned"

    appointment = Appointment(
        patient_name=request.patient_name,
        department=request.department,
        reason=request.reason,
        doctor=doctor,
        date=request.date,
        priority=priority
    )

    db.add(appointment)
    db.commit()

    return {
        "message": "Appointment booked successfully",
        "doctor": doctor,
        "priority": priority
    }


# ✅ 2. CHECK AVAILABILITY (GET)
@app.get("/availability")
def check_availability(
    doctor: str | None = Query(default=None),
    department: str | None = Query(default=None),
    date: str | None = Query(default=None)
):
    if doctor:
        return {
            "doctor": doctor,
            "available_slots": ["10 AM", "2 PM", "4 PM"]
        }

    return {
        "department": department,
        "available_doctors": ["Dr. A", "Dr. B"],
        "available_slots": ["11 AM", "1 PM", "3 PM"]
    }


# ✅ 3. LOG CONVERSATION
@app.post("/conversations")
def log_conversation(request: LogRequest, db: Session = Depends(get_db)):
    convo = Conversation(
        patient_name=request.patient_name,
        transcript=request.transcript
    )

    db.add(convo)
    db.commit()

    return {"message": "Conversation stored"}


# ✅ 4. CANCEL APPOINTMENT (DELETE)
@app.delete("/appointments")
def cancel_appointment(
    patient_name: str,
    doctor: str,
    date: str,
    db: Session = Depends(get_db)
):
    result = db.execute(
        select(Appointment).where(
            Appointment.patient_name == patient_name,
            Appointment.doctor == doctor,
            Appointment.date == date
        )
    )

    appointment = result.scalars().first()

    if not appointment:
        raise HTTPException(status_code=404, detail="No appointment found")

    db.delete(appointment)
    db.commit()

    return {"message": "Appointment cancelled"}


# ✅ 5. RESCHEDULE APPOINTMENT (PUT)
@app.put("/appointments")
def reschedule_appointment(request: RescheduleRequest, db: Session = Depends(get_db)):
    result = db.execute(
        select(Appointment).where(
            Appointment.patient_name == request.patient_name,
            Appointment.doctor == request.doctor,
            Appointment.date == request.old_date
        )
    )

    appointment = result.scalars().first()

    if not appointment:
        raise HTTPException(status_code=404, detail="No appointment found")

    appointment.date = request.new_date
    db.commit()

    return {"message": "Appointment rescheduled"}


# =========================
# ▶️ RUN SERVER
# =========================
import uvicorn

if __name__ == "__main__":
    uvicorn.run("backend:app", host="127.0.0.1", port=8000, reload=True)