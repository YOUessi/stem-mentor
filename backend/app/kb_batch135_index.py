"""Review-only FTS for 22 new original manuscripts (Batch133–135).

Never use this provisional corpus to justify student responses: no external
authentication is implemented, so full draft text is not exposed via HTTP.
"""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path
from collections import Counter
import json
import re
import sqlite3

ROOT=Path(__file__).resolve().parents[2]
FILES=(
    ROOT/"knowledge/editorial_review/kb_batch133_six_core_lessons.json",
    ROOT/"knowledge/editorial_review/kb_batch134_eight_proof_lessons.json",
    ROOT/"knowledge/editorial_review/kb_batch135_eight_deep_lessons.json",
)
_TOKENS=re.compile(r"[\u3400-\u9fff]+|[a-z0-9_]+")
_CONTROLS=re.compile(r"[\u0000-\u001f]")
# Human-authored search aliases are index keywords, NOT syllabus assertions.
ALIASES={"c_tangent_domain":"正切 正切函数 tan 定义域", "a_limits_quotient":"商法则 数列 极限 商 取商",
         "c_quadratic_sign":"二次不等式 判别式 符号", "c_union_intersection":"集合 并集 交集 分配律",
         "c_period":"周期函数 最小正周期", "sc_arith_progression":"等差 数列 等差数列 求和",
         "sc_extreme_point":"极值 最值 导数 驻点", "sc_space_projection":"投影 空间 向量"}


class LocalEditorOnlyError(PermissionError):
    pass

def tokenize(raw: str) -> list[str]:
    words=[]
    for w in _TOKENS.findall(raw.lower().replace("²","2").replace("−","-")):
        if re.fullmatch(r"[\u3400-\u9fff]+",w):
            words.extend(w[i:i+2] for i in range(len(w)-1))
            if len(w)==1:words.append(w)
        elif len(w)<=40:
            words.append(w)
    return list(dict.fromkeys(words))[:80]

@lru_cache(maxsize=1)
def load():
    rows=[]
    for f in FILES:
        data=json.loads(f.read_text(encoding="utf-8"))
        if not isinstance(data,list):raise ValueError("Unexpected review manuscript container")
        rows+=data
    if len(rows)!=22 or len({r["id"] for r in rows})!=22:
        raise ValueError("Pilot manuscript count / duplicate IDs")
    for r in rows:
        candidate_id=r.get("source_candidate_id",r.get("candidate_id"))
        if not isinstance(candidate_id,str) or not candidate_id.startswith("kb133-proposal-"):
            raise ValueError("Missing source candidate")
        if r["teacher_review_status"]!="REVIEW_PENDING" or r["teacher_review_evidence"] is not None:
            raise ValueError("Unattested approval in review corpus")
        if r["teacher_solution_visibility"]!="TEACHER_ONLY" or r["student_authoritative"]:
            raise ValueError("Teacher solution visibility forged")
        if r.get("formal_proof_certified") or r.get("free_student_step_verified"):
            raise ValueError("Proof or student-step verification forged")
        if len(r["source_pdf_sha256"])!=64:raise ValueError("Missing source digest")
        span=r.get("source_span_sha256")
        if span is None:span=r["source_line_lock"]["span_sha256"]
        if not re.fullmatch("[0-9a-f]{64}",span):
            raise ValueError("Missing source span digest")
    return rows

@lru_cache(maxsize=1)
def _index():
    docs=load()
    connection=sqlite3.connect(":memory:",check_same_thread=False)
    connection.execute('CREATE VIRTUAL TABLE idx USING fts5(body, tokenize="unicode61")')
    for r in docs:
        # Only formal, domain, applicability and misconception summaries:
        # full worked solutions NEVER enter the FTS index.
        parts=[r["formal_definition_or_theorem"],r["notation_and_domain"],
               r["applicability_and_hypotheses"],r["typical_wrong_solution"]]
        slug=r["id"].replace("kb135-deep-","")
        tokens=tokenize(ALIASES.get(slug,"")+" "+" ".join(parts))
        connection.execute("INSERT INTO idx(body) VALUES(?)",(" ".join(tokens),))
    connection.commit()
    return connection

def public_coverage():
    """May appear in an unauthenticated API: aggregate-only, no teacher content."""
    rows=load()
    return {
        "scope":"BOUNDED_22_REVIEW_MANUSCRIPTS_NOT_OFFICIAL_CENSUS",
        "candidate_manuscripts":len(rows),
        "by_track":dict(sorted(Counter(r["course_track"] for r in rows).items())),
        "official_course_atom_denominator":None,
        "teacher_review_status":"REVIEW_PENDING",
        "teacher_approved":0,"student_authoritative":0,
        "general_proof_certified":0,
        "student_solution_or_teacher_manuscript_included":False,
    }

def editor_preview_search(query: str, *, scope: str="", track: str|None=None, limit: int=8):
    """Local editor preview only. The scope flag is an accidental misuse guard,
    NOT authentication. Never mount as an HTTP route or tool for students.
    """
    if scope!="EDITOR_LOCAL":
        raise LocalEditorOnlyError("No editor scope: review previews are not student evidence")
    if not isinstance(query,str) or not 1<=len(query.strip())<=160 or _CONTROLS.search(query):
        raise ValueError("Search query must be nonempty ≤160 chars without controls")
    if type(limit) is not int or not 1<=limit<=20:
        raise ValueError("Invalid result limit")
    docs=load()
    valid_tracks={r["course_track"] for r in docs}
    if track is not None and track not in valid_tracks:
        raise ValueError("Unrecognized provisional track")
    terms=tokenize(query)
    if not terms:return []
    expr=" OR ".join('"'+w+'"' for w in terms)
    records=_index().execute(
        "SELECT rowid,bm25(idx) FROM idx WHERE idx MATCH ? ORDER BY bm25(idx)",
        (expr,),
    ).fetchall()
    found=[]
    for row_id,score in records:
        row=docs[row_id-1]
        if track is not None and row["course_track"]!=track:continue
        found.append({
            "id":row["id"],
            "source_candidate_id":row.get("source_candidate_id",row.get("candidate_id")),
            "track":row["course_track"],
            "review_status":"REVIEW_PENDING",
            "condition_status":"CONDITIONS_NOT_ESTABLISHED",
            "student_publishable":False,
            "rank":round(float(score),6),
        })
        if len(found)>=limit:break
    return found

def student_evidence_lookup(query: str, *, limit: int=8):
    """Default-deny: no draft reaches student prompt, regardless of lexical hit."""
    if not isinstance(query,str) or not 1<=len(query.strip())<=160 or _CONTROLS.search(query):
        raise ValueError("Invalid query")
    if type(limit) is not int or not 1<=limit<=20:
        raise ValueError("Invalid limit")
    return {"status":"NO_APPROVED_EVIDENCE","candidates":[],
            "teacher_solution_exposed":False,"unverified_content_exposed":False}
