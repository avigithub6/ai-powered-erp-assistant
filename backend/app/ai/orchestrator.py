import httpx
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError

from app.ai.llm.ollama_client import OllamaClient
from app.ai.tools.executor import ToolExecutor
from app.ai.tools.schemas import ToolSelection
from app.models import User
from app.schemas.ai import AIQueryResponse


def fallback_tool(question: str) -> ToolSelection | None:
    text = question.lower()

    if any(word in text for word in [
        "low stock",
        "low-stock",
        "reorder",
        "stock alert",
        "stock below",
    ]):
        tool = "low_stock"

    elif any(word in text for word in [
        "sales trend",
        "monthly sales",
        "sales over time",
        "sales performance",
    ]):
        tool = "sales_trend"

    elif any(word in text for word in [
        "top vendor",
        "best vendor",
        "vendor ranking",
        "top supplier",
        "best supplier",
        "supplier ranking",
    ]):
        tool = "top_vendors"

    elif any(word in text for word in [
        "top product",
        "best selling",
        "best-selling",
        "most sold",
        "highest selling",
    ]):
        tool = "top_products"

    elif any(word in text for word in [
        "inventory",
        "stock",
        "available items",
        "item details",
    ]):
        tool = "inventory"

    elif any(word in text for word in [
        "dashboard",
        "summary",
        "overview",
        "business status",
        "total sales",
        "total purchase",
        "purchase",
    ]):
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

        parts.extend([
            f"Completed sales orders: {data['sales_order_count']}",
            f"Inventory items: {data['inventory_item_count']}",
            f"Low-stock items: {data['low_stock_count']}",
        ])

        return "Dashboard summary: " + "; ".join(parts) + "."

    if tool == "sales_trend":
        if not data:
            return "No completed sales trend data is available."

        lines = [
            f"{item['month']}: {item['total_sales']}"
            for item in data
        ]

        return "Monthly sales trend: " + "; ".join(lines) + "."

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

        return "Top vendors by completed purchase value: " + "; ".join(
            lines
        ) + "."

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
        source = "fallback"

        try:
            model_response = await self.ollama_client.select_tool(
                question
            )

            selection = ToolSelection.model_validate(model_response)
            source = "ollama"

        except (
            httpx.HTTPError,
            ValueError,
            ValidationError,
            TypeError,
        ):
            selection = None

        if selection is None:
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

        try:
            result = executor.execute(
                selection=selection,
                tenant_id=current_user.tenant_id,
                role=current_user.role,
            )

        except HTTPException as exc:
            if exc.status_code == 403:
                raise

            raise

        safe_data = jsonable_encoder(result)

        return AIQueryResponse(
            answer=format_answer(selection.tool, safe_data),
            tool_used=selection.tool,
            source=source,
            data=safe_data,
        )