from sqlalchemy import text
from db.session import SessionLocal
import sys
import os

# Add the project root to sys.path to allow imports
sys.path.append(os.getcwd())


def test_connection():
    """
    Tests the database connection by executing a simple query.
    Returns True if successful, False otherwise.
    """
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False

if __name__ == "__main__":
    print("Testing database connection...")
    if test_connection():
        print("Success! Database connection is working.")
    else:
        print("Failed! Please check your DATABASE_URL and credentials.")
