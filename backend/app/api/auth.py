from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.database import SessionLocal
from app.models.database_models import User
from app.services.auth_service import (
    verify_password,
    create_access_token,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(data: LoginRequest):

    db = SessionLocal()

    try:
        user = (
            db.query(User)
            .filter(User.username == data.username)
            .first()
        )

        if user is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password",
            )

        if not verify_password(
            data.password,
            user.password,
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password",
            )

        token = create_access_token(
            user_id=user.id,
            username=user.username,
            role=user.role,
        )

        return {
            "message": "Login successful",
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role,
            },
        }

    finally:
        db.close()