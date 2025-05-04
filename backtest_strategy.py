def strategy_decision(df):
    # 简单逻辑：如果5MA上穿20MA做多，反之做空
    df['MA5'] = df['close'].rolling(window=5).mean()
    df['MA20'] = df['close'].rolling(window=20).mean()

    if df['MA5'].iloc[-2] < df['MA20'].iloc[-2] and df['MA5'].iloc[-1] > df['MA20'].iloc[-1]:
        return "long"
    elif df['MA5'].iloc[-2] > df['MA20'].iloc[-2] and df['MA5'].iloc[-1] < df['MA20'].iloc[-1]:
        return "short"
    else:
        return "neutral"
