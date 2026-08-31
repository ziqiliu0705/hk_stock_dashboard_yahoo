# -*- coding: utf-8 -*-
"""
Analysis Module
---------------
Five-dimension scoring model built on full Yahoo Finance fundamentals
plus price-derived metrics:

1. Valuation       (25%) -- P/E, P/B
2. Profitability   (25%) -- ROE, profit margin
3. Growth          (15%) -- revenue growth
4. Financial Health(20%) -- debt-to-equity
5. Momentum & Stability (15%) -- price return and volatility over the
                                 fetched historical period

Run: python analysis.py (after fetch_data.py)
"""

import pandas as pd
from config import FUNDAMENTALS_CSV, PRICES_CSV, PROCESSED_CSV


def min_max_normalize(series: pd.Series, invert: bool = False) -> pd.Series:
    """Normalize a column to 0-100. invert=True: lower raw value = higher score.
    Missing values get a neutral score of 50."""
    s = series.astype(float)
    valid = s.dropna()
    if valid.empty:
        return pd.Series([50.0] * len(s), index=s.index)
    if valid.max() == valid.min():
        return pd.Series([50.0] * len(s), index=s.index)
    score = (s - valid.min()) / (valid.max() - valid.min()) * 100
    if invert:
        score = 100 - score
    return score.fillna(50.0).round(1)


def find_price_column(prices_df: pd.DataFrame, ticker: str):
    return next((c for c in prices_df.columns if c.endswith(f"({ticker})")), None)


def compute_price_metrics(prices_df: pd.DataFrame, ticker: str) -> dict:
    empty = {"period_return_pct": None, "annualized_volatility_pct": None, "max_drawdown_pct": None}
    col = find_price_column(prices_df, ticker)
    if col is None:
        return empty
    series = prices_df[col].dropna()
    if len(series) < 10:
        return empty

    period_return = (series.iloc[-1] / series.iloc[0] - 1) * 100
    daily_returns = series.pct_change().dropna()
    annualized_vol = daily_returns.std() * (252 ** 0.5) * 100
    running_max = series.cummax()
    drawdown = (series - running_max) / running_max * 100
    max_drawdown = drawdown.min()

    return {
        "period_return_pct": round(period_return, 1),
        "annualized_volatility_pct": round(annualized_vol, 1),
        "max_drawdown_pct": round(max_drawdown, 1),
    }


def main():
    df = pd.read_csv(FUNDAMENTALS_CSV)

    try:
        prices_df = pd.read_csv(PRICES_CSV, index_col="date", parse_dates=True)
    except FileNotFoundError:
        prices_df = pd.DataFrame()

    metrics = [compute_price_metrics(prices_df, t) for t in df["ticker"]]
    df = pd.concat([df.reset_index(drop=True), pd.DataFrame(metrics)], axis=1)

    # 52-week range position: 0 = at 52w low, 100 = at 52w high
    range_span = df["52w_high"] - df["52w_low"]
    df["range_position_pct"] = (
        (df["current_price"] - df["52w_low"]) / range_span * 100
    ).clip(0, 100).round(1)

    # ---- 1. Valuation ----
    df["pe_score"] = min_max_normalize(df["trailing_pe"], invert=True)
    df["pb_score"] = min_max_normalize(df["price_to_book"], invert=True)
    df["valuation_score"] = (df["pe_score"] + df["pb_score"]) / 2

    # ---- 2. Profitability ----
    df["roe_score"] = min_max_normalize(df["roe"])
    df["margin_score"] = min_max_normalize(df["profit_margin"])
    df["profitability_score"] = (df["roe_score"] + df["margin_score"]) / 2

    # ---- 3. Growth ----
    df["growth_score"] = min_max_normalize(df["revenue_growth"])

    # ---- 4. Financial Health ----
    df["health_score"] = min_max_normalize(df["debt_to_equity"], invert=True)

    # ---- 5. Momentum & Stability ----
    df["momentum_score"] = min_max_normalize(df["period_return_pct"])
    df["stability_score"] = min_max_normalize(df["annualized_volatility_pct"], invert=True)
    df["momentum_stability_score"] = (df["momentum_score"] + df["stability_score"]) / 2

    # ---- Weighted composite ----
    WEIGHTS = {
        "valuation_score": 0.25,
        "profitability_score": 0.25,
        "growth_score": 0.15,
        "health_score": 0.20,
        "momentum_stability_score": 0.15,
    }
    df["overall_score"] = sum(df[col] * w for col, w in WEIGHTS.items()).round(1)

    # Save each dimension's weighted contribution for the dashboard's score-breakdown chart
    for col, w in WEIGHTS.items():
        df[f"contrib_{col}"] = (df[col] * w).round(1)

    def completeness(row):
        fields = ["roe", "profit_margin", "revenue_growth", "debt_to_equity"]
        available = sum(1 for f in fields if pd.notna(row.get(f)))
        return f"{available}/{len(fields)}"

    df["data_completeness"] = df.apply(completeness, axis=1)

    df = df.sort_values("overall_score", ascending=False)
    df.to_csv(PROCESSED_CSV, index=False, encoding="utf-8-sig")

    print("Analysis complete. Composite score ranking:")
    print(df[["name", "ticker", "overall_score", "valuation_score", "profitability_score",
              "growth_score", "health_score", "momentum_stability_score",
              "data_completeness"]].to_string(index=False))
    print(f"\nSaved to: {PROCESSED_CSV}")


if __name__ == "__main__":
    main()