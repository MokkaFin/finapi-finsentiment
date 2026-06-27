from datetime import date
from unittest.mock import patch

from finapi.prices import LatestPrice, PricePoint


def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_db_prices_returns_200(client):
    response = client.get("/db/prices/AAPL")
    assert response.status_code == 200


def test_db_news_returns_200(client):
    response = client.get("/db/news/AAPL")
    assert response.status_code == 200


def test_db_stats_returns_200(client):
    response = client.get("/db/stats")
    assert response.status_code == 200


def test_sentiment_missing_text(client):
    response = client.post("/sentiment", json={})
    assert response.status_code == 400


def test_sentiment_batch_empty(client):
    response = client.post("/sentiment/batch", json={"texts": []})
    assert response.status_code == 400


def test_sentiment_batch_too_many(client):
    response = client.post("/sentiment/batch", json={"texts": ["x"] * 101})
    assert response.status_code == 400


def test_sentiment_summary_returns_200(client):
    response = client.get("/db/sentiment-summary/AAPL")
    assert response.status_code == 200


def test_price_endpoint_success(client):
    mock_price = LatestPrice(ticker="AAPL", date=date(2026, 1, 1), close=150.0, currency="USD")
    with patch("finapi.app.get_latest_price", return_value=mock_price):
        response = client.get("/price/AAPL")
        assert response.status_code == 200


def test_price_endpoint_invalid(client):
    from finapi.prices import TickerNotFoundError

    with patch("finapi.app.get_latest_price", side_effect=TickerNotFoundError("not found")):
        response = client.get("/price/ZZZZZ")
        assert response.status_code == 404


def test_history_endpoint_success(client):
    mock_points = [PricePoint(date=date(2026, 1, 1), close=150.0)]
    with patch("finapi.app.get_history", return_value=mock_points):
        response = client.get("/history/AAPL?days=5")
        assert response.status_code == 200
