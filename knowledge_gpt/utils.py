import re
from io import BytesIO
from typing import Any, Dict, List

import docx2txt
from langchain import ConversationChain, LLMChain, PromptTemplate
import streamlit as st
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.docstore.document import Document
from langchain.llms import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import VectorStore
from langchain.vectorstores.faiss import FAISS
from openai.error import AuthenticationError
from pypdf import PdfReader
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory


# Does it work?
from langchain.callbacks.streamlit import StreamlitCallbackHandler

from knowledge_gpt.embeddings import OpenAIEmbeddings
from knowledge_gpt.prompts import STUFF_PROMPT
from langchain.schema import messages_from_dict, messages_to_dict


@st.cache_data()
def parse_docx(file: BytesIO) -> str:
    text = docx2txt.process(file)
    # Remove multiple newlines
    text = re.sub(r"\n\s*\n", "\n\n", text)
    return text


@st.cache_data()
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


@st.cache_data()
def parse_txt(file: BytesIO) -> str:
    text = file.read().decode("utf-8")
    # Remove multiple newlines
    text = re.sub(r"\n\s*\n", "\n\n", text)
    return text


@st.cache_data
def text_to_docs(text: str | List[str]) -> List[Document]:
    """Converts a string or list of strings to a list of Documents
    with metadata."""
    if isinstance(text, str):
        # Take a single string as one page
        text = [text]
    page_docs = [Document(page_content=page) for page in text]

    # Add page numbers as metadata
    for i, doc in enumerate(page_docs):
        doc.metadata["page"] = i + 1

    # Split pages into chunks
    doc_chunks = []

    for doc in page_docs:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
            chunk_overlap=0,
        )
        chunks = text_splitter.split_text(doc.page_content)
        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk, metadata={"page": doc.metadata["page"], "chunk": i}
            )
            # Add sources a metadata
            doc.metadata["source"] = f"{doc.metadata['page']}-{doc.metadata['chunk']}"
            doc_chunks.append(doc)
    return doc_chunks


# @st.cache_data(show_spinner=False)
def embed_docs(_docs: List[Document]) -> VectorStore:
    """Embeds a list of Documents and returns a FAISS index"""
    print("Embedding docs: %s" % _docs)

    if not st.session_state.get("OPENAI_API_KEY"):
        raise AuthenticationError(
            "Enter your OpenAI API key in the sidebar. You can get a key at"
            " https://platform.openai.com/account/api-keys."
        )
    else:
        # Embed the chunks
        embeddings = OpenAIEmbeddings(
            openai_api_key=st.session_state.get("OPENAI_API_KEY")
        )  # type: ignore
        index = FAISS.from_documents(_docs, embeddings)

        return index


@st.cache_data()
def search_docs(_index: VectorStore, query: str) -> List[Document]:
    print("Searching...index: %s" % _index)
    """Searches a FAISS index for similar chunks to the query
    and returns a list of Documents."""

    # Search for similar chunks
    docs = _index.similarity_search(query, k=3)
    return docs


@st.cache_data()
def get_answer_by_source(_docs: List[Document], query: str) -> Dict[str, Any]:
    """Gets an answer to a question from a list of Documents."""

    # Get the answer

    chain = load_qa_with_sources_chain(
        # llm=OpenAI(
        #     temperature=0, 
        #     openai_api_key=st.session_state.get("OPENAI_API_KEY"),
        # ),  # type: ignore
        llm=ChatOpenAI(
            temperature=0,
            streaming=True,
            verbose=True,
            openai_api_key=st.session_state.get("OPENAI_API_KEY"),
            # model_name="text-davinci-003",
            model_name="gpt-4",
        ), 
        chain_type="stuff",
        prompt=STUFF_PROMPT,
    )
    print('----------getting answer for docs: %s' % _docs)
    answer = chain(
        {"input_documents": _docs, "question": query}, return_only_outputs=True
    )
    print('----------answer: %s' % answer)
    return answer

# chatbot_template = """You are a chatbot that talks to humans.

#     {chat_history}
#     Human: {human_input}
#     Chatbot:"""
# chatbot_prompt = PromptTemplate(
#     input_variables=["chat_history", "human_input"],
#     template=chatbot_template
# )
# memory = ConversationBufferMemory(memory_key="chat_history")
# conversation_chain = LLMChain(
#     llm=ChatOpenAI(
#         temperature=0,
#         streaming=True,
#         verbose=True,
#         openai_api_key=st.session_state.get("OPENAI_API_KEY"),
#         # model_name="gpt-4",
#     ), 
#     prompt=chatbot_prompt,
#     verbose=True,
#     memory=memory,
# )
@st.cache_data
def get_answer_by_chat(query: str) -> Dict[str, Any]:
    return conversation_chain.predict(human_input=query)


def get_sources(_answer: Dict[str, Any], _docs: List[Document]) -> List[Document]:
    """Gets the source documents for an answer."""

    # Get sources for the answer
    source_keys = [s for s in _answer["output_text"].split("SOURCES: ")[-1].split(", ")]

    source_docs = []
    for doc in _docs:
        if doc.metadata["source"] in source_keys:
            source_docs.append(doc)

    return source_docs


def wrap_text_in_html(text: str | List[str]) -> str:
    """Wraps each text block separated by newlines in <p> tags"""
    if isinstance(text, list):
        # Add horizontal rules between pages
        text = "\n<hr/>\n".join(text)
    return "".join([f"<p>{line}</p>" for line in text.split("\n")])
