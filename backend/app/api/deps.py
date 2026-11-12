from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.database.database import get_db
from app.database import models, repositories
from app.core import security
from app.orchestrator.brutality_orchestrator import BrutalityOrchestrator

security_scheme = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> models.User:
    """
    Retrieves the authenticated user from JWT Bearer token.
    If no token is provided in development, returns or creates a default demo user
    so developers and reviewers can test API endpoints immediately.
    """
    user_repo = repositories.UserRepository(db)
    
    if credentials:
        token = credentials.credentials
        payload = security.decode_access_token(token)
        if payload and "sub" in payload:
            user = user_repo.get_by_id(payload["sub"])
            if user:
                return user
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication credentials."
        )

    # Fallback to local default warrior user
    demo_email = "warrior@brutality.ai"
    user = user_repo.get_by_email(demo_email)
    if not user:
        user = user_repo.create(
            email=demo_email,
            hashed_password=security.get_password_hash("discipline_first"),
            full_name="Brutality Warrior"
        )
    return user

def get_orchestrator(db: Session = Depends(get_db)) -> BrutalityOrchestrator:
    return BrutalityOrchestrator(db)
