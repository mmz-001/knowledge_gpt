import pytest
from langchain.docstore.document import Document

from knowledge_gpt.core.chunking import chunk_file
from tests.fake_file import FakeFile


@pytest.fixture
def single_page_file():
    doc = Document(page_content="This is a page.\nIt has stuff.")
    file = FakeFile(name="test.txt", id="1", docs=[doc])
    return file


@pytest.fixture
def multi_page_file():
    docs = [
        Document(page_content="This is the first page", metadata={"page": 1}),
        Document(page_content="This is the second page.", metadata={"page": 2}),
    ]
    file = FakeFile(name="test.pdf", id="2", docs=docs)
    return file


def test_chunk_file_single_page_no_overlap(single_page_file):
    chunked_file = chunk_file(single_page_file, chunk_size=6, chunk_overlap=0)
    assert len(chunked_file.docs) == 2  # The document should be split into 2 chunks

    assert chunked_file.docs[1].page_content == "It has stuff."
    assert chunked_file.docs[0].page_content == "This is a page."

    assert chunked_file.docs[0].metadata["chunk"] == 1
    assert chunked_file.docs[1].metadata["chunk"] == 2

    assert chunked_file.docs[0].metadata["source"] == "1-1"
    assert chunked_file.docs[1].metadata["source"] == "1-2"


def test_chunk_file_multi_page_no_overlap(multi_page_file):
    chunked_file = chunk_file(multi_page_file, chunk_size=10, chunk_overlap=0)
    assert (
        len(chunked_file.docs) == 2
    )  # Each of the two documents should be split into 2 chunks

    assert chunked_file.docs[0].page_content == "This is the first page"
    assert chunked_file.docs[1].page_content == "This is the second page."

    assert chunked_file.docs[0].metadata["page"] == 1
    assert chunked_file.docs[1].metadata["page"] == 2

    assert chunked_file.docs[0].metadata["chunk"] == 1
    assert chunked_file.docs[1].metadata["chunk"] == 1

    assert chunked_file.docs[0].metadata["source"] == "1-1"
    assert chunked_file.docs[1].metadata["source"] == "2-1"
