from Objects.player import Player


class Camera:
    """Caméra qui suit le joueur et contrôle le défilement du monde."""
    
    def __init__(self, levellength, screen_width=640, screen_height=640):
        """Initialise la caméra avec les limites du niveau."""
        self.speed = 1
        self.x = self.speed
        self.y = 0
        self.xpos = 0
        self.ymax = levellength
        self.screen_width = screen_width
        self.screen_height = screen_height
    
    def movecamera(self, obj):
        """Déplace un objet par rapport au mouvement de la caméra."""
        obj.x -= self.x
        
        if isinstance(obj, Player):
            if self.x == self.speed:
                self.xpos += self.speed
            else:
                self.xpos -= self.speed
    
    def check(self, player, w, h):
        """Détermine si la caméra doit se déplacer en fonction de la position du joueur."""
        if w - 200 < player.x + player.w < self.ymax - self.xpos - 200:
            self.x = self.speed
            return True
        elif player.x < 200 and self.xpos > 0:
            self.x = -self.speed
            return True
        else:
            return False
    
    def is_visible(self, obj):
        """Vérifie si un objet est visible à l'écran."""
        buffer = 64
        
        return (obj.x + obj.w + buffer >= 0 and 
                obj.x - buffer <= self.screen_width and
                obj.y + obj.h + buffer >= 0 and
                obj.y - buffer <= self.screen_height)