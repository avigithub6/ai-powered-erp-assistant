from fastapi import HTTPException, status

from app.core.permissions import ROLE_PERMISSIONS
from app.repositories.inventory_repository import InventoryRepository


class InventoryService:
    def __init__(self, repository: InventoryRepository):
        self.repository = repository

    @staticmethod
    def check_access(role: str):
        if "inventory:read" not in ROLE_PERMISSIONS.get(role, set()):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access inventory",
            )

    @staticmethod
    def serialize_item(item, role: str):
        data = {
            "id": item.id,
            "item_name": item.item_name,
            "sku": item.sku,
            "category": item.category,
            "stock_level": item.stock_level,
            "reorder_level": item.reorder_level,
            "selling_price": item.selling_price,
            "unit": item.unit,
        }

        if "inventory:procurement_read" in ROLE_PERMISSIONS.get(role, set()):
            data["purchase_price"] = item.purchase_price

        return data

    def list_items(
        self,
        tenant_id: int,
        role: str,
        limit: int = 20,
        offset: int = 0,
        low_stock_only: bool = False,
    ):
        self.check_access(role)

        items, total = self.repository.list_items(
            tenant_id, limit, offset, low_stock_only
        )

        return {
            "items": [self.serialize_item(item, role) for item in items],
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    def get_item(self, tenant_id: int, role: str, item_id: int):
        self.check_access(role)

        item = self.repository.get_item(tenant_id, item_id)

        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inventory item not found",
            )

        return self.serialize_item(item, role)
