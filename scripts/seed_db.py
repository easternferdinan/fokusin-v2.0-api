import sys
import os
from datetime import datetime, UTC, timedelta

# Add current directory to sys.path to allow importing from the project
# Add the parent directory to sys.path to allow importing from the root of the project
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session
from db.session import SessionLocal, engine, Base
from models import Member, Task, PomodoroSession, Notification, Report, StressAnalysis, Log
from enums.member_enums import MemberRole
from enums.task_enums import TaskCategory, TaskPriority
from enums.log_enums import LogLevel, LogEvent
from enums.pomodoro_enums import PomodoroStatus
from enums.stress_level import StressLevelEnum

def seed_db():
    print("Initializing database...")
    # This will create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    
    try:
        # 1. Create Members
        print("Seeding Members...")
        # Check if users already exist to avoid unique constraint errors
        existing_admin = db.query(Member).filter(Member.username == "admin").first()
        if existing_admin:
            print("Database already contains data. Skipping seeding to avoid duplicates.")
            return

        admin = Member(
            fullname="Admin User",
            username="admin",
            email="admin@example.com",
            password="adminpassword", # In real app, this should be hashed
            role=MemberRole.ADMIN,
            mental_health_history=False,
            academic_performance=0,
            social_support=0
        )
        
        user1 = Member(
            fullname="John Doe",
            username="johndoe",
            email="john@example.com",
            password="password123",
            role=MemberRole.USER,
            mental_health_history=False,
            academic_performance=9,
            social_support=8
        )
        
        user2 = Member(
            fullname="Jane Smith",
            username="janesmith",
            email="jane@example.com",
            password="password123",
            role=MemberRole.USER,
            mental_health_history=True,
            academic_performance=6,
            social_support=5
        )
        
        db.add_all([admin, user1, user2])
        db.commit()
        db.refresh(user1)
        db.refresh(user2)
        
        # 2. Create Tasks
        print("Seeding Tasks...")
        tasks_data = [
            {
                "title": "Complete AI Assignment",
                "description": "Finish the neural network implementation",
                "category": TaskCategory.KULIAH,
                "priority": TaskPriority.TINGGI,
                "target_duration": 120,
                "deadline": datetime.now(UTC) + timedelta(days=2),
                "user_id": user1.user_id
            },
            {
                "title": "Project Brainstorming",
                "description": "Discuss new features for the task tracker",
                "category": TaskCategory.PROYEK,
                "priority": TaskPriority.SEDANG,
                "target_duration": 60,
                "deadline": datetime.now(UTC) + timedelta(days=5),
                "user_id": user1.user_id
            },
            {
                "title": "Study for Midterms",
                "description": "Read chapters 1 to 5 of the textbook",
                "category": TaskCategory.KULIAH,
                "priority": TaskPriority.TINGGI,
                "target_duration": 180,
                "deadline": datetime.now(UTC) + timedelta(days=7),
                "user_id": user2.user_id
            }
        ]
        
        db_tasks = [Task(**task) for task in tasks_data]
        db.add_all(db_tasks)
        
        # 3. Create Pomodoro Sessions
        print("Seeding Pomodoro Sessions...")
        pomodoros = [
            PomodoroSession(
                user_id=user1.user_id,
                title="Deep Work: AI",
                status=PomodoroStatus.STOPPED,
                session_start=datetime.now(UTC) - timedelta(hours=2),
                session_end=datetime.now(UTC) - timedelta(hours=1, minutes=35),
                elapsed_time=1500, # 25 mins
                duration=25,
                break_duration=5,
                completed=True
            ),
            PomodoroSession(
                user_id=user2.user_id,
                title="Math Study",
                status=PomodoroStatus.PAUSED,
                session_start=datetime.now(UTC) - timedelta(hours=1),
                session_end=datetime.now(UTC) - timedelta(minutes=45),
                elapsed_time=900, # 15 mins
                duration=25,
                break_duration=5,
                completed=False
            )
        ]
        db.add_all(pomodoros)
        
        # 4. Create Stress Analysis
        print("Seeding Stress Analysis...")
        stress_records = [
            StressAnalysis(
                user_id=user1.user_id,
                self_esteem=8,
                depression=2,
                headache=1,
                sleep_quality=7,
                study_load=3,
                stress_level=StressLevelEnum.SEDANG
            ),
            StressAnalysis(
                user_id=user2.user_id,
                self_esteem=5,
                depression=5,
                headache=4,
                sleep_quality=4,
                study_load=8,
                stress_level=StressLevelEnum.TINGGI
            )
        ]
        db.add_all(stress_records)
        
        # 5. Create Notifications
        print("Seeding Notifications...")
        notifications = [
            Notification(
                user_id=user1.user_id,
                message="Welcome to AI Task Tracker!",
                is_read=True
            ),
            Notification(
                user_id=user1.user_id,
                message="Your task 'Complete AI Assignment' is due in 2 days.",
                is_read=False
            )
        ]
        db.add_all(notifications)
        
        # 6. Create Reports
        print("Seeding Reports...")
        reports = [
            Report(
                user_id=user1.user_id,
                title="Weekly Productivity Report",
                report_type="weekly",
                period="2024-W19",
                content="You completed 5 tasks this week.",
                description="Summary of tasks and focus time.",
                file_name="report_user1_w19.pdf",
                generated_at=datetime.now(UTC)
            )
        ]
        db.add_all(reports)
        
        # 7. Create Logs
        print("Seeding Logs...")
        logs = [
            Log(
                user_id=user1.user_id,
                level=LogLevel.INFO,
                event_type=LogEvent.USER_LOGIN,
                message="User John Doe logged in.",
                extra_data={"ip_address": "192.168.1.10", "browser": "Chrome"}
            ),
            Log(
                user_id=user1.user_id,
                level=LogLevel.INFO,
                event_type=LogEvent.TASK_CREATED,
                message="Created task 'Complete AI Assignment'.",
                extra_data={"task_id": str(db_tasks[0].task_id)}
            ),
            Log(
                user_id=user2.user_id,
                level=LogLevel.WARNING,
                event_type=LogEvent.SYSTEM_ERROR,
                message="Failed to sync Pomodoro session due to network timeout.",
                extra_data={"error_code": 504}
            )
        ]
        db.add_all(logs)
        
        db.commit()
        print("Database seeded successfully!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
