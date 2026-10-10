# AI Engineer — Production Patterns

Reference patterns for the ai-engineer agent. Load when implementing model serving or
inference endpoints that need these specific patterns.

## Production Model Server

```python
import logging
from dataclasses import dataclass, field
from datetime import datetime, UTC
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)


@dataclass(slots=True, kw_only=True)
class PredictionResult:
    """
    Result of a model prediction.

    Attributes:
        label: Predicted class label.
        confidence: Prediction confidence score.
        latency_ms: Inference latency in milliseconds.
        model_version: Version of the model used.
        timestamp: Prediction timestamp.
    """

    label: str
    confidence: float
    latency_ms: float
    model_version: str
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(tz=UTC)
    )


class ModelServer:
    """
    Serve ML model predictions via API.

    Attributes:
        model_path: Path to the serialized model.
        model_version: Semantic version of the loaded model.
    """

    def __init__(
        self,
        model_path: Path,
        model_version: str,
    ) -> None:
        """
        Initialize the model server.

        Args:
            model_path: Path to the serialized model file.
            model_version: Semantic version string.

        Raises:
            FileNotFoundError: If the model file does not exist.
        """

        if not model_path.exists():
            error_message = (
                f"[ERROR] Model file not found: {model_path}."
            )
            logger.error(error_message)
            raise FileNotFoundError(error_message)

        self.model_path = model_path
        self.model_version = model_version
        self._model = self._load_model(model_path)
        logger.info(
            "[INFO] Model %s loaded from %s.",
            model_version,
            model_path,
        )

    def predict(
        self, features: np.ndarray
    ) -> PredictionResult:
        """
        Run inference on input features.

        Args:
            features: Input feature array.

        Returns:
            Prediction result with label, confidence,
            and latency.

        Raises:
            ValueError: If features array is empty.
        """

        if features.size == 0:
            error_message = "[ERROR] Empty features array."
            logger.error(error_message)
            raise ValueError(error_message)

        start = datetime.now(tz=UTC)
        output = self._model.predict(features)
        elapsed_ms = (
            datetime.now(tz=UTC) - start
        ).total_seconds() * 1000

        result = PredictionResult(
            label=str(output["label"]),
            confidence=float(output["confidence"]),
            latency_ms=elapsed_ms,
            model_version=self.model_version,
        )
        logger.info(
            "[INFO] Prediction: %s (%.2f%%) in %.1fms.",
            result.label,
            result.confidence * 100,
            result.latency_ms,
        )
        return result
```

## FastAPI Inference Endpoint

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="ML Inference API")


class PredictRequest(BaseModel):
    """
    Inference request payload.

    Attributes:
        features: List of numeric feature values.
    """

    features: list[float] = Field(
        ..., min_length=1, description="Input features."
    )


class PredictResponse(BaseModel):
    """
    Inference response payload.

    Attributes:
        label: Predicted label.
        confidence: Confidence score.
        model_version: Model version used.
    """

    label: str
    confidence: float
    model_version: str


@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest) -> PredictResponse:
    """
    Run model inference on input features.

    Args:
        request: Prediction request with features.

    Returns:
        Prediction response with label and confidence.
    """

    try:
        result = model_server.predict(
            np.array(request.features).reshape(1, -1)
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return PredictResponse(
        label=result.label,
        confidence=result.confidence,
        model_version=result.model_version,
    )
```
