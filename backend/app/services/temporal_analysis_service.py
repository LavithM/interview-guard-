class TemporalAnalysisService:

    def analyze(self, feature_windows):

        if not feature_windows:

            return {
                "total_windows": 0,

                "face_absence_windows": 0,
                "low_gaze_windows": 0,
                "head_turn_windows": 0,
                "speech_windows": 0,

                "face_presence_percentage": 0.0,
                "low_gaze_percentage": 0.0,
                "head_turn_percentage": 0.0,
                "speech_percentage": 0.0,

                "total_blinks": 0,

                "additional_person_windows": 0,
                "additional_person_percentage": 0.0,

                "mobile_phone_windows": 0,
                "mobile_phone_percentage": 0.0,

                "detected_objects": {},
            }

        total_windows = len(
            feature_windows
        )

        face_absence_windows = 0
        low_gaze_windows = 0
        head_turn_windows = 0
        speech_windows = 0

        total_blinks = 0

        additional_person_windows = 0
        mobile_phone_windows = 0

        detected_objects = {}

        face_present_windows = 0

        # --------------------------------------------------
        # PROCESS EACH WINDOW
        # --------------------------------------------------

        for window in feature_windows:

            # ==============================================
            # FACE
            # ==============================================

            face_detected = window.get(
                "face_detected",
                False
            )

            if face_detected:

                face_present_windows += 1

            else:

                face_absence_windows += 1

            # ==============================================
            # GAZE
            # ==============================================

            gaze = float(
                window.get(
                    "gaze",
                    0.0
                )
            )

            if gaze < 0.40:

                low_gaze_windows += 1

            # ==============================================
            # HEAD POSE
            # ==============================================

            head_pose = window.get(
                "head_pose",
                {}
            )

            yaw = abs(
                float(
                    head_pose.get(
                        "yaw",
                        0.0
                    )
                )
            )

            pitch = abs(
                float(
                    head_pose.get(
                        "pitch",
                        0.0
                    )
                )
            )

            roll = abs(
                float(
                    head_pose.get(
                        "roll",
                        0.0
                    )
                )
            )

            if (
                yaw > 25
                or pitch > 25
                or roll > 25
            ):

                head_turn_windows += 1

            # ==============================================
            # SPEECH
            # ==============================================

            speech_detected = window.get(
                "speech_detected",
                False
            )

            if speech_detected:

                speech_windows += 1

            # ==============================================
            # BLINK
            # ==============================================

            total_blinks += int(
                window.get(
                    "blink",
                    0
                )
            )

            # ==============================================
            # OBJECT DETECTION
            # ==============================================

            object_detection = window.get(
                "object_detection",
                {}
            )

            maximum_person_count = int(
                object_detection.get(
                    "maximum_person_count",
                    0
                )
            )

            if maximum_person_count > 1:

                additional_person_windows += 1

            mobile_phone_detected = (
                object_detection.get(
                    "mobile_phone_detected",
                    False
                )
            )

            if mobile_phone_detected:

                mobile_phone_windows += 1

            # ==============================================
            # OBJECT COUNTS
            # ==============================================

            objects = object_detection.get(
                "objects",
                {}
            )

            for object_name, count in objects.items():

                detected_objects[object_name] = (
                    detected_objects.get(
                        object_name,
                        0
                    ) + int(count)
                )

        # --------------------------------------------------
        # PERCENTAGES
        # --------------------------------------------------

        face_presence_percentage = (
            face_present_windows
            / total_windows
        ) * 100

        low_gaze_percentage = (
            low_gaze_windows
            / total_windows
        ) * 100

        head_turn_percentage = (
            head_turn_windows
            / total_windows
        ) * 100

        speech_percentage = (
            speech_windows
            / total_windows
        ) * 100

        additional_person_percentage = (
            additional_person_windows
            / total_windows
        ) * 100

        mobile_phone_percentage = (
            mobile_phone_windows
            / total_windows
        ) * 100

        # --------------------------------------------------
        # RESULT
        # --------------------------------------------------

        return {

            "total_windows":
                total_windows,

            # Face
            "face_absence_windows":
                face_absence_windows,

            "face_presence_percentage":
                round(
                    face_presence_percentage,
                    2
                ),

            # Gaze
            "low_gaze_windows":
                low_gaze_windows,

            "low_gaze_percentage":
                round(
                    low_gaze_percentage,
                    2
                ),

            # Head
            "head_turn_windows":
                head_turn_windows,

            "head_turn_percentage":
                round(
                    head_turn_percentage,
                    2
                ),

            # Speech
            "speech_windows":
                speech_windows,

            "speech_percentage":
                round(
                    speech_percentage,
                    2
                ),

            # Blink
            "total_blinks":
                total_blinks,

            # Additional person
            "additional_person_windows":
                additional_person_windows,

            "additional_person_percentage":
                round(
                    additional_person_percentage,
                    2
                ),

            # Mobile phone
            "mobile_phone_windows":
                mobile_phone_windows,

            "mobile_phone_percentage":
                round(
                    mobile_phone_percentage,
                    2
                ),

            # Objects
            "detected_objects":
                detected_objects,
        }