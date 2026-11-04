from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models import User
from app.repositories.inventory_repository import InventoryRepository
from app.schemas.inventory import (
    InventoryListResponse,
    ProcurementInventoryResponse,
    SalesInventoryResponse,
)
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/inventory", tags=["Inventory"])


def get_service(db: Session) -> InventoryService:
    return InventoryService(InventoryRepository(db))


@router.get("", response_model=InventoryListResponse)
def list_inventory(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    low_stock_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = get_service(db)
    return service.list_items(
        current_user.tenant_id,
        current_user.role,
        limit,
        offset,
        low_stock_only,
    )


@router.get(
    "/{item_id}",
    response_model=SalesInventoryResponse | ProcurementInventoryResponse,
)
def get_inventory_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = get_service(db)
    return service.get_item(
        current_user.tenant_id,
        current_user.role,
        item_id,
    )
