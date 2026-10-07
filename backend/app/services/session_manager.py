
import json
from datetime import datetime, timezone

from app.database import SessionLocal
from app.models.database_models import (
    Interview,
    FeatureWindow,
    Analysis,
    Report,
)


def _session_to_dict(interview, db):
    feature_rows = (
        db.query(FeatureWindow)
        .filter(
            FeatureWindow.interview_id == interview.interview_id
        )
        .order_by(
            FeatureWindow.window_number.asc()
        )
        .all()
    )

    analysis_rows = (
        db.query(Analysis)
        .filter(
            Analysis.interview_id == interview.interview_id
        )
        .order_by(
            Analysis.id.asc()
        )
        .all()
    )

    features = []

    for row in feature_rows:
        try:
            features.append(
                json.loads(row.feature_data)
            )
        except Exception:
            features.append({})

    analyses = []

    for row in analysis_rows:
        try:
            analyses.append(
                json.loads(row.analysis_data)
            )
        except Exception:
            analyses.append({})

    return {
        "interview_id": interview.interview_id,
        "name": interview.candidate_name,
        "email": interview.candidate_email,
        "role": interview.role,
        "started_at": (
            interview.started_at.isoformat()
            if interview.started_at
            else None
        ),
        "ended_at": (
            interview.ended_at.isoformat()
            if interview.ended_at
            else None
        ),
        "status": interview.status,
        "features": features,
        "analysis": analyses,
    }


def create_session(
    interview_id,
    name,
    email,
    role,
):
    db = SessionLocal()

    try:
        interview = (
            db.query(Interview)
            .filter(
                Interview.interview_id == interview_id
            )
            .first()
        )

        if interview is None:
            return None

        interview.candidate_name = name
        interview.candidate_email = email
        interview.role = role
        interview.status = "active"
        interview.started_at = datetime.now(timezone.utc)
        interview.ended_at = None

        db.commit()
        db.refresh(interview)

        return _session_to_dict(
            interview,
            db,
        )

    finally:
        db.close()


def get_session(interview_id):
    db = SessionLocal()

    try:
        interview = (
            db.query(Interview)
            .filter(
                Interview.interview_id == interview_id
            )
            .first()
        )

        if interview is None:
            return None

        return _session_to_dict(
            interview,
            db,
        )

    finally:
        db.close()


def add_features(
    interview_id,
    features,
):
    db = SessionLocal()

    try:
        interview = (
            db.query(Interview)
            .filter(
                Interview.interview_id == interview_id
            )
            .first()
        )

        if interview is None:
            return None

        existing_count = (
            db.query(FeatureWindow)
            .filter(
                FeatureWindow.interview_id == interview_id
            )
            .count()
        )

        row = FeatureWindow(
            interview_id=interview_id,
            window_number=existing_count + 1,
            feature_data=json.dumps(
                features,
                default=str,
            ),
        )

        db.add(row)
        db.commit()

        return _session_to_dict(
            interview,
            db,
        )

    finally:
        db.close()


def add_analysis(
    interview_id,
    analysis,
):
    db = SessionLocal()

    try:
        interview = (
            db.query(Interview)
            .filter(
                Interview.interview_id == interview_id
            )
            .first()
        )

        if interview is None:
            return None

        row = Analysis(
            interview_id=interview_id,
            analysis_data=json.dumps(
                analysis,
                default=str,
            ),
        )

        db.add(row)
        db.commit()

        return _session_to_dict(
            interview,
            db,
        )

    finally:
        db.close()


def end_session(interview_id):
    db = SessionLocal()

    try:
        interview = (
            db.query(Interview)
            .filter(
                Interview.interview_id == interview_id
            )
            .first()
        )

        if interview is None:
            return None

        interview.status = "completed"
        interview.ended_at = datetime.now(
            timezone.utc
        )

        db.commit()
        db.refresh(interview)

        return _session_to_dict(
            interview,
            db,
        )

    finally:
        db.close()


def save_report(
    interview_id,
    report_data,
):
    db = SessionLocal()

    try:
        interview = (
            db.query(Interview)
            .filter(
                Interview.interview_id == interview_id
            )
            .first()
        )

        if interview is None:
            return None

        existing_report = (
            db.query(Report)
            .filter(
                Report.interview_id == interview_id
            )
            .first()
        )

        report_json = json.dumps(
            report_data,
            default=str,
        )

        if existing_report:
            existing_report.report_data = report_json
            existing_report.updated_at = datetime.now(
                timezone.utc
            )

        else:
            new_report = Report(
                interview_id=interview_id,
                report_data=report_json,
            )

            db.add(new_report)

        db.commit()

        return report_data

    finally:
        db.close()