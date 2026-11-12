from fastapi import APIRouter, Depends
from app.database import schemas, models
from app.api.deps import get_current_user, get_orchestrator
from app.orchestrator.brutality_orchestrator import BrutalityOrchestrator

router = APIRouter(prefix="/chat", tags=["Accountability Chat"])

@router.post("/message", response_model=schemas.ChatMessageResponse)
def send_chat_message(
    req: schemas.ChatMessageRequest,
    user: models.User = Depends(get_current_user),
    orchestrator: BrutalityOrchestrator = Depends(get_orchestrator)
):
    """
    Interactive chat powered by cross-session memory recall and Confront/Reality agent context.
    """
    result = orchestrator.chat_message(
        user_id=user.id,
        message=req.message,
        goal_id=req.goal_id
    )
    return result
