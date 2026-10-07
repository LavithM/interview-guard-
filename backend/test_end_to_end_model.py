from app.services.model_feature_adapter import ModelFeatureAdapter
from app.services.model_prediction_service import ModelPredictionService


adapter = ModelFeatureAdapter()
model_service = ModelPredictionService()


runtime_features = {
    "face_detected": True,
    "face_conf": 0.9,

    "head_pose": {
        "pitch": 0.1,
        "yaw": 0.05,
        "roll": 0.02,
    },

    "gaze": {
        "horizontal": 0.5,
        "vertical": 0.5,
        "gaze_on_script": 0.0,
        "gaze_direction": 0,
        "pupil_left_x": 0.5,
        "pupil_left_y": 0.5,
        "pupil_right_x": 0.5,
        "pupil_right_y": 0.5,
    },

    "object_detection": {
        "person_count": 1,
        "mobile_phone_detected": False,
        "mobile_phone_confidence": 0.0,
    },

    "hand_detection": {
        "hand_count": 2,
        "hand_obj_interaction": 0,
    },
}


# Step 1: Convert runtime features into model features
model_features = adapter.adapt(runtime_features)

print("\nModel features:")
print("----------------")

for name, value in model_features.items():
    print(f"{name}: {value}")


# Step 2: Send features into trained XGBoost model
prediction = model_service.predict(model_features)

print("\nModel prediction:")
print("-----------------")
print(prediction)