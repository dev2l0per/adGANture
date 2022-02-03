from flask import (
    Flask, render_template, request, Response, jsonify
)
import requests

app = Flask(__name__)

models = {
    "Cartoonize": {
        "JoJoGAN": {
            "url": "https://main-jo-jo-gan-dev2l0per.endpoint.ainize.ai",
            "endpoints": {
                "jojogan": {
                    "parameters": [
                        "file",
                        "pretrained",
                    ],
                },
            },
        },
        "AnimeGANv2": {
            "url": "https://main-animegan2-pytorch-dev2l0per.endpoint.ainize.ai",
            "endpoints": {
                "animeganv2": {
                    "parameters": [
                        "file",
                        "pretrained",
                    ],
                }
            }
        },
        "StarGANv2": {
            "url": "https://master-stargan-v2-frontend-gkswjdzz.endpoint.ainize.ai",
            "endpoints": {
                "predict": {
                    "parameters": [
                        "source",
                        "check_model",
                    ],
                },
            },
        },
        "UGATIT": {
            "url": "https://master-ugatit-kmswlee.endpoint.ainize.ai",
            "endpoints": {
                "selfie2anime": {
                    "parameters" [
                        "file",
                    ],
                },
                "anime2selfie": {
                    "parameters": [
                        "file",
                    ],
                },
            },
        },
        "Cartoonize": {
            "url": "https://master-white-box-cartoonization-psi1104.endpoint.ainize.ai",
            "endpoints": {
                "predict": {
                    "parameters": [
                        "file_type",
                        "source",
                    ],
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
        requestForm = dict()
        requestForm["endpoint"] = request.form["endpoint"]
        for parameter in model["endpoints"][requestForm["endpoint"]]["parameters"]:
            requestForm[parameter] = request.form[parameter]
    except:
        return Response("Error", status=400)

    return "ok"

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
    return Response(models[category], status=200)

@app.route("/")
def main():
    return render_template("index.html")

@app.route("healthz", methods=["GET"])
def healthCheck():
    return Response("OK", status=200)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='5000')