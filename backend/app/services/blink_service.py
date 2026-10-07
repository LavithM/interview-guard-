import math


class BlinkService:

    # MediaPipe Face Mesh landmark indices
    LEFT_EYE = {
        "top": 159,
        "bottom": 145,
        "left": 33,
        "right": 133,
    }

    RIGHT_EYE = {
        "top": 386,
        "bottom": 374,
        "left": 362,
        "right": 263,
    }

    def _distance(self, p1, p2):
        return math.sqrt(
            (p1["x"] - p2["x"]) ** 2
            + (p1["y"] - p2["y"]) ** 2
            + (p1["z"] - p2["z"]) ** 2
        )

    def _eye_aspect_ratio(self, landmarks, eye):
        vertical_distance = self._distance(
            landmarks[eye["top"]],
            landmarks[eye["bottom"]],
        )

        horizontal_distance = self._distance(
            landmarks[eye["left"]],
            landmarks[eye["right"]],
        )

        if horizontal_distance == 0:
            return 0.0

        return vertical_distance / horizontal_distance

    def calculate(self, landmarks):

        if len(landmarks) < 478:
            return {
                "left_ear": 0.0,
                "right_ear": 0.0,
                "average_ear": 0.0,
                "blink": 0,
            }

        left_ear = self._eye_aspect_ratio(
            landmarks,
            self.LEFT_EYE,
        )

        right_ear = self._eye_aspect_ratio(
            landmarks,
            self.RIGHT_EYE,
        )

        average_ear = (
            left_ear + right_ear
        ) / 2

        # Initial threshold.
        # We will calibrate this later using real video.
        blink = 1 if average_ear < 0.20 else 0

        return {
            "left_ear": round(left_ear, 4),
            "right_ear": round(right_ear, 4),
            "average_ear": round(average_ear, 4),
            "blink": blink,
        }