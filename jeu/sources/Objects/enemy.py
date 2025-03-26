import pygame
from Modules.spriteSheet import SpriteSheet

class Enemy:
    def __init__(self, x, y, w=48, h=48, enemy_type="FireMonster"):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.enemy_type = enemy_type
        
        self.initial_frames = 5
        
        # Mouvement
        self.direction = "LEFT"
        self.sprite_direction = "LEFT"
        self.speed = 1.5
        self.last_x = x
        self.last_y = y
        
        # Système de gravité
        self.maxG = 15
        self.currG = 0
        self.gAcc = 0.5
        self.isOnGround = False
        
        # État au sol
        self.gs = 0
        
        # Santé et dégâts
        self.max_health = 3
        self.health = self.max_health
        self.is_alive = True
        self.hit_cooldown = 0
        self.hit_cooldown_max = 30
        
        # Animation de dégât
        self.is_hit = False
        self.hit_animation_state = 0
        self.hit_delay = 5
        self.hit_current_delay = 0
        
        # Animation de mort
        self.is_dying = False
        self.death_animation_state = 0
        self.death_delay = 8
        self.death_current_delay = 0
        
        # Attributs de collision
        self.collide = True
        self.is_enemy = True
        self.topoffset = 0
        self.xoffset = 0
        self.collectable = False
        
        # États de mouvement
        self.blocked_left = False
        self.blocked_right = False
        self.ledge_check_distance = 20
        
        # Temps de recharge pour dégâts au joueur
        self.player_damage_cooldown = 0
        self.player_damage_cooldown_max = 60
        
        # Animation
        self.animation_state = 0
        self.delay = 8
        self.currDelay = 0
        
        # Chargement des animations de course
        try:
            sprite_sheet = SpriteSheet(pygame.image.load(f"./Assets/Enemies/{self.enemy_type}/run.png"))
            self.animation_length = 8
            self.animation = [sprite_sheet.getimage(8*x, 0, 8, 8) for x in range(self.animation_length)]
            
            # Redimensionnement des images
            for x in range(len(self.animation)):
                self.animation[x] = pygame.transform.scale(self.animation[x], (self.w, self.h))
        except Exception as e:
            print(f"Échec du chargement de l'animation: {e}")
            raise Exception("Échec du chargement de l'animation")
            
        # Chargement des animations de dégât
        try:
            hit_sheet = SpriteSheet(pygame.image.load(f"./Assets/Enemies/{self.enemy_type}/hit.png"))
            self.hit_frames = 4
            self.hit_animation = [hit_sheet.getimage(8*x, 0, 8, 8) for x in range(self.hit_frames)]
            
            for x in range(len(self.hit_animation)):
                self.hit_animation[x] = pygame.transform.scale(self.hit_animation[x], (self.w, self.h))
        except Exception as e:
            print(f"Échec du chargement de l'animation de dégât: {e}")
            # Animation de secours
            self.hit_frames = 4
            self.hit_animation = []
            for i in range(4):
                hit_frame = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
                hit_frame.fill((255, 100, 100, 255 - i*40))
                self.hit_animation.append(hit_frame)
            
        # Chargement des animations de mort
        try:
            death_sheet = SpriteSheet(pygame.image.load(f"./Assets/Enemies/{self.enemy_type}/dying.png"))
            self.death_frames = 4
            self.death_animation = [death_sheet.getimage(8*x, 0, 8, 8) for x in range(self.death_frames)]
            
            for x in range(len(self.death_animation)):
                self.death_animation[x] = pygame.transform.scale(self.death_animation[x], (self.w, self.h))
        except Exception as e:
            print(f"Échec du chargement de l'animation de mort: {e}")
            # Animation de secours
            self.death_frames = 4
            self.death_animation = []
            for i in range(4):
                death_frame = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
                alpha = 255 - (i * 60)
                death_frame.fill((255, 0, 0, max(0, alpha)))
                self.death_animation.append(death_frame)
                
        # Direction initiale du sprite
        self.sprite_direction = "RIGHT" if self.direction == "LEFT" else "LEFT"
    
    def draw(self, display):
        if not self.is_alive and not self.is_dying:
            return
            
        # Animation de mort
        if self.is_dying:
            frame = min(self.death_animation_state, len(self.death_animation) - 1)
            if self.sprite_direction == "RIGHT":
                display.blit(self.death_animation[frame], (self.x, self.y))
            else:
                display.blit(pygame.transform.flip(self.death_animation[frame], True, False), (self.x, self.y))
            
            if self.death_current_delay >= self.death_delay:
                self.death_animation_state += 1
                self.death_current_delay = 0
                if self.death_animation_state >= len(self.death_animation):
                    self.is_dying = False
            else:
                self.death_current_delay += 1
                
            return
        
        # Animation de dégât    
        if self.is_hit:
            frame = min(self.hit_animation_state, len(self.hit_animation) - 1)
            if self.sprite_direction == "RIGHT":
                display.blit(self.hit_animation[frame], (self.x, self.y))
            else:
                display.blit(pygame.transform.flip(self.hit_animation[frame], True, False), (self.x, self.y))
            
            if self.hit_current_delay >= self.hit_delay:
                self.hit_animation_state += 1
                self.hit_current_delay = 0
                if self.hit_animation_state >= len(self.hit_animation):
                    self.is_hit = False
            else:
                self.hit_current_delay += 1
                
            return
            
        # Animation normale
        if self.sprite_direction == "RIGHT":
            display.blit(self.animation[self.animation_state % self.animation_length], (self.x, self.y))
        else:
            display.blit(pygame.transform.flip(self.animation[self.animation_state % self.animation_length], True, False), (self.x, self.y))
        
        if self.currDelay >= self.delay:
            self.animation_state += 1
            self.currDelay = 0
        else:
            self.currDelay += 1
    
    def check_ledge_ahead(self, objects):
        """Détection des bords"""
        if not self.isOnGround:
            return

        check_x = 0
        if self.direction == "RIGHT":
            check_x = self.x + self.w + 2
        else:
            check_x = self.x - 2

        check_y = self.y + self.h + 5

        has_ground = False
        for obj in objects:
            if obj != self and hasattr(obj, 'collide') and obj.collide and not hasattr(obj, 'is_enemy'):
                if (check_x >= obj.x and check_x <= obj.x + obj.w and
                    check_y >= obj.y and check_y <= obj.y + obj.h):
                    has_ground = True
                    break
                
        if not has_ground:
            if self.direction == "RIGHT":
                self.direction = "LEFT"
                self.sprite_direction = "RIGHT"
            else:
                self.direction = "RIGHT"
                self.sprite_direction = "LEFT"
    
    def reverse_direction(self):
        """Inversion de direction"""
        if self.direction == "RIGHT":
            self.direction = "LEFT"
        else:
            self.direction = "RIGHT"
            
        self.sprite_direction = "RIGHT" if self.direction == "LEFT" else "LEFT"
    
    def update(self, keys):
        if not self.is_alive:
            return

        if self.is_dying:
            return

        self.last_x = self.x
        self.last_y = self.y

        if self.direction == "RIGHT":
            self.x += self.speed
        else:
            self.x -= self.speed

        if not self.isOnGround:
            if self.currG <= self.maxG:
                self.currG += self.gAcc
            self.y += self.currG
        else:
            self.currG = 0

        if self.gs != 0:
            self.isOnGround = True
        else:
            self.isOnGround = False
        self.gs = 0

        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1

        if self.player_damage_cooldown > 0:
            self.player_damage_cooldown -= 1
    
    def take_damage(self, damage):
        """Prise de dégâts"""
        if self.hit_cooldown == 0 and self.is_alive and not self.is_dying:
            self.health -= damage
            self.hit_cooldown = self.hit_cooldown_max
            
            self.is_hit = True
            self.hit_animation_state = 0
            self.hit_current_delay = 0
            
            if self.health <= 0:
                self.start_dying()
            
            return True
        return False
    
    def start_dying(self):
        """Démarrage de l'animation de mort"""
        self.is_alive = False
        self.is_dying = True
        self.death_animation_state = 0
        self.death_current_delay = 0
        
    def can_damage_player(self):
        """Vérification si l'ennemi peut infliger des dégâts au joueur"""
        return self.player_damage_cooldown == 0 and self.is_alive and not self.is_dying
        
    def reset_player_damage_cooldown(self):
        """Réinitialisation du temps de recharge après avoir infligé des dégâts"""
        self.player_damage_cooldown = self.player_damage_cooldown_max