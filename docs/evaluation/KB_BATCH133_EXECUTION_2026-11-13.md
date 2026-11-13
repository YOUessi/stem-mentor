# STEM Mentor — Batch133 Mac execution and official-scope evidence (2026-11-13)

Source development commit: b5aeb593a801cf59dda24f1ce590f2886ea9a4aa; Mac-only feature worktree feat/kb-batch133-official-atom-proposals; Draft PR #159 (stacked on Batch132 #158).
Host: YOUTangdeMacBook-Air.local, MacBook Air; no Tang coding, no force push or main merge; existing uncommitted Mac main-tree files preserved. Source PDF remains solely on the authorized Mac.

## K00/K01 — bounded curriculum proposal atomization

Created **41 original proposed atom records**, each with source printed page + PDFKit line range, SHA-256 line/span fingerprints, explicit mathematical hypotheses, invalid-condition counterexamples, curriculum track, typed knowledge category, provisional prerequisites and REVIEW_PENDING state. Track counts: compulsory 23, selective compulsory 11, elective A 7; other elective tracks 0 in this sample (not nationally zero). These records are editorial proposals, not a frozen official course denominator or teacher-approved content.

The official atom denominator for each of all seven tracks is **UNKNOWN/null** and full-source-census-complete is **false**. The historical 239/239 context checks inherited from Batch132 cover editorial candidates only, not official subject denominator. Protected PDF line content was not uploaded; original Mac source SHA replay and GitHub offline fingerprint checks are explicitly separate.

Primary artifacts: curriculum/highschool_math/k00_batch133_atomic_proposals.json and docs/evaluation/KB_BATCH133_REQUIREMENT_ATOM_DECOMPOSITION.md.

## K02–K06 — six original deep teacher-only lessons

1. Relative set complement with specified universe.
2. Quantifier negation and scope.
3. Quadratic discriminant and the a=0 degenerate case.
4. Intermediate-value zero existence with continuity and strict endpoint sign change.
5. Finite geometric sums with q=1 handled separately and quotient-defined sequences distinguished.
6. Lagrange mean value theorem via Rolle's theorem, including differentiability requirements.

Each original REVIEW_PENDING/TEACHER_ONLY draft includes formal definition/theorem, domain, all assumptions, justified steps, a concrete invalid boundary, typical mistake and repair, two justified teacher examples, three non-answer student hints, near and far transfer, and provenance. Totals **6 full lesson drafts, 12 teacher examples, 18 student hints**. No teacher approval or student answer leak.

## K07 — independently reproducible finite mathematics

SymPy-based exact arithmetic and symbolic checks independently recompute **12 worked examples and 6 invalid-condition witnesses**, totaling 18 finite checks. These do not establish universal theorem truth, arbitrary student-step correctness or official source semantic fidelity.

## K08/K09 — regression and release integrity

- The original Mac PDFKit source replay of all 41 proposals passed (exit 0).
- Focused negative tests: **584 passed in 3.76s, exit 0**, checking forged approval/denominator, altered provenance, orphan dependencies, incomplete lesson/teacher proof fields and teacher-solution leakage.
- Offline consistency re-check for proposals + lessons + exact witness oracle passed (exit 0).
- Full Mac Python/Node plus Chrome/Playwright execution is tracked below; final results must be taken only from actual .exit and .log files.
- Browser touch and pressure simulation does not certify physical iPad operation.

## Known failures and limitations

An initial browser wrapper invocation failed with "Create the Mac Python environment first" because the isolated worktree virtualenv link was not ready; the link to the actual Mac project environment was subsequently created. This initial failure is not a successful browser run.
Unresolved: 538 historical uncertified proof steps, 172 historical pending prerequisites, 10 mathematical conflicts; all seven official denominator values UNKNOWN, 0 teacher approvals, 0 student-authoritative knowledge releases.

Next: full-source requirement-to-atom census and cross-page deduplication, real proof/precondition and prerequisite adjudication, typed topic-by-topic deep lessons, and benchmarked retrieval refusals/teacher-answer isolation.

## Final Mac check evidence

**Verified all five final script exits were 0 on the authorized Mac**.
Full Python: **66,293 passed, 5 skipped**, one third-party Starlette/AnyIO deprecation warning; frontend Node: **111 passed / 0 failed**.
Chrome/Playwright comprehensive suite passed, browser pytest: **2 passed**. Focused Batch133: **584 passed**.

| Mac evidence log | Exit | Bytes | SHA-256 |
|---|---:|---:|---|
| docs/evaluation/logs/KB_BATCH133_MAC_CHECK_FINAL.log | 0 | 126226 | 8846e71d4883bc4cad3c2d1112a84aa1a723a572bf58cb1351b428fa1a9c99c4 |
| docs/evaluation/logs/KB_BATCH133_BROWSER_FINAL.log | 0 | 2443 | 6695ad1ec8474d383828409d072794412570be88cdd57fac44b444090b6cfafd |
| docs/evaluation/logs/KB_BATCH133_FOCUS_FINAL.log | 0 | 740 | c54c4b17dbb0713019e8463e26ffe71fa28add8a7d81758babb356df429c1ce3 |
| docs/evaluation/logs/KB_BATCH133_OFFLINE_FINAL.log | 0 | 56 | 23f0bb412ebc8bd064ee2defe8eec1c083f4f3f5b8bb909f4f38a2934f719e14 |
| docs/evaluation/logs/KB_BATCH133_SOURCE_MAC_FINAL.log | 0 | 81 | fbdda37fc6be9bc5c969fc1719c3a99b93460e75d9240933800efe9b37c8644d |

All five corresponding .exit files are included in the Git commit and each contains 0. Successful full tests do not certify any general theorem, teacher approval, or official curriculum denominator.
The source GitHub Actions run #43439808208 completed SUCCESS for the original Batch133 source commit; final-evidence commit starts a separate CI run and must be checked independently.
