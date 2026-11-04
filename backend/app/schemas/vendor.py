from pydantic import BaseModel, ConfigDict


class VendorResponse(BaseModel):
    id: int
    vendor_name: str
    contact_person: str | None
    email: str | None
    phone: str | None
    address: str | None

    model_config = ConfigDict(from_attributes=True)


class VendorListResponse(BaseModel):
    items: list[VendorResponse]
    total: int
    limit: int
    offset: int
