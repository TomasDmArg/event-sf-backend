# Roast My PR Contacts Backend Constitution

## Core Principles

### I. Ship-First Pragmatism
Optimize for a working, demoable feature within the 2-hour time box over completeness
or architectural purity. No speculative generality, no unused scaffolding, no
half-finished implementations. A bug fix or small feature does not need surrounding
cleanup; a one-shot script does not need a reusable helper. If it isn't needed for the
current challenge or demo, don't build it.

### II. Follow Existing Patterns
New code (SQLAlchemy models, Pydantic schemas, CRUD functions, router handlers) MUST
match the conventions already established in `app/models.py`, `app/schemas.py`,
`app/crud.py`, and `app/routers/contacts.py`: SQLAlchemy 2.0 `Mapped[]`-style columns,
Pydantic v2 `Field(...)` with `description` and `examples`, full docstrings on schema
classes, and the existing error/response shapes (`ErrorResponse`, `404`/`409`/`422`
patterns). Consistency with what's already in the repo beats a "better" pattern
introduced only for the new feature.

### III. Every Feature Ships Through a Reviewed PR
No direct pushes to `main`. Every feature branch opens a PR against the fork's own
`main`, gets a Qodo `/review` and at least one `/improve` pass, and either applies the
suggestion or replies explaining why not, before merging. The review loop is part of
the deliverable, not a formality to skip for speed.

### IV. Real Relational Modeling for One-to-Many Data
Relationships that are genuinely one-to-many (e.g. Contact → Address) MUST be modeled
as a separate table with a foreign key back to the parent and an explicit type/kind
column where relevant. Never model one-to-many data as bolted-on columns
(`address2`, `address3`) or a JSON blob field. This is a scored judging criterion, not
just good practice.

### V. No Backend Restarts Once Demo Data Exists
The database is in-memory SQLite; a restart wipes all contacts, photos, and addresses.
Once demo data is seeded, avoid any change that requires restarting the backend
process (schema changes, env var changes) — do those earlier, and re-seed demo data
only after the last restart before presenting.

### VI. Minimal Dependencies
Do not add a new Python or JS library unless the task cannot reasonably be done with
what's already in `requirements.txt` / `pyproject.toml` (backend) or `package.json`
(frontend). Prefer stdlib/base64/existing Tailwind utilities over pulling in an image
library, file-upload library, or UI kit for a 2-hour build.

## Development Workflow

Each challenge is its own feature branch and its own PR:
`feat/contact-photo` → `feat/multi-address` → `feat/<bonus-feature-name>`. Challenge 1
is finished, reviewed, and merged before Challenge 2 begins; a single merged, polished
PR beats two half-finished branches. Backend and frontend changes for the same
challenge may ship as separate PRs (one per repo) but should be scoped to land
together. Every PR gets `/review`, then `/improve`, before merge; commit messages and
PR descriptions may be generated with `/describe` and edited for accuracy.

## Governance

This constitution governs the hackathon build described above. Amendments are informal
given the time box — update this file directly if a principle stops fitting reality,
no separate approval process required. When a spec, plan, or task conflicts with a
principle here, the principle wins unless there's a documented reason (e.g. a Qodo
suggestion that's deliberately not applied) noted in the relevant PR.

**Version**: 1.0.0 | **Ratified**: 2026-08-26 | **Last Amended**: 2026-08-26
