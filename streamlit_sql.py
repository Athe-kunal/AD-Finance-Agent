import streamlit as st
import os
from dotenv import load_dotenv
import openai
import re
from text_to_sql.sql_data_prep import get_qp

# def chat_text_to_sql(question):
    # response = qp.run(query=question)

    # return response
import re
load_dotenv(override=True)


openai.api_key = os.environ["OPENAI_API_KEY"]

@st.cache_resource
def get_query_pipeline():
    qp = get_qp()
    return qp 

qp = get_query_pipeline()
def generate_response(question):
    response = qp.run(query=question)

    return response

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
            response = generate_response(prompt) 
            st.write(response) 
    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)