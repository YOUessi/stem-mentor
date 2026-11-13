# STEM Mentor — KB Batch101 Mac execution and acceptance ledger (2026-11-12)

## Source and isolation
- Project: `YOUessi/stem-mentor`, master #17 and K00–K09 #18–#27.
- Machine: **YOUTangdeMacBook-Air.local only**, macOS 26.3.2 arm64; Python 3.13.13, pytest 8.4.2, SymPy 1.14.0, Node 22.23.1. No Tang training, development, dataset processing, or tests.
- Independent worktree: `~/Documents/文件/stem-mentor-kb-batch101`; branch `feat/kb-batch101-prereq-review-queue`.
- Baseline: local Batch100 tree `c82750655b1f3f0e776efa1fe614bbb011e42a1f`; equivalent delivered remote Batch100 content is Draft PR #125, with upstream GitHub SHA `709f72a9a8a4cf36b29cc1b1e8e10cde6fc6716d` (different ancestry: do not rewrite, force-push, or merge).
- Mac **source commit**: `0307c59c515a9e31a1c3dbc53c2a57e7fc78efa4`; source tree `7b9463e7a0b6bc18fca656adb127a1500eb40ac8`.
- Main worktree's 11 preexisting edits unchanged; two regenerated historical policy evaluation JSON timestamps intentionally excluded from this commit.

## Work completed (all provisional)
1. **K00 page and topic evidence census:** 61 source pages, 428 project line anchors and 300 provisional topic labels, all digest-locked; pages **13, 14, 51** have no project anchors. No full-page teacher atomization: **0/61**. Project provisional seven-track labels: compulsory 75, selective compulsory 66, elective A 60, B 60, C 31, D 8, E 0. Official curriculum atom denominators remain **UNKNOWN for all seven tracks**. Neither 300 nor 86 is an official denominator.
2. **K00 editorial pair comparisons:** 20 distinct previously-uncompared mathematics themes now have source-line-linked author-composed comparison notes with applicability assumptions, mathematical distinction, valid and invalid cases and proposed relationship. Prior 166 editorial comparisons + new 20 = 186; 114 labels have no pairwise editorial comparison. These **do not** certify equivalence, merge official atoms or indicate teacher approval.
3. **K01/K08 prerequisite reviewer queue:** 172 textual prerequisite descriptions from 86 teacher-pending deep lesson drafts, all explicitly unresolved, linked to lexical-only review candidates or manual discovery; **135** lack adequate lexical nearest neighbors. 134 earlier unmatched semantic topics also have a reviewer queue; **101** need manual cross-domain search. Candidate suggestions are NOT formal prerequisites, valid implications, or student-eligible graph edges. Student graph promotions: **0**.
4. **K07 mathematical validity:** 20 bounded mathematical positive/boundary example pairs; six examples corrected to test their actual mathematical conditions instead of generic always-true inequalities (SSA ambiguity, sequence differences, one-sided derivatives, Fermat converse, degenerate ellipse, mean-value differentiability). Finite instances are **not** proof of universally quantified statements. No unverified student free response is promoted to verified.
5. **K01/K09 fail-closed gates:** 3 generators integrated into Mac and GitHub CI, including Batch100's previously missing source/coverage artifact checks. Per-source page anchor range, uniqueness, same-page extraction digest and known-page membership now checked. Four extra mutation regressions added for same-sized duplicate, unknown page, invalid line and changed page hash. All statuses remain `REVIEW_PENDING / TEACHER_ONLY`.

## Mac test evidence
- `bash scripts/mac_check.sh`: **63,878 Python passed, 5 skipped, 1 warning; 111/111 Node passed; final exit 0**. The raw log contains two overlapping Mac backend pytest invocations (63,798 and 63,878), both recorded; only the final completed 63,878-test run is counted here. Original log: `docs/evaluation/logs/KB_BATCH101_MAC_CHECK.log`.
- After exact mathematical oracle and source-page gate refinements, **500/500 focused tests passed, exit 0**: `docs/evaluation/logs/KB_BATCH101_FOCUSED_FINAL.log`. These are a *subset* of the full suite, not an additional 500 independent tests.
- Historical focused runs: 416 passed, mathematical pair focused 58 passed, preceding combined focused 496 passed; archived for reproducibility, not added to the total.
- Mac Chrome/Playwright checks passed (legacy through iPad emulation); browser pytest **2 passed**, exit 0. This is an emulation, **not** physical iPad / real student / live LLM certification.
- `bash -n scripts/mac_check.sh` and YAML syntax parsed; Python `--check` for Batch100 depth/coverage and Batch101 queue/math/coverage all exit 0.
- Explicit negative checks include source hash drift, duplicate/edit-authority attacks, nonexistent source coordinates, missing/duplicate prerequisites, false mathematical relation, fake teacher approval and student-answer leakage.
- Two transient remote transport retries occurred during test editing, but Mac worktree and focused reruns were verified afterward.
- The full backend suite was already running during the six last oracle replacements; later focused 500 tests and all artifact `--check` gates were rerun after those replacements. GitHub CI must independently re-run all tests on the published tree.

## Real remaining work / prioritization
- 114 themes still have no authored semantic pair comparison and 61 official source pages require *complete human atomization*, including the 3 unanchored pages. Formal per-track course atom denominators and judgments are unavailable.
- 172 textual prerequisites remain unconfirmed; no automatically constructed edge can bypass mathematical implication/cycle/track and teacher review.
- 86 deep lesson drafts are unapproved. Historical K07 debt includes **538** unverified proof steps and **10** unresolved conflicts (legacy counts, not newly closed here).
- **Teacher approval = 0. Student authoritative publication = 0.** Retrieval must fail closed and not expose teacher solutions.

Next batch: teacher-auditable source clause atomization for the seven tracks, 114 remaining semantic pairs, independent K07 proof/counterexample review for P0 cases, and new original complete lessons mapped to verified course evidence. No fabricated review status and no copyright textbook contents.
