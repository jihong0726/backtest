# backtest_settings.py

# 杠杆 & 资金
LEVERAGE = 10
CAPITAL = 10  # 每次开仓本金 USDT

# 手续费（开仓和平仓）
FEE_RATE = 0.0006  # 0.06%

# ATR 乘数
TP_MULTIPLIER = 1.5
SL_MULTIPLIER = 1.0

# OKX API 公共接口（历史K线）
OKX_KLINE_URL = "https://www.okx.com/api/v5/market/history-candles"
