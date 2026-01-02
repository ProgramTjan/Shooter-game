"""
Textuur systeem - Genereert procedurele texturen voor muren en deuren
"""
import pygame
from settings import *

# Textuur grootte
TEXTURE_SIZE = 256
HALF_TEXTURE_SIZE = TEXTURE_SIZE // 2


def create_brick_texture(base_color, mortar_color=(60, 50, 45)):
    """Maak een baksteen textuur"""
    texture = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE))
    texture.fill(mortar_color)
    
    brick_height = 32
    brick_width = 64
    mortar_size = 4
    
    for row in range(TEXTURE_SIZE // brick_height):
        offset = (brick_width // 2) if row % 2 else 0
        y = row * brick_height
        
        for col in range(-1, TEXTURE_SIZE // brick_width + 1):
            x = col * brick_width + offset
            
            # Variatie in kleur
            variation = ((row * 7 + col * 13) % 30) - 15
            color = tuple(max(0, min(255, c + variation)) for c in base_color)
            
            brick_rect = pygame.Rect(
                x + mortar_size // 2,
                y + mortar_size // 2,
                brick_width - mortar_size,
                brick_height - mortar_size
            )
            pygame.draw.rect(texture, color, brick_rect)
            
            # Subtle shading
            highlight = tuple(min(255, c + 20) for c in color)
            shadow = tuple(max(0, c - 30) for c in color)
            
            pygame.draw.line(texture, highlight, 
                           (brick_rect.left, brick_rect.top),
                           (brick_rect.right, brick_rect.top))
            pygame.draw.line(texture, highlight,
                           (brick_rect.left, brick_rect.top),
                           (brick_rect.left, brick_rect.bottom))
            pygame.draw.line(texture, shadow,
                           (brick_rect.right, brick_rect.top),
                           (brick_rect.right, brick_rect.bottom))
            pygame.draw.line(texture, shadow,
                           (brick_rect.left, brick_rect.bottom),
                           (brick_rect.right, brick_rect.bottom))
    
    return texture


def create_stone_texture(base_color):
    """Maak een steen/rots textuur"""
    texture = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE))
    texture.fill(base_color)
    
    import random
    random.seed(42)  # Consistente textuur
    
    # Voeg variatie toe
    for _ in range(500):
        x = random.randint(0, TEXTURE_SIZE - 1)
        y = random.randint(0, TEXTURE_SIZE - 1)
        size = random.randint(2, 8)
        variation = random.randint(-40, 40)
        color = tuple(max(0, min(255, c + variation)) for c in base_color)
        pygame.draw.circle(texture, color, (x, y), size)
    
    # Voeg scheuren toe
    for _ in range(10):
        start = (random.randint(0, TEXTURE_SIZE), random.randint(0, TEXTURE_SIZE))
        end = (start[0] + random.randint(-50, 50), start[1] + random.randint(-50, 50))
        dark = tuple(max(0, c - 50) for c in base_color)
        pygame.draw.line(texture, dark, start, end, 2)
    
    return texture


def create_metal_texture(base_color):
    """Maak een metaal textuur met rivets"""
    texture = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE))
    texture.fill(base_color)
    
    # Horizontale lijnen
    for y in range(0, TEXTURE_SIZE, 32):
        dark = tuple(max(0, c - 30) for c in base_color)
        light = tuple(min(255, c + 30) for c in base_color)
        pygame.draw.line(texture, dark, (0, y), (TEXTURE_SIZE, y), 2)
        pygame.draw.line(texture, light, (0, y + 2), (TEXTURE_SIZE, y + 2), 1)
    
    # Rivets
    rivet_color = tuple(min(255, c + 50) for c in base_color)
    rivet_shadow = tuple(max(0, c - 40) for c in base_color)
    
    for row in range(0, TEXTURE_SIZE, 64):
        for col in range(0, TEXTURE_SIZE, 64):
            # Rivet shadow
            pygame.draw.circle(texture, rivet_shadow, (col + 17, row + 17), 6)
            # Rivet
            pygame.draw.circle(texture, rivet_color, (col + 16, row + 16), 6)
            pygame.draw.circle(texture, base_color, (col + 16, row + 16), 4)
    
    return texture


def create_door_texture():
    """Maak een deur textuur - smaller dan normale muren"""
    texture = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE))
    
    # Achtergrond (bakstenen aan de zijkanten)
    brick_color = (150, 50, 50)
    mortar_color = (60, 50, 45)
    texture.fill(mortar_color)
    
    # Teken bakstenen achtergrond
    brick_height = 32
    brick_width = 64
    for row in range(TEXTURE_SIZE // brick_height):
        offset = (brick_width // 2) if row % 2 else 0
        y = row * brick_height
        for col in range(-1, TEXTURE_SIZE // brick_width + 1):
            x = col * brick_width + offset
            variation = ((row * 7 + col * 13) % 30) - 15
            color = tuple(max(0, min(255, c + variation)) for c in brick_color)
            pygame.draw.rect(texture, color, (x + 2, y + 2, brick_width - 4, brick_height - 4))
    
    # Deur in het midden (half zo breed)
    door_width = TEXTURE_SIZE // 2
    door_start = TEXTURE_SIZE // 4
    
    # Deur basis
    door_color = (100, 70, 45)
    pygame.draw.rect(texture, door_color, (door_start, 0, door_width, TEXTURE_SIZE))
    
    # Frame
    frame_color = (70, 50, 35)
    pygame.draw.rect(texture, frame_color, (door_start, 0, door_width, TEXTURE_SIZE), 12)
    
    # Panelen
    panel_color = (85, 60, 40)
    panel_highlight = (120, 90, 60)
    panel_shadow = (50, 35, 25)
    
    panel_height = 90
    panel_width = 35
    gap = 15
    
    for row in range(2):
        for col in range(2):
            x = door_start + 18 + col * (panel_width + gap)
            y = 20 + row * (panel_height + gap)
            
            # Panel achtergrond
            pygame.draw.rect(texture, panel_color, (x, y, panel_width, panel_height))
            
            # Highlight (linksboven)
            pygame.draw.line(texture, panel_highlight, (x, y), (x + panel_width, y), 2)
            pygame.draw.line(texture, panel_highlight, (x, y), (x, y + panel_height), 2)
            
            # Shadow (rechtsonder)
            pygame.draw.line(texture, panel_shadow, (x + panel_width, y), (x + panel_width, y + panel_height), 2)
            pygame.draw.line(texture, panel_shadow, (x, y + panel_height), (x + panel_width, y + panel_height), 2)
    
    # Deurklink
    knob_x = door_start + door_width - 25
    knob_y = TEXTURE_SIZE // 2
    pygame.draw.circle(texture, (180, 160, 80), (knob_x, knob_y), 8)
    pygame.draw.circle(texture, (220, 200, 100), (knob_x - 1, knob_y - 1), 5)
    pygame.draw.circle(texture, (100, 80, 40), (knob_x, knob_y), 3)
    
    return texture


def create_tech_texture(base_color):
    """Maak een sci-fi/tech textuur"""
    texture = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE))
    texture.fill(base_color)
    
    # Grid patroon
    grid_color = tuple(max(0, c - 20) for c in base_color)
    for x in range(0, TEXTURE_SIZE, 32):
        pygame.draw.line(texture, grid_color, (x, 0), (x, TEXTURE_SIZE), 1)
    for y in range(0, TEXTURE_SIZE, 32):
        pygame.draw.line(texture, grid_color, (0, y), (TEXTURE_SIZE, y), 1)
    
    # Lichtgevende strepen
    glow_color = (100, 200, 255)
    pygame.draw.rect(texture, glow_color, (TEXTURE_SIZE // 2 - 4, 0, 8, TEXTURE_SIZE))
    
    # Tech details
    detail_color = tuple(min(255, c + 40) for c in base_color)
    pygame.draw.rect(texture, detail_color, (20, 20, 60, 40), 2)
    pygame.draw.rect(texture, detail_color, (TEXTURE_SIZE - 80, 20, 60, 40), 2)
    pygame.draw.rect(texture, detail_color, (20, TEXTURE_SIZE - 60, 60, 40), 2)
    pygame.draw.rect(texture, detail_color, (TEXTURE_SIZE - 80, TEXTURE_SIZE - 60, 60, 40), 2)
    
    return texture


def create_tapestry_texture():
    """Maak een wandkleed/tapestry textuur met demonisch patroon"""
    texture = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE))
    
    # Donkerrode stof achtergrond
    base_color = (80, 25, 30)
    texture.fill(base_color)
    
    # Stof textuur effect
    import random
    random.seed(123)
    for _ in range(800):
        x = random.randint(0, TEXTURE_SIZE - 1)
        y = random.randint(0, TEXTURE_SIZE - 1)
        variation = random.randint(-15, 15)
        color = tuple(max(0, min(255, c + variation)) for c in base_color)
        texture.set_at((x, y), color)
    
    # Gouden rand/frame
    gold = (180, 140, 60)
    gold_dark = (120, 90, 40)
    border_width = 16
    
    # Buitenste rand
    pygame.draw.rect(texture, gold_dark, (0, 0, TEXTURE_SIZE, TEXTURE_SIZE), border_width + 4)
    pygame.draw.rect(texture, gold, (4, 4, TEXTURE_SIZE - 8, TEXTURE_SIZE - 8), border_width)
    
    # Binnenste decoratieve rand
    inner_border = 30
    pygame.draw.rect(texture, gold_dark, (inner_border, inner_border, 
                     TEXTURE_SIZE - inner_border*2, TEXTURE_SIZE - inner_border*2), 3)
    
    # Centraal demonisch symbool
    center_x, center_y = TEXTURE_SIZE // 2, TEXTURE_SIZE // 2
    symbol_color = (150, 50, 50)
    symbol_glow = (200, 80, 80)
    
    # Pentagram-achtige vorm
    import math
    points = []
    outer_radius = 70
    inner_radius = 35
    for i in range(5):
        # Buitenste punt
        angle = math.radians(-90 + i * 72)
        points.append((center_x + outer_radius * math.cos(angle),
                      center_y + outer_radius * math.sin(angle)))
        # Binnenste punt
        angle = math.radians(-90 + i * 72 + 36)
        points.append((center_x + inner_radius * math.cos(angle),
                      center_y + inner_radius * math.sin(angle)))
    
    # Teken ster met glow
    pygame.draw.polygon(texture, symbol_glow, points)
    pygame.draw.polygon(texture, symbol_color, points, 3)
    
    # Centrale cirkel
    pygame.draw.circle(texture, symbol_glow, (center_x, center_y), 25)
    pygame.draw.circle(texture, (60, 20, 25), (center_x, center_y), 20)
    pygame.draw.circle(texture, symbol_color, (center_x, center_y), 20, 2)
    
    # Oog in het midden
    pygame.draw.ellipse(texture, (200, 180, 50), (center_x - 12, center_y - 6, 24, 12))
    pygame.draw.ellipse(texture, (50, 20, 20), (center_x - 5, center_y - 4, 10, 8))
    
    # Decoratieve hoek ornamenten
    ornament_color = (160, 120, 50)
    corner_offset = 45
    ornament_size = 20
    
    corners = [(corner_offset, corner_offset), 
               (TEXTURE_SIZE - corner_offset, corner_offset),
               (corner_offset, TEXTURE_SIZE - corner_offset),
               (TEXTURE_SIZE - corner_offset, TEXTURE_SIZE - corner_offset)]
    
    for cx, cy in corners:
        # Klein symbool in elke hoek
        pygame.draw.circle(texture, ornament_color, (cx, cy), ornament_size, 2)
        pygame.draw.line(texture, ornament_color, (cx - 8, cy), (cx + 8, cy), 2)
        pygame.draw.line(texture, ornament_color, (cx, cy - 8), (cx, cy + 8), 2)
    
    # Verticale decoratieve lijnen aan zijkanten
    line_color = (140, 100, 45)
    for y_pos in [60, 100, 156, 196]:
        pygame.draw.line(texture, line_color, (40, y_pos), (55, y_pos), 2)
        pygame.draw.line(texture, line_color, (TEXTURE_SIZE - 55, y_pos), (TEXTURE_SIZE - 40, y_pos), 2)
    
    return texture


def create_torch_wall_texture():
    """Maak een muur textuur met een fakkel/toorts"""
    # Start met basis bakstenen
    texture = create_brick_texture((130, 45, 45))
    
    # Fakkel houder
    holder_color = (60, 50, 40)
    holder_x = TEXTURE_SIZE // 2
    holder_y = TEXTURE_SIZE // 2 + 20
    
    # Metalen houder
    pygame.draw.rect(texture, holder_color, (holder_x - 8, holder_y - 10, 16, 50))
    pygame.draw.rect(texture, (80, 70, 55), (holder_x - 8, holder_y - 10, 16, 50), 2)
    
    # Houten stok
    wood_color = (90, 60, 35)
    pygame.draw.rect(texture, wood_color, (holder_x - 5, holder_y - 60, 10, 70))
    pygame.draw.rect(texture, (110, 75, 45), (holder_x - 5, holder_y - 60, 10, 70), 1)
    
    # Vlam
    flame_colors = [(255, 200, 50), (255, 150, 30), (255, 100, 20), (200, 60, 20)]
    flame_y = holder_y - 65
    
    # Glow achter vlam
    for r in range(4, 0, -1):
        glow_alpha = 40 - r * 8
        glow_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (255, 150, 50, glow_alpha), (30, 40), 15 + r * 5)
        texture.blit(glow_surf, (holder_x - 30, flame_y - 30))
    
    # Vlam vorm
    flame_points = [
        (holder_x, flame_y - 35),      # Top
        (holder_x + 12, flame_y - 10),  # Rechts boven
        (holder_x + 8, flame_y + 5),    # Rechts onder
        (holder_x, flame_y + 10),       # Onder
        (holder_x - 8, flame_y + 5),    # Links onder
        (holder_x - 12, flame_y - 10),  # Links boven
    ]
    pygame.draw.polygon(texture, flame_colors[2], flame_points)
    
    # Binnenste vlam
    inner_points = [
        (holder_x, flame_y - 25),
        (holder_x + 6, flame_y - 8),
        (holder_x + 4, flame_y + 2),
        (holder_x, flame_y + 5),
        (holder_x - 4, flame_y + 2),
        (holder_x - 6, flame_y - 8),
    ]
    pygame.draw.polygon(texture, flame_colors[0], inner_points)
    
    return texture


class TextureManager:
    """Beheert alle texturen in de game"""
    
    def __init__(self):
        self.textures = {}
        self.load_textures()
        
    def load_textures(self):
        """Laad/genereer alle texturen"""
        # Standaard rode bakstenen
        brick_texture = create_brick_texture((150, 50, 50))
        self.textures[1] = brick_texture
        
        # Wandkleed/tapestry muur
        self.textures[2] = create_tapestry_texture()
        
        # Fakkel muur
        self.textures[3] = create_torch_wall_texture()
        
        # Donkere stenen muur
        self.textures[4] = create_stone_texture((70, 65, 60))
        
        # Metalen muur
        self.textures[5] = create_metal_texture((80, 85, 90))
        
        # Deur textuur (smaller, met bakstenen aan zijkanten)
        self.textures['door'] = create_door_texture()
        self.textures['door_side'] = brick_texture
        
        # Converteer voor snellere rendering
        for key in self.textures:
            self.textures[key] = self.textures[key].convert()
            
    def get_texture(self, texture_id):
        """Haal een textuur op"""
        return self.textures.get(texture_id, self.textures[1])
    
    def get_texture_column(self, texture_id, offset, height, darken=False):
        """
        Haal een verticale kolom uit een textuur en schaal deze
        offset: 0.0 - 1.0 positie in de textuur
        height: gewenste hoogte van de kolom
        darken: maak de kolom donkerder (voor schaduw effect)
        """
        texture = self.get_texture(texture_id)
        
        # Bereken x positie in textuur
        tex_x = int(offset * TEXTURE_SIZE) % TEXTURE_SIZE
        
        # Haal kolom uit textuur
        column = texture.subsurface((tex_x, 0, 1, TEXTURE_SIZE))
        
        # Schaal naar gewenste hoogte
        if height > 0:
            scaled = pygame.transform.scale(column, (SCALE, int(height)))
            
            if darken:
                # Maak donkerder voor schaduw effect
                dark_surface = pygame.Surface(scaled.get_size())
                dark_surface.fill((50, 50, 50))
                scaled.blit(dark_surface, (0, 0), special_flags=pygame.BLEND_RGB_SUB)
            
            return scaled
        
        return None

