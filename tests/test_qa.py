from langchain.docstore.document import Document
from knowledge_gpt.core.qa import get_sources
from knowledge_gpt.core.embedding import FolderIndex

from typing import List
from .fake_file import FakeFile
from knowledge_gpt.core.parsing import File

from .fake_vector_store import FakeVectorStore


def test_getting_sources_from_answer():
    """Test that we can get the sources from an answer."""
    files: List[File] = [
        FakeFile(
            name="file1",
            id="1",
            docs=[
                Document(page_content="1", metadata={"source": "1"}),
                Document(page_content="2", metadata={"source": "2"}),
            ],
        ),
        FakeFile(
            name="file2",
            id="2",
            docs=[
                Document(page_content="3", metadata={"source": "3"}),
                Document(page_content="4", metadata={"source": "4"}),
            ],
        ),
    ]
    folder_index = FolderIndex(files=files, index=FakeVectorStore())

    answer = "This is the answer. SOURCES: 1, 2, 3, 4"

    sources = get_sources(answer, folder_index)

    assert len(sources) == 4
    assert sources[0].metadata["source"] == "1"
    assert sources[1].metadata["source"] == "2"
    assert sources[2].metadata["source"] == "3"
    assert sources[3].metadata["source"] == "4"
