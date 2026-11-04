from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models import User
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import CustomerListResponse, CustomerResponse
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["Customers"])


def get_service(db: Session) -> CustomerService:
    return CustomerService(CustomerRepository(db))


@router.get("", response_model=CustomerListResponse)
def list_customers(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = get_service(db)
    return service.list_customers(
        current_user.tenant_id,
        current_user.role,
        limit,
        offset,
    )


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = get_service(db)
    return service.get_customer(
        current_user.tenant_id,
        current_user.role,
        customer_id,
    )
