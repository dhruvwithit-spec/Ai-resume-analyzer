from __future__ import annotations

import re
from collections import Counter
from functools import lru_cache

import spacy


@lru_cache(maxsize=1)
def get_nlp():
    """
    Load a spaCy pipeline once and reuse it across the app.

    The code tries to load `en_core_web_sm` first. If that model is not installed,
    it falls back to a lightweight blank English pipeline so the app still works.
    """

    try:
        return spacy.load("en_core_web_sm")
    except Exception:
        nlp = spacy.blank("en")
        if "sentencizer" not in nlp.pipe_names:
            nlp.add_pipe("sentencizer")
        return nlp


def clean_text(text: str) -> str:
    """Normalize whitespace and remove a few noisy characters."""

    if not text:
        return ""

    text = text.replace("\u2022", " ")
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def preprocess_text(text: str) -> dict:
    """
    Clean and tokenize text with spaCy.

    Returns a dictionary to keep downstream modules simple and beginner-friendly.
    """

    cleaned_text = clean_text(text)
    if not cleaned_text:
        return {
            "cleaned_text": "",
            "normalized_text": "",
            "tokens": [],
            "lemmas": [],
            "keywords": [],
        }

    nlp = get_nlp()
    doc = nlp(cleaned_text)

    tokens = []
    lemmas = []

    for token in doc:
        if token.is_space or token.is_punct:
            continue

        normalized = token.lemma_.lower().strip() if token.lemma_ else token.text.lower().strip()
        normalized = normalized if normalized != "-pron-" else token.text.lower().strip()

        tokens.append(token.text.lower().strip())
        if (
            normalized
            and not token.is_stop
            and not token.like_num
            and len(normalized) > 2
        ):
            lemmas.append(normalized)

    keyword_counts = Counter(lemmas)
    keywords = [word for word, _ in keyword_counts.most_common(25)]

    normalized_text = " " + " ".join(tokens) + " "

    return {
        "cleaned_text": cleaned_text,
        "normalized_text": normalized_text,
        "tokens": tokens,
        "lemmas": lemmas,
        "keywords": keywords,
    }
