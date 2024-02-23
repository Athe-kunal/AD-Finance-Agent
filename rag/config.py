# DATABASE_NAME = "rag/ad_project_db"
# DATABASE_NAME = "rag/AD-DB-LARGE"
# DATABASE_NAME = "rag/AD-DB-SMALL"
BASE_DATABASE_NAME = "rag/AD-DB-"
COLLECTION_NAME = "ad-project"
# COLLECTION_NAME = "ad-project-small"
# COLLECTION_NAME = "ad-project-large"
EMBEDDING_MODEL = "text-embedding-3-large"
TOP_K = 5
OPENAI_MODEL_NAME = "gpt-3.5-turbo-16k"
HYDE_OPENAI_MODEL_NAME = "gpt-3.5-turbo-16k"
MOD_HYDE_MODEL = "arsrira/ad-distilgpt2"

FINAL_LLM_PROMPT = """Use the following pieces of context to answer the question at the end.\n
        Be very diligent in using all the information and answering in a short and concise.\n

        {context}

        Question: {question}
        """

HYDE_PROMPT = """You are a expert at valuating companies. "Please write a passage to answer the question\n"
    "Try to include as many key details as possible and be concise.\n"
    "\n"
    "\n"
    "Question: {question}\n"
    "\n"
    "\n"
    'Passage:"""