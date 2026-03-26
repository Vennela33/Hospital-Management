def test_invalid_age(test_client):
    response = test_client.post("/patients", json={
        "name": "John",
        "age": -5,
        "phone": "1234567890",
        "doctor_id": 1
    })

    assert response.status_code == 422