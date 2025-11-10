import pygame
from classes.stock import Stock
from classes.player import Player
import time

class Game:
    def __init__(self):
        pygame.init()
        self.screen_width, self.screen_height = 1280, 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("랜덤 코인 게임 v0.2")
        self.clock = pygame.time.Clock()
        self.running = True

        # 한글 폰트
        font_path = "C:/Windows/Fonts/malgun.ttf"  # 맑은 고딕
        self.font = pygame.font.Font(font_path, 30)

        # 게임 초기화
        self.player = Player()
        self.stocks = [Stock(f"코인{i+1}", 100) for i in range(20)]
        self.selected_stock = None

        # 가격 갱신
        self.last_update = time.time()

        # 버튼 영역 정의
        self.purchase_buttons = [
            {"text": "1개 구매", "qty": 1, "rect": pygame.Rect(450, 100, 80, 30)},
            {"text": "5개 구매", "qty": 5, "rect": pygame.Rect(540, 100, 80, 30)},
            {"text": "10개 구매", "qty": 10, "rect": pygame.Rect(630, 100, 80, 30)}
        ]

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos

                # 종목 선택
                for i, stock in enumerate(self.stocks):
                    if 20 <= x <= 400 and 20 + i*30 <= y <= 20 + (i+1)*30:
                        for s in self.stocks:
                            s.selected = False
                        stock.selected = True
                        self.selected_stock = stock

                # 버튼 클릭 처리
                if self.selected_stock:
                    for btn in self.purchase_buttons:
                        if btn["rect"].collidepoint(event.pos):
                            quantity = btn["qty"]
                            success = self.player.invest(self.selected_stock, quantity)
                            if not success:
                                print("코인이 부족합니다!")

    def update_game(self):
        current_time = time.time()
        if current_time - self.last_update >= 10:  # 10초마다 가격 갱신
            for stock in self.stocks:
                stock.update_price()
            self.last_update = current_time

    def draw_ui(self):
        self.screen.fill((0,0,0))
        y = 20

        # 종목 리스트
        for stock in self.stocks:
            color = (0,255,0) if stock.selected else (255,255,255)
            text = self.font.render(f"{stock.name}: {stock.price}", True, color)
            self.screen.blit(text, (20, y))
            y += 30

        # 플레이어 자산
        asset_text = self.font.render(f"플레이어 코인: {self.player.coins}", True, (255,255,0))
        self.screen.blit(asset_text, (self.screen_width-250, 20))

        # 구매 버튼 표시
        if self.selected_stock:
            for btn in self.purchase_buttons:
                pygame.draw.rect(self.screen, (100,100,255), btn["rect"])
                btn_text = self.font.render(btn["text"], True, (255,255,255))
                self.screen.blit(btn_text, (btn["rect"].x+5, btn["rect"].y+5))

        # 보유 종목
        y = 300
        for stock, info in self.player.owned_stocks.items():
            quantity = info["quantity"]
            buy_price = info["buy_price"]
            current_price = stock.price
            profit = round((current_price - buy_price)/buy_price*100,2)
            text = self.font.render(
                f"{stock.name} x{quantity} | 총액: {current_price*quantity:.2f} | 수익률: {profit}%",
                True, (255,255,255)
            )
            self.screen.blit(text, (800, y))
            y += 25

    def run(self):
        while self.running:
            self.handle_events()
            self.update_game()
            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()
