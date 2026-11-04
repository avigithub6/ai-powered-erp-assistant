from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session

from app.models import (
    Inventory,
    PurchaseOrder,
    SalesOrder,
    SalesOrderItem,
    Vendor,
)


class DashboardRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_summary(self, tenant_id: int):
        total_sales = self.db.scalar(
            select(func.coalesce(func.sum(SalesOrder.total_amount), 0)).where(
                SalesOrder.tenant_id == tenant_id,
                SalesOrder.status == "COMPLETED",
            )
        )

        total_purchase_value = self.db.scalar(
            select(
                func.coalesce(func.sum(PurchaseOrder.total_amount), 0)
            ).where(
                PurchaseOrder.tenant_id == tenant_id,
                PurchaseOrder.status == "COMPLETED",
            )
        )

        sales_order_count = self.db.scalar(
            select(func.count(SalesOrder.id)).where(
                SalesOrder.tenant_id == tenant_id,
                SalesOrder.status == "COMPLETED",
            )
        ) or 0

        inventory_item_count = self.db.scalar(
            select(func.count(Inventory.id)).where(
                Inventory.tenant_id == tenant_id,
                Inventory.is_active.is_(True),
            )
        ) or 0

        low_stock_count = self.db.scalar(
            select(func.count(Inventory.id)).where(
                Inventory.tenant_id == tenant_id,
                Inventory.is_active.is_(True),
                Inventory.stock_level <= Inventory.reorder_level,
            )
        ) or 0

        return {
            "total_sales": total_sales,
            "total_purchase_value": total_purchase_value,
            "sales_order_count": sales_order_count,
            "inventory_item_count": inventory_item_count,
            "low_stock_count": low_stock_count,
        }

    def get_sales_trend(self, tenant_id: int, limit: int = 120):
        year = extract("year", SalesOrder.order_date)
        month = extract("month", SalesOrder.order_date)

        statement = (
            select(
                year.label("year"),
                month.label("month"),
                func.sum(SalesOrder.total_amount).label("total_sales"),
            )
            .where(
                SalesOrder.tenant_id == tenant_id,
                SalesOrder.status == "COMPLETED",
            )
            .group_by(year, month)
            .order_by(year, month)
            .limit(limit)
        )

        rows = self.db.execute(statement).all()

        return [
            {
                "month": f"{int(row.year):04d}-{int(row.month):02d}",
                "total_sales": row.total_sales,
            }
            for row in rows
        ]

    def get_top_products(self, tenant_id: int, limit: int = 5):
        statement = (
            select(
                Inventory.id.label("inventory_id"),
                Inventory.item_name,
                Inventory.sku,
                func.sum(SalesOrderItem.quantity).label(
                    "total_quantity_sold"
                ),
            )
            .join(
                SalesOrderItem,
                (SalesOrderItem.inventory_id == Inventory.id)
                & (SalesOrderItem.tenant_id == Inventory.tenant_id),
            )
            .join(
                SalesOrder,
                (SalesOrder.id == SalesOrderItem.sales_order_id)
                & (SalesOrder.tenant_id == SalesOrderItem.tenant_id),
            )
            .where(
                Inventory.tenant_id == tenant_id,
                SalesOrderItem.tenant_id == tenant_id,
                SalesOrder.tenant_id == tenant_id,
                SalesOrder.status == "COMPLETED",
            )
            .group_by(
                Inventory.id,
                Inventory.item_name,
                Inventory.sku,
            )
            .order_by(func.sum(SalesOrderItem.quantity).desc())
            .limit(limit)
        )

        return self.db.execute(statement).mappings().all()

    def get_top_vendors(self, tenant_id: int, limit: int = 5):
        statement = (
            select(
                Vendor.id.label("vendor_id"),
                Vendor.vendor_name,
                func.sum(PurchaseOrder.total_amount).label(
                    "total_purchase_value"
                ),
            )
            .join(
                PurchaseOrder,
                (PurchaseOrder.vendor_id == Vendor.id)
                & (PurchaseOrder.tenant_id == Vendor.tenant_id),
            )
            .where(
                Vendor.tenant_id == tenant_id,
                PurchaseOrder.tenant_id == tenant_id,
                PurchaseOrder.status == "COMPLETED",
            )
            .group_by(Vendor.id, Vendor.vendor_name)
            .order_by(
                func.sum(PurchaseOrder.total_amount).desc()
            )
            .limit(limit)
        )

        return self.db.execute(statement).mappings().all()

    def get_inventory(self, tenant_id: int, limit: int = 20, offset: int = 0):
        statement = (
            select(
                Inventory.id,
                Inventory.item_name,
                Inventory.sku,
                Inventory.stock_level,
                Inventory.reorder_level,
                Inventory.unit,
            )
            .where(
                Inventory.tenant_id == tenant_id,
                Inventory.is_active.is_(True),
            )
            .order_by(Inventory.item_name)
            .limit(limit)
            .offset(offset)
        )

        total = self.db.scalar(
            select(func.count(Inventory.id)).where(
                Inventory.tenant_id == tenant_id,
                Inventory.is_active.is_(True),
            )
        ) or 0

        items = self.db.execute(statement).mappings().all()

        return items, total

    def get_low_stock(self, tenant_id: int, limit: int = 20, offset: int = 0):
        condition = (
            (Inventory.tenant_id == tenant_id)
            & (Inventory.is_active.is_(True))
            & (Inventory.stock_level <= Inventory.reorder_level)
        )

        statement = (
            select(
                Inventory.id,
                Inventory.item_name,
                Inventory.sku,
                Inventory.stock_level,
                Inventory.reorder_level,
                Inventory.unit,
            )
            .where(condition)
            .order_by(Inventory.stock_level)
            .limit(limit)
            .offset(offset)
        )

        total = self.db.scalar(
            select(func.count(Inventory.id)).where(condition)
        ) or 0

        items = self.db.execute(statement).mappings().all()

        return items, total
