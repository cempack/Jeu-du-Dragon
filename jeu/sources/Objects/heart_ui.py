import pygame

class HeartUI:
    """Classe pour afficher les cœurs de vie du joueur à l'écran"""
    
    def __init__(self):
        # Chargement et configuration des cœurs
        self.heart_image = pygame.image.load("./Assets/UI/heart.png")
        self.heart_width = 32
        self.heart_height = 32
        self.heart_spacing = 10
        self.heart_y_position = 20
        
        # Pré-redimensionnement de l'image pour optimiser les performances
        self.scaled_heart = pygame.transform.scale(self.heart_image, 
                                                 (self.heart_width, self.heart_height))
        
    def draw(self, display, current_hearts, max_hearts):
        """Affiche les cœurs dans le coin supérieur gauche"""
        for i in range(max_hearts):
            heart_x = 20 + i * (self.heart_width + self.heart_spacing)
            
            if i < current_hearts:
                # Cœur plein
                display.blit(self.scaled_heart, (heart_x, self.heart_y_position))
            else:
                # Cœur vide (semi-transparent)
                heart_surface = pygame.Surface((self.heart_width, self.heart_height), pygame.SRCALPHA)
                heart_surface.blit(self.scaled_heart, (0, 0))
                heart_surface.set_alpha(80)
                display.blit(heart_surface, (heart_x, self.heart_y_position))