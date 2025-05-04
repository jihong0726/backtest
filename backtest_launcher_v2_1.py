import pandas as pd
from backtest_strategy import get_trade_signal
from backtest_utils import fetch_klines, calculate_atr, apply_fees
from datetime import datetime, timedelta
import csv

START_DATE = input("请输入回测开始日期（YYYY-MM-DD）：")
END_DATE = input("请输入回测结束日期（YYYY-MM-DD）：")

symbols = ["BTC-USDT-SWAP", "TRUMP-USDT-SWAP"]
timeframe = "5m"

initial_balance = 10
leverage = 10
target_profit = 0.2  # USDT
fee_rate = 0.0006

results = []
consecutive_losses = 0
max_consecutive_losses = 0

for symbol in symbols:
    print(f"🚀 正在分析：{symbol}")

    klines = fetch_klines(symbol, START_DATE, END_DATE, timeframe)
    if klines.empty:
        print(f"[跳过] 无法获取 {symbol} 的K线数据")
        continue

    for i in range(50, len(klines)-1):
        kline = klines.iloc[:i+1]  # 截取到当前
        signal = get_trade_signal(kline)

        if signal["direction"] == "neutral":
            continue  # 不做观望单

        entry_price = kline.iloc[-1]["close"]
        atr = calculate_atr(kline)

        if atr == 0 or pd.isna(atr):
            continue

        direction = signal["direction"]
        take_profit = entry_price + 1.5 * atr if direction == "long" else entry_price - 1.5 * atr
        stop_loss = entry_price - 1 * atr if direction == "long" else entry_price + 1 * atr

        trade_outcome = None
        exit_price = None
        outcome_time = None

        for j in range(i+1, len(klines)):
            next_price = klines.iloc[j]["close"]
            if direction == "long":
                if next_price >= take_profit:
                    trade_outcome = "win"
                    exit_price = take_profit
                    outcome_time = klines.iloc[j]["timestamp"]
                    break
                elif next_price <= stop_loss:
                    trade_outcome = "loss"
                    exit_price = stop_loss
                    outcome_time = klines.iloc[j]["timestamp"]
                    break
            else:
                if next_price <= take_profit:
                    trade_outcome = "win"
                    exit_price = take_profit
                    outcome_time = klines.iloc[j]["timestamp"]
                    break
                elif next_price >= stop_loss:
                    trade_outcome = "loss"
                    exit_price = stop_loss
                    outcome_time = klines.iloc[j]["timestamp"]
                    break

        if trade_outcome is None:
            continue

        pnl = ((exit_price - entry_price) / entry_price) * leverage * initial_balance
        if direction == "short":
            pnl *= -1

        pnl = apply_fees(pnl, initial_balance, fee_rate)
        result = {
            "时间": kline.iloc[-1]["timestamp"],
            "币种": symbol,
            "方向": "做多" if direction == "long" else "做空",
            "开仓价": round(entry_price, 6),
            "平仓价": round(exit_price, 6),
            "盈亏": round(pnl, 3),
            "结果": trade_outcome,
            "结束时间": outcome_time
        }
        results.append(result)

        # 连续亏损统计
        if pnl >= target_profit:
            consecutive_losses = 0
        else:
            consecutive_losses += 1
            if consecutive_losses > max_consecutive_losses:
                max_consecutive_losses = consecutive_losses

print("✅ 回测完成，正在统计结果...")

df = pd.DataFrame(results)
if not df.empty:
    total_trades = len(df)
    wins = df[df["盈亏"] >= target_profit]
    losses = df[df["盈亏"] < target_profit]

    print(f"总交易次数：{total_trades}")
    print(f"盈利次数：{len(wins)}")
    print(f"亏损次数：{len(losses)}")
    print(f"胜率：{round(len(wins)/total_trades*100, 2)}%")
    print(f"平均盈利：{round(wins['盈亏'].mean(), 3) if not wins.empty else 0}")
    print(f"平均亏损：{round(losses['盈亏'].mean(), 3) if not losses.empty else 0}")
    print(f"最大连续亏损次数：{max_consecutive_losses}")
    print(f"最大单笔盈利：{round(df['盈亏'].max(), 3)}")
    print(f"最大单笔亏损：{round(df['盈亏'].min(), 3)}")

    csv_filename = f"backtest_result_{START_DATE}_to_{END_DATE}.csv"
    df.to_csv(csv_filename, index=False, encoding="utf-8-sig")
    print(f"✅ 结果已保存为 {csv_filename}")
else:
    print("没有符合条件的交易。")
