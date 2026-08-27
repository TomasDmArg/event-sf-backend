# Implementation Plan: Contact Photo

**Branch**: `feat/contact-photo` | **Date**: 2026-08-26 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-contact-photo/spec.md`

## Summary

Add an optional `photo` field to the `Contact` record, stored as a base64 data-URL
string (no file storage needed since the DB is in-memory). Backend: add the column,
thread it through all four schemas and both write paths (POST/PUT/PATCH), validate
type/size. Frontend (sibling repo, not built from this plan): a photo upload control
on the create/edit form and a shared `Avatar` component (circular photo or initials
fallback) used in the list and detail views.

## Technical Context

**Language/Version**: Python 3.11+ (backend, this repo); TypeScript/Next.js (frontend, sibling repo `sf-frontend`, out of scope for this plan/tasks file)

**Primary Dependencies**: FastAPI, SQLAlchemy 2.0, Pydantic v2 (all already in `requirements.txt` — no new dependency)

**Storage**: In-memory SQLite via SQLAlchemy (existing `app/database.py`); photo stored as a `TEXT` column holding a base64 data URL

**Testing**: pytest (existing `tests/test_contacts_api.py` pattern — request/response assertions against the FastAPI `TestClient`)

**Target Platform**: Local dev server (`127.0.0.1:8000`), same as the rest of the app

**Project Type**: web-service (backend) + web-app (frontend, sibling repo)

**Performance Goals**: N/A beyond existing API latency; a single request must handle a ~2 MB base64 payload without noticeable delay

**Constraints**: Max photo size 2 MB (pre-encoding) enforced server-side in a Pydantic validator; accepted types JPEG/PNG/WebP/GIF sniffed from the data URL's declared MIME type; no new backend restart required after this ships (constitution principle V)

**Scale/Scope**: 3 seeded demo contacts; single-field addition, touches `models.py`, `schemas.py`, `crud.py`, `seed.py`, and the existing contact tests

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Ship-First Pragmatism**: PASS — one nullable string column, no new tables, no new endpoints.
- **II. Follow Existing Patterns**: PASS — `photo` added to `ContactBase`/`Contact` exactly like every other optional field (`Field(default=None, description=..., examples=...)`, `Mapped[str | None]`).
- **III. Reviewed PR**: N/A at plan time — enforced at merge time via Qodo `/review` + `/improve`.
- **IV. Real Relational Modeling**: N/A — photo is a scalar attribute of Contact, not a one-to-many relationship.
- **V. No Restart Mid-Demo**: PASS — this is the first challenge, built and merged before any demo data is seeded for real.
- **VI. Minimal Dependencies**: PASS — base64 handling and MIME sniffing use Python stdlib (`base64`, string prefix check on the data URL); no new package.

No violations. Re-check after design: still PASS (see Project Structure below — no structural surprises).

## Project Structure

### Documentation (this feature)

```text
specs/001-contact-photo/
├── plan.md              # This file
├── data-model.md         # Phase 1 output
├── quickstart.md         # Phase 1 output
└── checklists/
    └── requirements.md
```

(No `contracts/` directory — the only contract change is additive fields on the
existing `/api/v1/contacts` endpoints, already fully described by the updated
Pydantic schemas plus `quickstart.md`'s example requests.)

### Source Code (repository root)

```text
app/
├── models.py             # Contact.photo: Mapped[str | None] = mapped_column(Text)
├── schemas.py             # ContactBase.photo, ContactUpdate.photo (+ size/type validators)
├── crud.py                 # No change — generic field handling already covers new columns
├── seed.py                  # No change required (seed contacts may stay photo-less)
└── routers/contacts.py     # No change — generic pass-through already covers new field

tests/
└── test_contacts_api.py   # Add cases: create/update with photo, oversized/invalid rejected,
                             # PUT without photo field behavior documented (see Data Model)

# Sibling repo (sf-frontend) — tracked here for context only, not built from this plan:
src/components/Avatar.tsx        # circular photo or initials fallback
src/app/contacts/[id]/edit/...   # photo upload control, carries current photo through PUT
```

**Structure Decision**: Single-project backend change (Option 1-style, this repo
only) — everything lives in the existing flat `app/` package alongside the current
Contact fields, no new module. The frontend half of this feature is a separate PR in
`sf-frontend` and is out of scope for this plan/tasks pair.

## Complexity Tracking

*No constitution violations — table intentionally omitted.*
