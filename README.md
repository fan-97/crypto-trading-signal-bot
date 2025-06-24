# Crypto Trading Signal Bot

一个基于技术分析和K线形态的加密货币交易信号机器人。

## 功能特点

- 实时监控多个交易对和时间周期
- 技术指标分析（SMA、EMA、MACD、RSI等）
- K线形态识别（锤子线、吞没形态等）
- Telegram实时通知
- 自动生成交易建议

## 技术指标

- 趋势指标：
  - SMA（简单移动平均线）：20、50、200日
  - EMA（指数移动平均线）：20、50日
  - MACD（移动平均趋同散离）
  - ADX（平均趋向指标）
  - 一目均衡图（Ichimoku）
  - 抛物线SAR

- 动量指标：
  - RSI（相对强弱指标）
  - KDJ（随机指标）
  - Williams %R（威廉指标）
  - ROC（变动率）
  - AO（动量震荡器）

- 波动率指标：
  - 布林带（Bollinger Bands）
  - ATR（真实波幅）
  - 唐奇安通道（Donchian Channel）

- 成交量指标：
  - VWAP（成交量加权平均价格）
  - OBV（能量潮）
  - 动量指标（Force Index）
  - MFI（资金流量指标）

## K线形态识别

- 看涨形态：
  - 锤子线（Hammer）
  - 早晨之星（Morning Star）
  - 看涨吞没（Bullish Engulfing）
  - 双针探底（Tweezer Bottom）

- 看跌形态：
  - 流星线（Shooting Star）
  - 黄昏之星（Evening Star）
  - 看跌吞没（Bearish Engulfing）
  - 上吊线（Hanging Man）

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/crypto-trading-signal-bot.git
cd crypto-trading-signal-bot
```

2. 创建虚拟环境：
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 配置环境变量：
复制 `.env.example` 为 `.env` 并填入你的配置：
```
# Telegram Settings
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_IDS=your_chat_id

# Binance API
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret
```

## 使用方法

1. 启动监控：
```bash
python monitor_crypto.py
```

2. 测试形态识别：
```bash
python test_patterns.py
```

## 项目结构

```
app/
├── services/
│   ├── futures_data_fetcher.py  # 币安期货数据获取
│   ├── pattern_recognition.py   # K线形态识别
│   ├── technical_analysis.py    # 技术指标分析
│   ├── signal_generator.py      # 交易信号生成
│   ├── telegram_notifier.py     # Telegram通知
│   └── market_monitor.py        # 市场监控
├── monitor_crypto.py            # 主程序
├── test_patterns.py            # 形态识别测试
└── requirements.txt            # 项目依赖
```

## 配置说明

1. Telegram机器人设置：
   - 使用 @BotFather 创建机器人
   - 获取机器人token
   - 获取聊天ID

2. 币安API设置：
   - 在币安创建API密钥
   - 确保API有读取权限

## 注意事项

- 本项目仅供学习和参考，不构成投资建议
- 请在实盘交易前充分测试
- 建议先用测试网进行测试

## 许可证

MIT License
