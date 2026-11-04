from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Customer


class CustomerRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_customers(
        self,
        tenant_id: int,
        limit: int = 20,
        offset: int = 0,
    ):
        query = select(Customer).where(Customer.tenant_id == tenant_id)

        count_query = select(func.count(Customer.id)).where(
            Customer.tenant_id == tenant_id
        )

        total = self.db.scalar(count_query) or 0

        customers = self.db.scalars(
            query.order_by(Customer.name)
            .limit(limit)
            .offset(offset)
        ).all()

        return customers, total

    def get_customer(self, tenant_id: int, customer_id: int):
        return self.db.scalar(
            select(Customer).where(
                Customer.tenant_id == tenant_id,
                Customer.id == customer_id,
            )
        )
