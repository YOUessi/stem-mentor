# STEM Mentor KB Batch129 — Mac-only execution, source integrity and CI repair

**Date:** 2026-11-13. **Repository:** YOUessi/stem-mentor. **Draft PR:** #155.
**Code source base:** `3261c4668743bc034b941d780b2b7f28ba3fc7cd` (actual remote Batch128-aligned head).
**Initial Batch129 source commit:** `0e8872861dfcf151b15a5341b1ea1d77b2f26e60`.
**All local development, source checking and tests were performed on the authorised MacBook Air; Tang was not used.** Main worktree and unrelated changes were kept out of the feature branch.

## Delivered source content and provisional curriculum accounting

- K00/K01: 28 new page/line-hash-attested curriculum-context editorial reviews (four per each of seven tracks); cumulative historical candidate contextual reviews **104/239**, unresolved **135**. 56 *provisional teaching subtargets* split from these reviews are NOT official curriculum atoms.
- K02–K06: Nine original, substantial teacher-only lesson manuscripts: cosine law, stratified sampling, conditional probability, Bayes' theorem, Gaussian elimination, Bernoulli MLE, exponential population growth, commensurable music rhythm sync, and school-optional compound interest. Each includes explicit preconditions, reasoned steps, counterexample or invalid use, common wrong work, two controlled worked examples, three student-safe hint levels, and near/far transfer.
- K07: Independent SymPy/exact rational oracles for **18** controlled worked examples, **9** invalid-condition cases and **9** cross-topic checks. None is a general quantified proof or certification of arbitrary student solutions.
- K08/K09: `REVIEW_PENDING / TEACHER_ONLY`, never APPROVED or student authoritative. No PDF paragraph or genuine student data is committed.

## Mac and GitHub CI mismatch discovered and corrected

GitHub Actions run [#43412649204](https://github.com/YOUessi/stem-mentor/actions/runs/43412649204), triggered on the first Batch129 code commit, **FAILED** at `python scripts/build_kb_batch127_source_review.py --check`. The command accesses the Mac-only `/private/tmp/kb117_pdfkit_lines_private.json`; the clean GitHub runner has no licensed curriculum PDF/private extraction. It was improper to treat that private-source replay as a portable CI step.

The correction **does not skip source integrity** silently. There are now two explicitly separated gate types:

1. **Mac source-replay gate:** Original Batch127, Batch128 and Batch129 source check scripts still read/re-hash original licensed PDFKit line windows and validate published interpretation artifacts. Their result is recorded in the Mac focus log. This is the only gate that claims fresh source-window verification.
2. **GitHub offline committed-artifact gate:** `scripts/check_kb_batch127_129_offline.py` verifies all **84** committed 127–129 context records against source-window SHA commitments and pinned PDF manifest; validates seven-track counts, source references, duplicate IDs, length and format of line/span hashes, unchanged rendered reports and fail-closed review/official-denominator authority. Crucially, it emits `source_pdf_recomputed_in_ci=false` and `source_hashes_recomputed_in_ci=false` to avoid pretending original content is present.
3. **CI math/lesson replay:** `scripts/check_kb_batch129_offline_lessons.py` reconstructs all nine drafts from the already-verified committed context and runs independent mathematical oracles (18+9+9); original Mac `build_kb_batch129_lessons.py --check` still uses the private source path by default. Legacy Batch127 mathematical checks and Batch128 P0 proof checks stay in CI.
4. **Negative regression:** New 19-case offline test suite guards forged teacher approval, fabricated official denominator, student publication, dropped/extra source locks, mismatched/malformed hashes, PDF fingerprint drift, markdown drift, missing artifacts, and proof-step promotion, and explicitly verifies CI can run with the private PDFKit cache inaccessible. It covers only artifact consistency, not mathematical source interpretation.

This corrects the CI architecture without introducing copyrighted source text, falsely certifying proof steps, or loosening the Mac source replay. Real teacher approval remains required before any authoritative student publishing.

## Executed tests and actual results

| Test | Result | Notes |
|---|---|---|
| `scripts/mac_check.sh` | **EXIT 0** | 66,293 Python passed, 5 skipped, 1 dependency warning; Node 111 passed / 0 failed; baseline policy simulations passed. Full backend Python result not increased by standalone focused tests. |
| `scripts/mac_browser_check.sh` | **EXIT 0** | Playwright/Chrome flow successful; browser pytest 2 passed (simulated touch/pencil, not real iPad). |
| Initial Batch129 scoped test | **110/110 passed** | Logged before CI remediation. |
| Final 127/128/129 Mac source replay + CI portable gates + focused tests | **EXIT 0**, **129/129 passed** | 19 new offline tests + 110 existing Batch129 tests; 84 source artifacts checked offline; 18+9+9 finite math oracle checks. |
| GitHub Actions first head | **FAILED** | Diagnosed failure at Batch127 source replay requiring private Mac cache; not counted as successful CI. |
| GitHub Actions final head | **To be checked after remote evidence commit** | Final result must be obtained from GitHub; never inferred from the Mac result. |

## Raw evidence SHA-256

| Evidence file under `docs/evaluation/logs/` | SHA-256 |
|---|---|
| `KB_BATCH129_FOCUS_INITIAL.log` | `1e4931fa366170182d790a93911126269066429b563e365dc188aa515d8ca3a9` |
| `KB_BATCH129_FOCUS_INITIAL.exit` | `1ca4a13146b2891c0e462123ac0cb848f92e6221f18b870a1b78c232d1956c35` |
| `KB_BATCH129_MAC_CHECK_FINAL.log` | `6e01ad067b3a2d552b48db522f71559d0ebcc90da04c2b2345d5a53f1f39f9fc` |
| `KB_BATCH129_MAC_CHECK_FINAL.exit` | `1ca4a13146b2891c0e462123ac0cb848f92e6221f18b870a1b78c232d1956c35` |
| `KB_BATCH129_MAC_BROWSER_FINAL.log` | `a473d276660537af6a8f071aef66e36dcaa2d0968ea7692b92683cc6eb772ac2` |
| `KB_BATCH129_MAC_BROWSER_FINAL.exit` | `1ca4a13146b2891c0e462123ac0cb848f92e6221f18b870a1b78c232d1956c35` |
| `KB_BATCH129_CI_FIX_FOCUS_FINAL.log` | `f56f07647874542bd8de0ca82babd630525227854e83fcb2f7783c9f3bd84069` |
| `KB_BATCH129_CI_FIX_FOCUS_FINAL.exit` | `1ca4a13146b2891c0e462123ac0cb848f92e6221f18b870a1b78c232d1956c35` |

## Unresolved debt and next work

- Official atom denominator for compulsory, selective-compulsory and all elective tracks: **UNKNOWN**; 405 source layout cues are not official atoms.
- Of 239 historical editorial candidates, **135** still lack these source-context audit dossiers.
- Original 538 proof steps remain not formally certified; 172 historical prerequisite links require evidence adjudication; 10 mathematics conflicts remain OPEN.
- Teacher approved **0** and student authoritative publication **0**. No premature proof or teacher approval.
- Next batch should adjudicate a further large cross-track candidate set with stronger source semantics, audit high-priority proof-step justifications and prerequisite edges, expand rigorous lessons/transfer, and verify the repaired GitHub CI.

**Reproduction note:** Run `bash scripts/mac_check.sh` and `bash scripts/mac_browser_check.sh` on the authorised Mac. Run `python scripts/check_kb_batch127_129_offline.py --check` and `python scripts/check_kb_batch129_offline_lessons.py --check` anywhere with the checked-out source and dependencies; these are intentionally weaker than the Mac private-source replay.
