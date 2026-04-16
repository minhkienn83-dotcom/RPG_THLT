import pygame
import sys
from src.core.settings import *
from src.entities.player import Player # Giả định file này tồn tại theo scene_2.py
from src.scenes.scene_2 import Scene2

# 1. Tạo một lớp giả (Mock) cho SceneManager để Scene2 không bị lỗi khi chuyển cảnh
class MockSceneManager:
    def __init__(self):
        self.current_scene = None

    def switch_scene(self, scene_name):
        print(f"Chuyển đến cảnh: {scene_name}")

def main():
    # 2. Khởi tạo Pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Kiểm tra Scene 2 - FSM Hunter")
    clock = pygame.time.Clock()

    # 3. Khởi tạo Scene2
    # Lưu ý: Đảm bảo file 'dialogue_game.py' có sẵn trong thư mục vì scene_2.py có import nó
    scene_manager = MockSceneManager()
    test_scene = Scene2(scene_manager)

    running = True
    while running:
        # 4. Lấy danh sách sự kiện
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            
            # Phím tắt để reset nhanh khi đang test
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    test_scene.reset()
                    print("Đã Reset Scene 2")

        # 5. Cập nhật logic (Truyền danh sách events vào update theo yêu cầu của Scene2)
        test_scene.update(events)

        # 6. Vẽ nội dung lên màn hình
        test_scene.draw(screen)

        # Cập nhật hiển thị và duy trì FPS
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()