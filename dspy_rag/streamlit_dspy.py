import streamlit as st
import os
from dotenv import load_dotenv
import openai
import re
# from rag.frozen_rag import main_frozen_rag_answer
# from rag.hyde_rag import main_hyde_answer
# from rag.mod_hyde_rag import main_mod_hyde_answer
from rag_module import RAG
from database import load_database
import re
load_dotenv()

openai.api_key = os.environ["OPENAI_API_KEY"]

algo_type = st.selectbox("ALGO TYPE", ("mod-hyde","hyde","frozen"))
st.session_state['algo_type'] = algo_type

@st.cache_resource()
def get_retriever():
    retriever = load_database('hf',k=1)

retriever = get_retriever()

def generate_response(input_text):
    algo_type = st.session_state['algo_type']
    rag = RAG(retriever)

    response = rag.forward(input_text,algo_type)
    final_response = response.answer
    metadata = response.metadata
    context = response.context

    # if algo_type=="MOD_HYDE":
    #     final_response, context, metadata = main_mod_hyde_answer(input_text)
        
    # elif algo_type=="HYDE":
    #     #final_response, context, metadata = main_hyde_answer(input_text)
    # elif algo_type=="FROZEN":
    #     final_response, context, metadata = main_frozen_rag_answer(input_text)
    return final_response,metadata,context

if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "Hi, how can I help you?"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if prompt := st.chat_input():
    # Display user message in chat message container
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Answering..."):
            response,metadata,context = generate_response(prompt) 
            st.write(response) 
            expander = st.expander("See relevant Documents")
            expander_text = f"CONTEXT: {context}\n\n METADATA: {str(metadata)} "
            expander_text = re.sub(r'\$', r'\\$',expander_text)
            expander.write(expander_text)
    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)