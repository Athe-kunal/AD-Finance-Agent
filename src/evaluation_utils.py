### measure:
### 1. "embedding_distance".
### 2. "string_distance"
### 3. actual inference of an LLM.

import json
import math
from functools import lru_cache
from langchain_community.embeddings import HuggingFaceHubEmbeddings
from langchain_community.utils.math import cosine_similarity

def evaluate(llm_func):
    data = json.load('data/test/q&A.json')
    questions, expected_anss = [a['question'] for a in data], [a['answer'] for a in data]
    actual_anss = [llm_func(a) for a in questions]
    ans_pairs = zip(expected_anss, actual_anss)
    return [_compare_individual_answers(b[0], b[1]) for b in ans_pairs]
    
def _compare_individual_answers(expected_ans, actual_ans):
    return { "lev_distance": _find_levenshin_distance(expected_ans, actual_ans), "embed_distance": _find_embedding_distance(expected_ans, actual_ans) }

def _find_levenshin_distance(expected_ans, actual_ans):
    return lev(expected_ans, actual_ans)

def _find_embedding_distance(expected_ans, actual_ans):
    embeddings = HuggingFaceHubEmbeddings(model_name="all-MiniLM-L6-v2")
    return cosine_similarity(embeddings.embed_query(expected_ans), embeddings.embed_query(actual_ans))
        
@lru_cache
def lev(a, b):
    if len(a) == 0:
        return len(b)
    elif len(b) == 0:
        return len(a)
    elif a[0] == b[0]:
        return lev(a[1:], b[1:])
    else:
        return 1 + math.min(lev(a, b[1:]), lev(a[1:], b), lev(a[1:], b[1:]))