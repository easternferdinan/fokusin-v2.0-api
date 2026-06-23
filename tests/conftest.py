import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

os.environ.setdefault("DATABASE_URL", "sqlite:///test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-1234567890")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")

from unittest.mock import MagicMock, patch
from datetime import datetime, UTC, timedelta
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from models.member import Member
from models.task import Task
from models.pomodoro_session import PomodoroSession
from models.stress_analysis import StressAnalysis
from enums.member_enums import MemberRole
from enums.task_enums import TaskCategory, TaskPriority
from enums.pomodoro_enums import PomodoroStatus
from enums.stress_level import StressLevelEnum


@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)


@pytest.fixture
def mock_user():
    user = MagicMock(spec=Member)
    user.user_id = uuid4()
    user.fullname = "Test User"
    user.username = "testuser"
    user.email = "test@example.com"
    user.password = "$argon2id$v=19$m=65536,t=3,p=4$hashedpassword"
    user.role = MemberRole.MAHASISWA
    user.mental_health_history = False
    user.academic_performance = 3
    user.social_support = 2
    return user


@pytest.fixture
def mock_task():
    task = MagicMock(spec=Task)
    task.task_id = uuid4()
    task.user_id = uuid4()
    task.title = "Test Task"
    task.target_duration = 60
    task.priority = TaskPriority.SEDANG
    task.deadline = datetime.now(UTC) + timedelta(days=5)
    task.completed = True
    task.completed_at = datetime.now(UTC)
    return task


@pytest.fixture
def mock_pomodoro_session():
    session = MagicMock(spec=PomodoroSession)
    session.pomodoro_id = uuid4()
    session.user_id = uuid4()
    session.status = PomodoroStatus.ACTIVE
    session.session_start = datetime.now(UTC)
    session.elapsed_time = 1500
    return session


@pytest.fixture
def mock_stress_analysis():
    analysis = MagicMock(spec=StressAnalysis)
    analysis.analysis_id = uuid4()
    analysis.user_id = uuid4()
    analysis.self_esteem = 15
    analysis.depression = 8
    analysis.headache = 2
    analysis.sleep_quality = 3
    analysis.study_load = 3
    analysis.stress_level = StressLevelEnum.SEDANG
    analysis.created_at = datetime.now(UTC)
    return analysis
