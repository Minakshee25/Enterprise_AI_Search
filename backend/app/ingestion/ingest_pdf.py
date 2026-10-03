import sys

from langchain_ollama import OllamaEmbeddings

from app.ingestion.chunker import chunk_pages
from app.ingestion.pdf_loader import load_pdf_pages
from app.vectorstore.milvus import milvus_client
from app.config import settings

COLLECTION_NAME = "enterprise_policy_chunks"

embeddings = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url=settings.ollama_base_url,
)


def ensure_collection(
    dimension: int,
):

    if milvus_client.has_collection(
        COLLECTION_NAME
    ):
        return

    milvus_client.create_collection(
        collection_name=COLLECTION_NAME,
        dimension=dimension,
        metric_type="COSINE",
        auto_id=True,
        enable_dynamic_field=True,
    )


def ingest_pdf(
    pdf_path: str,
):

    pages = load_pdf_pages(
        pdf_path
    )

    print(
        f"Extracted {len(pages)} pages"
    )

    chunks = chunk_pages(
        pages
    )

    print(
        f"Created {len(chunks)} chunks"
    )

    if not chunks:
        raise ValueError(
            "No text chunks were extracted"
        )

    document_id = chunks[0]["document_id"]

    milvus_client.delete(
        collection_name=COLLECTION_NAME,
        filter=f'document_id == "{document_id}"',
    )


    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    vectors = embeddings.embed_documents(
        texts
    )

    dimension = len(
        vectors[0]
    )

    ensure_collection(
        dimension
    )

    data = []

    for chunk, vector in zip(
        chunks,
        vectors,
    ):

        data.append(
            {
                "vector": vector,
                "text": chunk["text"],
                "document_id":
                    chunk["document_id"],
                "source":
                    chunk["source"],
                "filename":
                    chunk["filename"],
                "page_number":
                    chunk["page_number"],
                "chunk_index":
                    chunk["chunk_index"],
            }
        )

    result = milvus_client.insert(
        collection_name=COLLECTION_NAME,
        data=data,
    )

    print(
        f"Inserted {result['insert_count']} chunks"
    )


if __name__ == "__main__":

    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python -m "
            "app.ingestion.ingest_pdf "
            "<pdf_path>"
        )

    ingest_pdf(
        sys.argv[1]
    )