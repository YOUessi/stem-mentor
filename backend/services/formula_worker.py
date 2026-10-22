"""Optional GPU formula worker. Install paddlepaddle + paddleocr separately.

Run on a trusted host only:
  uvicorn backend.services.formula_worker:app --host 127.0.0.1 --port 18931
The main app calls POST /recognize with a cropped image, never a whole notebook.
"""
import base64
import binascii
import io
import os
from functools import lru_cache

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from PIL import Image, UnidentifiedImageError

app = FastAPI(title="STEM Mentor Formula OCR", docs_url=None, redoc_url=None)


class FormulaRequest(BaseModel):
    image_base64: str = Field(min_length=10, max_length=12_000_000)
    model_hint: str = Field(default="PP-FormulaNet_plus-M", max_length=80)


@lru_cache(maxsize=1)
def get_model():
    from paddleocr import FormulaRecognition
    return FormulaRecognition(model_name="PP-FormulaNet_plus-M")


@app.post("/recognize")
def recognize(payload: FormulaRequest, x_formula_token: str | None = Header(default=None)):
    expected = os.environ.get("STEM_FORMULA_SERVICE_TOKEN", "")
    if expected and x_formula_token != expected:
        raise HTTPException(401, "Unauthorized")
    try:
        raw = base64.b64decode(payload.image_base64, validate=True)
        if len(raw) > 8 * 1024 * 1024:
            raise ValueError("too large")
        with Image.open(io.BytesIO(raw)) as im:
            if im.width * im.height > 12_000_000:
                raise ValueError("too many pixels")
            rgb = im.convert("RGB")
            import numpy as np
            matrix = np.asarray(rgb)
    except (ValueError, OSError, UnidentifiedImageError, binascii.Error, Image.DecompressionBombError) as exc:
        raise HTTPException(422, "Invalid image") from exc
    try:
        results = get_model().predict(input=matrix, batch_size=1)
        first = next(iter(results), None)
        data = first.json if first is not None else {}
        latex = data.get("res", {}).get("rec_formula", "")
        return {"latex": latex, "model": "PP-FormulaNet_plus-M",
                "confidence": None, "math_verified": False}
    except Exception as exc:
        raise HTTPException(503, "Formula model inference failed") from exc
