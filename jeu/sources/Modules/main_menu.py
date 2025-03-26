import pygame
import math
import os
from Modules.menu import Menu
from Modules.font_manager import get_font

class MainMenu:
    def __init__(self, display_width, display_height):
        self.display_width = display_width
        self.display_height = display_height
        
        # Initialisation des éléments graphiques
        self._load_background()
        self._load_fonts()
        self._setup_colors()
        self._load_play_button()
        self._load_sound_icons()
        
        # Dimensions et position du bouton
        self.button_width = 80
        self.button_height = 80
        self.button_x = display_width // 2 - self.button_width // 2
        self.button_y = 140
        
        # Configuration du champ de saisie du nom
        self.username = "Héros"
        self.username_active = False
        self.username_max_length = 12
        self.input_width = 300
        self.input_height = 40
        self.input_x = display_width // 2 - self.input_width // 2
        self.input_y = self.button_y + self.button_height + 20
        self.cursor_visible = True
        self.cursor_timer = 0
        
        # Texte des contrôles du jeu
        self.controls = [
            "CONTRÔLES:",
            "FLECHES GAUCHE / DROITE : Se déplacer",
            "ESPACE : Sauter (double saut possible)",
            "E : Interagir avec les objets",
            "Z : Attaquer"
        ]
        
        # Propriétés du bouton muet
        self.mute_button_size = 40
        self.mute_button_x = display_width - self.mute_button_size - 20
        self.mute_button_y = 20
        self.is_muted = False
    
    def _load_background(self):
        try:
            self.bg_image = pygame.image.load("./Assets/Terrain/bg.png")
        except:
            self.bg_image = None
            print("Impossible de charger l'image d'arrière-plan")
    
    def _load_fonts(self):
        self.title_font = get_font('bold', 'title')
        self.bold_font = get_font('bold', 'large')
        self.font = get_font('regular', 'medium')
        self.input_font = get_font('regular', 'large')
        self.small_font = get_font('regular', 'small')
    
    def _setup_colors(self):
        self.colors = {
            'bg': (20, 70, 45),              # Vert foncé
            'border': (10, 112, 48),         # Vert bordure
            'title': (255, 255, 255),        # Blanc
            'title_underline': (35, 123, 89), # Vert moyen
            'text': (255, 255, 255),         # Blanc
            'option_bg': (10, 112, 48),      # Vert bouton
            'input_bg': (5, 55, 30),         # Vert foncé (champ)
            'input_active': (35, 123, 89),   # Vert clair (actif)
            'shadow': (10, 50, 30)           # Ombre
        }
    
    def _load_play_button(self):
        try:
            self.play_button = pygame.image.load("./Assets/UI/play.png")
            self.play_button = pygame.transform.scale(self.play_button, (80, 80))
        except:
            self.play_button = None
            print("Impossible de charger l'image du bouton jouer")
    
    def _load_sound_icons(self):
        os.makedirs('./Assets/UI', exist_ok=True)
        
        try:
            self.sound_on_icon = pygame.image.load("./Assets/UI/sound_on.png")
            self.sound_off_icon = pygame.image.load("./Assets/UI/sound_off.png")
            
            icon_size = (40, 40)
            self.sound_on_icon = pygame.transform.scale(self.sound_on_icon, icon_size)
            self.sound_off_icon = pygame.transform.scale(self.sound_off_icon, icon_size)
        except:
            self.sound_on_icon = None
            self.sound_off_icon = None
            print("Impossible de charger les icônes de son")
    
    def draw_rounded_rect(self, surface, color, rect, radius):
        x, y, width, height = rect
        
        pygame.draw.rect(surface, color, (x + radius, y, width - 2*radius, height))
        pygame.draw.rect(surface, color, (x, y + radius, width, height - 2*radius))
        
        pygame.draw.circle(surface, color, (x + radius, y + radius), radius)
        pygame.draw.circle(surface, color, (x + width - radius, y + radius), radius)
        pygame.draw.circle(surface, color, (x + radius, y + height - radius), radius)
        pygame.draw.circle(surface, color, (x + width - radius, y + height - radius), radius)
    
    def draw(self, display):
        self._draw_background(display)
        self._draw_title(display)
        self._draw_username_input(display)
        self._draw_play_button(display)
        self._draw_instructions(display)
        self._draw_mute_button(display)
        self._draw_credits(display)
    
    def _draw_background(self, display):
        if self.bg_image:
            bg_width, bg_height = self.bg_image.get_size()
            for x in range(0, self.display_width, bg_width):
                for y in range(0, self.display_height, bg_height):
                    display.blit(self.bg_image, (x, y))
    
    def _draw_title(self, display):
        title_text = "LE JEU DU DRAGON"
        title = self.title_font.render(title_text, True, self.colors['title'])
        
        shadow = self.title_font.render(title_text, True, (30, 30, 30))
        shadow_offset = 3
        
        title_x = self.display_width // 2 - title.get_width() // 2
        title_y = 40
        
        display.blit(shadow, (title_x + shadow_offset, title_y + shadow_offset))
        display.blit(title, (title_x, title_y))
        
        line_width = title.get_width() + 40
        pygame.draw.line(display, self.colors['title_underline'], 
                        (self.display_width//2 - line_width//2, title_y + title.get_height() + 10), 
                        (self.display_width//2 + line_width//2, title_y + title.get_height() + 10), 3)
    
    def _draw_username_input(self, display):
        title_text = "LE JEU DU DRAGON"
        title = self.title_font.render(title_text, True, self.colors['title'])
        title_y = 40
        
        name_label = self.bold_font.render("VOTRE NOM:", True, self.colors['text'])
        name_x = self.display_width // 2 - name_label.get_width() // 2
        display.blit(name_label, (name_x, title_y + title.get_height() + 30))
        
        input_rect = pygame.Rect(
            self.display_width // 2 - self.input_width // 2,
            title_y + title.get_height() + 60,
            self.input_width, 
            self.input_height
        )
        self.input_y = input_rect.y
        
        input_border_color = self.colors['input_active'] if self.username_active else self.colors['border']
        
        pygame.draw.rect(display, self.colors['input_bg'], input_rect, border_radius=10)
        pygame.draw.rect(display, input_border_color, input_rect, 2, border_radius=10)
        
        indicator_x = input_rect.x + 15
        indicator_y = input_rect.y + input_rect.height // 2
        pygame.draw.circle(display, self.colors['text'], (indicator_x, indicator_y), 4)
        
        username_text = self.input_font.render(self.username, True, self.colors['text'])
        username_x = input_rect.x + 25
        username_y = input_rect.y + (self.input_height - username_text.get_height()) // 2
        display.blit(username_text, (username_x, username_y))
        
        if self.username_active:
            self.cursor_timer += 1
            if self.cursor_timer >= 30:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0
                
            if self.cursor_visible:
                cursor_x = username_x + username_text.get_width() + 2
                cursor_y = username_y
                pygame.draw.line(display, self.colors['text'], 
                              (cursor_x, cursor_y), 
                              (cursor_x, cursor_y + username_text.get_height()), 2)
    
    def _draw_play_button(self, display):
        title_text = "LE JEU DU DRAGON"
        title = self.title_font.render(title_text, True, self.colors['title'])
        title_y = 40
        
        input_rect_y = title_y + title.get_height() + 60
        self.button_y = input_rect_y + self.input_height + 30
        
        if self.play_button:
            display.blit(self.play_button, (self.button_x, self.button_y))
            
            play_text = self.bold_font.render("JOUER", True, self.colors['title'])
            play_text_width = play_text.get_width() + 20
            play_text_height = play_text.get_height() + 10
            play_rect = pygame.Rect(
                self.display_width // 2 - play_text_width // 2,
                self.button_y + self.button_height + 10,
                play_text_width,
                play_text_height
            )
            
            pygame.draw.rect(display, self.colors['option_bg'], play_rect, border_radius=10)
            
            play_x = self.display_width // 2 - play_text.get_width() // 2
            display.blit(play_text, (play_x, play_rect.y + 5))
    
    def _draw_instructions(self, display):
        instructions_width = 500
        instructions_height = 200
        instructions_x = self.display_width // 2 - instructions_width // 2
        instructions_y = self.button_y + self.button_height + 80
        
        instructions_surface = pygame.Surface((instructions_width, instructions_height), pygame.SRCALPHA)
        
        border_radius = 20
        self.draw_rounded_rect(instructions_surface, self.colors['bg'], 
                           (0, 0, instructions_width, instructions_height), border_radius)
        
        border_width = 4
        pygame.draw.rect(instructions_surface, self.colors['border'], 
                      (border_width//2, border_width//2, 
                       instructions_width - border_width, instructions_height - border_width), 
                      border_width, border_radius - border_width//2)
        
        y_offset = 25
        for i, text in enumerate(self.controls):
            instruction = self.font.render(text, True, self.colors['text'])
            x = instructions_width // 2 - instruction.get_width() // 2
            instructions_surface.blit(instruction, (x, y_offset + i * 35))
        
        display.blit(instructions_surface, (instructions_x, instructions_y))
    
    def _draw_mute_button(self, display):
        current_icon = self.sound_off_icon if self.is_muted else self.sound_on_icon
        
        button_surface = pygame.Surface((self.mute_button_size, self.mute_button_size), pygame.SRCALPHA)
        pygame.draw.circle(button_surface, (*self.colors['bg'], 200), 
                        (self.mute_button_size//2, self.mute_button_size//2), 
                        self.mute_button_size//2)
        
        pygame.draw.circle(button_surface, self.colors['border'], 
                        (self.mute_button_size//2, self.mute_button_size//2), 
                        self.mute_button_size//2, 2)
        
        display.blit(button_surface, (self.mute_button_x, self.mute_button_y))
        if current_icon:
            display.blit(current_icon, (self.mute_button_x, self.mute_button_y))
    
    def _draw_credits(self, display):
        credits_text = "Ce jeu a été créé par Elliot et William"
        credits = self.small_font.render(credits_text, True, self.colors['text'])
        credits_x = self.display_width // 2 - credits.get_width() // 2
        credits_y = self.display_height - credits.get_height() - 10
        display.blit(credits, (credits_x, credits_y))
    
    def handle_input_event(self, event):
        if not self.username_active:
            return
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.username = self.username[:-1]
            elif event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                self.username_active = False
            elif len(self.username) < self.username_max_length:
                if event.unicode.isalnum() or event.unicode in " -_":
                    self.username += event.unicode
                    
    def check_button_click(self, mouse_pos):
        x, y = mouse_pos
        button_rect = pygame.Rect(self.button_x, self.button_y, self.button_width, self.button_height)
        return button_rect.collidepoint(x, y)
    
    def check_input_field_click(self, mouse_pos):
        x, y = mouse_pos
        input_rect = pygame.Rect(
            self.display_width // 2 - self.input_width // 2,
            self.input_y,
            self.input_width,
            self.input_height
        )
        was_active = self.username_active
        self.username_active = input_rect.collidepoint(x, y)
        
        if not was_active and self.username_active:
            self.cursor_visible = True
            self.cursor_timer = 0
            
        return self.username_active
    
    def check_mute_button_click(self, mouse_pos):
        x, y = mouse_pos
        button_center = (self.mute_button_x + self.mute_button_size//2, 
                        self.mute_button_y + self.mute_button_size//2)
        distance = math.sqrt((x - button_center[0])**2 + (y - button_center[1])**2)
        
        if distance <= self.mute_button_size//2:
            self.is_muted = not self.is_muted
            return True
        return False
        
    def get_username(self):
        if self.username.strip() == "":
            return "Héros"
        return self.username