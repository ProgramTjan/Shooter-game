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


def create_lava_texture():
    """Maak een lava/vuur textuur - gevaarlijke vloer"""
    texture = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE))
    
    import random
    random.seed(666)  # Devil's seed
    
    # Base lava color
    base_color = (180, 60, 20)
    texture.fill(base_color)
    
    # Lava stromen
    for _ in range(150):
        x = random.randint(0, TEXTURE_SIZE - 1)
        y = random.randint(0, TEXTURE_SIZE - 1)
        size = random.randint(10, 40)
        
        # Bright hot spots
        bright = random.randint(200, 255)
        hot_color = (bright, bright // 2, 0)
        pygame.draw.circle(texture, hot_color, (x, y), size)
    
    # Donkere korstjes
    for _ in range(80):
        x = random.randint(0, TEXTURE_SIZE - 1)
        y = random.randint(0, TEXTURE_SIZE - 1)
        size = random.randint(5, 20)
        dark_color = (60, 20, 10)
        pygame.draw.circle(texture, dark_color, (x, y), size)
    
    # Gloeiende aderen
    for _ in range(20):
        start = (random.randint(0, TEXTURE_SIZE), random.randint(0, TEXTURE_SIZE))
        end = (start[0] + random.randint(-80, 80), start[1] + random.randint(-80, 80))
        glow = (255, random.randint(150, 200), random.randint(0, 50))
        pygame.draw.line(texture, glow, start, end, random.randint(2, 6))
    
    return texture


def create_hell_brick_texture():
    """Maak een hel-thema baksteen met gloed"""
    texture = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE))
    
    # Donkere achtergrond
    mortar_color = (30, 10, 10)
    texture.fill(mortar_color)
    
    brick_height = 32
    brick_width = 64
    mortar_size = 4
    
    import random
    random.seed(999)
    
    for row in range(TEXTURE_SIZE // brick_height):
        offset = (brick_width // 2) if row % 2 else 0
        y = row * brick_height
        
        for col in range(-1, TEXTURE_SIZE // brick_width + 1):
            x = col * brick_width + offset
            
            # Donkere rode bakstenen met variatie
            base_r = random.randint(60, 100)
            base_g = random.randint(15, 30)
            base_b = random.randint(10, 25)
            color = (base_r, base_g, base_b)
            
            brick_rect = pygame.Rect(
                x + mortar_size // 2,
                y + mortar_size // 2,
                brick_width - mortar_size,
                brick_height - mortar_size
            )
            pygame.draw.rect(texture, color, brick_rect)
            
            # Gloeiende scheuren
            if random.random() < 0.3:
                glow = (255, random.randint(80, 150), 0)
                crack_x = brick_rect.x + random.randint(5, brick_width - 10)
                crack_y = brick_rect.y + random.randint(2, brick_height - 5)
                pygame.draw.line(texture, glow, 
                               (crack_x, crack_y),
                               (crack_x + random.randint(-15, 15), crack_y + random.randint(-10, 10)), 2)
    
    return texture


def create_industrial_wall_texture():
    """Maak een industriële fabrieksmuur textuur"""
    texture = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE))
    
    # Donkergrijs metaal basis
    base_color = (70, 75, 80)
    texture.fill(base_color)
    
    # Grote metalen platen
    plate_color = (85, 90, 95)
    border_dark = (50, 55, 60)
    border_light = (100, 105, 110)
    
    plate_size = 128
    for row in range(2):
        for col in range(2):
            x = col * plate_size
            y = row * plate_size
            
            # Plaat
            pygame.draw.rect(texture, plate_color, (x + 4, y + 4, plate_size - 8, plate_size - 8))
            
            # 3D effect
            pygame.draw.line(texture, border_light, (x + 4, y + 4), (x + plate_size - 4, y + 4), 2)
            pygame.draw.line(texture, border_light, (x + 4, y + 4), (x + 4, y + plate_size - 4), 2)
            pygame.draw.line(texture, border_dark, (x + plate_size - 4, y + 4), (x + plate_size - 4, y + plate_size - 4), 2)
            pygame.draw.line(texture, border_dark, (x + 4, y + plate_size - 4), (x + plate_size - 4, y + plate_size - 4), 2)
    
    # Rivets in hoeken
    rivet_color = (60, 65, 70)
    rivet_highlight = (110, 115, 120)
    rivet_positions = [
        (16, 16), (TEXTURE_SIZE - 16, 16),
        (16, TEXTURE_SIZE - 16), (TEXTURE_SIZE - 16, TEXTURE_SIZE - 16),
        (TEXTURE_SIZE // 2, 16), (TEXTURE_SIZE // 2, TEXTURE_SIZE - 16),
        (16, TEXTURE_SIZE // 2), (TEXTURE_SIZE - 16, TEXTURE_SIZE // 2),
    ]
    
    for rx, ry in rivet_positions:
        pygame.draw.circle(texture, rivet_color, (rx + 1, ry + 1), 6)
        pygame.draw.circle(texture, rivet_highlight, (rx, ry), 6)
        pygame.draw.circle(texture, rivet_color, (rx, ry), 4)
    
    # Waarschuwingsstrepen
    warning_y = TEXTURE_SIZE // 2 - 10
    stripe_width = 20
    for i in range(0, TEXTURE_SIZE + stripe_width, stripe_width * 2):
        pygame.draw.polygon(texture, (200, 180, 0), [
            (i, warning_y),
            (i + stripe_width, warning_y),
            (i + stripe_width + 10, warning_y + 20),
            (i + 10, warning_y + 20)
        ])
    
    return texture


def create_rusty_pipe_texture():
    """Maak een roestige pijp/buis textuur"""
    texture = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE))
    
    import random
    random.seed(777)
    
    # Basis roestig metaal
    base_color = (100, 70, 50)
    texture.fill(base_color)
    
    # Verticale pijp
    pipe_x = TEXTURE_SIZE // 4
    pipe_width = TEXTURE_SIZE // 2
    pipe_color = (80, 85, 75)
    
    # Pijp basis
    pygame.draw.rect(texture, pipe_color, (pipe_x, 0, pipe_width, TEXTURE_SIZE))
    
    # Highlight aan linkerkant
    highlight = (110, 115, 105)
    pygame.draw.rect(texture, highlight, (pipe_x, 0, 10, TEXTURE_SIZE))
    
    # Schaduw aan rechterkant
    shadow = (50, 55, 45)
    pygame.draw.rect(texture, shadow, (pipe_x + pipe_width - 10, 0, 10, TEXTURE_SIZE))
    
    # Roest vlekken
    for _ in range(30):
        x = pipe_x + random.randint(10, pipe_width - 20)
        y = random.randint(0, TEXTURE_SIZE)
        size = random.randint(3, 12)
        rust = (random.randint(100, 140), random.randint(50, 70), random.randint(20, 40))
        pygame.draw.circle(texture, rust, (x, y), size)
    
    # Pijp ringen
    ring_color = (60, 65, 55)
    ring_highlight = (90, 95, 85)
    for y in [40, TEXTURE_SIZE // 2, TEXTURE_SIZE - 40]:
        pygame.draw.rect(texture, ring_color, (pipe_x - 5, y - 8, pipe_width + 10, 16))
        pygame.draw.line(texture, ring_highlight, (pipe_x - 5, y - 8), (pipe_x + pipe_width + 5, y - 8), 2)
    
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
    """Beheert alle texturen in de game - ondersteunt meerdere thema's"""
    
    def __init__(self, theme='dungeon'):
        self.textures = {}
        self.theme = theme
        self.all_themes = {}
        self.load_all_themes()
        self.set_theme(theme)
        
    def load_all_themes(self):
        """Laad texturen voor alle thema's"""
        # ===========================================
        # DUNGEON THEME - Klassieke kerker
        # ===========================================
        dungeon = {}
        brick_texture = create_brick_texture((150, 50, 50))
        dungeon[1] = brick_texture
        dungeon[2] = create_tapestry_texture()
        dungeon[3] = create_torch_wall_texture()
        dungeon[4] = create_stone_texture((70, 65, 60))
        dungeon[5] = create_metal_texture((80, 85, 90))
        dungeon[6] = create_stone_texture((50, 50, 60))  # Placeholder
        dungeon['door'] = create_door_texture()
        dungeon['door_side'] = brick_texture
        dungeon['floor_color'] = (40, 35, 30)
        dungeon['ceiling_color'] = (30, 25, 25)
        self.all_themes['dungeon'] = dungeon
        
        # ===========================================
        # INDUSTRIAL THEME - Verlaten fabriek
        # ===========================================
        industrial = {}
        metal_base = create_industrial_wall_texture()
        industrial[1] = metal_base
        industrial[2] = create_rusty_pipe_texture()
        industrial[3] = create_metal_texture((70, 75, 80))
        industrial[4] = create_industrial_wall_texture()
        industrial[5] = create_metal_texture((90, 95, 100))
        industrial[6] = create_stone_texture((60, 60, 65))
        industrial['door'] = create_metal_door_texture()
        industrial['door_side'] = metal_base
        industrial['floor_color'] = (45, 45, 50)
        industrial['ceiling_color'] = (35, 35, 40)
        self.all_themes['industrial'] = industrial
        
        # ===========================================
        # HELL THEME - Vulkanische onderwereld
        # ===========================================
        hell = {}
        hell_brick = create_hell_brick_texture()
        hell[1] = hell_brick
        hell[2] = create_hell_brick_texture()
        hell[3] = create_torch_wall_texture()  # Re-use torch
        hell[4] = create_hell_brick_texture()
        hell[5] = create_stone_texture((50, 30, 30))
        hell[6] = create_lava_texture()  # LAVA!
        hell['door'] = create_hell_door_texture()
        hell['door_side'] = hell_brick
        hell['floor_color'] = (50, 25, 20)
        hell['ceiling_color'] = (40, 15, 15)
        self.all_themes['hell'] = hell
        
        # Converteer alle texturen voor snellere rendering
        for theme_name in self.all_themes:
            for key in self.all_themes[theme_name]:
                if isinstance(self.all_themes[theme_name][key], pygame.Surface):
                    self.all_themes[theme_name][key] = self.all_themes[theme_name][key].convert()
    
    def set_theme(self, theme):
        """Wissel naar een ander thema"""
        if theme in self.all_themes:
            self.theme = theme
            self.textures = self.all_themes[theme]
            print(f"Texture theme set to: {theme}")
        else:
            print(f"Unknown theme: {theme}, using dungeon")
            self.theme = 'dungeon'
            self.textures = self.all_themes['dungeon']
            
    def get_floor_color(self):
        """Haal vloerkleur op voor huidige thema"""
        return self.textures.get('floor_color', (40, 35, 30))
    
    def get_ceiling_color(self):
        """Haal plafondkleur op voor huidige thema"""
        return self.textures.get('ceiling_color', (30, 25, 25))
            
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


def create_metal_door_texture():
    """Maak een metalen industriële deur"""
    texture = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE))
    
    # Achtergrond
    base = (70, 75, 80)
    texture.fill(base)
    
    # Deur in het midden
    door_width = TEXTURE_SIZE // 2
    door_start = TEXTURE_SIZE // 4
    
    # Deur plaat
    door_color = (90, 95, 100)
    pygame.draw.rect(texture, door_color, (door_start, 0, door_width, TEXTURE_SIZE))
    
    # Frame
    frame_color = (60, 65, 70)
    pygame.draw.rect(texture, frame_color, (door_start, 0, door_width, TEXTURE_SIZE), 8)
    
    # Waarschuwingsstrepen
    warning_color = (200, 180, 0)
    black = (30, 30, 30)
    stripe_height = 30
    y_pos = TEXTURE_SIZE - stripe_height - 20
    
    for i in range(door_start, door_start + door_width, 20):
        pygame.draw.polygon(texture, warning_color, [
            (i, y_pos),
            (i + 10, y_pos),
            (i + 20, y_pos + stripe_height),
            (i + 10, y_pos + stripe_height)
        ])
    
    # Hendel
    handle_color = (120, 125, 130)
    pygame.draw.rect(texture, handle_color, (door_start + door_width - 30, TEXTURE_SIZE // 2 - 20, 15, 40))
    pygame.draw.circle(texture, (80, 85, 90), (door_start + door_width - 22, TEXTURE_SIZE // 2), 8)
    
    # Ventilatierooster
    vent_color = (40, 45, 50)
    vent_y = 40
    for i in range(6):
        pygame.draw.rect(texture, vent_color, (door_start + 20, vent_y + i * 12, door_width - 40, 6))
    
    return texture


def create_hell_door_texture():
    """Maak een helse deur met gloeiende symbolen"""
    texture = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE))
    
    # Achtergrond donker
    base = (40, 15, 15)
    texture.fill(base)
    
    # Deur in het midden
    door_width = TEXTURE_SIZE // 2
    door_start = TEXTURE_SIZE // 4
    
    # Deur basis - donker hout/metaal
    door_color = (60, 25, 20)
    pygame.draw.rect(texture, door_color, (door_start, 0, door_width, TEXTURE_SIZE))
    
    # Frame met gloed
    frame_glow = (150, 50, 30)
    pygame.draw.rect(texture, frame_glow, (door_start, 0, door_width, TEXTURE_SIZE), 10)
    
    # Gloeiend symbool in midden
    import math
    center_x = TEXTURE_SIZE // 2
    center_y = TEXTURE_SIZE // 2
    
    # Pentagram
    glow_color = (255, 100, 50)
    points = []
    for i in range(5):
        angle = math.radians(-90 + i * 72)
        points.append((center_x + 50 * math.cos(angle), center_y + 50 * math.sin(angle)))
    
    # Verbind punten voor ster
    for i in range(5):
        pygame.draw.line(texture, glow_color, points[i], points[(i + 2) % 5], 4)
    
    # Centrale gloed
    pygame.draw.circle(texture, (200, 80, 40), (center_x, center_y), 15)
    pygame.draw.circle(texture, (255, 150, 50), (center_x, center_y), 8)
    
    # Spijkers/decoratie
    spike_color = (100, 40, 30)
    for y in [30, TEXTURE_SIZE - 30]:
        for x_off in [20, door_width - 20]:
            pygame.draw.circle(texture, spike_color, (door_start + x_off, y), 8)
            pygame.draw.circle(texture, glow_color, (door_start + x_off, y), 4)
    
    return texture

