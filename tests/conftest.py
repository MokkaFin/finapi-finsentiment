"""Shared fixtures for tests."""

import pytest

from finapi.app import create_app


@pytest.fixture
def client():
    """Flask test client (no real server)."""
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()
