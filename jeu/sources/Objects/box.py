import pygame


class Box:
    """Classe représentant une boîte rectangulaire pour la collision et l'affichage"""
    
    def __init__(self, x, y, w, h):
        """Initialise une boîte avec position et dimensions"""
        self.x, self.y, self.w, self.h = x, y, w, h
        self.collide = True
        self.collectable = False

        self.topoffset = 0
        self.xoffset = 0

    def draw(self, display):
        """Dessine la boîte sur la surface d'affichage"""
        pygame.draw.rect(display, (0, 0, 0), (self.x, self.y, self.w, self.h))

    def update(self, keys):
        """Met à jour l'état de la boîte si nécessaire"""
        pass