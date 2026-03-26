# Hospital API

A simple REST API built using FastAPI to manage Doctors and Patients.

#  Hospital Management API (FastAPI)

A complete backend system built using **FastAPI** for managing Doctors, Patients, Appointments, and Billing with advanced features like authentication, reporting, and transactions.

---

## Features

###  Doctor Management

* Create, update, delete (soft delete)
* Unique email validation
* Filter by specialization and status

###  Patient Management

* Assign patients to doctors
* Age and phone validation
* CRUD operations

###  Appointment Management

* Schedule appointments
* Prevent overlapping appointments
* Track appointment status

###  Billing System

* Generate billing linked to doctor, patient, appointment
* Auto-calculate total amount
* Prevent duplicate billing
* Soft delete support

### Reports & Analytics

* Revenue reports
* Filter by:

  * Doctor
  * Patient
  * Payment status
  * Date range
* Revenue per doctor
* Revenue per day

###  Authentication & Authorization

* JWT-based authentication
* Role-based access:

  * Admin → Full access
  * Doctor → Limited access

###  Advanced Features

* Pagination
* Filtering
* Database transactions (commit/rollback)
* Data integrity & constraints
* Global exception handling

---

## 🛠 Tech Stack

* **Python 3.9+**
* **FastAPI**
* **SQLAlchemy**
* **SQLite**
* **Pydantic**
* **Uvicorn**
* **JWT Authentication**
* **Pytest (Testing)**

---

##  Project Structure

```
app/
│
├── main.py
├── models.py
├── schemas.py
├── services.py
├── database.py
├── auth.py
│
├── routes/
│   ├── doctors.py
│   ├── patients.py
│   ├── appointments.py
│   ├── billings.py
│   ├── reports.py
│
tests/
│
├── test_doctor.py
├── test_patient.py
├── test_auth.py
├── test_appointment.py
```

---

## Installation & Setup

###  Clone the Repository

```
git clone https://github.com/yourusername/hospital-management-api.git
cd hospital-management-api
```

---

###  Create Virtual Environment

```
python -m venv venv
```

Activate:

```
venv\Scripts\activate
```

---

###  Install Dependencies

```
pip install -r requirements.txt
```

---

###  Run Server

```
uvicorn app.main:app --reload
```

---

##  API Documentation

Open Swagger UI:

```
http://127.0.0.1:8000/docs
```

---

##  Authentication

* Login to get JWT token
* Use token in Swagger (Authorize button)

Example:

```
Bearer <your_token>
```

---

##  Example APIs

###  Create Doctor

```
POST /doctors
```

---

###  Create Patient

```
POST /patients
```

---

###  Create Billing

```
POST /billings
```

---

###  Revenue Report

```
GET /reports/revenue?doctor_id=1&from=2026-01-01&to=2026-03-01
```

---

##  Sample Billing Request

```json
{
  "patient_id": 1,
  "doctor_id": 1,
  "appointment_id": 1,
  "consultation_fee": 500,
  "additional_charges": 100,
  "payment_mode": "cash"
}
```

---

##  Running Tests

```
pytest
```

---

## 📈 Coverage

```
pytest --cov=app
```

---

##  Business Rules Implemented

* Doctor must exist and be active
* Patient must exist
* Appointment must match doctor & patient
* Prevent duplicate billing
* Prevent billing for cancelled appointments
* Auto-calculate total amount

---

##  Transactions

* Billing creation + appointment update handled in one transaction
* Rollback on failure to maintain consistency

---

##  Key Concepts Used

* REST API Design
* Dependency Injection
* ORM (SQLAlchemy)
* JWT Authentication
* Role-Based Access Control
* Pagination & Filtering
* Database Transactions
* API Documentation (Swagger)

---

##  Author

**Vennela**

---

##  Notes

* This project is built for learning and demonstration purposes
* Can be extended with:

  * Docker
  * Deployment (AWS/Render)
  * CI/CD pipelines

---

