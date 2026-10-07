from app.services.realtime_analysis_service import (
    RealtimeAnalysisService
)


service = RealtimeAnalysisService()

try:

    result = service.process_speech(
        "test_audio.wav"
    )

    print("Realtime speech analysis:")
    print("-------------------------")

    print(
        "Transcript:",
        result["transcript"]
    )

    print(
        "Language:",
        result["language"]
    )

    print(
        "Language probability:",
        result["language_probability"]
    )

    print(
        "NLP:",
        result["nlp"]
    )

    window = service.build_feature_window()

    print()
    print("Feature window:")
    print("----------------")

    print(
        "Transcript:",
        window["transcript"]
    )

    print(
        "Language:",
        window["language"]
    )

    print(
        "NLP:",
        window["nlp"]
    )

    print(
        "Speech samples:",
        window["speech_samples"]
    )

finally:

    service.close()
    