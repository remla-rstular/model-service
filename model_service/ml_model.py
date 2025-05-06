import joblib
from loguru import logger
from sklearn.pipeline import Pipeline

_MODEL: tuple[Pipeline, str] | None = None


def load_model(model_path: str, model_version: str | None = None) -> None:
    global _MODEL

    if _MODEL is not None:
        logger.warning("Model already loaded, loading again will overwrite the existing model")

    _MODEL = (joblib.load(model_path), model_version or "N/A")
    logger.info(f"Model loaded from {model_path}")


def get_model() -> Pipeline:
    global _MODEL

    if _MODEL is None:
        raise Exception("Model not loaded")

    return _MODEL[0]


def get_model_version() -> str:
    global _MODEL

    if _MODEL is None:
        raise Exception("Model not loaded")

    return _MODEL[1]
