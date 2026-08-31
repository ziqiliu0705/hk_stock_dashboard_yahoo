# -*- coding: utf-8 -*-
"""
Data Source Layer -- Yahoo Finance (via yfinance)
---------------------------------------------------
Yahoo Finance offers the most complete free fundamentals available
(P/E, P/B, ROE, profit margin, revenue growth, debt-to-equity all in
one call via .info), which is why it's the primary source once network
access allows it (e.g. running from Hong Kong, where Yahoo isn't
blocked/rate-limited the way it can be from mainland China).

curl_cffi is used to impersonate a real Chrome browser's TLS fingerprint,
which reduces (but does not eliminate) the chance of hitting Yahoo's
rate limiter. Retry-with-backoff is built in for when it does trigger.
"""

import random
import time

import pandas as pd
import yfinance as yf
from curl_cffi import requests as curl_requests
from yfinance.exceptions import YFRateLimitError

MAX_RETRIES = 3
RETRY_BASE_WAIT_SECONDS = 20
REQUEST_DELAY_SECONDS = 2


def get_yf_session():
    """Impersonate a real Chrome browser's TLS fingerprint to reduce rate-limit risk"""
    return curl_requests.Session(impersonate="chrome")


def to_yfinance_code(ticker: str) -> str:
    if ticker.upper().endswith(".HK"):
        return ticker
    return f"{ticker}.HK"


def _with_retry(fetch_fn, label: str):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return fetch_fn()
        except YFRateLimitError:
            wait = RETRY_BASE_WAIT_SECONDS * attempt
            print(f"  [Rate Limited] {label}, waiting {wait}s before retry ({attempt}/{MAX_RETRIES})...")
            time.sleep(wait)
    return fetch_fn()  # let it raise on the final attempt


def fetch_fundamentals_yfinance(candidate_tickers: dict) -> pd.DataFrame:
    session = get_yf_session()
    rows = []
    for ticker, name in candidate_tickers.items():
        yf_code = to_yfinance_code(ticker)
        try:
            info = _with_retry(
                lambda: yf.Ticker(yf_code, session=session).info, f"{name}({ticker})"
            )
            if not info or len(info) < 3:
                raise ValueError("Empty response")
        except Exception as e:
            print(f"  [Warning] {name}({ticker}) fetch failed: {type(e).__name__}: {e}")
            continue

        rows.append({
            "ticker": ticker,
            "name": name,
            "market_cap": info.get("marketCap"),
            "trailing_pe": info.get("trailingPE"),
            "price_to_book": info.get("priceToBook"),
            "roe": info.get("returnOnEquity"),
            "profit_margin": info.get("profitMargins"),
            "revenue_growth": info.get("revenueGrowth"),
            "debt_to_equity": info.get("debtToEquity"),
            "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
            "52w_high": info.get("fiftyTwoWeekHigh"),
            "52w_low": info.get("fiftyTwoWeekLow"),
        })
        time.sleep(random.uniform(REQUEST_DELAY_SECONDS, REQUEST_DELAY_SECONDS + 1.5))

    return pd.DataFrame(rows)


def fetch_price_history_yfinance(ticker: str, start_date: str, end_date: str) -> pd.Series:
    session = get_yf_session()
    yf_code = to_yfinance_code(ticker)
    hist = _with_retry(
        lambda: yf.Ticker(yf_code, session=session).history(start=start_date, end=end_date),
        ticker,
    )
    if hist.empty:
        raise ValueError(f"{ticker} returned no price history")
    series = hist["Close"]
    series.name = ticker
    return series


def get_fundamentals(candidate_tickers: dict) -> pd.DataFrame:
    print(">> Fetching fundamentals via Yahoo Finance...")
    df = fetch_fundamentals_yfinance(candidate_tickers)
    if df.empty:
        raise RuntimeError("Yahoo Finance returned no data for any ticker. "
                            "Check network connectivity and try again.")
    print(f"   Success: retrieved {len(df)} tickers")
    return df


def get_price_history(tickers: dict, start_date: str, end_date: str) -> pd.DataFrame:
    all_prices = {}
    for ticker, name in tickers.items():
        try:
            series = fetch_price_history_yfinance(ticker, start_date, end_date)
            all_prices[f"{name}({ticker})"] = series
        except Exception as e:
            print(f"  [Warning] {name}({ticker}) price history fetch failed, skipped: {type(e).__name__}: {e}")
        time.sleep(random.uniform(1.0, 2.0))

    if not all_prices:
        raise RuntimeError("Price history fetch failed for all tickers")

    price_df = pd.DataFrame(all_prices)
    price_df.index.name = "date"
    return price_df.sort_index()