"""
Friendly Bot System - Een behulpzame bot per level
"""
import math
import pygame
from sprites import create_friendly_bot_sprite, create_friendly_bot_used_sprite


class FriendlyBot:
    """Vriendelijke bot die eenmalig hulp biedt"""
    
    def __init__(self, x, y, level_number=1, message=None, help_data=None):
        self.x = x
        self.y = y
        self.level_number = level_number
        self.message = message or "Stay alert, hunter."
        self.helped = False
        
        help_data = help_data or {}
        self.heal_amount = help_data.get('health', 15 + level_number * 5)
        self.ammo_amount = help_data.get('ammo', 20 + level_number * 5)
        self.health_packs = help_data.get('health_packs', 0)
        self.activation_range = help_data.get('range', 1.4)
        
        self.sprite_active = create_friendly_bot_sprite()
        self.sprite_used = create_friendly_bot_used_sprite()
        
        self.float_offset = 0.0
        self.float_phase = (x + y) * 0.6
        
    def update(self, dt, player, game):
        """Update animatie"""
        self.float_offset = math.sin(pygame.time.get_ticks() * 0.003 + self.float_phase) * 0.12
        
    def try_interact(self, player, game):
        """Probeer te interacteren met de bot"""
        if self.helped:
            return False
        
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < self.activation_range:
            self.helped = True
            self._apply_help(game)
            return True
            
        return False
            
    def _apply_help(self, game):
        """Geef hulp aan speler"""
        healed = min(self.heal_amount, game.player_max_health - game.player_health)
        if healed > 0:
            game.player_health += healed
            
        ammo_bonus = max(0, self.ammo_amount)
        if ammo_bonus > 0:
            game.weapons.add_ammo_all(ammo_bonus)
            
        if self.health_packs > 0:
            game.health_packs_inventory += self.health_packs
            
        bonus_parts = []
        if healed > 0:
            bonus_parts.append(f"+{healed} HP")
        if ammo_bonus > 0:
            bonus_parts.append(f"+{ammo_bonus} AMMO")
        if self.health_packs > 0:
            bonus_parts.append(f"+{self.health_packs} HEALTH PACK")
            
        bonus_text = " ".join(bonus_parts).strip()
        if bonus_text:
            full_message = f"BOT: {self.message} {bonus_text}"
        else:
            full_message = f"BOT: {self.message}"
            
        game.show_bot_message(full_message)
        
    def get_sprite(self):
        return self.sprite_used if self.helped else self.sprite_active
        
    @property
    def pos(self):
        return (self.x, self.y)


class FriendlyBotManager:
    """Beheert alle vriendelijke bots in een level"""
    
    def __init__(self, bot_data=None, level_number=1):
        self.bots = []
        
        if not bot_data:
            return
            
        if isinstance(bot_data, dict):
            bot_entries = [bot_data]
        else:
            bot_entries = bot_data
            
        for entry in bot_entries:
            position = entry.get('position')
            if not position:
                continue
            message = entry.get('message')
            help_data = entry.get('help', {})
            self.bots.append(FriendlyBot(position[0], position[1], level_number, message, help_data))
            
    def update(self, dt, player, game):
        for bot in self.bots:
            bot.update(dt, player, game)
            
    def render(self, sprite_renderer):
        for bot in self.bots:
            sprite = bot.get_sprite()
            sprite_renderer.add_sprite(sprite, bot.x, bot.y + bot.float_offset, 0.35, 0.25)
            
    def try_interact(self, player, game):
        for bot in self.bots:
            if bot.try_interact(player, game):
                return True
        return False
            
    def draw_minimap(self, screen, offset_x, offset_y, tile_size):
        for bot in self.bots:
            bx = offset_x + bot.x * tile_size
            by = offset_y + bot.y * tile_size
            color = (80, 200, 255) if not bot.helped else (100, 100, 100)
            pygame.draw.circle(screen, color, (int(bx), int(by)), 3)
