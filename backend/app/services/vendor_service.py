from fastapi import HTTPException, status

from app.core.permissions import ROLE_PERMISSIONS
from app.repositories.vendor_repository import VendorRepository


class VendorService:
    def __init__(self, repository: VendorRepository):
        self.repository = repository

    @staticmethod
    def check_access(role: str):
        if "vendors:read" not in ROLE_PERMISSIONS.get(role, set()):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access vendors",
            )

    def list_vendors(
        self,
        tenant_id: int,
        role: str,
        limit: int = 20,
        offset: int = 0,
    ):
        self.check_access(role)

        vendors, total = self.repository.list_vendors(
            tenant_id, limit, offset
        )

        return {
            "items": vendors,
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    def get_vendor(self, tenant_id: int, role: str, vendor_id: int):
        self.check_access(role)

        vendor = self.repository.get_vendor(tenant_id, vendor_id)

        if vendor is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vendor not found",
            )

        return vendor

    def search_steel_vendors(
        self,
        tenant_id: int,
        role: str,
        limit: int = 10,
    ):
        self.check_access(role)

        return self.repository.search_steel_vendors(
            tenant_id=tenant_id,
            limit=limit,
        )
