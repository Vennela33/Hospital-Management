from fastapi import APIRouter, Depends, Query
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import services, schemas
from app.dependencies import verify_token, admin_required, doctor_required
from app import models



router = APIRouter(prefix="/api/v1/doctors",tags=["Doctors"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/",dependencies=[Depends(verify_token)])
def create(data: schemas.DoctorCreate, db: Session = Depends(get_db),user=Depends(verify_token)):
    return services.create_doctor(db, data,user)


@router.get("/",dependencies=[Depends(verify_token)])
def list_doctors(
    specialization: str = Query(None),
    is_active: bool = Query(None),
    page: int = Query(1, gt=0),
    limit: int = Query(5, gt=0),
    db: Session = Depends(get_db)
):
    return services.get_doctors(db, specialization,is_active,page,limit)


@router.get("/{doctor_id}",dependencies=[Depends(verify_token)])
def get(doctor_id: int, db: Session = Depends(get_db)):
    return services.get_doctor(db, doctor_id)


@router.put("/{doctor_id}",dependencies=[Depends(verify_token)])
def update(doctor_id: int, data: schemas.DoctorUpdate, db: Session = Depends(get_db),user=Depends(verify_token)):
    return services.update_doctor_full(db, doctor_id, data,user)


@router.delete("/{doctor_id}",dependencies=[Depends(admin_required)])
def delete(doctor_id: int, db: Session = Depends(get_db)):
    return services.delete_doctor(db, doctor_id)


@router.get("/{doctor_id}/patients",dependencies=[Depends(verify_token)])
def doctor_patients(doctor_id: int, db: Session = Depends(get_db),user=Depends(verify_token)):
    if user['role']!="admin":
        raise HTTPException(status_code=403,detail="Only admin can delete")
    return services.get_patients_by_doctor(db, doctor_id)



@router.patch("/{doctor_id}", status_code=200,dependencies=[Depends(verify_token)])
def update_doctor_partial(
    doctor_id: int,
    data: schemas.DoctorUpdate,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):
    return services.update_doctor_partial(db, doctor_id, data,user)

