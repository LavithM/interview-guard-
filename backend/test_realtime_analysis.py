import cv2
import librosa

from app.services.realtime_analysis_service import (
    RealtimeAnalysisService
)


# Load test image
frame = cv2.imread("test_face.jpg")

if frame is None:
    print("Could not load test_face.jpg")
    exit()


# Load test audio
audio, sample_rate = librosa.load(
    "test_audio.wav",
    sr=16000,
    mono=True,
)


# Create real-time analysis service
service = RealtimeAnalysisService()


# Process video frame
video_result = service.process_video_frame(
    frame
)


# Process audio
audio_result = service.process_audio(
    audio,
    sample_rate
)


# Build combined feature window
window = service.build_feature_window()


print()
print("Real-time analysis result:")
print("--------------------------")

print("Face detected:", video_result["face_detected"])

if video_result["face_detected"]:

    print("Blink:", video_result["blink"])
    print("Gaze:", video_result["gaze"])

    print("Head pose:")
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

print()
print("Audio:")
print("Audio level:", audio_result["audio_level"])
print(
    "Speech detected:",
    audio_result["speech_detected"]
)

print()
print("Combined feature window:")
print("------------------------")
print("Gaze:", window["gaze"])
print("Blink:", window["blink"])
print("Lip movement:", window["lip_movement"])
print(
    "Audio level:",
    window["audio_level"]
)
print(
    "Speech detected:",
    window["speech_detected"]
)


# Clean up
service.close()