import pygame
import math
import random
from Modules.spriteSheet import SpriteSheet
from Modules.font_manager import get_font

class Dragon:
    def __init__(self, x, y, w=160, h=160):
        # Propriétés de base
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.enemy_type = "Dragon"
        self.name = "PYROFLAMME"
        self.start_x = x
        self.start_y = y
        self.is_enemy = True
        self.is_hazard = False
        self.collide = False
        self.topoffset = 30
        self.xoffset = 40
        self.collectable = False
        self.last_y = y
        self.gs = 0
        self.ignores_terrain = True
        
        # Propriétés du boss
        self.max_health = 15
        self.health = self.max_health
        self.is_boss = True
        self.is_alive = True
        self.is_dying = False
        
        # Animation
        self.animation_state = 0
        self.delay = 6
        self.curr_delay = 0
        
        # Mouvement
        self.direction = "RIGHT"
        self.sprite_direction = "RIGHT"
        self.max_speed = 2.4
        self.current_speed_x = 0
        self.current_speed_y = 0
        self.acceleration = 0.16
        self.deceleration = 0.15
        self.direction_change_cooldown = 0
        self.direction_change_delay = 30
        
        # Paramètres de vol
        self.target_y = y
        self.target_y_offset = 25
        self.max_vertical_speed = 1.8
        
        # Propriétés d'attaque
        self.is_attacking = False
        self.attack_state = 0
        self.attack_delay = 16
        self.attack_curr_delay = 0
        self.attack_cooldown = 0
        self.attack_cooldown_max = 180
        self.attack_range = 180
        self.attack_damage = 1
        
        # Suivi du joueur
        self.player_x = 0
        self.player_y = 0
        self.player_distance = 1000
        self.player_damage_cooldown = 0
        self.player_damage_cooldown_max = 90
        self.detection_range = 600
        
        # Dégâts et mort
        self.is_hit = False
        self.hit_state = 0
        self.hit_delay = 4
        self.hit_curr_delay = 0
        self.hit_cooldown = 0
        self.hit_cooldown_max = 20
        self.death_state = 0
        self.death_delay = 8
        self.death_curr_delay = 0
        self.hit_movement_penalty = 0.3
        
        # Comportement de repli
        self.is_retreating = False
        self.retreat_timer = 0
        self.retreat_duration = 45
        self.retreat_speed_boost = 1.4
        
        # Limites de la carte
        self.map_width = 5000
        self.map_height = 2000
        self.min_x = 10
        self.min_y = 10

        self.died_completely = False
        
        self.load_animations()
    
    def load_animations(self):
        animations_to_load = {
            'flying': {'path': "./Assets/Enemies/Dragon/flying.png", 'attr': 'animation'},
            'attack': {'path': "./Assets/Enemies/Dragon/attack.png", 'attr': 'attack_frames'},
            'hit': {'path': "./Assets/Enemies/Dragon/hit.png", 'attr': 'hit_frames'},
            'dying': {'path': "./Assets/Enemies/Dragon/dying.png", 'attr': 'death_frames'}
        }
        
        for anim_name, info in animations_to_load.items():
            try:
                sheet = SpriteSheet(pygame.image.load(info['path']))
                surface = sheet.ss
                frame_width = 192
                frame_count = surface.get_width() // frame_width
                frames = []
                for i in range(frame_count):
                    frame = sheet.getimage(i * frame_width, 0, frame_width, 192)
                    frame = pygame.transform.scale(frame, (self.w, self.h))
                    frames.append(frame)
                setattr(self, info['attr'], frames)
            except Exception as e:
                print(f"Failed to load {anim_name} animation: {e}")
                fallback_frames = 4
                color = (220, 60, 0)
                setattr(self, info['attr'], self.create_default_animation(color, fallback_frames))
    
    def create_default_animation(self, color, frames):
        frames_list = []
        for i in range(frames):
            frame = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            pygame.draw.ellipse(frame, color, (self.w//4, self.h//4, self.w//2, self.h//2))
            frames_list.append(frame)
        return frames_list
    
    def update(self, keys, player=None, objects=None):
        if not self.is_alive:
            if self.is_dying:
                self.update_death_animation()
            return
        
        if objects and self.map_width == 5000:
            for obj in objects:
                if hasattr(obj, 'x') and hasattr(obj, 'w'):
                    self.map_width = max(self.map_width, obj.x + obj.w + 100)
                if hasattr(obj, 'y') and hasattr(obj, 'h'):
                    self.map_height = max(self.map_height, obj.y + obj.h + 100)
        
        if self.direction_change_cooldown > 0:
            self.direction_change_cooldown -= 1
            
        if self.is_retreating:
            self.retreat_timer -= 1
            if self.retreat_timer <= 0:
                self.is_retreating = False
        
        if player and not player.is_dying:
            self.player_x = player.x + player.w / 2
            self.player_y = player.y + player.h / 2
            
            dx = self.player_x - (self.x + self.w / 2)
            dy = (self.player_y - self.target_y_offset) - (self.y + self.h / 2)
            
            self.player_distance = math.sqrt(dx*dx + dy*dy)
            
            new_direction = "LEFT" if dx > 0 else "RIGHT"
            if new_direction != self.sprite_direction and self.direction_change_cooldown <= 0:
                self.sprite_direction = new_direction
                self.direction_change_cooldown = self.direction_change_delay
            
            if (self.player_distance < self.attack_range and 
                not self.is_attacking and 
                not self.is_retreating and
                self.attack_cooldown <= 0 and
                not self.is_hit and
                random.random() < 0.8):  # 20% chance de ne pas attaquer même si à portée
                self.is_attacking = True
                self.attack_state = 0
                self.attack_curr_delay = 0
            
            speed_multiplier = self.hit_movement_penalty if self.is_hit else 1.0
            
            if self.is_retreating:
                dx = -dx * self.retreat_speed_boost
                dy = -(dy + 100)
            
            target_speed_x = 0
            if abs(dx) > 10:
                if self.player_distance < self.detection_range or self.is_retreating:
                    target_multiplier = speed_multiplier
                    if self.is_retreating:
                        target_multiplier *= self.retreat_speed_boost
                    
                    target_speed_x = math.copysign(self.max_speed * target_multiplier, dx)
                    self.direction = "RIGHT" if dx > 0 else "LEFT"
            
            if self.is_attacking and self.attack_state > 0:
                target_speed_x *= 0.2
            
            if abs(self.current_speed_x - target_speed_x) > self.acceleration:
                if self.current_speed_x < target_speed_x:
                    self.current_speed_x += self.acceleration * speed_multiplier
                else:
                    self.current_speed_x -= self.acceleration * speed_multiplier
            else:
                self.current_speed_x = target_speed_x
            
            target_speed_y = 0
            
            if self.is_retreating:
                if dy < 0:
                    target_speed_y = -self.max_vertical_speed * 1.2
                else:
                    target_speed_y = min(dy * 0.1, self.max_vertical_speed)
            else:
                if dy > 30:
                    target_speed_y = min(dy * 0.1, self.max_vertical_speed) * speed_multiplier
                elif dy < -5:
                    target_speed_y = max(dy * 0.1, -self.max_vertical_speed) * speed_multiplier
                else:
                    target_speed_y = self.current_speed_y * 0.9
            
            if self.is_attacking and self.attack_state > 0:
                target_speed_y *= 0.2
            
            if abs(self.current_speed_y - target_speed_y) > self.acceleration:
                if self.current_speed_y < target_speed_y:
                    self.current_speed_y += self.acceleration * speed_multiplier
                else:
                    self.current_speed_y -= self.acceleration * speed_multiplier
            else:
                self.current_speed_y = target_speed_y
            
            new_x = self.x + self.current_speed_x
            if new_x > self.min_x and new_x + self.w < self.map_width:
                self.x = new_x
            else:
                self.current_speed_x = 0
            
            new_y = self.y + self.current_speed_y
            if new_y > self.min_y and new_y + self.h < self.map_height:
                self.y = new_y
            else:
                self.current_speed_y = 0
        else:
            if random.random() < 0.005 and self.direction_change_cooldown <= 0:
                self.direction = "RIGHT" if random.random() < 0.5 else "LEFT"
                self.direction_change_cooldown = self.direction_change_delay
            
            target_speed_x = self.max_speed * 0.5 if self.direction == "RIGHT" else -self.max_speed * 0.5
            
            if self.is_hit:
                target_speed_x *= self.hit_movement_penalty
            
            if abs(self.current_speed_x - target_speed_x) > self.acceleration:
                if self.current_speed_x < target_speed_x:
                    self.current_speed_x += self.acceleration
                else:
                    self.current_speed_x -= self.acceleration
            else:
                self.current_speed_x = target_speed_x
            
            new_x = self.x + self.current_speed_x
            if new_x > self.min_x and new_x + self.w < self.map_width:
                self.x = new_x
                if self.direction_change_cooldown <= 0:
                    self.sprite_direction = self.direction
            else:
                self.direction = "LEFT" if self.direction == "RIGHT" else "RIGHT"
                self.current_speed_x = 0
            
            base_y = self.start_y - 75
            if self.y < base_y - 5:
                self.current_speed_y = min(self.current_speed_y + self.acceleration, self.max_vertical_speed * 0.5)
            elif self.y > base_y + 5:
                self.current_speed_y = max(self.current_speed_y - self.acceleration, -self.max_vertical_speed * 0.5)
            else:
                if abs(self.current_speed_y) > self.deceleration:
                    self.current_speed_y *= 0.9
                else:
                    self.current_speed_y = 0
            
            self.y += self.current_speed_y
        
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1
        if self.player_damage_cooldown > 0:
            self.player_damage_cooldown -= 1
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        self.update_animations()
        
        if self.is_attacking and self.attack_state == 1:
            if player and self.player_damage_cooldown <= 0:
                if self.player_distance < self.attack_range:
                    player.lose_heart(None)
                    self.reset_player_damage_cooldown()
        
        self.last_y = self.y
    
    def update_animations(self):
        if self.is_hit:
            if self.hit_curr_delay >= self.hit_delay:
                self.hit_state += 1
                self.hit_curr_delay = 0
                if self.hit_state >= len(self.hit_frames):
                    self.is_hit = False
                    self.hit_state = 0
            else:
                self.hit_curr_delay += 1
        elif self.is_attacking:
            if self.attack_curr_delay >= self.attack_delay:
                self.attack_state += 1
                self.attack_curr_delay = 0
                if self.attack_state >= len(self.attack_frames):
                    self.is_attacking = False
                    self.attack_state = 0
                    self.attack_cooldown = self.attack_cooldown_max
            else:
                self.attack_curr_delay += 1
        else:
            if self.curr_delay >= self.delay:
                self.animation_state = (self.animation_state + 1) % len(self.animation)
                self.curr_delay = 0
            else:
                self.curr_delay += 1
    
    def update_death_animation(self):
        if self.death_curr_delay >= self.death_delay:
            self.death_state += 1
            self.death_curr_delay = 0
            if self.death_state >= len(self.death_frames):
                self.is_dying = False
                self.died_completely = True
        else:
            self.death_curr_delay += 1
    
    def draw(self, display):
        if not self.is_alive and not self.is_dying:
            return
        
        if self.is_dying:
            frame = self.death_frames[min(self.death_state, len(self.death_frames)-1)]
        elif self.is_hit:
            frame = self.hit_frames[min(self.hit_state, len(self.hit_frames)-1)]
        elif self.is_attacking:
            frame = self.attack_frames[min(self.attack_state, len(self.attack_frames)-1)]
        else:
            frame = self.animation[self.animation_state]
        
        if self.sprite_direction != "RIGHT":
            frame = pygame.transform.flip(frame, True, False)
        
        display.blit(frame, (self.x, self.y))
    
    def draw_boss_bar(self, display):
        if not self.is_alive and not self.is_dying:
            return
            
        bar_width = 250
        bar_height = 24
        margin = 20
        x_pos = display.get_width() - bar_width - margin
        y_pos = margin
        
        bar_bg = (30, 30, 30)
        bar_border = (10, 112, 48)
        text_color = (255, 255, 255)
        
        health_percent = max(0, self.health / self.max_health)
        if health_percent > 0.6:
            health_color = (50, 180, 80)
        elif health_percent > 0.3:
            health_color = (230, 180, 50)
        else:
            health_color = (230, 60, 60)
        
        bg_rect = pygame.Rect(x_pos - 10, y_pos - 10, bar_width + 20, bar_height + 40)
        pygame.draw.rect(display, (20, 70, 45), bg_rect, 0, 10)
        pygame.draw.rect(display, bar_border, bg_rect, 2, 10)
        
        try:
            font = get_font('bold', 'small')
        except:
            font = pygame.font.SysFont("Arial", 18, bold=True)
        
        name_text = font.render(self.name, True, text_color)
        display.blit(name_text, (x_pos + (bar_width - name_text.get_width()) // 2, y_pos - 5))
        
        pygame.draw.rect(display, bar_bg, (x_pos, y_pos + 20, bar_width, bar_height), 0, 6)
        health_width = int(bar_width * health_percent)
        if health_width > 0:
            pygame.draw.rect(display, health_color, (x_pos, y_pos + 20, health_width, bar_height), 0, 6)
        
        health_text = font.render(f"{max(0, int(health_percent * 100))}%", True, text_color)
        display.blit(health_text, (x_pos + (bar_width - health_text.get_width()) // 2,
                                   y_pos + 20 + (bar_height - health_text.get_height()) // 2))
    
    def take_damage(self, damage):
        if self.hit_cooldown <= 0 and self.is_alive and not self.is_dying:
            self.health -= damage
            self.hit_cooldown = self.hit_cooldown_max
            self.is_hit = True
            self.hit_state = 0
            self.hit_curr_delay = 0
            
            self.is_retreating = True
            self.retreat_timer = self.retreat_duration
            
            self.current_speed_x *= 0.5
            self.current_speed_y *= 0.5
            
            if self.health <= 0:
                self.health = 0
                self.start_dying()
            return True
        return False
        
    def start_dying(self):
        self.is_alive = False
        self.is_dying = True
        self.death_state = 0
        self.death_curr_delay = 0
        
    def can_damage_player(self):
        if self.is_attacking and self.attack_state > 0:
            return self.player_damage_cooldown <= 0
            
        return False
        
    def reset_player_damage_cooldown(self):
        self.player_damage_cooldown = self.player_damage_cooldown_max
        
    def check_ledge_ahead(self, objects):
        pass