class FusionService:

    def analyze_window(self, window):

        gaze = float(
            window.get(
                "gaze",
                0.0
            )
        )

        blink = int(
            window.get(
                "blink",
                0
            )
        )

        head_pose = window.get(
            "head_pose",
            {}
        )

        yaw = float(
            head_pose.get(
                "yaw",
                0.0
            )
        )

        pitch = float(
            head_pose.get(
                "pitch",
                0.0
            )
        )

        roll = float(
            head_pose.get(
                "roll",
                0.0
            )
        )

        lip_movement = float(
            window.get(
                "lip_movement",
                0.0
            )
        )

        audio_level = float(
            window.get(
                "audio_level",
                0.0
            )
        )

        speech_detected = bool(
            window.get(
                "speech_detected",
                False
            )
        )

        face_detected = bool(
            window.get(
                "face_detected",
                False
            )
        )

        # ------------------------------------------------
        # GAZE
        # ------------------------------------------------

        if gaze < 0.40:

            gaze_indicator = "low"

        elif gaze < 0.65:

            gaze_indicator = "moderate"

        else:

            gaze_indicator = "stable"

        # ------------------------------------------------
        # HEAD POSE
        # ------------------------------------------------

        head_turn_detected = (
            abs(yaw) > 25
            or abs(pitch) > 25
            or abs(roll) > 25
        )

        # ------------------------------------------------
        # FACE
        # ------------------------------------------------

        face_status = (
            "present"
            if face_detected
            else "not_detected"
        )

        # ------------------------------------------------
        # AUDIO
        # ------------------------------------------------

        if audio_level < 0.005:

            audio_status = "quiet"

        elif audio_level < 0.02:

            audio_status = "normal"

        else:

            audio_status = "higher"

        # ------------------------------------------------
        # SPEECH
        # ------------------------------------------------

        speech_status = (
            "detected"
            if speech_detected
            else "not_detected"
        )

        # ------------------------------------------------
        # LIP MOVEMENT
        # ------------------------------------------------

        if lip_movement < 0.05:

            lip_status = "low"

        elif lip_movement < 0.15:

            lip_status = "moderate"

        else:

            lip_status = "active"

        # ------------------------------------------------
        # LIP SYNC / DTW
        # ------------------------------------------------

        lip_sync = window.get(
            "lip_sync",
            {}
        )

        dtw_distance = float(
            lip_sync.get(
                "dtw_distance",
                0.0
            )
        )

        lip_audio_alignment = float(
            lip_sync.get(
                "lip_audio_alignment",
                0.0
            )
        )

        if lip_audio_alignment >= 0.70:

            lip_sync_status = "aligned"

        elif lip_audio_alignment >= 0.40:

            lip_sync_status = "moderate"

        else:

            lip_sync_status = "low"

        # ------------------------------------------------
        # OBJECT DETECTION
        # ------------------------------------------------

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

        person_count_above_one = bool(
            object_detection.get(
                "person_count_above_one",
                False
            )
        )

        mobile_phone_detected = bool(
            object_detection.get(
                "mobile_phone_detected",
                False
            )
        )

        detected_objects = (
            object_detection.get(
                "objects",
                {}
            )
        )

        # ------------------------------------------------
        # INDICATORS
        # ------------------------------------------------

        indicators = []

        if not face_detected:

            indicators.append(
                "face_not_detected"
            )

        if gaze < 0.40:

            indicators.append(
                "low_gaze_score"
            )

        if head_turn_detected:

            indicators.append(
                "significant_head_movement"
            )

        if speech_detected:

            indicators.append(
                "speech_detected"
            )

        if person_count_above_one:

            indicators.append(
                "multiple_people_detected"
            )

        if mobile_phone_detected:

            indicators.append(
                "mobile_phone_detected"
            )

        if lip_audio_alignment < 0.40:

            indicators.append(
                "low_lip_audio_alignment"
            )

        # ------------------------------------------------
        # RESULT
        # ------------------------------------------------

        return {

            "face_status":
                face_status,

            "gaze": {

                "value":
                    round(
                        gaze,
                        4
                    ),

                "indicator":
                    gaze_indicator,
            },

            "blink_count":
                blink,

            "head_pose": {

                "yaw":
                    round(
                        yaw,
                        2
                    ),

                "pitch":
                    round(
                        pitch,
                        2
                    ),

                "roll":
                    round(
                        roll,
                        2
                    ),

                "turn_detected":
                    head_turn_detected,
            },

            "lip_movement": {

                "value":
                    round(
                        lip_movement,
                        4
                    ),

                "indicator":
                    lip_status,
            },

            "audio": {

                "level":
                    round(
                        audio_level,
                        4
                    ),

                "status":
                    audio_status,
            },

            "speech": {

                "detected":
                    speech_detected,

                "status":
                    speech_status,
            },

            "lip_sync": {

                "dtw_distance":
                    round(
                        dtw_distance,
                        4
                    ),

                "alignment":
                    round(
                        lip_audio_alignment,
                        4
                    ),

                "status":
                    lip_sync_status,
            },

            "objects": {

                "maximum_person_count":
                    maximum_person_count,

                "multiple_people_detected":
                    person_count_above_one,

                "mobile_phone_detected":
                    mobile_phone_detected,

                "detected_objects":
                    detected_objects,
            },

            "indicators":
                indicators,
        }