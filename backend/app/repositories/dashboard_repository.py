
from datetime import UTC, date, datetime, timedelta

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

    @staticmethod
    def _date_filters(column, start_date=None, end_date=None):
        conditions = []

        if start_date is not None:
            conditions.append(column >= start_date)

        if end_date is not None:
            conditions.append(column < end_date + timedelta(days=1))

        return conditions

    def get_summary(
        self,
        tenant_id: int,
        start_date: date | None = None,
        end_date: date | None = None,
    ):
        sales_conditions = [
            SalesOrder.tenant_id == tenant_id,
            SalesOrder.status == "COMPLETED",
            *self._date_filters(
                SalesOrder.order_date, start_date, end_date
            ),
        ]

        purchase_conditions = [
            PurchaseOrder.tenant_id == tenant_id,
            PurchaseOrder.status == "COMPLETED",
            *self._date_filters(
                PurchaseOrder.order_date, start_date, end_date
            ),
        ]

        total_sales = self.db.scalar(
            select(
                func.coalesce(func.sum(SalesOrder.total_amount), 0)
            ).where(*sales_conditions)
        )

        total_purchase_value = self.db.scalar(
            select(
                func.coalesce(func.sum(PurchaseOrder.total_amount), 0)
            ).where(*purchase_conditions)
        )

        sales_order_count = self.db.scalar(
            select(func.count(SalesOrder.id)).where(*sales_conditions)
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

    def get_total_sales(
        self,
        tenant_id: int,
        start_date: date | None = None,
        end_date: date | None = None,
    ):
        return self.db.scalar(
            select(
                func.coalesce(func.sum(SalesOrder.total_amount), 0)
            ).where(
                SalesOrder.tenant_id == tenant_id,
                SalesOrder.status == "COMPLETED",
                *self._date_filters(
                    SalesOrder.order_date, start_date, end_date
                ),
            )
        )

    def get_total_purchases(
        self,
        tenant_id: int,
        start_date: date | None = None,
        end_date: date | None = None,
    ):
        return self.db.scalar(
            select(
                func.coalesce(func.sum(PurchaseOrder.total_amount), 0)
            ).where(
                PurchaseOrder.tenant_id == tenant_id,
                PurchaseOrder.status == "COMPLETED",
                *self._date_filters(
                    PurchaseOrder.order_date, start_date, end_date
                ),
            )
        )

    def get_sales_trend(
        self,
        tenant_id: int,
        limit: int = 120,
        start_date: date | None = None,
        end_date: date | None = None,
    ):
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
                *self._date_filters(
                    SalesOrder.order_date, start_date, end_date
                ),
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

    def get_top_products(
        self,
        tenant_id: int,
        limit: int = 5,
        start_date: date | None = None,
        end_date: date | None = None,
    ):
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
                *self._date_filters(
                    SalesOrder.order_date, start_date, end_date
                ),
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

    def get_top_vendors(
        self,
        tenant_id: int,
        limit: int = 5,
        start_date: date | None = None,
        end_date: date | None = None,
    ):
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
                *self._date_filters(
                    PurchaseOrder.order_date, start_date, end_date
                ),
            )
            .group_by(Vendor.id, Vendor.vendor_name)
            .order_by(func.sum(PurchaseOrder.total_amount).desc())
            .limit(limit)
        )

        return self.db.execute(statement).mappings().all()

    def get_sales_purchase_comparison(self, tenant_id: int):
        end_date = datetime.now(UTC)
        start_date = end_date - timedelta(days=90)

        sales = self.db.scalar(
            select(
                func.coalesce(func.sum(SalesOrder.total_amount), 0)
            ).where(
                SalesOrder.tenant_id == tenant_id,
                SalesOrder.status == "COMPLETED",
                SalesOrder.order_date >= start_date,
                SalesOrder.order_date <= end_date,
            )
        )

        purchases = self.db.scalar(
            select(
                func.coalesce(func.sum(PurchaseOrder.total_amount), 0)
            ).where(
                PurchaseOrder.tenant_id == tenant_id,
                PurchaseOrder.status == "COMPLETED",
                PurchaseOrder.order_date >= start_date,
                PurchaseOrder.order_date <= end_date,
            )
        )

        sales_count = self.db.scalar(
            select(func.count(SalesOrder.id)).where(
                SalesOrder.tenant_id == tenant_id,
                SalesOrder.status == "COMPLETED",
                SalesOrder.order_date >= start_date,
                SalesOrder.order_date <= end_date,
            )
        ) or 0

        purchase_count = self.db.scalar(
            select(func.count(PurchaseOrder.id)).where(
                PurchaseOrder.tenant_id == tenant_id,
                PurchaseOrder.status == "COMPLETED",
                PurchaseOrder.order_date >= start_date,
                PurchaseOrder.order_date <= end_date,
            )
        ) or 0

        return {
            "period_days": 90,
            "sales_total": sales,
            "purchase_total": purchases,
            "sales_order_count": sales_count,
            "purchase_order_count": purchase_count,
            "start_date": start_date.date().isoformat(),
            "end_date": end_date.date().isoformat(),
        }

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
