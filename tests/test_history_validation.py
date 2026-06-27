def test_invalid_days(client):
    response = client.get("/history/AAPL?days=abc")
    assert response.status_code == 400


def test_days_out_of_range(client):
    response = client.get("/history/AAPL?days=999")
    assert response.status_code == 400
