"""Batch41: source-anchored ORIGINAL compulsory/selective review content, never approved.

Important: editorial goals are project-authored paraphrases of the 2017/2020 standard,
not verified official atom IDs, nor a completed syllabus denominator.
No student retrieval endpoint is exposed here.
"""
from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "knowledge/editorial_review/kb_batch41_core_selective.jsonl"
PDF_SHA_2020 = "cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195"
SEED_SHA = "f5a882c47c62ccc14b2b3c015840cbef3e8ad337a4080377d18735b01023462a"
EDITORIAL_FILES = {
 "kb31": (ROOT / "curriculum/highschool_math/k00_batch31_core_atomic_drafts.tsv",
          "b541e15070fefefc05d9730fd8dbc0ba571a9110fa84452f537c31879399dcf3"),
 "kb32": (ROOT / "curriculum/highschool_math/k00_batch32_compulsory_selective_editorial.tsv",
          "a851ae8ece74bfb33be0f080c635af6df52252a73b8ff7536e0118a928a98140"),
}
REPORT = ROOT / "docs/evaluation/KB_BATCH41_CORE_SELECTIVE_REVIEW_AUDIT.json"
MANUSCRIPT = ROOT / "docs/evaluation/KB_BATCH41_CORE_SELECTIVE_MANUSCRIPTS.md"

class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

class Derivation(Strict):
    statement: str = Field(min_length=5)
    reason: str = Field(min_length=5)

class ErrorRecord(Strict):
    false_claim: str = Field(min_length=3)
    counterexample: str = Field(min_length=12)
    why_invalid: str = Field(min_length=8)

class Exercise(Strict):
    question: str = Field(min_length=6)
    steps: list[str] = Field(min_length=2, max_length=2)
    answer: str = Field(min_length=1)
    check: str = Field(min_length=3)

class Lesson(Strict):
    goal: str = Field(min_length=12)
    title: str = Field(min_length=5)
    statement: str = Field(min_length=22)
    conditions: list[str] = Field(min_length=1)
    derivation: list[Derivation] = Field(min_length=3, max_length=3)
    error: ErrorRecord
    examples: list[Exercise] = Field(min_length=2, max_length=2)
    hints: list[str] = Field(min_length=3, max_length=3)
    near: str = Field(min_length=6)
    far: str = Field(min_length=6)
    prerequisites: list[str] = Field(min_length=1)
    status: Literal["REVIEW_PENDING"] = "REVIEW_PENDING"
    teacher_solution_visibility: Literal["TEACHER_ONLY"] = "TEACHER_ONLY"
    proof_status: Literal["NOT_FORMALLY_CERTIFIED"] = "NOT_FORMALLY_CERTIFIED"
    source_license: Literal["PROJECT_AUTHORED"] = "PROJECT_AUTHORED"
    student_publishable: Literal[False] = False
    approved_reviewer: None = None

    @model_validator(mode="after")
    def check_content(self):
        if len(set(self.hints)) != 3 or any(len(s) < 7 for s in self.hints):
            raise ValueError("Specific graduated hints required")
        if len({x.question for x in self.examples}) != 2:
            raise ValueError("Two distinct exercises required")
        if len({x.statement for x in self.derivation}) != 3:
            raise ValueError("Distinct reasoning stages required")
        return self

def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def source_goals():
    """Returns unique page-anchored editorial evidence. Not an official atomic syllabus."""
    result = {}
    for label, (path, pin) in EDITORIAL_FILES.items():
        if _sha(path) != pin:
            raise ValueError("Editorial source drift: "+label)
        for no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line or line.startswith("#"):
                continue
            bits = line.split("|")
            if label == "kb31":
                if len(bits)!=5: raise ValueError("Invalid KB31 source row")
                page, topic, kind, optional, goal = bits
                track = "COMPULSORY"
            else:
                if len(bits)!=6: raise ValueError("Invalid KB32 source row")
                page, track, topic, kind, optional, goal = bits
            if goal in result:
                raise ValueError("Duplicate project editorial goal")
            if kind not in {"concept","theorem","method"} or optional not in {"N","Y"}:
                raise ValueError("Unexpected source classification")
            result[goal] = dict(source=label, source_line=no,
                                printed_page=int(page), track=track,
                                topic=topic, kind=kind, optional=optional,
                                original_goal=goal)
    return result

def validate_seed(raw: str, *, check_pin: bool=True):
    if check_pin and hashlib.sha256(raw.encode("utf-8")).hexdigest() != SEED_SHA:
        raise ValueError("Original authored content SHA drift")
    sources = source_goals()
    rows = []
    seen = set()
    for line in raw.splitlines():
        if not line.strip(): continue
        data=json.loads(line)
        # Source JSONL is compact curated editorial input; normalize tuples into typed schema.
        data["derivation"]=[{"statement":claim,"reason":reason} for claim,reason in data["derivation"]]
        claim,example,reason=data["error"]
        data["error"]={"false_claim":claim,"counterexample":example,"why_invalid":reason}
        data["examples"]=[{"question":question,"steps":[step1,step2],"answer":answer,"check":check}
                          for question,step1,step2,answer,check in data["examples"]]
        lesson = Lesson.model_validate(data)
        if lesson.goal not in sources: raise ValueError("Unanchored editorial goal")
        if lesson.goal in seen: raise ValueError("Duplicate editorial goal")
        seen.add(lesson.goal)
        rows.append((lesson,sources[lesson.goal]))
    if len(rows)!=29 or len(seen)!=29:
        raise ValueError("Expected exactly 29 nonduplicate complete manuscripts")
    if sum(s["track"]=="SELECTIVE_COMPULSORY" for _,s in rows)!=4:
        raise ValueError("Selective compulsory composition drift")
    return tuple(rows)

@lru_cache(maxsize=1)
def staged():
    return validate_seed(SOURCE.read_text(encoding="utf-8"))

def student_retrieval_projection():
    return {"status":"UNPUBLISHED_REVIEW_ONLY","review_pending":len(staged()),
            "approved":0,"student_published":0,
            "student_documents":[],"teacher_solutions_exposed":[],
            "official_atomic_denominators": {x:None for x in
             ("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")}}

def render():
    lines=["# Batch41｜29 篇必修/选择性必修原创教师审核稿",
           "",
           "以下 29 个项目自编课程编辑目标已编制内容审核稿，但目标与原课标具体条款的逐项等价性未获教师确认。",
           "来源仅为仓库中 Batch31/32 的逐页编辑候选；非官方知识原子分母，全部 REVIEW_PENDING、TEACHER_ONLY、NOT_FORMALLY_CERTIFIED。",
           "定义/方法的三步内容是定义解释或合法性推导，不应冒充待证明的定理；定理的证明也未经正式认证。", ""]
    for number,(d,src) in enumerate(staged(),1):
        lines += [f"## {number:02}. {d.title}｜{src['track']}｜课标印刷页 {src['printed_page']}",
                  f"**项目原创编辑目标：** {d.goal}",
                  f"**知识类型：** {src['kind']}；**编辑来源：** {src['source']} 第 {src['source_line']} 行（非官方原子编号）。",
                  f"**正式表述：** {d.statement}",
                  "**使用前提：** "+"；".join(d.conditions),
                  "**前置知识：** "+"；".join(d.prerequisites),
                  "**逐步推理与依据：**"]
        for i,s in enumerate(d.derivation,1):
            lines.append(f"{i}. {s.statement} **依据：** {s.reason}")
        lines += [f"**典型错法：** {d.error.false_claim}",
                  f"**具体反例/失效例：** {d.error.counterexample}",
                  f"**失效原因：** {d.error.why_invalid}",
                  "**例题（教师侧完整解答，学生自主挑战不可检索）：**"]
        for i,ex in enumerate(d.examples,1):
            lines += [f"- **例题{i}：** {ex.question}",
                      f"  - 第一步：{ex.steps[0]}",
                      f"  - 第二步：{ex.steps[1]}",
                      f"  - 答案：{ex.answer}；核验：{ex.check}"]
        lines += ["**三级渐进提示（必须由教学策略按级别控制）：**"]
        for i,h in enumerate(d.hints,1):
            lines.append(f"{i}. {h}")
        lines += [f"**近迁移：** {d.near}",f"**远迁移：** {d.far}",
                  "**审核门禁：** REVIEW_PENDING / TEACHER_ONLY / NOT_FORMALLY_CERTIFIED / student_publishable=false", ""]
    return "\n".join(lines).rstrip()+"\n"

WITNESS_LINKS = {
    "set_complement_mask":"全集与补集的论域前提",
    "amgm_square_gap":"两数 AM–GM 与取等条件",
    "inequality_scale":"不等式同乘的符号门槛",
    "quadratic_roots_count":"二次方程的判别式",
    "radical_fraction_domain":"根式与分母定义域的交集",
    "log_product_powers":"对数乘积法则的双真数限制",
    "classical_probability":"古典概型的有限等可能门槛",
    "event_union":"概率并集的容斥公式",
    "event_independent":"独立与互斥的严格区别",
    "weighted_population_mean":"分层均值的权重来自总体比例",
    "sample_variance_unbiased_2":"样本方差分母必须声明",
    "arithmetic_term":"等差数列通项公式及索引条件",
    "arithmetic_sum":"等差数列配对求和定理",
    "geometric_sum":"等比数列前n项和的分支",
    "complex_division":"复数除法的共轭与分母非零",
    "plane_normal_dot":"线面垂直判定的两相交直线前提",
    "square_increase":"导数正值推出严格递增",
}

def audit():
    rows=[]
    for idx,(d,src) in enumerate(staged(),1):
        encoded=json.dumps(d.model_dump(mode="json"),sort_keys=True,ensure_ascii=False,separators=(",",":"))
        matched_ops=sorted(op for op,title in WITNESS_LINKS.items() if title==d.title)
        rows.append({"id":f"math.hs.editorial.batch41.{src['track'].lower()}.{idx:03d}",
                     "lesson_sha256":hashlib.sha256(encoded.encode("utf-8")).hexdigest(),
                     "source":src,"title":d.title,"status":d.status,
                     "math_certified":False,"official_clause_alignment_verified":False,
                     "teacher_approved":False,"student_publishable":False,
                     "worked_examples":len(d.examples),"hint_levels":len(d.hints),
                     "finite_case_witness_operators":matched_ops,
                     "has_general_proof_certification":False,
                     "counterexamples":1,"near_far_tasks":2})
    if len(WITNESS_LINKS)!=17 or len({v for v in WITNESS_LINKS.values()})!=17:
        raise ValueError("Batch41 finite math witness coverage drift")
    if sum(bool(row["finite_case_witness_operators"]) for row in rows)!=17:
        raise ValueError("Unmatched exact math witness to curated lesson")
    counts={k:sum(x["source"]["track"]==k for x in rows) for k in ("COMPULSORY","SELECTIVE_COMPULSORY")}
    return {"source_original_pdf_sha256_prior_audit_only":PDF_SHA_2020,
            "authored_seed_sha256":_sha(SOURCE),
            "editorial_source_shas":{k:v[1] for k,v in EDITORIAL_FILES.items()},
            "summary":{"draft_manuscripts":29,"by_track":counts,
                       "teacher_examples":58,"counterexamples":29,"hint_levels":87,
                       "near_far_transfers":58,"finite_case_witnessed_units":17,
                       "units_without_independent_finite_case":12,"teacher_approved":0,
                       "student_published":0,"official_atomic_denominators":student_retrieval_projection()["official_atomic_denominators"],
                       "historical_deep_drafts_unchanged":287},
            "records":rows,"student_projection":student_retrieval_projection()}

def build(*, check=False):
    targets={REPORT:json.dumps(audit(),ensure_ascii=False,sort_keys=True,indent=2)+"\n",MANUSCRIPT:render()}
    for path, expected in targets.items():
        if check:
            if not path.exists() or path.read_text(encoding="utf-8")!=expected:
                raise ValueError("Generated output drift: "+str(path))
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(expected,encoding="utf-8")

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true")
    build(check=p.parse_args().check)
