import streamlit as st
from dotenv import load_dotenv
import openai
import os
import re
from rag.frozen_rag import get_openai_answer, get_context

load_dotenv()

openai.api_key = os.environ["OPENAI_API_KEY"]

def generate_response(input_text):
    context,metadata = get_context(input_text)
    response = get_openai_answer(input_text,context)
    return response,metadata,context

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
            expander.text(context+metadata)
    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)