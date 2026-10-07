import math


class HeadPoseService:

    NOSE = 1

    LEFT_EYE = 33
    RIGHT_EYE = 263

    LEFT_CHEEK = 234
    RIGHT_CHEEK = 454

    FOREHEAD = 10
    CHIN = 152

    def _distance(self, p1, p2):

        return math.sqrt(
            (p1["x"] - p2["x"]) ** 2
            + (p1["y"] - p2["y"]) ** 2
            + (p1["z"] - p2["z"]) ** 2
        )

    def calculate(self, landmarks, image_width, image_height):

        if len(landmarks) < 478:
            return {
                "yaw": 0.0,
                "pitch": 0.0,
                "roll": 0.0,
            }

        left_eye = landmarks[self.LEFT_EYE]
        right_eye = landmarks[self.RIGHT_EYE]

        nose = landmarks[self.NOSE]

        left_cheek = landmarks[self.LEFT_CHEEK]
        right_cheek = landmarks[self.RIGHT_CHEEK]

        forehead = landmarks[self.FOREHEAD]
        chin = landmarks[self.CHIN]

        # ------------------------------------------------
        # ROLL
        # ------------------------------------------------

        eye_dx = (
            right_eye["x"] -
            left_eye["x"]
        )

        eye_dy = (
            right_eye["y"] -
            left_eye["y"]
        )

        roll = math.degrees(
            math.atan2(
                eye_dy,
                eye_dx
            )
        )

        # ------------------------------------------------
        # YAW
        # ------------------------------------------------

        face_width = self._distance(
            left_cheek,
            right_cheek
        )

        if face_width < 0.0001:
            yaw = 0.0

        else:

            face_center_x = (
                left_cheek["x"] +
                right_cheek["x"]
            ) / 2

            nose_offset = (
                nose["x"] -
                face_center_x
            )

            normalized_offset = (
                nose_offset /
                face_width
            )

            yaw = normalized_offset * 90.0

        # ------------------------------------------------
        # PITCH
        # ------------------------------------------------

        face_height = self._distance(
            forehead,
            chin
        )

        if face_height < 0.0001:

            pitch = 0.0

        else:

            nose_y = nose["y"]

            face_top = forehead["y"]
            face_bottom = chin["y"]

            expected_center = (
                face_top +
                face_bottom
            ) / 2

            vertical_offset = (
                nose_y -
                expected_center
            )

            normalized_pitch = (
                vertical_offset /
                face_height
            )

            pitch = normalized_pitch * 90.0

        # Keep values bounded.
        yaw = max(
            -90.0,
            min(90.0, yaw)
        )

        pitch = max(
            -90.0,
            min(90.0, pitch)
        )

        roll = max(
            -90.0,
            min(90.0, roll)
        )

        return {
            "yaw": round(yaw, 2),
            "pitch": round(pitch, 2),
            "roll": round(roll, 2),
        }