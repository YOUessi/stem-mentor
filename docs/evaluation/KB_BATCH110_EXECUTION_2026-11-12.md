# STEM Mentor · Batch110 Mac-only execution · 2026-11-12

## Development/source of truth

- Repository: `YOUessi/stem-mentor`; source worktree on MacBook Air: `~/Documents/文件/stem-mentor-kb-batch110`.
- Branch: `feat/kb-batch110-official-20-57-lesson-integrity`; base: Batch109 Draft PR #134, not `main`.
- Mac original content commit `8b6631e`; Mac content Git tree `d085fc0241b5f921d46a04da2b041ea71b407f1e`.
- GitHub code delivery commit `cfb695ff227cf411bcdba07567ab46800cfe24d8`; 18 Git blobs SHA-verified, remote tree equals Mac tree byte-for-byte. Native Mac Git push failed with HTTP low-speed timeout; GitHub Git objects created a non-force forward update. [Draft PR #135](https://github.com/YOUessi/stem-mentor/pull/135).
- The original Mac `main` worktree and its unrelated uncommitted changes were untouched; Tang was not used.

## K00 / K01: audited source and machine-checkable truth

- Official mathematics-standard PDF (2017/2020 revision) printed pages **20, 57**, with **58 PDFKit source lines**, partitioned into **15 continuous source blocks**, with cross-page context.
- **20 original provisional editorial curriculum candidates**, among them **14 finite exact mathematical witnesses** and **6 pedagogy/non-theorem cases**.
- Page 20's asterisk-tagged history activity is optional and not a compulsory theorem. Page 57 switches from elective A to elective B; two B candidates cannot be counted as A.
- New read-only coverage matrix combines batches 108–110: **60 provisional source candidates across 6/61 pages** (COMPULSORY 26 / SELECTIVE_COMPULSORY 0 / ELECTIVE_A 32 / ELECTIVE_B 2 / ELECTIVE_C-D-E 0). **This is not an official seven-track atomic denominator.**
- Every official seven-track denominator remains `UNKNOWN` and authoritative coverage ratios must remain null. **0/61** pages teacher fully atomic-reviewed; **0** teacher approvals and student authoritative releases. Schema tests reject duplicate source coordinates, forged status/denominators, track switches, and drift.

## K02–K06: eight original deep manuscripts

1. Power functions: exponent-dependent real domains.
2. Positive-base fractional exponents and power laws.
3. Exponential strict monotonicity, split by base ranges.
4. Logarithm change of base / product and quotient conditions.
5. Moment estimators and identifiability.
6. Bernoulli maximum likelihood including parameter endpoints.
7. p-value interpretation vs posterior probability.
8. Intercepted least squares, unique fit iff `Sxx > 0`.

All eight are `REVIEW_PENDING`, `TEACHER_ONLY`, machine-structurally complete **12/12 fields**, not teacher-certified mathematical truth. They provide **16 stepwise teacher worked examples**, **24 graded student-safe hints**, **16 near/far transfer exercises**, **8 counterexamples**, **12 draft proof steps** and **4 editorial candidate prerequisite links**. Teacher solutions must not be exposed to independent student exercises.

## K07–K09: tests, evidence, failure and recovery

- Four new focused test modules: `test_kb_batch110_scope.py`, `test_kb_batch110_lessons.py`, `test_kb_batch110_coverage.py`, `test_kb_batch110_independent_math.py` cover mathematical boundary cases, positive/negative examples, source integrity, legitimate visibility and forged authority rejection.
- First Mac full `scripts/mac_check.sh` invocation executed Python **65,251 passed / 5 skipped / 1 warning**, but **did NOT finish successfully**: it exited **2** after pytest with `scripts/mac_check.sh: line 165: unexpected EOF while looking for matching '\"'`. This failure is retained in `docs/evaluation/logs/KB_BATCH110_MAC_CHECK_FIRST_FAILURE.log`; do not mislabel as a full green run. A fresh `bash -n scripts/mac_check.sh` returned 0, then the unchanged script was rerun from the beginning with a new log.
- Final Mac **full re-run exit 0**: **65,267 Python passed / 5 skipped / 1 third-party warning / 0 failed** in **928.31 seconds**, **111/111 Node** passed. Separate Batch110 focused **151 passed**; student-policy synthetic **33/33**, structured-retrieval hard negatives **40/40**, Chrome/Playwright checks and browser pytest **2 passed**. Focused cases are already included in full Python count. No GPU or external model API was used.
- Independent Chrome/Playwright and browser-pytest log: `docs/evaluation/logs/KB_BATCH110_MAC_BROWSER_FINAL.log`, including browser pytest **2 passed** and no external learner data writes. This browser check does not certify mathematical truths.
- Raw Mac evidence SHA-256 (check the Git-tracked files, not a pasted claim):

| Log | SHA-256 | Evidence |
|---|---|---|
| `KB_BATCH110_MAC_CHECK_FINAL.log` | `0ef5ca0e420ac9d9a7c8c1ccbce75177f14284dff5c5b96654f93393c0dde389` | Final full exit 0; Python + Node |
| `KB_BATCH110_MAC_CHECK_FIRST_FAILURE.log` | `69d75024834a850ef94ac361135e5f595142cc284769477b16dcc8aff43cad94` | First full Python passed but shell parse exit 2 |
| `KB_BATCH110_MAC_FOCUSED_FINAL.log` | `e86c303d3d7e20af3a05650f8427fb0ef432eaf0b782ee77cd2af37dd1a65ae6` | 151 focused passed |
| `KB_BATCH110_MAC_NODE_POLICY_FINAL.log` | `278e97467b9408b0a29f329b1b0f2b71c38345700d7230354d00d6f99431e34d` | 111 Node passed / policy & retrieval |
| `KB_BATCH110_MAC_BROWSER_FINAL.log` | `31272e602cb92aee9a6a1b4fd636088c332795c92eab67a31afb1abff413515b` | Browser checks and 2 browser pytest passed |

The initial shell parse failure occurred after the long Python pass; the precise race cause was not conclusively established. CI now includes `bash -n` preflight, and the complete, unchanged script passed on its final Mac re-run. Mac snapshot modifications in `evaluations/results/2026-10-15-*` were intentionally left uncommitted. Finite SymPy/exact checks remain finite witnesses, not formal universal proofs.

## Remaining blockers (do not auto-promote)

- Official 7-track atom denominators UNKNOWN; 55/61 source pages not within this 3-batch pair's detailed partition evidence.
- 172 historical prerequisite relation labels not certified, 538 historical proof steps not fully certified, 10 recorded math conflicts outstanding.
- Structured manuscript completeness is not mathematical or curriculum approval. `APPROVED` remains 0, arbitrary student proofs verified 0.

## Next linked batch

1. Review printed pages **21 and 58** plus cross-page neighbors; add auditable evidence for all tracks without inventing denominators.
2. Build 8–15 complete original manuscripts across combinatorics, probability and modeling, with direct source linkage and per-step condition verification.
3. Act on the oldest high-risk P0 proof/condition conflicts and unverified prerequisite edges, improve reviewer work queue with exact failure examples.
4. Verify strict student-side authority/no-solution-leak retrieval behavior and independently rerun Mac Python, Node, browser and GitHub CI.
