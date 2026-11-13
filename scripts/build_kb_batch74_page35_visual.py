#!/usr/bin/env python3
"""Batch74 independently viewed PDFKit-corrupted curriculum p35 flow *image*.

Stores only original paraphrased graph semantics and a local PNG SHA, never
uploads original copyrighted page pixels or declares teacher approval.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
from pathlib import Path
import json
import build_kb_batch74_unmarked_review as U

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/"docs/evaluation/KB_BATCH74_PAGE35_VISUAL_EVIDENCE.json"
PDF=Path("/private/tmp/stem-mentor-official-math-2020-batch51.pdf")
IMAGE=Path("/private/tmp/kb51_official_page_35.png")
PNG_SHA="bfcf80effdcf8289eb4eb1bc006bdad55476d0872a14c43a5ebff1232548b435"

NODES=[
 ("REAL_SCENARIO","呈现具体现实背景"),
 ("FORMULATE","明确可研究的问题"),
 ("CONSTRUCT","设定变量与假设并建立模型"),
 ("SOLVE","进行数学求解"),
 ("VALIDATE","将输出与现实条件核对"),
 ("RESULT","解释为实际结论"),
]
EDGES=[
 ("REAL_SCENARIO","FORMULATE","NEXT"),
 ("FORMULATE","CONSTRUCT","NEXT"),
 ("CONSTRUCT","SOLVE","NEXT"),
 ("SOLVE","VALIDATE","NEXT"),
 ("VALIDATE","CONSTRUCT","INVALID_REALITY_REVISE_MODEL"),
 ("VALIDATE","RESULT","CONSISTENT_WITH_REALITY"),
]

def digest(p:Path)->str:
    return sha256(p.read_bytes()).hexdigest()

def build():
    triage=json.loads(U.OUTPUT.read_text(encoding="utf8"))
    row=next(r for r in triage["records"] if r["segment_id"]=="KB73-P035-L001-021")
    assert row["classification"]=="GRAPHIC_VISUAL_INSPECTED_PENDING_TEACHER"
    assert len(NODES)==6 and len(EDGES)==6
    assert {k for k,_ in NODES}=={x for e in EDGES for x in e[:2]}
    assert len([e for e in EDGES if e[0]=="VALIDATE"])==2
    assert ("VALIDATE","CONSTRUCT","INVALID_REALITY_REVISE_MODEL") in EDGES
    assert ("VALIDATE","RESULT","CONSISTENT_WITH_REALITY") in EDGES
    return dict(
        schema_version="kb74-page35-image-attested-v1",
        printed_page=35,pdf_page_index=42,
        source_pdf_sha256=U.PDF_SHA,
        local_render_png_sha256=PNG_SHA,
        image_not_committed=True,
        source_segment_id=row["segment_id"],
        source_span_sha256=row["span_sha256"],
        extract_text_corrupted=True,
        evidence_type="AGENT_VISUAL_OBSERVATION_OF_MAC_PDF_RENDER",
        teacher_review="REVIEW_PENDING",
        official_atom_count=None,
        mathematics_proof_certification="NOT_APPLICABLE_WORKFLOW_DIAGRAM",
        student_publishable=False,
        nodes=[dict(node_id=k,original_paraphrase=label) for k,label in NODES],
        edges=[dict(source=a,target=b,condition=c) for a,b,c in EDGES],
        visual_check_summary="源图展示现实情境经问题提出、建模和求解进入结果检验；不合实际则回到建模，合乎实际则形成实际结果。项目释义而非原文复制。",
        teacher_follow_up="需核查此流程与后续选题/开题/做题/结题活动是否分别落在知识、实践能力或教学方法；不得按6个框图节点虚构6条官方知识原子。",
    )

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    p.add_argument("--verify-local-image",action="store_true")
    a=p.parse_args()
    if a.verify_local_image:
        assert PDF.is_file() and digest(PDF)==U.PDF_SHA,"original PDF missing/drift"
        assert IMAGE.is_file() and digest(IMAGE)==PNG_SHA,"source visual PNG drift"
    x=build()
    payload=json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True)+"\n"
    if a.check:assert TARGET.read_text(encoding="utf8")==payload
    else:TARGET.write_text(payload,encoding="utf8")
    print("Batch74 p35 original Mac rendered image checked" if a.verify_local_image else
          "Batch74 p35 reproducible structural visual record")
if __name__=="__main__":
    main()
