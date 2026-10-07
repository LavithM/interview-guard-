import requests
import time


BASE_URL = "http://127.0.0.1:8000"


# ---------------------------------------------------------
# 1. START INTERVIEW
# ---------------------------------------------------------

print()
print("========================================")
print("1. STARTING INTERVIEW")
print("========================================")

start_response = requests.post(
    f"{BASE_URL}/interview/start",
    json={
        "name": "Test User",
        "email": "test@example.com",
        "role": "Software Engineer",
    }
)

print("Status:", start_response.status_code)

start_data = start_response.json()

print("Response:")
print(start_data)


if start_response.status_code != 200:
    raise SystemExit(
        "Failed to start interview"
    )


interview_id = (
    start_data["session"]["interview_id"]
)

print()
print("Interview ID:")
print(interview_id)


# ---------------------------------------------------------
# 2. SEND AUDIO
# ---------------------------------------------------------

print()
print("========================================")
print("2. SENDING AUDIO")
print("========================================")

with open(
    "test_audio.wav",
    "rb"
) as audio_file:

    audio_response = requests.post(
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
    audio_response.status_code
)

print(
    "Response:"
)

print(
    audio_response.json()
)


if audio_response.status_code != 200:

    raise SystemExit(
        "Audio processing failed"
    )


# ---------------------------------------------------------
# 3. SEND SPEECH
# ---------------------------------------------------------

print()
print("========================================")
print("3. SENDING SPEECH")
print("========================================")

with open(
    "test_audio.wav",
    "rb"
) as audio_file:

    speech_response = requests.post(
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
    speech_response.status_code
)

speech_data = speech_response.json()

print(
    "Response:"
)

print(
    speech_data
)


if speech_response.status_code != 200:

    raise SystemExit(
        "Speech processing failed"
    )


# ---------------------------------------------------------
# 4. BUILD FEATURE WINDOW
# ---------------------------------------------------------

print()
print("========================================")
print("4. BUILDING FEATURE WINDOW")
print("========================================")

window_response = requests.post(
    f"{BASE_URL}/interview/"
    f"{interview_id}/window"
)

print(
    "Status:",
    window_response.status_code
)

window_data = window_response.json()

print(
    "Response:"
)

print(
    window_data
)


if window_response.status_code != 200:

    raise SystemExit(
        "Feature window failed"
    )


# ---------------------------------------------------------
# 5. DISPLAY IMPORTANT FEATURES
# ---------------------------------------------------------

window = window_data["window"]

print()
print("========================================")
print("5. FEATURE WINDOW SUMMARY")
print("========================================")

print(
    "Face detected:",
    window.get("face_detected")
)

print(
    "Face presence:",
    window.get(
        "face_presence_percentage"
    )
)

print(
    "Gaze:",
    window.get("gaze")
)

print(
    "Blink count:",
    window.get("blink")
)

print(
    "Head pose:",
    window.get("head_pose")
)

print(
    "Lip movement:",
    window.get(
        "lip_movement"
    )
)

print(
    "Audio level:",
    window.get(
        "audio_level"
    )
)

print(
    "Speech detected:",
    window.get(
        "speech_detected"
    )
)

print(
    "MFCC count:",
    len(
        window.get(
            "mfcc",
            []
        )
    )
)

print(
    "Transcript:",
    window.get(
        "transcript"
    )
)

print(
    "Language:",
    window.get(
        "language"
    )
)

print(
    "NLP:",
    window.get(
        "nlp"
    )
)

print(
    "Fusion:",
    window.get(
        "fusion"
    )
)


# ---------------------------------------------------------
# 6. END INTERVIEW
# ---------------------------------------------------------

print()
print("========================================")
print("6. ENDING INTERVIEW")
print("========================================")

end_response = requests.post(
    f"{BASE_URL}/interview/"
    f"{interview_id}/end"
)

print(
    "Status:",
    end_response.status_code
)

end_data = end_response.json()

print(
    "Response:"
)

print(
    end_data
)


if end_response.status_code != 200:

    raise SystemExit(
        "Interview ending failed"
    )


print()
print("========================================")
print("COMPLETE API TEST FINISHED")
print("========================================")
