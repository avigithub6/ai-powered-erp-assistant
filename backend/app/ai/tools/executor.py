from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.ai.tools.schemas import ToolSelection
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
        selection: ToolSelection,
        tenant_id: int,
        role: str,
    ):
        tool = selection.tool
        limit = selection.arguments.limit

        if tool == "dashboard_summary":
            return self.dashboard_service.get_summary(
                tenant_id,
                role,
            )

        if tool == "sales_trend":
            return self.dashboard_service.get_sales_trend(
                tenant_id,
                role,
            )

        if tool == "top_products":
            return self.dashboard_service.get_top_products(
                tenant_id,
                role,
                limit,
            )

        if tool == "top_vendors":
            return self.dashboard_service.get_top_vendors(
                tenant_id,
                role,
                limit,
            )

        if tool == "sales_purchase_comparison":
            return self.dashboard_service.get_sales_purchase_comparison(
                tenant_id,
                role,
            )

        if tool == "vendor_search":
            return self.vendor_service.search_steel_vendors(
                tenant_id,
                role,
                limit,
            )

        if tool in {"inventory", "low_stock"}:
            result = self.inventory_service.list_items(
                tenant_id=tenant_id,
                role=role,
                limit=limit,
                offset=0,
                low_stock_only=(tool == "low_stock"),
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
            status_code=400,
            detail="Unsupported AI tool",
        )
