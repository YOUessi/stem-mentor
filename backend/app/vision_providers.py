"""Pluggable OCR/VLM providers. Image bytes are ephemeral; no upload persistence."""
import base64
import json
import os
import subprocess
import tempfile
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]
NATIVE_BIN = ROOT / "backend" / "native" / ".build" / "vision_ocr"


def run_native_ocr(png_bytes: bytes) -> tuple[list[dict], str]:
    """Run compiled Apple Vision CLI on macOS; never pretend text was recognized."""
    executable = Path(os.getenv("STEM_VISION_OCR_BIN", str(NATIVE_BIN)))
    if not executable.is_file():
        return [], "not_installed"
    try:
        with tempfile.TemporaryDirectory(prefix="mentor-ocr-") as temp:
            image_path = Path(temp) / "input.png"
            image_path.write_bytes(png_bytes)
            result = subprocess.run(
                [str(executable), str(image_path)], capture_output=True,
                text=True, timeout=25, check=False
            )
        if result.returncode:
            return [], "failed"
        payload = json.loads(result.stdout)
        lines = payload.get("lines", [])
        cleaned = []
        for line in lines[:200]:
            box = line.get("bbox", [])
            if not isinstance(box, list) or len(box) != 4:
                continue
            text = str(line.get("text", "")).strip()[:500]
            if not text:
                continue
            spans = []
            for segment in line.get("spans", [])[:5]:
                if not isinstance(segment, dict):
                    continue
                position = segment.get("bbox")
                label = str(segment.get("text", "")).strip()[:500]
                if not (isinstance(position, list) and len(position) == 4 and label):
                    continue
                try:
                    normalized = [max(0.0, min(1.0, float(v))) for v in position]
                except (ValueError, TypeError):
                    continue
                if normalized[2] <= 0 or normalized[3] <= 0:
                    continue
                spans.append({"text": label, "bbox": normalized})
            cleaned.append({
                "text": text,
                "confidence": max(0.0, min(1.0, float(line.get("confidence", 0.0)))),
                "bbox": [max(0.0, min(1.0, float(v))) for v in box],
                "spans": spans,
                "source": "apple_vision",
            })
        return cleaned, "ready"
    except (OSError, subprocess.TimeoutExpired, ValueError, json.JSONDecodeError):
        return [], "failed"


def call_formula_service(image_png: bytes, box: list[float]) -> tuple[dict | None, str]:
    """POST to optional PaddleOCR formula microservice (see services/formula_worker.py)."""
    endpoint = os.getenv("STEM_FORMULA_SERVICE_URL", "").strip()
    if not endpoint:
        return None, "not_configured"
    payload = {
        "image_base64": base64.b64encode(image_png).decode("ascii"),
        "model_hint": "PP-FormulaNet_plus-M",
    }
    try:
        token = os.getenv("STEM_FORMULA_SERVICE_TOKEN", "")
        headers = {"X-Formula-Token": token} if token else {}
        response = httpx.post(endpoint, json=payload, headers=headers,
                              timeout=httpx.Timeout(connect=2.0, read=22.0,
                                                    write=10.0, pool=2.0),
                              follow_redirects=False)
        response.raise_for_status()
        obj = response.json()
        latex = obj.get("latex", "")
        if not isinstance(latex, str) or not latex.strip():
            return None, "empty_result"
        return {
            "latex": latex.strip()[:1000],
            "source": "formula_ocr",
            "model": str(obj.get("model", "formula_service"))[:80],
            "bbox": box,
            "confidence": None if obj.get("confidence") is None
                else max(0.0, min(1.0, float(obj["confidence"]))),
            "verified": False,
        }, "ready"
    except (httpx.HTTPError, ValueError, KeyError, TypeError):
        return None, "failed"


def call_diagram_vlm(image_png: bytes) -> tuple[dict | None, str]:
    """Optional OpenAI-compatible image endpoint; only called with explicit UI opt-in."""
    endpoint = os.getenv("STEM_VLM_API_URL", "").strip()
    key = os.getenv("STEM_VLM_API_KEY", "").strip()
    model = os.getenv("STEM_VLM_MODEL", "").strip()
    if not (endpoint and key and model):
        return None, "not_configured"
    instructions = (
        "观察这张中学数学题图片。只返回 JSON 对象，键为 entities(字符串数组), "
        "relations(数组，每项含 type、objects 字符串数组、explanation)。"
        "仅报告图片中视觉可见的图元、标记；不得把看起来垂直、平行、相等或 "
        "按比例绘制的关系当成题目给定事实。没有证据就返回空数组。"
        "不求解数学题，不写推导，不推断隐含条件。"
    )
    payload = {
        "model": model,
        "temperature": 0,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": instructions},
                {"type": "image_url", "image_url": {
                    "url": "data:image/png;base64," + base64.b64encode(image_png).decode("ascii")
                }},
            ],
        }],
    }
    try:
        response = httpx.post(
            endpoint, json=payload, timeout=35, follow_redirects=False,
            headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
        )
        response.raise_for_status()
        raw_content = response.json()["choices"][0]["message"]["content"]
        if isinstance(raw_content, list):
            raw_content = "".join(
                item.get("text", "") for item in raw_content if isinstance(item, dict)
            )
        if not isinstance(raw_content, str):
            return None, "invalid_result"
        cleaned = raw_content.strip()
        fence = chr(96) * 3
        if cleaned.startswith(fence):
            cleaned = cleaned.split("\n", 1)[-1].rsplit(fence, 1)[0].strip()
        parsed = json.loads(cleaned)
        if not isinstance(parsed, dict):
            return None, "invalid_result"
        entities = [str(x)[:100] for x in parsed.get("entities", [])[:30]
                    if isinstance(x, str)]
        relations = []
        for relation in parsed.get("relations", [])[:30]:
            if not isinstance(relation, dict):
                continue
            relations.append({
                "type": str(relation.get("type", ""))[:70],
                "objects": [str(x)[:100] for x in relation.get("objects", [])[:8]],
                "explanation": str(relation.get("explanation", ""))[:240],
                "source": "vlm_observation",
                "status": "observed_unverified",
                "is_given": False,
            })
        return {"entities": entities, "relations": relations,
                "source": "vlm_observation", "verified": False}, "ready"
    except (httpx.HTTPError, json.JSONDecodeError, ValueError, KeyError, IndexError, TypeError):
        return None, "failed"
