import streamlit as st

from knowledge_gpt.components.sidebar import sidebar

from knowledge_gpt.ui import wrap_doc_in_html, is_valid

from knowledge_gpt.core.parsing import to_file
from knowledge_gpt.core.chunking import chunk_file
from knowledge_gpt.core.embedding import embed_docs
from knowledge_gpt.core.qa import get_answer, get_sources


st.set_page_config(page_title="KnowledgeGPT", page_icon="📖", layout="wide")
st.header("📖KnowledgeGPT")

sidebar()

openai_api_key = st.session_state.get("OPENAI_API_KEY")


if not openai_api_key:
    st.warning(
        "Enter your OpenAI API key in the sidebar. You can get a key at"
        " https://platform.openai.com/account/api-keys."
    )


uploaded_file = st.file_uploader(
    "Upload a pdf, docx, or txt file",
    type=["pdf", "docx", "txt"],
    help="Scanned documents are not supported yet!",
)

if not uploaded_file:
    st.stop()


file = to_file(uploaded_file)
file = chunk_file(file, chunk_size=800, chunk_overlap=0)


with st.spinner("Indexing document... This may take a while⏳"):
    index = embed_docs(
        file=file,
        embeddings="openai",
        vector_store="faiss",
        openai_api_key=openai_api_key,
    )

with st.form(key="qa_form"):
    query = st.text_area("Ask a question about the document")
    submit = st.form_submit_button("Submit")


with st.expander("Advanced Options"):
    show_all_chunks = st.checkbox("Show all chunks retrieved from vector search")
    show_full_doc = st.checkbox("Show parsed contents of the document")


if show_full_doc:
    with st.expander("Document"):
        # Hack to get around st.markdown rendering LaTeX
        st.markdown(f"<p>{wrap_doc_in_html(file.docs)}</p>", unsafe_allow_html=True)


if submit:
    if not is_valid(index, query):
        st.stop()

    # Output Columns
    answer_col, sources_col = st.columns(2)

    answer, relevant_docs = get_answer(
        query,
        model="openai",
        index=index,
        openai_api_key=openai_api_key,
        temperature=0,
    )
    if not show_all_chunks:
        # Get the sources for the answer
        sources = get_sources(answer, file)
    else:
        sources = relevant_docs

    with answer_col:
        st.markdown("#### Answer")
        st.markdown(answer["output_text"].split("SOURCES: ")[0])

    with sources_col:
        st.markdown("#### Sources")
        for source in sources:
            st.markdown(source.page_content)
            st.markdown(source.metadata["source"])
            st.markdown("---")
