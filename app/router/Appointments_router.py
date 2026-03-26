from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import schemas
from app.dependencies import verify_token, admin_required, doctor_required
from app import models
from app.services import appointments,billing


router = APIRouter(prefix="/appointments", tags=["Appointments"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/appointments", status_code=200, dependencies=[Depends(admin_required)])
def create_appointment(data: schemas.AppointmentCreate, db: Session = Depends(get_db)):
    return appointments.create_appointment(db, data)


@router.get("/doctors/{doctor_id}/appointments", status_code=200,dependencies=[Depends(verify_token)])
def get_doctor_appointments(doctor_id: int, db: Session = Depends(get_db)):
    return db.query(models.Appointment).filter(
        models.Appointment.doctor_id == doctor_id
    ).all()

@router.get("/patients/{patient_id}/appointments", status_code=200,dependencies=[Depends(verify_token)])
def get_patient_appointments(patient_id: int, db: Session = Depends(get_db)):
    return db.query(models.Appointment).filter(
        models.Appointment.patient_id == patient_id
    ).all()

@router.get("/",status_code=200,dependencies=[Depends(verify_token)])
def get_all(db: Session = Depends(get_db)):
    return appointments.get_appointments(db)

@router.delete("/{appointment_id}",status_code=200,dependencies=[Depends(admin_required)])
def delete(appointment_id: int, db: Session = Depends(get_db)):
    return appointments.delete_appointment(db, appointment_id)

@router.patch("/{appointment_id}",status_code=200,dependencies=[Depends(admin_required)])
def update(appointment_id: int, data: schemas.AppointmentUpdate, db: Session = Depends(get_db),user=Depends(verify_token)):
    return appointments.update_appointment(db, appointment_id, data,user)

@router.put("/{appointment_id}")
def update_appointment(
    appointment_id: int,
    data: dict,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admin can update")

    appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    for key, value in data.items():
        setattr(appointment, key, value)

    db.commit()
    db.refresh(appointment)

    return appointment