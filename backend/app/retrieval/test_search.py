import sys

from app.retrieval.search import (
    search_policy_chunks,
)


def main():

    if len(sys.argv) < 2:
        raise SystemExit(
            'Usage: python -m '
            'app.retrieval.test_search '
            '"your question"'
        )

    question = " ".join(
        sys.argv[1:]
    )

    results = search_policy_chunks(
        question,
        limit=5,
    )

    print("\nQuestion:")
    print(question)

    print("\nRetrieved chunks:")

    for index, result in enumerate(
        results,
        start=1,
    ):

        print(
            f"\n--- Result {index} ---"
        )

        print(
            f"Score: "
            f"{result['score']}"
        )

        print(
            f"Source: "
            f"{result['filename']} "
            f"(page {result['page_number']})"
        )

        print(
            f"Chunk: "
            f"{result['chunk_index']}"
        )

        print()

        print(
            result["text"]
        )


if __name__ == "__main__":
    main()