import pygame
from src.core.settings import *
from src.entities.player import Player

class Scene1:
    def __init__(self, scene_manager):
        self.scene_manager = scene_manager
        self.player = Player(100, 300)
        self.bullets = pygame.sprite.Group()
        
        # Cổng kim tự tháp (Khu vực chuyển màn)
        self.pyramid_gate = pygame.Rect(650, 200, 100, 200)

    def reset(self):
        self.player.rect.center = (100, 300)
        self.bullets.empty()

    def update(self, events):
        self.player.update()
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.player.attack(self.bullets)
                
        self.bullets.update()

        # Nếu player chạm vào cổng -> Chuyển sang Màn 2
        if self.player.rect.colliderect(self.pyramid_gate):
            self.scene_manager.switch_scene("Scene2")

    def draw(self, screen):
        # Vẽ nền Sa mạc
        screen.fill((210, 180, 140)) # Màu cát
        
        # Vẽ kim tự tháp (Đơn giản là một tam giác lớn)
        pygame.draw.polygon(screen, (180, 140, 100), [(500, 600), (900, 600), (700, 50)])
        
        # Vẽ cổng
        pygame.draw.rect(screen, (50, 30, 10), self.pyramid_gate)
        
        # Vẽ hướng dẫn
        font = pygame.font.SysFont("Arial", 24)
        info = font.render("WASD đế di chuyển. Đi vào cổng Kim Tự Tháp", True, BLACK)
        screen.blit(info, (20, 20))

        # Vẽ player và đạn
        self.player.draw(screen)
        self.bullets.draw(screen)
