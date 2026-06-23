from pathlib import Path

import pytest

from ml.stress_predictor import StressPredictor, get_predictor


class TestStressPredictor:
    def test_predict_returns_int(self):
        predictor = StressPredictor()
        features = {
            "self_esteem": 20,
            "mental_health_history": 0,
            "depression": 10,
            "headache": 2,
            "sleep_quality": 3,
            "academic_performance": 3,
            "study_load": 3,
            "social_support": 2,
        }
        result = predictor.predict(features)
        assert isinstance(result, int)
        assert result in (1, 2, 3)

    def test_predict_with_bool_mental_health_true(self):
        predictor = StressPredictor()
        features = {
            "self_esteem": 20,
            "mental_health_history": True,
            "depression": 10,
            "headache": 2,
            "sleep_quality": 3,
            "academic_performance": 3,
            "study_load": 3,
            "social_support": 2,
        }
        result = predictor.predict(features)
        assert isinstance(result, int)

    def test_predict_with_bool_mental_health_false(self):
        predictor = StressPredictor()
        features = {
            "self_esteem": 20,
            "mental_health_history": False,
            "depression": 10,
            "headache": 2,
            "sleep_quality": 3,
            "academic_performance": 3,
            "study_load": 3,
            "social_support": 2,
        }
        result = predictor.predict(features)
        assert isinstance(result, int)

    def test_model_file_not_found_raises_error(self):
        with pytest.raises(FileNotFoundError):
            StressPredictor(model_path="/nonexistent/path/model.pkl")

    def test_singleton_get_predictor(self):
        p1 = get_predictor()
        p2 = get_predictor()
        assert p1 is p2
