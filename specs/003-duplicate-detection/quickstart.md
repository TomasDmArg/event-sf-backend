# Quickstart: Duplicate Contact Detection

## Backend only (this repo)

```bash
.venv/bin/python -m app.main
```

1. Create two contacts sharing an email:

   ```bash
   curl -X POST http://127.0.0.1:8000/api/v1/contacts \
     -H "Content-Type: application/json" \
     -d '{"first_name":"Jon","last_name":"Smith","email":"dupe@example.com"}'
   curl -X POST http://127.0.0.1:8000/api/v1/contacts \
     -H "Content-Type: application/json" \
     -d '{"first_name":"John","last_name":"Smith","email":"dupe2@example.com","phone":"+1-555-0000"}'
   ```

   (Note: the existing unique-email constraint on Contact means an exact email
   duplicate can't be created via the normal API — use two different emails but a
   shared phone, or similar names, to exercise detection realistically. See
   Assumptions in `spec.md` if the challenge dataset needs an intentional exact-email
   duplicate for the demo.)

2. List duplicate candidates:

   ```bash
   curl http://127.0.0.1:8000/api/v1/contacts/duplicates
   ```

   Expect the Jon/John Smith pair flagged with reason `similar_name`.

3. Merge them, primary wins on conflicts by default:

   ```bash
   curl -X POST http://127.0.0.1:8000/api/v1/contacts/merge \
     -H "Content-Type: application/json" \
     -d '{"primary_id": 1, "secondary_id": 2}'
   ```

   Expect `200` with the merged contact showing addresses from both and a photo if
   either had one.

4. Confirm the secondary contact no longer exists:

   ```bash
   curl http://127.0.0.1:8000/api/v1/contacts/2
   ```

   Expect `404`.

## Full stack (with sf-frontend running against this backend)

1. Open the "possible duplicates" view — confirm flagged pairs show their reason.
2. Merge a pair with conflicting job titles — confirm the UI presents a choice rather
   than silently picking one.
3. Confirm addresses from both contacts appear on the merged result.
4. Dismiss a flagged pair that isn't actually a duplicate — confirm it stops
   appearing in the list.
