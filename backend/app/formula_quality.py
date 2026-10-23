"""Conservative OCR-output checks, not mathematical validation.

Only machine-checkable discrepancies are flagged. No warning (or clean syntax)
means *nothing* about algebraic correctness, student mastery or equivalence.
"""
from __future__ import annotations

import re


def braces_balanced(text: str) -> bool:
    """Check only curly braces. Interval parentheses may intentionally mismatch."""
    depth = 0
    i = 0
    while i < len(text):
        char = text[i]
        if char == "\\" and i + 1 < len(text) and text[i + 1] in "{}\\":
            i += 2
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth < 0:
                return False
        i += 1
    return depth == 0


def normalize_for_case_check(raw: str) -> str:
    # Avoid treating the Latin letter in English instructions as a math variable.
    return raw.strip().split(":", 1)[-1].strip()


def formula_quality_report(latex: str, ocr_source: str) -> dict:
    """Return actionable warnings while ALWAYS requiring explicit human review.

    Neither LaTeX syntactic sanity nor OCR source agreement is a math proof.
    """
    warnings: list[dict[str, str]] = []
    if not isinstance(latex, str) or not latex.strip():
        return {
            "state": "missing_formula",
            "warnings": [{
                "code": "empty_formula",
                "message": "未获得公式 LaTeX；请根据原图人工填写。",
            }],
            "mathematically_verified": False,
            "requires_human_review": True,
        }
    latex = latex[:1000]
    source = normalize_for_case_check(str(ocr_source)[:500])

    def add(code: str, message: str):
        if not any(x["code"] == code for x in warnings):
            warnings.append({"code": code, "message": message})

    if not braces_balanced(latex):
        add("unbalanced_braces", "LaTeX 花括号不配对，公式可能无法正确显示。")
    # These failure modes were observed with PP-FormulaNet on mixed printed lines.
    if "^" in source and re.search(r"\\(?:prime|wedge)\b", latex):
        add("power_vs_prime", "原文包含 ^，但结果含 prime/wedge，可能把幂次识别成撇号或逻辑运算。")
    if re.search(r"(?<![A-Za-z])x(?![A-Za-z])", source) and re.search(
            r"(?<![A-Za-z])X(?![A-Za-z])", latex):
        add("lowercase_x_vs_uppercase_X", "原始识别中有小写 x，结果出现大写 X，请检查变量大小写。")
    if re.search(r"(?<![A-Za-z])X(?![A-Za-z])", source) and re.search(
            r"(?<![A-Za-z])x(?![A-Za-z])", latex):
        add("uppercase_X_vs_lowercase_x", "原始识别中有大写 X，结果出现小写 x，请检查变量大小写。")
    if re.search(r"\\(?:because|therefore)\b", latex) and not any(
            x in source for x in ("∵", "∴", "因为", "所以", "因此")):
        add("unexpected_reasoning_symbol", "模型新增了推理符号，因为/所以标记需核对原图。")
    if re.search(r"\\(?:operatorname|text)\s*\{(?:Question|Given|Solve)\b",
                 latex, flags=re.IGNORECASE):
        add("instruction_leaked_into_formula", "题干说明文字似乎混入公式，请检查裁剪区域。")
    if r"\begin{array}" in latex or r"\begin{aligned}" in latex:
        add("extra_layout_wrapper", "结果增加了公式排版容器，需确认内容未被改变。")

    return {
        "state": "suspect" if warnings else "unverified",
        "warnings": warnings,
        "mathematically_verified": False,
        "requires_human_review": True,
    }
