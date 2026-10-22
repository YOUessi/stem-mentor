"""HTTP interface to recognition draft and explicit human confirmation."""
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from starlette.concurrency import run_in_threadpool
from pydantic import BaseModel, Field, model_validator

from .vision_pipeline import VisionInputError, analyze_image, MAX_FILE_BYTES

router = APIRouter()


@router.post("/api/vision/recognize")
async def recognize_question(
    file: UploadFile = File(...),
    diagram_present: bool = Form(False),
    allow_cloud_vlm: bool = Form(False),
    allow_formula_service: bool = Form(False),
):
    try:
        raw = await file.read(MAX_FILE_BYTES + 1)
        return await run_in_threadpool(
            analyze_image, raw, diagram_present=diagram_present,
            allow_cloud_vlm=allow_cloud_vlm,
            allow_formula_service=allow_formula_service)
    except VisionInputError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    finally:
        await file.close()


class MathExpressionCorrection(BaseModel):
    latex: str = Field(min_length=1, max_length=800)


class QuestionConfirmation(BaseModel):
    stem: str = Field(min_length=1, max_length=3500)
    expressions: list[MathExpressionCorrection] = Field(default_factory=list, max_length=12)

    @model_validator(mode="after")
    def require_text(self):
        if not self.stem.strip():
            raise ValueError("需要人工确认后的题干")
        return self


@router.post("/api/vision/confirm")
def confirm_question(payload: QuestionConfirmation):
    # A user acknowledgement, not an assertion of OCR or mathematical truth.
    stem = payload.stem.strip()
    formulas = [e.latex.strip() for e in payload.expressions]
    result = stem + ("\n\n公式补充（由用户确认）：\n" +
                     "\n".join(formulas) if formulas else "")
    if len(result) > 4000:
        raise HTTPException(422, "题目过长，请适当删减到 4000 字符以内")
    return {
        "confirmed": True,
        "confirmed_by": "explicit_user_action",
        "math_verified": False,
        "diagram_verified": False,
        "custom_problem": result,
        "can_create_simulation_session": True,
    }
