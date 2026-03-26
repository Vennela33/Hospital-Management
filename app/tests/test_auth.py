def test_login(test_client):
    response = test_client.post("/login?username=admin&password=admin")

    assert response.status_code == 200
    assert "access_token" in response.json()

def test_admin_access(test_client):
    login = test_client.post("/login?username=admin&password=admin")
    token = login.json()["access_token"]

    response = test_client.delete(
        "/doctors/1",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code in [200, 404]

def test_doctor_cannot_delete(test_client):
    login = test_client.post("/login?username=doctor&password=doctor")
    token = login.json()["access_token"]

    response = test_client.delete(
        "/doctors/1",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403