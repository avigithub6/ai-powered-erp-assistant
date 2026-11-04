from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ai.orchestrator import AIOrchestrator
from app.core.permissions import require_permission
from app.db.session import get_db
from app.models import User
from app.schemas.ai import AIQueryRequest, AIQueryResponse

router = APIRouter(prefix="/ai", tags=["AI Assistant"])


@router.post("/query", response_model=AIQueryResponse)
async def query_ai(
    request: AIQueryRequest,
    current_user: User = Depends(
        require_permission("ai:query")
    ),
    db: Session = Depends(get_db),
):
    orchestrator = AIOrchestrator()

    return await orchestrator.query(
        question=request.question,
        current_user=current_user,
        db=db,
    )