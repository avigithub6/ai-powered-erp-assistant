from datetime import datetime

from fastapi import HTTPException, status

from app.core.permissions import ROLE_PERMISSIONS
from app.repositories.purchase_repository import PurchaseRepository


class PurchaseService:
    def __init__(self, repository: PurchaseRepository):
        self.repository = repository

    @staticmethod
    def check_access(role: str):
        if "purchase:read" not in ROLE_PERMISSIONS.get(role, set()):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access purchases",
            )

    def list_orders(
        self,
        tenant_id: int,
        role: str,
        limit: int = 20,
        offset: int = 0,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ):
        self.check_access(role)

        if start_date and end_date and start_date > end_date:
            raise HTTPException(
                status_code=400,
                detail="Start date cannot be after end date",
            )

        return self.repository.list_orders(
            tenant_id, limit, offset, start_date, end_date
        )

    def get_order(self, tenant_id: int, role: str, order_id: int):
        self.check_access(role)

        order = self.repository.get_order(tenant_id, order_id)

        if order is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Purchase order not found",
            )

        return order
