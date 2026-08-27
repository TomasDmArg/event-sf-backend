# Tasks: Multiple Addresses

**Input**: Design documents from `specs/002-multi-address/` (plan.md, data-model.md, quickstart.md)

**Tests**: Included, following `tests/test_contacts_api.py`'s existing pattern.

**Organization**: Grouped by user story from `spec.md`. Frontend tasks (sibling `sf-frontend` repo) are listed for handoff context only.

## Phase 1: Foundational — Address model, schema, migration

**Purpose**: The Address table and its plumbing, needed before any user story can be exercised. Blocking.

- [ ] T001 Add `AddressType` enum (`home`/`work`/`other`) and `Address(Base)` model to `app/models.py`: FK `contact_id` with `ondelete="CASCADE"`, `type`, location fields, timestamps (mirror `Contact`'s pattern)
- [ ] T002 Add `addresses: Mapped[list["Address"]]` relationship to `Contact` in `app/models.py` with `cascade="all, delete-orphan"`; remove `address`, `city`, `state`, `postal_code`, `country` columns
- [ ] T003 Add `AddressBase`/`AddressCreate`/`AddressUpdate`/`AddressRead` to `app/schemas.py`, following `ContactBase`/`ContactCreate`/etc.'s `Field(...)` + docstring conventions
- [ ] T004 Remove flat address fields from `ContactBase`; add `addresses: list[AddressRead]` to `ContactRead`
- [ ] T005 Add address CRUD functions to `app/crud.py`: `create_address`, `list_addresses`, `get_address`, `update_address`, `delete_address` (all scoped by `contact_id`)
- [ ] T006 Create `app/routers/addresses.py`: `POST/GET/PATCH/DELETE` under `/api/v1/contacts/{contact_id}/addresses[/{address_id}]`, following `contacts.py`'s `_get_or_404`/`responses={}` conventions; register the router in `app/main.py`
- [ ] T007 Update `app/seed.py`: create each sample contact, then attach one `Address(type="home", ...)` per contact using its former flat location values

**Checkpoint**: `pytest` on existing `test_contacts_api.py` (updated for the new `ContactRead` shape) passes; addresses exist end-to-end.

---

## Phase 2: User Story 1 — Add multiple addresses to a contact (P1)

- [ ] T008 [US1] Test: `POST .../addresses` twice with different types returns `201` each time; `GET /contacts/{id}` shows both, in new `tests/test_addresses_api.py`
- [ ] T009 [US1] Test: two addresses of the *same* type both persist (FR-004), in `tests/test_addresses_api.py`
- [ ] T010 [US1] [Frontend] Detail page groups/labels addresses by type (Home/Work/Other sections or badges)

**Checkpoint**: Backend + UI support adding and viewing multiple addresses — demoable via `quickstart.md` steps 2–3.

---

## Phase 3: User Story 2 — Edit and remove individual addresses (P2)

- [ ] T011 [US2] Test: `PATCH .../addresses/{id}` changes only that address, sibling address unaffected, in `tests/test_addresses_api.py`
- [ ] T012 [US2] Test: `DELETE .../addresses/{id}` removes only that address, in `tests/test_addresses_api.py`
- [ ] T013 [US2] Test: changing an address's `type` preserves its other fields, in `tests/test_addresses_api.py`
- [ ] T014 [US2] [Frontend] Per-address edit/delete controls on the contact detail/edit page

---

## Phase 4: User Story 3 — Migrate existing single-address contacts (P2)

- [ ] T015 [US3] Test: after `seed_if_empty()`, each seeded contact has exactly one `Address` with `type="home"` matching its old flat fields, in `tests/test_contacts_api.py`

---

## Phase 5: Edge cases & data integrity

- [ ] T016 Test: invalid `type` value on create/update returns `422`, in `tests/test_addresses_api.py`
- [ ] T017 Test: deleting a contact cascades — its addresses are gone (query returns empty / 404), in `tests/test_addresses_api.py`
- [ ] T018 [Frontend] Empty state for a contact with zero addresses

## Phase 6: Polish

- [ ] T019 Run full `pytest` suite, confirm no regressions
- [ ] T020 [P] Open PR (`feat/multi-address` → fork's own `main`), run `/review`, then `/improve`, apply or reply to each suggestion, merge

## Dependencies

- Phase 1 blocks everything.
- Phases 2–4 can proceed in parallel once Phase 1 is done (independent test files/scenarios).
- Phase 5 depends on Phase 1 (model + router must exist).
- Phase 6 is last.
- **Sequencing note (constitution V)**: this whole feature starts only after Challenge 1 (`feat/contact-photo`) is merged, per the hackathon's "finish one challenge before starting the next" guidance.
