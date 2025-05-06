import os


def get_cache_dir() -> str:
    """
    Get the cache directory for the model.
    """
    cache_dir = os.getenv(
        "MODEL_CACHE_DIR", os.path.join(os.path.expanduser("~"), ".cache", "model_service")
    )
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir
