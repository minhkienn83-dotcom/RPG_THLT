import pygame
import math
from src.core.settings import *
from src.core.utils import load_spritesheet

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y):
        super().__init__()
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 255, 0), (5, 5), 5) # Đạn vàng
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10
        
        dx = target_x - x
        dy = target_y - y
        dist = math.hypot(dx, dy)
        if dist == 0:
            self.dx = 1
            self.dy = 0
        else:
            self.dx = dx / dist
            self.dy = dy / dist
        self.pos_x = float(x)
        self.pos_y = float(y)
            
    def update(self):
        self.pos_x += self.dx * self.speed
        self.pos_y += self.dy * self.speed
        self.rect.centerx = int(self.pos_x)
        self.rect.centery = int(self.pos_y)
        # Xóa đạn nếu bay ra ngoài màn hình
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Load sprite cho Player (Tạm lấy minion.png làm mẫu nhân vật)
        self.all_frames = load_spritesheet("assets/graphics/minion.png", 7, 7)
        self.animations = {
            "IDLE": self.all_frames[0],   # Row 0 (Tùy spritesheet thực tế)
            "RUN":  self.all_frames[1],   # Row Walk/Run 
            "ATTACK": self.all_frames[4], # Dòng Jump/Attack
        }
        self.current_state = "IDLE"
        self.frame_index = 0
        self.animation_speed = 0.15
        self.image = self.animations[self.current_state][int(self.frame_index)]
        
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = PLAYER_SPEED
        self.health = 100
        self.direction_x = 1 # 1 is right, -1 is left
        
        # Biến trạng thái chiến đấu
        self.is_attacking = False
        self.is_melee = False
        self.attack_timer = 0
        self.attack_duration = 20  # frame
        self.attack_cooldown = 0
        
    def animate(self):
        frames = self.animations[self.current_state]
        self.frame_index += self.animation_speed
        
        if self.frame_index >= len(frames):
            self.frame_index = 0
            if self.is_attacking:
                # Ngưng attack animation khi hết frames
                self.is_attacking = False
                self.current_state = "IDLE"
        
        current_frame_img = frames[int(self.frame_index)]
        
        # Lật ảnh theo hướng nhìn
        if self.direction_x == -1:
            self.image = pygame.transform.flip(current_frame_img, True, False)
        else:
            self.image = current_frame_img

    def update(self):
        self.move()
        self.handle_attack()
        self.animate()
        
    def move(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        
        if keys[pygame.K_w] or keys[pygame.K_UP]: dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: 
            dx -= 1
            self.direction_x = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: 
            dx += 1
            self.direction_x = 1
        
        # Cập nhật trạng thái cho Animation
        if not self.is_attacking:
            if dx == 0 and dy == 0:
                self.current_state = "IDLE"
            else:
                self.current_state = "RUN"
            
        # Chuẩn hóa vector di chuyển đường chéo
        if dx != 0 and dy != 0:
            norm = math.hypot(dx, dy)
            dx = dx / norm
            dy = dy / norm
            
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        
        # Giữ player trong màn hình
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

    def attack(self, bullets_group, is_melee=False):
        if self.attack_cooldown <= 0:
            self.is_attacking = True
            self.is_melee = is_melee
            self.current_state = "ATTACK"
            self.frame_index = 0
            self.attack_cooldown = 15 # Fix bắn nhanh hơn để dễ chơi
            
            mx, my = pygame.mouse.get_pos()
            # Đổi hướng nhân vật theo con trỏ chuột
            if mx < self.rect.centerx: self.direction_x = -1
            else: self.direction_x = 1
            
            if not is_melee:
                # Bắn đạn
                bullet = Bullet(self.rect.centerx, self.rect.centery, mx, my)
                bullets_group.add(bullet)

    def handle_attack(self):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        # Vẽ hitbox tấn công nếu đang đánh cận chiến
        if self.is_attacking and self.is_melee:
            attack_rect = self.get_attack_rect()
            pygame.draw.rect(screen, (255, 0, 0), attack_rect, 2) # Xung quanh để gỡ lỗi màu đỏ

    def get_attack_rect(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = mouse_x - self.rect.centerx
        dy = mouse_y - self.rect.centery
        angle = math.atan2(dy, dx)
        
        reach = 40
        ax = self.rect.centerx + math.cos(angle) * reach
        ay = self.rect.centery + math.sin(angle) * reach
        
        attack_rect = pygame.Rect(0, 0, 50, 50)
        attack_rect.center = (ax, ay)
        return attack_rect
