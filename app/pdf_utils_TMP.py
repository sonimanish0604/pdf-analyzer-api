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

#--09/15 -- commenting this 
#def has_embedded_javascript(file_bytes: bytes) -> bool:
#    try:
#        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
#            js = doc.get_javascript()
#            return js.strip() != ""
#    except Exception:
#        return False
#--adding below
# in app/pdf_utils.py
import io, re, zlib
import fitz  # PyMuPDF

_JS_PATTERNS = [
    rb"/S\s*/JavaScript",  # action type
    rb"/JavaScript\b",     # names tree or general marker
    rb"/JS\b",             # /JS entry
    rb"/OpenAction\b",     # doc-level auto action
    rb"/AA\b",             # additional actions
]

def _ensure_bytes(src):
    if isinstance(src, (bytes, bytearray)):
        return bytes(src)
    if hasattr(src, "read"):
        pos = src.tell() if hasattr(src, "tell") else 0
        data = src.read()
        try: src.seek(pos)
        except Exception: pass
        return data
    raise TypeError("expected bytes or file-like")

def has_embedded_javascript(src) -> bool:
    data = _ensure_bytes(src)

    # 1) Quick path via PyMuPDF
    try:
        with fitz.open(stream=data, filetype="pdf") as doc:
            js = (doc.get_javascript() or "").strip()
            if js:
                return True
    except Exception:
        pass

    # 2) Token search in raw bytes
    if any(re.search(p, data) for p in _JS_PATTERNS):
        if re.search(rb"/S\s*/JavaScript", data) and re.search(rb"/JS\b", data):
            return True

    # 3) Decompress Flate streams and look for JS markers
    for m in re.finditer(rb"<<[^>]*?/Filter\s*/FlateDecode[^>]*?>>\s*stream(.*?)endstream",
                         data, flags=re.S):
        comp = m.group(1)
        nl = comp.find(b"\n")
        if 0 <= nl <= 2:  # trim \n or \r\n after 'stream'
            comp = comp[nl+1:]
        try:
            decomp = zlib.decompress(comp, -15)  # raw deflate
        except Exception:
            continue
        if (b"/S/JavaScript" in decomp or b"/JavaScript" in decomp or b"/JS" in decomp
                or b"app.alert" in decomp):
            return True

    return False
#---done adding 09/15
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
