from app.services.nlp_service import (
    NLPService
)


nlp_service = NLPService()


transcript = """
Hello, my name is John.
I am a software developer.
Basically, I have three years of experience.
I like solving problems and building applications.
"""


result = nlp_service.analyze(
    transcript
)


print("NLP analysis:")
print("----------------")

print(
    "Word count:",
    result["word_count"]
)

print(
    "Sentence count:",
    result["sentence_count"]
)

print(
    "Filler word count:",
    result["filler_word_count"]
)

print(
    "Filler words:",
    result["filler_words"]
)

print(
    "Average words per sentence:",
    result[
        "average_words_per_sentence"
    ]
)
