
import httpx
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError

from app.ai.llm.ollama_client import OllamaClient
from app.ai.tools.executor import ToolExecutor
from app.ai.tools.schemas import ToolSelection
from app.models import User
from app.schemas.ai import AIQueryResponse


def fallback_tool(question: str) -> ToolSelection | None:
    text = " ".join(
        question.lower().replace("-", " ").split()
    )

    # 1. Vendor search
    if (
        "steel" in text
        and any(
            word in text
            for word in [
                "vendor",
                "vendors",
                "supplier",
                "suppliers",
                "delhi",
                "ncr",
                "gurugram",
                "gurgaon",
                "faridabad",
                "noida",
            ]
        )
    ):
        tool = "vendor_search"

    # 2. Low stock and replenishment
    elif any(
        phrase in text
        for phrase in [
            "low stock",
            "stock alert",
            "stock below",
            "below reorder",
            "reorder",
            "replenish",
            "replenishment",
            "need attention",
            "needs attention",
            "require attention",
            "requires attention",
            "inventory alert",
            "items to restock",
            "products to restock",
        ]
    ):
        tool = "low_stock"

    # 3. Explicit sales and purchase comparison
    elif (
        any(
            phrase in text
            for phrase in [
                "compare",
                "comparison",
                "versus",
                " vs ",
                "difference between",
                "higher than",
                "greater than",
                "lower than",
                "less than",
            ]
        )
        and any(
            word in text
            for word in ["sales", "sale", "revenue"]
        )
        and any(
            word in text
            for word in [
                "purchase",
                "purchases",
                "procurement",
            ]
        )
    ):
        tool = "sales_purchase_comparison"

    # 4. Monthly sales trends
    elif any(
        phrase in text
        for phrase in [
            "sales trend",
            "monthly sales",
            "monthly revenue",
            "revenue trend",
            "sales over time",
            "sales performance",
            "sales performing monthly",
            "sales performance over time",
            "overall sales trend",
            "monthly sales performance",
        ]
    ):
        tool = "sales_trend"

    # 5. Vendor rankings
    elif any(
        phrase in text
        for phrase in [
            "top vendor",
            "top vendors",
            "best vendor",
            "best vendors",
            "vendor ranking",
            "top supplier",
            "top suppliers",
            "best supplier",
            "best suppliers",
            "major supplier",
            "major suppliers",
            "highest purchase value",
            "highest value vendors",
            "highest value suppliers",
            "highest purchasing vendors",
        ]
    ):
        tool = "top_vendors"

    # 6. Best-selling products
    elif any(
        phrase in text
        for phrase in [
            "top product",
            "top products",
            "best selling",
            "best-selling",
            "most sold",
            "most popular products",
            "highest selling",
            "highest sales quantity",
            "product sales ranking",
            "selling products",
        ]
    ):
        tool = "top_products"

    # 7. General inventory
    elif any(
        phrase in text
        for phrase in [
            "inventory",
            "stock level",
            "stock levels",
            "available stock",
            "available items",
            "inventory availability",
            "item details",
            "current stock",
        ]
    ):
        tool = "inventory"

    # 8. General business summary
    elif any(
        phrase in text
        for phrase in [
            "dashboard",
            "summary",
            "summarize",
            "overview",
            "business status",
            "business performance",
            "total sales",
            "total sale",
            "total revenue",
            "total purchase",
            "total procurement",
            "purchase value",
            "purchase summary",
            "sales summary",
            "customer activity",
            "important business metrics",
            "overall business",
            "company performance",
        ]
    ):
        tool = "dashboard_summary"

    else:
        return None

    return ToolSelection(
        tool=tool,
        arguments={"limit": 5},
    )


def format_answer(tool: str, data: dict | list) -> str:
    if tool == "dashboard_summary":
        parts = []

        if data.get("total_sales") is not None:
            parts.append(f"Total sales: {data['total_sales']}")

        if data.get("total_purchase_value") is not None:
            parts.append(
                f"Total purchases: {data['total_purchase_value']}"
            )

        parts.extend(
            [
                f"Completed sales orders: {data['sales_order_count']}",
                f"Inventory items: {data['inventory_item_count']}",
                f"Low-stock items: {data['low_stock_count']}",
            ]
        )

        return "Dashboard summary: " + "; ".join(parts) + "."

    if tool == "sales_purchase_comparison":
        if not data:
            return "No sales and purchase comparison data is available."

        return (
            f"Last {data['period_days']} days comparison "
            f"({data['start_date']} to {data['end_date']}): "
            f"Completed sales value: {data['sales_total']}; "
            f"completed purchase value: {data['purchase_total']}; "
            f"sales orders: {data['sales_order_count']}; "
            f"purchase orders: {data['purchase_order_count']}."
        )

    if tool == "vendor_search":
        if not data:
            return "No steel vendors were found in Delhi NCR."

        lines = [
            (
                f"{item['vendor_name']} "
                f"(Address: {item['address']}): "
                f"Supplied products: {item['supplied_products']}"
            )
            for item in data
        ]

        return (
            "Steel vendors found in Delhi NCR: "
            + "; ".join(lines)
            + "."
        )

    if tool == "sales_trend":
        if not data:
            return (
                "Insufficient data: no completed sales trend data "
                "is available."
            )

        lines = [
            f"{item['month']}: {item['total_sales']}"
            for item in data
        ]

        answer = "Monthly sales trend: " + "; ".join(lines) + "."

        if len(data) < 2:
            return (
                answer
                + " Insufficient data to identify an increase or decrease. "
                + "Possible reasons cannot be confirmed from one month "
                + "of sales data."
            )

        first_sales = float(data[0]["total_sales"])
        last_sales = float(data[-1]["total_sales"])

        if first_sales == 0:
            return (
                answer
                + " Percentage change cannot be calculated because "
                + "the first month's sales were zero. "
                + "Possible reasons cannot be confirmed from sales "
                + "figures alone."
            )

        percentage_change = (
            (last_sales - first_sales) / first_sales
        ) * 100

        if percentage_change > 0:
            trend = "increased"
        elif percentage_change < 0:
            trend = "decreased"
        else:
            trend = "remained unchanged"

        return (
            answer
            + f" Sales {trend} by {abs(percentage_change):.2f}% "
            + f"from {data[0]['month']} to {data[-1]['month']}. "
            + "Possible reasons cannot be confirmed from sales "
            + "figures alone; pricing, demand, stock availability, "
            + "and marketing data would be needed."
        )

    if tool == "top_products":
        if not data:
            return "No completed sales product data is available."

        lines = [
            (
                f"{item['item_name']} "
                f"(SKU: {item['sku']}): "
                f"{item['total_quantity_sold']} units sold"
            )
            for item in data
        ]

        return "Top-selling products: " + "; ".join(lines) + "."

    if tool == "top_vendors":
        if not data:
            return "No completed purchase vendor data is available."

        lines = [
            (
                f"{item['vendor_name']}: "
                f"{item['total_purchase_value']}"
            )
            for item in data
        ]

        return (
            "Top vendors by completed purchase value: "
            + "; ".join(lines)
            + "."
        )

    if tool in {"inventory", "low_stock"}:
        items = data["items"]

        if not items:
            if tool == "low_stock":
                return "There are currently no low-stock inventory items."

            return "No inventory items were found."

        lines = [
            (
                f"{item['item_name']} "
                f"(SKU: {item['sku']}): "
                f"stock {item['stock_level']} {item['unit']}, "
                f"reorder level {item['reorder_level']}"
            )
            for item in items
        ]

        if tool == "low_stock":
            return (
                f"Found {data['total']} low-stock items: "
                + "; ".join(lines)
                + "."
            )

        return (
            f"Found {data['total']} inventory items: "
            + "; ".join(lines)
            + "."
        )

    return "I could not prepare an answer for this request."


class AIOrchestrator:
    def __init__(self):
        self.ollama_client = OllamaClient()

    async def query(self, question: str, current_user: User, db):
        selection = None
        source = "ollama"

        # Primary path: Ollama selects the tool.
        try:
            model_response = await self.ollama_client.select_tool(
                question
            )

            selection = ToolSelection.model_validate(
                model_response
            )

        except (
            httpx.HTTPError,
            ValueError,
            ValidationError,
            TypeError,
        ):
            # Recovery path: deterministic fallback.
            selection = fallback_tool(question)
            source = "fallback"

        if selection is None:
            return AIQueryResponse(
                answer=(
                    "I could not identify this ERP request. "
                    "Try asking about dashboard summary, sales trend, "
                    "top products, top vendors, inventory, or low stock."
                ),
                source=source,
            )

        executor = ToolExecutor(db)

        # Backend independently enforces permissions and tenant scope.
        result = executor.execute(
            selection=selection,
            tenant_id=current_user.tenant_id,
            role=current_user.role,
        )

        safe_data = jsonable_encoder(result)

        return AIQueryResponse(
            answer=format_answer(
                selection.tool,
                safe_data,
            ),
            tool_used=selection.tool,
            source=source,
            data=safe_data,
        )
