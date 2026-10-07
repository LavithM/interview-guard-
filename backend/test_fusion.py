from app.services.fusion_service import (
    FusionService
)


fusion = FusionService()


test_window = {
    "timestamp": 10.5,

    "face_detected": True,

    "gaze": 0.55,

    "blink": 2,

    "head_pose": {
        "yaw": 3.2,
        "pitch": 4.1,
        "roll": 0.5,
    },

    "lip_movement": 0.13,

    "audio_level": 0.018,

    "speech_detected": True,

    "visual_samples": 10,

    "audio_samples": 2,
}


result = fusion.analyze_window(
    test_window
)


print()
print("Fusion analysis:")
print("----------------")

print(
    "Face:",
    result["face_status"]
)

print(
    "Gaze:",
    result["gaze"]
)

print(
    "Blink count:",
    result["blink_count"]
)

print(
    "Head pose:",
    result["head_pose"]
)

print(
    "Lip movement:",
    result["lip_movement"]
)

print(
    "Audio:",
    result["audio"]
)

print(
    "Speech:",
    result["speech"]
)

print(
    "Indicators:",
    result["indicators"]
)
