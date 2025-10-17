# src/utils/file_parse.py
import io
from pdfminer.high_level import extract_text
import docx
import os

def extract_text_from_pdf(path: str) -> str:
    return extract_text(path)

def extract_text_from_docx(path: str) -> str:
    doc = docx.Document(path)
    full = []
    for p in doc.paragraphs:
        full.append(p.text)
    return "\n".join(full)

def extract_text_simple(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(path)
    elif ext in [".docx", ".doc"]:
        return extract_text_from_docx(path)
    else:
        # fallback to plain read
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
