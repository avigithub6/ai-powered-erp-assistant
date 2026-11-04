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


def test_inventory_list_returns_tenant_items(client):
    token = get_token(client, "admin_a")

    response = client.get(
        "/api/v1/inventory",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["sku"] == "SKU-A"


def test_inventory_detail_returns_item(client):
    token = get_token(client, "admin_a")

    response = client.get(
        "/api/v1/inventory/1",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["sku"] == "SKU-A"


def test_inventory_excludes_purchase_price_for_sales_user(client):
    token = get_token(client, "sales_a")

    response = client.get(
        "/api/v1/inventory/1",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert "purchase_price" not in response.json()


def test_inventory_includes_purchase_price_for_purchase_user(client):
    token = get_token(client, "purchase_a")

    response = client.get(
        "/api/v1/inventory/1",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["purchase_price"] == "60.00"


def test_inventory_excludes_other_tenant_item(client):
    token = get_token(client, "admin_a")

    response = client.get(
        "/api/v1/inventory/2",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
