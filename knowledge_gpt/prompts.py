# flake8: noqa
from langchain.prompts import PromptTemplate
#CONTENT:<span style="color: red"> ARPA-H will have a singular purpose—to drive breakthroughs in cancer, Alzheimer’s, diabetes, and more. ARPA-H is a medical breakthrough.</span>
#IMPORTANT: If you found important information to answer the question in the text insert tags "<span style="color: red"> Important Information </span>" around the text to mark it red.
## Use a shorter template to reduce the number of tokens in the prompt
template = """
Create a final answer to the given questions using the provided document excerpts(in no particular order) as references. 
ALWAYS include a "SOURCES" section in your answer including only the sources of the highest probability to answer the question.

If you are unable to answer the question, simply state NULL.
IMPORTANT: Final answer in the language of the user question. If the question is in german answer in german.
IMPORTANT: End you answer with a probability between low, medium and high to reflect how confident you are that your answer is correct. If there are nosources the probability is automatically low.
IMPORTANT: Do not attempt to fabricate an answer and leave the SOURCES section empty.
IMPORTANT: Answer as detailled as possible.



QUESTION: What  is the purpose of ARPA-H?
=========
Content: More support for patients and families. \n\nTo get there, I call on Congress to fund ARPA-H, the Advanced Research Projects Agency for Health. \n\nIt’s based on DARPA—the Defense Department project that led to the Internet, GPS, and so much more.  \n\nARPA-H will have a singular purpose—to drive breakthroughs in cancer, Alzheimer’s, diabetes, and more.
Source: 1-32
Content: While we’re at it, let’s make sure every American can get the health care they need. \n\nWe’ve already made historic investments in health care. \n\nWe’ve made it easier for Americans to get the care they need, when they need it. \n\nWe’ve made it easier for Americans to get the treatments they need, when they need them. \n\nWe’ve made it easier for Americans to get the medications they need, when they need them.
Source: 1-33
Content: The V.A. is pioneering new ways of linking toxic exposures to disease, already helping  veterans get the care they deserve. \n\nWe need to extend that same care to all Americans. \n\nThat’s why I’m calling on Congress to pass legislation that would establish a national registry of toxic exposures, and provide health care and financial assistance to those affected.
Source: 1-30
Content: ARPA-H is a medical breakthrough.
Source: 1-34
=========
FINAL ANSWER: The purpose of ARPA-H is to drive breakthroughs in cancer, Alzheimer’s, diabetes, and more. <Probability: high>
SOURCES: 1-32, 1-34


QUESTION: {question}
=========
{summaries}
=========
FINAL ANSWER:"""

STUFF_PROMPT = PromptTemplate(
    template=template, input_variables=["summaries", "question"]
)
