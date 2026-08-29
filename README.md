# 🧟 ZOMBIE SURVIVAL

### Survive the Night. Slay the Horde.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)
![Pygame](https://img.shields.io/badge/Pygame-2.x-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-Personal%20Use-lightgrey?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

A fast-paced top-down zombie survival game built with **Pygame**.

Fight endless waves, unlock powerful classes, evolve your weapons, collect skins, climb the leaderboard, and play with friends in local multiplayer.

**Presented by Anton Savin Sibu**

---

## 🔥 Features

- Wave-based survival that gets harder the longer you live
- 8 unique classes with different playstyles and abilities
- Deep weapon progression (Pistol → Dual → Shotgun → SMG/RPG → Minigun → Flamethrower → Plasma)
- Orbit weapons that evolve (Knives → Axes → Katanas → Auto Guns)
- Upgrade system with rarity tiers (Common → Legendary)
- Character skins + Gun armory
- Account system, leaderboards, and persistent saves
- Local multiplayer (2–4 players)
- Laptop controls **and** Mobile-style on-screen controls

---

## 🎮 Controls

### Laptop Mode (Default)
| Action              | Input                  |
|---------------------|------------------------|
| Move                | `W` `A` `S` `D`        |
| Aim & Shoot         | Mouse + Left Click     |
| Class Power         | `Q`                    |
| Reaper Arts (Admin) | `Q` / `E` / `R`        |
| Pause               | `P` or `Esc`           |
| Choose Upgrade      | `1` `2` `3` or Click   |
| Reroll Upgrades     | `R` (costs coins)      |

### Menu Hotkeys
- `C` → Classes & Shop  
- `M` → Multiplayer  
- `L` / `Tab` → Leaderboard  

### Mobile Mode
On the main menu, click **MODE** to switch to on-screen joystick + buttons (great for touchscreen).

---

## 🧬 Classes

| Class        | Role         | Ability                          |
|--------------|--------------|----------------------------------|
| Survivor     | Vanguard     | Second Wind (heal + regen)       |
| Ninja        | Assassin     | Shadow Clone                     |
| Engineer     | Technician   | Auto Turret                      |
| Time Lord    | Chronomancer | Time Rewind + Freeze             |
| Frozen       | Cryomancer   | Strong freeze + Cryo Blast       |
| Scientist    | Alchemist    | Toxic potions + poison clouds    |
| Magician     | Illusionist  | Vanish (untouchable)             |
| Reaper       | Shinigami    | Katana + Admin Arts *(Admin only)* |

---

## 🌐 Multiplayer

1. One player runs the multiplayer server (`multiplayer_server.py` or `Multiplayer Server.exe`)
2. In game → **Multiplayer**
3. Host creates a room and gets a 6-character code
4. Friends join with the code
5. Host starts the match

**Difficulty modes:**
- Normal → 6 team lives  
- Hardcore → 3 team lives  
- Nightmare → 1 team life  

> Players must be on the same network (or use Hamachi / Radmin / port forwarding).

---

## 📦 What's Included

| File / Folder     | Description |
|-------------------|-------------|
| `zombie.py`       | Main game source |
| `skins.zip`       | Optional art previews (class / gun / katana skins) |
| `requirements.txt`| Python dependencies |

> **Note:** The game draws weapons and characters at runtime.  
> `skins.zip` contains exported preview images — it is optional.

---

## 🚀 How to Run

### From Source
```bash
# 1. Install Python 3.8+
# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the game
python zombie.py
```

### Build Windows .exe (optional)
```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name "Zombie Survival" zombie.py
```
The executable will appear in the `dist/` folder.

---

## 💾 Save Data

The game automatically creates:

- `zombie_accounts.json` → Accounts  
- `zombie_leaderboard.json` → High scores  
- `zombie_player_saves/` → Player progress & skins  

---

## 📌 Tips for New Players

- Start with **Survivor** (free and balanced)
- Prioritize **Damage**, **Fire Rate**, and **Armor** early
- Don’t ignore **Orbit Weapons** — they become very strong
- At Gun Level 3 you choose between **SMG** or **RPG**
- Wave 100 is a full boss gauntlet

---

## 👨‍💻 Credits

**Game Design & Programming**  
Anton Savin Sibu

**Engine**  
Pygame

---

<div align="center">

**Survive as long as you can.**  
**The horde never stops.**

⭐ Star the repo if you enjoy the game!

</div>
