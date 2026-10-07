from app.database import SessionLocal
from app.models.database_models import Report

db = SessionLocal()

reports = db.query(Report).all()

print("=== REPORTS IN DATABASE ===")

for report in reports:
    print("Report ID:", report.id)
    print("Interview ID:", report.interview_id)
    print("Created:", report.created_at)
    print("Updated:", report.updated_at)
    print("Report data:")
    print(report.report_data)
    print("------------------------------")

db.close()