---
name: nasdaq-daily
version: "2.1"
description: 纳斯达克100指数日报生成与推送。每天早上自动从 Investing.com 获取准确数据，生成日报并推送到飞书。包含核心数据、板块分析、中概股表现及20个交易日历史数据表格。Use when: (1) 需要获取纳斯达克100每日行情, (2) 定时推送美股日报, (3) 跟踪科技股和中概股表现
---

# 纳斯达克100指数日报 v2.0

每天早上6点自动生成并推送纳斯达克100指数日报，数据严格来源于 Investing.com 官方历史数据表格。

## 日报内容结构

日报分为**两条独立消息**推送：

### 消息一：核心日报
```
📊 核心数据（纳斯达克100指数）
• 收盘：点数 + 涨跌点数 + 涨跌幅%
• 开盘：点数
• 最高/最低：点数 / 点数
• 交易量：亿股

📈 关联指数
• 纳斯达克综合指数：点数 + 涨跌幅
• 道琼斯指数：点数 + 涨跌幅  
• 标普500指数：点数 + 涨跌幅

🔥 板块/个股亮点
• 科技股：英伟达、特斯拉、微软、苹果、谷歌、Meta、亚马逊
• 芯片股：博通、英特尔、AMD、高通

🇨🇳 中概股表现
• 纳斯达克中国金龙指数涨跌幅
• 个股：阿里巴巴、京东、拼多多、百度、蔚来、小鹏汽车、理想汽车

📰 市场要闻
• 涨跌驱动因素（宏观政策、地缘事件、重要财报）
```

### 消息二：历史数据表格（独立推送）
```
📅 纳斯达克100指数 - 近20个交易日历史数据
━━━━━━━━━━━━━━━━━━━━━━

| 日期 | 收盘 | 涨跌幅 |
|------|------|--------|
| MM月DD日 | XX,XXX.XX | +/-X.XX% |
| ... | ... | ... |

📊 月度统计
━━━━━━━━━━━━━━━━━━━━━━
• 区间最高：XX,XXX.XX (MM/DD)
• 区间最低：XX,XXX.XX (MM/DD)
• 区间涨跌：-X,XXX.XX 点 (-X.XX%)
• 上涨天数：X天 | 下跌天数：X天
```

**配置项**（`config.json`）：
```json
{
  "history": {
    "enabled": true,        // 是否启用历史数据
    "days": 20,             // 交易日数量
    "show_stats": true,     // 是否显示月度统计
    "separate_message": true // 是否作为独立消息推送
  }
}
```

## 数据源规范（⚠️ 严格遵循）

### 主数据源（必须）

**纳斯达克100指数历史数据**：
```
https://cn.investing.com/indices/nq-100-historical-data
```

**页面结构**：
- 表格列顺序：日期 | 收盘 | 开盘 | 高 | 低 | 交易量 | 涨跌幅
- 最新日期在第一行
- 收盘价格格式如：24,188.59

### 关联指数数据源

| 指数 | URL |
|------|-----|
| 纳斯达克综合指数 | https://cn.investing.com/indices/nasdaq-composite-historical-data |
| 道琼斯指数 | https://cn.investing.com/indices/us-30-historical-data |
| 标普500 | https://cn.investing.com/indices/us-spx-500-historical-data |

### 备用数据源（当 Investing.com 无法访问时）

| 优先级 | 数据源 | URL |
|--------|--------|-----|
| P1 | Investing.com | https://cn.investing.com/indices/nq-100-historical-data |
| P2 | Yahoo Finance | https://finance.yahoo.com/quote/%5ENDX/history |
| P3 | 新浪财经 | https://finance.sina.com.cn/stock/usstock/c/NASDAQ.shtml |

## 数据抓取方案

### 方案一：Playwright（推荐，最可靠）

**原理**：使用真实 Chromium 浏览器渲染页面，绕过 Cloudflare 检测

**安装**：
```bash
# 安装 Playwright
pip install playwright
playwright install chromium
```

**核心代码** (`scripts/fetch_data.py`)：
```python
from playwright.sync_api import sync_playwright
import json

def fetch_nasdaq100():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()
        
        # 访问页面并等待表格加载
        page.goto('https://cn.investing.com/indices/nq-100-historical-data')
        page.wait_for_selector('table', timeout=30000)
        
        # 提取最新日期数据
        rows = page.query_selector_all('table tr')
        for row in rows[1:]:  # 跳过表头
            cells = row.query_selector_all('td')
            if len(cells) >= 7:
                data = {
                    'date': cells[0].inner_text().strip(),
                    'close': cells[1].inner_text().strip(),
                    'open': cells[2].inner_text().strip(),
                    'high': cells[3].inner_text().strip(),
                    'low': cells[4].inner_text().strip(),
                    'volume': cells[5].inner_text().strip(),
                    'change': cells[6].inner_text().strip()
                }
                return data
        
        browser.close()

def fetch_history(days=20):
    """获取近N个交易日历史数据"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()
        
        page.goto('https://cn.investing.com/indices/nq-100-historical-data')
        page.wait_for_selector('table', timeout=30000)
        
        rows = page.query_selector_all('table tr')
        history = []
        
        for row in rows[1:days+1]:  # 获取前N行
            cells = row.query_selector_all('td')
            if len(cells) >= 7:
                history.append({
                    'date': cells[0].inner_text().strip(),
                    'close': cells[1].inner_text().strip(),
                    'change': cells[6].inner_text().strip()
                })
        
        browser.close()
        return history

if __name__ == '__main__':
    result = fetch_nasdaq100()
    history = fetch_history(20)
    print(json.dumps({
        'latest': result,
        'history': history
    }, ensure_ascii=False))
```

### 方案二：DrissionPage（轻量级）

**原理**：集成 requests 和浏览器自动化，自动处理动态内容

**安装**：
```bash
pip install DrissionPage
```

**核心代码**：
```python
from DrissionPage import ChromiumPage

def fetch_data():
    page = ChromiumPage()
    page.get('https://cn.investing.com/indices/nq-100-historical-data')
    
    # 等待表格
    table = page.ele('tag:table')
    rows = table.eles('tag:tr')
    
    # 提取第一行数据（最新日期）
    first_data_row = rows[1]
    cells = first_data_row.eles('tag:td')
    
    return {
        'date': cells[0].text,
        'close': cells[1].text,
        'change': cells[6].text
    }
```

## 目录结构

```
nasdaq-daily/
├── SKILL.md                    # 本文件
├── config.json                 # 配置文件
├── scripts/
│   ├── fetch_data.py          # 数据抓取脚本
│   ├── generate_report.py     # 日报生成脚本
│   └── send_report.py         # 推送脚本
├── data/
│   ├── nasdaq100_history.json # 历史数据缓存
│   └── latest.json            # 最新数据
└── logs/
    └── fetch.log              # 抓取日志
```

## 配置文件 (`config.json`)

```json
{
  "primary_source": "https://cn.investing.com/indices/nq-100-historical-data",
  "backup_sources": [
    "https://finance.yahoo.com/quote/%5ENDX/history",
    "https://finance.sina.com.cn/stock/usstock/c/NASDAQ.shtml"
  ],
  "push": {
    "enabled": true,
    "channel": "feishu",
    "target": "ou_263b05f3f8bcbdb299bd0fdda204b047"
  },
  "schedule": {
    "cron": "7 6 * * *",
    "timezone": "Asia/Shanghai"
  },
  "history": {
    "enabled": true,
    "days": 20,
    "show_stats": true,
    "separate_message": true
  },
  "stocks": {
    "tech": ["NVDA", "TSLA", "MSFT", "AAPL", "GOOGL", "META", "AMZN"],
    "chips": ["AVGO", "INTC", "AMD", "QCOM"],
    "china": ["BABA", "JD", "PDD", "BIDU", "NIO", "XPEV", "LI"]
  }
}
```

### 配置说明

| 配置项 | 类型 | 说明 |
|--------|------|------|
| `history.enabled` | boolean | 是否启用历史数据表格 |
| `history.days` | number | 展示交易日数量（推荐20天，约一个月） |
| `history.show_stats` | boolean | 是否显示区间最高/最低/涨跌统计 |
| `history.separate_message` | boolean | 是否作为**独立消息**推送（true时历史表格单独发送） |

## 使用方法

### 1. 安装依赖

```bash
cd /root/.openclaw/skills/nasdaq-daily

# 安装 Playwright
pip install playwright
playwright install chromium

# 或使用 DrissionPage
pip install DrissionPage
```

### 2. 手动测试数据抓取

```bash
python3 scripts/fetch_data.py
```

### 3. 生成并推送日报

```bash
python3 scripts/generate_report.py --send
```

### 4. 设置定时任务

使用 OpenClaw cron：
```json
{
  "name": "nasdaq-daily-push",
  "schedule": {"kind": "cron", "expr": "7 6 * * *", "tz": "Asia/Shanghai"},
  "payload": {
    "kind": "agentTurn",
    "message": "运行 nasdaq-daily skill：抓取 Investing.com 的纳斯达克100数据，生成日报并推送到飞书。优先使用 Playwright 方案获取 https://cn.investing.com/indices/nq-100-historical-data 页面数据。"
  },
  "sessionTarget": "isolated"
}
```

## GitHub 发布安全规范

**⚠️ Token 严禁明文存储**

### 安全存储方案

1. **环境变量存储**（推荐）：
```bash
# 创建 secrets 目录
mkdir -p ~/.openclaw/secrets

# 保存 Token（仅所有者可读）
echo 'GITHUB_TOKEN=ghp_xxxxx' > ~/.openclaw/secrets/github.env
chmod 600 ~/.openclaw/secrets/github.env

# 使用时加载
source ~/.openclaw/secrets/github.env
curl -H "Authorization: token $GITHUB_TOKEN" ...
```

2. **OpenClaw 环境变量**：
```bash
# 添加到 openclaw 配置
export GITHUB_TOKEN="ghp_xxxxx"
```

### 发布脚本示例

```bash
#!/bin/bash
# scripts/publish.sh

# 加载 Token
source ~/.openclaw/secrets/github.env

# 推送到 GitHub
git push https://${GITHUB_TOKEN}@github.com/username/repo.git main
```

### Token 安全守则
- ❌ 绝不提交到 Git 仓库
- ❌ 绝不硬编码在脚本中
- ❌ 绝不在日志中输出
- ✅ 定期轮换（3-6个月）
- ✅ 仅授予最小必要权限（repo/public_repo）

## 历史数据表格格式

日报中的「近一个月历史数据」部分格式如下：

```
📅 近一个月历史数据
━━━━━━━━━━━━━━━━━━━━━━
| 日期 | 收盘 | 涨跌幅 |
|------|------|--------|
| 2026-03-23 | 24,188.59 | +1.22% |
| 2026-03-20 | 23,898.15 | -1.88% |
| ... | ... | ... |

月度统计：
• 区间最高：25,329.04 (02/25)
• 区间最低：23,898.15 (03/20)
• 区间涨跌：-1,140.45 点 (-4.51%)
• 上涨天数：9天 | 下跌天数：11天
```

**表格数据要求**：
- 展示近20个交易日（约一个月）
- 日期格式：YYYY-MM-DD
- 收盘价格保留2位小数
- 涨跌幅保留2位小数，带正负号
- 当日数据用粗体标注

**统计数据要求**：
- 区间最高/最低：从20天数据中找出极值
- 区间涨跌：首日收盘 - 最新收盘
- 上涨/下跌天数：统计正负天数

## 错误处理

### 常见错误

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| Cloudflare 拦截 | 请求被识别为机器人 | 使用 Playwright 真实浏览器 |
| 页面结构变化 | Investing.com 改版 | 更新 CSS 选择器 |
| 数据为空 | 美股休市或数据未更新 | 跳过并记录日志 |
| 网络超时 | 连接问题 | 重试3次后使用备用源 |

### 日志记录

所有操作记录到 `logs/fetch.log`，便于排查：
```
[2026-03-24 06:00:01] INFO: 开始抓取数据
[2026-03-24 06:00:08] INFO: 成功获取 NASDAQ100 数据: 24188.59 (+1.22%)
[2026-03-24 06:00:10] INFO: 日报已推送到飞书
```

## 验证数据准确性

抓取后必须验证以下字段：
- [ ] 日期格式正确（2026年03月23日）
- [ ] 收盘价格格式正确（24,188.59）
- [ ] 涨跌幅包含正负号（+1.22% 或 -0.50%）
- [ ] 数值范围合理（20000-30000 之间）

**交叉验证**：与 Yahoo Finance 或新浪财经对比，差异超过 0.5% 需人工确认。

## 阳阳的要求

> "我就要这个页面的数据，你想办法"

**承诺**：
1. 严格从 `https://cn.investing.com/indices/nq-100-historical-data` 获取数据
2. 使用 Playwright 真实浏览器绕过 Cloudflare
3. 每日抓取后记录原始数据，确保可追溯
4. 如遇抓取失败，使用备用源但明确标注，绝不隐瞒数据来源

---

**版本": 2.1
**更新日期**: 2026-03-24
**维护者**: Kimi Claw

---

## 版本更新日志

### v2.1 (2026-03-26)
- 历史数据表格作为**独立消息**推送（`separate_message: true`）
- 20个交易日涨跌幅表格格式规范  
- 日报内容结构拆分说明（核心日报 + 历史表格两条消息）
- 配置文件中 `history` 配置项扩展，支持 `separate_message` 选项

### v2.0 (2026-03-24)
- Playwright 数据抓取方案
- 近一个月历史数据表格
- 区间最高/最低/涨跌统计
- 数据源规范（严格遵循 Investing.com）

