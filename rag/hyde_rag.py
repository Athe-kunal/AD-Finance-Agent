from rag.database import load_database
from rag.config import *
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
import openai
import os
load_dotenv()

openai.api_key = os.environ["OPENAI_API_KEY"]

retriever = load_database(DATABASE_NAME)

def get_context_hyde(question_or_hyde_answer:str):
    nodes = retriever.retrieve(question_or_hyde_answer)
    context = ""
    metadata = []
    for node in nodes:
        context += node.text + "\n"
        metadata.append(node.metadata)
    return context,metadata

def get_openai_HyDE_answer(question):

    hyde_prompt_template = PromptTemplate(
        input_variables=["question"], template=HYDE_PROMPT
    )

    llm_prompt = hyde_prompt_template.format(question=question)

    hyde_llm = ChatOpenAI(
        temperature=0.0, model=HYDE_OPENAI_MODEL_NAME, streaming=False
    )

    output = hyde_llm.predict(llm_prompt)
    return output

def get_openai_answer(question, context):

    prompt_template = PromptTemplate(
        input_variables=["context", "question"], template=FINAL_LLM_PROMPT
    )

    llm_prompt = prompt_template.format(question=question, context=context)

    openai_llm = ChatOpenAI(
        temperature=0.0, model=OPENAI_MODEL_NAME, streaming=False
    )

    output = openai_llm.predict(llm_prompt)
    return output

def main_hyde_answer(question):
    hyde_answer = get_openai_HyDE_answer(question)
    context,metadata = get_context_hyde(hyde_answer)
    final_response = get_openai_answer(question,context)
    return final_response, context, metadata