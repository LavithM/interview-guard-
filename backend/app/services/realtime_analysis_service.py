from app.services.realtime_visual_service import (
    RealtimeVisualService
)

from app.services.feature_window_service import (
    FeatureWindowService
)

from app.services.audio_service import (
    AudioService
)

from app.services.speech_nlp_service import (
    SpeechNLPService
)

from app.services.fusion_service import (
    FusionService
)

from app.services.model_prediction_service import (
    ModelPredictionService
)

from app.services.model_feature_adapter import (
    ModelFeatureAdapter
)


class RealtimeAnalysisService:

    def __init__(self):

        self.visual_service = (
            RealtimeVisualService()
        )

        self.feature_window = (
            FeatureWindowService()
        )

        self.audio_service = (
            AudioService()
        )

        self.speech_nlp_service = (
            SpeechNLPService()
        )

        self.fusion_service = (
            FusionService()
        )

        self.model_prediction_service = (
            ModelPredictionService()
        )

        self.model_feature_adapter = (
            ModelFeatureAdapter()
        )

    def process_video_frame(
        self,
        frame
    ):

        visual_result = (
            self.visual_service.process_frame(
                frame
            )
        )

        self.feature_window.add_visual_features(
            visual_result
        )

        object_result = visual_result.get(
            "object_detection",
            {}
        )

        self.feature_window.add_object_features(
            object_result
        )

        return visual_result

    def process_audio(
        self,
        audio,
        sample_rate
    ):

        audio_result = (
            self.audio_service.process_audio(
                audio,
                sample_rate
            )
        )

        self.feature_window.add_audio_features(
            audio_result
        )

        return audio_result

    def process_speech(
        self,
        audio_path
    ):

        speech_result = (
            self.speech_nlp_service.analyze(
                audio_path
            )
        )

        self.feature_window.add_speech_features(
            speech_result
        )

        return speech_result

    def build_feature_window(self):

        window = (
            self.feature_window.build_window()
        )

        fusion_result = (
            self.fusion_service.analyze_window(
                window
            )
        )

        window["fusion"] = fusion_result

        # -----------------------------------------
        # Prepare features for XGBoost
        # -----------------------------------------

        model_features = (
            self.model_feature_adapter.adapt(
                window
            )
        )

        # -----------------------------------------
        # Run XGBoost prediction
        # -----------------------------------------

        model_prediction = (
            self.model_prediction_service.predict(
                model_features
            )
        )

        # -----------------------------------------
        # Store model information
        # -----------------------------------------

        window["model_features"] = (
            model_features
        )

        window["model_prediction"] = (
            model_prediction
        )

        return window

    def close(self):

        self.visual_service.close()