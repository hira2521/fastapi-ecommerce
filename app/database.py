from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.orm import Session

DATABASE_URL = "sqlite:///./store.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

Base = declarative_base()

#opens a new database session for each request and ensures it is closed after the request is done
def get_db():
    db = SessionLocal()
    try:
        yield db 
    finally:
        db.close()