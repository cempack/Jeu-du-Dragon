import pygame

class SpriteSheet:
    """Classe utilitaire pour gérer les feuilles de sprites dans pygame."""
    
    def __init__(self, image):
        """Initialise avec une image de feuille de sprites."""
        # Conversion avec alpha pour gérer la transparence
        self.ss = image.convert_alpha()

    def getimage(self, x, y, width, height):
        """Extrait un sprite individuel de la feuille.
        
        Paramètres:
            x, y: Coordonnées du sprite dans la feuille
            width, height: Dimensions du sprite en pixels
        """
        # Surface optimisée avec transparence alpha
        image = pygame.Surface([width, height], pygame.SRCALPHA).convert_alpha()
        
        # Copie du sprite depuis la feuille vers la nouvelle surface
        image.blit(self.ss, (0, 0), (x, y, width, height))
        
        return image