def test_create_doctor(test_client):
    response = test_client.post("/doctors", json={
        "name": "Dr Ravi",
        "specialization": "Cardiology",
        "email": "ravi@test.com"
    })

    assert response.status_code == 200
    assert response.json()["email"] == "ravi@test.com"

def test_duplicate_email(test_client):
    test_client.post("/doctors", json={
        "name": "Dr A",
        "specialization": "Cardiology",
        "email": "dup@test.com"
    })

    response = test_client.post("/doctors", json={
        "name": "Dr B",
        "specialization": "Cardiology",
        "email": "dup@test.com"
    })

    assert response.status_code == 400