import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.stress_predictor import get_predictor

def test_predictor():
    try:
        predictor = get_predictor()
        test_features = {
            "self_esteem": 20,
            "mental_health_history": 0,
            "depression": 10,
            "headache": 2,
            "sleep_quality": 3,
            "academic_performance": 3,
            "study_load": 3,
            "social_support": 2
        }
        
        prediction = predictor.predict(test_features)
        print(f"Prediction successful! Stress Level: {prediction}")
        return True
    except Exception as e:
        print(f"Prediction failed: {e}")
        return False

if __name__ == "__main__":
    if test_predictor():
        sys.exit(0)
    else:
        sys.exit(1)
