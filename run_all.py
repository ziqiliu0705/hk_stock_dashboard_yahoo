# -*- coding: utf-8 -*-
"""
一键运行脚本
------------
依次执行：
1. fetch_data.py  —— 抓取数据
2. analysis.py    —— 计算指标
3. 自动启动 streamlit 仪表盘

运行方式：python run_all.py
"""

import subprocess
import sys


def run_step(description, command):
    print(f"\n{'='*50}\n▶ {description}\n{'='*50}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"❌ 执行失败: {command}")
        sys.exit(1)


def main():
    run_step("第1步/3：抓取行业数据", f"{sys.executable} fetch_data.py")
    run_step("第2步/3：计算分析指标", f"{sys.executable} analysis.py")
    print(f"\n{'='*50}\n▶ 第3步/3：启动可视化仪表盘（浏览器将自动打开）\n{'='*50}")
    subprocess.run(f"{sys.executable} -m streamlit run dashboard.py", shell=True)


if __name__ == "__main__":
    main()
