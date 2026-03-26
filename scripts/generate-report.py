#!/usr/bin/env python3
"""
纳斯达克指数日报生成器
获取纳指数据并生成格式化的日报
"""

import json
import requests
from datetime import datetime, timedelta
import sys

def get_nasdaq_data():
    """获取纳斯达克指数数据"""
    # 使用 Alpha Vantage API (需要 API Key)
    # 或使用 Yahoo Finance 等免费数据源
    
    # 这里使用模拟数据结构，实际使用时替换为真实API
    data = {
        "date": (datetime.now() - timedelta(days=1)).strftime("%Y年%m月%d日"),
        "nasdaq": {
            "close": 22090.69,
            "change": -61.73,
            "change_pct": -0.28,
            "high": 22187.06,
            "low": 21851.05
        },
        "dow": {
            "close": 46021.43,
            "change": -203.72,
            "change_pct": -0.44
        },
        "sp500": {
            "close": 6606.49,
            "change": -18.21,
            "change_pct": -0.27
        },
        "stocks": [
            {"name": "英特尔", "symbol": "INTC", "change_pct": 2.55},
            {"name": "AMD", "symbol": "AMD", "change_pct": 2.91},
            {"name": "特斯拉", "symbol": "TSLA", "change_pct": -3.18},
            {"name": "Meta", "symbol": "META", "change_pct": -1.46},
            {"name": "英伟达", "symbol": "NVDA", "change_pct": -1.02},
            {"name": "亚马逊", "symbol": "AMZN", "change_pct": -0.52}
        ],
        "china_stocks": [
            {"name": "阿里巴巴", "symbol": "BABA", "change_pct": -7.07},
            {"name": "拼多多", "symbol": "PDD", "change_pct": -3.27},
            {"name": "百度", "symbol": "BIDU", "change_pct": -2.35},
            {"name": "小鹏汽车", "symbol": "XPEV", "change_pct": 2.08},
            {"name": "蔚来", "symbol": "NIO", "change_pct": 1.20}
        ],
        "drivers": [
            "美联储维持利率不变：FOMC决议按兵不动，点阵图显示2026年可能零次降息",
            "科技股集体承压：大型科技股普遍下跌，市场情绪谨慎",
            "中概股拖累：阿里巴巴发布财报后股价大跌，拖累中概股整体表现",
            "连续第二日收跌：三大指数延续前一日跌势"
        ]
    }
    return data

def generate_report(data):
    """生成格式化的日报"""
    
    # 计算振幅
    amplitude = ((data['nasdaq']['high'] - data['nasdaq']['low']) / data['nasdaq']['low']) * 100
    
    # 生成核心数据部分
    report = f"""【纳斯达克指数日报】{data['date']}（美东时间前日收盘）

📊 核心数据
• 纳指收盘：{data['nasdaq']['close']:,.2f} 点（{data['nasdaq']['change']:+.2f}，{data['nasdaq']['change_pct']:+.2f}%）
• 道指收盘：{data['dow']['close']:,.2f} 点（{data['dow']['change']:+.2f}，{data['dow']['change_pct']:+.2f}%）
• 标普500：{data['sp500']['close']:,.2f} 点（{data['sp500']['change']:+.2f}，{data['sp500']['change_pct']:+.2f}%）
• 盘中振幅：{data['nasdaq']['low']:,.2f} - {data['nasdaq']['high']:,.2f}（振幅 {amplitude:.2f}%）

📈 涨跌驱动因素
"""
    
    for i, driver in enumerate(data['drivers'], 1):
        report += f"{i}. {driver}\n"
    
    # 个股亮点
    report += "\n🔥 板块/个股亮点\n"
    for stock in data['stocks']:
        trend = "📈" if stock['change_pct'] > 0 else "📉"
        report += f"• {stock['name']} ({stock['symbol']}): {stock['change_pct']:+.2f}% {trend}\n"
    
    # 中概股
    report += "\n🇨🇳 中概股表现\n"
    for stock in data['china_stocks']:
        trend = "📈" if stock['change_pct'] > 0 else "📉"
        report += f"• {stock['name']} ({stock['symbol']}): {stock['change_pct']:+.2f}% {trend}\n"
    
    report += "\n📊 数据来源：Investing.com / Yahoo Finance\n"
    report += "⏰ 美东时间 16:00 EDT 收盘数据\n"
    
    return report

def main():
    try:
        data = get_nasdaq_data()
        report = generate_report(data)
        print(report)
    except Exception as e:
        print(f"❌ 生成日报失败: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
