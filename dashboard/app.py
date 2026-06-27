"""Interactive financial sentiment analysis dashboard."""
from datetime import datetime
import streamlit as st
from dashboard import api_client as api
from dashboard.charts import price_line_chart, sentiment_pie_chart, SENT_COLORS

# -------- Page config --------
st.set_page_config(
    page_title="FinSentiment Dashboard",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
)

# -------- Sidebar --------
with st.sidebar:
    st.title("Controls")
    st.caption("Configure your view below.")

    api_ok = api.get_health()
    if api_ok:
        st.success("API connected")
    else:
        st.error("API unreachable")
        st.info("Run 'python -m finapi.app' in another terminal.")
        st.stop()

    stats = api.get_db_stats()
    available_tickers = stats.get("tickers", [])
    if not available_tickers:
        st.warning("Empty DB. Run 'python scripts/run_etl.py AAPL MSFT'.")
        st.stop()

    ticker = st.selectbox("Ticker", available_tickers)

    if st.button("Refresh now"):
        st.cache_data.clear()
        st.rerun()

    st.divider()
    st.caption(
        f"DB: {stats['prices_count']} prices | {stats['news_count']} news "
        f"({stats['news_enriched']} with sentiment)"
    )

# -------- Header --------
st.title(f":chart_with_upwards_trend: FinSentiment - {ticker}")
st.caption("Interactive dashboard - prices, news, FinBERT sentiment")

# -------- Data loading with cache --------
@st.cache_data(ttl=60)
def load_prices(t: str):
    return api.get_db_prices(t)

@st.cache_data(ttl=60)
def load_news(t: str):
    return api.get_db_news(t)

@st.cache_data(ttl=60)
def load_summary(t: str):
    return api.get_sentiment_summary(t)

prices = load_prices(ticker)
news = load_news(ticker)
sentiment = load_summary(ticker)

# -------- Top metrics --------
col1, col2, col3, col4 = st.columns(4)
if prices:
    last = prices[0]
    prev = prices[1] if len(prices) > 1 else last
    delta = last["close"] - prev["close"]
    col1.metric("Latest price", f"{last['close']:.2f}", f"{delta:+.2f}")
    col2.metric("Date", last["date"])
    col3.metric("News stored", len(news))
    total_sent = sum(sentiment.values()) or 1
    pos_share = sentiment.get("positive", 0) / total_sent * 100
    col4.metric("Positive sentiment", f"{pos_share:.0f}%")

st.divider()

# -------- Charts --------
g1, g2 = st.columns([2, 1])
with g1:
    st.subheader("Price evolution")
    st.plotly_chart(price_line_chart(prices), use_container_width=True)
with g2:
    st.subheader("Sentiment distribution")
    if sentiment:
        st.plotly_chart(sentiment_pie_chart(sentiment), use_container_width=True)
    else:
        st.info("No sentiment calculated. Run 'enrich_sentiment.py'.")

# -------- News list --------
st.subheader(f"Latest news - {ticker}")
if not news:
    st.info("No news in DB.")
else:
    for n in news[:15]:
        sent = n.get("sentiment_label") or "neutral"
        color = SENT_COLORS.get(sent, "#94A3B8")
        st.markdown(
            f"<div style='border-left: 4px solid {color};"
            f" padding: 8px 14px; margin: 4px 0;"
            f" background: #F8FAFC;'>"
            f"<b>{n['title']}</b><br>"
            f"<small style='color:#64748B'>{n['publisher']} - "
            f"{n['published_at'][:16]} - "
            f"<span style='color:{color}; font-weight:bold;'>{sent.upper()}</span>"
            f"</small></div>",
            unsafe_allow_html=True,
        )

st.divider()
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")