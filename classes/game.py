import pygame
import time
from classes.stock import Stock
from classes.player import Player

class Game:
    def __init__(self):
        # Pygame 초기화
        pygame.init()
        
        # PC용 넓은 화면
        self.screen_width = 1280
        self.screen_height = 720
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height)
        )
        pygame.display.set_caption("Random Coin Game v0.1 - PC")
        self.clock = pygame.time.Clock()
        self.running = True

        # 게임 초기화
        self.player = Player()
        self.stocks = [Stock(f"Coin{i+1}", 100) for i in range(20)]
        self.selected_stock = self.stocks[0]
        self.player.invest(self.selected_stock)

        # 마지막 가격 갱신 시간
        self.last_update = time.time()

    def run(self):
        while self.running:
            self.handle_events()
            self.update_game()
            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(60)  # 60 FPS

        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update_game(self):
        import random
        # 10초마다 모든 종목 가격 갱신
        current_time = time.time()
        if current_time - self.last_update >= 2:
            for stock in self.stocks:
                stock.update_price()
            # 플레이어 자산 갱신
            self.player.update_assets()
            self.last_update = current_time

    def draw_ui(self):
        self.screen.fill((0, 0, 0))  # 배경 검정
        font = pygame.font.Font(None, 30)
        y = 20

        # 종목 리스트 출력 (왼쪽 영역)
        for stock in self.stocks:
            text = font.render(f"{stock.name}: {stock.price}", True, (255, 255, 255))
            self.screen.blit(text, (20, y))
            y += 30

        # 플레이어 자산 (오른쪽 상단)
        asset_text = font.render(f"Player Coins: {self.player.coins}", True, (255, 255, 0))
        self.screen.blit(asset_text, (self.screen_width - 250, 20))
