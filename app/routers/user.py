import secrets
import asyncio
from typing import Optional

from fastapi import APIRouter, status, HTTPException, Depends, BackgroundTasks, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, schemas, utils
from ..database import get_db
from ..email import send_verification_email


def send_email_background(email: str, token: str):
    """Synchronous wrapper to send verification email in background"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(send_verification_email(email, token))
    finally:
        loop.close()


router = APIRouter()


@router.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
async def create_user(
    user: schemas.UserCreate,
    background_tasks: BackgroundTasks,   # ✅ NEW
    db: Session = Depends(get_db)
):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists"
        )

    hashed_password = utils.hash(user.password)

    # ✅ Generate a random token
    verification_token = secrets.token_urlsafe(32)

    new_user = models.User(**user.dict())
    new_user.password = hashed_password
    new_user.verification_token = verification_token  # ✅ save token

    db.add(new_user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists"
        )

    db.refresh(new_user)

    # ✅ Send email IN THE BACKGROUND — doesn't slow down the response
    background_tasks.add_task(
        send_email_background,
        email=new_user.email,
        token=verification_token
    )

    return new_user


@router.get("/users/verify", response_model=schemas.UserOut)
def verify_email(
    request: Request,
    token: Optional[str] = None,
    db: Session = Depends(get_db)
):
    verification_token = token

    if not verification_token:
        authorization = request.headers.get("Authorization")
        if authorization and authorization.lower().startswith("bearer "):
            verification_token = authorization.split(" ", 1)[1].strip()

    if not verification_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token is required. Use ?token=... or send it as a Bearer token."
        )

    # Find the user with this token
    user = db.query(models.User).filter(
        models.User.verification_token == verification_token
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired verification link"
        )

    if user.is_verified:
        return user

    # ✅ Mark as verified and clear the token
    user.is_verified = True
    user.verification_token = None
    db.commit()
    db.refresh(user)

    return user


@router.get('/users/{id}', response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User with id: {id} does not exist'
        )
    return user