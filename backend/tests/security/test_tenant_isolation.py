from app.security.jwt import create_access_token


def test_company_a_login_returns_company_a_user(client):
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
    assert response.json()["tenant_id"] == 1
    assert response.json()["username"] == "admin_a"


def test_company_b_login_returns_company_b_user(client):
    login = client.post(
        "/api/v1/auth/login",
        json={
            "tenant_code": "COMPANY_B",
            "username": "admin_b",
            "password": "Demo@12345",
        },
    )

    token = login.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["tenant_id"] == 2
    assert response.json()["username"] == "admin_b"


def test_cross_tenant_user_claims_rejected(client):
    # User 1 belongs to tenant 1.
    # A token claiming that user 1 belongs to tenant 2 must be rejected.
    token = create_access_token(
        user_id=1,
        tenant_id=2,
        role="Administrator",
    )

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
