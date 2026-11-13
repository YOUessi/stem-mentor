# STEM Mentor / KB Batch103 — Mac-only execution and math audit (2026-11-12)

## Scope and source integrity

- Repository: `YOUessi/stem-mentor`. Parent: Batch102 PR #127, immutable HEAD `1ed66cd1d29d5ea5987a859f8ce53da8f941bc12`.
- Mac worktree: `~/Documents/文件/stem-mentor-kb-batch103`, isolated branch `feat/kb-batch103-core-math-atom-pairs`.
- Main worktree and Batch102 worktree remain untouched. No Tang development; no force push or main merge.
- Source inputs: frozen 300 project-only provisional curriculum label candidates, prior Batch101 20-pair and Batch102 20-pair reports, original SHA-256 source-line evidence.
- Newly authored: **20 substantial pairs** with explicit hypotheses, mathematical distinctions, worked positive and invalid/counterexample instances, frozen source line hashes and curriculum engineering tracks.
- Categories: sequences/limits, functions/calculus, mathematical models, plane/space geometry/vectors, discrete probability and statistics. These are **editorial pairing records, not 20 new finished DeepLesson lectures**.
- Source conservation: 206 previously compared + 20 newly paired + 74 remaining = 300 project provisional labels. Seven project tracks reconcile individually. **Official seven-track knowledge-atom denominators remain UNKNOWN**; project provisional labels must not be used as official coverage.
- Human complete page atomization: 0/61; 172 unreviewed textual prerequisite references; 538 historical uncertified proof steps; 10 outstanding mathematical conflicts; 86 prior deep-lesson drafts pending teacher approval.
- Newly released or teacher approved records: **0**. Every new record is `REVIEW_PENDING` and `student_publishable=false`; all universal proof and mathematical-equivalence certification flags false.

## Implementation

1. `scripts/kb_batch103_pair_authoring.json`: 20 original Chinese mathematical editor comparisons, each with assumptions, distinction, valid computation, invalid boundary.
2. `scripts/build_kb_batch103_math_pairs.py`: frozen-source join with explicit individual line hash, source uniqueness checks, seven-track conservation, no-authority promotion, 20 independent bounded math witnesses, deterministic JSON/Markdown and coverage report, fail-closed `--check`.
3. `backend/tests/test_kb_batch103_math_pairs.py`: new positive, negative, provenance, report-tampering, seven-track and deterministic regeneration regressions; explicit rejection of forged approval, fake official count, fabricated formal proofs and student publication.
4. Integrated the new `--check` gate into both `scripts/mac_check.sh` and `.github/workflows/ci.yml`.
5. Versioned generation outputs: `docs/evaluation/KB_BATCH103_20_MATH_COMPARISONS.{json,md}`, `docs/evaluation/KB_BATCH103_COVERAGE.json`.

## Mathematical validation boundaries

The 20 independently checked concrete examples cover convergence versus boundedness, reciprocal sequences, removable rational-function limits, first/second derivatives, vector inner/cross products, spatial line-plane degeneracies, shortest point-plane and skew-line distances, binomial coefficients, valid discrete probabilities, percentile conventions, and conditional proportions. **Exact checks of these concrete witnesses do not establish universally quantified statements, teacher-level semantic identity, the mathematical correctness of every natural-language argument or student free-form solutions.**

The pair comparison `样本百分位数的定义约定与解释` explicitly distinguishes nearest-rank 75% percentile (=3 for 1,2,3,4) from the interpolated convention (=3.25). The line-plane comparison explicitly distinguishes contained from disjoint-parallel cases; derivative tests reject the converse of the necessary stationary-point condition; 2×2 tables reject conditioning on an empty row.

## Reproduction and test evidence

- New focused regression: **80 passed, 0 failed**, exit code 0; log `docs/evaluation/logs/KB_BATCH103_FOCUSED_INITIAL.log`.
- Generator `--check`: PASS (20 unique source-anchored pairs, cumulative 226/300, remaining 74, all approval flags false).
- Full Mac `bash scripts/mac_check.sh`: see `docs/evaluation/logs/KB_BATCH103_MAC_CHECK_FINAL.log` and final recorded exit code after completion.
- GitHub CI: independent result must be checked separately after pushing the new Draft PR, not inferred from Mac success.
- Parent Batch102's GitHub Actions run #43118126847 was verified **completed/success** during this development batch.

## Remaining blocking work / Batch104 priorities

1. K00: establish actual official-standards seven-track atom denominators through complete source-page review, especially pages 13, 14 and 51, without mistaking engineering labels for official atoms.
2. K02–K06: author full original DeepLesson units and problem families across core, selective-compulsory and elective tracks; this batch contains source-pair analyses, not new teacher-approved complete lessons.
3. K01/K08: semantically resolve 172 prerequisite notes before any typed student graph edges are published.
4. K07: risk-prioritize and independently check the 538 uncertified historical proof steps and 10 known math conflicts.
5. K09: keep all new and legacy content pending real teacher approval; rerun full Mac and independent GitHub CI, maintain student-side fail-closed behavior.

## Final Mac verification and integrity

- Mac-only final `bash scripts/mac_check.sh` command **exit code 0** (terminal parent process PID 61118 reported `FULL_EXIT:0`, runtime 1184.14 seconds).
- Python **64,058 passed, 5 skipped, 1 warning, 0 failed**; the warning is third-party Starlette/AnyIO deprecation.
- Node **111/111 passed**, zero failures.
- New Batch103 focused tests **80 passed**, zero failed (included in Python full test count).
- Browser Chrome/Playwright script checks passed (29/29 scene renders, responsive widths and interaction tests in browser log); browser pytest **2 passed**. The separate browser log was executed on Mac; do not interpret this as a physical iPad or real model API test.
- Batch103 frozen-source `--check` **PASS**; `git diff --check` also passed. No automatic teacher approval or authoritative publication.
- Source code parent commit for this tested batch: `e67056c9e8ed56fc8db6eea9f4c78d8a74a5c6d9`; tested source tree `7d2e78356c5c56d818a96aefd4c97d90b530c227`. Final delivery commit adds only this report and original test logs.

Original Mac log digests:
- `docs/evaluation/logs/KB_BATCH103_MAC_CHECK_FINAL.log` SHA-256 `a522d9c05d328778a588d55b0765b25e321d3e22972e4c4f53613cd77f99b71a`
- `docs/evaluation/logs/KB_BATCH103_BROWSER_CHECK.log` SHA-256 `7e54cc3d9f43510f955fb12c87c72038703aa8a1d373db50fca83c729e7d86bf`
- `docs/evaluation/logs/KB_BATCH103_FOCUSED_INITIAL.log` SHA-256 `8c4b2558a0070047bea41e838e30ca2cfeb27510b863aa5333c3ae4865bb8d3b`

GitHub PR/CI status is separately verified after remote synchronization; do not infer it from local test results.
