from app.services.model_feature_adapter import ModelFeatureAdapter


adapter = ModelFeatureAdapter()

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


features = adapter.adapt(
    runtime_features
)

print("\nModel feature vector:")
print("---------------------")

for name, value in features.items():
    print(f"{name}: {value}")

print("\nTotal features:", len(features))