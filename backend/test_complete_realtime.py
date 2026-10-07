import requests


BASE_URL = "http://127.0.0.1:8000"


# ---------------------------------------------------------
# START INTERVIEW
# ---------------------------------------------------------

print()
print("========================================")
print("1. START INTERVIEW")
print("========================================")

response = requests.post(
    f"{BASE_URL}/interview/start",
    json={
        "name": "Realtime Test User",
        "email": "realtime@test.com",
        "role": "Software Engineer",
    }
)

print("Status:", response.status_code)

data = response.json()

print(data)

if response.status_code != 200:
    raise SystemExit(
        "Could not start interview"
    )

interview_id = data[
    "session"
]["interview_id"]

print()
print("Interview ID:", interview_id)


# ---------------------------------------------------------
# SEND CAMERA FRAME
# ---------------------------------------------------------

print()
print("========================================")
print("2. SEND CAMERA FRAME")
print("========================================")

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

print(
    "Status:",
    response.status_code
)

print(
    response.json()
)

if response.status_code != 200:
    raise SystemExit(
        "Camera frame failed"
    )


# ---------------------------------------------------------
# SEND AUDIO
# ---------------------------------------------------------

print()
print("========================================")
print("3. SEND AUDIO")
print("========================================")

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

print(
    "Status:",
    response.status_code
)

print(
    response.json()
)

if response.status_code != 200:
    raise SystemExit(
        "Audio failed"
    )


# ---------------------------------------------------------
# SEND SPEECH
# ---------------------------------------------------------

print()
print("========================================")
print("4. SEND SPEECH + NLP")
print("========================================")

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

print(
    "Status:",
    response.status_code
)

print(
    response.json()
)

if response.status_code != 200:
    raise SystemExit(
        "Speech failed"
    )


# ---------------------------------------------------------
# BUILD FEATURE WINDOW
# ---------------------------------------------------------

print()
print("========================================")
print("5. BUILD FEATURE WINDOW")
print("========================================")

response = requests.post(
    f"{BASE_URL}/interview/"
    f"{interview_id}/window"
)

print(
    "Status:",
    response.status_code
)

window_response = response.json()

print(
    window_response
)

if response.status_code != 200:
    raise SystemExit(
        "Feature window failed"
    )


window = window_response[
    "window"
]


# ---------------------------------------------------------
# PRINT IMPORTANT FEATURES
# ---------------------------------------------------------

print()
print("========================================")
print("6. COMBINED FEATURES")
print("========================================")

print(
    "Face detected:",
    window["face_detected"]
)

print(
    "Face presence:",
    window[
        "face_presence_percentage"
    ]
)

print(
    "Gaze:",
    window["gaze"]
)

print(
    "Blink:",
    window["blink"]
)

print(
    "Head pose:",
    window["head_pose"]
)

print(
    "Lip movement:",
    window[
        "lip_movement"
    ]
)

print(
    "Audio level:",
    window[
        "audio_level"
    ]
)

print(
    "Speech detected:",
    window[
        "speech_detected"
    ]
)

print(
    "MFCC count:",
    len(
        window["mfcc"]
    )
)

print(
    "Transcript:",
    window[
        "transcript"
    ]
)

print(
    "NLP:",
    window[
        "nlp"
    ]
)

print(
    "Fusion:",
    window[
        "fusion"
    ]
)


# ---------------------------------------------------------
# END INTERVIEW
# ---------------------------------------------------------

print()
print("========================================")
print("7. END INTERVIEW")
print("========================================")

response = requests.post(
    f"{BASE_URL}/interview/"
    f"{interview_id}/end"
)

print(
    "Status:",
    response.status_code
)

print(
    response.json()
)

if response.status_code != 200:
    raise SystemExit(
        "Interview ending failed"
    )


print()
print("========================================")
print("COMPLETE REALTIME TEST PASSED")
print("========================================")