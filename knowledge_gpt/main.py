import streamlit as st
from trubrics.integrations.streamlit import FeedbackCollector


from knowledge_gpt.components.sidebar import sidebar

from knowledge_gpt.ui import (
    wrap_doc_in_html,
    is_query_valid,
    is_file_valid,
    is_open_ai_key_valid,
    display_file_read_error,
)

from knowledge_gpt.core.caching import bootstrap_caching

from knowledge_gpt.core.parsing import read_file
from knowledge_gpt.core.chunking import chunk_file
from knowledge_gpt.core.embedding import embed_files
from knowledge_gpt.core.qa import query_folder

EMBEDDING = "openai"
VECTOR_STORE = "faiss"
MODEL = "openai"

# For testing
# EMBEDDING, VECTOR_STORE, MODEL = ["debug"] * 3

st.set_page_config(page_title="KnowledgeGPT", page_icon="📖", layout="wide")
st.header("📖KnowledgeGPT")

# Initialising submit as False
if "submit" not in st.session_state:
    st.session_state["submit"] = False

# Enable caching for expensive functions
bootstrap_caching()

sidebar()

openai_api_key = st.secrets.get("OPENAI_API_KEY")
email = st.secrets.get("TRUBRICS_EMAIL")
password = st.secrets.get("TRUBRICS_PASSWORD")


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

try:
    file = read_file(uploaded_file)
except Exception as e:
    display_file_read_error(e)

chunked_file = chunk_file(file, chunk_size=300, chunk_overlap=0)

if not is_file_valid(file):
    st.stop()

if not is_open_ai_key_valid(openai_api_key):
    st.stop()


with st.spinner("Indexing document... This may take a while⏳"):
    folder_index = embed_files(
        files=[chunked_file],
        embedding=EMBEDDING,
        vector_store=VECTOR_STORE,
        openai_api_key=openai_api_key,
    )

with st.form(key="qa_form"):
    query = st.text_area("Ask a question about the document")
    submit = st.form_submit_button("Submit")

    # Setting submit to True if the button is pressed
    if submit:
        st.session_state['submit'] = True


with st.expander("Advanced Options"):
    return_all_chunks = st.checkbox("Show all chunks retrieved from vector search")
    show_full_doc = st.checkbox("Show parsed contents of the document")


if show_full_doc:
    with st.expander("Document"):
        # Hack to get around st.markdown rendering LaTeX
        st.markdown(f"<p>{wrap_doc_in_html(file.docs)}</p>", unsafe_allow_html=True)

# this code runs after the form
if st.session_state['submit']:

    if not is_query_valid(query):
        st.stop()

    # Output Columns
    answer_col, sources_col = st.columns(2)

    result = query_folder(
            folder_index=folder_index,
            query=query,
            return_all=return_all_chunks,
            model=MODEL,
            openai_api_key=openai_api_key,
            temperature=0,
        )

    with answer_col:
        st.markdown("#### Answer")
        st.markdown(result.answer)

        # Object to collect feedback
        collector = FeedbackCollector(
            component_name="default",
            email=email, 
            password=password, 
        )
        
        # Collecting the feedback for result
        feedback_result = collector.st_feedback(
                feedback_type="thumbs",
                model=MODEL,
                open_feedback_label="[Optional] Provide additional feedback",
                key = 'key_result',
                metadata={"response": result.answer, "prompt": query}
            )
    

    with sources_col:
        st.markdown("#### Sources")
        for source in result.sources:
            st.markdown(source.page_content)
            st.markdown(source.metadata["source"])
            st.markdown("---")

                # Collecting the feedback for result
        feedback_source = collector.st_feedback(
                feedback_type="thumbs",
                model=MODEL,
                open_feedback_label="[Optional] Provide additional feedback",
                key = 'key_source',
                metadata={"response": source.metadata["source"], "prompt": query}
            )
    