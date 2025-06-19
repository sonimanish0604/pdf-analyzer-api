from PyPDF2 import PdfReader
import fitz  # PyMuPDF
import pikepdf
import re
import filetype
from typing import Tuple, List, Dict
from io import BytesIO


def is_true_pdf(file_stream: BytesIO) -> bool:
    file_stream.seek(0)
    kind = filetype.guess(file_stream.read(262))
    file_stream.seek(0)
    return kind is not None and kind.mime == 'application/pdf'


def is_encrypted(file_stream: BytesIO) -> bool:
    file_stream.seek(0)
    try:
        reader = PdfReader(file_stream)
        return reader.is_encrypted
    except:
        return True


def has_embedded_javascript(file_bytes: bytes) -> bool:
    try:
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            js = doc.get_javascript()
            return js.strip() != ""
    except Exception:
        return False


def extract_urls(file_stream: BytesIO) -> Dict[str, List[str]]:
    file_stream.seek(0)
    try:
        reader = PdfReader(file_stream)
        urls = []
        for page in reader.pages:
            text = page.extract_text() or ""
            urls += re.findall(r'https?://[^\s)>"]+', text)
        # Naive safe/suspicious split
        safe = [u for u in urls if any(k in u for k in ("wikipedia.org", "github.com", "mit.edu"))]
        suspicious = list(set(urls) - set(safe))
        return {"safe": safe, "suspicious": suspicious}
    except:
        return {"safe": [], "suspicious": []}


def has_embedded_files_and_names(file_stream: BytesIO) -> Tuple[bool, List[str]]:
    file_stream.seek(0)
    try:
        with pikepdf.open(file_stream) as pdf:
            names = []
            if "/Names" in pdf.root:
                embedded_files = pdf.root["/Names"].get("/EmbeddedFiles", None)
                if embedded_files:
                    for i in range(0, len(embedded_files["/Names"]), 2):
                        names.append(str(embedded_files["/Names"][i]))
            return (len(names) > 0, names)
    except:
        return (False, [])
