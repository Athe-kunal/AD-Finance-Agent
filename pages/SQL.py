import streamlit as st
import re

qp_dict = st.session_state['qp_dict']
region = st.selectbox("Region", ("US","China","Emerging","Japan","Europe","Global","India"))
st.session_state['region'] = region 

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
            response = qp_dict[region].run(prompt).message.content
            response = re.sub(r'\$', r'\\$',response)
            st.write(response) 
    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)