from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import SalesOrder


class SalesRepository:
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
        query = select(SalesOrder).where(
            SalesOrder.tenant_id == tenant_id
        )

        count_query = select(func.count(SalesOrder.id)).where(
            SalesOrder.tenant_id == tenant_id
        )

        if start_date is not None:
            query = query.where(SalesOrder.order_date >= start_date)
            count_query = count_query.where(
                SalesOrder.order_date >= start_date
            )

        if end_date is not None:
            query = query.where(SalesOrder.order_date <= end_date)
            count_query = count_query.where(
                SalesOrder.order_date <= end_date
            )

        total = self.db.scalar(count_query) or 0

        orders = self.db.scalars(
            query.order_by(SalesOrder.order_date.desc())
            .limit(limit)
            .offset(offset)
        ).all()

        return orders, total

    def get_order(self, tenant_id: int, order_id: int):
        query = (
            select(SalesOrder)
            .where(
                SalesOrder.tenant_id == tenant_id,
                SalesOrder.id == order_id,
            )
            .options(selectinload(SalesOrder.items))
        )

        return self.db.scalar(query)
