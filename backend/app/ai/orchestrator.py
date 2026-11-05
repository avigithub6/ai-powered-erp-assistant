
import httpx
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError

from app.ai.llm.ollama_client import OllamaClient
from app.ai.tools.executor import ToolExecutor
from app.ai.tools.schemas import StructuredIntent
from app.models import User
from app.schemas.ai import AIQueryResponse


def format_answer(tool: str, data: dict | list) -> str:
    if tool == "sales_summary":
        return (
            f"Total completed sales value: "
            f"{data['total_sales']}."
        )

    if tool == "purchase_summary":
        return (
            f"Total completed purchase value: "
            f"{data['total_purchase_value']}."
        )

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
            return "No vendors matched your search criteria."

        lines = [
            (
                f"{item['vendor_name']} "
                f"(Address: {item['address']}): "
                f"Supplied products: "
                f"{item['supplied_products'] or 'Not available'}"
            )
            for item in data
        ]

        return "Vendors found: " + "; ".join(lines) + "."

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

    @staticmethod
    def _response_metadata(intent: StructuredIntent):
        return {
            "intent": intent.intent,
            "entities": intent.entities.model_dump(exclude_none=True),
            "filters": intent.filters.model_dump(exclude_none=True),
            "date_range": (
                intent.date_range.model_dump(exclude_none=True)
                if intent.date_range
                else None
            ),
        }

    async def query(self, question: str, current_user: User, db):
        source = "ollama"

        # Step 1: Extract structured intent using the LLM.
        try:
            intent = await self.ollama_client.understand_intent(question)

            if not isinstance(intent, StructuredIntent):
                intent = StructuredIntent.model_validate(intent)

        except (
            httpx.HTTPError,
            ValueError,
            ValidationError,
            TypeError,
        ):
            return AIQueryResponse(
                answer=(
                    "I could not understand the request right now. "
                    "Please try again with a clear ERP-related question."
                ),
                source="fallback",
            )

        metadata = self._response_metadata(intent)

        # Step 2: Handle out-of-scope requests.
        if intent.request_type == "out_of_scope":
            return AIQueryResponse(
                answer=(
                    "I can help with ERP-related questions about "
                    "sales, purchases, vendors, inventory, products, "
                    "and business reports."
                ),
                source="guardrail",
                **metadata,
            )

        # Step 3: Ask for clarification when required.
        if intent.needs_clarification:
            return AIQueryResponse(
                answer=intent.clarification_question
                or "Please clarify your ERP request.",
                source="ollama",
                needs_clarification=True,
                clarification_question=intent.clarification_question,
                **metadata,
            )

        # Step 4: Reject unsupported vendor status filtering.
        if (
            intent.tool == "vendor_search"
            and (
                "vendor_status" in intent.unsupported_filters
                or intent.filters.status is not None
            )
        ):
            return AIQueryResponse(
                answer=(
                    "Vendor records mein active/inactive status "
                    "available nahi hai, isliye status ke basis par "
                    "filter nahi kar sakta. Aap vendor name, product "
                    "category ya location se search kar sakte hain."
                ),
                tool_used=intent.tool,
                source="guardrail",
                **metadata,
            )

        # Step 5: Reject any other unsupported filters.
        if intent.unsupported_filters:
            return AIQueryResponse(
                answer=(
                    "Your request contains a filter that is not "
                    "currently supported. Please remove that filter "
                    "and try again."
                ),
                tool_used=intent.tool,
                source="guardrail",
                **metadata,
            )

        if intent.tool is None:
            return AIQueryResponse(
                answer=(
                    "I could not identify the ERP operation. "
                    "Please clarify what information you need."
                ),
                source="guardrail",
                needs_clarification=True,
                **metadata,
            )

        # Step 6: Execute only the approved structured intent.
        # Tenant ID and role always come from authenticated user context.
        executor = ToolExecutor(db)

        result = executor.execute(
            intent=intent,
            tenant_id=current_user.tenant_id,
            role=current_user.role,
        )

        safe_data = jsonable_encoder(result)

        # Step 7: Generate an answer using verified database results.
        try:
            answer = await self.ollama_client.generate_answer(
                question=question,
                tool=intent.tool,
                data=safe_data,
            )

        except (
            httpx.HTTPError,
            ValueError,
            TypeError,
        ):
            answer = format_answer(
                intent.tool,
                safe_data,
            )
            source = "fallback"

        return AIQueryResponse(
            answer=answer,
            tool_used=intent.tool,
            source=source,
            data=safe_data,
            **metadata,
        )
