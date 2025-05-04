import requests
import pandas as pd

from backtest_settings import OKX_KLINE_URL

def fetch_5m_klines(symbol, start_date, end_date, limit=100):
    params = {
        "instId": symbol,
        "bar": "5m",
        "limit": limit
    }
    res = requests.get(OKX_KLINE_URL, params=params).json()
    if "data" not in res or len(res["data"]) == 0:
        return pd.DataFrame()
    df = pd.DataFrame(res["data"], columns=[
        'ts', 'open', 'high', 'low', 'close', 'volume', '_1', '_2', '_3', '_4', '_5'
    ])
    df['close'] = df['close'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    return df[::-1]  # 时间顺序

def calculate_atr(df, period=14):
    df['tr'] = df['high'] - df['low']
    df['ATR'] = df['tr'].rolling(window=period).mean()
    return df

def apply_fee(entry_price, exit_price, direction):
    if direction == "long":
        net = (exit_price - entry_price) * (1 - 2 * 0.0006)
    else:
        net = (entry_price - exit_price) * (1 - 2 * 0.0006)
    return net
