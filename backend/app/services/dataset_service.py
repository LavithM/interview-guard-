import csv
import os


class DatasetService:

    FEATURE_NAMES = [

        "face_detected",
        "face_presence_percentage",

        "gaze",
        "blink",

        "yaw",
        "pitch",
        "roll",

        "lip_movement",

        "audio_level",
        "speech_detected",

        "dtw_distance",
        "lip_audio_alignment",

        "maximum_person_count",
        "person_count_above_one",

        "mobile_phone_detected",
        "mobile_phone_detections",

        "word_count",
        "sentence_count",
        "filler_word_count",
        "average_words_per_sentence",
    ]

    LABEL_NAME = "label"

    def create_dataset_file(
        self,
        file_path
    ):

        directory = os.path.dirname(
            file_path
        )

        if directory:
            os.makedirs(
                directory,
                exist_ok=True
            )

        columns = (
            self.FEATURE_NAMES
            + [self.LABEL_NAME]
        )

        if not os.path.exists(file_path):

            with open(
                file_path,
                "w",
                newline="",
                encoding="utf-8"
            ) as file:

                writer = csv.DictWriter(
                    file,
                    fieldnames=columns
                )

                writer.writeheader()

        return file_path

    def append_sample(
        self,
        file_path,
        features,
        label
    ):

        columns = (
            self.FEATURE_NAMES
            + [self.LABEL_NAME]
        )

        row = {}

        for feature_name in (
            self.FEATURE_NAMES
        ):

            row[feature_name] = features.get(
                feature_name,
                0
            )

        row[self.LABEL_NAME] = label

        with open(
            file_path,
            "a",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=columns
            )

            writer.writerow(row)
            