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


def _extract_pdf_text(source) -> str:
    pdf_reader = PdfReader(source)
    text_content = ""
    for page in pdf_reader.pages:
        text_content += page.extract_text() or ""
    return text_content.strip()


@router.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_pdf(file: UploadFile = File(...)):
    file_name = os.path.basename(file.filename or "")
    file_path = file.filename or file_name
    if not file_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is missing a filename.",
        )

    try:
        pdf_bytes = await file.read()
        text_content = _extract_pdf_text(BytesIO(pdf_bytes)) if pdf_bytes else ""
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An error occurred while reading the PDF: {str(e)}",
        )

    if not text_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "No extractable text found in the uploaded PDF. "
                "Scanned PDFs without a text layer cannot be used."
            ),
        )

    pdf_processor = TextProcessor(
        path_to_file=file_path,
        name_file=file_name,
    )
    pdf_processor.process_whole_pdf(text_content)

    return {
        "message": "PDF indexed. You can now ask questions without uploading again.",
        "file_name": file_name,
    }


@router.post("/ask", status_code=status.HTTP_202_ACCEPTED)
async def ask_question(
    query: str = Form(...),
    file_name: str | None = Form(None),
):
    query_processor = QueryProcessor()
    answer, sources = query_processor.process_query(query, file_name=file_name)

    if answer is None:
        detail = (
            f"No indexed PDF named '{file_name}'."
            if file_name
            else "No PDF has been indexed yet. Upload a file via POST /home/upload first."
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

    return {"answer": answer, "sources": sources}
