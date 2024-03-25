from text_to_sql.sql_data_prep import get_qp
import concurrent.futures
from dspy_rag.rag_module import RAG
import streamlit as st
from dspy_rag.database import load_database

google_key = st.text_input('GOOGLE API KEY', '',help="Enter your API Key")
if google_key!="":
    st.session_state['GOOGLE_API_KEY'] = google_key
    @st.cache_resource
    def build_resources():
        regions_list = ["US","Europe","Global","India","Japan","Emerging","China"]
        #qp_dict = dict.fromkeys(regions_list)
        # def get_qp_helper(region:str):
        #     qp = get_qp(region)
        #     # qp_dict[region] = qp
        #     return qp

        # with concurrent.futures.ThreadPoolExecutor() as executor:
        #     # executor.map(get_qp_helper, regions_list)
        #     for region, region_qp in zip(regions_list, executor.map(get_qp_helper, regions_list)):
        #         # print('%d is prime: %s' % (number, prime))
        #         print(region)
        #         #qp_dict[region] = region_qp
        qp_dict = {}
        retriever = load_database("gemini",5,google_key)
        rag = RAG(
            retriever,
            use_reranker=False,
            use_cot=True,
            rerank_docs=5
        )
        return qp_dict,rag

    qp_dict,rag = build_resources()

    st.session_state['qp_dict'] = qp_dict
    st.session_state['rag'] = rag


