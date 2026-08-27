# Data Model: Multiple Addresses

## Address (new)

| Field         | Type                          | Nullable | Notes                                                        |
|---------------|--------------------------------|----------|---------------------------------------------------------------|
| `id`          | `Integer`, primary key         | No       |                                                                 |
| `contact_id`  | `Integer`, FK → `contacts.id`, `ON DELETE CASCADE` | No | Enforced at the DB level — SQLite FKs are already on process-wide. |
| `type`        | `Enum("home", "work", "other")` | No | Exactly one of Home/Work/Other; no other values accepted.     |
| `street`      | `String(300)`                  | Yes      | Mirrors old `Contact.address` field's length.                 |
| `city`        | `String(120)`                  | Yes      |                                                                 |
| `state`       | `String(120)`                  | Yes      |                                                                 |
| `postal_code` | `String(20)`                   | Yes      |                                                                 |
| `country`     | `String(120)`                  | Yes      |                                                                 |
| `created_at`  | `DateTime(timezone=True)`      | No       | Same pattern as `Contact.created_at`.                          |
| `updated_at`  | `DateTime(timezone=True)`      | No       | Same pattern as `Contact.updated_at`.                          |

A contact may have **zero or more** Address rows; multiple rows of the same `type`
are explicitly allowed (FR-004).

## Contact (modified)

- **Removed**: `address`, `city`, `state`, `postal_code`, `country` (moved into
  `Address`).
- **Added**: `addresses: Mapped[list["Address"]]` relationship,
  `cascade="all, delete-orphan"`, ordered by `Address.id` (insertion order — see
  Assumptions in `spec.md`).

## Relationship

```
Contact (1) ──< (many) Address
```

- FK: `Address.contact_id → Contact.id`
- Delete rule: `ON DELETE CASCADE` at the DB level (via `ondelete="CASCADE"` on the FK
  column) **and** `cascade="all, delete-orphan"` at the ORM relationship level, so
  deleting a Contact through either raw SQL or the ORM removes its addresses — no
  orphaned rows (FR-005).
- Uniqueness: none beyond the primary key. `type` is a category, not a unique
  constraint (FR-004) — two Work addresses on one contact is valid.

## Schema changes (`app/schemas.py`)

- `AddressType` — `str` `Enum`: `home`, `work`, `other`.
- `AddressBase` — `type`, `street`, `city`, `state`, `postal_code`, `country`
  (all content fields optional except `type`, mirroring `ContactBase`'s style).
- `AddressCreate(AddressBase)` — body of `POST .../addresses`.
- `AddressUpdate` — all fields optional, body of `PATCH .../addresses/{address_id}`
  (partial update, same semantics as `ContactUpdate`).
- `AddressRead(AddressBase)` — adds `id`, `contact_id`, `created_at`, `updated_at`.
- `ContactBase` — flat address fields removed.
- `ContactRead` — adds `addresses: list[AddressRead] = Field(default_factory=list)`.
- `ContactCreate`/`ContactReplace` do **not** accept nested addresses in this plan —
  addresses are created via their own endpoints after the contact exists, keeping the
  contact write contract simple. (If time allows, an optional `addresses` array on
  `ContactCreate` is a reasonable enhancement, not required by the spec.)

## Migration / seed impact

No persisted migration mechanism exists (in-memory DB, recreated on every start).
`app/seed.py` changes from setting flat `city`/`state`/`country` kwargs on
`ContactCreate` to: create the contact, then create one `Address` (`type="home"`)
per seeded contact using its previous location values — satisfying spec.md User
Story 3 (no data loss on the demo dataset) without needing a real ALTER/migration
script.
