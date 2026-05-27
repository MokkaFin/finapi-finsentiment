"""Tests basiques pour l'API Flask."""
import pytest
from finapi.app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health(client):
    """Test que /health renvoie 200."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_price_valid_ticker(client):
    """Test que /price/AAPL renvoie un JSON valide."""
    response = client.get("/price/AAPL")
    assert response.status_code == 200
    data = response.get_json()
    assert data["ticker"] == "AAPL"
    assert "close" in data
    assert "date" in data
    assert "currency" in data


def test_price_invalid_ticker(client):
    """Test que /price/ZZZZZ renvoie 404."""
    response = client.get("/price/ZZZZZ")
    assert response.status_code == 404


def test_history_valid(client):
    """Test que /history/AAPL?days=5 renvoie un JSON valide."""
    response = client.get("/history/AAPL?days=5")
    assert response.status_code == 200
    data = response.get_json()
    assert data["ticker"] == "AAPL"
    assert "prices" in data


def test_history_invalid_days(client):
    """Test que days=abc renvoie 400."""
    response = client.get("/history/AAPL?days=abc")
    assert response.status_code == 400


def test_history_out_of_range(client):
    """Test que days=999 renvoie 400."""
    response = client.get("/history/AAPL?days=999")
    assert response.status_code == 400