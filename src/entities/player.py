import pygame
import math
from src.core.settings import *
from src.core.utils import load_spritesheet, load_individual_sprites

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
        
        p1 = "assets/graphics/Main close attack/Individual Sprites"
        p2 = "assets/graphics/Main range attack/Individual Sprites"
        self.animations = {
            "IDLE": load_individual_sprites(p1, "adventurer-idle-0", scale=2),
            "RUN":  load_individual_sprites(p1, "adventurer-run-0", scale=2),
            "ATTACK_MELEE": load_individual_sprites(p1, "adventurer-attack1-0", scale=2),
            "ATTACK_RANGED": load_individual_sprites(p2, "adventurer-bow-0", scale=2),
        }
        
        # Cứu hộ an toàn nếu thiếu file
        for k in self.animations:
            if not self.animations[k]:
                self.animations[k] = [pygame.Surface((50,50), pygame.SRCALPHA)]
        
        self.current_state = "IDLE"
        self.frame_index = 0
        self.animation_speed = 0.25
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
            self.current_state = "ATTACK_MELEE" if is_melee else "ATTACK_RANGED"
            self.frame_index = 0
            
            # Khóa tốc độ cooldown theo thời gian render animation
            frames_count = len(self.animations[self.current_state])
            self.attack_cooldown = int(frames_count / self.animation_speed) - 2
            
            mx, my = pygame.mouse.get_pos()
            # Đổi hướng nhân vật theo con trỏ chuột
            if mx < self.rect.centerx: self.direction_x = -1
            else: self.direction_x = 1
            
            if not is_melee:
                # Bắn đạn, chỉnh offset mũi cung tí xíu
                bullet = Bullet(self.rect.centerx, self.rect.centery, mx, my)
                bullets_group.add(bullet)

    def handle_attack(self):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def draw(self, screen):
        # Tọa độ vẽ chuẩn tâm player
        draw_rect = self.image.get_rect(center=self.rect.center)
        screen.blit(self.image, draw_rect)
        
        # Chỉ lấy hitbox xử lý logic, không vẽ khung đỏ ra màn hình nữa
        if self.is_attacking and self.is_melee:
            attack_rect = self.get_attack_rect()

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
