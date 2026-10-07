import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone
from urllib import request

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
)
from pydantic import BaseModel

from app.database import SessionLocal
from app.models.database_models import (
    Interview,
    InterviewInvitation,
    Report,
)
from app.services.auth_dependencies import require_admin


router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


# ============================================================
# CONFIGURATION
# ============================================================

FRONTEND_URL = os.getenv(
    "INTERVIEWGUARD_FRONTEND_URL"
)


# ============================================================
# REQUEST MODELS
# ============================================================

class CreateInterviewRequest(BaseModel):
    candidate_name: str
    candidate_email: str
    role: str


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def hash_invitation_token(token: str) -> str:
    """
    Hash the candidate invitation token before storing it.
    The raw token is only included in the candidate URL.
    """
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


def generate_interview_id() -> str:
    """
    Generate a readable InterviewGuard interview ID.
    Example:
    IG-20260924153020-A1B2C3
    """

    timestamp = datetime.now(
        timezone.utc
    ).strftime("%Y%m%d%H%M%S")

    random_part = secrets.token_hex(3).upper()

    return f"IG-{timestamp}-{random_part}"


# ============================================================
# CREATE INTERVIEW
# ============================================================

@router.post("/interviews")
def create_interview(
    request: Request,
    data: CreateInterviewRequest,
    current_user=Depends(require_admin),
):
    """
    Admin creates a new interview invitation.

    This creates:

    1. Interview database record
    2. Secure invitation token
    3. Candidate login link
    4. Interview invitation record
    """

    db = SessionLocal()

    try:

        # ----------------------------------------------------
        # Generate unique interview ID
        # ----------------------------------------------------

        interview_id = generate_interview_id()

        while (
            db.query(Interview)
            .filter(
                Interview.interview_id == interview_id
            )
            .first()
            is not None
        ):
            interview_id = generate_interview_id()

        # ----------------------------------------------------
        # Create interview
        # ----------------------------------------------------

        interview = Interview(
            interview_id=interview_id,
            candidate_name=data.candidate_name,
            candidate_email=data.candidate_email,
            role=data.role,
            status="pending",
        )

        db.add(interview)

        # Flush so interview.id is available
        db.flush()

        # ----------------------------------------------------
        # Generate secure candidate invitation token
        # ----------------------------------------------------

        raw_token = secrets.token_urlsafe(32)

        token_hash = hash_invitation_token(
            raw_token
        )

        expires_at = (
            datetime.now(timezone.utc)
            + timedelta(days=7)
        )

        # ----------------------------------------------------
        # Candidate link
        # ----------------------------------------------------

        if FRONTEND_URL:
            frontend_url = FRONTEND_URL.rstrip("/")
        else:
            host = request.headers.get("host", "")

            if ":" in host:
                hostname = host.rsplit(":", 1)[0]
            else:
                hostname = host

            frontend_url = f"http://{hostname}:5173"

        candidate_link = (
            f"{frontend_url}/candidate/login"
            f"?interview={interview_id}"
            f"&token={raw_token}"
        )

        # ----------------------------------------------------
        # Create invitation
        # ----------------------------------------------------

        invitation = InterviewInvitation(
            interview_id=interview.id,
            token_hash=token_hash,
            candidate_link=candidate_link,
            candidate_name=data.candidate_name,
            candidate_email=data.candidate_email,
            role=data.role,
            created_by=current_user.get("sub"),
            status="pending",
            expires_at=expires_at,
        )

        db.add(invitation)

        # ----------------------------------------------------
        # Save everything
        # ----------------------------------------------------

        db.commit()

        # Refresh database objects
        db.refresh(interview)
        db.refresh(invitation)

        # ----------------------------------------------------
        # Return response
        # ----------------------------------------------------

        return {
            "message": "Interview created successfully",

            "interview": {
                "id": interview.id,
                "interview_id": interview.interview_id,
                "candidate_name": interview.candidate_name,
                "candidate_email": interview.candidate_email,
                "role": interview.role,
                "status": interview.status,
                "started_at": interview.started_at,
                "ended_at": interview.ended_at,
            },

            "invitation": {
                "candidate_link": candidate_link,
                "expires_at": expires_at,
                "status": invitation.status,
            },
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ============================================================
# GET RECENT INTERVIEWS
# ============================================================

@router.get("/interviews/recent")
def get_recent_interviews(
    limit: int = 10,
    current_user=Depends(require_admin),
):
    """
    Return recent interviews for the admin dashboard.

    This endpoint also returns the permanent candidate_link
    stored in InterviewInvitation.

    The candidate link does NOT change when the admin dashboard
    refreshes.
    """

    # --------------------------------------------------------
    # Validate limit
    # --------------------------------------------------------

    if limit < 1:
        limit = 1

    if limit > 100:
        limit = 100

    # --------------------------------------------------------
    # Open database
    # --------------------------------------------------------

    db = SessionLocal()

    try:

        # ----------------------------------------------------
        # Get recent interviews
        # ----------------------------------------------------

        interviews = (
            db.query(Interview)
            .order_by(
                Interview.id.desc()
            )
            .limit(limit)
            .all()
        )

        # ----------------------------------------------------
        # Prepare response
        # ----------------------------------------------------

        results = []

        for interview in interviews:

            # ------------------------------------------------
            # Find invitation belonging to this interview
            # ------------------------------------------------

            invitation = (
                db.query(InterviewInvitation)
                .filter(
                    InterviewInvitation.interview_id
                    == interview.id
                )
                .first()
            )

            # ------------------------------------------------
            # IMPORTANT:
            #
            # This must be:
            #
            # results.append({
            #
            # NOT:
            #
            # results.append({
            #     {
            #         ...
            #     }
            # })
            #
            # The previous version caused:
            #
            # TypeError:
            # unhashable type: 'dict'
            # ------------------------------------------------

            results.append(
                {
                    "id": interview.id,

                    "interview_id": (
                        interview.interview_id
                    ),

                    "candidate_name": (
                        interview.candidate_name
                    ),

                    "candidate_email": (
                        interview.candidate_email
                    ),

                    "role": interview.role,

                    "status": interview.status,

                    "started_at": (
                        interview.started_at
                    ),

                    "ended_at": (
                        interview.ended_at
                    ),

                    "candidate_link": (
                        invitation.candidate_link
                        if invitation
                        else None
                    ),
                }
            )

        # ----------------------------------------------------
        # Return dashboard data
        # ----------------------------------------------------

        return {
            "count": len(results),
            "interviews": results,
        }

    finally:
        db.close()


# ============================================================
# GET RECENT REPORTS
# ============================================================

@router.get("/reports/recent")
def get_recent_reports(
    limit: int = 10,
    current_user=Depends(require_admin),
):
    """
    Return recent interview reports.

    Admin only.
    """

    # --------------------------------------------------------
    # Validate limit
    # --------------------------------------------------------

    if limit < 1:
        limit = 1

    if limit > 100:
        limit = 100

    db = SessionLocal()

    try:

        # ----------------------------------------------------
        # Get recent reports
        # ----------------------------------------------------

        reports = (
            db.query(Report)
            .order_by(
                Report.id.desc()
            )
            .limit(limit)
            .all()
        )

        results = []

        # ----------------------------------------------------
        # Build response
        # ----------------------------------------------------

        for report in reports:

            interview = (
                db.query(Interview)
                .filter(
                    Interview.id
                    == report.interview_id
                )
                .first()
            )

            results.append(
                {
                    "id": report.id,

                    "interview_id": (
                        interview.interview_id
                        if interview
                        else None
                    ),

                    "candidate_name": (
                        interview.candidate_name
                        if interview
                        else None
                    ),

                    "candidate_email": (
                        interview.candidate_email
                        if interview
                        else None
                    ),

                    "role": (
                        interview.role
                        if interview
                        else None
                    ),

                    "interview_status": (
                        interview.status
                        if interview
                        else None
                    ),

                    "report_data": (
                        report.report_data
                    ),

                    "created_at": (
                        report.created_at
                    ),

                    "updated_at": (
                        report.updated_at
                    ),
                }
            )

        return {
            "count": len(results),
            "reports": results,
        }

    finally:
        db.close()


# ============================================================
# GET ONE REPORT
# ============================================================

@router.get("/reports/{interview_id}")
def get_report(
    interview_id: str,
    current_user=Depends(require_admin),
):
    """
    Get the final report for one interview.

    Admin only.
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
        # Find report
        # ----------------------------------------------------

        report = (
            db.query(Report)
            .filter(
                Report.interview_id
                == interview.id
            )
            .first()
        )

        if report is None:
            raise HTTPException(
                status_code=404,
                detail="Report not found",
            )

        # ----------------------------------------------------
        # Return report
        # ----------------------------------------------------

        return {
            "id": report.id,

            "interview": {
                "id": interview.id,

                "interview_id": (
                    interview.interview_id
                ),

                "candidate_name": (
                    interview.candidate_name
                ),

                "candidate_email": (
                    interview.candidate_email
                ),

                "role": interview.role,

                "status": interview.status,

                "started_at": (
                    interview.started_at
                ),

                "ended_at": (
                    interview.ended_at
                ),
            },

            "report": {
                "report_data": (
                    report.report_data
                ),

                "created_at": (
                    report.created_at
                ),

                "updated_at": (
                    report.updated_at
                ),
            },
        }

    finally:
        db.close()