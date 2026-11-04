
import sys
from typing import Any

import httpx

BASE_URL = "http://localhost:8000/api/v1"
PASSWORD = "Demo@12345"
TIMEOUT = 60.0

results: list[tuple[str, bool, str]] = []


# --------------------------------------------------
# TEST REPORT
# --------------------------------------------------

def record(name: str, passed: bool, detail: str = ""):
    results.append((name, passed, detail))

    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}")

    if detail:
        print(f"       {detail}")


# --------------------------------------------------
# AUTHENTICATION
# --------------------------------------------------

def login(
    client: httpx.Client,
    username: str,
    tenant_code: str,
) -> dict[str, str]:

    response = client.post(
        "/auth/login",
        json={
            "tenant_code": tenant_code,
            "username": username,
            "password": PASSWORD,
        },
    )

    response.raise_for_status()

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


# --------------------------------------------------
# AI REQUEST
# --------------------------------------------------

def ask_ai(
    client: httpx.Client,
    auth_headers: dict[str, str],
    question: str,
) -> dict[str, Any]:

    response = client.post(
        "/ai/query",
        headers=auth_headers,
        json={"question": question},
    )

    response.raise_for_status()

    return response.json()


def number(value: Any) -> float:
    return float(value or 0)


# --------------------------------------------------
# QUESTION TEST RUNNER
# --------------------------------------------------

def run_question(
    client: httpx.Client,
    auth_headers: dict[str, str],
    question_number: int,
    category: str,
    question: str,
    expected_tool: str,
    expected_type: str,
):

    test_name = f"Q{question_number:02d} [{category}] {question}"

    try:
        data = ask_ai(
            client,
            auth_headers,
            question,
        )

        actual_tool = data.get("tool_used")
        source = data.get("source")

        assert actual_tool == expected_tool, (
            f"Expected {expected_tool}, got {actual_tool}"
        )

        assert source in ("ollama", "fallback"), (
            f"Unexpected AI source: {source}"
        )

        answer = data.get("answer")

        assert isinstance(answer, str)
        assert answer.strip(), "AI answer is empty"

        result = data.get("data")

        assert result is not None, "Business data missing"

        if expected_type == "list":
            assert isinstance(result, list)

        elif expected_type == "dict":
            assert isinstance(result, dict)

        elif expected_type == "inventory":
            assert isinstance(result, dict)
            assert isinstance(result.get("items"), list)

        record(
            test_name,
            True,
            f"Tool={actual_tool}, Source={source}",
        )

        return data

    except (
        httpx.HTTPError,
        AssertionError,
        KeyError,
        TypeError,
        ValueError,
    ) as exc:

        record(
            test_name,
            False,
            str(exc),
        )

        return None


# --------------------------------------------------
# 50 BUSINESS QUESTIONS
# --------------------------------------------------

QUESTIONS = [

    # 1-8 SALES ANALYTICS

    (
        "Sales",
        "What are the total sales for my company?",
        "dashboard_summary",
        "dict",
    ),
    (
        "Sales",
        "Show me the monthly sales trend.",
        "sales_trend",
        "list",
    ),
    (
        "Sales",
        "Explain the sales performance.",
        "sales_trend",
        "list",
    ),
    (
        "Sales",
        "Show the sales over time.",
        "sales_trend",
        "list",
    ),
    (
        "Sales",
        "Which products have the highest sales quantity?",
        "top_products",
        "list",
    ),
    (
        "Sales",
        "Show the top five selling products.",
        "top_products",
        "list",
    ),
    (
        "Sales",
        "Give me the sales dashboard summary.",
        "dashboard_summary",
        "dict",
    ),
    (
        "Sales",
        "How are our sales performing monthly?",
        "sales_trend",
        "list",
    ),

    # 9-15 PURCHASE ANALYTICS

    (
        "Purchase",
        "What is the total purchase value?",
        "dashboard_summary",
        "dict",
    ),
    (
        "Purchase",
        "Show the top purchasing vendors.",
        "top_vendors",
        "list",
    ),
    (
        "Purchase",
        "Which vendors have the highest purchase value?",
        "top_vendors",
        "list",
    ),
    (
        "Purchase",
        "Show me our purchase summary.",
        "dashboard_summary",
        "dict",
    ),
    (
        "Purchase",
        "Compare sales and purchases for the last 90 days.",
        "sales_purchase_comparison",
        "dict",
    ),
    (
        "Purchase",
        "Are purchases higher than sales?",
        "sales_purchase_comparison",
        "dict",
    ),
    (
        "Purchase",
        "Show the comparison between sales and purchase orders.",
        "sales_purchase_comparison",
        "dict",
    ),

    # 16-23 INVENTORY

    (
        "Inventory",
        "Show current inventory availability.",
        "inventory",
        "inventory",
    ),
    (
        "Inventory",
        "Which products are low in stock?",
        "low_stock",
        "inventory",
    ),
    (
        "Inventory",
        "Find all low stock items.",
        "low_stock",
        "inventory",
    ),
    (
        "Inventory",
        "Which items need replenishment?",
        "low_stock",
        "inventory",
    ),
    (
        "Inventory",
        "Show products and their current stock levels.",
        "inventory",
        "inventory",
    ),
    (
        "Inventory",
        "Show products below their reorder level.",
        "low_stock",
        "inventory",
    ),
    (
        "Inventory",
        "Give me an inventory overview.",
        "inventory",
        "inventory",
    ),
    (
        "Inventory",
        "Which products have available stock?",
        "inventory",
        "inventory",
    ),

    # 24-30 VENDORS

    (
        "Vendors",
        "Show all top vendors.",
        "top_vendors",
        "list",
    ),
    (
        "Vendors",
        "Who are our major suppliers?",
        "top_vendors",
        "list",
    ),
    (
        "Vendors",
        "Find vendors supplying steel in Delhi NCR.",
        "vendor_search",
        "list",
    ),
    (
        "Vendors",
        "Find steel suppliers in Delhi.",
        "vendor_search",
        "list",
    ),
    (
        "Vendors",
        "Search vendors supplying steel in Gurgaon.",
        "vendor_search",
        "list",
    ),
    (
        "Vendors",
        "Show suppliers of steel in Faridabad.",
        "vendor_search",
        "list",
    ),
    (
        "Vendors",
        "Which vendors have supplied the highest value?",
        "top_vendors",
        "list",
    ),

    # 31-35 PRODUCTS AND CUSTOMERS

    (
        "Products",
        "Show our best selling products.",
        "top_products",
        "list",
    ),
    (
        "Products",
        "Which products are most popular?",
        "top_products",
        "list",
    ),
    (
        "Products",
        "Show the top three products.",
        "top_products",
        "list",
    ),
    (
        "Products",
        "Give me the product sales ranking.",
        "top_products",
        "list",
    ),
    (
        "Customers",
        "Show the business summary including customer activity.",
        "dashboard_summary",
        "dict",
    ),

    # 36-40 BUSINESS SUMMARY

    (
        "Dashboard",
        "Give me a complete business summary.",
        "dashboard_summary",
        "dict",
    ),
    (
        "Dashboard",
        "Show the company performance summary.",
        "dashboard_summary",
        "dict",
    ),
    (
        "Dashboard",
        "What is our current business performance?",
        "dashboard_summary",
        "dict",
    ),
    (
        "Dashboard",
        "Summarize our sales and purchase performance.",
        "dashboard_summary",
        "dict",
    ),
    (
        "Dashboard",
        "Show all important business metrics.",
        "dashboard_summary",
        "dict",
    ),

    # 41-45 COMPARISON AND TREND

    (
        "Comparison",
        "Compare sales and purchases over the last 90 days.",
        "sales_purchase_comparison",
        "dict",
    ),
    (
        "Comparison",
        "What is the difference between sales and purchases?",
        "sales_purchase_comparison",
        "dict",
    ),
    (
        "Comparison",
        "Are sales greater than purchases?",
        "sales_purchase_comparison",
        "dict",
    ),
    (
        "Comparison",
        "Explain our monthly revenue trend.",
        "sales_trend",
        "list",
    ),
    (
        "Comparison",
        "Show monthly sales performance and trend.",
        "sales_trend",
        "list",
    ),

    # 46-50 ADDITIONAL BUSINESS QUESTIONS

    (
        "Business",
        "Which products should we reorder?",
        "low_stock",
        "inventory",
    ),
    (
        "Business",
        "Show inventory items that require attention.",
        "low_stock",
        "inventory",
    ),
    (
        "Business",
        "Which vendors are our top suppliers?",
        "top_vendors",
        "list",
    ),
    (
        "Business",
        "Show the highest selling inventory products.",
        "top_products",
        "list",
    ),
    (
        "Business",
        "Give me the overall sales trend.",
        "sales_trend",
        "list",
    ),
]


# --------------------------------------------------
# DASHBOARD ACCURACY
# --------------------------------------------------

def test_dashboard_accuracy(
    client: httpx.Client,
    admin_headers: dict[str, str],
    ai_summary: dict[str, Any] | None,
):

    try:
        assert ai_summary is not None

        response = client.get(
            "/dashboard/summary",
            headers=admin_headers,
        )

        response.raise_for_status()

        dashboard = response.json()
        ai_data = ai_summary["data"]

        assert number(
            ai_data["total_sales"]
        ) == number(
            dashboard["total_sales"]
        )

        assert number(
            ai_data["total_purchase_value"]
        ) == number(
            dashboard["total_purchase_value"]
        )

        record(
            "AI summary matches dashboard",
            True,
            "Sales and purchase totals match.",
        )

    except (
        httpx.HTTPError,
        AssertionError,
        KeyError,
        TypeError,
        ValueError,
    ) as exc:

        record(
            "AI summary matches dashboard",
            False,
            str(exc),
        )


# --------------------------------------------------
# TENANT ISOLATION
# --------------------------------------------------

def test_tenant_isolation(
    client: httpx.Client,
    admin_a: dict[str, str],
    admin_b: dict[str, str],
):

    try:
        response_a = client.get(
            "/dashboard/summary",
            headers=admin_a,
        )

        response_b = client.get(
            "/dashboard/summary",
            headers=admin_b,
        )

        response_a.raise_for_status()
        response_b.raise_for_status()

        sales_a = number(
            response_a.json()["total_sales"]
        )

        sales_b = number(
            response_b.json()["total_sales"]
        )

        assert sales_a != sales_b

        record(
            "Company A and B data separation",
            True,
            f"A={sales_a}, B={sales_b}",
        )

    except (
        httpx.HTTPError,
        AssertionError,
        KeyError,
        TypeError,
        ValueError,
    ) as exc:

        record(
            "Tenant isolation",
            False,
            str(exc),
        )


# --------------------------------------------------
# SECURITY TESTS
# --------------------------------------------------

def test_role_security(
    client: httpx.Client,
    sales_headers: dict[str, str],
):

    try:
        response = client.post(
            "/ai/query",
            headers=sales_headers,
            json={
                "question": "Show me the top vendors."
            },
        )

        assert response.status_code == 403

        record(
            "Sales user restricted from top vendors",
            True,
            "HTTP 403 returned.",
        )

    except (
        httpx.HTTPError,
        AssertionError,
        KeyError,
        TypeError,
        ValueError,
    ) as exc:

        record(
            "Sales role security",
            False,
            str(exc),
        )


def test_unauthenticated_access(
    client: httpx.Client,
):

    try:
        response = client.post(
            "/ai/query",
            json={
                "question": "Show total sales"
            },
        )

        assert response.status_code in (401, 403)

        record(
            "Unauthenticated request rejected",
            True,
            f"HTTP {response.status_code}",
        )

    except (
        httpx.HTTPError,
        AssertionError,
        KeyError,
        TypeError,
        ValueError,
    ) as exc:

        record(
            "Authentication security",
            False,
            str(exc),
        )


def test_tenant_override_rejected(
    client: httpx.Client,
    admin_headers: dict[str, str],
):

    try:
        response = client.post(
            "/ai/query",
            headers=admin_headers,
            json={
                "question": "Show inventory",
                "tenant_id": 2,
            },
        )

        assert response.status_code == 422

        record(
            "Client cannot override tenant ID",
            True,
            "Unexpected tenant field rejected.",
        )

    except (
        httpx.HTTPError,
        AssertionError,
        KeyError,
        TypeError,
        ValueError,
    ) as exc:

        record(
            "Tenant override security",
            False,
            str(exc),
        )


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    print("\n========== ERP AI 50 QUESTION TEST ==========\n")

    try:
        with httpx.Client(
            base_url=BASE_URL,
            timeout=TIMEOUT,
        ) as client:

            admin_a = login(
                client,
                "admin_a",
                "COMPANY_A",
            )

            admin_b = login(
                client,
                "admin_b",
                "COMPANY_B",
            )

            sales_a = login(
                client,
                "sales_a",
                "COMPANY_A",
            )

            print(
                f"Total business questions: {len(QUESTIONS)}\n"
            )

            ai_summary = None

            for index, item in enumerate(QUESTIONS, start=1):

                category, question, tool, data_type = item

                result = run_question(
                    client,
                    admin_a,
                    index,
                    category,
                    question,
                    tool,
                    data_type,
                )

                if index == 1:
                    ai_summary = result

            print("\n--- DATA ACCURACY ---\n")

            test_dashboard_accuracy(
                client,
                admin_a,
                ai_summary,
            )

            print("\n--- TENANT ISOLATION ---\n")

            test_tenant_isolation(
                client,
                admin_a,
                admin_b,
            )

            print("\n--- ROLE SECURITY ---\n")

            test_role_security(
                client,
                sales_a,
            )

            print("\n--- AUTHENTICATION SECURITY ---\n")

            test_unauthenticated_access(client)

            test_tenant_override_rejected(
                client,
                admin_a,
            )

    except (
        httpx.HTTPError,
        AssertionError,
        KeyError,
        TypeError,
        ValueError,
    ) as exc:

        record(
            "Test setup / API connection",
            False,
            str(exc),
        )

    print("\n========== FINAL TEST REPORT ==========\n")

    passed = sum(
        1 for _, success, _ in results if success
    )

    failed = len(results) - passed

    print(f"Business questions : {len(QUESTIONS)}")
    print(f"Total tests        : {len(results)}")
    print(f"Passed             : {passed}")
    print(f"Failed             : {failed}")

    if failed:
        print("\nFAILED TESTS:")

        for name, success, detail in results:
            if not success:
                print(f"\n{name}")
                print(f"Reason: {detail}")

    print("\n=======================================\n")

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
