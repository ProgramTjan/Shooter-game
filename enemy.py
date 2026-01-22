"""
Vijand Systeem v2.0 - Verbeterde AI, States, en Combat Experience
=================================================================

Verbeteringen:
- State Machine (IDLE, PATROL, ALERT, CHASE, ATTACK, HURT, DYING)
- Verschillende vijand gedragstypes (Ranged, Charger, Dodger)
- Death animatie met fade-out
- Stagger/knockback bij schade
- Attack telegraphing (waarschuwing voor aanval)
- Alert system (vijanden waarschuwen elkaar)
- Verbeterde visual feedback
"""
import pygame
import math
import random
from settings import *
from map import is_wall, is_door
from sprites import create_enemy_walk_frames, create_dead_enemy_sprite, create_hurt_enemy_sprite
from sprites import create_boss_walk_frames, create_dead_boss_sprite


# ============================================
# ENEMY STATES
# ============================================
class EnemyState:
    IDLE = 'idle'
    PATROL = 'patrol'
    ALERT = 'alert'      # Net de speler gezien, korte reactie
    CHASE = 'chase'
    ATTACK = 'attack'    # Aanval uitvoeren
    HURT = 'hurt'        # Geraakt, korte stagger
    DYING = 'dying'      # Dood animatie
    DEAD = 'dead'


# ============================================
# ENEMY BEHAVIOR TYPES
# ============================================
class BehaviorType:
    RANGED = 'ranged'       # Houdt afstand, schiet
    CHARGER = 'charger'     # Rent naar speler, melee
    DODGER = 'dodger'       # Schiet en ontwijkt
    BOSS = 'boss'           # Boss specifiek gedrag


class EnemyBullet:
    """Een kogel geschoten door een vijand"""
    
    def __init__(self, x, y, target_x, target_y, damage=10, speed=0.015, color=(255, 200, 50)):
        self.x = x
        self.y = y
        self.damage = damage
        self.speed = speed
        self.color = color
        self.alive = True
        self.hit_range = 0.35  # Kleinere hit range voor eerlijkere gameplay
        self.lifetime = 0
        self.max_lifetime = 5000
        
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
        """Beweeg kogel"""
        if not self.alive:
            return
            
        self.lifetime += dt
        if self.lifetime > self.max_lifetime:
            self.alive = False
            return
            
        self.x += self.dir_x * self.speed * dt
        self.y += self.dir_y * self.speed * dt
            
        if is_wall(int(self.x), int(self.y)):
            self.alive = False
        
    def get_sprite(self):
        return self.sprite if self.alive else None


class Enemy:
    """
    Verbeterde vijand met state machine en gedragstypes
    """
    
    # Vijand types met stats (gebalanceerde damage waarden)
    ENEMY_TYPES = [
        {'color': 'red', 'health': 120, 'speed': 0.0012, 'damage': 8, 'fire_rate': 1500, 'behavior': BehaviorType.RANGED},
        {'color': 'green', 'health': 150, 'speed': 0.00096, 'damage': 10, 'fire_rate': 2000, 'behavior': BehaviorType.RANGED},
        {'color': 'blue', 'health': 80, 'speed': 0.0022, 'damage': 15, 'fire_rate': 0, 'behavior': BehaviorType.CHARGER},
        {'color': 'purple', 'health': 100, 'speed': 0.0016, 'damage': 8, 'fire_rate': 1800, 'behavior': BehaviorType.DODGER},
        {'color': 'orange', 'health': 100, 'speed': 0.00144, 'damage': 9, 'fire_rate': 1300, 'behavior': BehaviorType.RANGED},
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
        self.spawn_x = x
        self.spawn_y = y
        
        if enemy_type is None:
            enemy_type = random.choice(self.ENEMY_TYPES)
        
        self.color = enemy_type['color']
        self.health = enemy_type['health']
        self.max_health = enemy_type['health']
        self.base_speed = enemy_type['speed']
        self.speed = self.base_speed
        self.damage = enemy_type['damage']
        self.fire_rate = enemy_type.get('fire_rate', 1500)
        self.behavior = enemy_type.get('behavior', BehaviorType.RANGED)
        
        # State machine
        self.state = EnemyState.IDLE
        self.state_timer = 0
        self.previous_state = None
        
        # Patrol systeem
        self.patrol_points = self._generate_patrol_points()
        self.current_patrol_index = 0
        self.patrol_wait_time = 0
        self.patrol_wait_duration = random.randint(1000, 3000)
        
        # Alert systeem
        self.alert_duration = 500  # ms voor alert reactie
        self.alert_timer = 0
        self.is_alerted = False
        
        # Combat systeem
        self.attack_range = 10.0 if self.behavior != BehaviorType.CHARGER else 2.0
        self.min_attack_range = 2.0 if self.behavior != BehaviorType.CHARGER else 0.8
        self.attack_cooldown = self.fire_rate
        self.last_attack = 0
        self.projectiles = []
        self.bullet_speed = 0.018
        self.bullet_color = self.BULLET_COLORS.get(self.color, (255, 200, 50))
        
        # Attack telegraphing
        self.is_telegraphing = False
        self.telegraph_timer = 0
        self.telegraph_duration = 300  # ms warning voor aanval
        
        # Stagger/Hurt systeem
        self.hurt_timer = 0
        self.hurt_duration = 200  # ms stagger
        self.knockback_x = 0
        self.knockback_y = 0
        self.knockback_force = 0.003
        
        # Death animatie
        self.death_timer = 0
        self.death_duration = 800  # ms death fade
        self.death_alpha = 255
        
        # Dodger specifiek
        self.dodge_cooldown = 2000
        self.last_dodge = 0
        self.is_dodging = False
        self.dodge_timer = 0
        self.dodge_duration = 400
        self.dodge_dir_x = 0
        self.dodge_dir_y = 0
        
        # Charger specifiek
        self.charge_speed_multiplier = 2.5
        self.is_charging = False
        self.charge_timer = 0
        self.charge_duration = 1500
        self.charge_cooldown = 3000
        self.last_charge = 0
        
        self.alive = True
        
        # Animatie systeem
        self.walk_frames = create_enemy_walk_frames(self.color)
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 150
        self.is_moving = False
        
        self.sprite_hurt = create_hurt_enemy_sprite()
        self.sprite_dead = create_dead_enemy_sprite(self.color)
        
        self.target_x = x
        self.target_y = y
        self.path_update_time = 0
        self.path_update_interval = 500
        
        # Activatie afstand
        self.activation_range = 8.0
        self.is_activated = False
        
        # Detection
        self.detection_range = 12.0
        self.last_known_player_x = None
        self.last_known_player_y = None
        
    def _generate_patrol_points(self):
        """Genereer willekeurige patrol punten rond spawn positie (alleen op geldige posities)"""
        points = [(self.spawn_x, self.spawn_y)]
        attempts = 0
        max_attempts = 20
        
        while len(points) < random.randint(3, 5) and attempts < max_attempts:
            offset_x = random.uniform(-3, 3)
            offset_y = random.uniform(-3, 3)
            new_x = self.spawn_x + offset_x
            new_y = self.spawn_y + offset_y
            
            # Check of dit punt geldig is (geen muur)
            if not is_wall(int(new_x), int(new_y)):
                points.append((new_x, new_y))
            attempts += 1
            
        return points
        
    def _change_state(self, new_state):
        """Verander naar nieuwe state"""
        if self.state != new_state:
            self.previous_state = self.state
            self.state = new_state
            self.state_timer = 0
            
            # State-specifieke initialisatie
            if new_state == EnemyState.ALERT:
                self.alert_timer = 0
            elif new_state == EnemyState.DYING:
                self.death_timer = 0
                self.death_alpha = 255
            elif new_state == EnemyState.HURT:
                self.hurt_timer = 0
                
    def update(self, dt, player, door_manager=None, enemy_manager=None):
        """Update vijand met state machine"""
        # Update projectielen altijd
        self._update_projectiles(dt)
        
        # Check of echt dood
        if self.state == EnemyState.DEAD:
            return
            
        # Death animatie
        if self.state == EnemyState.DYING:
            self._update_dying(dt)
            return
            
        # Hurt/stagger state
        if self.state == EnemyState.HURT:
            self._update_hurt(dt, door_manager)
            return
            
        # Calculate distance to player
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        current_time = pygame.time.get_ticks()
        
        # Check voor speler detectie
        can_see_player = distance < self.detection_range and self._has_line_of_sight(player.x, player.y)
        
        # Update last known position
        if can_see_player:
            self.last_known_player_x = player.x
            self.last_known_player_y = player.y
            
            # Alert nearby enemies
            if enemy_manager and not self.is_alerted:
                self._alert_nearby_enemies(enemy_manager)
                self.is_alerted = True
        
        # State machine logic
        if self.state == EnemyState.IDLE:
            self._update_idle(dt, can_see_player)
        elif self.state == EnemyState.PATROL:
            self._update_patrol(dt, can_see_player, door_manager)
        elif self.state == EnemyState.ALERT:
            self._update_alert(dt)
        elif self.state == EnemyState.CHASE:
            self._update_chase(dt, player, distance, can_see_player, door_manager, current_time)
        elif self.state == EnemyState.ATTACK:
            self._update_attack(dt, player, distance, current_time)
            
        # Update animatie
        self._update_animation(dt)
        
    def _update_idle(self, dt, can_see_player):
        """Idle state - wacht of ga patrouileren"""
        self.is_moving = False
        self.state_timer += dt
        
        if can_see_player:
            self._change_state(EnemyState.ALERT)
        elif self.state_timer > random.randint(2000, 5000):
            self._change_state(EnemyState.PATROL)
            
    def _update_patrol(self, dt, can_see_player, door_manager):
        """Patrol state - beweeg tussen punten"""
        if can_see_player:
            self._change_state(EnemyState.ALERT)
            return
            
        # Wacht bij patrol punt
        if self.patrol_wait_time > 0:
            self.patrol_wait_time -= dt
            self.is_moving = False
            return
            
        # Beweeg naar volgend patrol punt
        target = self.patrol_points[self.current_patrol_index]
        dx = target[0] - self.x
        dy = target[1] - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist < 0.3:
            # Bereikt punt, ga naar volgende
            self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)
            self.patrol_wait_time = self.patrol_wait_duration
            self.is_moving = False
        else:
            # Beweeg naar punt
            move_x = (dx / dist) * self.speed * 0.5 * dt  # Langzamer tijdens patrol
            move_y = (dy / dist) * self.speed * 0.5 * dt
            
            new_x = self.x + move_x
            new_y = self.y + move_y
            
            if self.can_move_to(new_x, self.y, door_manager):
                self.x = new_x
                self.is_moving = True
            if self.can_move_to(self.x, new_y, door_manager):
                self.y = new_y
                self.is_moving = True
                
    def _update_alert(self, dt):
        """Alert state - korte reactie voor chase"""
        self.alert_timer += dt
        self.is_moving = False
        
        if self.alert_timer >= self.alert_duration:
            self._change_state(EnemyState.CHASE)
            
    def _update_chase(self, dt, player, distance, can_see_player, door_manager, current_time):
        """Chase state - volg en val aan gebaseerd op behavior type"""
        self.target_x = player.x
        self.target_y = player.y
        
        # Behavior-specifieke chase
        if self.behavior == BehaviorType.CHARGER:
            self._chase_charger(dt, player, distance, door_manager, current_time)
        elif self.behavior == BehaviorType.DODGER:
            self._chase_dodger(dt, player, distance, door_manager, current_time)
        else:
            self._chase_ranged(dt, player, distance, door_manager, current_time)
            
    def _chase_ranged(self, dt, player, distance, door_manager, current_time):
        """Ranged vijand - houd afstand en schiet"""
        dx = player.x - self.x
        dy = player.y - self.y
        
        self.is_moving = False
        ideal_distance = (self.attack_range + self.min_attack_range) / 2
        
        if distance > self.attack_range:
            # Te ver - kom dichterbij
            if distance > 0:
                move_x = (dx / distance) * self.speed * dt
                move_y = (dy / distance) * self.speed * dt
                
                new_x = self.x + move_x
                new_y = self.y + move_y
                
                if self.can_move_to(new_x, self.y, door_manager):
                    self.x = new_x
                    self.is_moving = True
                if self.can_move_to(self.x, new_y, door_manager):
                    self.y = new_y
                    self.is_moving = True
                    
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
        
        # Schiet als in range
        if distance >= self.min_attack_range and distance <= self.attack_range:
            if current_time - self.last_attack > self.attack_cooldown:
                if self._has_line_of_sight(player.x, player.y):
                    self._start_attack(player.x, player.y)
                    
    def _chase_charger(self, dt, player, distance, door_manager, current_time):
        """Charger vijand - rent naar speler voor melee"""
        dx = player.x - self.x
        dy = player.y - self.y
        
        # Check voor charge
        if not self.is_charging and distance < 6.0 and distance > self.min_attack_range:
            if current_time - self.last_charge > self.charge_cooldown:
                if self._has_line_of_sight(player.x, player.y):
                    self.is_charging = True
                    self.charge_timer = 0
                    self.last_charge = current_time
                    # Telegraph de charge
                    self.is_telegraphing = True
                    self.telegraph_timer = 0
                    
        if self.is_charging:
            self.charge_timer += dt
            
            # Telegraph fase
            if self.is_telegraphing:
                self.telegraph_timer += dt
                if self.telegraph_timer >= self.telegraph_duration:
                    self.is_telegraphing = False
                self.is_moving = False
                return
                
            # Charge beweging
            if self.charge_timer < self.charge_duration:
                speed = self.speed * self.charge_speed_multiplier
                if distance > 0:
                    move_x = (dx / distance) * speed * dt
                    move_y = (dy / distance) * speed * dt
                    
                    new_x = self.x + move_x
                    new_y = self.y + move_y
                    
                    if self.can_move_to(new_x, self.y, door_manager):
                        self.x = new_x
                    if self.can_move_to(self.x, new_y, door_manager):
                        self.y = new_y
                        
                self.is_moving = True
                
                # Melee hit check
                if distance < self.min_attack_range:
                    self.is_charging = False
                    self._change_state(EnemyState.ATTACK)
            else:
                self.is_charging = False
        else:
            # Normale beweging naar speler
            if distance > self.min_attack_range:
                if distance > 0:
                    move_x = (dx / distance) * self.speed * dt
                    move_y = (dy / distance) * self.speed * dt
                    
                    new_x = self.x + move_x
                    new_y = self.y + move_y
                    
                    if self.can_move_to(new_x, self.y, door_manager):
                        self.x = new_x
                        self.is_moving = True
                    if self.can_move_to(self.x, new_y, door_manager):
                        self.y = new_y
                        self.is_moving = True
            else:
                # In melee range
                if current_time - self.last_attack > 1000:  # 1s melee cooldown
                    self._change_state(EnemyState.ATTACK)
                    
    def _chase_dodger(self, dt, player, distance, door_manager, current_time):
        """Dodger vijand - schiet en ontwijkt"""
        dx = player.x - self.x
        dy = player.y - self.y
        
        # Check voor dodge
        if not self.is_dodging and distance < 5.0:
            if current_time - self.last_dodge > self.dodge_cooldown:
                self.is_dodging = True
                self.dodge_timer = 0
                self.last_dodge = current_time
                # Dodge perpendiculair op speler richting
                if random.random() > 0.5:
                    self.dodge_dir_x = -dy / distance if distance > 0 else 0
                    self.dodge_dir_y = dx / distance if distance > 0 else 1
                else:
                    self.dodge_dir_x = dy / distance if distance > 0 else 0
                    self.dodge_dir_y = -dx / distance if distance > 0 else 1
                    
        if self.is_dodging:
            self.dodge_timer += dt
            if self.dodge_timer < self.dodge_duration:
                speed = self.speed * 2.0
                move_x = self.dodge_dir_x * speed * dt
                move_y = self.dodge_dir_y * speed * dt
                
                new_x = self.x + move_x
                new_y = self.y + move_y
                
                if self.can_move_to(new_x, self.y, door_manager):
                    self.x = new_x
                if self.can_move_to(self.x, new_y, door_manager):
                    self.y = new_y
                    
                self.is_moving = True
            else:
                self.is_dodging = False
        else:
            # Normale ranged behavior met strafe
            self._chase_ranged(dt, player, distance, door_manager, current_time)
            
    def _update_attack(self, dt, player, distance, current_time):
        """Attack state - voer aanval uit"""
        self.state_timer += dt
        
        if self.behavior == BehaviorType.CHARGER:
            # Melee aanval
            if self.state_timer >= 300:  # Attack duration
                self.last_attack = current_time
                self._change_state(EnemyState.CHASE)
        else:
            # Ranged aanval is instant na telegraph
            self._change_state(EnemyState.CHASE)
            
    def _start_attack(self, target_x, target_y):
        """Start een aanval met telegraph"""
        self.is_telegraphing = True
        self.telegraph_timer = 0
        self._scheduled_attack_target = (target_x, target_y)
        
    def _update_hurt(self, dt, door_manager):
        """Hurt state - stagger en knockback"""
        self.hurt_timer += dt
        self.is_moving = False
        
        # Apply knockback
        if self.knockback_x != 0 or self.knockback_y != 0:
            knockback_decay = 0.9
            move_x = self.knockback_x * dt
            move_y = self.knockback_y * dt
            
            new_x = self.x + move_x
            new_y = self.y + move_y
            
            if self.can_move_to(new_x, self.y, door_manager):
                self.x = new_x
            if self.can_move_to(self.x, new_y, door_manager):
                self.y = new_y
                
            self.knockback_x *= knockback_decay
            self.knockback_y *= knockback_decay
            
            if abs(self.knockback_x) < 0.0001:
                self.knockback_x = 0
            if abs(self.knockback_y) < 0.0001:
                self.knockback_y = 0
        
        if self.hurt_timer >= self.hurt_duration:
            self._change_state(EnemyState.CHASE)
            
    def _update_dying(self, dt):
        """Dying state - death animatie"""
        self.death_timer += dt
        
        # Fade out
        progress = self.death_timer / self.death_duration
        self.death_alpha = int(255 * (1 - progress))
        
        if self.death_timer >= self.death_duration:
            self.state = EnemyState.DEAD
            self.alive = False
            
    def _update_animation(self, dt):
        """Update animatie frames"""
        # Telegraph animatie effect
        if self.is_telegraphing:
            self.telegraph_timer += dt
            if self.telegraph_timer >= self.telegraph_duration:
                self.is_telegraphing = False
                # Voer de aanval uit
                if hasattr(self, '_scheduled_attack_target'):
                    target = self._scheduled_attack_target
                    self._fire_bullet(target[0], target[1])
                    self.last_attack = pygame.time.get_ticks()
                    delattr(self, '_scheduled_attack_target')
        
        if self.is_moving:
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.walk_frames)
        else:
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
        # Spread gebaseerd op behavior
        if self.behavior == BehaviorType.DODGER:
            spread = 0.05  # Accurater
        else:
            spread = 0.15  # Meer spread
            
        target_x += random.uniform(-spread, spread)
        target_y += random.uniform(-spread, spread)
        
        bullet = EnemyBullet(
            self.x, self.y, target_x, target_y,
            self.damage, self.bullet_speed, self.bullet_color
        )
        self.projectiles.append(bullet)
        
    def _update_projectiles(self, dt):
        """Update alle kogels"""
        for proj in self.projectiles[:]:
            if proj.alive:
                proj.update(dt)
            else:
                self.projectiles.remove(proj)
                
    def _alert_nearby_enemies(self, enemy_manager):
        """Waarschuw vijanden in de buurt"""
        alert_range = 6.0
        for enemy in enemy_manager.enemies:
            if enemy is self or not enemy.alive:
                continue
            if enemy.state in [EnemyState.DEAD, EnemyState.DYING]:
                continue
                
            dx = enemy.x - self.x
            dy = enemy.y - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist < alert_range:
                if enemy.state in [EnemyState.IDLE, EnemyState.PATROL]:
                    enemy._change_state(EnemyState.ALERT)
                    enemy.is_alerted = True
                    enemy.last_known_player_x = self.last_known_player_x
                    enemy.last_known_player_y = self.last_known_player_y
                
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
        
    def get_melee_damage(self, player_x, player_y):
        """Check melee damage voor charger vijanden"""
        if self.behavior != BehaviorType.CHARGER:
            return 0
        if self.state != EnemyState.ATTACK:
            return 0
            
        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist < self.min_attack_range + 0.3:
            return self.damage
        return 0
                
    def can_move_to(self, x, y, door_manager=None):
        """Check of vijand naar positie kan bewegen met collision radius"""
        # Collision radius - hoe breed de vijand is
        collision_radius = 0.3
        
        # Check meerdere punten rond de vijand voor betere collision
        check_points = [
            (x, y),  # Midden
            (x - collision_radius, y),  # Links
            (x + collision_radius, y),  # Rechts
            (x, y - collision_radius),  # Boven
            (x, y + collision_radius),  # Onder
            (x - collision_radius, y - collision_radius),  # Links-boven
            (x + collision_radius, y - collision_radius),  # Rechts-boven
            (x - collision_radius, y + collision_radius),  # Links-onder
            (x + collision_radius, y + collision_radius),  # Rechts-onder
        ]
        
        for check_x, check_y in check_points:
            if is_wall(int(check_x), int(check_y)):
                return False
            if is_door(int(check_x), int(check_y)):
                if door_manager:
                    if not door_manager.can_pass(check_x, check_y):
                        return False
                else:
                    return False
        return True
        
    def take_damage(self, damage, attacker_x=None, attacker_y=None):
        """Neem schade met knockback en stagger"""
        if not self.alive or self.state in [EnemyState.DEAD, EnemyState.DYING]:
            return False
            
        self.health -= damage
        self.is_alerted = True
        
        # Knockback berekening
        if attacker_x is not None and attacker_y is not None:
            dx = self.x - attacker_x
            dy = self.y - attacker_y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 0:
                self.knockback_x = (dx / dist) * self.knockback_force
                self.knockback_y = (dy / dist) * self.knockback_force
        
        if self.health <= 0:
            self.health = 0
            self._change_state(EnemyState.DYING)
            return True
        else:
            # Stagger
            self._change_state(EnemyState.HURT)
            return False
            
    def get_drop(self):
        """Genereer een drop bij dood"""
        # Bepaal drop type met kansen
        roll = random.random()
        
        if roll < 0.10:  # 10% health pack
            return EnemyDrop(self.x, self.y, 'health_pack')
        elif roll < 0.35:  # 25% health
            return EnemyDrop(self.x, self.y, 'health')
        elif roll < 0.70:  # 35% ammo
            return EnemyDrop(self.x, self.y, 'ammo')
        else:
            return None  # 30% geen drop
            
    def apply_difficulty_scaling(self, level):
        """Pas difficulty scaling toe gebaseerd op level (gebalanceerd)"""
        # Elke level verhoogt stats - health schaalt meer dan damage
        health_scaling = 1.0 + (level - 1) * 0.12  # 12% health per level
        damage_scaling = 1.0 + (level - 1) * 0.08  # 8% damage per level (minder agressief)
        
        self.health = int(self.health * health_scaling)
        self.max_health = int(self.max_health * health_scaling)
        self.damage = int(self.damage * damage_scaling)
        
        # Speed scaling is minder agressief
        speed_scaling = 1.0 + (level - 1) * 0.05  # 5% per level
        self.speed = self.base_speed * speed_scaling
        
        # Fire rate wordt iets sneller (maar niet te veel)
        if self.fire_rate > 0:
            self.fire_rate = int(self.fire_rate / (1 + (level - 1) * 0.05))
        
    def get_sprite(self):
        """Haal huidige sprite op met effecten"""
        if self.state == EnemyState.DEAD:
            return self.sprite_dead
            
        if self.state == EnemyState.DYING:
            # Fade effect
            sprite = self.sprite_dead.copy()
            sprite.set_alpha(self.death_alpha)
            return sprite
            
        if self.state == EnemyState.HURT:
            return self.sprite_hurt
            
        # Telegraph effect - glow/pulse
        base_sprite = self.walk_frames[self.current_frame]
        
        if self.is_telegraphing:
            # Rode glow tijdens telegraph
            telegraph_sprite = base_sprite.copy()
            pulse = (math.sin(pygame.time.get_ticks() * 0.03) + 1) * 0.5
            overlay = pygame.Surface(telegraph_sprite.get_size(), pygame.SRCALPHA)
            overlay.fill((255, int(50 + pulse * 100), 50, int(100 + pulse * 50)))
            telegraph_sprite.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            return telegraph_sprite
            
        # Charger charge glow
        if self.is_charging and self.behavior == BehaviorType.CHARGER:
            charge_sprite = base_sprite.copy()
            overlay = pygame.Surface(charge_sprite.get_size(), pygame.SRCALPHA)
            overlay.fill((100, 100, 255, 80))
            charge_sprite.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            return charge_sprite
            
        # Dodger dodge glow
        if self.is_dodging and self.behavior == BehaviorType.DODGER:
            dodge_sprite = base_sprite.copy()
            overlay = pygame.Surface(dodge_sprite.get_size(), pygame.SRCALPHA)
            overlay.fill((150, 50, 200, 60))
            dodge_sprite.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            return dodge_sprite
            
        return base_sprite
        
    def get_sprite_with_health_bar(self):
        """Haal sprite op met health bar als beschadigd"""
        base = self.get_sprite()
        
        # Geen health bar voor dode vijanden of vol health
        if self.state in [EnemyState.DEAD, EnemyState.DYING]:
            return base
        if self.health >= self.max_health:
            return base
            
        # Maak kopie met health bar
        width = base.get_width()
        height = base.get_height()
        
        # Extra ruimte voor health bar boven sprite
        bar_height = 6
        bar_margin = 4
        new_height = height + bar_height + bar_margin
        
        result = pygame.Surface((width, new_height), pygame.SRCALPHA)
        result.blit(base, (0, bar_height + bar_margin))
        
        # Health bar
        bar_width = width - 10
        bar_x = 5
        bar_y = 2
        
        # Background
        pygame.draw.rect(result, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))
        
        # Health fill
        health_pct = self.health / self.max_health
        fill_width = int(bar_width * health_pct)
        
        # Kleur op basis van health
        if health_pct > 0.6:
            bar_color = (50, 200, 50)
        elif health_pct > 0.3:
            bar_color = (200, 200, 50)
        else:
            bar_color = (200, 50, 50)
            
        pygame.draw.rect(result, bar_color, (bar_x, bar_y, fill_width, bar_height))
        
        # Border
        pygame.draw.rect(result, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), 1)
        
        return result
        
    def get_minimap_color(self):
        """Geef kleur voor minimap gebaseerd op state en behavior"""
        if self.state in [EnemyState.DEAD, EnemyState.DYING]:
            return None  # Niet tekenen
            
        # Basis kleur per behavior type
        if self.behavior == BehaviorType.CHARGER:
            base_color = (100, 150, 255)  # Blauw voor chargers
        elif self.behavior == BehaviorType.DODGER:
            base_color = (200, 100, 255)  # Paars voor dodgers
        else:
            base_color = (255, 100, 100)  # Rood voor ranged
            
        # Modifier per state
        if self.state == EnemyState.ALERT:
            # Geel voor alert
            return (255, 255, 100)
        elif self.state == EnemyState.CHASE or self.state == EnemyState.ATTACK:
            # Oranje voor actief agressief
            return (255, 150, 50)
        elif self.state == EnemyState.PATROL:
            # Donkerder voor patrol
            return tuple(max(0, c - 80) for c in base_color)
        elif self.state == EnemyState.IDLE:
            # Nog donkerder voor idle
            return tuple(max(0, c - 100) for c in base_color)
            
        return base_color
        
    @property
    def pos(self):
        return (self.x, self.y)


class Projectile:
    """Een projectiel geschoten door de boss - snel en dodelijk"""
    
    def __init__(self, x, y, target_x, target_y, damage=15, speed=0.025):
        self.x = x
        self.y = y
        self.damage = damage
        self.speed = speed
        self.alive = True
        self.hit_range = 0.5  # Kleinere hit range voor eerlijkere gameplay
        self.lifetime = 0
        self.max_lifetime = 8000
        
        dx = target_x - x
        dy = target_y - y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0:
            self.dir_x = dx / dist
            self.dir_y = dy / dist
        else:
            self.dir_x = 0
            self.dir_y = 1
            
        self.sprite = self._create_sprite()
        self.glow_pulse = 0
        
    def _create_sprite(self):
        """Maak grote vuurbal sprite"""
        size = 64
        sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2
        
        for r in range(6, 0, -1):
            alpha = 80 - r * 10
            pygame.draw.circle(sprite, (255, 80, 0, alpha), (cx, cy), 20 + r * 4)
        
        pygame.draw.circle(sprite, (255, 150, 30), (cx, cy), 18)
        pygame.draw.circle(sprite, (255, 200, 50), (cx, cy), 14)
        pygame.draw.circle(sprite, (255, 255, 100), (cx, cy), 10)
        pygame.draw.circle(sprite, (255, 255, 200), (cx, cy), 6)
        pygame.draw.circle(sprite, (255, 255, 255), (cx, cy), 3)
        
        return sprite
        
    def update(self, dt):
        if not self.alive:
            return
            
        self.lifetime += dt
        if self.lifetime > self.max_lifetime:
            self.alive = False
            return
            
        self.x += self.dir_x * self.speed * dt
        self.y += self.dir_y * self.speed * dt
        
        self.glow_pulse = (math.sin(pygame.time.get_ticks() * 0.02) + 1) * 0.5
            
        if is_wall(int(self.x), int(self.y)):
            self.alive = False
            
        return False
        
    def get_sprite(self):
        if not self.alive:
            return None
        
        size = 64
        animated = pygame.Surface((size, size), pygame.SRCALPHA)
        
        glow_alpha = int(50 + self.glow_pulse * 60)
        pygame.draw.circle(animated, (255, 100, 0, glow_alpha), (size//2, size//2), 28)
        
        animated.blit(self.sprite, (0, 0))
        return animated


class Boss(Enemy):
    """De eindbaas - verbeterde versie met fases en betere aanvallen"""
    
    # Boss fases met verschillende gedragingen
    PHASE_THRESHOLDS = [0.75, 0.50, 0.25]  # Health percentages voor fase transitions
    
    def __init__(self, x, y, is_final=False):
        super().__init__(x, y)
        
        self.color = 'boss'
        self.is_final_boss = is_final
        self.behavior = BehaviorType.BOSS
        
        if is_final:
            self.health = 800
            self.max_health = 800
            self.base_speed = 0.00096
            self.speed = self.base_speed
            self.damage = 18  # Melee damage (verlaagd)
            self.projectile_damage = 12  # Projectile damage (verlaagd)
            self.projectile_speed = 0.030  # Iets langzamer
        else:
            self.health = 500
            self.max_health = 500
            self.base_speed = 0.0008
            self.speed = self.base_speed
            self.damage = 15  # Melee damage (verlaagd)
            self.projectile_damage = 10  # Projectile damage (verlaagd)
            self.projectile_speed = 0.025  # Iets langzamer
            
        self.attack_range = 2.5
        self.attack_cooldown = 800
        
        # Ranged attack
        self.ranged_attack_range = 15.0
        self.ranged_cooldown = 1500
        self.last_ranged_attack = 0
        self.projectiles = []
        
        self.is_boss = True
        self.activation_range = 12.0
        self.detection_range = 15.0
        
        # Boss animatie
        self.walk_frames = create_boss_walk_frames()
        self.animation_speed = 200
        
        self.sprite_hurt = create_hurt_enemy_sprite(128)
        self.sprite_dead = create_dead_boss_sprite()
        
        # Fase systeem
        self.current_phase = 1
        self.phase_transition_timer = 0
        self.is_transitioning = False
        
        # Rage mode (fase 4)
        self.rage_mode = False
        self.rage_threshold = 0.3
        
        # Boss specifieke aanvallen per fase
        self.multi_shot_cooldown = 4000
        self.last_multi_shot = 0
        
        # Fase 2: Spin attack
        self.spin_attack_cooldown = 5000
        self.last_spin_attack = 0
        self.is_spinning = False
        self.spin_timer = 0
        self.spin_duration = 2000
        
        # Fase 3: Summon minions (conceptueel - spawnt extra projectielen)
        self.barrage_cooldown = 6000
        self.last_barrage = 0
        
        # Telegraph voor boss attacks
        self.boss_telegraph_duration = 400
        
    def update(self, dt, player, door_manager=None, enemy_manager=None):
        if self.state == EnemyState.DEAD:
            self._update_projectiles(dt)
            return
            
        if self.state == EnemyState.DYING:
            self._update_projectiles(dt)
            self._update_dying(dt)
            return
            
        current_time = pygame.time.get_ticks()
        
        # Check fase transitie
        self._check_phase_transition()
        
        # Update spin attack
        if self.is_spinning:
            self._update_spin_attack(dt, player)
            self._update_projectiles(dt)
            return
            
        # Afstand tot speler
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Activatie
        if distance < self.activation_range:
            self.is_activated = True
            if self.state == EnemyState.IDLE:
                self._change_state(EnemyState.ALERT)
                
        if not self.is_activated:
            self.is_moving = False
            return
            
        # Fase-specifieke aanvallen
        if distance > self.attack_range and distance < self.ranged_attack_range:
            if self._has_line_of_sight(player.x, player.y):
                self._execute_phase_attack(player, distance, current_time)
        
        self._update_projectiles(dt)
            
        # Normale enemy update voor beweging
        super().update(dt, player, door_manager, enemy_manager)
        
    def _check_phase_transition(self):
        """Check en voer fase transities uit"""
        health_pct = self.health / self.max_health
        
        new_phase = 1
        if health_pct <= 0.25:
            new_phase = 4  # Rage fase
        elif health_pct <= 0.50:
            new_phase = 3
        elif health_pct <= 0.75:
            new_phase = 2
            
        if new_phase > self.current_phase:
            self._transition_to_phase(new_phase)
            
    def _transition_to_phase(self, phase):
        """Transitie naar nieuwe fase met stat boosts"""
        self.current_phase = phase
        
        if phase == 2:
            # Fase 2: Sneller, spin attack unlocked
            self.speed = self.base_speed * 1.2
            self.ranged_cooldown = int(self.ranged_cooldown * 0.9)
        elif phase == 3:
            # Fase 3: Nog sneller, barrage attack
            self.speed = self.base_speed * 1.4
            self.ranged_cooldown = int(self.ranged_cooldown * 0.8)
            self.projectile_speed *= 1.2
        elif phase == 4:
            # Fase 4: Rage mode (gebalanceerd)
            self.rage_mode = True
            self.speed = self.base_speed * 1.6
            self.damage = int(self.damage * 1.2)  # Minder damage boost
            self.projectile_damage = int(self.projectile_damage * 1.2)  # Minder damage boost
            self.attack_cooldown = 500
            self.ranged_cooldown = 1000
            self.animation_speed = 120
            
    def _execute_phase_attack(self, player, distance, current_time):
        """Voer fase-specifieke aanval uit"""
        # Basis ranged attack
        if current_time - self.last_ranged_attack > self.ranged_cooldown:
            if self.current_phase >= 4 and current_time - self.last_multi_shot > self.multi_shot_cooldown:
                # Rage: Multi-shot
                self._fire_multi_shot(player.x, player.y)
                self.last_multi_shot = current_time
            elif self.current_phase >= 3 and current_time - self.last_barrage > self.barrage_cooldown:
                # Fase 3: Barrage attack
                self._fire_barrage(player.x, player.y)
                self.last_barrage = current_time
            else:
                self._fire_projectile(player.x, player.y)
            self.last_ranged_attack = current_time
            
        # Fase 2+: Spin attack
        if self.current_phase >= 2 and distance < 4.0:
            if current_time - self.last_spin_attack > self.spin_attack_cooldown:
                self._start_spin_attack()
                self.last_spin_attack = current_time
                
    def _start_spin_attack(self):
        """Start spin attack"""
        self.is_spinning = True
        self.spin_timer = 0
        
    def _update_spin_attack(self, dt, player):
        """Update spin attack - schiet in alle richtingen"""
        self.spin_timer += dt
        self.is_moving = False
        
        # Schiet elke 200ms in een andere richting
        spin_interval = 150 if self.rage_mode else 200
        shots_fired = int(self.spin_timer / spin_interval)
        
        if shots_fired > 0 and self.spin_timer % spin_interval < dt:
            # Schiet in huidige spin richting
            angle = (self.spin_timer / self.spin_duration) * math.pi * 4  # 2 volledige rotaties
            tx = self.x + math.cos(angle) * 10
            ty = self.y + math.sin(angle) * 10
            self._fire_projectile(tx, ty)
            
        if self.spin_timer >= self.spin_duration:
            self.is_spinning = False
            
    def _fire_barrage(self, target_x, target_y):
        """Schiet een barrage van projectielen"""
        # Snelle burst van 5 projectielen
        dx = target_x - self.x
        dy = target_y - self.y
        base_angle = math.atan2(dy, dx)
        
        for i in range(5):
            # Kleine variatie in richting en timing
            angle = base_angle + random.uniform(-0.2, 0.2)
            tx = self.x + math.cos(angle) * 10
            ty = self.y + math.sin(angle) * 10
            
            speed = self.projectile_speed * random.uniform(0.8, 1.2)
            proj = Projectile(self.x, self.y, tx, ty, self.projectile_damage, speed)
            self.projectiles.append(proj)
        
    def _fire_projectile(self, target_x, target_y):
        """Schiet een vuurbal"""
        speed = self.projectile_speed if not self.rage_mode else self.projectile_speed * 1.3
        proj = Projectile(self.x, self.y, target_x, target_y, 
                         self.projectile_damage, speed)
        self.projectiles.append(proj)
        
    def _fire_multi_shot(self, target_x, target_y):
        """Schiet meerdere vuurballen in een spread"""
        angles = [-0.3, 0, 0.3]
        if self.is_final_boss:
            angles = [-0.4, -0.2, 0, 0.2, 0.4]
            
        dx = target_x - self.x
        dy = target_y - self.y
        base_angle = math.atan2(dy, dx)
        
        for angle_offset in angles:
            angle = base_angle + angle_offset
            tx = self.x + math.cos(angle) * 10
            ty = self.y + math.sin(angle) * 10
            
            speed = self.projectile_speed if not self.rage_mode else self.projectile_speed * 1.3
            proj = Projectile(self.x, self.y, tx, ty, 
                             self.projectile_damage, speed)
            self.projectiles.append(proj)
        
    def _update_projectiles(self, dt):
        """Update alle projectielen"""
        for proj in self.projectiles[:]:
            if proj.alive:
                proj.update(dt)
            else:
                self.projectiles.remove(proj)
                
    def get_projectile_damage(self, player_x, player_y):
        """Check of een projectiel de speler raakt"""
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
        if self.state == EnemyState.DEAD:
            return self.sprite_dead
            
        if self.state == EnemyState.DYING:
            sprite = self.sprite_dead.copy()
            sprite.set_alpha(self.death_alpha)
            return sprite
            
        if self.state == EnemyState.HURT:
            return self.sprite_hurt
            
        base_sprite = self.walk_frames[self.current_frame]
        
        # Rage mode visual
        if self.rage_mode:
            rage_sprite = base_sprite.copy()
            pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1) * 0.5
            overlay = pygame.Surface(rage_sprite.get_size(), pygame.SRCALPHA)
            overlay.fill((255, int(50 + pulse * 50), 0, int(80 + pulse * 40)))
            rage_sprite.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            return rage_sprite
            
        return base_sprite
        
    def get_sprite_with_health_bar(self):
        """Boss sprite met grote health bar"""
        base = self.get_sprite()
        
        if self.state in [EnemyState.DEAD, EnemyState.DYING]:
            return base
        if self.health >= self.max_health:
            return base
            
        width = base.get_width()
        height = base.get_height()
        
        bar_height = 10  # Grotere bar voor boss
        bar_margin = 6
        new_height = height + bar_height + bar_margin
        
        result = pygame.Surface((width, new_height), pygame.SRCALPHA)
        result.blit(base, (0, bar_height + bar_margin))
        
        bar_width = width - 16
        bar_x = 8
        bar_y = 2
        
        pygame.draw.rect(result, (40, 20, 20), (bar_x, bar_y, bar_width, bar_height))
        
        health_pct = self.health / self.max_health
        fill_width = int(bar_width * health_pct)
        
        # Boss health bar kleur - rood/oranje
        if self.rage_mode:
            bar_color = (255, 100, 0)  # Oranje in rage
        elif health_pct > 0.5:
            bar_color = (200, 50, 50)
        else:
            bar_color = (255, 50, 50)
            
        pygame.draw.rect(result, bar_color, (bar_x, bar_y, fill_width, bar_height))
        pygame.draw.rect(result, (150, 50, 50), (bar_x, bar_y, bar_width, bar_height), 2)
        
        return result
        
    def get_minimap_color(self):
        """Boss minimap kleur"""
        if self.state in [EnemyState.DEAD, EnemyState.DYING]:
            return None
            
        if self.rage_mode:
            return (255, 100, 0)  # Oranje in rage
        return (255, 50, 50)  # Rood
        
    def get_drop(self):
        """Boss dropt altijd goede items"""
        drops = []
        # Boss dropt health pack + veel ammo
        drops.append(EnemyDrop(self.x - 0.3, self.y, 'health_pack'))
        drops.append(EnemyDrop(self.x + 0.3, self.y, 'ammo'))
        drops.append(EnemyDrop(self.x, self.y - 0.3, 'health'))
        return drops  # Return list voor boss


class DamageNumber:
    """Floating damage number voor visual feedback"""
    
    def __init__(self, x, y, damage, is_crit=False):
        self.x = x
        self.y = y
        self.damage = damage
        self.is_crit = is_crit
        self.lifetime = 0
        self.max_lifetime = 1000
        self.alive = True
        self.velocity_y = -0.002  # Float upward
        
        # Sprite
        self.font = pygame.font.Font(None, 36 if not is_crit else 48)
        self.color = (255, 255, 100) if not is_crit else (255, 50, 50)
        
    def update(self, dt):
        self.lifetime += dt
        self.y += self.velocity_y * dt
        
        if self.lifetime >= self.max_lifetime:
            self.alive = False
            
    def get_alpha(self):
        """Fade out effect"""
        if self.lifetime > self.max_lifetime * 0.5:
            return int(255 * (1 - (self.lifetime - self.max_lifetime * 0.5) / (self.max_lifetime * 0.5)))
        return 255


class EnemyDrop:
    """Item dat een vijand dropt bij dood"""
    
    DROP_TYPES = {
        'health': {'color': (50, 255, 50), 'value': 15, 'chance': 0.25},
        'ammo': {'color': (255, 200, 50), 'value': 10, 'chance': 0.35},
        'health_pack': {'color': (255, 100, 100), 'value': 1, 'chance': 0.10},
    }
    
    def __init__(self, x, y, drop_type='ammo'):
        self.x = x
        self.y = y
        self.drop_type = drop_type
        self.alive = True
        self.lifetime = 0
        self.max_lifetime = 15000  # 15 seconden voordat het verdwijnt
        self.pickup_range = 0.8
        self.bob_offset = 0
        
        drop_data = self.DROP_TYPES.get(drop_type, self.DROP_TYPES['ammo'])
        self.color = drop_data['color']
        self.value = drop_data['value']
        
        self.sprite = self._create_sprite()
        
    def _create_sprite(self):
        """Maak drop sprite"""
        size = 24
        sprite = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2
        
        if self.drop_type == 'health':
            # Groen kruis
            pygame.draw.rect(sprite, self.color, (cx - 2, cy - 8, 4, 16))
            pygame.draw.rect(sprite, self.color, (cx - 8, cy - 2, 16, 4))
            pygame.draw.rect(sprite, (100, 255, 100), (cx - 1, cy - 7, 2, 14))
        elif self.drop_type == 'ammo':
            # Gele kogels
            pygame.draw.ellipse(sprite, self.color, (cx - 6, cy - 8, 5, 16))
            pygame.draw.ellipse(sprite, self.color, (cx + 1, cy - 8, 5, 16))
            pygame.draw.ellipse(sprite, (255, 255, 150), (cx - 5, cy - 7, 3, 10))
        elif self.drop_type == 'health_pack':
            # Rode doos met kruis
            pygame.draw.rect(sprite, (200, 50, 50), (cx - 8, cy - 6, 16, 12))
            pygame.draw.rect(sprite, (255, 255, 255), (cx - 2, cy - 4, 4, 8))
            pygame.draw.rect(sprite, (255, 255, 255), (cx - 6, cy - 1, 12, 2))
            
        # Glow effect
        glow = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.color, 50), (cx, cy), 10)
        sprite.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        
        return sprite
        
    def update(self, dt):
        """Update drop"""
        self.lifetime += dt
        
        # Bob animatie
        self.bob_offset = math.sin(self.lifetime * 0.005) * 0.1
        
        # Fade out in laatste 3 seconden
        if self.lifetime > self.max_lifetime - 3000:
            # Knipperen
            if int(self.lifetime / 200) % 2 == 0:
                self.sprite.set_alpha(128)
            else:
                self.sprite.set_alpha(255)
        
        if self.lifetime >= self.max_lifetime:
            self.alive = False
            
    def try_pickup(self, player_x, player_y):
        """Check of speler de drop oppakt"""
        if not self.alive:
            return None
            
        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist < self.pickup_range:
            self.alive = False
            return {'type': self.drop_type, 'value': self.value}
            
        return None
        
    def get_sprite(self):
        return self.sprite if self.alive else None


class KillCombo:
    """Houdt kill combo's bij voor bonus rewards"""
    
    def __init__(self):
        self.combo_count = 0
        self.combo_timer = 0
        self.combo_timeout = 3000  # 3 seconden om combo te behouden
        self.max_combo = 0
        self.combo_multiplier = 1.0
        
        # Bonus thresholds
        self.thresholds = {
            3: {'name': 'TRIPLE KILL!', 'health_bonus': 5, 'ammo_bonus': 5},
            5: {'name': 'KILLING SPREE!', 'health_bonus': 10, 'ammo_bonus': 10},
            7: {'name': 'RAMPAGE!', 'health_bonus': 15, 'ammo_bonus': 15},
            10: {'name': 'UNSTOPPABLE!', 'health_bonus': 25, 'ammo_bonus': 20},
        }
        
    def add_kill(self):
        """Voeg een kill toe aan de combo"""
        self.combo_count += 1
        self.combo_timer = 0
        
        if self.combo_count > self.max_combo:
            self.max_combo = self.combo_count
            
        # Update multiplier
        self.combo_multiplier = 1.0 + (self.combo_count - 1) * 0.1
        
        # Check voor bonus
        bonus = None
        for threshold, reward in sorted(self.thresholds.items()):
            if self.combo_count == threshold:
                bonus = reward
                break
                
        return bonus
        
    def update(self, dt):
        """Update combo timer"""
        if self.combo_count > 0:
            self.combo_timer += dt
            if self.combo_timer >= self.combo_timeout:
                self.combo_count = 0
                self.combo_multiplier = 1.0
                
    def get_display_info(self):
        """Haal info op voor HUD display"""
        if self.combo_count < 2:
            return None
            
        time_left = max(0, self.combo_timeout - self.combo_timer) / 1000
        return {
            'count': self.combo_count,
            'multiplier': self.combo_multiplier,
            'time_left': time_left,
        }


class DamageIndicator:
    """Toont richting van inkomende schade"""
    
    def __init__(self):
        self.indicators = []  # List of {'angle': float, 'intensity': float, 'timer': int}
        self.duration = 1000  # 1 seconde zichtbaar
        
    def add_damage(self, player_x, player_y, player_angle, damage_x, damage_y, damage_amount):
        """Voeg damage indicator toe"""
        # Bereken hoek van schade relatief aan speler kijkrichting
        dx = damage_x - player_x
        dy = damage_y - player_y
        damage_angle = math.atan2(dy, dx)
        
        # Relatief aan speler kijkrichting
        relative_angle = damage_angle - player_angle
        
        # Normaliseer naar -pi tot pi
        while relative_angle > math.pi:
            relative_angle -= 2 * math.pi
        while relative_angle < -math.pi:
            relative_angle += 2 * math.pi
            
        # Intensity gebaseerd op damage
        intensity = min(1.0, damage_amount / 30)
        
        self.indicators.append({
            'angle': relative_angle,
            'intensity': intensity,
            'timer': 0,
        })
        
    def update(self, dt):
        """Update indicators"""
        for ind in self.indicators[:]:
            ind['timer'] += dt
            if ind['timer'] >= self.duration:
                self.indicators.remove(ind)
                
    def get_indicators(self):
        """Haal actieve indicators op voor rendering"""
        result = []
        for ind in self.indicators:
            alpha = 1.0 - (ind['timer'] / self.duration)
            result.append({
                'angle': ind['angle'],
                'intensity': ind['intensity'] * alpha,
            })
        return result


class EnemyManager:
    """Beheert alle vijanden met verbeterde feedback"""
    
    def __init__(self, level=1, custom_positions=None, boss_position=None, game_map=None, is_final_boss=False):
        self.enemies = []
        self.boss = None
        self.boss_spawned = False
        self.level = level
        self.game_map = game_map
        self.is_final_boss = is_final_boss
        
        # Feedback systemen
        self.damage_numbers = []
        self.drops = []
        self.kill_combo = KillCombo()
        self.damage_indicator = DamageIndicator()
        
        self.spawn_enemies(custom_positions, boss_position)
        
    def spawn_enemies(self, custom_positions=None, boss_position=None):
        """Spawn vijanden op aangegeven of standaard posities met difficulty scaling"""
        if custom_positions is not None:
            for i, (x, y) in enumerate(custom_positions):
                enemy_type = Enemy.ENEMY_TYPES[i % len(Enemy.ENEMY_TYPES)]
                enemy = Enemy(x, y, enemy_type)
                # Apply difficulty scaling
                enemy.apply_difficulty_scaling(self.level)
                self.enemies.append(enemy)
        else:
            if self.level == 1:
                self._spawn_level1_enemies()
            elif self.level == 2:
                self._spawn_boss_level()
                
        if boss_position:
            self.boss = Boss(boss_position[0], boss_position[1], is_final=self.is_final_boss)
            self.enemies.append(self.boss)
            
    def _spawn_level1_enemies(self):
        """Level 1 enemies (fallback)"""
        spawn_positions = [
            (2.5, 2.5), (21.5, 2.5),
            (7.5, 8.5), (16.5, 8.5), (7.5, 15.5), (16.5, 15.5),
            (11.5, 10.5), (12.5, 13.5),
        ]
        
        for i, (x, y) in enumerate(spawn_positions):
            enemy_type = Enemy.ENEMY_TYPES[i % len(Enemy.ENEMY_TYPES)]
            self.enemies.append(Enemy(x, y, enemy_type))
            
    def _spawn_boss_level(self):
        """Boss level (fallback)"""
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
        """Update alle vijanden en systemen"""
        for enemy in self.enemies:
            # Check of enemy net doodging voor drop
            was_dying = enemy.state == EnemyState.DYING
            enemy.update(dt, player, door_manager, self)
            
            # Check of vijand net dood is gegaan (state changed to DEAD)
            if was_dying and enemy.state == EnemyState.DEAD:
                # Genereer drop(s)
                drop_result = enemy.get_drop()
                if drop_result:
                    # Boss returns list, normale vijanden single drop
                    if isinstance(drop_result, list):
                        self.drops.extend(drop_result)
                    else:
                        self.drops.append(drop_result)
            
        # Update damage numbers
        for dn in self.damage_numbers[:]:
            dn.update(dt)
            if not dn.alive:
                self.damage_numbers.remove(dn)
                
        # Update drops
        for drop in self.drops[:]:
            drop.update(dt)
            if not drop.alive:
                self.drops.remove(drop)
                
        # Update kill combo
        self.kill_combo.update(dt)
        
        # Update damage indicator
        self.damage_indicator.update(dt)
                
    def add_damage_number(self, x, y, damage, is_crit=False):
        """Voeg damage number toe"""
        self.damage_numbers.append(DamageNumber(x, y, damage, is_crit))
        
    def register_kill(self):
        """Registreer een kill voor combo systeem"""
        return self.kill_combo.add_kill()
        
    def check_drop_pickups(self, player_x, player_y):
        """Check of speler drops oppakt"""
        pickups = []
        for drop in self.drops[:]:
            result = drop.try_pickup(player_x, player_y)
            if result:
                pickups.append(result)
        return pickups
        
    def add_damage_indicator(self, player_x, player_y, player_angle, damage_x, damage_y, damage_amount):
        """Voeg damage richting indicator toe"""
        self.damage_indicator.add_damage(player_x, player_y, player_angle, damage_x, damage_y, damage_amount)
            
    def get_enemy_at_ray(self, player_x, player_y, angle, max_distance=MAX_DEPTH):
        """Vind vijand in schietrichting met line-of-sight check"""
        sin_a = math.sin(angle)
        cos_a = math.cos(angle)
        
        sorted_enemies = []
        for enemy in self.enemies:
            if not enemy.alive or enemy.state in [EnemyState.DEAD, EnemyState.DYING]:
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
            
            hit_radius = 0.5 / distance if hasattr(enemy, 'is_boss') else 0.4 / distance
            
            if abs(delta) < hit_radius:
                # Check of er een vrije zichtlijn is (geen muren tussen speler en vijand)
                if self._has_clear_line_of_sight(player_x, player_y, enemy.x, enemy.y):
                    return enemy, distance
                
        return None, 0
    
    def _has_clear_line_of_sight(self, start_x, start_y, end_x, end_y):
        """Check of er geen muren zijn tussen twee punten"""
        dx = end_x - start_x
        dy = end_y - start_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < 0.1:
            return True
            
        # Meer stappen voor nauwkeurigere check
        steps = int(distance * 4)
        if steps < 2:
            steps = 2
            
        for i in range(1, steps):
            t = i / steps
            check_x = start_x + dx * t
            check_y = start_y + dy * t
            
            if is_wall(int(check_x), int(check_y)):
                return False
                
        return True
        
    def check_player_damage(self, player):
        """Check schade van alle vijandelijke aanvallen met damage indicator"""
        total_damage = 0
        
        for enemy in self.enemies:
            if not enemy.alive or enemy.state in [EnemyState.DEAD, EnemyState.DYING]:
                continue
                
            enemy_damage = 0
                
            # Kogel damage
            if hasattr(enemy, 'get_bullet_damage'):
                bullet_damage = enemy.get_bullet_damage(player.x, player.y)
                enemy_damage += bullet_damage
                
            # Melee damage (chargers)
            if hasattr(enemy, 'get_melee_damage'):
                melee_damage = enemy.get_melee_damage(player.x, player.y)
                enemy_damage += melee_damage
                    
            # Boss projectile damage
            if hasattr(enemy, 'is_boss') and hasattr(enemy, 'get_projectile_damage'):
                proj_damage = enemy.get_projectile_damage(player.x, player.y)
                enemy_damage += proj_damage
                
            # Voeg damage indicator toe als er schade is
            if enemy_damage > 0:
                self.add_damage_indicator(
                    player.x, player.y, player.angle,
                    enemy.x, enemy.y, enemy_damage
                )
                total_damage += enemy_damage
                    
        return total_damage
        
    def render(self, sprite_renderer):
        """Render alle vijanden met health bars en drops"""
        # Render drops eerst (achtergrond)
        for drop in self.drops:
            if drop.alive:
                drop_sprite = drop.get_sprite()
                if drop_sprite:
                    sprite_renderer.add_sprite(drop_sprite, drop.x, drop.y + drop.bob_offset, 0.15, 0.3)
        
        # Render vijanden
        for enemy in self.enemies:
            if enemy.state == EnemyState.DEAD:
                continue
                
            # Gebruik sprite met health bar voor beschadigde vijanden
            sprite = enemy.get_sprite_with_health_bar()
            
            if hasattr(enemy, 'is_boss'):
                if enemy.state != EnemyState.DYING:
                    scale = 0.6
                    y_offset = 0.30  # Iets hoger voor health bar
                else:
                    scale = 0.4
                    y_offset = 0.5
                    
                # Boss projectielen
                if hasattr(enemy, 'projectiles'):
                    for proj in enemy.projectiles:
                        if proj.alive:
                            proj_sprite = proj.get_sprite()
                            if proj_sprite:
                                sprite_renderer.add_sprite(proj_sprite, proj.x, proj.y, 0.4, 0.0)
            else:
                if enemy.state != EnemyState.DYING:
                    scale = 0.3
                    y_offset = 0.20  # Iets hoger voor health bar
                else:
                    scale = 0.2
                    y_offset = 0.4
                    
            # Kogels van alle vijanden
            if hasattr(enemy, 'projectiles'):
                for proj in enemy.projectiles:
                    if proj.alive:
                        proj_sprite = proj.get_sprite()
                        if proj_sprite:
                            bullet_scale = 0.15 if not hasattr(enemy, 'is_boss') else 0.4
                            sprite_renderer.add_sprite(proj_sprite, proj.x, proj.y, bullet_scale, 0.0)
                            
            sprite_renderer.add_sprite(sprite, enemy.x, enemy.y, scale, y_offset)
            
    @property
    def alive_count(self):
        return sum(1 for e in self.enemies if e.alive and e.state not in [EnemyState.DEAD, EnemyState.DYING])
    
    @property
    def boss_alive(self):
        return self.boss and self.boss.alive and self.boss.state not in [EnemyState.DEAD, EnemyState.DYING]
