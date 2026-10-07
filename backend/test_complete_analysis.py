import cv2
import librosa

from app.services.realtime_analysis_service import (
    RealtimeAnalysisService
)


# ---------------------------------------------------------
# LOAD TEST CAMERA IMAGE
# ---------------------------------------------------------

frame = cv2.imread(
    "test_face.jpg"
)

if frame is None:
    print("Could not load test_face.jpg")
    exit()


# ---------------------------------------------------------
# LOAD TEST AUDIO
# ---------------------------------------------------------

audio, sample_rate = librosa.load(
    "test_audio.wav",
    sr=16000,
    mono=True,
)


# ---------------------------------------------------------
# CREATE REAL-TIME ANALYSIS SERVICE
# ---------------------------------------------------------

service = RealtimeAnalysisService()


# ---------------------------------------------------------
# PROCESS CAMERA FRAME
# ---------------------------------------------------------

print()
print("Processing camera frame...")
print("--------------------------")

video_result = (
    service.process_video_frame(
        frame
    )
)

print(
    "Face detected:",
    video_result["face_detected"]
)

if video_result["face_detected"]:

    print(
        "Blink:",
        video_result["blink"]
    )

    print(
        "Gaze:",
        video_result["gaze"]
    )

    print(
        "Head pose:"
    )

    print(
        "  Yaw:",
        video_result["head_pose"]["yaw"]
    )

    print(
        "  Pitch:",
        video_result["head_pose"]["pitch"]
    )

    print(
        "  Roll:",
        video_result["head_pose"]["roll"]
    )

    print(
        "Lip movement:",
        video_result["lip_movement"]
    )


# ---------------------------------------------------------
# PROCESS AUDIO
# ---------------------------------------------------------

print()
print("Processing audio...")
print("-------------------")

audio_result = (
    service.process_audio(
        audio,
        sample_rate
    )
)

print(
    "Audio level:",
    audio_result["audio_level"]
)

print(
    "Speech detected:",
    audio_result["speech_detected"]
)

print(
    "MFCC count:",
    len(audio_result["mfcc"])
)


# ---------------------------------------------------------
# BUILD FEATURE WINDOW
# ---------------------------------------------------------

print()
print("Building combined feature window...")
print("------------------------------------")

window = (
    service.build_feature_window()
)


# ---------------------------------------------------------
# PRINT COMBINED WINDOW
# ---------------------------------------------------------

print()
print("Combined feature window:")
print("------------------------")

print(
    "Timestamp:",
    window["timestamp"]
)

print(
    "Face detected:",
    window["face_detected"]
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
    window["lip_movement"]
)

print(
    "Audio level:",
    window["audio_level"]
)
print(
    "MFCC:",
    window["mfcc"]
)

print(
    "Speech detected:",
    window["speech_detected"]
)

print(
    "Visual samples:",
    window["visual_samples"]
)

print(
    "Audio samples:",
    window["audio_samples"]
)


# ---------------------------------------------------------
# PRINT FUSION ANALYSIS
# ---------------------------------------------------------

print()
print("Fusion analysis:")
print("----------------")

fusion = window["fusion"]

print(
    "Face status:",
    fusion["face_status"]
)

print(
    "Gaze:",
    fusion["gaze"]
)

print(
    "Blink count:",
    fusion["blink_count"]
)

print(
    "Head pose:",
    fusion["head_pose"]
)

print(
    "Lip movement:",
    fusion["lip_movement"]
)

print(
    "Audio:",
    fusion["audio"]
)

print(
    "Speech:",
    fusion["speech"]
)

print(
    "Indicators:",
    fusion["indicators"]
)


# ---------------------------------------------------------
# CLOSE SERVICE
# ---------------------------------------------------------

service.close()

print()
print("Complete analysis test finished.")