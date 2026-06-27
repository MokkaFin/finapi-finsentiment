"""Sentiment tests with FinBERT mocked (no model loading)."""

from unittest.mock import patch

import pytest

from finapi.sentiment import SentimentResult, analyze


@patch("finapi.sentiment.get_pipeline")
def test_analyze_positive(mock_pipe):
    mock_pipe.return_value = lambda text: [{"label": "positive", "score": 0.95}]
    result = analyze("Apple beats expectations")
    assert isinstance(result, SentimentResult)
    assert result.label == "positive"
    assert result.score == 0.95


def test_analyze_empty_raises():
    with pytest.raises(ValueError):
        analyze("")
