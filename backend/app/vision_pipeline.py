"""Image normalization, conservative OCR routing, and auditable question draft.

No model output is a mathematical fact until confirmed by the learner.
"""
import io
import re
from collections import Counter

from PIL import Image, ImageOps, UnidentifiedImageError

from . import vision_providers as providers

MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_PIXELS = 20_000_000
MAX_EDGE = 2200
Image.MAX_IMAGE_PIXELS = MAX_PIXELS

FORMULA_MARKS = re.compile(
    r"[=≤≥≠≈±×÷√∫∑∏∂∞∠∥⊥πθΔ△∈∉∪∩∴∵^_{}]"
    r"|(?:[0-9]+[ ]*/[ ]*[0-9]+)|(?:[a-zA-Z][²³⁴⁵⁶⁷⁸⁹⁰¹])"
)
DIAGRAM_MARKS = ("如图", "图中", "图示", "函数图像", "统计图", "坐标系", "示意图")


class VisionInputError(ValueError):
    pass


def normalize_image(raw: bytes) -> tuple[bytes, tuple[int, int]]:
    """Reject oversized/corrupt formats; strip metadata; bound image size."""
    if not raw:
        raise VisionInputError("请选择一张题目图片")
    if len(raw) > MAX_FILE_BYTES:
        raise VisionInputError("图片超过 8 MB 限制")
    try:
        with Image.open(io.BytesIO(raw)) as original:
            if original.format not in {"JPEG", "PNG", "WEBP"}:
                raise VisionInputError("仅支持 JPEG、PNG、WebP 图片")
            if original.width * original.height > MAX_PIXELS:
                raise VisionInputError("图片像素超过限制，请先裁剪")
            image = ImageOps.exif_transpose(original)
            image = image.convert("RGB")
            image.thumbnail((MAX_EDGE, MAX_EDGE), Image.Resampling.LANCZOS)
            dims = image.size
            buf = io.BytesIO()
            image.save(buf, "PNG", optimize=False)
            return buf.getvalue(), dims
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise VisionInputError("无法读取图片或图片已损坏") from exc


def is_formula_candidate(text: str) -> bool:
    return bool(FORMULA_MARKS.search(text))


def crop_region(png: bytes, bbox: list[float]) -> bytes:
    """Crop one OCR region in pixel space with context margin."""
    with Image.open(io.BytesIO(png)) as im:
        w, h = im.size
        x, y, rw, rh = bbox
        pad_x, pad_y = 0.02, 0.02
        left = int(max(0, (x - pad_x) * w))
        top = int(max(0, (y - pad_y) * h))
        right = int(min(w, (x + rw + pad_x) * w))
        bottom = int(min(h, (y + rh + pad_y) * h))
        if right <= left or bottom <= top:
            raise VisionInputError("OCR 区域坐标无效")
        cropped = im.crop((left, top, right, bottom))
        output = io.BytesIO()
        cropped.save(output, "PNG")
        return output.getvalue()


def analyze_image(raw: bytes, *, diagram_present: bool = False,
                  allow_cloud_vlm: bool = False,
                  allow_formula_service: bool = False) -> dict:
    image_png, (width, height) = normalize_image(raw)
    lines, local_status = providers.run_native_ocr(image_png)
    if not isinstance(lines, list):
        lines, local_status = [], "failed"
    # A limited number of suspicious lines get dedicated formula OCR.
    formula_candidates = [
        (i, line) for i, line in enumerate(lines[:200])
        if is_formula_candidate(line.get("text", "")) or
        (line.get("confidence", 1) < 0.5 and
         bool(re.search(r"[0-9a-zA-Z]", line.get("text", ""))))
    ][:12]
    expressions: list[dict] = []
    formula_statuses = []
    for i, line in formula_candidates:
        box = line.get("bbox", [0, 0, 1, 1])
        try:
            cropped = crop_region(image_png, box)
        except (VisionInputError, ValueError, TypeError):
            formula_statuses.append("invalid_region")
            continue
        expression, status = (providers.call_formula_service(cropped, box)
                              if allow_formula_service else (None, "skipped_no_consent"))
        formula_statuses.append(status)
        expressions.append({
            "id": f"expr-{i+1}",
            "latex": expression["latex"] if expression else "",
            "raw_text": line.get("text", ""),
            "bbox": box,
            "source": expression["source"] if expression else "awaiting_formula_ocr",
            "model": expression.get("model") if expression else None,
            "confidence": expression.get("confidence") if expression else None,
            "needs_review": True,
            "verified": False,
        })

    stem = "\n".join(str(line.get("text", "")).strip() for line in lines
                     if line.get("text", "")).strip()
    visual_needed = diagram_present or any(x in stem for x in DIAGRAM_MARKS)
    low_confidence = any(line.get("confidence", 1) < 0.55 for line in lines)
    diagram = {"entities": [], "relations": [], "source": "not_analyzed",
               "verified": False}
    if visual_needed and allow_cloud_vlm:
        candidate, vlm_status = providers.call_diagram_vlm(image_png)
        if candidate:
            diagram = candidate
    elif visual_needed:
        vlm_status = "skipped_no_consent"
    else:
        vlm_status = "skipped_not_needed"
    uncertain = []
    if local_status != "ready":
        uncertain.append("local_ocr_unavailable")
    if not stem:
        uncertain.append("question_text_missing")
    if formula_candidates and any(s != "ready" for s in formula_statuses):
        uncertain.append("formula_latex_not_verified")
    if visual_needed and vlm_status != "ready":
        uncertain.append("diagram_requires_manual_review")
    if low_confidence:
        uncertain.append("low_confidence_text")
    if vlm_status == "ready":
        uncertain.append("visual_relations_are_observations_not_givens")
    return {
        "pipeline": "HYBRID_VISION_V015",
        "image": {"width": width, "height": height,
                  "stored_on_server": False, "metadata_retained": False},
        "stem": stem,
        "lines": lines,
        "expressions": expressions,
        "diagram": diagram,
        "evidence": [
            {"id": f"line-{i+1}", "source": "apple_vision",
             "text": line["text"], "bbox": line["bbox"],
             "confidence": line["confidence"], "status": "observed_unverified"}
            for i, line in enumerate(lines)
        ],
        "routing": {
            "local_ocr": local_status,
            "formula_candidates": len(formula_candidates),
            "formula_consent": allow_formula_service,
            "formula_ocr": (dict(Counter(formula_statuses)) if formula_statuses
                            else {"not_needed": 1}),
            "visual_review_recommended": visual_needed,
            "vlm": vlm_status,
            "cloud_consent": allow_cloud_vlm,
        },
        "uncertain_fields": uncertain,
        "confirmed": False,
        "math_verified": False,
        "needs_human_review": True,
    }
