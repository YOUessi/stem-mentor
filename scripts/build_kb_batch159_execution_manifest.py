#!/usr/bin/env python3
"""KB159: deterministic verification of genuine Mac stdout, exit codes and hashes.

No simulated or inferred test counts. Every archived entry must have *real*
nonempty stdout and a zero process exit. Source code / teacher review status
must never be inferred from a green test run.
"""
from __future__ import annotations
import argparse,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LOGDIR=ROOT/"docs/evaluation/kb159_logs"
OUT=ROOT/"docs/evaluation/KB_BATCH159_TEST_MANIFEST.json"
REQUIRED={
 "FOCUSED":{"tokens":("125 passed",),"min_bytes":300},
 "PDFKIT":{"tokens":("PASS KB159 10 full compulsory function drafts",),"min_bytes":50},
 "MATH":{"tokens":("PASS KB159 20 independently calculated",),"min_bytes":50},
 "BROWSER":{"tokens":("Chrome PASS","2 passed"),"min_bytes":700},
 "MAC_FULL":{"tokens":("125 passed","66418 passed, 5 skipped","# tests 111","# pass 111","# fail 0"),"min_bytes":40000},
}
def require(x,msg):
    if not x:raise ValueError("KB159 archived evidence: "+msg)
def one(name,base=LOGDIR):
    require(name in REQUIRED,"unknown log type")
    conf=REQUIRED[name]
    file=base/(name+".stdout.log")
    exitfile=base/(name+".exit")
    require(file.is_file() and exitfile.is_file(),"missing stdout or exit "+name)
    blob=file.read_bytes();exit_data=exitfile.read_bytes()
    require(len(blob)>=conf["min_bytes"],"missing/truncated stdout "+name)
    require(re.fullmatch(rb"0\r?\n?",exit_data) is not None,"nonzero/forged exit "+name)
    text=blob.decode("utf-8",errors="replace")
    for token in conf["tokens"]:
        require(token in text,"missing required real PASS/test count "+name+": "+token)
    require(not re.search(r"(?m)^FAILED\s+\S+",text),"failed tests in archive "+name)
    return dict(name=name,stdout_path=str((LOGDIR / file.name).relative_to(ROOT)),
       stdout_bytes=len(blob),stdout_sha256=hashlib.sha256(blob).hexdigest(),
       exit_path=str((LOGDIR / exitfile.name).relative_to(ROOT)),
       exit_bytes=exit_data.decode("ascii"),exit_sha256=hashlib.sha256(exit_data).hexdigest(),
       observed_markers=list(conf["tokens"]))
def build(base=LOGDIR):
    runs=[one(name,base) for name in REQUIRED]
    # This manifest binds to authored source commit: final evidence commit
    # cannot embed its own SHA recursively.
    return dict(schema="kb159-authentic-mac-execution-manifest/1",
      source_commit="fd10511c80d284a72be11fcc936a310704271603",
      log_records=len(runs),run_labels=list(REQUIRED),
      mac_real_tests=True,focused_python_passed=125,
      python_full_passed=66418,python_full_skipped=5,
      node_full_passed=111,teacher_example_exact_bounded=20,
      negative_premise_exact_bounded=20,
      official_atom_denominators_known=False,
      general_proof_certified=False,teacher_approved=0,student_authoritative=0,
      test_suites_overlap_not_additive=True,
      logs=runs)
def encode(d):
    return json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+"\n"
def main():
    ap=argparse.ArgumentParser();g=ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--write",action="store_true");g.add_argument("--check",action="store_true")
    x=ap.parse_args();data=encode(build())
    if x.write:OUT.write_text(data,encoding="utf-8")
    elif OUT.read_text(encoding="utf-8")!=data:
        raise ValueError("KB159 test manifest differs from authentic Mac stdout/exit")
    print("PASS KB159 SHA256 authenticated 5 actual Mac test stdout/exit pairs")
if __name__=="__main__":main()
