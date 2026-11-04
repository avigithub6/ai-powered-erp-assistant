from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PurchaseOrderItemResponse(BaseModel):
    id: int
    inventory_id: int
    quantity: int
    unit_cost: Decimal
    line_total: Decimal

    model_config = ConfigDict(from_attributes=True)


class PurchaseOrderResponse(BaseModel):
    id: int
    vendor_id: int
    order_number: str
    status: str
    total_amount: Decimal
    order_date: datetime

    model_config = ConfigDict(from_attributes=True)


class PurchaseOrderDetailResponse(PurchaseOrderResponse):
    items: list[PurchaseOrderItemResponse]


class PurchaseOrderListResponse(BaseModel):
    items: list[PurchaseOrderResponse]
    total: int
    limit: int
    offset: int
