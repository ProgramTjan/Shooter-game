"""
Sprite Systeem - Rendert 2D sprites in de 3D wereld
"""
import pygame
import math
from settings import *


def create_enemy_sprite(color_scheme='red'):
    """Maak een demon/vijand sprite met verschillende kleuren"""
    size = 64  # Kleiner formaat
    sprite = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Kleur schemes
    colors = {
        'red': {'body': (180, 40, 40), 'head': (200, 50, 50), 'horn': (100, 30, 30), 'arm': (160, 35, 35)},
        'green': {'body': (40, 140, 40), 'head': (50, 160, 50), 'horn': (30, 80, 30), 'arm': (35, 120, 35)},
        'blue': {'body': (40, 40, 180), 'head': (50, 50, 200), 'horn': (30, 30, 100), 'arm': (35, 35, 160)},
        'purple': {'body': (140, 40, 140), 'head': (160, 50, 160), 'horn': (80, 30, 80), 'arm': (120, 35, 120)},
        'orange': {'body': (200, 100, 30), 'head': (220, 120, 40), 'horn': (120, 60, 20), 'arm': (180, 90, 25)},
    }
    
    c = colors.get(color_scheme, colors['red'])
    
    # Lichaam
    pygame.draw.ellipse(sprite, c['body'], (10, 18, 44, 42))
    
    # Hoofd
    pygame.draw.circle(sprite, c['head'], (32, 18), 14)
    
    # Hoorns
    pygame.draw.polygon(sprite, c['horn'], [(20, 10), (18, 0), (25, 8)])
    pygame.draw.polygon(sprite, c['horn'], [(44, 10), (46, 0), (39, 8)])
    
    # Ogen (gloeiend)
    pygame.draw.circle(sprite, (255, 255, 0), (26, 16), 4)
    pygame.draw.circle(sprite, (255, 255, 0), (38, 16), 4)
    pygame.draw.circle(sprite, (0, 0, 0), (27, 16), 2)
    pygame.draw.circle(sprite, (0, 0, 0), (39, 16), 2)
    
    # Mond
    pygame.draw.ellipse(sprite, (50, 0, 0), (24, 24, 16, 6))
    # Tanden
    for i in range(3):
        x = 26 + i * 5
        pygame.draw.polygon(sprite, (255, 255, 255), [(x, 24), (x + 3, 24), (x + 1, 28)])
    
    # Armen
    pygame.draw.ellipse(sprite, c['arm'], (2, 28, 12, 22))
    pygame.draw.ellipse(sprite, c['arm'], (50, 28, 12, 22))
    
    # Klauwen
    claw_color = (50, 20, 20)
    for i in range(2):
        pygame.draw.line(sprite, claw_color, (5 + i*4, 48), (3 + i*4, 58), 2)
        pygame.draw.line(sprite, claw_color, (55 + i*4, 48), (57 + i*4, 58), 2)
    
    return sprite


def create_dead_enemy_sprite(color_scheme='red'):
    """Maak een dode vijand sprite"""
    size = 64
    sprite = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Kleur gebaseerd op scheme
    colors = {
        'red': (100, 30, 30),
        'green': (30, 80, 30),
        'blue': (30, 30, 100),
        'purple': (80, 30, 80),
        'orange': (120, 60, 20),
    }
    body_color = colors.get(color_scheme, (100, 30, 30))
    
    # Bloedplas
    pygame.draw.ellipse(sprite, (100, 20, 20), (5, 45, 54, 18))
    
    # Lichaam (plat)
    pygame.draw.ellipse(sprite, body_color, (10, 40, 44, 16))
    
    # X ogen
    for ex in [22, 38]:
        pygame.draw.line(sprite, (40, 40, 40), (ex-3, 45), (ex+3, 51), 2)
        pygame.draw.line(sprite, (40, 40, 40), (ex+3, 45), (ex-3, 51), 2)
    
    return sprite


def create_hurt_enemy_sprite():
    """Maak een gewonde vijand sprite (wit flash)"""
    size = 64
    sprite = pygame.Surface((size, size), pygame.SRCALPHA)
    
    white = (255, 255, 255)
    pygame.draw.ellipse(sprite, white, (10, 18, 44, 42))
    pygame.draw.circle(sprite, white, (32, 18), 14)
    pygame.draw.polygon(sprite, white, [(20, 10), (18, 0), (25, 8)])
    pygame.draw.polygon(sprite, white, [(44, 10), (46, 0), (39, 8)])
    pygame.draw.ellipse(sprite, white, (2, 28, 12, 22))
    pygame.draw.ellipse(sprite, white, (50, 28, 12, 22))
    
    return sprite


class SpriteRenderer:
    """Rendert sprites in de 3D wereld"""
    
    def __init__(self, game):
        self.game = game
        self.sprites_to_render = []
        
    def add_sprite(self, sprite_surface, x, y, scale=1.0):
        """Voeg sprite toe aan render queue"""
        self.sprites_to_render.append({
            'surface': sprite_surface,
            'x': x,
            'y': y,
            'scale': scale
        })
        
    def clear(self):
        """Leeg de render queue"""
        self.sprites_to_render = []
        
    def render(self, screen, player, raycaster):
        """Render alle sprites met depth sorting"""
        if not self.sprites_to_render:
            return
            
        sprite_data = []
        
        for sprite in self.sprites_to_render:
            dx = sprite['x'] - player.x
            dy = sprite['y'] - player.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < 0.5:
                continue
                
            sprite_angle = math.atan2(dy, dx)
            delta_angle = sprite_angle - player.angle
            
            while delta_angle > math.pi:
                delta_angle -= 2 * math.pi
            while delta_angle < -math.pi:
                delta_angle += 2 * math.pi
                
            if abs(delta_angle) > HALF_FOV + 0.3:
                continue
                
            sprite_data.append({
                'surface': sprite['surface'],
                'distance': distance,
                'delta_angle': delta_angle,
                'scale': sprite['scale'],
                'pitch': player.pitch  # Voeg pitch toe
            })
            
        sprite_data.sort(key=lambda s: s['distance'], reverse=True)
        
        for data in sprite_data:
            self.render_sprite(screen, data, raycaster)
            
    def render_sprite(self, screen, sprite_data, raycaster):
        """Render een enkele sprite"""
        distance = sprite_data['distance']
        delta_angle = sprite_data['delta_angle']
        surface = sprite_data['surface']
        scale = sprite_data['scale']
        pitch = sprite_data.get('pitch', 0)
        
        screen_x = HALF_WIDTH + delta_angle * HALF_WIDTH / HALF_FOV
        
        sprite_height = (SCREEN_DIST / distance) * scale
        sprite_width = sprite_height * (surface.get_width() / surface.get_height())
        
        max_size = HEIGHT * 1.5
        if sprite_height > max_size:
            sprite_height = max_size
            sprite_width = sprite_height * (surface.get_width() / surface.get_height())
            
        if sprite_width > 0 and sprite_height > 0:
            try:
                scaled = pygame.transform.scale(surface, (int(sprite_width), int(sprite_height)))
            except:
                return
                
            x = screen_x - sprite_width / 2
            # Y positie aangepast voor pitch
            y = HALF_HEIGHT + pitch - sprite_height / 2
            
            # Depth check per kolom voor betere occlusie
            sprite_left = int(max(0, x))
            sprite_right = int(min(WIDTH, x + sprite_width))
            
            for col in range(sprite_left, sprite_right):
                ray_idx = int((col / WIDTH) * NUM_RAYS)
                if 0 <= ray_idx < len(raycaster.ray_results):
                    wall_depth = raycaster.ray_results[ray_idx]['depth']
                    if distance < wall_depth:
                        # Render deze kolom van de sprite
                        src_x = int((col - x) / sprite_width * surface.get_width())
                        src_x = max(0, min(surface.get_width() - 1, src_x))
                        
                        col_surface = scaled.subsurface((int(col - x), 0, 1, int(sprite_height)))
                        
                        # Fog effect
                        fog_factor = min(1, distance / MAX_DEPTH)
                        if fog_factor > 0.1:
                            fog_surf = pygame.Surface((1, int(sprite_height)), pygame.SRCALPHA)
                            fog_surf.fill((0, 0, 0, int(fog_factor * 150)))
                            col_surface = col_surface.copy()
                            col_surface.blit(fog_surf, (0, 0))
                        
                        screen.blit(col_surface, (col, y))
