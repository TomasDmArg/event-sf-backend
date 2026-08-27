# Implementation Plan: Duplicate Contact Detection

**Branch**: `feat/duplicate-detection` | **Date**: 2026-08-26 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/003-duplicate-detection/spec.md`

## Summary

Add a read-only "possible duplicates" endpoint that scans all contacts pairwise and
flags pairs sharing an email, phone, or a fuzzy-similar name, and a merge endpoint
that folds one contact into another (union of addresses, photo fallback, caller-chosen
resolution for conflicting scalar fields), deleting the losing contact. No new table —
duplicate candidates are computed on demand, not persisted (per spec.md Key Entities).

## Technical Context

**Language/Version**: Python 3.11+ (backend, this repo); TypeScript/Next.js (frontend, sibling repo, out of scope here)

**Primary Dependencies**: FastAPI, SQLAlchemy 2.0, Pydantic v2, `difflib.SequenceMatcher` (Python stdlib) for name similarity — no new package, per constitution VI

**Storage**: In-memory SQLite; reads existing `Contact`/`Address` tables, no schema change

**Testing**: pytest, new `tests/test_duplicates_api.py`

**Target Platform**: Local dev server, same as rest of the app

**Project Type**: web-service (backend) + web-app (frontend, sibling repo)

**Performance Goals**: N/A — pairwise scan over a handful of demo contacts is trivially fast; not built to scale beyond hackathon dataset sizes

**Constraints**: Merge must be atomic from the client's point of view (one request, one transaction) and must not lose any address or photo (spec.md SC-002); this is the bonus feature and is only started after Challenges 1 and 2 are each merged

**Scale/Scope**: One new router (`app/routers/duplicates.py`), a small `crud.py` addition for the merge operation, two new response schemas — no model/table changes

## Constitution Check

- **I. Ship-First Pragmatism**: PASS — on-demand computation, no persisted "duplicate" entity, no admin UI beyond what's needed to demo.
- **II. Follow Existing Patterns**: PASS — new router follows `contacts.py`'s structure; schemas follow existing `Field(...)` + docstring style.
- **III. Reviewed PR**: N/A at plan time — enforced at merge via Qodo.
- **IV. Real Relational Modeling**: N/A — no new one-to-many relationship introduced; reuses the Contact/Address model from Challenge 2.
- **V. No Restart Mid-Demo**: PASS — built last, after both prior challenges are merged and (per hackathon rule) before the final demo, no restart after this either.
- **VI. Minimal Dependencies**: PASS — `difflib` is stdlib.

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/003-duplicate-detection/
├── plan.md
├── quickstart.md
└── checklists/
    └── requirements.md
```

(No separate `data-model.md` — no new persisted entity; the "Duplicate Candidate Pair"
key entity from spec.md is a computed response shape, documented inline below.)

### Source Code (repository root)

```text
app/
├── crud.py                       # find_duplicate_candidates(db) -> list of (contact, contact, reasons);
│                                    merge_contacts(db, primary_id, secondary_id, resolutions) -> Contact
├── schemas.py                     # DuplicateReason enum, DuplicateCandidate, DuplicateCandidateList,
│                                    MergeRequest (field resolutions + which photo wins)
├── routers/duplicates.py          # NEW: GET /api/v1/contacts/duplicates, POST /api/v1/contacts/merge
└── main.py                        # Register new router

tests/
└── test_duplicates_api.py        # NEW: detection reasons, merge union of addresses/photo, conflict resolution, dismiss

# Sibling repo (sf-frontend) — tracked here for context only:
src/app/duplicates/page.tsx        # possible-duplicates list with reasons + merge action
src/components/MergeConflictModal.tsx  # scalar-field conflict picker
```

**Structure Decision**: Single-project backend change (this repo), a new
non-nested collection endpoint (`/api/v1/contacts/duplicates`,
`/api/v1/contacts/merge`) rather than a resource under a single contact, since a
duplicate pair spans two contacts and doesn't belong to either one specifically.

## Complexity Tracking

*No constitution violations — table intentionally omitted.*
