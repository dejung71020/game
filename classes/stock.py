import random

class Stock:
    def __init__(self, name, price, currency, base_min_mult, base_max_mult):
        self.name = name
        self.currency = currency
        self._price = price  # 내부 변수로 가격 저장
        self.base_min_mult = base_min_mult
        self.base_max_mult = base_max_mult
        self.selected = False
        
        # [추가] 가격 이력을 저장할 리스트
        # 가격 업데이트 시 여기에 값이 추가됩니다.
        self.price_history = [price] 
        # 최대 저장 개수 (예: 100개)
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
        
        # 현재 가격을 기준으로 변동폭 결정
        # min_mult와 max_mult 사이에서 랜덤 비율을 선택
        rand_mult = random.uniform(self.base_min_mult, self.base_max_mult)
        
        # 이전 가격의 +/- 10% 이내에서 변동을 추가
        base_change_percent = random.uniform(-0.1, 0.1) 
        
        # 변동폭 계산: (기본 변동 + 랜덤 영향)
        change_ratio = base_change_percent * rand_mult
        
        new_price = self._price * (1 + change_ratio)
        
        # 가격이 0 미만이 되는 것을 방지
        new_price = max(0.01, new_price) 
        
        # 현재 가격 (_price를 변경하는 부분)
        self._price = new_price 
        
        # [추가] 가격 이력 업데이트
        # 1. 새 가격을 리스트 끝에 추가
        self.price_history.append(self._price)
        
        # 2. 리스트 크기를 제한 (가장 오래된 데이터를 제거)
        if len(self.price_history) > self.max_history_length:
            self.price_history.pop(0)