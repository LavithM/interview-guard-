import requests
import time


BASE_URL = "http://127.0.0.1:8000"


# ---------------------------------------------------------
# START INTERVIEW
# ---------------------------------------------------------

print()
print("========================================")
print("STARTING MULTI-WINDOW TEST")
print("========================================")

response = requests.post(
    f"{BASE_URL}/interview/start",
    json={
        "name": "Multi Window Test",
        "email": "multi@test.com",
        "role": "Software Engineer",
    }
)

if response.status_code != 200:

    print(response.text)

    raise SystemExit(
        "Could not start interview"
    )

data = response.json()

interview_id = (
    data["session"]["interview_id"]
)

print(
    "Interview ID:",
    interview_id
)


# ---------------------------------------------------------
# CREATE MULTIPLE WINDOWS
# ---------------------------------------------------------

NUMBER_OF_WINDOWS = 5


for window_number in range(
    1,
    NUMBER_OF_WINDOWS + 1
):

    print()
    print("========================================")
    print(
        f"WINDOW {window_number}"
    )
    print("========================================")

    # -----------------------------------------------------
    # CAMERA
    # -----------------------------------------------------

    with open(
        "test_face.jpg",
        "rb"
    ) as image_file:

        response = requests.post(
            f"{BASE_URL}/interview/"
            f"{interview_id}/frame",

            files={
                "file": (
                    "test_face.jpg",
                    image_file,
                    "image/jpeg"
                )
            }
        )

    if response.status_code != 200:

        print(response.text)

        raise SystemExit(
            "Camera processing failed"
        )

    print(
        "Camera:",
        response.json()["analysis"]
    )


    # -----------------------------------------------------
    # AUDIO
    # -----------------------------------------------------

    with open(
        "test_audio.wav",
        "rb"
    ) as audio_file:

        response = requests.post(
            f"{BASE_URL}/interview/"
            f"{interview_id}/audio",

            files={
                "file": (
                    "test_audio.wav",
                    audio_file,
                    "audio/wav"
                )
            }
        )

    if response.status_code != 200:

        print(response.text)

        raise SystemExit(
            "Audio processing failed"
        )

    print(
        "Audio:",
        response.json()["analysis"]
    )


    # -----------------------------------------------------
    # SPEECH + NLP
    # -----------------------------------------------------

    with open(
        "test_audio.wav",
        "rb"
    ) as audio_file:

        response = requests.post(
            f"{BASE_URL}/interview/"
            f"{interview_id}/speech",

            files={
                "file": (
                    "test_audio.wav",
                    audio_file,
                    "audio/wav"
                )
            }
        )

    if response.status_code != 200:

        print(response.text)

        raise SystemExit(
            "Speech processing failed"
        )

    speech_result = (
        response.json()["analysis"]
    )

    print(
        "Transcript:",
        speech_result[
            "transcript"
        ]
    )

    print(
        "NLP:",
        speech_result[
            "nlp"
        ]
    )


    # -----------------------------------------------------
    # BUILD WINDOW
    # -----------------------------------------------------

    response = requests.post(
        f"{BASE_URL}/interview/"
        f"{interview_id}/window"
    )

    if response.status_code != 200:

        print(response.text)

        raise SystemExit(
            "Window creation failed"
        )

    window = (
        response.json()["window"]
    )

    print()
    print(
        "Window summary:"
    )

    print(
        "Face:",
        window[
            "face_detected"
        ]
    )

    print(
        "Gaze:",
        window[
            "gaze"
        ]
    )

    print(
        "Blink:",
        window[
            "blink"
        ]
    )

    print(
        "Audio:",
        window[
            "audio_level"
        ]
    )

    print(
        "Speech:",
        window[
            "speech_detected"
        ]
    )

    print(
        "Transcript:",
        window[
            "transcript"
        ]
    )

    print(
        "Fusion:",
        window[
            "fusion"
        ]
    )


    # -----------------------------------------------------
    # WAIT BETWEEN WINDOWS
    # -----------------------------------------------------

    if window_number < NUMBER_OF_WINDOWS:

        print()
        print(
            "Waiting for next window..."
        )

        time.sleep(1)


# ---------------------------------------------------------
# GET SESSION
# ---------------------------------------------------------

print()
print("========================================")
print("CHECKING SESSION")
print("========================================")

response = requests.get(
    f"{BASE_URL}/interview/"
    f"{interview_id}"
)

if response.status_code != 200:

    print(response.text)

    raise SystemExit(
        "Could not retrieve session"
    )

session = response.json()[
    "session"
]

print(
    "Stored feature windows:",
    len(
        session[
            "features"
        ]
    )
)


# ---------------------------------------------------------
# END INTERVIEW
# ---------------------------------------------------------

print()
print("========================================")
print("ENDING INTERVIEW")
print("========================================")

response = requests.post(
    f"{BASE_URL}/interview/"
    f"{interview_id}/end"
)

if response.status_code != 200:

    print(response.text)

    raise SystemExit(
        "Could not end interview"
    )

report = response.json()[
    "report"
]


# ---------------------------------------------------------
# REPORT SUMMARY
# ---------------------------------------------------------

print()
print("========================================")
print("FINAL REPORT")
print("========================================")

analysis = report[
    "analysis"
]

print(
    "Total feature windows:",
    analysis[
        "total_feature_windows"
    ]
)

print(
    "Average gaze:",
    analysis[
        "average_gaze"
    ]
)

print(
    "Blink count:",
    analysis[
        "blink_count"
    ]
)

print(
    "Average head pose:",
    analysis[
        "average_head_pose"
    ]
)

print(
    "Average lip movement:",
    analysis[
        "average_lip_movement"
    ]
)

print(
    "Average audio level:",
    analysis[
        "average_audio_level"
    ]
)

print(
    "Speech percentage:",
    analysis[
        "speech_percentage"
    ]
)

print(
    "Face presence:",
    analysis[
        "face_presence_percentage"
    ]
)

print(
    "Indicator counts:",
    analysis[
        "indicator_counts"
    ]
)


# ---------------------------------------------------------
# TIMELINE
# ---------------------------------------------------------

print()
print("========================================")
print("TIMELINE")
print("========================================")

for item in report[
    "timeline"
]:

    print(
        f"Window {item['window_number']}: "
        f"timestamp={item['timestamp']}, "
        f"face={item['face_detected']}, "
        f"gaze={item['gaze']}, "
        f"speech={item['speech_detected']}"
    )


print()
print("========================================")
print("MULTI-WINDOW TEST PASSED")
print("========================================")