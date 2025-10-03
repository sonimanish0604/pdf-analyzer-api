import re
import zlib
from io import BytesIO

import filetype
import fitz  # PyMuPDF
from PyPDF2 import PdfReader


# -------- helpers --------
def _ensure_bytes(src: bytes | bytearray | BytesIO) -> bytes:
    if isinstance(src, (bytes, bytearray)):
        return bytes(src)
    if hasattr(src, "read"):
        pos = src.tell() if hasattr(src, "tell") else 0
        data = src.read()
        try:
            src.seek(pos)
        except Exception:
            pass
        return data
    raise TypeError("expected bytes or file-like")


# -------- detectors --------
def is_true_pdf(file_stream: BytesIO) -> bool:
    file_stream.seek(0)
    kind = filetype.guess(file_stream.read(262))
    file_stream.seek(0)
    return kind is not None and kind.mime == "application/pdf"


def is_encrypted(file_stream: BytesIO) -> bool:
    file_stream.seek(0)
    try:
        reader = PdfReader(file_stream)
        return bool(reader.is_encrypted)
    except Exception:
        # If we can't read it as a PDF, treat as encrypted/unsafe
        return True


_JS_PATTERNS = [
    rb"/S\s*/JavaScript",
    rb"/JavaScript\b",
    rb"/JS\b",
    rb"/OpenAction\b",
    rb"/AA\b",
]


def has_embedded_javascript(src: bytes | bytearray | BytesIO) -> bool:
    data = _ensure_bytes(src)

    # 1) PyMuPDF quick path
    try:
        with fitz.open(stream=data, filetype="pdf") as doc:
            js = (doc.get_javascript() or "").strip()
            if js:
                return True
    except Exception:
        pass

    # 2) Token search
    if any(re.search(p, data) for p in _JS_PATTERNS):
        if re.search(rb"/S\s*/JavaScript", data) and re.search(rb"/JS\b", data):
            return True

    # 3) Decompress Flate streams and search inside
    for m in re.finditer(
        rb"<<[^>]*?/Filter\s*/FlateDecode[^>]*?>>\s*stream(.*?)endstream",
        data,
        flags=re.S,
    ):
        comp = m.group(1)
        nl = comp.find(b"\n")
        if 0 <= nl <= 2:
            comp = comp[nl + 1 :]
        try:
            decomp = zlib.decompress(comp, -15)
        except Exception:
            continue
        if (
            b"/S/JavaScript" in decomp
            or b"/JavaScript" in decomp
            or b"/JS" in decomp
            or b"app.alert" in decomp
        ):
            return True

    return False


def extract_urls(file_stream: BytesIO) -> dict[str, list[str]]:
    file_stream.seek(0)
    try:
        reader = PdfReader(file_stream)
        urls = []
        for page in reader.pages:
            text = page.extract_text() or ""
            urls += re.findall(r"https?://[^\s)>\"]+", text)
        safe = [
            u
            for u in urls
            if any(k in u for k in ("wikipedia.org", "github.com", "mit.edu"))
        ]
        suspicious = list(set(urls) - set(safe))
        return {"safe": safe, "suspicious": suspicious}
    except Exception:
        return {"safe": [], "suspicious": []}


def has_embedded_files_and_names(
    src: bytes | bytearray | BytesIO,
) -> tuple[bool, list[str]]:
    data = _ensure_bytes(src)
    # 1) PyMuPDF: enumerate embedded files
    try:
        names: list[str] = []
        with fitz.open(stream=data, filetype="pdf") as doc:
            for i in range(doc.embfile_count()):
                info = doc.embfile_info(i) or {}
                names.append(
                    info.get("filename") or info.get("name") or f"embedded_{i}"
                )
        if names:
            return True, names
    except Exception:
        pass
    # 2) Fallback: infer names from Filespec dictionaries
    names = re.findall(rb"/F\s*\(([^)]+)\)", data)
    names += re.findall(rb"/UF\s*\(([^)]+)\)", data)
    out = [n.decode("latin-1", "ignore") for n in names]
    return (len(out) > 0), out
