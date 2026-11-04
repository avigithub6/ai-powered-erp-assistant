from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Tenant, User
from app.schemas.auth import LoginRequest, TokenResponse
from app.security.jwt import create_access_token
from app.security.password import verify_password


def authenticate_user(
    db: Session,
    login_data: LoginRequest,
) -> TokenResponse:
    user = db.scalar(
        select(User)
        .join(Tenant, Tenant.id == User.tenant_id)
        .where(
            User.username == login_data.username,
            Tenant.code == login_data.tenant_code,
            User.is_active.is_(True),
            Tenant.is_active.is_(True),
        )
    )

    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid tenant code, username, or password",
    )

    if user is None:
        raise invalid_credentials

    if not verify_password(login_data.password, user.password_hash):
        raise invalid_credentials

    access_token = create_access_token(
        user_id=user.id,
        tenant_id=user.tenant_id,
        role=user.role,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )