import pygame
import math
from Modules.spriteSheet import SpriteSheet
from Modules.font_manager import get_font

class HeroSelector:
    def __init__(self, display_width, display_height):
        self.display_width = display_width
        self.display_height = display_height
        
        # Héros disponibles
        self.heroes = ["Knight", "Archer", "Assassin", "Mage"]
        self.selected_index = 0
        
        # Descriptions des héros
        self.hero_descriptions = {
            "Knight": "A la guerre comme à la guerre.",
            "Archer": "En plein dans le mille !",
            "Assassin": "*Le silence est d'or*",
            "Mage": "Vous ne passerez pas !"
        }
        
        # Chargement de l'arrière-plan
        try:
            self.bg_image = pygame.image.load("./Assets/Terrain/bg.png").convert()
        except Exception as e:
            print(f"Échec du chargement de l'image d'arrière-plan: {e}")
            self.bg_image = None
        
        # Chargement des polices
        self.load_fonts()
        
        # Palette de couleurs
        self.colors = {
            'bg': (20, 70, 45),               # Vert foncé
            'border': (10, 112, 48),          # Vert bordure
            'title': (255, 255, 255),         # Blanc
            'title_underline': (35, 123, 89), # Vert moyen
            'text': (255, 255, 255),          # Blanc
            'desc': (200, 255, 200),          # Vert clair
            'option_bg': (10, 112, 48),       # Vert moyen
            'option_selected': (255, 255, 255), # Blanc
            'arrow_active': (255, 255, 255),    # Blanc
            'arrow_inactive': (100, 100, 100),  # Gris
            'key_bg': (10, 90, 50),           # Fond des touches
            'instructions': (180, 255, 180)   # Vert clair
        }
        
        # Paramètres d'animation
        self.animation_frames = 4
        self.animation_delay = 5
        self.current_delay = 0
        self.current_frame = 0
        
        # Chargement des animations
        self.hero_animations = self.load_hero_animations()
    
    def load_fonts(self):
        """Charge les polices nécessaires"""
        self.title_font = get_font('bold', 'large')
        self.bold_font = get_font('bold', 'large')
        self.font = get_font('regular', 'medium')
        self.desc_font = get_font('regular', 'medium')
        self.key_font = get_font('bold', 'small')
    
    def load_hero_animations(self):
        """Charge les animations des personnages"""
        animations = {}
        
        for hero in self.heroes:
            try:
                sprite_sheet = SpriteSheet(pygame.image.load(f"./Assets/Characters/{hero}/run.png"))
                frames = [sprite_sheet.getimage(32 * x, 0, 32, 32) for x in range(self.animation_frames)]
                
                frames = [pygame.transform.scale(frame, (160, 160)) for frame in frames]
                animations[hero] = frames
            except Exception as e:
                print(f"Échec du chargement de l'animation {hero}: {e}")
                animations[hero] = []
                
        return animations
    
    def draw_rounded_rect(self, surface, color, rect, radius):
        """Dessine un rectangle arrondi"""
        x, y, width, height = rect
        
        pygame.draw.rect(surface, color, (x + radius, y, width - 2*radius, height))
        pygame.draw.rect(surface, color, (x, y + radius, width, height - 2*radius))
        
        pygame.draw.circle(surface, color, (x + radius, y + radius), radius)
        pygame.draw.circle(surface, color, (x + width - radius, y + radius), radius)
        pygame.draw.circle(surface, color, (x + radius, y + height - radius), radius)
        pygame.draw.circle(surface, color, (x + width - radius, y + height - radius), radius)
    
    def draw_arrow(self, display, direction, position, active=True):
        """Dessine une flèche dans la direction spécifiée"""
        x, y = position
        color = self.colors['arrow_active'] if active else self.colors['arrow_inactive']
        
        if direction == "left":
            points = [(x, y), (x + 12, y - 8), (x + 12, y + 8)]
        elif direction == "right":
            points = [(x, y), (x - 12, y - 8), (x - 12, y + 8)]
        elif direction == "up":
            points = [(x, y), (x - 8, y + 12), (x + 8, y + 12)]
        elif direction == "down":
            points = [(x, y), (x - 8, y - 12), (x + 8, y - 12)]
            
        pygame.draw.polygon(display, color, points)
    
    def draw_navigation_help(self, display, panel_x, panel_y, panel_width, panel_height):
        """Affiche les instructions de navigation"""
        help_y = panel_y + panel_height + 20
        
        instructions = [
            {"direction": "left", "text": "PRÉCÉDENT", "x_offset": -120},
            {"direction": "right", "text": "SUIVANT", "x_offset": 0},
            {"key": "ENTRÉE", "text": "CONFIRMER", "x_offset": 120}
        ]
        
        for instruction in instructions:
            center_x = self.display_width // 2 + instruction["x_offset"]
            
            if "direction" in instruction:
                key_size = 30
                key_bg_rect = pygame.Rect(
                    center_x - key_size // 2,
                    help_y,
                    key_size,
                    key_size
                )
                
                pygame.draw.rect(display, self.colors['key_bg'], key_bg_rect, border_radius=5)
                pygame.draw.rect(display, (255, 255, 255, 100), 
                                (key_bg_rect.x + 1, key_bg_rect.y + 1, 
                                 key_bg_rect.width - 2, key_bg_rect.height - 2),
                                1, border_radius=5)
                
                self.draw_arrow(display, instruction["direction"], 
                               (center_x, help_y + key_size // 2), True)
            else:
                key_text = self.key_font.render(instruction["key"], True, self.colors['option_selected'])
                text_width = key_text.get_width()
                padding = 10
                
                key_bg_rect = pygame.Rect(
                    center_x - text_width // 2 - padding,
                    help_y,
                    text_width + padding * 2,
                    30
                )
                
                pygame.draw.rect(display, self.colors['key_bg'], key_bg_rect, border_radius=5)
                pygame.draw.rect(display, (255, 255, 255, 100), 
                                (key_bg_rect.x + 1, key_bg_rect.y + 1, 
                                 key_bg_rect.width - 2, key_bg_rect.height - 2),
                                1, border_radius=5)
                
                display.blit(key_text, (center_x - text_width // 2, help_y + 15 - key_text.get_height() // 2))
            
            desc_text = self.font.render(instruction["text"], True, self.colors['instructions'])
            desc_y = help_y + (30 if "key" in instruction else 35)
            display.blit(desc_text, (center_x - desc_text.get_width() // 2, desc_y))
    
    def draw(self, display):
        """Affiche l'écran de sélection des héros"""
        # Arrière-plan
        if self.bg_image:
            bg_width, bg_height = self.bg_image.get_size()
            for x in range(0, self.display_width, bg_width):
                for y in range(0, self.display_height, bg_height):
                    display.blit(self.bg_image, (x, y))
        
        # Titre avec effet d'ombre
        title_text = "CHOISISSEZ VOTRE HÉROS"
        title = self.title_font.render(title_text, True, self.colors['title'])
        shadow = self.title_font.render(title_text, True, (30, 30, 30))
        
        title_x = self.display_width // 2 - title.get_width() // 2
        title_y = 80
        shadow_offset = 3
        
        display.blit(shadow, (title_x + shadow_offset, title_y + shadow_offset))
        display.blit(title, (title_x, title_y))
        
        # Ligne décorative sous le titre
        line_width = title.get_width() + 40
        line_y = title_y + title.get_height() + 10
        pygame.draw.line(display, self.colors['title_underline'], 
                        (self.display_width//2 - line_width//2, line_y), 
                        (self.display_width//2 + line_width//2, line_y), 3)
        
        # Panneau principal
        panel_width = 520
        panel_height = 380
        panel_x = self.display_width // 2 - panel_width // 2
        panel_y = title_y + title.get_height() + 30
        
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        
        border_radius = 20
        self.draw_rounded_rect(panel_surface, self.colors['bg'], 
                           (0, 0, panel_width, panel_height), border_radius)
        
        border_width = 4
        pygame.draw.rect(panel_surface, self.colors['border'], 
                      (border_width//2, border_width//2, 
                       panel_width - border_width, panel_height - border_width), 
                      border_width, border_radius - border_width//2)
        
        display.blit(panel_surface, (panel_x, panel_y))
        
        # Informations du héros
        if self.selected_index < len(self.heroes):
            hero_name = self.heroes[self.selected_index]
            
            # Nom du héros
            hero_display_name = self.get_hero_display_name(hero_name)
            name_text = self.bold_font.render(hero_display_name, True, self.colors['option_selected'])
            
            name_bg_width = name_text.get_width() + 40
            name_bg_height = name_text.get_height() + 20
            name_bg_x = panel_x + panel_width // 2 - name_bg_width // 2
            name_bg_y = panel_y + 30
            
            pygame.draw.rect(display, self.colors['option_bg'], 
                          (name_bg_x, name_bg_y, name_bg_width, name_bg_height), 
                          border_radius=10)
            
            name_center_x = name_bg_x + name_bg_width // 2 - name_text.get_width() // 2
            name_center_y = name_bg_y + name_bg_height // 2 - name_text.get_height() // 2
            display.blit(name_text, (name_center_x, name_center_y))
            
            # Description du héros
            hero_description = self.hero_descriptions.get(hero_name, "")
            desc_text = self.desc_font.render(hero_description, True, self.colors['desc'])
            
            desc_bg_width = desc_text.get_width() + 40
            desc_bg_height = desc_text.get_height() + 16
            desc_bg_x = panel_x + panel_width // 2 - desc_bg_width // 2
            desc_bg_y = name_bg_y + name_bg_height + 12
            
            desc_surface = pygame.Surface((desc_bg_width, desc_bg_height), pygame.SRCALPHA)
            pygame.draw.rect(desc_surface, self.colors['bg'] + (180,), 
                          (0, 0, desc_bg_width, desc_bg_height), 
                          border_radius=8)
            
            pygame.draw.rect(desc_surface, self.colors['border'] + (150,), 
                          (1, 1, desc_bg_width - 2, desc_bg_height - 2), 
                          2, border_radius=8)
            
            display.blit(desc_surface, (desc_bg_x, desc_bg_y))
            
            desc_center_x = desc_bg_x + desc_bg_width // 2 - desc_text.get_width() // 2
            desc_center_y = desc_bg_y + desc_bg_height // 2 - desc_text.get_height() // 2
            display.blit(desc_text, (desc_center_x, desc_center_y))
            
            # Animation du héros
            if hero_name in self.hero_animations and self.hero_animations[hero_name]:
                frames = self.hero_animations[hero_name]
                if frames:
                    current_frame = frames[self.current_frame % len(frames)]
                    char_x = panel_x + panel_width // 2 - current_frame.get_width() // 2
                    char_y = desc_bg_y + desc_bg_height + 20
                    
                    display.blit(current_frame, (char_x, char_y))
                    
                    # Mise à jour de l'animation
                    if self.current_delay >= self.animation_delay:
                        self.current_frame += 1
                        self.current_delay = 0
                    else:
                        self.current_delay += 1
        
        # Flèches de navigation
        left_active = self.selected_index > 0
        right_active = self.selected_index < len(self.heroes) - 1
        
        arrows_y = panel_y + panel_height // 2
        self.draw_arrow(display, "left", (panel_x + 40, arrows_y), left_active)
        self.draw_arrow(display, "right", (panel_x + panel_width - 40, arrows_y), right_active)
        
        # Aide à la navigation
        self.draw_navigation_help(display, panel_x, panel_y, panel_width, panel_height)
    
    def get_hero_display_name(self, hero_name):
        """Convertit les noms internes en noms d'affichage français"""
        translations = {
            "Knight": "CHEVALIER",
            "Archer": "ARCHER",
            "Assassin": "ASSASSIN",
            "Mage": "MAGE"
        }
        return translations.get(hero_name, hero_name.upper())
    
    def select_next(self):
        """Sélectionne le héros suivant"""
        if self.selected_index < len(self.heroes) - 1:
            self.selected_index += 1
            self.current_frame = 0
    
    def select_previous(self):
        """Sélectionne le héros précédent"""
        if self.selected_index > 0:
            self.selected_index -= 1
            self.current_frame = 0
    
    def get_selected_hero(self):
        """Renvoie le type de héros sélectionné"""
        if 0 <= self.selected_index < len(self.heroes):
            return self.heroes[self.selected_index]
        return "Knight"