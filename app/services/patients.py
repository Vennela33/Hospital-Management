from sqlalchemy.orm import Session,joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException,Depends
from app import models
from app.dependencies import verify_token
from sqlalchemy import func
from app.services import doctors


def create_patient(db: Session, data,user):
    doctor = db.query(models.Doctor).filter(models.Doctor.id == data.doctor_id).first()
    if user["role"]!="admin":
        raise HTTPException(status_code=403,detail="Only admin can Create")
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    if not doctor.is_active:
        raise HTTPException(status_code=400, detail="Doctor is inactive")

    patient = models.Patient(**data.dict(),created_by=user.get("sub"),updated_by=user.get("sub"))
    db.add(patient)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Duplicate entry")
    db.refresh(patient)
    return patient


def get_patient(db: Session, patient_id: int):
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


def get_patients(db: Session, age_gt=None,page: int=1, limit:int=10):
    query = db.query(models.Patient)
    if age_gt:
        query = query.filter(models.Patient.age == age_gt)
    offset=(page-1)*limit
    return query.offset(offset).limit(limit).all()


def get_patients_by_doctor(db: Session, doctor_id: int,user):
    doctor = doctors.get_doctor(db, doctor_id)
    if not doctor.is_active:
        raise HTTPException(status_code=400, detail="Doctor inactive")
    if user["role"]=="doctor" and user["sub"]!=str(doctor_id):
        raise HTTPException(status_code=403, detail="Not allowed")
    return db.query(models.Patient).filter(models.Patient.doctor_id==doctor_id).all()



def update_patient_full(db: Session, patient_id: int, data,user):
    patient = get_patient(db, patient_id)
    if user["role"]!="admin":
        raise HTTPException(status_code=403,detail="Only admin can Update")
    doctor = doctors.get_doctor(db, data.doctor_id)
    if not doctor.is_active:
        raise HTTPException(status_code=400, detail="Doctor inactive")

    patient.name = data.name
    patient.age = data.age
    patient.phone = data.phone
    patient.doctor_id = data.doctor_id
    patient.updated_by=user.get("sub")
    db.commit()
    db.refresh(patient)
    return patient



def update_patient_partial(db, patient_id, data,user):
    if user["role"]!="admin":
        raise HTTPException(status_code=403,detail="Only admin can Update")
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    update_data = data.dict(exclude_unset=True)
    if "doctor_id" in update_data:
        doctor = db.query(models.Doctor).filter(models.Doctor.id == update_data["doctor_id"]).first()
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
        if not doctor.is_active:
            raise HTTPException(status_code=400, detail="Doctor inactive")
    for key, value in update_data.items():
        setattr(patient, key, value)
    patient.updated_by=user.get("sub")
    db.commit()
    db.refresh(patient)
    return patient



def delete_patient(db: Session, patient_id: int,user=Depends(verify_token)):
    patient = get_patient(db, patient_id)
    if user["role"]!="admin":
        raise HTTPException(status_code=403,detail="Only admin can Delete")
    db.delete(patient)
    db.commit()
    return {"message": "Patient deleted successfully"}