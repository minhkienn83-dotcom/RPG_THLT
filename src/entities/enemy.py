import pygame
import random
import math
from src.automata.fsm import EnemyFSM
from src.core.utils import load_spritesheet_auto
from src.core.settings import *

# Cấu hình width thủ công cho những dải strip đặc biệt rách / không chuẩn
ENEMY_FRAME_CONFIG = {
    'spr_ArcherAttack_strip_NoBkg.png': 18,
    'spr_ArcherDash_strip_NoBkg.png': 14,
    'spr_ArcherDeath_strip_NoBkg.png': 24,
    'spr_ArcherIdle_strip_NoBkg.png': 8,
    'spr_ArcherJumpAndFall_strip_NoBkg.png': 12,
    'spr_ArcherMelee_strip_NoBkg.png': 28,
    'spr_ArcherRun_strip_NoBkg.png': 8,
    'spr_Attack_strip.png': 30, # 5100 / 170
    'spr_Dash_strip.png': 8, # 1360 / 170
    'spr_Death_strip.png': 40, # 6800 / 170
    'spr_Idle_strip.png': 16, # 2720 / 170
    'spr_Jump_strip.png': 55, # 5500 / 100
    'spr_Leap_strip.png': 80, # 10400 / 130
    'spr_SpinAttack_strip.png': 30, # 5100 / 170
    'spr_Taunt_strip.png': 18, # 3060 / 170
    'spr_Walk_strip.png': 8, # 1360 / 170
}

class Arrow(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y):
        super().__init__()
        self.image = pygame.Surface((15, 4), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (255, 100, 100), (0, 0, 15, 4)) # Đạn đỏ thẫm
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 8
        
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
        
        # Quay mũi tên
        angle = math.degrees(math.atan2(-self.dy, self.dx))
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect(center=(x, y))
            
    def update(self):
        self.pos_x += self.dx * self.speed
        self.pos_y += self.dy * self.speed
        self.rect.centerx = int(self.pos_x)
        self.rect.centery = int(self.pos_y)
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

class BaseEnemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        self.max_health = 100
        self.health = 100
        self.walk_speed = 1
        self.run_speed = 2
        
        self.animations = {}
        self.fsm = EnemyFSM()
        self.current_state = "PATROL"
        
        self.patrol_timer = 0
        self.patrol_duration = random.randint(60, 150)
        self.direction_x = random.choice([-1, 1])
        self.show_alert = False
        self.alert_start_time = 0
        
        self.frame_index = 0
        self.animation_speed = 0.25
        
        # Sẽ thiết lập image ở class con
        self.image = None
        self.rect = None

        self.is_attacking = False
        self.attack_timer = 0
        self.attack_cooldown = 0
    
    def take_damage(self, amount):
        if self.current_state != "DEAD":
            self.health -= amount
            if self.health <= 0:
                self.health = 0
                self.current_state = "DEAD"
                self.frame_index = 0

    def draw_health_bar(self, screen):
        if self.current_state != "DEAD" and self.rect:
            bar_width = 40
            bar_height = 5
            x = self.rect.centerx - bar_width // 2
            y = self.rect.top - 10
            health_ratio = max(0, self.health) / self.max_health
            current_bar_width = int(bar_width * health_ratio)
            pygame.draw.rect(screen, (255, 0, 0), (x, y, bar_width, bar_height))
            pygame.draw.rect(screen, (0, 255, 0), (x, y, current_bar_width, bar_height))


class Archer(BaseEnemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.max_health = 80
        self.health = 80
        self.run_speed = 1.5
        p = "assets/graphics/Enemy archer/"
        self.animations = {
            "IDLE": load_spritesheet_auto(p + "spr_ArcherIdle_strip_NoBkg.png", frame_config=ENEMY_FRAME_CONFIG),
            "PATROL": load_spritesheet_auto(p + "spr_ArcherRun_strip_NoBkg.png", frame_config=ENEMY_FRAME_CONFIG),
            "CHASE": load_spritesheet_auto(p + "spr_ArcherRun_strip_NoBkg.png", frame_config=ENEMY_FRAME_CONFIG),
            "ATTACK": load_spritesheet_auto(p + "spr_ArcherAttack_strip_NoBkg.png", frame_config=ENEMY_FRAME_CONFIG),
            "DEAD": load_spritesheet_auto(p + "spr_ArcherDeath_strip_NoBkg.png", frame_config=ENEMY_FRAME_CONFIG)
        }
        self.image = self.animations["IDLE"][0]
        self.rect = self.image.get_rect(center=(x, y))
        self.attack_range = 350
        
        # Thêm biến tránh Crash nếu file rỗng
        for k in self.animations:
            if not self.animations[k]:
                self.animations[k] = [pygame.Surface((50,50), pygame.SRCALPHA)]

    def update(self, player_pos, enemy_bullets):
        if self.current_state == "DEAD":
            # Chỉ chạy cho đến hết animation chết
            if int(self.frame_index) < len(self.animations["DEAD"]) - 1:
                self.frame_index += self.animation_speed
                img = self.animations["DEAD"][int(self.frame_index)]
                self.image = pygame.transform.flip(img, True, False) if self.direction_x == -1 else img
            return
            
        dx = player_pos[0] - self.rect.centerx
        dy = player_pos[1] - self.rect.centery
        dist = math.hypot(dx, dy)
        
        self.direction_x = 1 if dx > 0 else -1
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            
        if dist < self.attack_range:
            self.current_state = "ATTACK"
            # Mỗi vòng animation bắn 1 mũi tên
            if self.attack_cooldown <= 0:
                self.attack_cooldown = 70 # Cooldown
                arrow = Arrow(self.rect.centerx, self.rect.centery, player_pos[0], player_pos[1])
                enemy_bullets.add(arrow)
        elif dist < 600:
            self.current_state = "CHASE"
            self.rect.x += (dx / dist) * self.run_speed
            self.rect.y += (dy / dist) * self.run_speed
        else:
            self.current_state = "IDLE"
            
        # Animate
        frames = self.animations[self.current_state]
        self.frame_index += self.animation_speed
        if self.frame_index >= len(frames): self.frame_index = 0
        img = frames[int(self.frame_index)]
        
        old_center = self.rect.center
        self.image = pygame.transform.flip(img, True, False) if self.direction_x == -1 else img
        self.rect = self.image.get_rect(center=old_center)


class CloseRanger(BaseEnemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.max_health = 120
        self.health = 120
        self.run_speed = 2.5
        p = "assets/graphics/Enemy close ranger/"
        self.animations = {
            "IDLE": load_spritesheet_auto(p + "spr_Idle_strip.png", frame_config=ENEMY_FRAME_CONFIG),
            "PATROL": load_spritesheet_auto(p + "spr_Walk_strip.png", frame_config=ENEMY_FRAME_CONFIG),
            "CHASE": load_spritesheet_auto(p + "spr_Walk_strip.png", frame_config=ENEMY_FRAME_CONFIG),
            "ATTACK": load_spritesheet_auto(p + "spr_Attack_strip.png", frame_config=ENEMY_FRAME_CONFIG),
            "DEAD": load_spritesheet_auto(p + "spr_Death_strip.png", frame_config=ENEMY_FRAME_CONFIG)
        }
        self.image = self.animations["IDLE"][0]
        self.rect = self.image.get_rect(center=(x, y))
        self.attack_range = 60
        
        for k in self.animations:
            if not self.animations[k]:
                self.animations[k] = [pygame.Surface((50,50), pygame.SRCALPHA)]

    def update(self, player_pos, dummy_bullets=None):
        if self.current_state == "DEAD":
            if int(self.frame_index) < len(self.animations["DEAD"]) - 1:
                self.frame_index += self.animation_speed
                img = self.animations["DEAD"][int(self.frame_index)]
                self.image = pygame.transform.flip(img, True, False) if self.direction_x == -1 else img
            return
            
        dx = player_pos[0] - self.rect.centerx
        dy = player_pos[1] - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.direction_x = 1 if dx > 0 else -1
        
        if dist < self.attack_range:
            self.current_state = "ATTACK"
        elif dist < 600:
            self.current_state = "CHASE"
            self.rect.x += (dx / dist) * self.run_speed
            self.rect.y += (dy / dist) * self.run_speed
        else:
            self.current_state = "IDLE"
            
        frames = self.animations[self.current_state]
        self.frame_index += self.animation_speed
        if self.frame_index >= len(frames): self.frame_index = 0
        img = frames[int(self.frame_index)]
        
        old_center = self.rect.center
        self.image = pygame.transform.flip(img, True, False) if self.direction_x == -1 else img
        self.rect = self.image.get_rect(center=old_center)


class Gatekeeper(BaseEnemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.max_health = 400
        self.health = 400
        self.run_speed = 1.0
        p = "assets/graphics/Gatekeeper/Necromancer/"
        self.animations = {
            "IDLE": load_spritesheet_auto(p + "Idle/spr_NecromancerIdle_strip50.png"),
            "PATROL": load_spritesheet_auto(p + "Walk/spr_NecromancerWalk_strip10.png"),
            "CHASE": load_spritesheet_auto(p + "Walk/spr_NecromancerWalk_strip10.png"),
            "ATTACK": load_spritesheet_auto(p + "Attack/spr_NecromancerAttackWithEffect_strip47.png"),
            "DEAD": load_spritesheet_auto(p + "Death/spr_NecromancerDeath_strip52.png")
        }
        self.image = self.animations["IDLE"][0]
        self.rect = self.image.get_rect(center=(x, y))
        self.is_hostile = False
        self.animation_speed = 0.4
        
        for k in self.animations:
            if not self.animations[k]:
                self.animations[k] = [pygame.Surface((50,50), pygame.SRCALPHA)]
        
    def update(self, player_pos, enemy_bullets=None, is_waiting=False):
        if not self.is_hostile or is_waiting:
            self.current_state = "IDLE"
        elif self.current_state == "DEAD":
            if int(self.frame_index) < len(self.animations["DEAD"]) - 1:
                self.frame_index += self.animation_speed
        else:
            # Boss chầm chậm đi tới
            dx = player_pos[0] - self.rect.centerx
            dy = player_pos[1] - self.rect.centery
            dist = math.hypot(dx, dy)
            self.direction_x = 1 if dx > 0 else -1
            
            if dist < 120:
                self.current_state = "ATTACK"
            else:
                self.current_state = "CHASE"
                if dist > 0:
                    self.rect.x += (dx / dist) * self.run_speed
                    self.rect.y += (dy / dist) * self.run_speed
                
        frames = self.animations[self.current_state]
        self.frame_index += self.animation_speed
        if self.frame_index >= len(frames): self.frame_index = 0
        img = frames[int(self.frame_index)]
        
        # Vẽ tâm đúng y gốc cũ
        old_center = self.rect.center
        self.image = pygame.transform.flip(img, True, False) if self.direction_x == -1 else img
        self.rect = self.image.get_rect(center=old_center)