# -*- coding: utf-8 -*-
"""
配置文件：所有可调整参数都放在这里，方便你换行业/换股票池时不用改动其他代码。
"""

import datetime

# ============ 1. 选择你要分析的行业 ============
SECTOR_NAME = "HK-Listed Mainland Real Estate (Top 20 by Market Cap)"

# 候选池：先列出这个行业尽量全的公司（代码用 "xxxx.HK" 格式），
# 脚本会自动抓取每只股票的总市值，排序后只保留市值最高的 TOP_N 只进入正式分析。
# 这样即使某几个月排名有变化（比如新股上市、退市），也不需要手动改名单。
CANDIDATE_TICKERS = {
    "0688.HK": "COLI",
    "1109.HK": "CR Land",
    "2202.HK": "China Vanke",
    "0960.HK": "Longfor Group",
    "0817.HK": "China Jinmao",
    "3900.HK": "Greentown China",
    "3377.HK": "Sino-Ocean Group",
    "3383.HK": "Agile Group",
    "2007.HK": "Country Garden",
    "1918.HK": "Sunac China",
    "1813.HK": "KWG Group",
    "0123.HK": "Yuexiu Property",
    "0119.HK": "Poly Property",
    "0813.HK": "Shimao Group",
    "0884.HK": "CIFI Holdings",
    "3380.HK": "Logan Group",
    "1233.HK": "Times China",
    "1238.HK": "Powerlong",
    "2777.HK": "R&F Properties",
    "2772.HK": "Zhongliang Holdings",
    "0832.HK": "Central China RE",
    "1638.HK": "Kaisa Group",
    "3883.HK": "China Aoyuan",
    "0754.HK": "Hopson Development",
    "1628.HK": "Yuzhou Group",
    "3301.HK": "Ronshine China",
    "1996.HK": "Radiance Group",
    "1966.HK": "China SCE",
}
# 最终仪表盘只展示按总市值排序的前 N 名（脚本自动筛选，不用手动删减上面的候选池）
TOP_N = 20

# ============ 2. 时间范围设置（支持在仪表盘里自定义修改）============
# 默认回溯区间：过去2年到今天。仪表盘网页里也会有日期选择器，可以临时改，不用改这里。
DEFAULT_START_DATE = (datetime.date.today() - datetime.timedelta(days=730)).strftime("%Y-%m-%d")
DEFAULT_END_DATE = datetime.date.today().strftime("%Y-%m-%d")

# ============ 3. 请求节奏设置（yfinance 备用通道限流保护）============
REQUEST_DELAY_SECONDS = 3
MAX_RETRIES = 3
RETRY_BASE_WAIT_SECONDS = 20

# ============ 4. 输出路径 ============
DATA_DIR = "data"
FUNDAMENTALS_CSV = f"{DATA_DIR}/fundamentals.csv"
PRICES_CSV = f"{DATA_DIR}/prices.csv"
PROCESSED_CSV = f"{DATA_DIR}/processed_metrics.csv"
SELECTED_TICKERS_CSV = f"{DATA_DIR}/selected_tickers.csv"
