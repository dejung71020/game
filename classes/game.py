import pygame
import time
from classes.stock import Stock
from classes.player import Player
from classes.ui_config import UIConfig as UI
from classes.data_manager import DataManager

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

        # 종목 데이터 관리
        self.data_manager = DataManager()
        
        # 화폐 단위별 종목 20개
        self.stocks_by_currency = {
            "원": [],
            "코인": [],
            "금": [],
            "스탁": []
        }
        for cur in self.stocks_by_currency.keys():
            data_list = self.data_manager.get_category_data(cur)
            stocks = []
            for item in data_list[:20]:
                if cur == "원":
                    stocks.append(Stock(item["name"], item["price"], cur, base_min_mult=0.5, base_max_mult=2))
                elif cur == "코인":
                    stocks.append(Stock(item["name"], item["price"], cur, base_min_mult=0.2, base_max_mult=5))
                elif cur == "금":
                    stocks.append(Stock(item["name"], item["price"], cur, base_min_mult=0.05, base_max_mult=20))
                elif cur == "스탁":
                    stocks.append(Stock(item["name"], item["price"], cur, base_min_mult=0, base_max_mult=100))
            self.stocks_by_currency[cur] = stocks

        # 기본 선택 화폐
        self.selected_currency = "원"
        self.stocks = self.stocks_by_currency[self.selected_currency]
        self.selected_stock = None
        self.selected_owned_currency = "원"  # 보유종목 필터 초기값
        
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

        # 스크롤 관련
        self.scroll_index = 0
        self.visible_count = 10
        self.scroll_dragging = False
        self.scroll_handle_rect = pygame.Rect(410, UI.POS["stock_list_y"], 10, 200)

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

        self.insufficient_funds_msg = None  # 부족 금액 메시지
        self.msg_timer = 0  # 메시지 표시 시간

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
                x, y = event.pos

                # 화폐 단위 버튼 클릭
                for cur, rect in self.currency_buttons.items():
                    if rect.collidepoint(event.pos):
                        if self.selected_currency != cur:
                            self.selected_currency = cur
                            self.scroll_index = 0
                            self.selected_stock = None
                            self.stocks = self.stocks_by_currency[cur]

                # 마우스 휠
                if event.button == 4:
                    self.scroll_index = max(0, self.scroll_index - 1)
                elif event.button == 5:
                    self.scroll_index = min(len(self.stocks) - self.visible_count, self.scroll_index + 1)

                # 스크롤 핸들 클릭
                if self.scroll_handle_rect.collidepoint(event.pos):
                    self.scroll_dragging = True

                # 종목 선택
                for i, stock in enumerate(self.stocks[self.scroll_index:self.scroll_index+self.visible_count]):
                    rect = self.stock_buttons[i]
                    if rect.collidepoint(event.pos):
                        for s in self.stocks:
                            s.selected = False
                        stock.selected = True
                        self.selected_stock = stock

                # 구매 버튼
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
            total_cost = self.selected_stock.price * self.purchase_qty
            if available_cash >= total_cost:
                success = self.player.invest(self.selected_stock, self.purchase_qty)
                if not success:
                    self.show_insufficient_funds(currency, total_cost, available_cash)
            else:
                self.show_insufficient_funds(currency, total_cost, available_cash)

    # ---------------- 부족 금액 알림 ----------------
    def show_insufficient_funds(self, currency, required, available):
        missing = required - available
        self.insufficient_funds_msg = f"{currency} 잔액 부족! {missing:.2f} 필요"
        self.msg_timer = pygame.time.get_ticks()  # 메시지 시작 시간

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
        # 배경 그라데이션
        for i in range(self.screen_height):
            val = UI.BG_COLOR_BASE[0] + i // UI.GRADIENT_STEP
            pygame.draw.line(self.screen, (val, val, val+20), (0,i), (self.screen_width,i))

        # 화폐 단위 버튼
        for cur, rect in self.currency_buttons.items():
            mouse_pos = pygame.mouse.get_pos()

            # hover 효과
            if rect.collidepoint(mouse_pos):
                color = UI.COLORS["button_hover"]
                font_size = int(rect.height * UI.BUTTON_FONT_RATIO * 1.2)  # 20% 커짐
                font = pygame.font.Font(self.font_path, font_size)
                font.set_bold(True)
            else:
                color = UI.COLORS["button"]
                font_size = int(rect.height * UI.BUTTON_FONT_RATIO)
                font = pygame.font.Font(self.font_path, font_size)

            pygame.draw.rect(self.screen, color, rect, border_radius=UI.BUTTON_BORDER_RADIUS)
            pygame.draw.rect(self.screen, UI.COLORS["border_selected"], rect, 2, border_radius=UI.BUTTON_BORDER_RADIUS)

            text = font.render(cur, True, UI.COLORS["text"])
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)


        # 종목 리스트 (스크롤 적용)
        for i, stock in enumerate(self.stocks[self.scroll_index:self.scroll_index+self.visible_count]):
            rect = self.stock_buttons[i]
            mouse_pos = pygame.mouse.get_pos()

            # hover 색상 + 선택 색상
            if rect.collidepoint(mouse_pos):
                color = UI.COLORS["button_hover"]
                font_size = int(rect.height * UI.BUTTON_FONT_RATIO * 1.2)
                font = pygame.font.Font(self.font_path, font_size)
                font.set_bold(True)
            else:
                color = UI.COLORS["stock_selected"] if stock.selected else UI.COLORS["stock_normal"]
                font_size = int(rect.height * UI.BUTTON_FONT_RATIO)
                font = pygame.font.Font(self.font_path, font_size)

            pygame.draw.rect(self.screen, color, rect, border_radius=UI.BUTTON_BORDER_RADIUS)
            pygame.draw.rect(self.screen, UI.COLORS["border_selected"], rect, 2, border_radius=UI.BUTTON_BORDER_RADIUS)

            text = font.render(f"{stock.name}: {stock.price}", True, UI.COLORS["text"])
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)

        # 스크롤 바
        scroll_x = UI.POS["stock_list_x"] + UI.POS["stock_width"] + 5
        scroll_y = UI.POS["stock_list_y"]
        scroll_height = self.visible_count * UI.POS["stock_gap"]
        scroll_rect = pygame.Rect(scroll_x, scroll_y, 10, scroll_height)
        pygame.draw.rect(self.screen, (100,100,100), scroll_rect, border_radius=5)
        pygame.draw.rect(self.screen, (180,180,180), self.scroll_handle_rect, border_radius=5)

        # ---------------- 총보유자산 + 화폐별 현금 패널 ----------------
        panel_padding = 10  # 패널 안쪽 여백
        margin_right = 20   # 화면 오른쪽 마진

        # 총 보유자산
        total_assets = self.player.total_assets()
        total_str = f"총 보유자산: {total_assets:.2f}"

        # 화폐별 현금
        assets = self.player.assets_by_currency()
        currency_str = f"현금: {assets['원']:.2f} | 코인: {assets['코인']:.2f} | 금: {assets['금']:.2f} | 스탁: {assets['스탁']:.2f}"

        # 폰트
        font_size = self.base_font_size
        font = pygame.font.Font(self.font_path, font_size)
        
        # 텍스트 너비 계산 (패널 width 결정용)
        total_width = font.size(total_str)[0]
        currency_width = font.size(currency_str)[0]
        text_width = max(total_width, currency_width)
        
        # 패널 width 조정 (최소 300, 필요시 텍스트 길이에 맞춰 늘어남)
        panel_width = max(text_width + panel_padding*2, 300)
        panel_height = font_size*2 + panel_padding*3  # 두 줄 텍스트 + padding
        panel_x = self.screen_width - panel_width - margin_right
        panel_y = 20  # 화면 상단에서 거리 조정 가능

        # 패널 그리기
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, (50,50,70), panel_rect, border_radius=UI.BUTTON_BORDER_RADIUS)
        pygame.draw.rect(self.screen, UI.COLORS["border_selected"], panel_rect, 2, border_radius=UI.BUTTON_BORDER_RADIUS)

        # 텍스트 그리기
        self.screen.blit(font.render(total_str, True, UI.COLORS["coin_text"]),
                        (panel_x + panel_padding, panel_y + panel_padding))
        self.screen.blit(font.render(currency_str, True, UI.COLORS["coin_text"]),
                        (panel_x + panel_padding, panel_y + panel_padding + font_size + 5))

        # 구매 UI
        if self.selected_stock:
            panel_x = UI.POS["stock_list_x"]
            panel_y = UI.POS["stock_list_y"] + self.visible_count * UI.POS["stock_gap"] + 10
            panel_width = 380
            panel_height = 70
            panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
            pygame.draw.rect(self.screen, (50,50,70), panel_rect, border_radius=UI.BUTTON_BORDER_RADIUS)
            pygame.draw.rect(self.screen, UI.COLORS["border_selected"], panel_rect, 2, border_radius=UI.BUTTON_BORDER_RADIUS)

            # 선택 종목 + 구매 수량
            display_str = f"{self.selected_stock.name}: {self.purchase_qty}개 구매 예정"
            font = pygame.font.Font(self.font_path, 20)
            text = font.render(display_str, True, UI.COLORS["text"])
            self.screen.blit(text, (panel_x + 10, panel_y + 5))

            # ---------------- 구매 UI ----------------
        if self.selected_stock:
            panel_x = UI.POS["stock_list_x"]
            panel_y = UI.POS["stock_list_y"] + self.visible_count * UI.POS["stock_gap"] + 10
            panel_width = 395
            panel_height = 70
            panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
            pygame.draw.rect(self.screen, (50,50,70), panel_rect, border_radius=UI.BUTTON_BORDER_RADIUS)
            pygame.draw.rect(self.screen, UI.COLORS["border_selected"], panel_rect, 2, border_radius=UI.BUTTON_BORDER_RADIUS)

            # 선택 종목 + 구매 수량
            display_str = f"{self.selected_stock.name}: {self.purchase_qty}개 구매 예정"
            font = pygame.font.Font(self.font_path, 20)
            text = font.render(display_str, True, UI.COLORS["text"])
            self.screen.blit(text, (panel_x + 10, panel_y + 5))

            # 구매 버튼
            btn_gap = 5
            btn_x = panel_x + 10  # 시작 X 좌표
            btn_y = panel_y + 35  # Y 좌표

            for key in ["minus","plus","pct_10","pct_25","pct_50","pct_100","buy"]:
                rect = self.buttons[key]
                rect.x = btn_x
                rect.y = btn_y

                mouse_pos = pygame.mouse.get_pos()

                # 버튼 색상 설정
                if key == "buy":
                    base_color = (200,0,0)
                    hover_color = (255,50,50)
                else:
                    base_color = UI.COLORS["button"]
                    hover_color = UI.COLORS["button_hover"]

                color = hover_color if rect.collidepoint(mouse_pos) else base_color
                pygame.draw.rect(self.screen, color, rect, border_radius=UI.BUTTON_BORDER_RADIUS)
                pygame.draw.rect(self.screen, UI.COLORS["border_selected"], rect, 2, border_radius=UI.BUTTON_BORDER_RADIUS)

                # 라벨
                label = {
                    "minus":"-","plus":"+","buy":"구매",
                    "pct_10":"10%","pct_25":"25%","pct_50":"50%","pct_100":"100%"
                }[key]

                # ---------------- 폰트 처리 (hover시 커지고 진하게)
                if rect.collidepoint(mouse_pos):
                    font_size = int(rect.height * UI.BUTTON_FONT_RATIO * 1.2)  # 20% 커짐
                    font = pygame.font.Font(self.font_path, font_size)
                    bold = True
                    font.set_bold(bold)
                else:
                    font_size = int(rect.height * UI.BUTTON_FONT_RATIO)
                    font = pygame.font.Font(self.font_path, font_size)

                text = font.render(label, True, UI.COLORS["text"])
                text_rect = text.get_rect(center=rect.center)
                self.screen.blit(text, text_rect)

                # 다음 버튼 X 좌표 누적
                btn_x += rect.width + btn_gap

        # ---------------- 보유 종목 카드 (표 형태) ----------------
        y_start = UI.POS["owned_y_start"]
        columns = ["종목명", "수", "총액", "변동폭", "구매가", "현재가"]
        base_col_widths = [120, 70, 100, 80, 100, 100]  # 기본 컬럼 너비

        row_height = 30
        mouse_pos = pygame.mouse.get_pos()

        # 모든 row 데이터 준비
        row_texts = []
        row_rects = []
        for stock, info in self.player.owned_stocks.items():
            qty = info["quantity"]
            current_value = stock.price * qty
            buy_total = info["buy_price"] * qty
            profit_ratio = ((current_value - buy_total)/buy_total*100) if buy_total>0 else 0
            row_texts.append([
                stock.name,
                str(qty),
                f"{current_value:.2f}",
                f"{profit_ratio:+.2f}%",
                f"{info['buy_price']:.2f}",
                f"{stock.price:.2f}"
            ])

        # 각 컬럼 최대 width 계산
        font_size = 18
        font = pygame.font.Font(self.font_path, font_size)
        col_widths = base_col_widths.copy()
        for i, col in enumerate(columns):
            text_width, _ = font.size(col)
            col_widths[i] = max(col_widths[i], text_width + 10)
            for row in row_texts:
                w, _ = font.size(row[i])
                if w + 10 > col_widths[i]:
                    col_widths[i] = w + 10

        # 패널 width/height 계산
        panel_width = sum(col_widths)
        panel_max_width = self.screen_width // 2
        needs_h_scroll = False
        if panel_width > panel_max_width:
            needs_h_scroll = True
            visible_width = panel_max_width
        else:
            visible_width = panel_width

        panel_height = row_height * (len(row_texts) + 1)
        panel_max_height = self.screen_height - y_start - 20
        needs_v_scroll = False
        if panel_height > panel_max_height:
            needs_v_scroll = True
            visible_height = panel_max_height
        else:
            visible_height = panel_height

        # 스크롤 초기화
        if not hasattr(self, "owned_scroll_x"):
            self.owned_scroll_x = 0
        if not hasattr(self, "owned_scroll_y"):
            self.owned_scroll_y = 0

        # 패널 그리기
        panel_x = self.screen_width - visible_width - 20
        panel_rect = pygame.Rect(panel_x, y_start, visible_width, visible_height)
        pygame.draw.rect(self.screen, (50,50,70), panel_rect, border_radius=UI.BUTTON_BORDER_RADIUS)
        pygame.draw.rect(self.screen, UI.COLORS["border_selected"], panel_rect, 2, border_radius=UI.BUTTON_BORDER_RADIUS)

        # 클리핑
        clip_rect = self.screen.get_clip()
        self.screen.set_clip(panel_rect)

        # 헤더
        x = panel_x - self.owned_scroll_x
        y = y_start - self.owned_scroll_y
        for i, col in enumerate(columns):
            text = font.render(col, True, UI.COLORS["text"])
            self.screen.blit(text, (x + 5, y + 5))
            x += col_widths[i]

        # 세로 구분선
        x = panel_x - self.owned_scroll_x
        for w in col_widths:
            x += w
            pygame.draw.line(self.screen, UI.COLORS["border_selected"], (x, y_start), (x, y_start + panel_height))

        # 행 그리기 + hover & 선택 효과
        y = y_start + row_height - self.owned_scroll_y
        for idx, row in enumerate(row_texts):
            x = panel_x - self.owned_scroll_x
            row_rect = pygame.Rect(panel_x, y, panel_width, row_height)
            row_rects.append(row_rect)

            # 배경색: hover / 선택 / 기본
            if hasattr(self, "selected_owned_row") and self.selected_owned_row == idx:
                bg_color = UI.COLORS["row_selected"]
            elif row_rect.collidepoint(mouse_pos):
                bg_color = UI.COLORS["row_hover"]
            else:
                bg_color = (50,50,70)

            pygame.draw.rect(self.screen, bg_color, row_rect)

            # 텍스트
            for i, text_str in enumerate(row):
                color = UI.COLORS["profit"] if (i == 3 and float(row[3].replace("%",""))>=0) else (UI.COLORS["loss"] if i == 3 else UI.COLORS["text"])
                text = font.render(text_str, True, color)
                self.screen.blit(text, (x + 5, y))
                x += col_widths[i]

            # 가로 구분선
            pygame.draw.line(self.screen, UI.COLORS["border_selected"], (panel_x, y + row_height - 1), (panel_x + panel_width, y + row_height - 1))
            y += row_height

        # 클리핑 해제
        self.screen.set_clip(clip_rect)

        # 스크롤바
        if needs_v_scroll:
            v_scroll_rect = pygame.Rect(panel_x + visible_width - 10, y_start, 10, visible_height)
            pygame.draw.rect(self.screen, (100,100,100), v_scroll_rect)
        if needs_h_scroll:
            h_scroll_rect = pygame.Rect(panel_x, y_start + visible_height - 10, visible_width, 10)
            pygame.draw.rect(self.screen, (100,100,100), h_scroll_rect)


                # 부족 금액 메시지 표시 (1.5초 유지)
        if self.insufficient_funds_msg:
            current_time = pygame.time.get_ticks()
            if current_time - self.msg_timer <= 1500:
                # 구매 UI 패널 위치 기준으로 바로 아래
                panel_x = UI.POS["stock_list_x"]
                panel_y = UI.POS["stock_list_y"] + self.visible_count*UI.POS["stock_gap"] + 10 + 70 + 5  # 구매UI 패널 높이 70 + 간격 5
                panel_width = 395
                panel_height = 40
                msg_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
                pygame.draw.rect(self.screen, (80,0,0), msg_rect, border_radius=UI.BUTTON_BORDER_RADIUS)
                pygame.draw.rect(self.screen, (255,0,0), msg_rect, 2, border_radius=UI.BUTTON_BORDER_RADIUS)
                font = pygame.font.Font(UI.FONT_PATH, 20)
                text = font.render(self.insufficient_funds_msg, True, (255,200,200))
                text_rect = text.get_rect(center=msg_rect.center)
                self.screen.blit(text, text_rect)
            else:
                self.insufficient_funds_msg = None  # 메시지 사라짐사라짐
    # ---------------- 실행 ----------------
    def run(self):
        while self.running:
            self.handle_events()
            self.update_game()
            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()
