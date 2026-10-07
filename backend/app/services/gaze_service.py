class GazeService:

    LEFT_EYE = {
        "left": 33,
        "right": 133,
        "top": 159,
        "bottom": 145,
        "iris": [468, 469, 470, 471],
    }

    RIGHT_EYE = {
        "left": 362,
        "right": 263,
        "top": 386,
        "bottom": 374,
        "iris": [472, 473, 474, 475],
    }

    def _eye_gaze(self, landmarks, eye):

        left = landmarks[eye["left"]]
        right = landmarks[eye["right"]]
        top = landmarks[eye["top"]]
        bottom = landmarks[eye["bottom"]]

        iris_points = [
            landmarks[index]
            for index in eye["iris"]
        ]

        iris_x = sum(
            point["x"]
            for point in iris_points
        ) / len(iris_points)

        iris_y = sum(
            point["y"]
            for point in iris_points
        ) / len(iris_points)

        eye_width = abs(
            right["x"] - left["x"]
        )

        eye_height = abs(
            bottom["y"] - top["y"]
        )

        if eye_width < 0.0001 or eye_height < 0.0001:
            return {
                "horizontal": 0.5,
                "vertical": 0.5,
                "pupil_x": 0.5,
                "pupil_y": 0.5,
            }

        horizontal = (
            iris_x - left["x"]
        ) / eye_width

        vertical = (
            iris_y - top["y"]
        ) / eye_height

        horizontal = max(
            0.0,
            min(1.0, horizontal)
        )

        vertical = max(
            0.0,
            min(1.0, vertical)
        )

        return {
            "horizontal": horizontal,
            "vertical": vertical,
            "pupil_x": horizontal,
            "pupil_y": vertical,
        }

    def _gaze_direction(self, horizontal, vertical):

        # These are normalized directions.
        # 0 = approximately centered.
        # 1 = top-left
        # 2 = top-right
        # 3 = bottom-left
        # 4 = bottom-right

        horizontal_threshold = 0.20
        vertical_threshold = 0.20

        horizontal_direction = 0
        vertical_direction = 0

        if horizontal < 0.5 - horizontal_threshold:
            horizontal_direction = -1
        elif horizontal > 0.5 + horizontal_threshold:
            horizontal_direction = 1

        if vertical < 0.5 - vertical_threshold:
            vertical_direction = -1
        elif vertical > 0.5 + vertical_threshold:
            vertical_direction = 1

        if horizontal_direction == 0 and vertical_direction == 0:
            return 0

        if horizontal_direction == -1 and vertical_direction == -1:
            return 1

        if horizontal_direction == 1 and vertical_direction == -1:
            return 2

        if horizontal_direction == -1 and vertical_direction == 1:
            return 3

        if horizontal_direction == 1 and vertical_direction == 1:
            return 4

        # Horizontal or vertical-only movement.
        # Map it to the closest available dataset category.
        if horizontal_direction == -1:
            return 1

        if horizontal_direction == 1:
            return 2

        if vertical_direction == -1:
            return 1

        return 3

    def calculate(self, landmarks):

        if len(landmarks) < 478:
            return {
                "horizontal": 0.5,
                "vertical": 0.5,
                "gaze_score": 0.0,
                "gaze_on_script": 0.0,
                "gaze_direction": 0,
                "pupil_left_x": 0.5,
                "pupil_left_y": 0.5,
                "pupil_right_x": 0.5,
                "pupil_right_y": 0.5,
            }

        left = self._eye_gaze(
            landmarks,
            self.LEFT_EYE
        )

        right = self._eye_gaze(
            landmarks,
            self.RIGHT_EYE
        )

        horizontal = (
            left["horizontal"] +
            right["horizontal"]
        ) / 2

        vertical = (
            left["vertical"] +
            right["vertical"]
        ) / 2

        horizontal_deviation = abs(
            horizontal - 0.5
        )

        vertical_deviation = abs(
            vertical - 0.5
        )

        deviation = (
            horizontal_deviation +
            vertical_deviation
        )

        gaze_score = max(
            0.0,
            1.0 - deviation
        )

        gaze_direction = self._gaze_direction(
            horizontal,
            vertical
        )

        # At this stage we do not have a physical
        # interview script location in the camera frame.
        # Therefore this remains a neutral value.
        gaze_on_script = 0.0

        return {
            "horizontal": round(
                horizontal,
                4
            ),
            "vertical": round(
                vertical,
                4
            ),
            "gaze_score": round(
                gaze_score,
                4
            ),
            "gaze_on_script": gaze_on_script,
            "gaze_direction": gaze_direction,
            "pupil_left_x": round(
                left["pupil_x"],
                4
            ),
            "pupil_left_y": round(
                left["pupil_y"],
                4
            ),
            "pupil_right_x": round(
                right["pupil_x"],
                4
            ),
            "pupil_right_y": round(
                right["pupil_y"],
                4
            ),
        }