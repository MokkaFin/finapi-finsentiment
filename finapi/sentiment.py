"""Service d'analyse de sentiment financier via FinBERT."""
from __future__ import annotations
import logging
from dataclasses import dataclass
from functools import lru_cache
from transformers import pipeline

log = logging.getLogger(__name__)
MODEL_NAME = "ProsusAI/finbert"


@dataclass
class SentimentResult:
    label: str        # "positive" / "neutral" / "negative"
    score: float      # probabilité 0..1
    text_preview: str


@lru_cache(maxsize=1)
def get_pipeline():
    """Charge le modèle une seule fois (singleton)."""
    log.info("Loading FinBERT model (first call)...")
    pipe = pipeline("sentiment-analysis", model=MODEL_NAME)
    log.info("FinBERT model loaded.")
    return pipe


def analyze(text: str) -> SentimentResult:
    if not text or not text.strip():
        raise ValueError("Texte vide")
    pipe = get_pipeline()
    out = pipe(text[:512])[0]  # FinBERT max 512 tokens
    return SentimentResult(
        label=out["label"].lower(),
        score=round(float(out["score"]), 4),
        text_preview=text[:80] + ("..." if len(text) > 80 else ""),
    )


def analyze_batch(texts: list[str]) -> list[SentimentResult]:
    if not texts:
        return []
    pipe = get_pipeline()
    truncated = [t[:512] for t in texts if t and t.strip()]
    outputs = pipe(truncated, batch_size=16)
    return [
        SentimentResult(
            label=o["label"].lower(),
            score=round(float(o["score"]), 4),
            text_preview=t[:80] + ("..." if len(t) > 80 else ""),
        )
        for t, o in zip(truncated, outputs)
    ]