from app.services.vision_service import VisionService
from app.services.blink_service import BlinkService
from app.services.gaze_service import GazeService
from app.services.head_pose_service import HeadPoseService
from app.services.lip_movement_service import LipMovementService


class VisualFeatureService:

    def __init__(self):

        self.vision = VisionService()
        self.blink = BlinkService()
        self.gaze = GazeService()
        self.head_pose = HeadPoseService()
        self.lip_movement = LipMovementService()

    def process_frame(self, frame):

        vision_result = self.vision.process_frame(frame)

        if not vision_result["face_detected"]:
            return {
                "face_detected": False,
                "blink": 0,
                "gaze": 0.0,
                "head_pose": {
                    "yaw": 0.0,
                    "pitch": 0.0,
                    "roll": 0.0,
                },
                "lip_movement": 0.0,
            }

        landmarks = vision_result["landmarks"]

        blink_result = self.blink.calculate(
            landmarks
        )

        gaze_result = self.gaze.calculate(
            landmarks
        )

        height, width = frame.shape[:2]

        head_pose_result = self.head_pose.calculate(
            landmarks,
            width,
            height,
        )

        lip_result = self.lip_movement.calculate(
            landmarks
        )

        return {
            "face_detected": True,

            "blink": blink_result["blink"],

            "gaze": gaze_result["gaze_score"],

            "head_pose": head_pose_result,

            "lip_movement": lip_result["lip_movement"],
        }

    def close(self):

        self.vision.close()