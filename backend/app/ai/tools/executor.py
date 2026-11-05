
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ai.tools.schemas import StructuredIntent
from app.repositories.dashboard_repository import DashboardRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.vendor_repository import VendorRepository
from app.services.dashboard_service import DashboardService
from app.services.inventory_service import InventoryService
from app.services.vendor_service import VendorService

INVENTORY_ALLOWED_FIELDS = {
    "id",
    "item_name",
    "sku",
    "category",
    "stock_level",
    "reorder_level",
    "selling_price",
    "unit",
}


class ToolExecutor:
    def __init__(self, db: Session):
        self.db = db

        self.dashboard_service = DashboardService(
            DashboardRepository(db)
        )

        self.inventory_service = InventoryService(
            InventoryRepository(db)
        )

        self.vendor_service = VendorService(
            VendorRepository(db)
        )

    def execute(
        self,
        intent: StructuredIntent,
        tenant_id: int,
        role: str,
    ):
        if intent.request_type != "erp" or intent.tool is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only approved ERP intents can be executed",
            )

        if intent.needs_clarification:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Intent clarification is required before execution",
            )

        tool = intent.tool
        limit = intent.arguments.limit

        start_date = (
            intent.date_range.start_date
            if intent.date_range
            else None
        )
        end_date = (
            intent.date_range.end_date
            if intent.date_range
            else None
        )

        entities = intent.entities
        filters = intent.filters

        if tool == "sales_summary":
            return self.dashboard_service.get_total_sales(
                tenant_id,
                role,
                start_date=start_date,
                end_date=end_date,
            )

        if tool == "purchase_summary":
            return self.dashboard_service.get_total_purchases(
                tenant_id,
                role,
                start_date=start_date,
                end_date=end_date,
            )

        if tool == "dashboard_summary":
            return self.dashboard_service.get_summary(
                tenant_id,
                role,
                start_date=start_date,
                end_date=end_date,
            )

        if tool == "sales_trend":
            return self.dashboard_service.get_sales_trend(
                tenant_id,
                role,
                limit=limit,
                start_date=start_date,
                end_date=end_date,
            )

        if tool == "top_products":
            return self.dashboard_service.get_top_products(
                tenant_id,
                role,
                limit=limit,
                start_date=start_date,
                end_date=end_date,
            )

        if tool == "top_vendors":
            return self.dashboard_service.get_top_vendors(
                tenant_id,
                role,
                limit=limit,
                start_date=start_date,
                end_date=end_date,
            )

        if tool == "sales_purchase_comparison":
            return self.dashboard_service.get_sales_purchase_comparison(
                tenant_id,
                role,
            )

        if tool == "vendor_search":
            if filters.status:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Vendor status filtering is not supported "
                        "because vendor status is not available."
                    ),
                )

            return self.vendor_service.search_vendors(
                tenant_id=tenant_id,
                role=role,
                limit=limit,
                vendor_name=entities.vendor_name,
                product_name=entities.product_name,
                category=filters.category,
                location=filters.location,
            )

        if tool in {"inventory", "low_stock"}:
            is_active = True

            if filters.status:
                normalized_status = filters.status.strip().lower()

                if normalized_status in {"active", "inactive"}:
                    is_active = normalized_status == "active"
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Unsupported inventory status filter",
                    )

            result = self.inventory_service.list_items(
                tenant_id=tenant_id,
                role=role,
                limit=limit,
                offset=0,
                low_stock_only=(tool == "low_stock"),
                product_name=entities.product_name,
                sku=entities.sku,
                category=filters.category,
                is_active=is_active,
            )

            safe_items = [
                {
                    key: value
                    for key, value in item.items()
                    if key in INVENTORY_ALLOWED_FIELDS
                }
                for item in result["items"]
            ]

            return {
                "items": safe_items,
                "total": result["total"],
            }

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported AI tool",
        )
