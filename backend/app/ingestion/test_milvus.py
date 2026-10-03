from langchain_ollama import OllamaEmbeddings

from app.vectorstore.milvus import milvus_client


COLLECTION_NAME = "aiassistant_documents"

embeddings = OllamaEmbeddings(
    model="nomic-embed-text"
)


def main():

    documents = [
        "Comprehensive car insurance may cover accidental damage to your own vehicle.",
        "Third-party insurance covers liability for damage caused to other people or property.",
        "A policy excess is the amount the customer may need to contribute toward a claim.",
    ]

    vectors = embeddings.embed_documents(
        documents
    )

    dimension = len(vectors[0])

    print(
        f"Embedding dimension: {dimension}"
    )

    if milvus_client.has_collection(
        COLLECTION_NAME
    ):
        milvus_client.drop_collection(
            COLLECTION_NAME
        )

    milvus_client.create_collection(
        collection_name=COLLECTION_NAME,
        dimension=dimension,
        metric_type="COSINE",
    )

    data = []

    for index, (
        text,
        vector,
    ) in enumerate(
        zip(documents, vectors)
    ):
        data.append(
            {
                "id": index,
                "vector": vector,
                "text": text,
            }
        )

    milvus_client.insert(
        collection_name=COLLECTION_NAME,
        data=data,
    )

    question = (
        "What insurance protects my own car "
        "if I have an accident?"
    )

    query_vector = (
        embeddings.embed_query(question)
    )

    results = milvus_client.search(
        collection_name=COLLECTION_NAME,
        data=[query_vector],
        limit=2,
        output_fields=["text"],
    )

    print("\nQuestion:")
    print(question)

    print("\nRetrieved results:")

    for result in results[0]:
        print(
            result["distance"],
            "->",
            result["entity"]["text"],
        )


if __name__ == "__main__":
    main()