def grade_retrieval(state):
    chunks = state.get(
        "retrieved_chunks",
        [],
    )

    if not chunks:
        return {
            "retrieval_quality": "poor",
            "retrieval_score": None,
        }

    top_score = chunks[0]["score"]

    quality = (
        "good"
        if top_score >= 0.65
        else "poor"
    )

    return {
        "retrieval_quality": quality,
        "retrieval_score": top_score,
    }