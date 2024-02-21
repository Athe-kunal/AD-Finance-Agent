from rag.database import query_database, load_database
from rag.config import *
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI


global index

index = load_database(DATABASE_NAME)

def get_context(question):
    nodes = query_database(question,index)
    context = ""
    metadata = []
    for node in nodes:
        context += node.text + "\n"
        metadata.append(node.metadata)
    return context,metadata

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

def main_frozen_rag_answer(question):
    context,metadata = get_context(question)
    final_response = get_openai_answer(question,context)
    return final_response, context, metadata