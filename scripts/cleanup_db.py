import sys
import os

# Add current directory to sys.path to allow importing from the project
# Add the parent directory to sys.path to allow importing from the root of the project
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session
from db.session import SessionLocal
from models import Member, Task, PomodoroSession, Notification, Report, StressAnalysis

def cleanup_db():
    print("Starting database cleanup...")
    db: Session = SessionLocal()
    
    try:
        # Delete data from tables in order to respect foreign key constraints
        # Child tables first, parent tables last
        
        print("Deleting Reports...")
        db.query(Report).delete()
        
        print("Deleting Notifications...")
        db.query(Notification).delete()
        
        print("Deleting Stress Analysis records...")
        db.query(StressAnalysis).delete()
        
        print("Deleting Pomodoro Sessions...")
        db.query(PomodoroSession).delete()
        
        print("Deleting Tasks...")
        db.query(Task).delete()
        
        print("Deleting Members...")
        db.query(Member).delete()
        
        db.commit()
        print("All data deleted successfully from the tables!")
        
    except Exception as e:
        print(f"Error during cleanup: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Optional: Ask for confirmation since this is destructive
    confirm = input("This will delete ALL data from the database tables. Are you sure? (y/n): ")
    if confirm.lower() == 'y':
        cleanup_db()
    else:
        print("Cleanup cancelled.")
