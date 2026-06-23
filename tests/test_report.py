from datetime import datetime, UTC, timedelta
from unittest.mock import MagicMock

import pytest

from services.report_service import get_stress_trend_service, get_recommendations_service
from schemas.report import PotentialStressFactorsResponse
from core.exceptions import DatabaseOperationError
from enums.stress_level import StressLevelEnum
from enums.report_enums import ReportRecommendationColorLabelEnum


def make_analysis(day_offset: int, stress_level: StressLevelEnum):
    a = MagicMock()
    a.created_at = datetime.now(UTC) - timedelta(days=day_offset)
    a.stress_level = stress_level
    return a


class TestGetStressTrendService:
    def test_period_harian(self, mock_db):
        records = [
            make_analysis(0, StressLevelEnum.RENDAH),
            make_analysis(1, StressLevelEnum.SEDANG),
            make_analysis(2, StressLevelEnum.TINGGI),
        ]
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = records

        result = get_stress_trend_service(mock_db, MagicMock(), "harian")
        assert len(result.labels) == 7
        assert len(result.values) == 7
        assert all(isinstance(v, float) for v in result.values)

    def test_period_mingguan(self, mock_db):
        records = [
            make_analysis(0, StressLevelEnum.RENDAH),
            make_analysis(7, StressLevelEnum.SEDANG),
            make_analysis(14, StressLevelEnum.TINGGI),
            make_analysis(21, StressLevelEnum.RENDAH),
        ]
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = records

        result = get_stress_trend_service(mock_db, MagicMock(), "mingguan")
        assert len(result.labels) == 4
        assert len(result.values) == 4

    def test_period_bulanan(self, mock_db):
        """Create records spanning multiple months."""
        today = datetime.now(UTC)
        records = [
            make_analysis(0, StressLevelEnum.SEDANG),
            make_analysis(35, StressLevelEnum.TINGGI),
            make_analysis(70, StressLevelEnum.RENDAH),
            make_analysis(100, StressLevelEnum.SEDANG),
            make_analysis(130, StressLevelEnum.TINGGI),
            make_analysis(160, StressLevelEnum.RENDAH),
        ]
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = records

        result = get_stress_trend_service(mock_db, MagicMock(), "bulanan")
        assert len(result.labels) == 6
        assert len(result.values) == 6

    def test_invalid_period_raises_error(self, mock_db):
        with pytest.raises(DatabaseOperationError):
            get_stress_trend_service(mock_db, MagicMock(), "tahunan")

    def test_empty_data_returns_zeros(self, mock_db):
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []

        result = get_stress_trend_service(mock_db, MagicMock(), "harian")
        assert len(result.values) == 7
        assert all(v == 0.0 for v in result.values)


class TestGetRecommendationsService:
    def test_all_tinggi_returns_three_danger(self):
        factors = PotentialStressFactorsResponse(
            deadline_is_tomorrow_tasks="tinggi",
            piling_up_tasks="tinggi",
            sleep_quality="buruk",
        )
        result = get_recommendations_service(MagicMock(), MagicMock(), factors)
        assert len(result) == 3
        for r in result:
            assert r.color_label == ReportRecommendationColorLabelEnum.DANGER

    def test_all_sedang_returns_three_warning(self):
        factors = PotentialStressFactorsResponse(
            deadline_is_tomorrow_tasks="sedang",
            piling_up_tasks="sedang",
            sleep_quality="sedang",
        )
        result = get_recommendations_service(MagicMock(), MagicMock(), factors)
        assert len(result) == 3
        for r in result:
            assert r.color_label == ReportRecommendationColorLabelEnum.WARNING

    def test_all_baik_returns_one_success(self):
        factors = PotentialStressFactorsResponse(
            deadline_is_tomorrow_tasks="rendah",
            piling_up_tasks="rendah",
            sleep_quality="baik",
        )
        result = get_recommendations_service(MagicMock(), MagicMock(), factors)
        assert len(result) == 1
        assert result[0].color_label == ReportRecommendationColorLabelEnum.SUCCESS

    def test_deadline_tinggi_others_normal(self):
        factors = PotentialStressFactorsResponse(
            deadline_is_tomorrow_tasks="tinggi",
            piling_up_tasks="rendah",
            sleep_quality="baik",
        )
        result = get_recommendations_service(MagicMock(), MagicMock(), factors)
        assert len(result) == 1
        assert result[0].subject == "deadline_is_tomorrow_tasks"
        assert result[0].color_label == ReportRecommendationColorLabelEnum.DANGER

    def test_only_sleep_buruk(self):
        factors = PotentialStressFactorsResponse(
            deadline_is_tomorrow_tasks="rendah",
            piling_up_tasks="rendah",
            sleep_quality="buruk",
        )
        result = get_recommendations_service(MagicMock(), MagicMock(), factors)
        assert len(result) == 1
        assert result[0].subject == "sleep_quality"
        assert result[0].color_label == ReportRecommendationColorLabelEnum.DANGER
