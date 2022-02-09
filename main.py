from flask import (
    Flask, render_template, request, Response, jsonify, send_file
)
import requests
from requests_toolbelt import MultipartEncoder
from enum import Enum

app = Flask(__name__)

class FileType(Enum):
    FILE = 1
    STRING = 2

models = {
    "Cartoonize": {
        "JoJoGAN": {
            "url": "https://main-jo-jo-gan-dev2l0per.endpoint.ainize.ai",
            "endpoints": {
                "jojogan": {
                    "parameters": {
                        "file": "file",
                        "pretrained": "string",
                    },
                },
            },
        },
        "AnimeGANv2": {
            "url": "https://main-animegan2-pytorch-dev2l0per.endpoint.ainize.ai",
            "endpoints": {
                "animeganv2": {
                    "parameters": {
                        "file": "file",
                        "pretrained": "string",
                    },
                }
            }
        },
        "StarGANv2": {
            "url": "https://master-stargan-v2-frontend-gkswjdzz.endpoint.ainize.ai",
            "endpoints": {
                "predict": {
                    "parameters": {
                        "source": "file",
                        "check_model": "string",
                    },
                },
            },
        },
        "UGATIT": {
            "url": "https://master-ugatit-kmswlee.endpoint.ainize.ai",
            "endpoints": {
                "selfie2anime": {
                    "parameters": {
                        "file": "file",
                    },
                },
                "anime2selfie": {
                    "parameters": {
                        "file": "file",
                    },
                },
            },
        },
        "Cartoonize": {
            "url": "https://master-white-box-cartoonization-psi1104.endpoint.ainize.ai",
            "endpoints": {
                "predict": {
                    "parameters": {
                        "file_type": "string",
                        "source": "file",
                    },
                },
            },
        },
    },
}

@app.route("/gan", methods=["POST"])
def gan():
    try:
        selectedCategory = request.form['category']
        modelName = request.form['model']
    except:
        return Response("Empty Field", status=400)
    
    try:
        model = models[selectedCategory][modelName]
        endpoint = request.form["endpoint"]
        requestFile = dict()
        requestData = dict()
        for k, v in model["endpoints"][endpoint]["parameters"].items():
            if v == "string":
                requestData[k] = request.form[k]
            elif v == "file":
                requestFile[k] = (request.files[k].filename, request.files[k], request.files[k].content_type)
    except:
        return Response("Error", status=400)

    print(requestFile)

    response = requests.post(url=str(model["url"] + "/" + endpoint),
        files=requestFile,
        data=requestData
    )

    return send_file(response.content, mimetype='image/jpeg')

@app.route("/category", methods=["GET"])
def getCategory():
    result = []
    for k, v in models.items():
        result.append(k)
    return Response(result, status=200)

@app.route("/category/<category>")
def getModelsInCategory(category):
    if category not in models:
        return Response("Not Found Category", status=404)
    return jsonify(models[category]), 200

@app.route("/")
def main():
    return render_template("index.html")

@app.route("/healthz", methods=["GET"])
def healthCheck():
    return Response("OK", status=200)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='1234')