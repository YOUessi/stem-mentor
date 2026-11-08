"""Batch42: 313 PROJECT-EDITORIAL targets with source-anchored draft / legacy crosswalk.
Never use project editorial candidates as official standards coverage denominators.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from collections import Counter, defaultdict
from pydantic import BaseModel, ConfigDict, Field, model_validator

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"docs/evaluation/KB_BATCH42_PROJECT_SCOPE_MATRIX.json"
NOTES=ROOT/"docs/evaluation/KB_BATCH42_PROJECT_SCOPE_GAPS.md"
TRACKS=("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")
PINS={
"kb31":("curriculum/highschool_math/k00_batch31_core_atomic_drafts.tsv","b541e15070fefefc05d9730fd8dbc0ba571a9110fa84452f537c31879399dcf3"),
"kb32":("curriculum/highschool_math/k00_batch32_compulsory_selective_editorial.tsv","a851ae8ece74bfb33be0f080c635af6df52252a73b8ff7536e0118a928a98140"),
"kb33":("curriculum/highschool_math/k00_batch33_elective_editorial.tsv","ad5b47d8aac24142ed5256eb238fad31256892c3ce65b2b6d70b512d99e5e7c4"),
"kb34":("knowledge/editorial_review/kb_batch34_seed.jsonl","de5d3c5f1f3635682398beb44a33aab590c92b944449bba3aa50c4450952cd8e"),
"kb35":("knowledge/editorial_review/kb_batch35_seed.jsonl","6ed09a6db38380f6e5ace3bcf9b41819a1141a0e83ff96efb2ab34eed4a3e97a"),
"kb37":("knowledge/editorial_review/kb_batch37_scope_repairs.jsonl","7cf991096365c704e859173187c72469c49ede251b865ed01ebef196c31283af"),
"kb38":("knowledge/editorial_review/kb_batch38_partial.jsonl","d28e04b16511017119c3560568d9d22f46af6f8eebc57185ee8bf7773f7e2be1"),
"kb39":("knowledge/editorial_review/kb_batch39_remaining.jsonl","5a6073a9d4c13b370a344a290102bde0b7eef4c1abf5b53d24ecfdd1b864f78b"),
"kb41":("knowledge/editorial_review/kb_batch41_core_selective.jsonl","f5a882c47c62ccc14b2b3c015840cbef3e8ad337a4080377d18735b01023462a"),
"kb42":("knowledge/editorial_review/kb_batch42_core_extension.jsonl","02e1847c2800187cf4c9b2fa288ee10abc16b5c5e9687b98f3b05cdbd3fad81d"),
}

class GateError(ValueError): pass

class Row(BaseModel):
    model_config=ConfigDict(extra="forbid")
    editorial_id: str = Field(min_length=8)
    source_batch: str
    source_line: int = Field(ge=1)
    source_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    printed_page: int = Field(ge=15,le=73)
    track: str
    topic: str
    kind: str
    optional_starred: bool
    goal: str = Field(min_length=9)
    direct_review_drafts: list[str]
    legacy_associations_unverified: list[str]
    editorial_status: str
    official_clause_verified: bool = False
    math_certified: bool = False
    teacher_approved: bool = False
    student_published: bool = False
    @model_validator(mode="after")
    def gate(self):
        if (self.official_clause_verified or self.math_certified or
            self.teacher_approved or self.student_published):
            raise GateError("Never certify a project editing hypothesis")
        expected="DRAFT_REVIEW_PENDING" if self.direct_review_drafts else (
            "LEGACY_ONLY_NOT_EQUIVALENT" if self.legacy_associations_unverified else "NO_DIRECT_LINK")
        if self.editorial_status!=expected or self.track not in TRACKS:
            raise GateError("Falsified status/track")
        if len(set(self.direct_review_drafts))!=len(self.direct_review_drafts):
            raise GateError("Duplicate draft ID")
        return self

def read_pinned(label, content=None):
    path,sha=PINS[label]
    content=(ROOT/path).read_bytes() if content is None else content
    if hashlib.sha256(content).hexdigest()!=sha: raise GateError("SHA drift "+label)
    return content.decode("utf-8")

def candidates(overrides=None):
    overrides=overrides or {}
    rows=[]; counts=Counter(); unique=set()
    for label in ("kb31","kb32","kb33"):
        for lineno,s in enumerate(read_pinned(label,overrides.get(label)).splitlines(),1):
            if not s.strip() or s.startswith("#"): continue
            bits=s.split("|")
            if label=="kb31" and len(bits)==5:
                page,topic,kind,star,goal=bits; track="COMPULSORY"
            elif label=="kb32" and len(bits)==6:
                page,track,topic,kind,star,goal=bits
            elif label=="kb33" and len(bits)==5:
                page,track,topic,kind,goal=bits; star="N"
            else: raise GateError("Bad frozen row "+label+":"+str(lineno))
            if not page.isdecimal(): raise GateError("Bad page")
            page=int(page)
            if (label=="kb31" and not 15<=page<=28 or
                label=="kb32" and not 29<=page<=50 or
                label=="kb33" and not 52<=page<=73):raise GateError("Source page mismatch")
            if (label=="kb31" and track!="COMPULSORY" or
                label=="kb32" and track not in TRACKS[:2] or
                label=="kb33" and track not in TRACKS[2:] or
                kind not in ("concept","theorem","method") or star not in ("N","Y")):
                raise GateError("Invalid source labels")
            # Batch33 IDs use a page-wide sequence across mixed-track transition pages.
            # In particular p64, p69, p73 do NOT reset the ordinal when track changes.
            groupkey=(label,page) if label=="kb33" else (label,track,page)
            counts[groupkey]+=1
            marker="C" if track=="COMPULSORY" else "S" if track=="SELECTIVE_COMPULSORY" else track[-1]
            identifier=f"{label.upper()}-{marker}-P{page:03d}-A{counts[groupkey]:03d}"
            if identifier in unique:raise GateError("Duplicate ID")
            unique.add(identifier)
            rows.append(dict(editorial_id=identifier,source_batch=label,source_line=lineno,
                source_sha256=PINS[label][1],printed_page=page,track=track,topic=topic,kind=kind,
                optional_starred=star=="Y",goal=goal))
    if len(rows)!=313:raise GateError("Candidate count drift")
    return rows

def authored():
    from .kb_batch34_review import Manuscript
    from .kb_batch35_review import Manuscript35
    from .kb_batch37_review import ScopeRepair
    from .kb_batch38_review import PartialRepair
    from .kb_batch39_review import RemainingPartial
    from .kb_batch41_core_review import staged
    from .kb_batch42_review import staged as staged42
    models={"kb34":Manuscript,"kb35":Manuscript35,"kb37":ScopeRepair,"kb38":PartialRepair,"kb39":RemainingPartial}
    found=defaultdict(list); ids=set()
    for label in ("kb34","kb35","kb37","kb38","kb39"):
        for line in read_pinned(label).splitlines():
            if not line.strip():continue
            d=models[label].model_validate(json.loads(line))
            if d.id in ids:raise GateError("Repeated manuscript ID")
            ids.add(d.id)
            if d.review.status!="REVIEW_PENDING" or d.review.reviewer_id or d.student_publishable:
                raise GateError("Forged approval")
            if d.teacher_solution_visibility!="TEACHER_ONLY" or d.proof_verification!="NOT_FORMALLY_CERTIFIED":
                raise GateError("Unsafe authored manuscript")
            found[d.editorial_candidate_id].append(d.id)
    for lesson,source in staged():
        if lesson.status!="REVIEW_PENDING" or lesson.student_publishable or lesson.teacher_solution_visibility!="TEACHER_ONLY":
            raise GateError("Unsafe core manuscript")
        found[lesson.goal].append("kb41:"+hashlib.sha256(json.dumps(lesson.model_dump(mode="json"),sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:16])
    if hashlib.sha256((ROOT/PINS["kb42"][0]).read_bytes()).hexdigest()!=PINS["kb42"][1]:
        raise GateError("Batch42 authored SHA drift")
    for eid,lesson,source in staged42():
        found[lesson.goal].append("kb42:"+eid)
    return found

def prior_links():
    from .deep_knowledge import lessons
    ids={l.id for l in lessons()}
    result=defaultdict(list)
    path=ROOT/"curriculum/highschool_math/k00_batch33_draft_associations.tsv"
    for s in path.read_text(encoding="utf-8").splitlines():
        if not s.strip() or s.startswith("#"):continue
        bits=s.split("|")
        if len(bits)!=3 or bits[1] not in ids or len(bits[2])<10:
            raise GateError("Orphan or malformed legacy association")
        result[bits[0]].append(bits[1])
    return result

def build():
    base=candidates(); drafts=authored(); legacy=prior_links()
    known={x["editorial_id"] for x in base}
    goals={x["goal"] for x in base if x["source_batch"] in ("kb31","kb32")}
    if set(drafts)-(known|goals) or set(legacy)-known:
        raise GateError("Orphan authored/legacy target")
    rows=[]
    for r in base:
        anchor=r["goal"] if r["source_batch"]!="kb33" else r["editorial_id"]
        direct=sorted(drafts.get(anchor,[])); old=sorted(set(legacy.get(r["editorial_id"],[])))
        status="DRAFT_REVIEW_PENDING" if direct else "LEGACY_ONLY_NOT_EQUIVALENT" if old else "NO_DIRECT_LINK"
        rows.append(Row.model_validate({**r,"direct_review_drafts":direct,
             "legacy_associations_unverified":old,"editorial_status":status}).model_dump(mode="json"))
    tracks={}
    for track in TRACKS:
        rr=[r for r in rows if r["track"]==track]
        tracks[track]=dict(project_candidate_count=len(rr),
            with_direct_review_draft=sum(bool(r["direct_review_drafts"]) for r in rr),
            legacy_association_only=sum(not r["direct_review_drafts"] and bool(r["legacy_associations_unverified"]) for r in rr),
            missing_direct_editorial_link=sum(r["editorial_status"]=="NO_DIRECT_LINK" for r in rr),
            official_atom_denominator=None,official_verified_coverage=None,teacher_approved=0,student_published=0)
        assert len(rr)==sum(tracks[track][q] for q in ("with_direct_review_draft","legacy_association_only","missing_direct_editorial_link"))
    return dict(schema_version="batch42-project-editorial-scope-v1",
        warning="313 is the incomplete project-authored editorial candidate set, NOT the official syllabus denominator or educational coverage.",
        source_standard_sha256="cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195",
        source_pins={k:dict(path=p,sha256=s) for k,(p,s) in PINS.items()},
        summary=dict(project_candidates=len(rows),direct_review_drafts=sum(bool(r["direct_review_drafts"]) for r in rows),
          legacy_only=sum(r["editorial_status"]=="LEGACY_ONLY_NOT_EQUIVALENT" for r in rows),
          missing_editorial_link=sum(r["editorial_status"]=="NO_DIRECT_LINK" for r in rows),
          teacher_approved=0,student_published=0,official_atom_denominator=None),
        tracks=tracks,rows=rows,
        safety="REVIEW_PENDING / TEACHER_ONLY / NOT_FORMALLY_CERTIFIED; no student-facing lesson content")

def render(data):
    lines=["# Batch42｜313 个项目课程编辑目标的可审计关联与缺口（非官方分母）","",
       "本报告将 Batch31/32/33 的项目原创候选逐条冻结，并与现有已编写教师审核稿、历史非认证讲义关联逐项连接。",
       "源行号、页码、SHA256 和精确目标均保留在同名 JSON 机器台账中。所有官方正式知识原子分母仍为 null。",
       "","|课程轨道|项目编辑目标|直接教师审核稿|仅历史未认证关联|无直接关联|官方分母|",
       "|---|---:|---:|---:|---:|---|"]
    for k in TRACKS:
        d=data["tracks"][k]
        lines.append(f"|{k}|{d['project_candidate_count']}|{d['with_direct_review_draft']}|{d['legacy_association_only']}|{d['missing_direct_editorial_link']}|未核实|")
    lines+=["", "## 下一批高优缺口（前 40 项示例）",""]
    for r in [r for r in data["rows"] if r["editorial_status"]=="NO_DIRECT_LINK"][:40]:
        lines.append(f"- {r['editorial_id']}，页 {r['printed_page']}：{r['goal']}")
    lines+=["", "## 不得误读","",
        "直接稿只是项目审核草稿，不能当作课标逐条等价或定理形式证明；历史工程讲义关联不等于具体编辑目标已经完整覆盖。",
        "本台账不存储教师的例题完整解答，也不得成为学生端 API 或外部模型的事实索引。课标仍需原版 PDF 逐页/逐条人工确认。",
        "审核状态一律 REVIEW_PENDING；无真实教师批准、无学生端深度内容发布。",""]
    return "\n".join(lines)

def write(*,check=False):
    data=build()
    j=json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True)+"\n"
    m=render(data)
    if check:
        if OUT.read_text(encoding="utf-8")!=j or NOTES.read_text(encoding="utf-8")!=m:
            raise GateError("Generated audit drift")
    else:
        OUT.write_text(j,encoding="utf-8")
        NOTES.write_text(m,encoding="utf-8")
    return data

def editor_goal_lookup(goal_id, *, scope=""):
    """Local editorial-only metadata, scope is not auth; do not expose via HTTP."""
    if scope!="EDITOR_LOCAL":raise PermissionError("Cannot retrieve unreviewed editorial goal")
    if not isinstance(goal_id,str) or len(goal_id)>60:raise ValueError("Invalid editorial id")
    for r in build()["rows"]:
        if r["editorial_id"]==goal_id:return r
    raise KeyError("Unknown goal")

def student_goal_lookup(goal_id):
    """Fail closed for all unapproved editorial draft content."""
    if not isinstance(goal_id,str) or len(goal_id)>60:raise ValueError("Invalid editorial id")
    return {"status":"NO_APPROVED_GOAL_EVIDENCE","candidates":[],
            "teacher_solution_exposed":False,"unverified_content_exposed":False}

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true")
    a=p.parse_args()
    print("PASS",write(check=a.check)["summary"])
