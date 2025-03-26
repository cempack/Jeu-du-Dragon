import pygame
from Objects.player import Player
from Objects.portal import Portal
from Objects.heart_ui import HeartUI
from Objects.dragon import Dragon
from Objects.dialog import Dialog
from Modules.camera import Camera
from Modules.level import LevelManager
from Modules.collision import player_check, enemy_check, check_player_attacks
from Objects.teleporter import Teleporter
from Modules.main_menu import MainMenu
from Modules.hero_selector import HeroSelector
from Modules.you_win_menu import YouWinMenu
from Modules.music_manager import MusicManager
from Modules.sound_manager import SoundManager
from Objects.coin import Coin
from Modules.font_manager import get_font

pygame.init()

# Configuration de l'affichage
display_width = 32 * 20
display_height = 32 * 20
display = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption("Le Jeu Du Dragon")
pygame.display.set_icon(pygame.image.load("Assets/icon.ico"))
clock = pygame.time.Clock()
done = False

class SpatialGrid:
    """Grille spatiale pour optimiser la détection de collisions"""
    def __init__(self, width, height, cell_size=128):
        self.cell_size = cell_size
        self.grid = {}

    def clear(self):
        self.grid = {}

    def insert(self, obj):
        """Insère un objet dans les cellules qu'il occupe"""
        if not hasattr(obj, 'x'):
            return

        obj_width = getattr(obj, 'width', getattr(obj, 'w', 64))
        obj_height = getattr(obj, 'height', getattr(obj, 'h', 64))

        x1, y1 = int(obj.x // self.cell_size), int(obj.y // self.cell_size)
        x2, y2 = int((obj.x + obj_width) // self.cell_size), int((obj.y + obj_height) // self.cell_size)

        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):
                cell = (x, y)
                if cell not in self.grid:
                    self.grid[cell] = []
                self.grid[cell].append(obj)

    def get_nearby_objects(self, obj):
        """Récupère les objets potentiellement en collision"""
        nearby = set()

        obj_width = getattr(obj, 'width', getattr(obj, 'w', 64))
        obj_height = getattr(obj, 'height', getattr(obj, 'h', 64))

        x1, y1 = int(obj.x // self.cell_size), int(obj.y // self.cell_size)
        x2, y2 = int((obj.x + obj_width) // self.cell_size), int((obj.y + obj_height) // self.cell_size)

        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):
                cell = (x, y)
                if cell in self.grid:
                    for other in self.grid[cell]:
                        if other != obj:
                            nearby.add(other)

        return list(nearby)

    def get_objects_in_viewport(self, camera_x, camera_y, viewport_width, viewport_height):
        """Récupère les objets visibles à l'écran"""
        visible = set()
        x1, y1 = int(camera_x // self.cell_size), int(camera_y // self.cell_size)
        x2, y2 = int((camera_x + viewport_width) // self.cell_size), int((camera_y + viewport_height) // self.cell_size)

        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):
                cell = (x, y)
                if cell in self.grid:
                    visible.update(self.grid[cell])

        return list(visible)

# Initialisation des gestionnaires
music_manager = MusicManager()
sound_manager = SoundManager()
dialog = Dialog(display_width, display_height)
dialog.set_music_manager(music_manager)

# Initialisation du gestionnaire de niveaux
level_manager = LevelManager()
level_manager.add_level("lobby", './Assets/Levels/Lobby/level.tmx')
level_manager.add_level("level1", './Assets/Levels/Level1/level.tmx')
level_manager.add_level("level2", './Assets/Levels/Level2/level.tmx')
level_manager.add_level("level3", './Assets/Levels/Level3/level.tmx')
level_manager.add_level("level4", './Assets/Levels/Level4/level.tmx')
level_manager.add_level("level5", './Assets/Levels/Level5/level.tmx')

# États du jeu et variables
player = None
gameState = 1  # 1 = menu principal, 2 = sélection héros, 3 = jeu, 4 = niveau terminé, 5 = écran victoire
current_level_name = None  # Niveau actuel pour la musique
previous_level_name = None  # Niveau précédent pour les dialogues
current_objects = []
camera = None
first_game_start = True  # Premier lancement du jeu
dialog_pending = None
dialog_delay = 0
failed_quiz = False  # Échec quiz et retour au lobby
level = None  # Objet niveau actuel

# Création des composants UI
main_menu = MainMenu(display_width, display_height)
hero_selector = HeroSelector(display_width, display_height)
you_win_menu = YouWinMenu(display_width, display_height)
heart_ui = HeartUI()

def update_portal_status():
    """Met à jour l'état des portails selon la collecte de pièces"""
    coins_exist = False
    all_collected = True
    
    for obj in current_objects:
        if isinstance(obj, Coin):
            coins_exist = True
            if not obj.collected:
                all_collected = False
                break
    
    for obj in current_objects:
        if isinstance(obj, Portal):
            if coins_exist and all_collected:
                obj.activate()
            else:
                obj.deactivate()

def switch_level(level_name, character_type, death_respawn=False):
    """Change de niveau et gère les transitions"""
    global current_objects, camera, gameState, player, current_level_name, previous_level_name, first_game_start, dialog_delay, dialog_pending, failed_quiz, level
    
    # Vérification de l'accessibilité du niveau
    if not level_manager.is_level_accessible(level_name) and level_name != "lobby":
        return False
    
    # Mémorisation du niveau précédent pour les dialogues
    previous_level_name = current_level_name
    
    # Création ou mise à jour du joueur
    if player is None:
        player = Player(0, 0, 64, 64, character_type=character_type)
    else:
        player.character_type = character_type
        player.__init__(0, 0, 64, 64, character_type=character_type)
    
    # 5 cœurs pour le combat final
    if level_name == "level5":
        player.max_hearts = 5
        player.current_hearts = 5
    
    level = level_manager.get_level(level_name, display_width, display_height)
    if level:
        current_objects = level.objects
        
        # Réinitialisation position et propriétés du joueur
        player.x = 0
        player.y = 0
        player.jumpVel = 0
        player.currG = 0
        player.isOnGround = False
        player.min_visible_y = 40
        current_objects.insert(0, player)
        
        # Connexion des téléporteurs au gestionnaire de niveaux
        for obj in current_objects:
            if isinstance(obj, Teleporter):
                obj.set_level_manager(level_manager)
        
        camera = Camera(level.map_width)
        gameState = 3
        
        # Musique appropriée pour ce niveau
        if current_level_name != level_name:
            music_manager.play(level_name)
            current_level_name = level_name
        
        # Configuration des dialogues à afficher
        dialog_pending = None
        if level_name == "lobby" and first_game_start:
            dialog_pending = "game_start"
            first_game_start = False
        elif level_name == "level1" and previous_level_name != "level1":
            dialog_pending = "enter_level1"
        elif level_name == "level5":
            dialog_pending = "enter_level5"
        elif level_name == "lobby" and not failed_quiz and not death_respawn:
            # Retour de différents niveaux
            if previous_level_name == "level1":
                dialog_pending = "return_from_level1"
            elif previous_level_name == "level2":
                dialog_pending = "return_from_level2"
            elif previous_level_name == "level3":
                dialog_pending = "return_from_level3"
            elif previous_level_name == "level4":
                dialog_pending = "return_from_level4"

        failed_quiz = False
            
        if dialog_pending:
            dialog_delay = 60
            
        update_portal_status()
        return True
    return False

def draw_rounded_rect(surface, color, rect, radius):
    """Dessine un rectangle avec des coins arrondis"""
    x, y, width, height = rect

    pygame.draw.rect(surface, color, (x + radius, y, width - 2*radius, height))
    pygame.draw.rect(surface, color, (x, y + radius, width, height - 2*radius))

    pygame.draw.circle(surface, color, (x + radius, y + radius), radius)
    pygame.draw.circle(surface, color, (x + width - radius, y + radius), radius)
    pygame.draw.circle(surface, color, (x + radius, y + height - radius), radius)
    pygame.draw.circle(surface, color, (x + width - radius, y + height - radius), radius)

def draw_teleporter_prompt(display, width, height):
    """Affiche le message d'interaction avec le téléporteur"""
    colors = {
        'bg': (20, 70, 45),
        'border': (10, 112, 48),
        'text': (255, 255, 255),
    }

    font = get_font('bold', 'medium')
    message = "APPUYEZ SUR E POUR INTERAGIR"
    text = font.render(message, True, colors['text'])

    text_width = text.get_width() + 20
    text_height = text.get_height() + 10
    prompt_rect = pygame.Rect(
        width//2 - text_width//2,
        60,
        text_width,
        text_height
    )

    s = pygame.Surface((text_width, text_height), pygame.SRCALPHA)
    border_radius = 10

    bg_color = colors['bg'] + (230,)
    draw_rounded_rect(s, bg_color, (0, 0, text_width, text_height), border_radius)

    display.blit(s, prompt_rect)

    border_width = 2
    pygame.draw.rect(display, colors['border'], 
                    (prompt_rect.x, prompt_rect.y, 
                    prompt_rect.width, prompt_rect.height), 
                    border_width, border_radius - border_width//2)

    display.blit(text, (prompt_rect.x + 10, prompt_rect.y + 5))

# Démarrage avec la musique du menu
music_manager.play('menu')
current_level_name = 'menu'

# Boucle principale du jeu
while not done:
    clock.tick(60)
    keys = pygame.key.get_pressed()
    events = pygame.event.get()

    # Vérification fin de piste musicale
    music_manager.check_end_of_track()

    for e in events:
        if e.type == pygame.QUIT:
            done = True

    display.fill((0, 0, 0))

    if gameState == 1:  # Menu Principal
        # Musique du menu
        if current_level_name != 'menu':
            music_manager.play('menu')
            current_level_name = 'menu'

        main_menu.draw(display)

        for e in events:
            if e.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                if main_menu.check_button_click(pos):
                    # Passage à la sélection du héros
                    gameState = 2
                    music_manager.play('hero_select')
                    sound_manager.play('tap')
                    current_level_name = 'hero_select'

                    # Transmission du nom d'utilisateur
                    dialog.set_username(main_menu.get_username())
                elif main_menu.check_mute_button_click(pos):
                    # Basculement mode muet
                    sound_manager.play('tap')
                    music_manager.toggle_mute()
                    sound_manager.toggle_mute()
                    dialog.toggle_mute(music_manager.is_muted())
                elif main_menu.check_input_field_click(pos):
                    sound_manager.play('tap')

            main_menu.handle_input_event(e)

    elif gameState == 2:  # Sélection du Héros
        hero_selector.draw(display)

        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_LEFT:
                    hero_selector.select_previous()
                    sound_manager.play('tap')
                elif e.key == pygame.K_RIGHT:
                    hero_selector.select_next()
                    sound_manager.play('tap')
                elif e.key == pygame.K_RETURN:
                    selected_hero = hero_selector.get_selected_hero()
                    sound_manager.play('tap')
                    switch_level("lobby", selected_hero)

    elif gameState == 3:  # Gameplay
        dialog_active = dialog.is_visible()

        # Mise à jour des dialogues
        if dialog_active:
            dialog.update()
            for e in events:
                if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                    was_visible = dialog.is_visible()
                    dialog_dismissed = dialog.advance() == False and was_visible
                    if dialog_dismissed:
                        for obj in current_objects:
                            if obj == player:
                                obj.ignore_current_jump_press = True

        # Gestion du délai de dialogue
        if dialog_pending and dialog_delay > 0:
            dialog_delay -= 1
            if dialog_delay <= 0:
                dialog.show(dialog_pending)
                dialog_pending = None

        # Mise à jour des objets uniquement si pas de dialogue
        if not dialog_active:
            # Mise à jour de tous les objets
            for obj in current_objects:
                if obj == player:
                    obj.update(keys, sound_manager)
                elif hasattr(obj, '__class__') and obj.__class__.__name__ == "Dragon":
                    # Cas spécial pour le Dragon
                    obj.update(keys, player, current_objects)
                elif hasattr(obj, 'update'):
                    if hasattr(obj, 'is_enemy') and obj.is_enemy:
                        try:
                            obj.update(keys, player, current_objects)
                        except TypeError:
                            obj.update(keys)
                    else:
                        obj.update(keys)

            # Mouvement de la caméra
            if camera:
                while camera.check(player, display_width, display_height):
                    for obj in current_objects:
                        camera.movecamera(obj)

            # Configuration de la grille spatiale
            spatial_grid = SpatialGrid(level.map_width, level.map_height)
            for obj in current_objects:
                if hasattr(obj, 'collide') and obj.collide:
                    spatial_grid.insert(obj)

            # Collecte des ennemis pour les collisions
            enemies = [obj for obj in current_objects if hasattr(obj, 'is_enemy') and obj.is_enemy]

            # Vérification des attaques du joueur
            check_player_attacks(player, enemies)

            # Détection des collisions entre ennemis et terrain
            for enemy in enemies:
                enemy.check_ledge_ahead(current_objects)
                nearby_objects = spatial_grid.get_nearby_objects(enemy)
                for obj in nearby_objects:
                    if obj != enemy and hasattr(obj, 'collide') and obj.collide:
                        enemy_check(enemy, obj)

            # Détection des collisions pour le joueur
            nearby_objects = spatial_grid.get_nearby_objects(player)
            for obj in nearby_objects:
                if hasattr(obj, 'collide') and obj.collide:
                    player_check(player, obj, sound_manager)

            # Mise à jour de l'état des portails
            update_portal_status()

            # Vérification proximité des portails
            for obj in current_objects:
                if isinstance(obj, Portal):
                    obj.check_proximity(player)

            # Gestion des interactions avec les portails
            for e in events:
                if e.type == pygame.KEYDOWN and e.key == pygame.K_e:
                    for obj in current_objects:
                        if isinstance(obj, Portal) and obj.prompt_visible and obj.is_active:
                            if not obj.quiz_visible:
                                result = obj.show_quiz(current_level_name)
                                if result == "teleport":
                                    if current_level_name != "lobby":
                                        level_manager.mark_level_completed(current_level_name)

                                    switch_level(obj.destination, player.character_type)
                                    break

            # Vérification des téléporteurs
            teleporter_prompts = []

            for obj in current_objects:
                if isinstance(obj, Teleporter) and not obj.menu_visible:
                    if (abs(player.x - obj.x) < 64 and abs(player.y - obj.y) < 64):
                        teleporter_prompts.append(obj)

                        for e in events:
                            if e.type == pygame.KEYDOWN and e.key == pygame.K_e:
                                obj.activate()
                                sound_manager.play('tap')

            # Réapparition après mort
            if player.respawn_after_death:
                player.respawn_after_death = False
                player.is_dying = False
                player.current_hearts = player.max_hearts
                switch_level("lobby", player.character_type, death_respawn=True)
                continue

            update_portal_status()

        # Affichage des objets visibles uniquement
        if camera and level:
            visible_objects = level.get_visible_objects(camera.x, display_width, display_height)
            for obj in visible_objects:
                if obj != player:
                    obj.draw(display)
            player.draw(display)
        else:
            for obj in current_objects[1:]:
                obj.draw(display)
            player.draw(display)

        # Affichage des barres de vie des boss
        for obj in current_objects:
            if hasattr(obj, 'is_boss') and obj.is_boss and hasattr(obj, 'draw_boss_bar'):
                obj.draw_boss_bar(display)

        # Affichage des dialogues par-dessus tout
        if dialog_active:
            dialog.draw(display)

        # Affichage des prompts de téléporteur
        if not dialog_active and teleporter_prompts:
            draw_teleporter_prompt(display, display_width, display_height)

        # Affichage des menus de téléporteurs
        for obj in current_objects:
            if isinstance(obj, Teleporter) and obj.menu_visible:
                obj.draw_menu(display)

        # Affichage des quiz de portails
        for obj in current_objects:
            if isinstance(obj, Portal) and obj.quiz_visible:
                obj.draw_quiz(display)

        heart_ui.draw(display, player.current_hearts, player.max_hearts)

        # Navigation dans les menus de téléporteurs
        if not dialog_active:
            for e in events:
                if e.type == pygame.KEYDOWN:
                    for obj in current_objects:
                        if isinstance(obj, Teleporter) and obj.menu_visible:
                            if e.key == pygame.K_UP:
                                obj.select_previous()
                                sound_manager.play('tap')
                            elif e.key == pygame.K_DOWN:
                                obj.select_next()
                                sound_manager.play('tap')
                            elif e.key == pygame.K_RETURN:
                                destination = obj.get_selected_destination()
                                sound_manager.play('tap')
                                
                                accessible = (destination == "level5" or level_manager.is_level_accessible(destination))
                                not_completed = (destination == "lobby" or destination == "level5" or
                                                not level_manager.is_level_completed(destination))

                                if destination and accessible and not_completed:
                                    switch_level(destination, player.character_type)
                                    obj.hide_menu()
                            elif e.key == pygame.K_ESCAPE:
                                obj.hide_menu()
                                sound_manager.play('tap')

            # Navigation dans les quiz de portails
            for obj in current_objects:
                if isinstance(obj, Portal) and obj.quiz_visible:
                    for e in events:
                        if e.type == pygame.KEYDOWN:
                            if obj.answer_result is None:
                                if e.key == pygame.K_UP:
                                    obj.select_previous()
                                    sound_manager.play('tap')
                                elif e.key == pygame.K_DOWN:
                                    obj.select_next()
                                    sound_manager.play('tap')
                                elif e.key == pygame.K_RETURN:
                                    obj.confirm_answer()
                                    sound_manager.play('tap')

            # Vérification des résultats de quiz
            for obj in current_objects:
                if isinstance(obj, Portal) and obj.quiz_visible:
                    result = obj.update(None)
                    if result == "teleport":
                        if current_level_name != "lobby":
                            level_manager.mark_level_completed(current_level_name)
                        switch_level(obj.destination, player.character_type)
                        break
                    elif result == "teleport_to_lobby":
                        failed_quiz = True
                        switch_level("lobby", player.character_type)
                        break

        # Vérification de la mort du dragon
        for obj in current_objects:
            if hasattr(obj, '__class__') and obj.__class__.__name__ == "Dragon" and hasattr(obj, 'died_completely') and obj.died_completely:
                gameState = 5  # Écran de victoire
                obj.died_completely = False
                you_win_menu.username = main_menu.get_username()
                music_manager.play('menu')
                break

    elif gameState == 5:  # Écran de victoire
        you_win_menu.draw(display)

        for e in events:
            if e.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                if you_win_menu.check_button_click(pos):
                    done = True

        # Touche Échap pour quitter
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            done = True

    pygame.display.flip()