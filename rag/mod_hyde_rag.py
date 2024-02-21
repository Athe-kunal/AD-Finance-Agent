from rag.database import query_database, load_database
from rag.config import *
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from transformers import pipeline

global pipe
pipe = pipeline("text-generation", model=MOD_HYDE_MODEL)

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


def get_mod_HyDE_answer(question):
    out = pipe(question,max_new_tokens=100,do_sample=True,min_new_tokens=10)
    return out[0]['generated_text']

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

def main_mod_hyde_answer(question):
    hyde_answer = get_mod_HyDE_answer(question)
    context,metadata = get_context_hyde(hyde_answer)
    final_response = get_openai_answer(question,context)
    return final_response, context, metadata