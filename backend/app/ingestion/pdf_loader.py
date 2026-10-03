from hashlib import sha256
from pathlib import Path

from pypdf import PdfReader


def load_pdf_pages(
    pdf_path: str | Path,
) -> list[dict]:

    path = Path(pdf_path)

    document_id = sha256(
        path.read_bytes()
    ).hexdigest()

    reader = PdfReader(
        str(path)
    )

    pages = []

    for page_number, page in enumerate(
        reader.pages,
        start=1,
    ):
        text = (
            page.extract_text() or ""
        ).strip()

        if not text:
            continue

        pages.append(
            {
                "document_id": document_id,
                "source": "pdf",
                "filename": path.name,
                "page_number": page_number,
                "text": text,
            }
        )

    return pages