from io import BytesIO
from typing import List, Any, Optional
import re

import docx2txt
from langchain.docstore.document import Document
from pypdf import PdfReader
from hashlib import md5

from abc import abstractmethod, ABC
from copy import deepcopy


class File(ABC):
    """Represents an uploaded file comprised of Documents"""

    def __init__(
        self,
        name: str,
        id: str,
        metadata: Optional[dict[str, Any]] = None,
        docs: Optional[List[Document]] = None,
    ):
        self.name = name
        self.id = id
        self.metadata = metadata or {}
        self.docs = docs or []

    @classmethod
    @abstractmethod
    def from_bytes(cls, file: BytesIO) -> "File":
        """Creates a File from a BytesIO object"""

    def __repr__(self) -> str:
        return (
            f"File(name={self.name}, id={self.id},"
            " metadata={self.metadata}, docs={self.docs})"
        )

    def __str__(self) -> str:
        return f"File(name={self.name}, id={self.id}, metadata={self.metadata})"

    def copy(self) -> "File":
        """Create a deep copy of this File"""
        return self.__class__(
            name=self.name,
            id=self.id,
            metadata=deepcopy(self.metadata),
            docs=deepcopy(self.docs),
        )


def strip_consecutive_newlines(text: str) -> str:
    """Strips consecutive newlines from a string
    possibly with whitespace in between
    """
    return re.sub(r"\s*\n\s*", "\n", text)


class DocxFile(File):
    @classmethod
    def from_bytes(cls, file: BytesIO) -> "DocxFile":
        text = docx2txt.process(file)
        text = strip_consecutive_newlines(text)
        doc = Document(page_content=text.strip())
        return cls(name=file.name, id=md5(file.read()).hexdigest(), docs=[doc])


class PdfFile(File):
    @classmethod
    def from_bytes(cls, file: BytesIO) -> "PdfFile":
        pdf = PdfReader(file)
        docs = []
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            text = strip_consecutive_newlines(text)
            doc = Document(page_content=text.strip())
            doc.metadata["page"] = i + 1
            docs.append(doc)
        return cls(name=file.name, id=md5(file.read()).hexdigest(), docs=docs)


class TxtFile(File):
    @classmethod
    def from_bytes(cls, file: BytesIO) -> "TxtFile":
        text = file.read().decode("utf-8")
        text = strip_consecutive_newlines(text)
        file.seek(0)
        doc = Document(page_content=text.strip())
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
