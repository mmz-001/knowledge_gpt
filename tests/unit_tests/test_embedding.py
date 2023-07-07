from knowledge_gpt.core.embedding import FolderIndex, embed_files
from .fake_file import FakeFile
from langchain.docstore.document import Document
from knowledge_gpt.core.parsing import File
from knowledge_gpt.core.debug import FakeVectorStore
from typing import List


def test_combining_files():
    """Tests that combining files works."""

    files: List[File] = [
        FakeFile(
            name="file1",
            id="1",
            docs=[Document(page_content="1"), Document(page_content="2")],
        ),
        FakeFile(
            name="file2",
            id="2",
            docs=[Document(page_content="3"), Document(page_content="4")],
        ),
    ]

    all_docs = FolderIndex._combine_files(files)

    assert len(all_docs) == 4
    assert all_docs[0].page_content == "1"
    assert all_docs[1].page_content == "2"
    assert all_docs[2].page_content == "3"
    assert all_docs[3].page_content == "4"

    assert all_docs[0].metadata["file_name"] == "file1"
    assert all_docs[0].metadata["file_id"] == "1"
    assert all_docs[1].metadata["file_name"] == "file1"
    assert all_docs[1].metadata["file_id"] == "1"
    assert all_docs[2].metadata["file_name"] == "file2"
    assert all_docs[2].metadata["file_id"] == "2"
    assert all_docs[3].metadata["file_name"] == "file2"
    assert all_docs[3].metadata["file_id"] == "2"


def test_embed_fake_embedding_vector_store():
    """Tests that embedding files works for a fake embedding
    and a fake vector store.
    """

    files: List[File] = [
        FakeFile(
            name="file1",
            id="1",
            docs=[Document(page_content="1"), Document(page_content="2")],
        ),
        FakeFile(
            name="file2",
            id="2",
            docs=[Document(page_content="3"), Document(page_content="4")],
        ),
    ]

    folder_index = embed_files(
        files=files,
        embedding="debug",
        vector_store="debug",
    )

    assert isinstance(folder_index.index, FakeVectorStore)

    assert len(folder_index.files) == 2
    assert len(folder_index.index.texts) == 4
    assert folder_index.index.texts[0] == "1"
    assert folder_index.index.texts[1] == "2"
    assert folder_index.index.texts[2] == "3"
    assert folder_index.index.texts[3] == "4"
    assert folder_index.index.texts[0] == folder_index.files[0].docs[0].page_content
    assert folder_index.index.texts[1] == folder_index.files[0].docs[1].page_content
