# Feature Specification: Multiple Addresses

**Feature Branch**: `feat/multi-address`

**Created**: 2026-08-26

**Status**: Draft

**Input**: User description: "Right now each contact has exactly one address. Change it so a contact can have many addresses, each with a type: Home, Work, or Other. This one tests whether your AI tooling actually models the one-to-many relationship correctly."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add multiple addresses to a contact (Priority: P1)

As a user, I want to record more than one address for a contact (e.g. their home and
their office) so the contact record reflects reality instead of forcing me to pick
just one.

**Why this priority**: This is the core of the challenge; without it there's nothing
to demo or judge for one-to-many correctness.

**Independent Test**: On a contact, add a Home address and a Work address; reload the
contact detail page and confirm both are present with their correct type labels.

**Acceptance Scenarios**:

1. **Given** a contact with zero addresses, **When** the user adds a Home address,
   **Then** the contact shows exactly one address, labeled Home.
2. **Given** a contact with one address, **When** the user adds a second address of a
   different type, **Then** the contact shows both addresses, each with its own type
   label.
3. **Given** a contact with multiple addresses, **When** the user views the contact
   detail page, **Then** addresses are grouped or clearly labeled by type (Home, Work,
   Other) rather than shown as an undifferentiated list.

---

### User Story 2 - Edit and remove individual addresses (Priority: P2)

As a user, I want to edit or delete a single address on a contact without affecting
that contact's other addresses.

**Why this priority**: Necessary for the feature to be usable beyond a one-time add;
also the strongest signal of correct one-to-many modeling (each address is an
independent record with its own identity).

**Independent Test**: On a contact with two addresses, edit one and confirm the other
is untouched; delete one and confirm the other remains.

**Acceptance Scenarios**:

1. **Given** a contact with a Home and a Work address, **When** the user edits the
   Work address's street, **Then** the Home address is unchanged.
2. **Given** a contact with two addresses, **When** the user deletes one, **Then** the
   contact retains exactly the other one, and the deleted address no longer appears
   anywhere.
3. **Given** a contact with one address, **When** the user changes its type from Home
   to Other, **Then** the address's content is preserved and only its type changes.

---

### User Story 3 - Migrate existing single-address contacts (Priority: P2)

As a user with existing seeded contacts (each having the legacy single address
fields), I want those addresses to show up correctly under the new multi-address
model instead of disappearing.

**Why this priority**: Without this, the demo's seeded contacts silently lose their
address data, which would look like a regression to judges.

**Independent Test**: Start the backend fresh with seed data; confirm each seeded
contact's original address appears as one Address record of a sensible default type.

**Acceptance Scenarios**:

1. **Given** the backend starts with its seeded contacts (each having legacy single
   address fields), **When** the API is queried, **Then** each contact's original
   address is present as one Address entry (default type: Home) rather than lost.

### Edge Cases

- What happens when a contact has zero addresses? Detail page shows a clear empty
  state, not an error or blank section.
- What happens when a user tries to add an address with an invalid/unsupported type?
  Request is rejected with a validation error; only Home, Work, Other are accepted.
- What happens when a contact has multiple addresses of the same type (e.g. two Work
  addresses)? This MUST be allowed — type is a category, not a uniqueness constraint.
- What happens to a contact's addresses when the contact itself is deleted? All of
  that contact's addresses are deleted along with it (no orphaned address records).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow a contact to have zero, one, or many addresses.
- **FR-002**: Each address MUST have a type of exactly one of: Home, Work, Other.
- **FR-003**: System MUST allow addresses to be added, edited, and deleted
  independently of one another and of the rest of the contact record.
- **FR-004**: System MUST allow multiple addresses of the same type on one contact.
- **FR-005**: System MUST cascade-delete a contact's addresses when the contact is
  deleted, leaving no orphaned address records.
- **FR-006**: System MUST reject an address with a type outside the allowed set
  (Home/Work/Other) with a validation error.
- **FR-007**: The contact detail view MUST present addresses grouped or clearly
  labeled by type rather than as an unlabeled flat list.
- **FR-008**: Existing seeded/legacy single-address contact data MUST be represented
  under the new model without data loss (each becomes one Address record).
- **FR-009**: Address content fields (street, city, state, postal code, country) MUST
  match the granularity already used by the legacy single-address fields on Contact.

### Key Entities

- **Contact**: Existing entity; no longer owns address fields directly — instead owns
  zero or more Address records.
- **Address**: New entity representing one physical address belonging to exactly one
  contact. Attributes: type (Home/Work/Other), street, city, state, postal code,
  country. Independently identifiable, editable, and deletable.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A contact can hold 2+ addresses of different (or the same) type
  simultaneously, verified via the API and the UI.
- **SC-002**: Editing or deleting one address never modifies or removes a sibling
  address on the same contact (0% cross-contamination across 100% of test edits).
- **SC-003**: The data model uses a genuine one-to-many relationship (separate table +
  foreign key), not additional flat columns or a serialized blob — verifiable by
  inspecting the schema.
- **SC-004**: Seeded demo contacts retain their original address data after the
  migration, with zero data loss.

## Assumptions

- A dedicated `Address` table with a foreign key to `Contact` and a `type` enum/string
  column (Home/Work/Other) is the correct model — per the challenge's explicit
  guidance, `address2`/`address3`-style columns or a JSON blob are out of scope and
  considered incorrect.
- The legacy single `address`/`city`/`state`/`postal_code`/`country` fields on Contact
  are removed (or deprecated) in favor of the new Address relationship, with a
  one-time migration of existing values into a single default "Home" Address per
  contact — since the database is in-memory, this migration happens in the seed data
  logic, not a persisted schema migration.
- This feature spans both the backend (this repo: Address model, FK, CRUD,
  cascade-delete) and the sibling frontend repo (multi-address form UI, grouped
  display); this spec covers the full user-facing behavior, and the implementation
  plan will split work by repo.
- Ordering of addresses within a type is not significant for this feature (insertion
  order is acceptable).
