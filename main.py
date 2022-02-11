from io import BytesIO
from flask import (
    Flask, render_template, request, Response, jsonify, send_file
)
import requests
from requests_toolbelt import MultipartEncoder
from enum import Enum
import json

app = Flask(__name__)

models = {
    "Cartoonize": {
        "JoJoGAN": {
            "url": "https://main-jo-jo-gan-dev2l0per.endpoint.ainize.ai",
            "endpoints": {
                "jojogan": {
                    "file": {
                        "file": [],
                    },
                    "string": {
                        "pretrained": [],
                    },
                },
            },
        },
        "AnimeGANv2": {
            "url": "https://main-animegan2-pytorch-dev2l0per.endpoint.ainize.ai",
            "endpoints": {
                "animeganv2": {
                    "file": {
                        "file": [],
                    },
                    "string": {
                        "pretrained": [
                            "celeba_distill",
                            "face_paint_512_v1",
                            "face_paint_512_v2",
                            "paprika",
                        ],
                    },
                },
            },
        },
        "StarGANv2": {
            "url": "https://master-stargan-v2-frontend-gkswjdzz.endpoint.ainize.ai",
            "endpoints": {
                "predict": {
                    "file": {
                        "source": [],
                    },
                    "string": {
                        "check_model": [
                            "Human Face",
                            "Animal Face",
                        ],
                    },
                },
            },
        },
        "UGATIT": {
            "url": "https://master-ugatit-kmswlee.endpoint.ainize.ai",
            "endpoints": {
                "selfie2anime": {
                    "file": {
                        "file": [],
                    },
                },
                "anime2selfie": {
                    "file": {
                        "file": [],
                    },
                },
            },
        },
        "Cartoonize": {
            "url": "https://master-white-box-cartoonization-psi1104.endpoint.ainize.ai",
            "endpoints": {
                "predict": {
                    "file": {
                        "source": [],
                    },
                    "string": {
                        "file_type": [
                            "image",
                            "video",
                        ],
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
        for type, parameters in model["endpoints"][endpoint].items():
            if type == "string":
                for parameter in parameters.keys():
                    requestData[parameter] = request.form[parameter]
            elif type == "file":
                for parameter in parameters.keys():
                    requestFile[parameter] = (request.files[parameter].filename, request.files[parameter], request.files[parameter].content_type)
                    mimeType = request.files[parameter].content_type
    except:
        return Response("Error", status=400)

    response = requests.post(url=str(model["url"] + "/" + endpoint),
        files=requestFile,
        data=requestData
    )

    if response.status_code != 200:
        return Response("Model API Error", status=response.status_code)

    return send_file(BytesIO(response.content), mimetype=mimeType)

@app.route("/category", methods=["GET"])
def getCategory():
    result = []
    for k, v in models.items():
        result.append(k)
    return jsonify(result), 200

@app.route("/category/<category>", methods=["GET"])
def getModelsInCategory(category):
    if category not in models:
        return Response("Not Found Category", status=404)
    return jsonify(models[category]), 200

@app.route("/category/<category>/<model>", methods=["GET"])
def getModel(category, model):
    if category not in models:
        return Response("Not Found Category", status=404)
    if model not in models[category]:
        return Response("Not Found Model", status=404)
    return jsonify(models[category][model]), 200

@app.route("/", methods=["GET"])
def main():
    return render_template("index.html")

@app.route("/healthz", methods=["GET"])
def healthCheck():
    return Response("OK", status=200)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='1234')