# STEM Mentor v0.14 — iPad-first handwriting study pilot

**Status:** Implemented in `feat/v014-ipad-pencil-workspace`; Mac browser tested. **Not validated on a physical iPad or Apple Pencil.**

## User experience / 产品目标

The existing green STEM Mentor home and original computer-based study workspace continue to exist. A new, **opt-in** path provides iPad-oriented practice:

1. `/ipad` — lightweight learning home: continue paper, choose a controlled problem, recent *actual* completed episodes, due reviews, honest "unverified" mistakes.
2. `/ipad/study` — full-screen paper (fixed top bar, edge toolbar, minimal persistent chrome).
3. Agent stays **closed by default**. Tapping Help opens a side panel in landscape or bottom drawer on portrait/narrow screens. Closing it preserves writing and viewport.
4. One notebook document is bound to the synthetic student ID + current learning session ID; stroke data lives in the current browser's IndexedDB only.

No OCR, no generic handwritten-math understanding, no learning-result grading, no remote ink uploading, and **no real student account authentication** in this release.

## Data layers and interface

- `apps/web/ipad/index.html`, `ipad.css`: new screen composition; original `/` and app color scheme preserved.
- `ink_core.js`: immutable version-1 vector document model, bounded 50 pages / 1,800 strokes per page / 2,500 samples per stroke. Page IDs, stroke IDs, pen pressure, Erase-near, polygon lasso selection and translation, reversible history, coordinate transforms with anchored zoom. Node tests cover invariants.
- `storage.js`: IndexedDB store `stem-mentor-synthetic-ink-v1`. IndexedDB writes use a transaction with success/failure surface; browser-local storage is **not secured with login/encryption**, so only synthetic data is allowed.
- `app.js`: application controller for pointer events, coalesced pressure samples, touch gestures, local autosave with revision counter, notebooks, and voluntary Tutor textual help.
- New FastAPI routes `GET /ipad`, `GET /ipad/study` return the same static client HTML; no new backend endpoint receives strokes.
- Old green Tutor work area adds a clearly optional “进入 iPad 全屏手写学习本” link. Existing `/api/sessions` and history retain their older behavior.

**Data flow:**
```
pen/mouse/touch → pointer sample → immutable vector document → IndexedDB (local only)
student voluntarily types a request → existing simulated Tutor POST /api/sessions/{id}/turns
```
The second route **never automatically sends the selected ink or an image**. A selection tells the student which hand-written area they might describe, but the system cannot interpret that ink on its own.

## Interaction rules

| Interaction | Expected behavior | Limit |
|---|---|---|
| Pen (including coalesced events) | Smooth vector samples, pressure 0.1–1.0 and width; immutable strokes | Browser emulation does not measure true Pencil lag |
| Touch by default | Pan with one finger; two-finger pinch + anchored zoom | Palm rejection heuristic only; requires physical iPad test |
| Eraser | Whole intersecting stroke removed; undoable | Not pixel-level erasure |
| Lasso | Select strokes whose samples are inside polygon, move as a group | Partially intersecting paths not captured in every case |
| Undo/Redo | Explicit reversible document edits | In-memory undo history resets after page reload |
| New page | Adds a blank page, retains prior pages | No PDF import/annotation in this pilot |
| Autosave | Debounced IndexedDB writes and flush on page hide; save errors displayed | Browser storage quota / clearing remains a risk; export JSON |
| Agent | Closed until requested; opens in responsive panel | Tutoring remains deterministic simulated text; no OCR or math proof verification |

A JSON export is available as a manual local escape hatch; no automatic cloud sync. Drawing by a finger can be deliberately enabled, but basic two-finger navigation is optimized for the default touch-as-navigation path.

## Tested / untested

The frozen candidate should pass Node vector-core tests, all existing Node and Python regressions, and **the complete legacy Chrome suite plus two new browser checks**. The checks exercise actual IndexedDB persistence, undo/redo, eraser/lasso, across-page restore, voluntary Tutor request, widths 1024 / 834 / 390px, simulated touch pinch, and emulated pen pressure.

**Not validated yet:** physical Apple Pencil writing latency/pressure curve, tilt, accidental palm contact, hardware pen switching, long handwritten sessions and browser storage evictions. This release is not a production iPad app, not a complete Goodnotes replacement, and it does not understand formulas from ink. For a production notebook we must add user authentication, sensitive-data policy, backup/restore, richer selection, accessibility, and device-specific iPad QA.

## Release policy

Develop and test **only on MacBook Air** in an isolated worktree. No Tang, no model API, no live user data. Complete Mac and GitHub CI before merging. Production stable service `http://127.0.0.1:8000` stays at v0.13 until a separate deployment decision; the local v0.14 pilot is currently at `http://127.0.0.1:18914/ipad`.

Knowledge content and theorem database remain a separate engineering workstream; this pilot neither changes nor certifies the existing 113-topic curriculum mapping.
