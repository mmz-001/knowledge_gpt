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
from knowledge_gpt.core.qa import query_folder, query, request, API_KEY
from knowledge_gpt.core.utils import get_llm
from PIL import Image
import os

EMBEDDING = "openai"
VECTOR_STORE = "faiss"

# Uncomment to enable debug mode
# MODEL_LIST.insert(0, "debug")

st.set_page_config(page_title="CareerNavi - Navigating your career path", page_icon="📖", layout="wide")

image = Image.open(os.path.dirname(os.path.abspath(__file__)) + '/Team-Logo.png')
col1, mid, col2 = st.columns([1, 0.2, 20])
with col1:
    st.image(image, width=75)
with col2:
    st.header("CareerNavi", divider='rainbow', anchor=False)

st.subheader("Landing Your Dream Job :sunglasses: - An online generative AI platform could understand, track and navigate career planning.")

# Enable caching for expensive functions
bootstrap_caching()

openai_api_key = API_KEY

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
    #Next Job Title
    folder_index = embed_files(
        files=[chunked_file],
        embedding=EMBEDDING if model != "debug" else "debug",
        vector_store=VECTOR_STORE if model != "debug" else "debug",
        openai_api_key=openai_api_key,
    )

    llm = get_llm(model=model, openai_api_key=openai_api_key, temperature=0)

    job_title_query = "What is the job title of the resume content below ? Please return me the job title and nothing else"
    job_title_result = query_folder(
        folder_index=folder_index,
        query=job_title_query,
        llm=llm,
    )
    resume_job_title = job_title_result.answer

    next_level_query = "what is next level of {}. Please return me the next level and nothing else?".format(resume_job_title)
    next_level_result = request(
        query=next_level_query,
    )

    st.markdown(':blue[Next Job Position: ] ' + next_level_result)

    #Top 3 Skills
    learning_skills = "With current role of {}, list down top three of job skills which will be matching with {} level".format(resume_job_title, next_level_result)
    learning_skills_results = request(
        query=learning_skills,
    )
    st.markdown(':blue[Harden Your Skills: ] ')
    st.markdown(learning_skills_results, unsafe_allow_html=True)

    #Salary Ranges
    salary_query = "The salary ranges of {} in Vietnam".format(next_level_result)
    salary_result = request(
        query=salary_query,
    )
    st.markdown(':blue[and Earn Compensation: ] ' + salary_result)

    # Output Columns
    resume_info_tabs, career_path_tabs, suggestion_tabs, certifications_tab, recommend_jobs_tab = st.tabs(["Resume Information", "Career Pathways", "Job Competencies", "Well-Known Certifications", "Recommend Jobs"])

    #Resume Information
    resume_content = ""
    for doc in file.docs:
        resume_content += "\n" + doc.page_content

    resume_info_query = "What is the Job Title, Job Level, Year of Experiences, Skills, Working Experiences, Education of the resume content below ?"
    resume_info_query = resume_info_query + "\n" + resume_content
    resume_info_result = request(
        query=resume_info_query,
    )

    with resume_info_tabs:
        resume_info_tabs.subheader("Resume Information", anchor=False)
        resume_info_tabs.markdown(resume_info_result.replace("\n", "<br/>"), unsafe_allow_html=True)

    #Career Pathways
    career_path_query = "what is career pathway of {}?".format(resume_job_title)
    career_path_result = request(
        query=career_path_query,
    )

    with career_path_tabs:
        career_path_tabs.subheader("Career Pathways", anchor=False)
        career_path_tabs.write(career_path_result)

    #Skill Sets
    suggestion_query = "Tell me detailed job knowledge, competencies, experience and most interesting skills of {}".format(next_level_result)
    suggestion_result = request(
        query=suggestion_query,
    )

    with suggestion_tabs:
        suggestion_tabs.subheader("Job Competencies")
        suggestion_tabs.write(suggestion_result)

    #Career Roadmap
    road_map_query = "Write down a list of well-known certifications of {} with working reference hyperlink in HTML format".format(next_level_result)
    road_map_result = request(
        query=road_map_query,
    )

    with certifications_tab:
        certifications_tab.subheader("Well-Known Certifications")
        certifications_tab.write(road_map_result, unsafe_allow_html=True)

    #Career Roadmap
    recommend_jobs = "Write down a list of {} jobs of VietnamWorks in Vietnam with working reference hyperlink in HTML format".format(next_level_result)
    recommend_jobs_result = request(
        query=recommend_jobs,
    )

    with recommend_jobs_tab:
        recommend_jobs_tab.subheader("Recommend Jobs")
        recommend_jobs_tab.write(recommend_jobs_result, unsafe_allow_html=True)


    # with sources_col:
    #     st.markdown("#### Sources")
    #     for source in result.sources:
    #         st.markdown(source.page_content)
    #         st.markdown(source.metadata["source"])
    #         st.markdown("---")
