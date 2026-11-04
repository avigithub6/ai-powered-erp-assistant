from pydantic import BaseModel, ConfigDict


class CustomerResponse(BaseModel):
    id: int
    name: str
    email: str | None
    phone: str | None
    address: str | None

    model_config = ConfigDict(from_attributes=True)


class CustomerListResponse(BaseModel):
    items: list[CustomerResponse]
    total: int
    limit: int
    offset: int
