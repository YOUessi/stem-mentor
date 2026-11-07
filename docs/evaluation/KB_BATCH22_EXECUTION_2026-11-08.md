# STEM Mentor / KB Batch22 execution and audit — 2026-11-08

**Mac-only development and tests.** Branch `feat/kb-batch22-math-gaps-k00-proof` is a stacked Draft PR candidate based on Batch21 commit `7fe211a68b2c5fec83bbe0bc151538cfc296eaf3`. Verified implementation commit: `2661e88957c71e41cf1818b0bed75a2053834641`. No main rewrite, no Tang development, no real student data.

## Source boundary and curriculum denominator (K00/K01)

- The existing **427 overlapping human syllabus review tasks** remain **61 page-split + 315 numbered-position-split + 23 unnumbered D/E heading-split + 28 editorial gap tickets**. These are *workflow tasks, not official atomic course units*; do not add them to claim a course denominator. Existing project engineering map increased from 161 to **173 project-proposed candidates** by adding 12 explicitly labeled elective draft links. It is not an official standard atomization.
- Course level matrices separately count COMPULSORY, SELECTIVE_COMPULSORY, elective A/B/C/D/E, and elective unassigned. All verified official per-track atomic denominators, official rates and signoffs **remain null/0**. No full-syllabus inventory claim.
- 28/28 editorial gap tickets remain OPEN. 11 existing Batch21 topic-adjacent drafts + **12 new Batch22 topic-adjacent drafts** give **23/28** candidates with *non-authoritative* draft proximity, **not 23 official clauses covered**. Five gaps without proximity are **018/019/023/024/026**. See `KB_BATCH22_EDITORIAL_TRACK_MATRIX.json` and `KB_BATCH22_CURRICULUM_REVIEW_MATRIX.json`.

## Original mathematics and lesson gates (K05/K06/K07/K08)

**12 original REVIEW_PENDING / TEACHER_ONLY elective lessons**, 6 theorems, 5 methods and 1 concept; tracks A=5, B=1, C=2, D=2, E=2. Titles and source IDs are in `curriculum/highschool_math/author_draft_batch22.json` and `knowledge/deep/v1/elective_gap_batch22.json`.

1. Two-dimensional affine isometry and composition, 3D orthogonal isometries and oriented volume.
2. Triangular density, normal variance chi-square testing, Pearson goodness-of-fit with expected-count warnings, full two-factor orthogonal design.
3. Keynes affine equilibrium and contraction, Cobb–Douglas log-domain constraints.
4. Non-commuting rotation/reflection, perspective pinhole depth guards, great-circle spherical triangle with antipodal/coincident degeneracies.
5. Independent normal sampling mean law and standard error.

Each has explicit conditions, prerequisites, theorem steps or method rationale, counterexample/nonexample, misconception and repair, a three-stage hint ladder, near/far transfer, and **two independently reviewed arithmetic examples** (24 total), with teacher-side solutions restricted from student challenge flow. **Quality correction in this run:** replaced automatic comma-splitting that created duplicate/“。。” intermediate steps with 24 manually scoped first steps and added regression tests. Also corrected spherical geodesic language to distinguish distinct non-antipodal, coincident and antipodal endpoint cases. The finite oracle supports seven **specific exact rational instance checks** (orthogonal isometry, triangular CDF, chi-square statistic arithmetic, Pearson statistic, affine fixed point, pinhole projection, normal mean moments). Oracle responses explicitly **do not verify a full theorem, statistical distribution assumptions, teacher approval or free-text student steps**. Independent SymPy checks cover 3D reflections, orthogonal design rank, rotation-reflection order, spherical orthant, and all 24 examples.

**Proof evidence:** history 451 frozen proof obligations + Batch21 23 + Batch22 23 = **497 unverified steps across 247 live lesson drafts**; new 23 are conservative **14 P0 human-attention / 9 P1 human-attention**, by heuristic flags only. None of 497 is marked formally certified. The historical 10 version conflicts stay unresolved; prior 23 semantic gaps remain open. All **0 teacher APPROVED, 0 student-published deep units, 0 student free-text step certifications**.

**Generator and fail-closed audit:** run in order:
```sh
.venv/bin/python scripts/author_kb_batch22.py --check
.venv/bin/python scripts/build_kb_batch22_lessons.py --check
.venv/bin/python scripts/build_kb_batch22_proof_and_scope.py --check
cd backend && PYTHONPATH=. ../.venv/bin/python -m pytest -q tests/test_kb_batch22_elective_math.py
```
The new source matrices are auditable snapshots, **not independent proof of source/teacher authority**.

## Mac execution and failure reproduction (K09)

- Initial Python attempt incorrectly collected browser modules together with backend and got **4 collection errors**; direct browser runner was executed separately. The first scoped backend full run was **20,469 passed / 59 failed** from legacy dynamic vs frozen curriculum/lesson assertions. Three focused reruns narrowed 31 → 4 → 0 failures; provenance snapshots were preserved by differentiating historical Batch21 checks from current Batch22 inventory.
- After fixing the authored intermediate steps and spherical degeneracy: **Batch22 focused: 2,339 passed / 0 failed**. Python backend full final **21,206 passed / 0 failed, 1 third-party Starlette/anyio deprecation warning, 59.46s**; real Mac execution log `evaluations/results/2026-11-08-kb-batch22/backend-final-after-quality.log`.
- **35/35** Python CI script gates passed: `ci-gates-verified.log`. **Node 111/111 passed**: `node-final-after-quality.log`. Policy/retrieval **33/33 + 40/40**, JS syntax PASS: `integration-final.log`.
- **Full Mac Chrome browser suite after quality corrections PASSED (EXIT=0)**, including responsive math laboratories, numerics, keyboard/extremes, transfer, iPad pointer simulation and review pytest 2 passed; see browser-final-after-quality.log. This is pointer simulation, not validation on a physical iPad. Initial Chrome run also passed.
- Tests use synthetic/local evidence only; no teacher signoff, no model certification of free explanations. Historical evaluation fixture timestamps were restored to their original committed state (no fabricated old test timestamps).

## Next batch priorities and release blockers

1. **K00 #18:** split all numbered and unnumbered requirements into independently audited official atoms, with original page/line references and human judgment; reconcile the independent 248/315 extraction schemes before any denominators/rates become non-null. Address all compulsory/selective/elective tracks without counting E optional course offerings as mandatory.
2. **K07 #25:** individual reviewer evidence for 127 historical P0 and 14 newly high-attention steps; separately classify Batch21's 23; adjudicate the ten unresolved historical versions. Finite exact tests do not certify all-proof correctness.
3. **K05/K06:** continue five remaining editorial topics (018/019/023/024/026) and expand required-track lessons, variants and counterexamples beyond trial coverage.
4. **K08/K09:** implement verified source-to-lesson atomic mappings, real teacher attestation/registry and Approved-only Agent citation/permission boundary; run unseen-problem/teacher review and prevent any release until gates are met.

**No issue is closed and no draft is promoted to APPROVED.**
