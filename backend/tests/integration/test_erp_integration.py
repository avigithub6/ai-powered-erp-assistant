from datetime import UTC, datetime

import pytest


def get_token(client, tenant_code, username):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "tenant_code": tenant_code,
            "username": username,
            "password": "Demo@12345",
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def mock_spring_boot_client(monkeypatch, captured_tenants):
    async def fake_get_sales_orders(
        self,
        tenant_id,
        limit=20,
        offset=0,
    ):
        captured_tenants.append(tenant_id)

        company = "A" if tenant_id == 1 else "B"

        return {
            "items": [
                {
                    "id": tenant_id,
                    "order_number": f"SO-{company}-001",
                    "status": "COMPLETED",
                    "total_amount": "2500.00",
                    "order_date": datetime.now(UTC).isoformat(),
                }
            ],
            "total": 1,
            "limit": limit,
            "offset": offset,
        }

    monkeypatch.setattr(
        "app.api.v1.erp_integration.SpringBootERPClient.get_sales_orders",
        fake_get_sales_orders,
    )


@pytest.mark.parametrize(
    ("tenant_code", "username", "expected_tenant_id", "expected_order"),
    [
        ("COMPANY_A", "admin_a", 1, "SO-A-001"),
        ("COMPANY_B", "admin_b", 2, "SO-B-001"),
    ],
)
def test_integrated_sales_orders_are_tenant_isolated(
    client,
    monkeypatch,
    tenant_code,
    username,
    expected_tenant_id,
    expected_order,
):
    captured_tenants = []
    mock_spring_boot_client(monkeypatch, captured_tenants)

    token = get_token(client, tenant_code, username)

    response = client.get(
        "/api/v1/erp-integration/sales/orders?limit=5&offset=0",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert captured_tenants == [expected_tenant_id]
    assert response.json()["items"][0]["order_number"] == expected_order


def test_company_a_cannot_override_tenant_id(
    client,
    monkeypatch,
):
    captured_tenants = []
    mock_spring_boot_client(monkeypatch, captured_tenants)

    token = get_token(client, "COMPANY_A", "admin_a")

    response = client.get(
        "/api/v1/erp-integration/sales/orders?tenant_id=2",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert captured_tenants == [1]
    assert response.json()["items"][0]["order_number"] == "SO-A-001"


def test_purchase_user_cannot_access_integrated_sales(
    client,
    monkeypatch,
):
    captured_tenants = []
    mock_spring_boot_client(monkeypatch, captured_tenants)

    token = get_token(client, "COMPANY_A", "purchase_a")

    response = client.get(
        "/api/v1/erp-integration/sales/orders",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert captured_tenants == []
