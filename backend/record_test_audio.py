import sounddevice as sd
import soundfile as sf


sample_rate = 16000
duration = 5

print("Recording for 5 seconds...")
print("Please speak normally into your microphone.")

audio = sd.rec(
    int(duration * sample_rate),
    samplerate=sample_rate,
    channels=1,
    dtype="float32",
)

sd.wait()

sf.write(
    "test_audio.wav",
    audio,
    sample_rate,
)

print("Recording finished.")
print("Saved as: test_audio.wav")
