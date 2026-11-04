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

    def get_summary(self, tenant_id: int, role: str):
        self._check_permission(role, "dashboard:read")

        data = self.repository.get_summary(tenant_id)

        if "purchase:analytics" not in ROLE_PERMISSIONS.get(role, set()):
            data["total_purchase_value"] = None

        if "sales:analytics" not in ROLE_PERMISSIONS.get(role, set()):
            data["total_sales"] = None
            data["sales_order_count"] = 0

        return data

    def get_sales_trend(self, tenant_id: int, role: str):
        self._check_permission(role, "sales:analytics")
        return self.repository.get_sales_trend(tenant_id)

    def get_top_products(self, tenant_id: int, role: str, limit: int = 5):
        self._check_permission(role, "sales:analytics")
        return self.repository.get_top_products(tenant_id, limit)

    def get_top_vendors(self, tenant_id: int, role: str, limit: int = 5):
        self._check_permission(role, "purchase:analytics")
        return self.repository.get_top_vendors(tenant_id, limit)

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
