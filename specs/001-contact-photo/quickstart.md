# Quickstart: Contact Photo

Manual verification once the feature is implemented, mirroring the acceptance
scenarios in `spec.md`.

## Backend only (this repo)

```bash
.venv/bin/python -m app.main
```

1. Create a contact with a photo:

   ```bash
   curl -X POST http://127.0.0.1:8000/api/v1/contacts \
     -H "Content-Type: application/json" \
     -d '{
       "first_name": "Ada",
       "last_name": "Lovelace",
       "email": "ada2@example.com",
       "photo": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
     }'
   ```

   Expect `201` with `"photo"` echoed back in the response.

2. Oversized/invalid photo is rejected:

   ```bash
   curl -X POST http://127.0.0.1:8000/api/v1/contacts \
     -H "Content-Type: application/json" \
     -d '{"first_name":"Bad","last_name":"Photo","email":"bad@example.com","photo":"not-a-data-url"}'
   ```

   Expect `422`.

3. PUT (full replace) without `photo` clears it — confirms the backend contract
   documented in `data-model.md`:

   ```bash
   curl -X PUT http://127.0.0.1:8000/api/v1/contacts/1 \
     -H "Content-Type: application/json" \
     -d '{"first_name":"Ada","last_name":"Lovelace","email":"ada2@example.com"}'
   ```

   Expect `"photo": null` in the response — this is why the frontend edit form must
   carry the photo through.

## Full stack (with sf-frontend running against this backend)

1. Open the app, create a contact, upload a photo (a common JPEG/PNG under 2 MB).
2. Confirm the contact list shows a circular cropped avatar for that contact.
3. Open a contact with no photo — confirm it shows an initials circle, same size/shape.
4. Edit the photo-having contact's phone number only (not touching the photo field in
   the UI) and save — confirm the photo is still present afterward.
5. Clear the photo on a contact and save — confirm it falls back to initials.
