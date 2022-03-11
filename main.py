from io import BytesIO
from flask import (
    Flask, render_template, request, Response, jsonify, send_file
)
import requests, json

app = Flask(__name__)

model_info_file = "./gan_info.json"

with open(model_info_file, 'r') as json_file:
  models = json.load(json_file)
  
def processing(model, endpoint, request_file, request_data):
    try:
        response = requests.post(url=str(model['url'] + '/' + endpoint),
            files=request_file,
            data=request_data,
        )

        return response
    except Exception as e:
        return "error"

@app.route("/gan", methods=["POST"])
def gan():
    try:
        selected_category = request.form['category']
        model_name = request.form['model']
    except:
        return Response("Empty Field", status=400)

    try:
        model = models[selected_category][model_name]
        endpoint = request.form["endpoint"]
        request_file = dict()
        request_data = dict()
        for type, parameters in model["endpoints"][endpoint].items():
            if type == "string":
                for parameter in parameters.keys():
                    request_data[parameter] = request.form[parameter]
            elif type == "file":
                for parameter in parameters.keys():
                    request_file[parameter] = (request.files[parameter].filename, request.files[parameter], request.files[parameter].content_type)
                    mime_type = request.files[parameter].content_type
    except:
        return Response("Bad Request Error", status=400)
    
    result = processing(model, endpoint, request_file, request_data)
    
    if result == "error":
        return Response('Server Error', status=500)
    elif result.status_code != 200:
        return Response(result.content, status=result.status_code)

    return send_file(BytesIO(result.content), mimetype=mime_type)

@app.route("/category", methods=["GET"])
def get_category():
    result = []
    for k in models.keys():
        result.append(k)
    return jsonify(result), 200

@app.route("/category/<category>", methods=["GET"])
def get_models_in_category(category):
    if category not in models:
        return Response("Not Found Category", status=404)
    return jsonify(models[category]), 200

@app.route("/category/<category>/<model>", methods=["GET"])
def get_model(category, model):
    if category not in models:
        return Response("Not Found Category", status=404)
    if model not in models[category]:
        return Response("Not Found Model", status=404)
    return jsonify(models[category][model]), 200

@app.route("/", methods=["GET"])
def main():
    return render_template("index.html")

@app.route("/health", methods=["GET"])
def health_check():
    return Response("OK", status=200)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5000', threaded=True)