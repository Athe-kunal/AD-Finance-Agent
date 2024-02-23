from flask import Flask,request
from flask_cors import CORS, cross_origin
from processQuery import generate_response
import ast
import json

with open('books.json', 'r') as json_file:
    data = json.load(json_file)
    print(data)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/test")
@cross_origin()
def index():
    return {
        'success': 'Test call success'
    }

@app.route("/query")
@cross_origin()
def processQuery():
    qryString = request.args.get('query')
    qryRagModel = request.args.get('model')
    if (not qryString or not qryRagModel):
        return {
            "text": "Query or Model Param missing"
        }
    else:
        response, context, meta_data = generate_response(qryString,qryRagModel)
        books = ast.literal_eval(f"{meta_data}")
        for book in books:
            coordinates = ast.literal_eval(f"{book['page_num_coordinates']}")
            book['page_num_coordinates'] = coordinates
            book['bookURL'] = data[book['book_source']]
        return {
            "result": f"Recevied response",
            "response": f"{response}",
            "context": f"{context}",
            "metaData": books
        }

