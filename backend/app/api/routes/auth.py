from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database import repositories, schemas, models
from app.core import security
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=schemas.Token, status_code=status.HTTP_201_CREATED)
def register(req: schemas.UserRegister, db: Session = Depends(get_db)):
    repo = repositories.UserRepository(db)
    existing = repo.get_by_email(req.email)
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    hashed_pw = security.get_password_hash(req.password)
    user = repo.create(email=req.email, hashed_password=hashed_pw, full_name=req.full_name)

    token = security.create_access_token({"sub": user.id, "email": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/login", response_model=schemas.Token)
def login(req: schemas.UserLogin, db: Session = Depends(get_db)):
    repo = repositories.UserRepository(db)
    user = repo.get_by_email(req.email)
    if not user or not security.verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    token = security.create_access_token({"sub": user.id, "email": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=schemas.UserResponse)
def get_me(user: models.User = Depends(get_current_user)):
    return user
