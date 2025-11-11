# classes/shop.py
from typing import List
from classes.storeitem import StoreItem # StoreItem 클래스를 임포트합니다.

class Shop:
    """
    StoreItem 목록을 관리하고 상점 로직을 처리하는 클래스입니다.
    """
    def __init__(self):
        # 상점에서 판매하는 모든 아이템 목록
        self.items: List[StoreItem] = []
        self._initialize_items()

    def _initialize_items(self):
        """요청하신 세 가지 아이템 목록을 초기화합니다."""
        
        # 1. 상승 확률 5% 증가 아이템
        self.items.append(StoreItem(
            name="성공 부스터",
            currency="코인",
            price=10.0,
            description="종목의 상승 확률을 영구적으로 5% 증가시킵니다. [EFFECT: up_prob_add: 0.05]",
            is_available=True,
            image_link="path/to/success_booster.png"
        ))

        # 2. max_gain_mult 2 증가 아이템
        self.items.append(StoreItem(
            name="초대박 기회",
            currency="금",
            price=5.0,
            description="종목당 최대 이득 배율을 2만큼 증가시킵니다. [EFFECT: max_gain_add: 2.0]",
            is_available=True,
            image_link="path/to/mega_gain.png"
        ))

        # 3. max_loss_mult 0.1 증가 아이템
        self.items.append(StoreItem(
            name="위험 감수 증폭",
            currency="원",
            price=100000.0,
            description="종목당 최대 손실 배율을 0.1만큼 증가시킵니다. [EFFECT: max_loss_add: 0.1]",
            is_available=True,
            image_link="path/to/risk_amplifier.png"
        ))

    def get_all_items(self) -> List[StoreItem]:
        """모든 아이템 목록을 반환합니다."""
        return self.items
        
    def get_available_items(self) -> List[StoreItem]:
        """현재 구매 가능한 아이템 목록을 반환합니다."""
        return [item for item in self.items if item.is_available]

    def get_item_by_name(self, name: str) -> StoreItem or None:
        """아이템 이름으로 아이템 객체를 찾습니다."""
        for item in self.items:
            if item.name == name:
                return item
        return None
        
    # def purchase_item(self, player, item_name):
    #     """
    #     아이템 구매 로직을 구현할 자리입니다.
    #     (예: 잔액 확인, 아이템 효과 적용, 인벤토리 추가 등)
    #     """
    #     pass