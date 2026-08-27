# Tasks: Duplicate Contact Detection

**Input**: Design documents from `specs/003-duplicate-detection/` (plan.md, quickstart.md)

**Tests**: Included, new `tests/test_duplicates_api.py`.

**Organization**: Grouped by user story from `spec.md`. Frontend tasks (sibling `sf-frontend` repo) are listed for handoff context only.

**Note**: This is the bonus/stretch feature — start only after Challenge 1 and Challenge 2 are each merged (constitution + spec.md Assumptions).

## Phase 1: Foundational — detection + schemas

- [ ] T001 Add `DuplicateReason` enum (`email`/`phone`/`similar_name`) and `DuplicateCandidate`/`DuplicateCandidateList` response schemas to `app/schemas.py`
- [ ] T002 Add `find_duplicate_candidates(db)` to `app/crud.py`: pairwise scan over all contacts, flag on exact email match, exact phone match, or `difflib.SequenceMatcher` ratio above a threshold (e.g. 0.85) on full names; return each pair once with all applicable reasons
- [ ] T003 Add `GET /api/v1/contacts/duplicates` to a new `app/routers/duplicates.py`, returning `DuplicateCandidateList`; register router in `app/main.py`

**Checkpoint**: Detection endpoint returns correct pairs — demoable via `quickstart.md` steps 1–2.

## Phase 2: User Story 1 — Detect likely duplicate contacts (P1)

- [ ] T004 [US1] Test: two contacts with the same phone are flagged with reason `phone`, in `tests/test_duplicates_api.py`
- [ ] T005 [US1] Test: two contacts with similar-but-not-identical names are flagged with reason `similar_name`, in `tests/test_duplicates_api.py`
- [ ] T006 [US1] Test: two clearly distinct contacts are not flagged, in `tests/test_duplicates_api.py`
- [ ] T007 [US1] [Frontend] "Possible duplicates" view listing flagged pairs with their reason(s)

## Phase 3: User Story 2 — Merge two duplicate contacts (P1)

- [ ] T008 [US2] Add `MergeRequest` schema (`primary_id`, `secondary_id`, optional `field_resolutions: dict[str, "primary"|"secondary"]`, optional `photo_from: "primary"|"secondary"`) to `app/schemas.py`
- [ ] T009 [US2] Add `merge_contacts(db, primary_id, secondary_id, resolutions)` to `app/crud.py`: re-point all of the secondary's `Address` rows to the primary (skip exact-duplicate addresses), apply photo fallback/choice, apply scalar-field resolutions, delete the secondary contact, all in one transaction
- [ ] T010 [US2] Add `POST /api/v1/contacts/merge` to `app/routers/duplicates.py`, returning the merged `ContactRead`
- [ ] T011 [US2] Test: merge unions addresses from both contacts (no loss), in `tests/test_duplicates_api.py`
- [ ] T012 [US2] Test: merge keeps a photo if either source had one; explicit `photo_from` choice respected when both have one, in `tests/test_duplicates_api.py`
- [ ] T013 [US2] Test: after merge, the secondary contact returns `404`; exactly one contact remains, in `tests/test_duplicates_api.py`
- [ ] T014 [US2] Test: conflicting scalar field (e.g. `job_title`) requires/respects `field_resolutions` rather than silently picking one, in `tests/test_duplicates_api.py`
- [ ] T015 [US2] [Frontend] Merge action + conflict-resolution modal on the duplicates view

## Phase 4: Edge cases

- [ ] T016 Test: exact-duplicate address on both contacts is not duplicated post-merge, in `tests/test_duplicates_api.py`
- [ ] T017 [Frontend] Dismiss action for a flagged pair (client-side/session-scoped, per spec.md Assumptions — no backend persistence needed)

## Phase 5: Polish

- [ ] T018 Run full `pytest` suite, confirm no regressions
- [ ] T019 [P] Open PR (`feat/duplicate-detection` → fork's own `main`), run `/review`, then `/improve`, apply or reply to each suggestion, merge

## Dependencies

- Phase 1 blocks Phases 2–4.
- Phase 2 and the detection half of the frontend can proceed once Phase 1 is done.
- Phase 3 depends on Phase 2's schemas existing but is otherwise independent business logic.
- Phase 5 is last.
- Whole feature depends on Challenge 1 (photo field) and Challenge 2 (Address table) already being merged.
