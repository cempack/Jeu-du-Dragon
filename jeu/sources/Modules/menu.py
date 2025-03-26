import pygame
import math
from Modules.font_manager import FontManager

class Menu:
    def __init__(self, width=450, height=320, options=None, title="MENU"):
        """Initialise un menu avec dimensions, options et titre personnalisables."""
        self.width = width
        self.height = height
        self.options = options or []
        self.title = title
        self.visible = False
        self.selected_option = 0
        
        # Système de couleurs
        self.colors = {
            'bg': (20, 70, 45),               # Vert foncé
            'border': (10, 112, 48),          # Vert bordure
            'title': (255, 255, 255),         # Blanc
            'title_underline': (35, 123, 89), # Vert moyen
            'option_normal': (144, 238, 144), # Vert clair
            'option_bg': (10, 112, 48),       # Vert foncé
            'option_selected': (255, 255, 255), # Blanc
            'instructions': (144, 238, 144)   # Vert clair
        }
        
        # Traductions pour les options
        self.translations = {}
        
        # Récupération du gestionnaire de polices
        self.font_manager = FontManager.get_instance()
        
    def set_options(self, options):
        """Met à jour les options du menu."""
        self.options = options
        self.selected_option = 0
    
    def set_translations(self, translations_dict):
        """Définit les traductions pour les noms d'affichage des options."""
        self.translations = translations_dict
        
    def set_colors(self, colors_dict):
        """Met à jour les couleurs."""
        for key, value in colors_dict.items():
            self.colors[key] = value
            
    def draw_rounded_rect(self, surface, color, rect, radius):
        """Dessine un rectangle arrondi."""
        x, y, width, height = rect
        
        pygame.draw.rect(surface, color, (x + radius, y, width - 2*radius, height))
        pygame.draw.rect(surface, color, (x, y + radius, width, height - 2*radius))
        
        pygame.draw.circle(surface, color, (x + radius, y + radius), radius)
        pygame.draw.circle(surface, color, (x + width - radius, y + radius), radius)
        pygame.draw.circle(surface, color, (x + radius, y + height - radius), radius)
        pygame.draw.circle(surface, color, (x + width - radius, y + height - radius), radius)
    
    def draw(self, display):
        """Affiche le menu sur l'écran."""
        if not self.visible:
            return
            
        menu_x = display.get_width() // 2 - self.width // 2
        menu_y = display.get_height() // 2 - self.height // 2
        
        menu_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Fond du menu avec coins arrondis
        border_radius = 20
        self.draw_rounded_rect(menu_surface, self.colors['bg'], (0, 0, self.width, self.height), border_radius)
        
        # Bordure
        border_width = 4
        pygame.draw.rect(menu_surface, self.colors['border'], 
                      (border_width//2, border_width//2, 
                       self.width - border_width, self.height - border_width), 
                      border_width, border_radius - border_width//2)
        
        # Utilisation du gestionnaire de polices
        font = self.font_manager.get_font_regular('medium')
        bold_font = self.font_manager.get_font_bold('large')
        small_font = self.font_manager.get_font_regular('small')
        
        # Titre
        title = bold_font.render(self.title, True, self.colors['title'])
        title_x = self.width//2 - title.get_width()//2
        menu_surface.blit(title, (title_x, 50))
        
        # Ligne décorative
        line_width = title.get_width() + 40
        line_y = 85
        pygame.draw.line(menu_surface, self.colors['title_underline'], 
                      (self.width//2 - line_width//2, line_y), 
                      (self.width//2 + line_width//2, line_y), 3)
        
        # Options du menu
        for i, option in enumerate(self.options):
            option_y = 135 + i * 50
            
            if i == self.selected_option:
                # Fond de l'option sélectionnée
                option_width, option_height = 300, 40
                option_x = self.width//2 - option_width//2
                pygame.draw.rect(menu_surface, self.colors['option_bg'], 
                              (option_x, option_y, option_width, option_height), border_radius=10)
                color = self.colors['option_selected']
            else:
                color = self.colors['option_normal']
            
            # Appliquer la traduction si disponible
            display_name = self.translations.get(option, option.upper())
                
            # Texte de l'option
            text = bold_font.render(display_name, True, color)
            menu_surface.blit(text, (self.width//2 - text.get_width()//2, option_y + 5))
        
        # Instructions avec effet de pulsation
        pulse = 20 + int(15 * math.sin(pygame.time.get_ticks() / 200))
        instruction_color = (
            self.colors['instructions'][0], 
            self.colors['instructions'][1], 
            max(0, min(255, self.colors['instructions'][2] - pulse))
        )
        
        instructions = font.render("Flèches pour sélectionner, Entrée pour confirmer", True, instruction_color)
        menu_surface.blit(instructions, (self.width//2 - instructions.get_width()//2, self.height - 60))
        
        # Affichage du menu
        display.blit(menu_surface, (menu_x, menu_y))
        
    def show(self):
        """Affiche le menu."""
        self.visible = True
        
    def hide(self):
        """Cache le menu."""
        self.visible = False
        
    def is_visible(self):
        """Vérifie si le menu est visible."""
        return self.visible
        
    def get_selected_option(self):
        """Récupère l'option sélectionnée."""
        if self.visible and 0 <= self.selected_option < len(self.options):
            return self.options[self.selected_option]
        return None
        
    def select_next(self):
        """Sélectionne l'option suivante."""
        if self.visible and self.options:
            self.selected_option = (self.selected_option + 1) % len(self.options)
        
    def select_previous(self):
        """Sélectionne l'option précédente."""
        if self.visible and self.options:
            self.selected_option = (self.selected_option - 1) % len(self.options)