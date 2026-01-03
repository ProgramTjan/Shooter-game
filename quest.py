"""
Quest Systeem - Demonic Crystals Quest
=======================================
Verzamel alle mystieke kristallen om de boss te verzwakken!
"""
import pygame
import math
from settings import *


class Crystal:
    """Een verzamelbaar demonisch kristal"""
    
    CRYSTAL_TYPES = [
        {'name': 'Blood Crystal', 'color': (255, 50, 50), 'glow': (255, 100, 100)},
        {'name': 'Soul Crystal', 'color': (50, 200, 255), 'glow': (100, 220, 255)},
        {'name': 'Void Crystal', 'color': (180, 50, 255), 'glow': (200, 100, 255)},
        {'name': 'Flame Crystal', 'color': (255, 150, 50), 'glow': (255, 200, 100)},
    ]
    
    def __init__(self, x, y, crystal_type_idx):
        self.x = x
        self.y = y
        self.collected = False
        
        crystal_type = self.CRYSTAL_TYPES[crystal_type_idx % len(self.CRYSTAL_TYPES)]
        self.name = crystal_type['name']
        self.color = crystal_type['color']
        self.glow_color = crystal_type['glow']
        
        # Animatie
        self.float_offset = 0
        self.rotation = 0
        self.glow_pulse = 0
        
        # Pickup range
        self.pickup_range = 1.0
        
        # Maak sprite
        self.sprite = self._create_sprite()
        
    def _create_sprite(self):
        """Maak een gloeiend kristal sprite"""
        size = 48
        sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        
        center_x, center_y = size // 2, size // 2
        
        # Glow effect (meerdere lagen)
        for r in range(4, 0, -1):
            glow_size = 16 + r * 4
            alpha = 40 - r * 8
            glow_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*self.glow_color, alpha), 
                             (center_x, center_y), glow_size)
            sprite.blit(glow_surf, (0, 0))
        
        # Kristal vorm (diamant/hexagon)
        crystal_points = [
            (center_x, center_y - 18),      # Top
            (center_x + 12, center_y - 6),  # Rechts boven
            (center_x + 12, center_y + 6),  # Rechts onder
            (center_x, center_y + 18),      # Onder
            (center_x - 12, center_y + 6),  # Links onder
            (center_x - 12, center_y - 6),  # Links boven
        ]
        
        # Donkere basis
        pygame.draw.polygon(sprite, tuple(max(0, c - 60) for c in self.color), 
                           crystal_points)
        
        # Lichtere zijkant (highlight)
        highlight_points = [
            crystal_points[0],
            crystal_points[1],
            crystal_points[2],
            (center_x, center_y),
        ]
        pygame.draw.polygon(sprite, self.color, highlight_points)
        
        # Zeer lichte highlight
        bright_points = [
            crystal_points[0],
            (center_x + 6, center_y - 8),
            (center_x, center_y - 2),
            (center_x - 4, center_y - 8),
        ]
        bright_color = tuple(min(255, c + 80) for c in self.color)
        pygame.draw.polygon(sprite, bright_color, bright_points)
        
        # Rand
        pygame.draw.polygon(sprite, tuple(min(255, c + 40) for c in self.color), 
                           crystal_points, 2)
        
        # Sterretje / glinstering
        pygame.draw.circle(sprite, (255, 255, 255), (center_x - 4, center_y - 10), 2)
        
        return sprite
        
    def update(self, dt, player_x, player_y):
        """Update kristal animatie en check pickup"""
        if self.collected:
            return False
            
        # Animatie
        self.float_offset = math.sin(pygame.time.get_ticks() * 0.003) * 0.1
        self.rotation += dt * 0.001
        self.glow_pulse = (math.sin(pygame.time.get_ticks() * 0.005) + 1) * 0.5
        
        # Check pickup
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < self.pickup_range:
            self.collected = True
            return True  # Crystal collected!
            
        return False
        
    def get_sprite(self):
        """Geef huidige sprite terug (met animatie effecten)"""
        if self.collected:
            return None
            
        # Creëer animated sprite met glow pulse
        size = 48
        animated = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Extra glow op basis van pulse
        glow_alpha = int(20 + self.glow_pulse * 30)
        glow_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*self.glow_color, glow_alpha), 
                          (size//2, size//2), 22)
        animated.blit(glow_surf, (0, 0))
        
        # Basis sprite
        animated.blit(self.sprite, (0, 0))
        
        return animated


class LevelKey:
    """Een sleutel die nodig is om de exit deur te openen"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.collected = False
        self.pickup_range = 1.2
        
        # Animatie
        self.float_offset = 0
        self.rotation = 0
        self.glow_pulse = 0
        
        # Sprite
        self.sprite = self._create_sprite()
        
    def _create_sprite(self):
        """Maak een gouden sleutel sprite"""
        size = 48
        sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        
        cx, cy = size // 2, size // 2
        
        # Glow effect
        for r in range(4, 0, -1):
            glow_size = 16 + r * 3
            alpha = 35 - r * 7
            pygame.draw.circle(sprite, (255, 215, 0, alpha), (cx, cy), glow_size)
        
        # Sleutel basis (goud)
        key_color = (255, 200, 50)
        key_dark = (180, 140, 30)
        key_light = (255, 230, 100)
        
        # Sleutel ring (bovenaan)
        pygame.draw.circle(sprite, key_dark, (cx, cy - 10), 10)
        pygame.draw.circle(sprite, key_color, (cx, cy - 10), 8)
        pygame.draw.circle(sprite, (40, 30, 20), (cx, cy - 10), 5)
        pygame.draw.circle(sprite, key_light, (cx - 2, cy - 12), 2)
        
        # Sleutel steel
        pygame.draw.rect(sprite, key_dark, (cx - 3, cy - 2, 6, 18))
        pygame.draw.rect(sprite, key_color, (cx - 2, cy - 2, 4, 18))
        pygame.draw.line(sprite, key_light, (cx - 1, cy), (cx - 1, cy + 14), 1)
        
        # Sleutel tanden
        pygame.draw.rect(sprite, key_dark, (cx, cy + 10, 8, 4))
        pygame.draw.rect(sprite, key_color, (cx + 1, cy + 11, 6, 2))
        pygame.draw.rect(sprite, key_dark, (cx, cy + 6, 6, 3))
        pygame.draw.rect(sprite, key_color, (cx + 1, cy + 7, 4, 1))
        
        return sprite
        
    def update(self, dt, player_x, player_y):
        """Update animatie en check pickup"""
        if self.collected:
            return False
            
        # Animatie
        self.float_offset = math.sin(pygame.time.get_ticks() * 0.003) * 0.12
        self.rotation += dt * 0.002
        self.glow_pulse = (math.sin(pygame.time.get_ticks() * 0.004) + 1) * 0.5
        
        # Check pickup
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < self.pickup_range:
            self.collected = True
            return True
            
        return False
        
    def get_sprite(self):
        """Geef huidige sprite terug"""
        if self.collected:
            return None
            
        size = 48
        animated = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Pulserende glow
        glow_alpha = int(20 + self.glow_pulse * 25)
        pygame.draw.circle(animated, (255, 215, 0, glow_alpha), 
                          (size//2, size//2), 20)
        
        animated.blit(self.sprite, (0, 0))
        return animated


class ExitDoor:
    """De exit deur naar het volgende level"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_open = False
        self.activated = False
        self.activation_range = 1.5
        
        # Animatie
        self.glow_pulse = 0
        self.open_animation = 0
        
        # Sprites
        self.sprite_closed = self._create_closed_sprite()
        self.sprite_open = self._create_open_sprite()
        
    def _create_closed_sprite(self):
        """Maak gesloten deur sprite"""
        size = 64
        sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        
        cx, cy = size // 2, size // 2
        
        # Deur frame
        frame_color = (80, 60, 40)
        pygame.draw.rect(sprite, frame_color, (cx - 20, cy - 28, 40, 56))
        
        # Deur paneel
        door_color = (60, 45, 30)
        pygame.draw.rect(sprite, door_color, (cx - 16, cy - 24, 32, 48))
        
        # Decoratie
        pygame.draw.rect(sprite, (50, 35, 25), (cx - 12, cy - 20, 24, 18))
        pygame.draw.rect(sprite, (50, 35, 25), (cx - 12, cy + 4, 24, 18))
        
        # Slot (rood = gesloten)
        pygame.draw.circle(sprite, (150, 30, 30), (cx + 10, cy), 5)
        pygame.draw.circle(sprite, (200, 50, 50), (cx + 10, cy), 3)
        
        # Sleutelgat
        pygame.draw.ellipse(sprite, (20, 15, 10), (cx + 7, cy - 2, 6, 8))
        
        return sprite
        
    def _create_open_sprite(self):
        """Maak open deur sprite met portaal effect"""
        size = 64
        sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        
        cx, cy = size // 2, size // 2
        
        # Deur frame
        frame_color = (80, 60, 40)
        pygame.draw.rect(sprite, frame_color, (cx - 20, cy - 28, 40, 56))
        
        # Portaal effect (blauw/paars glow)
        for r in range(5, 0, -1):
            alpha = 50 - r * 8
            color = (100, 150, 255, alpha)
            pygame.draw.ellipse(sprite, color, 
                              (cx - 14 - r, cy - 22 - r, 28 + r*2, 44 + r*2))
        
        # Binnenste portaal
        pygame.draw.ellipse(sprite, (150, 180, 255), (cx - 14, cy - 22, 28, 44))
        pygame.draw.ellipse(sprite, (200, 220, 255), (cx - 10, cy - 16, 20, 32))
        pygame.draw.ellipse(sprite, (255, 255, 255), (cx - 5, cy - 8, 10, 16))
        
        # Sparkles
        pygame.draw.circle(sprite, (255, 255, 255), (cx - 6, cy - 14), 2)
        pygame.draw.circle(sprite, (255, 255, 255), (cx + 8, cy + 8), 2)
        
        return sprite
        
    def unlock(self):
        """Open de deur"""
        self.is_open = True
        
    def update(self, dt, player_x, player_y, has_key, crystals_complete):
        """Update deur state"""
        self.glow_pulse = (math.sin(pygame.time.get_ticks() * 0.005) + 1) * 0.5
        
        if self.is_open:
            self.open_animation = min(1.0, self.open_animation + dt * 0.003)
        
        # Check of speler de deur activeert
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < self.activation_range:
            if has_key and crystals_complete and self.is_open:
                self.activated = True
                return True
        
        return False
        
    def get_sprite(self):
        """Geef huidige sprite terug"""
        if self.is_open:
            size = 64
            animated = pygame.Surface((size, size), pygame.SRCALPHA)
            
            # Pulserende glow voor open deur
            glow_alpha = int(30 + self.glow_pulse * 40)
            pygame.draw.ellipse(animated, (100, 150, 255, glow_alpha), 
                              (size//2 - 22, size//2 - 30, 44, 60))
            
            animated.blit(self.sprite_open, (0, 0))
            return animated
        else:
            return self.sprite_closed


class AmmoPack:
    """Een ammo pack die opgepakt kan worden"""
    
    def __init__(self, x, y, ammo_amount=30):
        self.x = x
        self.y = y
        self.collected = False
        self.ammo_amount = ammo_amount
        self.pickup_range = 1.2
        
        # Animatie
        self.float_offset = 0
        self.pulse = 0
        
        # Sprite
        self.sprite = self._create_sprite()
        
    def _create_sprite(self):
        """Maak ammo pack sprite - gouden/bruine doos met kogels"""
        size = 40
        sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        
        cx, cy = size // 2, size // 2
        
        # Glow achtergrond (gouden gloed)
        for r in range(3, 0, -1):
            glow_size = 14 + r * 3
            alpha = 25 - r * 6
            pygame.draw.circle(sprite, (255, 200, 50, alpha), (cx, cy), glow_size)
        
        # Bruine ammo doos
        box_w, box_h = 26, 18
        box_color = (120, 80, 40)
        pygame.draw.rect(sprite, box_color, 
                        (cx - box_w//2, cy - box_h//2 + 2, box_w, box_h))
        pygame.draw.rect(sprite, (90, 60, 30),
                        (cx - box_w//2, cy - box_h//2 + 2, box_w, box_h), 2)
        
        # Highlight op doos
        pygame.draw.rect(sprite, (150, 100, 50),
                        (cx - box_w//2 + 2, cy - box_h//2 + 4, box_w - 4, 3))
        
        # Kogels in de doos (gouden punten)
        bullet_color = (220, 180, 60)
        bullet_tip = (255, 220, 100)
        for i in range(4):
            bx = cx - 9 + i * 6
            by = cy - 3
            # Kogel huls
            pygame.draw.rect(sprite, bullet_color, (bx, by, 4, 10))
            # Kogel punt
            pygame.draw.polygon(sprite, bullet_tip, [
                (bx, by), (bx + 4, by), (bx + 2, by - 4)
            ])
        
        # "AMMO" tekst hint (kleine streepjes)
        pygame.draw.line(sprite, (80, 50, 25), (cx - 8, cy + 8), (cx + 8, cy + 8), 1)
        
        return sprite
        
    def update(self, dt, player_x, player_y):
        """Update animatie"""
        if self.collected:
            return False
            
        # Animatie
        self.float_offset = math.sin(pygame.time.get_ticks() * 0.004 + 1.5) * 0.08
        self.pulse = (math.sin(pygame.time.get_ticks() * 0.005 + 0.5) + 1) * 0.5
        
        return False
        
    def get_sprite(self):
        """Geef sprite met animatie"""
        if self.collected:
            return None
            
        size = 40
        animated = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Pulserende glow
        glow_alpha = int(15 + self.pulse * 20)
        pygame.draw.circle(animated, (255, 200, 100, glow_alpha), 
                          (size//2, size//2), 16)
        
        animated.blit(self.sprite, (0, 0))
        return animated


class HealthPack:
    """Een health pack die opgepakt kan worden"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.collected = False
        self.heal_amount = 35
        self.pickup_range = 1.0
        
        # Animatie
        self.float_offset = 0
        self.pulse = 0
        
        # Sprite
        self.sprite = self._create_sprite()
        
    def _create_sprite(self):
        """Maak health pack sprite - wit/rood kruis"""
        size = 40
        sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        
        cx, cy = size // 2, size // 2
        
        # Glow achtergrond
        for r in range(3, 0, -1):
            glow_size = 15 + r * 3
            alpha = 30 - r * 8
            pygame.draw.circle(sprite, (255, 100, 100, alpha), (cx, cy), glow_size)
        
        # Witte doos achtergrond
        box_size = 22
        pygame.draw.rect(sprite, (255, 255, 255), 
                        (cx - box_size//2, cy - box_size//2, box_size, box_size))
        pygame.draw.rect(sprite, (200, 200, 200),
                        (cx - box_size//2, cy - box_size//2, box_size, box_size), 2)
        
        # Rood kruis
        cross_width = 6
        cross_length = 16
        cross_color = (220, 40, 40)
        
        # Horizontaal deel
        pygame.draw.rect(sprite, cross_color,
                        (cx - cross_length//2, cy - cross_width//2, cross_length, cross_width))
        # Verticaal deel
        pygame.draw.rect(sprite, cross_color,
                        (cx - cross_width//2, cy - cross_length//2, cross_width, cross_length))
        
        # Highlight op kruis
        pygame.draw.rect(sprite, (255, 80, 80),
                        (cx - cross_length//2, cy - cross_width//2, cross_length, 2))
        pygame.draw.rect(sprite, (255, 80, 80),
                        (cx - cross_width//2, cy - cross_length//2, 2, cross_length))
        
        return sprite
        
    def update(self, dt, player_x, player_y):
        """Update animatie en check pickup"""
        if self.collected:
            return False
            
        # Animatie
        self.float_offset = math.sin(pygame.time.get_ticks() * 0.004) * 0.08
        self.pulse = (math.sin(pygame.time.get_ticks() * 0.006) + 1) * 0.5
        
        # Check pickup
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < self.pickup_range:
            self.collected = True
            return True
            
        return False
        
    def get_sprite(self):
        """Geef sprite met animatie"""
        if self.collected:
            return None
            
        # Animated glow
        size = 40
        animated = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Pulserende glow
        glow_alpha = int(15 + self.pulse * 25)
        pygame.draw.circle(animated, (255, 150, 150, glow_alpha), 
                          (size//2, size//2), 18)
        
        animated.blit(self.sprite, (0, 0))
        return animated


class QuestManager:
    """Beheert de crystal collection quest, sleutels en exit deuren"""
    
    def __init__(self, crystal_positions=None, health_pack_positions=None, ammo_pack_positions=None,
                 key_position=None, exit_door_position=None, is_boss_level=False):
        self.crystals = []
        self.collected_count = 0
        self.total_crystals = 0
        self.quest_complete = False
        self.boss_weakened = False
        self.is_boss_level = is_boss_level
        
        # Health packs in het level
        self.health_packs = []
        
        # Ammo packs in het level
        self.ammo_packs = []
        
        # Sleutel systeem
        self.key = None
        self.has_key = False
        
        # Exit deur
        self.exit_door = None
        self.level_complete = False
        
        # Notificaties
        self.notification_text = ""
        self.notification_time = 0
        self.notification_duration = 3000  # 3 seconden
        
        # Quest complete bonus
        self.health_bonus = 50
        self.boss_damage_reduction = 0.5  # Boss doet 50% minder schade
        
        # Spawn items op aangegeven of standaard posities
        self._spawn_health_packs(health_pack_positions)
        self._spawn_ammo_packs(ammo_pack_positions)
        self._spawn_crystals(crystal_positions)
        self._spawn_key(key_position)
        self._spawn_exit_door(exit_door_position)
        
    def _spawn_health_packs(self, positions=None):
        """Plaats health packs door het level"""
        if positions is None:
            positions = [
                (7.5, 7.5),     # Noord-west gang
                (16.5, 16.5),   # Zuid-oost gang
                (11.5, 22.5),   # Zuid centrum
            ]
        
        for x, y in positions:
            self.health_packs.append(HealthPack(x, y))
            
    def _spawn_ammo_packs(self, positions=None):
        """Plaats ammo packs door het level"""
        if positions is None:
            positions = [
                (4.5, 4.5),     # Noord-west
                (19.5, 4.5),    # Noord-oost
                (4.5, 19.5),    # Zuid-west
                (19.5, 19.5),   # Zuid-oost
            ]
        
        for x, y in positions:
            self.ammo_packs.append(AmmoPack(x, y))
            
    def _spawn_key(self, position=None):
        """Plaats de level sleutel"""
        if position is None:
            return  # Geen sleutel in dit level
        
        self.key = LevelKey(position[0], position[1])
        
    def _spawn_exit_door(self, position=None):
        """Plaats de exit deur"""
        if position is None:
            return  # Geen exit deur in dit level
            
        self.exit_door = ExitDoor(position[0], position[1])
        
    def _spawn_crystals(self, positions=None):
        """Plaats kristallen op interessante locaties in het level"""
        if positions is None:
            positions = [
                (2.5, 17.5),    # Linksonder bij wandkleed - Blood Crystal
                (21.5, 6.5),    # Rechtsboven bij wandkleed - Soul Crystal
                (11.5, 11.5),   # Centrum arena - Void Crystal
                (21.5, 17.5),   # Rechtsonder bij wandkleed - Flame Crystal
            ]
        
        for i, (x, y) in enumerate(positions):
            crystal = Crystal(x, y, i)
            self.crystals.append(crystal)
            
        self.total_crystals = len(self.crystals)
        
    def update(self, dt, player, enemy_manager=None):
        """Update quest state, health packs, ammo packs, key en exit door"""
        # Update crystals
        for crystal in self.crystals:
            if not crystal.collected:
                was_collected = crystal.update(dt, player.x, player.y)
                
                if was_collected:
                    self.collected_count += 1
                    self._on_crystal_collected(crystal, enemy_manager)
                    
        # Update health packs (alleen animatie)
        for hp in self.health_packs:
            if not hp.collected:
                hp.update(dt, player.x, player.y)
                
        # Update ammo packs (alleen animatie)
        for ap in self.ammo_packs:
            if not ap.collected:
                ap.update(dt, player.x, player.y)
                
        # Update sleutel
        if self.key and not self.key.collected:
            was_collected = self.key.update(dt, player.x, player.y)
            if was_collected:
                self.has_key = True
                self.notification_text = "KEY COLLECTED! Find the Exit!"
                self.notification_time = pygame.time.get_ticks()
                
                # Open de exit deur als crystals ook compleet zijn
                if self.exit_door and self.quest_complete:
                    self.exit_door.unlock()
                    
        # Update exit deur
        if self.exit_door:
            activated = self.exit_door.update(dt, player.x, player.y, 
                                              self.has_key, self.quest_complete)
            if activated:
                self.level_complete = True
    
    def try_pickup_health_pack(self, player_x, player_y):
        """Probeer een health pack op te pakken, return True als opgepakt"""
        for hp in self.health_packs:
            if not hp.collected:
                dx = player_x - hp.x
                dy = player_y - hp.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                # Grotere pickup range voor makkelijker oppakken
                if distance < 1.2:
                    hp.collected = True
                    return True
        return False
        
    def try_pickup_ammo_pack(self, player_x, player_y):
        """Probeer een ammo pack op te pakken, return ammo_amount als opgepakt, anders 0"""
        for ap in self.ammo_packs:
            if not ap.collected:
                dx = player_x - ap.x
                dy = player_y - ap.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance < ap.pickup_range:
                    ap.collected = True
                    return ap.ammo_amount
        return 0
                    
    def _on_crystal_collected(self, crystal, enemy_manager):
        """Wordt aangeroepen wanneer een kristal wordt opgepakt"""
        remaining = self.total_crystals - self.collected_count
        
        if remaining > 0:
            self.notification_text = f"{crystal.name} collected! ({self.collected_count}/{self.total_crystals})"
        else:
            if self.has_key and self.exit_door:
                self.notification_text = "ALL CRYSTALS! Exit door unlocked!"
            else:
                self.notification_text = "ALL CRYSTALS COLLECTED! Find the Key!"
            self.quest_complete = True
            self.boss_weakened = True
            
            # Verzwak de boss (voor boss levels)
            if enemy_manager and enemy_manager.boss:
                boss = enemy_manager.boss
                boss.damage = int(boss.damage * self.boss_damage_reduction)
                boss.speed *= 0.8
                
            # Open exit deur als we ook de sleutel hebben
            if self.exit_door and self.has_key:
                self.exit_door.unlock()
                
        self.notification_time = pygame.time.get_ticks()
        
    def render_crystals(self, sprite_renderer):
        """Voeg kristallen toe aan sprite renderer"""
        for crystal in self.crystals:
            if not crystal.collected:
                sprite = crystal.get_sprite()
                if sprite:
                    # Floating effect
                    y_offset = crystal.float_offset
                    sprite_renderer.add_sprite(sprite, crystal.x, crystal.y + y_offset, 0.4)
                    
    def render_health_packs(self, sprite_renderer):
        """Voeg health packs toe aan sprite renderer"""
        for hp in self.health_packs:
            if not hp.collected:
                sprite = hp.get_sprite()
                if sprite:
                    # Floating effect
                    sprite_renderer.add_sprite(sprite, hp.x, hp.y + hp.float_offset, 0.3)
                    
    def render_ammo_packs(self, sprite_renderer):
        """Voeg ammo packs toe aan sprite renderer"""
        for ap in self.ammo_packs:
            if not ap.collected:
                sprite = ap.get_sprite()
                if sprite:
                    # Floating effect
                    sprite_renderer.add_sprite(sprite, ap.x, ap.y + ap.float_offset, 0.3)
                    
    def render_key(self, sprite_renderer):
        """Voeg sleutel toe aan sprite renderer"""
        if self.key and not self.key.collected:
            sprite = self.key.get_sprite()
            if sprite:
                sprite_renderer.add_sprite(sprite, self.key.x, self.key.y + self.key.float_offset, 0.4)
                
    def render_exit_door(self, sprite_renderer):
        """Voeg exit deur toe aan sprite renderer"""
        if self.exit_door:
            sprite = self.exit_door.get_sprite()
            if sprite:
                sprite_renderer.add_sprite(sprite, self.exit_door.x, self.exit_door.y, 0.8)
                    
    def draw_hud(self, screen, font, small_font):
        """Teken quest HUD elementen"""
        current_time = pygame.time.get_ticks()
        
        # Quest progress indicator (rechtsboven)
        quest_x = WIDTH - 220
        quest_y = 40
        
        # Achtergrond panel - groter als we key/door hebben
        panel_width = 200
        panel_height = 95 if (self.key or self.exit_door) else 70
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel.fill((20, 10, 30, 180))
        pygame.draw.rect(panel, (100, 50, 150), (0, 0, panel_width, panel_height), 2)
        screen.blit(panel, (quest_x, quest_y))
        
        # Quest titel
        title_text = small_font.render("DEMONIC CRYSTALS", True, (180, 100, 255))
        screen.blit(title_text, (quest_x + 10, quest_y + 5))
        
        # Progress tekst
        if self.quest_complete:
            progress_color = (100, 255, 100)
            progress_str = "COMPLETE!"
        else:
            progress_color = (255, 200, 100)
            progress_str = f"{self.collected_count} / {self.total_crystals}"
            
        progress_text = font.render(progress_str, True, progress_color)
        screen.blit(progress_text, (quest_x + 10, quest_y + 25))
        
        # Mini crystal icons
        for i in range(self.total_crystals):
            icon_x = quest_x + 10 + i * 45
            icon_y = quest_y + 50
            
            if i < self.collected_count:
                # Collected - vol icoon
                color = Crystal.CRYSTAL_TYPES[i]['color']
                pygame.draw.polygon(screen, color, [
                    (icon_x + 8, icon_y),
                    (icon_x + 16, icon_y + 8),
                    (icon_x + 8, icon_y + 16),
                    (icon_x, icon_y + 8),
                ])
            else:
                # Not collected - leeg icoon
                pygame.draw.polygon(screen, (60, 60, 80), [
                    (icon_x + 8, icon_y),
                    (icon_x + 16, icon_y + 8),
                    (icon_x + 8, icon_y + 16),
                    (icon_x, icon_y + 8),
                ], 2)
        
        # Sleutel en deur status
        if self.key or self.exit_door:
            status_y = quest_y + 72
            
            # Sleutel status
            if self.key:
                if self.has_key:
                    key_color = (255, 215, 0)
                    key_text = "KEY"
                else:
                    key_color = (100, 100, 100)
                    key_text = "KEY"
                pygame.draw.circle(screen, key_color, (quest_x + 20, status_y), 8)
                pygame.draw.circle(screen, (40, 30, 20), (quest_x + 20, status_y), 4)
                kt = small_font.render(key_text, True, key_color)
                screen.blit(kt, (quest_x + 32, status_y - 8))
            
            # Exit deur status
            if self.exit_door:
                door_x = quest_x + 100
                if self.exit_door.is_open:
                    door_color = (100, 200, 255)
                    door_text = "EXIT OPEN"
                else:
                    door_color = (150, 50, 50)
                    door_text = "EXIT LOCKED"
                pygame.draw.rect(screen, door_color, (door_x, status_y - 6, 12, 12))
                dt = small_font.render(door_text, True, door_color)
                screen.blit(dt, (door_x + 16, status_y - 8))
        
        # Notification popup (midden bovenaan)
        if current_time - self.notification_time < self.notification_duration:
            # Fade out effect
            alpha = 255
            time_passed = current_time - self.notification_time
            if time_passed > self.notification_duration - 500:
                alpha = int(255 * (self.notification_duration - time_passed) / 500)
                
            notif_surf = font.render(self.notification_text, True, (255, 220, 100))
            
            # Achtergrond
            notif_width = notif_surf.get_width() + 40
            notif_height = 40
            notif_x = HALF_WIDTH - notif_width // 2
            notif_y = 130
            
            bg = pygame.Surface((notif_width, notif_height), pygame.SRCALPHA)
            bg.fill((40, 20, 60, min(200, alpha)))
            pygame.draw.rect(bg, (150, 100, 200, min(255, alpha)), 
                           (0, 0, notif_width, notif_height), 2)
            screen.blit(bg, (notif_x, notif_y))
            
            # Tekst met alpha
            notif_surf.set_alpha(alpha)
            screen.blit(notif_surf, (notif_x + 20, notif_y + 8))
            
    def draw_minimap_crystals(self, screen, offset_x, offset_y, tile_size):
        """Teken kristallen op de minimap"""
        current_time = pygame.time.get_ticks()
        pulse = (math.sin(current_time * 0.005) + 1) * 0.5
        
        for i, crystal in enumerate(self.crystals):
            if not crystal.collected:
                cx = offset_x + crystal.x * tile_size
                cy = offset_y + crystal.y * tile_size
                
                # Pulserende glow
                glow_size = int(4 + pulse * 2)
                pygame.draw.circle(screen, crystal.glow_color, (int(cx), int(cy)), glow_size)
                pygame.draw.circle(screen, crystal.color, (int(cx), int(cy)), 3)
                
    def draw_minimap_health_packs(self, screen, offset_x, offset_y, tile_size):
        """Teken health packs op de minimap"""
        for hp in self.health_packs:
            if not hp.collected:
                hx = offset_x + hp.x * tile_size
                hy = offset_y + hp.y * tile_size
                
                # Wit kruis icoon
                pygame.draw.rect(screen, (255, 255, 255), (int(hx) - 3, int(hy) - 1, 6, 2))
                pygame.draw.rect(screen, (255, 255, 255), (int(hx) - 1, int(hy) - 3, 2, 6))
                
    def draw_minimap_ammo_packs(self, screen, offset_x, offset_y, tile_size):
        """Teken ammo packs op de minimap"""
        for ap in self.ammo_packs:
            if not ap.collected:
                ax = offset_x + ap.x * tile_size
                ay = offset_y + ap.y * tile_size
                
                # Gouden/oranje vierkant icoon
                pygame.draw.rect(screen, (255, 180, 50), (int(ax) - 2, int(ay) - 2, 4, 4))
                
    def draw_minimap_key(self, screen, offset_x, offset_y, tile_size):
        """Teken sleutel op de minimap"""
        if self.key and not self.key.collected:
            kx = offset_x + self.key.x * tile_size
            ky = offset_y + self.key.y * tile_size
            
            # Gouden sleutel icoon
            pygame.draw.circle(screen, (255, 215, 0), (int(kx), int(ky)), 4)
            pygame.draw.circle(screen, (255, 255, 150), (int(kx), int(ky)), 2)
            
    def draw_minimap_exit_door(self, screen, offset_x, offset_y, tile_size):
        """Teken exit deur op de minimap"""
        if self.exit_door:
            dx = offset_x + self.exit_door.x * tile_size
            dy = offset_y + self.exit_door.y * tile_size
            
            if self.exit_door.is_open:
                # Open deur - blauw/paars
                pygame.draw.rect(screen, (100, 150, 255), (int(dx) - 3, int(dy) - 3, 6, 6))
            else:
                # Gesloten deur - rood
                pygame.draw.rect(screen, (150, 50, 50), (int(dx) - 3, int(dy) - 3, 6, 6))

