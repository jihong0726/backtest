import pandas as pd
import datetime
from strategy_v7_3 import generate_signal
from backtest_utils import fetch_historical_klines, calculate_fee, calculate_atr
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# =================== Google Sheet 设置 ====================
SPREADSHEET_ID = '1eKEjJfAWtgIBtMDlbdocc2ZXYvi0uAJR_YbkMdaIWdg'
SHEET_NAME = 'Backtest'
CREDENTIALS_FILE = 'cryptobotsheet-1fced9e786b8.json'

def write_to_google_sheet(data):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
    sheet.append_row(data, value_input_option='USER_ENTERED')
# ========================================================

# =================== 回测参数 ============================
symbol_list = ["BTC-USDT-SWAP", "TRUMP-USDT-SWAP"]
start_date = "2024-01-01"
end_date = "2024-04-30"
initial_capital = 10  # 每次开仓 10U
leverage = 10
min_profit = 0.2
fee_rate = 0.0006
# ========================================================

results = []
for symbol in symbol_list:
    print(f"🔎 正在回测 {symbol}...")
    df = fetch_historical_klines(symbol, start_date, end_date, interval="5m")
    if df is None or df.empty:
        print(f"[跳过] {symbol} 无法获取数据。")
        continue

    df["signal"] = df.apply(lambda row: generate_signal(row, symbol), axis=1)
    atr = calculate_atr(df, period=14)

    # 回测逻辑
    wins = 0
    losses = 0
    total_trades = 0

    for i in range(14, len(df)-1):  # 从 ATR 计算后开始
        signal = df.iloc[i]["signal"]
        price = df.iloc[i]["close"]
        next_price = df.iloc[i+1]["close"]
        atr_value = atr.iloc[i]

        if signal in ["long", "short"]:
            entry_price = price
            tp = entry_price + 1.5 * atr_value if signal == "long" else entry_price - 1.5 * atr_value
            sl = entry_price - 1 * atr_value if signal == "long" else entry_price + 1 * atr_value

            # 模拟下一根 K 线价格波动（简化版）
            hit_tp = (next_price >= tp) if signal == "long" else (next_price <= tp)
            hit_sl = (next_price <= sl) if signal == "long" else (next_price >= sl)

            fee = calculate_fee(entry_price, initial_capital, leverage, fee_rate)

            if hit_tp:
                profit = (abs(tp - entry_price) * initial_capital * leverage) - fee
                result = "Win" if profit >= min_profit else "Loss"
            elif hit_sl:
                result = "Loss"
            else:
                result = "Hold"

            total_trades += 1
            if result == "Win":
                wins += 1
            elif result == "Loss":
                losses += 1

            # 记录
            timestamp = df.iloc[i]["timestamp"]
            record = [
                symbol,
                datetime.datetime.utcfromtimestamp(timestamp/1000).strftime("%Y-%m-%d %H:%M"),
                signal,
                entry_price,
                tp,
                sl,
                next_price,
                result
            ]
            results.append(record)

            # 写入 Google Sheet
            write_to_google_sheet(record)

    win_rate = wins / total_trades * 100 if total_trades > 0 else 0
    print(f"✅ {symbol} 回测完成：交易 {total_trades} 次，胜率 {win_rate:.2f}%")

# CSV 备份
columns = ["币对", "时间", "信号", "开仓价", "止盈价", "止损价", "下一根K线收盘价", "结果"]
pd.DataFrame(results, columns=columns).to_csv("backtest_results.csv", index=False)
print("📊 回测结果已保存到 backtest_results.csv 和 Google Sheet。")
