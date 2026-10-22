"""Loopback-only formula OCR worker with a single serialized Paddle GPU model.

Launch only on 127.0.0.1, put it behind an authenticated SSH tunnel.
The model is loaded lazily. Never store images or log student image contents.
"""
from __future__ import annotations

import base64
import binascii
import io
import os
import secrets
import threading
import time
from functools import lru_cache

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from PIL import Image, UnidentifiedImageError

app = FastAPI(title="STEM Mentor Math Formula OCR", docs_url=None, redoc_url=None)
_MODEL_LOCK = threading.Lock()
_MODEL_NAME = "PP-FormulaNet_plus-M"
_MAX_IMAGE_BYTES = 8 * 1024 * 1024
_MAX_PIXELS = 12_000_000


class FormulaRequest(BaseModel):
    image_base64: str = Field(min_length=10, max_length=12_000_000)
    model_hint: str = Field(default=_MODEL_NAME, max_length=80)


@lru_cache(maxsize=1)
def get_model():
    from paddleocr import FormulaRecognition
    device = os.getenv("STEM_FORMULA_DEVICE", "gpu:0")
    return FormulaRecognition(model_name=_MODEL_NAME, device=device)


@app.get("/health")
def health():
    return {
        "status": "ready" if get_model.cache_info().currsize else "not_loaded",
        "model_name": _MODEL_NAME,
        "model_loaded": bool(get_model.cache_info().currsize),
        "authentication_required": True,
    }


@app.post("/recognize")
def recognize(payload: FormulaRequest,
              x_formula_token: str | None = Header(default=None)):
    expected = os.environ.get("STEM_FORMULA_SERVICE_TOKEN", "")
    if not expected:
        raise HTTPException(503, "Formula service token not configured")
    if not x_formula_token or not secrets.compare_digest(expected, x_formula_token):
        raise HTTPException(401, "Unauthorized")
    try:
        raw = base64.b64decode(payload.image_base64, validate=True)
        if len(raw) > _MAX_IMAGE_BYTES:
            raise ValueError("image too large")
        with Image.open(io.BytesIO(raw)) as image:
            if image.width * image.height > _MAX_PIXELS:
                raise ValueError("too many pixels")
            # decoding may raise for truncated/corrupted files
            rgb = image.convert("RGB")
            import numpy as np
            matrix = np.asarray(rgb)
    except (ValueError, OSError, UnidentifiedImageError, binascii.Error,
            Image.DecompressionBombError) as exc:
        raise HTTPException(422, "Invalid image") from exc

    try:
        with _MODEL_LOCK:
            started = time.perf_counter()
            predictions = get_model().predict(input=matrix, batch_size=1)
            first = next(iter(predictions), None)
            data = first.json if first is not None else {}
            latex = data.get("res", {}).get("rec_formula", "")
            elapsed = round((time.perf_counter() - started) * 1000, 2)
        if not isinstance(latex, str) or not latex.strip():
            raise ValueError("Empty formula response")
        return {
            "latex": latex,
            "model": _MODEL_NAME,
            "confidence": None,
            "elapsed_ms": elapsed,
            "math_verified": False,
        }
    except Exception as exc:
        # Do not leak internal stacktraces or model/cache paths to HTTP clients.
        raise HTTPException(503, "Formula model inference failed") from exc
