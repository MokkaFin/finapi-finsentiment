"""Affiche un résumé textuel de la base. Usage: python scripts/show_db.py"""

from finapi.db import SessionLocal, init_db
from finapi.models import NewsItem, PriceRecord


def main() -> None:
    init_db()
    with SessionLocal() as session:
        price_count = session.query(PriceRecord).count()
        news_count = session.query(NewsItem).count()

        tickers_prices = [r[0] for r in session.query(PriceRecord.ticker).distinct().all()]
        tickers_news = [r[0] for r in session.query(NewsItem.ticker).distinct().all()]

        print(f"\n{'=' * 40}")
        print("  finapi.db — résumé")
        print(f"{'=' * 40}")
        print(f"  prices : {price_count} lignes | tickers : {', '.join(sorted(tickers_prices))}")
        print(f"  news   : {news_count} lignes | tickers : {', '.join(sorted(tickers_news))}")
        print(f"{'=' * 40}\n")


if __name__ == "__main__":
    main()
