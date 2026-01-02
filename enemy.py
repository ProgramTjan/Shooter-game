"""
Vijand Systeem - Vijanden met AI, health, aanvallen en Boss
"""
import pygame
import math
import random
from settings import *
from map import is_wall, is_door
from sprites import create_enemy_sprite, create_dead_enemy_sprite, create_hurt_enemy_sprite
from sprites import create_boss_sprite, create_dead_boss_sprite


class Enemy:
    """Een vijand/demon"""
    
    ENEMY_TYPES = [
        {'color': 'red', 'health': 80, 'speed': 0.0012, 'damage': 6},
        {'color': 'green', 'health': 100, 'speed': 0.001, 'damage': 10},
        {'color': 'blue', 'health': 60, 'speed': 0.0018, 'damage': 5},
        {'color': 'purple', 'health': 120, 'speed': 0.0008, 'damage': 12},
        {'color': 'orange', 'health': 70, 'speed': 0.0015, 'damage': 8},
    ]
    
    def __init__(self, x, y, enemy_type=None):
        self.x = x
        self.y = y
        
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
        
        self.sprite_normal = create_enemy_sprite(self.color)
        self.sprite_hurt = create_hurt_enemy_sprite()
        self.sprite_dead = create_dead_enemy_sprite(self.color)
        
        self.target_x = x
        self.target_y = y
        self.path_update_time = 0
        self.path_update_interval = 500
        
        # Activatie afstand - vijand beweegt pas als speler dichtbij is
        self.activation_range = 8.0
        self.is_activated = False
        
    def update(self, dt, player, door_manager=None):
        if not self.alive:
            return
            
        # Check activatie
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < self.activation_range:
            self.is_activated = True
            
        if not self.is_activated:
            return
            
        current_time = pygame.time.get_ticks()
        
        if current_time - self.path_update_time > self.path_update_interval:
            self.target_x = player.x
            self.target_y = player.y
            self.path_update_time = current_time
        
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
        if is_wall(x, y):
            return False
        if is_door(x, y):
            if door_manager:
                return door_manager.can_pass(x, y)
            return False
        return True
        
    def attack(self, player):
        pass
        
    def take_damage(self, damage):
        if not self.alive:
            return False
            
        self.health -= damage
        self.hurt_time = pygame.time.get_ticks()
        self.is_activated = True  # Activeer bij schade
        
        if self.health <= 0:
            self.health = 0
            self.alive = False
            return True
        return False
        
    def get_sprite(self):
        if not self.alive:
            return self.sprite_dead
            
        current_time = pygame.time.get_ticks()
        if current_time - self.hurt_time < self.hurt_duration:
            return self.sprite_hurt
            
        return self.sprite_normal
        
    @property
    def pos(self):
        return (self.x, self.y)


class Boss(Enemy):
    """De eindbaas - groter, sterker, gevaarlijker"""
    
    def __init__(self, x, y):
        super().__init__(x, y)
        
        self.color = 'boss'
        self.health = 400
        self.max_health = 400
        self.speed = 0.0008
        self.damage = 20
        self.attack_range = 2.0
        self.attack_cooldown = 1000
        
        self.is_boss = True
        self.activation_range = 10.0
        
        # Boss sprites
        self.sprite_normal = create_boss_sprite()
        self.sprite_hurt = create_hurt_enemy_sprite(128)
        self.sprite_dead = create_dead_boss_sprite()
        
        # Boss speciale aanvallen
        self.rage_mode = False
        self.rage_threshold = 0.3  # Rage als health < 30%
        
    def update(self, dt, player, door_manager=None):
        if not self.alive:
            return
            
        # Check rage mode
        if self.health / self.max_health < self.rage_threshold and not self.rage_mode:
            self.rage_mode = True
            self.speed *= 1.5
            self.damage = int(self.damage * 1.3)
            self.attack_cooldown = 500
            
        super().update(dt, player, door_manager)
        
    def get_sprite(self):
        if not self.alive:
            return self.sprite_dead
            
        current_time = pygame.time.get_ticks()
        if current_time - self.hurt_time < self.hurt_duration:
            return self.sprite_hurt
            
        return self.sprite_normal


class EnemyManager:
    """Beheert alle vijanden inclusief de boss"""
    
    def __init__(self, level=1):
        self.enemies = []
        self.boss = None
        self.boss_spawned = False
        self.level = level
        self.spawn_enemies()
        
    def spawn_enemies(self):
        """Spawn vijanden verspreid over het level"""
        if self.level == 1:
            self._spawn_level1_enemies()
        elif self.level == 2:
            self._spawn_boss_level()
            
    def _spawn_level1_enemies(self):
        """Level 1: Normale vijanden, geen boss"""
        spawn_positions = [
            # Noordelijke kamers
            (2.5, 2.5),
            (21.5, 2.5),
            
            # Smalle gangen (gevaarlijk!)
            (7.5, 8.5),
            (16.5, 8.5),
            (7.5, 15.5),
            (16.5, 15.5),
            
            # Centrale arena
            (11.5, 10.5),
            (12.5, 13.5),
            
            # Donkere stenen kamer (noordoost)
            (11.5, 2.5),
            (12.5, 4.5),
            
            # Metalen kamer (zuidoost)  
            (11.5, 17.5),
            (12.5, 20.5),
            
            # Wandkleed kamers
            (2.5, 6.5),
            (21.5, 17.5),
            
            # Zuid kamers
            (2.5, 20.5),
            (21.5, 20.5),
        ]
        
        for i, (x, y) in enumerate(spawn_positions):
            enemy_type = Enemy.ENEMY_TYPES[i % len(Enemy.ENEMY_TYPES)]
            self.enemies.append(Enemy(x, y, enemy_type))
            
    def _spawn_boss_level(self):
        """Level 2: Boss arena met de Demon Lord en elite guards"""
        # Elite guards rondom de boss
        guard_positions = [
            (8.5, 8.5),
            (14.5, 8.5),
            (8.5, 14.5),
            (14.5, 14.5),
            (11.5, 6.5),
            (11.5, 16.5),
        ]
        
        # Spawn sterke vijanden als guards
        for i, (x, y) in enumerate(guard_positions):
            # Afwisselen tussen purple (sterk) en orange (snel)
            enemy_type = Enemy.ENEMY_TYPES[3 if i % 2 == 0 else 4]
            self.enemies.append(Enemy(x, y, enemy_type))
            
        # Spawn de boss in het midden
        self.boss = Boss(11.5, 11.5)
        self.enemies.append(self.boss)
        
    def update(self, dt, player, door_manager=None):
        for enemy in self.enemies:
            enemy.update(dt, player, door_manager)
            
    def get_enemy_at_ray(self, player_x, player_y, angle, max_distance=MAX_DEPTH):
        sin_a = math.sin(angle)
        cos_a = math.cos(angle)
        
        # Sorteer vijanden op afstand (dichtste eerst)
        sorted_enemies = []
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            dx = enemy.x - player_x
            dy = enemy.y - player_y
            distance = math.sqrt(dx*dx + dy*dy)
            sorted_enemies.append((enemy, distance))
        
        sorted_enemies.sort(key=lambda x: x[1])
        
        for enemy, distance in sorted_enemies:
            if distance > max_distance or distance < 0.5:
                continue
                
            dx = enemy.x - player_x
            dy = enemy.y - player_y
            enemy_angle = math.atan2(dy, dx)
            
            delta = enemy_angle - angle
            while delta > math.pi:
                delta -= 2 * math.pi
            while delta < -math.pi:
                delta += 2 * math.pi
            
            # Grotere hit radius voor boss
            hit_radius = 0.5 / distance if hasattr(enemy, 'is_boss') else 0.4 / distance
            
            if abs(delta) < hit_radius:
                return enemy, distance
                
        return None, 0
        
    def check_player_damage(self, player):
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
        for enemy in self.enemies:
            sprite = enemy.get_sprite()
            # Boss is groter
            if hasattr(enemy, 'is_boss'):
                scale = 1.2 if enemy.alive else 0.8
            else:
                scale = 0.6 if enemy.alive else 0.4
            sprite_renderer.add_sprite(sprite, enemy.x, enemy.y, scale)
            
    @property
    def alive_count(self):
        return sum(1 for e in self.enemies if e.alive)
    
    @property
    def boss_alive(self):
        return self.boss and self.boss.alive
