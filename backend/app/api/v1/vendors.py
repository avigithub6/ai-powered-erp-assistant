from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models import User
from app.repositories.vendor_repository import VendorRepository
from app.schemas.vendor import VendorListResponse, VendorResponse
from app.services.vendor_service import VendorService

router = APIRouter(prefix="/vendors", tags=["Vendors"])


def get_service(db: Session) -> VendorService:
    return VendorService(VendorRepository(db))


@router.get("", response_model=VendorListResponse)
def list_vendors(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = get_service(db)
    return service.list_vendors(
        current_user.tenant_id,
        current_user.role,
        limit,
        offset,
    )


@router.get("/{vendor_id}", response_model=VendorResponse)
def get_vendor(
    vendor_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = get_service(db)
    return service.get_vendor(
        current_user.tenant_id,
        current_user.role,
        vendor_id,
    )
