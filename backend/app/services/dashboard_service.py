
from datetime import date

from fastapi import HTTPException, status

from app.core.permissions import ROLE_PERMISSIONS
from app.repositories.dashboard_repository import DashboardRepository


class DashboardService:
    def __init__(self, repository: DashboardRepository):
        self.repository = repository

    @staticmethod
    def _check_permission(role: str, permission: str):
        if permission not in ROLE_PERMISSIONS.get(role, set()):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource",
            )

    def get_summary(
        self,
        tenant_id: int,
        role: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ):
        self._check_permission(role, "dashboard:read")

        data = self.repository.get_summary(
            tenant_id,
            start_date=start_date,
            end_date=end_date,
        )

        if "purchase:analytics" not in ROLE_PERMISSIONS.get(role, set()):
            data["total_purchase_value"] = None

        if "sales:analytics" not in ROLE_PERMISSIONS.get(role, set()):
            data["total_sales"] = None
            data["sales_order_count"] = 0

        return data

    def get_total_sales(
        self,
        tenant_id: int,
        role: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ):
        self._check_permission(role, "sales:analytics")
        return {
            "total_sales": self.repository.get_total_sales(
                tenant_id,
                start_date=start_date,
                end_date=end_date,
            )
        }

    def get_total_purchases(
        self,
        tenant_id: int,
        role: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ):
        self._check_permission(role, "purchase:analytics")
        return {
            "total_purchase_value": self.repository.get_total_purchases(
                tenant_id,
                start_date=start_date,
                end_date=end_date,
            )
        }

    def get_sales_trend(
        self,
        tenant_id: int,
        role: str,
        limit: int = 120,
        start_date: date | None = None,
        end_date: date | None = None,
    ):
        self._check_permission(role, "sales:analytics")
        return self.repository.get_sales_trend(
            tenant_id,
            limit,
            start_date=start_date,
            end_date=end_date,
        )

    def get_top_products(
        self,
        tenant_id: int,
        role: str,
        limit: int = 5,
        start_date: date | None = None,
        end_date: date | None = None,
    ):
        self._check_permission(role, "sales:analytics")
        return self.repository.get_top_products(
            tenant_id,
            limit,
            start_date=start_date,
            end_date=end_date,
        )

    def get_top_vendors(
        self,
        tenant_id: int,
        role: str,
        limit: int = 5,
        start_date: date | None = None,
        end_date: date | None = None,
    ):
        self._check_permission(role, "purchase:analytics")
        return self.repository.get_top_vendors(
            tenant_id,
            limit,
            start_date=start_date,
            end_date=end_date,
        )

    def get_sales_purchase_comparison(self, tenant_id: int, role: str):
        self._check_permission(role, "sales:analytics")
        self._check_permission(role, "purchase:analytics")
        return self.repository.get_sales_purchase_comparison(tenant_id)

    def get_inventory(
        self,
        tenant_id: int,
        role: str,
        limit: int = 20,
        offset: int = 0,
    ):
        self._check_permission(role, "inventory:read")
        return self.repository.get_inventory(tenant_id, limit, offset)

    def get_low_stock(
        self,
        tenant_id: int,
        role: str,
        limit: int = 20,
        offset: int = 0,
    ):
        self._check_permission(role, "inventory:read")
        return self.repository.get_low_stock(tenant_id, limit, offset)
