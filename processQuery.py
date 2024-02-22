from rag.frozen_rag import main_frozen_rag_answer
from rag.hyde_rag import main_hyde_answer
from rag.mod_hyde_rag import main_mod_hyde_answer

def generate_response(input_text,model):
    algo_type = model

    if algo_type=="MOD_HYDE":
        final_response, context, metadata = main_mod_hyde_answer(input_text)
    elif algo_type=="HYDE":
        final_response, context, metadata = main_hyde_answer(input_text)
    elif algo_type=="FROZEN":
        final_response, context, metadata = main_frozen_rag_answer(input_text)
    return final_response,context,metadata
