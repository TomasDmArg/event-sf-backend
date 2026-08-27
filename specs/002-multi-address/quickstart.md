# Quickstart: Multiple Addresses

## Backend only (this repo)

```bash
.venv/bin/python -m app.main
```

1. Confirm seeded contacts kept their address (migrated, per data-model.md):

   ```bash
   curl http://127.0.0.1:8000/api/v1/contacts/1
   ```

   Expect `"addresses": [{"type": "home", "city": "San Francisco", ...}]`.

2. Add a second address of a different type:

   ```bash
   curl -X POST http://127.0.0.1:8000/api/v1/contacts/1/addresses \
     -H "Content-Type: application/json" \
     -d '{"type": "work", "street": "1 Market St", "city": "San Francisco", "state": "CA", "country": "USA"}'
   ```

   Expect `201`; `GET /api/v1/contacts/1` now shows two addresses.

3. Add a second Work address (same type twice — must succeed, per FR-004):

   ```bash
   curl -X POST http://127.0.0.1:8000/api/v1/contacts/1/addresses \
     -H "Content-Type: application/json" \
     -d '{"type": "work", "street": "2nd Office", "city": "Oakland"}'
   ```

   Expect `201`, not a conflict.

4. Edit one address, confirm the other is untouched:

   ```bash
   curl -X PATCH http://127.0.0.1:8000/api/v1/contacts/1/addresses/2 \
     -H "Content-Type: application/json" \
     -d '{"street": "Updated St"}'
   ```

5. Invalid type is rejected:

   ```bash
   curl -X POST http://127.0.0.1:8000/api/v1/contacts/1/addresses \
     -H "Content-Type: application/json" \
     -d '{"type": "vacation"}'
   ```

   Expect `422`.

6. Delete a contact and confirm its addresses are gone (cascade):

   ```bash
   curl -X DELETE http://127.0.0.1:8000/api/v1/contacts/1
   curl http://127.0.0.1:8000/api/v1/contacts/1/addresses   # or inspect via a fresh contact list
   ```

## Full stack (with sf-frontend running against this backend)

1. Open a contact's detail page — confirm addresses are grouped/labeled by type
   (Home, Work, Other), not a flat unlabeled list.
2. Add a Home and a Work address through the UI; confirm both appear correctly
   grouped.
3. Delete one address; confirm the other remains and the deleted one disappears
   immediately.
4. Confirm a contact with zero addresses shows a clear empty state, not an error.
