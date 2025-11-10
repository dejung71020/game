class Player:
    def __init__(self):
        self.coins = 100
        self.owned_stock = None

    def invest(self, stock):
        self.owned_stock = stock

    def update_assets(self):
        if self.owned_stock:
            # 간단히 가격 변동분 반영
            self.coins = round(self.owned_stock.price, 2)