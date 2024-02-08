import chromadb
import glob
import json
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    SentenceTransformersTokenTextSplitter,
)
from sentence_transformers import CrossEncoder


def index_artifacts_to_db(collection_name="default", verbose=True):
    chunked_docs = _prepare_document_chunks_from_artifacts()
    chunked_tokens = _convert_text_chunks_into_token_chunk_metadata_pairs(chunked_docs)
    if verbose:
        print(
            f"The number of text docs retrieved is {len(chunked_docs)} with total number of token chunks being {sum([len(a) for a in chunked_tokens])}"
        )
    collection = _create_index_from_token_chunk_metadata_pairs(
        chunked_tokens, collection_name
    )
    if verbose:
        print(f"Collection created with number of documents: {collection.count()}")


def delete_peristent_collection(collection_name):
    client = chromadb.PersistentClient("../assets/index")
    client.delete_collection(collection_name)


def retrieve_relevant_docs_from_index(
    queries, collection_name="default", n_docs=5, re_ranker_policy="rrf", verbose=True
):
    client = chromadb.PersistentClient("../assets/index")
    collection = client.get_collection(collection_name)

    results = collection.query(
        query_texts=queries, n_results=15
    )  ## retrieve the set of results using multiple queries.
    original_query = queries[0]  ## the first entry of queries is the original query.

    re_ranked_results = []
    if re_ranker_policy != "rrf":
        re_ranked_results = _re_rank_results_using_cross_encoder(
            results, original_query, n_docs
        )
    else:
        re_ranked_results = _re_rank_results_using_rrf(results, n_docs)
    return re_ranked_results


def _prepare_document_chunks_from_artifacts(doc_chunk_size=512):
    ## get all the files with .json extension with their names etc.
    json_files = glob.glob("../artifacts/*/*/*.json")

    ## extract the text content from the files.
    text_docs = []
    for file_name in json_files:
        with open(file_name, "r") as f:
            text_docs.append([json.load(f)["text"], file_name])

    ## divide each piece of text into "chunks" of text.
    character_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ", ", " ", ".", ""],
        chunk_size=doc_chunk_size,  ## number of characters.
    )
    chunked_doc_pairs = [
        [character_splitter.split_text(text_doc_pair[0]), text_doc_pair[1]]
        for text_doc_pair in text_docs
    ]
    return chunked_doc_pairs


def _convert_text_chunks_into_token_chunk_metadata_pairs(
    chunked_doc_pairs, character_overlap=0, tokens_per_token_chunk=128
):
    token_splitter = SentenceTransformersTokenTextSplitter(
        chunk_overlap=character_overlap, tokens_per_chunk=tokens_per_token_chunk
    )

    chunked_token_pairs = []
    for chunked_doc_pair in chunked_doc_pairs:
        ## each doc_pair consists of [List[str], str].
        for chunk_doc_pair in chunked_doc_pair:
            chunked_tokens = token_splitter.split_text(
                chunk_doc_pair[0]
            )  ## splitting the document that is character splitted into token chunks based on model capacity and information specificity requirements.
            chunked_token_pairs += [[a, chunked_doc_pair[1]] for a in chunked_tokens]

    return chunked_token_pairs


def _create_index_from_token_chunk_metadata_pairs(
    token_metadata_pairs, collection_name
):
    ids = [str(i) for i in range(len(token_metadata_pairs))]
    embedding_function = SentenceTransformerEmbeddingFunction()
    client = chromadb.PersistentClient("../assets/index")
    collection = client.create_collection(
        collection_name, embedding_function=embedding_function
    )
    collection.add(
        ids=ids,
        documents=[a[0] for a in token_metadata_pairs],
        metadatas=[{"source": a[1]} for a in token_metadata_pairs],
    )
    return collection


def _re_rank_results_using_cross_encoder(results, original_query, top_n):
    retrieved_documents = list(
        set(
            [
                document
                for querywise_documents in results["documents"]
                for document in querywise_documents
            ]
        )
    )
    cross_encoder = CrossEncoder(
        "cross-encoder/ms-marco-MiniLM-L-6-v2"
    )  ## stored in local cache of system after first time run.
    inference_pairs = [[original_query, doc] for doc in retrieved_documents]
    inference_scores = cross_encoder.predict(inference_pairs)
    retrieved_documents_with_scores = list(zip(retrieved_documents, inference_scores))
    sorted_doc_with_scores = sorted(
        retrieved_documents_with_scores, key=lambda x: -x[1]
    )
    return sorted_doc_with_scores[0:top_n]


def _re_rank_results_using_rrf(results, top_n):
    ranked_document_with_scores = []
    for querywise_documents in results["documents"]:
        for idx, doc in enumerate(querywise_documents):
            try:
                index = [a[0] for a in ranked_document_with_scores].index(doc)
                ranked_document_with_scores[index][1] += 1 / (idx + 1)
            except ValueError:
                ranked_document_with_scores.append([doc, 1 / (idx + 1)])
    sorted_doc_with_scores = sorted(ranked_document_with_scores, key=lambda x: -x[1])
    return sorted_doc_with_scores[0:top_n]
