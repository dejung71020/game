class Player:
    def __init__(self):
        self.coins = 100  # 초기 코인
        self.owned_stocks = {}  # {Stock: {"quantity": int, "buy_price": float}}

    def invest(self, stock, quantity):
        cost = stock.price * quantity
        if self.coins >= cost:
            self.coins -= cost
            if stock in self.owned_stocks:
                old_qty = self.owned_stocks[stock]["quantity"]
                old_price = self.owned_stocks[stock]["buy_price"]
                new_avg = (old_price*old_qty + stock.price*quantity)/(old_qty + quantity)
                self.owned_stocks[stock]["quantity"] += quantity
                self.owned_stocks[stock]["buy_price"] = new_avg
            else:
                self.owned_stocks[stock] = {"quantity": quantity, "buy_price": stock.price}
            return True
        return False

    def total_value(self):
        total = 0
        for stock, info in self.owned_stocks.items():
            total += stock.price * info["quantity"]
        return total

    def profit_loss(self):
        total_buy = sum(info["buy_price"]*info["quantity"] for info in self.owned_stocks.values())
        total_now = self.total_value()
        if total_buy == 0:
            return 0
        return (total_now - total_buy)/total_buy*100
