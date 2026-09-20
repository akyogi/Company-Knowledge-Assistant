import os
from io import BytesIO

from pypdf import PdfReader
from fastapi import HTTPException, APIRouter, UploadFile, File, Form
from starlette import status

from tools.TextProcessor import TextProcessor
from tools.QueryProcessor import QueryProcessor

router = APIRouter(
    prefix="/home",
    tags=["home"],
)


def _resolve_pdf_path(file_path: str, file_name: str) -> str:
    if os.path.isfile(file_path):
        return file_path
    joined = os.path.join(file_path, file_name)
    if os.path.isfile(joined):
        return joined
    return file_path


def _extract_pdf_text(source) -> str:
    pdf_reader = PdfReader(source)
    text_content = ""
    for page in pdf_reader.pages:
        text_content += page.extract_text() or ""
    return text_content.strip()


@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def get_response(
    query: str = Form(...),
    file_name: str = Form(...),
    file_path: str = Form(...),
    file: UploadFile | None = File(None),
):
    text_content = ""
    resolved_path = _resolve_pdf_path(file_path, file_name)

    try:
        if file is not None:
            pdf_bytes = await file.read()
            if pdf_bytes:
                text_content = _extract_pdf_text(BytesIO(pdf_bytes))
        if not text_content and os.path.isfile(resolved_path):
            with open(resolved_path, "rb") as disk_file:
                text_content = _extract_pdf_text(disk_file)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An error occurred while reading the PDF: {str(e)}",
        )

    if not text_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "No extractable text found in the PDF. Upload the file in the "
                "`file` form field, or pass a valid file_path (folder or full "
                "path) plus file_name. Scanned PDFs without a text layer cannot be used."
            ),
        )

    pdf_processor = TextProcessor(
        path_to_file=resolved_path,
        name_file=file_name,
    )
    pdf_processor.process_whole_pdf(text_content)

    query_processor = QueryProcessor()
    answer, sources = query_processor.process_query(query)

    return {"answer": answer, "sources": sources}

