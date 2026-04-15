import pygame
import random
from src.core.settings import *
from src.entities.player import Player
from src.entities.enemy import Gatekeeper, Archer, CloseRanger
from dialogue_game import dialogue_automaton

class Scene2:
    def __init__(self, scene_manager):
        self.scene_manager = scene_manager
        self.player = Player(400, 500)
        self.boss = Gatekeeper(400, 200)
        
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.gate = pygame.Rect(350, 20, 100, 50)
        
        # Trạng thái Màn chơi
        self.dialogue_active = False
        self.dialogue_finished = False
        self.current_dialogue_state = 'TRUNG_LAP'
        
        self.has_key = False
        self.key_dropped = False
        self.key_rect = pygame.Rect(400, 250, 20, 20)
        
        self.font = pygame.font.SysFont("tahoma", 20)
        self.big_font = pygame.font.SysFont("tahoma", 24, bold=True)
        self.dialogue_char_index = 0
        
        self.minions_spawned = False
        self.boss_defeated = False
        self.game_over_timer = 0

    def reset(self):
        self.player.rect.center = (400, 500)
        self.player.health = 100
        self.boss.health = 300
        self.boss.is_hostile = False
        self.boss.current_state = "PATROL"
        
        
        self.enemies.empty()
        self.bullets.empty()
        self.enemy_bullets.empty()
        
        self.dialogue_active = False
        self.dialogue_finished = False
        self.current_dialogue_state = 'TRUNG_LAP'
        self.dialogue_char_index = 0
        self.minions_spawned = False
        self.boss_defeated = False
        self.has_key = False
        self.key_dropped = False
        self.game_over_timer = 0

    def trigger_hostile(self):
        self.dialogue_active = False
        self.dialogue_finished = True
        self.boss.is_hostile = True
        # Gọi 6 lính ra ngẫu nhiên quanh boss
        if not self.minions_spawned:
            for _ in range(6):
                x = random.randint(50, 750)
                y = random.randint(100, 500)
                if random.choice([True, False]):
                    self.enemies.add(Archer(x, y))
                else:
                    self.enemies.add(CloseRanger(x, y))
            self.minions_spawned = True

    def _wrap_string(self, text, font, max_width):
        raw_lines = text.split('\n')
        wrapped_lines = []
        for r_line in raw_lines:
            words = r_line.split(' ')
            cur_line = ""
            for w in words:
                if not cur_line:
                    cur_line = w
                else:
                    test_line = cur_line + " " + w
                    if font.size(test_line)[0] <= max_width:
                        cur_line = test_line
                    else:
                        wrapped_lines.append(cur_line.strip())
                        cur_line = w
            if cur_line:
                wrapped_lines.append(cur_line.strip())
        return "\n".join(wrapped_lines)

    def update(self, events):
        # 0. Đang chờ Game Over
        if self.game_over_timer > 0:
            self.game_over_timer -= 1
            if self.game_over_timer <= 0:
                self.reset()
            return

        # 1. Nếu đang hội thoại -> Bỏ qua di chuyển
        if self.dialogue_active:
            state_data = dialogue_automaton[self.current_dialogue_state]
            
            # Khởi tạo Text Wrap
            if getattr(self, 'wrapped_text_current_state', None) != self.current_dialogue_state:
                self.wrapped_text_cache = self._wrap_string(state_data['mo_ta'], self.big_font, 660)
                self.wrapped_text_current_state = self.current_dialogue_state
                
            full_text = self.wrapped_text_cache
            is_typing_finished = self.dialogue_char_index >= len(full_text)
            
            # Chạy chữ nếu chưa xong
            if not is_typing_finished:
                self.dialogue_char_index += 0.5
                
            for event in events:
                if event.type == pygame.KEYDOWN:
                    # BLOCK Input nếu chữ Tùy chọn chưa hiển thị (chữ chưa chạy xong)
                    if is_typing_finished:
                        options = state_data.get('options', {})
                        pressed_key = pygame.key.name(event.key)
                        
                        if pressed_key in options:
                            next_state = options[pressed_key][1]
                            self.current_dialogue_state = next_state
                            self.dialogue_char_index = 0 # Trả chữ chạy về 0
                            
                            # Kiểm tra xem có phải trạng thái cuối?
                            if dialogue_automaton[next_state]['is_final']:
                                if next_state == 'CHO_PHEP_QUA':
                                    self.dialogue_active = False
                                    self.dialogue_finished = True
                                    self.key_dropped = True
                                elif next_state == 'TRUC_XUAT':
                                    self.trigger_hostile()
            return # Khóa Update

        # 2. Cập nhật Player & Xử lý Tấn công của Player
        self.player.update()
        
        # Player đánh quái
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Chuột trái -> Bắn đạn
                    self.player.attack(self.bullets, is_melee=False)
                elif event.button == 3:
                    # Chuột phải -> Chém cận chiến
                    self.player.attack(self.bullets, is_melee=True)
                    attack_rect = self.player.get_attack_rect()
                    # Sát thương cận chiến lan tỏa (Area of Effect) - dùng hitbox bé hơn cho quái
                    for enemy in self.enemies:
                        if enemy.current_state != "DEAD" and enemy.rect.inflate(-160, -100).colliderect(attack_rect):
                            enemy.take_damage(40) # Cận chiến dame to hơn
                    
                    is_waiting = any(e.current_state != "DEAD" for e in self.enemies)
                    if self.boss.is_hostile and self.boss.current_state != "DEAD" and self.boss.rect.inflate(-100, -80).colliderect(attack_rect) and not is_waiting:
                        self.boss.take_damage(50)
                
        self.bullets.update()
        
        # Xử lý đạn trúng đích
        for bullet in list(self.bullets):
            hit_something = False
            # Trúng lính
            for enemy in self.enemies:
                if enemy.current_state != "DEAD" and enemy.rect.inflate(-160, -100).colliderect(bullet.rect):
                    enemy.take_damage(15) # Giảm dame đạn xuống 15
                    hit_something = True
                    break
            
            # Trúng Boss chỉ khi hết lính
            is_waiting = any(e.current_state != "DEAD" for e in self.enemies)
            if not hit_something and self.boss.is_hostile and self.boss.current_state != "DEAD" and not is_waiting and self.boss.rect.inflate(-100, -80).colliderect(bullet.rect):
                self.boss.take_damage(20) # Giảm dame đạn xuống 20
                hit_something = True
                
            if hit_something:
                self.bullets.remove(bullet)

        # 3. Cập nhật Boss liên tục
        if self.boss.is_hostile:
            # Boss đứng chờ nếu còn lính SỐNG (kể cả lính đang diễn cảnh chết chưa xóa hẳn)
            is_waiting = any(e.current_state != "DEAD" for e in self.enemies)
            self.boss.update(self.player.rect.center, self.enemy_bullets, is_waiting=is_waiting)
            
            if self.boss.current_state == "DEAD" and not self.key_dropped:
                self.key_dropped = True
                self.boss_defeated = True
                self.key_rect.center = self.boss.rect.center
                
        # Cập nhật tụi lính và kẻ địch trừ máu player (Đơn giản hóa)
        for enemy in list(self.enemies):
            enemy.update(self.player.rect.center, self.enemy_bullets)
            if enemy.current_state == "DEAD":
                if int(enemy.frame_index) >= len(enemy.animations["DEAD"]) - 1:
                    self.enemies.remove(enemy) # Animation chết chạy xong thì bốc hơi
            elif enemy.current_state == "ATTACK" and enemy.rect.inflate(-160, -100).colliderect(self.player.rect):
                self.player.health -= 0.1 # Địch cắn mất 0.1HP/frame
                
        if self.boss.current_state == "ATTACK" and self.boss.rect.inflate(-100, -80).colliderect(self.player.rect):
            self.player.health -= 0.2 # Boss cắn 0.2HP/frame (~ 12HP/s)

        self.enemy_bullets.update()
        for arrow in list(self.enemy_bullets):
            # Nhỏ hitbox đạn lại tí để né sát nút
            if arrow.rect.inflate(-5, -5).colliderect(self.player.rect):
                self.player.health -= 5 # Đạn tiễn của cung thủ trừ 5 máu
                self.enemy_bullets.remove(arrow)

        if self.player.health <= 0 and self.game_over_timer <= 0:
            # Game Over và Reset (Hẹn 120 frames sau Reset)
            self.game_over_timer = 120
            return

        # 4. Kích hoạt hội thoại khi lại gần
        if not self.dialogue_finished and not self.boss.is_hostile:
            dist_to_boss = self.player.rect.colliderect(self.boss.rect.inflate(100, 100))
            if dist_to_boss:
                self.dialogue_active = True

        # 5. Nhặt chìa khóa
        if self.key_dropped and not self.has_key:
            if self.player.rect.colliderect(self.key_rect):
                self.has_key = True

        # 6. Vào cổng khi có chìa
        if self.has_key and self.player.rect.colliderect(self.gate):
            self.scene_manager.switch_scene("Scene3")


    def draw(self, screen):
        screen.fill((40, 40, 40)) # Nền đền tối
        
        # Cổng
        gate_color = (0, 255, 0) if self.has_key else (150, 0, 0)
        pygame.draw.rect(screen, gate_color, self.gate)
        gate_text = self.font.render("GATE", True, BLACK)
        screen.blit(gate_text, (self.gate.x + 25, self.gate.y + 15))

        # Boss & lính
        if self.boss.current_state != "DEAD":
            screen.blit(self.boss.image, self.boss.rect)
            if self.boss.is_hostile:
                self.boss.draw_health_bar(screen)
            
        self.enemies.draw(screen)
        for enemy in self.enemies:
            enemy.draw_health_bar(screen)
            
        self.bullets.draw(screen)
        self.enemy_bullets.draw(screen)

        # Chìa khóa
        if self.key_dropped and not self.has_key:
            pygame.draw.rect(screen, (255, 215, 0), self.key_rect) # Màu vàng gold

        # Player
        self.player.draw(screen)

        # Máu Player
        hp_text = self.font.render(f"HP: {int(self.player.health)}", True, GREEN)
        screen.blit(hp_text, (20, 20))
        
        # Máu Boss
        is_waiting = any(e.current_state != "DEAD" for e in self.enemies)
        if self.boss.is_hostile and self.boss.current_state != "DEAD" and not is_waiting:
            boss_hp = self.font.render(f"BOSS HP: {self.boss.health}", True, RED)
            screen.blit(boss_hp, (400, 20))

        # Khung Hội thoại
        if self.dialogue_active:
            self.draw_dialogue(screen)
            
        # Màn hình Game Over
        if self.game_over_timer > 0:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            death_text = self.big_font.render("THẤT BẠI! BẠN ĐÃ CHẾT", True, RED)
            screen.blit(death_text, (SCREEN_WIDTH//2 - 130, SCREEN_HEIGHT//2 - 20))

    def draw_dialogue(self, screen):
        # Vẽ Box (Mở rộng cho cao hơn)
        box_rect = pygame.Rect(50, 350, 700, 230)
        pygame.draw.rect(screen, (20, 20, 50), box_rect)
        pygame.draw.rect(screen, WHITE, box_rect, 3)
        
        state_data = dialogue_automaton[self.current_dialogue_state]
        
        # Lấy văn bản đã được wrap từ cache
        full_text = getattr(self, 'wrapped_text_cache', state_data['mo_ta'])
        current_text = full_text[:int(self.dialogue_char_index)]
        lines = current_text.split('\n')
        
        y_text = 370
        for line in lines:
            if line:
                desc_surf = self.big_font.render(line, True, (200, 200, 255))
                screen.blit(desc_surf, (70, y_text))
            y_text += 30
            
        # Tính vị trí vẽ các Options (Bên dưới dòng description cuối cùng xíu)
        total_lines = len(full_text.split('\n'))
        y_offset = 370 + total_lines * 30 + 10
        
        # Chỉ khi chữ chạy xong mới vẽ Option menu
        if self.dialogue_char_index >= len(full_text):
            options = state_data.get('options', {})
            for key, (text, next_st) in options.items():
                opt_surf = self.font.render(f"[{key}] {text[:70]}", True, WHITE)
                screen.blit(opt_surf, (70, y_offset))
                y_offset += 30
                
            hint_surf = self.font.render("Nhấn chữ số (1, 2, 3...) tương ứng trên bàn phím để trả lời!", True, (255, 100, 100))
            screen.blit(hint_surf, (70, 550))
