from collections.abc import Callable

from fastapi import Depends, HTTPException, status

from app.core.dependencies import get_current_user
from app.models import User

ROLE_PERMISSIONS: dict[str, set[str]] = {
    "Administrator": {
        "sales:read",
        "sales:analytics",
        "purchase:read",
        "purchase:analytics",
        "inventory:read",
        "inventory:procurement_read",
        "vendors:read",
        "customers:read",
        "dashboard:read",
        "ai:query",
    },
    "Sales Executive": {
        "sales:read",
        "sales:analytics",
        "inventory:read",
        "customers:read",
        "dashboard:read",
        "ai:query",
    },
    "Purchase Executive": {
        "purchase:read",
        "purchase:analytics",
        "inventory:read",
        "inventory:procurement_read",
        "vendors:read",
        "dashboard:read",
        "ai:query",
    },
    "Management": {
        "sales:read",
        "sales:analytics",
        "purchase:read",
        "purchase:analytics",
        "inventory:read",
        "inventory:procurement_read",
        "vendors:read",
        "customers:read",
        "dashboard:read",
        "ai:query",
    },
}


def require_permission(permission: str) -> Callable:
    def permission_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        allowed_permissions = ROLE_PERMISSIONS.get(
            current_user.role,
            set(),
        )

        if permission not in allowed_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource",
            )

        return current_user

    return permission_checker
