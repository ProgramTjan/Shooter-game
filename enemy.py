"""
Vijand Systeem - Vijanden met AI, health en aanvallen
"""
import pygame
import math
import random
from settings import *
from map import is_wall, is_door
from sprites import create_enemy_sprite, create_dead_enemy_sprite, create_hurt_enemy_sprite


class Enemy:
    """Een vijand/demon"""
    
    # Verschillende vijand types
    ENEMY_TYPES = [
        {'color': 'red', 'health': 80, 'speed': 0.002, 'damage': 8},
        {'color': 'green', 'health': 100, 'speed': 0.0015, 'damage': 12},
        {'color': 'blue', 'health': 60, 'speed': 0.003, 'damage': 6},
        {'color': 'purple', 'health': 120, 'speed': 0.001, 'damage': 15},
        {'color': 'orange', 'health': 70, 'speed': 0.0025, 'damage': 10},
    ]
    
    def __init__(self, x, y, enemy_type=None):
        self.x = x
        self.y = y
        
        # Kies random type of gebruik gegeven type
        if enemy_type is None:
            enemy_type = random.choice(self.ENEMY_TYPES)
        
        self.color = enemy_type['color']
        self.health = enemy_type['health']
        self.max_health = enemy_type['health']
        self.speed = enemy_type['speed']
        self.damage = enemy_type['damage']
        
        self.attack_range = 1.5
        self.attack_cooldown = 1000
        self.last_attack = 0
        
        self.alive = True
        self.hurt_time = 0
        self.hurt_duration = 100
        
        # Sprites
        self.sprite_normal = create_enemy_sprite(self.color)
        self.sprite_hurt = create_hurt_enemy_sprite()
        self.sprite_dead = create_dead_enemy_sprite(self.color)
        
        # Pathfinding
        self.target_x = x
        self.target_y = y
        self.path_update_time = 0
        self.path_update_interval = 500
        
    def update(self, dt, player, door_manager=None):
        """Update vijand"""
        if not self.alive:
            return
            
        current_time = pygame.time.get_ticks()
        
        if current_time - self.path_update_time > self.path_update_interval:
            self.target_x = player.x
            self.target_y = player.y
            self.path_update_time = current_time
            
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > self.attack_range:
            if distance > 0:
                move_x = (dx / distance) * self.speed * dt
                move_y = (dy / distance) * self.speed * dt
                
                new_x = self.x + move_x
                new_y = self.y + move_y
                
                if self.can_move_to(new_x, self.y, door_manager):
                    self.x = new_x
                if self.can_move_to(self.x, new_y, door_manager):
                    self.y = new_y
        else:
            if current_time - self.last_attack > self.attack_cooldown:
                self.attack(player)
                self.last_attack = current_time
                
    def can_move_to(self, x, y, door_manager=None):
        """Check of vijand naar positie kan bewegen"""
        if is_wall(x, y):
            return False
        if is_door(x, y):
            if door_manager:
                return door_manager.can_pass(x, y)
            return False
        return True
        
    def attack(self, player):
        """Aanval de speler"""
        pass
        
    def take_damage(self, damage):
        """Neem schade"""
        if not self.alive:
            return False
            
        self.health -= damage
        self.hurt_time = pygame.time.get_ticks()
        
        if self.health <= 0:
            self.health = 0
            self.alive = False
            return True
        return False
        
    def get_sprite(self):
        """Haal huidige sprite op"""
        if not self.alive:
            return self.sprite_dead
            
        current_time = pygame.time.get_ticks()
        if current_time - self.hurt_time < self.hurt_duration:
            return self.sprite_hurt
            
        return self.sprite_normal
        
    @property
    def pos(self):
        return (self.x, self.y)


class EnemyManager:
    """Beheert alle vijanden"""
    
    def __init__(self):
        self.enemies = []
        self.spawn_enemies()
        
    def spawn_enemies(self):
        """Spawn vijanden op de map"""
        spawn_positions = [
            (4.5, 5.5),
            (10.5, 5.5),
            (7.5, 8.5),
            (4.5, 11.5),
            (10.5, 11.5),
            (13.5, 7.5),
            (7.5, 13.5),
        ]
        
        for i, (x, y) in enumerate(spawn_positions):
            # Elke vijand krijgt een ander type
            enemy_type = Enemy.ENEMY_TYPES[i % len(Enemy.ENEMY_TYPES)]
            self.enemies.append(Enemy(x, y, enemy_type))
            
    def update(self, dt, player, door_manager=None):
        """Update alle vijanden"""
        for enemy in self.enemies:
            enemy.update(dt, player, door_manager)
            
    def get_enemy_at_ray(self, player_x, player_y, angle, max_distance=MAX_DEPTH):
        """Check of er een vijand geraakt wordt door ray"""
        sin_a = math.sin(angle)
        cos_a = math.cos(angle)
        
        for enemy in self.enemies:
            if not enemy.alive:
                continue
                
            dx = enemy.x - player_x
            dy = enemy.y - player_y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > max_distance or distance < 0.5:
                continue
                
            enemy_angle = math.atan2(dy, dx)
            
            delta = enemy_angle - angle
            while delta > math.pi:
                delta -= 2 * math.pi
            while delta < -math.pi:
                delta += 2 * math.pi
                
            hit_radius = 0.4 / distance
            
            if abs(delta) < hit_radius:
                return enemy, distance
                
        return None, 0
        
    def check_player_damage(self, player):
        """Check of vijanden de speler kunnen aanvallen"""
        damage = 0
        current_time = pygame.time.get_ticks()
        
        for enemy in self.enemies:
            if not enemy.alive:
                continue
                
            dx = player.x - enemy.x
            dy = player.y - enemy.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < enemy.attack_range:
                if current_time - enemy.last_attack > enemy.attack_cooldown:
                    damage += enemy.damage
                    enemy.last_attack = current_time
                    
        return damage
        
    def render(self, sprite_renderer):
        """Voeg alle vijanden toe aan sprite renderer"""
        for enemy in self.enemies:
            sprite = enemy.get_sprite()
            scale = 0.6 if enemy.alive else 0.4  # Kleiner
            sprite_renderer.add_sprite(sprite, enemy.x, enemy.y, scale)
            
    @property
    def alive_count(self):
        """Aantal levende vijanden"""
        return sum(1 for e in self.enemies if e.alive)
