import pygame

class Hazard:
    """
    Représente un objet dangereux qui peut endommager le joueur.
    """
    def __init__(self, x, y, w, h, image=None):
        """
        Initialise un objet dangereux.
        
        Args:
            x, y: Coordonnées de position
            w, h: Largeur et hauteur
            image: Surface pygame optionnelle
        """
        self.x, self.y, self.w, self.h = x, y, w, h
        self.image = image
        self.collide = True
        self.collectable = False
        self.is_hazard = True  # Identifie cet objet comme dangereux
        self.topoffset = 0
        self.xoffset = 0
        
    def draw(self, display):
        """Affiche l'objet dangereux sur l'écran."""
        if self.image:
            display.blit(self.image, (self.x, self.y))
        else:
            # Représentation visuelle par défaut
            pygame.draw.rect(display, (255, 0, 0), (self.x, self.y, self.w, self.h))
            
    def update(self, keys):
        """Met à jour l'état de l'objet selon les entrées."""
        pass