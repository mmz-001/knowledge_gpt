from typing import List
import streamlit as st
from langchain.docstore.document import Document
from knowledge_gpt.core.parsing import File
import openai
from streamlit.logger import get_logger
from typing import NoReturn

logger = get_logger(__name__)


def wrap_doc_in_html(docs: List[Document]) -> str:
    """Wraps each page in document separated by newlines in <p> tags"""
    text = [doc.page_content for doc in docs]
    if isinstance(text, list):
        # Add horizontal rules between pages
        text = "\n<hr/>\n".join(text)
    return "".join([f"<p>{line}</p>" for line in text.split("\n")])


def is_query_valid(query: str) -> bool:
    if not query:
        st.error("Stel hier je vraag!")
        return False
    return True


def is_file_valid(file: File) -> bool:
    if (
        len(file.docs) == 0
        or "".join([doc.page_content for doc in file.docs]).strip() == ""
    ):
        st.error("Het document kan niet worden gelezen! Zorg ervoor dat het document tekst bevat.")
        logger.error("Het document kan niet worden gelezen.")
        return False
    return True


def display_file_read_error(e: Exception, file_name: str) -> NoReturn:
    st.error("Error lezen bestand. Is het bestand misschien corrupted of encrypted")
    logger.error(f"{e.__class__.__name__}: {e}. Extension: {file_name.split('.')[-1]}")
    st.stop()


@st.cache_data(show_spinner=False)
def is_open_ai_key_valid(openai_api_key, model: str) -> bool:
    if model == "debug":
        return True

    if not openai_api_key:
        st.error("Please enter your OpenAI API key in the sidebar!")
        return False
    try:
        system_prompt = """
        Je bent een vriendelijke en behulpzame instructiecoach die docenten op een MBO school helpt bij het plannen van een les.
        De docenten geven les aan niveau 1 studenten. Op basis van het bestand dat de docent je heeft gegeven, 
        en op basis van wat de docent precies van je vraagt, maak jij het lesplan.  
        Jij moet in ieder geval van de docent weten:  1. THEMA: In grote lijnen waar de les over gaat, 2. SPECIFIEK: Welk speciek onderdeel van dit thema, en 
        3. VOORKENNIS: Welke voorkennis de studenten hebb.

        Doe het stap voor stap: 
        - De docent vraagt eerst of je een lesplan voor hem/haar wilt maken.
        - Jij vraagt dan om THEMA, SPECIFIEK, en VOORKENNIS
        - Vervolgens ga je het lesplan maken
        Gebruik een helder leerdoel want dat is wat de studenten na de les moeten begrijpen en/of kunnen doen. 
        Maak het lesplan in markdown formaat met een verscheidenheid aan lestechnieken en -modaliteiten, 
        waaronder directe instructie, controleren op begrip
        (inclusief het verzamelen van bewijs van begrip van een brede steekproef van studenten), discussie, 
        een boeiende activiteit in de klas en een opdracht.  
        Leg uit waarom je specifiek voor elk kiest. Probeer het niet groter te maken dan 2  A4-tjes """

        openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": "test"}],  
            api_key=openai_api_key,
        )
    except Exception as e:
        st.error(f"{e.__class__.__name__}: {e}")
        logger.error(f"{e.__class__.__name__}: {e}")
        return False

    return True
