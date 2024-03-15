from rag.database import load_database
from rag.config import *
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from transformers import pipeline
from dotenv import load_dotenv
import openai
import os
load_dotenv(dotenv_path="../.env",override=True)

openai.api_key = os.environ["OPENAI_API_KEY"]

pipe = pipeline("text-generation", model=MOD_HYDE_MODEL)

retriever = load_database()

def get_context_hyde(question_or_hyde_answer:str):
    nodes = retriever.retrieve(question_or_hyde_answer)
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
    print(hyde_answer)
    context,metadata = get_context_hyde(hyde_answer)
    print(context,metadata)
    final_response = get_openai_answer(question,context)
    print(final_response)
    return final_response, context, metadata