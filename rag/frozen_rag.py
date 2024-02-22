from rag.config import *
from rag.database import load_database
import chromadb
from llama_index.core import Document
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext
from llama_index.embeddings.openai import OpenAIEmbedding
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
import openai
import os
load_dotenv()

openai.api_key = os.environ["OPENAI_API_KEY"]

# def load_database(path:str):
    # path = "../ + path
# db2 = chromadb.PersistentClient(path=DATABASE_NAME)
# print(db2.heartbeat())
# embed_model = OpenAIEmbedding(model=EMBEDDING_MODEL,api_key=os.environ['OPENAI_API_KEY'])
# chroma_collection = db2.get_or_create_collection(COLLECTION_NAME)
# print(chroma_collection.count())
# vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
# index_ = VectorStoreIndex.from_vector_store(
#     vector_store,
#     embed_model=embed_model,
# )
# retriever = index_.as_retriever(similarity_top_k=TOP_K)

retriever = load_database()

def get_context(question):
    nodes = retriever.retrieve(question)
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
    print(context,metadata)
    final_response = get_openai_answer(question,context)
    return final_response, context, metadata
    

if __name__=="__main__":
    main_frozen_rag_answer("What are the first steps in valuation?")