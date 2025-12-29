"""
Sprite Systeem - Rendert 2D sprites in de 3D wereld
"""
import pygame
import math
from settings import *


def create_enemy_sprite(color_scheme='red', size=64):
    """Maak een demon/vijand sprite met verschillende kleuren"""
    sprite = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Schaal factor
    s = size / 64
    
    # Kleur schemes
    colors = {
        'red': {'body': (180, 40, 40), 'head': (200, 50, 50), 'horn': (100, 30, 30), 'arm': (160, 35, 35)},
        'green': {'body': (40, 140, 40), 'head': (50, 160, 50), 'horn': (30, 80, 30), 'arm': (35, 120, 35)},
        'blue': {'body': (40, 40, 180), 'head': (50, 50, 200), 'horn': (30, 30, 100), 'arm': (35, 35, 160)},
        'purple': {'body': (140, 40, 140), 'head': (160, 50, 160), 'horn': (80, 30, 80), 'arm': (120, 35, 120)},
        'orange': {'body': (200, 100, 30), 'head': (220, 120, 40), 'horn': (120, 60, 20), 'arm': (180, 90, 25)},
        'boss': {'body': (80, 20, 20), 'head': (100, 25, 25), 'horn': (50, 10, 10), 'arm': (70, 18, 18)},
    }
    
    c = colors.get(color_scheme, colors['red'])
    
    # Lichaam
    pygame.draw.ellipse(sprite, c['body'], (int(10*s), int(18*s), int(44*s), int(42*s)))
    
    # Hoofd
    pygame.draw.circle(sprite, c['head'], (int(32*s), int(18*s)), int(14*s))
    
    # Hoorns
    pygame.draw.polygon(sprite, c['horn'], [(int(20*s), int(10*s)), (int(18*s), 0), (int(25*s), int(8*s))])
    pygame.draw.polygon(sprite, c['horn'], [(int(44*s), int(10*s)), (int(46*s), 0), (int(39*s), int(8*s))])
    
    # Ogen (gloeiend)
    eye_color = (255, 0, 0) if color_scheme == 'boss' else (255, 255, 0)
    pygame.draw.circle(sprite, eye_color, (int(26*s), int(16*s)), int(4*s))
    pygame.draw.circle(sprite, eye_color, (int(38*s), int(16*s)), int(4*s))
    pygame.draw.circle(sprite, (0, 0, 0), (int(27*s), int(16*s)), int(2*s))
    pygame.draw.circle(sprite, (0, 0, 0), (int(39*s), int(16*s)), int(2*s))
    
    # Mond
    pygame.draw.ellipse(sprite, (50, 0, 0), (int(24*s), int(24*s), int(16*s), int(6*s)))
    # Tanden
    for i in range(3):
        x = int((26 + i * 5) * s)
        pygame.draw.polygon(sprite, (255, 255, 255), [(x, int(24*s)), (x + int(3*s), int(24*s)), (x + int(1*s), int(28*s))])
    
    # Armen
    pygame.draw.ellipse(sprite, c['arm'], (int(2*s), int(28*s), int(12*s), int(22*s)))
    pygame.draw.ellipse(sprite, c['arm'], (int(50*s), int(28*s), int(12*s), int(22*s)))
    
    # Klauwen
    claw_color = (50, 20, 20)
    for i in range(2):
        pygame.draw.line(sprite, claw_color, (int((5 + i*4)*s), int(48*s)), (int((3 + i*4)*s), int(58*s)), max(1, int(2*s)))
        pygame.draw.line(sprite, claw_color, (int((55 + i*4)*s), int(48*s)), (int((57 + i*4)*s), int(58*s)), max(1, int(2*s)))
    
    return sprite


def create_boss_sprite():
    """Maak een grote boss sprite"""
    size = 128  # Dubbel zo groot
    sprite = pygame.Surface((size, size), pygame.SRCALPHA)
    
    s = size / 64  # Schaal factor
    
    # Donkere kleuren voor boss
    body_color = (100, 20, 20)
    head_color = (120, 25, 25)
    horn_color = (60, 15, 15)
    
    # Lichaam (groter en breder)
    pygame.draw.ellipse(sprite, body_color, (int(8*s), int(20*s), int(48*s), int(40*s)))
    
    # Hoofd
    pygame.draw.circle(sprite, head_color, (int(32*s), int(20*s)), int(16*s))
    
    # Grote hoorns
    pygame.draw.polygon(sprite, horn_color, [(int(18*s), int(10*s)), (int(12*s), 0), (int(24*s), int(6*s))])
    pygame.draw.polygon(sprite, horn_color, [(int(46*s), int(10*s)), (int(52*s), 0), (int(40*s), int(6*s))])
    # Extra hoorns
    pygame.draw.polygon(sprite, horn_color, [(int(24*s), int(6*s)), (int(20*s), int(-5*s)), (int(28*s), int(4*s))])
    pygame.draw.polygon(sprite, horn_color, [(int(40*s), int(6*s)), (int(44*s), int(-5*s)), (int(36*s), int(4*s))])
    
    # Gloeiende rode ogen
    pygame.draw.circle(sprite, (255, 50, 50), (int(24*s), int(18*s)), int(5*s))
    pygame.draw.circle(sprite, (255, 50, 50), (int(40*s), int(18*s)), int(5*s))
    pygame.draw.circle(sprite, (255, 200, 50), (int(24*s), int(18*s)), int(3*s))
    pygame.draw.circle(sprite, (255, 200, 50), (int(40*s), int(18*s)), int(3*s))
    pygame.draw.circle(sprite, (0, 0, 0), (int(25*s), int(18*s)), int(2*s))
    pygame.draw.circle(sprite, (0, 0, 0), (int(41*s), int(18*s)), int(2*s))
    
    # Grote mond met veel tanden
    pygame.draw.ellipse(sprite, (30, 0, 0), (int(20*s), int(28*s), int(24*s), int(10*s)))
    for i in range(5):
        x = int((22 + i * 4) * s)
        pygame.draw.polygon(sprite, (255, 255, 255), 
                          [(x, int(28*s)), (x + int(3*s), int(28*s)), (x + int(1*s), int(35*s))])
    
    # Grote armen met spikes
    pygame.draw.ellipse(sprite, (90, 18, 18), (0, int(25*s), int(16*s), int(28*s)))
    pygame.draw.ellipse(sprite, (90, 18, 18), (int(48*s), int(25*s), int(16*s), int(28*s)))
    
    # Spike details op armen
    spike_color = (60, 15, 15)
    pygame.draw.polygon(sprite, spike_color, [(int(4*s), int(30*s)), (int(-2*s), int(35*s)), (int(6*s), int(38*s))])
    pygame.draw.polygon(sprite, spike_color, [(int(60*s), int(30*s)), (int(66*s), int(35*s)), (int(58*s), int(38*s))])
    
    # Grote klauwen
    for i in range(3):
        pygame.draw.line(sprite, (40, 10, 10), 
                        (int((4 + i*5)*s), int(52*s)), 
                        (int((1 + i*5)*s), int(62*s)), int(3*s))
        pygame.draw.line(sprite, (40, 10, 10), 
                        (int((52 + i*5)*s), int(52*s)), 
                        (int((55 + i*5)*s), int(62*s)), int(3*s))
    
    # Gloeiende aura effect
    for r in range(3):
        alpha = 30 - r * 10
        glow = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (255, 50, 0, alpha), 
                           (int((6-r*2)*s), int((18-r*2)*s), int((52+r*4)*s), int((44+r*4)*s)))
        sprite.blit(glow, (0, 0))
    
    return sprite


def create_dead_enemy_sprite(color_scheme='red'):
    """Maak een dode vijand sprite"""
    size = 64
    sprite = pygame.Surface((size, size), pygame.SRCALPHA)
    
    colors = {
        'red': (100, 30, 30),
        'green': (30, 80, 30),
        'blue': (30, 30, 100),
        'purple': (80, 30, 80),
        'orange': (120, 60, 20),
        'boss': (60, 15, 15),
    }
    body_color = colors.get(color_scheme, (100, 30, 30))
    
    pygame.draw.ellipse(sprite, (100, 20, 20), (5, 45, 54, 18))
    pygame.draw.ellipse(sprite, body_color, (10, 40, 44, 16))
    
    for ex in [22, 38]:
        pygame.draw.line(sprite, (40, 40, 40), (ex-3, 45), (ex+3, 51), 2)
        pygame.draw.line(sprite, (40, 40, 40), (ex+3, 45), (ex-3, 51), 2)
    
    return sprite


def create_dead_boss_sprite():
    """Maak een dode boss sprite"""
    size = 128
    sprite = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Grote bloedplas
    pygame.draw.ellipse(sprite, (80, 15, 15), (10, 80, 108, 40))
    pygame.draw.ellipse(sprite, (60, 12, 12), (20, 75, 88, 35))
    
    # Lichaam
    pygame.draw.ellipse(sprite, (50, 10, 10), (20, 70, 88, 30))
    
    # X ogen
    for ex in [44, 74]:
        pygame.draw.line(sprite, (30, 30, 30), (ex-6, 78), (ex+6, 90), 3)
        pygame.draw.line(sprite, (30, 30, 30), (ex+6, 78), (ex-6, 90), 3)
    
    return sprite


def create_hurt_enemy_sprite(size=64):
    """Maak een gewonde vijand sprite (wit flash)"""
    sprite = pygame.Surface((size, size), pygame.SRCALPHA)
    s = size / 64
    
    white = (255, 255, 255)
    pygame.draw.ellipse(sprite, white, (int(10*s), int(18*s), int(44*s), int(42*s)))
    pygame.draw.circle(sprite, white, (int(32*s), int(18*s)), int(14*s))
    pygame.draw.polygon(sprite, white, [(int(20*s), int(10*s)), (int(18*s), 0), (int(25*s), int(8*s))])
    pygame.draw.polygon(sprite, white, [(int(44*s), int(10*s)), (int(46*s), 0), (int(39*s), int(8*s))])
    pygame.draw.ellipse(sprite, white, (int(2*s), int(28*s), int(12*s), int(22*s)))
    pygame.draw.ellipse(sprite, white, (int(50*s), int(28*s), int(12*s), int(22*s)))
    
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
                'pitch': player.pitch
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
            y = HALF_HEIGHT + pitch - sprite_height / 2
            
            sprite_left = int(max(0, x))
            sprite_right = int(min(WIDTH, x + sprite_width))
            
            for col in range(sprite_left, sprite_right):
                ray_idx = int((col / WIDTH) * NUM_RAYS)
                if 0 <= ray_idx < len(raycaster.ray_results):
                    wall_depth = raycaster.ray_results[ray_idx]['depth']
                    if distance < wall_depth:
                        src_x = int((col - x) / sprite_width * surface.get_width())
                        src_x = max(0, min(surface.get_width() - 1, src_x))
                        
                        col_surface = scaled.subsurface((int(col - x), 0, 1, int(sprite_height)))
                        
                        fog_factor = min(1, distance / MAX_DEPTH)
                        if fog_factor > 0.1:
                            fog_surf = pygame.Surface((1, int(sprite_height)), pygame.SRCALPHA)
                            fog_surf.fill((0, 0, 0, int(fog_factor * 150)))
                            col_surface = col_surface.copy()
                            col_surface.blit(fog_surf, (0, 0))
                        
                        screen.blit(col_surface, (col, y))
