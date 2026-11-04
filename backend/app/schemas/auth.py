from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    tenant_code: str = Field(min_length=1, max_length=50)
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class CurrentUserResponse(BaseModel):
    id: int
    tenant_id: int
    username: str
    full_name: str
    email: str
    role: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)