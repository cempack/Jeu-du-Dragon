from Objects.player import Player
from Modules.camera import Camera

# États du jeu
MENU_STATE = 1
GAME_STATE = 2

# Variables globales
player = None
display_width = 32 * 20
display_height = 32 * 20
current_objects = []
camera = None
gameState = MENU_STATE
level_manager = None

def init_game():
    """
    Initialise les composants du jeu et crée le joueur.
    À appeler avant tout changement de niveau.
    """
    global player, level_manager
    
    player = Player(0, 0, 64, 64, character_type="Archer")

def switch_level(level_name):
    """
    Change vers un niveau spécifique.
    
    Args:
        level_name: Nom du niveau à charger
        
    Returns:
        bool: True si réussi, False sinon
    """
    global current_objects, camera, gameState
    
    if level_manager is None:
        print("Erreur: Jeu non initialisé. Appelez init_game() d'abord.")
        return False
        
    level = level_manager.get_level(level_name, display_width, display_height)
    if level:
        current_objects = level.objects
        
        # Réinitialisation du joueur
        player.x = 0
        player.y = 0
        player.jumpVel = 0
        player.currG = 0
        player.isOnGround = False
        
        # Joueur en première position
        current_objects.insert(0, player)
        
        camera = Camera(32 * 40)
        gameState = GAME_STATE
        return True
    
    return False