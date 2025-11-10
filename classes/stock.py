import random

class Stock:
    def __init__(self, name, price, currency="coin",
                 base_up_prob=0.7, base_min_mult=0.99, base_max_mult=1.01):
        self.name = name
        self.price = price
        self.price_history = [price]
        self.currency = currency

        # 각 종목마다 ±10% 오차 적용
        self.up_prob = self._apply_random_error(base_up_prob, 0.1, 0, 1)
        self.min_mult = self._apply_random_error(base_min_mult, 0.1)
        self.max_mult = self._apply_random_error(base_max_mult, 0.1)

        self.selected = False  # 선택 상태 표시

    def _apply_random_error(self, value, error_ratio, min_val=None, max_val=None):
        delta = value * error_ratio
        val = random.uniform(value - delta, value + delta)
        if min_val is not None:
            val = max(val, min_val)
        if max_val is not None:
            val = min(val, max_val)
        return val

    def update_price(self):
        if random.random() < self.up_prob:
            multiplier = random.uniform(1.0, self.max_mult)
        else:
            multiplier = random.uniform(self.min_mult, 1.0)

        self.price *= multiplier
        self.price = round(self.price, 2)
        self.price_history.append(self.price)
