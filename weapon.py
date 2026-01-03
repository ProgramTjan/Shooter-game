"""
Wapen Systeem - Meerdere wapens met schieten en animatie
"""
import pygame
import math
from settings import *


def create_pistol_sprite():
    """Maak een pistool sprite"""
    width = 120
    height = 150
    sprite = pygame.Surface((width, height), pygame.SRCALPHA)
    
    hand_color = (210, 170, 130)
    pygame.draw.ellipse(sprite, hand_color, (35, 90, 50, 40))
    
    grip_color = (40, 35, 30)
    pygame.draw.rect(sprite, grip_color, (45, 85, 30, 55))
    pygame.draw.rect(sprite, (30, 25, 20), (45, 85, 30, 55), 2)
    
    slide_color = (50, 50, 55)
    pygame.draw.rect(sprite, slide_color, (40, 40, 40, 50))
    pygame.draw.rect(sprite, (70, 70, 75), (42, 42, 5, 46))
    
    pygame.draw.rect(sprite, (40, 40, 45), (50, 20, 20, 25))
    pygame.draw.ellipse(sprite, (20, 20, 25), (52, 15, 16, 12))
    
    pygame.draw.arc(sprite, (35, 30, 25), (35, 85, 25, 25), 3.14, 6.28, 3)
    
    return sprite


def create_pistol_fire_sprite():
    width = 120
    height = 150
    sprite = pygame.Surface((width, height), pygame.SRCALPHA)
    
    base = create_pistol_sprite()
    sprite.blit(base, (0, 0))
    
    flash_center = (60, 18)
    pygame.draw.circle(sprite, (255, 200, 50, 200), flash_center, 20)
    pygame.draw.circle(sprite, (255, 255, 200), flash_center, 12)
    pygame.draw.circle(sprite, (255, 255, 255), flash_center, 6)
    
    return sprite


def create_machinegun_sprite():
    """Maak een machinegun sprite"""
    width = 160
    height = 180
    sprite = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Hand
    hand_color = (210, 170, 130)
    pygame.draw.ellipse(sprite, hand_color, (50, 120, 60, 45))
    
    # Voorste hand
    pygame.draw.ellipse(sprite, hand_color, (90, 60, 40, 30))
    
    # Handgreep
    grip_color = (35, 35, 40)
    pygame.draw.rect(sprite, grip_color, (55, 110, 35, 60))
    pygame.draw.rect(sprite, (25, 25, 30), (55, 110, 35, 60), 2)
    
    # Body van de gun
    body_color = (45, 45, 50)
    pygame.draw.rect(sprite, body_color, (40, 50, 80, 65))
    pygame.draw.rect(sprite, (60, 60, 65), (42, 52, 8, 61))  # Highlight
    
    # Barrel (lang)
    barrel_color = (35, 35, 40)
    pygame.draw.rect(sprite, barrel_color, (55, 10, 30, 45))
    pygame.draw.ellipse(sprite, (20, 20, 25), (58, 5, 24, 15))
    
    # Barrel holes (machinegun look)
    for i in range(3):
        pygame.draw.circle(sprite, (15, 15, 18), (70, 15 + i * 12), 4)
    
    # Magazine
    mag_color = (40, 40, 45)
    pygame.draw.rect(sprite, mag_color, (60, 95, 20, 35))
    pygame.draw.rect(sprite, (30, 30, 35), (60, 95, 20, 35), 2)
    
    # Stock
    pygame.draw.rect(sprite, (50, 40, 35), (40, 85, 20, 50))
    
    # Details
    pygame.draw.line(sprite, (55, 55, 60), (45, 70), (115, 70), 2)
    pygame.draw.rect(sprite, (55, 55, 60), (100, 55, 15, 25), 2)  # Sight
    
    return sprite


def create_machinegun_fire_sprite():
    width = 160
    height = 180
    sprite = pygame.Surface((width, height), pygame.SRCALPHA)
    
    base = create_machinegun_sprite()
    sprite.blit(base, (0, 0))
    
    # Grote muzzle flash
    flash_center = (70, 8)
    pygame.draw.circle(sprite, (255, 180, 50, 180), flash_center, 25)
    pygame.draw.circle(sprite, (255, 220, 100), flash_center, 15)
    pygame.draw.circle(sprite, (255, 255, 200), flash_center, 8)
    
    # Sparks
    import random
    random.seed(pygame.time.get_ticks() // 50)
    for _ in range(6):
        angle = random.uniform(0, 2 * math.pi)
        dist = random.randint(20, 40)
        sx = flash_center[0] + int(math.cos(angle) * dist)
        sy = flash_center[1] + int(math.sin(angle) * dist * 0.5)
        pygame.draw.circle(sprite, (255, 200, 50), (sx, sy), random.randint(2, 4))
    
    return sprite


def create_shotgun_sprite():
    width = 180
    height = 220
    sprite = pygame.Surface((width, height), pygame.SRCALPHA)
    
    grip_color = (80, 50, 30)
    grip_dark = (50, 30, 20)
    pygame.draw.rect(sprite, grip_color, (70, 160, 40, 60))
    pygame.draw.rect(sprite, grip_dark, (70, 160, 40, 60), 3)
    
    hand_color = (210, 170, 130)
    pygame.draw.ellipse(sprite, hand_color, (55, 150, 70, 45))
    pygame.draw.ellipse(sprite, hand_color, (115, 70, 35, 30))
    
    barrel_color = (60, 60, 70)
    barrel_light = (90, 90, 100)
    pygame.draw.rect(sprite, barrel_color, (60, 20, 55, 160))
    pygame.draw.rect(sprite, barrel_light, (65, 20, 8, 160))
    
    pygame.draw.ellipse(sprite, (20, 20, 25), (65, 10, 45, 22))
    pygame.draw.ellipse(sprite, (10, 10, 15), (70, 13, 35, 16))
    
    pump_color = (100, 60, 40)
    pygame.draw.rect(sprite, pump_color, (55, 75, 65, 30))
    pygame.draw.rect(sprite, grip_dark, (55, 75, 65, 30), 2)
    
    return sprite


def create_shotgun_fire_sprite():
    width = 180
    height = 220
    sprite = pygame.Surface((width, height), pygame.SRCALPHA)
    
    base = create_shotgun_sprite()
    sprite.blit(base, (0, 0))
    
    flash_center = (88, 18)
    for radius in range(45, 15, -5):
        alpha = 150 - radius * 2
        pygame.draw.circle(sprite, (255, 150 + radius, 0, max(0, alpha)), flash_center, radius)
    pygame.draw.circle(sprite, (255, 255, 200), flash_center, 20)
    pygame.draw.circle(sprite, (255, 255, 255), flash_center, 10)
    
    return sprite


def create_shotgun_pump_sprite():
    width = 180
    height = 220
    sprite = pygame.Surface((width, height), pygame.SRCALPHA)
    
    grip_color = (80, 50, 30)
    grip_dark = (50, 30, 20)
    pygame.draw.rect(sprite, grip_color, (70, 170, 40, 60))
    pygame.draw.rect(sprite, grip_dark, (70, 170, 40, 60), 3)
    
    hand_color = (210, 170, 130)
    pygame.draw.ellipse(sprite, hand_color, (55, 160, 70, 45))
    pygame.draw.ellipse(sprite, hand_color, (115, 100, 35, 30))
    
    barrel_color = (60, 60, 70)
    barrel_light = (90, 90, 100)
    pygame.draw.rect(sprite, barrel_color, (60, 30, 55, 160))
    pygame.draw.rect(sprite, barrel_light, (65, 30, 8, 160))
    
    pygame.draw.ellipse(sprite, (20, 20, 25), (65, 20, 45, 22))
    pygame.draw.ellipse(sprite, (10, 10, 15), (70, 23, 35, 16))
    
    pump_color = (100, 60, 40)
    pygame.draw.rect(sprite, pump_color, (55, 105, 65, 30))
    pygame.draw.rect(sprite, grip_dark, (55, 105, 65, 30), 2)
    
    pygame.draw.ellipse(sprite, (200, 50, 50), (125, 90, 12, 22))
    
    return sprite


class Pistol:
    """Snel schietend pistool"""
    
    def __init__(self):
        self.name = "PISTOL"
        self.damage = 18
        self.fire_rate = 200
        self.last_fire = 0
        self.ammo = 150
        self.max_ammo = 150
        
        self.state = 'idle'
        self.animation_start = 0
        self.fire_duration = 50
        
        self.sprite_idle = create_pistol_sprite()
        self.sprite_fire = create_pistol_fire_sprite()
        
        self.bob_offset = 0
        self.bob_speed = 0.012
        
    def update(self, dt, is_moving=False):
        current_time = pygame.time.get_ticks()
        
        if self.state == 'firing':
            if current_time - self.animation_start > self.fire_duration:
                self.state = 'idle'
                
        if is_moving and self.state == 'idle':
            self.bob_offset = math.sin(current_time * self.bob_speed) * 4
        else:
            self.bob_offset *= 0.9
            
    def can_fire(self):
        if self.ammo <= 0:
            return False
        if self.state != 'idle':
            return False
        current_time = pygame.time.get_ticks()
        if current_time - self.last_fire < self.fire_rate:
            return False
        return True
        
    def fire(self):
        if not self.can_fire():
            return False
        self.ammo -= 1
        self.last_fire = pygame.time.get_ticks()
        self.animation_start = self.last_fire
        self.state = 'firing'
        return True
        
    def get_sprite(self):
        if self.state == 'firing':
            return self.sprite_fire
        return self.sprite_idle
        
    def render(self, screen):
        sprite = self.get_sprite()
        x = HALF_WIDTH - sprite.get_width() // 2 + 30
        y = HEIGHT - sprite.get_height() + 20
        y += int(self.bob_offset)
        if self.state == 'firing':
            y += 8
        screen.blit(sprite, (x, y))
        
    def add_ammo(self, amount):
        self.ammo = min(self.max_ammo, self.ammo + amount)


class MachineGun:
    """Snelle machinegun met automatisch vuur"""
    
    def __init__(self):
        self.name = "MACHINEGUN"
        self.damage = 12
        self.fire_rate = 80  # Zeer snel!
        self.last_fire = 0
        self.ammo = 200
        self.max_ammo = 200
        
        self.state = 'idle'
        self.animation_start = 0
        self.fire_duration = 40
        
        self.sprite_idle = create_machinegun_sprite()
        self.sprite_fire = create_machinegun_fire_sprite()
        
        self.bob_offset = 0
        self.bob_speed = 0.015
        
        # Recoil shake
        self.shake_offset = 0
        
    def update(self, dt, is_moving=False):
        current_time = pygame.time.get_ticks()
        
        if self.state == 'firing':
            if current_time - self.animation_start > self.fire_duration:
                self.state = 'idle'
                
        if is_moving and self.state == 'idle':
            self.bob_offset = math.sin(current_time * self.bob_speed) * 3
        else:
            self.bob_offset *= 0.9
            
        # Shake afnemen
        self.shake_offset *= 0.8
            
    def can_fire(self):
        if self.ammo <= 0:
            return False
        current_time = pygame.time.get_ticks()
        if current_time - self.last_fire < self.fire_rate:
            return False
        return True
        
    def fire(self):
        if not self.can_fire():
            return False
        self.ammo -= 1
        self.last_fire = pygame.time.get_ticks()
        self.animation_start = self.last_fire
        self.state = 'firing'
        # Random shake
        import random
        self.shake_offset = random.uniform(-3, 3)
        return True
        
    def get_sprite(self):
        if self.state == 'firing':
            return self.sprite_fire
        return self.sprite_idle
        
    def render(self, screen):
        sprite = self.get_sprite()
        x = HALF_WIDTH - sprite.get_width() // 2 + self.shake_offset
        y = HEIGHT - sprite.get_height() + 15
        y += int(self.bob_offset)
        if self.state == 'firing':
            y += 5
        screen.blit(sprite, (x, y))
        
    def add_ammo(self, amount):
        self.ammo = min(self.max_ammo, self.ammo + amount)


class Shotgun:
    """Krachtige shotgun"""
    
    def __init__(self):
        self.name = "SHOTGUN"
        self.damage = 50
        self.fire_rate = 700
        self.last_fire = 0
        self.ammo = 40
        self.max_ammo = 40
        
        self.state = 'idle'
        self.animation_start = 0
        self.fire_duration = 100
        self.pump_duration = 300
        
        self.sprite_idle = create_shotgun_sprite()
        self.sprite_fire = create_shotgun_fire_sprite()
        self.sprite_pump = create_shotgun_pump_sprite()
        
        self.bob_offset = 0
        self.bob_speed = 0.01
        
    def update(self, dt, is_moving=False):
        current_time = pygame.time.get_ticks()
        
        if self.state == 'firing':
            if current_time - self.animation_start > self.fire_duration:
                self.state = 'pumping'
                self.animation_start = current_time
        elif self.state == 'pumping':
            if current_time - self.animation_start > self.pump_duration:
                self.state = 'idle'
                
        if is_moving and self.state == 'idle':
            self.bob_offset = math.sin(current_time * self.bob_speed) * 5
        else:
            self.bob_offset *= 0.9
            
    def can_fire(self):
        if self.ammo <= 0:
            return False
        if self.state != 'idle':
            return False
        current_time = pygame.time.get_ticks()
        if current_time - self.last_fire < self.fire_rate:
            return False
        return True
        
    def fire(self):
        if not self.can_fire():
            return False
        self.ammo -= 1
        self.last_fire = pygame.time.get_ticks()
        self.animation_start = self.last_fire
        self.state = 'firing'
        return True
        
    def get_sprite(self):
        if self.state == 'firing':
            return self.sprite_fire
        elif self.state == 'pumping':
            return self.sprite_pump
        return self.sprite_idle
        
    def render(self, screen):
        sprite = self.get_sprite()
        x = HALF_WIDTH - sprite.get_width() // 2
        y = HEIGHT - sprite.get_height() + 25
        y += int(self.bob_offset)
        if self.state == 'firing':
            y += 20
        screen.blit(sprite, (x, y))
        
    def add_ammo(self, amount):
        self.ammo = min(self.max_ammo, self.ammo + amount)


class WeaponManager:
    """Beheert alle wapens"""
    
    def __init__(self):
        self.weapons = [Pistol(), MachineGun(), Shotgun()]
        self.current_index = 0
        self.switching = False
        self.switch_time = 0
        self.switch_duration = 200
        
    @property
    def current(self):
        return self.weapons[self.current_index]
        
    def switch_to(self, index):
        if 0 <= index < len(self.weapons) and index != self.current_index:
            self.current_index = index
            self.switching = True
            self.switch_time = pygame.time.get_ticks()
            
    def next_weapon(self):
        next_idx = (self.current_index + 1) % len(self.weapons)
        self.switch_to(next_idx)
        
    def update(self, dt, is_moving=False):
        current_time = pygame.time.get_ticks()
        
        if self.switching:
            if current_time - self.switch_time > self.switch_duration:
                self.switching = False
                
        self.current.update(dt, is_moving)
        
    def can_fire(self):
        return not self.switching and self.current.can_fire()
        
    def fire(self):
        if self.can_fire():
            return self.current.fire()
        return False
        
    def render(self, screen):
        if not self.switching:
            self.current.render(screen)
            
    def add_ammo_all(self, amount):
        """Voeg ammo toe aan alle wapens"""
        for weapon in self.weapons:
            weapon.ammo += amount