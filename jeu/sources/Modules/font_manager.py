import pygame
import os

class FontManager:
    """Gestionnaire de polices centralisé pour le jeu."""
    
    # Chemins des polices
    FONT_REGULAR = "Fonts/PixelOperator8.ttf"
    FONT_BOLD = "Fonts/PixelOperator8-Bold.ttf"
    
    # Tailles prédéfinies
    SIZES = {
        'tiny': 6,
        'small': 10,
        'medium': 14,
        'large': 20,
        'title': 28,
    }
    
    # Instance singleton
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """Récupère ou crée l'instance singleton."""
        if cls._instance is None:
            cls._instance = FontManager()
        return cls._instance
    
    def __init__(self):
        """Initialise le cache de polices et vérifie les chemins alternatifs."""
        if FontManager._instance is not None:
            raise RuntimeError("L'instance existe déjà, utilisez get_instance()")
            
        pygame.font.init()
        self._font_cache = {}
        self._alt_path = ""
        
        # Vérification des chemins alternatifs
        if not os.path.exists(self.FONT_REGULAR):
            if os.path.exists(f"Assets/{self.FONT_REGULAR}"):
                self._alt_path = "Assets/"
            elif os.path.exists(f"./Assets/{self.FONT_REGULAR}"):
                self._alt_path = "./Assets/"
    
    def get_font(self, style='regular', size='medium', custom_size=None):
        """Récupère une police avec style et taille spécifiques."""
        if style.lower() == 'bold':
            font_path = self._alt_path + self.FONT_BOLD
        else:
            font_path = self._alt_path + self.FONT_REGULAR
        
        if custom_size is not None:
            pixel_size = custom_size
        else:
            pixel_size = self.SIZES.get(size, self.SIZES['medium'])
        
        cache_key = f"{font_path}_{pixel_size}"
        
        if cache_key in self._font_cache:
            return self._font_cache[cache_key]
        
        try:
            font = pygame.font.Font(font_path, pixel_size)
        except Exception as e:
            print(f"Échec du chargement de la police {font_path}: {e}")
            font = pygame.font.SysFont(None, pixel_size)
        
        self._font_cache[cache_key] = font
        return font

    def get_font_regular(self, size='medium', custom_size=None):
        """Méthode pratique pour obtenir une police régulière."""
        return self.get_font('regular', size, custom_size)

    def get_font_bold(self, size='medium', custom_size=None):
        """Méthode pratique pour obtenir une police en gras."""
        return self.get_font('bold', size, custom_size)

    def get_title_font(self):
        """Police pour les titres."""
        return self.get_font('bold', 'title')

    def get_header_font(self):
        """Police pour les en-têtes."""
        return self.get_font('bold', 'large')

    def get_dialog_font(self):
        """Police pour les dialogues."""
        return self.get_font('regular', 'medium')
    
    def get_ui_font(self):
        """Police pour les éléments d'interface."""
        return self.get_font('regular', 'small')
    
    def get_ui_bold_font(self):
        """Police en gras pour les éléments d'interface."""
        return self.get_font('bold', 'small')

# Fonction d'accès global
def get_font(style='regular', size='medium', custom_size=None):
    """Accès global pour récupérer une police du FontManager."""
    return FontManager.get_instance().get_font(style, size, custom_size)