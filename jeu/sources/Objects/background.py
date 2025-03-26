class Background:
    """Classe pour gérer les éléments d'arrière-plan du jeu."""
    
    def __init__(self, x, y, w, h, image):
        """Initialise un élément d'arrière-plan.
        
        Args:
            x, y: Position de l'élément
            w, h: Dimensions de l'élément
            image: Surface contenant l'image de l'élément
        """
        self.x, self.y, self.w, self.h, self.image = x, y, w, h, image
        self.collide = False
        self.collectable = False

    def draw(self, display):
        """Dessine l'élément sur l'écran.
        
        Args:
            display: Surface d'affichage
        """
        display.blit(self.image, (self.x, self.y))

    def update(self, keys):
        """Met à jour l'état de l'élément (non utilisé pour l'arrière-plan).
        
        Args:
            keys: Liste des touches pressées
        """
        pass