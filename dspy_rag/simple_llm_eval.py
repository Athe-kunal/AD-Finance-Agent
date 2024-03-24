import dspy
import sys
from dsp.utils import dotdict
from rag_module import RAG
from config import *
from database import load_database
import pandas as pd
import os
import tqdm
# This is a WIP, the next step is to optimize this metric as itself a DSPy module (pretty meta)

# Reference - https://github.com/stanfordnlp/dspy/blob/main/examples/tweets/tweet_metric.py


# Signature for LLM assessments.
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')


class Assess(dspy.Signature):
    """Assess the quality of an answer to a question."""
    
    context = dspy.InputField(desc="The context for answering the question.")
    assessed_question = dspy.InputField(desc="The evaluation criterion.")
    assessed_answer = dspy.InputField(desc="The answer to the question.")
    assessment_answer = dspy.OutputField(desc="A rating between 1 and 5. Only output the rating and nothing else.")

def llm_metric(gold, pred, metricLM,trace=None):
    
    retriever = load_database('hf',k=1)
    predicted_answer = pred.answer
    question = gold.question
    
    print(f"Test Question: {question}")
    print(f"Predicted Answer: {predicted_answer}")
    
    detail = "Is the assessed answer detailed?"
    faithful = "Is the assessed text grounded in the context? Say no if it includes significant facts not in the context."
    overall = f"Please rate how well this answer answers the question, `{question}` based on the context.\n `{predicted_answer}`"
    
    with dspy.context(lm=metricLM):
        
        context = [p.text for p in retriever.retrieve(question)]
        detail = dspy.ChainOfThought(Assess)(context="N/A", assessed_question=detail, assessed_answer=predicted_answer)
        faithful = dspy.ChainOfThought(Assess)(context=context, assessed_question=faithful, assessed_answer=predicted_answer)
        overall = dspy.ChainOfThought(Assess)(context=context, assessed_question=overall, assessed_answer=predicted_answer)
    
    print(f"Faithful: {faithful.assessment_answer}")
    print(f"Detail: {detail.assessment_answer}")
    print(f"Overall: {overall.assessment_answer}")
    
    
    #total = float(detail.assessment_answer) + float(faithful.assessment_answer)*2 + float(overall.assessment_answer)
    
    return float(detail.assessment_answer),float(faithful.assessment_answer),float(overall.assessment_answer)

class ChromaDBPipelineRM(dspy.Retrieve):
    def __init__(self,embedding_source:str="hf",k:int=5):
        super().__init__()
        self.retriever = load_database(embedding_source,k)
    
    def forward(self,query):
        llama_index_docs = self.retriever.retrieve(query)
        metadata_list = []
        context_list = []

        for ld in llama_index_docs:
            metadata_list.append(ld.metadata)
            context_list.append(ld.text)
        return dspy.Prediction(
            passages = [dotdict({"long_text": x}) for x in context_list],
            metadata = metadata_list
        )

class DSPyRM(dspy.Module):
    def __init__(self):
        super().__init__()
        self.retriever_model = ChromaDBPipelineRM(embedding_source="hf",k=5)
    
    def forward(self,query,k):
        vectorDB_output = self.retriever_model(query)
        return vectorDB_output.passages

if __name__=="__main__":
    EMBEDDING_SOURCE = 'hf'
    TOP_K = 5

    metricLM = dspy.OpenAI(model='gpt-3.5-turbo-0125', max_tokens=4096, api_key=OPENAI_API_KEY,model_type='chat')
    
    eval_dataset = pd.read_csv("../src/data/Evaluation Dataset.csv")
    eval_dataset = eval_dataset.loc[:,["QUESTION","ANSWER"]]
    
    eval_dataset.dropna(inplace=True)
    questions = eval_dataset['QUESTION']
    answers = eval_dataset['ANSWER']
    
    
    lm = dspy.Google("models/gemini-1.0-pro",
                         api_key=GOOGLE_API_KEY,
                    )
    
    #lm = dspy.OpenAI(model='gpt-3.5-turbo-0125', max_tokens=4096, api_key=OPENAI_API_KEY)
    
    dspy.settings.configure(lm = lm)
    

    retriever = load_database(embedding_source=EMBEDDING_SOURCE,k = TOP_K)
    rag = RAG(retriever,use_cot=False)

    detail_ls = []
    faith_ls = []
    overall_ls = []

    preds = []
    true_answers = []
    accuracy = 0
    num_questions = 10
    k=0
    for i,(question,answer) in enumerate(tqdm.tqdm(zip(questions[:num_questions],
                               answers[:num_questions]))):
        
        try:
            response = rag(question)
            test_example = dspy.Example(question=question)
            
            test_pred = dspy.Example(answer=response.answer)
            
            pred_option = response.answer.split('.')[0]
            
            true_option = answer.split(".")[0]
            if pred_option==true_option:
                accuracy+=1

            preds.append(response.answer)
            k+=1

        except Exception as err: 
            # print("Issue with question: ")
            # print("IDX: ",i)
            # print("R: ",response.answer)
            # print("A: ",answer)
            # print("ERR: ",err)
            continue
        
        detail,faith,overall = llm_metric(test_example, test_pred,metricLM)
        detail_ls.append(detail)
        faith_ls.append(faith)
        overall_ls.append(overall)
    
    print("Number of correct questions: ")
    print("Accuracy: ",accuracy/k)
    
    metric_df = pd.DataFrame()
    metric_df["QUESTION"] = questions[:k]
    metric_df["ACTUAL ANSWER"] = answers[:k]
    metric_df["PREDICTED ANSWER"] = preds[:k]
    
    metric_df["DETAIL"] = detail_ls
    metric_df["FAITHFULNESS"] = faith_ls
    metric_df["OVERALL"] = overall_ls

    metric_df.to_csv("../outputs/Metric_df.csv")
    print("Average detail: ",sum(detail_ls)/len(detail_ls))
    print("Average faith: ",sum(faith_ls)/len(faith_ls))
    print("Average overall: ",sum(overall_ls)/len(overall_ls))

    

    