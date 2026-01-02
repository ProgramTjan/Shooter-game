"""
DOOMIE Level Editor
====================
Visuele editor om levels te ontwerpen.

Besturing:
    Linker muisknop    - Plaats geselecteerde tile
    Rechter muisknop   - Wis tile (maak leeg)
    Scroll wiel        - Wissel tussen tile types
    
    0 = Leeg (zwart)
    1 = Rode bakstenen
    2 = Wandkleed/Tapestry
    3 = Fakkel muur
    4 = Donkere steen
    5 = Metaal
    9 = Deur
    
    S = Opslaan naar map.py
    L = Laden vanuit map.py
    C = Wis hele map
    N = Nieuwe grotere/kleinere map
    G = Toggle grid
    P = Plaats speler start positie
    
    Pijltjes = Scroll als map groter is dan scherm
    +/- = Zoom in/uit
    ESC = Afsluiten
"""

import pygame
import sys
import os

# Initialiseer pygame
pygame.init()

# Editor instellingen
EDITOR_WIDTH = 1400
EDITOR_HEIGHT = 900
TOOLBAR_HEIGHT = 120
TILE_SIZE = 32  # Standaard tile grootte in editor

# Kleuren voor tiles
TILE_COLORS = {
    0: (20, 20, 30),      # Leeg - donker
    1: (150, 50, 50),     # Rode bakstenen
    2: (120, 40, 60),     # Wandkleed
    3: (180, 120, 60),    # Fakkel
    4: (70, 65, 60),      # Donkere steen
    5: (80, 85, 90),      # Metaal
    9: (140, 100, 60),    # Deur
}

TILE_NAMES = {
    0: "Leeg",
    1: "Bakstenen",
    2: "Wandkleed",
    3: "Fakkel",
    4: "Steen",
    5: "Metaal",
    9: "Deur",
}

# UI kleuren
BG_COLOR = (30, 30, 40)
TOOLBAR_BG = (40, 40, 55)
GRID_COLOR = (60, 60, 80)
SELECT_COLOR = (255, 200, 50)
TEXT_COLOR = (220, 220, 230)
ACCENT_COLOR = (100, 150, 255)


class LevelEditor:
    def __init__(self):
        self.screen = pygame.display.set_mode((EDITOR_WIDTH, EDITOR_HEIGHT))
        pygame.display.set_caption("DOOMIE Level Editor")
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Fonts
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 22)
        self.title_font = pygame.font.Font(None, 36)
        
        # Map data
        self.map_width = 24
        self.map_height = 24
        self.map_data = [[0 for _ in range(self.map_width)] for _ in range(self.map_height)]
        
        # Speler start positie
        self.player_start = (2.5, 1.5)
        
        # Editor state
        self.selected_tile = 1
        self.tile_types = [0, 1, 2, 3, 4, 5, 9]
        self.show_grid = True
        self.zoom = 1.0
        self.scroll_x = 0
        self.scroll_y = 0
        
        # Berekende waardes
        self.update_dimensions()
        
        # Mouse state
        self.mouse_held = False
        self.right_mouse_held = False
        
        # Berichten
        self.message = ""
        self.message_time = 0
        
        # Laad bestaande map indien beschikbaar
        self.load_map()
        
    def update_dimensions(self):
        """Update berekende dimensies op basis van zoom"""
        self.tile_display_size = int(TILE_SIZE * self.zoom)
        self.map_area_height = EDITOR_HEIGHT - TOOLBAR_HEIGHT
        
    def show_message(self, text):
        """Toon een tijdelijk bericht"""
        self.message = text
        self.message_time = pygame.time.get_ticks()
        
    def get_tile_at_mouse(self, mx, my):
        """Bereken welke tile onder de muis is"""
        if my < TOOLBAR_HEIGHT:
            return None, None
            
        # Bereken tile positie
        tx = int((mx + self.scroll_x) / self.tile_display_size)
        ty = int((my - TOOLBAR_HEIGHT + self.scroll_y) / self.tile_display_size)
        
        if 0 <= tx < self.map_width and 0 <= ty < self.map_height:
            return tx, ty
        return None, None
        
    def set_tile(self, tx, ty, value):
        """Zet een tile waarde"""
        if tx is not None and ty is not None:
            if 0 <= tx < self.map_width and 0 <= ty < self.map_height:
                self.map_data[ty][tx] = value
                
    def handle_events(self):
        """Verwerk input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event)
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Links
                    self.mouse_held = True
                    mx, my = pygame.mouse.get_pos()
                    
                    # Check toolbar clicks
                    if my < TOOLBAR_HEIGHT:
                        self.handle_toolbar_click(mx, my)
                    else:
                        tx, ty = self.get_tile_at_mouse(mx, my)
                        self.set_tile(tx, ty, self.selected_tile)
                        
                elif event.button == 3:  # Rechts
                    self.right_mouse_held = True
                    mx, my = pygame.mouse.get_pos()
                    tx, ty = self.get_tile_at_mouse(mx, my)
                    self.set_tile(tx, ty, 0)
                    
                elif event.button == 4:  # Scroll up
                    idx = self.tile_types.index(self.selected_tile)
                    idx = (idx + 1) % len(self.tile_types)
                    self.selected_tile = self.tile_types[idx]
                    
                elif event.button == 5:  # Scroll down
                    idx = self.tile_types.index(self.selected_tile)
                    idx = (idx - 1) % len(self.tile_types)
                    self.selected_tile = self.tile_types[idx]
                    
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_held = False
                elif event.button == 3:
                    self.right_mouse_held = False
                    
    def handle_keydown(self, event):
        """Verwerk toetsenbord input"""
        if event.key == pygame.K_ESCAPE:
            self.running = False
            
        elif event.key == pygame.K_s:
            self.save_map()
            
        elif event.key == pygame.K_l:
            self.load_map()
            
        elif event.key == pygame.K_c:
            self.clear_map()
            
        elif event.key == pygame.K_g:
            self.show_grid = not self.show_grid
            self.show_message("Grid: " + ("AAN" if self.show_grid else "UIT"))
            
        elif event.key == pygame.K_n:
            self.new_map_dialog()
            
        elif event.key == pygame.K_p:
            self.show_message("Klik op speler start positie...")
            # Dit wordt afgehandeld in een speciale modus
            
        elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
            self.zoom = min(3.0, self.zoom + 0.25)
            self.update_dimensions()
            self.show_message(f"Zoom: {int(self.zoom * 100)}%")
            
        elif event.key == pygame.K_MINUS:
            self.zoom = max(0.5, self.zoom - 0.25)
            self.update_dimensions()
            self.show_message(f"Zoom: {int(self.zoom * 100)}%")
            
        # Nummer toetsen voor tile selectie
        elif event.key == pygame.K_0:
            self.selected_tile = 0
        elif event.key == pygame.K_1:
            self.selected_tile = 1
        elif event.key == pygame.K_2:
            self.selected_tile = 2
        elif event.key == pygame.K_3:
            self.selected_tile = 3
        elif event.key == pygame.K_4:
            self.selected_tile = 4
        elif event.key == pygame.K_5:
            self.selected_tile = 5
        elif event.key == pygame.K_9:
            self.selected_tile = 9
            
    def handle_toolbar_click(self, mx, my):
        """Verwerk klik op toolbar"""
        # Tile selector buttons
        start_x = 20
        for i, tile_type in enumerate(self.tile_types):
            btn_x = start_x + i * 55
            if btn_x <= mx <= btn_x + 45 and 50 <= my <= 95:
                self.selected_tile = tile_type
                return
                
    def update(self):
        """Update editor state"""
        # Pijltjes voor scrolling
        keys = pygame.key.get_pressed()
        scroll_speed = 10
        
        if keys[pygame.K_LEFT]:
            self.scroll_x = max(0, self.scroll_x - scroll_speed)
        if keys[pygame.K_RIGHT]:
            max_scroll = max(0, self.map_width * self.tile_display_size - EDITOR_WIDTH)
            self.scroll_x = min(max_scroll, self.scroll_x + scroll_speed)
        if keys[pygame.K_UP]:
            self.scroll_y = max(0, self.scroll_y - scroll_speed)
        if keys[pygame.K_DOWN]:
            max_scroll = max(0, self.map_height * self.tile_display_size - self.map_area_height)
            self.scroll_y = min(max_scroll, self.scroll_y + scroll_speed)
            
        # Continuous painting met muis ingedrukt
        mx, my = pygame.mouse.get_pos()
        if self.mouse_held and my >= TOOLBAR_HEIGHT:
            tx, ty = self.get_tile_at_mouse(mx, my)
            self.set_tile(tx, ty, self.selected_tile)
        elif self.right_mouse_held and my >= TOOLBAR_HEIGHT:
            tx, ty = self.get_tile_at_mouse(mx, my)
            self.set_tile(tx, ty, 0)
            
    def draw_toolbar(self):
        """Teken de toolbar"""
        # Achtergrond
        pygame.draw.rect(self.screen, TOOLBAR_BG, (0, 0, EDITOR_WIDTH, TOOLBAR_HEIGHT))
        pygame.draw.line(self.screen, ACCENT_COLOR, (0, TOOLBAR_HEIGHT - 1), 
                        (EDITOR_WIDTH, TOOLBAR_HEIGHT - 1), 2)
        
        # Titel
        title = self.title_font.render("DOOMIE Level Editor", True, ACCENT_COLOR)
        self.screen.blit(title, (20, 10))
        
        # Tile selector
        start_x = 20
        for i, tile_type in enumerate(self.tile_types):
            btn_x = start_x + i * 55
            btn_y = 50
            
            # Button achtergrond
            color = TILE_COLORS[tile_type]
            pygame.draw.rect(self.screen, color, (btn_x, btn_y, 45, 45))
            
            # Selectie indicator
            if tile_type == self.selected_tile:
                pygame.draw.rect(self.screen, SELECT_COLOR, (btn_x - 3, btn_y - 3, 51, 51), 3)
            else:
                pygame.draw.rect(self.screen, (80, 80, 100), (btn_x, btn_y, 45, 45), 1)
                
            # Nummer
            num_text = self.small_font.render(str(tile_type), True, TEXT_COLOR)
            self.screen.blit(num_text, (btn_x + 3, btn_y + 3))
            
        # Geselecteerde tile naam
        tile_name = TILE_NAMES.get(self.selected_tile, "?")
        name_text = self.font.render(f"Geselecteerd: {tile_name}", True, TEXT_COLOR)
        self.screen.blit(name_text, (start_x + len(self.tile_types) * 55 + 20, 60))
        
        # Instructies rechts
        instructions = [
            "LMB: Plaats | RMB: Wis | Scroll: Wissel",
            "S: Opslaan | L: Laden | G: Grid | C: Wissen",
            "+/-: Zoom | Pijltjes: Scroll"
        ]
        for i, text in enumerate(instructions):
            inst = self.small_font.render(text, True, (150, 150, 170))
            self.screen.blit(inst, (EDITOR_WIDTH - 350, 15 + i * 20))
            
        # Map info
        info = self.small_font.render(f"Map: {self.map_width}x{self.map_height} | Zoom: {int(self.zoom * 100)}%", 
                                      True, (150, 150, 170))
        self.screen.blit(info, (EDITOR_WIDTH - 350, 80))
        
        # Bericht
        if self.message:
            current_time = pygame.time.get_ticks()
            if current_time - self.message_time < 2000:
                msg_text = self.font.render(self.message, True, SELECT_COLOR)
                msg_rect = msg_text.get_rect(center=(EDITOR_WIDTH // 2, TOOLBAR_HEIGHT - 15))
                self.screen.blit(msg_text, msg_rect)
            else:
                self.message = ""
                
    def draw_map(self):
        """Teken de map"""
        # Map gebied
        map_surface = pygame.Surface((EDITOR_WIDTH, self.map_area_height))
        map_surface.fill(BG_COLOR)
        
        # Bereken zichtbare tiles
        start_tx = int(self.scroll_x / self.tile_display_size)
        start_ty = int(self.scroll_y / self.tile_display_size)
        end_tx = min(self.map_width, start_tx + int(EDITOR_WIDTH / self.tile_display_size) + 2)
        end_ty = min(self.map_height, start_ty + int(self.map_area_height / self.tile_display_size) + 2)
        
        # Teken tiles
        for ty in range(start_ty, end_ty):
            for tx in range(start_tx, end_tx):
                tile = self.map_data[ty][tx]
                color = TILE_COLORS.get(tile, (100, 100, 100))
                
                x = tx * self.tile_display_size - self.scroll_x
                y = ty * self.tile_display_size - self.scroll_y
                
                pygame.draw.rect(map_surface, color, 
                               (x, y, self.tile_display_size - 1, self.tile_display_size - 1))
                
                # Speciale markers
                if tile == 9:  # Deur
                    # Teken deur symbool
                    cx = x + self.tile_display_size // 2
                    cy = y + self.tile_display_size // 2
                    pygame.draw.rect(map_surface, (100, 70, 45), 
                                   (x + 4, y + 2, self.tile_display_size - 8, self.tile_display_size - 4))
                                   
                elif tile == 3:  # Fakkel
                    # Teken vlam symbool
                    cx = x + self.tile_display_size // 2
                    cy = y + self.tile_display_size // 3
                    pygame.draw.circle(map_surface, (255, 200, 50), (cx, cy), 4)
                    
        # Grid
        if self.show_grid:
            for tx in range(start_tx, end_tx + 1):
                x = tx * self.tile_display_size - self.scroll_x
                pygame.draw.line(map_surface, GRID_COLOR, (x, 0), (x, self.map_area_height))
            for ty in range(start_ty, end_ty + 1):
                y = ty * self.tile_display_size - self.scroll_y
                pygame.draw.line(map_surface, GRID_COLOR, (0, y), (EDITOR_WIDTH, y))
                
        # Speler start positie
        px = int(self.player_start[0] * self.tile_display_size - self.scroll_x)
        py = int(self.player_start[1] * self.tile_display_size - self.scroll_y)
        pygame.draw.circle(map_surface, (50, 255, 50), (px, py), 8)
        pygame.draw.circle(map_surface, (255, 255, 255), (px, py), 8, 2)
        
        # Muis hover indicator
        mx, my = pygame.mouse.get_pos()
        if my >= TOOLBAR_HEIGHT:
            tx, ty = self.get_tile_at_mouse(mx, my)
            if tx is not None:
                hx = tx * self.tile_display_size - self.scroll_x
                hy = ty * self.tile_display_size - self.scroll_y
                pygame.draw.rect(map_surface, SELECT_COLOR, 
                               (hx, hy, self.tile_display_size, self.tile_display_size), 2)
                               
        self.screen.blit(map_surface, (0, TOOLBAR_HEIGHT))
        
    def draw(self):
        """Render alles"""
        self.screen.fill(BG_COLOR)
        self.draw_map()
        self.draw_toolbar()
        pygame.display.flip()
        
    def save_map(self):
        """Sla de map op naar map.py"""
        try:
            # Genereer map code
            lines = [
                '# Level Map - Gegenereerd door DOOMIE Level Editor',
                '# 0 = lege ruimte',
                '# 1 = rode bakstenen muur',
                '# 2 = wandkleed/tapestry muur',
                '# 3 = fakkel muur',
                '# 4 = donkere stenen muur',
                '# 5 = metalen muur',
                '# 9 = deur',
                '',
                '# Mini map schaal',
                'MINIMAP_SCALE = 5',
                'MINIMAP_TILE_SIZE = 6',
                '',
                f'# Level layout ({self.map_width}x{self.map_height})',
                'MAP = ['
            ]
            
            for row in self.map_data:
                row_str = '    [' + ', '.join(str(tile) for tile in row) + '],'
                lines.append(row_str)
                
            lines.append(']')
            lines.append('')
            lines.append('MAP_WIDTH = len(MAP[0])')
            lines.append('MAP_HEIGHT = len(MAP)')
            lines.append('')
            lines.append('')
            lines.append('def get_map_value(x, y):')
            lines.append('    """Geeft de waarde van een map tile terug"""')
            lines.append('    if 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT:')
            lines.append('        return MAP[int(y)][int(x)]')
            lines.append('    return 1  # Buiten de map = muur')
            lines.append('')
            lines.append('')
            lines.append('def is_wall(x, y):')
            lines.append('    """Checkt of een positie een muur is (1-5, niet 0 en niet deur 9)"""')
            lines.append('    val = get_map_value(x, y)')
            lines.append('    return val >= 1 and val <= 5  # 1-5 = muur types, 9 = deur')
            lines.append('')
            lines.append('')
            lines.append('def is_door(x, y):')
            lines.append('    """Checkt of een positie een deur is"""')
            lines.append('    return get_map_value(x, y) == 9')
            lines.append('')
            
            # Schrijf naar bestand
            with open('map.py', 'w') as f:
                f.write('\n'.join(lines))
                
            self.show_message("Map opgeslagen naar map.py!")
            print("Map opgeslagen!")
            
        except Exception as e:
            self.show_message(f"Fout bij opslaan: {e}")
            print(f"Fout: {e}")
            
    def load_map(self):
        """Laad de map vanuit map.py"""
        try:
            if os.path.exists('map.py'):
                # Importeer de map
                import importlib
                import map as map_module
                importlib.reload(map_module)
                
                self.map_data = [row[:] for row in map_module.MAP]
                self.map_height = len(self.map_data)
                self.map_width = len(self.map_data[0]) if self.map_data else 24
                
                self.show_message(f"Map geladen: {self.map_width}x{self.map_height}")
                print(f"Map geladen: {self.map_width}x{self.map_height}")
            else:
                self.show_message("Geen map.py gevonden, nieuwe map gemaakt")
                
        except Exception as e:
            self.show_message(f"Fout bij laden: {e}")
            print(f"Fout: {e}")
            
    def clear_map(self):
        """Wis de hele map"""
        # Maak randen muren, binnenste leeg
        self.map_data = [[0 for _ in range(self.map_width)] for _ in range(self.map_height)]
        
        # Maak buitenste rand muren
        for x in range(self.map_width):
            self.map_data[0][x] = 1
            self.map_data[self.map_height - 1][x] = 1
        for y in range(self.map_height):
            self.map_data[y][0] = 1
            self.map_data[y][self.map_width - 1] = 1
            
        self.show_message("Map gewist (met muur rand)")
        
    def new_map_dialog(self):
        """Maak een nieuwe map met andere afmetingen"""
        # Simpele size cycling
        sizes = [(16, 16), (24, 24), (32, 32), (48, 48)]
        current_size = (self.map_width, self.map_height)
        
        try:
            idx = sizes.index(current_size)
            idx = (idx + 1) % len(sizes)
        except ValueError:
            idx = 0
            
        self.map_width, self.map_height = sizes[idx]
        self.clear_map()
        self.scroll_x = 0
        self.scroll_y = 0
        self.show_message(f"Nieuwe map: {self.map_width}x{self.map_height}")
        
    def run(self):
        """Main loop"""
        print("\n" + "=" * 50)
        print("  DOOMIE Level Editor")
        print("=" * 50)
        print("\nBesturing:")
        print("  LMB        - Plaats tile")
        print("  RMB        - Wis tile")
        print("  Scroll     - Wissel tile type")
        print("  0-5, 9     - Selecteer tile type")
        print("  S          - Opslaan")
        print("  L          - Laden")
        print("  G          - Toggle grid")
        print("  C          - Wis map")
        print("  N          - Nieuwe map grootte")
        print("  +/-        - Zoom")
        print("  Pijltjes   - Scroll")
        print("  ESC        - Afsluiten")
        print("=" * 50 + "\n")
        
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
            
        pygame.quit()


if __name__ == "__main__":
    editor = LevelEditor()
    editor.run()

