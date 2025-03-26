import pygame
import os
import random
import time

class MusicManager:
    def __init__(self):
        # Initialisation du système audio
        pygame.mixer.init()
        
        # Paramètres audio
        self.volume = 1
        self.muted = False
        self.previous_volume = self.volume
        
        # État des pistes
        self.current_track = None
        self.current_track_path = None
        self.last_track_change = time.time()
        self.last_end_check = time.time()
        
        # Paramètres de sélection des pistes
        self.secondary_chance = 0.3
        self.main_track_context = 'menu'  # Contexte par défaut au retour d'une piste secondaire
        
        # Configuration du répertoire de musique
        os.makedirs('./Assets/Music', exist_ok=True)
        
        # Définition des pistes
        self.tracks = {
            'menu': './Assets/Music/main.mp3',
            'lobby': './Assets/Music/main.mp3',
            'level1': './Assets/Music/main.mp3',
            'level2': './Assets/Music/main.mp3',
            'level3': './Assets/Music/main.mp3',
            'level4': './Assets/Music/main.mp3',
            'level5': './Assets/Music/epic_fight.mp3',
            'hero_select': './Assets/Music/main.mp3',
            'secondary': './Assets/Music/secondary.mp3',
        }
        
        # Piste par défaut
        self.default_track = './Assets/Music/main.mp3'
    
    def play(self, track_name, loops=0, fade_ms=500):
        # Détermination du chemin de la piste
        target_track_path = self.tracks.get(track_name, self.default_track)
        
        # Ne rien faire si la même piste est déjà en cours
        if self.current_track_path == target_track_path and pygame.mixer.music.get_busy():
            return
        
        # Mise à jour du contexte pour les pistes principales
        if track_name != 'secondary' and track_name in self.tracks:
            self.main_track_context = track_name
            
        # Mise à jour des informations de la piste courante
        self.current_track = track_name
        self.current_track_path = target_track_path
        self.last_track_change = time.time()
        
        # Vérification du fichier et lancement de la lecture
        if not os.path.exists(target_track_path):
            target_track_path = self.default_track
        
        if os.path.exists(target_track_path):
            try:
                pygame.mixer.music.fadeout(fade_ms)
                pygame.mixer.music.load(target_track_path)
                pygame.mixer.music.set_volume(0.0 if self.muted else self.volume)
                pygame.mixer.music.play(loops, fade_ms=fade_ms)
            except Exception as e:
                print(f"Erreur lors de la lecture de la musique: {e}")
        else:
            print(f"Attention: Aucune piste valide trouvée pour '{track_name}'")
    
    def stop(self, fade_ms=500):
        pygame.mixer.music.fadeout(fade_ms)
        self.current_track = None
        self.current_track_path = None
    
    def pause(self):
        pygame.mixer.music.pause()
    
    def unpause(self):
        pygame.mixer.music.unpause()
    
    def toggle_mute(self):
        self.muted = not self.muted
        
        if self.muted:
            self.previous_volume = self.volume
            pygame.mixer.music.set_volume(0.0)
        else:
            pygame.mixer.music.set_volume(self.previous_volume)
        
        return self.muted
    
    def set_volume(self, volume):
        self.volume = max(0.0, min(1.0, volume))  # Limiter entre 0.0 et 1.0
        if not self.muted:
            pygame.mixer.music.set_volume(self.volume)
    
    def get_volume(self):
        return 0.0 if self.muted else self.volume
    
    def is_muted(self):
        return self.muted
        
    def check_end_of_track(self):
        # Limiter les vérifications à une par seconde pour optimiser les performances
        current_time = time.time()
        if current_time - self.last_end_check < 1.0:
            return
        
        self.last_end_check = current_time
        
        # Gestion des transitions entre pistes quand la musique s'arrête
        if not pygame.mixer.music.get_busy() and self.current_track:
            # Si une piste secondaire se termine, retour au contexte principal
            if self.current_track == 'secondary':
                self.play(self.main_track_context)
            # Pour les pistes principales, possibilité de passer à secondaire ou rejouer
            elif self.current_track in ['menu', 'lobby', 'level1', 'level2', 
                                       'level3', 'level4', 'level5', 'hero_select']:
                if random.uniform(0, 1) < self.secondary_chance:
                    self.play('secondary')
                else:
                    self.play(self.current_track)
            else:
                # Rejouer tout autre type de piste
                self.play(self.current_track)