from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import UserDB
from app.auth import hash_password

def create_admin():
    db: Session = SessionLocal()

    email = "admin@example.com"
    password = "adminpassword"
    name = "Admin"


    existing = db.query(UserDB).filter(UserDB.email == email).first()
    if existing:
        print("Admin user already exists.")
        return
    
    admin = UserDB(
        name=name,
        email=email,
        password_hash=hash_password(password),
        is_admin=True
    )

    db.add(admin)
    db.commit()
    print("Admin user created successfully.")

if __name__ == "__main__":
    create_admin()