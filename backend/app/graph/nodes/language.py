from langdetect import detect


SUPPORTED_LANGUAGES = {
    "en",
    "da",
    "no",
    "sv",
}


def detect_input_language(state):
    query = state["original_query"]

    try:
        language = detect(query)
    except Exception:
        language = "en"

    if language not in SUPPORTED_LANGUAGES:
        language = "en"

    return {
        "language": language,
        "requires_translation":
            language != "en",
    }