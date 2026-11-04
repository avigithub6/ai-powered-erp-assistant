
import logging
from time import perf_counter

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.ai.orchestrator import AIOrchestrator
from app.core.dependencies import get_current_user
from app.core.permissions import ROLE_PERMISSIONS
from app.db.session import get_ai_db, get_db
from app.models import AIQueryAudit, User
from app.schemas.ai import AIQueryRequest, AIQueryResponse

router = APIRouter(prefix="/ai", tags=["AI Assistant"])

logger = logging.getLogger(__name__)


@router.post("/query", response_model=AIQueryResponse)
async def query_ai(
    request: AIQueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_ai_db),
    audit_db: Session = Depends(get_db),
):
    start_time = perf_counter()

    allowed_permissions = ROLE_PERMISSIONS.get(
        current_user.role,
        set(),
    )

    # Record authenticated users' permission-denied attempts.
    if "ai:query" not in allowed_permissions:
        audit_record = AIQueryAudit(
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            question=request.question,
            selected_tool=None,
            source=None,
            status="denied",
            execution_time_ms=int(
                (perf_counter() - start_time) * 1000
            ),
            error_type="PermissionDenied",
        )

        try:
            audit_db.add(audit_record)
            audit_db.commit()

        except Exception:
            audit_db.rollback()
            logger.exception(
                "Permission-denied AI audit log could not be saved"
            )

            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI audit logging is temporarily unavailable",
            ) from None

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )

    response = None
    status_value = "success"
    error_type = None

    try:
        orchestrator = AIOrchestrator()

        response = await orchestrator.query(
            question=request.question,
            current_user=current_user,
            db=db,
        )

    except Exception as exc:
        status_value = "failed"
        error_type = type(exc).__name__
        logger.exception("AI query execution failed")
        raise

    finally:
        execution_time_ms = int(
            (perf_counter() - start_time) * 1000
        )

        audit_record = AIQueryAudit(
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            question=request.question,
            selected_tool=(
                response.tool_used if response else None
            ),
            source=response.source if response else None,
            status=status_value,
            execution_time_ms=execution_time_ms,
            error_type=error_type,
        )

        try:
            audit_db.add(audit_record)
            audit_db.commit()

        except Exception:
            audit_db.rollback()
            logger.exception("AI audit log could not be saved")

            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI audit logging is temporarily unavailable",
            ) from None

    return response
