from io import BytesIO
from typing import List, Any

import docx2txt
from langchain.docstore.document import Document
from pypdf import PdfReader
from hashlib import md5

from dataclasses import dataclass
from abc import abstractmethod


@dataclass(frozen=True)
class File:
    """Represents an uploaded file comprised of Documents"""

    name: str
    id: str  # unique hash of the file
    metadata: dict[str, Any] = {}
    docs: List[Document] = []

    @classmethod
    @abstractmethod
    def from_bytes(cls, file: BytesIO) -> "File":
        """Creates a File from a BytesIO object"""


class DocxFile(File):
    @classmethod
    def from_bytes(cls, file: BytesIO) -> "DocxFile":
        text = docx2txt.process(file)
        doc = Document(page_content=text)
        return cls(name=file.name, id=md5(file.read()).hexdigest(), docs=[doc])


class PdfFile(File):
    @classmethod
    def from_bytes(cls, file: BytesIO) -> "PdfFile":
        pdf = PdfReader(file)
        docs = []
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            doc = Document(page_content=text)
            doc.metadata["page"] = i + 1
            docs.append(doc)
        return cls(name=file.name, id=md5(file.read()).hexdigest(), docs=docs)


class TxtFile(File):
    @classmethod
    def from_bytes(cls, file: BytesIO) -> "TxtFile":
        text = file.read().decode("utf-8")
        file.seek(0)
        doc = Document(page_content=text)
        return cls(name=file.name, id=md5(file.read()).hexdigest(), docs=[doc])


def read_file(file: BytesIO) -> File:
    """Reads an uploaded file and returns a File object"""
    if file.name.endswith(".docx"):
        return DocxFile.from_bytes(file)
    elif file.name.endswith(".pdf"):
        return PdfFile.from_bytes(file)
    elif file.name.endswith(".txt"):
        return TxtFile.from_bytes(file)
    else:
        raise NotImplementedError
