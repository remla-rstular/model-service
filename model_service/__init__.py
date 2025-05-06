import os

from asgiref.wsgi import WsgiToAsgi
from dotenv import load_dotenv
from flask import Flask, request

from model_service.dto import ModelServicePredictRequest, ModelServicePredictResponse
from model_service.github import download_model
from model_service.ml_model import get_model, load_model, get_model_version

load_dotenv()

# Download the model
model_path, model_version = download_model(desired_version=os.getenv("MODEL_VERSION"))
load_model(model_path=model_path, model_version=model_version)

app = Flask(__name__)


@app.route("/predict", methods=["POST"])
def predict():
    # Parse the request data
    try:
        req_data = ModelServicePredictRequest.model_validate(request.get_json())
    except Exception as e:
        return {"error": str(e)}, 400

    # Get the model
    model = get_model()
    # Make the prediction
    pred_data = req_data.review if isinstance(req_data.review, list) else [req_data.review]
    try:
        prediction = model.predict(pred_data)
    except Exception as e:
        return {"error": str(e)}, 500

    if isinstance(req_data.review, str):
        response = ModelServicePredictResponse(
            is_positive=bool(prediction[0]), review=req_data.review
        )
    else:
        response = ModelServicePredictResponse(is_positive=[bool(p) for p in prediction])
    return response.model_dump_json(), 200


@app.route("/version/model", methods=["GET"])
def version():
    return {"version": get_model_version()}, 200


@app.route("/version/app", methods=["GET"])
def app_version():
    return {"version": os.getenv("SERVICE_VERSION")}, 200


asgi_app = WsgiToAsgi(app)
