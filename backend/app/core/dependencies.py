import logging
from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.db.session import get_db
from app.models import Tenant, User
from app.security.jwt import decode_access_token

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)

        user_id = int(payload["sub"])
        tenant_id = int(payload["tenant_id"])

        if user_id <= 0 or tenant_id <= 0:
            raise ValueError("Invalid token claims")

    except (ValueError, KeyError, TypeError):
        logger.warning("Authentication rejected: invalid token")
        raise credentials_exception

    user = db.scalar(
        select(User).where(
            User.id == user_id,
            User.tenant_id == tenant_id,
        )
    )

    if user is None or not user.is_active:
        logger.warning(
            "Authentication rejected: inactive or missing user_id=%s",
            user_id,
        )
        raise credentials_exception

    tenant = db.scalar(
        select(Tenant).where(
            Tenant.id == user.tenant_id,
            Tenant.is_active.is_(True),
        )
    )

    if tenant is None:
        logger.warning(
            "Authentication rejected: inactive tenant_id=%s",
            tenant_id,
        )
        raise credentials_exception

    return user


def require_roles(*allowed_roles: str) -> Callable:
    def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role not in allowed_roles:
            logger.warning(
                "Authorization denied: user_id=%s tenant_id=%s role=%s",
                current_user.id,
                current_user.tenant_id,
                current_user.role,
            )

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource",
            )

        return current_user

    return role_checker