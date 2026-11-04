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


def auth_headers(client, username="admin_a"):
    token = get_token(client, username)
    return {"Authorization": f"Bearer {token}"}


def test_dashboard_summary_returns_tenant_metrics(client):
    response = client.get(
        "/api/v1/dashboard/summary",
        headers=auth_headers(client),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_sales"] == "200.00"
    assert data["total_purchase_value"] == "120.00"
    assert data["sales_order_count"] == 1
    assert data["inventory_item_count"] == 1
    assert data["low_stock_count"] == 1


def test_sales_user_cannot_see_purchase_total(client):
    response = client.get(
        "/api/v1/dashboard/summary",
        headers=auth_headers(client, "sales_a"),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_sales"] == "200.00"
    assert data["total_purchase_value"] is None


def test_purchase_user_cannot_see_sales_total(client):
    response = client.get(
        "/api/v1/dashboard/summary",
        headers=auth_headers(client, "purchase_a"),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_sales"] is None
    assert data["sales_order_count"] == 0
    assert data["total_purchase_value"] == "120.00"


def test_sales_trend_returns_completed_sales(client):
    response = client.get(
        "/api/v1/dashboard/sales-trend",
        headers=auth_headers(client),
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["total_sales"] == "200.00"
    assert len(data[0]["month"]) == 7


def test_top_products_returns_sold_products(client):
    response = client.get(
        "/api/v1/dashboard/top-products",
        headers=auth_headers(client),
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["item_name"] == "Product A"
    assert data[0]["sku"] == "SKU-A"
    assert data[0]["total_quantity_sold"] == 2


def test_top_vendors_returns_purchase_values(client):
    response = client.get(
        "/api/v1/dashboard/top-vendors",
        headers=auth_headers(client),
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["vendor_name"] == "Vendor A"
    assert data[0]["total_purchase_value"] == "120.00"


def test_dashboard_inventory_is_tenant_scoped(client):
    response = client.get(
        "/api/v1/dashboard/inventory",
        headers=auth_headers(client),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["item_name"] == "Product A"
    assert data["items"][0]["sku"] == "SKU-A"
    assert "purchase_price" not in data["items"][0]


def test_dashboard_low_stock_returns_items_at_reorder_level(client):
    response = client.get(
        "/api/v1/dashboard/low-stock",
        headers=auth_headers(client),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["stock_level"] == 5
    assert data["items"][0]["reorder_level"] == 10


def test_sales_user_cannot_access_top_vendors(client):
    response = client.get(
        "/api/v1/dashboard/top-vendors",
        headers=auth_headers(client, "sales_a"),
    )

    assert response.status_code == 403


def test_purchase_user_cannot_access_sales_trend(client):
    response = client.get(
        "/api/v1/dashboard/sales-trend",
        headers=auth_headers(client, "purchase_a"),
    )

    assert response.status_code == 403
