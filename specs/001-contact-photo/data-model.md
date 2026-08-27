# Data Model: Contact Photo

## Contact (modified)

Adds one field to the existing `Contact` model (`app/models.py`) and its schemas
(`app/schemas.py`). No new table.

| Field   | Type              | Nullable | Notes                                                                 |
|---------|-------------------|----------|------------------------------------------------------------------------|
| `photo` | `TEXT`            | Yes      | Base64 **WebP** data URL, e.g. `data:image/webp;base64,UklGR...`. Always WebP after server-side processing, regardless of upload format. `None` means "no photo, show initials." |

### Validation & processing rules (per Clarifications 2026-08-26)

- Accepted **upload** MIME types (parsed from the incoming data URL prefix):
  `image/jpeg`, `image/png`, `image/webp`, `image/gif`.
- Max upload size: 2 MB measured on the **decoded** bytes, checked before the image is
  even handed to Pillow.
- The declared MIME prefix is **not trusted on its own** — `app/image.py`'s
  `decode_and_recompress()` decodes the bytes with Pillow (`Image.open` +
  `.verify()`/re-open pattern) and rejects anything that isn't genuinely a decodable
  image, regardless of what the prefix claimed.
- On success, the image is resized (if needed) to a max dimension (e.g. 512px on the
  longest edge — matches the frontend's own client-side downscale, so this is a
  backstop, not the primary size reduction) and re-encoded as WebP at a reasonable
  quality setting, then re-wrapped as a `data:image/webp;base64,...` string — this is
  the value actually stored in `Contact.photo`.
- Malformed data URLs, undecodable bytes, or anything that fails Pillow verification
  are rejected with `422`.
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
