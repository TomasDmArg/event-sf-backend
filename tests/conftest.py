import os
from collections.abc import Iterator

# Tests get their own empty in-memory database — no seed rows.
os.environ["CONTACTS_DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["CONTACTS_SEED_DATA"] = "false"

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


@pytest.fixture
def client() -> Iterator[TestClient]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def tiny_photo() -> str:
    """A 1x1 PNG, small enough to be a valid upload."""
    return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="


@pytest.fixture
def payload() -> dict:
    return {
        "first_name": "Ada",
        "last_name": "Lovelace",
        "email": "ada@example.com",
        "phone": "+1-415-555-0101",
        "company": "Analytical Engines",
        "job_title": "Mathematician",
        "city": "San Francisco",
        "state": "CA",
        "postal_code": "94105",
        "country": "USA",
        "notes": "First programmer.",
    }
