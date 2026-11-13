#!/usr/bin/env python3
"""Editorial review of 42 real syllabus anchors across compulsory/selective/electives A-D.

Original paraphrases, not copied source text. Teacher atomization remains pending.
Optional Mac-only --verify-local-source checks PDF SHA and every PDFKit line SHA.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
AUTHOR=ROOT/"curriculum/highschool_math/kb_batch81_semantic_authoring.json"
SOURCE=ROOT/"curriculum/highschool_math/kb_batch80_review_queue.json"
PARTS=ROOT/"curriculum/highschool_math/k00_batch51_pdfkit_page_fingerprints.json"
OUT=ROOT/"docs/evaluation/KB_BATCH81_SEMANTIC_TRIAGE.json"
MD=ROOT/"docs/evaluation/KB_BATCH81_SEMANTIC_TRIAGE.md"
LOCAL_PDF=Path.home()/"Library/Caches/stem-mentor-source-review/highschool_math_standard_2020.pdf"
LOCAL_LINES=Path("/private/tmp")
ROLES=("CURRICULUM_HEADING","MIXED_CLAUSE","MATHEMATICAL_REQUIREMENT",
       "COMPETENCY_REQUIREMENT","APPLICATION_CONTEXT")
PDF_SHA="cc4d3a20daa09f5185037e93fbacd58f7df1147392e3dae4bf261c3700ba4195"
SOURCE_QUEUE_SHA256="f9c2f95a7cd6a49383769b88762eee79f6366ff744a19d865f6be3674e28653e"
EQUIVALENCE_PAIRS=(
 ("KB80-A052-L009","KB80-A058-L008","HEADING_LEVEL_SIMILARITY_ONLY"),
 ("KB80-A052-L010","KB80-A058-L009","RELATED_LIMIT_INSTANCES_NO_EQUIVALENCE_PROOF"),
 ("KB80-A038-L011","KB80-A052-L010","RELATED_SEQUENCES_DIFFERENT_LEARNING_SCOPE"),
)
def require(ok,message):
 if not ok:raise ValueError(message)
def load(p):return json.loads(p.read_text(encoding="utf8"))
def dump(obj):return json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+"\n"

def build(auth=None,upstream=None,verify_local_source=False):
 auth=load(AUTHOR) if auth is None else auth
 upstream=load(SOURCE) if upstream is None else upstream
 require(auth["schema_version"]=="kb81-42-source-semantic-editorial-proposals-v1"
      and auth["teacher_review"]=="REVIEW_PENDING"
      and auth["copyright_policy"]=="ORIGINAL_PARAPHRASES_NO_SOURCE_PASSAGE",
      "Invalid editorial source/version claim")
 require(upstream["source_pdf_sha256"]==PDF_SHA and upstream["official_atom_denominator"] is None,
      "Original curriculum source lineage changed")
 require(sha256(dump(upstream).encode("utf8")).hexdigest()==SOURCE_QUEUE_SHA256,
      "Frozen 428-anchor source queue was modified")
 src={r["review_id"]:r for r in upstream["anchor_review_queue"]}
 rows=auth["records"]
 require(len(rows)==42 and len({r["review_id"] for r in rows})==42,
         "Expected exactly 42 unique provisional Mac source reviews")
 require(all(r["semantic_role_provisional"] in ROLES for r in rows),
         "Unrecognized semantic review role")
 if verify_local_source:
  require(LOCAL_PDF.is_file() and sha256(LOCAL_PDF.read_bytes()).hexdigest()==PDF_SHA,
          "Original official PDF unavailable or SHA mismatch")
  pages={int(k) for r in rows for k in [src[r["review_id"]]["printed_page"]]}
  p=load(PARTS)
  official={int(s["printed_page"]):s["pdfkit_text_sha256"]
            for s in p["pages"]}
  for page in pages:
   raw=(LOCAL_LINES/f"kb56_page_{page}.txt").read_bytes()
   require(sha256(raw).hexdigest()==official[page],
           "PDFKit page text drift: "+str(page))
 results=[]
 for item in rows:
  sid=item["review_id"]
  require(sid in src,"Unknown source anchor: "+sid)
  origin=src[sid]
  require(item["track"]==origin["track"],"Cross-track source error")
  role=item["semantic_role_provisional"]
  candidates=item["possible_math_units_for_teacher_split"]
  require(type(candidates) is list and len(candidates)==len(set(candidates)),
          "Duplicate candidate semantics")
  if role=="CURRICULUM_HEADING":
   require(candidates==[],"Headings cannot silently create mathematics atoms")
  elif role in ("MATHEMATICAL_REQUIREMENT", "MIXED_CLAUSE"):
   require(1<=len(candidates)<=5,"Mathematical clauses must name provisional split proposals")
  else:
   # A competence requirement or application-context heading can carry no
   # standalone math atom. Inventing one would inflate the curriculum census.
   require(len(candidates)<=5,"Excessive candidate split proposals")
  require(len(item["original_editorial_paraphrase"])>=16,
          "Incomplete original source-specific editorial paraphrase")
  require(item["teacher_confirmed"] is False and item["student_publishable"] is False
          and item["official_atom_count"] is None
          and item["cross_track_equivalence"]=="NOT_ADJUDICATED",
          "Editorial triage forged as official approval")
  if verify_local_source:
   pg=origin["printed_page"];line=origin["pdfkit_line"]
   txt=(LOCAL_LINES/f"kb56_page_{pg}.txt").read_text(encoding="utf8").splitlines()
   require(sha256(txt[line-1].encode()).hexdigest()==origin["source_line_sha256"],
           "Source row SHA drift "+sid)
  results.append({
   "review_id":sid,"source_pdf_sha256":PDF_SHA,"source_line_sha256":origin["source_line_sha256"],
   "source_page_pdfkit_sha256":origin["source_page_pdfkit_sha256"],
   "source_parent_segment":origin["parent_segment"],
   "printed_page":origin["printed_page"],"pdfkit_line":origin["pdfkit_line"],
   "track":origin["track"],"source_structure_kind":origin["kind"],
   "semantic_role_provisional":role,
   "original_editorial_paraphrase":item["original_editorial_paraphrase"],
   "possible_math_units_for_teacher_split":candidates,
   "equivalence_review":"PENDING_INDEPENDENT_MATH_AND_SOURCE_REVIEW",
   "editorial_triaged":True,"official_atom_count":None,"teacher_review":"REVIEW_PENDING",
   "teacher_approved":False,"student_publishable":False,
  })
 for x,y,label in EQUIVALENCE_PAIRS:
  require(x in {z["review_id"] for z in results}
    and y in {z["review_id"] for z in results},"Orphan cross-track relation")
  require(label!="MATHEMATICALLY_EQUIVALENT","No unsupported equivalence certification")
 bytrack=Counter(r["track"] for r in results)
 byrole=Counter(r["semantic_role_provisional"] for r in results)
 require(sum(bytrack.values())==42 and sum(byrole.values())==42,
         "Cross-track source semantic conservation failed")
 return {
  "schema_version":"kb81-42-source-semantic-triage-v1",
  "source_pdf_sha256":PDF_SHA,
  "source_review_anchor_count":428,
  "selected_independently_paraphrased_anchors":42,
  "remaining_without_manual_semantic_paraphrase":386,
  "teacher_full_page_atomizations":0,
  "teacher_approved":0,"student_published":0,
  "official_curriculum_atom_denominator":None,
  "provisional_candidate_splits_not_deduplicated":sum(len(r["possible_math_units_for_teacher_split"]) for r in results),
  "by_track":{k:bytrack[k] for k in ("COMPULSORY","SELECTIVE_COMPULSORY","ELECTIVE_A","ELECTIVE_B","ELECTIVE_C","ELECTIVE_D","ELECTIVE_E")},
  "by_provisional_role":dict(sorted(byrole.items())),
  "cross_track_links":[{"left":x,"right":y,"relationship":label,
     "mathematical_equivalence_certified":False} for x,y,label in EQUIVALENCE_PAIRS],
  "rows":results,"all_semantics_subject_to_independent_teacher_review":True,
 }

def markdown(x):
 lines=["# Batch81 | 42 syllabus-source semantic review proposals","",
  "**42/428 anchor obligations now have source-specific original editorial paraphrases** across six tracks.",
  "This is a *project editorial proposal*, not a teacher-reviewed official atomic denominator.",
  "The source PDF was verified on Mac with SHA "+PDF_SHA+"; the repo contains NO copied PDF passages.",
  "Selected input page/line identifiers and their SHA witnesses are machine-auditable.","",
  "| Track | Editorially paraphrased anchors |",
  "|---|---:|"]
 lines += [f"| {k} | {v} |" for k,v in x["by_track"].items()]
 lines += ["","| Source line role | Count |","|---|---:|"]
 lines += [f"| {k} | {v} |" for k,v in x["by_provisional_role"].items()]
 lines += ["","* Source structural heading != official math atom.",
  "* Identical topic labels in elective A/B != proven mathematical equivalence.",
  "* Elective E needs an actual school course inventory; 0 anchored lines is NOT 0 official atoms.",
  "* Every draft remains REVIEW_PENDING; 0 full-page teacher atomization and 0 published student chapters.",""]
 return "\n".join(lines)

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--check",action="store_true")
 p.add_argument("--verify-local-source",action="store_true")
 args=p.parse_args()
 d=build(verify_local_source=args.verify_local_source)
 for path,content in ((OUT,dump(d)),(MD,markdown(d))):
  if args.check:require(path.exists() and path.read_text()==content,"Semantic output drift: "+str(path))
  else:path.write_text(content)
 print("Batch81 semantic proposals: 42 of 428 source anchors; teacher review zero")
if __name__=="__main__":main()
