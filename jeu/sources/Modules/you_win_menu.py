import pygame
from Modules.font_manager import get_font

class YouWinMenu:
    def __init__(self, display_width, display_height):
        self.display_width = display_width
        self.display_height = display_height
        self.username = "Héros"
        
        # Initialisation des éléments d'interface
        self._load_background()
        self._load_fonts()
        self._setup_colors()
        
        # Positionnement vertical des éléments
        self.title_y = int(display_height * 0.15)
        self.message_y = int(display_height * 0.35)
        
        # Dimensions et position du bouton de sortie
        self.button_width = 200
        self.button_height = 60
        self.button_x = display_width // 2 - self.button_width // 2
        self.button_y = int(display_height * 0.7)
    
    def _load_background(self):
        try:
            self.bg_image = pygame.image.load("./Assets/Terrain/bg.png")
        except:
            self.bg_image = None
            print("Échec du chargement de l'image d'arrière-plan")
    
    def _load_fonts(self):
        self.title_font = get_font('bold', 'title')
        self.bold_font = get_font('bold', 'large')
        self.font = get_font('regular', 'medium')
        self.small_font = get_font('regular', 'small')
    
    def _setup_colors(self):
        self.colors = {
            'bg': (20, 70, 45),               # Fond vert foncé
            'border': (10, 112, 48),          # Bordure verte
            'title': (255, 255, 255),         # Texte blanc
            'title_underline': (35, 123, 89), # Accent vert clair
            'text': (255, 255, 255),          # Texte blanc
            'option_bg': (10, 112, 48),       # Fond bouton vert
            'button_hover': (35, 123, 89),    # Surbrillance bouton
            'shadow': (10, 50, 30),           # Ombre verte foncée
        }
    
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
        self._draw_message(display)
        
        mouse_pos = pygame.mouse.get_pos()
        self._draw_exit_button(display, mouse_pos)
        self._draw_credits(display)
    
    def _draw_background(self, display):
        if self.bg_image:
            bg_width, bg_height = self.bg_image.get_size()
            for x in range(0, self.display_width, bg_width):
                for y in range(0, self.display_height, bg_height):
                    display.blit(self.bg_image, (x, y))
    
    def _draw_title(self, display):
        title_text = "VICTOIRE !"
        title = self.title_font.render(title_text, True, self.colors['title'])
        
        shadow = self.title_font.render(title_text, True, (30, 30, 30))
        shadow_offset = 3
        
        title_x = self.display_width // 2 - title.get_width() // 2
        
        display.blit(shadow, (title_x + shadow_offset, self.title_y + shadow_offset))
        display.blit(title, (title_x, self.title_y))
        
        line_width = title.get_width() + 40
        pygame.draw.line(display, self.colors['title_underline'], 
                        (self.display_width//2 - line_width//2, self.title_y + title.get_height() + 10), 
                        (self.display_width//2 + line_width//2, self.title_y + title.get_height() + 10), 3)
    
    def _draw_message(self, display):
        message_width = 500
        message_height = 180
        message_x = self.display_width // 2 - message_width // 2
        
        message_surface = pygame.Surface((message_width, message_height), pygame.SRCALPHA)
        
        border_radius = 20
        self.draw_rounded_rect(message_surface, self.colors['bg'], 
                          (0, 0, message_width, message_height), border_radius)
        
        border_width = 4
        pygame.draw.rect(message_surface, self.colors['border'], 
                      (border_width//2, border_width//2, 
                       message_width - border_width, message_height - border_width), 
                      border_width, border_radius - border_width//2)
        
        congratulation_text = f"Félicitations, {self.username} !"
        congratulation = self.bold_font.render(congratulation_text, True, self.colors['text'])
        
        dragon_text = "Vous avez vaincu le dragon PYROFLAMME"
        dragon_msg = self.font.render(dragon_text, True, self.colors['text'])
        
        end_text = "et terminé votre quête avec succès."
        end_msg = self.font.render(end_text, True, self.colors['text'])
        
        congrats_x = message_width // 2 - congratulation.get_width() // 2
        congrats_y = 30
        
        dragon_x = message_width // 2 - dragon_msg.get_width() // 2
        dragon_y = 80
        
        end_x = message_width // 2 - end_msg.get_width() // 2
        end_y = 120
        
        message_surface.blit(congratulation, (congrats_x, congrats_y))
        message_surface.blit(dragon_msg, (dragon_x, dragon_y))
        message_surface.blit(end_msg, (end_x, end_y))
        
        display.blit(message_surface, (message_x, self.message_y))
    
    def _draw_exit_button(self, display, mouse_pos):
        button_rect = pygame.Rect(self.button_x, self.button_y, self.button_width, self.button_height)
        
        hover = button_rect.collidepoint(mouse_pos)
        
        button_color = self.colors['button_hover'] if hover else self.colors['option_bg']
        pygame.draw.rect(display, button_color, button_rect, border_radius=15)
        pygame.draw.rect(display, self.colors['border'], button_rect, 2, border_radius=15)
        
        exit_text = self.bold_font.render("QUITTER", True, self.colors['title'])
        exit_x = self.button_x + (self.button_width - exit_text.get_width()) // 2
        exit_y = self.button_y + (self.button_height - exit_text.get_height()) // 2
        display.blit(exit_text, (exit_x, exit_y))
    
    def _draw_credits(self, display):
        credits_text = "Ce jeu a été créé par Elliot et William"
        credits = self.small_font.render(credits_text, True, self.colors['text'])
        credits_x = self.display_width // 2 - credits.get_width() // 2
        credits_y = self.display_height - credits.get_height() - 10
        display.blit(credits, (credits_x, credits_y))
    
    def check_button_click(self, mouse_pos):
        x, y = mouse_pos
        button_rect = pygame.Rect(self.button_x, self.button_y, self.button_width, self.button_height)
        return button_rect.collidepoint(x, y)