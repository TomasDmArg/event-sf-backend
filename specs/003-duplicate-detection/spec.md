# Feature Specification: Duplicate Contact Detection

**Feature Branch**: `feat/duplicate-detection`

**Created**: 2026-08-26

**Status**: Draft

**Input**: User description: "Bonus feature: detect likely-duplicate contacts (same email/phone/similar name) and offer a merge action that combines addresses/photo."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Detect likely duplicate contacts (Priority: P1)

As a user, I want the app to flag contacts that look like duplicates of each other
(matching email, matching phone, or very similar name) so I don't end up with
fragmented, redundant contact records.

**Why this priority**: This is the detection half of the feature and the part that
must exist before merge makes sense.

**Independent Test**: Create two contacts with the same email (or same phone, or
near-identical names); confirm the app surfaces them as a likely-duplicate pair
somewhere the user will see it (e.g. a "possible duplicates" view or an inline flag on
the contact).

**Acceptance Scenarios**:

1. **Given** two contacts with the exact same email address, **When** duplicate
   detection runs, **Then** the pair is flagged as a likely duplicate with "matching
   email" as the reason.
2. **Given** two contacts with the exact same phone number, **When** duplicate
   detection runs, **Then** the pair is flagged as a likely duplicate with "matching
   phone" as the reason.
3. **Given** two contacts with very similar but not identical names (e.g. "Jon Smith"
   vs "John Smith"), **When** duplicate detection runs, **Then** the pair is flagged
   as a likely duplicate with "similar name" as the reason.
4. **Given** two contacts with clearly different email, phone, and name, **When**
   duplicate detection runs, **Then** they are not flagged.

---

### User Story 2 - Merge two duplicate contacts (Priority: P1)

As a user reviewing a flagged duplicate pair, I want to merge them into one contact,
combining their addresses and keeping a photo, so I end up with a single clean record
instead of manually copying data and deleting one by hand.

**Why this priority**: Detection alone doesn't resolve anything; merge is what makes
the feature actually useful and demoable end-to-end.

**Independent Test**: From a flagged duplicate pair (one with a photo and one or more
addresses, the other with different addresses), trigger merge; confirm the resulting
single contact has the union of both contacts' addresses, a photo (if either had one),
and the other contact record no longer exists.

**Acceptance Scenarios**:

1. **Given** a flagged duplicate pair where one contact has a photo and the other does
   not, **When** the user merges them, **Then** the resulting contact has the photo.
2. **Given** a flagged duplicate pair where each contact has different addresses,
   **When** the user merges them, **Then** the resulting contact has the union of all
   addresses from both (no duplicates dropped, no addresses lost).
3. **Given** a flagged duplicate pair, **When** the user merges them, **Then** exactly
   one contact remains afterward and the other is deleted.
4. **Given** a flagged duplicate pair with conflicting scalar fields (e.g. different
   job titles), **When** the user merges them, **Then** the user is able to see the
   conflict and choose which value survives, rather than one silently overwriting the
   other with no visibility.

### Edge Cases

- What happens when a contact is flagged as a possible duplicate of more than one
  other contact? Each pair is shown independently; merging one pair does not affect
  the other flagged pair until the user acts on it too.
- What happens when the user dismisses a flagged pair as "not a duplicate"? The pair
  is no longer surfaced as a suggestion (for this session at minimum).
- What happens when both contacts in a pair have a photo? The user's chosen "primary"
  contact's photo wins by default, but this is visible/overridable at merge time, not
  silent.
- What happens when both contacts have an address of the same type (e.g. both have a
  Home address)? Both are kept post-merge (addresses are additive, not deduplicated by
  type) unless they are exact duplicates of each other, in which case only one is
  kept.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST identify contact pairs as likely duplicates when they share
  an identical email address.
- **FR-002**: System MUST identify contact pairs as likely duplicates when they share
  an identical phone number.
- **FR-003**: System MUST identify contact pairs as likely duplicates when their full
  names are highly similar (fuzzy match) without being identical.
- **FR-004**: System MUST surface the specific reason(s) a pair was flagged (matching
  email / matching phone / similar name).
- **FR-005**: System MUST allow the user to merge a flagged pair into a single
  contact.
- **FR-006**: Merge MUST combine addresses from both contacts into the resulting
  contact (union, deduplicated only when an address is an exact duplicate).
- **FR-007**: Merge MUST retain a photo on the resulting contact if either source
  contact had one, with the user able to pick which one wins when both have a photo.
- **FR-008**: Merge MUST let the user resolve conflicts on scalar fields (e.g. job
  title, company) that differ between the two contacts, rather than picking silently.
- **FR-009**: After a successful merge, exactly one contact MUST remain and the other
  MUST no longer exist in the system.
- **FR-010**: System MUST allow the user to dismiss a flagged pair without merging.

### Key Entities

- **Contact**: Existing entity (now with Photo and Addresses from prior features);
  merge target and merge source.
- **Duplicate Candidate Pair**: A computed (not persisted) association between two
  contacts, with one or more reasons (email/phone/name) and a similarity signal — not
  a stored entity, derived at query/view time from existing contact data.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Two contacts sharing an exact email or phone are flagged as duplicates
  100% of the time.
- **SC-002**: Merging a flagged pair never loses an address or photo that existed on
  either source contact (0% data loss across the merge).
- **SC-003**: A user can go from "two duplicate contacts exist" to "one clean merged
  contact" in a single guided flow without manually copying field values.
- **SC-004**: Clearly distinct contacts (no shared email/phone, dissimilar names) are
  never flagged as duplicates (0% false positives on the demo dataset).

## Assumptions

- "Similar name" uses a lightweight fuzzy-match approach (e.g. normalized string
  distance) computed on demand — no external service or ML model, consistent with the
  Minimal Dependencies principle.
- Duplicate detection runs on demand (e.g. when viewing a "possible duplicates" list)
  rather than as a background job, since the backend has no persistence across
  restarts and the demo dataset is small.
- This feature spans both the backend (this repo: detection endpoint, merge endpoint)
  and the sibling frontend repo (duplicates view, merge UI with conflict picker); this
  spec covers the full user-facing behavior, and the implementation plan will split
  work by repo.
- This is the bonus/stretch feature, built only after Challenge 1 and Challenge 2 are
  each merged and demoable.
- Because `Contact.email` is unique (enforced today via `_reject_duplicate_email` in
  `app/routers/contacts.py`), two contacts can never actually share an *exact* email
  under normal use — in practice the "matching email" detection path only fires if
  that constraint is ever relaxed or bypassed; the demo should rely on matching phone
  and/or similar name to reliably show a flagged pair.
