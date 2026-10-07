from app.services.speech_nlp_service import (
    SpeechNLPService
)


service = SpeechNLPService()

result = service.analyze(
    "test_audio.wav"
)


print("Speech + NLP analysis:")
print("-----------------------")

print(
    "Language:",
    result["language"]
)

print(
    "Language probability:",
    result["language_probability"]
)

print(
    "Transcript:"
)

print(
    result["transcript"]
)

print()

print("NLP features:")

print(
    "Word count:",
    result["nlp"]["word_count"]
)

print(
    "Sentence count:",
    result["nlp"]["sentence_count"]
)

print(
    "Filler word count:",
    result["nlp"]["filler_word_count"]
)

print(
    "Filler words:",
    result["nlp"]["filler_words"]
)

print(
    "Average words per sentence:",
    result["nlp"][
        "average_words_per_sentence"
    ]
)
