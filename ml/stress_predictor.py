import joblib
import pandas as pd
import os
from pathlib import Path

class StressPredictor:
    def __init__(self, model_path: str = None):
        if model_path is None:
            # Default path relative to this file
            base_path = Path(__file__).parent
            model_path = base_path / "stress_rf_model.pkl"
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}")
            
        with open(model_path, "rb") as f:
            self.model = joblib.load(f)

    def predict(self, features: dict) -> int:
        """
        Predict stress level based on input features.
        Expected keys in features dict:
        - self_esteem
        - mental_health_history (bool or int 0/1)
        - depression
        - headache
        - sleep_quality
        - academic_performance
        - study_load
        - social_support
        """
        # Ensure mental_health_history is int (0 or 1) as expected by many models
        if "mental_health_history" in features:
            features["mental_health_history"] = 1 if features["mental_health_history"] else 0

        data = pd.DataFrame([features])
        
        # Ensure columns are in the correct order if the model expects it
        # Based on the original script's order:
        column_order = [
            "self_esteem", "mental_health_history", "depression", "headache",
            "sleep_quality", "academic_performance", "study_load", "social_support"
        ]
        
        # Reorder and filter to only required columns
        data = data[column_order]
        
        prediction = self.model.predict(data)
        return int(prediction[0])

# Global instance for easy access
predictor = None

def get_predictor():
    global predictor
    if predictor is None:
        predictor = StressPredictor()
    return predictor