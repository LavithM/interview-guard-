from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.services.auth_service import decode_access_token


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials

    try:
        payload = decode_access_token(token)

        return payload

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired access token",
        )


def require_admin(
    current_user=Depends(get_current_user),
):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )

    return current_user


def require_candidate(
    current_user=Depends(get_current_user),
):
    if current_user.get("role") != "candidate":
        raise HTTPException(
            status_code=403,
            detail="Candidate access required",
        )

    return current_user