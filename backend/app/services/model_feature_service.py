class ModelFeatureService:

    def extract(self, window):

        head_pose = window.get(
            "head_pose",
            {}
        )

        object_detection = window.get(
            "object_detection",
            {}
        )

        lip_sync = window.get(
            "lip_sync",
            {}
        )

        nlp = window.get(
            "nlp",
            {}
        )

        features = {

            # -----------------------------
            # FACE
            # -----------------------------

            "face_detected":
                int(
                    bool(
                        window.get(
                            "face_detected",
                            False
                        )
                    )
                ),

            "face_presence_percentage":
                float(
                    window.get(
                        "face_presence_percentage",
                        0.0
                    )
                ),

            # -----------------------------
            # GAZE
            # -----------------------------

            "gaze":
                float(
                    window.get(
                        "gaze",
                        0.0
                    )
                ),

            # -----------------------------
            # BLINK
            # -----------------------------

            "blink":
                float(
                    window.get(
                        "blink",
                        0
                    )
                ),

            # -----------------------------
            # HEAD POSE
            # -----------------------------

            "yaw":
                float(
                    head_pose.get(
                        "yaw",
                        0.0
                    )
                ),

            "pitch":
                float(
                    head_pose.get(
                        "pitch",
                        0.0
                    )
                ),

            "roll":
                float(
                    head_pose.get(
                        "roll",
                        0.0
                    )
                ),

            # -----------------------------
            # LIP MOVEMENT
            # -----------------------------

            "lip_movement":
                float(
                    window.get(
                        "lip_movement",
                        0.0
                    )
                ),

            # -----------------------------
            # AUDIO
            # -----------------------------

            "audio_level":
                float(
                    window.get(
                        "audio_level",
                        0.0
                    )
                ),

            "speech_detected":
                int(
                    bool(
                        window.get(
                            "speech_detected",
                            False
                        )
                    )
                ),

            # -----------------------------
            # LIP / AUDIO ALIGNMENT
            # -----------------------------

            "dtw_distance":
                float(
                    lip_sync.get(
                        "dtw_distance",
                        0.0
                    )
                ),

            "lip_audio_alignment":
                float(
                    lip_sync.get(
                        "lip_audio_alignment",
                        0.0
                    )
                ),

            # -----------------------------
            # OBJECT DETECTION
            # -----------------------------

            "maximum_person_count":
                float(
                    object_detection.get(
                        "maximum_person_count",
                        0
                    )
                ),

            "person_count_above_one":
                int(
                    bool(
                        object_detection.get(
                            "person_count_above_one",
                            False
                        )
                    )
                ),

            "mobile_phone_detected":
                int(
                    bool(
                        object_detection.get(
                            "mobile_phone_detected",
                            False
                        )
                    )
                ),

            "mobile_phone_detections":
                float(
                    object_detection.get(
                        "mobile_phone_detections",
                        0
                    )
                ),

            # -----------------------------
            # SPEECH / NLP
            # -----------------------------

            "word_count":
                float(
                    nlp.get(
                        "word_count",
                        0
                    )
                ),

            "sentence_count":
                float(
                    nlp.get(
                        "sentence_count",
                        0
                    )
                ),

            "filler_word_count":
                float(
                    nlp.get(
                        "filler_word_count",
                        0
                    )
                ),

            "average_words_per_sentence":
                float(
                    nlp.get(
                        "average_words_per_sentence",
                        0.0
                    )
                ),
        }

        return features