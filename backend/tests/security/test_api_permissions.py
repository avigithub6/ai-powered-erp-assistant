def get_token(client, username):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "tenant_code": "COMPANY_A",
            "username": username,
            "password": "Demo@12345",
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def headers(client, username):
    return {"Authorization": f"Bearer {get_token(client, username)}"}


def test_sales_executive_cannot_access_purchases(client):
    response = client.get(
        "/api/v1/purchases",
        headers=headers(client, "sales_a"),
    )
    assert response.status_code == 403


def test_sales_executive_cannot_access_vendors(client):
    response = client.get(
        "/api/v1/vendors",
        headers=headers(client, "sales_a"),
    )
    assert response.status_code == 403


def test_purchase_executive_cannot_access_sales(client):
    response = client.get(
        "/api/v1/sales",
        headers=headers(client, "purchase_a"),
    )
    assert response.status_code == 403


def test_purchase_executive_cannot_access_customers(client):
    response = client.get(
        "/api/v1/customers",
        headers=headers(client, "purchase_a"),
    )
    assert response.status_code == 403


def test_administrator_can_access_sales_and_purchases(client):
    auth = headers(client, "admin_a")

    sales_response = client.get("/api/v1/sales", headers=auth)
    purchases_response = client.get("/api/v1/purchases", headers=auth)

    assert sales_response.status_code == 200
    assert purchases_response.status_code == 200


def test_management_can_access_sales_and_purchase_analytics(client):
    auth = headers(client, "manager_a")

    sales_response = client.get(
        "/api/v1/dashboard/sales-trend",
        headers=auth,
    )
    purchase_response = client.get(
        "/api/v1/dashboard/top-vendors",
        headers=auth,
    )

    assert sales_response.status_code == 200
    assert purchase_response.status_code == 200
