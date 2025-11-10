import pygame
import time
from classes.stock import Stock
from classes.player import Player
from classes.ui_config import UIConfig as UI

class Game:
    def __init__(self):
        pygame.init()
        self.screen_width, self.screen_height = 1280, 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("랜덤 코인 게임 v0.2.3 통합")
        self.clock = pygame.time.Clock()
        self.running = True

        # 플레이어
        self.player = Player()

        # 화폐 단위별 종목 20개 (min_mult, max_mult 반영)
        self.stocks_by_currency = {
            "원": [Stock(f"원코인{i+1}", 10, "원", base_min_mult=0.5, base_max_mult=2) for i in range(20)],
            "코인": [Stock(f"코인이{i+1}", 10000, "코인", base_min_mult=0.2, base_max_mult=5) for i in range(20)],
            "금": [Stock(f"금{i+1}", 10000000, "금", base_min_mult=0.05, base_max_mult=20) for i in range(20)],
            "스탁": [Stock(f"스탁{i+1}", 1000000000, "스탁", base_min_mult=0, base_max_mult=100) for i in range(20)]
        }

        # 기본 선택 화폐
        self.selected_currency = "원"
        self.stocks = self.stocks_by_currency[self.selected_currency]
        self.selected_stock = None

        # 화폐 단위 버튼
        self.currency_buttons = {
            "원": pygame.Rect(20, 20, 80, 30),
            "코인": pygame.Rect(110, 20, 80, 30),
            "금": pygame.Rect(200, 20, 80, 30),
            "스탁": pygame.Rect(290, 20, 80, 30),
        }

        # 종목 버튼 20개
        self.stock_buttons = [pygame.Rect(UI.POS["stock_list_x"],
                                          UI.POS["stock_list_y"] + i*UI.POS["stock_gap"],
                                          UI.POS["stock_width"],
                                          UI.POS["stock_height"]) for i in range(20)]

        self.scroll_index = 0
        self.visible_count = 10  # 한 화면에 보이는 버튼 개수
        self.scroll_dragging = False
        self.scroll_handle_rect = pygame.Rect(410, UI.POS["stock_list_y"], 10, 200)  # 초기 위치

        # 구매 버튼 및 수량
        self.purchase_qty = 1
        self.buttons = {
            "minus": pygame.Rect(450, UI.POS["purchase_y"], 30, UI.POS["stock_height"]),
            "plus": pygame.Rect(490, UI.POS["purchase_y"], 30, UI.POS["stock_height"]),
            "pct_10": pygame.Rect(530, UI.POS["purchase_y"], 50, UI.POS["stock_height"]),
            "pct_25": pygame.Rect(590, UI.POS["purchase_y"], 50, UI.POS["stock_height"]),
            "pct_50": pygame.Rect(650, UI.POS["purchase_y"], 50, UI.POS["stock_height"]),
            "pct_100": pygame.Rect(710, UI.POS["purchase_y"], 60, UI.POS["stock_height"]),
            "buy": pygame.Rect(780, UI.POS["purchase_y"], 80, UI.POS["stock_height"]),
        }

        # 가격 갱신
        self.last_update = time.time()

        # 폰트
        self.font_path = UI.FONT_PATH
        self.base_font_size = UI.FONT_SIZE
        self.font = pygame.font.Font(self.font_path, self.base_font_size)

    # ---------------- 이벤트 처리 ----------------
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 마우스 휠
                if event.button == 4:  # 휠 업
                    self.scroll_index = max(0, self.scroll_index - 1)
                elif event.button == 5:  # 휠 다운
                    self.scroll_index = min(len(self.stocks) - self.visible_count, self.scroll_index + 1)

                # 스크롤 핸들 클릭
                if self.scroll_handle_rect.collidepoint(event.pos):
                    self.scroll_dragging = True

                x, y = event.pos
                # 종목 선택
                for i, stock in enumerate(self.stocks[self.scroll_index:self.scroll_index+self.visible_count]):
                    rect = self.stock_buttons[i]
                    if rect.collidepoint(event.pos):
                        for s in self.stocks:
                            s.selected = False
                        stock.selected = True
                        self.selected_stock = stock

                # 구매 버튼 처리
                if self.selected_stock:
                    for key, rect in self.buttons.items():
                        if rect.collidepoint(event.pos):
                            self.handle_purchase_buttons(key)

            elif event.type == pygame.MOUSEBUTTONUP:
                self.scroll_dragging = False

            elif event.type == pygame.MOUSEMOTION and self.scroll_dragging:
                # 스크롤 핸들 드래그
                mouse_y = event.pos[1]
                scroll_area_y = UI.POS["stock_list_y"]
                scroll_area_height = self.visible_count * UI.POS["stock_gap"]
                handle_height = self.scroll_handle_rect.height
                mouse_y = max(scroll_area_y, min(mouse_y, scroll_area_y + scroll_area_height - handle_height))
                self.scroll_handle_rect.y = mouse_y

                # scroll_index 계산
                ratio = (mouse_y - scroll_area_y) / (scroll_area_height - handle_height)
                self.scroll_index = int(ratio * (len(self.stocks) - self.visible_count))



    # ---------------- 구매 버튼 처리 ----------------
    def handle_purchase_buttons(self, key):
        if not self.selected_stock:
            return

        currency = self.selected_stock.currency
        available_cash = self.player.cash[currency]
        max_qty = int(available_cash / self.selected_stock.price)

        if key == "minus":
            if self.purchase_qty > 1:
                self.purchase_qty -= 1
        elif key == "plus":
            if self.purchase_qty < max_qty:
                self.purchase_qty += 1
        elif key == "pct_10":
            self.purchase_qty = max(1, int(max_qty * 0.1))
        elif key == "pct_25":
            self.purchase_qty = max(1, int(max_qty * 0.25))
        elif key == "pct_50":
            self.purchase_qty = max(1, int(max_qty * 0.5))
        elif key == "pct_100":
            self.purchase_qty = max(1, max_qty)
        elif key == "buy":
            if max_qty >= self.purchase_qty:
                success = self.player.invest(self.selected_stock, self.purchase_qty)
                if not success:
                    print(f"{currency} 잔액 부족!")
            else:
                print(f"{currency} 잔액 부족!")


    # ---------------- 가격 업데이트 ----------------
    def update_game(self):
        current_time = time.time()
        if current_time - self.last_update >= 10:
            for stock_list in self.stocks_by_currency.values():
                for stock in stock_list:
                    stock.update_price()
            self.last_update = current_time

    # ---------------- UI 그리기 ----------------
    def get_auto_font(self, rect, ratio=UI.BUTTON_FONT_RATIO):
        font_size = int(rect.height * ratio)
        return pygame.font.Font(self.font_path, font_size)
    
    def draw_ui(self):
        # ---------------- 배경 그라데이션 ----------------
        for i in range(self.screen_height):
            val = UI.BG_COLOR_BASE[0] + i // UI.GRADIENT_STEP
            pygame.draw.line(self.screen, (val, val, val+20), (0,i), (self.screen_width,i))

        # ---------------- 화폐 단위 버튼 ----------------
        for cur, rect in self.currency_buttons.items():
            mouse_pos = pygame.mouse.get_pos()
            color = UI.COLORS["button_hover"] if cur == self.selected_currency else UI.COLORS["button"]
            pygame.draw.rect(self.screen, color, rect, border_radius=UI.BUTTON_BORDER_RADIUS)
            font = self.get_auto_font(rect)
            text = font.render(cur, True, UI.COLORS["text"])
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)

        # ---------------- 좌측 종목 리스트 버튼 ----------------
        for i, stock in enumerate(self.stocks[self.scroll_index:self.scroll_index+self.visible_count]):
            rect = self.stock_buttons[i]
            color = UI.COLORS["stock_selected"] if stock.selected else UI.COLORS["stock_normal"]
            pygame.draw.rect(self.screen, color, rect, border_radius=UI.BUTTON_BORDER_RADIUS)
            font = self.get_auto_font(rect)
            text = font.render(f"{stock.name}: {stock.price}", True, UI.COLORS["text"])
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)

        # ---------------- 스크롤 바 ----------------
        scroll_x = UI.POS["stock_list_x"] + UI.POS["stock_width"] + 5
        scroll_y = UI.POS["stock_list_y"]
        scroll_height = self.visible_count * UI.POS["stock_gap"]
        scroll_rect = pygame.Rect(scroll_x, scroll_y, 10, scroll_height)
        pygame.draw.rect(self.screen, (100,100,100), scroll_rect, border_radius=5)
        pygame.draw.rect(self.screen, (180,180,180), self.scroll_handle_rect, border_radius=5)

        # ---------------- 상단 보유 자산 (오른쪽 정렬 + 테두리) ----------------
        margin = 20
        total_assets = self.player.total_assets()  # 현금 + 모든 종목 현재가치 합산
        total_str = f"총 보유자산: {total_assets:.2f}"

        font_size = self.base_font_size
        font = pygame.font.Font(self.font_path, font_size)
        text_width, text_height = font.size(total_str)
        while text_width > self.screen_width - margin*2 and font_size > 10:
            font_size -= 1
            font = pygame.font.Font(self.font_path, font_size)
            text_width, text_height = font.size(total_str)

        x_pos = self.screen_width - text_width - margin
        y_pos = UI.POS["asset_y"] + 30
        self.screen.blit(font.render(total_str, True, UI.COLORS["coin_text"]), (x_pos, y_pos))
        pygame.draw.rect(self.screen, UI.COLORS["border_selected"],
                        (x_pos-5, y_pos-2, text_width+10, text_height+4), 2)

        # ---------------- 화폐별 보유 현금 ----------------
        assets = self.player.assets_by_currency()
        currency_str = f"현금: {assets['원']:.2f} | 코인: {assets['코인']:.2f} | 금: {assets['금']:.2f} | 스탁: {assets['스탁']:.2f}"
        text_width, text_height = font.size(currency_str)
        while text_width > self.screen_width - margin*2 and font_size > 10:
            font_size -= 1
            font = pygame.font.Font(self.font_path, font_size)
            text_width, text_height = font.size(currency_str)

        y_pos_currency = y_pos + text_height + 10
        self.screen.blit(font.render(currency_str, True, UI.COLORS["coin_text"]),
                        (self.screen_width - text_width - margin, y_pos_currency))
        pygame.draw.rect(self.screen, UI.COLORS["border_selected"],
                        (self.screen_width - text_width - margin-5, y_pos_currency-2,
                        text_width+10, text_height+4), 2)

        # ---------------- 구매 UI 패널 ----------------
        if self.selected_stock:
            # ---------------- 좌측 종목 리스트 바로 아래에 구매 UI 배치 ----------------
            panel_x = UI.POS["stock_list_x"]
            panel_y = UI.POS["stock_list_y"] + len(self.stocks)*UI.POS["stock_gap"] + 10
            panel_width = 380  # 종목 버튼과 같은 폭
            panel_height = 70
            panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)

            # 패널 배경 & 테두리
            pygame.draw.rect(self.screen, (50,50,70), panel_rect, border_radius=UI.BUTTON_BORDER_RADIUS)
            pygame.draw.rect(self.screen, UI.COLORS["border_selected"], panel_rect, 2, border_radius=UI.BUTTON_BORDER_RADIUS)

            # ---------------- 선택 종목 + 구매 수량 ----------------
            display_str = f"{self.selected_stock.name}: {self.purchase_qty}개 구매 예정"
            font = pygame.font.Font(self.font_path, 20)
            text = font.render(display_str, True, UI.COLORS["text"])
            self.screen.blit(text, (panel_x + 10, panel_y + 5))

            # ---------------- 구매 버튼 ----------------
            btn_gap = 5
            btn_x_start = panel_x + 10
            btn_y = panel_y + 35  # 텍스트 아래
            for idx, key in enumerate(["minus","plus","pct_10","pct_25","pct_50","pct_100","buy"]):
                rect = self.buttons[key]
                rect.x = btn_x_start + idx*(rect.width + btn_gap)
                rect.y = btn_y
                mouse_pos = pygame.mouse.get_pos()
                color = UI.COLORS["button_hover"] if rect.collidepoint(mouse_pos) else UI.COLORS["button"]
                pygame.draw.rect(self.screen, color, rect, border_radius=UI.BUTTON_BORDER_RADIUS)
                pygame.draw.rect(self.screen, UI.COLORS["border_selected"], rect, 2, border_radius=UI.BUTTON_BORDER_RADIUS)
                label = {
                    "minus":"-","plus":"+","buy":"구매",
                    "pct_10":"10%","pct_25":"25%","pct_50":"50%","pct_100":"100%"
                }[key]
                text = font.render(label, True, UI.COLORS["text"])
                text_rect = text.get_rect(center=rect.center)
                self.screen.blit(text, text_rect)

        # ---------------- 보유 코인 카드 ----------------
        owned_x_start = UI.POS["asset_x"]
        y = UI.POS["owned_y_start"]
        card_width = self.screen_width - owned_x_start - 20
        max_height = self.screen_height - y - 20
        owned_count = len(self.player.owned_stocks)
        gap = min(UI.POS["owned_y_gap"], max_height//max(owned_count,1))

        for stock, info in self.player.owned_stocks.items():
            qty = info["quantity"]
            current_value = stock.price * qty
            one_price = stock.price
            profit_ratio = ((current_value - info["buy_price"]*qty)/(info["buy_price"]*qty)*100) if info["buy_price"]*qty>0 else 0
            color = UI.COLORS["profit"] if profit_ratio>=0 else UI.COLORS["loss"]
            text_str = f"{stock.name} | 1개 가격: {one_price} | 보유: {qty} | 총액: {current_value:.2f} | 변동: {profit_ratio:+.2f}%"
            font_size = self.base_font_size
            font = pygame.font.Font(self.font_path, font_size)
            text_width,_ = font.size(text_str)
            while text_width > card_width and font_size>10:
                font_size -=1
                font = pygame.font.Font(self.font_path, font_size)
                text_width,_ = font.size(text_str)
            text = font.render(text_str, True, color)
            self.screen.blit(text,(owned_x_start, y))
            y += gap






    # ---------------- 실행 ----------------
    def run(self):
        while self.running:
            self.handle_events()
            self.update_game()
            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()
