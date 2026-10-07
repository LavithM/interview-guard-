from app.services.feature_window_service import (
    FeatureWindowService
)


window = FeatureWindowService()


# Simulate visual data from 3 video frames.

window.add_visual_features({
    "face_detected": True,
    "blink": 0,
    "gaze": 0.80,
    "head_pose": {
        "yaw": 2.0,
        "pitch": 4.0,
        "roll": 1.0,
    },
    "lip_movement": 0.15,
})

window.add_visual_features({
    "face_detected": True,
    "blink": 1,
    "gaze": 0.75,
    "head_pose": {
        "yaw": 3.0,
        "pitch": 5.0,
        "roll": 1.5,
    },
    "lip_movement": 0.20,
})

window.add_visual_features({
    "face_detected": True,
    "blink": 0,
    "gaze": 0.85,
    "head_pose": {
        "yaw": 1.0,
        "pitch": 3.0,
        "roll": 0.5,
    },
    "lip_movement": 0.18,
})


# Simulate audio data.

window.add_audio_features({
    "audio_level": 0.02,
    "speech_detected": True,
})

window.add_audio_features({
    "audio_level": 0.03,
    "speech_detected": True,
})


# Build one feature window.

result = window.build_window()


print()
print("Feature window:")
print("----------------")

print("Timestamp:", result["timestamp"])
print("Average gaze:", result["gaze"])
print("Blink count:", result["blink"])

print("Head pose:")
print("  Yaw:", result["head_pose"]["yaw"])
print("  Pitch:", result["head_pose"]["pitch"])
print("  Roll:", result["head_pose"]["roll"])

print("Lip movement:", result["lip_movement"])
print("Audio level:", result["audio_level"])
print("Speech detected:", result["speech_detected"])