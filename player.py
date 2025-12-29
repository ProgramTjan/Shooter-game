import pygame
import math
from settings import *
from map import is_wall, is_door


class Player:
    def __init__(self):
        self.x, self.y = PLAYER_POS
        self.angle = PLAYER_ANGLE
        self.pitch = 0  # Verticale kijkhoek (-200 tot 200 pixels offset)
        self.door_manager = None
        
        # Muis instellingen
        self.mouse_sensitivity = 0.003
        self.pitch_sensitivity = 0.5
        self.max_pitch = 200  # Max pixels omhoog/omlaag kijken
        
    def set_door_manager(self, door_manager):
        """Stel door manager in voor collision checking"""
        self.door_manager = door_manager
        
    def movement(self, dt):
        """Verwerk speler beweging"""
        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)
        
        # Bewegingssnelheid met delta time
        speed = PLAYER_SPEED * dt
        speed_sin = speed * sin_a
        speed_cos = speed * cos_a
        
        dx, dy = 0, 0
        
        keys = pygame.key.get_pressed()
        
        # Vooruit/achteruit
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dx += speed_cos
            dy += speed_sin
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dx -= speed_cos
            dy -= speed_sin
            
        # Zijwaarts (strafing)
        if keys[pygame.K_a]:
            dx += speed_sin
            dy -= speed_cos
        if keys[pygame.K_d]:
            dx -= speed_sin
            dy += speed_cos
            
        # Collision detection
        self.check_wall_collision(dx, dy)
        
        # Hoek normaliseren
        self.angle %= 2 * math.pi
        
    def handle_mouse(self, mouse_rel):
        """Verwerk muisbeweging voor draaien en pitch"""
        dx, dy = mouse_rel
        
        # Horizontaal draaien
        self.angle += dx * self.mouse_sensitivity
        self.angle %= 2 * math.pi
        
        # Verticaal kijken (pitch)
        self.pitch -= dy * self.pitch_sensitivity
        self.pitch = max(-self.max_pitch, min(self.max_pitch, self.pitch))
        
    def check_wall_collision(self, dx, dy):
        """Check en pas beweging aan voor muur en deur collision"""
        scale = PLAYER_SIZE_SCALE / 1000  # Collision buffer
        
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Check X beweging
        check_x = new_x + (scale if dx > 0 else -scale)
        if self.can_move_to(check_x, self.y):
            self.x = new_x
            
        # Check Y beweging
        check_y = new_y + (scale if dy > 0 else -scale)
        if self.can_move_to(self.x, check_y):
            self.y = new_y
            
    def can_move_to(self, x, y):
        """Check of speler naar positie kan bewegen"""
        # Check muren
d    if is_wall(x, y):
            return False
            
        # Check deuren
        if is_door(x, y):
            if self.door_manager:
                return self.door_manager.can_pass(x, y)
            return False
            
        return True
            
    @property
    def pos(self):
        return (self.x, self.y)
    
    @property
    def map_pos(self):
        return (int(self.x), int(self.y))
