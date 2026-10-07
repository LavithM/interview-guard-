import json

from fastapi import APIRouter, Depends, HTTPException

from app.database import SessionLocal
from app.models.database_models import Interview, Report
from app.services.auth_dependencies import require_admin

router = APIRouter(
    prefix="/admin",
    tags=["Admin Interviews"],
)


@router.get("/interviews")
def list_interviews(current_user=Depends(require_admin)):
    db = SessionLocal()
    try:
        rows = (
            db.query(Interview)
            .order_by(Interview.started_at.desc(), Interview.id.desc())
            .all()
        )

        return {
            "interviews": [
                {
                    "interview_id": row.interview_id,
                    "candidate_name": row.candidate_name,
                    "candidate_email": row.candidate_email,
                    "role": row.role,
                    "status": row.status,
                    "started_at": row.started_at.isoformat() if row.started_at else None,
                    "ended_at": row.ended_at.isoformat() if row.ended_at else None,
                }
                for row in rows
            ]
        }
    finally:
        db.close()


@router.get("/interviews/{interview_id}/report")
def get_interview_report(
    interview_id: str,
    current_user=Depends(require_admin),
):
    db = SessionLocal()
    try:
        interview = (
            db.query(Interview)
            .filter(Interview.interview_id == interview_id)
            .first()
        )

        if interview is None:
            raise HTTPException(status_code=404, detail="Interview not found")

        report_row = (
            db.query(Report)
            .filter(Report.interview_id == interview_id)
            .first()
        )

        report_data = {}
        if report_row:
            try:
                report_data = json.loads(report_row.report_data)
            except Exception:
                report_data = {}

        return {
            "interview_id": interview.interview_id,
            "candidate_name": interview.candidate_name,
            "candidate_email": interview.candidate_email,
            "role": interview.role,
            "status": interview.status,
            "started_at": interview.started_at.isoformat() if interview.started_at else None,
            "ended_at": interview.ended_at.isoformat() if interview.ended_at else None,
            "report": report_data,
        }
    finally:
        db.close()
