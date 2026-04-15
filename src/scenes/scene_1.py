import pygame
from src.core.settings import *
from src.entities.player import Player

class Scene1:
    def __init__(self, scene_manager):
        self.scene_manager = scene_manager
        self.player = Player(100, 480) # Y adjusted so bottom is near 500
        self.bullets = pygame.sprite.Group()
        
        # Cổng kim tự tháp (Khu vực chuyển màn) ở mặt đất
        self.pyramid_gate = pygame.Rect(650, 350, 100, 150)

    def reset(self):
        self.player.rect.center = (100, 480)
        self.bullets.empty()

    def update(self, events):
        self.player.update()
        
        # Ở Màn 1: Ép di chuyển ngang, không cho đi lên xuống
        self.player.rect.bottom = 500
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.player.attack(self.bullets)
                
        self.bullets.update()

        # Nếu player chạm vào cổng -> Chuyển sang Màn 2
        if self.player.rect.colliderect(self.pyramid_gate):
            self.scene_manager.switch_scene("Scene2")

    def draw(self, screen):
        # Vẽ bầu trời sa mạc
        screen.fill((135, 206, 235)) # Màu trời xanh
        
        # Vẽ kim tự tháp (Đơn giản là một tam giác lớn)
        pygame.draw.polygon(screen, (180, 140, 100), [(450, 500), (900, 500), (675, 100)])
        
        # Cổng Kim Tự Tháp
        pygame.draw.rect(screen, (50, 30, 10), self.pyramid_gate)
        
        # Vẽ mặt đất cát
        pygame.draw.rect(screen, (210, 180, 140), (0, 500, SCREEN_WIDTH, SCREEN_HEIGHT - 500))
        
        # Vẽ hướng dẫn
        font = pygame.font.SysFont("tahoma", 24)
        info = font.render("A/D để di chuyển. Đi vào cổng Kim Tự Tháp", True, BLACK)
        screen.blit(info, (20, 20))

        # Vẽ player và đạn
        self.player.draw(screen)
        self.bullets.draw(screen)
