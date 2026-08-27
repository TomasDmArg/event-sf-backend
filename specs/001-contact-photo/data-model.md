# Data Model: Contact Photo

## Contact (modified)

Adds one field to the existing `Contact` model (`app/models.py`) and its schemas
(`app/schemas.py`). No new table.

| Field   | Type              | Nullable | Notes                                                                 |
|---------|-------------------|----------|------------------------------------------------------------------------|
| `photo` | `TEXT`            | Yes      | Base64 data URL, e.g. `data:image/png;base64,iVBORw0KG...`. `None` means "no photo, show initials." |

### Validation rules

- Accepted MIME types (parsed from the data URL prefix): `image/jpeg`, `image/png`,
  `image/webp`, `image/gif`.
- Max size: 2 MB measured on the **decoded** bytes (reject before it ever reaches the
  DB), enforced by a Pydantic `field_validator` on `photo` in `ContactBase`.
- Malformed data URLs (wrong prefix, invalid base64) are rejected with `422`.
- `None`/omitted is always valid (no photo).

### Schema changes

- `ContactBase.photo: str | None` — inherited by `ContactCreate` and `ContactReplace`,
  so both creation and full-replace can set/clear it.
- `ContactUpdate.photo: str | None` — present so PATCH can also set/clear it
  explicitly, consistent with every other optional field on that schema.
- `ContactRead.photo: str | None` — returned as-is (frontend renders directly as an
  `<img src>`).

### Full-replace (PUT) behavior — the trap called out in the challenge hints

`ContactReplace` is a full replacement: any field the client omits is written as
`None`. This is already true for every other optional field (`phone`, `company`,
etc.) and photo is no exception at the **backend** contract level — the backend does
not special-case photo to "preserve if omitted." The responsibility for not wiping the
photo sits with the **frontend edit form**, which must pre-fill the photo field from
the currently-loaded contact and re-send it on every PUT. This is documented here so
it isn't missed when the sibling frontend PR is built, and is covered by an explicit
acceptance scenario in `spec.md` (User Story 1, scenario 3).

## Migration / seed impact

No migration needed — this is an additive nullable column on an in-memory schema
that's recreated fresh on every backend start (`app/database.py`). Seeded contacts in
`app/seed.py` simply have `photo=None` by default (initials fallback), unless the
implementer chooses to seed a sample photo for demo polish — optional, not required.
