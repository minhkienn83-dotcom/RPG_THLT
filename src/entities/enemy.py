import pygame
import random
import math
from src.automata.fsm import EnemyFSM
from src.core.utils import load_spritesheet
from src.core.settings import *

class BaseEnemy(pygame.sprite.Sprite):
    def __init__(self, x, y, sheet_path, rows, cols):
        super().__init__()
        
        # 1. Thông số cơ bản
        self.max_health = 100
        self.health = 100
        self.walk_speed = 1
        self.run_speed = 2
        
        # 2. Logic Animation & FSM
        self.all_frames = load_spritesheet(sheet_path, rows, cols)
        self.animations = {
            "PATROL": self.all_frames[1], # Dòng Walk
            "CHASE":  self.all_frames[2], # Dòng Run
            "ATTACK": self.all_frames[4], # Dòng Jump
            "DEAD":   self.all_frames[5]  # Dòng Hurt
        }
        
        self.fsm = EnemyFSM()
        self.current_state = "PATROL"
        
        # 3. Biến điều khiển di chuyển và Alert
        self.patrol_timer = 0
        self.patrol_duration = random.randint(60, 150)
        self.direction_x = random.choice([-1, 1])
        self.show_alert = False
        self.alert_start_time = 0
        
        # 4. Hình ảnh và Vị trí
        self.frame_index = 0
        self.animation_speed = 0.15
        self.image = self.animations[self.current_state][self.frame_index]
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, player_pos):
        if self.current_state == "DEAD":
            self.animate() # Chỉ chạy animation chết
            return
            
        # Lưu trạng thái cũ để kiểm tra chuyển đổi
        old_state = self.current_state
        
        # Tính khoảng cách đến người chơi
        dist = math.hypot(player_pos[0] - self.rect.centerx, player_pos[1] - self.rect.centery)
        
        # Cập nhật FSM
        self.fsm.compute_next_state(dist, self.health)
        self.current_state = self.fsm.get_current_state()
        
        # Kích hoạt dấu "!" khi bắt đầu đuổi theo
        if old_state == "PATROL" and self.current_state == "CHASE":
            self.show_alert = True
            self.alert_start_time = pygame.time.get_ticks()
        
        self.move(player_pos)
        self.animate()

    def move(self, player_pos):
        if self.current_state == "PATROL":
            self.patrol_timer += 1
            if self.patrol_timer >= self.patrol_duration:
                self.patrol_timer = 0
                self.patrol_duration = random.randint(60, 150)
                self.direction_x = random.choice([-1, 0, 1])
            
            self.rect.x += self.direction_x * self.walk_speed
            
            # Giữ nhân vật trong màn hình
            if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
                self.direction_x *= -1

        elif self.current_state == "CHASE":
            dx = player_pos[0] - self.rect.centerx
            dy = player_pos[1] - self.rect.centery
            norm = math.hypot(dx, dy)
            if norm != 0:
                self.direction_x = 1 if dx > 0 else -1
                self.rect.x += (dx / norm) * self.run_speed
                self.rect.y += (dy / norm) * self.run_speed

    def animate(self):
        frames = self.animations[self.current_state]
        self.frame_index += self.animation_speed
        
        if self.frame_index >= len(frames):
            self.frame_index = 0
        
        current_frame_img = frames[int(self.frame_index)]
        
        # Lật ảnh theo hướng di chuyển
        if self.direction_x == -1:
            self.image = pygame.transform.flip(current_frame_img, True, False)
        else:
            self.image = current_frame_img

    def draw_alert(self, screen):
        if self.show_alert:
            if pygame.time.get_ticks() - self.alert_start_time < 1000:
                font = pygame.font.SysFont("Arial", 30, bold=True)
                alert_text = font.render("!", True, (255, 0, 0))
                screen.blit(alert_text, (self.rect.centerx - 5, self.rect.top - 35))
            else:
                self.show_alert = False

    def take_damage(self, amount):
        if self.current_state != "DEAD":
            self.health -= amount
            if self.health <= 0:
                self.health = 0
                self.fsm.compute_next_state(0, self.health)
                self.current_state = self.fsm.get_current_state()
                self.frame_index = 0 # reset animation

    def draw_health_bar(self, screen):
        if self.current_state != "DEAD":
            # Chiều rộng thanh máu gốc
            bar_width = 40
            bar_height = 5
            # Vị trí trên đầu
            x = self.rect.centerx - bar_width // 2
            y = self.rect.top - 10
            
            # Tính tỉ lệ máu
            health_ratio = max(0, self.health) / self.max_health
            current_bar_width = int(bar_width * health_ratio)
            
            # Vẽ nền đỏ, máu xanh lá
            pygame.draw.rect(screen, (255, 0, 0), (x, y, bar_width, bar_height))
            pygame.draw.rect(screen, (0, 255, 0), (x, y, current_bar_width, bar_height))
                
# --- CÁC LOẠI KẺ ĐỊCH CỤ THỂ ---

class Minion(BaseEnemy):
    def __init__(self, x, y):
        # Minion dùng ảnh gốc, kích thước 6 hàng x 6 cột theo ảnh bạn gửi
        super().__init__(x, y, "assets/graphics/minion.png", 7, 7)
        self.walk_speed = 1
        self.run_speed = 2

class Scout(BaseEnemy):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/graphics/scout.png", 7, 5)
        self.walk_speed = 2
        self.run_speed = 4
        # Bạn có thể điều chỉnh tỉ lệ kích thước để phân biệt Scout
        self.image = pygame.transform.scale(self.image, (40, 40))

class Guardian(BaseEnemy):
    def __init__(self, x, y):
        # Dùng hình ảnh của scout nhưng nhân đôi kích thước cho to hơn
        super().__init__(x, y, "assets/graphics/scout.png", 7, 5) 
        self.max_health = 300
        self.health = 300 # Boss trâu hơn
        self.walk_speed = 1
        self.run_speed = 3
        
        # Scale up tất cả các frame của Boss để trông bự và nguy hiểm hơn
        for state in self.animations:
            new_frames = []
            for frame in self.animations[state]:
                # Phóng to mỗi frame lên gấp 2
                w, h = frame.get_size()
                big_frame = pygame.transform.scale(frame, (w * 2, h * 2))
                new_frames.append(big_frame)
            self.animations[state] = new_frames
            
        self.image = self.animations[self.current_state][0]
        self.rect = self.image.get_rect(center=(x, y))
        self.is_hostile = False # Ban đầu có thể không đuổi theo

    def update(self, player_pos):
        if not self.is_hostile:
            # Nếu chưa Hostile thì đứng im (IDLE) - tạm ép IDLE bằng row Walk
            self.current_state = "PATROL"
            self.animate()
            return
        super().update(player_pos)
        
    def animate(self):
        super().animate()