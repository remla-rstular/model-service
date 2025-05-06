import os

from asgiref.wsgi import WsgiToAsgi
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_httpauth import HTTPTokenAuth
from lib_ml.preprocess import process_text

from model_service.dto import ModelServicePredictRequest, ModelServicePredictResponse
from model_service.github import download_model
from model_service.ml_model import get_model, get_model_version, load_model

load_dotenv()

auth = HTTPTokenAuth(scheme="Bearer")

token_file = os.getenv("AUTH_TOKEN_FILE")
if not token_file:
    raise ValueError("AUTH_TOKEN_FILE environment variable is not set.")
with open(token_file, "r") as f:
    STATIC_TOKEN = f.read().strip()


@auth.verify_token
def verify_token(token):
    # Compare the provided token with our static token
    if token == STATIC_TOKEN:
        return True
    return False


# Download the model
model_path, model_version = download_model(desired_version=os.getenv("MODEL_VERSION"))
load_model(model_path=model_path, model_version=model_version)

app = Flask(__name__)


@app.route("/predict", methods=["POST"])
@auth.login_required
def predict():
    # Parse the request data
    try:
        req_data = ModelServicePredictRequest.model_validate(request.get_json())
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    # Get the model
    model = get_model()
    # Make the prediction
    pred_data = req_data.review if isinstance(req_data.review, list) else [req_data.review]
    # Preprocess the data
    pred_data = process_text(pred_data)
    try:
        prediction = model.predict(pred_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    if isinstance(req_data.review, str):
        response = ModelServicePredictResponse(
            is_positive=bool(prediction[0]), review=req_data.review
        )
    else:
        response = ModelServicePredictResponse(is_positive=[bool(p) for p in prediction])
    return jsonify(response.model_dump_json()), 200


@app.route("/version/model", methods=["GET"])
@auth.login_required
def version():
    return jsonify({"version": get_model_version()}), 200


@app.route("/version/app", methods=["GET"])
@auth.login_required
def app_version():
    return jsonify({"version": os.getenv("SERVICE_VERSION")}), 200


asgi_app = WsgiToAsgi(app)
