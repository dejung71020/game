import pygame
from classes.stock import Stock
from classes.player import Player

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Random Coin Game v0.1")
        self.clock = pygame.time.Clock()
        self.running = True

        # 초기화
        self.player = Player()
        self.stocks = [Stock(f"Coin{i+1}", 100) for i in range(20)]
        self.selected_stock = self.stocks[0]

        self.invest()  # 플레이어 초기 투자

    def invest(self):
        self.player.invest(self.selected_stock)

    def run(self):
        import time
        last_update = time.time()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # 10초마다 가격 갱신
            if time.time() - last_update > 10:
                for stock in self.stocks:
                    stock.update_price()
                self.player.update_assets()
                last_update = time.time()

            # 화면 출력
            self.screen.fill((0, 0, 0))
            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(60)

    def draw_ui(self):
        font = pygame.font.Font(None, 30)
        y = 20
        for stock in self.stocks:
            text = font.render(f"{stock.name}: {stock.price}", True, (255, 255, 255))
            self.screen.blit(text, (20, y))
            y += 30

        # 플레이어 자산
        text = font.render(f"Player Coins: {self.player.coins}", True, (255, 255, 0))
        self.screen.blit(text, (20, y))
