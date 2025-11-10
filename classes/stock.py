import random

class Stock:
    def __init__(self, name, price, currency="coin",
                 base_up_prob=0.7, base_min_mult=0.99, base_max_mult=1.01):
        """
        name: 종목 이름
        price: 초기 가격
        currency: "coin", "gold", "diamond"
        base_up_prob: 기본 상승 확률
        base_min_mult, base_max_mult: 기본 변동폭
        """
        self.name = name
        self.price = price
        self.price_history = [price]
        self.currency = currency

        # 각 종목마다 ±10% 오차 적용
        self.up_prob = self._apply_random_error(base_up_prob, 0.1, min_val=0, max_val=1)
        self.min_mult = self._apply_random_error(base_min_mult, 0.1)
        self.max_mult = self._apply_random_error(base_max_mult, 0.1)

    def _apply_random_error(self, value, error_ratio, min_val=None, max_val=None):
        """
        value ± error_ratio * value 랜덤
        """
        delta = value * error_ratio
        val = random.uniform(value - delta, value + delta)
        if min_val is not None:
            val = max(val, min_val)
        if max_val is not None:
            val = min(val, max_val)
        return val

    def update_price(self):
        # 상승/하락 결정
        if random.random() < self.up_prob:
            # 상승
            multiplier = random.uniform(1.0, self.max_mult)
        else:
            # 하락
            multiplier = random.uniform(self.min_mult, 1.0)

        self.price *= multiplier
        self.price = round(self.price, 2)
        self.price_history.append(self.price)
