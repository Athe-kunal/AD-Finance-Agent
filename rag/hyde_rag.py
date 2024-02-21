from rag.database import query_database, load_database
from rag.config import *
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI


global index

index = load_database(DATABASE_NAME)

def get_context_hyde(question_or_hyde_answer:str):
    nodes = query_database(question_or_hyde_answer,index)
    context = ""
    metadata = []
    for node in nodes:
        context += node.text + "\n"
        metadata.append(node.metadata)
    return context,metadata

def get_openai_HyDE_answer(question):
    hyde_prompt = """You are a expert at valuating companies. "Please write a passage to answer the question\n"
    "Try to include as many key details as possible.\n"
    "\n"
    "\n"
    "Question: {question}\n"
    "\n"
    "\n"
    'Passage:""" 

    hyde_prompt_template = PromptTemplate(
        input_variables=["question"], template=hyde_prompt
    )

    llm_prompt = hyde_prompt_template.format(question=question)

    hyde_llm = ChatOpenAI(
        temperature=0.0, model=HYDE_OPENAI_MODEL_NAME, streaming=False
    )

    output = hyde_llm.predict(llm_prompt)
    return output

def get_openai_answer(question, context):
    prompt = """Use the following pieces of context to answer the question at the end.\n
        Be very diligent in using all the information and answering in a detailed manner.\n

        {context}

        Question: {question}
        """

    prompt_template = PromptTemplate(
        input_variables=["context", "question"], template=prompt
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