#from dspy_rag.config import *
from dspy_rag.config import *
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.legacy.embeddings.openai import OpenAIEmbedding
from llama_index.legacy.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.embeddings.gemini import GeminiEmbedding
import chromadb
import torch
import os
import streamlit as st
import dspy
def load_database(embedding_source:str,k,api_key:str=""):
    if "mxbai" in EMBEDDING_MODEL:
        database_name_path = BASE_DATABASE_NAME + "-MXBAI"
        collection_name = COLLECTION_NAME 
    elif "large" in EMBEDDING_MODEL and embedding_source=="openai":
        database_name_path = BASE_DATABASE_NAME + "LARGE"
        collection_name = COLLECTION_NAME + "-large"
    elif "small" in EMBEDDING_MODEL:
        database_name_path = BASE_DATABASE_NAME + "SMALL"
        collection_name = COLLECTION_NAME + "-small"
    elif "nomic" in EMBEDDING_MODEL:
        database_name_path = BASE_DATABASE_NAME + "-NOMIC-v1"
        collection_name = COLLECTION_NAME 
    elif "models" in EMBEDDING_MODEL:
        database_name_path = BASE_DATABASE_NAME + "-GEMINI"
        collection_name = COLLECTION_NAME 
    # print(collection_name)
    db2 = chromadb.PersistentClient(path=database_name_path)
    if embedding_source == "openai":
        embed_model = OpenAIEmbedding(model=EMBEDDING_MODEL,api_key=os.environ['OPENAI_API_KEY'])
    elif embedding_source == 'hf':
        if torch.cuda.is_available():
            embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL,trust_remote_code=True,device='cuda:0')
        else:
            embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL,trust_remote_code=True)
    elif embedding_source == "gemini":
        embed_model = GeminiEmbedding(model_name=EMBEDDING_MODEL,api_key=api_key)
    print(db2)
    chroma_collection = db2.get_collection(collection_name)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    index_ = VectorStoreIndex.from_vector_store(
        vector_store,
        embed_model=embed_model,
    )
    retriever = index_.as_retriever(similarity_top_k=k*5)
    return retriever