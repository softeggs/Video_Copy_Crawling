from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from backend.auth import create_access_token, hash_password, verify_password
from backend.database import get_db
from backend.dependencies import get_current_user
from backend.models import User
from backend.schemas import LoginRequest, LoginResponse, RegisterRequest, UserDTO

router = APIRouter(prefix="/auth", tags=["auth"])


def _to_user_dto(user: User) -> UserDTO:
    return UserDTO(
        user_id=str(user.id),
        username=user.username,
        display_name=user.display_name,
        table_id=user.table_id,
    )


@router.post("/register", response_model=LoginResponse)
def register(payload: RegisterRequest, db: Annotated[Session, Depends(get_db)]) -> LoginResponse:
    username = payload.username.strip()
    email = payload.email.strip().lower()
    display_name = payload.display_name.strip()

    existing = db.execute(
        select(User).where(or_(User.username == username, User.email == email))
    ).scalars().first()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username or email already exists")

    user = User(
        username=username,
        email=email,
        display_name=display_name,
        password_hash=hash_password(payload.password),
        table_id="",
        is_active=True,
        is_admin=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return LoginResponse(token=create_access_token(user.id), user=_to_user_dto(user))


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Annotated[Session, Depends(get_db)]) -> LoginResponse:
    username = payload.username.strip()

    user = db.execute(select(User).where(User.username == username)).scalars().first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

    return LoginResponse(token=create_access_token(user.id), user=_to_user_dto(user))


@router.get("/me", response_model=UserDTO)
def me(user: Annotated[User, Depends(get_current_user)]) -> UserDTO:
    return _to_user_dto(user)

