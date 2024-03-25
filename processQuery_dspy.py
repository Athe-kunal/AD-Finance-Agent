from dspy_rag.rag_module import RAG
from dspy_rag.database import load_database
from dspy_rag.config import *

retriever = load_database("gemini",TOP_K)
rag = RAG(retriever)

def generate_response(input_text:str,model:str):
    algo_type = model
    algo_type = algo_type.lower()
    assert algo_type in ["mod_hyde","frozen","hyde"], 'The algo type should be in ["mod_hyde","frozen","hyde"]'
    # if algo_type=="MOD_HYDE":
    dspy_answer = rag(input_text,algo_type)
    final_response,context,metadata = dspy_answer.answer,dspy_answer.context,dspy_answer.metadata
    # elif algo_type=="HYDE":
    # elif algo_type=="FROZEN":
    return final_response,context,metadata