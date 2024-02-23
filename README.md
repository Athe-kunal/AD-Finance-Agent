# AD-Finance-Agent

In this repo, we are building a bot that can mimic the style of Prof. Aswath Damodaran based on his YouTube lectures and textbooks. Here, we are working on three techniques, Retrieval-Augmented Generation (RAG), Hypothetical document embeddings (HyDE) and Modified HyDE, which is a novel concept of finetuning a decoder-only model on our raw data followed by HyDE from the generated answer. It is a research question that we are looking to explore.

The vector database are stored [here](https://drive.google.com/file/d/1TG3A25Phy9xx-N7VMc55dqjgqS9PuEYJ/view?usp=drivesdk). You can download from here and place the two folders inside the VectorDB, named 
AD-DB-LARGE AND AD-DB-SMALL, and store it inside the rag folder

### Environment Setup

**Create**

```
python -m venv <NAME_OF_THE_ENVIRONMENT>
```

**Activate** 

```
source <NAME_OF_THE_ENVIRONMENT>/bin/activate
```

**Install**

```
pip install -r requirements.txt
```

### Setup environment variables

Please add `.env` files at below shown positions.

ad-finance-agent
    │
    ├── rag
    │   ├── .env
    ├── text_to_sql
    │   ├── .env
    └── app.py
    └── .env

**Content**

```
OPENAI_API_KEY=<INSERT_YOUR_OPENAI_GENERATEDKEY>
```

### Run the App

```
flask run
```

### **Front-end**

**To Start the Front-end service please refer [here.](https://github.com/Athe-kunal/AD-Finance-Agent/blob/deploy/web/ad-finance-agent-ui/README.md)**

