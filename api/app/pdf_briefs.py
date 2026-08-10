from io import BytesIO
from pathlib import Path

from pypdf import PdfReader

from .domain import PDFBriefResponse

MAX_PDF_BYTES = 2 * 1024 * 1024
MAX_PDF_PAGES = 5


class PDFBriefError(ValueError):
    def __init__(self, detail: str, status_code: int = 422) -> None:
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


def extract_pdf_brief(
    *,
    file_name: str | None,
    content_type: str | None,
    content: bytes,
) -> PDFBriefResponse:
    display_name = _display_name(file_name)
    if content_type != "application/pdf":
        raise PDFBriefError("Upload a PDF document with the application/pdf content type.", 415)
    if Path(display_name).suffix.lower() != ".pdf":
        raise PDFBriefError("The uploaded document must use a .pdf filename.", 415)
    if len(content) > MAX_PDF_BYTES:
        raise PDFBriefError("The PDF is larger than the 2 MiB demonstration limit.", 413)
    if not content.startswith(b"%PDF-"):
        raise PDFBriefError("The uploaded file does not have a valid PDF signature.")

    try:
        reader = PdfReader(BytesIO(content), strict=True)
        if reader.is_encrypted:
            raise PDFBriefError("Encrypted PDFs are not supported in this demonstration.")
        page_count = len(reader.pages)
        if page_count == 0:
            raise PDFBriefError("The PDF does not contain any pages.")
        if page_count > MAX_PDF_PAGES:
            raise PDFBriefError("The PDF has more than the five-page demonstration limit.")
        extracted = "\n".join(page.extract_text() or "" for page in reader.pages)
    except PDFBriefError:
        raise
    except Exception as error:
        raise PDFBriefError("The PDF could not be read as a valid document.") from error

    normalized = " ".join(extracted.split())
    if not normalized:
        raise PDFBriefError(
            "No searchable text was found. Convert scanned pages to a text-searchable PDF first."
        )
    if len(normalized) < 40:
        raise PDFBriefError("The extracted brief must contain at least 40 characters.")
    if len(normalized) > 1600:
        raise PDFBriefError("The extracted brief exceeds the 1,600-character evaluator limit.")

    return PDFBriefResponse(
        file_name=display_name,
        page_count=page_count,
        character_count=len(normalized),
        text=normalized,
    )


def _display_name(file_name: str | None) -> str:
    normalized = Path(file_name or "client-brief.pdf").name.strip()
    if not normalized:
        normalized = "client-brief.pdf"
    return normalized[-120:]
