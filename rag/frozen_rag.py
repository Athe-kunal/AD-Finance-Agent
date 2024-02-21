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
    prompt_template = """Use the following pieces of context to answer the question at the end.\n
        Be very diligent in using all the information and answering extensively. Also, don't miss out any numerical figures if there are any.\n

        {context}

        Question: {question}
        """

    prompt_template = PromptTemplate(
        input_variables=["context", "question"], template=prompt_template
    )

    llm_prompt = prompt_template.format(question=question, context=context)

    earnings_call_llm = ChatOpenAI(
        temperature=0.0, model=OPENAI_MODEL_NAME, streaming=False
    )

    output = earnings_call_llm.predict(llm_prompt)
    return output

