"""
Raycasting Engine met Texture Mapping, Deur Support en Pitch
"""
import pygame
import math
from settings import *
from map import MAP, MAP_WIDTH, MAP_HEIGHT, get_map_value


class RayCaster:
    def __init__(self, game):
        self.game = game
        self.ray_results = []
        self.textures = None
        self.door_manager = None
        self.pitch = 0  # Verticale kijkhoek offset
        
    def set_textures(self, texture_manager):
        """Stel texture manager in"""
        self.textures = texture_manager
        
    def set_door_manager(self, door_manager):
        """Stel door manager in"""
        self.door_manager = door_manager
        
    def raycast(self, player):
        """Voer raycasting uit vanuit speler positie"""
        self.ray_results = []
        self.pitch = player.pitch  # Krijg pitch van speler
        
        ox, oy = player.x, player.y
        ray_angle = player.angle - HALF_FOV
        
        for ray in range(NUM_RAYS):
            sin_a = math.sin(ray_angle)
            cos_a = math.cos(ray_angle)
            
            # Cast ray en krijg resultaat
            depth, wall_type, tex_offset, is_vertical, is_door = self.cast_ray(ox, oy, sin_a, cos_a)
            
            # Fix fisheye effect
            depth *= math.cos(player.angle - ray_angle)
            
            self.ray_results.append({
                'depth': depth,
                'wall_type': wall_type,
                'tex_offset': tex_offset,
                'is_vertical': is_vertical,
                'is_door': is_door,
                'ray_angle': ray_angle
            })
            
            ray_angle += DELTA_ANGLE
            
    def cast_ray(self, ox, oy, sin_a, cos_a):
        """Cast een enkele ray en return resultaat"""
        # Horizontale intersecties
        h_result = self.cast_horizontal(ox, oy, sin_a, cos_a)
        
        # Verticale intersecties  
        v_result = self.cast_vertical(ox, oy, sin_a, cos_a)
        
        # Kies kortste afstand
        if h_result[0] < v_result[0]:
            return (*h_result, False)  # is_vertical = False
        else:
            return (*v_result, True)   # is_vertical = True
            
    def cast_horizontal(self, ox, oy, sin_a, cos_a):
        """Cast ray voor horizontale muur intersecties"""
        if sin_a == 0:
            return (MAX_DEPTH, 0, 0, False)
            
        # Bepaal richting
        if sin_a > 0:
            y_step = 1
            y_intercept = int(oy) + 1
        else:
            y_step = -1
            y_intercept = int(oy)
            
        # Bereken eerste intersectie
        depth_y = (y_intercept - oy) / sin_a
        x_intercept = ox + depth_y * cos_a
        
        # Bereken delta
        delta_depth = y_step / sin_a
        dx = delta_depth * cos_a
        
        # March de ray
        for _ in range(MAX_DEPTH):
            tile_x = int(x_intercept)
            tile_y = int(y_intercept) if sin_a > 0 else int(y_intercept) - 1
            
            if 0 <= tile_x < MAP_WIDTH and 0 <= tile_y < MAP_HEIGHT:
                wall_type = get_map_value(tile_x, tile_y)
                
                # Check voor deur
                if wall_type == 9 and self.door_manager:
                    door_offset = self.door_manager.get_door_offset(tile_x, tile_y)
                    # Bereken textuur offset
                    tex_offset = x_intercept % 1
                    
                    # Als deur open genoeg is, ga door
                    if tex_offset < door_offset:
                        x_intercept += dx
                        y_intercept += y_step
                        depth_y += abs(delta_depth)
                        continue
                    
                    # Pas offset aan voor deur positie
                    tex_offset = (tex_offset - door_offset) / (1 - door_offset) if door_offset < 1 else 0
                    return (depth_y, wall_type, tex_offset, True)
                    
                elif wall_type and wall_type != 9:
                    # Normale muur
                    tex_offset = x_intercept % 1
                    return (depth_y, wall_type, tex_offset, False)
                    
            x_intercept += dx
            y_intercept += y_step
            depth_y += abs(delta_depth)
            
        return (MAX_DEPTH, 0, 0, False)
        
    def cast_vertical(self, ox, oy, sin_a, cos_a):
        """Cast ray voor verticale muur intersecties"""
        if cos_a == 0:
            return (MAX_DEPTH, 0, 0, False)
            
        # Bepaal richting
        if cos_a > 0:
            x_step = 1
            x_intercept = int(ox) + 1
        else:
            x_step = -1
            x_intercept = int(ox)
            
        # Bereken eerste intersectie
        depth_x = (x_intercept - ox) / cos_a
        y_intercept = oy + depth_x * sin_a
        
        # Bereken delta
        delta_depth = x_step / cos_a
        dy = delta_depth * sin_a
        
        # March de ray
        for _ in range(MAX_DEPTH):
            tile_x = int(x_intercept) if cos_a > 0 else int(x_intercept) - 1
            tile_y = int(y_intercept)
            
            if 0 <= tile_x < MAP_WIDTH and 0 <= tile_y < MAP_HEIGHT:
                wall_type = get_map_value(tile_x, tile_y)
                
                # Check voor deur
                if wall_type == 9 and self.door_manager:
                    door_offset = self.door_manager.get_door_offset(tile_x, tile_y)
                    tex_offset = y_intercept % 1
                    
                    # Als deur open genoeg is, ga door
                    if tex_offset < door_offset:
                        x_intercept += x_step
                        y_intercept += dy
                        depth_x += abs(delta_depth)
                        continue
                    
                    tex_offset = (tex_offset - door_offset) / (1 - door_offset) if door_offset < 1 else 0
                    return (depth_x, wall_type, tex_offset, True)
                    
                elif wall_type and wall_type != 9:
                    tex_offset = y_intercept % 1
                    return (depth_x, wall_type, tex_offset, False)
                    
            x_intercept += x_step
            y_intercept += dy
            depth_x += abs(delta_depth)
            
        return (MAX_DEPTH, 0, 0, False)
        
    def render(self, screen):
        """Render de 3D view met texturen en pitch"""
        # Bereken horizon positie gebaseerd op pitch
        horizon = HALF_HEIGHT + self.pitch
        
        # Teken plafond (boven horizon)
        if horizon > 0:
            pygame.draw.rect(screen, CEILING_COLOR, (0, 0, WIDTH, horizon))
        
        # Teken vloer (onder horizon)
        if horizon < HEIGHT:
            pygame.draw.rect(screen, FLOOR_COLOR, (0, horizon, WIDTH, HEIGHT - horizon))
        
        # Teken muren met texturen
        for ray_idx, ray_data in enumerate(self.ray_results):
            depth = ray_data['depth']
            wall_type = ray_data['wall_type']
            tex_offset = ray_data['tex_offset']
            is_vertical = ray_data['is_vertical']
            is_door = ray_data['is_door']
            
            if depth <= 0:
                depth = 0.0001
                
            # Bereken muur hoogte
            wall_height = SCREEN_DIST / depth
            
            x = ray_idx * SCALE
            # Y positie aangepast voor pitch
            y = horizon - wall_height // 2
            
            # Render met texturen als beschikbaar
            if self.textures and wall_type:
                # Bepaal textuur ID
                if is_door:
                    tex_id = 'door'
                else:
                    tex_id = wall_type
                    
                # Haal textuur kolom
                darken = not is_vertical  # Horizontale muren donkerder
                column = self.textures.get_texture_column(tex_id, tex_offset, wall_height, darken)
                
                if column:
                    # Distance fog
                    fog_factor = min(1, depth / MAX_DEPTH)
                    if fog_factor > 0.1:
                        fog_surface = pygame.Surface(column.get_size())
                        fog_surface.fill((0, 0, 0))
                        fog_surface.set_alpha(int(fog_factor * 180))
                        column.blit(fog_surface, (0, 0))
                    
                    screen.blit(column, (x, y))
            else:
                # Fallback naar kleuren
                base_color = WALL_COLORS.get(wall_type, (150, 150, 150))
                
                if not is_vertical:
                    color = tuple(max(0, int(c * 0.7)) for c in base_color)
                else:
                    color = base_color
                    
                fog_factor = min(1, depth / MAX_DEPTH)
                color = tuple(int(c * (1 - fog_factor * 0.7)) for c in color)
                
                pygame.draw.rect(screen, color, (x, y, SCALE, wall_height))
