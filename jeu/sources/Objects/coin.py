import pygame
from Modules.spriteSheet import SpriteSheet


class Coin:
    def __init__(self, x, y, w, h, image):
        # Position et dimensions de la pièce
        self.x, self.y, self.w, self.h, self.image = x, y, 32, 32, image
        self.collide = True
        self.collectable = True
        self.collected = False
        self.topoffset = 18
        self.xoffset = 19

        # Animation d'état inactif
        self.idle_length = 11
        coin_idle = SpriteSheet(pygame.image.load("./Assets/Collectables/Coin.png"))
        self.idle = [coin_idle.getimage(16 * x, 0, 16, 16) for x in range(self.idle_length)]
        self.idle_state = 0
        self.delay = 3
        self.currDelay = 0

        # Animation de collection
        self.death_length = 6
        coin_death = SpriteSheet(pygame.image.load("./Assets/Collectables/collected.png"))
        self.death = [coin_death.getimage(32 * x, 0, 32, 32) for x in range(self.death_length)]
        self.death_state = 0
        self.d_delay = 2
        self.d_currDelay = 0

    def draw(self, display):
        if not self.collected:
            # Affichage de l'animation d'inactivité
            display.blit(pygame.transform.scale(self.idle[self.idle_state % self.idle_length],
                                               (self.w, self.h)), (self.x, self.y))
            
            # Gestion du timing d'animation
            if self.currDelay == self.delay:
                self.idle_state += 1
                self.currDelay = 0
            else:
                self.currDelay += 1
        else:
            # Lecture de l'animation de collection une seule fois
            if self.death_state < self.death_length:
                display.blit(pygame.transform.scale(self.death[self.death_state],
                                                  (self.w, self.h)), (self.x, self.y))

                if self.d_currDelay == self.d_delay:
                    self.death_state += 1
                    self.d_currDelay = 0
                else:
                    self.d_currDelay += 1

    def update(self, keys):
        pass