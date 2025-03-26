import pygame
import math
from pygame import mixer
from Modules.font_manager import get_font

class Dialog:
    def __init__(self, display_width, display_height):
        self.display_width = display_width
        self.display_height = display_height
        self.visible = False
        self.current_dialog = None
        self.current_sentence_index = 0
        self.text_progress = 0
        self.text_speed = 0.5  # Caractères par frame
        self.last_char_time = 0
        self.complete = False
        self.dialog_sound = None
        self.dialog_channel = None
        self.music_manager = None  # Référence au gestionnaire de musique
        self.original_music_volume = 1.0
        self.username = "Héros"  # Nom par défaut
        
        # Initialisation des polices avec FontManager
        self.dialog_font = get_font('regular', 'medium')
        self.continue_font = get_font('bold', 'small')
            
        # Propriétés de la boîte de dialogue
        self.box_width = int(display_width * 0.8)
        self.box_height = 150
        self.box_x = (display_width - self.box_width) // 2
        self.box_y = display_height - self.box_height - 20
        self.padding = 20
        
        # Couleurs de l'interface
        self.colors = {
            'bg': (20, 70, 45),             # Fond vert foncé
            'border': (10, 112, 48),        # Bordure verte
            'text': (255, 255, 255),        # Texte blanc
            'prompt': (144, 238, 144),      # Indicateur vert clair
            'shadow': (10, 50, 30)          # Ombre du texte
        }
        
        # Animation de l'indicateur
        self.indicator_animation = 0
        
        # Chargement du son de dialogue
        self.load_sound()
        
    def set_username(self, username):
        """Définit le nom du joueur pour les dialogues personnalisés"""
        if username and username.strip():
            self.username = username
    
    def set_music_manager(self, music_manager):
        """Définit la référence au gestionnaire de musique"""
        self.music_manager = music_manager

        # Synchronisation de l'état de sourdine
        if self.music_manager and self.music_manager.is_muted():
            if self.dialog_sound:
                self.dialog_sound.set_volume(0)

    def toggle_mute(self, is_muted):
        """Synchronise l'état de sourdine du son de dialogue"""
        if self.dialog_sound:
            if is_muted:
                self.dialog_sound.set_volume(0)
            else:
                self.dialog_sound.set_volume(0.3)
        
    def load_sound(self):
        """Charge l'effet sonore du dialogue"""
        try:
            self.dialog_sound = pygame.mixer.Sound("Assets/Sounds/dialog.mp3")
            self.dialog_sound.set_volume(0.3)
            self.dialog_channel = pygame.mixer.Channel(3)  # Canal réservé pour les dialogues
        except Exception as e:
            print(f"Échec du chargement du son de dialogue: {e}")
            
    def draw_rounded_rect(self, surface, color, rect, radius):
        """Dessine un rectangle arrondi sur la surface donnée"""
        x, y, width, height = rect
        
        pygame.draw.rect(surface, color, (x + radius, y, width - 2*radius, height))
        pygame.draw.rect(surface, color, (x, y + radius, width, height - 2*radius))
        
        pygame.draw.circle(surface, color, (x + radius, y + radius), radius)
        pygame.draw.circle(surface, color, (x + width - radius, y + radius), radius)
        pygame.draw.circle(surface, color, (x + radius, y + height - radius), radius)
        pygame.draw.circle(surface, color, (x + width - radius, y + height - radius), radius)
            
    def show(self, dialog_key):
        """Affiche un dialogue par sa clé"""
        if dialog_key in dialogs:
            self.current_dialog = dialogs[dialog_key]
            self.current_sentence_index = 0
            self.text_progress = 0
            self.complete = False
            self.visible = True
            self.last_char_time = pygame.time.get_ticks()
            
            # Baisse le volume de la musique pendant le dialogue
            if self.music_manager:
                self.original_music_volume = self.music_manager.get_volume()
                self.music_manager.set_volume(self.original_music_volume * 0.2)
                
            return True
        return False
        
    def hide(self):
        """Cache la boîte de dialogue"""
        self.visible = False
        self.stop_sound()
        
        # Restaure le volume de la musique
        if self.music_manager:
            self.music_manager.set_volume(self.original_music_volume)
        
    def is_visible(self):
        """Vérifie si le dialogue est visible"""
        return self.visible
        
    def update(self):
        """Met à jour l'animation du dialogue"""
        if not self.visible:
            return
            
        # Animation de l'indicateur
        self.indicator_animation = (self.indicator_animation + 0.05) % (2 * math.pi)
        
        # Gestion de l'animation du texte
        current_time = pygame.time.get_ticks()
        if not self.complete:
            elapsed = current_time - self.last_char_time
            if elapsed > 25:  # 25ms entre caractères
                self.text_progress += self.text_speed
                self.last_char_time = current_time
                
                # Joue le son si un nouveau caractère est ajouté
                if int(self.text_progress) > int(self.text_progress - self.text_speed):
                    self.play_sound()
                    
        # Vérifie si la phrase actuelle est complète
        current_sentences = self.current_dialog["sentences"]
        current_text = current_sentences[self.current_sentence_index]
        
        if int(self.text_progress) >= len(current_text):
            self.complete = True
            self.stop_sound()
            
    def play_sound(self):
        """Joue le son de frappe"""
        if self.dialog_sound and self.dialog_channel:
            if not self.dialog_channel.get_busy():
                self.dialog_channel.play(self.dialog_sound)
                
    def stop_sound(self):
        """Arrête le son de frappe"""
        if self.dialog_channel and self.dialog_channel.get_busy():
            self.dialog_channel.stop()
            
    def advance(self):
        """Avance à la phrase suivante ou termine le dialogue"""
        if not self.visible:
            return False
            
        # Si le texte est en cours d'affichage, l'affiche immédiatement
        if not self.complete:
            current_sentences = self.current_dialog["sentences"]
            self.text_progress = len(current_sentences[self.current_sentence_index])
            self.complete = True
            self.stop_sound()
            return True
            
        # Passe à la phrase suivante
        current_sentences = self.current_dialog["sentences"]
        if self.current_sentence_index < len(current_sentences) - 1:
            self.current_sentence_index += 1
            self.text_progress = 0
            self.complete = False
            return True
        else:
            # Fin du dialogue
            self.hide()
            return False
            
    def draw(self, display):
        """Dessine la boîte de dialogue et le texte"""
        if not self.visible:
            return
            
        # Crée la boîte de dialogue avec coins arrondis
        dialog_surface = pygame.Surface((self.box_width, self.box_height), pygame.SRCALPHA)
        
        # Dessine l'arrière-plan
        border_radius = 15
        self.draw_rounded_rect(dialog_surface, self.colors['bg'], 
                              (0, 0, self.box_width, self.box_height), border_radius)
        
        # Dessine la bordure
        border_width = 3
        pygame.draw.rect(dialog_surface, self.colors['border'], 
                      (border_width//2, border_width//2, 
                       self.box_width - border_width, self.box_height - border_width), 
                      border_width, border_radius - border_width//2)
        
        # Récupère la phrase actuelle et calcule la partie visible
        current_sentences = self.current_dialog["sentences"]
        current_text = current_sentences[self.current_sentence_index]
        
        # Remplace {player} par le nom d'utilisateur
        current_text = current_text.replace("{player}", self.username)
        
        visible_text = current_text[:int(self.text_progress)]
        
        # Affiche le nom du locuteur si disponible
        if "speaker" in self.current_dialog:
            speaker_name = self.current_dialog["speaker"]
            name_text = self.dialog_font.render(speaker_name, True, self.colors['text'])
            
            # Arrière-plan du nom
            name_padding = 10
            name_bg_width = name_text.get_width() + name_padding * 2
            name_bg_height = name_text.get_height() + name_padding
            
            name_bg_rect = (self.padding, 15, name_bg_width, name_bg_height)
            
            self.draw_rounded_rect(dialog_surface, self.colors['border'], name_bg_rect, 8)
            dialog_surface.blit(name_text, (self.padding + name_padding, 15 + name_padding//2))
        
        # Enveloppe et dessine le texte visible
        text_x = self.padding
        text_y = self.padding + 30  # Espace pour le nom du locuteur
        max_width = self.box_width - (self.padding * 2)
        line_height = self.dialog_font.get_linesize()
        
        # Système de retour à la ligne
        words = visible_text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_width = self.dialog_font.size(test_line)[0]
            
            if test_width < max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
                
        if current_line:
            lines.append(' '.join(current_line))
        
        # Dessine le texte avec effet d'ombre
        for i, line in enumerate(lines):
            # Ombre du texte
            shadow_text = self.dialog_font.render(line, True, self.colors['shadow'])
            dialog_surface.blit(shadow_text, (text_x + 1, text_y + i * line_height + 1))
            
            # Texte principal
            text = self.dialog_font.render(line, True, self.colors['text'])
            dialog_surface.blit(text, (text_x, text_y + i * line_height))
        
        # Dessine l'indicateur "appuyez sur espace" si le texte est complet
        if self.complete:
            indicator_y_offset = math.sin(self.indicator_animation) * 3
            continue_text = self.continue_font.render("Appuyez sur ESPACE pour continuer", True, self.colors['prompt'])
            dialog_surface.blit(
                continue_text, 
                (self.box_width - continue_text.get_width() - self.padding,
                 self.box_height - continue_text.get_height() - self.padding + indicator_y_offset)
            )
        
        # Affiche le dialogue sur l'écran
        display.blit(dialog_surface, (self.box_x, self.box_y))

# Dictionnaire des dialogues
dialogs = {
    "game_start": {
        "speaker": "Vieux Sage",
        "sentences": [
            "Bienvenue dans le royaume de Pyrthos, jeune vagabon!",
            "Autrefois ce royaume était calme et plaisant.",
            "Aujourd'hui, il en est autrement!",
            "Notre royaume est menacé par un terrible dragon",
            "Il porte le tragique nom de Pyroflamme, qui a élu domicile dans la montagne.",
            "Vous, {player}, devez vous entraîner à travers les différents niveaux avant d'affronter cette terrible créature.",
            "Bonne chance dans votre aventure!",
            "Et, {player}, rappelez-en vous bien: ceci n'est pas un jeu, le sort de Pyrthos vous accompagne..."
        ]
    },
    
    "enter_level1": {
        "speaker": "Guide",
        "sentences": [
            "Le premier niveau a commencé!",
            "Collectez toutes les pièces pour prouver votre habileté.",
            "Utilisez les flèches pour vous déplacer et la barre d'espace pour sauter.",
            "Un double saut est possible pour atteindre les plateformes élevées!"
        ]
    },
    
    "return_from_level1": {
        "speaker": "Vieux Sage",
        "sentences": [
            "Bravo, {player}! Vous avez terminé le premier niveau d'entraînement.",
            "Votre habilité est impressionnante, mais le chemin est encore long.",
            "Continuez à vous entraîner pour être prêt à affronter le dragon.",
            "Vous rendez un grand service a nos habitants" 
        ]
    },
    
    "return_from_level2": {
        "speaker": "Vieux Sage",
        "sentences": [
            "Excellent travail, {player}! Le second niveau est complété.",
            "Vous maîtrisez bien les déplacements, mais les ennemis du prochain niveau seront coriaces.",
            "Utilisez la touche Z pour attaquer ceux qui vous menaces.",
            "Continuez comme ça {player} et vous aller nous sauver"
        ]
    },
    
    "return_from_level3": {
        "speaker": "Maître d'Armes",
        "sentences": [
            "Impressionnant! Vous avez réussi le niveau avec aisance.",
            "Votre technique est bonne, je crois que vous avez un don.",
            "Cependant, vous aurez besoin de plus de puissance pour affronter le dragon.",
            "Le prochain niveau testera votre courage, {player}, et votre endurance."
        ]
    },
    
    "return_from_level4": {
        "speaker": "Vieux Sage",
        "sentences": [
            "Je suis stupéfait! Vous avez triomphé de tous les niveaux.",
            "Je crois que vous êtes maintenant prêt à affronter Pyroflamme.",
            "Méfiez-vous {player}, il est rusé et puissant, de plus ses dents sont comme des lames.",
            "Le destin de Pyrthos repose sur vos épaules {player}. Bonne chance, héros!"
        ]
    },
    
    "enter_level5": {
        "speaker": "???",
        "sentences": [
            "GROOOOAR! Qui ose me réveiller pendant ma somnolence?",
            "Un minuscule humain pense pouvoir me défier, MOI, le grand dragon Pyroflamme?!?",
            "Très bien... Voyons si vous résisterez à mes flammes!",
            "Que le combat commence!"
        ]
    }
}