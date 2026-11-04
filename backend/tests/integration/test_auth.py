def test_login_success(client, caplog):
    import logging

    with caplog.at_level(logging.INFO):
        response = client.post(
            "/api/v1/auth/login",
            json={
                "tenant_code": "COMPANY_A",
                "username": "admin_a",
                "password": "Demo@12345",
            },
        )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["expires_in"] == 1800
    assert response.json()["access_token"]

    assert "Authentication successful" in caplog.text
    assert "admin_a" not in caplog.text
    assert "Demo@12345" not in caplog.text
    assert response.json()["access_token"] not in caplog.text


def test_login_invalid_password(client, caplog):
    import logging

    with caplog.at_level(logging.WARNING):
        response = client.post(
            "/api/v1/auth/login",
            json={
                "tenant_code": "COMPANY_A",
                "username": "admin_a",
                "password": "WrongPassword",
            },
        )

    assert response.status_code == 401
    assert "Authentication failed" in caplog.text
    assert "admin_a" in caplog.text
    assert "WrongPassword" not in caplog.text


def test_profile_requires_authentication(client):
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_profile_returns_authenticated_user(client):
    login = client.post(
        "/api/v1/auth/login",
        json={
            "tenant_code": "COMPANY_A",
            "username": "admin_a",
            "password": "Demo@12345",
        },
    )

    token = login.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["username"] == "admin_a"
    assert response.json()["tenant_id"] == 1