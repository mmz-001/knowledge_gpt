import re
from io import BytesIO
from typing import List

import docx2txt
from langchain.docstore.document import Document
from pypdf import PdfReader
from pydantic import BaseModel
from hashlib import md5


class File(BaseModel):
    """Represents an uploaded file comprised of Documents"""

    name: str
    id: str  # unique hash of the file
    metadata: dict[str, str | float | int] = {}
    docs: List[Document] = []


def parse_docx(file: BytesIO) -> str:
    text = docx2txt.process(file)
    # Remove multiple newlines
    text = re.sub(r"\n\s*\n", "\n\n", text)
    return text


def parse_pdf(file: BytesIO) -> List[str]:
    pdf = PdfReader(file)
    output = []
    for page in pdf.pages:
        text = page.extract_text()
        # Merge hyphenated words
        text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)
        # Fix newlines in the middle of sentences
        text = re.sub(r"(?<!\n\s)\n(?!\s\n)", " ", text.strip())
        # Remove multiple newlines
        text = re.sub(r"\n\s*\n", "\n\n", text)

        output.append(text)

    return output


def parse_txt(file: BytesIO) -> str:
    text = file.read().decode("utf-8")
    # Remove multiple newlines
    text = re.sub(r"\n\s*\n", "\n\n", text)
    return text


def to_file(uploaded_file: BytesIO) -> File:
    """Parses an uploaded file and returns a File object with Documents"""
    docs = []
    id = md5(uploaded_file.read()).hexdigest()
    uploaded_file.seek(0)
    file = File(name=uploaded_file.name, id=id)

    if uploaded_file.name.endswith(".pdf"):
        texts = parse_pdf(uploaded_file)
        for i, text in enumerate(texts):
            doc = Document(page_content=text)
            doc.metadata["page"] = i + 1
            docs.append(doc)

    elif uploaded_file.name.endswith(".docx"):
        # No page numbers for docx
        text = parse_docx(uploaded_file)
        docs = [Document(page_content=text)]

    elif uploaded_file.name.endswith(".txt"):
        # No page numbers for txt
        text = parse_txt(uploaded_file)
        docs = [Document(page_content=text)]

    file.docs = docs
    return file
