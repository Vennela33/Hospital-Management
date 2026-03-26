from pydantic import BaseModel, EmailStr, Field
import re
from datetime import datetime


class DoctorBase(BaseModel):
    name: str
    specialization: str
    email: EmailStr
    is_active: bool = True
class DoctorCreate(DoctorBase):
    pass


class DoctorUpdate(BaseModel):
    name: str | None = None
    specialization: str | None = None
    email: EmailStr | None = None
    is_active: bool | None = None

class DoctorResponse(BaseModel):
    id:int
    is_active:bool
    class Config:
        from_attributes=True



class PatientBase(BaseModel):
    name: str
    age: int = Field(..., gt=0)
    phone: str
    doctor_id: int
    @classmethod
    def validate_phone(cls,v):
        if not re.fullmatch(r"\d{10}",phone):
            raise ValueError("Phone must be exactly 10 digits")
        return v


class PatientCreate(PatientBase):
    doctor_id:int


class PatientUpdate(BaseModel):
    name: str | None = None
    age: int | None = None
    phone: str | None = None
    doctor_id: int | None = None

class PatientResponse(PatientBase):
    id:int
    doctor_id:int

    class Config:
        from_attributes=True


class AppointmentCreate(BaseModel):
    doctor_id:int
    patient_id:int
    appointment_date:datetime


class AppointmentUpdate(BaseModel):
    appointment_date:datetime=None
    status:str=None


class AppointmentResponse(BaseModel):
    id:int
    doctor_id:int
    patient_id:int
    appointment_date:datetime
    status:str

    class config:
        from_attributes=True


class BillingCreate(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_id: int | None = None
    consultation_fee: float
    additional_charges: float = 0
    payment_mode: str


class BillingUpdate(BaseModel):
    consultation_fee: float | None = None
    additional_charges: float | None = None
    payment_status: str | None = None


class BillingResponse(BaseModel):
    id: int
    total_amount: float
    payment_status: str

    class Config:
        from_attributes = True