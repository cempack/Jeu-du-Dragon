import pygame
from Modules.font_manager import FontManager

class Ui:
    """Classe de base pour les éléments d'interface utilisateur"""
    def __init__(self, x, y, w, h, image):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.image = image
        
    def draw(self, display):
        # Affiche l'image redimensionnée aux bonnes dimensions
        display.blit(pygame.transform.scale(self.image, (self.w, self.h)), (self.x, self.y))
    
    def update(self, keys):
        pass
    
    def clicked(self, pos):
        # Vérifie si la position est dans les limites de l'élément
        x, y = pos
        if self.x <= x <= self.x + self.w and self.y <= y <= self.y + self.h:
            return True
        return False
    
    def activate(self):
        pass


class StartButton(Ui):
    """Bouton pour démarrer le jeu"""
    def __init__(self, x, y, w, h, image, text="START"):
        super().__init__(x, y, w, h, image)
        self.text = text
        self.font = FontManager.get_instance().get_ui_bold_font()
        
    def draw(self, display):
        # Affiche le bouton
        super().draw(display)
        
        # Affiche le texte centré sur le bouton
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_x = self.x + (self.w - text_surface.get_width()) // 2
        text_y = self.y + (self.h - text_surface.get_height()) // 2
        display.blit(text_surface, (text_x, text_y))
    
    def activate(self):
        return "start game"