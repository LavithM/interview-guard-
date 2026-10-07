import re


class NLPService:

    FILLER_WORDS = {
        "um",
        "uh",
        "erm",
        "hmm",
        "like",
        "basically",
        "actually",
        "you know",
        "i mean",
    }

    def analyze(self, transcript: str):

        if not transcript:
            return {
                "word_count": 0,
                "sentence_count": 0,
                "filler_word_count": 0,
                "filler_words": [],
                "average_words_per_sentence": 0.0,
            }

        transcript = transcript.strip()

        # -------------------------------------------------
        # WORDS
        # -------------------------------------------------

        words = re.findall(
            r"\b[\w']+\b",
            transcript.lower()
        )

        word_count = len(words)

        # -------------------------------------------------
        # SENTENCES
        # -------------------------------------------------

        sentences = re.split(
            r"[.!?]+",
            transcript
        )

        sentences = [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

        sentence_count = len(sentences)

        # -------------------------------------------------
        # FILLER WORDS
        # -------------------------------------------------

        filler_words = []

        for word in words:

            if word in self.FILLER_WORDS:
                filler_words.append(word)

        filler_word_count = len(
            filler_words
        )

        # -------------------------------------------------
        # AVERAGE SENTENCE LENGTH
        # -------------------------------------------------

        if sentence_count > 0:

            average_words_per_sentence = (
                word_count
                / sentence_count
            )

        else:

            average_words_per_sentence = 0.0

        # -------------------------------------------------
        # RESULT
        # -------------------------------------------------

        return {
            "word_count": word_count,

            "sentence_count":
                sentence_count,

            "filler_word_count":
                filler_word_count,

            "filler_words":
                filler_words,

            "average_words_per_sentence":
                round(
                    average_words_per_sentence,
                    2
                ),
        }