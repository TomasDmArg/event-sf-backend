# Implementation Plan: Multiple Addresses

**Branch**: `feat/multi-address` | **Date**: 2026-08-26 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/002-multi-address/spec.md`

## Summary

Replace the flat `address`/`city`/`state`/`postal_code`/`country` columns on `Contact`
with a new `Address` table (FK `contact_id`, `type` enum Home/Work/Other, plus the
same location fields). Add nested address read/write support to the contact schemas
and new sub-resource endpoints for address CRUD. SQLAlchemy relationship with
`cascade="all, delete-orphan"` handles cascade-delete; SQLite FKs are already enabled
process-wide (`app/database.py`'s `PRAGMA foreign_keys=ON` listener), so DB-level
cascade is real, not just ORM-level.

## Technical Context

**Language/Version**: Python 3.11+ (backend, this repo); TypeScript/Next.js (frontend, sibling repo `sf-frontend`, out of scope for this plan/tasks file)

**Primary Dependencies**: FastAPI, SQLAlchemy 2.0, Pydantic v2 (existing — no new dependency; SQLAlchemy's `Enum` type covers the Home/Work/Other constraint without extra libs)

**Storage**: In-memory SQLite; new `addresses` table with `FOREIGN KEY(contact_id) REFERENCES contacts(id) ON DELETE CASCADE`

**Testing**: pytest, extending `tests/test_contacts_api.py` plus a new `tests/test_addresses_api.py` for the address sub-resource, following the existing test file's fixture/style patterns (see `tests/conftest.py`)

**Target Platform**: Local dev server, same as rest of the app

**Project Type**: web-service (backend) + web-app (frontend, sibling repo)

**Performance Goals**: N/A — demo-scale data (a handful of contacts, a handful of addresses each)

**Constraints**: Must be a real relational table with FK + type column (constitution principle IV, and explicitly judged); legacy single-address fields are removed from `Contact`, not kept alongside the new table (avoids two sources of truth); existing seeded contacts' addresses must migrate into one Address row each so no demo data is lost

**Scale/Scope**: New `Address` model + table, updated `Contact` model (drop 5 columns), new Pydantic schemas (`AddressCreate`/`AddressUpdate`/`AddressRead`), new nested field on `ContactRead`, new router `app/routers/addresses.py` (or extend `contacts.py` with a nested resource — see Structure Decision), updated `seed.py`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Ship-First Pragmatism**: PASS — one new table, straightforward nested CRUD, no speculative fields beyond the challenge's explicit ask (type + the location fields Contact already had).
- **II. Follow Existing Patterns**: PASS — `Address` model mirrors `Contact`'s `Mapped[]` style; `AddressCreate`/`Update`/`Read` mirror `ContactCreate`/`Update`/`Read`'s `Field(...)` + docstring style; router follows `contacts.py`'s `_get_or_404` / `HTTPException` / `responses={}` conventions.
- **III. Reviewed PR**: N/A at plan time — enforced at merge via Qodo.
- **IV. Real Relational Modeling**: PASS by construction — this is the entire point of the plan (separate `addresses` table, FK, `type` column, not bolted-on columns or JSON).
- **V. No Restart Mid-Demo**: PASS — built and merged before real demo data exists; this is the second challenge, backend not restarted after Challenge 1's data is in place until this is fully merged (per hackathon workflow: finish and merge one challenge before starting the next).
- **VI. Minimal Dependencies**: PASS — SQLAlchemy `Enum` (stdlib-adjacent, already imported package) covers type validation; no new package.

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/002-multi-address/
├── plan.md
├── data-model.md
├── quickstart.md
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
app/
├── models.py                  # New Address(Base) model; Contact drops address/city/state/postal_code/country,
│                                 gains addresses: Mapped[list["Address"]] relationship (cascade="all, delete-orphan")
├── schemas.py                  # New AddressBase/AddressCreate/AddressUpdate/AddressRead (+ AddressType enum);
│                                 ContactBase drops flat address fields; ContactRead gains addresses: list[AddressRead]
├── crud.py                     # New address CRUD functions (create/list/get/update/delete scoped to a contact)
├── routers/
│   ├── contacts.py              # Drop flat address fields from create/replace/update payload handling
│   └── addresses.py             # NEW: nested router, prefix /api/v1/contacts/{contact_id}/addresses
├── main.py                      # Register new addresses router
└── seed.py                      # SAMPLE_CONTACTS: replace flat address kwargs with one Address per contact after creation

tests/
├── test_contacts_api.py        # Update: contact payloads no longer carry flat address fields; ContactRead now has `addresses`
└── test_addresses_api.py       # NEW: create/list/get/update/delete address, cascade-delete-on-contact-delete, type validation

# Sibling repo (sf-frontend) — tracked here for context only:
src/components/AddressList.tsx   # grouped-by-type address display
src/app/contacts/[id]/edit/...   # multi-address form (add/remove/edit rows, type picker)
```

**Structure Decision**: Single-project backend change (this repo). Addresses are
modeled as a nested sub-resource under `/api/v1/contacts/{contact_id}/addresses`
(new `app/routers/addresses.py`) rather than a top-level `/api/v1/addresses`
collection, since every address acceptance scenario in `spec.md` is scoped to "a
contact's addresses" and this keeps the API surface consistent with how the frontend
will actually use it (load a contact, see/edit its addresses). `ContactRead` embeds
the full `addresses: list[AddressRead]` so a single `GET /contacts/{id}` gives the
frontend everything needed for the detail page without N+1 requests.

## Complexity Tracking

*No constitution violations — table intentionally omitted.*
