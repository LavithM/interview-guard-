from app.database import SessionLocal
from app.models.database_models import Interview

db = SessionLocal()

rows = db.query(Interview).order_by(Interview.id.desc()).all()

print("\n=== INTERVIEWS IN DATABASE ===")

for row in rows:
    print("ID:", row.id)
    print("Interview ID:", row.interview_id)
    print("Candidate:", row.candidate_name)
    print("Email:", row.candidate_email)
    print("Role:", row.role)
    print("Status:", row.status)
    print("Started:", row.started_at)
    print("------------------------------")

db.close()
