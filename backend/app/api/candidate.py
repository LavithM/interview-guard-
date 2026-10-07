import hashlib

from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from pydantic import BaseModel

from app.database import SessionLocal

from app.models.database_models import (
    Interview,
    InterviewInvitation,
)

from app.services.auth_service import (
    create_access_token,
)

from app.services.auth_dependencies import (
    require_candidate,
)

from app.services.realtime_analysis_service import (
    RealtimeAnalysisService,
)

from app.services.session_manager import (
    create_session,
)

from app.api.interview import (
    realtime_services,
)


router = APIRouter(
    prefix="/candidate",
    tags=["Candidate"],
)


# ============================================================
# REQUEST MODELS
# ============================================================

class CandidateLoginRequest(BaseModel):
    invitation_token: str
    email: str


# ============================================================
# HELPER
# ============================================================

def hash_invitation_token(token: str) -> str:
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


# ============================================================
# CANDIDATE LOGIN
# ============================================================

@router.post("/login")
def candidate_login(
    data: CandidateLoginRequest,
):
    """
    Validate the interview invitation and create a
    candidate authentication token.
    """

    db = SessionLocal()

    try:

        token_hash = hash_invitation_token(
            data.invitation_token
        )

        invitation = (
            db.query(InterviewInvitation)
            .filter(
                InterviewInvitation.token_hash
                == token_hash
            )
            .first()
        )

        if invitation is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid interview invitation",
            )

        # ----------------------------------------------------
        # Check expiration
        # ----------------------------------------------------

        now = datetime.now(timezone.utc)

        expires_at = invitation.expires_at

        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(
                tzinfo=timezone.utc
            )

        if now > expires_at:
            raise HTTPException(
                status_code=401,
                detail="Interview invitation has expired",
            )

        # ----------------------------------------------------
        # Check invitation status
        # ----------------------------------------------------

        if invitation.status != "pending":
            raise HTTPException(
                status_code=400,
                detail=(
                    "Interview invitation is no longer available"
                ),
            )

        # ----------------------------------------------------
        # Check candidate email
        # ----------------------------------------------------

        if (
            data.email.lower().strip()
            != invitation.candidate_email.lower().strip()
        ):
            raise HTTPException(
                status_code=401,
                detail=(
                    "Candidate email does not match invitation"
                ),
            )

        # ----------------------------------------------------
        # Create candidate JWT
        # ----------------------------------------------------

        token = create_access_token(
            user_id=invitation.id,
            username=invitation.candidate_email,
            role="candidate",
        )

        return {
            "message": "Candidate login successful",

            "access_token": token,

            "token_type": "bearer",

            "candidate": {
                "name": invitation.candidate_name,

                "email": invitation.candidate_email,

                "role": invitation.role,

                "interview_id": (
                    invitation.interview_id
                ),
            },
        }

    finally:
        db.close()


# ============================================================
# GET CANDIDATE INTERVIEW
# ============================================================

@router.get("/interviews/{interview_id}")
def get_candidate_interview(
    interview_id: str,
    current_user=Depends(require_candidate),
):
    """
    Return only the candidate's interview information.

    No AI analysis is returned.
    """

    db = SessionLocal()

    try:

        interview = (
            db.query(Interview)
            .filter(
                Interview.interview_id
                == interview_id
            )
            .first()
        )

        if interview is None:
            raise HTTPException(
                status_code=404,
                detail="Interview not found",
            )

        # ----------------------------------------------------
        # Verify candidate ownership
        # ----------------------------------------------------

        candidate_email = (
            current_user.get(
                "username",
                "",
            )
            .lower()
            .strip()
        )

        interview_email = (
            interview.candidate_email
            .lower()
            .strip()
        )

        if candidate_email != interview_email:
            raise HTTPException(
                status_code=403,
                detail=(
                    "You are not allowed to access this interview"
                ),
            )

        return {
            "interview_id": (
                interview.interview_id
            ),

            "candidate_name": (
                interview.candidate_name
            ),

            "role": interview.role,

            "status": interview.status,
        }

    finally:
        db.close()


# ============================================================
# START CANDIDATE INTERVIEW
# ============================================================

@router.post("/interviews/{interview_id}/start")
def start_candidate_interview(
    interview_id: str,
    current_user=Depends(require_candidate),
):
    """
    Start the database interview AND the realtime
    session-manager interview using the SAME interview ID.
    """

    db = SessionLocal()

    try:

        # ----------------------------------------------------
        # Find interview
        # ----------------------------------------------------

        interview = (
            db.query(Interview)
            .filter(
                Interview.interview_id
                == interview_id
            )
            .first()
        )

        if interview is None:
            raise HTTPException(
                status_code=404,
                detail="Interview not found",
            )

        # ----------------------------------------------------
        # Verify candidate ownership
        # ----------------------------------------------------

        candidate_email = (
            current_user.get(
                "username",
                "",
            )
            .lower()
            .strip()
        )

        interview_email = (
            interview.candidate_email
            .lower()
            .strip()
        )

        if candidate_email != interview_email:
            raise HTTPException(
                status_code=403,
                detail=(
                    "You are not allowed to start this interview"
                ),
            )

        # ----------------------------------------------------
        # Completed interviews cannot restart
        # ----------------------------------------------------

        if interview.status == "completed":
            raise HTTPException(
                status_code=400,
                detail=(
                    "Interview has already been completed"
                ),
            )

        # ----------------------------------------------------
        # Find invitation
        # ----------------------------------------------------

        invitation = (
            db.query(InterviewInvitation)
            .filter(
                InterviewInvitation.interview_id
                == interview.id
            )
            .first()
        )

        # ----------------------------------------------------
        # Already active
        # ----------------------------------------------------

        if interview.status == "active":

            # Make sure realtime service exists
            if interview_id not in realtime_services:
                realtime_services[
                    interview_id
                ] = RealtimeAnalysisService()

            return {
                "message": "Interview already started",

                "interview_id": interview_id,

                "status": "active",

                "started_at": (
                    interview.started_at.isoformat()
                    if interview.started_at
                    else None
                ),
            }

        # ----------------------------------------------------
        # Create session-manager session
        #
        # THIS IS THE IMPORTANT FIX.
        #
        # interview.py expects get_session(interview_id)
        # to exist.
        # ----------------------------------------------------

        session = create_session(
            interview_id=interview_id,
            name=interview.candidate_name,
            email=interview.candidate_email,
            role=interview.role,
        )

        # ----------------------------------------------------
        # Start database interview
        # ----------------------------------------------------

        started_at = datetime.now(timezone.utc)

        interview.status = "active"

        interview.started_at = started_at

        # ----------------------------------------------------
        # Mark invitation active
        # ----------------------------------------------------

        if invitation is not None:
            invitation.status = "active"

        # ----------------------------------------------------
        # Save database
        # ----------------------------------------------------

        db.commit()

        # ----------------------------------------------------
        # Create realtime AI service
        # ----------------------------------------------------

        realtime_services[
            interview_id
        ] = RealtimeAnalysisService()

        return {
            "message": "Interview started successfully",

            "interview_id": interview_id,

            "status": "active",

            "started_at": started_at.isoformat(),
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()