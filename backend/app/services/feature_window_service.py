import time

from app.services.lip_sync_service import (
    LipSyncService
)


class FeatureWindowService:

    def __init__(self):
        self.visual_frames = []
        self.audio_windows = []
        self.speech_windows = []
        self.object_windows = []

        self.start_time = time.time()

        self.lip_sync_service = (
            LipSyncService()
        )

    def add_visual_features(
        self,
        visual_features
    ):
        if visual_features is None:
            return

        self.visual_frames.append(
            visual_features
        )

    def add_audio_features(
        self,
        audio_features
    ):
        if audio_features is None:
            return

        self.audio_windows.append(
            audio_features
        )

    def add_speech_features(
        self,
        speech_features
    ):
        if speech_features is None:
            return

        self.speech_windows.append(
            speech_features
        )

    def add_object_features(
        self,
        object_features
    ):
        if object_features is None:
            return

        self.object_windows.append(
            object_features
        )

    def _safe_float(self, value, default=0.0):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def _safe_int(self, value, default=0):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def _average_mfcc(self):

        if not self.audio_windows:
            return []

        mfcc_lists = []

        for item in self.audio_windows:

            if not isinstance(item, dict):
                continue

            mfcc = item.get(
                "mfcc",
                []
            )

            if mfcc:
                mfcc_lists.append(
                    mfcc
                )

        if not mfcc_lists:
            return []

        number_of_coefficients = len(
            mfcc_lists[0]
        )

        average_mfcc = []

        for index in range(
            number_of_coefficients
        ):

            values = [
                self._safe_float(
                    mfcc[index]
                )
                for mfcc in mfcc_lists
                if len(mfcc) > index
            ]

            if values:

                average = (
                    sum(values)
                    / len(values)
                )

                average_mfcc.append(
                    round(
                        average,
                        4
                    )
                )

        return average_mfcc

    def _build_object_features(self):

        if not self.object_windows:

            return {
                "average_person_count": 0.0,
                "maximum_person_count": 0,
                "person_count_above_one": False,
                "mobile_phone_detected": False,
                "mobile_phone_detections": 0,
                "objects": {},
                "object_samples": 0,
            }

        person_counts = []

        mobile_phone_detections = 0

        object_counts = {}

        for item in self.object_windows:

            if not isinstance(item, dict):
                continue

            person_count = self._safe_int(
                item.get(
                    "person_count",
                    0
                )
            )

            person_counts.append(
                person_count
            )

            objects = item.get(
                "objects",
                []
            )

            if not isinstance(objects, list):
                continue

            for obj in objects:

                if not isinstance(obj, dict):
                    continue

                class_name = obj.get(
                    "class",
                    ""
                )

                if not class_name:
                    continue

                object_counts[class_name] = (
                    object_counts.get(
                        class_name,
                        0
                    ) + 1
                )

                if class_name == "cell phone":
                    mobile_phone_detections += 1

        if person_counts:

            average_person_count = (
                sum(person_counts)
                / len(person_counts)
            )

            maximum_person_count = max(
                person_counts
            )

        else:

            average_person_count = 0.0
            maximum_person_count = 0

        person_count_above_one = any(
            count > 1
            for count in person_counts
        )

        mobile_phone_detected = (
            mobile_phone_detections > 0
        )

        return {
            "average_person_count": round(
                average_person_count,
                2
            ),

            "maximum_person_count":
                maximum_person_count,

            "person_count_above_one":
                person_count_above_one,

            "mobile_phone_detected":
                mobile_phone_detected,

            "mobile_phone_detections":
                mobile_phone_detections,

            "objects":
                object_counts,

            "object_samples":
                len(
                    self.object_windows
                ),
        }

    def _calculate_lip_sync(self):

        lip_movements = [
            self._safe_float(
                item.get(
                    "lip_movement",
                    0.0
                )
            )
            for item in self.visual_frames
            if isinstance(item, dict)
            and item.get(
                "face_detected",
                False
            )
        ]

        audio_levels = [
            self._safe_float(
                item.get(
                    "audio_level",
                    0.0
                )
            )
            for item in self.audio_windows
            if isinstance(item, dict)
        ]

        return self.lip_sync_service.calculate(
            lip_movements,
            audio_levels
        )

    def build_window(self):

        timestamp = (
            time.time()
            - self.start_time
        )

        valid_visual_frames = [
            item
            for item in self.visual_frames
            if isinstance(item, dict)
        ]

        face_frames = [
            item
            for item in valid_visual_frames
            if item.get(
                "face_detected",
                False
            )
        ]

        if face_frames:

            gaze_values = []

            blink_values = []

            yaw_values = []

            pitch_values = []

            roll_values = []

            lip_values = []

            for item in face_frames:

                # Gaze may be a number in some
                # feature-window formats.
                gaze_value = item.get(
                    "gaze",
                    0.0
                )

                if isinstance(
                    gaze_value,
                    dict
                ):
                    gaze_value = gaze_value.get(
                        "gaze_score",
                        gaze_value.get(
                            "score",
                            0.0
                        )
                    )

                gaze_values.append(
                    self._safe_float(
                        gaze_value
                    )
                )

                blink_values.append(
                    self._safe_int(
                        item.get(
                            "blink",
                            0
                        )
                    )
                )

                head_pose = item.get(
                    "head_pose",
                    {}
                )

                if not isinstance(
                    head_pose,
                    dict
                ):
                    head_pose = {}

                yaw_values.append(
                    self._safe_float(
                        head_pose.get(
                            "yaw",
                            0.0
                        )
                    )
                )

                pitch_values.append(
                    self._safe_float(
                        head_pose.get(
                            "pitch",
                            0.0
                        )
                    )
                )

                roll_values.append(
                    self._safe_float(
                        head_pose.get(
                            "roll",
                            0.0
                        )
                    )
                )

                lip_values.append(
                    self._safe_float(
                        item.get(
                            "lip_movement",
                            0.0
                        )
                    )
                )

            average_gaze = (
                sum(gaze_values)
                / len(gaze_values)
            )

            blink_count = sum(
                blink_values
            )

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

            average_lip = (
                sum(lip_values)
                / len(lip_values)
            )

        else:

            average_gaze = 0.0
            blink_count = 0
            average_yaw = 0.0
            average_pitch = 0.0
            average_roll = 0.0
            average_lip = 0.0

        total_visual_samples = len(
            valid_visual_frames
        )

        face_detected_samples = sum(
            1
            for item in valid_visual_frames
            if item.get(
                "face_detected",
                False
            )
        )

        face_presence_percentage = 0.0

        if total_visual_samples > 0:

            face_presence_percentage = (
                face_detected_samples
                / total_visual_samples
            ) * 100

        face_detected = (
            face_detected_samples > 0
        )

        valid_audio_windows = [
            item
            for item in self.audio_windows
            if isinstance(item, dict)
        ]

        if valid_audio_windows:

            audio_levels = [
                self._safe_float(
                    item.get(
                        "audio_level",
                        0.0
                    )
                )
                for item in valid_audio_windows
            ]

            speech_values = [
                bool(
                    item.get(
                        "speech_detected",
                        False
                    )
                )
                for item in valid_audio_windows
            ]

            average_audio_level = (
                sum(audio_levels)
                / len(audio_levels)
            )

            speech_detected = any(
                speech_values
            )

        else:

            average_audio_level = 0.0
            speech_detected = False

        average_mfcc = (
            self._average_mfcc()
        )

        if self.speech_windows:

            transcripts = [
                item.get(
                    "transcript",
                    ""
                )
                for item in self.speech_windows
                if isinstance(item, dict)
            ]

            combined_transcript = " ".join(
                text.strip()
                for text in transcripts
                if isinstance(text, str)
                and text.strip()
            )

            latest_nlp = (
                self.speech_windows[-1].get(
                    "nlp",
                    {}
                )
                if isinstance(
                    self.speech_windows[-1],
                    dict
                )
                else {}
            )

            language = (
                self.speech_windows[-1].get(
                    "language",
                    ""
                )
                if isinstance(
                    self.speech_windows[-1],
                    dict
                )
                else ""
            )

            language_probability = (
                self.speech_windows[-1].get(
                    "language_probability",
                    0.0
                )
                if isinstance(
                    self.speech_windows[-1],
                    dict
                )
                else 0.0
            )

        else:

            combined_transcript = ""
            latest_nlp = {}
            language = ""
            language_probability = 0.0

        object_features = (
            self._build_object_features()
        )

        lip_sync = (
            self._calculate_lip_sync()
        )

        result = {

            "timestamp": round(
                timestamp,
                3
            ),

            "face_detected":
                face_detected,

            "face_presence_percentage":
                round(
                    face_presence_percentage,
                    2
                ),

            "gaze": round(
                average_gaze,
                4
            ),

            "blink":
                blink_count,

            "head_pose": {

                "yaw": round(
                    average_yaw,
                    2
                ),

                "pitch": round(
                    average_pitch,
                    2
                ),

                "roll": round(
                    average_roll,
                    2
                ),
            },

            "lip_movement":
                round(
                    average_lip,
                    4
                ),

            "audio_level":
                round(
                    average_audio_level,
                    4
                ),

            "speech_detected":
                speech_detected,

            "mfcc":
                average_mfcc,

            "transcript":
                combined_transcript,

            "language":
                language,

            "language_probability":
                round(
                    self._safe_float(
                        language_probability
                    ),
                    4
                ),

            "nlp":
                latest_nlp,

            "object_detection":
                object_features,

            "lip_sync":
                lip_sync,

            "visual_samples":
                len(
                    self.visual_frames
                ),

            "audio_samples":
                len(
                    self.audio_windows
                ),

            "speech_samples":
                len(
                    self.speech_windows
                ),

            "object_samples":
                len(
                    self.object_windows
                ),
        }

        # Clear the current window after aggregation.
        self.visual_frames = []
        self.audio_windows = []
        self.speech_windows = []
        self.object_windows = []

        return result

    def reset(self):

        self.visual_frames = []
        self.audio_windows = []
        self.speech_windows = []
        self.object_windows = []

        self.start_time = time.time()
        