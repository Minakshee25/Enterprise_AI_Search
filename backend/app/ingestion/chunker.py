from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150,
)


def chunk_pages(
    pages: list[dict],
) -> list[dict]:

    chunks = []

    chunk_index = 0

    for page in pages:

        page_chunks = (
            text_splitter.split_text(
                page["text"]
            )
        )

        for text in page_chunks:

            chunks.append(
                {
                    "document_id":
                        page["document_id"],

                    "source":
                        page["source"],

                    "filename":
                        page["filename"],

                    "page_number":
                        page["page_number"],

                    "chunk_index":
                        chunk_index,

                    "text":
                        text,
                }
            )

            chunk_index += 1

    return chunks