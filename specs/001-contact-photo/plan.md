# Implementation Plan: Contact Photo

**Branch**: `feat/contact-photo` | **Date**: 2026-08-26 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-contact-photo/spec.md`

## Summary

Add an optional `photo` field to the `Contact` record, stored as a base64 WebP data-URL
string (no file storage needed since the DB is in-memory). Backend: add the column,
thread it through all four schemas and both write paths (POST/PUT/PATCH), and — per
`spec.md`'s Clarifications — decode and verify the uploaded bytes are a real image,
then re-encode to WebP before storing, so both list and detail responses can safely
return the full photo. Frontend (sibling repo, not built from this plan): a photo
upload control that downscales client-side before submit, and a shared `Avatar`
component (circular photo or initials fallback) used in the list and detail views.

## Technical Context

**Language/Version**: Python 3.11+ (backend, this repo); TypeScript/Next.js (frontend, sibling repo `sf-frontend`, out of scope for this plan/tasks file)

**Primary Dependencies**: FastAPI, SQLAlchemy 2.0, Pydantic v2 (existing); **Pillow (new)** — needed to decode/verify uploaded image bytes and re-encode to WebP, per the Clarifications answer to reject a MIME-prefix-only trust model. This is a deliberate, justified exception to Constitution VI (Minimal Dependencies) — see Complexity Tracking.

**Storage**: In-memory SQLite via SQLAlchemy (existing `app/database.py`); photo stored as a `TEXT` column holding a base64 **WebP** data URL (post-verification, post-compression — see Data Model)

**Testing**: pytest (existing `tests/test_contacts_api.py` pattern — request/response assertions against the FastAPI `TestClient`)

**Target Platform**: Local dev server (`127.0.0.1:8000`), same as the rest of the app

**Project Type**: web-service (backend) + web-app (frontend, sibling repo)

**Performance Goals**: N/A beyond existing API latency; a single request must handle a ~2 MB base64 payload without noticeable delay; Pillow decode+re-encode of one small (client-downscaled) image is well under 100ms

**Constraints**: Max upload size 2 MB (pre-encoding) enforced server-side; accepted upload types JPEG/PNG/WebP/GIF, decoded and verified with Pillow (not just the declared MIME prefix), then re-encoded to WebP for storage; `GET /api/v1/contacts` (list) and `GET /api/v1/contacts/{id}` (detail) both return the full (now-small) photo — no separate summary schema; no new backend restart required after this ships (constitution principle V)

**Scale/Scope**: 3 seeded demo contacts; single-field addition plus a compression step, touches `models.py`, `schemas.py`, `crud.py`, `seed.py`, `requirements.txt`, and the existing contact tests

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Ship-First Pragmatism**: PASS — one nullable string column, no new tables, no new endpoints; the decode/compress step is a single helper function, not a subsystem.
- **II. Follow Existing Patterns**: PASS — `photo` added to `ContactBase`/`Contact` exactly like every other optional field (`Field(default=None, description=..., examples=...)`, `Mapped[str | None]`).
- **III. Reviewed PR**: N/A at plan time — enforced at merge time via Qodo `/review` + `/improve`.
- **IV. Real Relational Modeling**: N/A — photo is a scalar attribute of Contact, not a one-to-many relationship.
- **V. No Restart Mid-Demo**: PASS — this is the first challenge, built and merged before any demo data is seeded for real.
- **VI. Minimal Dependencies**: **VIOLATION, justified** — adding Pillow to actually decode/verify/re-encode images. See Complexity Tracking below.

Re-check after design: still holds — the only deviation is the documented Pillow addition.

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
├── schemas.py             # ContactBase.photo, ContactUpdate.photo (+ field_validator calling image.py)
├── image.py                # NEW: decode_and_recompress(data_url: str) -> str — Pillow decode/verify,
│                             resize to a max dimension, re-encode WebP, re-wrap as a data URL; raises
│                             ValueError on invalid/corrupt/oversized input (caught by the schema validator)
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

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| New dependency: Pillow | The Clarifications session explicitly resolved that the backend must decode and verify uploaded bytes are genuine image data (not trust a declared MIME prefix), and must re-encode to WebP so list responses stay light — neither is doable with the stdlib. | Trusting the data-URL's declared MIME prefix (the original, dependency-free plan) was rejected during clarification in favor of real verification + compression; hand-rolling image format sniffing/decoding without a library is far more code and far less correct than one well-known dependency. |
