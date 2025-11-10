class Stock:
    def __init__(self, name, price):
        self.name = name
        self.price = price
        self.price_history = [price]

    def update_price(self):
        import random
        # 0.9 ~ 1.1 배율 랜덤
        multiplier = random.uniform(0.9, 1.1)
        self.price *= multiplier
        self.price = round(self.price, 2)
        self.price_history.append(self.price)
