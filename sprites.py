"""
Sprite Systeem - Rendert 2D sprites in de 3D wereld
Met mensachtige vijanden en loopanimaties
"""
import pygame
import math
from settings import *


# Kleur schemes voor verschillende vijand types
ENEMY_COLORS = {
    'red': {
        'skin': (210, 160, 140),
        'shirt': (180, 40, 40),
        'pants': (60, 50, 50),
        'hair': (50, 30, 20),
        'boots': (40, 30, 25),
    },
    'green': {
        'skin': (180, 200, 160),
        'shirt': (40, 120, 40),
        'pants': (50, 60, 50),
        'hair': (30, 50, 30),
        'boots': (35, 45, 30),
    },
    'blue': {
        'skin': (200, 180, 170),
        'shirt': (40, 60, 160),
        'pants': (40, 40, 60),
        'hair': (30, 30, 50),
        'boots': (30, 30, 45),
    },
    'purple': {
        'skin': (200, 170, 190),
        'shirt': (120, 40, 140),
        'pants': (50, 40, 55),
        'hair': (60, 30, 70),
        'boots': (45, 30, 50),
    },
    'orange': {
        'skin': (220, 180, 150),
        'shirt': (200, 120, 40),
        'pants': (70, 55, 40),
        'hair': (100, 60, 30),
        'boots': (60, 45, 30),
    },
}


def create_humanoid_sprite(color_scheme='red', size=64, walk_frame=0):
    """
    Maak een mensachtige vijand sprite
    walk_frame: 0 = idle, 1 = walk left leg forward, 2 = walk right leg forward
    """
    sprite = pygame.Surface((size, size), pygame.SRCALPHA)
    
    s = size / 64  # Schaal factor
    cx = size // 2  # Center x
    
    colors = ENEMY_COLORS.get(color_scheme, ENEMY_COLORS['red'])
    
    # Arm/been posities gebaseerd op walk frame
    if walk_frame == 0:  # Idle
        left_arm_angle = 0
        right_arm_angle = 0
        left_leg_offset = 0
        right_leg_offset = 0
    elif walk_frame == 1:  # Links been voor
        left_arm_angle = 15
        right_arm_angle = -15
        left_leg_offset = 4
        right_leg_offset = -3
    else:  # Rechts been voor
        left_arm_angle = -15
        right_arm_angle = 15
        left_leg_offset = -3
        right_leg_offset = 4
    
    # === BENEN ===
    leg_width = int(7 * s)
    leg_height = int(18 * s)
    leg_y = int(44 * s)
    
    # Linker been
    left_leg_x = cx - int(8 * s)
    pygame.draw.rect(sprite, colors['pants'], 
                    (left_leg_x, leg_y + left_leg_offset * s, leg_width, leg_height))
    # Linker laars
    pygame.draw.rect(sprite, colors['boots'],
                    (left_leg_x - 1, leg_y + leg_height - int(4*s) + left_leg_offset * s, 
                     leg_width + 2, int(5*s)))
    
    # Rechter been
    right_leg_x = cx + int(1 * s)
    pygame.draw.rect(sprite, colors['pants'],
                    (right_leg_x, leg_y + right_leg_offset * s, leg_width, leg_height))
    # Rechter laars
    pygame.draw.rect(sprite, colors['boots'],
                    (right_leg_x - 1, leg_y + leg_height - int(4*s) + right_leg_offset * s,
                     leg_width + 2, int(5*s)))
    
    # === TORSO ===
    torso_width = int(22 * s)
    torso_height = int(20 * s)
    torso_x = cx - torso_width // 2
    torso_y = int(26 * s)
    
    # Shirt/torso
    pygame.draw.rect(sprite, colors['shirt'], (torso_x, torso_y, torso_width, torso_height))
    
    # Kraag detail
    collar_color = tuple(min(255, c + 30) for c in colors['shirt'])
    pygame.draw.rect(sprite, collar_color, (torso_x + int(6*s), torso_y, int(10*s), int(4*s)))
    
    # === ARMEN ===
    arm_width = int(6 * s)
    arm_length = int(16 * s)
    
    # Linker arm
    left_arm_x = torso_x - arm_width + 2
    left_arm_y = torso_y + int(2 * s) + int(left_arm_angle * 0.3 * s)
    pygame.draw.rect(sprite, colors['shirt'], (left_arm_x, left_arm_y, arm_width, arm_length))
    # Hand
    pygame.draw.circle(sprite, colors['skin'], 
                      (left_arm_x + arm_width // 2, left_arm_y + arm_length), int(3*s))
    
    # Rechter arm - omhoog gericht met wapen
    right_arm_x = torso_x + torso_width - 2
    right_arm_y = torso_y + int(2 * s)
    
    # Arm naar voren gericht (korter verticaal, meer naar voren)
    pygame.draw.rect(sprite, colors['shirt'], (right_arm_x, right_arm_y, arm_width, int(arm_length * 0.7)))
    # Onderarm naar voren
    forearm_x = right_arm_x + arm_width
    forearm_y = right_arm_y + int(arm_length * 0.5)
    pygame.draw.rect(sprite, colors['shirt'], (forearm_x - 2, forearm_y, int(10*s), arm_width))
    
    # Hand met wapen
    hand_x = forearm_x + int(8*s)
    hand_y = forearm_y + arm_width // 2
    pygame.draw.circle(sprite, colors['skin'], (hand_x, hand_y), int(3*s))
    
    # === WAPEN (Pistool/Gun) ===
    gun_color = (40, 40, 45)
    gun_highlight = (70, 70, 75)
    
    # Loop van het wapen (naar voren gericht)
    gun_x = hand_x + int(2*s)
    gun_y = hand_y - int(2*s)
    pygame.draw.rect(sprite, gun_color, (gun_x, gun_y, int(12*s), int(4*s)))  # Loop
    pygame.draw.rect(sprite, gun_highlight, (gun_x, gun_y, int(12*s), int(1*s)))  # Highlight
    
    # Handvat
    pygame.draw.rect(sprite, gun_color, (gun_x - int(2*s), gun_y + int(3*s), int(4*s), int(6*s)))
    
    # Vuurmond accent
    pygame.draw.rect(sprite, (60, 60, 65), (gun_x + int(10*s), gun_y, int(2*s), int(4*s)))
    
    # === HOOFD ===
    head_radius = int(10 * s)
    head_y = int(16 * s)
    
    # Haar (achter hoofd)
    hair_color = colors['hair']
    pygame.draw.circle(sprite, hair_color, (cx, head_y - int(2*s)), head_radius + int(2*s))
    
    # Hoofd/gezicht
    pygame.draw.circle(sprite, colors['skin'], (cx, head_y), head_radius)
    
    # Haar (boven op hoofd)
    pygame.draw.ellipse(sprite, hair_color, 
                       (cx - head_radius, head_y - head_radius - int(2*s), 
                        head_radius * 2, int(10*s)))
    
    # Ogen
    eye_offset = int(4 * s)
    eye_y = head_y - int(1 * s)
    eye_size = int(3 * s)
    
    # Wit van oog
    pygame.draw.circle(sprite, (255, 255, 255), (cx - eye_offset, eye_y), eye_size)
    pygame.draw.circle(sprite, (255, 255, 255), (cx + eye_offset, eye_y), eye_size)
    
    # Pupillen
    pupil_size = int(2 * s)
    pygame.draw.circle(sprite, (30, 30, 30), (cx - eye_offset, eye_y), pupil_size)
    pygame.draw.circle(sprite, (30, 30, 30), (cx + eye_offset, eye_y), pupil_size)
    
    # Wenkbrauwen (boos)
    brow_color = tuple(max(0, c - 30) for c in hair_color)
    pygame.draw.line(sprite, brow_color, 
                    (cx - eye_offset - int(3*s), eye_y - int(4*s)),
                    (cx - eye_offset + int(3*s), eye_y - int(3*s)), max(1, int(2*s)))
    pygame.draw.line(sprite, brow_color,
                    (cx + eye_offset + int(3*s), eye_y - int(4*s)),
                    (cx + eye_offset - int(3*s), eye_y - int(3*s)), max(1, int(2*s)))
    
    # Mond (grimas)
    mouth_y = head_y + int(5 * s)
    pygame.draw.arc(sprite, (100, 50, 50), 
                   (cx - int(4*s), mouth_y - int(2*s), int(8*s), int(4*s)),
                   3.14, 6.28, max(1, int(2*s)))
    
    return sprite


def create_enemy_walk_frames(color_scheme='red', size=64):
    """Genereer alle walk animation frames voor een vijand"""
    frames = []
    frames.append(create_humanoid_sprite(color_scheme, size, 0))  # Idle
    frames.append(create_humanoid_sprite(color_scheme, size, 1))  # Walk 1
    frames.append(create_humanoid_sprite(color_scheme, size, 0))  # Idle (midden)
    frames.append(create_humanoid_sprite(color_scheme, size, 2))  # Walk 2
    return frames


def create_enemy_sprite(color_scheme='red', size=64):
    """Backwards compatible - retourneer idle frame"""
    return create_humanoid_sprite(color_scheme, size, 0)


def create_boss_sprite(walk_frame=0):
    """Maak een grote boss sprite - imposante commandant"""
    size = 128
    sprite = pygame.Surface((size, size), pygame.SRCALPHA)
    
    s = size / 64
    cx = size // 2
    
    # Boss kleuren - donker en imposant
    colors = {
        'skin': (180, 140, 130),
        'armor': (50, 50, 60),
        'armor_highlight': (80, 80, 95),
        'cape': (120, 20, 30),
        'cape_dark': (80, 15, 20),
        'hair': (30, 25, 25),
        'boots': (35, 30, 30),
        'gold': (200, 170, 80),
    }
    
    # Walk animation offsets
    if walk_frame == 0:
        left_leg_offset = 0
        right_leg_offset = 0
        bob = 0
    elif walk_frame == 1:
        left_leg_offset = 5
        right_leg_offset = -4
        bob = -2
    else:
        left_leg_offset = -4
        right_leg_offset = 5
        bob = -2
    
    # === CAPE (achtergrond) ===
    cape_points = [
        (cx - int(20*s), int(25*s)),
        (cx + int(20*s), int(25*s)),
        (cx + int(25*s), int(58*s)),
        (cx - int(25*s), int(58*s)),
    ]
    pygame.draw.polygon(sprite, colors['cape'], cape_points)
    # Cape schaduw
    pygame.draw.polygon(sprite, colors['cape_dark'], [
        (cx, int(25*s)),
        (cx + int(25*s), int(58*s)),
        (cx, int(55*s)),
    ])
    
    # === BENEN ===
    leg_width = int(10 * s)
    leg_height = int(22 * s)
    leg_y = int(42 * s) + bob
    
    # Linker been (gepantserd)
    left_leg_x = cx - int(12 * s)
    pygame.draw.rect(sprite, colors['armor'], 
                    (left_leg_x, leg_y + left_leg_offset, leg_width, leg_height))
    pygame.draw.rect(sprite, colors['armor_highlight'],
                    (left_leg_x, leg_y + left_leg_offset, int(3*s), leg_height))
    # Laars
    pygame.draw.rect(sprite, colors['boots'],
                    (left_leg_x - 2, leg_y + leg_height - int(5*s) + left_leg_offset, 
                     leg_width + 4, int(7*s)))
    
    # Rechter been
    right_leg_x = cx + int(2 * s)
    pygame.draw.rect(sprite, colors['armor'],
                    (right_leg_x, leg_y + right_leg_offset, leg_width, leg_height))
    pygame.draw.rect(sprite, colors['armor_highlight'],
                    (right_leg_x, leg_y + right_leg_offset, int(3*s), leg_height))
    # Laars
    pygame.draw.rect(sprite, colors['boots'],
                    (right_leg_x - 2, leg_y + leg_height - int(5*s) + right_leg_offset,
                     leg_width + 4, int(7*s)))
    
    # === TORSO (gepantserd) ===
    torso_width = int(32 * s)
    torso_height = int(24 * s)
    torso_x = cx - torso_width // 2
    torso_y = int(22 * s) + bob
    
    # Borstplaat
    pygame.draw.rect(sprite, colors['armor'], (torso_x, torso_y, torso_width, torso_height))
    # Highlight
    pygame.draw.rect(sprite, colors['armor_highlight'], 
                    (torso_x, torso_y, int(8*s), torso_height))
    # Gouden details
    pygame.draw.rect(sprite, colors['gold'], 
                    (torso_x + int(12*s), torso_y + int(4*s), int(8*s), int(8*s)), 2)
    pygame.draw.line(sprite, colors['gold'],
                    (cx, torso_y), (cx, torso_y + torso_height), 2)
    
    # === ARMEN (gepantserd) ===
    arm_width = int(10 * s)
    arm_length = int(20 * s)
    
    # Schouderplaten
    pygame.draw.ellipse(sprite, colors['armor_highlight'],
                       (torso_x - int(6*s), torso_y - int(2*s), int(14*s), int(10*s)))
    pygame.draw.ellipse(sprite, colors['armor_highlight'],
                       (torso_x + torso_width - int(8*s), torso_y - int(2*s), int(14*s), int(10*s)))
    
    # Linker arm
    left_arm_x = torso_x - arm_width + 2
    left_arm_y = torso_y + int(6 * s)
    pygame.draw.rect(sprite, colors['armor'], (left_arm_x, left_arm_y, arm_width, arm_length))
    # Gauntlet
    pygame.draw.rect(sprite, colors['armor_highlight'],
                    (left_arm_x - 1, left_arm_y + arm_length - int(5*s), arm_width + 2, int(6*s)))
    
    # Rechter arm - naar voren gericht met wapen
    right_arm_x = torso_x + torso_width - 2
    right_arm_y = torso_y + int(6 * s)
    # Bovenarm
    pygame.draw.rect(sprite, colors['armor'], (right_arm_x, right_arm_y, arm_width, int(arm_length * 0.6)))
    
    # Onderarm naar voren (horizontaal)
    forearm_x = right_arm_x + arm_width
    forearm_y = right_arm_y + int(arm_length * 0.4)
    pygame.draw.rect(sprite, colors['armor'], (forearm_x - 2, forearm_y, int(14*s), arm_width))
    # Gauntlet
    pygame.draw.rect(sprite, colors['armor_highlight'],
                    (forearm_x + int(10*s), forearm_y - 1, int(5*s), arm_width + 2))
    
    # === DEMONISCH WAPEN (Grote vuurstaf/cannon) ===
    weapon_x = forearm_x + int(13*s)
    weapon_y = forearm_y + arm_width // 2
    
    # Wapen basis (donker metaal met rode gloed)
    weapon_color = (30, 25, 35)
    weapon_glow = (150, 40, 30)
    weapon_gold = colors['gold']
    
    # Hoofdloop
    pygame.draw.rect(sprite, weapon_color, (weapon_x, weapon_y - int(4*s), int(20*s), int(8*s)))
    
    # Gouden ringen
    pygame.draw.rect(sprite, weapon_gold, (weapon_x + int(3*s), weapon_y - int(5*s), int(3*s), int(10*s)))
    pygame.draw.rect(sprite, weapon_gold, (weapon_x + int(12*s), weapon_y - int(5*s), int(3*s), int(10*s)))
    
    # Vuurmond met gloed
    pygame.draw.rect(sprite, weapon_glow, (weapon_x + int(17*s), weapon_y - int(3*s), int(4*s), int(6*s)))
    pygame.draw.circle(sprite, (255, 100, 50), (weapon_x + int(20*s), weapon_y), int(3*s))
    
    # Demonic details
    pygame.draw.circle(sprite, weapon_glow, (weapon_x + int(8*s), weapon_y), int(2*s))
    
    # === HOOFD ===
    head_radius = int(14 * s)
    head_y = int(14 * s) + bob
    
    # Helm
    helm_color = colors['armor']
    pygame.draw.circle(sprite, helm_color, (cx, head_y), head_radius)
    
    # Gezicht opening
    pygame.draw.ellipse(sprite, colors['skin'],
                       (cx - int(8*s), head_y - int(4*s), int(16*s), int(14*s)))
    
    # Ogen (intens, rood glanzend)
    eye_offset = int(5 * s)
    eye_y = head_y
    pygame.draw.circle(sprite, (200, 50, 50), (cx - eye_offset, eye_y), int(4*s))
    pygame.draw.circle(sprite, (200, 50, 50), (cx + eye_offset, eye_y), int(4*s))
    pygame.draw.circle(sprite, (255, 150, 100), (cx - eye_offset, eye_y), int(2*s))
    pygame.draw.circle(sprite, (255, 150, 100), (cx + eye_offset, eye_y), int(2*s))
    
    # Helm hoorns/decoratie
    horn_color = colors['gold']
    pygame.draw.polygon(sprite, horn_color, [
        (cx - int(10*s), head_y - int(8*s)),
        (cx - int(15*s), head_y - int(18*s)),
        (cx - int(8*s), head_y - int(10*s)),
    ])
    pygame.draw.polygon(sprite, horn_color, [
        (cx + int(10*s), head_y - int(8*s)),
        (cx + int(15*s), head_y - int(18*s)),
        (cx + int(8*s), head_y - int(10*s)),
    ])
    
    # Gloeiende aura
    for r in range(3):
        alpha = 25 - r * 7
        glow = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (255, 50, 50, alpha),
                           (cx - int((25 + r*5)*s), int((15 + bob - r*3)*s),
                            int((50 + r*10)*s), int((50 + r*6)*s)))
        sprite.blit(glow, (0, 0))
    
    return sprite


def create_boss_walk_frames():
    """Genereer walk frames voor de boss"""
    frames = []
    frames.append(create_boss_sprite(0))
    frames.append(create_boss_sprite(1))
    frames.append(create_boss_sprite(0))
    frames.append(create_boss_sprite(2))
    return frames


def create_dead_enemy_sprite(color_scheme='red'):
    """Maak een dode mensachtige vijand sprite - liggend op de grond"""
    size = 64
    sprite = pygame.Surface((size, size), pygame.SRCALPHA)
    
    colors = ENEMY_COLORS.get(color_scheme, ENEMY_COLORS['red'])
    s = size / 64
    
    # Bloedplas
    pygame.draw.ellipse(sprite, (100, 20, 20), (int(5*s), int(45*s), int(54*s), int(16*s)))
    
    # Liggend lichaam (horizontaal)
    # Torso
    pygame.draw.ellipse(sprite, colors['shirt'], (int(15*s), int(42*s), int(34*s), int(14*s)))
    
    # Hoofd (op zij)
    head_x = int(10*s)
    head_y = int(48*s)
    pygame.draw.circle(sprite, colors['skin'], (head_x, head_y), int(8*s))
    pygame.draw.circle(sprite, colors['hair'], (head_x - int(2*s), head_y - int(3*s)), int(6*s))
    
    # X ogen
    pygame.draw.line(sprite, (50, 50, 50), (head_x - 2, head_y - 2), (head_x + 2, head_y + 2), 2)
    pygame.draw.line(sprite, (50, 50, 50), (head_x + 2, head_y - 2), (head_x - 2, head_y + 2), 2)
    
    # Benen (gestrekt)
    pygame.draw.rect(sprite, colors['pants'], (int(45*s), int(44*s), int(14*s), int(6*s)))
    pygame.draw.rect(sprite, colors['boots'], (int(56*s), int(44*s), int(5*s), int(6*s)))
    
    return sprite


def create_dead_boss_sprite():
    """Maak een dode boss sprite - gevallen krijger"""
    size = 128
    sprite = pygame.Surface((size, size), pygame.SRCALPHA)
    
    s = size / 64
    
    # Grote bloedplas
    pygame.draw.ellipse(sprite, (80, 15, 15), (int(10*s), int(50*s), int(108*s), int(25*s)))
    
    # Cape gespreid
    pygame.draw.ellipse(sprite, (80, 15, 20), (int(5*s), int(45*s), int(118*s), int(30*s)))
    
    # Gepantserd lichaam (liggend)
    armor_color = (40, 40, 50)
    pygame.draw.ellipse(sprite, armor_color, (int(25*s), int(52*s), int(78*s), int(18*s)))
    
    # Helm (op zij)
    pygame.draw.circle(sprite, armor_color, (int(20*s), int(58*s)), int(12*s))
    # Gouden hoorn gebroken
    pygame.draw.polygon(sprite, (150, 130, 60), [
        (int(15*s), int(50*s)),
        (int(8*s), int(45*s)),
        (int(18*s), int(52*s)),
    ])
    
    # X ogen (in helm opening)
    pygame.draw.line(sprite, (100, 30, 30), (int(17*s), int(55*s)), (int(23*s), int(61*s)), 2)
    pygame.draw.line(sprite, (100, 30, 30), (int(23*s), int(55*s)), (int(17*s), int(61*s)), 2)
    
    return sprite


def create_hurt_enemy_sprite(size=64):
    """Maak een gewonde vijand sprite (wit/rood flash) - mensachtig silhouet"""
    sprite = pygame.Surface((size, size), pygame.SRCALPHA)
    s = size / 64
    cx = size // 2
    
    flash_color = (255, 200, 200)
    
    # Benen
    pygame.draw.rect(sprite, flash_color, (cx - int(8*s), int(44*s), int(7*s), int(18*s)))
    pygame.draw.rect(sprite, flash_color, (cx + int(1*s), int(44*s), int(7*s), int(18*s)))
    
    # Torso
    pygame.draw.rect(sprite, flash_color, (cx - int(11*s), int(26*s), int(22*s), int(20*s)))
    
    # Armen
    pygame.draw.rect(sprite, flash_color, (cx - int(17*s), int(28*s), int(6*s), int(16*s)))
    pygame.draw.rect(sprite, flash_color, (cx + int(11*s), int(28*s), int(6*s), int(16*s)))
    
    # Hoofd
    pygame.draw.circle(sprite, flash_color, (cx, int(16*s)), int(10*s))
    
    return sprite


def create_friendly_bot_sprite(size=64, active=True):
    """Maak een vriendelijke hulp-bot sprite"""
    sprite = pygame.Surface((size, size), pygame.SRCALPHA)
    s = size / 64
    cx = size // 2
    
    # Kleuren
    body_color = (70, 130, 190) if active else (80, 80, 80)
    body_shadow = (50, 90, 130) if active else (60, 60, 60)
    accent = (120, 200, 255) if active else (120, 120, 120)
    eye_color = (80, 255, 200) if active else (120, 120, 120)
    
    # Schaduw / hover ring
    shadow_w = int(36 * s)
    shadow_h = int(10 * s)
    pygame.draw.ellipse(sprite, (0, 0, 0, 120), (cx - shadow_w // 2, int(52 * s), shadow_w, shadow_h))
    
    # Body
    body_w = int(32 * s)
    body_h = int(24 * s)
    body_x = cx - body_w // 2
    body_y = int(30 * s)
    pygame.draw.rect(sprite, body_color, (body_x, body_y, body_w, body_h), border_radius=int(6 * s))
    inner_pad = int(3 * s)
    pygame.draw.rect(sprite, body_shadow,
                     (body_x + inner_pad, body_y + inner_pad, body_w - inner_pad * 2, body_h - inner_pad * 2),
                     border_radius=int(5 * s))
    
    # Head
    head_w = int(26 * s)
    head_h = int(16 * s)
    head_x = cx - head_w // 2
    head_y = int(12 * s)
    pygame.draw.rect(sprite, body_color, (head_x, head_y, head_w, head_h), border_radius=int(6 * s))
    pygame.draw.rect(sprite, accent, (head_x + int(2 * s), head_y + int(2 * s),
                                     head_w - int(4 * s), head_h - int(4 * s)),
                     width=0, border_radius=int(4 * s))
    
    # Ogen
    eye_y = head_y + int(7 * s)
    eye_offset = int(6 * s)
    pygame.draw.circle(sprite, eye_color, (cx - eye_offset, eye_y), int(2 * s))
    pygame.draw.circle(sprite, eye_color, (cx + eye_offset, eye_y), int(2 * s))
    
    # Antenne
    antenna_y = head_y - int(6 * s)
    pygame.draw.line(sprite, accent, (cx, head_y), (cx, antenna_y), max(1, int(2 * s)))
    pygame.draw.circle(sprite, accent, (cx, antenna_y), int(3 * s))
    
    # Paneel op body
    panel_w = int(14 * s)
    panel_h = int(10 * s)
    panel_x = cx - panel_w // 2
    panel_y = body_y + int(6 * s)
    pygame.draw.rect(sprite, accent, (panel_x, panel_y, panel_w, panel_h), border_radius=int(3 * s))
    pygame.draw.line(sprite, body_color,
                    (panel_x + panel_w // 2, panel_y + int(2 * s)),
                    (panel_x + panel_w // 2, panel_y + panel_h - int(2 * s)), max(1, int(2 * s)))
    pygame.draw.line(sprite, body_color,
                    (panel_x + int(3 * s), panel_y + panel_h // 2),
                    (panel_x + panel_w - int(3 * s), panel_y + panel_h // 2), max(1, int(2 * s)))
    
    return sprite


def create_friendly_bot_used_sprite(size=64):
    """Maak een gedeactiveerde hulp-bot sprite"""
    return create_friendly_bot_sprite(size=size, active=False)


class SpriteRenderer:
    """Rendert sprites in de 3D wereld"""
    
    def __init__(self, game):
        self.game = game
        self.sprites_to_render = []
        
    def add_sprite(self, sprite_surface, x, y, scale=1.0, y_offset=0.0):
        """Voeg sprite toe aan render queue
        y_offset: verticale offset op scherm (positief = lager/naar vloer)
        """
        self.sprites_to_render.append({
            'surface': sprite_surface,
            'x': x,
            'y': y,
            'scale': scale,
            'y_offset': y_offset
        })
        
    def clear(self):
        """Leeg de render queue"""
        self.sprites_to_render = []
        
    def render(self, screen, player, raycaster):
        """Render alle sprites met depth sorting"""
        if not self.sprites_to_render:
            return
            
        sprite_data = []
        
        for sprite in self.sprites_to_render:
            dx = sprite['x'] - player.x
            dy = sprite['y'] - player.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < 0.5:
                continue
                
            sprite_angle = math.atan2(dy, dx)
            delta_angle = sprite_angle - player.angle
            
            while delta_angle > math.pi:
                delta_angle -= 2 * math.pi
            while delta_angle < -math.pi:
                delta_angle += 2 * math.pi
                
            if abs(delta_angle) > HALF_FOV + 0.3:
                continue
                
            sprite_data.append({
                'surface': sprite['surface'],
                'distance': distance,
                'delta_angle': delta_angle,
                'scale': sprite['scale'],
                'pitch': player.pitch,
                'y_offset': sprite.get('y_offset', 0.0)
            })
            
        sprite_data.sort(key=lambda s: s['distance'], reverse=True)
        
        for data in sprite_data:
            self.render_sprite(screen, data, raycaster)
            
    def render_sprite(self, screen, sprite_data, raycaster):
        """Render een enkele sprite"""
        distance = sprite_data['distance']
        delta_angle = sprite_data['delta_angle']
        surface = sprite_data['surface']
        scale = sprite_data['scale']
        pitch = sprite_data.get('pitch', 0)
        y_offset = sprite_data.get('y_offset', 0.0)
        
        screen_x = HALF_WIDTH + delta_angle * HALF_WIDTH / HALF_FOV
        
        sprite_height = (SCREEN_DIST / distance) * scale
        sprite_width = sprite_height * (surface.get_width() / surface.get_height())
        
        max_size = HEIGHT * 1.5
        if sprite_height > max_size:
            sprite_height = max_size
            sprite_width = sprite_height * (surface.get_width() / surface.get_height())
            
        if sprite_width > 0 and sprite_height > 0:
            try:
                scaled = pygame.transform.scale(surface, (int(sprite_width), int(sprite_height)))
            except:
                return
            
            # y_offset wordt geschaald op basis van afstand voor perspectief
            screen_y_offset = (y_offset * SCREEN_DIST / distance)
            
            x = screen_x - sprite_width / 2
            y = HALF_HEIGHT + pitch - sprite_height / 2 + screen_y_offset
            
            sprite_left = int(max(0, x))
            sprite_right = int(min(WIDTH, x + sprite_width))
            
            for col in range(sprite_left, sprite_right):
                ray_idx = int((col / WIDTH) * NUM_RAYS)
                if 0 <= ray_idx < len(raycaster.ray_results):
                    wall_depth = raycaster.ray_results[ray_idx]['depth']
                    if distance < wall_depth:
                        src_x = int((col - x) / sprite_width * surface.get_width())
                        src_x = max(0, min(surface.get_width() - 1, src_x))
                        
                        col_surface = scaled.subsurface((int(col - x), 0, 1, int(sprite_height)))
                        
                        fog_factor = min(1, distance / MAX_DEPTH)
                        if fog_factor > 0.1:
                            # Maak een kopie om de originele sprite niet aan te passen
                            col_surface = col_surface.copy()
                            # Pas fog alleen toe op niet-transparante pixels
                            # door BLEND_RGBA_MULT te gebruiken
                            fog_surf = pygame.Surface((1, int(sprite_height)), pygame.SRCALPHA)
                            darkness = int(255 * (1 - fog_factor * 0.6))
                            fog_surf.fill((darkness, darkness, darkness, 255))
                            col_surface.blit(fog_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                        
                        screen.blit(col_surface, (col, y))
