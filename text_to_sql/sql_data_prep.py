import os
import pandas as pd
from pathlib import Path
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.core.bridge.pydantic import BaseModel, Field
from llama_index.llms.openai.base import OpenAI
import openai
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Integer,
)
from llama_index.core.retrievers import SQLRetriever
from typing import List
from llama_index.core.query_pipeline import FnComponent
import re
import json
from text_to_sql.config import *
from llama_index.core.objects import (
    SQLTableNodeMapping,
    ObjectIndex,
    SQLTableSchema,
)
from llama_index.core.utilities.sql_wrapper import SQLDatabase
from llama_index.core.indices.vector_store import VectorStoreIndex
from llama_index.core.prompts.default_prompts import DEFAULT_TEXT_TO_SQL_PROMPT
from llama_index.core.prompts import PromptTemplate
from llama_index.core.query_pipeline import FnComponent
from llama_index.core.llms import ChatResponse
from llama_index.core.query_pipeline import QueryPipeline as QP
from llama_index.core.service_context import ServiceContext
from llama_index.core.indices.vector_store import VectorStoreIndex
from llama_index.core.indices.loading import load_index_from_storage
from sqlalchemy import text
from llama_index.core.schema import TextNode
from llama_index.core.storage import StorageContext
import os
from pathlib import Path
from typing import Dict
from llama_index.core.indices.struct_store.sql_retriever import SQLRetriever
from typing import List
from llama_index.core.query_pipeline import FnComponent
from tqdm import tqdm
from llama_index.core.query_pipeline import (
    QueryPipeline as QP,
    Link,
    InputComponent,
    CustomQueryComponent,
)

load_dotenv()

openai.api_key = os.environ['OPENAI_API_KEY']

def get_qp():
    table_infos = []
    for file_name in os.listdir(TABLEINFO_DIR):
        file_path = os.path.join(TABLEINFO_DIR, file_name)
        with open(file_path, "r") as f:
            data = json.load(f)
            table_infos.append(data)

    # create engine
    engine = create_engine(f"sqlite:///text_to_sql/all_tables_.db")
    metadata_obj = MetaData()
    sql_database = SQLDatabase(engine)

    table_node_mapping = SQLTableNodeMapping(sql_database)
    table_schema_objs = [
        SQLTableSchema(table_name=t["table_name"], context_str=t["table_summary"])
        for t in table_infos
    ]  # add a SQLTableSchema for each table

    obj_index = ObjectIndex.from_objects(
        table_schema_objs,
        table_node_mapping,
        VectorStoreIndex,
    )
    obj_retriever = obj_index.as_retriever(similarity_top_k=3)

    def get_table_context_str(table_schema_objs: List[SQLTableSchema], sql_database):
        """Get table context string."""
        context_strs = []
        for table_schema_obj in table_schema_objs:
            table_info = sql_database.get_single_table_info(table_schema_obj.table_name)
            if table_schema_obj.context_str:
                table_opt_context = " The table description is: "
                table_opt_context += table_schema_obj.context_str
                table_info += table_opt_context

            context_strs.append(table_info)
        return "\n\n".join(context_strs)

    table_parser_component = FnComponent(fn=get_table_context_str)

    def parse_response_to_sql(response: ChatResponse) -> str:
        """Parse response to SQL."""
        response = response.message.content
        sql_query_start = response.find("SQLQuery:")
        if sql_query_start != -1:
            response = response[sql_query_start:]
            # TODO: move to removeprefix after Python 3.9+
            if response.startswith("SQLQuery:"):
                response = response[len("SQLQuery:") :]
        sql_result_start = response.find("SQLResult:")
        if sql_result_start != -1:
            response = response[:sql_result_start]
        return response.strip().strip("```").strip()

    sql_parser_component = FnComponent(fn=parse_response_to_sql)

    text2sql_prompt = DEFAULT_TEXT_TO_SQL_PROMPT.partial_format(
        dialect=engine.dialect.name
    )

    response_synthesis_prompt_str = (
        "Given an input question, synthesize a response from the query results. Multiply all non-percentage values by one million. Write the numbers in a easy-human readable format. Return the SQL query and relevant rows used as well \n"
        "Query: {query_str}\n"
        "SQL: {sql_query}\n"
        "SQL Response: {context_str}\n"
        "Response Context: {sql_query} & {context_str} \n"
        "SqlQuery: "
        "Response: "
    )
    response_synthesis_prompt = PromptTemplate(
        response_synthesis_prompt_str,
    )

    llm1 = OpenAI(model=MODEL_1, temperature=0.0)
    llm2 = OpenAI(model=MODEL_2, temperature=0.0)

    qp = QP(verbose=False)
    service_context = ServiceContext.from_defaults(callback_manager=qp.callback_manager)
    vector_index_dict = {}

    def index_all_tables(
        sql_database: SQLDatabase, table_index_dir: str = TABLE_INDEX_DIR
    ) -> Dict[str, VectorStoreIndex]:
        """Index all tables."""
        if not Path(table_index_dir).exists():
            os.makedirs(table_index_dir)

        vector_index_dict = {}
        engine = sql_database.engine
        for table_name in tqdm(sql_database.get_usable_table_names()):
            # print(f"Indexing rows in table: {table_name}")
            # rebuild storage context
            storage_context = StorageContext.from_defaults(
                persist_dir=f"{table_index_dir}/{table_name}"
            )
            # load index
            index = load_index_from_storage(
                storage_context,
                index_id="vector_index",
                service_context=service_context,
            )
            vector_index_dict[table_name] = index
        return vector_index_dict

    vector_index_dict = index_all_tables(sql_database)
    sql_retriever = SQLRetriever(sql_database)

    def get_table_context_and_rows_str(
        query_str: str, table_schema_objs: List[SQLTableSchema]
    ):
        """Get table context string."""
        context_strs = []
        for table_schema_obj in table_schema_objs:
            # first append table info + additional context
            table_info = sql_database.get_single_table_info(table_schema_obj.table_name)
            if table_schema_obj.context_str:
                table_opt_context = " The table description is: "
                table_opt_context += table_schema_obj.context_str
                table_info += table_opt_context

            # also lookup vector index to return relevant table rows
            vector_retriever = vector_index_dict[
                table_schema_obj.table_name
            ].as_retriever(similarity_top_k=2)
            relevant_nodes = vector_retriever.retrieve(query_str)
            if len(relevant_nodes) > 0:
                table_row_context = "\nHere are some relevant example rows (values in the same order as columns above)\n"
                for node in relevant_nodes:
                    table_row_context += str(node.get_content()) + "\n"
                table_info += table_row_context

            context_strs.append(table_info)
        return "\n\n".join(context_strs)

    table_parser_component = FnComponent(fn=get_table_context_and_rows_str)
    qp.add_modules(
        {
            "input": InputComponent(),
            "table_retriever": obj_retriever,
            "table_output_parser": table_parser_component,
            "text2sql_prompt": text2sql_prompt,
            "text2sql_llm": llm1,
            "sql_output_parser": sql_parser_component,
            "sql_retriever": sql_retriever,
            "response_synthesis_prompt": response_synthesis_prompt,
            "response_synthesis_llm": llm2,
        }
    )

    qp.add_link("input", "table_retriever")
    qp.add_link("input", "table_output_parser", dest_key="query_str")
    qp.add_link("table_retriever", "table_output_parser", dest_key="table_schema_objs")
    qp.add_link("input", "text2sql_prompt", dest_key="query_str")
    qp.add_link("table_output_parser", "text2sql_prompt", dest_key="schema")
    qp.add_chain(
        ["text2sql_prompt", "text2sql_llm", "sql_output_parser", "sql_retriever"]
    )
    qp.add_link("sql_output_parser", "response_synthesis_prompt", dest_key="sql_query")
    qp.add_link("sql_retriever", "response_synthesis_prompt", dest_key="context_str")
    qp.add_link("input", "response_synthesis_prompt", dest_key="query_str")
    qp.add_link("response_synthesis_prompt", "response_synthesis_llm")

    return qp
