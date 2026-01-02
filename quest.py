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


class QuestManager:
    """Beheert de crystal collection quest"""
    
    def __init__(self):
        self.crystals = []
        self.collected_count = 0
        self.total_crystals = 0
        self.quest_complete = False
        self.boss_weakened = False
        
        # Notificaties
        self.notification_text = ""
        self.notification_time = 0
        self.notification_duration = 3000  # 3 seconden
        
        # Quest complete bonus
        self.health_bonus = 50
        self.boss_damage_reduction = 0.5  # Boss doet 50% minder schade
        
        self._spawn_crystals()
        
    def _spawn_crystals(self):
        """Plaats kristallen op interessante locaties in het level"""
        # Kristal posities (in verschillende kamers, verspreid door de gangen)
        crystal_positions = [
            (2.5, 17.5),    # Linksonder bij wandkleed - Blood Crystal
            (21.5, 6.5),    # Rechtsboven bij wandkleed - Soul Crystal
            (11.5, 11.5),   # Centrum arena - Void Crystal
            (21.5, 17.5),   # Rechtsonder bij wandkleed - Flame Crystal
        ]
        
        for i, (x, y) in enumerate(crystal_positions):
            crystal = Crystal(x, y, i)
            self.crystals.append(crystal)
            
        self.total_crystals = len(self.crystals)
        
    def update(self, dt, player, enemy_manager=None):
        """Update quest state"""
        for crystal in self.crystals:
            if not crystal.collected:
                was_collected = crystal.update(dt, player.x, player.y)
                
                if was_collected:
                    self.collected_count += 1
                    self._on_crystal_collected(crystal, enemy_manager)
                    
    def _on_crystal_collected(self, crystal, enemy_manager):
        """Wordt aangeroepen wanneer een kristal wordt opgepakt"""
        remaining = self.total_crystals - self.collected_count
        
        if remaining > 0:
            self.notification_text = f"{crystal.name} collected! ({self.collected_count}/{self.total_crystals})"
        else:
            self.notification_text = "ALL CRYSTALS COLLECTED! Boss weakened!"
            self.quest_complete = True
            self.boss_weakened = True
            
            # Verzwak de boss
            if enemy_manager and enemy_manager.boss:
                boss = enemy_manager.boss
                boss.damage = int(boss.damage * self.boss_damage_reduction)
                boss.speed *= 0.8
                
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
                    
    def draw_hud(self, screen, font, small_font):
        """Teken quest HUD elementen"""
        current_time = pygame.time.get_ticks()
        
        # Quest progress indicator (rechtsboven)
        quest_x = WIDTH - 220
        quest_y = 40
        
        # Achtergrond panel
        panel_width = 200
        panel_height = 70
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

