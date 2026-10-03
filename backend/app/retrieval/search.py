from langchain_ollama import OllamaEmbeddings

from app.vectorstore.milvus import milvus_client


COLLECTION_NAME = "enterprise_policy_chunks"


embeddings = OllamaEmbeddings(
    model="nomic-embed-text"
)


def search_policy_chunks(
    query: str,
    limit: int = 5,
) -> list[dict]:

    query_vector = embeddings.embed_query(
        query
    )

    results = milvus_client.search(
        collection_name=COLLECTION_NAME,
        data=[query_vector],
        limit=limit,
        output_fields=[
            "text",
            "document_id",
            "source",
            "filename",
            "page_number",
            "chunk_index",
        ],
    )

    matches = []

    for result in results[0]:

        entity = result["entity"]

        matches.append(
            {
                "score": result["distance"],
                "text": entity["text"],
                "document_id":
                    entity["document_id"],
                "source":
                    entity["source"],
                "filename":
                    entity["filename"],
                "page_number":
                    entity["page_number"],
                "chunk_index":
                    entity["chunk_index"],
            }
        )

    return matches