import pygame
from src.core.settings import *
from src.entities.player import Player

class Scene1:
    def __init__(self, scene_manager):
        self.scene_manager = scene_manager
        self.player = Player(100, 480)
        self.bullets = pygame.sprite.Group()

        # --- PHẦN CĂN CHỈNH KIM TỰ THÁP ---
        try:
            # 1. Load Background
            self.bg_image = pygame.image.load("assets/graphics/Map/Scene1/scene1background.jpg").convert()
            self.bg_image = pygame.transform.scale(self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

            # 2. Load và Scale Kim tự tháp
            raw_pyramid = pygame.image.load("assets/graphics/Map/Scene1/pyramid.png").convert_alpha()
            
            # Đặt kích thước mới (Ví dụ: rộng 300px, cao tự tính theo tỉ lệ hoặc đặt 300x300)
            # Bạn có thể thay đổi số 300, 300 này để to/nhỏ tùy ý
            self.pyramid_image = pygame.transform.scale(raw_pyramid, (300, 300))
            
            self.pyramid_rect = self.pyramid_image.get_rect()
            
            # Đẩy sát sang bên phải màn hình
            self.pyramid_rect.right = SCREEN_WIDTH 
            # Đặt đáy kim tự tháp nằm trên mặt đất (khớp với chân player)
            self.pyramid_rect.bottom = 500 + 60
            
            # 3. Định nghĩa lại vùng cửa (Gate) dựa trên kích thước mới của kim tự tháp
            # Cửa thường nằm ở giữa đáy kim tự tháp
            self.pyramid_gate = pygame.Rect(
                self.pyramid_rect.centerx - 20, 
                self.pyramid_rect.bottom - 60, 
                40, 60
            )
            
        except Exception as e:
            print(f"Lỗi: {e}")
            # ... (phần xử lý lỗi như cũ)
    def reset(self):
        """Hàm này được gọi mỗi khi switch_scene về Scene1"""
        self.player.rect.center = (100, 480)
        # Kiểm tra xem bullets có tồn tại không trước khi empty
        if hasattr(self, 'bullets'):
            self.bullets.empty()

    def update(self, events):
        self.player.update()
        self.player.rect.bottom = 530 # Giữ nhân vật trên mặt đất
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.player.attack(self.bullets)
                
        self.bullets.update()

        # Chuyển cảnh khi chạm cửa
        if self.player.rect.colliderect(self.pyramid_gate):
            self.scene_manager.switch_scene("Scene2")

    def draw(self, screen):
        # Vẽ theo thứ tự: Nền -> Kim tự tháp -> Nhân vật
        screen.blit(self.bg_image, (0, 0))
        screen.blit(self.pyramid_image, self.pyramid_rect)
        
        self.player.draw(screen)
        self.bullets.draw(screen)