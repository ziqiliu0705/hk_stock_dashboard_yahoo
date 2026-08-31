# -*- coding: utf-8 -*-
"""
Dashboard (Streamlit + Plotly) -- Investment Bank Research Report Style
-------------------------------------------------------------------
Local run: streamlit run dashboard.py
Cloud deploy: see README.md
"""

import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

import data_sources as ds
from config import SECTOR_NAME, TOP_N, PROCESSED_CSV, PRICES_CSV
from styles import get_custom_css, get_plotly_template, CHART_PALETTE

st.set_page_config(
    page_title=f"{SECTOR_NAME} | Research Dashboard",
    page_icon="H",
    layout="wide",
)

pio.templates["ib_theme"] = get_plotly_template()
pio.templates.default = "ib_theme"
st.markdown(get_custom_css(), unsafe_allow_html=True)


@st.cache_data(ttl=3600, show_spinner="Loading fundamentals data...")
def load_fundamentals():
    return pd.read_csv(PROCESSED_CSV)


@st.cache_data(ttl=3600, show_spinner="Loading cached price history...")
def load_cached_prices():
    return pd.read_csv(PRICES_CSV, index_col="date", parse_dates=True)


@st.cache_data(ttl=1800, show_spinner="Fetching price history for selected date range...")
def fetch_prices_dynamic(tickers_tuple, start_date_str, end_date_str):
    tickers_dict = dict(tickers_tuple)
    return ds.get_price_history(tickers_dict, start_date_str, end_date_str)


try:
    df = load_fundamentals()
except FileNotFoundError:
    st.error(
        "Data files not found.\n\n"
        "Local run: please run `python fetch_data.py` then `python analysis.py` first.\n\n"
        "Cloud deploy: please make sure the CSV files under data/ are committed to the GitHub repo."
    )
    st.stop()

selected_tickers = dict(zip(df["ticker"], df["name"]))

if "prices" not in st.session_state:
    try:
        st.session_state["prices"] = load_cached_prices()
        st.session_state["price_range_label"] = "(Showing: default range saved during data fetch)"
    except FileNotFoundError:
        st.session_state["prices"] = None
        st.session_state["price_range_label"] = ""

prices = st.session_state["prices"]


st.markdown(f"""
<div class="ib-header">
    <h1>{SECTOR_NAME}</h1>
    <p>EQUITY RESEARCH &middot; MULTI-FACTOR VALUATION & RISK DASHBOARD &nbsp;|&nbsp; Data Source: Yahoo Finance</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### About This Dashboard")
    st.markdown(
        f"The candidate pool is automatically filtered to the top {TOP_N} names by total market "
        "cap. A five-factor weighted model scores each company across valuation, profitability, "
        "growth, financial health, and price momentum/stability."
    )
    st.markdown("---")
    st.markdown("### Custom Price History Range")
    st.caption("Change the dates and click the button below to re-fetch price data for that range")

    default_end = datetime.date.today()
    default_start = default_end - datetime.timedelta(days=730)
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        start_date = st.date_input("Start Date", value=default_start, max_value=default_end)
    with col_d2:
        end_date = st.date_input("End Date", value=default_end, max_value=default_end)

    if st.button("Update Price Chart", use_container_width=True):
        if start_date >= end_date:
            st.error("Start date must be before end date")
        else:
            tickers_tuple = tuple(selected_tickers.items())
            with st.spinner("Fetching data, please wait..."):
                try:
                    new_prices = fetch_prices_dynamic(
                        tickers_tuple, start_date.isoformat(), end_date.isoformat()
                    )
                    st.session_state["prices"] = new_prices
                    st.session_state["price_range_label"] = f"(Current range: {start_date} to {end_date})"
                    st.success("Price data updated. Re-run analysis.py to refresh scores for this range.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Fetch failed: {type(e).__name__}: {e}")

    st.markdown("---")
    st.markdown("### Scoring Weights")
    st.markdown(
        "- Valuation (P/E, P/B): 25%\n"
        "- Profitability (ROE, margin): 25%\n"
        "- Growth (revenue growth): 15%\n"
        "- Financial Health (debt/equity): 20%\n"
        "- Momentum & Stability (price): 15%"
    )
    st.caption("Missing fundamentals default to a neutral score of 50 for that sub-component.")
    st.markdown("---")
    st.caption("For analytical demonstration only. Not investment advice.")


st.subheader("Sector Overview")
col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Companies Covered", len(df))
col2.metric("Avg P/E", f"{df['trailing_pe'].mean():.1f}x" if df["trailing_pe"].notna().any() else "N/A")
col3.metric("Avg ROE", f"{df['roe'].mean()*100:.1f}%" if df["roe"].notna().any() else "N/A")
col4.metric("Avg Debt/Equity", f"{df['debt_to_equity'].mean():.0f}" if df["debt_to_equity"].notna().any() else "N/A")
col5.metric("Total Market Cap", f"HK${df['market_cap'].sum()/1e8:.0f}B" if df["market_cap"].notna().any() else "N/A")
col6.metric("Top Composite Score", df.iloc[0]["name"])

st.divider()

tab0, tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Overview & Ranking", "Valuation", "Profitability & Growth",
    "Financial Health", "Momentum & Risk", "Price History", "Company Profile & Data"
])

with tab0:
    fig_rank = px.bar(
        df.sort_values("overall_score"), x="overall_score", y="name", orientation="h",
        color="overall_score", color_continuous_scale=["#A0453A", "#D4C0A1", "#4A7C6F"],
        title="Composite Score Ranking", labels={"overall_score": "Composite Score", "name": ""},
    )
    fig_rank.update_layout(coloraxis_showscale=False, height=max(400, 26 * len(df)))
    st.plotly_chart(fig_rank, use_container_width=True)

    st.caption("Score breakdown: weighted contribution of each factor to the composite score")
    contrib_cols = ["contrib_valuation_score", "contrib_profitability_score", "contrib_growth_score",
                     "contrib_health_score", "contrib_momentum_stability_score"]
    contrib_labels = ["Valuation", "Profitability", "Growth", "Financial Health", "Momentum & Stability"]
    plot_df = df.sort_values("overall_score")
    fig_breakdown = go.Figure()
    for col, label, color in zip(contrib_cols, contrib_labels, CHART_PALETTE):
        if col in plot_df.columns:
            fig_breakdown.add_trace(go.Bar(
                x=plot_df[col], y=plot_df["name"], orientation="h", name=label, marker_color=color,
            ))
    fig_breakdown.update_layout(
        barmode="stack", title="Composite Score Breakdown by Factor",
        xaxis_title="Weighted Contribution", height=max(400, 26 * len(df)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig_breakdown, use_container_width=True)

with tab1:
    col_a, col_b = st.columns(2)
    with col_a:
        fig_pe = px.bar(
            df.sort_values("trailing_pe"), x="name", y="trailing_pe",
            title="Price-to-Earnings (P/E)", labels={"trailing_pe": "P/E (x)", "name": ""},
        )
        fig_pe.update_traces(marker_color=CHART_PALETTE[0])
        st.plotly_chart(fig_pe, use_container_width=True)
    with col_b:
        fig_pb = px.bar(
            df.sort_values("price_to_book"), x="name", y="price_to_book",
            title="Price-to-Book (P/B)", labels={"price_to_book": "P/B (x)", "name": ""},
        )
        fig_pb.update_traces(marker_color=CHART_PALETTE[1])
        st.plotly_chart(fig_pb, use_container_width=True)
    fig_cap = px.bar(
        df.sort_values("market_cap"), x="name", y="market_cap",
        title="Market Capitalization", labels={"market_cap": "Market Cap", "name": ""},
    )
    fig_cap.update_traces(marker_color=CHART_PALETTE[2])
    st.plotly_chart(fig_cap, use_container_width=True)

with tab2:
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        fig_roe = px.bar(
            df.sort_values("roe"), x="name", y="roe",
            title="Return on Equity (ROE)", labels={"roe": "ROE", "name": ""},
        )
        fig_roe.update_traces(marker_color=CHART_PALETTE[3])
        fig_roe.update_yaxes(tickformat=".0%")
        st.plotly_chart(fig_roe, use_container_width=True)
    with col_b:
        fig_margin = px.bar(
            df.sort_values("profit_margin"), x="name", y="profit_margin",
            title="Profit Margin", labels={"profit_margin": "Profit Margin", "name": ""},
        )
        fig_margin.update_traces(marker_color=CHART_PALETTE[4])
        fig_margin.update_yaxes(tickformat=".0%")
        st.plotly_chart(fig_margin, use_container_width=True)
    with col_c:
        fig_growth = px.bar(
            df.sort_values("revenue_growth"), x="name", y="revenue_growth",
            title="Revenue Growth", labels={"revenue_growth": "Revenue Growth", "name": ""},
        )
        colors_g = [CHART_PALETTE[2] if v >= 0 else CHART_PALETTE[3] for v in df.sort_values("revenue_growth")["revenue_growth"]]
        fig_growth.update_traces(marker_color=colors_g)
        fig_growth.update_yaxes(tickformat=".0%")
        st.plotly_chart(fig_growth, use_container_width=True)

    st.caption("Ideal quadrant: top-right (high ROE, high margin)")
    prof_df = df.dropna(subset=["roe", "profit_margin"])
    fig_prof_scatter = px.scatter(
        prof_df, x="roe", y="profit_margin", size="market_cap", color="name", text="name",
        labels={"roe": "ROE", "profit_margin": "Profit Margin"}, size_max=55,
    )
    fig_prof_scatter.update_traces(textposition="top center")
    fig_prof_scatter.update_xaxes(tickformat=".0%")
    fig_prof_scatter.update_yaxes(tickformat=".0%")
    fig_prof_scatter.update_layout(showlegend=False, title="ROE vs Profit Margin")
    st.plotly_chart(fig_prof_scatter, use_container_width=True)

with tab3:
    fig_debt = px.bar(
        df.sort_values("debt_to_equity"), x="name", y="debt_to_equity",
        title="Debt-to-Equity Ratio", labels={"debt_to_equity": "Debt/Equity", "name": ""},
    )
    fig_debt.update_traces(marker_color=CHART_PALETTE[3])
    st.plotly_chart(fig_debt, use_container_width=True)

    st.caption("Ideal quadrant: bottom-right (low leverage, high profitability)")
    health_df = df.dropna(subset=["debt_to_equity", "roe"])
    fig_health_scatter = px.scatter(
        health_df, x="debt_to_equity", y="roe", size="market_cap", color="name", text="name",
        labels={"debt_to_equity": "Debt/Equity", "roe": "ROE"}, size_max=55,
    )
    fig_health_scatter.update_traces(textposition="top center")
    fig_health_scatter.update_yaxes(tickformat=".0%")
    fig_health_scatter.update_layout(showlegend=False, title="Leverage vs Profitability")
    st.plotly_chart(fig_health_scatter, use_container_width=True)

with tab4:
    col_a, col_b = st.columns(2)
    with col_a:
        ret_df = df.dropna(subset=["period_return_pct"]).sort_values("period_return_pct")
        colors = [CHART_PALETTE[2] if v >= 0 else CHART_PALETTE[3] for v in ret_df["period_return_pct"]]
        fig_ret = go.Figure(go.Bar(
            x=ret_df["period_return_pct"], y=ret_df["name"], orientation="h", marker_color=colors,
        ))
        fig_ret.update_layout(title="Price Return Over Fetched Period (%)",
                              xaxis_title="Return (%)", yaxis_title="")
        st.plotly_chart(fig_ret, use_container_width=True)
    with col_b:
        vol_df = df.dropna(subset=["annualized_volatility_pct"]).sort_values("annualized_volatility_pct")
        fig_vol = px.bar(
            vol_df, x="annualized_volatility_pct", y="name", orientation="h",
            title="Annualized Volatility (%)",
            labels={"annualized_volatility_pct": "Volatility (%)", "name": ""},
        )
        fig_vol.update_traces(marker_color=CHART_PALETTE[4])
        st.plotly_chart(fig_vol, use_container_width=True)

    st.caption("Ideal quadrant: bottom-right (high return, low volatility)")
    rr_df = df.dropna(subset=["annualized_volatility_pct", "period_return_pct"])
    fig_rr = px.scatter(
        rr_df, x="annualized_volatility_pct", y="period_return_pct",
        size="market_cap", color="name", text="name",
        labels={"annualized_volatility_pct": "Annualized Volatility (%)", "period_return_pct": "Period Return (%)"},
        size_max=55,
    )
    fig_rr.update_traces(textposition="top center")
    fig_rr.add_hline(y=0, line_dash="dot", line_color="#B0B0B0")
    fig_rr.update_layout(showlegend=False, title="Risk vs Return Quadrant")
    st.plotly_chart(fig_rr, use_container_width=True)

with tab5:
    if prices is None or prices.empty:
        st.warning("No price history data yet. Select a date range on the left and click "
                   "'Update Price Chart'.")
    else:
        st.caption(st.session_state.get("price_range_label", ""))
        valid_cols = [c for c in prices.columns if prices[c].notna().any()]
        prices_valid = prices[valid_cols]
        normalized = prices_valid.apply(lambda col: col / col.dropna().iloc[0] * 100)
        fig_price = go.Figure()
        for i, col in enumerate(normalized.columns):
            fig_price.add_trace(go.Scatter(
                x=normalized.index, y=normalized[col], mode="lines", name=col,
                line=dict(color=CHART_PALETTE[i % len(CHART_PALETTE)], width=2),
            ))
        fig_price.update_layout(
            title="Historical Price Comparison (Indexed, Base = 100)",
            yaxis_title="Indexed Price", xaxis_title="",
        )
        st.plotly_chart(fig_price, use_container_width=True)

with tab6:
    col_left, col_right = st.columns([1, 1.5])
    with col_left:
        selected = st.selectbox("Select a company", df["name"].tolist())
        row = df[df["name"] == selected].iloc[0]
        categories = ["Valuation", "Profitability", "Growth", "Financial Health", "Momentum & Stability"]
        values = [row["valuation_score"], row["profitability_score"], row["growth_score"],
                  row["health_score"], row["momentum_stability_score"]]
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=values + [values[0]], theta=categories + [categories[0]],
            fill="toself", name=selected, line=dict(color=CHART_PALETTE[1]),
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False, title=f"{selected} Profile",
        )
        st.plotly_chart(fig_radar, use_container_width=True)
        st.caption(f"Data completeness: {row.get('data_completeness', 'N/A')}")
        if pd.notna(row.get("max_drawdown_pct")):
            st.caption(f"Max drawdown over fetched period: {row['max_drawdown_pct']:.1f}%")
        if pd.notna(row.get("range_position_pct")):
            st.caption(f"52-week range position: {row['range_position_pct']:.0f}% (0 = low, 100 = high)")

    with col_right:
        st.markdown(f"**{selected} Composite Score: {row['overall_score']:.1f} / 100**")
        display_cols = ["name", "ticker", "overall_score", "valuation_score", "profitability_score",
                         "growth_score", "health_score", "momentum_stability_score",
                         "trailing_pe", "price_to_book", "roe", "profit_margin",
                         "revenue_growth", "debt_to_equity"]
        display_cols = [c for c in display_cols if c in df.columns]
        st.dataframe(
            df[display_cols].sort_values("overall_score", ascending=False),
            use_container_width=True,
            height=440,
        )