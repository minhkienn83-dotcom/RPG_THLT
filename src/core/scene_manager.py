import pygame

class SceneManager:
    def __init__(self):
        self.scenes = {}
        self.current_scene_name = None

    def add_scene(self, name, scene):
        self.scenes[name] = scene

    def switch_scene(self, name):
        if name in self.scenes:
            self.current_scene_name = name
            # Gọi hàm khởi tạo lại màn chơi nếu cần (reset trạng thái)
            if hasattr(self.scenes[name], 'reset'):
                self.scenes[name].reset()

    def update(self, events):
        if self.current_scene_name:
            self.scenes[self.current_scene_name].update(events)

    def draw(self, screen):
        if self.current_scene_name:
            self.scenes[self.current_scene_name].draw(screen)
