from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import services, schemas
from app.dependencies import verify_token, admin_required, doctor_required
from app import models


router = APIRouter(prefix="/appointments", tags=["Appointments"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/appointments", status_code=200, dependencies=[Depends(admin_required)])
def create_appointment(data: schemas.AppointmentCreate, db: Session = Depends(get_db)):
    return services.create_appointment(db, data)


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
    return services.get_appointments(db)

@router.delete("/{appointment_id}",status_code=200,dependencies=[Depends(admin_required)])
def delete(appointment_id: int, db: Session = Depends(get_db)):
    return services.delete_appointment(db, appointment_id)

@router.patch("/{appointment_id}",status_code=200,dependencies=[Depends(admin_required)])
def update(appointment_id: int, data: schemas.AppointmentUpdate, db: Session = Depends(get_db),user=Depends(verify_token)):
    return services.update_appointment(db, appointment_id, data,user)