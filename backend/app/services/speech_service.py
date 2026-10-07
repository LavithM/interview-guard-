from faster_whisper import WhisperModel


class SpeechService:

    def __init__(self):

        self.model = WhisperModel(
            "tiny",
            device="cpu",
            compute_type="int8"
        )

    def transcribe(
        self,
        audio_path: str
    ):

        segments, info = self.model.transcribe(
            audio_path,
            beam_size=5,
            language="en"
        )

        transcript_parts = []

        for segment in segments:

            transcript_parts.append(
                segment.text.strip()
            )

        transcript = " ".join(
            transcript_parts
        ).strip()

        return {
            "transcript": transcript,
            "language": info.language,
            "language_probability": round(
                info.language_probability,
                4
            )
        }