# Tasks: Contact Photo

**Input**: Design documents from `specs/001-contact-photo/` (plan.md, data-model.md, quickstart.md)

**Tests**: Included — the repo already has a pytest suite (`tests/test_contacts_api.py`) covering every contact endpoint; adding photo coverage there follows Constitution Principle II (Follow Existing Patterns).

**Organization**: Backend tasks (this repo) are grouped by user story from `spec.md`. Frontend tasks (sibling `sf-frontend` repo) are listed separately for context/handoff — they are not executed from this repo's task runner.

## Phase 1: Backend — Foundational

**Purpose**: The `photo` field itself, needed before any user story can be exercised.

- [ ] T001 Add `photo: Mapped[str | None] = mapped_column(Text)` to `Contact` in `app/models.py`
- [ ] T002 Add `photo: str | None = Field(default=None, ...)` to `ContactBase` in `app/schemas.py` (inherited by `ContactCreate`/`ContactReplace`), and to `ContactUpdate` and `ContactRead`
- [ ] T002a Add `Pillow` to `requirements.txt` / `pyproject.toml` dependencies (per Clarifications — see `plan.md` Complexity Tracking)
- [ ] T003 Create `app/image.py` with `decode_and_recompress(data_url: str) -> str`: parse the data-URL prefix (reject if not `image/{jpeg,png,webp,gif}`), decode base64 (reject if >2 MB decoded or invalid base64), decode+verify with Pillow (reject if not a real image), resize to a max dimension if needed, re-encode as WebP, return a new `data:image/webp;base64,...` string; raise `ValueError` with a clear message on any rejection
- [ ] T003a Add a `field_validator` on `photo` in `app/schemas.py` (`ContactBase`/`ContactUpdate`) that calls `decode_and_recompress()` and turns a `ValueError` into a Pydantic validation error
- [ ] T004 Confirm `crud.py` and `routers/contacts.py` need no changes (both already do generic `model_dump()` field pass-through) — verify by running the existing test suite; confirm `GET /api/v1/contacts` (list) returns the same `photo` field as detail, no separate summary schema needed (per Clarifications)

**Checkpoint**: `photo` field exists end-to-end through create/read; ready for story-level tests.

---

## Phase 2: User Story 1 — Add a photo to a contact (P1)

- [ ] T005 [US1] Test: `POST /api/v1/contacts` with a valid small base64 photo returns `201` with a `photo` echoed back as a `data:image/webp;base64,...` string (re-encoded, per Clarifications), in `tests/test_contacts_api.py`
- [ ] T006 [US1] Test: `PATCH /api/v1/contacts/{id}` with a new `photo` replaces the old one, in `tests/test_contacts_api.py`
- [ ] T007 [US1] Test: `POST`/`PATCH` with an oversized, malformed, or non-image (e.g. valid base64 of random bytes with an `image/png` prefix) `photo` returns `422`, in `tests/test_contacts_api.py`
- [ ] T007a [US1] Test: `GET /api/v1/contacts` (list) includes `photo` on each item, matching what `GET /api/v1/contacts/{id}` returns, in `tests/test_contacts_api.py`

**Checkpoint**: Backend fully supports add/replace with validation — independently demoable via `quickstart.md` step 1–2.

---

## Phase 3: User Story 2 — Circular avatar with initials fallback (P1)

*(Frontend-only story — tracked here for completeness, executed in the sibling `sf-frontend` repo, not this one.)*

- [ ] T008 [US2] [Frontend] Build shared `Avatar` component: `rounded-full aspect-square object-cover` image when `photo` is present, initials circle (first letter of `first_name` + `last_name`) otherwise
- [ ] T009 [US2] [Frontend] Use `Avatar` in the contact list view
- [ ] T010 [US2] [Frontend] Use `Avatar` in the contact detail view

**Checkpoint**: Visual acceptance criteria in `spec.md` User Story 2 verifiable in the browser.

---

## Phase 4: User Story 3 — Remove a contact's photo (P3)

- [ ] T011 [US3] Test: `PATCH /api/v1/contacts/{id}` with `"photo": null` clears the photo, in `tests/test_contacts_api.py`
- [ ] T012 [US3] [Frontend] Add a "remove photo" control on the edit form that clears the field

---

## Phase 5: Frontend — Edit form photo carry-through (the hint's trap)

*(Frontend-only, but blocking for the "no silent wipe" acceptance scenario in `spec.md` US1.)*

- [ ] T013 [Frontend] Edit form must load the contact's current `photo` into its PUT payload state and re-send it unless the user explicitly changed/cleared it, per `data-model.md`'s note that the backend does not preserve omitted fields on PUT

---

## Phase 6: Polish

- [ ] T014 Run full `pytest` suite (`tests/`) and confirm no regressions on existing contact tests
- [ ] T015 [P] Open PR on the fork (`feat/contact-photo` → fork's own `main`), run `/review`, then `/improve`, apply or reply to each suggestion, merge

## Dependencies

- Phase 1 blocks all others.
- Phase 2 (US1) and Phase 3 (US2) can proceed in parallel once Phase 1 is done (different repos).
- Phase 4 (US3) depends on Phase 1 only.
- Phase 5 depends on Phase 3 (Avatar component existing) for a full demo, but is really a correctness fix for US1 and should not be deferred.
- Phase 6 is last.
