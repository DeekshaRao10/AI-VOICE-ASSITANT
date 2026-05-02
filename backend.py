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
def detect_priority(reason: str | None):
    if not reason:
        return "NORMAL"
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
    patient_name: str | None = "Unknown"
    department: str | None = "General"
    reason: str | None = "Not specified"
    date: str | None = "TBD"
    doctor: str | None = None


# LOG
class LogRequest(BaseModel):
    patient_name: str | None = "Unknown"
    transcript: str | None = ""


# RESCHEDULE
class RescheduleRequest(BaseModel):
    patient_name: str
    doctor: str | None = None
    old_date: str
    new_date: str

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    date: str,
    doctor: str | None = None,
    db: Session = Depends(get_db)
):
    query = select(Appointment).where(
        Appointment.patient_name == patient_name,
        Appointment.date == date
    )
    if doctor:
        query = query.where(Appointment.doctor == doctor)
        
    result = db.execute(query)

    appointment = result.scalars().first()

    if not appointment:
        raise HTTPException(status_code=404, detail="No appointment found")

    db.delete(appointment)
    db.commit()

    return {"message": "Appointment cancelled"}


# ✅ 5. RESCHEDULE APPOINTMENT (PUT)

@app.put("/appointments")
def reschedule_appointment(request: RescheduleRequest, db: Session = Depends(get_db)):
    query = select(Appointment).where(
        Appointment.patient_name.ilike(request.patient_name.strip()),
        Appointment.date == request.old_date.strip()
    )

    if request.doctor and request.doctor.strip():
        query = query.where(Appointment.doctor == request.doctor.strip())

    result = db.execute(query)
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