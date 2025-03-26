import pygame

def player_check(player, obj, sound_manager=None):
    xoffset = 12 + obj.xoffset
    yoffset = 18
    topoffset = obj.topoffset
    
    is_hazard = hasattr(obj, 'is_hazard') and obj.is_hazard
    is_enemy = hasattr(obj, 'is_enemy') and obj.is_enemy
    
    if player.is_dying:
        return

    # Collision gauche
    if player.x + xoffset < obj.x + obj.w and player.x + player.w - xoffset > obj.x \
            and player.last_y + player.h > obj.y + topoffset and player.last_y < obj.y + obj.h - yoffset and \
            (player.state == "RUN_LEFT" or (player.state == "JUMP" and player.pastState == "RUN_LEFT")):
        if obj.collectable:
            if not obj.collected and sound_manager:
                sound_manager.play('coin')
            obj.collected = True
        elif is_hazard:
            player.lose_heart(sound_manager)
        elif is_enemy and obj.is_alive and obj.can_damage_player():
            player.lose_heart(sound_manager)
            if not player.is_dying and obj.is_alive:
                player.x += 15
                player.jumpVel = 7
                obj.reset_player_damage_cooldown()
        elif not is_enemy:
            player.x = obj.x + obj.w - xoffset
            player.speed *= 0.6
    # Collision droite
    elif player.x + player.w - xoffset > obj.x and player.x + xoffset < obj.x + obj.w \
            and player.last_y + player.h > obj.y + topoffset and player.last_y < obj.y + obj.h - yoffset and \
            (player.state == "RUN_RIGHT" or (player.state == "JUMP" and player.pastState == "RUN_RIGHT")):
        if obj.collectable:
            if not obj.collected and sound_manager:
                sound_manager.play('coin')
            obj.collected = True
        elif is_hazard:
            player.lose_heart(sound_manager)
        elif is_enemy and obj.is_alive and obj.can_damage_player():
            player.lose_heart(sound_manager)
            if not player.is_dying and obj.is_alive:
                player.x -= 15
                player.jumpVel = 7
                obj.reset_player_damage_cooldown()
        elif not is_enemy:
            player.x = obj.x - player.w + xoffset
            player.speed *= 0.6

    # Collision avec le sol
    if player.y + player.h >= obj.y + topoffset and player.last_y + player.h <= obj.y + topoffset + 12 \
            and player.x + xoffset < obj.x + obj.w \
            and player.x + player.w - xoffset > obj.x:
        if obj.collectable:
            if not obj.collected and sound_manager:
                sound_manager.play('coin')
            obj.collected = True
        elif is_hazard:
            player.lose_heart(sound_manager)
        elif is_enemy and obj.is_alive and obj.can_damage_player():
            player.lose_heart(sound_manager)
            if not player.is_dying and obj.is_alive:
                player.jumpVel = 12
                player.isOnGround = False
                player.currG = 0
                obj.reset_player_damage_cooldown()
        elif not is_enemy:
            player.y = obj.y - player.h + topoffset
            player.gs += 1
            player.isOnGround = True
            player.jumpVel = 0
            player.currG = 0
            return
    
    # Collision avec le plafond
    elif player.y < obj.y + obj.h - yoffset and player.last_y >= obj.y + obj.h - yoffset \
            and player.x + xoffset < obj.x + obj.w \
            and player.x + player.w - xoffset > obj.x and player.state == "JUMP":
        if obj.collectable:
            if not obj.collected and sound_manager:
                sound_manager.play('coin')
            obj.collected = True
        elif is_hazard:
            player.lose_heart(sound_manager)
        elif is_enemy and obj.is_alive and obj.can_damage_player():
            player.lose_heart(sound_manager)
            if not player.is_dying and obj.is_alive:
                player.jumpVel = 0
                player.currG = 2
                obj.reset_player_damage_cooldown()
        elif not is_enemy:
            player.y = obj.y + obj.h - yoffset
            player.isOnGround = False
            player.jumpVel = 0
            player.currG = 0

def enemy_check(enemy, obj):
    if not enemy.is_alive or enemy.is_dying:
        return
        
    # Ne pas vérifier les collisions pour le dragon (il vole à travers les murs)
    if hasattr(enemy, 'ignores_terrain') and enemy.ignores_terrain:
        return
        
    # Ignorer les objets non solides
    if not hasattr(obj, 'collide') or not obj.collide or obj.collectable:
        return
    
    # Ignorer les autres ennemis ou dangers
    if hasattr(obj, 'is_enemy') or hasattr(obj, 'is_hazard'):
        return
        
    # Collision avec le sol
    if enemy.y + enemy.h >= obj.y and enemy.y < obj.y + obj.h \
            and enemy.x + enemy.w - 5 > obj.x and enemy.x + 5 < obj.x + obj.w:
        if enemy.y + enemy.h <= obj.y + 10 and enemy.last_y + enemy.h <= obj.y:
            enemy.y = obj.y - enemy.h
            enemy.gs += 1
            return
    
    # Collision horizontale avec les murs
    if enemy.y + enemy.h - 5 > obj.y and enemy.y + 5 < obj.y + obj.h:
        # Collision à droite
        if enemy.direction == "RIGHT" and enemy.x + enemy.w > obj.x and enemy.x < obj.x:
            enemy.direction = "LEFT"
            enemy.sprite_direction = "RIGHT"
            enemy.x = obj.x - enemy.w - 1
        
        # Collision à gauche
        elif enemy.direction == "LEFT" and enemy.x < obj.x + obj.w and enemy.x + enemy.w > obj.x + obj.w:
            enemy.direction = "RIGHT"
            enemy.sprite_direction = "LEFT"
            enemy.x = obj.x + obj.w + 1

def check_player_attacks(player, enemies):
    if not player.is_attacking:
        return
        
    attack_rect = player.get_attack_rect()
    if not attack_rect:
        return
        
    for enemy in enemies:
        if not enemy.is_alive or enemy.is_dying:
            continue
            
        # Ajustement de la hitbox pour le dragon
        if enemy.__class__.__name__ == "Dragon":
            enemy_rect = pygame.Rect(
                enemy.x + enemy.w * 0.2,
                enemy.y + enemy.h * 0.2,
                enemy.w * 0.6,
                enemy.h * 0.6
            )
        else:
            enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.w, enemy.h)
        
        if attack_rect.colliderect(enemy_rect):
            enemy.take_damage(player.attack_damage)