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


def test_vendor_list_returns_tenant_vendors(client):
    token = get_token(client, "admin_a")

    response = client.get(
        "/api/v1/vendors",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["vendor_name"] == "Vendor A"


def test_vendor_detail_returns_vendor(client):
    token = get_token(client, "admin_a")

    response = client.get(
        "/api/v1/vendors/1",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["vendor_name"] == "Vendor A"


def test_vendor_endpoint_blocks_sales_user(client):
    token = get_token(client, "sales_a")

    response = client.get(
        "/api/v1/vendors",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_vendor_endpoint_hides_other_tenant_data(client):
    token = get_token(client, "admin_a")

    response = client.get(
        "/api/v1/vendors/2",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
