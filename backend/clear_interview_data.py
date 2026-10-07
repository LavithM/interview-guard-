from pathlib import Path

from app.database import SessionLocal
from app.models.database_models import (
    FeatureWindow,
    Analysis,
    Report,
    InterviewInvitation,
    Interview,
)


def clear_directory(directory: str):
    """
    Delete files inside a directory but keep the directory itself.
    """
    path = Path(directory)

    if not path.exists():
        return

    for item in path.iterdir():
        try:
            if item.is_file() or item.is_symlink():
                item.unlink()

            elif item.is_dir():
                import shutil
                shutil.rmtree(item)

        except Exception as e:
            print(f"Could not delete {item}: {e}")


def main():
    db = SessionLocal()

    try:
        print("Deleting interview database data...")

        # Delete child records first
        feature_windows_deleted = db.query(FeatureWindow).delete(
            synchronize_session=False
        )

        analyses_deleted = db.query(Analysis).delete(
            synchronize_session=False
        )

        reports_deleted = db.query(Report).delete(
            synchronize_session=False
        )

        invitations_deleted = db.query(InterviewInvitation).delete(
            synchronize_session=False
        )

        # Delete interviews last
        interviews_deleted = db.query(Interview).delete(
            synchronize_session=False
        )

        db.commit()

        print()
        print("Database cleanup complete.")
        print(f"Feature windows deleted: {feature_windows_deleted}")
        print(f"Analyses deleted:        {analyses_deleted}")
        print(f"Reports deleted:         {reports_deleted}")
        print(f"Invitations deleted:     {invitations_deleted}")
        print(f"Interviews deleted:      {interviews_deleted}")

    except Exception as e:
        db.rollback()
        print()
        print("ERROR: Database cleanup failed.")
        print(e)
        return

    finally:
        db.close()

    # ---------------------------------------------------------
    # Delete generated interview files
    # ---------------------------------------------------------

    print()
    print("Deleting generated interview files...")

    clear_directory("uploads")
    clear_directory("recordings")
    clear_directory("reports")

    print("Uploads cleared.")
    print("Recordings cleared.")
    print("Reports folder cleared.")

    print()
    print("======================================")
    print("ALL INTERVIEW DATA HAS BEEN CLEARED")
    print("======================================")
    print()
    print("The admin user has NOT been deleted.")


if __name__ == "__main__":
    main()
