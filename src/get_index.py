from retrieval_utils import index_artifacts_to_db, delete_peristent_collection, retrieve_relevant_docs_from_index

if __name__ == "__main__":
    ## Step1a: create a persistent collection.
    ## index_artifacts_to_db("sample")
    
    ## Step1b: deleting a persistent collection.
    ## delete_peristent_collection("sample")
    
    ## Step2: query the persistent collection.
    print(retrieve_relevant_docs_from_index(["What is finance?", "How is finance?"], "sample"))