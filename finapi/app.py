"""Application Flask exposant les endpoints de prix."""
from flask import Flask, jsonify, request
from finapi.prices import TickerNotFoundError, get_history, get_latest_price


def create_app() -> Flask:
    app = Flask(__name__)

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

    return app


if __name__ == "__main__":
    create_app().run(debug=True, port=5000)