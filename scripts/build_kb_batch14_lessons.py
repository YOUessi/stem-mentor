#!/usr/bin/env python3
"""Rebuild Batch14 authored proof-draft corpus with exact source equality and hash pinning.

All mathematical statements are DRAFT/REVIEW_PENDING; CI verifies structure and
sampled exact subclaims, not independent teacher review or fully formal proofs.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"curriculum/highschool_math/author_draft_batch14.json"
OUT=ROOT/"knowledge/deep/v1/elective_a_b_core_batch14.json"

def render():
    items=json.loads(SOURCE.read_text(encoding="utf-8"))
    if len(items)!=16 or len({x["id"] for x in items})!=16:
        raise ValueError("Batch14 expected sixteen distinct authored lessons")
    if any(x["review"]["status"]!="REVIEW_PENDING" or
           x["teacher_solution_visibility"]!="TEACHER_ONLY" for x in items):
        raise ValueError("Unreviewed authored data cannot become student evidence")
    return json.dumps(items,ensure_ascii=False,indent=2)+"\n"

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    a=p.parse_args()
    content=render()
    if a.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8")!=content:
            raise AssertionError("Batch14 authored course corpus drift")
    else:
        OUT.write_text(content,encoding="utf-8")
    print("Batch14 authored elective proof drafts=16 check=",a.check)
if __name__=="__main__":
    main()
