import pygame

class Decoration:
    def __init__(self, x, y, width, height, image):
        """Initialise un objet de décoration"""
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = image
        self.rect = pygame.Rect(x, y, width, height)
    
    def update(self, keys=None):
        """Méthode update vide - les décorations n'ont pas de comportement"""
        pass
    
    def draw(self, surface):
        """Dessine la décoration sur la surface donnée"""
        surface.blit(self.image, (self.x, self.y))