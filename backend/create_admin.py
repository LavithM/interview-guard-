from app.database import Base, engine, SessionLocal
from app.models.database_models import User
from app.services.auth_service import hash_password


Base.metadata.create_all(bind=engine)


db = SessionLocal()

try:
    username = "admin"
    password = "admin123"
    role = "admin"

    existing_user = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if existing_user:
        print("Admin user already exists.")
    else:
        admin = User(
            username=username,
            password=hash_password(password),
            role=role,
        )

        db.add(admin)
        db.commit()

        print("Admin user created successfully.")
        print("Username:", username)
        print("Password:", password)

finally:
    db.close()