import pytest
from io import BytesIO

from knowledge_gpt.core.parsing import (
    DocxFile,
    PdfFile,
    TxtFile,
    read_file,
    strip_consecutive_newlines,
)
from pathlib import Path

TESTS_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = TESTS_ROOT.parent.resolve()
RESOURCE_ROOT = PROJECT_ROOT / "resources"
SAMPLE_ROOT = RESOURCE_ROOT / "samples"


def test_docx_file():
    with open(SAMPLE_ROOT / "test_hello.docx", "rb") as f:
        file = BytesIO(f.read())
        file.name = "test.docx"
        docx_file = DocxFile.from_bytes(file)

    assert docx_file.name == "test.docx"
    assert len(docx_file.docs) == 1
    assert docx_file.docs[0].page_content == "Hello World"


def test_docx_file_with_multiple_pages():
    with open(SAMPLE_ROOT / "test_hello_multi.docx", "rb") as f:
        file = BytesIO(f.read())
        file.name = "test.docx"
        docx_file = DocxFile.from_bytes(file)

    assert docx_file.name == "test.docx"
    assert len(docx_file.docs) == 1
    assert (
        docx_file.docs[0].page_content == "Hello World 1\nHello World 2\nHello World 3"
    )


def test_pdf_file_with_single_page():
    with open(SAMPLE_ROOT / "test_hello.pdf", "rb") as f:
        file = BytesIO(f.read())
        file.name = "test_hello.pdf"
        pdf_file = PdfFile.from_bytes(file)

    assert pdf_file.name == "test_hello.pdf"
    assert len(pdf_file.docs) == 1
    assert pdf_file.docs[0].page_content == "Hello World"


def test_pdf_file_with_multiple_pages():
    with open(SAMPLE_ROOT / "test_hello_multi.pdf", "rb") as f:
        file = BytesIO(f.read())
        file.name = "test_hello_multiple.pdf"
        pdf_file = PdfFile.from_bytes(file)

    assert pdf_file.name == "test_hello_multiple.pdf"
    assert len(pdf_file.docs) == 3
    assert pdf_file.docs[0].page_content == "Hello World 1"
    assert pdf_file.docs[1].page_content == "Hello World 2"
    assert pdf_file.docs[2].page_content == "Hello World 3"

    assert pdf_file.docs[0].metadata["page"] == 1
    assert pdf_file.docs[1].metadata["page"] == 2
    assert pdf_file.docs[2].metadata["page"] == 3


def test_txt_file():
    with open(SAMPLE_ROOT / "test_hello.txt", "rb") as f:
        file = BytesIO(f.read())
        file.name = "test.txt"
        txt_file = TxtFile.from_bytes(file)

    assert txt_file.name == "test.txt"
    assert len(txt_file.docs) == 1
    assert txt_file.docs[0].page_content == "Hello World"


def test_read_file():
    # Test the `read_file` function with each file type
    for ext, FileClass in [(".docx", DocxFile), (".pdf", PdfFile), (".txt", TxtFile)]:
        with open(SAMPLE_ROOT / f"test_hello{ext}", "rb") as f:
            file = BytesIO(f.read())
            file.name = f"test_hello{ext}"
            file_obj = read_file(file)

        assert isinstance(file_obj, FileClass)
        assert file_obj.name == f"test_hello{ext}"
        assert len(file_obj.docs) == 1
        assert file_obj.docs[0].page_content == "Hello World"


def test_read_file_not_implemented():
    file = BytesIO(b"Hello World")
    file.name = "test.unknown"
    with pytest.raises(NotImplementedError):
        read_file(file)


def test_strip_consecutive_newlines():
    # Test with multiple consecutive newlines
    text = "\n\n\n"
    expected = "\n"
    assert strip_consecutive_newlines(text) == expected

    # Test with newlines and spaces
    text = "\n \n \n"
    expected = "\n"
    assert strip_consecutive_newlines(text) == expected

    # Test with newlines and tabs
    text = "\n\t\n\t\n"
    expected = "\n"
    assert strip_consecutive_newlines(text) == expected

    # Test with mixed whitespace characters
    text = "\n \t\n \t \n"
    expected = "\n"
    assert strip_consecutive_newlines(text) == expected

    # Test with no consecutive newlines
    text = "\nHello\nWorld\n"
    expected = "\nHello\nWorld\n"
    assert strip_consecutive_newlines(text) == expected
