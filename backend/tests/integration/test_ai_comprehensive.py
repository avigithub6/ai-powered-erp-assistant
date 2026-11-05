
import httpx
import pytest
from app.ai.llm.ollama_client import OllamaClient
from app.ai.tools.schemas import StructuredIntent
from pydantic import ValidationError


def get_token(client, username, tenant_code="COMPANY_A"):
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


def headers(client, username="admin_a", tenant_code="COMPANY_A"):
    token = get_token(client, username, tenant_code)
    return {"Authorization": f"Bearer {token}"}


def mock_tool(monkeypatch, tool, limit=5):
    async def understand_intent(self, question):
        return StructuredIntent(
            request_type="erp",
            tool=tool,
            arguments={"limit": limit},
        )

    async def generate_answer(self, question, tool, data):
        return "Mocked ERP answer based on authorized data."

    monkeypatch.setattr(
        OllamaClient,
        "understand_intent",
        understand_intent,
    )
    monkeypatch.setattr(
        OllamaClient,
        "generate_answer",
        generate_answer,
    )


def test_ai_top_products_returns_database_results(client, monkeypatch):
    mock_tool(monkeypatch, "top_products")

    response = client.post(
        "/api/v1/ai/query",
        headers=headers(client),
        json={"question": "Show top products"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["tool_used"] == "top_products"
    assert data["source"] == "ollama"
    assert data["data"]
    assert data["data"][0]["item_name"] == "Product A"
    assert data["data"][0]["total_quantity_sold"] == 2


def test_ai_top_vendors_returns_database_results(client, monkeypatch):
    mock_tool(monkeypatch, "top_vendors")

    response = client.post(
        "/api/v1/ai/query",
        headers=headers(client),
        json={"question": "Show top vendors"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["tool_used"] == "top_vendors"
    assert data["data"]
    assert data["data"][0]["vendor_name"] == "Vendor A"
    assert float(data["data"][0]["total_purchase_value"]) == 120.0


def test_ai_sales_trend_returns_monthly_data(client, monkeypatch):
    mock_tool(monkeypatch, "sales_trend")

    response = client.post(
        "/api/v1/ai/query",
        headers=headers(client),
        json={"question": "Show monthly sales trend"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["tool_used"] == "sales_trend"
    assert isinstance(data["data"], list)
    assert data["data"]
    assert "month" in data["data"][0]
    assert float(data["data"][0]["total_sales"]) == 200.0


def test_ai_sales_purchase_comparison_returns_both_values(
    client, monkeypatch
):
    mock_tool(monkeypatch, "sales_purchase_comparison")

    response = client.post(
        "/api/v1/ai/query",
        headers=headers(client),
        json={"question": "Compare sales and purchases"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["tool_used"] == "sales_purchase_comparison"
    assert float(data["data"]["sales_total"]) == 200.0
    assert float(data["data"]["purchase_total"]) == 120.0


def test_ai_vendor_search_uses_tenant_data(client, monkeypatch):
    mock_tool(monkeypatch, "vendor_search")

    response = client.post(
        "/api/v1/ai/query",
        headers=headers(client),
        json={"question": "Find steel vendors in Delhi NCR"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["tool_used"] == "vendor_search"
    assert isinstance(data["data"], list)


def test_ai_management_can_access_sales_and_purchase_summary(
    client, monkeypatch
):
    mock_tool(monkeypatch, "dashboard_summary")

    response = client.post(
        "/api/v1/ai/query",
        headers=headers(client, "manager_a"),
        json={"question": "Show business summary"},
    )

    assert response.status_code == 200
    data = response.json()["data"]

    assert float(data["total_sales"]) == 200.0
    assert float(data["total_purchase_value"]) == 120.0


def test_ai_purchase_user_can_access_top_vendors(client, monkeypatch):
    mock_tool(monkeypatch, "top_vendors")

    response = client.post(
        "/api/v1/ai/query",
        headers=headers(client, "purchase_a"),
        json={"question": "Show top vendors"},
    )

    assert response.status_code == 200
    assert response.json()["tool_used"] == "top_vendors"


def test_ai_sales_user_can_access_top_products(client, monkeypatch):
    mock_tool(monkeypatch, "top_products")

    response = client.post(
        "/api/v1/ai/query",
        headers=headers(client, "sales_a"),
        json={"question": "Show top products"},
    )

    assert response.status_code == 200
    assert response.json()["tool_used"] == "top_products"


def test_ai_purchase_user_cannot_access_sales_purchase_comparison(
    client, monkeypatch
):
    mock_tool(monkeypatch, "sales_purchase_comparison")

    response = client.post(
        "/api/v1/ai/query",
        headers=headers(client, "purchase_a"),
        json={"question": "Compare sales and purchases"},
    )

    assert response.status_code == 403


def test_ai_sales_user_cannot_access_sales_purchase_comparison(
    client, monkeypatch
):
    mock_tool(monkeypatch, "sales_purchase_comparison")

    response = client.post(
        "/api/v1/ai/query",
        headers=headers(client, "sales_a"),
        json={"question": "Compare sales and purchases"},
    )

    assert response.status_code == 403


def test_ai_company_b_cannot_receive_company_a_inventory(
    client, monkeypatch
):
    mock_tool(monkeypatch, "inventory")

    response = client.post(
        "/api/v1/ai/query",
        headers=headers(client, "admin_b", "COMPANY_B"),
        json={"question": "Show inventory"},
    )

    assert response.status_code == 200

    items = response.json()["data"]["items"]

    assert items
    assert all(item["item_name"] == "Product B" for item in items)
    assert all(item["item_name"] != "Product A" for item in items)


def test_ai_client_cannot_override_tenant_id(client, monkeypatch):
    mock_tool(monkeypatch, "inventory")

    response = client.post(
        "/api/v1/ai/query",
        headers=headers(client, "admin_a"),
        json={
            "question": "Show inventory",
            "tenant_id": 2,
        },
    )

    assert response.status_code == 422


def test_ai_rejects_question_shorter_than_minimum(client):
    response = client.post(
        "/api/v1/ai/query",
        headers=headers(client),
        json={"question": "a"},
    )

    assert response.status_code == 422


def test_ai_rejects_question_longer_than_maximum(client):
    response = client.post(
        "/api/v1/ai/query",
        headers=headers(client),
        json={"question": "x" * 1001},
    )

    assert response.status_code == 422


def test_ai_rejects_extra_request_fields(client):
    response = client.post(
        "/api/v1/ai/query",
        headers=headers(client),
        json={
            "question": "Show inventory",
            "sql": "SELECT * FROM users",
        },
    )

    assert response.status_code == 422


def test_ai_rejects_invalid_tool_limit():
    with pytest.raises(ValidationError):
        StructuredIntent(
            request_type="erp",
            tool="top_products",
            arguments={"limit": 100},
        )

    with pytest.raises(ValidationError):
        StructuredIntent(
            request_type="erp",
            tool="top_products",
            arguments={"limit": 0},
        )


def test_ai_rejects_unapproved_tool():
    with pytest.raises(ValidationError):
        StructuredIntent(
            request_type="erp",
            tool="execute_sql",
            arguments={"limit": 5},
        )


def test_ai_rejects_extra_tool_arguments():
    with pytest.raises(ValidationError):
        StructuredIntent.model_validate({
            "request_type": "erp",
            "tool": "inventory",
            "arguments": {
                "limit": 5,
                "tenant_id": 2,
            },
        })


def test_ai_unsupported_question_returns_safe_response(
    client, monkeypatch
):
    async def classify_out_of_scope(self, question):
        return StructuredIntent(
            request_type="out_of_scope",
            tool=None,
            intent="general_question",
        )

    monkeypatch.setattr(
        OllamaClient,
        "understand_intent",
        classify_out_of_scope,
    )

    response = client.post(
        "/api/v1/ai/query",
        headers=headers(client),
        json={"question": "Tell me a joke"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["tool_used"] is None
    assert data["source"] == "guardrail"
    assert "erp-related questions" in data["answer"].lower()
    assert data["data"] is None


def test_ai_answer_generation_failure_uses_safe_fallback(
    client, monkeypatch
):
    async def understand_intent(self, question):
        return StructuredIntent(
            request_type="erp",
            tool="top_products",
            arguments={"limit": 5},
        )

    async def unavailable_answer(self, question, tool, data):
        raise httpx.ConnectError("Ollama unavailable")

    monkeypatch.setattr(
        OllamaClient,
        "understand_intent",
        understand_intent,
    )
    monkeypatch.setattr(
        OllamaClient,
        "generate_answer",
        unavailable_answer,
    )

    response = client.post(
        "/api/v1/ai/query",
        headers=headers(client),
        json={"question": "Show top products"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["source"] == "fallback"
    assert data["tool_used"] == "top_products"
    assert data["data"]


def test_ai_inventory_does_not_leak_confidential_fields(
    client, monkeypatch
):
    mock_tool(monkeypatch, "inventory")

    response = client.post(
        "/api/v1/ai/query",
        headers=headers(client, "sales_a"),
        json={"question": "Show inventory"},
    )

    assert response.status_code == 200

    items = response.json()["data"]["items"]
    assert items

    for item in items:
        assert "purchase_price" not in item
        assert "vendor_name" not in item
        assert "tenant_id" not in item
        assert "unit_cost" not in item


def test_ai_dashboard_matches_dashboard_api(client, monkeypatch):
    mock_tool(monkeypatch, "dashboard_summary")

    ai_response = client.post(
        "/api/v1/ai/query",
        headers=headers(client),
        json={"question": "Show dashboard summary"},
    )

    dashboard_response = client.get(
        "/api/v1/dashboard/summary",
        headers=headers(client),
    )

    assert ai_response.status_code == 200
    assert dashboard_response.status_code == 200

    ai_data = ai_response.json()["data"]
    dashboard_data = dashboard_response.json()

    assert float(ai_data["total_sales"]) == float(
        dashboard_data["total_sales"]
    )
    assert float(ai_data["total_purchase_value"]) == float(
        dashboard_data["total_purchase_value"]
    )
