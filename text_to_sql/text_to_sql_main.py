from text_to_sql.sql_data_prep import get_qp

qp = get_qp()
def chat_text_to_sql(question):
    response = qp.run(query=question)

    return response