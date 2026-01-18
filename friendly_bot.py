"""
Friendly Bot System - Een behulpzame bot per level
Requires player interaction (E key) to activate
"""
import math
import pygame
from sprites import create_friendly_bot_sprite, create_friendly_bot_used_sprite
from settings import WIDTH, HEIGHT, HALF_WIDTH, HALF_HEIGHT


class FriendlyBot:
    """Vriendelijke bot die eenmalig hulp biedt via interactie"""
    
    def __init__(self, x, y, level_number=1, message=None, help_data=None):
        self.x = x
        self.y = y
        self.level_number = level_number
        self.message = message or "Stay alert, hunter."
        self.helped = False
        self.in_range = False  # Is speler dichtbij genoeg voor interactie?
        
        help_data = help_data or {}
        self.heal_amount = help_data.get('health', 15 + level_number * 5)
        self.ammo_amount = help_data.get('ammo', 20 + level_number * 5)
        self.health_packs = help_data.get('health_packs', 0)
        self.interaction_range = help_data.get('range', 2.0)  # Iets groter voor interactie
        
        self.sprite_active = create_friendly_bot_sprite()
        self.sprite_used = create_friendly_bot_used_sprite()
        
        self.float_offset = 0.0
        self.float_phase = (x + y) * 0.6
        
    def update(self, dt, player):
        """Update animatie en range check"""
        self.float_offset = math.sin(pygame.time.get_ticks() * 0.003 + self.float_phase) * 0.12
        
        if self.helped:
            self.in_range = False
            return
            
        # Check of speler in interactie range is
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        self.in_range = distance < self.interaction_range
        
    def try_interact(self, game):
        """Probeer te interacteren met de bot - returns True als succesvol"""
        if self.helped or not self.in_range:
            return False
            
        self.helped = True
        self._apply_help(game)
        return True
            
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
            
        # Bouw bonus tekst
        bonus_parts = []
        if healed > 0:
            bonus_parts.append(f"+{healed} HP")
        if ammo_bonus > 0:
            bonus_parts.append(f"+{ammo_bonus} AMMO")
        if self.health_packs > 0:
            bonus_parts.append(f"+{self.health_packs} HEALTH PACK")
            
        bonus_text = "  |  ".join(bonus_parts)
        
        # Toon prominente bot dialoog
        game.show_bot_dialogue(self.message, bonus_text)
        
    def get_sprite(self):
        return self.sprite_used if self.helped else self.sprite_active
        
    @property
    def pos(self):
        return (self.x, self.y)


class FriendlyBotManager:
    """Beheert alle vriendelijke bots in een level"""
    
    def __init__(self, bot_data=None, level_number=1):
        self.bots = []
        self.show_interact_prompt = False
        
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
            
    def update(self, dt, player):
        """Update alle bots en check voor interact prompt"""
        self.show_interact_prompt = False
        for bot in self.bots:
            bot.update(dt, player)
            if bot.in_range and not bot.helped:
                self.show_interact_prompt = True
                
    def try_interact(self, game):
        """Probeer te interacteren met een bot in range"""
        for bot in self.bots:
            if bot.try_interact(game):
                return True
        return False
            
    def render(self, sprite_renderer):
        for bot in self.bots:
            sprite = bot.get_sprite()
            sprite_renderer.add_sprite(sprite, bot.x, bot.y + bot.float_offset, 0.35)
            
    def draw_interact_prompt(self, screen, font):
        """Teken de 'Press E to interact' prompt als een bot in range is"""
        if not self.show_interact_prompt:
            return
            
        current_time = pygame.time.get_ticks()
        
        # Pulserende achtergrond
        pulse = abs(math.sin(current_time * 0.005))
        bg_alpha = int(150 + pulse * 50)
        
        # Prompt tekst
        prompt_text = "[ E ] TALK TO FRIENDLY BOT"
        
        # Maak de prompt surface
        text_surf = font.render(prompt_text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(HALF_WIDTH, HEIGHT - 150))
        
        # Achtergrond met glow effect
        padding_x, padding_y = 25, 12
        bg_rect = pygame.Rect(
            text_rect.x - padding_x,
            text_rect.y - padding_y,
            text_rect.width + padding_x * 2,
            text_rect.height + padding_y * 2
        )
        
        # Glow border
        glow_color = (80, 200, 255)
        
        # Donkere achtergrond
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill((10, 25, 40, bg_alpha))
        screen.blit(bg_surface, (bg_rect.x, bg_rect.y))
        
        # Pulserende border
        pygame.draw.rect(screen, (glow_color[0], glow_color[1], glow_color[2]), bg_rect, 3, border_radius=8)
        
        # Inner glow
        inner_rect = bg_rect.inflate(-6, -6)
        pygame.draw.rect(screen, (glow_color[0]//2, glow_color[1]//2, glow_color[2]//2), inner_rect, 1, border_radius=6)
        
        # Tekst
        screen.blit(text_surf, text_rect)
        
        # Kleine indicator pijl
        arrow_y = text_rect.bottom + 8 + int(pulse * 5)
        pygame.draw.polygon(screen, glow_color, [
            (HALF_WIDTH, arrow_y + 10),
            (HALF_WIDTH - 8, arrow_y),
            (HALF_WIDTH + 8, arrow_y)
        ])
            
    def draw_minimap(self, screen, offset_x, offset_y, tile_size):
        for bot in self.bots:
            bx = offset_x + bot.x * tile_size
            by = offset_y + bot.y * tile_size
            color = (80, 200, 255) if not bot.helped else (100, 100, 100)
            pygame.draw.circle(screen, color, (int(bx), int(by)), 3)
