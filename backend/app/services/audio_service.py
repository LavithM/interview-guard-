import numpy as np
import librosa


class AudioService:

    def process_audio(self, audio, sample_rate):

        if audio is None or len(audio) == 0:
            return {
                "audio_level": 0.0,
                "speech_detected": False,
                "mfcc": [],
            }

        # Make sure audio is a NumPy array.
        audio = np.asarray(audio, dtype=np.float32)

        # Calculate RMS energy.
        rms = librosa.feature.rms(
            y=audio
        )

        audio_level = float(
            np.mean(rms)
        )

        # Simple speech/activity threshold.
        # This is an initial threshold and will
        # be calibrated later with real interview audio.
        speech_detected = audio_level > 0.01

        # Calculate MFCC features.
        mfcc = librosa.feature.mfcc(
            y=audio,
            sr=sample_rate,
            n_mfcc=13,
        )

        mean_mfcc = np.mean(
            mfcc,
            axis=1
        )

        return {
            "audio_level": round(
                audio_level,
                4
            ),

            "speech_detected": speech_detected,

            "mfcc": [
                round(float(value), 4)
                for value in mean_mfcc
            ],
        }
    