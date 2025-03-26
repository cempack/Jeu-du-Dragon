import pygame
import math
from Modules.spriteSheet import SpriteSheet
import random
from Modules.menu import Menu
from Modules.font_manager import get_font

class Portal:
    def __init__(self, x, y, w, h, image):
        self.x, self.y, self.w, self.h, self.image = x, y, 48, 48, image
        self.collide = False
        self.collectable = False
        self.topoffset = 0
        self.xoffset = 0
        
        # Animation du portail
        self.animation_length = 11
        portal_sheet = SpriteSheet(pygame.image.load("./Assets/Terrain/portal.png"))
        self.animation = [portal_sheet.getimage(32 * x, 0, 32, 32) for x in range(self.animation_length)]
        self.animation_state = 0
        
        # Délai d'animation
        self.delay = 4
        self.currDelay = 0
        
        # Propriétés du portail
        self.destination = "lobby"
        self.is_active = False  # Le portail est inactif jusqu'à ce que le niveau soit terminé
        self.prompt_visible = False
        
        # Propriétés du quiz
        self.quiz_visible = False
        self.selected_answer = 0
        self.wrong_attempts = 0
        self.max_attempts = 2
        self.answer_result = None  # None, "correct", "wrong"
        self.result_timer = 0
        self.current_question = None
        
        # Création du menu pour le quiz
        self.quiz_menu = Menu(width=500, height=500, title="RÉPONDEZ À LA QUESTION")
        
        # Chargement des polices avec FontManager
        self.title_font = get_font('bold', 'large')
        self.question_font = get_font('bold', 'medium')
        self.option_font = get_font('bold', 'medium')
        self.instruction_font = get_font('regular', 'small')
            
        # Couleurs
        self.colors = {
            'bg': (20, 70, 45),
            'border': (10, 112, 48),
            'title': (255, 255, 255),
            'title_underline': (35, 123, 89),
            'option_normal': (220, 255, 220),
            'option_bg': (15, 85, 40),
            'option_selected': (255, 255, 255),
            'option_selected_bg': (30, 130, 70),
            'option_wrong': (255, 100, 100),
            'option_wrong_bg': (130, 30, 30),
            'option_correct': (100, 255, 100),
            'option_correct_bg': (30, 130, 30),
            'instructions': (180, 255, 180),
            'key_bg': (10, 90, 50),
        }
        
        # Questions par niveau
        self.questions = {
            "level1": [
                {
                    "question": "Quelle est la capitale de la France ?",
                    "options": ["Paris", "Londres", "Berlin", "Madrid"],
                    "correct": 0
                },
                {
                    "question": "Combien font 10 × 3 ?",
                    "options": ["3", "13", "30", "10"],
                    "correct": 2
                },
                {
                    "question": "Aller, est un verbes de quel groupe ?",
                    "options": ["1er groupe", "2ème groupe", "3ème groupe", "Aucune de ces réponses"],
                    "correct": 2
                },
                {
                    "question": "Qui a découvert l'Amérique en 1492 ?",
                    "options": ["Jean-Luc Reichmann", "Vangelis", "Marine Le Pen", "Christophe Colomb"],
                    "correct": 3
                },
                {
                    "question": "Comment dit-on, Bonjours, en anglais ?",
                    "options": ["Ohayo", "Hello", "Bonjours", "Good-bye"],
                    "correct": 1
                },
                {
                    "question": "Le soleil tourne t'il autour de la Terre ?",
                    "options": ["Non", "Oui", "Pas souvent", "Souvent"],
                    "correct": 0
                },
                {
                    "question": "Une voiture est ?",
                    "options": ["Un animal rare", "Une musique", "Une marque de téléphone", "Un moyen de transport"],
                    "correct": 3
                }
            ],
            "level2": [
                {
                    "question": "Combien font 8 × 9 ?",
                    "options": ["63", "72", "81", "90"],
                    "correct": 1
                },
                {
                    "question": "Quel est le plus grand mammifère terrestre?",
                    "options": ["Rhinocéros", "Éléphant d'Afrique", "Girafe", "Hippopotame"],
                    "correct": 1
                },
                {
                    "question": "La phrase, il fit preuve de courage et de bonté ?",
                    "options": ["Simple", "Dynamique", "Averbale", "Complexe"],
                    "correct": 0
                },
                {
                    "question": "Un en anglais se dit ?",
                    "options": ["Uno", "Un", "One", "A"],
                    "correct": 2
                },
                {
                    "question": "L'Antiquité se termine en ?",
                    "options": ["-3300 av JC", "l'année 0", "L'année 476", "L'année 1789"],
                    "correct": 1
                },
                {
                    "question": "Un atome est constitué de ?",
                    "options": ["Électrons", "Protons", "Neutrons", "Des trois"],
                    "correct": 3
                },
                {
                    "question": "Le Nil est un fleuve ?",
                    "options": ["Européen", "Asiatique", "Américain", "Africain"],
                    "correct": 3
                }
                
            ],
            "level3": [
                {
                    "question": "Comment dit on, Joyeux anniversaire, en anglais ?",
                    "options": ["Happy Birthday", "Merry Christmas", "Happy New Year", "Happy Valentine's Day"],
                    "correct": 0
                },
                {
                    "question": "Combien font 100 ÷ 12 ?",
                    "options": ["6", "7", "8", "9"],
                    "correct": 2
                },
                {
                    "question": "Vagabonder signifie ?",
                    "options": ["Etre dans un wagon bondé", "Marché vers chez sois", "Marcher sans but", "Crier sans but"],
                    "correct": 2
                },
                {
                    "question": "Quand est mort Louis XVI ?",
                    "options": ["En 1789", "En 1793", "En 1796", "En 1803"],
                    "correct": 1
                },
                {
                    "question": "La première coupe du monde de football remporter par la France a était remporté en ?",
                    "options": ["1984", "1998", "2016", "2018"],
                    "correct": 1
                },
                {
                    "question": "Combien de pays contient l'Union Européenne ?",
                    "options": ["27", "28", "30", "35"],
                    "correct": 0
                },
                {
                    "question": "La fusion, en physique, est le passage de l'eau ?",
                    "options": ["Liquide vers solide", "Gazeux vers solide", "Liquide vers gazeux", "Solide vers liquide"],
                    "correct": 3
                }
            ],
            "level4": [
                {
                    "question": "Quelle était la déesse grec de la magie ?",
                    "options": ["Géras", "Némésis", "Hestia", "Hécate"],
                    "correct": 3
                },
                {
                    "question": "Completez la phrase: Dès que le passant glissa sur la peau de banane, vous ... aux éclats.",
                    "options": ["Riâtes", "Rîtes", "Riîtes", "Râtes"],
                    "correct": 1
                },
                {
                    "question": "Combien fait 14 au carré ?",
                    "options": ["192", "194", "196", "198"],
                    "correct": 2
                },
                {
                    "question": "Dans quel pays se trouve l'Everest ?",
                    "options": ["Chine", "Népal", "Bhoutan", "Inde"],
                    "correct": 1
                },
                {
                    "question": "Quel est le prétérite du verbe Blow ?",
                    "options": ["Blew", "Blowed", "Blow", "Blown"],
                    "correct": 0
                },
                {
                    "question": "Les personnages : Mercutio, Frère Laurent, Tybalt, Benvolio. Sont extrait de quelle oeuvre ?",
                    "options": ["Le songe d'une nuit d'été", "Hamlet", "Othello", "Roméo et Juliette"],
                    "correct": 3
                },
                {
                    "question": "Lequel de ces organes n'est pas un organe vitale ?",
                    "options": ["Cerveau", "Peau", "Coeur", "Rate"],
                    "correct": 3
                }
            ]
        }
        
    def draw(self, display):
        # Dessine l'animation du portail
        image = self.animation[self.animation_state % self.animation_length]
        scaled_image = pygame.transform.scale(image, (self.w, self.h))
        
        # Applique la transparence si inactif
        if not self.is_active:
            temp = scaled_image.copy()
            temp.set_alpha(100)
            display.blit(temp, (self.x, self.y))
        else:
            display.blit(scaled_image, (self.x, self.y))
        
        # Mise à jour de l'animation
        if self.currDelay == self.delay:
            self.animation_state += 1
            self.currDelay = 0
        else:
            self.currDelay += 1
            
        # Affiche le prompt si le portail est actif et le joueur est à proximité
        if self.is_active and self.prompt_visible and not self.quiz_visible:
            prompt_surf = self.create_prompt_surface()
            prompt_x = self.x + self.w//2 - prompt_surf.get_width()//2
            prompt_y = self.y - prompt_surf.get_height() - 60
            display.blit(prompt_surf, (prompt_x, prompt_y))
        
    def create_prompt_surface(self):
        font = get_font('bold', 'small')
        text = font.render("APPUYEZ SUR E", True, (255, 255, 255))
        
        width = text.get_width() + 20
        height = text.get_height() + 16
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Rend le fond plus visible
        pygame.draw.rect(
            surface, 
            (10, 112, 48, 230),
            (0, 0, width, height),
            border_radius=8
        )
        
        # Ajoute une bordure plus marquée
        pygame.draw.rect(
            surface,
            (35, 123, 89),
            (1, 1, width-2, height-2),
            2,
            border_radius=8
        )
        
        surface.blit(text, (10, 8))
        return surface
        
    def draw_quiz(self, display):
        display_width, display_height = display.get_width(), display.get_height()

        menu_width = 500
        menu_height = 480
        menu_x = display_width // 2 - menu_width // 2
        menu_y = display_height // 2 - menu_height // 2

        # Création d'une surface pour le menu avec transparence
        menu_surface = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)

        # Dessine le fond du rectangle arrondi en utilisant la méthode du Menu
        self.quiz_menu.draw_rounded_rect(menu_surface, self.colors['bg'], 
                          (0, 0, menu_width, menu_height), 20)

        # Dessine la bordure
        border_width = 4
        pygame.draw.rect(menu_surface, self.colors['border'], 
                      (border_width//2, border_width//2, 
                       menu_width - border_width, menu_height - border_width), 
                      border_width, 20 - border_width//2)

        # Affiche la surface du menu
        display.blit(menu_surface, (menu_x, menu_y))

        # Dessine le titre
        title_text = self.title_font.render("RÉPONDEZ À LA QUESTION", True, self.colors['title'])
        title_x = display_width // 2 - title_text.get_width() // 2
        title_y = menu_y + 30

        display.blit(title_text, (title_x, title_y))

        # Dessine le soulignement
        line_width = title_text.get_width() + 20
        pygame.draw.line(display, self.colors['title_underline'], 
                        (title_x - 10, title_y + title_text.get_height() + 5), 
                        (title_x + title_text.get_width() + 10, title_y + title_text.get_height() + 5), 3)

        # Dessine la question
        if self.current_question:
            # Traitement du texte de la question
            question_text = self.current_question["question"]
            question_y = title_y + 50

            max_width = menu_width - 60
            words = question_text.split(' ')
            lines = []
            current_line = words[0]

            for word in words[1:]:
                test_line = current_line + " " + word
                text_width = self.question_font.size(test_line)[0]
                if text_width <= max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            lines.append(current_line)

            # Calcule la hauteur de la boîte de question
            line_height = self.question_font.get_linesize()
            question_box_height = len(lines) * line_height + 20

            # Dessine le fond de la question
            question_bg_rect = pygame.Rect(
                display_width // 2 - (max_width + 20) // 2,
                question_y - 10,
                max_width + 20,
                question_box_height
            )
            pygame.draw.rect(
                display, 
                (15, 60, 35),
                question_bg_rect,
                border_radius=10
            )

            # Dessine chaque ligne de la question
            for i, line in enumerate(lines):
                line_surface = self.question_font.render(line, True, (255, 255, 255))
                line_x = display_width // 2 - line_surface.get_width() // 2
                line_y = question_y + i * line_height
                display.blit(line_surface, (line_x, line_y))

            # Dessine les options
            options_start_y = question_y + question_box_height + 15
            option_height = 45
            option_width = 380
            option_spacing = 12

            for i, option in enumerate(self.current_question["options"]):
                option_y = options_start_y + i * (option_height + option_spacing)

                # Détermine les couleurs selon le statut
                bg_color = self.colors['option_bg']
                text_color = self.colors['option_normal']

                # Option sélectionnée
                if i == self.selected_answer:
                    bg_color = self.colors['option_selected_bg']
                    text_color = self.colors['option_selected']

                # Réponse correcte ou incorrecte
                if self.answer_result is not None:
                    if i == self.current_question["correct"] and self.answer_result == "correct":
                        bg_color = self.colors['option_correct_bg']
                        text_color = self.colors['option_correct']
                    elif i == self.selected_answer and self.answer_result == "wrong":
                        bg_color = self.colors['option_wrong_bg']
                        text_color = self.colors['option_wrong']

                # Dessine le fond de l'option
                option_rect = pygame.Rect(
                    display_width // 2 - option_width // 2,
                    option_y,
                    option_width,
                    option_height
                )

                pygame.draw.rect(
                    display, 
                    bg_color, 
                    option_rect,
                    border_radius=10
                )

                # Dessine la bordure si sélectionnée ou montrant le résultat
                if i == self.selected_answer or (self.answer_result == "correct" and i == self.current_question["correct"]):
                    border_width = 2
                    border_color = (255, 255, 255, 160)
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
                        border_radius=10 - border_width//2
                    )

                # Dessine le texte de l'option avec troncature si nécessaire
                option_text = option
                if self.option_font.size(option_text)[0] > option_width - 80:
                    while self.option_font.size(option_text + "...")[0] > option_width - 80 and len(option_text) > 0:
                        option_text = option_text[:-1]
                    option_text += "..."

                text_surface = self.option_font.render(option_text, True, text_color)
                text_x = option_rect.x + 45 if self.answer_result is not None else option_rect.x + 20
                text_y = option_y + (option_height - text_surface.get_height()) // 2
                display.blit(text_surface, (text_x, text_y))

                # Dessine la coche ou la croix si le résultat est affiché
                if self.answer_result is not None:
                    indicator_radius = 12
                    indicator_x = option_rect.x + 22
                    indicator_y = option_rect.y + option_rect.height // 2

                    if i == self.current_question["correct"] and self.answer_result == "correct":
                        # Dessine un cercle lumineux pour la bonne réponse
                        for r in range(2):
                            alpha = 120 - (r * 30)
                            pygame.draw.circle(
                                display,
                                (80, 255, 120, alpha),
                                (indicator_x, indicator_y),
                                indicator_radius + r
                            )

                        # Cercle intérieur solide
                        pygame.draw.circle(
                            display,
                            (30, 150, 70),
                            (indicator_x, indicator_y),
                            indicator_radius
                        )

                        # Dessine une coche
                        check_color = (220, 255, 220)
                        cx, cy = indicator_x, indicator_y

                        # Première ligne (partie courte de la coche)
                        pygame.draw.line(
                            display,
                            check_color,
                            (cx - 4, cy),
                            (cx - 2, cy + 3),
                            2
                        )

                        # Seconde ligne (partie longue de la coche)
                        pygame.draw.line(
                            display,
                            check_color,
                            (cx - 2, cy + 3),
                            (cx + 4, cy - 4),
                            2
                        )

                    # Dessine une croix pour une réponse incorrecte
                    elif i == self.selected_answer and self.answer_result == "wrong":
                        # Dessine un cercle lumineux pour la mauvaise réponse
                        for r in range(2):
                            alpha = 120 - (r * 30)
                            pygame.draw.circle(
                                display,
                                (255, 80, 80, alpha),
                                (indicator_x, indicator_y),
                                indicator_radius + r
                            )

                        # Cercle intérieur solide
                        pygame.draw.circle(
                            display,
                            (150, 30, 30),
                            (indicator_x, indicator_y),
                            indicator_radius
                        )

                        # Dessine un X
                        cross_color = (255, 220, 220)
                        cx, cy = indicator_x, indicator_y
                        size = 5

                        pygame.draw.line(
                            display,
                            cross_color,
                            (cx - size, cy - size),
                            (cx + size, cy + size),
                            2
                        )

                        pygame.draw.line(
                            display,
                            cross_color,
                            (cx + size, cy - size),
                            (cx - size, cy + size),
                            2
                        )

            # Calcule la hauteur totale nécessaire pour les options
            total_options_height = len(self.current_question["options"]) * (option_height + option_spacing) - option_spacing

            # Dessine les instructions ou le message d'état
            instructions_y = options_start_y + total_options_height + 20

            # Affiche le message d'état si le résultat est montré
            if self.answer_result is not None:
                if self.answer_result == "correct":
                    status_text = self.instruction_font.render("Bonne réponse! Téléportation...", True, (100, 255, 100))
                else:
                    attempts_left = self.max_attempts - self.wrong_attempts
                    if attempts_left > 0:
                        status_text = self.instruction_font.render(
                            f"Mauvaise réponse! {attempts_left} essai{'s' if attempts_left > 1 else ''} restant{'s' if attempts_left > 1 else ''}.", 
                            True, (255, 100, 100))
                    else:
                        status_text = self.instruction_font.render(
                            "Échec! Retour au lobby...", 
                            True, (255, 100, 100))

                # Dessine le texte d'état
                status_x = display_width // 2 - status_text.get_width() // 2
                display.blit(status_text, (status_x, instructions_y))
            else:
                # Montre simplement les contrôles de navigation pendant la réponse
                self.draw_navigation_help(display, menu_x, menu_y, menu_width, instructions_y, "selection")

    def draw_navigation_help(self, display, menu_x, menu_y, menu_width, help_y, mode="selection"):
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

                # Dessine la flèche
                direction = instruction["direction"]
                x, y = center_x, help_y + key_size // 2
                color = (255, 255, 255)

                if direction == "up":
                    points = [(x, y - 6), (x - 8, y + 2), (x + 8, y + 2)]
                elif direction == "down":
                    points = [(x, y + 6), (x - 8, y - 2), (x + 8, y - 2)]

                pygame.draw.polygon(display, color, points)

                # Dessine le texte d'instruction
                desc_text = self.instruction_font.render(instruction["text"], True, self.colors['instructions'])
                display.blit(
                    desc_text, 
                    (center_x - desc_text.get_width() // 2, help_y + key_size + 5)
                )

            else:
                key_text = self.instruction_font.render(instruction["key"], True, self.colors['option_selected'])
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
        
    def update(self, keys):
        # Gestion du timer de résultat
        if self.answer_result is not None:
            self.result_timer += 1
            if self.result_timer > 120:  # 2 secondes
                self.result_timer = 0
                
                # Traite le résultat selon la réponse
                if self.answer_result == "correct":
                    # Succès - procède à la téléportation
                    self.hide_quiz()
                    return "teleport"
                else:
                    # Échec
                    if self.wrong_attempts >= self.max_attempts:
                        # Trop de mauvaises tentatives, retour au lobby
                        self.hide_quiz()
                        self.wrong_attempts = 0
                        return "teleport_to_lobby"
                    else:
                        # Réinitialisation pour une autre tentative
                        self.answer_result = None
    
    def activate(self):
        """Active le portail quand le niveau est terminé"""
        self.is_active = True
    
    def deactivate(self):
        """Désactive le portail"""
        self.is_active = False
        self.prompt_visible = False
        
    def check_proximity(self, player):
        """Vérifie si le joueur est assez proche pour afficher le prompt"""
        if self.is_active:
            proximity = (
                abs(player.x + player.w/2 - (self.x + self.w/2)) < 50 and
                abs(player.y + player.h - (self.y + self.h/2)) < 50
            )
            self.prompt_visible = proximity
        else:
            self.prompt_visible = False
        return self.prompt_visible
        
    def show_quiz(self, level_name):
        """Affiche le quiz pour ce portail si le niveau a des questions"""
        # Ne pas afficher de quiz pour le niveau 5 (combat du dragon)
        if level_name == "level5":
            return "teleport"  # Passe le quiz pour le niveau 5
            
        # Récupère une question pour ce niveau
        if level_name in self.questions and self.questions[level_name]:
            self.current_question = random.choice(self.questions[level_name])
            self.selected_answer = 0
            self.quiz_visible = True
            self.answer_result = None
            return "quiz_shown"
        else:
            # Pas de questions pour ce niveau, téléportation directe
            return "teleport"
    
    def hide_quiz(self):
        """Cache le menu du quiz"""
        self.quiz_visible = False
        self.current_question = None
    
    def select_next(self):
        """Passe à l'option de réponse suivante"""
        if self.quiz_visible and self.current_question and self.answer_result is None:
            self.selected_answer = (self.selected_answer + 1) % len(self.current_question["options"])
    
    def select_previous(self):
        """Passe à l'option de réponse précédente"""
        if self.quiz_visible and self.current_question and self.answer_result is None:
            self.selected_answer = (self.selected_answer - 1) % len(self.current_question["options"])
    
    def confirm_answer(self):
        """Soumet la réponse sélectionnée et vérifie si elle est correcte"""
        if self.quiz_visible and self.current_question and self.answer_result is None:
            if self.selected_answer == self.current_question["correct"]:
                self.answer_result = "correct"
            else:
                self.answer_result = "wrong"
                self.wrong_attempts += 1
            return self.answer_result
        return None