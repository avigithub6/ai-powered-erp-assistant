from datetime import UTC, datetime, timedelta

import jwt
from jwt import InvalidTokenError

from app.config import settings


def create_access_token(
    user_id: int,
    tenant_id: int,
    role: str,
) -> str:
    now = datetime.now(UTC)

    payload = {
        "sub": str(user_id),
        "tenant_id": tenant_id,
        "role": role,
        "iat": now,
        "exp": now + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        ),
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except InvalidTokenError as exc:
        raise ValueError("Invalid or expired access token") from exc