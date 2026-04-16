import pygame
from src.core.settings import *
from src.entities.player import Player

class Scene1:
    def __init__(self, scene_manager):
        self.scene_manager = scene_manager
        
        # Giả sử nhân vật của bạn đang đứng ở y = 500
        self.player = Player(100, 500) 

        # ---------------- THÊM CODE LOAD ẢNH ----------------
        
        # 1. Load và scale Background cho vừa toàn màn hình
        self.bg_image = pygame.image.load("assets/graphics/Map/Scene1/scene1background.jpg").convert()
        self.bg_image = pygame.transform.scale(self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # 2. Load Kim tự tháp (Nhớ dùng .png và convert_alpha để giữ nền trong suốt)
        self.pyramid_image = pygame.image.load("assets/graphics/Map/Scene1/pyramid.png").convert_alpha()
        
        # (Tùy chọn) Scale kim tự tháp nếu ảnh gốc quá to hoặc quá nhỏ
        # self.pyramid_image = pygame.transform.scale(self.pyramid_image, (400, 400))
        
        # 3. Lấy Rect và căn chỉnh vị trí
        self.pyramid_rect = self.pyramid_image.get_rect()
        
        # Căn sang bên phải màn hình (cách lề phải 20px)
        self.pyramid_rect.right = SCREEN_WIDTH - 20
        
        # QUAN TRỌNG: Căn đáy của Kim tự tháp bằng với đáy của Player để nằm chung trên mặt đất
        self.pyramid_rect.bottom = self.player.rect.bottom 
        
        # ----------------------------------------------------