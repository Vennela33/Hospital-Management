from sqlalchemy.orm import Session,joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException,Depends
from app import models
from app.dependencies import verify_token
from sqlalchemy import func
from app.services import doctors, patients


def create_appointment(db, data):
    doctor = doctors.get_doctor(db, data.doctor_id)
    if not doctor.is_active:
        raise HTTPException(status_code=400, detail="Doctor inactive")
    patient = patients.get_patient(db, data.patient_id)
    existing = db.query(models.Appointment).filter(
        models.Appointment.doctor_id == data.doctor_id,
        models.Appointment.appointment_date == data.appointment_date,
        models.Appointment.status!="cancelled"
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Slot already booked")
    appointment = models.Appointment(**data.dict())
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


def get_appointments(db):
    return db.query(models.Appointment).all()


def get_appointment(db, appointment_id):
    appointment = db.query(models.Appointment).filter(
        models.Appointment.id == appointment_id
    ).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment


def update_appointment(db, appointment_id, data,user):
    if user['role']!='admin':
        raise HTTPException(status_code=403,detail="Only admin can update")
    appointment = get_appointment(db, appointment_id)
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(appointment, key, value)
    db.commit()
    db.refresh(appointment)
    return appointment


def delete_appointment(db, appointment_id):
    appointment = get_appointment(db, appointment_id)
    db.delete(appointment)
    db.commit()
    return {"message": "Appointment deleted"}
