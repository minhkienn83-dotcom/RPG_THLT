import pygame
import sys
from src.core.settings import *
from src.core.scene_manager import SceneManager
from src.scenes.scene_1 import Scene1
from src.scenes.scene_2 import Scene2
from src.scenes.scene_3 import Scene3

# Khởi tạo Pygame
pygame.init()
pygame.font.init() # Khởi tạo font
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("FSM Dungeon RPG - CTU Automata Project")
clock = pygame.time.Clock()

# Quản lý Màn Chơi
scene_manager = SceneManager()
scene_manager.add_scene("Scene1", Scene1(scene_manager))
scene_manager.add_scene("Scene2", Scene2(scene_manager))
scene_manager.add_scene("Scene3", Scene3(scene_manager))

# Khởi chạy màn đầu tiên
scene_manager.switch_scene("Scene1")

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Cập nhật logic màn hiện tại
    scene_manager.update(events)

    # Vẽ Màn Hình
    scene_manager.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)