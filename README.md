# AD-Finance-Agent

Idhar project k baare me 4 line bol

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
