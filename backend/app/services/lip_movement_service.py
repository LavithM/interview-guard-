import math


class LipMovementService:

    # Important mouth landmarks
    UPPER_LIP = 13
    LOWER_LIP = 14

    LEFT_MOUTH = 61
    RIGHT_MOUTH = 291

    def _distance(self, p1, p2):

        return math.sqrt(
            (p1["x"] - p2["x"]) ** 2
            + (p1["y"] - p2["y"]) ** 2
            + (p1["z"] - p2["z"]) ** 2
        )

    def calculate(self, landmarks):

        if len(landmarks) < 478:
            return {
                "mouth_open": 0.0,
                "lip_movement": 0.0,
            }

        upper_lip = landmarks[self.UPPER_LIP]
        lower_lip = landmarks[self.LOWER_LIP]

        left_mouth = landmarks[self.LEFT_MOUTH]
        right_mouth = landmarks[self.RIGHT_MOUTH]

        mouth_open = self._distance(
            upper_lip,
            lower_lip
        )

        mouth_width = self._distance(
            left_mouth,
            right_mouth
        )

        if mouth_width < 0.0001:
            return {
                "mouth_open": 0.0,
                "lip_movement": 0.0,
            }

        # Normalize mouth opening relative
        # to the person's mouth width.
        lip_movement = (
            mouth_open / mouth_width
        )

        return {
            "mouth_open": round(
                mouth_open,
                4
            ),
            "lip_movement": round(
                lip_movement,
                4
            ),
        }
    