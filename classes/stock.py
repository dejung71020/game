# classes/stock.py
import random

class Stock:
    """
    사용자가 직접 설정한 상승 확률, 최대 증가 배율, 최대 하락 배율을 적용하는 클래스.
    """
    def __init__(self, name, price, currency, bias, max_gain_mult, max_loss_mult):
        self.name = name
        self.currency = currency
        self._price = price
        self.bias = bias                        # 상승 확률 (0.0 ~ 1.0)
        self.max_gain_mult = max_gain_mult      # 최대 상승 배율 (예: 20.0)
        self.max_loss_mult = max_loss_mult      # 최대 하락 배율 (예: 0.01)
        
        self.selected = False
        self.price_history = [price] 
        self.max_history_length = 100 

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, new_price):
        self._price = max(0.01, new_price)

    def update_price(self):
        """가격 변동 로직을 실행하고 이력을 저장합니다."""
        
        # 1. 방향 결정 (Bias 반영)
        if random.random() < self.bias:
            # 2. 상승 방향: 최대 증가 배율 (max_gain_mult) 사용
            # 상승 배율은 1.0 (변동 없음)부터 max_gain_mult 사이에서 결정
            # 변동율 = (랜덤 배율 - 1.0)
            multiplier = random.uniform(1.0, self.max_gain_mult)
        else:
            # 2. 하락 방향: 최대 하락 배율 (max_loss_mult) 사용
            # 하락 배율은 max_loss_mult부터 1.0 (변동 없음) 사이에서 결정
            # 변동율 = (랜덤 배율 - 1.0)
            multiplier = random.uniform(self.max_loss_mult, 1.0)
            
        # 3. 새로운 가격 계산
        new_price = self._price * multiplier
        
        # 4. 가격 업데이트 및 이력 저장
        self._price = max(0.01, new_price) 
        
        self.price_history.append(self._price)
        if len(self.price_history) > self.max_history_length:
            self.price_history.pop(0)