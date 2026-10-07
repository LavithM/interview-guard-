class ModelFeatureAdapter:

    def adapt(self, runtime_features):

        head_pose = runtime_features.get("head_pose", {})
        gaze = runtime_features.get("gaze", {})
        object_detection = runtime_features.get(
            "object_detection",
            {},
        )
        hand_detection = runtime_features.get(
            "hand_detection",
            {},
        )

        # Some feature-window values can be numeric aggregates
        # instead of dictionaries. Normalize them safely.
        if not isinstance(head_pose, dict):
            head_pose = {}

        if not isinstance(gaze, dict):
            gaze = {}

        if not isinstance(object_detection, dict):
            object_detection = {}

        if not isinstance(hand_detection, dict):
            hand_detection = {}

        features = {
            "face_present": int(
                bool(runtime_features.get("face_detected", False))
            ),

            "no_of_face": float(
                object_detection.get("person_count", 0)
            ),

            "face_conf": float(
                runtime_features.get("face_conf", 0.0)
            ),

            "hand_count": float(
                hand_detection.get("hand_count", 0)
            ),

            "hand_obj_interaction": float(
                hand_detection.get(
                    "hand_obj_interaction",
                    0,
                )
            ),

            "head_pitch": float(
                head_pose.get("pitch", 0.0)
            ),

            "head_yaw": float(
                head_pose.get("yaw", 0.0)
            ),

            "head_roll": float(
                head_pose.get("roll", 0.0)
            ),

            "phone_present": int(
                bool(
                    object_detection.get(
                        "mobile_phone_detected",
                        False,
                    )
                )
            ),

            "phone_conf": float(
                object_detection.get(
                    "mobile_phone_confidence",
                    0.0,
                )
            ),

            "gaze_on_script": float(
                gaze.get("gaze_on_script", 0.0)
            ),

            "gaze_direction": int(
                gaze.get("gaze_direction", 0)
            ),

            "gazePoint_x": float(
                gaze.get("horizontal", 0.5)
            ),

            "gazePoint_y": float(
                gaze.get("vertical", 0.5)
            ),

            "pupil_left_x": float(
                gaze.get("pupil_left_x", 0.5)
            ),

            "pupil_left_y": float(
                gaze.get("pupil_left_y", 0.5)
            ),

            "pupil_right_x": float(
                gaze.get("pupil_right_x", 0.5)
            ),

            "pupil_right_y": float(
                gaze.get("pupil_right_y", 0.5)
            ),
        }

        return features