from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class SalesOrderItemResponse(BaseModel):
    id: int
    inventory_id: int
    quantity: int
    unit_price: Decimal
    line_total: Decimal

    model_config = ConfigDict(from_attributes=True)


class SalesOrderResponse(BaseModel):
    id: int
    customer_id: int
    order_number: str
    status: str
    total_amount: Decimal
    order_date: datetime

    model_config = ConfigDict(from_attributes=True)


class SalesOrderDetailResponse(SalesOrderResponse):
    items: list[SalesOrderItemResponse]


class SalesOrderListResponse(BaseModel):
    items: list[SalesOrderResponse]
    total: int
    limit: int
    offset: int
