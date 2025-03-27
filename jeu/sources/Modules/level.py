import pygame
from pytmx.util_pygame import load_pygame
from Objects.coin import Coin
from Objects.enemy import Enemy
from Objects.dragon import Dragon
from Objects.ground import Ground
from Objects.background import Background
from Objects.box import Box
from Objects.decoration import Decoration
from Objects.teleporter import Teleporter
from Objects.portal import Portal

class Level:
    """Classe gérant les données de niveau et le placement des objets depuis les fichiers TMX de Tiled"""
    def __init__(self, level_path, display_width, display_height):
        self.level_path = level_path
        self.display_width = display_width
        self.display_height = display_height
        self.objects = []
        self.map_width = 0
        self.map_height = 0
        self.level_name = level_path.split('/')[-2]
        self.load_level()

    def load_level(self):
        """Charge les données du niveau depuis un fichier TMX et crée les objets correspondants"""
        self.objects = []
        enemy_positions = []
        tiled_map = load_pygame(self.level_path)
        self.map_width = tiled_map.width * tiled_map.tilewidth
        self.map_height = tiled_map.height * tiled_map.tileheight
    
        # Ajout des murs aux limites
        self.objects.append(Box(-10, 0, 10, self.map_height))
        self.objects.append(Box(self.map_width, 0, 10, self.map_height))
    
        # Premier passage - collecte des positions d'ennemis
        for layer in tiled_map.visible_layers:
            if layer.name == "Enemy":
                for x, y, image in layer.tiles():
                    enemy_positions.append((x * tiled_map.tilewidth, y * tiled_map.tileheight))
    
        # Définition des gestionnaires de couches
        layer_handlers = {
            "Background": lambda x, y, img: Background(x, y, tiled_map.tilewidth, tiled_map.tileheight, img),
            "Terrain": lambda x, y, img: Ground(x, y, tiled_map.tilewidth, tiled_map.tileheight, img),
            "Collectibles": lambda x, y, img: Coin(x, y, tiled_map.tilewidth, tiled_map.tileheight, img),
            "Teleporter": lambda x, y, img: Teleporter(x, y, tiled_map.tilewidth, tiled_map.tileheight, img),
            "Decoration": lambda x, y, img: Decoration(x, y, tiled_map.tilewidth, tiled_map.tileheight, img),
            "Portal": lambda x, y, img: Portal(x, y, tiled_map.tilewidth, tiled_map.tileheight, img),
            "Enemy": lambda x, y, img: Dragon(x, y, tiled_map.tilewidth * 4, tiled_map.tileheight * 4)
                if self.level_name == "Level5" else Enemy(x, y, tiled_map.tilewidth, tiled_map.tileheight, "FireMonster"),
            "Dragon": lambda x, y, img: Dragon(x, y, tiled_map.tilewidth * 4, tiled_map.tileheight * 4)
        }
    
        # Ordre de rendu des couches (arrière-plan à premier plan)
        layer_order = [
            "Background",
            "Decoration",
            "Terrain",
            "Enemy",
            "Dragon",
            "Collectibles",
            "Portal",
            "Teleporter"
        ]
    
        # Regrouper les couches par nom pour gérer les doublons
        layers_by_name = {}
        for layer in tiled_map.visible_layers:
            if layer.name not in layers_by_name:
                layers_by_name[layer.name] = []
            layers_by_name[layer.name].append(layer)
    
        # Traitement des couches dans l'ordre spécifié
        for layer_name in layer_order:
            if layer_name in layers_by_name:
                for layer in layers_by_name[layer_name]:
                    for x, y, image in layer.tiles():
                        tile_x = x * tiled_map.tilewidth
                        tile_y = y * tiled_map.tileheight
    
                        # Ignore les tuiles de terrain qui chevauchent les positions d'ennemis
                        if layer_name == "Terrain" and (tile_x, tile_y) in enemy_positions:
                            continue
                        
                        if layer_name in layer_handlers:
                            self.objects.append(layer_handlers[layer_name](tile_x, tile_y, image))
    
        return self.objects
    
    def check_level_complete(self):
        """Vérifie si le niveau est terminé en fonction des pièces collectées"""
        has_coins = False
        for obj in self.objects:
            if isinstance(obj, Coin):
                has_coins = True
                if not obj.collected:
                    return False
        return has_coins
    
    def get_visible_objects(self, camera_x, viewport_width, viewport_height):
        """Renvoie uniquement les objets visibles dans la vue actuelle"""
        visible = []
        padding = 128  # Zone tampon hors écran

        for obj in self.objects:
            # Toujours inclure le joueur et les objets spéciaux
            if hasattr(obj, 'is_player') or isinstance(obj, Portal) or isinstance(obj, Dragon):
                visible.append(obj)
                continue

            # Récupération des dimensions de l'objet
            obj_width = getattr(obj, 'width', getattr(obj, 'w', 64))
            obj_height = getattr(obj, 'height', getattr(obj, 'h', 64))

            # Vérification si l'objet est dans la vue étendue
            if (obj.x + obj_width > camera_x - padding and 
                obj.x < camera_x + viewport_width + padding and
                obj.y + obj_height > -padding and
                obj.y < viewport_height + padding):
                visible.append(obj)

        return visible


class LevelManager:
    """Classe gérant la progression et l'accessibilité des niveaux"""
    def __init__(self):
        self.levels = {}
        self.current_level = None
        self.completed_levels = set()
        self.level_order = []
        
    def add_level(self, name, path):
        """Enregistre un niveau dans le gestionnaire"""
        self.levels[name] = path
        if name != "lobby":
            self.level_order.append(name)
        
    def get_level(self, name, display_width, display_height):
        """Charge et renvoie un niveau spécifique"""
        if name in self.levels:
            self.current_level = name
            return Level(self.levels[name], display_width, display_height)
        return None
    
    def get_next_level(self, display_width, display_height):
        """Récupère le niveau suivant après le niveau actuel"""
        if self.current_level in self.level_order:
            current_index = self.level_order.index(self.current_level)
            if current_index < len(self.level_order) - 1:
                next_level = self.level_order[current_index + 1]
                
                if self.is_level_accessible(next_level):
                    self.current_level = next_level
                    return Level(self.levels[next_level], display_width, display_height)
                
        return None
    
    def mark_level_completed(self, level_name):
        """Marque un niveau comme terminé"""
        if level_name != "lobby":
            self.completed_levels.add(level_name)
    
    def is_level_completed(self, level_name):
        """Vérifie si un niveau a été terminé"""
        return level_name in self.completed_levels
    
    def is_level_accessible(self, level_name):
        """Vérifie si un niveau est accessible selon la progression"""
        # Le lobby est toujours accessible
        if level_name == "lobby":
            return True
            
        # Le niveau 1 est accessible par défaut
        if level_name == "level1":
            return True
            
        # Pour les autres niveaux, vérifier la progression
        if level_name in self.level_order:
            current_index = self.level_order.index(level_name)
            
            # Si c'est le niveau 2 ou supérieur, le niveau précédent doit être terminé
            if current_index > 0:
                previous_level = self.level_order[current_index - 1]
                return self.is_level_completed(previous_level)
                
        # Par défaut : non accessible
        return False