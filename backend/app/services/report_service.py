from app.services.temporal_analysis_service import (
    TemporalAnalysisService
)


def generate_report(session):

    features = session.get(
        "features",
        []
    )

    temporal_service = (
        TemporalAnalysisService()
    )

    temporal_analysis = (
        temporal_service.analyze(
            features
        )
    )

    # --------------------------------------------------
    # BASIC ANALYSIS
    # --------------------------------------------------

    total_windows = len(
        features
    )

    if total_windows == 0:

        average_gaze = 0.0

        total_blinks = 0

        average_lip_movement = 0.0

        average_audio_level = 0.0

    else:

        gaze_values = [
            float(
                item.get(
                    "gaze",
                    0.0
                )
            )
            for item in features
        ]

        average_gaze = (
            sum(gaze_values)
            / len(gaze_values)
        )

        total_blinks = sum(
            int(
                item.get(
                    "blink",
                    0
                )
            )
            for item in features
        )

        lip_values = [
            float(
                item.get(
                    "lip_movement",
                    0.0
                )
            )
            for item in features
        ]

        average_lip_movement = (
            sum(lip_values)
            / len(lip_values)
        )

        audio_values = [
            float(
                item.get(
                    "audio_level",
                    0.0
                )
            )
            for item in features
        ]

        average_audio_level = (
            sum(audio_values)
            / len(audio_values)
        )

    # --------------------------------------------------
    # HEAD POSE
    # --------------------------------------------------

    if total_windows > 0:

        yaw_values = [
            float(
                item.get(
                    "head_pose",
                    {}
                ).get(
                    "yaw",
                    0.0
                )
            )
            for item in features
        ]

        pitch_values = [
            float(
                item.get(
                    "head_pose",
                    {}
                ).get(
                    "pitch",
                    0.0
                )
            )
            for item in features
        ]

        roll_values = [
            float(
                item.get(
                    "head_pose",
                    {}
                ).get(
                    "roll",
                    0.0
                )
            )
            for item in features
        ]

        average_yaw = (
            sum(yaw_values)
            / len(yaw_values)
        )

        average_pitch = (
            sum(pitch_values)
            / len(pitch_values)
        )

        average_roll = (
            sum(roll_values)
            / len(roll_values)
        )

    else:

        average_yaw = 0.0
        average_pitch = 0.0
        average_roll = 0.0

    # --------------------------------------------------
    # INDICATOR COUNTS
    # --------------------------------------------------

    indicator_counts = {}

    for feature in features:

        fusion = feature.get(
            "fusion",
            {}
        )

        indicators = fusion.get(
            "indicators",
            []
        )

        for indicator in indicators:

            indicator_counts[indicator] = (
                indicator_counts.get(
                    indicator,
                    0
                ) + 1
            )

    # --------------------------------------------------
    # SPEECH
    # --------------------------------------------------

    speech_percentage = (
        temporal_analysis.get(
            "speech_percentage",
            0.0
        )
    )

    # --------------------------------------------------
    # FACE
    # --------------------------------------------------

    face_presence_percentage = (
        temporal_analysis.get(
            "face_presence_percentage",
            0.0
        )
    )

    # --------------------------------------------------
    # OBJECT INFORMATION
    # --------------------------------------------------

    object_analysis = {

        "additional_person_windows":
            temporal_analysis.get(
                "additional_person_windows",
                0
            ),

        "additional_person_percentage":
            temporal_analysis.get(
                "additional_person_percentage",
                0.0
            ),

        "mobile_phone_windows":
            temporal_analysis.get(
                "mobile_phone_windows",
                0
            ),

        "mobile_phone_percentage":
            temporal_analysis.get(
                "mobile_phone_percentage",
                0.0
            ),

        "detected_objects":
            temporal_analysis.get(
                "detected_objects",
                {}
            ),
    }

    # --------------------------------------------------
    # TRANSCRIPT
    # --------------------------------------------------

    transcripts = []

    total_word_count = 0
    total_filler_words = 0

    for feature in features:

        transcript = feature.get(
            "transcript",
            ""
        )

        if transcript:

            transcripts.append(
                transcript
            )

        nlp = feature.get(
            "nlp",
            {}
        )

        total_word_count += int(
            nlp.get(
                "word_count",
                0
            )
        )

        total_filler_words += int(
            nlp.get(
                "filler_word_count",
                0
            )
        )

    combined_transcript = " ".join(
        transcripts
    )

    # --------------------------------------------------
    # TIMELINE
    # --------------------------------------------------

    timeline = []

    for index, feature in enumerate(
        features,
        start=1
    ):

        timeline.append({

            "window_number":
                index,

            "timestamp":
                feature.get(
                    "timestamp",
                    0.0
                ),

            "face_detected":
                feature.get(
                    "face_detected",
                    False
                ),

            "gaze":
                feature.get(
                    "gaze",
                    0.0
                ),

            "blink":
                feature.get(
                    "blink",
                    0
                ),

            "head_pose":
                feature.get(
                    "head_pose",
                    {}
                ),

            "lip_movement":
                feature.get(
                    "lip_movement",
                    0.0
                ),

            "audio_level":
                feature.get(
                    "audio_level",
                    0.0
                ),

            "speech_detected":
                feature.get(
                    "speech_detected",
                    False
                ),

            "object_detection":
                feature.get(
                    "object_detection",
                    {}
                ),

            "transcript":
                feature.get(
                    "transcript",
                    ""
                ),

            "nlp":
                feature.get(
                    "nlp",
                    {}
                ),

            "fusion":
                feature.get(
                    "fusion",
                    {}
                ),
        })

    # --------------------------------------------------
    # FINAL REPORT
    # --------------------------------------------------

    return {

        "interview_id":
            session.get(
                "interview_id"
            ),

        "candidate": {

            "name":
                session.get(
                    "name"
                ),

            "email":
                session.get(
                    "email"
                ),

            "role":
                session.get(
                    "role"
                ),
        },

        "interview": {

            "started_at":
                session.get(
                    "started_at"
                ),

            "ended_at":
                session.get(
                    "ended_at"
                ),

            "status":
                session.get(
                    "status"
                ),
        },

        "analysis": {

            "total_feature_windows":
                total_windows,

            "average_gaze":
                round(
                    average_gaze,
                    4
                ),

            "blink_count":
                total_blinks,

            "average_head_pose": {

                "yaw":
                    round(
                        average_yaw,
                        2
                    ),

                "pitch":
                    round(
                        average_pitch,
                        2
                    ),

                "roll":
                    round(
                        average_roll,
                        2
                    ),
            },

            "average_lip_movement":
                round(
                    average_lip_movement,
                    4
                ),

            "average_audio_level":
                round(
                    average_audio_level,
                    4
                ),

            "speech_percentage":
                speech_percentage,

            "face_presence_percentage":
                face_presence_percentage,

            "indicator_counts":
                indicator_counts,

            "temporal":
                temporal_analysis,

            "objects":
                object_analysis,

            "speech": {

                "word_count":
                    total_word_count,

                "filler_word_count":
                    total_filler_words,

                "transcript":
                    combined_transcript,
            },
        },

        "timeline":
            timeline,
    }