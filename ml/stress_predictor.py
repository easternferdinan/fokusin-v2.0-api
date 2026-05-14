import joblib
import pandas as pd

with open("./ml/stress_rf_model.pkl", "rb") as f:
    model = joblib.load(f)

def predict_stress():
    features = {
        "academic_performance": 3,
        "depression": 10,
        "headaches": 2,
        "mental_health_history": 0,
        "self_esteem": 20,
        "sleep_quality": 3,
        "social_support": 2,
        "study_load": 3,
    }

data = pd.DataFrame([{
    "self_esteem": 20,
    "mental_health_history": 0,
    "depression": 10,
    "headache": 2,
    "sleep_quality": 3,
    "academic_performance": 3,
    "study_load": 3,
    "social_support": 2
}])
    
print(model.predict(data))
print(model.predict_proba(data))
# print(model.n_features_in_)
# print(model.feature_names_in_)