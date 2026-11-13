#!/usr/bin/env python3
"""Build eight substantive teacher-only DeepLessons and immutable evidence audit."""
from __future__ import annotations
import argparse,json,sys,re
from collections import Counter
from hashlib import sha256
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"backend")]
from kb_batch110_lesson_authoring import UNITS
from build_kb_batch110_scope import build as source_build,serialize,TRACKS
from app.deep_knowledge import DEEP_DIR,DeepLesson,curriculum
PACK=DEEP_DIR/"batch110_exponent_inference.json"
AUDIT=ROOT/"docs/evaluation/KB_BATCH110_LESSONS_AUDIT.json"
MD=ROOT/"docs/evaluation/KB_BATCH110_LESSONS.md"
DEPENDENCIES={1:[0],2:[1],3:[2],5:[4]}

def require(condition,msg):
    if not condition:raise ValueError(msg)

def build(units=UNITS):
    source=source_build()
    anchors={r["key"]:r for r in source["candidates"]}
    maps={r["id"]:r for r in curriculum()}
    require(len(units)==8,"batch110 must contain eight independently authored lessons")
    keys=[r["source_key"] for r in units]
    require(len(set(keys))==8 and set(keys)<=set(anchors),"duplicate/unknown source")
    earlier=[]
    for path in sorted(DEEP_DIR.glob("*.json")):
        if path==PACK: continue
        version=re.match(r"batch(\d+)",path.name)
        if version and int(version.group(1))>110:continue
        earlier.extend(json.loads(path.read_text(encoding="utf8")))
    prior_ids=[r["id"] for r in earlier]
    require(len(set(prior_ids))==len(prior_ids),"duplicate historical lesson IDs")
    lessons=[];links=[]
    for idx,u in enumerate(units):
        kind=u["kind"];cid=u["curriculum_id"]
        require(cid in maps and kind in {"theorem","concept","method"},
                "unknown mapping/type")
        require(len(u["statement"])>=50 and len(u["assumptions"])>=2
                and len(u["notation"])>=2 and len(u["prereqs"])>=2,
                "missing mathematical definition, domain, notation or prerequisite")
        require(len(u["reasoning"])>=3,"missing explanation or theorem proof")
        if kind=="theorem":
            require(all(isinstance(x,(tuple,list)) and len(x)==2
                and all(isinstance(v,str) and len(v)>=18 for v in x)
                for x in u["reasoning"]),"unjustified theorem step")
        else:
            require(all(isinstance(x,str) and len(x)>=20 for x in u["reasoning"]),
                    "missing concept/method reasoning")
        require(len(u["negative"])==3 and all(len(x)>=20 for x in u["negative"]),
                "missing specific misconception, counterexample or explanation")
        require(len(u["examples"])==2 and all(len(e["steps"])>=2 and
                len(e["question"])>=15 and len(e["answer"])>=10 and
                len(e["check"])>=15 for e in u["examples"]),
                "two fully checked worked teacher examples required")
        require(len(u["hints"])==3 and len(set(u["hints"]))==3 and
                all(len(x)>=14 for x in u["hints"]),"three-stage hint ladder missing")
        require(len(u["near"])>=20 and len(u["far"])>=20,
                "near+far transfer insufficient")
        src=anchors[u["source_key"]]
        require(src["math_witness"]["status"]=="FINITE_EXACT_INSTANCE_ONLY",
                "source has no independent bounded math instance")
        require(src["track_hint"]==("COMPULSORY" if idx<4 else "ELECTIVE_A"),
                "source lesson track mismatch")
        require((idx<4)==(maps[cid]["level"]=="必修"),
                "engineering level differs from source compulsory/elective")
        deps=DEPENDENCIES.get(idx,[])
        require(all(0<=d<idx for d in deps),"invalid/cyclic prerequisite edge")
        ident=f"math.hs.batch110.{idx+1:02d}"
        doc=dict(
          id=ident,curriculum_ids=[cid],kind=kind,title=u["title"],version="1.0.0",
          notation=u["notation"],prerequisites=u["prereqs"],
          prerequisite_lesson_ids=[f"math.hs.batch110.{x+1:02d}" for x in deps],
          definition=u["statement"] if kind=="concept" else None,
          statement=u["statement"],assumptions=u["assumptions"],
          proof_steps=[dict(claim=x,reason=y) for x,y in u["reasoning"]]
                       if kind=="theorem" else [],
          rationale_steps=u["reasoning"] if kind!="theorem" else [],
          boundaries=u["assumptions"],
          counterexamples=[dict(false_claim=u["negative"][0],
                                example=u["negative"][1],explanation=u["negative"][2])],
          misconceptions=[dict(error=u["negative"][0],why_wrong=u["negative"][2],
             repair_question="请指出该解法遗漏的条件，并通过代入、反例或边界解释如何修正。")],
          worked_examples=u["examples"],hint_ladder=u["hints"],
          transfer=dict(near=u["near"],far=u["far"]),
          provenance=dict(kind="PROJECT_AUTHORED",permission="PROJECT_AUTHORED",
             curriculum_standard="普通高中数学课程标准（2017年版2020年修订）",
             standard_url="https://www.pep.com.cn/xw/zt/rjwy/gzkb2020/202205/P020220517519489596282.pdf",
             author_role="PROJECT_AUTHOR"),
          review=dict(status="REVIEW_PENDING",reviewer_id=None,
                      reviewed_at=None,review_record=None),
          teacher_solution_visibility="TEACHER_ONLY")
        DeepLesson.model_validate(doc)
        lessons.append(doc)
        links.append(dict(lesson_id=ident,source_key=u["source_key"],
           source_candidate_id=src["id"],source_printed_page=src["page"],
           source_pdfkit_sha256=src["source_page_pdfkit_sha256"],
           source_track_hint=src["track_hint"],engineering_curriculum_id=cid,
           engineering_level=maps[cid]["level"],official_math_atom_id=None,
           teacher_approved=False,general_proof_certified=False))
    require(not {d["id"] for d in lessons}&set(prior_ids),"duplicate lesson ID across batches")
    report=dict(
      batch=110,status="REVIEW_PENDING",visibility="TEACHER_ONLY",
      number_of_new_deep_drafts=len(lessons),new_teacher_worked_examples=16,
      new_no_answer_hint_levels=24,new_near_and_far_transfer_tasks=16,
      new_counterexamples=8,new_prerequisite_id_edges=sum(len(x["prerequisite_lesson_ids"]) for x in lessons),
      new_proof_step_candidates=sum(len(x["proof_steps"]) for x in lessons),
      new_finite_math_witnesses=8,
      lesson_type_counts=dict(Counter(x["kind"] for x in lessons)),
      historical_deep_lessons=len(earlier),all_deep_lessons=len(earlier)+len(lessons),
      editorial_source_crosswalk=links,
      official_seven_track_atom_denominators={t:None for t in TRACKS},
      teacher_approvals=0,student_authoritative_releases=0,
      general_proof_certificates=0,arbitrary_student_steps_certified=0,
      source_author_sha256=sha256((ROOT/"scripts/kb_batch110_lesson_authoring.py").read_bytes()).hexdigest(),
      scope_audit_sha256=sha256(serialize(source).encode()).hexdigest(),
      limitations=[
       "Finite cases do not certify theorem proof or justify promotion to APPROVED.",
       "Eight lesson drafts do not establish a global seven-track curricular denominator.",
       "Teacher worked examples are not available to independent-challenge student retrieval.",
       "A source page's elective-A topic is not converted into compulsory coverage by a legacy mapping."])
    return lessons,report

def markdown(lessons,audit):
    parts=["# Batch110｜指数函数、对数、参数估计与回归八份深度讲义（候审）","",
           "这八份是原创教师候审内容；任何数学定理一般证明仍需教师逐步核验。","",
           "学生自主挑战仅可用提示，不得检索教师解答。",""]
    for doc,link in zip(lessons,audit["editorial_source_crosswalk"]):
        parts.extend([f"## {doc['id']}｜{doc['title']}","",
          f"课标来源候选：{link['source_candidate_id']}；工程映射：{link['engineering_curriculum_id']}，并非官方原子认定。","",
          "**陈述或定义：** "+doc["statement"],"",
          "**适用条件：** "+"；".join(doc["assumptions"]),"",
          "**符号：** "+"；".join(doc["notation"]),"",
          "**先修：** "+"；".join(doc["prerequisites"]),""])
        for n,x in enumerate(doc["proof_steps"],1):
            parts.extend([f"**证明第{n}步：** {x['claim']}","**依据：** "+x["reason"],""])
        for n,x in enumerate(doc["rationale_steps"],1):
            parts.extend([f"**解释第{n}步：** {x}",""])
        c=doc["counterexamples"][0]
        parts.extend(["**易错主张：** "+c["false_claim"],"",
                      "**具体反例：** "+c["example"],"",
                      "**边界说明：** "+c["explanation"],""])
        for n,e in enumerate(doc["worked_examples"],1):
            parts.extend([f"### 教师例题{n}",e["question"],""])
            parts.extend([f"{k}. {s}" for k,s in enumerate(e["steps"],1)])
            parts.extend(["","**教师答案：** "+e["answer"],"",
                         "**校验：** "+e["check"],""])
        parts.extend(["**三层不剧透提示：** "+"；".join(doc["hint_ladder"]),"",
                      "**近迁移：** "+doc["transfer"]["near"],"",
                      "**远迁移：** "+doc["transfer"]["far"],""])
    return "\n".join(parts).rstrip()+"\n"

def main():
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true")
    args=p.parse_args();docs,audit=build()
    for path,data in ((PACK,serialize(docs)),(AUDIT,serialize(audit)),(MD,markdown(docs,audit))):
        if args.check:require(path.read_text(encoding="utf8")==data,"generated artifact drift "+str(path))
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(data,encoding="utf8")
    print("Batch110 lessons PASS",len(docs),audit["lesson_type_counts"],
          audit["new_proof_step_candidates"])
if __name__=="__main__":main()
