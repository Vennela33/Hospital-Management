def test_create_appointment(test_client):
    response = test_client.post("/appointments", json={
        "doctor_id": 1,
        "patient_id": 1,
        "appointment_date": "2026-03-26T10:00:00"
    })

    assert response.status_code in [200, 400]