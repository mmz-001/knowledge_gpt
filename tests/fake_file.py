from knowledge_gpt.core.parsing import File
from io import BytesIO


class FakeFile(File):
    """A fake file for testing purposes"""

    @classmethod
    def from_bytes(cls, file: BytesIO) -> "FakeFile":
        return NotImplemented
