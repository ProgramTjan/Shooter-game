# 🔥 DOOMIE

Een DOOM-achtige first-person shooter gemaakt in Python met raycasting.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.5+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🎮 Over het Spel

DOOMIE is een retro-style first-person shooter geïnspireerd door de klassieke DOOM (1993). Het spel gebruikt **raycasting** techniek om een 3D-achtige omgeving te renderen vanuit een 2D map, net zoals de originele DOOM engine.

### Features

- 🏛️ **Raycasting Engine** - Klassieke pseudo-3D rendering
- 🧱 **Procedurele Texturen** - Dynamisch gegenereerde muur texturen
- 🚪 **Interactieve Deuren** - Open en sluit deuren met animatie
- 👹 **Vijanden** - Verschillende demon types met AI
- 🔫 **Meerdere Wapens** - Pistool (snel) en Shotgun (krachtig)
- 🖱️ **Muis Besturing** - Moderne FPS controls met verticaal kijken
- 🗺️ **Minimap** - Overzicht van het level
- 💥 **Visuele Effecten** - Muzzle flash, hit markers, damage feedback

## 🚀 Installatie

### Vereisten

- Python 3.8 of hoger
- pip (Python package manager)

### Stappen

1. **Clone de repository**
   ```bash
   git clone https://github.com/ProgramTjan/Shooter-game.git
   cd Shooter-game
   ```

2. **Installeer dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start het spel**
   ```bash
   python main.py
   ```

## 🎯 Besturing

| Toets | Actie |
|-------|-------|
| `W` / `↑` | Vooruit |
| `S` / `↓` | Achteruit |
| `A` | Strafe links |
| `D` | Strafe rechts |
| `Muis` | Rondkijken |
| `Linker muisknop` / `SPACE` | Schieten |
| `1` | Pistool selecteren |
| `2` | Shotgun selecteren |
| `Q` | Wissel wapen |
| `E` | Open/sluit deur |
| `M` | Minimap toggle |
| `ESC` | Afsluiten |

## 🎮 Gameplay

- **Doel:** Elimineer alle vijanden om te winnen
- **Wapens:** 
  - *Pistool* - Snel vuren, lage schade
  - *Shotgun* - Langzaam, hoge schade
- **Vijanden:** Verschillende kleuren met unieke stats (health, snelheid, schade)
- **Deuren:** Druk `E` bij een deur om te openen

## 📁 Projectstructuur

```
Shooter-game/
├── main.py          # Hoofdbestand met game loop
├── player.py        # Speler beweging en controls
├── raycasting.py    # Raycasting engine
├── textures.py      # Procedurele textuur generatie
├── sprites.py       # Sprite rendering systeem
├── enemy.py         # Vijanden met AI
├── weapon.py        # Wapen systeem
├── door.py          # Deur mechaniek
├── map.py           # Level layout
├── settings.py      # Game configuratie
├── requirements.txt # Python dependencies
└── README.md        # Deze file
```

## 🛠️ Technologie

- **Python 3** - Programmeertaal
- **Pygame** - Game framework en rendering
- **NumPy** - Numerieke berekeningen

## 📖 Hoe werkt Raycasting?

Raycasting is een rendering techniek waarbij "rays" (stralen) worden geschoten vanuit het oogpunt van de speler. Voor elke verticale kolom op het scherm wordt een ray gecast om te bepalen:

1. Welke muur wordt geraakt
2. Op welke afstand
3. Welk deel van de textuur zichtbaar is

Dit creëert een 3D illusie terwijl de berekeningen relatief simpel blijven - perfect voor retro gaming!

## 🎨 Screenshots

*Game in actie met raycasted muren, vijanden en HUD*

## 📝 Toekomstige Features

- [ ] Meer levels
- [ ] Geluidseffecten
- [ ] Power-ups (health, ammo)
- [ ] Meer vijand types
- [ ] Boss fights
- [ ] Level editor

## 📄 Licentie

Dit project is gemaakt voor educatieve doeleinden.

---

*Gemaakt met ❤️ en Python*

