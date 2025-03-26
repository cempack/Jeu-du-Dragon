import pygame

class Ground:
    """Classe représentant un élément de sol dans le jeu."""
    
    def __init__(self, x, y, w, h, image):
        """Initialise un élément de sol avec position, dimensions et image."""
        self.x, self.y, self.w, self.h, self.image = x, y, w, h, image
        self.collide = True
        self.collectable = False

        self.topoffset = 0
        self.xoffset = 0

    def draw(self, display):
        """Affiche l'élément de sol sur l'écran."""
        display.blit(self.image, (self.x, self.y))

    def update(self, keys):
        """Met à jour l'état de l'élément de sol."""
        pass