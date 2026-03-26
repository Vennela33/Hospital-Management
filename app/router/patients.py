from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import services, schemas
from app.dependencies import verify_token
from app import models

router = APIRouter(prefix="/api/v1/patients",tags=["Patients"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/",dependencies=[Depends(verify_token)])
def create(data: schemas.PatientCreate, db: Session = Depends(get_db),user=Depends(verify_token)):
    return services.create_patient(db, data,user)


@router.get("/",dependencies=[Depends(verify_token)])
def list_patients(
    age_gt: int = Query(None),
    page: int = Query(1, gt=0),
    limit: int = Query(5, gt=0),
    db: Session = Depends(get_db)
):
    return services.get_patients(db,age_gt, page, limit)


@router.put("/{patient_id}", status_code=200,dependencies=[Depends(verify_token)])
def update_patient_full(
    patient_id: int,
    data: schemas.PatientUpdate,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):
    patient = services.get_patient(db, patient_id)

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    return services.update_patient_full(db, patient_id, data,user)


@router.patch("/{patient_id}", status_code=200,dependencies=[Depends(verify_token)])
def update_patient_partial(
    patient_id: int,
    data: schemas.PatientUpdate,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):
    patient = services.get_patient(db, patient_id)

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    return services.update_patient_partial(db, patient_id, data,user)


@router.delete("/{patient_id}", status_code=200,dependencies=[Depends(verify_token)])
def delete_patient(patient_id: int,db: Session = Depends(get_db)):
    patient = services.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return services.delete_patient(db, patient_id)
