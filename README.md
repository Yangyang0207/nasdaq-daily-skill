# NASDAQ-100 Daily Skill

纳斯达克100指数日报生成与推送 Skill for OpenClaw

## 功能

每天早上自动从 [Investing.com](https://cn.investing.com/indices/nq-100-historical-data) 获取纳斯达克100指数数据，生成日报并通过飞书推送。

### 日报内容

1. **核心日报** - 指数收盘数据、科技股/中概股表现、市场要闻
2. **历史数据表格** - 近20个交易日涨跌幅 + 月度统计

## 安装

```bash
# 克隆仓库
git clone https://github.com/Yangyang0207/nasdaq-daily-skill.git

# 进入目录
cd nasdaq-daily-skill

# 安装依赖
pip install playwright
playwright install chromium
```

## 配置

编辑 `config.json`：

```json
{
  "primary_source": "https://cn.investing.com/indices/nq-100-historical-data",
  "push": {
    "enabled": true,
    "channel": "feishu",
    "target": "your_feishu_user_id"
  },
  "schedule": {
    "cron": "7 6 * * *",
    "timezone": "Asia/Shanghai"
  },
  "history": {
    "enabled": true,
    "days": 20,
    "separate_message": true
  }
}
```

## 使用

### 手动运行

```bash
python3 scripts/generate-report.py
```

### 定时任务（OpenClaw）

```json
{
  "name": "nasdaq-daily-push",
  "schedule": {"kind": "cron", "expr": "7 6 * * *", "tz": "Asia/Shanghai"},
  "payload": {
    "kind": "agentTurn",
    "message": "运行 nasdaq-daily skill"
  },
  "sessionTarget": "isolated"
}
```

## 数据源

- **主数据源**: Investing.com (纳斯达克100历史数据表格)
- **备用源**: Yahoo Finance、新浪财经

## 版本更新

### v2.1 (2026-03-26)
- 历史数据表格作为独立消息推送
- 新增 `separate_message` 配置项

### v2.0 (2026-03-24)
- Playwright 数据抓取
- 近20个交易日历史数据
- 区间统计功能

## License

MIT
