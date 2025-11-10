import random

class Stock:
    def __init__(self, name, price, currency="coin",
                 base_up_prob=0.7, base_min_mult=0.5, base_max_mult=2.0):
        self.name = name
        self.price = price
        self.price_history = [price]
        self.currency = currency
        self.up_prob = base_up_prob
        self.min_mult = base_min_mult
        self.max_mult = base_max_mult
        self.selected = False

    def update_price(self):
        if random.random() < self.up_prob:
            multiplier = random.uniform(1.0, self.max_mult)
        else:
            multiplier = random.uniform(self.min_mult, 1.0)
        self.price *= multiplier
        self.price = round(self.price,2)
        self.price_history.append(self.price)
