from app.database import Base, engine

from app.models.database_models import (
    User,
    Interview,
    FeatureWindow,
    Analysis,
    Report,
)


def initialize_database():
    Base.metadata.create_all(bind=engine)

    print("InterviewGuard database initialized successfully.")
    print("Database file: interviewguard.db")


if __name__ == "__main__":
    initialize_database()
