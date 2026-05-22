"""
Resume Service — PDF parsing and file management business logic

Key design decisions:
- pdfplumber is SYNCHRONOUS — always run in threadpool executor
- File storage is local (UPLOAD_DIR/{user_id}/{filename})
- Each resume's parsed text is stored in MySQL for fast retrieval
"""

import pdfplumber


def parse_pdf_file(file_path: str) -> str:
    """
    Extract all text from PDF using pdfplumber.

    This is a SYNCHRONOUS function — it blocks while reading the PDF.
    Always call via run_in_executor to avoid blocking the async event loop.

    Example of correct usage in router:
        loop = asyncio.get_event_loop()
        text = await loop.run_in_executor(None, parse_pdf_file, file_path)

    Args:
        file_path: Absolute path to the PDF file on disk

    Returns:
        Extracted text content as a single string
    """
    full_text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + "\n"
    return full_text.strip()


def parse_text_file(file_path: str) -> str:
    """
    Read plain text resume file and return content.

    Also synchronous — use run_in_executor for consistency.

    Args:
        file_path: Absolute path to the text file

    Returns:
        File content as string
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()
