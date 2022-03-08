from io import BytesIO
from queue import Empty, Queue
import threading
from flask import (
    Flask, render_template, request, Response, jsonify, send_file
)
import requests, time

app = Flask(__name__)

models = {
    "Cartoonize": {
        "JoJoGAN": {
            "url": "https://main-jo-jo-gan-dev2l0per.endpoint.ainize.ai",
            "github": "https://github.com/dev2l0per/JoJoGAN",
            "ainize": "https://ainize.ai/dev2l0per/JoJoGAN?branch=main",
            "endpoints": {
                "jojogan": {
                    "file": {
                        "file": [],
                    },
                    "string": {
                        "pretrained": [
                            "arcane_caitlyn",
                            "arcane_caitlyn_preserve_color",
                            "arcane_jinx",
                            "arcane_jinx_preserve_color",
                            "arcane_multi",
                            "arcane_multi_preserve_color",
                            "disney",
                            "disney_preserve_color",
                            "jojo",
                            "jojo_preserve_color",
                            "jojo_yasuho",
                            "jojo_yasuho_preserve_color",
                            "supergirl",
                            "supergirl_preserve_color",
                            "art",
                        ],
                    },
                },
            },
        },
        "AnimeGANv2": {
            "url": "https://main-animegan2-pytorch-dev2l0per.endpoint.ainize.ai",
            "github": "https://github.com/dev2l0per/animegan2-pytorch",
            "ainize": "https://ainize.ai/dev2l0per/animegan2-pytorch?branch=main",
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
        "UGATIT": {
            "url": "https://master-ugatit-kmswlee.endpoint.ainize.ai",
            "github": "https://github.com/kmswlee/UGATIT",
            "ainize": "https://ainize.ai/kmswlee/UGATIT",
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
        "Cartoonizer": {
            "url": "https://master-white-box-cartoonization-psi1104.endpoint.ainize.ai",
            "github": "https://github.com/psi1104/White-box-Cartoonization",
            "ainize": "https://ainize.ai/psi1104/White-box-Cartoonization?branch=master",
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
        "Cartoonify": {
            "url": "https://ainize-cartoonify-dev2l0per.endpoint.ainize.ai",
            "github": "https://github.com/dev2l0per/Cartoonify",
            "ainize": "https://ainize.ai/dev2l0per/Cartoonify?branch=ainize",
            "endpoints": {
                "cartoonify": {
                    "file": {
                        "file": [],
                    },
                },
            },
        },
    },
    "Neural Style Transfer": {
        "neural-style-tf": {
            "url": "https://master-neural-style-tf-jeong-hyun-su.endpoint.ainize.ai",
            "github": "https://github.com/Jeong-Hyun-Su/neural-style-tf",
            "ainize": "https://ainize.ai/Jeong-Hyun-Su/neural-style-tf",
            "endpoints": {
                "combine": {
                    "file": {
                        "content": [],
                        "style": [],
                    },
                    "string": {
                        "range": [
                            '1',
                            '2',
                            '3',
                            '4',
                            '5',
                        ],
                    },
                },
            },
        },
    },
    "Detection": {
        "Instance Shadow Detection": {
            "url": "https://master-instance-shadow-detection-gmlee329.endpoint.ainize.ai",
            "github": "https://github.com/Jeong-Hyun-Su/neural-style-tf",
            "ainize": "https://ainize.ai/gmlee329/InstanceShadowDetection",
            "endpoints": {
                "detection": {
                    "file": {
                        "image": [],
                    },
                },
            },
        },
    },
    "High Resolution Translation": {
        "HiDT": {
            "url": "https://master-hi-dt-psi1104.endpoint.ainize.ai",
            "github": "https://github.com/psi1104/HiDT",
            "ainize": "https://ainize.ai/psi1104/HiDT?branch=master",
            "endpoints": {
                "predict": {
                    "file": {
                        "source": [],
                    },
                    "string": {
                        "daytime": [
                            "day1",
                            "day2",
                            "day3",
                            "day4",
                            "sunset1",
                            "sunset2",
                            "sunset3",
                            "sunset4",
                            "bluehour1",
                            "bluehour2",
                            "night1",
                            "night2",
                            "night3",
                            "night4",
                            "night5",
                            "night6",
                        ],
                        "inference_size": [
                            "256",
                            "512",
                            "1024",
                        ],
                    },
                },
            },
        },
    },
}

requestsQueue = Queue()
BATCH_SIZE = 1
CHECK_INTERVAL = 0.1

def handle_requests_by_batch():
    while True:
        requestsBatch = []
        while not (len(requestsBatch) >= BATCH_SIZE):
            try:
                requestsBatch.append(requestsQueue.get(timeout=CHECK_INTERVAL))
            except Empty:
                continue
            
            for request in requestsBatch:
                request['output'] = processing(request['input'][0], request['input'][1], request['input'][2], request['input'][3])

def processing(model, endpoint, requestFile, requestData):
    try:
        response = requests.post(url=str(model['url'] + '/' + endpoint),
            files=requestFile,
            data=requestData,
        )

        return response
    except Exception as e:
        return "error"

@app.route("/gan", methods=["POST"])
def gan():
    if requestsQueue.qsize() > BATCH_SIZE:
        return Response('Too Many Requests', status=429)

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
    
    req = {
        'input': [model, endpoint, requestFile, requestData],
    }

    requestsQueue.put(req)

    while 'output' not in req:
        time.sleep(CHECK_INTERVAL)

    io = req['output']
    
    if io == "error":
        return Response('Server Error', status=500)
    elif io.status_code != 200:
        return Response(io.content, status=io.status_code)

    return send_file(BytesIO(io.content), mimetype=mimeType)

@app.route("/category", methods=["GET"])
def getCategory():
    result = []
    for k in models.keys():
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

@app.route("/health", methods=["GET"])
def healthCheck():
    return Response("OK", status=200)

threading.Thread(target=handle_requests_by_batch).start()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='5000')