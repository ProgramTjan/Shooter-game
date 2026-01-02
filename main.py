"""
DOOMIE - Een DOOM-achtige raycasting game in Python
===================================================

Besturing:
    W/UP        - Vooruit
    S/DOWN      - Achteruit
    A/D         - Strafe links/rechts
    MUIS        - Rondkijken (horizontaal + verticaal)
    SPACE/CLICK - Schieten
    1/2/Q       - Wissel wapen
    E           - Open/sluit deur
    M           - Minimap toggle
    ESC         - Afsluiten
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
from map import MAP, MINIMAP_TILE_SIZE
from quest import QuestManager


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
        
        # Level systeem
        self.current_level = 1
        self.transitioning = False
        self.transition_time = 0
        self.transition_duration = 3000  # 3 seconden transitie
        
        # Texture manager
        print("Loading textures...")
        self.textures = TextureManager()
        
        # Door manager
        self.door_manager = DoorManager(MAP)
        print(f"Found {len(self.door_manager.doors)} doors")
        
        # Game objecten
        self.player = Player()
        self.player.set_door_manager(self.door_manager)
        self.player_health = 100
        self.player_max_health = 100
        
        self.raycaster = RayCaster(self)
        self.raycaster.set_textures(self.textures)
        self.raycaster.set_door_manager(self.door_manager)
        
        # Sprite renderer
        self.sprite_renderer = SpriteRenderer(self)
        
        # Vijanden (level 1 = geen boss)
        self.enemy_manager = EnemyManager(level=1)
        print(f"Level 1: Spawned {len(self.enemy_manager.enemies)} enemies")
        
        # Wapens
        self.weapons = WeaponManager()
        
        # Quest systeem
        self.quest = QuestManager()
        print(f"Quest: Collect {self.quest.total_crystals} Demonic Crystals!")
        
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
        
        # Game state
        self.game_over = False
        self.victory = False
        
        # Centreer muis en reset relatieve beweging
        pygame.mouse.set_pos(HALF_WIDTH, HALF_HEIGHT)
        pygame.mouse.get_rel()  # Reset de relatieve beweging buffer
        
    def handle_events(self):
        """Verwerk input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_m:
                    self.show_minimap = not self.show_minimap
                elif event.key == pygame.K_e:
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
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
                    
                    # Check victory - alleen in level 2 als boss verslagen
                    if self.current_level == 2 and self.enemy_manager.alive_count == 0:
                        self.victory = True
                    
    def update(self, dt):
        """Update game state"""
        if self.game_over or self.victory:
            return
            
        # Check level transitie
        if self.transitioning:
            current_time = pygame.time.get_ticks()
            if current_time - self.transition_time > self.transition_duration:
                self.start_boss_level()
            return
            
        # Check of quest compleet is en start transitie
        if self.current_level == 1 and self.quest.quest_complete and not self.transitioning:
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
        
        # Update quest (alleen in level 1)
        if self.current_level == 1:
            self.quest.update(dt, self.player, self.enemy_manager)
        
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
                
    def start_boss_level(self):
        """Start level 2: Boss Arena"""
        self.current_level = 2
        self.transitioning = False
        
        # Reset player positie naar centrum
        self.player.x = 2.5
        self.player.y = 2.5
        self.player.angle = 0.8  # Kijk richting centrum
        
        # Geef health bonus voor het voltooien van de quest
        health_bonus = 50
        self.player_health = min(self.player_max_health, self.player_health + health_bonus)
        
        # Spawn boss level vijanden
        self.enemy_manager = EnemyManager(level=2)
        
        # Reset doors
        self.door_manager = DoorManager(MAP)
        self.player.set_door_manager(self.door_manager)
        self.raycaster.set_door_manager(self.door_manager)
        
        # Reset muis
        pygame.mouse.set_pos(HALF_WIDTH, HALF_HEIGHT)
        pygame.mouse.get_rel()
        
        print("\n" + "="*50)
        print("  LEVEL 2: BOSS ARENA")
        print("  Defeat the DEMON LORD!")
        print("="*50 + "\n")
        
    def draw_transition(self):
        """Teken level transitie scherm"""
        # Donkere overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        # Pulserende achtergrond
        current_time = pygame.time.get_ticks()
        pulse = (math.sin(current_time * 0.005) + 1) * 0.5
        overlay.fill((20, 0, 40, 230))
        self.screen.blit(overlay, (0, 0))
        
        # Titel
        title = self.title_font.render("QUEST COMPLETE!", True, (255, 200, 50))
        title_rect = title.get_rect(center=(HALF_WIDTH, HALF_HEIGHT - 100))
        self.screen.blit(title, title_rect)
        
        # Subtitle
        sub = self.big_font.render("Entering Boss Arena...", True, (200, 100, 255))
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
        pygame.draw.rect(self.screen, (40, 20, 60), (bar_x, bar_y, bar_width, bar_height))
        # Fill
        pygame.draw.rect(self.screen, (180, 80, 255), (bar_x, bar_y, int(bar_width * progress), bar_height))
        # Border
        pygame.draw.rect(self.screen, (100, 50, 150), (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Hint tekst
        hint = self.font.render("Prepare for battle!", True, (150, 150, 200))
        hint_rect = hint.get_rect(center=(HALF_WIDTH, HALF_HEIGHT + 140))
        self.screen.blit(hint, hint_rect)
        
    def draw_minimap(self):
        """Teken minimap in hoek"""
        minimap_size = len(MAP) * MINIMAP_TILE_SIZE
        offset_x = 10
        offset_y = HEIGHT - minimap_size - 10
        
        # Achtergrond
        pygame.draw.rect(self.screen, (20, 20, 20), 
                        (offset_x - 2, offset_y - 2, 
                         minimap_size + 4, minimap_size + 4))
        
        # Teken tiles
        for y, row in enumerate(MAP):
            for x, tile in enumerate(row):
                if tile:
                    if tile == 9:
                        door = self.door_manager.get_door(x, y)
                        if door and door.open_amount > 0.5:
                            color = (100, 70, 45)
                        else:
                            color = (180, 120, 80)
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
                    
        # Teken crystals op minimap
        self.quest.draw_minimap_crystals(self.screen, offset_x, offset_y, MINIMAP_TILE_SIZE)
                    
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
            
        # Controls hint
        hint_text = self.small_font.render("[MOUSE] Look  [1/2/3] Weapon  [SPACE] Shoot  [E] Door", True, (120, 120, 120))
        self.screen.blit(hint_text, (WIDTH - 400, HEIGHT - 25))
        
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
        overlay.fill((0, 50, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        text = self.big_font.render("VICTORY!", True, (50, 255, 50))
        text_rect = text.get_rect(center=(HALF_WIDTH, HALF_HEIGHT - 80))
        self.screen.blit(text, text_rect)
        
        sub_text = self.font.render("The Demon Lord has been vanquished!", True, (200, 255, 200))
        sub_rect = sub_text.get_rect(center=(HALF_WIDTH, HALF_HEIGHT - 20))
        self.screen.blit(sub_text, sub_rect)
        
        sub_text2 = self.font.render("You are the champion!", True, (255, 220, 100))
        sub_rect2 = sub_text2.get_rect(center=(HALF_WIDTH, HALF_HEIGHT + 20))
        self.screen.blit(sub_text2, sub_rect2)
        
        exit_text = self.small_font.render("Press ESC to exit", True, (200, 200, 200))
        exit_rect = exit_text.get_rect(center=(HALF_WIDTH, HALF_HEIGHT + 70))
        self.screen.blit(exit_text, exit_rect)
        
    def draw(self):
        """Render alles naar scherm"""
        self.screen.fill(BLACK)
        
        # Render 3D view
        self.raycaster.render(self.screen)
        
        # Render sprites (vijanden en crystals)
        self.sprite_renderer.clear()
        self.enemy_manager.render(self.sprite_renderer)
        if self.current_level == 1:
            self.quest.render_crystals(self.sprite_renderer)
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
        
        # Quest HUD (alleen in level 1)
        if self.current_level == 1:
            self.quest.draw_hud(self.screen, self.font, self.small_font)
        else:
            # Level 2 indicator
            boss_level_text = self.font.render("LEVEL 2: BOSS ARENA", True, (255, 100, 100))
            self.screen.blit(boss_level_text, (WIDTH - 250, 40))
        
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
        print("\n" + "="*50)
        print("  DOOMIE - DOOM-achtige game in Python")
        print("="*50)
        print("\nBesturing:")
        print("  W/UP        - Vooruit")
        print("  S/DOWN      - Achteruit")
        print("  A/D         - Strafe links/rechts")
        print("  MUIS        - Rondkijken")
        print("  SPACE/CLICK - Schieten (houd ingedrukt voor machinegun)")
        print("  1/2/3/Q     - Wissel wapen (Pistol/MachineGun/Shotgun)")
        print("  E           - Open/sluit deur")
        print("  M           - Minimap toggle")
        print("  ESC         - Afsluiten")
        print("\n" + "="*50)
        print("\n  LEVEL 1: CRYSTAL HUNT")
        print("  QUEST: Collect all 4 Demonic Crystals!")
        print("  Complete the quest to unlock the Boss Arena!")
        print("="*50 + "\n")
        
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
