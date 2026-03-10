from jesse.strategies import Strategy
import jesse.indicators as ta

class SimpleCross(Strategy):
    # 定义短线和长线指标
    @property
    def short_ema(self):
        return ta.ema(self.candles, 20)

    @property
    def long_ema(self):
        return ta.ema(self.candles, 50)

    # 做多条件：短线上穿长线
    def should_long(self) -> bool:
        return self.short_ema > self.long_ema

    # 做空条件：短线下穿长线
    def should_short(self) -> bool:
        return self.short_ema < self.long_ema

    def should_cancel_entry(self) -> bool:
        return False

    # 执行做多操作：全仓买入
    def go_long(self):
        qty = self.capital / self.price
        self.buy = qty, self.price

    # 执行做空操作：全仓卖出
    def go_short(self):
        qty = self.capital / self.price
        self.sell = qty, self.price
