#
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from __future__ import annotations
from aiohttp import ClientSession
from dataclasses import asdict, dataclass
import fxn
from json import dumps, loads
from numpy import ndarray
from pathlib import Path
from PIL import Image
from platform import system
from typing import Any, AsyncIterator, Dict, List, Union
from uuid import uuid4

from .api import query
from .predictor import PredictorType
from .value import Value

@dataclass(frozen=True)
class Prediction:
    """
    Prediction.

    Members:
        id (str): Prediction ID.
        tag (str): Predictor tag.
        type (PredictorType): Prediction type.
        created (str): Date created.
    """
    id: str
    tag: str
    type: PredictorType
    created: str
    FIELDS = f"""
    id
    tag
    type
    created
    ... on CloudPrediction {{
        results {{
            data
            type
            shape
        }}
        latency
        error
        logs
    }}
    """

    @classmethod
    def create (
        cls,
        tag: str,
        raw_outputs: bool=False,
        return_binary_path: bool=True,
        data_url_limit: int=None,
        access_key: str=None,
        **inputs: Dict[str, Union[ndarray, str, float, int, bool, List, Dict[str, Any], Path, Image.Image, Value]],
    ) -> Union[CloudPrediction, EdgePrediction]:
        """
        Create a prediction.

        Parameters:
            tag (str): Predictor tag.
            raw_outputs (bool): Skip converting output values into Pythonic types.
            return_binary_path (bool): Write binary values to file and return a `Path` instead of returning `BytesIO` instance.
            data_url_limit (int): Return a data URL if a given output value is smaller than this size in bytes. Only applies to `CLOUD` predictions.
            access_key (str): Function access key.
            inputs (dict): Input values. Only applies to `CLOUD` predictions.

        Returns:
            CloudPrediction | EdgePrediction: Created prediction.
        """
        # Serialize inputs
        key = uuid4().hex
        inputs = { name: Value.from_value(value, name, key=key) for name, value in inputs.items() }
        inputs = [{ "name": name, **asdict(value) } for name, value in inputs.items()]
        # Query
        response = query(f"""
            mutation ($input: CreatePredictionInput!) {{
                createPrediction (input: $input) {{
                    {cls.FIELDS}
                }}
            }}""",
            { "input": { "tag": tag, "client": cls.__get_client(), "inputs": inputs, "dataUrlLimit": data_url_limit } },
            access_key=access_key
        )
        # Parse
        prediction = cls.__parse_prediction(response["createPrediction"])
        # Return
        return prediction
    
    @classmethod
    async def stream (
        cls,
        tag: str,
        raw_outputs: bool=False,
        return_binary_path: bool=True,
        data_url_limit: int=None,
        access_key: str=None,
        **inputs: Dict[str, Union[ndarray, str, float, int, bool, List, Dict[str, Any], Path, Image.Image, Value]],
    ) -> AsyncIterator[Union[CloudPrediction, EdgePrediction]]:
        """
        Create a streaming prediction.

        NOTE: This feature is currently experimental.

        Parameters:
            tag (str): Predictor tag.
            raw_outputs (bool): Skip converting output values into Pythonic types.
            return_binary_path (bool): Write binary values to file and return a `Path` instead of returning `BytesIO` instance.
            data_url_limit (int): Return a data URL if a given output value is smaller than this size in bytes. Only applies to `CLOUD` predictions.
            access_key (str): Function access key.
            inputs (dict): Input values. Only applies to `CLOUD` predictions.

        Returns:
            CloudPrediction | EdgePrediction: Created prediction.
        """
        # Serialize inputs
        key = uuid4().hex
        inputs = { name: asdict(Value.from_value(value, name, key=key)) for name, value in inputs.items() }
        # Request
        url = f"{fxn.api_url}/predict/{tag}?stream=true&rawOutputs=true&dataUrlLimit={data_url_limit}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_key or fxn.access_key}",
            "fxn-client": cls.__get_client()
        }
        async with ClientSession(headers=headers) as session:
            async with session.post(url, data=dumps(inputs)) as response:
                async for chunk in response.content.iter_any():
                    payload = loads(chunk)
                    # Check status
                    if response.status >= 400:
                        raise RuntimeError(payload.get("error"))
                    # Yield
                    prediction = cls.__parse_prediction(payload, raw_outputs=raw_outputs, return_binary_path=return_binary_path)
                    yield prediction

    @classmethod
    def __get_client (cls) -> str:
        id = system()
        if id == "Darwin":
            return "macos"
        if id == "Linux":
            return "linux"
        if id == "Windows":
            return "windows"
        raise RuntimeError(f"Function cannot make predictions on the {id} platform")
    
    @classmethod
    def __parse_prediction (
        cls,
        prediction: Dict[str, Any],
        raw_outputs: bool=False,
        return_binary_path: bool=True
    ) -> Union[CloudPrediction, EdgePrediction]:
        if not prediction:
            return None
        if "results" in prediction and prediction["results"] is not None:
            prediction["results"] = [Value(**value) for value in prediction["results"]]
            if not raw_outputs:
                prediction["results"] = [value.to_value(return_binary_path=return_binary_path) for value in prediction["results"]]
        prediction = CloudPrediction(**prediction) if prediction["type"] == PredictorType.Cloud else EdgePrediction(**prediction)
        return prediction

@dataclass(frozen=True)
class CloudPrediction (Prediction):
    """
    Cloud prediction.

    Members:
        results (list): Prediction results.
        latency (float): Prediction latency in milliseconds.
        error (str): Prediction error. This is `null` if the prediction completed successfully.
        logs (str): Prediction logs.
    """
    results: List[Value] = None
    latency: float = None
    error: str = None
    logs: str = None

@dataclass(frozen=True)
class EdgePrediction (Prediction):
    """
    Edge prediction.
    """