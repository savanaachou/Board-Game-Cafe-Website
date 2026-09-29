import importlib
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def app(tmp_path, monkeypatch):
    """Fresh Flask app + freshly seeded SQLite DB for every test function.

    Each test gets its own temp .db file so tests never see each other's
    writes and never touch the real cafe.db a developer might have locally.
    """
    db_path = tmp_path / "test_cafe.db"
    monkeypatch.setenv("DATABASE_PATH", str(db_path))
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")

    # boardGameCafe creates its db connection and seeds data at *import*
    # time, so a plain import would reuse whatever ran first. Reload it
    # fresh against the new DATABASE_PATH for every test.
    import boardGameCafe as module
    importlib.reload(module)

    module.app.config.update(TESTING=True)
    yield module.app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def logged_in_client(client):
    """Client signed in as seeded demo customer #3 (Savana / dicebox2026)."""
    client.post('/', data={'customer_id': '3', 'password': 'dicebox2026'})
    return client
