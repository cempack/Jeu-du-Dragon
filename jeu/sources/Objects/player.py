import pygame
from Modules.spriteSheet import SpriteSheet


class Player:
    def __init__(self, x, y, w, h, character_type="Knight"):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.delay = 5
        self.currDelay = 0
        self.character_type = character_type

        # Mouvement horizontal
        self.speed = 0
        self.maxSpeed = 5
        self.acc = 0.4

        # Mouvement vertical
        self.maxG = 100
        self.currG = 0
        self.gAcc = 0.5
        self.isOnGround = False

        self.jumpVel = 0
        self.jumpMax = 15
        self.min_visible_y = 0

        # Variables de saut
        self.jump_cooldown = 0
        self.jump_cooldown_max = 10
        self.jump_sound_played = False
        self.double_jump_sound_played = False
        
        # Double saut
        self.canDoubleJump = False
        self.doubleJumpActive = False
        self.prev_jump_pressed = False

        # Collisions
        self.last_y = y
        self.gs = 0

        # Système de vie
        self.max_hearts = 3
        self.current_hearts = 3
        self.invincible = False
        self.invincible_timer = 0
        self.invincible_duration = 60
        
        # État de mort
        self.is_dying = False
        self.dying_state = 0
        self.dying_delay = 8
        self.dying_current_delay = 0
        self.respawn_after_death = False

        # Variables d'attaque
        self.is_attacking = False
        self.attack_state = 0
        self.attack_delay = 5
        self.attack_current_delay = 0
        self.attack_cooldown = 0
        self.attack_damage = 1

        # Animation de dégâts
        self.is_hit = False
        self.hit_state = 0
        self.hit_delay = 5
        self.hit_current_delay = 0

        self.ignore_current_jump_press = False

        # Stats spécifiques au personnage
        self.setup_character_stats()

        # Sprites
        self.state = "IDLE_RIGHT"
        self.pastState = "RUN_RIGHT"
        self.facing_right = True

        self.idle_state = 0
        player_idle = SpriteSheet(pygame.image.load(f"./Assets/Characters/{self.character_type}/idle.png"))
        self.idle = self.load_animation_frames(player_idle, 32, 32)

        self.run_state = 0
        player_run = SpriteSheet(pygame.image.load(f"./Assets/Characters/{self.character_type}/run.png"))
        self.run = self.load_animation_frames(player_run, 32, 32)
            
        self.doublejump_state = 0
        player_doublejump = SpriteSheet(pygame.image.load(f"./Assets/Characters/{self.character_type}/double_jump.png"))
        self.doublejump = self.load_animation_frames(player_doublejump, 32, 32)

        self.player_jump = pygame.transform.scale(pygame.image.load(f"./Assets/Characters/{self.character_type}/jump.png"), (80, 80))
        self.player_fall = pygame.transform.scale(pygame.image.load(f"./Assets/Characters/{self.character_type}/fall.png"), (80, 80))

        # Chargement des animations d'attaque
        try:
            player_attack = SpriteSheet(pygame.image.load(f"./Assets/Characters/{self.character_type}/attack.png"))
            self.attack_frames = self.load_animation_frames(player_attack, 32, 32)
        except Exception as e:
            print(f"Impossible de charger l'animation d'attaque pour {self.character_type}: {e}")
            self.attack_frames = [self.idle[0]] * 4

        # Chargement des animations de dégâts
        try:
            player_hit = SpriteSheet(pygame.image.load(f"./Assets/Characters/{self.character_type}/hit.png"))
            self.hit_frames = self.load_animation_frames(player_hit, 32, 32)
        except Exception as e:
            print(f"Impossible de charger l'animation de dégâts pour {self.character_type}: {e}")
            self.hit_frames = [self.idle[0]] * 2

        # Chargement des animations de mort
        try:
            player_dying = SpriteSheet(pygame.image.load(f"./Assets/Characters/{self.character_type}/dying.png"))
            self.dying = self.load_animation_frames(player_dying, 32, 32)
        except Exception as e:
            print(f"Impossible de charger l'animation de mort pour {self.character_type}: {e}")
            self.dying = [self.idle[0]] * 4

    def load_animation_frames(self, spritesheet, frame_width, frame_height):
        surface = spritesheet.ss
        sheet_width = surface.get_width()
        frame_count = sheet_width // frame_width
        
        frames = [spritesheet.getimage(frame_width * x, 0, frame_width, frame_height) for x in range(frame_count)]
        
        for i in range(len(frames)):
            frames[i] = pygame.transform.scale(frames[i], (80, 80))
            
        return frames

    def setup_character_stats(self):
        self.attack_delay = 5
    
        if self.character_type == "Knight":
            self.attack_cooldown_max = 50
            self.maxSpeed = 4
            self.attack_damage = 2
            self.attack_range = 50
            self.attack_width = self.h - 20
            self.attack_vertical_offset = 10
        elif self.character_type == "Archer":
            self.attack_cooldown_max = 30
            self.maxSpeed = 5
            self.attack_damage = 1.2
            self.attack_range = 140
            self.attack_width = 30
            self.attack_vertical_offset = 25
            self.attack_delay = 3
        elif self.character_type == "Assassin":
            self.attack_cooldown_max = 20
            self.maxSpeed = 6
            self.attack_damage = 1.6
            self.attack_range = 40
            self.attack_width = self.h - 25
            self.attack_vertical_offset = 15
        elif self.character_type == "Mage":
            self.attack_cooldown_max = 40
            self.maxSpeed = 4.5
            self.attack_damage = 1.8
            self.attack_range = 110
            self.attack_width = 50
            self.attack_vertical_offset = 20
            self.attack_delay = 3
        else:
            self.attack_cooldown_max = 30
            self.maxSpeed = 5
            self.attack_damage = 1
            self.attack_range = 50
            self.attack_width = 40
            self.attack_vertical_offset = 15

    def draw(self, display):
        # Effet de clignotement pendant l'invincibilité
        if self.invincible and pygame.time.get_ticks() % 200 < 100:
            return
            
        # Animation de mort
        if self.is_dying:
            display.blit(self.dying[self.dying_state % len(self.dying)], (self.x, self.y))
            if self.dying_current_delay == self.dying_delay:
                self.dying_state += 1
                self.dying_current_delay = 0
                if self.dying_state >= len(self.dying):
                    self.respawn_after_death = True
            else:
                self.dying_current_delay += 1
            return
            
        # Animation de dégâts
        if self.is_hit:
            if self.facing_right:
                display.blit(self.hit_frames[self.hit_state % len(self.hit_frames)], (self.x, self.y))
            else:
                display.blit(pygame.transform.flip(self.hit_frames[self.hit_state % len(self.hit_frames)], True, 0), (self.x, self.y))
                
            if self.hit_current_delay == self.hit_delay:
                self.hit_state += 1
                self.hit_current_delay = 0
                if self.hit_state >= len(self.hit_frames):
                    self.is_hit = False
            else:
                self.hit_current_delay += 1
            return
        
        # Animation d'attaque
        if self.is_attacking:
            if self.facing_right:
                display.blit(self.attack_frames[self.attack_state % len(self.attack_frames)], (self.x, self.y))
            else:
                display.blit(pygame.transform.flip(self.attack_frames[self.attack_state % len(self.attack_frames)], True, 0), (self.x, self.y))
                
            if self.attack_current_delay == self.attack_delay:
                self.attack_state += 1
                self.attack_current_delay = 0
                if self.attack_state >= len(self.attack_frames):
                    self.is_attacking = False
            else:
                self.attack_current_delay += 1
            
        # Animations normales
        elif self.doubleJumpActive:
            if self.pastState == "RUN_RIGHT":
                display.blit(self.doublejump[self.doublejump_state % len(self.doublejump)], (self.x, self.y))
            else:
                display.blit(pygame.transform.flip(self.doublejump[self.doublejump_state % len(self.doublejump)], 1, 0), (self.x, self.y))
            
            if self.currDelay == self.delay:
                self.doublejump_state += 1
                self.currDelay = 0
                if self.doublejump_state >= len(self.doublejump):
                    self.doubleJumpActive = False
            else:
                self.currDelay += 1
        elif not self.isOnGround and self.jumpVel > self.currG:
            if self.pastState == "RUN_RIGHT":
                display.blit(self.player_jump, (self.x, self.y))
            else:
                display.blit(pygame.transform.flip(self.player_jump, 1, 0), (self.x, self.y))
        elif not self.isOnGround:
            if self.pastState == "RUN_RIGHT":
                display.blit(self.player_fall, (self.x, self.y))
            else:
                display.blit(pygame.transform.flip(self.player_fall, 1, 0), (self.x, self.y))
        elif self.state == "IDLE_RIGHT":
            display.blit(self.idle[self.idle_state % len(self.idle)], (self.x, self.y))
            if self.currDelay == self.delay:
                self.idle_state += 1
                self.currDelay = 0
            else:
                self.currDelay += 1
        elif self.state == "IDLE_LEFT":
            display.blit(pygame.transform.flip(self.idle[self.idle_state % len(self.idle)], 1, 0), (self.x, self.y))
            if self.currDelay == self.delay:
                self.idle_state += 1
                self.currDelay = 0
            else:
                self.currDelay += 1
        elif self.state == "RUN_RIGHT":
            display.blit(self.run[self.run_state % len(self.run)], (self.x, self.y))
            if self.currDelay == self.delay:
                self.run_state += 1
                self.currDelay = 0
            else:
                self.currDelay += 1
        elif self.state == "RUN_LEFT":
            display.blit(pygame.transform.flip(self.run[self.run_state % len(self.run)], 1, 0), (self.x, self.y))
            if self.currDelay == self.delay:
                self.run_state += 1
                self.currDelay = 0
            else:
                self.currDelay += 1

        # Suivi des collisions
        self.last_y = self.y
        if self.gs != 0:
            self.isOnGround = True
        else:
            self.isOnGround = False
        self.gs = 0

    def update(self, keys, sound_manager=None):
        # Ignorer les contrôles si mort ou touché
        if self.is_dying or self.is_hit:
            return
            
        # Minuteur d'invincibilité
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
        
        # Cooldown d'attaque
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # Cooldown de saut
        if self.jump_cooldown > 0:
            self.jump_cooldown -= 1
                
        # Gestion de l'attaque
        if keys[pygame.K_z] and self.attack_cooldown == 0 and not self.is_attacking:
            self.is_attacking = True
            self.attack_state = 0
            self.attack_current_delay = 0
            self.attack_cooldown = self.attack_cooldown_max
            if sound_manager:
                sound_manager.play("hit")
        
        # Mouvement horizontal (ignorer pour Knight/Assassin pendant l'attaque)
        should_handle_movement = not (self.is_attacking and (self.character_type == "Knight" or self.character_type == "Assassin"))
        
        if should_handle_movement:
            stall = self.x
            if keys[pygame.K_RIGHT] and keys[pygame.K_LEFT]:
                self.speed = 0
            else:
                if keys[pygame.K_RIGHT]:
                    if self.speed <= self.maxSpeed:
                        self.speed += self.acc
                    self.x += self.speed
                    self.state = "RUN_RIGHT"
                    self.pastState = "RUN_RIGHT"
                    self.facing_right = True
                elif keys[pygame.K_LEFT]:
                    if self.speed <= self.maxSpeed:
                        self.speed += self.acc
                    self.x -= self.speed
                    self.state = "RUN_LEFT"
                    self.pastState = "RUN_LEFT"
                    self.facing_right = False
                else:
                    if self.pastState == "RUN_RIGHT" or self.pastState == "JUMP_RIGHT":
                        self.state = "IDLE_RIGHT"
                    elif self.pastState == "RUN_LEFT" or self.pastState == "JUMP_LEFT":
                        self.state = "IDLE_LEFT"
            if stall == self.x:
                self.speed = 0
    
        # État d'ignorance actuel
        current_ignore_state = self.ignore_current_jump_press
        
        # Gestion du saut
        jump_key_pressed = keys[pygame.K_SPACE] and not current_ignore_state
        
        # Saut normal avec cooldown
        if self.isOnGround and jump_key_pressed and self.jump_cooldown == 0:
            self.jumpVel = self.jumpMax
            self.isOnGround = False
            self.canDoubleJump = True
            self.jump_cooldown = self.jump_cooldown_max
            self.jump_sound_played = False
            self.double_jump_sound_played = False
            
            if sound_manager:
                sound_manager.play("jump")
                self.jump_sound_played = True
            
        # Double saut - uniquement sur nouvelle pression
        elif (not self.isOnGround and 
              self.canDoubleJump and 
              jump_key_pressed and 
              not self.prev_jump_pressed and 
              self.jump_cooldown == 0):
              
            self.jumpVel = self.jumpMax * 1.3
            self.canDoubleJump = False
            self.doubleJumpActive = True
            self.doublejump_state = 0
            self.jump_cooldown = self.jump_cooldown_max
            
            if sound_manager and not self.double_jump_sound_played:
                sound_manager.play("jump")
                self.double_jump_sound_played = True
        
        # Mise à jour de l'état précédent du saut
        if not current_ignore_state:
            self.prev_jump_pressed = keys[pygame.K_SPACE]
        
        # Réinitialiser le double saut à l'atterrissage
        if self.isOnGround:
            self.jumpVel = 0
            self.doubleJumpActive = False
            if self.jump_cooldown == 0:
                self.jump_sound_played = False
                self.double_jump_sound_played = False
            
        if not self.isOnGround and self.jumpVel > self.currG:
            self.state = "JUMP"
    
        # Calcul de la nouvelle position Y
        new_y = self.y - self.jumpVel
        
        # Vérifier si la position pousse le joueur trop loin hors de l'écran
        allowed_overflow = self.h // 0.15
        if new_y >= self.min_visible_y - allowed_overflow:
            self.y = new_y
        else:
            self.y = self.min_visible_y - allowed_overflow
            self.jumpVel = 0
    
        # Application de la gravité
        if not self.isOnGround:
            if self.currG <= self.maxG:
                self.currG += self.gAcc
            self.y += self.currG
        else:
            self.currG = 0
    
        # Réinitialisation du drapeau d'ignorance
        if not keys[pygame.K_SPACE]:
            self.ignore_current_jump_press = False
            
    def lose_heart(self, sound_manager=None):
        if self.invincible or self.is_dying or self.is_hit:
            return False
            
        self.current_hearts -= 1
        
        # Animation de dégâts
        self.is_hit = True
        self.hit_state = 0
        self.hit_current_delay = 0
        
        if sound_manager:
            sound_manager.play("hurt")
        
        if self.current_hearts <= 0:
            self.is_dying = True
            self.dying_state = 0
            return True
        else:
            self.invincible = True
            self.invincible_timer = self.invincible_duration
            return False
            
    def heal(self, hearts=1):
        self.current_hearts = min(self.current_hearts + hearts, self.max_hearts)
        
    def get_attack_rect(self):
        """Renvoie le rectangle pour la hitbox d'attaque du joueur"""
        if not self.is_attacking:
            return None
            
        # Retourner le rect d'attaque uniquement au milieu de l'animation
        if self.attack_state < 1 or self.attack_state > 2:
            return None
        
        attack_range = getattr(self, 'attack_range', 50)
        attack_width = getattr(self, 'attack_width', self.h - 20)
        vertical_offset = getattr(self, 'attack_vertical_offset', 10)
        
        if self.facing_right:
            return pygame.Rect(
                self.x + self.w - 10,
                self.y + vertical_offset,
                attack_range,
                attack_width
            )
        else:
            return pygame.Rect(
                self.x - attack_range + 10,
                self.y + vertical_offset,
                attack_range,
                attack_width
            )