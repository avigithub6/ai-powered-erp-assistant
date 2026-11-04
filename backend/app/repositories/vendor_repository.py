from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Vendor


class VendorRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_vendors(
        self,
        tenant_id: int,
        limit: int = 20,
        offset: int = 0,
    ):
        query = select(Vendor).where(Vendor.tenant_id == tenant_id)

        count_query = select(func.count(Vendor.id)).where(
            Vendor.tenant_id == tenant_id
        )

        total = self.db.scalar(count_query) or 0

        vendors = self.db.scalars(
            query.order_by(Vendor.vendor_name)
            .limit(limit)
            .offset(offset)
        ).all()

        return vendors, total

    def get_vendor(self, tenant_id: int, vendor_id: int):
        return self.db.scalar(
            select(Vendor).where(
                Vendor.tenant_id == tenant_id,
                Vendor.id == vendor_id,
            )
        )
