
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Inventory


class InventoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_items(
        self,
        tenant_id: int,
        limit: int = 20,
        offset: int = 0,
        low_stock_only: bool = False,
        product_name: str | None = None,
        sku: str | None = None,
        category: str | None = None,
        is_active: bool | None = True,
    ):
        conditions = [Inventory.tenant_id == tenant_id]

        if is_active is not None:
            conditions.append(Inventory.is_active.is_(is_active))

        if low_stock_only:
            conditions.append(
                Inventory.stock_level <= Inventory.reorder_level
            )

        if product_name:
            conditions.append(
                Inventory.item_name.ilike(f"%{product_name}%")
            )

        if sku:
            conditions.append(Inventory.sku.ilike(f"%{sku}%"))

        if category:
            conditions.append(Inventory.category.ilike(f"%{category}%"))

        statement = select(Inventory).where(*conditions)
        count_statement = (
            select(func.count(Inventory.id)).where(*conditions)
        )

        total = self.db.scalar(count_statement) or 0

        items = self.db.scalars(
            statement.order_by(Inventory.item_name)
            .limit(limit)
            .offset(offset)
        ).all()

        return items, total

    def get_item(self, tenant_id: int, item_id: int):
        return self.db.scalar(
            select(Inventory).where(
                Inventory.tenant_id == tenant_id,
                Inventory.id == item_id,
                Inventory.is_active.is_(True),
            )
        )
