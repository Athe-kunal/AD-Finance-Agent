from dspy_rag.config import *

def generate_response_dspy(input_text:str,algo_type:str,rag):
    algo_type = algo_type.lower()
    assert algo_type in ["mod_hyde","frozen","hyde"], 'The algo type should be in ["mod_hyde","frozen","hyde"]'
    # if algo_type=="MOD_HYDE":
    dspy_answer = rag(input_text,algo_type)
    final_response,context,metadata = dspy_answer.answer,dspy_answer.context,dspy_answer.metadata
    # elif algo_type=="HYDE":
    # elif algo_type=="FROZEN":
    return final_response,context,metadata

# from dspy_rag.database import load_database

# ret = load_database("gemini",5,"AIzaSyDpSb9WnVhU5qs5lIpE7NNiJWkCt2WE6Jk")