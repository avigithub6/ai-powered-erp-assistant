from fastapi import HTTPException, status

from app.core.permissions import ROLE_PERMISSIONS
from app.repositories.customer_repository import CustomerRepository


class CustomerService:
    def __init__(self, repository: CustomerRepository):
        self.repository = repository

    @staticmethod
    def check_access(role: str):
        if "customers:read" not in ROLE_PERMISSIONS.get(role, set()):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access customers",
            )

    def list_customers(
        self,
        tenant_id: int,
        role: str,
        limit: int = 20,
        offset: int = 0,
    ):
        self.check_access(role)

        customers, total = self.repository.list_customers(
            tenant_id, limit, offset
        )

        return {
            "items": customers,
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    def get_customer(self, tenant_id: int, role: str, customer_id: int):
        self.check_access(role)

        customer = self.repository.get_customer(tenant_id, customer_id)

        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found",
            )

        return customer
