"""
DOOMIE - Een DOOM-achtige raycasting game in Python
===================================================

Besturing:
    W/UP        - Vooruit
    S/DOWN      - Achteruit
    A/D         - Strafe links/rechts
    MUIS        - Rondkijken (horizontaal + verticaal)
    SPACE/CLICK - Schieten
    1/2/3/Q     - Wissel wapen
    E           - Open/sluit deur
    H           - Gebruik Health Pack
    M           - Minimap toggle
    ESC         - Afsluiten

Levels:
    1. THE DUNGEON - Verzamel de Demonic Crystals
    2. BOSS ARENA - Versla de Demon Lord
    3. THE FACTORY - Ontsnap uit de fabriek
    4. THE INFERNO - Overleef de hel
    5. THE THRONE ROOM - Finale confrontatie
"""

import pygame
import sys
import math
from settings import *
from player import Player
from raycasting import RayCaster
from textures import TextureManager
from door import DoorManager
from sprites import SpriteRenderer
from enemy import EnemyManager
from weapon import WeaponManager
from map import MINIMAP_TILE_SIZE
from quest import QuestManager
from friendly_bot import FriendlyBotManager
from levels import get_level_data, get_total_levels


class Game:
    def __init__(self):
        pygame.init()
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)  # Vang de muis
        
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("DOOMIE - A DOOM-like Game")
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.show_minimap = True
        self.friendly_bot_manager = None
        
        # Level systeem
        self.current_level = 1
        self.total_levels = get_total_levels()
        self.level_data = None
        self.current_map = None
        self.transitioning = False
        self.transition_time = 0
        self.transition_duration = 3000  # 3 seconden transitie
        
        # Story intro systeem
        self.showing_story = True
        self.story_lines = []
        self.story_current_line = 0
        self.story_current_char = 0
        self.story_char_timer = 0
        self.story_char_delay = 40  # ms per karakter (typewriter snelheid)
        self.story_line_delay = 800  # ms pauze na elke regel
        self.story_waiting = False
        self.story_wait_timer = 0
        self.story_complete = False
        self.story_skip_requested = False
        
        # Texture manager (start met dungeon thema)
        print("Loading textures...")
        self.textures = TextureManager(theme='dungeon')
        
        # Laad eerste level (maar start met story)
        self._load_level(1)
        self._start_story()
        
        # Wapens
        self.weapons = WeaponManager()
        
        # Game objecten worden in _load_level gezet
        self.player_health = 100
        self.player_max_health = 100
        
        # Health pack inventory - speler start met 1
        self.health_packs_inventory = 1
        self.health_pack_heal = 35
        
        # Font voor HUD
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 72)
        self.title_font = pygame.font.Font(None, 96)
        
        # Feedback
        self.hit_marker_time = 0
        self.damage_flash_time = 0
        self.kill_text = ""
        self.kill_text_time = 0
        
        # Friendly bot dialogue system
        self.bot_dialogue_active = False
        self.bot_dialogue_message = ""
        self.bot_dialogue_bonus = ""
        self.bot_dialogue_start_time = 0
        self.bot_dialogue_duration = 5000  # 5 seconden zichtbaar
        
        # Game state
        self.game_over = False
        self.victory = False
        
        # Centreer muis en reset relatieve beweging
        pygame.mouse.set_pos(HALF_WIDTH, HALF_HEIGHT)
        pygame.mouse.get_rel()  # Reset de relatieve beweging buffer
        
    def _load_level(self, level_num):
        """Laad een specifiek level"""
        self.level_data = get_level_data(level_num)
        if not self.level_data:
            print(f"Error: Level {level_num} not found!")
            return
            
        self.current_level = level_num
        self.current_map = self.level_data['map']
        
        # Wissel naar juiste thema
        theme = self.level_data.get('theme', 'dungeon')
        self.textures.set_theme(theme)
        
        # Door manager voor dit level
        self.door_manager = DoorManager(self.current_map)
        print(f"\n{'='*50}")
        print(f"  LEVEL {level_num}: {self.level_data['name']}")
        print(f"  {self.level_data['subtitle']}")
        print(f"  Theme: {theme}")
        print(f"  Found {len(self.door_manager.doors)} doors")
        print(f"{'='*50}\n")
        
        # Player
        if not hasattr(self, 'player') or self.player is None:
            self.player = Player()
        
        start_pos = self.level_data.get('player_start', (2.5, 2.5))
        self.player.x = start_pos[0]
        self.player.y = start_pos[1]
        self.player.angle = 0.8
        self.player.set_door_manager(self.door_manager)
        self.player.set_map(self.current_map)
        
        # Raycaster
        if not hasattr(self, 'raycaster') or self.raycaster is None:
            self.raycaster = RayCaster(self)
        self.raycaster.set_textures(self.textures)
        self.raycaster.set_door_manager(self.door_manager)
        self.raycaster.set_map(self.current_map)
        
        # Sprite renderer
        if not hasattr(self, 'sprite_renderer') or self.sprite_renderer is None:
            self.sprite_renderer = SpriteRenderer(self)
        
        # Enemies
        enemy_positions = self.level_data.get('enemy_positions', [])
        boss_position = self.level_data.get('boss_position', None)
        has_boss = self.level_data.get('has_boss', False)
        is_final_boss = self.level_data.get('is_final_boss', False)
        
        self.enemy_manager = EnemyManager(
            level=level_num, 
            custom_positions=enemy_positions,
            boss_position=boss_position if has_boss else None,
            game_map=self.current_map,
            is_final_boss=is_final_boss
        )
        print(f"Spawned {len(self.enemy_manager.enemies)} enemies" + 
              (" (including BOSS!)" if has_boss else ""))
        
        # Quest systeem
        health_pack_positions = self.level_data.get('health_pack_positions', None)
        ammo_pack_positions = self.level_data.get('ammo_pack_positions', None)
        key_position = self.level_data.get('key_position', None)
        exit_door_position = self.level_data.get('exit_door_position', None)
        is_boss_level = self.level_data.get('has_boss', False)
        
        if self.level_data.get('has_quest', False):
            crystal_positions = self.level_data.get('crystal_positions', None)
            self.quest = QuestManager(
                crystal_positions, health_pack_positions, ammo_pack_positions,
                key_position, exit_door_position, is_boss_level
            )
            print(f"Quest: Collect {self.quest.total_crystals} Crystals + Key!")
        else:
            # Boss level - geen crystals/key/exit
            self.quest = QuestManager(
                crystal_positions=[], 
                health_pack_positions=health_pack_positions, 
                ammo_pack_positions=ammo_pack_positions,
                is_boss_level=True
            )
            
        # Friendly help bot
        bot_data = self.level_data.get('bot', None)
        self.friendly_bot_manager = FriendlyBotManager(bot_data, level_num)
        self.bot_dialogue_active = False
        self.bot_dialogue_message = ""
        self.bot_dialogue_bonus = ""
            
        # Reset muis
        pygame.mouse.set_pos(HALF_WIDTH, HALF_HEIGHT)
        pygame.mouse.get_rel()
        
    def _start_story(self):
        """Start de story intro voor het huidige level"""
        self.showing_story = True
        self.story_complete = False
        self.story_skip_requested = False
        self.story_current_line = 0
        self.story_current_char = 0
        self.story_char_timer = pygame.time.get_ticks()
        self.story_waiting = False
        self.story_wait_timer = 0
        
        # Haal story uit level data
        story = self.level_data.get('story', [])
        if not story:
            # Geen story, skip
            self.showing_story = False
            return
            
        self.story_lines = story
        
    def _update_story(self, dt):
        """Update de typewriter effect"""
        if not self.showing_story or self.story_complete:
            return
            
        current_time = pygame.time.get_ticks()
        
        # Skip check - toon alles direct
        if self.story_skip_requested:
            self.story_current_line = len(self.story_lines)
            self.story_complete = True
            return
        
        # Wachten na een regel?
        if self.story_waiting:
            if current_time - self.story_wait_timer > self.story_line_delay:
                self.story_waiting = False
                self.story_current_line += 1
                self.story_current_char = 0
                self.story_char_timer = current_time
            return
            
        # Alle regels gedaan?
        if self.story_current_line >= len(self.story_lines):
            self.story_complete = True
            return
            
        # Huidige regel
        current_line_text = self.story_lines[self.story_current_line]
        
        # Typewriter effect
        if current_time - self.story_char_timer > self.story_char_delay:
            self.story_current_char += 1
            self.story_char_timer = current_time
            
            # Regel compleet?
            if self.story_current_char >= len(current_line_text):
                self.story_waiting = True
                self.story_wait_timer = current_time
                
    def _draw_story(self):
        """Teken het story intro scherm"""
        # Donkere achtergrond
        self.screen.fill((5, 5, 15))
        
        # Sterren effect op achtergrond
        import random
        random.seed(42)
        for _ in range(100):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            brightness = random.randint(30, 100)
            pygame.draw.circle(self.screen, (brightness, brightness, brightness), (x, y), 1)
        
        # Level titel bovenaan
        level_name = self.level_data.get('name', f'LEVEL {self.current_level}')
        title_color = self._get_theme_color()
        
        # Glowing title effect
        title_surf = self.title_font.render(level_name, True, title_color)
        title_rect = title_surf.get_rect(center=(HALF_WIDTH, 80))
        
        # Glow
        glow_surf = self.title_font.render(level_name, True, (title_color[0]//3, title_color[1]//3, title_color[2]//3))
        for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
            self.screen.blit(glow_surf, (title_rect.x + offset[0], title_rect.y + offset[1]))
        self.screen.blit(title_surf, title_rect)
        
        # Level nummer
        level_num_text = self.font.render(f"LEVEL {self.current_level}", True, (150, 150, 150))
        level_num_rect = level_num_text.get_rect(center=(HALF_WIDTH, 130))
        self.screen.blit(level_num_text, level_num_rect)
        
        # Horizontale lijn
        pygame.draw.line(self.screen, title_color, (HALF_WIDTH - 200, 160), (HALF_WIDTH + 200, 160), 2)
        
        # Story tekst met typewriter effect
        story_y = 200
        line_height = 35
        
        for i, line in enumerate(self.story_lines):
            if i < self.story_current_line:
                # Hele regel tonen
                text_to_show = line
                alpha = 255
            elif i == self.story_current_line and not self.story_complete:
                # Huidige regel met typewriter
                text_to_show = line[:self.story_current_char]
                alpha = 255
            else:
                # Nog niet zichtbaar
                continue
                
            if text_to_show:
                # Speciale kleuren voor bepaalde woorden
                if any(word in line.upper() for word in ['DEMON', 'BOSS', 'KING', 'LORD', 'FIREBALLS', 'RAGE', 'INFERNO', 'HELL']):
                    text_color = (255, 100, 100)
                elif any(word in line.upper() for word in ['CRYSTALS', 'KEY', 'EXIT', 'POWER']):
                    text_color = (255, 220, 100)
                elif any(word in line.upper() for word in ['FIGHT', 'DESTROY', 'END THIS']):
                    text_color = (255, 50, 50)
                else:
                    text_color = (200, 200, 220)
                    
                text_surf = self.font.render(text_to_show, True, text_color)
                text_rect = text_surf.get_rect(center=(HALF_WIDTH, story_y + i * line_height))
                self.screen.blit(text_surf, text_rect)
        
        # Objective box onderaan
        if self.story_complete:
            obj_text = self.level_data.get('objective', 'Complete the level')
            
            # Box
            box_width = 500
            box_height = 60
            box_x = HALF_WIDTH - box_width // 2
            box_y = HEIGHT - 150
            
            pygame.draw.rect(self.screen, (30, 20, 40), (box_x, box_y, box_width, box_height))
            pygame.draw.rect(self.screen, title_color, (box_x, box_y, box_width, box_height), 3)
            
            obj_label = self.small_font.render("OBJECTIVE:", True, (150, 150, 150))
            self.screen.blit(obj_label, (box_x + 20, box_y + 8))
            
            obj_surf = self.font.render(obj_text, True, (255, 255, 100))
            self.screen.blit(obj_surf, (box_x + 20, box_y + 28))
        
        # Instructies onderaan
        if self.story_complete:
            hint = "Press SPACE or CLICK to begin"
            hint_color = (100, 255, 100)
            # Pulseren
            pulse = (math.sin(pygame.time.get_ticks() * 0.005) + 1) * 0.5
            hint_alpha = int(150 + pulse * 105)
        else:
            hint = "Press SPACE to skip"
            hint_color = (150, 150, 150)
            hint_alpha = 200
            
        hint_surf = self.small_font.render(hint, True, hint_color)
        hint_rect = hint_surf.get_rect(center=(HALF_WIDTH, HEIGHT - 40))
        self.screen.blit(hint_surf, hint_rect)
        
    def _get_theme_color(self):
        """Haal de thema kleur op"""
        theme = self.level_data.get('theme', 'dungeon')
        if theme == 'industrial':
            return (100, 180, 255)
        elif theme == 'hell':
            return (255, 80, 50)
        else:  # dungeon
            return (180, 100, 255)

    def show_bot_dialogue(self, message, bonus_text=""):
        """Toon een prominente bot dialoog"""
        self.bot_dialogue_active = True
        self.bot_dialogue_message = message
        self.bot_dialogue_bonus = bonus_text
        self.bot_dialogue_start_time = pygame.time.get_ticks()
        
    def handle_events(self):
        """Verwerk input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    
                # Story intro handling
                elif self.showing_story:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        if self.story_complete:
                            # Start het level
                            self.showing_story = False
                        else:
                            # Skip de animatie
                            self.story_skip_requested = True
                            
                # Normale game controls
                elif event.key == pygame.K_m:
                    self.show_minimap = not self.show_minimap
                elif event.key == pygame.K_e:
                    # Probeer eerst bot interactie, dan deur
                    if self.friendly_bot_manager:
                        self.friendly_bot_manager.try_interact(self)
                    self.door_manager.interact(self.player.x, self.player.y, self.player.angle)
                elif event.key == pygame.K_SPACE:
                    self.shoot()
                elif event.key == pygame.K_1:
                    self.weapons.switch_to(0)  # Pistol
                elif event.key == pygame.K_2:
                    self.weapons.switch_to(1)  # MachineGun
                elif event.key == pygame.K_3:
                    self.weapons.switch_to(2)  # Shotgun
                elif event.key == pygame.K_q:
                    self.weapons.next_weapon()
                elif event.key == pygame.K_h:
                    self.use_health_pack()
                elif event.key == pygame.K_i:
                    if self.friendly_bot_manager:
                        self.friendly_bot_manager.try_interact(self.player, self)
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Story handling
                    if self.showing_story:
                        if self.story_complete:
                            self.showing_story = False
                        else:
                            self.story_skip_requested = True
                    else:
                        self.shoot()
                    
    def shoot(self):
        """Schiet met wapen"""
        if self.game_over or self.victory or self.transitioning:
            return
            
        if self.weapons.fire():
            # Check of we een vijand raken
            enemy, distance = self.enemy_manager.get_enemy_at_ray(
                self.player.x, self.player.y, self.player.angle
            )
            
            if enemy:
                # Bereken schade (minder op afstand)
                weapon = self.weapons.current
                damage = weapon.damage * (1 - distance / MAX_DEPTH * 0.5)
                killed = enemy.take_damage(int(damage))
                
                self.hit_marker_time = pygame.time.get_ticks()
                
                if killed:
                    # Speciale tekst voor boss kill
                    if hasattr(enemy, 'is_boss'):
                        self.kill_text = "DEMON LORD DEFEATED!"
                    else:
                        self.kill_text = "ENEMY KILLED!"
                    self.kill_text_time = pygame.time.get_ticks()
                    
                    # Check victory - alleen in finale boss level als alle vijanden verslagen
                    if self.level_data.get('has_boss', False) and self.enemy_manager.alive_count == 0:
                        if self.current_level >= self.total_levels:
                            # Finale overwinning!
                            self.victory = True
                        else:
                            # Naar volgend level
                            self.transitioning = True
                            self.transition_time = pygame.time.get_ticks()
                        
    def use_health_pack(self):
        """Gebruik een health pack uit inventory"""
        if self.game_over or self.victory:
            return
            
        if self.health_packs_inventory > 0 and self.player_health < self.player_max_health:
            self.health_packs_inventory -= 1
            old_health = self.player_health
            self.player_health = min(self.player_max_health, self.player_health + self.health_pack_heal)
            healed = self.player_health - old_health
            self.kill_text = f"+{healed} HP"
            self.kill_text_time = pygame.time.get_ticks()
                    
    def update(self, dt):
        """Update game state"""
        # Story intro update
        if self.showing_story:
            self._update_story(dt)
            return
            
        if self.game_over or self.victory:
            return
            
        # Check level transitie
        if self.transitioning:
            current_time = pygame.time.get_ticks()
            if current_time - self.transition_time > self.transition_duration:
                self._start_next_level()
            return
            
        # Check of level compleet is via exit door
        if self.level_data.get('has_quest', False) and self.quest.level_complete and not self.transitioning:
            self.transitioning = True
            self.transition_time = pygame.time.get_ticks()
            return
            
        # Muis beweging - warp muis terug naar centrum voor oneindige rotatie
        mouse_rel = pygame.mouse.get_rel()
        self.player.handle_mouse(mouse_rel)
        pygame.mouse.set_pos(HALF_WIDTH, HALF_HEIGHT)
            
        # Speler beweging
        keys = pygame.key.get_pressed()
        is_moving = keys[pygame.K_w] or keys[pygame.K_s] or keys[pygame.K_a] or keys[pygame.K_d]
        is_moving = is_moving or keys[pygame.K_UP] or keys[pygame.K_DOWN]
        
        self.player.movement(dt)
        self.door_manager.update(dt)
        self.enemy_manager.update(dt, self.player, self.door_manager)
        self.weapons.update(dt, is_moving)
        self.raycaster.raycast(self.player)
        
        # Update quest en health packs
        self.quest.update(dt, self.player, self.enemy_manager)
        
        # Update friendly bot
        if self.friendly_bot_manager:
            self.friendly_bot_manager.update(dt, self.player)
        
        # Check health pack pickup (automatisch oppakken)
        picked_up = self.quest.try_pickup_health_pack(self.player.x, self.player.y)
        if picked_up:
            self.health_packs_inventory += 1
            self.kill_text = "+1 HEALTH PACK!"
            self.kill_text_time = pygame.time.get_ticks()
            
        # Check ammo pack pickup (automatisch oppakken)
        ammo_picked = self.quest.try_pickup_ammo_pack(self.player.x, self.player.y)
        if ammo_picked > 0:
            self.weapons.add_ammo_all(ammo_picked)
            self.kill_text = f"+{ammo_picked} AMMO!"
            self.kill_text_time = pygame.time.get_ticks()
        
        # Automatisch vuur (houd muis/spatie ingedrukt)
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0] or keys[pygame.K_SPACE]:
            self.shoot()
        
        # Check vijand aanvallen
        damage = self.enemy_manager.check_player_damage(self.player)
        if damage > 0:
            self.player_health -= damage
            self.damage_flash_time = pygame.time.get_ticks()
            
            if self.player_health <= 0:
                self.player_health = 0
                self.game_over = True
                
    def _start_next_level(self):
        """Start het volgende level"""
        next_level = self.current_level + 1
        
        if next_level > self.total_levels:
            # Alle levels voltooid!
            self.victory = True
            self.transitioning = False
            return
            
        self.transitioning = False
        
        # Geef health bonus voor het voltooien van het level
        health_bonus = 30
        self.player_health = min(self.player_max_health, self.player_health + health_bonus)
        
        # Laad het nieuwe level
        self._load_level(next_level)
        
        # Start story intro voor nieuw level
        self._start_story()
        
    def draw_transition(self):
        """Teken level transitie scherm"""
        # Donkere overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        # Pulserende achtergrond - kleur gebaseerd op volgend level thema
        current_time = pygame.time.get_ticks()
        next_level_data = get_level_data(self.current_level + 1)
        
        # Thema kleuren
        theme = next_level_data.get('theme', 'dungeon') if next_level_data else 'dungeon'
        if theme == 'industrial':
            bg_color = (30, 35, 40, 230)
            bar_color = (100, 150, 200)
            text_color = (150, 200, 255)
        elif theme == 'hell':
            bg_color = (40, 10, 10, 230)
            bar_color = (255, 100, 50)
            text_color = (255, 150, 100)
        else:  # dungeon
            bg_color = (20, 0, 40, 230)
            bar_color = (180, 80, 255)
            text_color = (200, 100, 255)
            
        overlay.fill(bg_color)
        self.screen.blit(overlay, (0, 0))
        
        # Titel - level compleet
        if self.level_data.get('has_quest', False):
            title_text = "QUEST COMPLETE!"
        else:
            title_text = "BOSS DEFEATED!"
        title = self.title_font.render(title_text, True, (255, 200, 50))
        title_rect = title.get_rect(center=(HALF_WIDTH, HALF_HEIGHT - 100))
        self.screen.blit(title, title_rect)
        
        # Next level info
        if next_level_data:
            next_name = next_level_data.get('name', 'UNKNOWN')
            sub = self.big_font.render(f"Entering: {next_name}", True, text_color)
        else:
            sub = self.big_font.render("Victory approaching...", True, text_color)
        sub_rect = sub.get_rect(center=(HALF_WIDTH, HALF_HEIGHT))
        self.screen.blit(sub, sub_rect)
        
        # Progress bar
        elapsed = current_time - self.transition_time
        progress = min(1.0, elapsed / self.transition_duration)
        
        bar_width = 400
        bar_height = 20
        bar_x = HALF_WIDTH - bar_width // 2
        bar_y = HALF_HEIGHT + 80
        
        # Background
        pygame.draw.rect(self.screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))
        # Fill
        pygame.draw.rect(self.screen, bar_color, (bar_x, bar_y, int(bar_width * progress), bar_height))
        # Border
        pygame.draw.rect(self.screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Hint tekst
        if next_level_data:
            hint_text = next_level_data.get('subtitle', 'Prepare for battle!')
        else:
            hint_text = "Prepare for battle!"
        hint = self.font.render(hint_text, True, (150, 150, 200))
        hint_rect = hint.get_rect(center=(HALF_WIDTH, HALF_HEIGHT + 140))
        self.screen.blit(hint, hint_rect)
        
    def draw_minimap(self):
        """Teken minimap in hoek"""
        current_map = self.current_map
        minimap_size = len(current_map) * MINIMAP_TILE_SIZE
        offset_x = 10
        offset_y = HEIGHT - minimap_size - 10
        
        # Achtergrond
        pygame.draw.rect(self.screen, (20, 20, 20), 
                        (offset_x - 2, offset_y - 2, 
                         minimap_size + 4, minimap_size + 4))
        
        # Teken tiles
        for y, row in enumerate(current_map):
            for x, tile in enumerate(row):
                if tile:
                    if tile == 9:
                        door = self.door_manager.get_door(x, y)
                        if door and door.open_amount > 0.5:
                            color = (100, 70, 45)
                        else:
                            color = (180, 120, 80)
                    elif tile == 6:
                        # Lava/hazard - rood/oranje
                        color = (200, 80, 30)
                    else:
                        color = WALL_COLORS.get(tile, (100, 100, 100))
                    
                    pygame.draw.rect(self.screen, color,
                                   (offset_x + x * MINIMAP_TILE_SIZE,
                                    offset_y + y * MINIMAP_TILE_SIZE,
                                    MINIMAP_TILE_SIZE - 1,
                                    MINIMAP_TILE_SIZE - 1))
        
        # Teken vijanden op minimap
        for enemy in self.enemy_manager.enemies:
            if enemy.alive:
                ex = offset_x + enemy.x * MINIMAP_TILE_SIZE
                ey = offset_y + enemy.y * MINIMAP_TILE_SIZE
                # Boss is groter en anders gekleurd
                if hasattr(enemy, 'is_boss'):
                    pygame.draw.circle(self.screen, (255, 100, 0), (int(ex), int(ey)), 5)
                else:
                    pygame.draw.circle(self.screen, (255, 0, 0), (int(ex), int(ey)), 2)
        
        # Teken friendly bots op minimap
        if self.friendly_bot_manager:
            self.friendly_bot_manager.draw_minimap(self.screen, offset_x, offset_y, MINIMAP_TILE_SIZE)
                    
        # Teken crystals, items, key en exit deur op minimap
        self.quest.draw_minimap_crystals(self.screen, offset_x, offset_y, MINIMAP_TILE_SIZE)
        self.quest.draw_minimap_health_packs(self.screen, offset_x, offset_y, MINIMAP_TILE_SIZE)
        self.quest.draw_minimap_ammo_packs(self.screen, offset_x, offset_y, MINIMAP_TILE_SIZE)
        self.quest.draw_minimap_key(self.screen, offset_x, offset_y, MINIMAP_TILE_SIZE)
        self.quest.draw_minimap_exit_door(self.screen, offset_x, offset_y, MINIMAP_TILE_SIZE)
                    
        # Teken speler
        player_x = offset_x + self.player.x * MINIMAP_TILE_SIZE
        player_y = offset_y + self.player.y * MINIMAP_TILE_SIZE
        
        pygame.draw.circle(self.screen, (255, 255, 0), 
                          (int(player_x), int(player_y)), 4)
        
        # Kijkrichting
        line_length = 15
        end_x = player_x + math.cos(self.player.angle) * line_length
        end_y = player_y + math.sin(self.player.angle) * line_length
        pygame.draw.line(self.screen, (255, 255, 0),
                        (player_x, player_y), (end_x, end_y), 2)
        
    def _draw_bot_dialogue(self, elapsed):
        """Teken prominente bot dialoog in het midden van het scherm"""
        # Fade in/out
        fade_duration = 500
        if elapsed < fade_duration:
            alpha = int(255 * (elapsed / fade_duration))
        elif elapsed > self.bot_dialogue_duration - fade_duration:
            alpha = int(255 * ((self.bot_dialogue_duration - elapsed) / fade_duration))
        else:
            alpha = 255
            
        # Grote semi-transparante achtergrond
        dialogue_width = 700
        dialogue_height = 180
        dialogue_x = HALF_WIDTH - dialogue_width // 2
        dialogue_y = HALF_HEIGHT - 50
        
        # Achtergrond
        bg_surface = pygame.Surface((dialogue_width, dialogue_height), pygame.SRCALPHA)
        bg_surface.fill((5, 15, 25, int(alpha * 0.9)))
        
        # Glow border
        glow_color = (80, 200, 255)
        pygame.draw.rect(bg_surface, (*glow_color, alpha), (0, 0, dialogue_width, dialogue_height), 4, border_radius=12)
        pygame.draw.rect(bg_surface, (glow_color[0]//2, glow_color[1]//2, glow_color[2]//2, alpha//2), 
                        (4, 4, dialogue_width-8, dialogue_height-8), 2, border_radius=10)
        
        self.screen.blit(bg_surface, (dialogue_x, dialogue_y))
        
        # Bot icoon/naam
        bot_label = self.font.render("FRIENDLY BOT", True, glow_color)
        bot_label.set_alpha(alpha)
        label_rect = bot_label.get_rect(center=(HALF_WIDTH, dialogue_y + 30))
        self.screen.blit(bot_label, label_rect)
        
        # Horizontale lijn
        line_y = dialogue_y + 55
        line_surface = pygame.Surface((dialogue_width - 60, 2), pygame.SRCALPHA)
        line_surface.fill((*glow_color, alpha//2))
        self.screen.blit(line_surface, (dialogue_x + 30, line_y))
        
        # Hoofdbericht
        message_surf = self.font.render(self.bot_dialogue_message, True, (255, 255, 255))
        message_surf.set_alpha(alpha)
        message_rect = message_surf.get_rect(center=(HALF_WIDTH, dialogue_y + 90))
        self.screen.blit(message_surf, message_rect)
        
        # Bonus tekst (groter en opvallender)
        if self.bot_dialogue_bonus:
            bonus_color = (100, 255, 100)  # Groen voor bonussen
            bonus_surf = self.title_font.render(self.bot_dialogue_bonus, True, bonus_color)
            bonus_surf.set_alpha(alpha)
            bonus_rect = bonus_surf.get_rect(center=(HALF_WIDTH, dialogue_y + 140))
            self.screen.blit(bonus_surf, bonus_rect)
            
    def draw_hud(self):
        """Teken HUD elementen"""
        current_time = pygame.time.get_ticks()
        
        # Health bar
        health_width = 200
        health_height = 20
        health_x = 20
        health_y = 20
        
        # Background
        pygame.draw.rect(self.screen, (60, 20, 20), 
                        (health_x, health_y, health_width, health_height))
        # Health
        health_fill = (self.player_health / self.player_max_health) * health_width
        health_color = (50, 200, 50) if self.player_health > 30 else (200, 50, 50)
        pygame.draw.rect(self.screen, health_color,
                        (health_x, health_y, health_fill, health_height))
        # Border
        pygame.draw.rect(self.screen, (100, 100, 100),
                        (health_x, health_y, health_width, health_height), 2)
        # Text
        health_text = self.font.render(f"HP: {self.player_health}", True, WHITE)
        self.screen.blit(health_text, (health_x + 5, health_y))
        
        # Wapen info
        weapon = self.weapons.current
        weapon_text = self.font.render(f"{weapon.name}", True, (200, 200, 200))
        self.screen.blit(weapon_text, (20, 50))
        
        ammo_text = self.font.render(f"AMMO: {weapon.ammo}", True, (200, 200, 50))
        self.screen.blit(ammo_text, (20, 80))
        
        # Enemies left
        enemies_text = self.small_font.render(
            f"Enemies: {self.enemy_manager.alive_count}", True, (200, 100, 100))
        self.screen.blit(enemies_text, (20, 110))
        
        # Health packs inventory
        hp_color = (100, 255, 100) if self.health_packs_inventory > 0 else (100, 100, 100)
        hp_text = self.small_font.render(
            f"Health Packs: {self.health_packs_inventory} [H]", True, hp_color)
        self.screen.blit(hp_text, (20, 130))
        
        # Boss health bar (als boss nog leeft en geactiveerd is)
        if self.enemy_manager.boss_alive:
            boss = self.enemy_manager.boss
            if boss.is_activated:
                # Boss health bar bovenaan scherm
                boss_bar_width = 400
                boss_bar_height = 25
                boss_bar_x = HALF_WIDTH - boss_bar_width // 2
                boss_bar_y = 10
                
                # Background
                pygame.draw.rect(self.screen, (40, 10, 10), 
                                (boss_bar_x, boss_bar_y, boss_bar_width, boss_bar_height))
                # Health
                boss_fill = (boss.health / boss.max_health) * boss_bar_width
                boss_color = (200, 50, 50) if not boss.rage_mode else (255, 100, 0)
                pygame.draw.rect(self.screen, boss_color,
                                (boss_bar_x, boss_bar_y, boss_fill, boss_bar_height))
                # Border
                pygame.draw.rect(self.screen, (150, 50, 50),
                                (boss_bar_x, boss_bar_y, boss_bar_width, boss_bar_height), 3)
                # Text
                boss_name = "DEMON LORD" if not boss.rage_mode else "DEMON LORD [ENRAGED]"
                boss_text = self.font.render(boss_name, True, (255, 200, 200))
                boss_text_rect = boss_text.get_rect(center=(HALF_WIDTH, boss_bar_y + boss_bar_height // 2))
                self.screen.blit(boss_text, boss_text_rect)
        
        # FPS
        fps = int(self.clock.get_fps())
        fps_text = self.small_font.render(f"FPS: {fps}", True, (0, 255, 0))
        self.screen.blit(fps_text, (WIDTH - 80, 10))
        
        # Hit marker
        if current_time - self.hit_marker_time < 200:
            marker_size = 15
            marker_color = (255, 50, 50)
            cx, cy = HALF_WIDTH, HALF_HEIGHT
            pygame.draw.line(self.screen, marker_color, 
                           (cx - marker_size, cy - marker_size),
                           (cx - 5, cy - 5), 3)
            pygame.draw.line(self.screen, marker_color,
                           (cx + marker_size, cy - marker_size),
                           (cx + 5, cy - 5), 3)
            pygame.draw.line(self.screen, marker_color,
                           (cx - marker_size, cy + marker_size),
                           (cx - 5, cy + 5), 3)
            pygame.draw.line(self.screen, marker_color,
                           (cx + marker_size, cy + marker_size),
                           (cx + 5, cy + 5), 3)
        else:
            # Normal crosshair
            crosshair_size = 10
            pygame.draw.line(self.screen, WHITE,
                            (HALF_WIDTH - crosshair_size, HALF_HEIGHT),
                            (HALF_WIDTH + crosshair_size, HALF_HEIGHT), 2)
            pygame.draw.line(self.screen, WHITE,
                            (HALF_WIDTH, HALF_HEIGHT - crosshair_size),
                            (HALF_WIDTH, HALF_HEIGHT + crosshair_size), 2)
        
        # Kill text
        if current_time - self.kill_text_time < 1500:
            kill_surf = self.font.render(self.kill_text, True, (255, 50, 50))
            kill_rect = kill_surf.get_rect(center=(HALF_WIDTH, 100))
            self.screen.blit(kill_surf, kill_rect)
            
        # Friendly bot interact prompt (when near bot)
        if self.friendly_bot_manager and not self.bot_dialogue_active:
            self.friendly_bot_manager.draw_interact_prompt(self.screen, self.font)
            
        # Friendly bot dialogue (prominent display)
        if self.bot_dialogue_active:
            elapsed = current_time - self.bot_dialogue_start_time
            if elapsed < self.bot_dialogue_duration:
                self._draw_bot_dialogue(elapsed)
            else:
                self.bot_dialogue_active = False
            
        # Controls hint
        hint_text = self.small_font.render("[WASD] Move  [1/2/3] Weapon  [E] Interact  [H] Heal", True, (120, 120, 120))
        self.screen.blit(hint_text, (WIDTH - 380, HEIGHT - 25))
        
    def draw_damage_flash(self):
        """Teken rood flash als speler geraakt wordt"""
        current_time = pygame.time.get_ticks()
        if current_time - self.damage_flash_time < 200:
            flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            alpha = int(100 * (1 - (current_time - self.damage_flash_time) / 200))
            flash.fill((255, 0, 0, alpha))
            self.screen.blit(flash, (0, 0))
            
    def draw_game_over(self):
        """Teken game over scherm"""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        text = self.big_font.render("GAME OVER", True, (255, 50, 50))
        text_rect = text.get_rect(center=(HALF_WIDTH, HALF_HEIGHT - 50))
        self.screen.blit(text, text_rect)
        
        sub_text = self.font.render("Press ESC to exit", True, (200, 200, 200))
        sub_rect = sub_text.get_rect(center=(HALF_WIDTH, HALF_HEIGHT + 20))
        self.screen.blit(sub_text, sub_rect)
        
    def draw_victory(self):
        """Teken victory scherm"""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        # Kleurrijke gradient effect
        current_time = pygame.time.get_ticks()
        pulse = (math.sin(current_time * 0.003) + 1) * 0.5
        
        overlay.fill((0, int(40 + pulse * 20), 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Grote titel
        text = self.title_font.render("VICTORY!", True, (50, 255, 50))
        text_rect = text.get_rect(center=(HALF_WIDTH, HALF_HEIGHT - 100))
        self.screen.blit(text, text_rect)
        
        # Subtitels
        sub_text = self.big_font.render("All realms have been conquered!", True, (200, 255, 200))
        sub_rect = sub_text.get_rect(center=(HALF_WIDTH, HALF_HEIGHT - 20))
        self.screen.blit(sub_text, sub_rect)
        
        sub_text2 = self.font.render(f"You completed all {self.total_levels} levels!", True, (255, 220, 100))
        sub_rect2 = sub_text2.get_rect(center=(HALF_WIDTH, HALF_HEIGHT + 30))
        self.screen.blit(sub_text2, sub_rect2)
        
        champion_text = self.font.render("You are the ULTIMATE CHAMPION!", True, (255, 200, 50))
        champion_rect = champion_text.get_rect(center=(HALF_WIDTH, HALF_HEIGHT + 70))
        self.screen.blit(champion_text, champion_rect)
        
        exit_text = self.small_font.render("Press ESC to exit", True, (200, 200, 200))
        exit_rect = exit_text.get_rect(center=(HALF_WIDTH, HALF_HEIGHT + 120))
        self.screen.blit(exit_text, exit_rect)
        
    def draw(self):
        """Render alles naar scherm"""
        # Story intro
        if self.showing_story:
            self._draw_story()
            pygame.display.flip()
            return
            
        self.screen.fill(BLACK)
        
        # Render 3D view
        self.raycaster.render(self.screen)
        
        # Render sprites (vijanden, crystals en health packs)
        self.sprite_renderer.clear()
        self.enemy_manager.render(self.sprite_renderer)
        if self.friendly_bot_manager:
            self.friendly_bot_manager.render(self.sprite_renderer)
        
        # Render crystals, key, exit door alleen voor quest levels
        if self.level_data.get('has_quest', False):
            self.quest.render_crystals(self.sprite_renderer)
            self.quest.render_key(self.sprite_renderer)
            self.quest.render_exit_door(self.sprite_renderer)
        # Health/ammo packs altijd
        self.quest.render_health_packs(self.sprite_renderer)
        self.quest.render_ammo_packs(self.sprite_renderer)
        self.sprite_renderer.render(self.screen, self.player, self.raycaster)
        
        # Damage flash
        self.draw_damage_flash()
        
        # Wapen
        self.weapons.render(self.screen)
        
        # Minimap
        if self.show_minimap:
            self.draw_minimap()
            
        # HUD
        self.draw_hud()
        
        # Quest HUD of Level indicator
        if self.level_data.get('has_quest', False):
            self.quest.draw_hud(self.screen, self.font, self.small_font)
        
        # Level indicator altijd zichtbaar
        level_name = self.level_data.get('name', f'LEVEL {self.current_level}')
        
        # Kleur gebaseerd op thema
        theme = self.level_data.get('theme', 'dungeon')
        if theme == 'industrial':
            level_color = (150, 200, 255)
        elif theme == 'hell':
            level_color = (255, 100, 100)
        else:
            level_color = (200, 150, 255)
            
        level_text = self.small_font.render(f"LEVEL {self.current_level}: {level_name}", True, level_color)
        self.screen.blit(level_text, (WIDTH - 300, 40))
        
        # Level transitie
        if self.transitioning:
            self.draw_transition()
        
        # Game over / Victory
        if self.game_over:
            self.draw_game_over()
        elif self.victory:
            self.draw_victory()
        
        pygame.display.flip()
        
    def run(self):
        """Main game loop"""
        print("\n" + "="*60)
        print("  DOOMIE - DOOM-achtige game in Python")
        print("  Multi-Level Edition")
        print("="*60)
        print("\nBesturing:")
        print("  W/UP        - Vooruit")
        print("  S/DOWN      - Achteruit")
        print("  A/D         - Strafe links/rechts")
        print("  MUIS        - Rondkijken")
        print("  SPACE/CLICK - Schieten (houd ingedrukt voor machinegun)")
        print("  1/2/3/Q     - Wissel wapen (Pistol/MachineGun/Shotgun)")
        print("  H           - Gebruik Health Pack (+35 HP)")
        print("  E           - Open/sluit deur")
        print("  M           - Minimap toggle")
        print("  ESC         - Afsluiten")
        print("\n" + "="*60)
        print(f"\n  LEVELS: {self.total_levels} realms to conquer!")
        print("  1. THE DUNGEON    - Collect Crystals")
        print("  2. BOSS ARENA     - Defeat Demon Lord")
        print("  3. THE FACTORY    - Escape Industrial Hell")
        print("  4. THE INFERNO    - Survive Hell's Depths")
        print("  5. THE THRONE ROOM - Final Confrontation")
        print("="*60 + "\n")
        
        while self.running:
            dt = self.clock.tick(FPS)
            
            self.handle_events()
            self.update(dt)
            self.draw()
            
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
