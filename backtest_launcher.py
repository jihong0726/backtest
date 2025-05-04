import pandas as pd
from backtest_utils import fetch_5m_klines, calculate_atr, apply_fee
from backtest_strategy import strategy_decision
from backtest_settings import LEVERAGE, CAPITAL, TP_MULTIPLIER, SL_MULTIPLIER

symbol = input("请输入币种（如 BTC-USDT-SWAP）：")
date = input("请输入回测日期（如 2024-05-01）：")

df = fetch_5m_klines(symbol, date, date)
if df.empty:
    print("❌ 无法获取K线数据")
    exit()

df = calculate_atr(df)

direction = strategy_decision(df)
print(f"策略建议：{direction}")

if direction == "neutral":
    print("当前无开仓信号")
else:
    entry_price = df['close'].iloc[-1]
    atr = df['ATR'].iloc[-1] if not pd.isna(df['ATR'].iloc[-1]) else 0.01

    if direction == "long":
        tp = entry_price + atr * TP_MULTIPLIER
        sl = entry_price - atr * SL_MULTIPLIER
    else:
        tp = entry_price - atr * TP_MULTIPLIER
        sl = entry_price + atr * SL_MULTIPLIER

    print(f"入场价：{entry_price}")
    print(f"止盈价：{tp}")
    print(f"止损价：{sl}")

    # 假设实际行情平仓价格
    exit_price = df['close'].iloc[-1]  # 这里假设持有一根K线

    profit = apply_fee(entry_price, exit_price, direction) * LEVERAGE * CAPITAL
    print(f"模拟平仓盈亏（扣手续费）：{profit:.4f} USDT")
