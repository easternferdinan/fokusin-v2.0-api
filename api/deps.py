from typing import Generator
from db.session import SessionLocal

def get_db() -> Generator:
    """
    Dependency to provide a database session to API endpoints.
    Ensures the session is closed after the request is handled.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()