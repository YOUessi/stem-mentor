# STEM Mentor｜Batch97 Mac-only execution and delivery evidence (2026-11-11)

## Source and isolation
- Repository: `YOUessi/stem-mentor`; worktree `/Users/youtang/Documents/文件/stem-mentor-kb-batch97`; feature branch `feat/kb-batch97-math-subject-depth`.
- Base: Draft PR #121 `feat/kb-batch96-verified-deep-audit` (stacked PR, not `main`).
- Initial content commit: `9a7c05e73bf3c6ca1c4ebc61224e523b13cad26a`; mathematics and rendered-definition correction commit: `b82bf266e6bbf7e5b5b1d9cde4ee2536b64c1608`.
- The Mac main repository's **11 pre-existing local changes** were not touched or staged; Tang was not used.
- Two pre-existing generated evaluation JSON files became modified during the Mac suite; excluded from Batch97 commits to avoid unrelated changes. Synthetic test output does **not** establish real student outcomes.

## K00–K01 provisional source accounting (not official atoms)
- Machine-auditable project source queue: 300 provisional topic labels, individually source ID/page/track/SHA linked.
- Editorial categories: 166 pair-comparison-not-atomized; 24 individual-scope-not-atomized; 56 no-individual-editorial; **54 teacher-pending deep drafts** (Batch94 14 + Batch95 16 + Batch96 12 + Batch97 12). All 300 categories are mutually exclusive in the generated matrix.
- Another 134 provisional labels lack pairwise semantic comparison. They are **not** a denominator for official curriculum coverage.
- **Official seven-track atomic denominators: UNKNOWN**; 61 source pages still lack complete human atomization (0/61); teacher approvals 0; student authoritative releases 0. Existing engineering 113/board71/method26 are not deep-lesson totals.
- Candidate source SHA must equal a frozen source-row SHA; fake approval, duplicate source, and index elevation have negative regression checks.

## K02–K06 new original mathematics drafts
Twelve source-locked Chinese editor/teacher-side drafts across selective compulsory (3), electives A (3), B (3), C (2), D (1), addressing:
1. 3D coordinates and Euclidean distance;
2. line–plane relations by normal/direction vectors;
3. parabola and hyperbola locus conditions;
4. finite-limit arithmetic and quotient prerequisites;
5. fundamental theorem of calculus under supported assumptions;
6. joint continuous density and rectangular probability;
7. constrained optimization on a compact rectangle;
8. feature scaling and Euclidean clustering distances;
9. two-level orthogonal experimental designs;
10. independence of axioms versus derivability;
11. sample-frame coverage and nonresponse;
12. reflection isometry of Euclidean space.

Each record includes definitions/statements, assumptions, staged proof or method rationale, boundary and counterexample, misconception, two teacher-only worked examples, three hints, near/far transfer, source and review metadata; **24 original teacher examples and 36 hints**. All `REVIEW_PENDING`, `TEACHER_ONLY`, `NOT_FORMALLY_CERTIFIED`.
No source excerpt is presented as permission to republish a textbook; teacher review remains mandatory.

## K07 independent bounded math checks and fixes
- 12 callable exact/finite-instance diagnostics using rational arithmetic and bounded SymPy; valid premises plus actual invalid-input rejection, including nonzero normals, nondegenerate hyperbola condition, quotient-limit nonzero denominator, normalized density, zero-variance z-score and rectangle ordering.
- In correction commit `b82bf26`, replaced a constant-boolean invalid-case witness with an actual exception check on reversed rectangle bounds; generalized exact rectangle extrema from fixed coordinates to arbitrary finite rational closed rectangles.
- Added independent exhaustive integer-grid comparison of supported polynomial extrema and regression ensuring theorem/method definitions survive into rendered lesson statements.
- The finite checks **do not certify arbitrary mathematical proofs or student-supplied solution steps**. Legacy obligations still 538 uncertified proof steps, 106 P0 without directly linked teacher cards, 10 unresolved mathematical conflicts.

## K08–K09 student safety and reproducibility
- Editor draft discovery remains teacher-scoped; student search returns `NO_APPROVED_EVIDENCE` and must not leak complete worked solutions.
- Generated source ledger and deep content are deterministic, with `--check` hooks in Mac/CI and regression tests for false SHA/approval/step claims.

## Real Mac test evidence
All evidence lives in `evaluations/results/2026-11-11-kb-batch97/`. The initial focus: 169 passed; after correction: 170 passed.
- `mac_full_rerun.log` + `mac_full_rerun.exit`: **63,033 Python passed, 5 skipped, 1 warning**, plus Node **111/111**, exit 0.
- `mac_browser.log` + `mac_browser.exit`: 15 Chrome/Playwright scripts passed and browser pytest **2 passed**; exit 0. iPad checks are pointer-emulation, not physical-device tests.
- `mac_focus_rerun.log` + `mac_focus_rerun.exit`: **170 passed**, exit 0.
- Final independent delivery focus `mac_focus_delivery.log/.exit`: both builder `--check` tests and **157 direct Batch97 focused tests passed**, exit 0.
- Full-suite count includes focused tests; do not add as distinct cases. Recorded failures during earlier drafts were corrected before the final green run. One third-party dependency warning remains.
- The preceding GitHub Actions run on original content commit `9a7c05e` was Success, but CI for the final delivery HEAD must be checked separately before claiming final GitHub green.

## Open blocking dependencies and Batch98
1. Resolve official 7-track atom denominators with real cross-page semantic deduplication and independent full-page human review; preserve unknown denominators until then.
2. Continue **56** individually unaudited provisional labels, **134** without pair comparison, and expand teacher-pending complete deep drafts in sets rather than declaring the 54 drafts complete syllabus coverage.
3. Prioritize the 106 P0 source steps lacking direct review cards; the 538 uncertified steps and 10 unresolved conflicts require substantive mathematics review, not more numeric witnesses alone.
4. Run teacher-only retrieval and student leakage regression whenever lessons change; prevent DRAFT/REVIEW_PENDING from reaching student authority.
5. Continue Mac-only full Python, Node, Chrome tests and record actual code SHA, exit codes, failures, CI. No teacher approval or release is implied by passing tests.
