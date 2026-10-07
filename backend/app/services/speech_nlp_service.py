from app.services.speech_service import (
    SpeechService
)

from app.services.nlp_service import (
    NLPService
)


class SpeechNLPService:

    def __init__(self):

        self.speech_service = (
            SpeechService()
        )

        self.nlp_service = (
            NLPService()
        )

    def analyze(
        self,
        audio_path: str
    ):

        # ---------------------------------------------
        # SPEECH TO TEXT
        # ---------------------------------------------

        speech_result = (
            self.speech_service.transcribe(
                audio_path
            )
        )

        transcript = (
            speech_result["transcript"]
        )

        # ---------------------------------------------
        # NLP
        # ---------------------------------------------

        nlp_result = (
            self.nlp_service.analyze(
                transcript
            )
        )

        # ---------------------------------------------
        # COMBINED RESULT
        # ---------------------------------------------

        return {
            "transcript": transcript,

            "language":
                speech_result["language"],

            "language_probability":
                speech_result[
                    "language_probability"
                ],

            "nlp": nlp_result,
        }