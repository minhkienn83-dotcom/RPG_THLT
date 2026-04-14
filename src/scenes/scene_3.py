import pygame
from src.core.settings import *

class Scene3:
    def __init__(self, scene_manager):
        self.scene_manager = scene_manager
        
        self.font = pygame.font.SysFont("Arial", 40, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 25)
        
    def reset(self):
        pass

    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                # Bấm Enter để chơi lại (nếu cần)
                self.scene_manager.switch_scene("Scene1")

    def draw(self, screen):
        # Phòng kho báu
        screen.fill((50, 40, 20)) # Nền vàng tối
        
        # Vẽ một số cục vàng (Kho báu)
        pygame.draw.circle(screen, (255, 215, 0), (400, 300), 50)
        pygame.draw.circle(screen, (255, 215, 0), (350, 350), 40)
        pygame.draw.circle(screen, (255, 215, 0), (450, 350), 40)

        title = self.font.render("YOU WIN! TÌM THẤY KHO BÁU!", True, (255, 255, 50))
        screen.blit(title, (150, 200))
        
        subtitle = self.small_font.render("Nhấn ENTER để văng ra khỏi đền (Chơi lại).", True, WHITE)
        screen.blit(subtitle, (180, 450))
