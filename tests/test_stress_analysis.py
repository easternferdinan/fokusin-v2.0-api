from datetime import datetime, UTC, timedelta
from unittest.mock import MagicMock

import pytest

from services.stress_analysis_service import (
    calculate_study_load_service,
    create_stress_analysis_service,
    check_stress_analysis_requirements_service,
)
from schemas.stress_analysis import StressAnalysisCreateRequest
from enums.task_enums import TaskPriority
from enums.stress_level import StressLevelEnum


def make_task(priority: TaskPriority, deadline_delta_days: int, target_duration: int = 60):
    task = MagicMock()
    task.priority = priority
    task.deadline = datetime.now(UTC) + timedelta(days=deadline_delta_days)
    task.target_duration = target_duration
    return task


class TestCalculateStudyLoadService:
    def test_no_tasks_done_today(self, mock_db, mocker):
        mocker.patch(
            "services.stress_analysis_service.get_tasks_done_today_service",
            return_value=[],
        )
        result = calculate_study_load_service(mock_db, MagicMock())
        assert result == 1

    def test_no_avg_elapsed(self, mock_db, mocker):
        task = make_task(TaskPriority.RENDAH, 5, 60)
        mocker.patch(
            "services.stress_analysis_service.get_tasks_done_today_service",
            return_value=[task],
        )
        mock_db.query.return_value.filter.return_value.scalar.return_value = None

        result = calculate_study_load_service(mock_db, MagicMock())
        assert result == 1

    def test_pomodoro_equivalent_le_1_5(self, mock_db, mocker):
        task = make_task(TaskPriority.RENDAH, 5, 10)
        mocker.patch(
            "services.stress_analysis_service.get_tasks_done_today_service",
            return_value=[task],
        )
        mock_db.query.return_value.filter.return_value.scalar.return_value = 60
        # total_weighted = 10 * 1.0 * 1.0 = 10
        # pomodoro_equivalent = 10 / 60 = 0.167 <= 1.5 -> return 1
        result = calculate_study_load_service(mock_db, MagicMock())
        assert result == 1

    def test_pomodoro_equivalent_gt_1_5_le_3_5(self, mock_db, mocker):
        task = make_task(TaskPriority.SEDANG, 5, 120)
        mocker.patch(
            "services.stress_analysis_service.get_tasks_done_today_service",
            return_value=[task],
        )
        mock_db.query.return_value.filter.return_value.scalar.return_value = 60
        # total_weighted = 120 * 1.3 * 1.0 = 156
        # pomodoro_equivalent = 156 / 60 = 2.6 -> 1.5 < 2.6 <= 3.5 -> return 2
        result = calculate_study_load_service(mock_db, MagicMock())
        assert result == 2

    def test_pomodoro_equivalent_gt_3_5_le_5_5(self, mock_db, mocker):
        task = make_task(TaskPriority.TINGGI, 5, 180)
        mocker.patch(
            "services.stress_analysis_service.get_tasks_done_today_service",
            return_value=[task],
        )
        mock_db.query.return_value.filter.return_value.scalar.return_value = 60
        # total_weighted = 180 * 1.6 * 1.0 = 288
        # pomodoro_equivalent = 288 / 60 = 4.8 -> 3.5 < 4.8 <= 5.5 -> return 3
        result = calculate_study_load_service(mock_db, MagicMock())
        assert result == 3

    def test_pomodoro_equivalent_gt_5_5_le_8_5(self, mock_db, mocker):
        task = make_task(TaskPriority.TINGGI, 2, 180)
        mocker.patch(
            "services.stress_analysis_service.get_tasks_done_today_service",
            return_value=[task],
        )
        mock_db.query.return_value.filter.return_value.scalar.return_value = 60
        # total_weighted = 180 * 1.6 * 1.2 = 345.6
        # pomodoro_equivalent = 345.6 / 60 = 5.76 -> 5.5 < 5.76 <= 8.5 -> return 4
        result = calculate_study_load_service(mock_db, MagicMock())
        assert result == 4

    def test_pomodoro_equivalent_gt_8_5(self, mock_db, mocker):
        task = make_task(TaskPriority.TINGGI, 0, 400)
        mocker.patch(
            "services.stress_analysis_service.get_tasks_done_today_service",
            return_value=[task],
        )
        mock_db.query.return_value.filter.return_value.scalar.return_value = 60
        # total_weighted = 400 * 1.6 * 1.8 = 1152
        # pomodoro_equivalent = 1152 / 60 = 19.2 > 8.5 -> return 5
        result = calculate_study_load_service(mock_db, MagicMock())
        assert result == 5

    def test_deadline_weight_gt_3_days(self, mock_db, mocker):
        task = make_task(TaskPriority.RENDAH, 10, 60)
        mocker.patch(
            "services.stress_analysis_service.get_tasks_done_today_service",
            return_value=[task],
        )
        mock_db.query.return_value.filter.return_value.scalar.return_value = 60
        # deadline_weight = 1.0
        result = calculate_study_load_service(mock_db, MagicMock())
        assert result == 1

    def test_deadline_weight_eq_2_days(self, mock_db, mocker):
        task = make_task(TaskPriority.RENDAH, 2, 120)
        mocker.patch(
            "services.stress_analysis_service.get_tasks_done_today_service",
            return_value=[task],
        )
        mock_db.query.return_value.filter.return_value.scalar.return_value = 60
        # deadline_weight = 1.2
        # total_weighted = 120 * 1.0 * 1.2 = 144
        # pomodoro_equivalent = 144 / 60 = 2.4 -> return 2
        result = calculate_study_load_service(mock_db, MagicMock())
        assert result == 2

    def test_deadline_weight_eq_1_day(self, mock_db, mocker):
        task = make_task(TaskPriority.SEDANG, 1, 120)
        mocker.patch(
            "services.stress_analysis_service.get_tasks_done_today_service",
            return_value=[task],
        )
        mock_db.query.return_value.filter.return_value.scalar.return_value = 60
        # deadline_weight = 1.5
        # total_weighted = 120 * 1.3 * 1.5 = 234
        # pomodoro_equivalent = 234 / 60 = 3.9 -> return 3
        result = calculate_study_load_service(mock_db, MagicMock())
        assert result == 3


class TestCreateStressAnalysisService:
    def test_create_stress_prediction_1(self, mock_db, mock_user, mocker):
        mocker.patch(
            "services.stress_analysis_service.calculate_study_load_service",
            return_value=3,
        )
        mock_predictor = mocker.patch("services.stress_analysis_service.get_predictor")
        mock_predictor.return_value.predict.return_value = 1

        data = StressAnalysisCreateRequest(
            self_esteem=20,
            depression=5,
            headache=1,
            sleep_quality=4,
        )
        result = create_stress_analysis_service(mock_db, data, mock_user)
        assert result.stress_level == StressLevelEnum.RENDAH

    def test_create_stress_prediction_3(self, mock_db, mock_user, mocker):
        mocker.patch(
            "services.stress_analysis_service.calculate_study_load_service",
            return_value=3,
        )
        mock_predictor = mocker.patch("services.stress_analysis_service.get_predictor")
        mock_predictor.return_value.predict.return_value = 3

        data = StressAnalysisCreateRequest(
            self_esteem=5,
            depression=18,
            headache=4,
            sleep_quality=1,
        )
        result = create_stress_analysis_service(mock_db, data, mock_user)
        assert result.stress_level == StressLevelEnum.TINGGI

    def test_create_stress_database_error_raises(self, mock_db, mock_user, mocker):
        mocker.patch(
            "services.stress_analysis_service.calculate_study_load_service",
            return_value=3,
        )
        mock_predictor = mocker.patch("services.stress_analysis_service.get_predictor")
        mock_predictor.return_value.predict.return_value = 2
        mock_db.add.side_effect = Exception("DB error")

        data = StressAnalysisCreateRequest(
            self_esteem=10,
            depression=10,
            headache=2,
            sleep_quality=2,
        )
        with pytest.raises(Exception):
            create_stress_analysis_service(mock_db, data, mock_user)


class TestCheckStressAnalysisRequirementsService:
    def test_all_requirements_met(self, mock_db, mocker):
        mocker.patch(
            "services.stress_analysis_service.get_tasks_done_today_service",
            return_value=[MagicMock()],
        )
        mocker.patch(
            "services.stress_analysis_service.get_today_pomodoro_minutes_service",
            return_value=30,
        )
        mocker.patch(
            "services.stress_analysis_service.get_today_stress_assesment_count_service",
            return_value=1,
        )
        result = check_stress_analysis_requirements_service(mock_db, MagicMock())
        assert result.task_done_today is True
        assert result.pomodoro_done_today is True
        assert result.stress_assesment_done_today is True

    def test_no_requirements_met(self, mock_db, mocker):
        mocker.patch(
            "services.stress_analysis_service.get_tasks_done_today_service",
            return_value=[],
        )
        mocker.patch(
            "services.stress_analysis_service.get_today_pomodoro_minutes_service",
            return_value=0,
        )
        mocker.patch(
            "services.stress_analysis_service.get_today_stress_assesment_count_service",
            return_value=0,
        )
        result = check_stress_analysis_requirements_service(mock_db, MagicMock())
        assert result.task_done_today is False
        assert result.pomodoro_done_today is False
        assert result.stress_assesment_done_today is False
