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


def test_sales_inventory_contains_only_approved_fields(client):
    response = client.get(
        "/api/v1/inventory",
        headers=headers(client, "sales_a"),
    )

    assert response.status_code == 200
    item = response.json()["items"][0]

    expected_fields = {
        "id",
        "item_name",
        "sku",
        "category",
        "stock_level",
        "reorder_level",
        "selling_price",
        "unit",
    }

    assert set(item.keys()) == expected_fields
    assert "purchase_price" not in item


def test_purchase_inventory_includes_purchase_price(client):
    response = client.get(
        "/api/v1/inventory",
        headers=headers(client, "purchase_a"),
    )

    assert response.status_code == 200
    item = response.json()["items"][0]

    assert "purchase_price" in item
    assert item["purchase_price"] == "60.00"


def test_dashboard_inventory_does_not_expose_purchase_price(client):
    response = client.get(
        "/api/v1/dashboard/inventory",
        headers=headers(client, "admin_a"),
    )

    assert response.status_code == 200

    item = response.json()["items"][0]

    expected_fields = {
        "id",
        "item_name",
        "sku",
        "stock_level",
        "reorder_level",
        "unit",
    }

    assert set(item.keys()) == expected_fields
    assert "purchase_price" not in item


def test_sales_user_dashboard_does_not_expose_purchase_total(client):
    response = client.get(
        "/api/v1/dashboard/summary",
        headers=headers(client, "sales_a"),
    )

    assert response.status_code == 200
    assert response.json()["total_purchase_value"] is None


def test_purchase_user_dashboard_does_not_expose_sales_total(client):
    response = client.get(
        "/api/v1/dashboard/summary",
        headers=headers(client, "purchase_a"),
    )

    assert response.status_code == 200
    assert response.json()["total_sales"] is None
    assert response.json()["sales_order_count"] == 0
