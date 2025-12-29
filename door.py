"""
Deur systeem - Interactieve deuren met open/sluit animatie
"""
import pygame
from settings import *


class Door:
    """Een interactieve deur"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_open = False
        self.is_moving = False
        self.open_amount = 0.0  # 0.0 = dicht, 1.0 = open
        self.open_speed = 0.003
        self.close_delay = 3000  # ms voordat deur automatisch sluit
        self.open_time = 0
        
    def update(self, dt):
        """Update deur animatie"""
        if self.is_moving:
            if self.is_open:
                # Deur openen
                self.open_amount += self.open_speed * dt
                if self.open_amount >= 0.9:
                    self.open_amount = 0.9
                    self.is_moving = False
                    self.open_time = pygame.time.get_ticks()
            else:
                # Deur sluiten
                self.open_amount -= self.open_speed * dt
                if self.open_amount <= 0:
                    self.open_amount = 0
                    self.is_moving = False
                    
        # Auto-close na delay
        elif self.is_open and not self.is_moving:
            if pygame.time.get_ticks() - self.open_time > self.close_delay:
                self.close()
                
    def open(self):
        """Open de deur"""
        if not self.is_open and self.open_amount < 0.9:
            self.is_open = True
            self.is_moving = True
            
    def close(self):
        """Sluit de deur"""
        if self.is_open:
            self.is_open = False
            self.is_moving = True
            
    def toggle(self):
        """Toggle deur open/dicht"""
        if self.is_open:
            self.close()
        else:
            self.open()
            
    def can_pass(self):
        """Check of speler door de deur kan"""
        return self.open_amount > 0.5
    
    @property
    def pos(self):
        return (self.x, self.y)


class DoorManager:
    """Beheert alle deuren in het level"""
    
    def __init__(self, game_map):
        self.doors = {}
        self.find_doors(game_map)
        
    def find_doors(self, game_map):
        """Vind alle deuren in de map (waarde 9 = deur)"""
        for y, row in enumerate(game_map):
            for x, tile in enumerate(row):
                if tile == 9:  # Deur tile
                    self.doors[(x, y)] = Door(x, y)
                    
    def update(self, dt):
        """Update alle deuren"""
        for door in self.doors.values():
            door.update(dt)
            
    def get_door(self, x, y):
        """Haal deur op positie"""
        return self.doors.get((int(x), int(y)))
    
    def interact(self, player_x, player_y, player_angle):
        """Interacteer met dichtsbijzijnde deur"""
        import math
        
        # Kijk waar speler naar kijkt
        check_x = player_x + math.cos(player_angle) * 1.5
        check_y = player_y + math.sin(player_angle) * 1.5
        
        door = self.get_door(check_x, check_y)
        if door:
            door.toggle()
            return True
            
        # Check ook directe omgeving
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                door = self.get_door(int(player_x) + dx, int(player_y) + dy)
                if door:
                    # Check afstand
                    dist = math.sqrt((door.x + 0.5 - player_x)**2 + (door.y + 0.5 - player_y)**2)
                    if dist < 2.0:
                        door.toggle()
                        return True
        return False
    
    def is_door(self, x, y):
        """Check of positie een deur is"""
        return (int(x), int(y)) in self.doors
    
    def can_pass(self, x, y):
        """Check of speler door kan op deze positie"""
        door = self.get_door(x, y)
        if door:
            return door.can_pass()
        return True
    
    def get_door_offset(self, x, y):
        """Haal deur open-offset voor rendering"""
        door = self.get_door(x, y)
        if door:
            return door.open_amount
        return 0

