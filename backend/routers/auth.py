from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import create_access_token, hash_password, verify_password
from ..dependencies import get_current_user, get_db


router = APIRouter(prefix="/auth", tags=["auth"])


def _to_user_response(user: models.User) -> schemas.UserResponse:
    return schemas.UserResponse(
        user_id=str(user.id),
        username=user.username,
        display_name=user.display_name,
        table_id="",
    )


@router.post("/register", response_model=schemas.LoginResponse)
def register(payload: schemas.UserRegisterRequest, db: Session = Depends(get_db)) -> schemas.LoginResponse:
    user = models.User(
        username=payload.username.strip(),
        email=payload.email,
        password_hash=hash_password(payload.password),
        display_name=payload.display_name.strip(),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username or email already exists") from exc
    db.refresh(user)

    token = create_access_token(user.id)
    return schemas.LoginResponse(token=token, user=_to_user_response(user))


@router.post("/login", response_model=schemas.LoginResponse)
def login(payload: schemas.UserLoginRequest, db: Session = Depends(get_db)) -> schemas.LoginResponse:
    user = db.query(models.User).filter(models.User.username == payload.username.strip()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is disabled")

    token = create_access_token(user.id)
    return schemas.LoginResponse(token=token, user=_to_user_response(user))


@router.get("/me", response_model=schemas.UserResponse)
def me(current_user: models.User = Depends(get_current_user)) -> schemas.UserResponse:
    return _to_user_response(current_user)
