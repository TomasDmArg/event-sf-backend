# Feature Specification: Contact Photo

**Feature Branch**: `feat/contact-photo`

**Created**: 2026-08-26

**Status**: Draft

**Input**: User description: "Let users add a photo to a contact. Bonus points for showing it as a circular profile image, LinkedIn style. If a contact has no photo, keep showing their initials."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add a photo to a contact (Priority: P1)

As a user of the contacts app, I want to attach a photo to a contact so that I can
recognize them visually instead of relying on their name alone.

**Why this priority**: This is the entire challenge. Without it there is nothing to
demo.

**Independent Test**: Create or edit a contact, upload an image, save, and confirm the
photo persists and reloads correctly on the contact detail and list views.

**Acceptance Scenarios**:

1. **Given** a contact with no photo, **When** the user uploads an image and saves,
   **Then** the contact's photo is stored and shown wherever that contact appears.
2. **Given** a contact that already has a photo, **When** the user uploads a new image
   and saves, **Then** the old photo is replaced by the new one.
3. **Given** a contact with a photo, **When** the user edits any other field (e.g.
   phone number) through the edit form and saves, **Then** the photo is still present
   afterward (not silently cleared).

---

### User Story 2 - Circular avatar with initials fallback (Priority: P1)

As a user browsing contacts, I want a consistent circular avatar for every contact —
their photo if they have one, or their initials if they don't — so the UI looks
polished and predictable.

**Why this priority**: Explicitly called out for bonus points and is the primary UI
polish judged in the demo.

**Independent Test**: View the contact list and detail page for one contact with a
photo and one without; confirm both render a circular avatar of consistent size, one
showing the image, the other showing initials.

**Acceptance Scenarios**:

1. **Given** a contact with a photo, **When** their avatar renders anywhere in the UI,
   **Then** it displays as a circular, cropped image (not stretched/distorted).
2. **Given** a contact with no photo, **When** their avatar renders, **Then** it shows
   a circle containing their initials (first letter of first name + first letter of
   last name).
3. **Given** a contact's photo is removed, **When** the avatar re-renders, **Then** it
   falls back to the initials circle.

---

### User Story 3 - Remove a contact's photo (Priority: P3)

As a user, I want to remove a contact's photo (e.g. it was wrong) and have them fall
back to initials, without deleting the contact.

**Why this priority**: Not explicitly required by the challenge, but a natural
counterpart to "add a photo" and cheap to support given the same field is used for
both add and replace.

**Independent Test**: On a contact with a photo, clear the photo field and save;
confirm the avatar reverts to initials.

**Acceptance Scenarios**:

1. **Given** a contact with a photo, **When** the user explicitly clears the photo and
   saves, **Then** the contact has no photo and displays initials.

### Edge Cases

- What happens when the uploaded file is not an image (wrong content type)? System
  rejects it with a clear error before it's stored.
- What happens when the uploaded image is very large? System enforces a maximum file
  size and rejects oversized uploads with a clear error rather than accepting and
  degrading performance.
- What happens when a contact has only a first name's worth of usable initial (e.g.
  single-character name)? Initials fall back to whatever characters are available
  (at least one).
- What happens on the full-replace edit form (PUT) if the photo field is omitted?
  Per the "no silent wipe" acceptance scenario above, the edit form must always carry
  the current photo value through, even when the user didn't change it.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow a photo to be attached to a contact at creation time
  or via edit.
- **FR-002**: System MUST allow an existing contact photo to be replaced with a new
  one.
- **FR-003**: System MUST allow an existing contact photo to be removed, reverting
  the contact to the initials fallback.
- **FR-004**: System MUST persist the photo as part of the contact record so it
  survives page reloads and navigation (but not a backend process restart, since the
  store is in-memory — see Assumptions).
- **FR-005**: System MUST render a circular, cropped avatar for every contact in both
  the list view and the detail view.
- **FR-006**: System MUST show an initials-based fallback avatar for any contact
  without a photo, using consistent sizing/shape with the photo avatar.
- **FR-007**: System MUST validate that an uploaded photo is an image file before
  accepting it.
- **FR-008**: System MUST enforce a maximum photo file size and reject uploads that
  exceed it with a clear, user-visible error.
- **FR-009**: The contact edit (full-replace) flow MUST carry forward the current
  photo value when the user does not change it, so editing unrelated fields never
  wipes the photo.

### Key Entities

- **Contact**: Existing entity, gains a photo attribute (present or absent) alongside
  its current fields.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can add a photo to a contact and see it rendered as a circular
  avatar within one save action (no page reload required beyond the normal
  create/edit flow).
- **SC-002**: 100% of contacts without a photo show a legible initials avatar instead
  of a broken image or blank space.
- **SC-003**: Editing an unrelated field on a photo-bearing contact never results in
  photo loss (0% regression on the "silent wipe" edge case called out in the
  challenge hints).
- **SC-004**: Oversized or non-image uploads are rejected with a clear error message
  in under 1 second, without corrupting the contact record.

## Assumptions

- The backend database is in-memory (SQLite), so the simplest and sufficient storage
  approach is a base64-encoded image string field on the Contact record — no file
  storage/blob service needed for this challenge.
- A reasonable max photo size is 2 MB before base64 encoding, enforced on both
  frontend (pre-upload check) and backend (defense in depth).
- Accepted image types are the common web formats: JPEG, PNG, WebP, GIF.
- "Circular, LinkedIn style" means `rounded-full`, fixed aspect-square dimensions, and
  `object-cover` cropping so non-square source images don't distort.
- This feature spans both the backend (this repo: photo field + validation) and the
  sibling frontend repo (upload UI + avatar component); this spec covers the full
  user-facing behavior, and the implementation plan will split work by repo.
