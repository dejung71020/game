import random

class Stock:
    def __init__(self, name, price, currency, base_min_mult, base_max_mult, bias=0.5):
        self.name = name
        self.currency = currency
        self._price = price  # 내부 변수로 가격 저장
        self.base_min_mult = base_min_mult
        self.base_max_mult = base_max_mult
        self.bias = bias # 종목별 상승 경향성 (0.0 ~ 1.0)
        self.selected = False
        self.price_history = [price] 
        self.max_history_length = 100 

    @property
    def price(self):
        """현재 가격을 반환하는 getter."""
        return self._price

    @price.setter
    def price(self, new_price):
        """가격 설정 시 0 미만 방지 및 이력에 추가 (사용 권장 안 함)"""
        self._price = max(0.01, new_price)

    def update_price(self):
        """가격 변동 로직을 실행하고 이력을 저장합니다."""
        
        # 1. 변동 폭 크기 결정 (Volatility)
        # base_max_mult 값이 클수록 변동 폭이 커지도록 합니다.
        # 예: base_max_mult=10 (스탁)은 base_max_mult=1000 (원)보다 변동 폭이 작음
        
        # '원'의 최대치(1000)를 기준으로 상대적 변동성 비율을 계산 (최대 1.0)
        vol_factor = self.base_max_mult / 1000.0 if self.base_max_mult > 0 else 0.01
        
        # 기본 변동률 (최소 0.001% ~ 최대 5%까지 변동 가능하도록 설정)
        min_volatility = 0.00001
        base_max_change_limit = 0.05
        max_volatility = base_max_change_limit * vol_factor
        
        # 실제 적용될 변동률 (크기)
        volatility = random.uniform(min_volatility, max_volatility)
        
        
        # 2. 방향 결정 (Bias 반영)
        # self.bias 확률로 상승 (direction = 1)
        if random.random() < self.bias:
            direction = 1  # 상승
        else:
            direction = -1 # 하락
            
        # 3. 가격 업데이트
        change_amount = self._price * (direction * volatility)
        new_price = self._price + change_amount
        
        # 가격이 0 미만이 되는 것을 방지
        self._price = max(0.01, new_price) 
        
        # 4. 가격 이력 업데이트
        self.price_history.append(self._price)
        
        # 5. 리스트 크기를 제한 (가장 오래된 데이터를 제거)
        if len(self.price_history) > self.max_history_length:
            self.price_history.pop(0)