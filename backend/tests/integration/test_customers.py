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


def test_customer_list_returns_tenant_customers(client):
    token = get_token(client, "admin_a")

    response = client.get(
        "/api/v1/customers",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["name"] == "Customer A"


def test_customer_detail_returns_customer(client):
    token = get_token(client, "admin_a")

    response = client.get(
        "/api/v1/customers/1",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Customer A"


def test_customer_endpoint_blocks_purchase_user(client):
    token = get_token(client, "purchase_a")

    response = client.get(
        "/api/v1/customers",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_customer_endpoint_hides_other_tenant_data(client):
    token = get_token(client, "admin_a")

    response = client.get(
        "/api/v1/customers/2",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
