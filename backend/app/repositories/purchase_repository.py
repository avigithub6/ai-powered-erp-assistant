from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import PurchaseOrder


class PurchaseRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_orders(
        self,
        tenant_id: int,
        limit: int = 20,
        offset: int = 0,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ):
        query = select(PurchaseOrder).where(
            PurchaseOrder.tenant_id == tenant_id
        )

        count_query = select(func.count(PurchaseOrder.id)).where(
            PurchaseOrder.tenant_id == tenant_id
        )

        if start_date is not None:
            query = query.where(PurchaseOrder.order_date >= start_date)
            count_query = count_query.where(
                PurchaseOrder.order_date >= start_date
            )

        if end_date is not None:
            query = query.where(PurchaseOrder.order_date <= end_date)
            count_query = count_query.where(
                PurchaseOrder.order_date <= end_date
            )

        total = self.db.scalar(count_query) or 0

        orders = self.db.scalars(
            query.order_by(PurchaseOrder.order_date.desc())
            .limit(limit)
            .offset(offset)
        ).all()

        return orders, total

    def get_order(self, tenant_id: int, order_id: int):
        query = (
            select(PurchaseOrder)
            .where(
                PurchaseOrder.tenant_id == tenant_id,
                PurchaseOrder.id == order_id,
            )
            .options(selectinload(PurchaseOrder.items))
        )

        return self.db.scalar(query)
