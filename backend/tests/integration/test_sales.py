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


def test_sales_list_returns_tenant_orders(client):
    token = get_token(client, "admin_a")

    response = client.get(
        "/api/v1/sales",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["order_number"] == "SO-A-001"


def test_sales_detail_returns_order_items(client):
    token = get_token(client, "admin_a")

    response = client.get(
        "/api/v1/sales/1",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["order_number"] == "SO-A-001"
    assert len(response.json()["items"]) == 1


def test_sales_user_cannot_access_other_tenant_order(client):
    token = get_token(client, "admin_a")

    response = client.get(
        "/api/v1/sales/2",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404


def test_purchase_user_cannot_access_sales(client):
    token = get_token(client, "purchase_a")

    response = client.get(
        "/api/v1/sales",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
