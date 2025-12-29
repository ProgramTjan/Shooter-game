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


class Game:
    def __init__(self):
        pygame.init()
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)  # Vang de muis
        
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("DOOMIE - A DOOM-like Game")
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.show_minimap = True
        
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
        
        # Vijanden
        self.enemy_manager = EnemyManager()
        print(f"Spawned {len(self.enemy_manager.enemies)} enemies")
        
        # Wapens
        self.weapons = WeaponManager()
        
        # Font voor HUD
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 72)
        
        # Feedback
        self.hit_marker_time = 0
        self.damage_flash_time = 0
        self.kill_text = ""
        self.kill_text_time = 0
        
        # Game state
        self.game_over = False
        self.victory = False
        
        # Centreer muis
        pygame.mouse.set_pos(HALF_WIDTH, HALF_HEIGHT)
        
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
                    self.weapons.switch_to(1)  # Shotgun
                elif event.key == pygame.K_q:
                    self.weapons.next_weapon()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.shoot()
                    
    def shoot(self):
        """Schiet met wapen"""
        if self.game_over or self.victory:
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
                    self.kill_text = "ENEMY KILLED!"
                    self.kill_text_time = pygame.time.get_ticks()
                    
                    # Check victory
                    if self.enemy_manager.alive_count == 0:
                        self.victory = True
                    
    def update(self, dt):
        """Update game state"""
        if self.game_over or self.victory:
            return
            
        # Muis beweging
        mouse_rel = pygame.mouse.get_rel()
        self.player.handle_mouse(mouse_rel)
            
        # Speler beweging
        keys = pygame.key.get_pressed()
        is_moving = keys[pygame.K_w] or keys[pygame.K_s] or keys[pygame.K_a] or keys[pygame.K_d]
        is_moving = is_moving or keys[pygame.K_UP] or keys[pygame.K_DOWN]
        
        self.player.movement(dt)
        self.door_manager.update(dt)
        self.enemy_manager.update(dt, self.player, self.door_manager)
        self.weapons.update(dt, is_moving)
        self.raycaster.raycast(self.player)
        
        # Check vijand aanvallen
        damage = self.enemy_manager.check_player_damage(self.player)
        if damage > 0:
            self.player_health -= damage
            self.damage_flash_time = pygame.time.get_ticks()
            
            if self.player_health <= 0:
                self.player_health = 0
                self.game_over = True
        
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
                pygame.draw.circle(self.screen, (255, 0, 0), (int(ex), int(ey)), 3)
                    
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
        hint_text = self.small_font.render("[MOUSE] Look  [1/2] Weapon  [SPACE] Shoot  [E] Door", True, (120, 120, 120))
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
        overlay.fill((0, 50, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        text = self.big_font.render("VICTORY!", True, (50, 255, 50))
        text_rect = text.get_rect(center=(HALF_WIDTH, HALF_HEIGHT - 50))
        self.screen.blit(text, text_rect)
        
        sub_text = self.font.render("All enemies eliminated!", True, (200, 255, 200))
        sub_rect = sub_text.get_rect(center=(HALF_WIDTH, HALF_HEIGHT + 20))
        self.screen.blit(sub_text, sub_rect)
        
        exit_text = self.small_font.render("Press ESC to exit", True, (200, 200, 200))
        exit_rect = exit_text.get_rect(center=(HALF_WIDTH, HALF_HEIGHT + 60))
        self.screen.blit(exit_text, exit_rect)
        
    def draw(self):
        """Render alles naar scherm"""
        self.screen.fill(BLACK)
        
        # Render 3D view
        self.raycaster.render(self.screen)
        
        # Render sprites (vijanden)
        self.sprite_renderer.clear()
        self.enemy_manager.render(self.sprite_renderer)
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
        print("  SPACE/CLICK - Schieten")
        print("  1/2/Q       - Wissel wapen")
        print("  E           - Open/sluit deur")
        print("  M           - Minimap toggle")
        print("  ESC         - Afsluiten")
        print("\n" + "="*50)
        print("\nKill all enemies to win!")
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
