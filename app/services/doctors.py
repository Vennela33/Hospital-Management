from sqlalchemy.orm import Session,joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException,Depends
from app import models
from app.dependencies import verify_token
from sqlalchemy import func

def create_doctor(db: Session, data,user):
    if user["role"]!="admin":
        raise HTTPException(status_code=403,detail="Only admin can Create")
    existing = db.query(models.Doctor).filter(models.Doctor.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    doctor = models.Doctor(**data.dict(),created_by=user.get("sub"),updated_by=user.get("sub"))
    db.add(doctor)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already exists")
    db.refresh(doctor)
    return doctor


def get_doctor(db: Session, doctor_id: int):
    doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


def get_doctors(db, specialization=None, is_active=None,page: int=1, limit:int=10):
    query = db.query(models.Doctor)

    if specialization:
        query = query.filter(models.Doctor.specialization.ilike(f"%{specialization}%"))

    if is_active is not None:
        query = query.filter(models.Doctor.is_active == is_active)
    
    offset=(page-1)*limit
    return query.offset(offset).limit(limit).all()


def get_doctors_with_patients(db: Session):
    return db.query(models.Doctor).options(joinedload(models.Doctor.patients)).all()


def update_doctor_full(db: Session, doctor_id: int, data,user):
    if user["role"]!="admin":
        raise HTTPException(status_code=403,detail="Only admin can update")
    doctor = get_doctor(db, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    doctor.name = data.name
    doctor.specialization = data.specialization
    doctor.email = data.email
    doctor.is_active = data.is_active
    doctor.updates_by=user.get("sub")
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_Code=400, detail="Email already exists")
    db.refresh(doctor)
    return doctor



def update_doctor_partial(db, doctor_id, data,user):
    if user["role"]!="admin":
        raise HTTPException(status_code=403,detail="Only admin can update")
    doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(doctor, key, value)
    doctor.updated_by=user.get("sub")
    db.commit()
    db.refresh(doctor)
    return doctor



def delete_doctor(db: Session, doctor_id: int):
    doctor = get_doctor(db, doctor_id)
    doctor.is_active = False
    db.commit()

    return {"message": "Doctor deactivated successfully"}




def paginate(query, page: int, limit: int):
    total = query.count()
    data = query.offset((page - 1) * limit).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": data
    }



def test_create_doctor():
    response = client.post("/doctors", json={...})
    assert response.status_code == 200


def get_patients(db):
    return db.query(models.Patient).options(
        joinedload(models.Patient.doctor)
    ).all()