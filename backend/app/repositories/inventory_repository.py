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
    ):
        query = select(Inventory).where(
            Inventory.tenant_id == tenant_id,
            Inventory.is_active.is_(True),
        )

        count_query = select(func.count(Inventory.id)).where(
            Inventory.tenant_id == tenant_id,
            Inventory.is_active.is_(True),
        )

        if low_stock_only:
            condition = Inventory.stock_level <= Inventory.reorder_level
            query = query.where(condition)
            count_query = count_query.where(condition)

        total = self.db.scalar(count_query) or 0

        items = self.db.scalars(
            query.order_by(Inventory.item_name)
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
