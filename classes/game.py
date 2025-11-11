import pygame
import time
import random
from classes.stock import Stock
from classes.player import Player
from classes.ui_config import UIConfig as UI
from classes.data_manager import DataManager

class Game:
    def __init__(self):
        pygame.init()
        self.screen_width, self.screen_height = 1280, 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("랜덤 코인 게임 v0.3.4 통합 (차트 시각화 추가)")
        self.clock = pygame.time.Clock()
        self.running = True

        # 플레이어
        self.player = Player()

        # 종목 데이터 관리
        self.data_manager = DataManager()
        
        # 화폐 단위별 종목 20개 초기화
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
                    stocks.append(Stock(item["name"], item["price"], cur, base_min_mult=0.01, base_max_mult=2000, bias=0.51))
                elif cur == "코인":
                    stocks.append(Stock(item["name"], item["price"], cur, base_min_mult=0.03, base_max_mult=7000, bias=0.58))
                elif cur == "금":
                    stocks.append(Stock(item["name"], item["price"], cur, base_min_mult=0.05, base_max_mult=12000, bias=0.64))
                elif cur == "스탁":
                    stocks.append(Stock(item["name"], item["price"], cur, base_min_mult=0.07, base_max_mult=100000, bias=0.71))
            self.stocks_by_currency[cur] = stocks

        # 초기 차트 데이터 생성을 위해 몇 번 업데이트 실행 (선택 사항)
        for _ in range(30):
            for stock_list in self.stocks_by_currency.values():
                for stock in stock_list:
                    stock.update_price()
                    
        # 기본 선택 화폐
        self.selected_currency = "원"
        self.stocks = self.stocks_by_currency[self.selected_currency]
        self.selected_stock = None
        self.selected_owned_currency = "원" 

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
        self.scroll_handle_rect = pygame.Rect(UI.POS["stock_list_x"] + UI.POS["stock_width"] + 5, 
                                              UI.POS["stock_list_y"], 
                                              10, 
                                              200)

        # ------------------- 거래 관련 상태 변수 -------------------
        self.purchase_qty = 1
        self.sell_qty = 0
        self.selected_owned_row = -1
        self.selected_owned_stock_info = None
        
        # [추가] 보유 종목 스크롤 관련 변수
        self.owned_scroll_x = 0
        self.owned_scroll_y = 0
        self.owned_scroll_dragging = False
        self.owned_v_scroll_handle_rect = None


        # 버튼의 기본 Rect (위치는 0,0)
        self.buttons = {
            "minus": pygame.Rect(0, 0, 30, UI.POS["stock_height"]),
            "plus": pygame.Rect(0, 0, 30, UI.POS["stock_height"]),
            "pct_10": pygame.Rect(0, 0, 50, UI.POS["stock_height"]),
            "pct_25": pygame.Rect(0, 0, 50, UI.POS["stock_height"]),
            "pct_50": pygame.Rect(0, 0, 50, UI.POS["stock_height"]),
            "pct_100": pygame.Rect(0, 0, 60, UI.POS["stock_height"]),
            "buy_exec": pygame.Rect(0, 0, 80, UI.POS["stock_height"]),
            "sell_exec": pygame.Rect(0, 0, 80, UI.POS["stock_height"]),
        }
        
        self.buy_buttons = {}
        self.sell_buttons = {}

        self.insufficient_funds_msg = None
        self.msg_timer = 0

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
                # 화폐 단위 버튼 클릭
                for cur, rect in self.currency_buttons.items():
                    if rect.collidepoint(event.pos):
                        if self.selected_currency != cur:
                            self.selected_currency = cur
                            self.scroll_index = 0
                            self.selected_stock = None
                            self.selected_owned_stock_info = None
                            self.stocks = self.stocks_by_currency[cur]

                # 마우스 휠 (일반 종목 리스트)
                if event.button == 4:
                    self.scroll_index = max(0, self.scroll_index - 1)
                elif event.button == 5:
                    max_scroll = max(0, len(self.stocks) - self.visible_count)
                    self.scroll_index = min(max_scroll, self.scroll_index + 1)
                    
                # 보유 종목 스크롤 핸들 클릭
                if hasattr(self, "owned_v_scroll_handle_rect") and self.owned_v_scroll_handle_rect:
                    if self.owned_v_scroll_handle_rect.collidepoint(event.pos):
                         self.owned_scroll_dragging = True


                # 스크롤 핸들 클릭 (일반 종목 리스트)
                if self.scroll_handle_rect.collidepoint(event.pos):
                    self.scroll_dragging = True

                # 종목 선택 (매수 대상)
                for i, stock in enumerate(self.stocks[self.scroll_index:self.scroll_index+self.visible_count]):
                    rect = self.stock_buttons[i]
                    if rect.collidepoint(event.pos):
                        for s in self.stocks:
                            s.selected = False
                        stock.selected = True
                        self.selected_stock = stock
                        self.purchase_qty = 1
                        self.sell_qty = 0
                        self.selected_owned_stock_info = None
                        self.selected_owned_row = -1

                # 보유 종목 카드 클릭 (매도 대상)
                if hasattr(self, "owned_row_rects"):
                    for idx, row_rect in enumerate(self.owned_row_rects):
                        if row_rect.collidepoint(event.pos):
                            owned_stocks_list = list(self.player.owned_stocks.keys())
                            
                            if idx < len(owned_stocks_list):
                                stock_to_sell = owned_stocks_list[idx]
                                
                                self.selected_owned_row = idx
                                self.selected_owned_stock_info = (stock_to_sell, self.player.owned_stocks[stock_to_sell])
                                
                                if self.selected_stock:
                                    self.selected_stock.selected = False
                                stock_to_sell.selected = True
                                self.selected_stock = stock_to_sell 
                                
                                max_sell_qty = self.player.owned_stocks[stock_to_sell]['quantity']
                                self.sell_qty = max(1, max_sell_qty)
                                self.purchase_qty = 0
                                break

                # 구매/판매 버튼 처리 - 위치 기반 분리
                if self.selected_stock:
                    pos = event.pos
                    
                    # 1. 구매 UI 버튼 클릭 확인 (is_selling=False)
                    for key, rect in self.buy_buttons.items():
                        if rect.collidepoint(pos):
                            self.handle_purchase_buttons(key, is_selling=False) 
                            return 

                    # 2. 판매 UI 버튼 클릭 확인 (is_selling=True)
                    for key, rect in self.sell_buttons.items():
                        if rect.collidepoint(pos):
                            self.handle_purchase_buttons(key, is_selling=True) 
                            return 

            elif event.type == pygame.MOUSEBUTTONUP:
                self.scroll_dragging = False
                self.owned_scroll_dragging = False #보유 종목 드래그 상태 해제

            elif event.type == pygame.MOUSEMOTION:
                # 일반 종목 리스트 스크롤 드래그
                if self.scroll_dragging:
                    # 스크롤 핸들 드래그
                    scroll_area_y = UI.POS["stock_list_y"]
                    scroll_area_height = self.visible_count * UI.POS["stock_gap"]
                    handle_height = self.scroll_handle_rect.height
                    
                    mouse_y = event.pos[1]
                    mouse_y = max(scroll_area_y, min(mouse_y, scroll_area_y + scroll_area_height - handle_height))
                    self.scroll_handle_rect.y = mouse_y

                    # scroll_index 계산
                    ratio = (mouse_y - scroll_area_y) / (scroll_area_height - handle_height)
                    max_scroll = len(self.stocks) - self.visible_count
                    self.scroll_index = int(ratio * max_scroll)
                
                # 보유 종목 스크롤 드래그
                elif self.owned_scroll_dragging:
                    # 보유 종목 드래그는 복잡성 문제로 현재는 휠 스크롤만 사용
                    pass


            # 마우스 휠 이벤트 처리 (보유 종목 스크롤)
            elif event.type == pygame.MOUSEWHEEL:
                # 휠 스크롤 감도 설정
                scroll_amount = event.y * 30 
                
                # 최대 스크롤 가능 높이 계산 (대략 계산)
                panel_needed_height = len(self.player.owned_stocks) * 30 + 30
                
                # Y 시작 지점부터 화면 끝까지의 여유 공간 (draw_ui에서 계산하는 것을 참고하여 대략 추정)
                # 총 보유자산 패널 높이 + 여백 제외 (panel_height_assets는 약 70px)
                panel_max_height = self.screen_height - (self.base_font_size * 2 + 10 * 3 + 20) 
                
                max_scroll_y = max(0, panel_needed_height - panel_max_height)
                
                # 스크롤 적용 및 범위 제한
                self.owned_scroll_y = max(0, min(max_scroll_y, self.owned_scroll_y - scroll_amount))


    # ---------------- 구매/판매 버튼 처리 (is_selling 매개변수 사용) ----------------
    def get_trade_context(self, is_selling):
        """거래에 필요한 현재 상태(수량, 현금, 최대 수량 등)를 반환합니다."""
        stock = self.selected_stock
        if not stock: return None
        currency = stock.currency
        price = stock.price
        
        if is_selling:
            available_qty = self.player.owned_stocks.get(stock, {}).get("quantity", 0)
            target_qty = self.sell_qty
            max_qty = available_qty
            total_amount = price * target_qty
            
            can_execute = (target_qty > 0 and target_qty <= available_qty)
        else:
            available_cash = self.player.cash[currency]
            max_qty = int(available_cash / price)
            target_qty = self.purchase_qty
            total_amount = price * target_qty

            can_execute = (target_qty > 0 and available_cash >= total_amount)
        
        return {
            "stock": stock,
            "currency": currency,
            "target_qty": target_qty,
            "max_qty": max_qty,
            "total_amount": total_amount,
            "available_cash": self.player.cash[currency],
            "available_qty": self.player.owned_stocks.get(stock, {}).get("quantity", 0),
            "can_execute": can_execute
        }


    def handle_purchase_buttons(self, key, is_selling):
        context = self.get_trade_context(is_selling)
        if not context: return

        stock = context['stock']
        currency = context['currency']
        target_qty = context['target_qty']
        max_qty = context['max_qty']
        available_qty = context['available_qty']

        # 수량 설정 버튼 처리 (공통)
        new_qty = target_qty

        # [수정] 수량 변경 로직: max_qty가 0이 아닌 경우에만 유효하게 동작
        if max_qty > 0:
            if key == "minus":
                new_qty = max(0, target_qty - 1)
            elif key == "plus":
                new_qty = min(max_qty, target_qty + 1)
            elif key == "pct_10":
                new_qty = min(max_qty, max(1, int(max_qty * 0.1)))
            elif key == "pct_25":
                new_qty = min(max_qty, max(1, int(max_qty * 0.25)))
            elif key == "pct_50":
                new_qty = min(max_qty, max(1, int(max_qty * 0.5)))
            elif key == "pct_100":
                new_qty = max_qty

        # 수량 업데이트: 해당 모드의 변수만 변경
        if is_selling:
            self.sell_qty = new_qty
        else:
            self.purchase_qty = new_qty

        # --- 실행 버튼 처리 ---
        if key == "buy_exec":
            if context['can_execute']:
                success = self.player.invest(stock, self.purchase_qty)
                if success:
                    self.purchase_qty = 1
            else:
                # 잔액 부족 메시지 표시
                self.show_insufficient_funds(currency, context['total_amount'], context['available_cash'])
        
        elif key == "sell_exec":
            if context['can_execute']:
                success = self.player.sell(stock, self.sell_qty)
                if success:
                    if stock not in self.player.owned_stocks:
                        self.selected_owned_stock_info = None 
                        self.selected_owned_row = -1
                    self.sell_qty = 0
            else:
                 # 보유 수량 부족 메시지 표시
                 self.show_insufficient_funds("보유 수량", self.sell_qty, available_qty, is_selling=True)

    # ---------------- 부족 금액/수량 알림 ----------------
    def show_insufficient_funds(self, currency_or_item, required, available, is_selling=False):
        missing = required - available
        if is_selling:
            self.insufficient_funds_msg = f"{currency_or_item} 부족! {missing:.0f}개 초과"
        else:
            self.insufficient_funds_msg = f"{currency_or_item} 잔액 부족! {missing:.2f} 필요"
        self.msg_timer = pygame.time.get_ticks() 

    # ---------------- 가격 업데이트 ----------------
    def update_game(self):
        current_time = time.time()
        if current_time - self.last_update >= 10:
            for stock_list in self.stocks_by_currency.values():
                for stock in stock_list:
                    # Stock.update_price()가 이제 price_history를 업데이트합니다.
                    stock.update_price()
            self.last_update = current_time

    # ---------------- 차트 렌더링 함수 [추가] ----------------
    def draw_chart(self, stock: Stock, rect: pygame.Rect):
        """가격 이력 데이터를 Pygame 화면에 라인 차트로 그립니다."""
        history = stock.price_history
        if len(history) < 2:
            return

        # 1. 스케일링 준비
        min_price = min(history)
        max_price = max(history)
        price_range = max_price - min_price
        
        chart_area = rect.inflate(-10, -10) # 패딩 10px
        
        # 제목 및 가격 정보 표시
        font_small = pygame.font.Font(self.font_path, 14)
        title_text = font_small.render(f"[{stock.name}] Chart ({stock.currency}{stock.price:.2f})", True, UI.COLORS["text"])
        self.screen.blit(title_text, (rect.x + 5, rect.y + 5))
        
        # 2. 가격 정규화 및 좌표 변환
        points = []
        x_start = chart_area.left
        x_end = chart_area.right
        y_bottom = chart_area.bottom
        y_top = chart_area.top

        # 최대 기록 길이(max_history_length)만큼의 X 좌표를 계산합니다.
        # 실제 데이터는 history에 있는 만큼만 사용합니다.
        num_data_points = len(history)
        
        for i, price in enumerate(history):
            # X 좌표: 데이터 개수에 따라 분배 (가장 오른쪽 점이 최신)
            x = x_start + int(i / (stock.max_history_length - 1) * chart_area.width)
            
            # Y 좌표: 가격 정규화 (0.0 ~ 1.0)
            if price_range == 0:
                normalized = 0.5 # 가격 변동 없으면 중앙
            else:
                normalized = (price - min_price) / price_range
            
            # Y 좌표: 화면 좌표로 변환 (0.0이 top, 1.0이 bottom)
            y = y_bottom - int(normalized * chart_area.height)
            points.append((x, y))

        # 3. 차트 라인 그리기
        if len(points) >= 2:
            pygame.draw.lines(self.screen, UI.COLORS["coin_text"], False, points, 2)
            
            # 현재 가격 점 표시 (가장 오른쪽 점)
            pygame.draw.circle(self.screen, UI.COLORS["coin_text"], points[-1], 4)
            
        # 4. 최고/최저가 라벨 표시
        # 최고가 라벨 (차트 상단)
        max_label = font_small.render(f"Max: {stock.currency}{max_price:.2f}", True, UI.COLORS["profit"])
        self.screen.blit(max_label, (rect.x + rect.width - max_label.get_width() - 5, y_top + 5))
        
        # 최저가 라벨 (차트 하단)
        min_label = font_small.render(f"Min: {stock.currency}{min_price:.2f}", True, UI.COLORS["loss"])
        self.screen.blit(min_label, (rect.x + rect.width - min_label.get_width() - 5, y_bottom - 20))


    # ---------------- UI 그리기 ----------------
    def get_auto_font(self, rect, ratio=UI.BUTTON_FONT_RATIO):
        font_size = int(rect.height * ratio)
        return pygame.font.Font(self.font_path, font_size)
    
    def draw_ui(self):
        # 배경 그라데이션
        for i in range(self.screen_height):
            val = UI.BG_COLOR_BASE[0] + i // UI.GRADIENT_STEP
            pygame.draw.line(self.screen, (val, val, val+20), (0,i), (self.screen_width,i))

        # 화폐 단위 버튼 (기존 로직 유지)
        for cur, rect in self.currency_buttons.items():
            mouse_pos = pygame.mouse.get_pos()
            if rect.collidepoint(mouse_pos) or self.selected_currency == cur:
                color = UI.COLORS["button_hover"]
                font_size = int(rect.height * UI.BUTTON_FONT_RATIO * 1.2)
                font = pygame.font.Font(self.font_path, font_size)
                font.set_bold(True)
            else:
                color = UI.COLORS["button"]
                font_size = int(rect.height * UI.BUTTON_FONT_RATIO)
                font = pygame.font.Font(self.font_path, font_size)

            pygame.draw.rect(self.screen, color, rect, border_radius=UI.BUTTON_BORDER_RADIUS)
            if self.selected_currency == cur:
                 pygame.draw.rect(self.screen, UI.COLORS["coin_text"], rect, 3, border_radius=UI.BUTTON_BORDER_RADIUS)
            else:
                pygame.draw.rect(self.screen, UI.COLORS["border_selected"], rect, 2, border_radius=UI.BUTTON_BORDER_RADIUS)

            text = font.render(cur, True, UI.COLORS["text"])
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)

        # 종목 리스트 (기존 로직 유지)
        for i, stock in enumerate(self.stocks[self.scroll_index:self.scroll_index+self.visible_count]):
            rect = self.stock_buttons[i]
            mouse_pos = pygame.mouse.get_pos()

            is_hovered = rect.collidepoint(mouse_pos)
            is_selected = stock.selected

            if is_hovered or is_selected:
                color = UI.COLORS["stock_selected"] if is_selected else UI.COLORS["button_hover"]
                font_size = int(rect.height * UI.BUTTON_FONT_RATIO * 1.2)
                font = pygame.font.Font(self.font_path, font_size)
                font.set_bold(True)
            else:
                color = UI.COLORS["stock_normal"]
                font_size = int(rect.height * UI.BUTTON_FONT_RATIO)
                font = pygame.font.Font(self.font_path, font_size)

            pygame.draw.rect(self.screen, color, rect, border_radius=UI.BUTTON_BORDER_RADIUS)
            pygame.draw.rect(self.screen, UI.COLORS["border_selected"], rect, 2, border_radius=UI.BUTTON_BORDER_RADIUS)

            text = font.render(f"{stock.name}: {stock.price:.2f}", True, UI.COLORS["text"])
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)

        # 스크롤 바 (위치 조정 반영 - 기존 로직 유지)
        scroll_x = UI.POS["stock_list_x"] + UI.POS["stock_width"] + 5
        scroll_y = UI.POS["stock_list_y"]
        scroll_height = self.visible_count * UI.POS["stock_gap"]
        scroll_rect = pygame.Rect(scroll_x, scroll_y, 10, scroll_height)
        pygame.draw.rect(self.screen, (100,100,100), scroll_rect, border_radius=5)
        
        if len(self.stocks) > self.visible_count:
            handle_ratio = self.visible_count / len(self.stocks)
            handle_min_height = 20
            handle_height = max(handle_min_height, int(scroll_height * handle_ratio))
            
            if not self.scroll_dragging:
                scrollable_area = scroll_height - handle_height
                max_scroll_index = len(self.stocks) - self.visible_count
                if max_scroll_index > 0:
                    handle_y = scroll_y + (self.scroll_index / max_scroll_index) * scrollable_area
                else:
                    handle_y = scroll_y
                self.scroll_handle_rect = pygame.Rect(scroll_x, handle_y, 10, handle_height)
            
            pygame.draw.rect(self.screen, (180,180,180), self.scroll_handle_rect, border_radius=5)


        # ---------------- 총보유자산 + 화폐별 현금 패널 (기존 로직 유지) ----------------
        panel_padding = 10 
        margin_right = 20 
        total_assets = self.player.total_assets()
        total_str = f"총 보유자산: {total_assets:.2f} 원"
        assets = self.player.assets_by_currency()
        currency_str = f"현금: 원 {assets['원']:.2f} | 코인 {assets['코인']:.2f} | 금 {assets['금']:.2f} | 스탁 {assets['스탁']:.2f}"
        font_size = self.base_font_size
        font = pygame.font.Font(self.font_path, font_size)
        total_width = font.size(total_str)[0]
        currency_width = font.size(currency_str)[0]
        text_width = max(total_width, currency_width)
        panel_width_assets = max(text_width + panel_padding*2, 300)
        panel_height_assets = font_size*2 + panel_padding*3 
        panel_x_assets = self.screen_width - panel_width_assets - margin_right
        panel_y_assets = 20 

        panel_rect_assets = pygame.Rect(panel_x_assets, panel_y_assets, panel_width_assets, panel_height_assets)
        pygame.draw.rect(self.screen, (50,50,70), panel_rect_assets, border_radius=UI.BUTTON_BORDER_RADIUS)
        pygame.draw.rect(self.screen, UI.COLORS["border_selected"], panel_rect_assets, 2, border_radius=UI.BUTTON_BORDER_RADIUS)

        self.screen.blit(font.render(total_str, True, UI.COLORS["coin_text"]),
                         (panel_x_assets + panel_padding, panel_y_assets + panel_padding))
        self.screen.blit(font.render(currency_str, True, UI.COLORS["coin_text"]),
                         (panel_x_assets + panel_padding, panel_y_assets + panel_padding + font_size + 5))

        # ---------------- 차트 패널 [재추가] ----------------
        chart_height = 200
        chart_panel_rect = pygame.Rect(panel_x_assets, panel_y_assets + panel_height_assets + 10, panel_width_assets, chart_height)
        
        pygame.draw.rect(self.screen, (30, 30, 45), chart_panel_rect, border_radius=UI.BUTTON_BORDER_RADIUS)
        pygame.draw.rect(self.screen, UI.COLORS["border_selected"], chart_panel_rect, 2, border_radius=UI.BUTTON_BORDER_RADIUS)
        
        # 선택된 종목이 있을 경우 차트 그리기
        selected_stock = None
        for stock in self.stocks:
            if stock.selected:
                selected_stock = stock
                break

        if selected_stock:
            self.draw_chart(selected_stock, chart_panel_rect)

        # ---------------- 구매/판매 UI (기존 로직 유지) ----------------
        msg_panel_y_start = 0
        
        if self.selected_stock:
            panel_width = 395 + 40
            panel_height = 70
            purchase_panel_x = UI.POS["stock_list_x"] # 20
            
            purchase_panel_y = UI.POS["stock_list_y"] + self.visible_count * UI.POS["stock_gap"] + 10
            sell_panel_y = purchase_panel_y + panel_height + 5
            
            self.buy_buttons.clear()
            self.sell_buttons.clear()

            def draw_trade_panel(panel_x, panel_y, is_selling):
                panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
                pygame.draw.rect(self.screen, (50,50,70), panel_rect, border_radius=UI.BUTTON_BORDER_RADIUS)
                pygame.draw.rect(self.screen, UI.COLORS["border_selected"], panel_rect, 2, border_radius=UI.BUTTON_BORDER_RADIUS)

                context = self.get_trade_context(is_selling)
                if not context: return panel_y + panel_height

                stock = context['stock']
                current_owned_qty = context['available_qty']
                current_qty = context['target_qty']
                total_amount = context['total_amount']
                max_qty = context['max_qty']
                
                if is_selling:
                    exec_key = "sell_exec"
                    exec_label = "판매"
                    exec_color = (0, 150, 0)
                    exec_hover_color = (50, 200, 50)
                    target_buttons_dict = self.sell_buttons
                    total_color = UI.COLORS["profit"]
                else:
                    exec_key = "buy_exec"
                    exec_label = "구매"
                    exec_color = (200, 0, 0)
                    exec_hover_color = (255, 50, 50)
                    target_buttons_dict = self.buy_buttons
                    total_color = UI.COLORS["coin_text"]

                currency_unit = stock.currency
                display_str = (
                    f"[{stock.name}] 보유: {current_owned_qty:.0f}개 / "
                    f"{exec_label}: {current_qty:.0f}개"
                )
                total_str = f"총액: {total_amount:.2f} {currency_unit}"

                font = pygame.font.Font(self.font_path, 18)
                text = font.render(display_str, True, UI.COLORS["text"])
                self.screen.blit(text, (panel_x + 10, panel_y + 5))
                
                total_text = font.render(total_str, True, total_color)
                total_rect = total_text.get_rect(right=panel_x + panel_width - 10, top=panel_y + 5)
                self.screen.blit(total_text, total_rect)


                btn_gap = 5
                btn_x = panel_x + 10
                btn_y = panel_y + 35
                
                buttons_to_draw = ["minus", "plus", "pct_10", "pct_25", "pct_50", "pct_100", exec_key]
                
                for key in buttons_to_draw:
                    base_key = key if key not in ["buy_exec", "sell_exec"] else ("buy_exec" if not is_selling else "sell_exec")
                    rect_template = self.buttons.get(base_key, self.buttons["buy_exec"]) 
                    rect = pygame.Rect(rect_template)
                    
                    rect.x = btn_x
                    rect.y = btn_y
                    
                    target_buttons_dict[key] = rect
                    
                    is_enabled = True
                    if key in ["minus", "pct_10", "pct_25", "pct_50"]:
                        is_enabled = current_qty > 0 and max_qty > 0
                    elif key in ["plus", "pct_100"]:
                        is_enabled = max_qty > 0 and current_qty < max_qty
                    elif key == exec_key:
                        is_enabled = context['can_execute']
                    
                    mouse_pos = pygame.mouse.get_pos()
                    
                    if key == exec_key:
                        base_color = exec_color
                        hover_color = exec_hover_color
                        label = exec_label
                    else:
                        base_color = UI.COLORS["button"]
                        hover_color = UI.COLORS["button_hover"]
                        label = {
                            "minus":"-","plus":"+",
                            "pct_10":"10%","pct_25":"25%","pct_50":"50%","pct_100":"100%"
                        }[key]

                    if not is_enabled:
                        color = UI.COLORS["disabled"]
                    else:
                        color = hover_color if rect.collidepoint(mouse_pos) else base_color
                        
                    pygame.draw.rect(self.screen, color, rect, border_radius=UI.BUTTON_BORDER_RADIUS)
                    
                    border_thickness = 2 if is_enabled else 1
                    pygame.draw.rect(self.screen, UI.COLORS["border_selected"], rect, border_thickness, border_radius=UI.BUTTON_BORDER_RADIUS)

                    if rect.collidepoint(mouse_pos) and is_enabled:
                        font_size = int(rect.height * UI.BUTTON_FONT_RATIO * 1.2)
                        font_btn = pygame.font.Font(self.font_path, font_size)
                        font_btn.set_bold(True)
                    else:
                        font_size = int(rect.height * UI.BUTTON_FONT_RATIO)
                        font_btn = pygame.font.Font(self.font_path, font_size)
                    
                    text_color = UI.COLORS["text_disabled"] if not is_enabled else UI.COLORS["text"]
                    text = font_btn.render(label, True, text_color)
                    text_rect = text.get_rect(center=rect.center)
                    self.screen.blit(text, text_rect)
                    btn_x += rect.width + btn_gap

                return panel_rect.bottom 


            draw_trade_panel(purchase_panel_x, purchase_panel_y, is_selling=False)
            
            if self.selected_stock in self.player.owned_stocks or self.selected_owned_stock_info:
                draw_trade_panel(purchase_panel_x, sell_panel_y, is_selling=True)
                msg_panel_y_start = sell_panel_y + panel_height + 5
            else:
                msg_panel_y_start = purchase_panel_y + panel_height + 5

        # ---------------- 부족 금액/수량 메시지 (기존 로직 유지) ----------------
        if self.insufficient_funds_msg:
            current_time = pygame.time.get_ticks()
            if current_time - self.msg_timer <= 1500:
                msg_panel_x = UI.POS["stock_list_x"]
                msg_panel_y = msg_panel_y_start 
                msg_panel_width = 395 + 40
                msg_panel_height = 40
                msg_rect = pygame.Rect(msg_panel_x, msg_panel_y, msg_panel_width, msg_panel_height)
                pygame.draw.rect(self.screen, (80,0,0), msg_rect, border_radius=UI.BUTTON_BORDER_RADIUS)
                pygame.draw.rect(self.screen, (255,0,0), msg_rect, 2, border_radius=UI.BUTTON_BORDER_RADIUS)
                font = pygame.font.Font(UI.FONT_PATH, 20)
                text = font.render(self.insufficient_funds_msg, True, (255,200,200))
                text_rect = text.get_rect(center=msg_rect.center)
                self.screen.blit(text, text_rect)
            else:
                self.insufficient_funds_msg = None

        # ---------------- 보유 종목 카드 (위치 및 스크롤 개선) ----------------
        
        # Y 시작 지점을 차트 패널 아래로 조정
        # ---------------- 보유 종목 카드 (위치 및 스크롤 개선) ----------------
        
        # Y 시작 지점을 차트 패널 아래로 조정
        y_start = chart_panel_rect.bottom + 20 
        
        columns = ["종목명", "수", "총액", "변동폭", "구매가", "현재가"]
        # 열 너비 (Asset Panel의 폭에 맞게 조정되었을 것으로 가정)
        base_col_widths = [120, 70, 100, 80, 100, 100] 
        col_x_start = panel_x_assets # 자산 패널과 X 좌표 일치
        row_height = 30
        
        font_small = pygame.font.Font(self.font_path, 16)
        
        # 1. 헤더 그리기
        # panel_width_assets 변수를 사용하여 헤더 영역의 폭을 지정합니다.
        header_rect = pygame.Rect(col_x_start, y_start, panel_width_assets, row_height)
        pygame.draw.rect(self.screen, (80, 80, 100), header_rect)
        
        current_x = col_x_start
        for i, col_name in enumerate(columns):
            text_surf = font_small.render(col_name, True, UI.COLORS["text"])
            # 헤더는 중앙 정렬
            text_rect = text_surf.get_rect(center=(current_x + base_col_widths[i] // 2, y_start + row_height // 2))
            self.screen.blit(text_surf, text_rect)
            current_x += base_col_widths[i]
            # 열 구분선
            if i < len(columns) - 1:
                pygame.draw.line(self.screen, UI.COLORS["border_selected"], (current_x, y_start), (current_x, y_start + row_height))

        # 데이터 표시 영역 설정 (스크롤 영역)
        data_y_start = y_start + row_height
        data_height = self.screen_height - data_y_start - 20 # 화면 하단 여백 20px
        data_panel_rect = pygame.Rect(col_x_start, data_y_start, panel_width_assets, data_height)
        
        # 데이터 표시 영역 클리핑 설정 (이 영역을 벗어나는 내용은 숨김)
        clip_rect = data_panel_rect.copy()
        self.screen.set_clip(clip_rect)

        row_texts = []
        owned_stocks_list = list(self.player.owned_stocks.items())
        
        self.owned_row_rects = [] # 클릭 처리를 위한 Rect 저장

        for idx, (stock, info) in enumerate(owned_stocks_list):
            qty = info["quantity"]
            current_value = stock.price * qty
            buy_total = info["buy_price"] * qty
            
            # 변동폭 (손익률) 계산
            profit_loss = current_value - buy_total
            profit_ratio = (profit_loss / buy_total * 100) if buy_total > 0 else 0
            
            # 행의 Y 좌표 계산 (스크롤 위치 반영)
            row_y = data_y_start + idx * row_height - self.owned_scroll_y
            
            # 행 배경 Rect (클릭 처리를 위해 클리핑 영역 밖에 저장)
            row_rect_full = pygame.Rect(col_x_start, row_y, panel_width_assets, row_height)
            self.owned_row_rects.append(row_rect_full)
            
            # 현재 행이 화면에 보이는지 확인 (클리핑된 영역 내에 있는지)
            if row_rect_full.bottom > data_y_start and row_rect_full.top < data_panel_rect.bottom:
            
                # 선택된 행 강조
                if idx == self.selected_owned_row:
                    pygame.draw.rect(self.screen, UI.COLORS["stock_selected"], row_rect_full)
                else:
                    # 일반 행 배경 (홀수/짝수 구분)
                    bg_color = (40, 40, 60) if idx % 2 == 0 else (50, 50, 70)
                    pygame.draw.rect(self.screen, bg_color, row_rect_full)
                
                current_x = col_x_start
                
                # 셀 데이터 준비
                cell_data = [
                    stock.name,
                    f"{qty:,.0f}",
                    f"{current_value:,.2f}",
                    f"{profit_ratio:+.2f}%", # 변동폭은 손익률로 표시
                    f"{info['buy_price']:,.2f}",
                    f"{stock.price:,.2f}"
                ]
                
                for j, data in enumerate(cell_data):
                    width = base_col_widths[j]
                    
                    # 텍스트 색상 설정
                    text_color = UI.COLORS["text"]
                    if j == 3: # 변동폭(손익률)
                        if profit_ratio > 0: text_color = UI.COLORS["profit"]
                        elif profit_ratio < 0: text_color = UI.COLORS["loss"]
                    
                    text_surf = font_small.render(data, True, text_color)
                    
                    # 정렬: 종목명은 왼쪽, 나머지는 오른쪽 정렬
                    if j == 0: # 종목명 (왼쪽 정렬)
                        text_rect = text_surf.get_rect(midleft=(current_x + 5, row_y + row_height // 2))
                    else: # 나머지 (오른쪽 정렬)
                        text_rect = text_surf.get_rect(midright=(current_x + width - 5, row_y + row_height // 2))

                    self.screen.blit(text_surf, text_rect)
                    current_x += width
                        
        # 클리핑 해제 (화면 전체에 다시 그릴 수 있도록 복구)
        self.screen.set_clip(None) 
        
        # 2. 보유 종목 스크롤 바 그리기 (수직 스크롤)
        panel_needed_height = len(owned_stocks_list) * row_height
        max_scroll_y = max(0, panel_needed_height - data_height)
        
        if max_scroll_y > 0:
            scroll_x = data_panel_rect.right + 5
            scroll_y = data_panel_rect.top
            scroll_height = data_panel_rect.height
            
            # 스크롤 영역 배경
            scroll_rect = pygame.Rect(scroll_x, scroll_y, 10, scroll_height)
            pygame.draw.rect(self.screen, (100,100,100), scroll_rect, border_radius=5)

            # 핸들 크기 계산
            handle_ratio = data_height / panel_needed_height
            handle_min_height = 20
            handle_height = max(handle_min_height, int(scroll_height * handle_ratio))
            
            # 핸들 위치 계산
            scrollable_area = scroll_height - handle_height
            # self.owned_scroll_y 값에 따라 핸들 위치 결정
            handle_y = scroll_y + (self.owned_scroll_y / max_scroll_y) * scrollable_area
            
            self.owned_v_scroll_handle_rect = pygame.Rect(scroll_x, handle_y, 10, handle_height)
            pygame.draw.rect(self.screen, (180,180,180), self.owned_v_scroll_handle_rect, border_radius=5)
        else:
            self.owned_v_scroll_handle_rect = None


    # ---------------- 실행 ----------------
    def run(self):
        while self.running:
            self.handle_events()
            self.update_game()
            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()