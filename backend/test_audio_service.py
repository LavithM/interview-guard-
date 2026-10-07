import librosa

from app.services.audio_service import AudioService


audio, sample_rate = librosa.load(
    "test_audio.wav",
    sr=16000,
    mono=True,
)


audio_service = AudioService()

result = audio_service.process_audio(
    audio,
    sample_rate,
)


print("Audio analysis:")
print("----------------")
print("Sample rate:", sample_rate)
print("Audio level:", result["audio_level"])
print("Speech detected:", result["speech_detected"])
print("MFCC values:", result["mfcc"])
print("Number of MFCC values:", len(result["mfcc"]))
