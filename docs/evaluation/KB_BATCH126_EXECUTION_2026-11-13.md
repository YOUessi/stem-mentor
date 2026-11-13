# STEM Mentor — Batch126 Mac acceptance, source-context audit and frozen test evidence

**Date:** 2026-11-13. **Development and tests:** authorized MacBook Air exclusively; Tang not used.

- Local source commit: `74ec6e3b2e33c78b44c0bd7e85c2a2b2ae019ea8`; source tree: `95bafcf52bbf425fb920e56904ea6d46b1f113ac`.
- GitHub Draft PR #151: https://github.com/YOUessi/stem-mentor/pull/151 . The GitHub source commit differs from the local commit ID because of native Git-object sync; compare the **tree**, not only commit hashes. The final report and logs are attached later as a fast-forward evidence commit.
- Issue scope: https://github.com/YOUessi/stem-mentor/issues/17 and #18–#27. Teacher sign-off is still required and must not be simulated.

## Concrete work

- **K00/K01 source evidence**: 26 manually interpreted, source-line-locked context dossiers on the *authorized Mac PDFKit source*. Exactly 20 previously weak/absent-anchor editorial candidates and 6 residual numbered clauses; all feature page, line range, PDF sha256, per-line and span SHA-256, scope track, a project-authored interpretation and a remaining mathematical/source caveat. No copyright syllabus paragraph is reproduced in the repo.
- **K00 honesty gates**: among 239 historical editorial candidates, only these 20 were reviewed at line-context level this batch; 219 are untouched. Do not claim 26/26 means full syllabus coverage. Historical 135 unlinked cues still require adjudication, including 6 numbered clauses whose record does not grant official atom status.
- **K07 finite exact checks**: 12 SymPy/precise-arithmetic witness types with an admissible and a degenerate/invalid case each, **24 finite witnesses** (not universal formal theorem proofs). Includes non-collinear points, distinct planes, bisection sign checks, positive probability weights, zero-variance, logarithm base, induction examples and vector-plane conditions.
- **K08/K09 review safety**: mutation tests reject forged teacher signatures, approval, student authority, official atom IDs, source-line hashes, track/page changes and invented denominator counts. Candidate content remains `REVIEW_PENDING` and teacher-only.
- **Source limitations**: the page 35 modeling loop needs image-level verification; elective C clause continued from page 64 to 65 needs both pages; starred mathematical induction is not automatically a universal selective-compulsory requirement. An attested PDFKit text line is not a teacher certificate.

## Mac final tests (genuinely executed)

| Suite | Result | Exit |
|---|---|---|
| Batch126 focused negative and mathematical witness tests | **89 passed** | 0 |
| `scripts/mac_check.sh`: entire backend Python | **66,293 passed, 5 skipped, 1 external deprecation warning** | 0 |
| Node suite inside `mac_check.sh` | **111 passed, 0 failed** | included in full EXIT 0 |
| `scripts/mac_browser_check.sh` Chrome/Playwright | **pass**, browser pytest **2 passed** | 0 |

The 89 targeted tests overlap the full suite, therefore do not add them to 66,293. Touch/pen testing is browser emulation, not actual iPad hardware. No model API required or invoked.

## Raw log SHA-256 and exact exit evidence

- `docs/evaluation/logs/KB_BATCH126_FOCUS_PRE_GATE.exit`: 2 bytes, SHA-256 `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa`
- `docs/evaluation/logs/KB_BATCH126_FOCUS_PRE_GATE.log`: 179 bytes, SHA-256 `6e97d7732e3f3ba1ef2dffbda5a2298c21efa11271e0adb3270e71157fc9e91a`
- `docs/evaluation/logs/KB_BATCH126_MAC_BROWSER_FINAL.exit`: 2 bytes, SHA-256 `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa`
- `docs/evaluation/logs/KB_BATCH126_MAC_BROWSER_FINAL.log`: 2442 bytes, SHA-256 `92377e5e6f41717f9f9a81023d390eaf938e13a86561b5797ae59341296e335c`
- `docs/evaluation/logs/KB_BATCH126_MAC_CHECK_FINAL.exit`: 2 bytes, SHA-256 `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa`
- `docs/evaluation/logs/KB_BATCH126_MAC_CHECK_FINAL.log`: 122511 bytes, SHA-256 `247af536d887b4e2b131941fc3c1e3dc5174f40e3b3289923ea3425fd731a5bf`

## Remaining scope and next development batch

- Seven tracks' **official full semantic atom denominators = UNKNOWN**. `teacher_approved=0`, `student_authoritative=0`. Neither 113 engineering mappings nor 239 editorial proposals is the official denominator.
- Historical 172 prereq relationships, 538 unverified proof steps and 10 unresolved mathematical conflicts remain open (this batch did not fix them).
- Next: classify the 219 untouched weak candidates with exact numbered requirement spans and cross-page scope; map activities to problem families rather than forcing theorem atom IDs; formulate candidate per-track denominator with exclusion/duplicate records; expand complete teacher-review math lessons and test student-agent retrieval safety.
- Protect Mac main and the two pre-existing evaluation result snapshot modifications. No forced update, no merge to main, no student data and no full copyrighted syllabus text uploaded.

## Reproduction

```bash
.venv/bin/python scripts/build_kb_batch126_context_evidence.py --check --verify-local-source
PYTHONPATH=backend .venv/bin/python -m pytest -q tests/test_kb_batch126_context_attestation.py
bash scripts/mac_check.sh
bash scripts/mac_browser_check.sh
```

Remote GitHub CI on the final evidence commit must be checked separately and is not presumed green from Mac runs.
