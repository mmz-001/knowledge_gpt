import streamlit as st

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
from knowledge_gpt.core.qa import query_folder, query, request
from knowledge_gpt.core.utils import get_llm


EMBEDDING = "openai"
VECTOR_STORE = "faiss"

# Uncomment to enable debug mode
# MODEL_LIST.insert(0, "debug")

st.set_page_config(page_title="KnowledgeGPT", page_icon="📖", layout="wide")
st.header("📖CareerNavi")

# Enable caching for expensive functions
bootstrap_caching()

openai_api_key = st.session_state.get("OPENAI_API_KEY")


uploaded_file = st.file_uploader(
    "Upload a pdf, docx, or txt file",
    type=["pdf", "docx", "txt"],
    help="Scanned documents are not supported yet!",
)

model: str = "gpt-3.5-turbo"  # type: ignore

if not uploaded_file:
    st.stop()

try:
    file = read_file(uploaded_file)
except Exception as e:
    display_file_read_error(e, file_name=uploaded_file.name)

chunked_file = chunk_file(file, chunk_size=300, chunk_overlap=0)

if not is_file_valid(file):
    st.stop()


with st.spinner("Indexing document... This may take a while⏳"):
    folder_index = embed_files(
        files=[chunked_file],
        embedding=EMBEDDING if model != "debug" else "debug",
        vector_store=VECTOR_STORE if model != "debug" else "debug",
        openai_api_key=openai_api_key,
    )

    # Output Columns
    resume_info_col, career_path_col, suggestion_col, salary_col = st.columns(4)

    llm = get_llm(model=model, openai_api_key=openai_api_key, temperature=0)

    resume_info_query = "What is the Job Title, Year of Experiences, Skills, Working Experiences, Education of the resume content below ?"
    resume_info_result = query_folder(
        folder_index=folder_index,
        query=resume_info_query,
        llm=llm,
    )

    job_title_query = "What is the job title of the resume content below ?"
    job_title_result = query_folder(
        folder_index=folder_index,
        query=job_title_query,
        llm=llm,
    )

    career_path_query = "what is career pathway of {}?".format(job_title_result.answer)
    career_path_result = request(
        query=career_path_query,
    )

    suggestion_query = "Tell me skill sets of {}".format(job_title_result.answer)
    suggestion_result = request(
        query=suggestion_query,
    )

    salary_query = "What is the Salary range of {} in VietNam?".format(job_title_result.answer)
    salary_result = request(
        query=salary_query,
    )

    with resume_info_col:
        st.markdown("#### Resume Info")
        st.markdown(resume_info_result.answer)


    with career_path_col:
        st.markdown("#### Career Path")
        st.markdown(career_path_result)

    with suggestion_col:
        st.markdown("#### Suggestion")
        st.markdown(suggestion_result)

    with salary_col:
        st.markdown("#### Salary")
        st.markdown(salary_result)
    # with sources_col:
    #     st.markdown("#### Sources")
    #     for source in result.sources:
    #         st.markdown(source.page_content)
    #         st.markdown(source.metadata["source"])
    #         st.markdown("---")
