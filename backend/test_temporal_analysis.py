from app.services.temporal_analysis_service import (
    TemporalAnalysisService
)


windows = [
    {
        "face_detected": True,
        "gaze": 0.70,
        "head_pose": {
            "yaw": 2,
            "pitch": 3,
            "roll": 1,
        },
        "speech_detected": True,
        "blink": 1,
    },

    {
        "face_detected": True,
        "gaze": 0.35,
        "head_pose": {
            "yaw": 30,
            "pitch": 2,
            "roll": 1,
        },
        "speech_detected": True,
        "blink": 0,
    },

    {
        "face_detected": False,
        "gaze": 0.0,
        "head_pose": {
            "yaw": 0,
            "pitch": 0,
            "roll": 0,
        },
        "speech_detected": False,
        "blink": 0,
    },

    {
        "face_detected": True,
        "gaze": 0.30,
        "head_pose": {
            "yaw": 35,
            "pitch": 3,
            "roll": 2,
        },
        "speech_detected": True,
        "blink": 1,
    },

    {
        "face_detected": True,
        "gaze": 0.75,
        "head_pose": {
            "yaw": 1,
            "pitch": 2,
            "roll": 1,
        },
        "speech_detected": True,
        "blink": 0,
    },
]


service = TemporalAnalysisService()

result = service.analyze(windows)

print("\nTEMPORAL ANALYSIS")
print("-------------------------")

for key, value in result.items():
    print(f"{key}: {value}")