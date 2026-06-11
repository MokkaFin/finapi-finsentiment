"""Application Flask exposant les endpoints de prix."""
from flask import Flask, jsonify, request
from finapi.prices import TickerNotFoundError, get_history, get_latest_price
from finapi.db import SessionLocal, init_db
from finapi.models import PriceRecord, NewsItem
from finapi.sentiment import analyze, analyze_batch

def create_app() -> Flask:
    app = Flask(__name__)
    init_db()
    @app.get("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    @app.get("/price/<ticker>")
    def price(ticker: str):
        try:
            latest = get_latest_price(ticker)
        except TickerNotFoundError as e:
            return jsonify({"error": str(e), "code": 404}), 404
        except Exception:
            return jsonify({"error": "Erreur interne", "code": 500}), 500
        return jsonify({
            "ticker": latest.ticker,
            "date": latest.date.isoformat(),
            "close": latest.close,
            "currency": latest.currency,
        })

    @app.get("/history/<ticker>")
    def history(ticker: str):
        raw_days = request.args.get("days", "30")
        try:
            days = int(raw_days)
        except ValueError:
            return jsonify({
                "error": "Le parametre 'days' doit etre un entier",
                "code": 400,
            }), 400
        if not 1 <= days <= 365:
            return jsonify({
                "error": "Le parametre 'days' doit etre entre 1 et 365",
                "code": 400,
            }), 400
        try:
            points = get_history(ticker, days)
        except TickerNotFoundError as e:
            return jsonify({"error": str(e), "code": 404}), 404
        except Exception:
            return jsonify({"error": "Erreur interne", "code": 500}), 500
        return jsonify({
            "ticker": ticker.upper(),
            "days_requested": days,
            "prices": [
                {"date": p.date.isoformat(), "close": p.close}
                for p in points
            ],
        })

    @app.get("/compare")
    def compare():
        raw_tickers = request.args.get("tickers", "")
        if not raw_tickers:
            return jsonify({
                "error": "Le parametre 'tickers' est requis",
                "code": 400,
            }), 400
        tickers = [t.strip().upper() for t in raw_tickers.split(",") if t.strip()]
        if len(tickers) < 2:
            return jsonify({
                "error": "Au moins 2 tickers sont requis",
                "code": 400,
            }), 400
        results = {}
        errors = {}
        for ticker in tickers:
            try:
                latest = get_latest_price(ticker)
                results[ticker] = {
                    "date": latest.date.isoformat(),
                    "close": latest.close,
                    "currency": latest.currency,
                }
            except TickerNotFoundError:
                errors[ticker] = "introuvable"
            except Exception:
                errors[ticker] = "erreur interne"
        return jsonify({
            "prices": results,
            "errors": errors,
        })
    @app.get("/db/prices/<ticker>")
    def db_prices(ticker: str):
        """Lit les prix stockés pour un ticker (les plus récents en premier)."""
        with SessionLocal() as session:
            rows = (
                session.query(PriceRecord)
                .filter(PriceRecord.ticker == ticker.upper())
                .order_by(PriceRecord.date.desc())
                .limit(100)
                .all()
            )
        return jsonify({
            "ticker": ticker.upper(),
            "count": len(rows),
            "prices": [{"date": r.date.isoformat(), "close": r.close} for r in rows],
        })


    @app.get("/db/news/<ticker>")
    def db_news(ticker: str):
        """Lit les news stockées pour un ticker."""
        with SessionLocal() as session:
            rows = (
                session.query(NewsItem)
                .filter(NewsItem.ticker == ticker.upper())
                .order_by(NewsItem.published_at.desc())
                .limit(20)
                .all()
            )
        return jsonify({
            "ticker": ticker.upper(),
            "count": len(rows),
            "news": [
                {
                    "published_at": r.published_at.isoformat(),
                    "title": r.title,
                    "publisher": r.publisher,
                    "url": r.url,
                }
                for r in rows
            ],
        })
    @app.get("/db/stats")
    def db_stats():
        """Renvoie le nombre de lignes par table."""
        with SessionLocal() as session:
            price_count = session.query(PriceRecord).count()
            news_count = session.query(NewsItem).count()
        return jsonify({
            "prices": price_count,
            "news": news_count,
        })
    @app.post("/sentiment")
    def sentiment():
        """Analyse le sentiment d'un texte unique. Body JSON: {"text": "..."}."""
        payload = request.get_json(silent=True) or {}
        text = payload.get("text")
        if not text:
            return jsonify({"error": "Champ 'text' manquant dans le body JSON", "code": 400}), 400
        try:
            result = analyze(text)
        except ValueError as e:
            return jsonify({"error": str(e), "code": 400}), 400
        except Exception:
            return jsonify({"error": "Erreur interne", "code": 500}), 500
        return jsonify({
            "label": result.label,
            "score": result.score,
            "text_preview": result.text_preview,
        })


    @app.post("/sentiment/batch")
    def sentiment_batch():
        """Analyse plusieurs textes. Body JSON: {"texts": ["...", "..."]}."""
        payload = request.get_json(silent=True) or {}
        texts = payload.get("texts")
        if not isinstance(texts, list) or not texts:
            return jsonify({"error": "Champ 'texts' (liste non vide) requis", "code": 400}), 400
        if len(texts) > 100:
            return jsonify({"error": "Maximum 100 textes par requête", "code": 400}), 400
        try:
            results = analyze_batch(texts)
        except Exception:
            return jsonify({"error": "Erreur interne", "code": 500}), 500
        return jsonify({
            "count": len(results),
            "results": [
                {"label": r.label, "score": r.score, "text_preview": r.text_preview}
                for r in results
            ],
        })


    @app.get("/db/sentiment-summary/<ticker>")
    def sentiment_summary(ticker: str):
        """Résumé des sentiments stockés pour un ticker."""
        from sqlalchemy import func
        with SessionLocal() as session:
            rows = (
                session.query(NewsItem.sentiment_label, func.count(NewsItem.id))
                .filter(NewsItem.ticker == ticker.upper())
                .filter(NewsItem.sentiment_label.isnot(None))
                .group_by(NewsItem.sentiment_label)
                .all()
            )
        return jsonify({
            "ticker": ticker.upper(),
            "distribution": {label: count for label, count in rows},
        })
    return app


if __name__ == "__main__":
    create_app().run(debug=True, port=5000)