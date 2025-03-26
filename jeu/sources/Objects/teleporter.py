import pygame
import math
from Modules.menu import Menu
from Modules.font_manager import get_font

class Teleporter:
    def __init__(self, x, y, w, h, image):
        # Position et dimensions
        self.x, self.y, self.w, self.h = x, y, w, h
        self.image = image
        self.collide = True
        self.collectable = False
        self.activated = False
        
        # Configuration du menu de téléportation
        self.menu = Menu(
            width=500,
            height=500,
            options=["level1", "level2", "level3", "level4", "level5"],
            title="PORTAIL DE TÉLÉPORTATION"
        )
        
        # Noms d'affichage pour les niveaux
        self.menu.set_translations({
            "level1": "NIVEAU 1",
            "level2": "NIVEAU 2",
            "level3": "NIVEAU 3",
            "level4": "NIVEAU 4",
            "level5": "ENTRE DU DRAGON"
        })
        
        # Palette de couleurs pour l'interface
        self.colors = {
            'bg': (20, 70, 45),
            'border': (10, 112, 48),
            'title': (255, 255, 255),
            'title_underline': (35, 123, 89),
            'option_normal': (220, 255, 220),
            'option_bg': (15, 85, 40),
            'option_selected': (255, 255, 255),
            'option_selected_bg': (30, 130, 70),
            'option_locked': (130, 130, 130),
            'option_completed': (200, 255, 150),
            'instructions': (180, 255, 180),
            'key_bg': (10, 90, 50),
            'scroll_indicator': (255, 255, 255, 150)
        }
        
        # Variables d'animation et d'affichage
        self.topoffset = 0
        self.xoffset = 0
        self.pulse_time = 0
        
        self.proximity_indicator = False
        self.indicator_alpha = 0
        
        self.glow_surface = None
        self.update_glow_surface()
        
        self.max_visible_options = 3
        self.scroll_offset = 0
        self.scroll_target = 0
        
        self.level_manager = None
        
        # Chargement des polices avec FontManager
        self.title_font = get_font('bold', 'large')
        self.option_font = get_font('bold', 'medium')
        self.instruction_font = get_font('regular', 'small')
        self.prompt_font = get_font('bold', 'small')
        self.key_font = get_font('bold', 'tiny')
    
    def set_level_manager(self, level_manager):
        self.level_manager = level_manager
    
    def update_glow_surface(self):
        # Création de l'effet de halo lumineux
        size = max(self.w, self.h) * 2
        self.glow_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        center = size // 2
        for radius in range(center, 0, -1):
            alpha = int(100 * (radius / center))
            color = (50, 200, 120, max(0, 100 - alpha))
            pygame.draw.circle(self.glow_surface, color, (center, center), radius)
    
    def draw(self, display):
        if not self.menu.is_visible():
            # Dessin du halo lumineux pulsant
            if self.glow_surface:
                glow_size = self.glow_surface.get_width()
                pulse_intensity = 0.08 * abs(math.sin(self.pulse_time / 400))
                scaled_size = int(glow_size * (1.0 + pulse_intensity))
                
                scaled_glow = pygame.transform.scale(
                    self.glow_surface, 
                    (scaled_size, scaled_size)
                )
                
                glow_x = self.x + self.w//2 - scaled_glow.get_width()//2
                glow_y = self.y + self.h//2 - scaled_glow.get_height()//2
                display.blit(scaled_glow, (glow_x, glow_y))
            
            # Animation de pulsation du téléporteur
            scale_factor = 1.0 + 0.15 * abs(math.sin(self.pulse_time / 500))
            self.pulse_time += 1
            
            width = int(self.w * scale_factor)
            height = int(self.h * scale_factor)
            x_offset = (width - self.w) // 2
            y_offset = (height - self.h) // 2
            
            scaled_img = pygame.transform.scale(self.image, (width, height))
            display.blit(scaled_img, (self.x - x_offset, self.y - y_offset))
            
            # Affichage de l'indicateur de proximité
            if self.proximity_indicator:
                if self.indicator_alpha < 255:
                    self.indicator_alpha += 15
                
                prompt_surf = self.create_prompt_surface()
                prompt_surf.set_alpha(self.indicator_alpha)
                
                prompt_x = self.x + self.w//2 - prompt_surf.get_width()//2
                prompt_y = self.y - prompt_surf.get_height() - 20
                display.blit(prompt_surf, (prompt_x, prompt_y))
            else:
                self.indicator_alpha = 0
        else:
            # Affichage simple quand le menu est ouvert
            display.blit(pygame.transform.scale(self.image, (self.w, self.h)), (self.x, self.y))
    
    def create_prompt_surface(self):
        # Création du message d'interaction
        text = self.prompt_font.render("APPUYEZ SUR E", True, (255, 255, 255))
        
        width = text.get_width() + 20
        height = text.get_height() + 16
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        radius = 8
        pygame.draw.rect(
            surface, 
            (10, 112, 48, 230),
            (0, 0, width, height),
            border_radius=radius
        )
        
        pygame.draw.rect(
            surface,
            (35, 123, 89),
            (1, 1, width-2, height-2),
            2,
            border_radius=radius
        )
        
        surface.blit(text, (10, 8))
        
        return surface
    
    def draw_menu(self, display):
        # Affichage du menu de téléportation
        display_width, display_height = display.get_width(), display.get_height()
        
        menu_width = 500
        menu_height = 500
        menu_x = display_width // 2 - menu_width // 2
        menu_y = display_height // 2 - menu_height // 2
        
        menu_surface = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)
        
        # Fond et bordure du menu
        border_radius = 20
        self.draw_rounded_rect(menu_surface, self.colors['bg'], 
                          (0, 0, menu_width, menu_height), border_radius)
        
        border_width = 4
        pygame.draw.rect(menu_surface, self.colors['border'], 
                      (border_width//2, border_width//2, 
                       menu_width - border_width, menu_height - border_width), 
                      border_width, border_radius - border_width//2)
        
        display.blit(menu_surface, (menu_x, menu_y))
        
        # Titre du menu
        title_text = self.title_font.render("TABLETTE DE TÉLÉPORTATION", True, self.colors['title'])
        title_x = display_width // 2 - title_text.get_width() // 2
        title_y = menu_y + 40
        
        display.blit(title_text, (title_x, title_y))
        
        # Ligne de séparation sous le titre
        line_width = title_text.get_width() + 20
        pygame.draw.line(display, self.colors['title_underline'], 
                        (title_x - 10, title_y + title_text.get_height() + 5), 
                        (title_x + title_text.get_width() + 10, title_y + title_text.get_height() + 5), 3)
        
        # Afficher les options et aides de navigation
        self.draw_custom_options(display, menu_x, menu_y, menu_width, menu_height)
        self.draw_navigation_help(display, menu_x, menu_y, menu_width, menu_height)
        
        # Message pour revenir
        esc_text = self.instruction_font.render("APPUYEZ SUR ÉCHAP POUR REVENIR", True, self.colors['instructions'])
        esc_x = display_width // 2 - esc_text.get_width() // 2
        esc_y = menu_y + menu_height + 20
        
        bg_rect = pygame.Rect(
            esc_x - 10, 
            esc_y - 5, 
            esc_text.get_width() + 20, 
            esc_text.get_height() + 10
        )
        
        background = pygame.Surface(
            (bg_rect.width, bg_rect.height), 
            pygame.SRCALPHA
        )
        
        pygame.draw.rect(
            background, 
            (10, 70, 30, 180),
            (0, 0, bg_rect.width, bg_rect.height),
            border_radius=8
        )
        
        display.blit(background, (bg_rect.x, bg_rect.y))
        display.blit(esc_text, (esc_x, esc_y))
    
    def draw_arrow(self, display, direction, position, active=True):
        # Dessin des flèches de navigation
        x, y = position
        color = self.colors['option_selected'] if active else (150, 150, 150)
        
        if direction == "left":
            points = [(x, y), (x + 12, y - 8), (x + 12, y + 8)]
        elif direction == "right":
            points = [(x, y), (x - 12, y - 8), (x - 12, y + 8)]
        elif direction == "up":
            points = [(x, y), (x - 8, y + 12), (x + 8, y + 12)]
        elif direction == "down":
            points = [(x, y), (x - 8, y - 12), (x + 8, y - 12)]
        
        pygame.draw.polygon(display, color, points)
    
    def draw_navigation_help(self, display, menu_x, menu_y, menu_width, menu_height):
        # Affichage des instructions de navigation
        help_y = menu_y + menu_height - 90
        
        instructions = [
            {"direction": "up", "text": "HAUT", "x_offset": -80},
            {"direction": "down", "text": "BAS", "x_offset": 0},
            {"key": "ENTRÉE", "text": "CONFIRMER", "x_offset": 80}
        ]
        
        for instruction in instructions:
            if "direction" in instruction:
                center_x = menu_x + menu_width // 2 + instruction["x_offset"]
                key_size = 30
                
                key_bg_rect = pygame.Rect(
                    center_x - key_size // 2,
                    help_y,
                    key_size,
                    key_size
                )
                
                pygame.draw.rect(
                    display, 
                    self.colors['key_bg'], 
                    key_bg_rect,
                    border_radius=5
                )
                
                pygame.draw.rect(
                    display, 
                    (255, 255, 255, 100), 
                    (key_bg_rect.x + 1, key_bg_rect.y + 1, key_bg_rect.width - 2, key_bg_rect.height - 2),
                    1, 
                    border_radius=5
                )
                
                self.draw_arrow(
                    display, 
                    instruction["direction"], 
                    (center_x, help_y + key_size // 2),
                    True
                )
                
                desc_text = self.instruction_font.render(instruction["text"], True, self.colors['instructions'])
                display.blit(
                    desc_text, 
                    (center_x - desc_text.get_width() // 2, help_y + key_size + 5)
                )
                
            else:
                key_text = self.key_font.render(instruction["key"], True, self.colors['option_selected'])
                text_width = key_text.get_width()
                padding = 10
                
                center_x = menu_x + menu_width // 2 + instruction["x_offset"]
                
                key_bg_rect = pygame.Rect(
                    center_x - text_width // 2 - padding,
                    help_y,
                    text_width + padding * 2,
                    30
                )
                
                pygame.draw.rect(
                    display, 
                    self.colors['key_bg'], 
                    key_bg_rect,
                    border_radius=5
                )
                
                pygame.draw.rect(
                    display, 
                    (255, 255, 255, 100), 
                    (key_bg_rect.x + 1, key_bg_rect.y + 1, key_bg_rect.width - 2, key_bg_rect.height - 2),
                    1, 
                    border_radius=5
                )
                
                display.blit(
                    key_text, 
                    (center_x - text_width // 2, help_y + 15 - key_text.get_height() // 2)
                )
                
                desc_text = self.instruction_font.render(instruction["text"], True, self.colors['instructions'])
                display.blit(
                    desc_text, 
                    (center_x - desc_text.get_width() // 2, help_y + 35)
                )
        
    def draw_rounded_rect(self, surface, color, rect, radius):
        # Dessin d'un rectangle avec coins arrondis
        x, y, width, height = rect
        
        pygame.draw.rect(surface, color, (x + radius, y, width - 2*radius, height))
        pygame.draw.rect(surface, color, (x, y + radius, width, height - 2*radius))
        
        pygame.draw.circle(surface, color, (x + radius, y + radius), radius)
        pygame.draw.circle(surface, color, (x + width - radius, y + radius), radius)
        pygame.draw.circle(surface, color, (x + radius, y + height - radius), radius)
        pygame.draw.circle(surface, color, (x + width - radius, y + height - radius), radius)
    
    def draw_custom_options(self, display, menu_x, menu_y, menu_width, menu_height):
        # Affichage des options de téléportation
        options = self.menu.options
        selected_index = self.menu.selected_option
        
        menu_center_x = menu_x + menu_width // 2
        
        start_y = menu_y + 130
        option_height = 60
        option_width = 320
        option_padding = 25
        
        self.scroll_offset = max(0, min(selected_index - 1, len(options) - self.max_visible_options))
        
        start_idx = int(self.scroll_offset)
        end_idx = min(start_idx + self.max_visible_options, len(options))
        
        can_scroll_up = start_idx > 0
        can_scroll_down = end_idx < len(options)
        
        # Indicateurs de défilement
        if can_scroll_up:
            arrow_x = menu_center_x
            arrow_y = start_y - 12
            
            pygame.draw.polygon(
                display,
                self.colors['scroll_indicator'],
                [(arrow_x, arrow_y - 6), (arrow_x - 8, arrow_y + 2), (arrow_x + 8, arrow_y + 2)]
            )
        
        if can_scroll_down:
            arrow_x = menu_center_x
            arrow_y = start_y + (self.max_visible_options * (option_height + option_padding)) + 5
            
            pygame.draw.polygon(
                display,
                self.colors['scroll_indicator'],
                [(arrow_x, arrow_y + 6), (arrow_x - 8, arrow_y - 2), (arrow_x + 8, arrow_y - 2)]
            )
        
        # Affichage des options visibles
        for i in range(start_idx, end_idx):
            local_index = i - start_idx
            option = options[i]
            display_name = self.menu.translations.get(option, option.upper())
            
            is_selected = (i == selected_index)
            
            # Vérification de l'état du niveau
            is_accessible = True
            is_completed = False
            
            if self.level_manager and option != "lobby":
                is_accessible = self.level_manager.is_level_accessible(option)
                is_completed = self.level_manager.is_level_completed(option)
            
            # Couleurs selon l'état du niveau
            if not is_accessible:
                bg_color = (30, 30, 30)
                text_color = self.colors['option_locked']
            elif is_completed:
                bg_color = self.colors['option_selected_bg'] if is_selected else (20, 90, 50)
                text_color = self.colors['option_completed'] if is_selected else (180, 230, 180)
            else:
                bg_color = self.colors['option_selected_bg'] if is_selected else self.colors['option_bg']
                text_color = self.colors['option_selected'] if is_selected else self.colors['option_normal']
            
            # Dimensions ajustées pour l'option sélectionnée
            actual_width = option_width + (10 if is_selected else 0)
            actual_height = option_height + (4 if is_selected else 0)
            
            option_y = start_y + (local_index * (option_height + option_padding))
            option_rect = pygame.Rect(
                menu_center_x - actual_width // 2,
                option_y - (2 if is_selected else 0),
                actual_width,
                actual_height
            )
            
            # Fond de l'option
            pygame.draw.rect(
                display, 
                bg_color, 
                option_rect,
                border_radius=12
            )
            
            # Bordure de l'option
            border_width = 3 if is_selected else 1
            border_color = (255, 255, 255, 160) if is_selected else (255, 255, 255, 60)
            border_rect = pygame.Rect(
                option_rect.x + border_width//2,
                option_rect.y + border_width//2,
                option_rect.width - border_width,
                option_rect.height - border_width
            )
            pygame.draw.rect(
                display, 
                border_color, 
                border_rect,
                border_width, 
                border_radius=12 - border_width//2
            )
            
            # Effet de halo pour l'option sélectionnée
            if is_selected and is_accessible:
                glow_surf = pygame.Surface((actual_width + 20, actual_height + 20), pygame.SRCALPHA)
                pygame.draw.rect(
                    glow_surf,
                    (50, 200, 100, 40),
                    (0, 0, actual_width + 20, actual_height + 20),
                    border_radius=15
                )
                display.blit(
                    glow_surf, 
                    (option_rect.x - 10, option_rect.y - 10)
                )
            
            # Indicateur de niveau complété
            if is_completed:
                check_circle_radius = 14
                check_circle_x = option_rect.x + 25
                check_circle_y = option_rect.y + option_rect.height // 2

                # Halo pour niveau complété
                for r in range(3):
                    alpha = 120 - (r * 30)
                    pygame.draw.circle(
                        display,
                        (80, 255, 120, alpha),
                        (check_circle_x, check_circle_y),
                        check_circle_radius + r
                    )

                # Cercle intérieur
                pygame.draw.circle(
                    display,
                    (30, 150, 70),
                    (check_circle_x, check_circle_y),
                    check_circle_radius
                )

                # Dessin de la coche
                check_color = (220, 255, 220)
                cx, cy = check_circle_x, check_circle_y

                # Première ligne de la coche
                pygame.draw.line(
                    display,
                    check_color,
                    (cx - 5, cy),
                    (cx - 2, cy + 3),
                    2
                )

                # Seconde ligne de la coche
                pygame.draw.line(
                    display,
                    check_color,
                    (cx - 2, cy + 3),
                    (cx + 5, cy - 4),
                    2
                )

                # Texte "Complété"
                status_font = pygame.font.SysFont(None, 16)
                status_text = status_font.render("COMPLÉTÉ", True, (150, 255, 150))
                display.blit(
                    status_text,
                    (option_rect.x + option_rect.width - status_text.get_width() - 15,
                     option_rect.y + option_rect.height - status_text.get_height() - 8)
                )
                
            # Indicateur de niveau verrouillé
            if not is_accessible:
                lock_circle_radius = 14
                lock_circle_x = option_rect.x + 25
                lock_circle_y = option_rect.y + option_rect.height // 2
                
                # Cercle rouge pour niveau verrouillé
                for r in range(3):
                    alpha = 100 - (r * 25)
                    pygame.draw.circle(
                        display,
                        (180, 50, 50, alpha),
                        (lock_circle_x, lock_circle_y),
                        lock_circle_radius + r
                    )
                
                # Cercle intérieur
                pygame.draw.circle(
                    display,
                    (100, 30, 30),
                    (lock_circle_x, lock_circle_y),
                    lock_circle_radius
                )
                
                # Dessin du cadenas
                lock_width = 10
                lock_height = 12
                base_x = lock_circle_x - lock_width // 2
                base_y = lock_circle_y - lock_height // 2 + 2
                
                # Base du cadenas
                pygame.draw.rect(
                    display,
                    (220, 220, 220),
                    (base_x, base_y, lock_width, lock_height),
                    border_radius=2
                )
                
                # Anse du cadenas
                shackle_width = 6
                pygame.draw.rect(
                    display,
                    (220, 220, 220),
                    (base_x + lock_width//2 - shackle_width//2, 
                     base_y - 6, 
                     shackle_width, 7),
                    border_radius=2
                )
                
                # Trou de serrure
                pygame.draw.circle(
                    display,
                    (80, 30, 30),
                    (lock_circle_x, lock_circle_y + 2),
                    2
                )
                
                # Texte "Verrouillé"
                status_font = pygame.font.SysFont(None, 16)
                status_text = status_font.render("VERROUILLÉ", True, (200, 100, 100))
                display.blit(
                    status_text,
                    (option_rect.x + option_rect.width - status_text.get_width() - 15,
                     option_rect.y + option_rect.height - status_text.get_height() - 8)
                )
            
            # Nom de l'option
            text = self.option_font.render(display_name, True, text_color)
            text_x = menu_center_x - text.get_width() // 2
            text_y = option_rect.y + (option_rect.height - text.get_height()) // 2
            display.blit(text, (text_x, text_y))
    
    def update(self, keys):
        pass
    
    def set_proximity(self, is_near):
        self.proximity_indicator = is_near
    
    def show_menu(self):
        self.menu.show()
    
    def hide_menu(self):
        self.menu.hide()
    
    @property
    def menu_visible(self):
        return self.menu.is_visible()
    
    def get_selected_destination(self):
        selected = self.menu.get_selected_option()
        
        # Vérification que le niveau sélectionné est accessible
        if self.level_manager and selected != "lobby":
            if not (selected == "level5" or self.level_manager.is_level_accessible(selected)):
                return None
        
        return selected
    
    def select_next(self):
        self.menu.select_next()
    
    def select_previous(self):
        self.menu.select_previous()
    
    def activate(self):
        self.activated = True
        self.show_menu()
        return "teleport_menu_opened"