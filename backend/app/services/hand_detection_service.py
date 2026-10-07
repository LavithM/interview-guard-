import math

import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class HandDetectionService:
    def __init__(self):
        base_options = python.BaseOptions(
            model_asset_path="models/hand_landmarker.task"
        )

        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=2,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )

        self.detector = vision.HandLandmarker.create_from_options(
            options
        )

    def _distance(self, point1, point2):
        return math.sqrt(
            (point1[0] - point2[0]) ** 2
            + (point1[1] - point2[1]) ** 2
        )

    def _hand_is_near_object(
        self,
        hand_landmarks,
        object_detection,
        frame_width,
        frame_height,
    ):
        if not hand_landmarks:
            return False

        if not object_detection:
            return False

        # Use the wrist and fingertips as representative
        # hand points.
        hand_indices = [
            0,   # wrist
            4,   # thumb tip
            8,   # index finger tip
            12,  # middle finger tip
            16,  # ring finger tip
            20,  # little finger tip
        ]

        hand_points = []

        for index in hand_indices:
            landmark = hand_landmarks[index]

            x = landmark.x * frame_width
            y = landmark.y * frame_height

            hand_points.append((x, y))

        for detected_object in object_detection.get(
            "objects",
            []
        ):
            bbox = detected_object.get(
                "bbox"
            )

            if not bbox or len(bbox) != 4:
                continue

            x1, y1, x2, y2 = bbox

            object_center = (
                (x1 + x2) / 2,
                (y1 + y2) / 2,
            )

            object_width = max(
                1.0,
                x2 - x1
            )

            object_height = max(
                1.0,
                y2 - y1
            )

            # Distance threshold is based on the size
            # of the detected object.
            threshold = max(
                object_width,
                object_height
            ) * 0.75

            for hand_point in hand_points:

                distance = self._distance(
                    hand_point,
                    object_center
                )

                if distance <= threshold:
                    return True

        return False

    def process_frame(
        self,
        frame,
        object_detection=None,
    ):
        if frame is None:
            return {
                "hand_count": 0,
                "hands_detected": False,
                "hand_obj_interaction": 0,
            }

        rgb_frame = frame[:, :, ::-1]

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame,
        )

        result = self.detector.detect(mp_image)

        hand_count = len(
            result.hand_landmarks
        )

        frame_height, frame_width = (
            frame.shape[:2]
        )

        interaction_detected = False

        if object_detection is not None:

            for hand_landmarks in result.hand_landmarks:

                if self._hand_is_near_object(
                    hand_landmarks,
                    object_detection,
                    frame_width,
                    frame_height,
                ):
                    interaction_detected = True
                    break

        return {
            "hand_count": hand_count,
            "hands_detected": hand_count > 0,
            "hand_obj_interaction": int(
                interaction_detected
            ),
        }

    def close(self):
        self.detector.close()