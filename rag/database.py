import sys
sys.path.append('../')
import json
# from src.book_preprocess import get_book_data
from llama_index.core import Document
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext
from llama_index.embeddings.openai import OpenAIEmbedding
import chromadb
from rag.config import *
from dotenv import load_dotenv
import openai
import os
load_dotenv()

openai.api_key = os.environ["OPENAI_API_KEY"]

# def get_book_transcripts_data():
#     book_doc_data = get_book_data(100)
#     with open(r'..\artifacts\YouTube_API_Transcripts\chunked_transcripts_mba.json', 'r') as file:
#         mba_data = json.load(file)

#     with open(r'..\artifacts\YouTube_API_Transcripts\chunked_transcripts_undergrad.json', 'r') as file:
#         undergrad_data = json.load(file)

#     with open(r'..\artifacts\YouTube_API_Transcripts\chunked_misc_transcripts.json', 'r') as file:
#         misc_data = json.load(file)
    
#     all_data_list = []
#     for book_doc in book_doc_data:
#         # try:
#         if book_doc=={}: continue
#         all_data_list.append(
#             Document(
#                 text=book_doc['text'],
#                 metadata={
#                     'page_num_coordinates':str(book_doc['page_num_coordinates']),
#                     'book_source':book_doc['book_source'],
#                 },
#                 excluded_embed_metadata_keys=['page_num_coordinates','book_source'],
#                 excluded_llm_metadata_keys=['page_num_coordinates','book_source'],
#             )
#         )

#     for json_data in [undergrad_data,mba_data,misc_data]:
#         for youtube_id, text_list in json_data.items():
#             all_data_list.append(
#                 Document(
#                     text=text_list[0]['text'],
#                     metadata={
#                         "youtube_id":youtube_id,
#                         "start_timestamp":text_list[0]['start_time'],
#                     },
#                     excluded_embed_metadata_keys=['youtube_id','start_timestamp'],
#                     excluded_llm_metadata_keys=['youtube_id','start_timestamp'],
#                 )
#             )
#             # break
#     return all_data_list

def create_database():
    all_data_list = get_book_transcripts_data()
    if "small" in EMBEDDING_MODEL:
        database_name = DATABASE_NAME + "_SMALL"
    elif "large" in EMBEDDING_MODEL:
        database_name = DATABASE_NAME + "_LARGE"
    ad_project_db = chromadb.PersistentClient(path=database_name)
    ad_project_chroma_collection = ad_project_db.get_or_create_collection(COLLECTION_NAME)
    embed_model = OpenAIEmbedding(model=EMBEDDING_MODEL)
    vector_store = ChromaVectorStore(chroma_collection=ad_project_chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_documents(
        all_data_list, storage_context=storage_context, embed_model=embed_model,
        show_progress=True
    )

    return index

def load_database():
    if "large" in EMBEDDING_MODEL:
        database_name_path = BASE_DATABASE_NAME + "LARGE"
        collection_name = COLLECTION_NAME + "-large"
    elif "small" in EMBEDDING_MODEL:
        database_name_path = BASE_DATABASE_NAME + "SMALL"
        collection_name = COLLECTION_NAME + "-small"
    db2 = chromadb.PersistentClient(path=database_name_path)
    embed_model = OpenAIEmbedding(model=EMBEDDING_MODEL,api_key=os.environ['OPENAI_API_KEY'])
    chroma_collection = db2.get_collection(collection_name)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    index_ = VectorStoreIndex.from_vector_store(
        vector_store,
        embed_model=embed_model,
    )
    retriever = index_.as_retriever(similarity_top_k=TOP_K)
    return retriever



