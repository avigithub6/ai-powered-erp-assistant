from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models import Inventory, Vendor, VendorItem


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

    def search_steel_vendors(self, tenant_id: int, limit: int = 10):
        location_filter = or_(
            Vendor.address.ilike("%Delhi%"),
            Vendor.address.ilike("%Gurugram%"),
            Vendor.address.ilike("%Gurgaon%"),
            Vendor.address.ilike("%Faridabad%"),
            Vendor.address.ilike("%Noida%"),
            Vendor.address.ilike("%Ghaziabad%"),
        )

        statement = (
            select(
                Vendor.id.label("vendor_id"),
                Vendor.vendor_name,
                Vendor.address,
                func.group_concat(
                    func.distinct(Inventory.item_name)
                ).label("supplied_products"),
            )
            .join(
                VendorItem,
                (VendorItem.vendor_id == Vendor.id)
                & (VendorItem.tenant_id == Vendor.tenant_id),
            )
            .join(
                Inventory,
                (Inventory.id == VendorItem.inventory_id)
                & (Inventory.tenant_id == VendorItem.tenant_id),
            )
            .where(
                Vendor.tenant_id == tenant_id,
                VendorItem.tenant_id == tenant_id,
                Inventory.tenant_id == tenant_id,
                Inventory.is_active.is_(True),
                or_(
                    Inventory.category.ilike("%steel%"),
                    Inventory.item_name.ilike("%steel%"),
                ),
                location_filter,
            )
            .group_by(
                Vendor.id,
                Vendor.vendor_name,
                Vendor.address,
            )
            .order_by(Vendor.vendor_name)
            .limit(limit)
        )

        return self.db.execute(statement).mappings().all()

    def get_vendor(self, tenant_id: int, vendor_id: int):
        return self.db.scalar(
            select(Vendor).where(
                Vendor.tenant_id == tenant_id,
                Vendor.id == vendor_id,
            )
        )
