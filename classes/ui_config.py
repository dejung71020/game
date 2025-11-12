# classes/ui_config.py
class UIConfig:
    FONT_PATH = "C:/Windows/Fonts/malgun.ttf"
    FONT_SIZE = 28
    FONT_SIZE_SMALL = 14
    FONT_SIZE_MEDIUM = 24
    FONT_SIZE_LARGE = 36
    BG_COLOR_BASE = (20, 20, 40)
    GRADIENT_STEP = 30
    # 새로운 색상 정의 추가 (모달/UI 배경용)
    COLOR_WHITE = (255, 255, 255)
    COLOR_BLACK = (0, 0, 0)
    COLOR_LIGHT_GREY = (200, 200, 200) # 모달 배경색
    COLOR_DARK_BLUE = (20, 20, 50)     # 모달 테두리 및 텍스트색
    
    COLORS = {
        "stock_normal": (80, 80, 80),
        "stock_hover": (100, 100, 100),
        "stock_selected": (0, 200, 0),
        "border_selected": (255, 255, 0),
        "text": (255, 255, 255),
        "profit": (0, 255, 0),
        "loss": (255, 0, 0),
        "button": (80, 80, 255),
        "button_hover": (120, 120, 255),
        "card_bg": (50, 50, 80),
        "coin_text": (255, 255, 0),
        "row_hover": (80,80,100),     # 마우스 오버 시 배경
        "row_selected": (100,100,150), # 클릭 시 선택 배경
        "disabled": (40, 40, 40), # 예시: 짙은 회색
        "text_disabled": (100, 100, 100),
        "store_text" : (128, 0, 128),
        "exchange_text" : (0, 100, 0),
    }

    POS = {
        "stock_list_x": 20,
        "stock_list_y": 70,
        "stock_width": 420,
        "stock_height": 30,
        "stock_gap": 35,
        "asset_x": 1030,
        "asset_y": 20,
        "owned_y_start": 550,
        "owned_y_gap": 70,
        "purchase_y": 100,
    }

    BUTTON_BORDER_RADIUS = 8
    BUTTON_BORDER_WIDTH = 2
    BUTTON_FONT_RATIO = 0.6
    COIN_ICON = "💰"
    