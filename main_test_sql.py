# from text_to_sql.text_to_sql_main import chat_text_to_sql

# # print(chat_text_to_sql("What is the change in goodwill for aerospace industry?"))
# print(chat_text_to_sql("What are the total debt without losses for advertisement sector?"))

from sqlalchemy import create_engine
create_engine("sqlite:///text_to_sql/US/all_tables_.db")