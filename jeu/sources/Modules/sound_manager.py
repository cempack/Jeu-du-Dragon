import pygame
import os

class SoundManager:
    def __init__(self):
        # Initialisation du mixer pygame si nécessaire
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        self.volume = 1.0
        self.muted = False
        self.previous_volume = self.volume
        self.sounds = {}
        
        # Création du dossier si absent
        sound_dir = './Assets/Sounds'
        os.makedirs(sound_dir, exist_ok=True)
        
        self.load_sounds()
    
    def load_sounds(self):
        """Charge tous les effets sonores du jeu"""
        sound_files = {
            'coin': './Assets/Sounds/coin.wav',
            'hurt': './Assets/Sounds/hurt.wav',
            'tap': './Assets/Sounds/tap.wav',
            'jump': './Assets/Sounds/jump.wav',
            'hit': './Assets/Sounds/hit.wav'
        }
        
        for name, path in sound_files.items():
            try:
                sound = pygame.mixer.Sound(path)
                sound.set_volume(self.volume)
                self.sounds[name] = sound
            except Exception as e:
                print(f"Erreur de chargement du son '{name}' depuis {path}: {e}")
    
    def play(self, sound_name):
        """Joue un effet sonore"""
        if not self.muted and sound_name in self.sounds:
            self.sounds[sound_name].play()
    
    def toggle_mute(self):
        """Active/désactive le son"""
        if not self.muted:
            self.previous_volume = self.volume
            self.muted = True
            for sound in self.sounds.values():
                sound.set_volume(0.0)
        else:
            self.muted = False
            for sound in self.sounds.values():
                sound.set_volume(self.volume)
    
    def set_volume(self, volume):
        """Définit le volume sonore (entre 0.0 et 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        
        if not self.muted:
            for sound in self.sounds.values():
                sound.set_volume(self.volume)
    
    def get_volume(self):
        """Renvoie le niveau de volume actuel"""
        return self.volume
    
    def is_muted(self):
        """Vérifie si le son est coupé"""
        return self.muted