from app.services.speech_service import (
    SpeechService
)


speech_service = SpeechService()

result = speech_service.transcribe(
    "test_audio.wav"
)

print("Speech-to-text result:")
print("-----------------------")

print(
    "Language:",
    result["language"]
)

print(
    "Language probability:",
    result["language_probability"]
)

print(
    "Transcript:"
)

print(
    result["transcript"]
)