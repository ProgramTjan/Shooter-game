# Game Settings
import math
import pygame

# Initialiseer pygame om scherminfo te krijgen
pygame.init()
_display_info = pygame.display.Info()

# Scherm instellingen (automatische fullscreen resolutie)
WIDTH = _display_info.current_w
HEIGHT = _display_info.current_h
HALF_WIDTH = WIDTH // 2
HALF_HEIGHT = HEIGHT // 2
FPS = 60

# Speler instellingen
PLAYER_POS = (2.5, 1.5)  # Start positie (linksboven)
PLAYER_ANGLE = 0
PLAYER_SPEED = 0.004
PLAYER_ROT_SPEED = 0.002
PLAYER_SIZE_SCALE = 60

# Raycasting instellingen
FOV = math.pi / 3  # 60 graden field of view
HALF_FOV = FOV / 2
NUM_RAYS = WIDTH // 2
HALF_NUM_RAYS = NUM_RAYS // 2
DELTA_ANGLE = FOV / NUM_RAYS
MAX_DEPTH = 20

# Muur instellingen
SCREEN_DIST = HALF_WIDTH / math.tan(HALF_FOV)
SCALE = WIDTH // NUM_RAYS

# Kleuren
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 50, 200)
DARK_GRAY = (40, 40, 40)
FLOOR_COLOR = (60, 40, 30)
CEILING_COLOR = (30, 30, 50)

# Muur kleuren per type (voor minimap en fallback)
WALL_COLORS = {
    1: (150, 50, 50),    # Rode bakstenen
    2: (120, 40, 60),    # Wandkleed (donkerrood)
    3: (180, 120, 60),   # Fakkel muur (warm)
    4: (70, 65, 60),     # Donkere steen
    5: (80, 85, 90),     # Metaal
    9: (180, 120, 80),   # Deur kleur
}

