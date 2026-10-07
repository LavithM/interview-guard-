from app.services.visual_feature_service import VisualFeatureService
from app.services.object_detection_service import ObjectDetectionService
from app.services.hand_detection_service import HandDetectionService


class RealtimeVisualService:
    def __init__(self):
        self.visual_service = VisualFeatureService()
        self.object_detection_service = ObjectDetectionService()
        self.hand_detection_service = HandDetectionService()

    def process_frame(self, frame):

        visual_result = self.visual_service.process_frame(
            frame
        )

        object_result = (
            self.object_detection_service.process_frame(
                frame
            )
        )

        hand_result = (
            self.hand_detection_service.process_frame(
                frame,
                object_result,
            )
        )

        return {
            **visual_result,
            "object_detection": object_result,
            "hand_detection": hand_result,
        }

    def close(self):
        self.visual_service.close()
        self.hand_detection_service.close()