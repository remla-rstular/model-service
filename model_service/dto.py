from pydantic import BaseModel


class ModelServicePredictRequest(BaseModel):
    review: str | list[str]


class ModelServicePredictResponse(BaseModel):
    is_positive: bool | list[bool]
