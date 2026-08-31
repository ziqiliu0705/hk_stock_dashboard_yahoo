# -*- coding: utf-8 -*-
"""
数据抓取主流程
--------------
流程：
1. 从候选池（config.CANDIDATE_TICKERS，可能20-30只）抓取基本面快照
2. 按总市值排序，只保留前 TOP_N 只，作为本次分析的正式股票池
3. 对这批入选股票抓取历史价格（用于走势图）
4. 保存三个文件：selected_tickers.csv / fundamentals.csv / prices.csv

运行方式：
    python fetch_data.py                          使用config.py里的默认日期区间
    python fetch_data.py --start 2023-01-01 --end 2024-12-31   自定义日期区间
"""

import argparse
import os
import sys

import data_sources as ds
from config import (
    CANDIDATE_TICKERS,
    TOP_N,
    DEFAULT_START_DATE,
    DEFAULT_END_DATE,
    DATA_DIR,
    FUNDAMENTALS_CSV,
    PRICES_CSV,
    SELECTED_TICKERS_CSV,
)


def parse_args():
    parser = argparse.ArgumentParser(description="抓取港股行业对标数据")
    parser.add_argument("--start", default=DEFAULT_START_DATE, help="历史价格起始日期 YYYY-MM-DD")
    parser.add_argument("--end", default=DEFAULT_END_DATE, help="历史价格结束日期 YYYY-MM-DD")
    return parser.parse_args()


def main():
    args = parse_args()
    os.makedirs(DATA_DIR, exist_ok=True)

    print(f"候选池共 {len(CANDIDATE_TICKERS)} 只股票，将按总市值筛选前 {TOP_N} 名\n")

    # 第1步：抓候选池全部的基本面快照（含市值），用于排序筛选
    fundamentals_df = ds.get_fundamentals(CANDIDATE_TICKERS)

    if fundamentals_df.empty or fundamentals_df["market_cap"].isna().all():
        print("\n❌ 未能获取到有效的市值数据，无法完成筛选，请检查数据源是否可用。")
        sys.exit(1)

    # 第2步：按市值排序，取前TOP_N
    fundamentals_df = fundamentals_df.dropna(subset=["market_cap"])
    fundamentals_df = fundamentals_df.sort_values("market_cap", ascending=False).head(TOP_N)
    fundamentals_df = fundamentals_df.reset_index(drop=True)

    selected_tickers = dict(zip(fundamentals_df["ticker"], fundamentals_df["name"]))
    print(f"\n✅ 已按总市值筛选出前 {len(selected_tickers)} 只股票：")
    for i, (t, n) in enumerate(selected_tickers.items(), 1):
        cap = fundamentals_df[fundamentals_df["ticker"] == t]["market_cap"].values[0]
        print(f"   {i}. {n} ({t})  总市值约 {cap/1e8:.1f} 亿" if cap else f"   {i}. {n} ({t})")

    fundamentals_df.to_csv(FUNDAMENTALS_CSV, index=False, encoding="utf-8-sig")
    pd_selected = fundamentals_df[["ticker", "name"]]
    pd_selected.to_csv(SELECTED_TICKERS_CSV, index=False, encoding="utf-8-sig")
    print(f"\n✅ 基本面数据已保存: {FUNDAMENTALS_CSV}")
    print(f"✅ 入选股票清单已保存: {SELECTED_TICKERS_CSV}")

    # 第3步：只对入选的这批股票抓历史价格
    print(f"\n开始抓取历史价格（{args.start} 至 {args.end}）...")
    price_df = ds.get_price_history(selected_tickers, args.start, args.end)
    price_df.to_csv(PRICES_CSV, encoding="utf-8-sig")
    print(f"✅ 历史价格数据已保存: {PRICES_CSV}（覆盖 {price_df.shape[1]} 只股票，{price_df.shape[0]} 个交易日）")


if __name__ == "__main__":
    main()
