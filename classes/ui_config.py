class UIConfig:
    FONT_PATH = "C:/Windows/Fonts/malgun.ttf"
    FONT_SIZE = 28

    BG_COLOR_BASE = (20, 20, 40)
    GRADIENT_STEP = 30

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
        "row_selected": (100,100,150) # 클릭 시 선택 배경
    }

    POS = {
        "stock_list_x": 20,
        "stock_list_y": 60,
        "stock_width": 380,
        "stock_height": 28,
        "stock_gap": 30,
        "asset_x": 1030,
        "asset_y": 20,
        "owned_y_start": 300,
        "owned_y_gap": 35,
        "purchase_y": 100,
    }

    BUTTON_BORDER_RADIUS = 8
    BUTTON_BORDER_WIDTH = 2
    BUTTON_FONT_RATIO = 0.6
    COIN_ICON = "💰"
