"""
Vijand Systeem - Mensachtige vijanden met loopanimaties, AI en Boss
"""
import pygame
import math
import random
from settings import *
from map import is_wall, is_door
from sprites import create_enemy_walk_frames, create_dead_enemy_sprite, create_hurt_enemy_sprite
from sprites import create_boss_walk_frames, create_dead_boss_sprite


class EnemyBullet:
    """Een kogel geschoten door een vijand"""
    
    def __init__(self, x, y, target_x, target_y, damage=10, speed=0.015, color=(255, 200, 50)):
        self.x = x
        self.y = y
        self.damage = damage
        self.speed = speed
        self.color = color
        self.alive = True
        self.hit_range = 0.5
        self.lifetime = 0
        self.max_lifetime = 5000  # 5 seconden max
        
        # Bereken richting naar target
        dx = target_x - x
        dy = target_y - y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0:
            self.dir_x = dx / dist
            self.dir_y = dy / dist
        else:
            self.dir_x = 0
            self.dir_y = 1
            
        # Sprite
        self.sprite = self._create_sprite()
        
    def _create_sprite(self):
        """Maak kogel sprite"""
        size = 16
        sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2
        
        # Glow
        pygame.draw.circle(sprite, (*self.color[:3], 80), (cx, cy), 6)
        # Core
        pygame.draw.circle(sprite, self.color, (cx, cy), 4)
        pygame.draw.circle(sprite, (255, 255, 255), (cx, cy), 2)
        
        return sprite
        
    def update(self, dt):
        """Beweeg kogel (check alleen muur collision, player check in get_bullet_damage)"""
        if not self.alive:
            return
            
        # Lifetime check
        self.lifetime += dt
        if self.lifetime > self.max_lifetime:
            self.alive = False
            return
            
        # Beweeg
        self.x += self.dir_x * self.speed * dt
        self.y += self.dir_y * self.speed * dt
            
        # Check muur collision
        if is_wall(int(self.x), int(self.y)):
            self.alive = False
        
    def get_sprite(self):
        return self.sprite if self.alive else None


class Enemy:
    """Een mensachtige vijand met wapen en schietmechanisme"""
    
    # Minder vijanden maar sterker - meer health, meer damage
    ENEMY_TYPES = [
        {'color': 'red', 'health': 120, 'speed': 0.0015, 'damage': 12, 'fire_rate': 1500},
        {'color': 'green', 'health': 150, 'speed': 0.0012, 'damage': 18, 'fire_rate': 2000},
        {'color': 'blue', 'health': 90, 'speed': 0.0022, 'damage': 10, 'fire_rate': 1200},
        {'color': 'purple', 'health': 180, 'speed': 0.001, 'damage': 22, 'fire_rate': 2500},
        {'color': 'orange', 'health': 100, 'speed': 0.0018, 'damage': 15, 'fire_rate': 1300},
    ]
    
    # Kogel kleuren per vijand type
    BULLET_COLORS = {
        'red': (255, 100, 100),
        'green': (100, 255, 100),
        'blue': (100, 150, 255),
        'purple': (200, 100, 255),
        'orange': (255, 180, 80),
    }
    
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
        self.fire_rate = enemy_type.get('fire_rate', 1500)  # ms tussen schoten
        
        # Schiet systeem
        self.attack_range = 10.0  # Vijanden schieten van afstand!
        self.min_attack_range = 2.0  # Niet te dichtbij
        self.attack_cooldown = self.fire_rate
        self.last_attack = 0
        self.projectiles = []  # Kogels van deze vijand
        self.bullet_speed = 0.018
        self.bullet_color = self.BULLET_COLORS.get(self.color, (255, 200, 50))
        
        self.alive = True
        self.hurt_time = 0
        self.hurt_duration = 100
        
        # Animatie systeem
        self.walk_frames = create_enemy_walk_frames(self.color)
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 150  # ms per frame
        self.is_moving = False
        
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
        # Update projectielen ook als vijand dood is
        self._update_projectiles(dt)
        
        if not self.alive:
            return
            
        # Check activatie
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < self.activation_range:
            self.is_activated = True
            
        if not self.is_activated:
            self.is_moving = False
            return
            
        current_time = pygame.time.get_ticks()
        
        if current_time - self.path_update_time > self.path_update_interval:
            self.target_x = player.x
            self.target_y = player.y
            self.path_update_time = current_time
        
        self.is_moving = False  # Reset, wordt true als we bewegen
        
        # Beweeg naar ideale schietafstand (niet te dichtbij, niet te ver)
        ideal_distance = (self.attack_range + self.min_attack_range) / 2
        
        if distance > self.attack_range:
            # Te ver weg - kom dichterbij
            if distance > 0:
                move_x = (dx / distance) * self.speed * dt
                move_y = (dy / distance) * self.speed * dt
                
                new_x = self.x + move_x
                new_y = self.y + move_y
                
                moved = False
                if self.can_move_to(new_x, self.y, door_manager):
                    self.x = new_x
                    moved = True
                if self.can_move_to(self.x, new_y, door_manager):
                    self.y = new_y
                    moved = True
                    
                self.is_moving = moved
        elif distance < self.min_attack_range:
            # Te dichtbij - ga achteruit
            if distance > 0:
                move_x = -(dx / distance) * self.speed * dt * 0.5
                move_y = -(dy / distance) * self.speed * dt * 0.5
                
                new_x = self.x + move_x
                new_y = self.y + move_y
                
                if self.can_move_to(new_x, self.y, door_manager):
                    self.x = new_x
                if self.can_move_to(self.x, new_y, door_manager):
                    self.y = new_y
        
        # Schiet op speler als in range en zichtlijn vrij
        if distance >= self.min_attack_range and distance <= self.attack_range:
            if current_time - self.last_attack > self.attack_cooldown:
                if self._has_line_of_sight(player.x, player.y):
                    self._fire_bullet(player.x, player.y)
                    self.last_attack = current_time
                
        # Update animatie
        if self.is_moving:
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.walk_frames)
        else:
            # Idle - gebruik frame 0
            self.current_frame = 0
            self.animation_timer = 0
            
    def _has_line_of_sight(self, target_x, target_y):
        """Check of er een vrije zichtlijn naar het doel is"""
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < 0.1:
            return True
            
        steps = int(distance * 2)
        if steps < 1:
            steps = 1
            
        for i in range(1, steps):
            t = i / steps
            check_x = self.x + dx * t
            check_y = self.y + dy * t
            
            if is_wall(int(check_x), int(check_y)):
                return False
                
        return True
        
    def _fire_bullet(self, target_x, target_y):
        """Schiet een kogel naar de speler"""
        # Kleine random spread voor meer realisme
        spread = 0.1
        target_x += random.uniform(-spread, spread)
        target_y += random.uniform(-spread, spread)
        
        bullet = EnemyBullet(
            self.x, self.y, target_x, target_y,
            self.damage, self.bullet_speed, self.bullet_color
        )
        self.projectiles.append(bullet)
        
    def _update_projectiles(self, dt):
        """Update alle kogels (beweging en muur collision)"""
        for proj in self.projectiles[:]:
            if proj.alive:
                proj.update(dt)
            else:
                self.projectiles.remove(proj)
                
    def get_bullet_damage(self, player_x, player_y):
        """Check of een kogel de speler raakt, return damage"""
        total_damage = 0
        for proj in self.projectiles[:]:
            if proj.alive:
                dx = player_x - proj.x
                dy = player_y - proj.y
                dist = math.sqrt(dx*dx + dy*dy)
                if dist < proj.hit_range:
                    proj.alive = False
                    total_damage += proj.damage
        return total_damage
                
    def can_move_to(self, x, y, door_manager=None):
        if is_wall(x, y):
            return False
        if is_door(x, y):
            if door_manager:
                return door_manager.can_pass(x, y)
            return False
        return True
        
        
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
            
        # Return huidige animatie frame
        return self.walk_frames[self.current_frame]
        
    @property
    def pos(self):
        return (self.x, self.y)


class Projectile:
    """Een projectiel geschoten door de boss - snel en dodelijk"""
    
    def __init__(self, x, y, target_x, target_y, damage=25, speed=0.025):
        self.x = x
        self.y = y
        self.damage = damage
        self.speed = speed  # Veel sneller!
        self.alive = True
        self.hit_range = 0.8  # Grotere hit range
        self.lifetime = 0
        self.max_lifetime = 8000  # Max 8 seconden voordat het verdwijnt
        
        # Bereken richting naar target
        dx = target_x - x
        dy = target_y - y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0:
            self.dir_x = dx / dist
            self.dir_y = dy / dist
        else:
            self.dir_x = 0
            self.dir_y = 1
            
        # Sprite
        self.sprite = self._create_sprite()
        self.glow_pulse = 0
        
    def _create_sprite(self):
        """Maak grote, duidelijke vuurbal sprite"""
        size = 64  # Groter!
        sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2
        
        # Grote outer glow
        for r in range(6, 0, -1):
            alpha = 80 - r * 10
            pygame.draw.circle(sprite, (255, 80, 0, alpha), (cx, cy), 20 + r * 4)
        
        # Inner glow
        pygame.draw.circle(sprite, (255, 150, 30), (cx, cy), 18)
        
        # Core - fel oranje/geel
        pygame.draw.circle(sprite, (255, 200, 50), (cx, cy), 14)
        pygame.draw.circle(sprite, (255, 255, 100), (cx, cy), 10)
        pygame.draw.circle(sprite, (255, 255, 200), (cx, cy), 6)
        pygame.draw.circle(sprite, (255, 255, 255), (cx, cy), 3)
        
        return sprite
        
    def update(self, dt):
        """Beweeg projectiel (player hit check in get_projectile_damage)"""
        if not self.alive:
            return
            
        # Lifetime check
        self.lifetime += dt
        if self.lifetime > self.max_lifetime:
            self.alive = False
            return
            
        # Beweeg - snelle vuurbal!
        self.x += self.dir_x * self.speed * dt
        self.y += self.dir_y * self.speed * dt
        
        # Glow animatie
        self.glow_pulse = (math.sin(pygame.time.get_ticks() * 0.02) + 1) * 0.5
            
        # Check muur collision
        if is_wall(int(self.x), int(self.y)):
            self.alive = False
            
        return False
        
    def get_sprite(self):
        if not self.alive:
            return None
        
        size = 64  # Groter!
        animated = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Pulserende extra glow - feller
        glow_alpha = int(50 + self.glow_pulse * 60)
        pygame.draw.circle(animated, (255, 100, 0, glow_alpha), (size//2, size//2), 28)
        
        animated.blit(self.sprite, (0, 0))
        return animated


class Boss(Enemy):
    """De eindbaas - imposante commandant met dodelijke vuurbal aanvallen"""
    
    def __init__(self, x, y, is_final=False):
        super().__init__(x, y)
        
        self.color = 'boss'
        self.is_final_boss = is_final
        
        # Final boss is veel sterker
        if is_final:
            self.health = 800
            self.max_health = 800
            self.speed = 0.0012
            self.damage = 30
            self.projectile_damage = 35
            self.projectile_speed = 0.035  # Zeer snelle vuurballen
        else:
            self.health = 500
            self.max_health = 500
            self.speed = 0.001
            self.damage = 25
            self.projectile_damage = 25
            self.projectile_speed = 0.028  # Snelle vuurballen
            
        self.attack_range = 2.5
        self.attack_cooldown = 800
        
        # Projectiel aanval - verder en vaker
        self.ranged_attack_range = 15.0  # Veel verder schieten!
        self.ranged_cooldown = 1500  # 1.5 seconden tussen vuurballen
        self.last_ranged_attack = 0
        self.projectiles = []
        
        self.is_boss = True
        self.activation_range = 12.0  # Grotere activatie range
        
        # Boss animatie frames
        self.walk_frames = create_boss_walk_frames()
        self.animation_speed = 200
        
        self.sprite_hurt = create_hurt_enemy_sprite(128)
        self.sprite_dead = create_dead_boss_sprite()
        
        # Boss speciale aanvallen
        self.rage_mode = False
        self.rage_threshold = 0.3
        
    def update(self, dt, player, door_manager=None):
        if not self.alive:
            # Update projectielen ook als boss dood is
            self._update_projectiles(dt)
            return
            
        current_time = pygame.time.get_ticks()
            
        # Check rage mode - boss wordt gevaarlijk!
        if self.health / self.max_health < self.rage_threshold and not self.rage_mode:
            self.rage_mode = True
            self.speed *= 1.8  # Veel sneller
            self.damage = int(self.damage * 1.5)
            self.projectile_damage = int(self.projectile_damage * 1.5)
            self.attack_cooldown = 400
            self.ranged_cooldown = 800  # Elke 0.8 seconden een vuurbal!
            self.animation_speed = 100
            
        # Check afstand tot speler voor projectiel aanval
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Schiet vuurbal als speler in range maar niet te dichtbij
        if self.is_activated and distance > self.attack_range and distance < self.ranged_attack_range:
            if current_time - self.last_ranged_attack > self.ranged_cooldown:
                self._fire_projectile(player.x, player.y)
                self.last_ranged_attack = current_time
        
        # Update projectielen
        self._update_projectiles(dt)
            
        super().update(dt, player, door_manager)
        
    def _fire_projectile(self, target_x, target_y):
        """Schiet een vuurbal naar de speler - snel en dodelijk!"""
        speed = self.projectile_speed if not self.rage_mode else self.projectile_speed * 1.3
        proj = Projectile(self.x, self.y, target_x, target_y, 
                         self.projectile_damage, speed)
        self.projectiles.append(proj)
        
    def _update_projectiles(self, dt):
        """Update alle projectielen (player hit check in get_projectile_damage)"""
        for proj in self.projectiles[:]:
            if proj.alive:
                proj.update(dt)
            else:
                self.projectiles.remove(proj)
                
    def get_projectile_damage(self, player_x, player_y):
        """Check of een projectiel de speler raakt, return damage"""
        total_damage = 0
        for proj in self.projectiles[:]:
            if proj.alive:
                dx = player_x - proj.x
                dy = player_y - proj.y
                dist = math.sqrt(dx*dx + dy*dy)
                if dist < proj.hit_range:
                    proj.alive = False
                    total_damage += proj.damage
        return total_damage
        
    def get_sprite(self):
        if not self.alive:
            return self.sprite_dead
            
        current_time = pygame.time.get_ticks()
        if current_time - self.hurt_time < self.hurt_duration:
            return self.sprite_hurt
            
        # Return huidige animatie frame
        return self.walk_frames[self.current_frame]


class EnemyManager:
    """Beheert alle vijanden inclusief de boss"""
    
    def __init__(self, level=1, custom_positions=None, boss_position=None, game_map=None, is_final_boss=False):
        self.enemies = []
        self.boss = None
        self.boss_spawned = False
        self.level = level
        self.game_map = game_map
        self.is_final_boss = is_final_boss
        self.spawn_enemies(custom_positions, boss_position)
        
    def spawn_enemies(self, custom_positions=None, boss_position=None):
        """Spawn vijanden op aangegeven of standaard posities"""
        if custom_positions is not None:
            # Gebruik aangepaste posities
            for i, (x, y) in enumerate(custom_positions):
                enemy_type = Enemy.ENEMY_TYPES[i % len(Enemy.ENEMY_TYPES)]
                self.enemies.append(Enemy(x, y, enemy_type))
        else:
            # Fallback naar oude systeem
            if self.level == 1:
                self._spawn_level1_enemies()
            elif self.level == 2:
                self._spawn_boss_level()
                
        # Spawn boss als positie gegeven
        if boss_position:
            self.boss = Boss(boss_position[0], boss_position[1], is_final=self.is_final_boss)
            self.enemies.append(self.boss)
            
    def _spawn_level1_enemies(self):
        """Level 1: Normale vijanden, geen boss (fallback)"""
        spawn_positions = [
            (2.5, 2.5), (21.5, 2.5),
            (7.5, 8.5), (16.5, 8.5), (7.5, 15.5), (16.5, 15.5),
            (11.5, 10.5), (12.5, 13.5),
            (11.5, 2.5), (12.5, 4.5),
            (11.5, 17.5), (12.5, 20.5),
            (2.5, 6.5), (21.5, 17.5),
            (2.5, 20.5), (21.5, 20.5),
        ]
        
        for i, (x, y) in enumerate(spawn_positions):
            enemy_type = Enemy.ENEMY_TYPES[i % len(Enemy.ENEMY_TYPES)]
            self.enemies.append(Enemy(x, y, enemy_type))
            
    def _spawn_boss_level(self):
        """Level 2: Boss arena met de Demon Lord (fallback)"""
        guard_positions = [
            (8.5, 8.5), (14.5, 8.5), (8.5, 14.5), 
            (14.5, 14.5), (11.5, 6.5), (11.5, 16.5),
        ]
        
        for i, (x, y) in enumerate(guard_positions):
            enemy_type = Enemy.ENEMY_TYPES[3 if i % 2 == 0 else 4]
            self.enemies.append(Enemy(x, y, enemy_type))
            
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
        """Check schade van alle vijandelijke kogels en projectielen"""
        damage = 0
        
        for enemy in self.enemies:
            # Check kogel damage van normale vijanden
            if hasattr(enemy, 'get_bullet_damage'):
                bullet_damage = enemy.get_bullet_damage(player.x, player.y)
                damage += bullet_damage
                    
            # Check projectile damage van boss (vuurballen)
            if hasattr(enemy, 'is_boss') and hasattr(enemy, 'get_projectile_damage'):
                proj_damage = enemy.get_projectile_damage(player.x, player.y)
                damage += proj_damage
                    
        return damage
        
    def render(self, sprite_renderer):
        for enemy in self.enemies:
            sprite = enemy.get_sprite()
            # Boss is groter
            if hasattr(enemy, 'is_boss'):
                if enemy.alive:
                    scale = 0.6
                    y_offset = 0.35  # Stevig op de grond
                else:
                    scale = 0.4
                    y_offset = 0.5  # Liggend op de grond
                    
                # Render boss projectielen (vuurballen) - groter en duidelijker
                if hasattr(enemy, 'projectiles'):
                    for proj in enemy.projectiles:
                        if proj.alive:
                            proj_sprite = proj.get_sprite()
                            if proj_sprite:
                                sprite_renderer.add_sprite(proj_sprite, proj.x, proj.y, 0.4, 0.0)
            else:
                if enemy.alive:
                    scale = 0.3
                    y_offset = 0.25  # Stevig op de grond
                else:
                    scale = 0.2
                    y_offset = 0.4  # Liggend op de grond
                    
            # Render kogels van alle vijanden (ook normale)
            if hasattr(enemy, 'projectiles'):
                for proj in enemy.projectiles:
                    if proj.alive:
                        proj_sprite = proj.get_sprite()
                        if proj_sprite:
                            # Vijand kogels zijn kleiner dan boss vuurballen
                            bullet_scale = 0.15 if not hasattr(enemy, 'is_boss') else 0.4
                            sprite_renderer.add_sprite(proj_sprite, proj.x, proj.y, bullet_scale, 0.0)
                            
            sprite_renderer.add_sprite(sprite, enemy.x, enemy.y, scale, y_offset)
            
    @property
    def alive_count(self):
        return sum(1 for e in self.enemies if e.alive)
    
    @property
    def boss_alive(self):
        return self.boss and self.boss.alive
