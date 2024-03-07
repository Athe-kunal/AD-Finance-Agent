from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext
from llama_index.embeddings.openai import OpenAIEmbedding
import chromadb
import os
from dotenv import load_dotenv
import os
load_dotenv(override=True)
import openai

openai.api_key = os.environ['OPENAI_API_KEY']
print(os.getcwd())

db2 = chromadb.PersistentClient(path="ad_project_db")
print(db2.heartbeat())
EMBEDDING_MODEL = "text-embedding-3-small"
embed_model = OpenAIEmbedding(model=EMBEDDING_MODEL)
COLLECTION_NAME = "ad-project"
chroma_collection = db2.get_collection(COLLECTION_NAME)
print(chroma_collection.count())
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
print("Here1")
index_ = VectorStoreIndex.from_vector_store(
    vector_store,
    embed_model=embed_model,
)
print("Here2")

retriever = index_.as_retriever(similarity_top_k=5)
print("Here3")
# print(chroma_collection.peek())
nodes = retriever.retrieve("What is Valuations?")
print("Here4")

for node in nodes:
    print(node.text)

# query_engine = index_.as_query_engine()
# response = query_engine.query("What did the author do growing up?")
# print(response)
{
    "response":"",
    "metadata": [{"page"},{},{}],
    "context": ""
}