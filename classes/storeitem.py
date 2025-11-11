# classes/storeitem.py

class StoreItem:
    """
    상점에서 판매될 개별 아이템의 정보를 담는 클래스입니다.
    """
    
    def __init__(self, name: str, currency: str, price: float, description: str, 
                 is_available: bool = True, image_link: str = None):
        """
        StoreItem 객체를 초기화합니다.
        
        :param name: 아이템명 (예: '성공 부스터')
        :param currency: 화폐 단위 (예: '원', '코인', '금', '스탁')
        :param price: 단위에 따른 가격 (화폐 단위에 맞는 실제 가격)
        :param description: 아이템 설명 (효과 태그 포함 권장)
        :param is_available: 판매 여부 (True: 재고 있음, False: 재고 없음)
        :param image_link: 아이템 이미지 링크 (Pygame 이미지 로드에 사용될 경로)
        """
        self.name = name
        self.currency = currency
        self.price = price
        self.description = description
        self.is_available = is_available
        self.image_link = image_link

    def __str__(self):
        """아이템 정보를 문자열로 반환합니다."""
        status = "재고 있음" if self.is_available else "품절"
        return (f"[{self.name}] 가격: {self.price} {self.currency} / 재고: {status}\n"
                f"   설명: {self.description}")