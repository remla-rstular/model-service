import os
from typing import TypedDict

import requests
from loguru import logger

from model_service.settings import get_cache_dir

MODEL_REPOSITORY = "remla-rstular/model-training"


class ModelRelease(TypedDict):
    tag_name: str
    model_url: str


def get_latest_model_release(
    desired_version: str | None = None, repository: str = MODEL_REPOSITORY
) -> ModelRelease:
    """
    Get the latest release from a GitHub repository

    Args:
        repo_owner (str): Repository owner (username or organization)
        repo_name (str): Repository name

    Returns:
        dict: Latest release information
    """
    url = f"https://api.github.com/repos/{repository}/releases/"

    if desired_version:
        url += f"tags/{desired_version}"
    else:
        url += "latest"

    response = requests.get(url)

    if response.status_code == 200:
        resp_json = response.json()
        return {
            "model_url": resp_json["assets"][0]["url"],
            "tag_name": resp_json["tag_name"],
        }
    else:
        raise Exception(f"Failed to fetch release. Status code: {response.status_code}")


def download_model(desired_version: str | None = None) -> tuple[str, str]:
    """
    Download the model from the latest release

    Args:
        desired_version (str): Desired version of the model to download
    """
    model_data = get_latest_model_release(desired_version)
    model_url = model_data["model_url"]
    tag_name = model_data["tag_name"]

    cache_dir = get_cache_dir()
    MODEL_FILENAME = f"{cache_dir}/model_{tag_name}.pkl"

    # Check if the model file already exists
    if os.path.exists(MODEL_FILENAME):
        logger.info(f"Model already exists at {MODEL_FILENAME}")
        return MODEL_FILENAME, tag_name

    response = requests.get(model_url, headers={"Accept": "application/octet-stream"})
    if response.status_code == 200:
        with open(MODEL_FILENAME, "wb") as f:
            f.write(response.content)
        logger.info(f"Model downloaded and saved to {MODEL_FILENAME}")
        return MODEL_FILENAME, tag_name
    else:
        raise Exception(f"Failed to download model. Status code: {response.status_code}")
