from app.services.dataset_service import (
    DatasetService
)


service = DatasetService()


file_path = (
    "dataset/interview_features.csv"
)


service.create_dataset_file(
    file_path
)


sample_features = {

    "face_detected": 1,

    "face_presence_percentage": 96.0,

    "gaze": 0.72,

    "blink": 3,

    "yaw": 2.5,

    "pitch": -1.2,

    "roll": 0.8,

    "lip_movement": 0.13,

    "audio_level": 0.015,

    "speech_detected": 1,

    "dtw_distance": 0.10,

    "lip_audio_alignment": 0.90,

    "maximum_person_count": 1,

    "person_count_above_one": 0,

    "mobile_phone_detected": 0,

    "mobile_phone_detections": 0,

    "word_count": 40,

    "sentence_count": 5,

    "filler_word_count": 2,

    "average_words_per_sentence": 8.0,
}


service.append_sample(
    file_path=file_path,
    features=sample_features,
    label=0
)


print(
    "Dataset file created:"
)

print(
    file_path
)