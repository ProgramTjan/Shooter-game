# Level Map - Ondersteunt dynamische level laden
# 0 = lege ruimte
# 1 = rode bakstenen muur
# 2 = wandkleed/tapestry muur
# 3 = fakkel muur
# 4 = donkere stenen muur / hell brick
# 5 = metalen muur / industrial
# 6 = lava (hell thema)
# 9 = deur

# Mini map schaal
MINIMAP_SCALE = 5
MINIMAP_TILE_SIZE = 6

# Default Level layout (24x24) - wordt overschreven door level loader
MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 3, 1, 1, 0, 1, 1, 4, 4, 4, 4, 1, 1, 0, 1, 1, 3, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 9, 0, 0, 1, 4, 0, 0, 4, 1, 0, 0, 9, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 4, 0, 0, 4, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1],
    [1, 3, 0, 0, 0, 0, 1, 0, 0, 9, 0, 0, 0, 0, 9, 0, 0, 1, 0, 0, 0, 0, 3, 1],
    [1, 1, 1, 1, 0, 1, 1, 0, 0, 1, 4, 0, 0, 4, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1],
    [1, 2, 0, 9, 0, 0, 0, 0, 0, 1, 4, 4, 4, 4, 1, 0, 0, 0, 0, 0, 9, 0, 2, 1],
    [1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1],
    [1, 0, 0, 1, 1, 1, 3, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 3, 1, 1, 1, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 3, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 3, 1],
    [1, 1, 9, 1, 1, 0, 0, 9, 0, 9, 0, 0, 0, 0, 9, 0, 9, 0, 0, 1, 1, 9, 1, 1],
    [1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 1, 1, 1, 3, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 3, 1, 1, 1, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 5, 5, 5, 5, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1],
    [1, 2, 0, 9, 0, 0, 0, 0, 0, 1, 5, 0, 0, 5, 1, 0, 0, 0, 0, 0, 9, 0, 2, 1],
    [1, 1, 1, 1, 0, 1, 1, 0, 0, 9, 0, 0, 0, 0, 9, 0, 0, 1, 1, 0, 1, 1, 1, 1],
    [1, 3, 0, 0, 0, 0, 1, 0, 0, 1, 5, 0, 0, 5, 1, 0, 0, 1, 0, 0, 0, 0, 3, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 5, 5, 5, 5, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 9, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 9, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 3, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 3, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

# Actieve map (kan dynamisch veranderd worden)
_active_map = MAP

MAP_WIDTH = len(MAP[0])
MAP_HEIGHT = len(MAP)


def set_active_map(new_map):
    """Stel de actieve map in voor het huidige level"""
    global _active_map, MAP_WIDTH, MAP_HEIGHT
    _active_map = new_map
    MAP_WIDTH = len(new_map[0]) if new_map else 24
    MAP_HEIGHT = len(new_map) if new_map else 24


def get_map_value(x, y, game_map=None):
    """Geeft de waarde van een map tile terug"""
    current_map = game_map if game_map else _active_map
    width = len(current_map[0]) if current_map else 24
    height = len(current_map) if current_map else 24
    
    if 0 <= x < width and 0 <= y < height:
        return current_map[int(y)][int(x)]
    return 1  # Buiten de map = muur


def is_wall(x, y, game_map=None):
    """Checkt of een positie een muur is (1-6, niet 0 en niet deur 9)"""
    val = get_map_value(x, y, game_map)
    return val >= 1 and val <= 6  # 1-6 = muur/lava types, 9 = deur


def is_door(x, y, game_map=None):
    """Checkt of een positie een deur is"""
    return get_map_value(x, y, game_map) == 9
