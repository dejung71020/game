class Player:
    def __init__(self):
        # 각 화폐별 현금
        self.cash = {
            "원": 100.0,
            "코인": 0.0,
            "금": 0.0,
            "스탁": 0.0
        }
        # 보유 종목: {Stock: {"quantity": int, "buy_price": float, "currency": str}}
        self.owned_stocks = {}

    # ---------------- 투자 ----------------
    def invest(self, stock, quantity):
        cost = stock.price * quantity
        currency = stock.currency  # Stock 클래스에서 currency 속성 사용
        if self.cash[currency] >= cost:
            self.cash[currency] -= cost
            if stock in self.owned_stocks:
                old_qty = self.owned_stocks[stock]["quantity"]
                old_price = self.owned_stocks[stock]["buy_price"]
                new_avg = (old_price*old_qty + stock.price*quantity)/(old_qty + quantity)
                self.owned_stocks[stock]["quantity"] += quantity
                self.owned_stocks[stock]["buy_price"] = new_avg
            else:
                self.owned_stocks[stock] = {"quantity": quantity, "buy_price": stock.price, "currency": currency}
            return True
        return False

    # ---------------- 총보유자산 ----------------
    def total_assets(self):
        total = 0
        # 1) 현금화된 원
        total += self.cash["원"]
        # 2) 각 화폐 단위로 산 종목 가치 합산
        for stock, info in self.owned_stocks.items():
            total += stock.price * info["quantity"]
        return total

    # ---------------- 화폐별 현금만 ----------------
    def assets_by_currency(self):
        return self.cash.copy()
