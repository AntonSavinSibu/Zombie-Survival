import pygame
import math
import random
import sys
import json
import socket
import threading
import hashlib
import os
import re
import time


# =========================================================
# ACCOUNT SYSTEM
# =========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ACCOUNTS_FILE = os.path.join(BASE_DIR, "zombie_accounts.json")
LEADERBOARD_FILE = os.path.join(BASE_DIR, "zombie_leaderboard.json")
SAVES_DIR = os.path.join(BASE_DIR, "zombie_player_saves")
ADMIN_USERNAME = "AntonXD"
ADMIN_PASSWORD_HASH = hashlib.sha256("antonisgood".encode("utf-8")).hexdigest()
ADMIN_TAG = "🧟ADMIN"           # line 1 above player
ADMIN_DISPLAY_NAME = "AntonXD"  # line 2 above player
ADMIN_TITLE = "🧟ADMIN  •  AntonXD"
admin_title_visible = True      # F7 toggles on/off
current_username = ""
is_admin = False
account_message = ""

# =========================================================
# AIMBOT / PLAYER NAME SETTINGS
# =========================================================
aimbot_enabled = False
admin_no_cooldown = False
aimbot_range = 700
aimbot_target_type = "nearest"

def _load_accounts():
    try:
        with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return {}

def _save_accounts(data):
    with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _password_hash(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def _ensure_admin_account():
    data = _load_accounts()
    changed = False
    if ADMIN_USERNAME not in data:
        data[ADMIN_USERNAME] = {"password": ADMIN_PASSWORD_HASH, "role": "admin"}
        changed = True
    elif data[ADMIN_USERNAME].get("role") != "admin":
        data[ADMIN_USERNAME]["role"] = "admin"
        changed = True
    if changed:
        _save_accounts(data)

def _account_save_path():
    os.makedirs(SAVES_DIR, exist_ok=True)
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", current_username or "player")
    return os.path.join(SAVES_DIR, safe + ".json")

def create_account(username, password):
    username = username.strip()
    if not username or len(username) > 20 or not password:
        return False, "Enter a username and password."
    data = _load_accounts()
    if username in data:
        return False, "Username already exists."
    data[username] = {"password": _password_hash(password), "role": "player"}
    _save_accounts(data)
    return True, "Account created."

def authenticate(username, password):
    data = _load_accounts()
    record = data.get(username)
    if not record or record.get("password") != _password_hash(password):
        return False
    return True

def login_screen():
    global current_username, is_admin
    _ensure_admin_account()

    mode = "login"
    username = ""
    password = ""
    focus = "username"
    show_password = False
    message = "WELCOME BACK"

    user_box = pygame.Rect(WIDTH // 2 - 200, 312, 400, 58)
    pass_box = pygame.Rect(WIDTH // 2 - 200, 400, 400, 58)
    action_box = pygame.Rect(WIDTH // 2 - 200, 484, 400, 58)
    switch_box = pygame.Rect(WIDTH // 2 - 200, 554, 400, 48)
    show_box = pygame.Rect(WIDTH // 2 + 140, 400, 58, 58)
    login_panel = pygame.Rect(226, 84, 648, 574)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if user_box.collidepoint(event.pos):
                    focus = "username"
                elif pass_box.collidepoint(event.pos) and not show_box.collidepoint(event.pos):
                    focus = "password"
                elif show_box.collidepoint(event.pos):
                    show_password = not show_password
                elif action_box.collidepoint(event.pos):
                    if mode == "create":
                        ok, msg = create_account(username, password)
                        message = msg
                        if ok:
                            mode = "login"
                            password = ""
                            focus = "username"
                    else:
                        if authenticate(username.strip(), password):
                            current_username = username.strip()
                            record = _load_accounts().get(current_username, {})
                            is_admin = record.get("role") == "admin"
                            if is_admin:
                                unlocked_characters.update(ADMIN_CLASSES)
                                unlocked_characters.add("Executor")
                            return
                        message = "INVALID USERNAME OR PASSWORD"
                elif switch_box.collidepoint(event.pos):
                    mode = "create" if mode == "login" else "login"
                    username = ""
                    password = ""
                    focus = "username"
                    show_password = False
                    message = "CREATE YOUR ACCOUNT" if mode == "create" else "WELCOME BACK"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F2:
                    mode = "create" if mode == "login" else "login"
                    username = password = ""
                    focus = "username"
                    show_password = False
                    message = "CREATE YOUR ACCOUNT" if mode == "create" else "WELCOME BACK"
                elif event.key == pygame.K_TAB:
                    focus = "password" if focus == "username" else "username"
                elif event.key == pygame.K_BACKSPACE:
                    if focus == "username":
                        username = username[:-1]
                    else:
                        password = password[:-1]
                elif event.key == pygame.K_RETURN:
                    if mode == "create":
                        ok, msg = create_account(username, password)
                        message = msg
                        if ok:
                            mode = "login"
                            password = ""
                            focus = "username"
                    else:
                        if authenticate(username.strip(), password):
                            current_username = username.strip()
                            record = _load_accounts().get(current_username, {})
                            is_admin = record.get("role") == "admin"
                            if is_admin:
                                unlocked_characters.update(ADMIN_CLASSES)
                                unlocked_characters.add("Executor")
                            return
                        message = "INVALID USERNAME OR PASSWORD"
                elif event.unicode and event.unicode.isprintable():
                    if focus == "username" and len(username) < 20 and not event.unicode.isspace():
                        username += event.unicode
                    elif focus == "password" and len(password) < 32:
                        password += event.unicode

        now = pygame.time.get_ticks()
        screen.fill((6, 8, 12))
        draw_zombie_bg(screen, now)
        draw_glass_panel(screen, login_panel, GOLD)
        center_text(screen, FONT_TITLE, "ZOMBIE SURVIVAL", (WIDTH // 2 + 3, 155), (44, 26, 6))
        center_text(screen, FONT_TITLE, "ZOMBIE SURVIVAL", (WIDTH // 2, 152), GOLD)
        center_text(screen, FONT_TINY, "SURVIVE THE NIGHT   •   SLAY THE HORDE",
                    (WIDTH // 2, 196), STONE_LIGHT)
        center_text(screen, FONT_TINY, "PRESENTED BY ANTON SAVIN SIBU",
                    (WIDTH // 2, 218), GOLD)
        pygame.draw.line(screen, _sh(GOLD, 0.55), (login_panel.x + 90, 216),
                         (login_panel.right - 90, 216), 2)
        tag = "CREATE ACCOUNT" if mode == "create" else "LOGIN"
        center_text(screen, FONT_BIG, tag, (WIDTH // 2, 250), WHITE)

        for rect, label, value, active in (
            (user_box, "USERNAME", username, focus == "username"),
            (pass_box, "PASSWORD", (password if show_password else "*" * len(password)), focus == "password"),
        ):
            center_text(screen, FONT_TINY, label, (rect.x + 52, rect.y - 19),
                        CYAN if active else STONE_LIGHT)
            if active:
                ring = pygame.Surface((rect.w + 20, rect.h + 20), pygame.SRCALPHA)
                for n in range(7, 0, -1):
                    f = (7 - n) / 7.0
                    pygame.draw.rect(ring, _sh(CYAN, 0.055 * (f ** 1.7) + 0.006),
                                     (10 - n * 1.3, 10 - n * 1.3, rect.w + n * 2.6, rect.h + n * 2.6),
                                     2, border_radius=9 + n)
                screen.blit(ring, (rect.x - 10, rect.y - 10), special_flags=pygame.BLEND_RGB_ADD)
            pygame.draw.rect(screen, (15, 18, 25), rect, border_radius=9)
            pygame.draw.rect(screen, (24, 29, 38), rect.inflate(-6, -6), border_radius=7)
            pygame.draw.rect(screen, CYAN if active else STONE, rect, 3, border_radius=9)
            screen.blit(FONT_SMALL.render(value, True, WHITE), (rect.x + 18, rect.y + 17))
            if active and (now // 500) % 2 == 0:
                caret = rect.x + 18 + FONT_SMALL.size(value)[0] + 2
                pygame.draw.line(screen, CYAN, (caret, rect.y + 15), (caret, rect.y + 43), 2)

        pygame.draw.rect(screen, (25, 30, 38), show_box, border_radius=8)
        pygame.draw.rect(screen, CYAN if show_password else STONE, show_box, 2, border_radius=8)
        center_text(screen, FONT_TINY, "SHOW", show_box.center, WHITE)

        draw_button(screen, action_box,
                    "CREATE ACCOUNT" if mode == "create" else "LOGIN",
                    action_box.collidepoint(pygame.mouse.get_pos()))
        draw_button(screen, switch_box,
                    "BACK TO LOGIN" if mode == "create" else "CREATE NEW ACCOUNT",
                    switch_box.collidepoint(pygame.mouse.get_pos()))

        msg_color = RED if "INVALID" in message or "already" in message.lower() else CYAN
        center_text(screen, FONT_TINY, message, (WIDTH // 2, 625), msg_color)
        center_text(screen, FONT_TINY, "TAB = SWITCH FIELD   •   ENTER = SUBMIT   •   F2 = TOGGLE MODE",
                    (WIDTH // 2, 665), STONE_LIGHT)
        pygame.display.flip()
        clock.tick(60)

pygame.init()

# ---- AUDIO (mono, safe, soft) ----
try:
    pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=1024)
except Exception:
    pass

import array as _array

_SR = 22050


def _clamp16(v):
    return int(max(-32767, min(32767, v)))


def _soft_env(i, n, attack=0.02, release=0.12):
    t = i / max(1, n - 1)
    a = min(0.25, attack)
    r = min(0.45, release)
    if t < a:
        return t / max(1e-6, a)
    if t > 1.0 - r:
        return max(0.0, (1.0 - t) / max(1e-6, r))
    return 1.0


def _buf_to_sound(samples, volume=1.0):
    """samples: list/iterable of float -1..1 -> mono Sound or None"""
    if not pygame.mixer.get_init():
        return None
    arr = _array.array("h")
    peak = 1e-6
    tmp = []
    for v in samples:
        tmp.append(v)
        if abs(v) > peak:
            peak = abs(v)
    scale = (volume * 32000.0) / peak
    for v in tmp:
        arr.append(_clamp16(v * scale))
    try:
        return pygame.mixer.Sound(buffer=arr)
    except Exception:
        return None


def _make_tone(freq, duration_ms, volume=0.22, wave="sine", attack=0.01, release=0.08):
    n = max(1, int(_SR * duration_ms / 1000.0))
    out = []
    for i in range(n):
        t = i / _SR
        env = _soft_env(i, n, attack, release)
        if wave == "noise":
            s = random.uniform(-1, 1) * 0.45
        elif wave == "thump":
            s = math.sin(2 * math.pi * freq * t * (1.0 - 0.45 * (i / n)))
            s += 0.3 * math.sin(2 * math.pi * (freq * 0.5) * t)
        elif wave == "piano":
            s = math.sin(2 * math.pi * freq * t)
            s += 0.4 * math.sin(2 * math.pi * freq * 2 * t) * math.exp(-t * 6)
            s += 0.15 * math.sin(2 * math.pi * freq * 3 * t) * math.exp(-t * 9)
            s *= 0.55
        else:
            s = math.sin(2 * math.pi * freq * t)
            s += 0.22 * math.sin(2 * math.pi * freq * 2.01 * t)
            s *= 0.8
        out.append(env * s)
    return _buf_to_sound(out, volume)


def _mix_tones(parts, duration_ms, volume=0.22):
    n = max(1, int(_SR * duration_ms / 1000.0))
    buf = [0.0] * n
    for freq, amp, wave in parts:
        for i in range(n):
            t = i / _SR
            env = _soft_env(i, n, 0.012, 0.18)
            if wave == "noise":
                s = random.uniform(-1, 1) * 0.35
            elif wave == "thump":
                s = math.sin(2 * math.pi * freq * t * (1.0 - 0.5 * (i / n)))
            else:
                s = math.sin(2 * math.pi * freq * t)
                s += 0.25 * math.sin(2 * math.pi * freq * 2 * t) * math.exp(-t * 5)
            buf[i] += amp * env * s
    return _buf_to_sound(buf, volume)


def _make_song_piano(notes, tempo=72, volume=0.12):
    beat = 60.0 / tempo
    out = []
    for freq, beats in notes:
        n = max(1, int(_SR * beat * beats))
        for i in range(n):
            t = i / _SR
            env = _soft_env(i, n, 0.03, 0.35)
            if freq <= 0:
                s = 0.0
            else:
                s = math.sin(2 * math.pi * freq * t)
                s += 0.4 * math.sin(2 * math.pi * freq * 2 * t) * math.exp(-t * 4.5)
                s += 0.14 * math.sin(2 * math.pi * freq * 3 * t) * math.exp(-t * 7)
                s += 0.07 * math.sin(2 * math.pi * (freq * 0.5) * t)
                s *= 0.5
            out.append(env * s)
    return _buf_to_sound(out, volume)


# Soft ambient intro (gentle piano)
_F3, _G3, _A3, _B3 = 174.61, 196.00, 220.00, 246.94
_C4, _Cs4, _D4, _E4, _F4, _Fs4, _G4, _A4, _B4 = 261.63, 277.18, 293.66, 329.63, 349.23, 369.99, 392.00, 440.00, 493.88
_C5, _Cs5, _D5, _E5, _F5, _Fs5, _G5, _A5, _B5 = 523.25, 554.37, 587.33, 659.25, 698.46, 739.99, 783.99, 880.00, 987.77

_INTRO_NOTES = [
    (_Fs4, 1.0), (_Cs5, 1.0), (_A4, 1.0), (_Cs5, 1.0),
    (_Fs4, 1.0), (_D5, 1.0), (_A4, 1.0), (_Cs5, 1.0),
    (_E4, 1.0), (_B4, 1.0), (_G4, 1.0), (_B4, 1.0),
    (_Fs4, 1.0), (_Cs5, 1.5), (0, 0.5),
    (_A4, 1.0), (_Cs5, 1.0), (_Fs5, 1.5), (_Cs5, 0.5),
    (_A4, 1.0), (_Fs4, 1.0), (_E4, 1.0), (_Fs4, 1.0),
    (_Cs4, 2.0), (_Fs4, 1.5), (0, 0.5),
    (_D4, 1.0), (_A4, 1.0), (_Fs4, 1.0), (_A4, 1.0),
    (_Cs4, 1.0), (_G4, 1.0), (_E4, 1.0), (_Fs4, 2.0),
    (0, 1.0),
]

_GAME_NOTES = [
    (_E4, 0.5), (_G4, 0.5), (_B4, 0.5), (_E5, 0.5),
    (_D5, 0.5), (_B4, 0.5), (_G4, 0.5), (_E4, 0.5),
    (_A4, 0.5), (_C5, 0.5), (_E5, 0.5), (_A5, 0.75),
    (0, 0.25), (_G4, 0.5), (_B4, 0.5), (_D5, 0.5), (_G5, 0.5),
    (_E5, 0.5), (_B4, 0.5), (_G4, 0.5), (_E4, 1.0),
    (_F4, 0.5), (_A4, 0.5), (_C5, 0.5), (_F5, 0.5),
    (_E5, 0.5), (_C5, 0.5), (_A4, 0.5), (_E4, 1.0),
    (0, 0.5),
]

SFX = {}
MUSIC = {"intro": None, "game": None}
_current_music = None
_music_channel = None


def init_audio():
    global SFX, MUSIC, _music_channel
    if not pygame.mixer.get_init():
        return
    try:
        pygame.mixer.set_num_channels(16)
        _music_channel = pygame.mixer.Channel(0)
    except Exception:
        _music_channel = None

    try:
        SFX = {
            "shoot": _mix_tones([(880, 0.7, "sine"), (440, 0.25, "sine")], 55, 0.16),
            "shoot_heavy": _mix_tones([(140, 0.9, "thump"), (90, 0.4, "sine")], 120, 0.28),
            "flame": _mix_tones([(70, 0.5, "noise"), (120, 0.35, "sine")], 90, 0.18),
            "hit": _mix_tones([(320, 0.7, "sine"), (160, 0.4, "thump")], 70, 0.22),
            "damage": _mix_tones([(200, 0.8, "thump"), (380, 0.35, "sine"), (90, 0.3, "noise")], 110, 0.26),
            "explode": _mix_tones([(60, 0.9, "thump"), (40, 0.5, "noise"), (120, 0.25, "sine")], 220, 0.3),
            "pickup": _mix_tones([(660, 0.5, "piano"), (990, 0.4, "piano")], 140, 0.18),
            "levelup": _mix_tones([(523, 0.5, "piano"), (659, 0.4, "piano"), (784, 0.45, "piano")], 280, 0.2),
            "hurt": _mix_tones([(110, 0.85, "thump"), (70, 0.4, "noise")], 160, 0.28),
            "click": _mix_tones([(720, 0.6, "sine")], 35, 0.12),
            "convert": _mix_tones([(523, 0.45, "piano"), (784, 0.4, "piano")], 160, 0.18),
        }
    except Exception:
        SFX = {}

    # Songs disabled — only SFX are used
    MUSIC["intro"] = None
    MUSIC["game"] = None


def play_sfx(name, volume=None):
    snd = SFX.get(name)
    if not snd:
        return
    try:
        if volume is not None:
            snd.set_volume(max(0.0, min(1.0, volume)))
        else:
            snd.set_volume(0.55)
        snd.play()
    except Exception:
        pass


def set_music(mode):
    """Background songs disabled — keep only sound effects."""
    global _current_music, _music_channel
    _current_music = None
    try:
        if _music_channel is not None:
            _music_channel.stop()
    except Exception:
        pass


init_audio()




# =========================================================
# VISUAL ASSETS / AIM ASSIST
# =========================================================
ASSET_DIR = os.path.join(BASE_DIR, "zombie_game_assets")
AIM_ASSIST = True
AIM_ASSIST_RANGE = 560
AIM_ASSIST_ANGLE = math.radians(24)

def _load_asset(name):
    path = os.path.join(ASSET_DIR, name)
    try:
        image = pygame.image.load(path).convert_alpha()
        return image
    except (pygame.error, FileNotFoundError):
        return None

GUN_ASSETS = {
    "pistol": _load_asset("pistol.png"),
    "dual_pistols": _load_asset("dual_pistols.png"),
    "shotgun": _load_asset("shotgun.png"),
    "rpg": _load_asset("rpg.png"),
}


# =========================================================
# SETTINGS
# =========================================================
WIDTH = 1100
HEIGHT = 700
FPS = 60

# Performance / soft caps (prevents lag spikes on Wave 100+)
MAX_ZOMBIES = 60
MAX_MINIONS = 32          # non-boss zombies
MAX_BULLETS = 80
MAX_ORBIT_BULLETS = 40
MAX_EXPLOSIONS = 14
MAX_POISON_CLOUDS = 12
MAX_MOON_WAVES = 14
MAX_MEDS = 14
MAX_SLASHES = 18

# Shared soft shadow (avoid allocating every frame per zombie)
_ZOMBIE_SHADOW = None
_PLAYER_SHADOW = None

# control_mode: "laptop" = WASD + mouse | "mobile" = on-screen stick + buttons
control_mode = "laptop"   # "laptop" or "mobile"

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF)
pygame.display.set_caption("ZOMBIE SURVIVAL — Presented by Anton Savin Sibu")
clock = pygame.time.Clock()

FONT_SMALL = pygame.font.SysFont("consolas", 20, bold=True)
FONT = pygame.font.SysFont("consolas", 28, bold=True)
FONT_BIG = pygame.font.SysFont("consolas", 50, bold=True)
FONT_HUGE = pygame.font.SysFont("consolas", 75, bold=True)
FONT_TITLE = pygame.font.SysFont("arialblack", 82, bold=True)
FONT_NAME = pygame.font.SysFont("arialblack", 34, bold=True)
FONT_ABILITY = pygame.font.SysFont("consolas", 20, bold=True)
FONT_TINY = pygame.font.SysFont("consolas", 16, bold=True)

# =========================================================
# COLORS
# =========================================================
BG = (22, 20, 30)
GRID = (38, 34, 48)
WHITE = (255, 255, 255)
BLACK = (10, 10, 10)

PLAYER_COLOR = (60, 160, 255)
SKIN = (245, 190, 135)
SKIN_DARK = (190, 125, 85)
HAIR = (55, 35, 25)
SHIRT = (50, 110, 210)
SHIRT_DARK = (30, 70, 145)
PANTS = (35, 45, 75)
BOOT = (45, 35, 30)

GUN_COLOR = (75, 75, 80)
GUN_DARK = (40, 40, 45)
METAL = (185, 185, 195)
BULLET_COLOR = (255, 220, 60)

ZOMBIE_COLOR = (75, 180, 75)
FAST_ZOMBIE_COLOR = (190, 120, 50)
TANK_COLOR = (120, 70, 160)
BOSS_COLOR = (220, 60, 70)

HEALTH_COLOR = (60, 210, 80)
XP_COLOR = (80, 150, 255)

WOOD = (126, 82, 45)
WOOD_DARK = (78, 48, 28)
WOOD_LIGHT = (160, 105, 55)
STONE = (85, 85, 85)
STONE_LIGHT = (120, 120, 120)
GOLD = (255, 210, 60)
GREEN = (80, 190, 80)
RED = (210, 65, 65)
BLUE = (70, 140, 220)
PURPLE = (150, 80, 190)
CYAN = (70, 220, 220)

# =========================================================
# PLAYER
# =========================================================
player_x = WIDTH // 2
player_y = HEIGHT // 2
player_speed = 5
max_health = 100
health = max_health

# =========================================================
# MAIN GUN
# =========================================================
gun_level = 1
damage = 25
bullet_speed = 14
bullet_size = 5
shoot_delay = 250
last_shot = 0
crit_chance = 0.08
crit_multiplier = 1.75
damage_reduction = 0.0
upgrade_rerolls = 1
upgrade_pick_count = 0

# --- upgrade-driven build stats ---
lifesteal = 0          # HP healed per kill
regen_amount = 0       # HP per regen tick
regen_timer = 0
pierce = 0             # extra zombies a bullet passes through
shrapnel = 0           # shrapnel burst level
thorns = 0             # damage reflected to attackers
freeze_chance = 0.0    # chance to freeze on hit
coin_bonus = 0.0
xp_bonus = 0.0
med_drop_chance = 0.22
# Final gun choices after Triple Shot.
has_smg = False
has_rpg = False

# =========================================================
# ORBIT WEAPON
# 0 knives -> 3 knives -> 4 axes -> 5 katanas -> 5 auto guns
# =========================================================
orbit_type = "none"
orbit_count = 0
orbit_angle = 0.0
orbit_radius = 78
orbit_speed = 0.055
orbit_damage = 18
orbit_hit_cooldowns = {}
orbit_trail = []
orbit_target_memory = {}

# Auto-gun orbit weapons have their own firing timer.
orbit_last_shot = 0
orbit_shoot_delay = 650
orbit_bullets = []
turret_bullets = []

# =========================================================
# XP / GAME
# =========================================================
xp = 0
level = 1
xp_needed = 100
wave = 1
score = 0
kills = 0
run_recorded = False
best_run_flags = (False, False)

zombies = []
bullets = []
explosions = []
power_fx = []  # power-use animations (75% transparent)
slashes = []            # katana slash arcs (Reaper class)
moon_waves = []         # MOON FANG crescent projectiles (admin Reaper)
storm_bolts = []         # Storm Sovereign lightning bolts
storm_domain_until = 0
admin_power_cd = {"q": 0, "e": 0, "r": 0, "f": 0}
bankai_until = 0
bankai_next = 0
werewolf_until = 0
werewolf_bonus = {}
executor_until = 0
executor_bonus = {}
meds = []

game_over = False
upgrade_screen = False
upgrade_options = []
gun_choice_screen = False
paused = False
intro_screen = True
character_screen = False
leaderboard_screen = False
friends_screen = False
friends_tab = 0
friend_search = ""
friend_message = ""
gift_amount = "20"
leaderboard_tab = 0
multiplayer_screen = False
selected_character = "Survivor"

# Multiplayer room connection. Run multiplayer_server.py and set SERVER_HOST.
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5050
mp_socket = None
mp_thread = None
mp_connected = False
mp_code = ""
mp_id = ""
mp_is_host = False
mp_status = ""
mp_started = False
mp_remote_players = {}
mp_send_timer = 0
mp_join_entry = False
mp_difficulty = "normal"
mp_team_lives = 6
mp_player_dead = False
mp_remote_dead_seen = set()

# Character powers
ability_cooldown = 0
ability_duration_until = 0
character_heal_timer = 0
shadow_clone = None
turret = None
poison_bombs = []
poison_clouds = []
crucifixes = []
# Time Lord rewind
time_history = []
TIME_HISTORY_MAX = 40
time_history_last = 0
rewind_fx_until = 0
rewind_active = False
rewind_path = []
rewind_index = 0
rewind_next = 0
rewind_target_hp = 0


CHARACTERS = {
    "Survivor": "Heals himself and stays balanced.",
    "Ninja": "Summons a Shadow Clone with 5 HP to fight.",
    "Engineer": "Places one automatic turret with 8 HP.",
    "Time Lord": "Slowly rewinds your body through time, then freezes the field.",
    "Frozen": "Has a 25% chance to freeze a zombie.",
    "Scientist": "Throws toxic potions that leave lasting poison smoke.",
    "Magician": "Disappears for 5 seconds.",
    "Reaper": "ADMIN CLASS. Slices zombies apart with a katana.",
    "Storm Sovereign": "ADMIN CLASS. Commands lightning, storms, and annihilation beams.",
    "Executor": "OP CLASS. 100M. Transform into Overlord Form and erase the horde.",
    "Priest": "Throws holy crucifixes. Zombies that touch them fight for you.",
}

# =========================================================
# CHARACTER SHOP / SAVE DATA
# =========================================================
CHARACTER_PRICES = {"Survivor": 0, "Ninja": 900, "Engineer": 9500, "Time Lord": 2200, "Frozen": 3600, "Scientist": 5200, "Magician": 7500, "Reaper": 0, "Storm Sovereign": 100000000, "Executor": 100000000, "Priest": 4800}
CHARACTER_ABILITIES = {
    "Survivor": ("SECOND WIND", "Heal 35 HP instantly."),
    "Ninja": ("SHADOW CLONE", "Summon a player-matching clone with 5 HP."),
    "Engineer": ("AUTO TURRET", "Place one turret. 8 HP, auto-fires, 30s cooldown."),
    "Time Lord": ("TIME REWIND", "Slow rewind 3s + restore HP + freeze zombies 4.5s."),
    "Frozen": ("CRYO BLAST", "Freeze nearby zombies for 3 seconds."),
    "Scientist": ("TOXIC POTION", "Hurl a vial that shatters into lingering poison smoke."),
    "Magician": ("VANISH", "Become untouchable for 5 seconds."),
    "Reaper": ("SHINIGAMI ARTS", "Q TEMPEST  •  E KUROSHIO  •  R BANKAI  •  F WEREWOLF"),
    "Storm Sovereign": ("STORM DECREE", "Q THUNDER  •  E CHAIN BOLT  •  R TEMPEST  •  F JUDGMENT"),
    "Executor": ("OVERLORD ARTS", "Q ERASURE  •  E JUDGMENT RAY  •  R OMEGA BURST  •  F OVERLORD FORM"),
    "Priest": ("HOLY ARTS", "Q CRUCIFIX mine  •  E HOLY WATER splash convert + ally berserk"),
}
CHARACTER_STATS = {
    "Survivor": {"hp": 115, "speed": 5.2, "damage": 1.00, "fire": 1.00, "armor": 0.04, "passive": "SECOND WIND: regenerates HP over time."},
    "Ninja": {"hp": 95, "speed": 6.4, "damage": 1.08, "fire": 0.92, "armor": 0.00, "passive": "SHADOW STEP: faster movement and stronger clone."},
    "Engineer": {"hp": 110, "speed": 4.9, "damage": 1.05, "fire": 0.96, "armor": 0.06, "passive": "TECH ARMOR: turret gets stronger every wave."},
    "Time Lord": {"hp": 110, "speed": 5.4, "damage": 1.10, "fire": 1.00, "armor": 0.04, "passive": "TEMPORAL CORE: slow rewind + freeze. Reduced cooldowns."},
    "Frozen": {"hp": 100, "speed": 5.0, "damage": 1.06, "fire": 0.98, "armor": 0.02, "passive": "CRYO CORE: stronger freeze chance."},
    "Scientist": {"hp": 100, "speed": 5.0, "damage": 1.12, "fire": 1.00, "armor": 0.02, "passive": "TOXIC LAB: potions leave deadly poison smoke clouds."},
    "Magician": {"hp": 90, "speed": 5.8, "damage": 1.10, "fire": 0.95, "armor": 0.00, "passive": "ARCANE VEIL: vanishing lasts longer."},
    "Reaper": {"hp": 130, "speed": 6.6, "damage": 1.30, "fire": 1.00, "armor": 0.10, "passive": "SOUL HARVEST: katana cleaves crowds and drains life."},
    "Storm Sovereign": {"hp": 160, "speed": 5.8, "damage": 1.55, "fire": 0.85, "armor": 0.14, "passive": "STORM CROWN: bullets shock nearby zombies. Lightning scales with wave."},
    "Executor": {"hp": 200, "speed": 5.2, "damage": 1.80, "fire": 0.80, "armor": 0.18, "passive": "EXECUTION MARK: kills refund 2% max HP. Overlord Form multiplies power."},
    "Priest": {"hp": 105, "speed": 5.1, "damage": 1.05, "fire": 1.00, "armor": 0.03, "passive": "SANCTIFY: converted zombies last longer and hit harder."},
}

CHARACTER_NAMES = list(CHARACTER_PRICES)
character_index = 0
coins = 0
gems = 0
unlocked_characters = {"Survivor"}
SAVE_FILE = os.path.join(BASE_DIR, "zombie_survival_save.json")

# =========================================================
# CLASSES, ROLES AND SKINS
# =========================================================
CLASS_ROLES = {
    "Survivor": "VANGUARD",
    "Ninja": "ASSASSIN",
    "Engineer": "TECHNICIAN",
    "Time Lord": "CHRONOMANCER",
    "Frozen": "CRYOMANCER",
    "Scientist": "ALCHEMIST",
    "Magician": "ILLUSIONIST",
    "Reaper": "SHINIGAMI",
    "Storm Sovereign": "STORM GOD",
    "Executor": "OVERLORD",
    "Priest": "EXORCIST",
}

# Classes only an admin account may see or select.
ADMIN_CLASSES = {"Reaper", "Storm Sovereign"}
# Classes that swing a blade instead of firing bullets.
MELEE_CLASSES = {"Reaper"}


def _dim(c, f):
    return (max(0, min(255, int(c[0] * f))), max(0, min(255, int(c[1] * f))),
            max(0, min(255, int(c[2] * f))))


def class_list():
    """Selectable classes; admin-only classes appear for admins only."""
    return [n for n in CHARACTER_NAMES if n not in ADMIN_CLASSES or is_admin]


def is_melee_class(name=None):
    return (name or selected_character) in MELEE_CLASSES


# ---------------------------------------------------------
# CLASS SKINS  (skin 0 is always the free default look)
# ---------------------------------------------------------
_SKIN_SPECS = {
    "Survivor": [("DESERT OPS", 1200, (222, 178, 80), (150, 132, 86), (96, 82, 52), None),
                 ("URBAN GHOST", 2600, (120, 200, 255), (72, 80, 92), (40, 46, 54), None)],
    "Ninja": [("CRIMSON SHINOBI", 1800, (255, 70, 70), (70, 20, 26), (38, 10, 14), None),
              ("JADE SHADOW", 3200, (80, 230, 150), (22, 52, 42), (10, 28, 22), None)],
    "Engineer": [("HAZARD YELLOW", 2000, (255, 220, 60), (214, 178, 40), (142, 112, 20), None),
                 ("CARBON RIG", 4200, (150, 160, 175), (54, 58, 66), (28, 30, 36), None)],
    "Time Lord": [("VOID CHRONO", 2400, (190, 120, 255), (48, 28, 86), (26, 14, 50), None),
                  ("SOLAR CHRONO", 4600, (255, 190, 70), (120, 72, 28), (70, 40, 14), None)],
    "Frozen": [("GLACIER", 2600, (180, 240, 255), (70, 130, 168), (36, 78, 108), None),
               ("OBSIDIAN FROST", 5000, (120, 220, 235), (32, 38, 46), (16, 20, 26), None)],
    "Scientist": [("BIOHAZARD", 3000, (140, 230, 90), (222, 240, 220), (150, 180, 148), None),
                  ("BLACK LAB", 5400, (255, 80, 80), (44, 46, 54), (24, 26, 32), None)],
    "Magician": [("BLOOD MAGE", 3400, (240, 60, 90), (92, 20, 44), (52, 10, 26), None),
                 ("ASTRAL MAGE", 6000, (110, 200, 255), (28, 54, 102), (14, 30, 62), None)],
    "Storm Sovereign": [
        ("STORM CROWN", 0, (120, 220, 255), (18, 28, 48), (8, 14, 28), (230, 240, 255)),
        ("THUNDER EMPEROR", 0, (255, 230, 80), (30, 28, 12), (14, 12, 6), (245, 235, 200)),
        ("VOID STORM", 0, (160, 80, 255), (16, 10, 32), (6, 4, 14), (210, 200, 240)),
        ("BLOOD THUNDER", 0, (255, 60, 80), (36, 8, 12), (18, 4, 6), (240, 200, 190)),
        ("ABSOLUTE ZERO", 0, (180, 255, 255), (12, 40, 50), (4, 18, 24), (220, 245, 255)),
    ],
    "Priest": [
        ("HOLY ORDER", 1800, (255, 230, 120), (230, 230, 240), (180, 180, 200), None),
        ("CARDINAL", 3200, (220, 40, 40), (40, 20, 30), (20, 8, 12), None),
        ("SAINT", 5000, (180, 230, 255), (240, 245, 255), (200, 210, 230), None),
    ],
    "Executor": [
        ("CRIMSON OVERLORD", 0, (255, 60, 40), (40, 12, 12), (18, 6, 6), (245, 220, 200)),
        ("GOLDEN EXECUTIONER", 0, (255, 210, 60), (50, 40, 10), (24, 18, 4), (250, 230, 190)),
        ("VOID SENTENCE", 0, (160, 80, 255), (16, 8, 28), (6, 4, 14), (220, 200, 240)),
        ("ABSOLUTE ZERO", 0, (100, 230, 255), (10, 24, 40), (4, 12, 20), (220, 240, 255)),
    ],
    "Reaper": [
        ("MOONLIGHT SHINIGAMI", 0, (140, 210, 255), (28, 34, 52), (14, 18, 30), (246, 220, 202)),
        ("HELLFIRE SHINIGAMI", 0, (255, 130, 60), (58, 24, 20), (30, 12, 10), (242, 208, 186)),
        ("VOID SHINIGAMI", 0, (160, 90, 255), (18, 12, 36), (8, 6, 18), (220, 200, 240)),
        ("BLOOD MOON SHINIGAMI", 0, (255, 40, 80), (42, 8, 16), (22, 4, 8), (240, 190, 180)),
        ("CELESTIAL SHINIGAMI", 0, (255, 230, 120), (40, 36, 70), (18, 16, 36), (250, 236, 210)),
        ("SHADOW EMPEROR", 0, (90, 255, 200), (10, 14, 18), (4, 6, 8), (200, 210, 220)),
        ("DRAGON SOUL SHINIGAMI", 0, (255, 90, 40), (48, 18, 12), (24, 8, 6), (245, 210, 180)),
        ("AURORA SHINIGAMI", 0, (80, 220, 255), (16, 40, 56), (8, 20, 28), (230, 245, 255)),
        ("VOID BLACK", 0, (255, 255, 255), (8, 8, 10), (0, 0, 0), (12, 12, 14)),
    ],
}

CLASS_SKINS = {}
for _cname in CHARACTER_PRICES:
    CLASS_SKINS[_cname] = [{"name": "STANDARD", "price": 0, "base": True}]
    for _sn, _sp, _acc, _suit, _suitd, _body in _SKIN_SPECS.get(_cname, []):
        CLASS_SKINS[_cname].append({"name": _sn, "price": _sp, "base": False,
                                    "accent": _acc, "suit": _suit, "suit_d": _suitd,
                                    "skin": _body})

# ---------------------------------------------------------
# GUN SKINS
# ---------------------------------------------------------
GUN_SKINS = [
    {"key": "steel", "name": "STANDARD STEEL", "price": 0,
     "steel_d": (44, 47, 54), "steel": (92, 98, 108), "steel_l": (150, 158, 170),
     "shine": (216, 222, 232), "poly": (32, 34, 40), "accent": (255, 210, 60),
     "wood": (132, 86, 46), "wood_l": (172, 118, 62)},
    {"key": "midnight", "name": "MIDNIGHT", "price": 1500,
     "steel_d": (24, 26, 34), "steel": (52, 58, 74), "steel_l": (96, 106, 130),
     "shine": (170, 186, 215), "poly": (18, 20, 26), "accent": (90, 160, 255),
     "wood": (46, 50, 64), "wood_l": (72, 78, 96)},
    {"key": "gold", "name": "GOLD RUSH", "price": 4000,
     "steel_d": (96, 66, 10), "steel": (186, 140, 30), "steel_l": (238, 200, 90),
     "shine": (255, 242, 190), "poly": (70, 50, 10), "accent": (255, 244, 200),
     "wood": (120, 80, 26), "wood_l": (170, 120, 44)},
    {"key": "toxic", "name": "TOXIC WASTE", "price": 6000,
     "steel_d": (24, 44, 26), "steel": (58, 116, 60), "steel_l": (110, 200, 110),
     "shine": (200, 255, 190), "poly": (18, 32, 20), "accent": (150, 255, 90),
     "wood": (50, 80, 40), "wood_l": (80, 120, 60)},
    {"key": "crimson", "name": "CRIMSON WAR", "price": 8500,
     "steel_d": (60, 14, 18), "steel": (148, 36, 42), "steel_l": (226, 88, 92),
     "shine": (255, 190, 190), "poly": (40, 10, 12), "accent": (255, 130, 100),
     "wood": (90, 30, 26), "wood_l": (130, 50, 42)},
    {"key": "plasma", "name": "PLASMA CORE", "price": 12000,
     "steel_d": (26, 20, 50), "steel": (72, 54, 140), "steel_l": (150, 120, 240),
     "shine": (220, 205, 255), "poly": (20, 16, 36), "accent": (120, 240, 255),
     "wood": (56, 40, 96), "wood_l": (86, 64, 140)},
    {"key": "ice", "name": "FROSTBITE", "price": 7500,
     "steel_d": (30, 70, 100), "steel": (90, 170, 210), "steel_l": (180, 230, 255),
     "shine": (230, 250, 255), "poly": (20, 40, 55), "accent": (120, 230, 255),
     "wood": (40, 70, 90), "wood_l": (70, 110, 130)},
    {"key": "ember", "name": "EMBER FORGE", "price": 9000,
     "steel_d": (70, 30, 15), "steel": (180, 80, 30), "steel_l": (255, 150, 60),
     "shine": (255, 220, 160), "poly": (40, 18, 10), "accent": (255, 120, 40),
     "wood": (80, 40, 20), "wood_l": (120, 60, 30)},
    {"key": "neon", "name": "NEON STRIKE", "price": 11000,
     "steel_d": (20, 40, 50), "steel": (40, 200, 180), "steel_l": (100, 255, 230),
     "shine": (200, 255, 245), "poly": (10, 25, 30), "accent": (0, 255, 180),
     "wood": (20, 50, 45), "wood_l": (40, 90, 80)},
    {"key": "void", "name": "VOID EDGE", "price": 14000,
     "steel_d": (20, 10, 35), "steel": (80, 40, 120), "steel_l": (160, 100, 220),
     "shine": (220, 180, 255), "poly": (12, 8, 22), "accent": (180, 80, 255),
     "wood": (30, 15, 45), "wood_l": (55, 30, 80)},
    {"key": "sakura", "name": "SAKURA STEEL", "price": 10000,
     "steel_d": (90, 40, 60), "steel": (220, 120, 160), "steel_l": (255, 190, 210),
     "shine": (255, 230, 240), "poly": (50, 20, 35), "accent": (255, 140, 180),
     "wood": (100, 50, 70), "wood_l": (150, 80, 100)},
    {"key": "obsidian", "name": "OBSIDIAN", "price": 13000,
     "steel_d": (12, 12, 16), "steel": (40, 42, 50), "steel_l": (90, 95, 110),
     "shine": (180, 190, 210), "poly": (8, 8, 12), "accent": (255, 80, 60),
     "wood": (25, 22, 28), "wood_l": (45, 42, 50)},
    # Admin Reaper exclusive: pure black blade with white outline
    {"key": "void_black", "name": "VOID BLACK", "price": 0,
     "steel_d": (0, 0, 0), "steel": (8, 8, 10), "steel_l": (22, 22, 26),
     "shine": (255, 255, 255), "poly": (0, 0, 0), "accent": (255, 255, 255),
     "wood": (6, 6, 8), "wood_l": (255, 255, 255), "outline": True},
]
GUN_SKIN_KEYS = [g["key"] for g in GUN_SKINS]

# ---------------------------------------------------------
# OWNERSHIP STATE
# ---------------------------------------------------------
owned_class_skins = {}          # class name -> set of skin names
equipped_class_skins = {}       # class name -> skin name
owned_gun_skins = {"steel", "void_black"}
equipped_gun_skin = "steel"
skin_index = 0                  # cursor on the class screen
gun_skin_index = 0              # cursor on the armory screen
armory_screen = False


def class_skin_list(name):
    return CLASS_SKINS.get(name, CLASS_SKINS["Survivor"])


def skin_owned(class_name, skin):
    if skin.get("base") or skin["price"] == 0:
        return True
    return skin["name"] in owned_class_skins.get(class_name, set())


def equipped_skin_name(class_name):
    return equipped_class_skins.get(class_name, "STANDARD")


def current_class_skin(class_name):
    want = equipped_skin_name(class_name)
    for sk in class_skin_list(class_name):
        if sk["name"] == want:
            return sk
    return class_skin_list(class_name)[0]


def find_class_skin(class_name, skin_name):
    for sk in class_skin_list(class_name):
        if sk["name"] == skin_name:
            return sk
    return class_skin_list(class_name)[0]


def class_palette(class_name, skin_name=None):
    """(accent, body, suit, suit_dark) honouring the equipped (or previewed) skin."""
    sk = find_class_skin(class_name, skin_name) if skin_name else current_class_skin(class_name)
    base_suit = CHAR_SUIT.get(class_name, ((76, 88, 58), (46, 56, 36)))
    accent = sk.get("accent") or CHAR_ACCENT.get(class_name, CYAN)
    body = sk.get("skin") or CHAR_SKIN.get(class_name, (231, 176, 126))
    suit = sk.get("suit") or base_suit[0]
    suit_d = sk.get("suit_d") or base_suit[1]
    return accent, body, suit, suit_d


def gun_palette(skin_key=None):
    want = skin_key or equipped_gun_skin
    for g in GUN_SKINS:
        if g["key"] == want:
            return g
    return GUN_SKINS[0]


def load_profile():
    global coins, gems, unlocked_characters, selected_character, character_index
    global owned_class_skins, equipped_class_skins, owned_gun_skins, equipped_gun_skin
    global skin_index, gun_skin_index
    try:
        with open(_account_save_path() if current_username else SAVE_FILE, "r", encoding="utf-8") as f:
            data=json.load(f)
        coins=max(0,int(data.get("coins",0)))
        gems=max(0,int(data.get("gems",0)))
        unlocked_characters=set(data.get("unlocked",["Survivor"]))
        unlocked_characters.add("Survivor")
        saved=data.get("selected","Survivor")
        if saved in unlocked_characters and saved in CHARACTER_PRICES: selected_character=saved
        owned = data.get("class_skins_owned", {})
        if isinstance(owned, dict):
            owned_class_skins = {k: set(v) for k, v in owned.items() if isinstance(v, list)}
        eq = data.get("class_skins_equipped", {})
        if isinstance(eq, dict):
            equipped_class_skins = {k: v for k, v in eq.items() if isinstance(v, str)}
        gs = data.get("gun_skins_owned", ["steel"])
        if isinstance(gs, list):
            owned_gun_skins = set(gs) | {"steel", "void_black"}
        eg = data.get("gun_skin", "steel")
        if eg in GUN_SKIN_KEYS and eg in owned_gun_skins:
            equipped_gun_skin = eg
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        pass
    names = class_list()
    if selected_character not in names:
        # Admin-only classes never load for a normal account.
        selected_character = "Survivor"
    character_index = names.index(selected_character)
    skin_index = 0
    gun_skin_index = GUN_SKIN_KEYS.index(equipped_gun_skin) if equipped_gun_skin in GUN_SKIN_KEYS else 0
    _GUN_ART_CACHE.clear()
    _PORTRAIT_CACHE.clear()

def save_profile():
    try:
        with open(_account_save_path() if current_username else SAVE_FILE,"w",encoding="utf-8") as f:
            json.dump({"coins":coins,"gems":gems,"unlocked":sorted(unlocked_characters),"selected":selected_character,
                       "class_skins_owned":{k:sorted(v) for k,v in owned_class_skins.items()},
                       "class_skins_equipped":dict(equipped_class_skins),
                       "gun_skins_owned":sorted(owned_gun_skins),
                       "gun_skin":equipped_gun_skin},f)
    except OSError:
        pass

def add_coins(amount):
    global coins
    coins += max(0,int(amount))
    save_profile()

def add_gems(amount):
    global gems
    gems += max(0, int(amount))
    save_profile()

shop_flash = None  # (message, timestamp) shown in the shop after a buy/equip action

def buy_or_equip_current():
    global selected_character, coins, shop_flash
    name=class_list()[character_index]
    price=CHARACTER_PRICES[name]
    now=pygame.time.get_ticks()
    if name in unlocked_characters:
        if selected_character==name:
            shop_flash=(f"{name.upper()} ALREADY EQUIPPED", now)
        else:
            selected_character=name
            shop_flash=(f"{name.upper()} EQUIPPED!", now)
    elif coins >= price:
        coins -= price
        unlocked_characters.add(name)
        selected_character=name
        shop_flash=(f"{name.upper()} UNLOCKED & EQUIPPED!", now)
    else:
        shop_flash=(f"NEED {price-coins:,} MORE COINS", now)
        return
    save_profile()


def skin_gem_price(skin):
    if skin.get("base") or skin.get("price", 0) == 0:
        return 0
    return max(5, int(skin.get("price", 1000) // 200))


def buy_or_equip_class_skin():
    """Buy class skins with GEMS (from bosses), or equip if owned."""
    global gems, shop_flash, equipped_class_skins, owned_class_skins
    name = class_list()[character_index]
    skins = class_skin_list(name)
    skin = skins[skin_index % len(skins)]
    now = pygame.time.get_ticks()
    gcost = skin_gem_price(skin)
    if name not in unlocked_characters:
        shop_flash = ("UNLOCK THE CLASS FIRST", now); return
    if skin_owned(name, skin):
        if equipped_skin_name(name) == skin["name"]:
            shop_flash = (f"{skin['name']} ALREADY ON", now); return
        equipped_class_skins[name] = skin["name"]
        shop_flash = (f"{skin['name']} EQUIPPED!", now)
    elif gcost <= 0:
        owned_class_skins.setdefault(name, set()).add(skin["name"])
        equipped_class_skins[name] = skin["name"]
        shop_flash = (f"{skin['name']} EQUIPPED!", now)
    elif gems >= gcost:
        gems -= gcost
        owned_class_skins.setdefault(name, set()).add(skin["name"])
        equipped_class_skins[name] = skin["name"]
        shop_flash = (f"{skin['name']} UNLOCKED! (-{gcost} GEMS)", now)
    else:
        shop_flash = (f"NEED {gcost - gems} MORE GEMS", now); return
    _PORTRAIT_CACHE.clear()
    save_profile()


def gun_gem_price(skin):
    if skin.get("price", 0) == 0:
        return 0
    return max(8, int(skin.get("price", 1000) // 250))


def buy_or_equip_gun_skin():
    """Buy weapon skins with GEMS."""
    global gems, shop_flash, equipped_gun_skin, owned_gun_skins
    skin = GUN_SKINS[gun_skin_index % len(GUN_SKINS)]
    now = pygame.time.get_ticks()
    gcost = gun_gem_price(skin)
    if skin["key"] in owned_gun_skins or gcost == 0:
        if equipped_gun_skin == skin["key"]:
            shop_flash = (f"{skin['name']} ALREADY ON", now); return
        equipped_gun_skin = skin["key"]
        shop_flash = (f"{skin['name']} EQUIPPED!", now)
    elif gems >= gcost:
        gems -= gcost
        owned_gun_skins.add(skin["key"])
        equipped_gun_skin = skin["key"]
        shop_flash = (f"{skin['name']} UNLOCKED! (-{gcost} GEMS)", now)
    else:
        shop_flash = (f"NEED {gcost - gems} MORE GEMS", now); return
    _GUN_ART_CACHE.clear()
    save_profile()

# =========================================================
# MULTIPLAYER NETWORKING
# =========================================================
def mp_send(data):
    global mp_socket
    if mp_socket:
        try:
            mp_socket.sendall((json.dumps(data) + "\n").encode())
        except OSError:
            pass

def mp_listener():
    global mp_connected, mp_code, mp_id, mp_is_host, mp_status, mp_started, mp_difficulty, mp_team_lives, mp_remote_dead_seen
    buf = ""
    try:
        while mp_socket:
            data = mp_socket.recv(8192)
            if not data:
                break
            buf += data.decode(errors="ignore")
            while "\n" in buf:
                line, buf = buf.split("\n", 1)
                if not line.strip():
                    continue
                msg = json.loads(line)
                typ = msg.get("type")
                if typ == "created":
                    mp_code = msg["code"]; mp_id = msg["id"]; mp_is_host = True
                    mp_status = "ROOM CREATED — SHARE THE CODE"
                elif typ == "joined":
                    mp_code = msg["code"]; mp_id = msg["id"]; mp_is_host = bool(msg.get("host"))
                    mp_status = "JOINED ROOM — WAITING FOR HOST"
                elif typ == "players":
                    mp_status = f"PLAYERS: {len(msg.get('players', []))}/4"
                elif typ == "start":
                    mp_started = True
                elif typ == "state":
                    rid = msg.get("id")
                    if rid and rid != mp_id:
                        remote_dead = bool(msg.get("dead", False))
                        previous_dead = bool(mp_remote_players.get(rid, {}).get("dead", False))
                        mp_remote_players[rid] = {
                            "x": float(msg.get("x", 0)),
                            "y": float(msg.get("y", 0)),
                            "character": msg.get("character", "Survivor"),
                            "username": msg.get("username", "PLAYER"),
                            "shooting": bool(msg.get("shooting", False)),
                            "dead": remote_dead,
                            "wave": int(msg.get("wave", 1)),
                        }
                        incoming_diff = msg.get("difficulty")
                        if incoming_diff in ("normal", "hardcore", "nightmare"):
                            mp_difficulty = incoming_diff
                            if mp_difficulty == "normal": mp_team_lives = max(mp_team_lives, 6)
                            elif mp_difficulty == "hardcore": mp_team_lives = max(mp_team_lives, 3)
                            else: mp_team_lives = max(mp_team_lives, 1)
                        if remote_dead and not previous_dead:
                            mp_team_lives = max(0, mp_team_lives - 1)
                        if not remote_dead and previous_dead:
                            mp_remote_dead_seen.discard(rid)
                elif typ == "error":
                    mp_status = "❌ " + str(msg.get("message", "ERROR"))
    except (OSError, ValueError, json.JSONDecodeError):
        pass
    mp_connected = False

def mp_connect():
    global mp_socket, mp_thread, mp_connected, mp_status
    try:
        mp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        mp_socket.settimeout(3)
        mp_socket.connect((SERVER_HOST, SERVER_PORT))
        mp_socket.settimeout(None)
        mp_connected = True
        mp_status = "CONNECTED"
        mp_thread = threading.Thread(target=mp_listener, daemon=True)
        mp_thread.start()
        return True
    except OSError as e:
        mp_socket = None
        mp_connected = False
        mp_status = f"SERVER ERROR: {e}"
        return False

def mp_create_room():
    global mp_remote_players, mp_started, mp_difficulty, mp_team_lives, mp_player_dead
    mp_remote_players = {}; mp_started = False; mp_player_dead = False
    mp_difficulty = "normal"; mp_team_lives = 6
    if mp_connect():
        mp_send({
            "action": "create",
            "username": current_username or "HOST",
            "character": selected_character,
            "gun_skin": equipped_gun_skin if "equipped_gun_skin" in globals() else "steel",
        })

def mp_join_room(code):
    global mp_remote_players, mp_started, mp_player_dead
    mp_remote_players = {}; mp_started = False; mp_player_dead = False
    if mp_connect():
        mp_send({
            "action": "join",
            "code": code.upper().strip(),
            "username": current_username or "PLAYER",
            "character": selected_character,
            "gun_skin": equipped_gun_skin if "equipped_gun_skin" in globals() else "steel",
        })

def mp_leave():
    global mp_socket, mp_connected, mp_code, mp_status, mp_started, mp_remote_players
    if mp_socket:
        try: mp_send({"action":"leave"}); mp_socket.close()
        except OSError: pass
    mp_socket = None; mp_connected = False; mp_code = ""; mp_started = False; mp_remote_players = {}
    mp_status = ""

def mp_start_game():
    global mp_started
    if mp_is_host and mp_connected:
        mp_send({"action":"start", "difficulty": mp_difficulty})
        mp_started = True

def mp_send_state(now, shooting=False):
    global mp_send_timer
    if not mp_connected or not mp_code:
        return
    if now - mp_send_timer >= 50:
        mp_send_timer = now
        mp_send({"action":"state", "x":player_x, "y":player_y,
                 "character":selected_character, "username":current_username,
                 "shooting":shooting, "dead":mp_player_dead, "wave":wave,
                 "difficulty":mp_difficulty})

def draw_multiplayer_screen():
    draw_zombie_bg(screen, pygame.time.get_ticks())
    center_text(screen, FONT_TITLE, "MULTIPLAYER", (WIDTH//2, 70), GOLD)
    panel = pygame.Rect(260, 125, 580, 490)
    draw_panel(screen, panel, (10,13,18), (65,75,70), 3)

    if not mp_connected:
        create = pygame.Rect(330, 205, 440, 65)
        join = pygame.Rect(330, 285, 440, 65)
        back = pygame.Rect(330, 465, 440, 65)
        mx,my=pygame.mouse.get_pos()
        draw_button(screen, create, "CREATE GAME", create.collidepoint(mx,my))
        draw_button(screen, join, "JOIN GAME", join.collidepoint(mx,my))
        draw_button(screen, back, "BACK", back.collidepoint(mx,my))
        center_text(screen, FONT_TINY, "2–4 PLAYERS  •  ROOM CODE", (WIDTH//2, 390), STONE_LIGHT)
        if mp_join_entry:
            center_text(screen, FONT_SMALL, mp_code or "______", (WIDTH//2, 440), CYAN)
        if mp_status:
            center_text(screen, FONT_TINY, mp_status, (WIDTH//2, 575), RED)
        return

    if mp_code:
        center_text(screen, FONT_SMALL, "ROOM CODE", (WIDTH//2, 180), STONE_LIGHT)
        center_text(screen, FONT_TINY, f"MODE: {mp_difficulty.upper()}  |  1=NORMAL  2=HARDCORE  3=NIGHTMARE" if mp_is_host else f"MODE: {mp_difficulty.upper()}", (WIDTH//2, 145), GOLD)
        center_text(screen, FONT_TITLE, mp_code, (WIDTH//2, 235), CYAN)
        center_text(screen, FONT_SMALL, mp_status, (WIDTH//2, 305), WHITE)
        center_text(screen, FONT_TINY, "SEND THIS CODE TO YOUR FRIENDS", (WIDTH//2, 345), GOLD)

        if mp_is_host:
            start=pygame.Rect(330, 400, 440, 65)
            mx,my=pygame.mouse.get_pos()
            draw_button(screen,start,"START GAME",start.collidepoint(mx,my))
        else:
            center_text(screen,FONT_SMALL,"WAITING FOR HOST...",(WIDTH//2,430),STONE_LIGHT)

        back=pygame.Rect(330,520,440,55)
        mx,my=pygame.mouse.get_pos()
        draw_button(screen,back,"LEAVE ROOM",back.collidepoint(mx,my))


def draw_remote_players(surface):
    for data in mp_remote_players.values():
        if data.get("dead", False):
            continue
        x,y=int(data["x"]),int(data["y"])
        pygame.draw.circle(surface,(245,190,135),(x,y-12),14)
        pygame.draw.circle(surface,(30,80,150),(x,y+15),20)
        pygame.draw.circle(surface,CYAN,(x,y),27,2)
        name = str(data.get("username", "PLAYER"))
        label=FONT_TINY.render(name,True,WHITE)
        surface.blit(label,(x-label.get_width()//2,y-58))
        char_label=FONT_TINY.render(str(data.get("character","PLAYER")),True,STONE_LIGHT)
        surface.blit(char_label,(x-char_label.get_width()//2,y+35))

def draw_multiplayer_lives(surface):
    if not mp_connected or not mp_started:
        return
    mode_names = {"normal":"NORMAL", "hardcore":"HARDCORE", "nightmare":"NIGHTMARE"}
    mode = mode_names.get(mp_difficulty, "NORMAL")
    title = FONT_SMALL.render(f"TEAM LIVES: {mp_team_lives}   •   {mode}", True, GOLD)
    surface.blit(title, (20, 20))
    if mp_player_dead:
        msg = FONT_SMALL.render("YOU ARE DOWN — RESPAWN NEXT WAVE", True, RED)
        surface.blit(msg, (WIDTH//2-msg.get_width()//2, 88))

# =========================================================
# HIT EFFECTS
# =========================================================
player_flash_until = 0
last_player_hit_time = 0
screen_shake_until = 0
screen_shake_strength = 0

def spawn_power_anim(x, y, current_time, color=(120, 220, 255), style="ring", size=120, life=700):
    """Transparent power cast animation (75% transparent => alpha ~64)."""
    power_fx.append({
        "x": float(x), "y": float(y),
        "time": current_time,
        "life": life,
        "color": color,
        "style": style,
        "size": size,
    })


def draw_power_anims(surface, current_time):
    """Draw power-use FX at 75% transparency (25% opacity)."""
    ALPHA = 64  # 75% transparent
    for fx in power_fx[:]:
        age = current_time - fx["time"]
        if age >= fx["life"]:
            power_fx.remove(fx)
            continue
        p = age / max(1, fx["life"])
        fade = (1.0 - p) * ALPHA
        col = fx.get("color", (120, 220, 255))
        x, y = int(fx["x"]), int(fx["y"])
        size = int(fx.get("size", 120))
        style = fx.get("style", "ring")

        if style == "ring":
            # expanding rings
            for i in range(3):
                r = int(20 + (size + 40) * p + i * 18)
                a = int(fade * (1.0 - i * 0.22) * (1.0 - p * 0.3))
                if a <= 2:
                    continue
                s = pygame.Surface((r * 2 + 8, r * 2 + 8), pygame.SRCALPHA)
                pygame.draw.circle(s, (*col, a), (r + 4, r + 4), r, max(2, 5 - i))
                surface.blit(s, (x - r - 4, y - r - 4))
            # soft fill pulse
            r2 = int(size * (0.35 + 0.65 * (1.0 - p)))
            s2 = pygame.Surface((r2 * 2 + 4, r2 * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(s2, (*col, int(fade * 0.45)), (r2 + 2, r2 + 2), r2)
            surface.blit(s2, (x - r2 - 2, y - r2 - 2))
        elif style == "burst":
            # star burst rays + ring
            rays = 10
            for i in range(rays):
                ang = i * (math.tau / rays) + p * 1.2
                length = size * (0.5 + 0.8 * p)
                a = int(fade * (1.0 - p))
                if a <= 2:
                    continue
                s = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
                cx = size * 1.5
                cy = size * 1.5
                x2 = cx + math.cos(ang) * length
                y2 = cy + math.sin(ang) * length
                pygame.draw.line(s, (*col, a), (cx, cy), (x2, y2), 3)
                surface.blit(s, (x - cx, y - cy))
            r = int(30 + size * p)
            s = pygame.Surface((r * 2 + 6, r * 2 + 6), pygame.SRCALPHA)
            pygame.draw.circle(s, (*col, int(fade * 0.7)), (r + 3, r + 3), r, 3)
            surface.blit(s, (x - r - 3, y - r - 3))
        elif style == "holy":
            # cross + expanding halo
            a = int(fade)
            s = pygame.Surface((size * 2 + 40, size * 2 + 40), pygame.SRCALPHA)
            cx = size + 20
            cy = size + 20
            arm = int(size * (0.4 + 0.3 * (1.0 - p)))
            pygame.draw.rect(s, (*col, a), (cx - 6, cy - arm, 12, arm * 2))
            pygame.draw.rect(s, (*col, a), (cx - arm, cy - 6, arm * 2, 12))
            r = int(size * (0.5 + p))
            pygame.draw.circle(s, (*col, int(a * 0.6)), (cx, cy), r, 3)
            pygame.draw.circle(s, (*col, int(a * 0.3)), (cx, cy), int(r * 1.25), 2)
            surface.blit(s, (x - cx, y - cy))
        else:
            # default soft circle
            r = int(size * (0.4 + 0.8 * p))
            s = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(s, (*col, int(fade * 0.8)), (r + 2, r + 2), r)
            surface.blit(s, (x - r - 2, y - r - 2))


def trigger_hit_effect(current_time, strength=3):
    global screen_shake_until, screen_shake_strength
    screen_shake_until = max(screen_shake_until, current_time + 80)
    screen_shake_strength = max(screen_shake_strength, strength)

def damage_player(amount, current_time):
    global health, player_flash_until, last_player_hit_time, mp_player_dead, mp_team_lives, game_over, damage_reduction
    if mp_player_dead and mp_connected and mp_started:
        return
    # Small invulnerability window keeps contact damage from draining HP
    # every single frame while still making hits feel responsive.
    if current_time - last_player_hit_time < 185:
        return
    amount = max(1, amount * (1.0 - damage_reduction))
    health -= amount
    play_sfx("hurt", 0.28)

    if thorns:
        for z in zombies[:]:
            if math.hypot(z["x"] - player_x, z["y"] - player_y) < z["radius"] + 34:
                z["health"] -= thorns
                z["hit_flash_until"] = current_time + 75
                if z["health"] <= 0:
                    kill_zombie(z)
    last_player_hit_time = current_time
    player_flash_until = current_time + 120
    trigger_hit_effect(current_time, 3)
    if health <= 0:
        health = 0
        if mp_connected and mp_started:
            mp_player_dead = True
            mp_team_lives = max(0, mp_team_lives - 1)
            if mp_team_lives <= 0:
                game_over = True
        else:
            game_over = True

# =========================================================
# NAMES
# =========================================================
def gun_name():
    table = BLADE_TIER_NAMES if is_melee_class() else GUN_TIER_NAMES
    return table.get(gun_level, table[max(table)])


def orbit_name():
    if orbit_type == "none":
        return "LOCKED"
    names = {
        "knife": "KNIFE",
        "axe": "AXE",
        "katana": "KATANA",
        "auto": "AUTO GUN",
    }
    return f"{orbit_count} {names[orbit_type]}"


def next_orbit_text():
    if orbit_type == "none":
        return "GET 1 KNIFE"
    if orbit_type == "knife":
        if orbit_count < 3:
            return f"KNIFE {orbit_count} -> {orbit_count + 1}"
        return "3 KNIVES -> 1 AXE"
    if orbit_type == "axe":
        if orbit_count < 4:
            return f"AXE {orbit_count} -> {orbit_count + 1}"
        return "4 AXES -> 1 KATANA"
    if orbit_type == "katana":
        if orbit_count < 5:
            return f"KATANA {orbit_count} -> {orbit_count + 1}"
        return "5 KATANAS -> 1 AUTO GUN"
    if orbit_type == "auto":
        if orbit_count < 5:
            return f"AUTO GUN {orbit_count} -> {orbit_count + 1}"
        return "MAX LEVEL"
    return ""


# =========================================================
# UPGRADE INFORMATION  (stacking levels + rarity weighting)
# =========================================================
LEGENDARY = (255, 150, 40)

UPGRADE_DATA = {
    # key: name, description, color, rarity, max stacks
    "health":     {"name": "FIELD MEDKIT",    "description": "Instantly heal 40 HP.",            "color": GREEN,  "rarity": "COMMON", "max": 99},
    "damage":     {"name": "DAMAGE CORE",     "description": "+14 bullet damage.",               "color": RED,    "rarity": "COMMON", "max": 10},
    "fire":       {"name": "RAPID TRIGGER",   "description": "Shoot 12% faster.",                "color": GOLD,   "rarity": "COMMON", "max": 8},
    "speed":      {"name": "SPRINT MODULE",   "description": "+0.9 movement speed.",             "color": BLUE,   "rarity": "COMMON", "max": 6},
    "bullet":     {"name": "HOT AMMO",        "description": "+4 bullet speed.",                 "color": PURPLE, "rarity": "COMMON", "max": 6},
    "bigrounds":  {"name": "HEAVY ROUNDS",    "description": "+2 bullet size, +6% damage.",      "color": METAL,  "rarity": "COMMON", "max": 5},
    "greed":      {"name": "BLOOD MONEY",     "description": "+30% coins from kills.",           "color": GOLD,   "rarity": "COMMON", "max": 6},
    "scholar":    {"name": "COMBAT DRILLS",   "description": "+25% XP from kills.",              "color": XP_COLOR, "rarity": "COMMON", "max": 5},
    "scavenger":  {"name": "SCAVENGER",       "description": "+9% medkit drop chance.",          "color": GREEN,  "rarity": "COMMON", "max": 5},
    "maxhealth":  {"name": "ARMOR PLATE",     "description": "+30 max HP and full heal.",        "color": GREEN,  "rarity": "RARE",   "max": 8},
    "crit":       {"name": "CRITICAL CORE",   "description": "+8% critical-hit chance.",         "color": GOLD,   "rarity": "RARE",   "max": 7},
    "armor":      {"name": "NANO ARMOR",      "description": "Take 7% less damage.",             "color": CYAN,   "rarity": "RARE",   "max": 7},
    "lifesteal":  {"name": "VAMPIRISM",       "description": "Heal 3 HP per kill.",              "color": RED,    "rarity": "RARE",   "max": 5},
    "regen":      {"name": "NANO REGEN",      "description": "Regenerate 3 HP every 2.5s.",      "color": GREEN,  "rarity": "RARE",   "max": 5},
    "cryo":       {"name": "CRYO ROUNDS",     "description": "14% chance to freeze on hit.",     "color": CYAN,   "rarity": "RARE",   "max": 4},
    "critpower":  {"name": "OVERCHARGE",      "description": "+0.30x critical damage.",          "color": RED,    "rarity": "EPIC",   "max": 6},
    "pierce":     {"name": "RAILGUN ROUNDS",  "description": "Bullets pass through +1 zombie.",  "color": CYAN,   "rarity": "EPIC",   "max": 4},
    "shrapnel":   {"name": "SHRAPNEL ROUNDS", "description": "Bullets burst for splash damage.", "color": (255, 140, 60), "rarity": "EPIC", "max": 3},
    "thorns":     {"name": "SPIKE PLATING",   "description": "Zombies that hit you take 25.",    "color": METAL,  "rarity": "EPIC",   "max": 4},
    "gun":        {"name": "WEAPON EVOLUTION", "description": "Upgrade your held weapon.",       "color": GOLD,   "rarity": "RARE", "max": 99},
    "orbit":      {"name": "ORBITAL EVOLUTION", "description": "Evolve your orbit weapon.",     "color": CYAN,   "rarity": "RARE", "max": 99},
}

RARITY_COLORS = {
    "COMMON": (150, 158, 168),
    "RARE": (80, 150, 245),
    "EPIC": (185, 105, 235),
    "LEGENDARY": LEGENDARY,
}
RARITY_WEIGHTS = {"COMMON": 62, "RARE": 30, "EPIC": 12, "LEGENDARY": 5}

upgrade_levels = {}


def upgrade_level_of(key):
    return upgrade_levels.get(key, 0)


def upgrade_is_maxed(key):
    if key == "gun":
        return gun_level >= GUN_MAX_LEVEL
    if key == "orbit":
        return orbit_type == "auto" and orbit_count >= 5
    return upgrade_level_of(key) >= UPGRADE_DATA[key]["max"]


def create_upgrade_options():
    """Three weighted cards; rarer picks get likelier as the run goes on."""
    pool = [k for k in UPGRADE_DATA if not upgrade_is_maxed(k)]
    if len(pool) <= 3:
        return pool + ["health"] * (3 - len(pool))

    luck = 1.0 + min(1.6, level * 0.06)
    picks = []
    for _ in range(3):
        weights = []
        for key in pool:
            rarity = UPGRADE_DATA[key]["rarity"]
            w = RARITY_WEIGHTS[rarity]
            if rarity in ("EPIC", "LEGENDARY"):
                w *= luck
            # taper upgrades already stacked high so cards stay varied
            w /= (1.0 + upgrade_level_of(key) * 0.35)
            weights.append(w)
        choice = random.choices(pool, weights=weights, k=1)[0]
        picks.append(choice)
        pool.remove(choice)
    return picks


def upgrade_card_description(key):
    """Live description that reflects the player's current build."""
    data = UPGRADE_DATA[key]
    if key == "orbit":
        return next_orbit_text() or data["description"]
    if key == "gun":
        if is_melee_class():
            return "SHARPEN THE BLADE: +50% DAMAGE"
        if gun_level == 3:
            return "CHOOSE SMG OR RPG"
        return "NEXT WEAPON TIER: +50% DAMAGE"
    return data["description"]


def upgrade_stat_line(key):
    """Short 'current value' readout shown at the bottom of each card."""
    if key == "damage":
        return f"DAMAGE {int(damage)} -> {int(damage) + 14}"
    if key == "fire":
        return f"DELAY {shoot_delay}ms -> {max(52, int(shoot_delay * 0.88))}ms"
    if key == "speed":
        return f"SPEED {player_speed:.1f} -> {player_speed + 0.9:.1f}"
    if key == "bullet":
        return f"VELOCITY {bullet_speed} -> {bullet_speed + 4}"
    if key == "maxhealth":
        return f"MAX HP {max_health} -> {max_health + 30}"
    if key == "health":
        return f"HP {int(health)} / {max_health}"
    if key == "crit":
        return f"CRIT {int(crit_chance*100)}% -> {int(min(0.75, crit_chance+0.08)*100)}%"
    if key == "critpower":
        return f"CRIT DMG {crit_multiplier:.2f}x -> {min(4.5, crit_multiplier+0.30):.2f}x"
    if key == "armor":
        return f"ARMOR {int(damage_reduction*100)}% -> {int(min(0.65, damage_reduction+0.07)*100)}%"
    if key == "lifesteal":
        return f"HEAL/KILL {lifesteal} -> {lifesteal + 3}"
    if key == "regen":
        return f"REGEN {regen_amount} -> {regen_amount + 3} HP"
    if key == "cryo":
        return f"FREEZE {int(freeze_chance*100)}% -> {int(min(0.7, freeze_chance+0.14)*100)}%"
    if key == "pierce":
        return f"PIERCE {pierce} -> {pierce + 1}"
    if key == "shrapnel":
        return f"BURST {shrapnel} -> {shrapnel + 1}"
    if key == "thorns":
        return f"THORNS {thorns} -> {thorns + 25}"
    if key == "greed":
        return f"COINS +{int(coin_bonus*100)}% -> +{int((coin_bonus+0.30)*100)}%"
    if key == "scholar":
        return f"XP +{int(xp_bonus*100)}% -> +{int((xp_bonus+0.25)*100)}%"
    if key == "scavenger":
        return f"DROPS {int(med_drop_chance*100)}% -> {int(min(0.7, med_drop_chance+0.09)*100)}%"
    if key == "bigrounds":
        return f"CALIBER {bullet_size} -> {bullet_size + 2}"
    if key == "gun":
        if is_melee_class():
            nxt = BLADE_TIER_NAMES.get(gun_level + 1, "MAX")
        elif gun_level == 3:
            nxt = "SMG / RPG"
        elif gun_level in (4, 5):
            nxt = GUN_TIER_NAMES[6]
        else:
            nxt = GUN_TIER_NAMES.get(gun_level + 1, "MAX")
        return f"{gun_name()} -> {nxt}"
    if key == "orbit":
        return "NO ORBIT YET" if orbit_type == "none" else orbit_name()
    return ""


# =========================================================
# UPGRADE CARD LAYOUT / RENDERING
# =========================================================
CARD_W, CARD_H, CARD_GAP, CARD_Y = 292, 402, 26, 196


def upgrade_card_rects():
    total = CARD_W * 3 + CARD_GAP * 2
    sx = (WIDTH - total) // 2
    return [pygame.Rect(sx + i * (CARD_W + CARD_GAP), CARD_Y, CARD_W, CARD_H) for i in range(3)]


def _wrap(font, text, max_px):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if font.size(test)[0] > max_px and cur:
            lines.append(cur)
            cur = w
        else:
            cur = test
    if cur:
        lines.append(cur)
    return lines


def draw_upgrade_cards(mx, my):
    t = pygame.time.get_ticks()
    for i, base in enumerate(upgrade_card_rects()):
        if i >= len(upgrade_options):
            break
        key = upgrade_options[i]
        data = UPGRADE_DATA[key]
        rarity = data.get("rarity", "COMMON")
        rc = RARITY_COLORS.get(rarity, WHITE)
        hovered = base.collidepoint(mx, my)
        rect = base.move(0, -8) if hovered else base.copy()

        # outer glow for the good stuff
        if rarity in ("EPIC", "LEGENDARY") or hovered:
            pulse = 0.55 + 0.45 * math.sin(t * 0.004 + i)
            g = pygame.Surface((rect.w + 56, rect.h + 56), pygame.SRCALPHA)
            for n in range(10, 0, -1):
                a = int((30 if hovered else 15) * ((10 - n) / 10.0) ** 2.1 * (0.6 + 0.4 * pulse))
                pygame.draw.rect(g, (*rc, a), (28 - n * 1.7, 28 - n * 1.7,
                                               rect.w + n * 3.4, rect.h + n * 3.4),
                                 border_radius=16 + n * 2)
            screen.blit(g, (rect.x - 28, rect.y - 28), special_flags=pygame.BLEND_RGBA_ADD)

        # drop shadow + body
        sh = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        pygame.draw.rect(sh, (0, 0, 0, 150), (0, 0, rect.w, rect.h), border_radius=16)
        screen.blit(sh, (rect.x + 7, rect.y + 10))

        body = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        top = _mix((26, 30, 38), rc, 0.20 if hovered else 0.12)
        for yy in range(rect.h):
            f = yy / float(rect.h)
            pygame.draw.line(body, _mix(top, (11, 13, 17), f ** 0.75), (0, yy), (rect.w, yy))
        mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, rect.w, rect.h), border_radius=16)
        body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        screen.blit(body, rect.topleft)
        pygame.draw.rect(screen, _sh(rc, 0.5), rect, 4, border_radius=16)
        pygame.draw.rect(screen, rc if hovered else _sh(rc, 0.8), rect.inflate(-6, -6), 2, border_radius=13)

        # rarity ribbon
        ribbon = pygame.Rect(rect.x + 6, rect.y + 6, rect.w - 12, 30)
        rs = pygame.Surface((ribbon.w, ribbon.h), pygame.SRCALPHA)
        rs.fill((*rc, 46))
        screen.blit(rs, ribbon.topleft)
        center_text(screen, FONT_TINY, rarity, ribbon.center, rc)

        # icon plate
        plate = pygame.Rect(rect.x + 26, rect.y + 44, rect.w - 52, 152)
        ps = pygame.Surface((plate.w, plate.h), pygame.SRCALPHA)
        pygame.draw.rect(ps, (0, 0, 0, 120), (0, 0, plate.w, plate.h), border_radius=12)
        screen.blit(ps, plate.topleft)
        pygame.draw.rect(screen, _sh(rc, 0.45), plate, 2, border_radius=12)
        draw_upgrade_icon(screen, key, plate.centerx - 100, plate.centery - 72)

        # name
        name_lines = _wrap(FONT_SMALL, data["name"], rect.w - 36)
        ny = rect.y + 206
        for line in name_lines[:2]:
            center_text(screen, FONT_SMALL, line, (rect.centerx, ny), WHITE)
            ny += 22

        # stack pips
        lvl = upgrade_level_of(key)
        cap = data.get("max", 99)
        if cap <= 10:
            pip_y = ny + 6
            total_w = cap * 15
            for p in range(cap):
                px = rect.centerx - total_w // 2 + p * 15 + 7
                pygame.draw.circle(screen, rc if p < lvl else (52, 58, 68), (px, pip_y), 5)
            ny = pip_y + 14
        elif lvl:
            center_text(screen, FONT_TINY, f"OWNED x{lvl}", (rect.centerx, ny + 6), rc)
            ny += 20

        # description
        for line in _wrap(FONT_TINY, upgrade_card_description(key), rect.w - 40)[:3]:
            center_text(screen, FONT_TINY, line, (rect.centerx, ny + 12), (222, 226, 234))
            ny += 20

        # live stat delta
        stat = upgrade_stat_line(key)
        if stat:
            bar = pygame.Rect(rect.x + 18, rect.bottom - 92, rect.w - 36, 30)
            bs = pygame.Surface((bar.w, bar.h), pygame.SRCALPHA)
            bs.fill((*rc, 30))
            screen.blit(bs, bar.topleft)
            center_text(screen, FONT_TINY, stat, bar.center, _mix(rc, WHITE, 0.5))

        # pick key badge
        badge = pygame.Rect(rect.centerx - 48, rect.bottom - 54, 96, 38)
        pygame.draw.rect(screen, (18, 21, 27), badge, border_radius=9)
        pygame.draw.rect(screen, rc if hovered else STONE_LIGHT, badge, 3, border_radius=9)
        center_text(screen, FONT_SMALL, f"[ {i + 1} ]", badge.center, WHITE if hovered else STONE_LIGHT)


# =========================================================
# APPLY ORBIT UPGRADE
# =========================================================
def apply_orbit_upgrade():
    global orbit_type, orbit_count, orbit_damage
    global orbit_shoot_delay, orbit_last_shot, orbit_radius, orbit_speed

    if orbit_type == "none":
        orbit_type, orbit_count, orbit_damage = "knife", 1, 20
        orbit_radius, orbit_speed = 78, 0.055
    elif orbit_type == "knife":
        if orbit_count < 3:
            orbit_count += 1
            orbit_damage += 3
        else:
            orbit_type, orbit_count, orbit_damage = "axe", 1, 32
            orbit_radius, orbit_speed = 84, 0.060
    elif orbit_type == "axe":
        if orbit_count < 4:
            orbit_count += 1
            orbit_damage += 4
        else:
            orbit_type, orbit_count, orbit_damage = "katana", 1, 48
            orbit_radius, orbit_speed = 90, 0.065
    elif orbit_type == "katana":
        if orbit_count < 5:
            orbit_count += 1
            orbit_damage += 5
        else:
            orbit_type, orbit_count, orbit_damage = "auto", 1, 62
            orbit_radius, orbit_speed = 96, 0.070
            orbit_shoot_delay, orbit_last_shot = 520, 0
    elif orbit_type == "auto":
        if orbit_count < 5:
            orbit_count += 1
            orbit_damage += 7
            orbit_shoot_delay = max(220, orbit_shoot_delay - 55)
            orbit_radius = min(112, orbit_radius + 3)


# =========================================================
# FINAL GUN CHOICE
# =========================================================
def choose_special_gun(choice):
    global gun_level, has_smg, has_rpg, damage, shoot_delay, bullet_speed

    # SMG and RPG are mutually exclusive final choices.
    if choice == "smg":
        has_smg = True
        has_rpg = False
        gun_level = 4
        shoot_delay = min(shoot_delay, 85)
        bullet_speed = max(bullet_speed, 14)
        # SMG = very fast single shots. Preserve a good damage value while
        # giving it a clearly different identity from Triple Shot.
        shoot_delay = min(shoot_delay, 85)
        damage = int(damage * 1.5) + 5

    elif choice == "rpg":
        has_rpg = True
        has_smg = False
        gun_level = 5
        # RPG = slow, heavy explosive shots.
        shoot_delay = max(shoot_delay, 500)
        bullet_speed = max(9, bullet_speed)
        damage = int(damage * 1.5) + 30


# =========================================================
# APPLY NORMAL UPGRADES
# =========================================================
def apply_upgrade(upgrade):
    global health, max_health, damage, shoot_delay
    global player_speed, bullet_speed, gun_level, bullet_size
    global crit_chance, crit_multiplier, damage_reduction
    global upgrade_pick_count, upgrade_levels
    global lifesteal, regen_amount, pierce, shrapnel, thorns
    global freeze_chance, coin_bonus, xp_bonus, med_drop_chance

    if upgrade == "health":
        if named_bosses_alive():
            pass  # no instant heal during boss gauntlet
        else:
            health = min(max_health, health + 40)
    elif upgrade == "damage":
        damage += 14
    elif upgrade == "fire":
        shoot_delay = max(52, int(shoot_delay * 0.88))
    elif upgrade == "speed":
        player_speed += 0.9
    elif upgrade == "bullet":
        bullet_speed += 4
    elif upgrade == "bigrounds":
        bullet_size += 2
        damage = int(damage * 1.06)
    elif upgrade == "maxhealth":
        max_health += 30
        if not named_bosses_alive():
            health = max_health
    elif upgrade == "crit":
        crit_chance = min(0.75, crit_chance + 0.08)
    elif upgrade == "critpower":
        crit_multiplier = min(4.5, crit_multiplier + 0.30)
    elif upgrade == "armor":
        damage_reduction = min(0.65, damage_reduction + 0.07)
    elif upgrade == "lifesteal":
        lifesteal += 3
    elif upgrade == "regen":
        regen_amount += 3
    elif upgrade == "cryo":
        freeze_chance = min(0.70, freeze_chance + 0.14)
    elif upgrade == "pierce":
        pierce += 1
    elif upgrade == "shrapnel":
        shrapnel += 1
    elif upgrade == "thorns":
        thorns += 25
    elif upgrade == "greed":
        coin_bonus += 0.30
    elif upgrade == "scholar":
        xp_bonus += 0.25
    elif upgrade == "scavenger":
        med_drop_chance = min(0.70, med_drop_chance + 0.09)
    elif upgrade == "gun":
        # WEAPON EVOLUTION: every step multiplies damage by 1.5 (+50%).
        if is_melee_class():
            if gun_level < GUN_MAX_LEVEL:
                gun_level += 1
                damage = int(damage * 1.5) + 1
                if gun_level >= 4:
                    shoot_delay = max(150, int(shoot_delay * 0.9))
        elif gun_level == 1:
            gun_level = 2
            damage = int(damage * 1.5) + 1
        elif gun_level == 2:
            gun_level = 3
            damage = int(damage * 1.5) + 1
        elif gun_level in (4, 5):
            gun_level = 6                                  # MINIGUN
            damage = int(damage * 1.5) + 1
            shoot_delay = min(shoot_delay, 70)
            bullet_speed = max(bullet_speed, 15)
        elif gun_level == 6:
            gun_level = 7                                  # FLAMETHROWER
            damage = int(damage * 1.55) + 2
            shoot_delay = min(shoot_delay, 48)             # rapid stream
            bullet_speed = max(11, min(bullet_speed, 14))
        elif gun_level == 7:
            gun_level = 8                                  # PLASMA RIFLE
            damage = int(damage * 1.5) + 1
            shoot_delay = max(110, min(shoot_delay, 150))
            bullet_speed = max(bullet_speed, 19)
            pierce += 2
            bullet_size += 2
    elif upgrade == "orbit":
        apply_orbit_upgrade()

    upgrade_levels[upgrade] = upgrade_levels.get(upgrade, 0) + 1
    upgrade_pick_count += 1




# =========================================================
# PIXEL PLAYER — ENHANCED
# =========================================================
def draw_werewolf(surface, x, y, scale=1.0, boss=False):
    """Legendary werewolf form — massive silhouette, blood moon aura, energy claws."""
    t = pygame.time.get_ticks()
    s = float(scale)
    bob = int(math.sin(t * 0.014) * (5 * s))
    pulse = 0.5 + 0.5 * math.sin(t * 0.028)
    pulse2 = 0.5 + 0.5 * math.sin(t * 0.045)
    fur = (48, 44, 54)
    fur_m = (95, 90, 105)
    fur_l = (165, 160, 180)
    fur_d = (18, 16, 24)
    eye = (255, 40, 30)
    claw_c = (255, 245, 250)
    aura = (200, 25, 40)
    gold = (255, 200, 70)
    moon = (255, 90, 100)

    def sc(v):
        return int(v * s)

    # multi-layer ground shadow
    for si, (sw, sh, sa) in enumerate(((170, 52, 85), (140, 42, 110), (110, 32, 130))):
        shadow = pygame.Surface((sc(sw), sc(sh)), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, sa), shadow.get_rect())
        surface.blit(shadow, shadow.get_rect(center=(x, y + sc(46) + si * 2)))

    # blood-moon outer bloom
    bloom_r = sc(110 + int(14 * pulse))
    bloom = pygame.Surface((bloom_r * 2 + 20, bloom_r * 2 + 20), pygame.SRCALPHA)
    for ring in range(10, 0, -1):
        rr = int(bloom_r * ring / 10)
        a = int((16 + 12 * pulse) * (ring / 10.0) ** 1.5)
        pygame.draw.circle(bloom, (*aura, a), (bloom_r + 10, bloom_r + 10), rr)
    surface.blit(bloom, (x - bloom_r - 10, y - bloom_r - 10 + bob // 2), special_flags=pygame.BLEND_RGBA_ADD)

    # aura rings
    for i, rad in enumerate((100, 86, 72, 58, 46)):
        a = int(30 + 28 * pulse) - i * 4
        ring = pygame.Surface((sc(rad) * 2 + 16, sc(rad) * 2 + 16), pygame.SRCALPHA)
        pygame.draw.circle(ring, (*aura, max(8, a)), (sc(rad) + 8, sc(rad) + 8), sc(rad), 3)
        if i % 2 == 0:
            pygame.draw.circle(ring, (*moon, max(6, a // 2)), (sc(rad) + 8, sc(rad) + 8), sc(rad) - 5, 1)
        surface.blit(ring, ring.get_rect(center=(x, y + sc(2))))

    # orbiting blood shards + embers
    for i in range(18):
        ang = t * 0.0038 + i * (math.tau / 18)
        rr = sc(62 + 16 * math.sin(t * 0.009 + i))
        px = int(x + math.cos(ang) * rr)
        py = int(y + math.sin(ang * 1.15) * rr * 0.72 - sc(6))
        sz = 3 + (i % 3)
        pts = [(px, py - sz * 2), (px + sz, py), (px, py + sz * 2), (px - sz, py)]
        pygame.draw.polygon(surface, (210, 40, 50), pts)
        if i % 3 == 0:
            pygame.draw.polygon(surface, gold, pts, 1)
    for i in range(16):
        ang = t * 0.005 + i * 0.45
        px = int(x + math.cos(ang) * sc(58 + 12 * math.sin(t * 0.012 + i)))
        py = int(y + math.sin(ang * 1.3) * sc(34) - sc(14))
        pygame.draw.circle(surface, (230, 55, 55), (px, py), 2 + (i % 3))

    # digitigrade legs
    for side, so in ((-1, -sc(24)), (1, sc(24))):
        pygame.draw.polygon(surface, fur_d, [
            (x + so - sc(11), y + sc(8) + bob), (x + so + sc(11), y + sc(8) + bob),
            (x + so + sc(9), y + sc(30) + bob), (x + so - sc(13), y + sc(30) + bob)])
        pygame.draw.polygon(surface, fur, [
            (x + so - sc(9), y + sc(28) + bob), (x + so + sc(7), y + sc(28) + bob),
            (x + so + side * sc(6) + sc(5), y + sc(52) + bob),
            (x + so + side * sc(6) - sc(8), y + sc(52) + bob)])
        pygame.draw.ellipse(surface, fur_d, (x + so + side * sc(6) - sc(13), y + sc(48) + bob, sc(24), sc(13)))
        for c in range(4):
            pygame.draw.line(surface, claw_c,
                             (x + so + side * sc(6) - sc(9) + c * sc(5), y + sc(56) + bob),
                             (x + so + side * sc(6) - sc(9) + c * sc(5) + side, y + sc(68) + bob), max(2, sc(3)))

    # torso
    torso = pygame.Rect(x - sc(40), y - sc(22) + bob, sc(80), sc(68))
    pygame.draw.rect(surface, (6, 6, 10), torso.inflate(sc(16), sc(16)), border_radius=sc(16))
    pygame.draw.rect(surface, fur_d, torso.inflate(sc(8), sc(8)), border_radius=sc(14))
    pygame.draw.rect(surface, fur, torso, border_radius=sc(12))
    pygame.draw.rect(surface, fur_m, (x - sc(30), y - sc(8) + bob, sc(60), sc(16)), border_radius=sc(5))
    pygame.draw.ellipse(surface, fur_l, (x - sc(18), y + sc(8) + bob, sc(36), sc(28)))
    # glowing heart core
    core_r = sc(9 + int(3 * pulse2))
    pygame.draw.circle(surface, (100, 8, 16), (x, y + sc(14) + bob), core_r + sc(5))
    pygame.draw.circle(surface, (230, 40, 50), (x, y + sc(14) + bob), core_r)
    pygame.draw.circle(surface, gold, (x, y + sc(14) + bob), max(2, core_r // 2))
    pygame.draw.line(surface, (50, 18, 22), (x - sc(22), y - sc(10) + bob), (x + sc(12), y + sc(18) + bob), max(2, sc(2)))

    # arms + claws toward mouse (or left if boss)
    if boss:
        ang = math.sin(t * 0.004) * 0.6 + math.pi
    else:
        mx, my = pygame.mouse.get_pos()
        ang = math.atan2(my - y, mx - x)
    for side in (-1, 1):
        ax = x + int(math.cos(ang) * sc(24) + side * math.cos(ang + 1.57) * sc(34))
        ay = y + int(math.sin(ang) * sc(24) + side * math.sin(ang + 1.57) * sc(34)) + bob
        pygame.draw.circle(surface, fur_d, (ax - int(math.cos(ang) * sc(12)), ay - int(math.sin(ang) * sc(12))), sc(17))
        pygame.draw.circle(surface, fur, (ax - int(math.cos(ang) * sc(12)), ay - int(math.sin(ang) * sc(12))), sc(14))
        pygame.draw.circle(surface, fur_d, (ax, ay), sc(16))
        pygame.draw.circle(surface, fur_m, (ax, ay), sc(13))
        glow = pygame.Surface((sc(80), sc(80)), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 50, 40, int(55 + 45 * pulse)), (sc(40), sc(40)), sc(30))
        surface.blit(glow, glow.get_rect(center=(ax, ay)), special_flags=pygame.BLEND_RGBA_ADD)
        for c in range(5):
            ca = ang - 0.55 + c * 0.28
            length = sc(30 + (5 if c in (1, 2, 3) else 0))
            tip = (ax + int(math.cos(ca) * length), ay + int(math.sin(ca) * length))
            pygame.draw.line(surface, (18, 18, 26), (ax, ay), tip, max(3, sc(7)))
            pygame.draw.line(surface, claw_c, (ax, ay), tip, max(2, sc(4)))
            pygame.draw.circle(surface, (255, 100, 70), tip, max(2, sc(4)))
            pygame.draw.circle(surface, WHITE, tip, max(1, sc(2)))

    # head + snout
    head_r = pygame.Rect(x - sc(30), y - sc(74) + bob, sc(60), sc(54))
    pygame.draw.rect(surface, (6, 6, 10), head_r.inflate(sc(10), sc(10)), border_radius=sc(12))
    pygame.draw.rect(surface, fur_d, head_r.inflate(sc(4), sc(4)), border_radius=sc(10))
    pygame.draw.rect(surface, fur, head_r, border_radius=sc(9))
    pygame.draw.polygon(surface, fur_m, [
        (x - sc(15), y - sc(36) + bob), (x + sc(15), y - sc(36) + bob),
        (x + sc(11), y - sc(2) + bob), (x - sc(11), y - sc(2) + bob)])
    pygame.draw.polygon(surface, fur_l, [
        (x - sc(10), y - sc(30) + bob), (x + sc(10), y - sc(30) + bob), (x, y - sc(8) + bob)])
    pygame.draw.ellipse(surface, (12, 10, 16), (x - sc(9), y - sc(14) + bob, sc(18), sc(13)))
    pygame.draw.rect(surface, (18, 16, 22), (x - sc(13), y - sc(8) + bob, sc(26), sc(11)))
    for fang_x in (-sc(9), -sc(3), sc(3), sc(9)):
        pygame.draw.polygon(surface, WHITE, [
            (x + fang_x - sc(2), y - sc(8) + bob), (x + fang_x + sc(2), y - sc(8) + bob),
            (x + fang_x, y + sc(8) + bob)])
    # ears
    pygame.draw.polygon(surface, fur_d, [
        (x - sc(32), y - sc(64) + bob), (x - sc(17), y - sc(104) + bob), (x - sc(6), y - sc(64) + bob)])
    pygame.draw.polygon(surface, (200, 90, 110), [
        (x - sc(27), y - sc(66) + bob), (x - sc(17), y - sc(92) + bob), (x - sc(10), y - sc(66) + bob)])
    pygame.draw.polygon(surface, fur_d, [
        (x + sc(32), y - sc(64) + bob), (x + sc(17), y - sc(104) + bob), (x + sc(6), y - sc(64) + bob)])
    pygame.draw.polygon(surface, (200, 90, 110), [
        (x + sc(27), y - sc(66) + bob), (x + sc(17), y - sc(92) + bob), (x + sc(10), y - sc(66) + bob)])
    # eyes
    eye_glow = pygame.Surface((sc(90), sc(44)), pygame.SRCALPHA)
    pygame.draw.ellipse(eye_glow, (255, 35, 25, int(100 + 70 * pulse)), (sc(4), sc(4), sc(34), sc(24)))
    pygame.draw.ellipse(eye_glow, (255, 35, 25, int(100 + 70 * pulse)), (sc(50), sc(4), sc(34), sc(24)))
    surface.blit(eye_glow, (x - sc(44), y - sc(62) + bob), special_flags=pygame.BLEND_RGBA_ADD)
    pygame.draw.ellipse(surface, eye, (x - sc(22), y - sc(58) + bob, sc(18), sc(13)))
    pygame.draw.ellipse(surface, eye, (x + sc(4), y - sc(58) + bob, sc(18), sc(13)))
    pygame.draw.ellipse(surface, gold, (x - sc(16), y - sc(55) + bob, sc(8), sc(7)))
    pygame.draw.ellipse(surface, gold, (x + sc(10), y - sc(55) + bob, sc(8), sc(7)))

    # tail
    for i in range(8):
        tx = x - sc(36) - i * sc(9)
        ty = y + sc(14) + bob + int(math.sin(t * 0.02 + i * 0.5) * sc(6)) + i * sc(3)
        pygame.draw.circle(surface, fur_d if i % 2 == 0 else fur, (tx, ty), sc(12 - i))

    if not boss:
        left = max(0, werewolf_until - t)
        frac = left / 20000.0
        pygame.draw.circle(surface, (255, 60, 40), (x, y - sc(120)), sc(16), 2)
        if frac > 0:
            pygame.draw.arc(surface, gold, (x - sc(16), y - sc(136), sc(32), sc(32)),
                            -1.57, -1.57 + math.tau * frac, max(3, sc(5)))
        lab = FONT_TINY.render("WEREWOLF", True, (255, 120, 80))
        surface.blit(lab, (x - lab.get_width() // 2, y - sc(148)))
        for i in range(6):
            a = t * 0.01 + i * 1.1
            pygame.draw.circle(surface, gold,
                               (int(x + math.cos(a) * sc(24)), int(y - sc(120) + math.sin(a) * sc(9))), 2)
    else:
        lab = FONT_SMALL.render("AntonXD", True, gold)
        surface.blit(lab, (x - lab.get_width() // 2, y - sc(130)))


def draw_player(surface, x, y, character_name=None):
    character_name = character_name or selected_character
    x = int(x)
    y = int(y)
    t = pygame.time.get_ticks()
    if werewolf_until and t < werewolf_until:
        draw_werewolf(surface, x, y)
        return
    if executor_until and t < executor_until and (character_name or selected_character) == "Executor":
        draw_executor_form(surface, x, y)
        return
    bob = int(math.sin(t * 0.008) * 2)

    mx, my = pygame.mouse.get_pos()
    angle = math.atan2(my - y, mx - x)
    dx, dy = math.cos(angle), math.sin(angle)
    side_x, side_y = -dy, dx

    hit = pygame.time.get_ticks() < player_flash_until

    # Character palette
    palettes = {
        "Ninja": ((200, 165, 130), (90, 55, 40), BLACK, (255, 45, 85)),
        "Engineer": ((240, 195, 145), (175, 130, 90), (55, 40, 25), (255, 200, 40)),
        "Time Lord": ((225, 190, 165), (160, 120, 95), (190, 110, 255), (190, 110, 255)),
        "Frozen": ((195, 230, 250), (70, 150, 190), (90, 230, 255), (90, 230, 255)),
        "Scientist": ((235, 200, 155), (170, 130, 95), (40, 80, 45), (120, 255, 90)),
        "Magician": ((220, 175, 145), (145, 90, 170), (90, 35, 130), (210, 70, 255)),
        "Survivor": ((235, 185, 140), (175, 125, 85), (50, 35, 25), (70, 170, 255)),
        "Reaper": ((240, 225, 210), (150, 155, 170), (18, 19, 24), (180, 210, 255)),
        "Storm Sovereign": ((230, 240, 255), (140, 160, 190), (18, 30, 50), (100, 220, 255)),
        "Executor": ((245, 220, 200), (160, 110, 90), (40, 12, 12), (255, 60, 40)),
        "Priest": ((240, 220, 195), (180, 150, 120), (230, 230, 240), (255, 230, 120)),
    }
    base_skin, dark_skin, hair, accent = palettes.get(
        character_name, palettes["Survivor"]
    )
    _sk = current_class_skin(character_name)
    if not _sk.get("base"):
        _acc, _body, _suit, _suit_d = class_palette(character_name)
        base_skin, dark_skin, hair, accent = _body, _dim(_body, 0.72), _suit_d, _acc

    if hit:
        base_skin = dark_skin = hair = accent = WHITE

    # Ground shadow (cached)
    global _PLAYER_SHADOW
    if _PLAYER_SHADOW is None:
        _PLAYER_SHADOW = pygame.Surface((70, 34), pygame.SRCALPHA)
        pygame.draw.ellipse(_PLAYER_SHADOW, (0, 0, 0, 105), _PLAYER_SHADOW.get_rect())
    surface.blit(_PLAYER_SHADOW, _PLAYER_SHADOW.get_rect(center=(x, y + 27)))

    # Legs / boots — top-down pixel character
    leg_y = y + 16 + bob
    for off in (-9, 9):
        pygame.draw.rect(surface, BLACK, (x + off - 6, leg_y - 1, 12, 19))
        pygame.draw.rect(surface, PANTS, (x + off - 4, leg_y, 8, 13))
        pygame.draw.rect(surface, BOOT, (x + off - 7, leg_y + 10, 14, 8))

    # Torso with outline
    body = pygame.Rect(x - 18, y - 3 + bob, 36, 37)
    pygame.draw.rect(surface, BLACK, body.inflate(5, 5), border_radius=6)
    shirt = {
        "Ninja": (28, 28, 38),
        "Engineer": (200, 140, 30),
        "Time Lord": (70, 40, 120),
        "Frozen": (40, 100, 145),
        "Scientist": (55, 95, 55),
        "Magician": (90, 35, 130),
        "Survivor": (50, 110, 210),
        "Reaper": (22, 26, 38),
        "Storm Sovereign": (24, 48, 80),
        "Executor": (50, 14, 14),
        "Priest": (230, 230, 240),
    }.get(character_name, SHIRT)
    if not _sk.get("base"):
        shirt = class_palette(character_name)[2]
    if hit:
        shirt = WHITE
    pygame.draw.rect(surface, shirt, body, border_radius=5)
    pygame.draw.rect(surface, SHIRT_DARK if character_name == "Survivor" and not hit else dark_skin,
                     (x - 13, y + 13 + bob, 26, 15), border_radius=3)

    # Backpack / character details
    if character_name == "Scientist":
        pygame.draw.rect(surface, BLACK, (x - 24, y + 2 + bob, 7, 22))
        pygame.draw.rect(surface, CYAN, (x - 22, y + 4 + bob, 4, 18))
    elif character_name == "Ninja":
        pygame.draw.rect(surface, RED, (x - 23, y + 1 + bob, 7, 3))
        pygame.draw.rect(surface, RED, (x + 16, y + 1 + bob, 7, 3))
    elif character_name == "Engineer":
        pygame.draw.rect(surface, GOLD, (x - 22, y + 1 + bob, 7, 4))
        pygame.draw.rect(surface, STONE, (x + 15, y + 4 + bob, 9, 18))
    elif character_name == "Time Lord":
        pygame.draw.rect(surface, GOLD, (x - 12, y + 8 + bob, 24, 4))
    elif character_name == "Frozen":
        pygame.draw.rect(surface, CYAN, (x - 10, y + 17 + bob, 20, 4))
    elif character_name == "Magician":
        pygame.draw.rect(surface, PURPLE, (x - 15, y + 20 + bob, 30, 5))
    elif character_name == "Reaper":
        pygame.draw.rect(surface, accent, (x - 14, y + 4 + bob, 28, 3))
        pygame.draw.rect(surface, accent, (x - 3, y + 4 + bob, 6, 20))
        pygame.draw.rect(surface, (18, 19, 24), (x - 24, y - 1 + bob, 8, 26), border_radius=3)
    elif character_name == "Storm Sovereign":
        # storm mantle + lightning core
        pygame.draw.rect(surface, accent, (x - 16, y + 2 + bob, 32, 4))
        pygame.draw.circle(surface, accent, (x, y + 14 + bob), 6)
        pygame.draw.circle(surface, WHITE, (x, y + 14 + bob), 3)
        pygame.draw.rect(surface, (12, 20, 36), (x - 22, y - 2 + bob, 8, 28), border_radius=3)

    # Arms reach toward the gun
    hand1_x = x + int(dx * 27 + side_x * 8)
    hand1_y = y + int(dy * 27 + side_y * 8) + bob
    hand2_x = x + int(dx * 27 - side_x * 8)
    hand2_y = y + int(dy * 27 - side_y * 8) + bob
    arm_color = dark_skin
    if hit:
        arm_color = WHITE

    for hx, hy in ((hand1_x, hand1_y), (hand2_x, hand2_y)):
        pygame.draw.line(surface, BLACK, (x + int(dx * 10), y + int(dy * 10) + bob),
                         (hx, hy), 11)
        pygame.draw.line(surface, arm_color, (x + int(dx * 10), y + int(dy * 10) + bob),
                         (hx, hy), 7)
        pygame.draw.rect(surface, BLACK, (hx - 7, hy - 7, 14, 14))
        pygame.draw.rect(surface, base_skin, (hx - 5, hy - 5, 10, 10))

    # Head
    head = pygame.Rect(x - 17, y - 35 + bob, 34, 32)
    pygame.draw.rect(surface, BLACK, head.inflate(5, 5), border_radius=4)
    pygame.draw.rect(surface, dark_skin, head, border_radius=3)
    pygame.draw.rect(surface, base_skin, (x - 13, y - 31 + bob, 26, 24), border_radius=2)

    # Hair / helmet / hat
    if character_name == "Ninja":
        pygame.draw.rect(surface, BLACK, (x - 17, y - 34 + bob, 34, 9))
        pygame.draw.rect(surface, RED, (x + 10, y - 30 + bob, 16, 3))
    elif character_name == "Time Lord":
        pygame.draw.rect(surface, GOLD, (x - 18, y - 40 + bob, 36, 6))
        pygame.draw.rect(surface, GOLD, (x - 12, y - 44 + bob, 24, 5))
    elif character_name == "Scientist":
        pygame.draw.rect(surface, WHITE, (x - 20, y - 41 + bob, 40, 7))
        pygame.draw.rect(surface, CYAN, (x - 12, y - 40 + bob, 24, 2))
    elif character_name == "Magician":
        pygame.draw.polygon(surface, PURPLE, [
            (x - 20, y - 31 + bob), (x + 20, y - 31 + bob),
            (x, y - 53 + bob)
        ])
    elif character_name == "Frozen":
        pygame.draw.rect(surface, CYAN, (x - 17, y - 40 + bob, 34, 7))
        pygame.draw.rect(surface, WHITE, (x - 11, y - 44 + bob, 22, 4))
    elif character_name == "Reaper":
        hood = hair if hit is False else WHITE
        pygame.draw.polygon(surface, hood, [
            (x - 20, y - 2 + bob), (x - 19, y - 33 + bob), (x, y - 45 + bob),
            (x + 19, y - 33 + bob), (x + 20, y - 2 + bob),
        ])
        pygame.draw.polygon(surface, (6, 6, 9), [
            (x - 13, y - 6 + bob), (x - 12, y - 29 + bob), (x, y - 37 + bob),
            (x + 12, y - 29 + bob), (x + 13, y - 6 + bob),
        ])
        for ex in (-6, 6):
            pygame.draw.rect(surface, accent, (x + ex - 2, y - 24 + bob, 5, 4))
        pygame.draw.rect(surface, accent, (x - 20, y - 4 + bob, 40, 2))
    elif character_name == "Storm Sovereign":
        # storm crown
        crown = accent if not hit else WHITE
        pygame.draw.polygon(surface, crown, [
            (x - 18, y - 32 + bob), (x - 12, y - 48 + bob), (x - 4, y - 36 + bob),
            (x, y - 52 + bob), (x + 4, y - 36 + bob), (x + 12, y - 48 + bob),
            (x + 18, y - 32 + bob),
        ])
        pygame.draw.rect(surface, hair, (x - 16, y - 34 + bob, 32, 6))
        for ex in (-6, 6):
            pygame.draw.rect(surface, accent, (x + ex - 2, y - 24 + bob, 5, 5))
    else:
        pygame.draw.rect(surface, hair, (x - 15, y - 36 + bob, 30, 8))
        pygame.draw.rect(surface, hair, (x - 10, y - 40 + bob, 20, 5))

    # Eyes follow aim direction
    eye_shift = 4 if dx >= 0 else -4
    pygame.draw.rect(surface, BLACK, (x - 8 + eye_shift, y - 24 + bob, 5, 6))
    pygame.draw.rect(surface, BLACK, (x + 3 + eye_shift, y - 24 + bob, 5, 6))

    # Tiny directional visor highlight
    pygame.draw.rect(surface, WHITE, (x + (7 if dx > 0 else -12), y - 15 + bob, 5, 2))


# =========================================================
# PIXEL HELD GUN — TEMPLATE ASSETS
# =========================================================
def draw_held_gun(surface, x, y, angle):
    if werewolf_until and pygame.time.get_ticks() < werewolf_until:
        return  # claws are part of the werewolf body
    """Procedurally drawn, supersampled weapons with recoil, heat glow and muzzle FX."""
    x, y = int(x), int(y)
    t = pygame.time.get_ticks()
    since = t - last_shot

    art = _gun_art(gun_level, is_melee_class())
    length = art.get_width()

    # recoil: weapon kicks back along the aim line right after a shot
    kick = 0.0
    if since < 130:
        kick = 9.0 * (1.0 - since / 130.0) ** 2
    px = x - math.cos(angle) * kick
    py = y - math.sin(angle) * kick

    # keep the weapon upright when the player aims to the left
    if math.cos(angle) < 0:
        art = pygame.transform.flip(art, False, True)
    rotated = pygame.transform.rotate(art, -math.degrees(angle))
    surface.blit(rotated, rotated.get_rect(center=(int(px), int(py))))

    muzzle_d = length * 0.46
    fx = px + math.cos(angle) * muzzle_d
    fy = py + math.sin(angle) * muzzle_d

    if is_melee_class():
        # Blades get a trailing edge shimmer instead of gunfire effects.
        if since < 190:
            fade = 1.0 - since / 190.0
            acc = _cmix(gun_palette()["accent"], (255, 255, 255), 0.35)
            tr = pygame.Surface((length + 40, length + 40), pygame.SRCALPHA)
            cc = tr.get_width() // 2
            for i in range(5, 0, -1):
                pygame.draw.circle(tr, (*acc, int(16 * fade * (i / 5.0) ** 2)), (cc, cc), int(length * 0.5 * i / 5))
            surface.blit(tr, tr.get_rect(center=(int(fx), int(fy))))
        return

    # heat glow on the barrel tip for the fast/heavy weapons
    if gun_level >= 4 and since < 900:
        heat = max(0.0, 1.0 - since / 900.0)
        hg = pygame.Surface((40, 40), pygame.SRCALPHA)
        col = {5: (255, 90, 50), 6: (255, 140, 50), 7: (255, 110, 40),
               8: (120, 240, 255)}.get(gun_level, (255, 170, 60))
        for r in range(9, 0, -1):
            pygame.draw.circle(hg, (*col, int(20 * heat * (r / 9.0) ** 2)), (20, 20), r * 2)
        surface.blit(hg, hg.get_rect(center=(int(fx), int(fy))))

    # muzzle flash
    if since < 90:
        fade = 1.0 - since / 90.0
        size = int(78 * (0.55 + 0.45 * fade))
        flash = pygame.Surface((size, size), pygame.SRCALPHA)
        c = size // 2
        big = size * 0.46
        # soft bloom
        for r in range(10, 0, -1):
            pygame.draw.circle(flash, (255, 200, 90, int(26 * fade * (r / 10.0) ** 2)), (c, c), int(big * r / 10))
        # star burst
        pygame.draw.polygon(flash, (255, 214, 90, int(240 * fade)), [
            (c + big, c), (c + big * 0.28, c - big * 0.34), (c, c - big * 0.62),
            (c - big * 0.20, c - big * 0.26), (c - big * 0.42, c),
            (c - big * 0.20, c + big * 0.26), (c, c + big * 0.62), (c + big * 0.28, c + big * 0.34)])
        pygame.draw.polygon(flash, (255, 255, 224, int(250 * fade)), [
            (c + big * 0.62, c), (c + big * 0.16, c - big * 0.20), (c, c - big * 0.34),
            (c - big * 0.12, c - big * 0.14), (c - big * 0.24, c),
            (c - big * 0.12, c + big * 0.14), (c, c + big * 0.34), (c + big * 0.16, c + big * 0.20)])
        rot = pygame.transform.rotate(flash, -math.degrees(angle))
        surface.blit(rot, rot.get_rect(center=(int(fx), int(fy))))

        # sparks
        for i in range(5):
            sa = angle + random.uniform(-0.5, 0.5)
            sd = random.uniform(10, 34) * fade
            pygame.draw.circle(surface, (255, 230, 150),
                               (int(fx + math.cos(sa) * sd), int(fy + math.sin(sa) * sd)),
                               random.randint(1, 3))

    # lingering smoke puff
    if 60 <= since < 520:
        p = (since - 60) / 460.0
        sm = pygame.Surface((54, 54), pygame.SRCALPHA)
        pygame.draw.circle(sm, (160, 160, 170, int(70 * (1 - p))), (27, 27), int(6 + 16 * p))
        surface.blit(sm, sm.get_rect(center=(int(fx + math.cos(angle) * 12 * p),
                                             int(fy + math.sin(angle) * 12 * p - 10 * p))))

    # ejected shell casing
    if since < 320 and gun_level in (1, 2, 3, 4):
        p = since / 320.0
        ex = px + math.cos(angle - 1.8) * (16 + 40 * p)
        ey = py + math.sin(angle - 1.8) * (16 + 40 * p) - 26 * p + 44 * p * p
        shell = pygame.Surface((9, 5), pygame.SRCALPHA)
        pygame.draw.rect(shell, (214, 172, 66), (0, 0, 9, 5), border_radius=2)
        pygame.draw.rect(shell, (255, 226, 150), (0, 0, 9, 2))
        surface.blit(pygame.transform.rotate(shell, -p * 620), (int(ex), int(ey)))


_GUN_ART_CACHE = {}

GUN_MAX_LEVEL = 8
GUN_TIER_NAMES = {1: "PISTOL", 2: "DUAL PISTOLS", 3: "SHOTGUN", 4: "SMG", 5: "RPG",
                  6: "MINIGUN", 7: "FLAMETHROWER", 8: "PLASMA RIFLE"}
BLADE_TIER_NAMES = {
    1: "1 KATANA",
    2: "2 KATANA",
    3: "3 KATANA",
    4: "SUN BLADE",
    5: "DUAL FLAME",
    6: "TRIPLE INFERNO",
    7: "HAKI FLAME",
    8: "BANKAI HAKI",
}


def _gun_art(level, melee=False, skin_key=None):
    key = (level, skin_key or equipped_gun_skin, melee)
    art = _GUN_ART_CACHE.get(key)
    if art is None:
        art = _build_katana_art(level, skin_key) if melee else _build_gun_art(level, skin_key)
        _GUN_ART_CACHE[key] = art
    return art


def _gun_pal(skin_key=None):
    p = gun_palette(skin_key)
    return (p["steel_d"], p["steel"], p["steel_l"], p["shine"], p["poly"],
            p["accent"], p["wood"], p["wood_l"])


def _cmix(a, b, t):
    return (int(a[0] + (b[0] - a[0]) * t), int(a[1] + (b[1] - a[1]) * t), int(a[2] + (b[2] - a[2]) * t))


def _build_katana_art(level, skin_key=None):
    """Anime katana for the Shinigami class, facing right, supersampled then downscaled."""
    SS = 4
    W, H = {1: (104, 44), 2: (110, 62), 3: (118, 72)}.get(level, (130 + min(3, max(0, level - 4)) * 4, 74))
    SD, ST, SL, SH, PL, AC, WD, WL = _gun_pal(skin_key)
    s = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
    k = SS
    sk_key = skin_key or equipped_gun_skin
    void_black = (sk_key == "void_black")
    if void_black:
        # Full black blade, pure white edge / outline
        SD, ST, SL = (0, 0, 0), (6, 6, 8), (14, 14, 18)
        SH, PL, AC = (255, 255, 255), (0, 0, 0), (255, 255, 255)
        WD, WL = (4, 4, 6), (255, 255, 255)
        EDGE = (255, 255, 255)
    else:
        EDGE = _cmix(SH, (255, 255, 255), 0.55)

    def PGn(pts, col):
        pygame.draw.polygon(s, col, [(int(p[0] * k), int(p[1] * k)) for p in pts])

    def LN(p1, p2, col, w):
        pygame.draw.line(s, col, (int(p1[0] * k), int(p1[1] * k)), (int(p2[0] * k), int(p2[1] * k)),
                         max(1, int(w * k)))

    def CIn(x, y, r, col, w=0):
        pygame.draw.circle(s, col, (int(x * k), int(y * k)), max(1, int(r * k)),
                           0 if w == 0 else max(1, int(w * k)))

    def curve_pts(my, hilt_x, tip_x, thick, curve, off=0.0, top=True):
        """Sample one side of the sori (curved blade). Edge faces up."""
        pts = []
        N = 16
        span = tip_x - hilt_x
        for i in range(N + 1):
            t = i / N
            x = hilt_x + span * t
            y = my - curve * (t ** 1.7)                      # blade sweeps upward to the tip
            taper = thick * (1.0 - 0.72 * max(0.0, (t - 0.62) / 0.38) ** 1.5)
            pts.append((x, y - taper - off if top else y + taper * 0.86 + off))
        return pts

    def blade(my, hilt_x, tip_x, thick, curve, mode="normal"):
        # Element recolors the METAL of the blade (not only edge glow)
        local_SL, local_ST, local_EDGE = SL, ST, EDGE
        if not void_black:
            if mode == "fire":
                local_SL = (255, 120, 30)       # hot orange metal
                local_ST = (180, 50, 10)
                local_EDGE = (255, 230, 120)    # bright flame edge
            elif mode == "haki":
                local_SL = (120, 60, 220)       # electric purple metal
                local_ST = (50, 20, 100)
                local_EDGE = (200, 180, 255)
            elif mode == "bankai":
                # last tier: flame + electric on metal
                local_SL = (255, 70, 40)        # fire base
                local_ST = (80, 20, 140)        # electric undertone
                local_EDGE = (180, 220, 255)    # electric edge
        # silhouette (thicker white outline for VOID BLACK)
        out_off = 1.8 if void_black else 1.1
        outline = curve_pts(my, hilt_x, tip_x, thick, curve, out_off, True) + \
            list(reversed(curve_pts(my, hilt_x, tip_x, thick, curve, out_off, False)))
        PGn(outline, (255, 255, 255) if void_black else (9, 10, 13))
        # steel body (element-tinted)
        body = curve_pts(my, hilt_x, tip_x, thick, curve, 0.0, True) + \
            list(reversed(curve_pts(my, hilt_x, tip_x, thick, curve, 0.0, False)))
        PGn(body, (8, 8, 10) if void_black else local_SL)
        # shinogi band
        band = curve_pts(my, hilt_x, tip_x, thick, curve, 0.0, True) + \
            list(reversed(curve_pts(my, hilt_x, tip_x, thick * 0.16, curve, 0.0, True)))
        PGn(band, local_EDGE if not void_black else EDGE)
        if void_black:
            # extra white edge line so the blade reads clearly on dark arenas
            hm2 = curve_pts(my, hilt_x, tip_x, thick * 0.05, curve, 0.0, True)
            for i in range(len(hm2) - 1):
                LN(hm2[i], hm2[i + 1], (255, 255, 255), 1.4)
        # dark ji (lower flat)
        low = curve_pts(my, hilt_x, tip_x, thick * 0.34, curve, 0.0, False) + \
            list(reversed(curve_pts(my, hilt_x, tip_x, thick, curve, 0.0, False)))
        PGn(low, _cmix(local_ST if not void_black else ST, (0, 0, 0), 0.42))
        # hamon: wavy temper line
        hm = curve_pts(my, hilt_x, tip_x, thick * 0.52, curve, 0.0, True)
        for i in range(len(hm) - 1):
            wob = 0.5 if i % 2 == 0 else -0.5
            LN((hm[i][0], hm[i][1] + wob), (hm[i + 1][0], hm[i + 1][1] - wob), _cmix(SH, WHITE, 0.2), 0.9)
        # kissaki glint near the point
        tp = curve_pts(my, hilt_x, tip_x, thick, curve, 0.0, True)[-1]
        LN((tp[0] - 13, tp[1] + 1.6), (tp[0] - 1, tp[1]), (255, 255, 255), 1.3)

        # ---- habaki collar ----
        PGn([(hilt_x - 1, my - thick - 1.5), (hilt_x + 9, my - thick - 1.5),
             (hilt_x + 9, my + thick), (hilt_x - 1, my + thick)], _cmix(AC, WHITE, 0.3))
        LN((hilt_x + 4, my - thick), (hilt_x + 4, my + thick), _cmix(AC, (0, 0, 0), 0.3), 0.8)

        # ---- circular tsuba (anime round guard) ----
        gr = thick + 5.5
        CIn(hilt_x - 2, my, gr, (10, 11, 14))
        CIn(hilt_x - 2, my, gr - 1.1, AC)
        CIn(hilt_x - 2, my, gr - 3.4, _cmix(AC, (0, 0, 0), 0.45))
        CIn(hilt_x - 2, my, gr - 1.1, _cmix(AC, WHITE, 0.55), 0.9)

        # ---- tsuka: wrapped handle with diamond ito ----
        hl = 30.0
        hx0, hx1 = hilt_x - 4 - hl, hilt_x - 4
        PGn([(hx0, my - 4.6), (hx1, my - 4.2), (hx1, my + 4.2), (hx0, my + 4.6)], (13, 14, 18))
        PGn([(hx0 + 0.8, my - 3.8), (hx1, my - 3.4), (hx1, my + 3.4), (hx0 + 0.8, my + 3.8)], WD)
        for i in range(7):
            xx = hx0 + 1.6 + i * (hl - 3) / 7.0
            LN((xx, my - 3.6), (xx + 3.4, my + 3.6), WL, 1.1)
            LN((xx + 3.4, my - 3.6), (xx, my + 3.6), _cmix(WL, (0, 0, 0), 0.25), 1.1)
        CIn(hx0 + hl * 0.5, my, 1.5, _cmix(AC, WHITE, 0.4))
        # kashira end cap
        PGn([(hx0 - 3.4, my - 5), (hx0 + 1.5, my - 4.6), (hx0 + 1.5, my + 4.6), (hx0 - 3.4, my + 5)], AC)
        PGn([(hx0 - 2.6, my - 4), (hx0 + 0.6, my - 3.7), (hx0 + 0.6, my - 1.4), (hx0 - 2.6, my - 1.8)],
            _cmix(AC, WHITE, 0.5))
        # sageo cord fluttering off the pommel
        LN((hx0 - 2, my + 3), (hx0 - 9, my + 8), _cmix(AC, (0, 0, 0), 0.2), 1.2)
        LN((hx0 - 9, my + 8), (hx0 - 4, my + 12), _cmix(AC, (0, 0, 0), 0.2), 1.2)
        return curve_pts(my, hilt_x, tip_x, thick, curve, 0.0, True)

    # Multi-blade layouts matching Reaper tier table
    # 1:1 normal  2:2 normal  3:3 normal  4:1 fire+2n  5:2 fire+1n  6:3 fire  7:3 haki  8:3 bankai
    layouts = {
        1: [(H * 0.55, "normal")],
        2: [(H * 0.28, "normal"), (H * 0.72, "normal")],
        3: [(H * 0.20, "normal"), (H * 0.50, "normal"), (H * 0.80, "normal")],
        4: [(H * 0.22, "fire"), (H * 0.50, "normal"), (H * 0.78, "normal")],
        5: [(H * 0.22, "fire"), (H * 0.50, "fire"), (H * 0.78, "normal")],
        6: [(H * 0.20, "fire"), (H * 0.50, "fire"), (H * 0.80, "fire")],
        7: [(H * 0.20, "haki"), (H * 0.50, "haki"), (H * 0.80, "haki")],
        8: [(H * 0.18, "bankai"), (H * 0.50, "bankai"), (H * 0.82, "bankai")],
    }
    edges = []
    for my, mode in layouts.get(level, layouts[1]):
        thick = 4.4 if level <= 3 else 5.4
        curve = 7 if level <= 3 else 10
        tip_x = W - 5 if mode == "normal" else W - 3
        blade(my, 40, tip_x, thick, curve, mode)
        edges.append((my, thick, curve, mode))
        # elemental edge glow + extra bankai dual glow
        if mode != "normal":
            gcol = {"fire": (255, 140, 40), "haki": (160, 100, 255), "bankai": (255, 50, 40)}[mode]
            g = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
            pts = curve_pts(my, 40, tip_x, thick, curve, 0.0, True)
            for i in range(8, 0, -1):
                pygame.draw.lines(g, (*gcol, int(40 * (i / 8.0) ** 2)), False,
                                  [(int(p[0] * k), int(p[1] * k)) for p in pts], max(1, int(i * 1.8 * k)))
            s.blit(g, (0, 0))
            if mode == "bankai":
                # electric secondary glow on top of flame metal
                g2 = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
                for i in range(5, 0, -1):
                    pygame.draw.lines(g2, (120, 200, 255, int(50 * (i / 5.0))), False,
                                      [(int(p[0] * k), int(p[1] * k - 2 * k)) for p in pts],
                                      max(1, int(i * 1.2 * k)))
                s.blit(g2, (0, 0))
            if mode == "fire":
                # flame tongues near tip
                tip = pts[-1]
                for j in range(4):
                    CIn(tip[0] - 4 - j * 3, tip[1] - 2 - j, 1.2 + j * 0.3,
                        (255, 180 - j * 30, 40))
    if void_black:
        # soft white outline glow around the whole blade art
        glow = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
        mask = pygame.mask.from_surface(s)
        outline_pts = mask.outline(every=2)
        if len(outline_pts) > 2:
            pygame.draw.lines(glow, (255, 255, 255, 120), True, outline_pts, max(2, int(2 * k)))
        s.blit(glow, (0, 0))
    return pygame.transform.smoothscale(s, (W, H))


def _build_gun_art(level, skin_key=None):
    """Build one weapon facing right, at 4x, then downscale for clean edges."""
    SS = 4
    specs = {1: (74, 40), 2: (76, 56), 3: (104, 42), 4: (108, 46), 5: (124, 54),
             6: (140, 62), 7: (132, 58), 8: (136, 56)}
    W, H = specs.get(level, (90, 44))
    s = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
    k = SS
    cy = H * SS // 2

    STEEL_D, STEEL, STEEL_L, SHINE, POLY, ACC, WOODC, WOODL = _gun_pal(skin_key)
    GRIP_D = _cmix(POLY, (0, 0, 0), 0.25)
    GRIP_L = _cmix(POLY, STEEL, 0.55)
    CASE = _cmix(STEEL_D, POLY, 0.5)
    CASE_L = _cmix(STEEL, STEEL_L, 0.35)

    def R(x, y, w, h, col, rad=0):
        pygame.draw.rect(s, col, (int(x * k), int(y * k), max(1, int(w * k)), max(1, int(h * k))),
                         border_radius=int(rad * k))

    def outline(x, y, w, h, rad=0):
        pygame.draw.rect(s, (10, 11, 14), (int(x * k) - 2, int(y * k) - 2, int(w * k) + 4, int(h * k) + 4),
                         border_radius=int(rad * k) + 2)

    def PGn(pts, col):
        pygame.draw.polygon(s, col, [(int(p[0] * k), int(p[1] * k)) for p in pts])

    def CIR(x, y, r, col, width=0):
        pygame.draw.circle(s, col, (int(x * k), int(y * k)), max(1, int(r * k)), int(width * k))

    def glow(x, y, r, col, strength=26):
        g = pygame.Surface((s.get_width(), s.get_height()), pygame.SRCALPHA)
        for i in range(9, 0, -1):
            pygame.draw.circle(g, (*col, int(strength * (i / 9.0) ** 2)),
                               (int(x * k), int(y * k)), int(r * k * (10 - i) / 9.0))
        s.blit(g, (0, 0))

    def barrel(x, y, w, h, tip=True):
        """Barrel with a top highlight and a dark underside."""
        outline(x, y, w, h, 2)
        R(x, y, w, h, STEEL, 2)
        R(x, y, w, max(1, h * 0.34), STEEL_L, 2)
        R(x, y + h * 0.74, w, max(1, h * 0.26), STEEL_D, 2)
        pygame.draw.line(s, SHINE, (int(x * k), int((y + h * 0.22) * k)),
                         (int((x + w) * k), int((y + h * 0.22) * k)), max(1, int(1.2 * k)))
        if tip:
            R(x + w - 3, y - 1, 3, h + 2, (16, 17, 21), 1)

    if level == 1:  # ---------------- PISTOL ----------------
        my = H / 2
        outline(10, my - 5, 30, 12, 3)
        R(10, my - 5, 30, 12, POLY, 3)                     # slide rear
        barrel(24, my - 4.5, 34, 9)                        # slide/barrel
        R(26, my - 6.5, 16, 3, STEEL_L, 1)                 # rear sight rail
        R(52, my - 7, 4, 3, STEEL_D, 1)                    # front sight
        PGn([(12, my + 6), (26, my + 6), (22, my + 22), (10, my + 22)], GRIP_D)  # grip
        PGn([(13, my + 7), (24, my + 7), (21, my + 20), (12, my + 20)], GRIP_L)
        for i in range(4):                                  # grip texture
            pygame.draw.line(s, _cmix(GRIP_L, STEEL_L, 0.4), (int(14 * k), int((my + 9 + i * 3) * k)),
                             (int(23 * k), int((my + 9 + i * 3) * k)), max(1, int(0.8 * k)))
        PGn([(26, my + 6), (33, my + 6), (31, my + 13), (27, my + 13)], GRIP_D)  # trigger guard
        R(27, my + 6.5, 3, 5, ACC, 1)                       # trigger
        R(38, my - 3, 5, 6, ACC, 1)                         # ejection port accent

    elif level == 2:  # ---------------- DUAL PISTOLS ----------------
        for n, oy in enumerate((H * 0.28, H * 0.72)):
            my = oy
            outline(12, my - 4.5, 26, 10, 3)
            R(12, my - 4.5, 26, 10, POLY, 3)
            barrel(24, my - 4, 32, 8)
            R(50, my - 6, 4, 2.5, STEEL_D, 1)
            PGn([(14, my + 5), (26, my + 5), (23, my + 17), (13, my + 17)], GRIP_D)
            PGn([(15, my + 6), (24, my + 6), (22, my + 15), (14, my + 15)], GRIP_L)
            PGn([(26, my + 5), (32, my + 5), (30, my + 11), (27, my + 11)], GRIP_D)
            R(27, my + 5.5, 3, 4, ACC, 1)
            R(36, my - 2.5, 4, 5, ACC, 1)

    elif level == 3:  # ---------------- SHOTGUN ----------------
        my = H / 2
        PGn([(6, my + 1), (24, my - 4), (24, my + 12), (8, my + 15)], _cmix(WOODC, (0, 0, 0), 0.4))
        PGn([(8, my + 2), (22, my - 2), (22, my + 10), (10, my + 12)], WOODC)
        pygame.draw.line(s, WOODL, (int(10 * k), int((my + 4) * k)), (int(21 * k), int((my + 1) * k)),
                         max(1, int(1.4 * k)))
        outline(22, my - 7, 30, 15, 3)
        R(22, my - 7, 30, 15, CASE, 3)                                                  # receiver
        R(23, my - 6, 28, 5, CASE_L, 2)
        barrel(48, my - 6, 50, 11)                                                      # main barrel
        R(48, my + 4, 46, 6, STEEL_D, 2)                                                # under-tube magazine
        R(50, my + 5, 42, 2, STEEL, 1)
        PGn([(34, my + 8), (48, my + 8), (46, my + 20), (32, my + 20)], _cmix(WOODC, (0, 0, 0), 0.4))
        PGn([(35, my + 9), (46, my + 9), (44, my + 18), (34, my + 18)], WOODC)
        PGn([(24, my + 8), (32, my + 8), (30, my + 16), (25, my + 16)], GRIP_D)
        R(25, my + 8.5, 4, 5, ACC, 1)
        R(92, my - 9, 4, 3, STEEL_D, 1)                                                 # bead sight
        R(28, my - 10, 18, 3, STEEL_L, 1)                                               # top rib

    elif level == 4:  # ---------------- SMG ----------------
        my = H / 2
        PGn([(4, my - 3), (18, my - 3), (18, my + 4), (4, my + 4)], POLY)                # folding stock
        R(4, my - 3, 3, 7, GRIP_L, 1)
        outline(16, my - 8, 40, 16, 3)
        R(16, my - 8, 40, 16, CASE, 3)                                                   # receiver
        R(17, my - 7, 38, 5, CASE_L, 2)
        for i in range(6):                                                                # cooling vents
            R(22 + i * 5, my - 4.5, 2.6, 6, (16, 17, 21), 1)
        barrel(54, my - 4.5, 40, 9)
        R(88, my - 6.5, 8, 13, GRIP_D, 2)                                                 # muzzle brake
        R(89, my - 5, 6, 3, STEEL_L, 1)
        R(20, my - 12, 26, 3.5, _cmix(STEEL, STEEL_D, 0.4), 1)                            # optic rail
        R(30, my - 17, 12, 6, GRIP_D, 2)                                                  # red-dot sight
        pygame.draw.circle(s, (255, 70, 70), (int(36 * k), int((my - 14) * k)), int(1.8 * k))
        PGn([(30, my + 8), (44, my + 8), (46, my + 26), (32, my + 26)], GRIP_D)            # magazine
        PGn([(31, my + 9), (43, my + 9), (45, my + 24), (33, my + 24)], GRIP_L)
        PGn([(18, my + 8), (28, my + 8), (26, my + 22), (17, my + 22)], GRIP_D)            # pistol grip
        PGn([(19, my + 9), (26, my + 9), (24, my + 20), (18, my + 20)], GRIP_L)
        R(28, my + 8.5, 3.5, 5, ACC, 1)                                                    # trigger
        R(60, my + 5, 16, 4, CASE, 1)                                                      # foregrip
        R(50, my - 2, 5, 5, ACC, 1)                                                        # tech accent

    elif level == 5:  # ---------------- RPG ----------------
        my = H / 2
        TUBE = _cmix(STEEL, (86, 96, 70), 0.45)
        TUBE_L = _cmix(TUBE, WHITE, 0.28)
        TUBE_D = _cmix(TUBE, (0, 0, 0), 0.45)
        outline(10, my - 9, 84, 18, 5)
        R(10, my - 9, 84, 18, TUBE, 5)                                                   # launch tube
        R(11, my - 8, 82, 5, TUBE_L, 4)
        R(11, my + 4, 82, 4, TUBE_D, 4)
        R(10, my - 10, 10, 20, TUBE_D, 4)                                                # rear blast cone
        PGn([(2, my - 13), (12, my - 9), (12, my + 9), (2, my + 13)], _cmix(TUBE, TUBE_D, 0.5))
        for i in range(3):                                                                # tube rings
            R(30 + i * 18, my - 10, 3, 20, TUBE_D, 2)
        R(22, my - 15, 30, 4, _cmix(TUBE, TUBE_L, 0.5), 1)                                # top rail
        R(30, my - 22, 16, 8, TUBE_D, 2)                                                  # scope
        pygame.draw.circle(s, (120, 210, 255), (int(38 * k), int((my - 18) * k)), int(2.4 * k))
        PGn([(28, my + 8), (40, my + 8), (38, my + 24), (26, my + 24)], GRIP_D)           # grip
        PGn([(29, my + 9), (38, my + 9), (36, my + 22), (28, my + 22)], GRIP_L)
        R(40, my + 8.5, 4, 5, ACC, 1)
        R(58, my + 8, 18, 5, TUBE_D, 2)                                                   # foregrip
        # warhead
        PGn([(92, my - 12), (104, my - 12), (116, my), (104, my + 12), (92, my + 12)], (150, 42, 38))
        PGn([(92, my - 10), (102, my - 10), (112, my), (102, my + 10), (92, my + 10)], (206, 66, 58))
        R(90, my - 13, 5, 26, (172, 52, 46), 2)
        pygame.draw.line(s, (255, 190, 90), (int(96 * k), int((my - 7) * k)),
                         (int(108 * k), int(my * k)), max(1, int(1.6 * k)))
        for fy_ in (-12, 12):                                                             # fins
            PGn([(90, my + fy_ * 0.7), (98, my + fy_ * 1.35), (92, my + fy_ * 1.35)], (120, 34, 30))

    elif level == 6:  # ---------------- MINIGUN ----------------
        my = H / 2
        # ammo drum
        outline(8, my - 4, 30, 30, 6)
        R(8, my - 4, 30, 30, CASE, 6)
        R(9, my - 3, 28, 8, CASE_L, 5)
        CIR(23, my + 11, 10, STEEL_D)
        CIR(23, my + 11, 7, STEEL)
        CIR(23, my + 11, 3.4, ACC)
        # receiver housing
        outline(30, my - 14, 34, 24, 4)
        R(30, my - 14, 34, 24, CASE, 4)
        R(31, my - 13, 32, 7, CASE_L, 3)
        for i in range(4):
            R(36 + i * 7, my - 4, 3, 9, (14, 15, 19), 1)
        # rotating barrel cluster
        for i, oy in enumerate((-9.5, -3.5, 2.5, 8.5)):
            shade = (STEEL_L if i in (0, 1) else STEEL)
            outline(62, my + oy - 2.6, 66, 5.4, 2)
            R(62, my + oy - 2.6, 66, 5.4, shade, 2)
            R(62, my + oy - 2.6, 66, 1.6, _cmix(shade, WHITE, 0.35), 2)
            R(124, my + oy - 3.2, 4, 6.6, (16, 17, 21), 1)
        # barrel shroud rings
        for rx in (66, 92, 116):
            R(rx, my - 14, 4, 28, STEEL_D, 2)
            R(rx, my - 14, 4, 8, STEEL_L, 2)
        # spade grip + trigger
        PGn([(30, my + 10), (44, my + 10), (42, my + 28), (28, my + 28)], GRIP_D)
        PGn([(31, my + 11), (42, my + 11), (40, my + 26), (30, my + 26)], GRIP_L)
        R(44, my + 11, 4, 5, ACC, 1)
        # heat accent
        glow(126, my, 6, ACC, 22)

    elif level == 7:  # ---------------- FLAMETHROWER ----------------
        my = H / 2
        # fuel tank on the back
        outline(4, my - 12, 26, 26, 10)
        R(4, my - 12, 26, 26, CASE, 10)
        R(5, my - 11, 24, 8, CASE_L, 8)
        R(6, my + 6, 22, 5, _cmix(CASE, (0, 0, 0), 0.35), 6)
        R(12, my - 4, 10, 10, (196, 60, 40), 3)
        R(13, my - 3, 8, 3, (240, 120, 80), 2)
        # pressure gauge
        CIR(26, my - 12, 5, STEEL_D)
        CIR(26, my - 12, 3.4, SHINE)
        # body / receiver
        outline(28, my - 8, 38, 17, 3)
        R(28, my - 8, 38, 17, CASE, 3)
        R(29, my - 7, 36, 5, CASE_L, 2)
        # fuel hose
        for i in range(9):
            CIR(30 + i * 3.4, my + 12 + math.sin(i * 0.9) * 2.2, 2.4, _cmix(POLY, STEEL, 0.35))
        # nozzle assembly
        barrel(64, my - 5, 44, 10)
        R(104, my - 8, 10, 16, STEEL_D, 3)
        R(105, my - 6.5, 8, 4, STEEL_L, 2)
        for i in range(3):                                       # nozzle vents
            R(92 + i * 5, my - 9.5, 2.6, 4, (16, 17, 21), 1)
        # pilot flame at the tip
        PGn([(114, my - 4), (126, my - 1), (114, my + 4)], (255, 170, 50))
        PGn([(114, my - 2), (122, my), (114, my + 2)], (255, 236, 170))
        glow(120, my, 8, (255, 150, 60), 30)
        # grips
        PGn([(34, my + 9), (46, my + 9), (44, my + 26), (32, my + 26)], GRIP_D)
        PGn([(35, my + 10), (44, my + 10), (42, my + 24), (34, my + 24)], GRIP_L)
        R(46, my + 10, 4, 5, ACC, 1)
        R(74, my + 6, 16, 5, GRIP_D, 2)
        R(75, my + 7, 14, 2, GRIP_L, 1)

    else:  # ---------------- PLASMA RIFLE (level 8+) ----------------
        my = H / 2
        CORE = _cmix(ACC, (120, 240, 255), 0.5)
        # stock
        PGn([(4, my - 5), (22, my - 7), (22, my + 8), (4, my + 6)], POLY)
        PGn([(6, my - 4), (20, my - 6), (20, my + 2), (6, my + 3)], GRIP_L)
        # main chassis
        outline(20, my - 10, 52, 20, 5)
        R(20, my - 10, 52, 20, CASE, 5)
        R(21, my - 9, 50, 6, CASE_L, 4)
        R(21, my + 5, 50, 4, _cmix(CASE, (0, 0, 0), 0.4), 4)
        # energy cell window
        R(30, my - 5, 22, 9, (12, 14, 20), 2)
        R(31, my - 4, 20, 7, CORE, 2)
        for i in range(4):
            R(33 + i * 4.6, my - 3.4, 2.2, 5.6, _cmix(CORE, WHITE, 0.55), 1)
        glow(41, my, 9, CORE, 30)
        # emitter barrel with coils
        R(70, my - 5, 44, 10, STEEL_D, 3)
        R(70, my - 5, 44, 3.4, STEEL_L, 3)
        for i in range(4):
            R(76 + i * 9, my - 8, 4.6, 16, _cmix(STEEL, STEEL_L, 0.4), 2)
            R(76 + i * 9, my - 8, 4.6, 4, SHINE, 2)
        # muzzle prongs + arc
        PGn([(112, my - 9), (126, my - 6), (126, my - 2), (112, my - 1)], STEEL_L)
        PGn([(112, my + 9), (126, my + 6), (126, my + 2), (112, my + 1)], STEEL)
        pygame.draw.line(s, CORE, (int(126 * k), int((my - 4) * k)), (int(126 * k), int((my + 4) * k)),
                         max(1, int(2.2 * k)))
        glow(126, my, 8, CORE, 34)
        # optic
        R(34, my - 16, 22, 7, GRIP_D, 2)
        R(36, my - 15, 18, 3, CORE, 1)
        # grip + trigger
        PGn([(24, my + 9), (38, my + 9), (36, my + 26), (22, my + 26)], GRIP_D)
        PGn([(25, my + 10), (36, my + 10), (34, my + 24), (24, my + 24)], GRIP_L)
        R(38, my + 10, 4, 5, ACC, 1)
        R(60, my + 8, 18, 5, GRIP_D, 2)

    return pygame.transform.smoothscale(s, (W, H))


# =========================================================
# ORBIT WEAPON DRAWING
# =========================================================
def draw_orbit_weapon(surface, x, y, angle):
    """Draw orbit weapons with their INNER end toward the player and OUTER end toward enemies."""
    x, y = int(x), int(y)
    pulse = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() * 0.012 + angle * 2.0)

    if orbit_type in ("katana", "auto"):
        # Build the weapon horizontally: left = player-facing handle, right = outward muzzle/blade.
        if orbit_type == "katana":
            weapon = pygame.Surface((94, 26), pygame.SRCALPHA)
            pygame.draw.rect(weapon, BLACK, (3, 9, 88, 8), border_radius=3)
            pygame.draw.rect(weapon, WOOD_DARK, (3, 7, 22, 12), border_radius=3)
            pygame.draw.rect(weapon, WOOD, (5, 9, 17, 8))
            pygame.draw.rect(weapon, GOLD, (23, 5, 4, 16))
            blade = [(27, 7), (82, 7), (91, 13), (82, 19), (27, 19)]
            pygame.draw.polygon(weapon, (225, 230, 238), blade)
            pygame.draw.line(weapon, WHITE, (30, 9), (82, 9), 2)
            pygame.draw.line(weapon, (170, 180, 195), (34, 17), (82, 17), 1)
        else:
            weapon = pygame.Surface((72, 32), pygame.SRCALPHA)
            pygame.draw.rect(weapon, BLACK, (3, 8, 55, 16), border_radius=4)
            pygame.draw.rect(weapon, GUN_COLOR, (7, 10, 43, 12), border_radius=3)
            pygame.draw.rect(weapon, METAL, (43, 12, 25, 7))
            pygame.draw.rect(weapon, BLACK, (56, 11, 12, 9))
            pygame.draw.rect(weapon, WOOD, (15, 21, 12, 9))
            pygame.draw.rect(weapon, GOLD, (9, 6, 9, 4))

        rotated = pygame.transform.rotate(weapon, -math.degrees(angle))
        surface.blit(rotated, rotated.get_rect(center=(x, y)))
        pygame.draw.circle(surface, (70, 220, 220), (x, y), int(13 + pulse * 4), 1)
        return

    if orbit_type == "knife":
        weapon = pygame.Surface((58, 22), pygame.SRCALPHA)
        pygame.draw.rect(weapon, BLACK, (2, 7, 54, 8))
        pygame.draw.rect(weapon, WOOD_DARK, (3, 6, 17, 10))
        pygame.draw.rect(weapon, GOLD, (18, 4, 4, 14))
        pygame.draw.polygon(weapon, (220, 225, 230), [(22,5),(51,5),(57,11),(51,17),(22,17)])
        pygame.draw.line(weapon, WHITE, (24,7), (51,7), 2)
        rotated = pygame.transform.rotate(weapon, -math.degrees(angle))
        surface.blit(rotated, rotated.get_rect(center=(x, y)))
    elif orbit_type == "axe":
        weapon = pygame.Surface((66, 34), pygame.SRCALPHA)
        pygame.draw.rect(weapon, BLACK, (5,14,45,7))
        pygame.draw.rect(weapon, WOOD_DARK, (7,15,40,5))
        pygame.draw.rect(weapon, WOOD, (9,16,36,3))
        pygame.draw.polygon(weapon, BLACK, [(43,5),(60,5),(64,10),(64,24),(60,29),(43,29)])
        pygame.draw.polygon(weapon, STONE_LIGHT, [(45,7),(58,7),(61,11),(61,23),(58,27),(45,27)])
        rotated = pygame.transform.rotate(weapon, -math.degrees(angle))
        surface.blit(rotated, rotated.get_rect(center=(x, y)))


def orbit_positions():
    if orbit_type == "none" or orbit_count <= 0:
        return []

    positions = []
    for i in range(orbit_count):
        a = orbit_angle + (math.tau * i / orbit_count)
        positions.append((
            player_x + math.cos(a) * orbit_radius,
            player_y + math.sin(a) * orbit_radius,
            a
        ))
    return positions


# =========================================================
# PIXEL UI ICONS
# =========================================================
def draw_heart(surface, x, y, size):
    pixel = max(2, size // 5)
    points = [
        (x + pixel, y),
        (x + pixel * 2, y),
        (x + pixel * 2, y + pixel),
        (x + pixel * 3, y),
        (x + pixel * 4, y),
        (x + pixel * 5, y + pixel),
        (x + pixel * 5, y + pixel * 2),
        (x + pixel * 4, y + pixel * 2),
        (x + pixel * 4, y + pixel * 3),
        (x + pixel * 3, y + pixel * 4),
        (x + pixel * 2, y + pixel * 3),
        (x + pixel, y + pixel * 3),
        (x, y + pixel * 2),
        (x, y + pixel),
    ]
    pygame.draw.polygon(surface, RED, points)


def draw_sword(surface, x, y):
    pygame.draw.rect(surface, (220, 220, 220), (x + 35, y + 10, 12, 90))
    pygame.draw.rect(surface, (245, 245, 245), (x + 47, y + 20, 10, 70))
    pygame.draw.rect(surface, WOOD, (x + 25, y + 85, 35, 12))
    pygame.draw.rect(surface, WOOD_DARK, (x + 35, y + 97, 15, 35))


def draw_gun_icon(surface, x, y):
    pygame.draw.rect(surface, (75, 75, 80), (x + 25, y + 35, 100, 28))
    pygame.draw.rect(surface, (45, 45, 50), (x + 100, y + 43, 45, 12))
    pygame.draw.rect(surface, WOOD, (x + 55, y + 60, 25, 50))
    pygame.draw.rect(surface, GOLD, (x + 85, y + 42, 12, 12))


def draw_boots(surface, x, y):
    pygame.draw.rect(surface, BLUE, (x + 25, y + 35, 45, 65))
    pygame.draw.rect(surface, BLUE, (x + 65, y + 50, 65, 45))
    pygame.draw.rect(surface, STONE_LIGHT, (x + 20, y + 95, 55, 15))
    pygame.draw.rect(surface, STONE_LIGHT, (x + 65, y + 90, 75, 15))


def draw_bullet_icon(surface, x, y):
    pygame.draw.rect(surface, GOLD, (x + 55, y + 15, 25, 90))
    pygame.draw.rect(surface, (255, 240, 150), (x + 55, y + 15, 25, 25))


def draw_lightning(surface, x, y):
    points = [
        (x + 70, y + 10),
        (x + 35, y + 65),
        (x + 60, y + 65),
        (x + 40, y + 120),
        (x + 105, y + 50),
        (x + 78, y + 50),
    ]
    pygame.draw.polygon(surface, GOLD, points)


def draw_shield(surface, x, y):
    points = [
        (x + 40, y + 15),
        (x + 110, y + 15),
        (x + 110, y + 75),
        (x + 75, y + 115),
        (x + 40, y + 75),
    ]
    pygame.draw.polygon(surface, GREEN, points)
    pygame.draw.rect(surface, WHITE, (x + 70, y + 35, 10, 50))
    pygame.draw.rect(surface, WHITE, (x + 50, y + 55, 50, 10))


def draw_knife_icon(surface, x, y):
    pygame.draw.rect(surface, (230, 230, 235), (x + 68, y + 15, 12, 85))
    pygame.draw.rect(surface, (170, 175, 180), (x + 80, y + 25, 8, 65))
    pygame.draw.rect(surface, WOOD, (x + 60, y + 90, 35, 13))
    pygame.draw.rect(surface, GOLD, (x + 58, y + 82, 40, 8))


def draw_axe_icon(surface, x, y):
    pygame.draw.rect(surface, WOOD, (x + 70, y + 25, 10, 100))
    pygame.draw.rect(surface, STONE_LIGHT, (x + 50, y + 20, 45, 28))
    pygame.draw.rect(surface, STONE, (x + 58, y + 26, 37, 18))


def draw_katana_icon(surface, x, y):
    pygame.draw.rect(surface, (235, 235, 240), (x + 70, y + 5, 8, 105))
    pygame.draw.rect(surface, (200, 200, 210), (x + 78, y + 15, 5, 85))
    pygame.draw.rect(surface, GOLD, (x + 55, y + 92, 45, 7))
    pygame.draw.rect(surface, WOOD_DARK, (x + 68, y + 99, 10, 28))


def draw_orbit_icon(surface, x, y):
    if orbit_type == "knife":
        draw_knife_icon(surface, x, y)
    elif orbit_type == "axe":
        draw_axe_icon(surface, x, y)
    elif orbit_type == "katana":
        draw_katana_icon(surface, x, y)
    elif orbit_type == "auto":
        draw_gun_icon(surface, x, y)
    else:
        draw_knife_icon(surface, x, y)


ICON_W, ICON_H, _ICON_SS = 200, 144, 4
_UPG_ICON_CACHE = {}


def draw_upgrade_icon(surface, upgrade, x, y):
    """Blit the cached high-detail medallion icon. x/y = top-left of the icon area."""
    art = _UPG_ICON_CACHE.get(upgrade)
    if art is None:
        art = _build_upgrade_icon(upgrade)
        _UPG_ICON_CACHE[upgrade] = art
    surface.blit(art, (int(x), int(y)))


def _build_upgrade_icon(key):
    """Draw one icon at 4x into a medallion, then downscale for smooth edges."""
    k = _ICON_SS
    s = pygame.Surface((ICON_W * k, ICON_H * k), pygame.SRCALPHA)
    tint = UPGRADE_DATA.get(key, {}).get("color", CYAN)
    CX, CY, R = 100.0, 72.0, 57.0

    def D(v):
        return int(round(v * k))

    def circle(cx, cy, r, col, w=0):
        pygame.draw.circle(s, col, (D(cx), D(cy)), D(r), max(1, D(w)) if w else 0)

    def poly(pts, col):
        pygame.draw.polygon(s, col, [(D(a), D(b)) for a, b in pts])

    def rect(rx, ry, rw, rh, col, rad=0):
        pygame.draw.rect(s, col, (D(rx), D(ry), D(rw), D(rh)), 0, border_radius=D(rad))

    def frame(rx, ry, rw, rh, col, w=2, rad=0):
        pygame.draw.rect(s, col, (D(rx), D(ry), D(rw), D(rh)), max(1, D(w)), border_radius=D(rad))

    def line(x1, y1, x2, y2, col, w=2):
        pygame.draw.line(s, col, (D(x1), D(y1)), (D(x2), D(y2)), max(1, D(w)))

    def arc(rx, ry, rw, rh, a1, a2, col, w=3):
        pygame.draw.arc(s, col, (D(rx), D(ry), D(rw), D(rh)), a1, a2, max(1, D(w)))

    def ellipse(rx, ry, rw, rh, col, w=0):
        pygame.draw.ellipse(s, col, (D(rx), D(ry), D(rw), D(rh)), max(1, D(w)) if w else 0)

    def glow(cx, cy, r, col, strength=30):
        g = pygame.Surface((D(r * 2 + 8), D(r * 2 + 8)), pygame.SRCALPHA)
        c = g.get_width() // 2
        steps = 12
        for n in range(steps, 0, -1):
            a = int(strength * ((steps - n) / steps) ** 2.0)
            pygame.draw.circle(g, (*col, a), (c, c), int(D(r) * n / steps))
        s.blit(g, (D(cx) - c, D(cy) - c), special_flags=pygame.BLEND_RGBA_ADD)

    def glyph(text, size, col, cx, cy):
        f = pygame.font.SysFont("arial", D(size), bold=True)
        img = f.render(text, True, col)
        s.blit(img, img.get_rect(center=(D(cx), D(cy))))

    # ---------------- medallion backdrop ----------------
    edge = _mix((9, 11, 15), tint, 0.10)
    core = _mix((30, 34, 43), tint, 0.34)
    for r in range(int(R), 0, -1):
        f = r / R
        circle(CX, CY, r, _mix(core, edge, f ** 1.15))

    # faint tint bloom behind the emblem
    glow(CX, CY, 30, tint, 22)

    # ring + bevel
    circle(CX, CY, R, _sh(tint, 0.95), 2.2)
    circle(CX, CY, R - 4.5, (0, 0, 0), 1.4)
    circle(CX, CY, R - 6, _mix(edge, WHITE, 0.10), 1)

    # top gloss, masked to the disc
    gl = pygame.Surface(s.get_size(), pygame.SRCALPHA)
    pygame.draw.ellipse(gl, (255, 255, 255, 26), (D(CX - 42), D(CY - 50), D(84), D(40)))
    pygame.draw.ellipse(gl, (255, 255, 255, 16), (D(CX - 30), D(CY + 22), D(60), D(24)))
    mask = pygame.Surface(s.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (D(CX), D(CY)), D(R - 6))
    gl.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    s.blit(gl, (0, 0))

    # tick marks around the rim
    for i in range(24):
        a = i * math.tau / 24
        r1, r2 = R - 2.5, R - (7 if i % 6 == 0 else 5)
        line(CX + math.cos(a) * r1, CY + math.sin(a) * r1,
             CX + math.cos(a) * r2, CY + math.sin(a) * r2,
             _sh(tint, 0.75 if i % 6 == 0 else 0.45), 1.4 if i % 6 == 0 else 1)

    WH = (245, 248, 252)
    STL_D = (46, 50, 58)
    STL = (104, 110, 122)
    STL_L = (168, 176, 190)
    BRASS = (206, 162, 62)
    BRASS_L = (248, 214, 128)
    BRASS_D = (128, 96, 30)

    def shaded_poly(pts, base, lift=(0, -3), light=None):
        """Dark silhouette + lighter face on top for instant depth."""
        poly(pts, _sh(base, 0.5))
        poly([(a + lift[0], b + lift[1]) for a, b in pts], base)
        if light:
            poly([(a + lift[0] * 1.6, b + lift[1] * 1.9) for a, b in pts], light)

    # ---------------- emblems ----------------
    if key == "health":                                  # FIELD MEDKIT
        rect(CX - 34, CY - 20, 68, 46, (150, 156, 166), 6)
        rect(CX - 31, CY - 17, 62, 40, WH, 5)
        rect(CX - 31, CY - 17, 62, 12, (216, 222, 230), 5)
        rect(CX - 10, CY - 28, 20, 9, (120, 128, 140), 3)
        rect(CX - 8, CY - 26, 16, 5, (176, 184, 196), 2)
        rect(CX - 5, CY - 11, 10, 30, (196, 44, 44))
        rect(CX - 19, CY - 1, 38, 10, (196, 44, 44))
        rect(CX - 4, CY - 10, 4, 28, (232, 84, 84))
        line(CX - 31, CY + 8, CX + 31, CY + 8, (200, 208, 218), 1.4)
        rect(CX + 6, CY - 6, 5, 7, (120, 128, 140), 2)

    elif key == "damage":                                # DAMAGE CORE
        for i in range(6):
            a = i * math.tau / 6 + 0.5
            shaded_poly([(CX + math.cos(a) * 16, CY + math.sin(a) * 16),
                         (CX + math.cos(a + 0.42) * 40, CY + math.sin(a + 0.42) * 40),
                         (CX + math.cos(a - 0.42) * 40, CY + math.sin(a - 0.42) * 40)],
                        STL, (0, -2), STL_L)
        glow(CX, CY, 24, (255, 70, 60), 46)
        circle(CX, CY, 22, (110, 16, 16))
        circle(CX, CY, 19, (196, 40, 34))
        circle(CX, CY, 13, (248, 96, 76))
        circle(CX, CY, 6, (255, 216, 190))
        circle(CX - 6, CY - 7, 4, (255, 240, 230))

    elif key == "fire":                                  # RAPID TRIGGER
        for i, ox in enumerate((-46, -30)):
            poly([(CX + ox, CY - 20), (CX + ox + 16, CY), (CX + ox, CY + 20)],
                 _sh(GOLD, 0.45 + i * 0.16))
        glow(CX + 8, CY, 32, (255, 200, 70), 46)
        bolt = [(CX + 22, CY - 44), (CX - 8, CY - 2), (CX + 10, CY - 2),
                (CX - 4, CY + 44), (CX + 32, CY - 6), (CX + 12, CY - 6)]
        poly([(a + 2, b + 4) for a, b in bolt], (92, 58, 6))
        poly(bolt, (238, 178, 30))
        poly([(a - 1, b - 3) for a, b in bolt], (255, 214, 70))
        line(CX + 16, CY - 34, CX + 2, CY - 8, (255, 252, 220), 2.6)
        line(CX + 4, CY + 30, CX + 18, CY + 4, (255, 240, 170), 2.0)

    elif key == "speed":                                 # SPRINT MODULE
        for ly, lw in ((-20, 30), (-6, 40), (10, 26)):
            line(CX - 20 - lw, CY + ly, CX - 22, CY + ly, _mix(CYAN, WHITE, 0.30), 3.2)
            line(CX - 20 - lw, CY + ly, CX - 20 - lw * 0.45, CY + ly, WH, 3.2)
        # heel wings
        for wsc, wcol in ((1.0, (150, 198, 246)), (0.66, (222, 240, 255))):
            wing = [(CX - 6, CY - 16), (CX - 6 - 30 * wsc, CY - 30 * wsc),
                    (CX - 6 - 12 * wsc, CY - 12 * wsc), (CX - 6, CY - 6)]
            poly([(a + 2, b + 3) for a, b in wing], (26, 56, 96))
            poly(wing, wcol)
        # shoe body (side view, toe to the right)
        shoe = [(CX - 20, CY - 18), (CX - 2, CY - 20), (CX + 8, CY - 4),
                (CX + 30, CY + 4), (CX + 34, CY + 14), (CX - 20, CY + 14)]
        poly([(a + 2, b + 3) for a, b in shoe], (14, 34, 62))
        poly(shoe, (48, 106, 190))
        poly([(CX - 18, CY - 16), (CX - 4, CY - 17), (CX + 4, CY - 4),
              (CX - 18, CY - 4)], (86, 154, 228))
        line(CX - 18, CY - 2, CX + 30, CY + 6, (26, 62, 108), 2.2)
        # sole
        rect(CX - 22, CY + 13, 58, 10, (232, 238, 248), 5)
        rect(CX - 22, CY + 18, 58, 5, (170, 182, 200), 4)
        for i in range(4):
            line(CX - 14 + i * 12, CY + 19, CX - 14 + i * 12, CY + 23, (128, 140, 158), 1.6)
        # laces
        for i in range(3):
            line(CX - 14 + i * 6, CY - 15 + i * 4, CX - 4 + i * 6, CY - 12 + i * 4,
                 (232, 240, 252), 2.0)

    elif key == "bullet":                                # HOT AMMO
        for i in range(5):
            line(CX - 46 + i * 3, CY - 16 + i * 8, CX - 12 + i * 4, CY - 16 + i * 8,
                 _mix(PURPLE, WHITE, 0.15 + i * 0.08), 3)
        glow(CX + 6, CY, 26, (190, 120, 250), 44)
        rect(CX - 12, CY - 11, 26, 22, BRASS_D, 4)
        rect(CX - 12, CY - 11, 26, 9, BRASS_L, 4)
        rect(CX - 12, CY - 2, 26, 12, BRASS, 4)
        poly([(CX + 14, CY - 12), (CX + 38, CY), (CX + 14, CY + 12)], (150, 88, 200))
        poly([(CX + 14, CY - 9), (CX + 32, CY), (CX + 14, CY + 8)], (206, 150, 250))
        line(CX + 18, CY - 4, CX + 28, CY - 1, (250, 230, 255), 1.6)

    elif key == "bigrounds":                             # HEAVY ROUNDS
        for i, ox in enumerate((-28, 0, 28)):
            bh = 40 if i == 1 else 34
            base = CY + 26 if i == 1 else CY + 22
            top = base - bh
            rect(CX + ox - 14, top, 28, bh, BRASS_D, 5)
            rect(CX + ox - 12, top + 2, 24, bh - 4, BRASS, 4)
            rect(CX + ox - 12, top + 2, 8, bh - 4, BRASS_L, 4)
            rect(CX + ox - 14, base - 7, 28, 6, _sh(BRASS, 0.62), 2)
            line(CX + ox - 14, top + 9, CX + ox + 14, top + 9, _sh(BRASS, 0.6), 1.6)
            tip = [(CX + ox - 14, top + 1), (CX + ox, top - 20), (CX + ox + 14, top + 1)]
            poly([(a, b + 2) for a, b in tip], (36, 38, 46))
            poly(tip, STL)
            poly([(CX + ox - 9, top), (CX + ox - 2, top - 15), (CX + ox + 2, top)], STL_L)

    elif key == "greed":                                 # BLOOD MONEY
        # coins behind
        for ox, oy, r in ((-32, 18, 19), (32, 20, 17)):
            circle(CX + ox, CY + oy + 3, r, (78, 54, 8))
            circle(CX + ox, CY + oy, r, BRASS_D)
            circle(CX + ox, CY + oy, r - 2.4, BRASS)
            circle(CX + ox, CY + oy - 2, r - 8, BRASS_L)
        # coin edge stack under the main coin
        for i, oy in enumerate((30, 24)):
            ellipse(CX - 28, CY + oy, 56, 14, BRASS_D)
            ellipse(CX - 28, CY + oy - 3, 56, 14, BRASS)
        # main coin
        circle(CX, CY - 6, 33, (74, 50, 6))
        circle(CX, CY - 8, 33, BRASS_D)
        circle(CX, CY - 8, 30, BRASS)
        circle(CX, CY - 10, 25, BRASS_L)
        circle(CX, CY - 8, 30, _sh(BRASS, 0.5), 1.8)
        for i in range(22):                              # milled edge
            a = i * math.tau / 22
            line(CX + math.cos(a) * 30, CY - 8 + math.sin(a) * 30,
                 CX + math.cos(a) * 33, CY - 8 + math.sin(a) * 33, _sh(BRASS, 0.6), 1.4)
        glyph("$", 46, (255, 250, 216), CX, CY - 11)
        glyph("$", 42, (126, 88, 12), CX, CY - 9)
        # blood running off the coin
        for dx, dy, r in ((-16, 26, 5.0), (4, 32, 4.0), (20, 24, 3.4)):
            circle(CX + dx, CY + dy, r, (168, 22, 28))
            poly([(CX + dx - r, CY + dy), (CX + dx, CY + dy - r * 2.8),
                  (CX + dx + r, CY + dy)], (168, 22, 28))
            circle(CX + dx - r * 0.34, CY + dy - r * 0.3, r * 0.32, (240, 100, 100))

    elif key == "scholar":                               # COMBAT DRILLS
        for bx, bh in ((-32, 16), (-11, 26), (10, 36), (31, 46)):
            rect(CX + bx - 8, CY + 26 - bh, 16, bh, _sh(XP_COLOR, 0.42), 3)
            rect(CX + bx - 6, CY + 28 - bh, 12, bh - 4, _sh(XP_COLOR, 0.78), 2)
            rect(CX + bx - 6, CY + 28 - bh, 4, bh - 4, _mix(XP_COLOR, WHITE, 0.30), 2)
        cap = [(CX - 42, CY - 18), (CX, CY - 38), (CX + 42, CY - 18), (CX, CY + 2)]
        poly([(a, b + 4) for a, b in cap], (14, 34, 74))
        poly(cap, _sh(XP_COLOR, 0.85))
        poly([(CX - 30, CY - 18), (CX, CY - 32), (CX + 30, CY - 18), (CX, CY - 5)],
             _mix(XP_COLOR, WHITE, 0.34))
        poly([(CX - 22, CY - 8), (CX + 22, CY - 8), (CX + 18, CY + 12), (CX - 18, CY + 12)],
             (16, 40, 84))
        poly([(CX - 20, CY - 7), (CX + 20, CY - 7), (CX + 17, CY + 8), (CX - 17, CY + 8)],
             _sh(XP_COLOR, 0.7))
        line(CX + 30, CY - 16, CX + 34, CY + 6, GOLD, 2.6)
        circle(CX + 34, CY + 10, 4.4, GOLD)
        circle(CX + 32.5, CY + 8.5, 2, (255, 246, 200))

    elif key == "scavenger":                             # SCAVENGER (supply drop)
        BASE, RX, RY = CY - 14, 35.0, 25.0

        def gore(a1, a2, col):
            pts = [(CX + math.cos(a1) * RX, BASE)]
            steps = 12
            for i in range(steps + 1):
                a = a1 + (a2 - a1) * i / steps
                pts.append((CX + math.cos(a) * RX, BASE - math.sin(a) * RY))
            pts.append((CX + math.cos(a2) * RX, BASE))
            poly(pts, col)

        gore(math.pi, math.pi * 0.68, (188, 56, 56))
        gore(math.pi * 0.68, math.pi * 0.32, (238, 240, 246))
        gore(math.pi * 0.32, 0.0, (188, 56, 56))
        arc(CX - RX, BASE - RY, RX * 2, RY * 2, 0, math.pi, (138, 32, 32), 2.4)
        for sgn in (-1, 1):                              # scalloped hem
            for i in range(3):
                ex = CX + sgn * (5 + i * 10)
                ellipse(ex - 6, BASE - 4, 12, 8, (162, 44, 44))
        ellipse(CX - 7, BASE - 4, 14, 8, (208, 212, 222))
        # cords
        for sx, ex in ((-30, -13), (30, 13), (-10, -4), (10, 4)):
            line(CX + sx, BASE - 2, CX + ex, CY + 2, (204, 210, 220), 1.8)
        # crate
        rect(CX - 23, CY + 1, 46, 33, (94, 64, 30), 4)
        rect(CX - 20, CY + 4, 40, 27, (168, 118, 60), 3)
        rect(CX - 20, CY + 4, 40, 7, (194, 142, 78), 3)
        line(CX - 20, CY + 4, CX + 20, CY + 31, (126, 86, 42), 1.8)
        line(CX + 20, CY + 4, CX - 20, CY + 31, (126, 86, 42), 1.8)
        rect(CX - 4, CY + 9, 8, 18, (238, 240, 246), 1)
        rect(CX - 9, CY + 14, 18, 8, (238, 240, 246), 1)
        rect(CX - 3.4, CY + 10, 6.8, 16, (198, 46, 46), 1)
        rect(CX - 8, CY + 15, 16, 6, (198, 46, 46), 1)
        for sx, sy, sr in ((-42, 6, 3.0), (43, 12, 2.6), (36, -20, 2.2)):
            poly([(CX + sx - sr, CY + sy), (CX + sx, CY + sy - sr * 3),
                  (CX + sx + sr, CY + sy), (CX + sx, CY + sy + sr * 3)], (255, 246, 200))

    elif key == "maxhealth":                             # ARMOR PLATE
        shaded_poly([(CX, CY - 42), (CX + 36, CY - 26), (CX + 30, CY + 20),
                     (CX, CY + 40), (CX - 30, CY + 20), (CX - 36, CY - 26)],
                    (72, 148, 84), (0, -3), (118, 200, 126))
        poly([(CX, CY - 33), (CX + 27, CY - 20), (CX, CY - 8), (CX - 27, CY - 20)], (150, 216, 156))
        pts = [(CX, CY + 24), (CX - 20, CY - 1), (CX - 18, CY - 12), (CX - 10, CY - 18),
               (CX, CY - 8), (CX + 10, CY - 18), (CX + 18, CY - 12), (CX + 20, CY - 1)]
        poly(pts, (140, 30, 36))
        poly([(a, b - 2) for a, b in pts], (218, 58, 62))
        poly([(CX - 12, CY - 12), (CX - 5, CY - 14), (CX - 7, CY - 4), (CX - 14, CY - 3)], (255, 172, 176))
        for rx, ry in ((-26, -22), (26, -22), (-22, 14), (22, 14)):
            circle(CX + rx, CY + ry, 3.2, (34, 60, 38))
            circle(CX + rx, CY + ry - 0.8, 2.4, STL_L)

    elif key == "crit":                                  # CRITICAL CORE
        circle(CX, CY, 38, (28, 24, 12))
        circle(CX, CY, 36, _sh(GOLD, 0.9), 3)
        circle(CX, CY, 25, _sh(GOLD, 0.7), 2)
        circle(CX, CY, 13, _sh(GOLD, 0.55), 2)
        for a in (0, math.pi / 2, math.pi, 3 * math.pi / 2):
            line(CX + math.cos(a) * 13, CY + math.sin(a) * 13,
                 CX + math.cos(a) * 44, CY + math.sin(a) * 44, GOLD, 3)
        glow(CX, CY, 14, (255, 90, 70), 44)
        circle(CX, CY, 8, (200, 40, 34))
        circle(CX, CY, 4.5, (255, 210, 190))
        line(CX + 18, CY - 34, CX - 4, CY - 6, (216, 222, 232), 3.4)
        poly([(CX + 18, CY - 34), (CX + 32, CY - 42), (CX + 26, CY - 26)], (255, 240, 210))

    elif key == "armor":                                 # NANO ARMOR
        shaded_poly([(CX, CY - 42), (CX + 34, CY - 26), (CX + 28, CY + 20),
                     (CX, CY + 40), (CX - 28, CY + 20), (CX - 34, CY - 26)],
                    _sh(CYAN, 0.55), (0, -3), _mix(CYAN, WHITE, 0.20))
        for hx, hy in ((0, -22), (-14, -4), (14, -4), (0, 14)):
            hp = [(CX + hx + math.cos(a * math.tau / 6) * 10,
                   CY + hy + math.sin(a * math.tau / 6) * 10) for a in range(6)]
            poly(hp, (14, 44, 52))
            pygame.draw.polygon(s, _mix(CYAN, WHITE, 0.5), [(D(a), D(b)) for a, b in hp], max(1, D(1.6)))
        glow(CX, CY - 4, 26, CYAN, 34)
        line(CX - 22, CY - 30, CX + 4, CY - 38, (220, 252, 255), 2.2)

    elif key == "lifesteal":                             # VAMPIRISM
        circle(CX, CY + 2, 30, (72, 8, 14))
        circle(CX, CY - 1, 30, (198, 34, 40))
        circle(CX, CY - 4, 24, (222, 52, 58))
        circle(CX - 9, CY - 12, 10, (250, 122, 128))
        arc(CX - 30, CY - 31, 60, 60, 0.55, 2.15, (132, 14, 20), 2.6)
        # upper jaw line + two clearly separated fangs
        line(CX - 22, CY - 8, CX + 22, CY - 8, (110, 10, 16), 3.0)
        for sgn in (-1, 1):
            bx = CX + sgn * 13
            fang = [(bx - 6.5, CY - 8), (bx + 6.5, CY - 8), (bx + 1.0, CY + 20)]
            poly([(a + 1.6, b + 2) for a, b in fang], (98, 10, 16))
            poly(fang, (250, 250, 252))
            poly([(bx - 4.5, CY - 7), (bx - 0.5, CY - 7), (bx - 1.4, CY + 10)], (198, 206, 220))
        for dx, dy, r in ((-14, 30, 4.2), (15, 28, 3.4), (0, 38, 2.8)):
            circle(CX + dx, CY + dy, r, (146, 16, 22))
            poly([(CX + dx - r, CY + dy), (CX + dx, CY + dy - r * 2.4),
                  (CX + dx + r, CY + dy)], (146, 16, 22))
            circle(CX + dx - r * 0.34, CY + dy - r * 0.3, r * 0.3, (238, 96, 96))

    elif key == "regen":                                 # NANO REGEN
        glow(CX, CY, 30, GREEN, 32)
        arc(CX - 36, CY - 36, 72, 72, 0.55, 5.55, _sh(GREEN, 0.5), 9)
        arc(CX - 36, CY - 34, 72, 72, 0.55, 5.55, (120, 214, 126), 6)
        poly([(CX + 24, CY - 34), (CX + 44, CY - 6), (CX + 12, CY - 10)], _sh(GREEN, 0.5))
        poly([(CX + 24, CY - 31), (CX + 40, CY - 9), (CX + 15, CY - 12)], (140, 226, 146))
        rect(CX - 8, CY - 21, 16, 42, (30, 70, 40), 3)
        rect(CX - 21, CY - 8, 42, 16, (30, 70, 40), 3)
        rect(CX - 6, CY - 19, 12, 38, WH, 2)
        rect(CX - 19, CY - 6, 38, 12, WH, 2)
        rect(CX - 6, CY - 19, 5, 38, (206, 216, 226), 2)

    elif key == "cryo":                                  # CRYO ROUNDS
        glow(CX, CY, 34, CYAN, 34)
        for i in range(6):
            a = i * math.tau / 6
            ex, ey = CX + math.cos(a) * 44, CY + math.sin(a) * 44
            line(CX, CY, ex, ey, _sh(CYAN, 0.6), 7)
            line(CX, CY, ex, ey, (206, 248, 255), 3.4)
            for f, bl in ((0.52, 15), (0.78, 10)):
                bx, by = CX + math.cos(a) * 44 * f, CY + math.sin(a) * 44 * f
                for sgn in (-1, 1):
                    line(bx, by, bx + math.cos(a + sgn * 0.95) * bl,
                         by + math.sin(a + sgn * 0.95) * bl, (196, 244, 255), 2.6)
        circle(CX, CY, 11, (170, 236, 252))
        circle(CX, CY, 6, WH)

    elif key == "critpower":                             # OVERCHARGE
        glow(CX, CY, 36, (255, 120, 60), 50)
        for i in range(12):
            a = i * math.tau / 12
            r2 = 48 if i % 2 == 0 else 36
            poly([(CX + math.cos(a - 0.13) * 18, CY + math.sin(a - 0.13) * 18),
                  (CX + math.cos(a) * r2, CY + math.sin(a) * r2),
                  (CX + math.cos(a + 0.13) * 18, CY + math.sin(a + 0.13) * 18)],
                 (236, 92, 40) if i % 2 == 0 else (255, 168, 60))
        circle(CX, CY, 22, (150, 24, 20))
        circle(CX, CY, 19, (238, 78, 54))
        circle(CX, CY, 12, (255, 190, 140))
        line(CX - 9, CY - 9, CX + 9, CY + 9, (120, 16, 14), 4)
        line(CX + 9, CY - 9, CX - 9, CY + 9, (120, 16, 14), 4)
        line(CX - 8, CY - 8, CX + 8, CY + 8, WH, 2.2)
        line(CX + 8, CY - 8, CX - 8, CY + 8, WH, 2.2)

    elif key == "pierce":                                # RAILGUN ROUNDS
        glow(CX, CY, 34, CYAN, 40)
        line(CX - 52, CY, CX + 30, CY, _sh(CYAN, 0.55), 10)
        line(CX - 52, CY, CX + 30, CY, (150, 240, 252), 5)
        for ox in (-30, 2, 34):
            circle(CX + ox, CY, 17, (26, 44, 30))
            circle(CX + ox, CY - 2, 15, (104, 154, 96))
            circle(CX + ox - 5, CY + 3, 5, (62, 104, 60))
            circle(CX + ox - 5, CY - 7, 3.4, (22, 28, 22))
            circle(CX + ox + 5, CY - 7, 3.4, (22, 28, 22))
            line(CX + ox - 6, CY + 8, CX + ox + 6, CY + 8, (30, 40, 30), 2)
            circle(CX + ox, CY, 17, (18, 30, 22), 1.8)
            circle(CX + ox, CY, 5.5, (18, 28, 20))
            circle(CX + ox, CY, 3.4, (198, 246, 255))
        line(CX - 52, CY, CX + 48, CY, (232, 254, 255), 2.4)
        poly([(CX + 52, CY), (CX + 34, CY - 13), (CX + 34, CY + 13)], _sh(CYAN, 0.8))
        poly([(CX + 48, CY), (CX + 35, CY - 9), (CX + 35, CY + 9)], WH)

    elif key == "shrapnel":                              # SHRAPNEL ROUNDS
        glow(CX, CY, 30, (255, 150, 50), 52)
        for i in range(14):
            a = i * math.tau / 14 + 0.2
            r1 = 22
            r2 = 50 if i % 2 == 0 else 40
            poly([(CX + math.cos(a) * r1, CY + math.sin(a) * r1),
                  (CX + math.cos(a) * r2 + math.cos(a + 1.6) * 4,
                   CY + math.sin(a) * r2 + math.sin(a + 1.6) * 4),
                  (CX + math.cos(a) * r2 - math.cos(a + 1.6) * 4,
                   CY + math.sin(a) * r2 - math.sin(a + 1.6) * 4)],
                 STL_L if i % 3 else _mix((255, 170, 60), WHITE, 0.2))
        circle(CX, CY, 22, (128, 56, 12))
        circle(CX, CY, 19, (240, 138, 40))
        circle(CX, CY, 12, (255, 208, 120))
        circle(CX, CY, 5, WH)
        for a in (0.6, 2.3, 4.1, 5.6):
            circle(CX + math.cos(a) * 15, CY + math.sin(a) * 15, 2.6, (90, 40, 10))

    elif key == "thorns":                                # SPIKE PLATING
        for i in range(9):
            a = i * math.tau / 9 - math.pi / 2
            shaded_poly([(CX + math.cos(a - 0.20) * 28, CY + math.sin(a - 0.20) * 28),
                         (CX + math.cos(a) * 50, CY + math.sin(a) * 50),
                         (CX + math.cos(a + 0.20) * 28, CY + math.sin(a + 0.20) * 28)],
                        STL, (0, -2), STL_L)
        shaded_poly([(CX, CY - 36), (CX + 30, CY - 22), (CX + 25, CY + 17),
                     (CX, CY + 34), (CX - 25, CY + 17), (CX - 30, CY - 22)],
                    (86, 92, 104), (0, -3), (144, 152, 166))
        poly([(CX, CY - 28), (CX + 23, CY - 17), (CX, CY - 6), (CX - 23, CY - 17)], (188, 196, 210))
        for rx, ry in ((-18, 4), (18, 4), (0, 20)):
            circle(CX + rx, CY + ry, 3.4, (40, 44, 52))
            circle(CX + rx, CY + ry - 0.8, 2.4, STL_L)

    elif key == "gun":                                   # WEAPON EVOLUTION
        BY = CY + 12
        rect(CX - 38, BY - 8, 54, 16, STL_D, 4)
        rect(CX - 36, BY - 6, 50, 6, STL, 3)
        rect(CX + 12, BY - 5, 30, 10, STL, 3)
        rect(CX + 12, BY - 5, 30, 4, STL_L, 2)
        rect(CX + 38, BY - 7, 6, 14, (22, 24, 30), 2)
        rect(CX - 32, BY - 15, 20, 5, STL_L, 2)
        poly([(CX - 34, BY + 8), (CX - 20, BY + 8), (CX - 24, BY + 25), (CX - 39, BY + 25)],
             (30, 32, 40))
        poly([(CX - 32, BY + 10), (CX - 22, BY + 10), (CX - 26, BY + 22), (CX - 36, BY + 22)],
             (62, 66, 78))
        rect(CX - 18, BY + 8, 5, 8, GOLD, 2)
        rect(CX - 12, BY + 8, 15, 20, (44, 48, 58), 3)
        rect(CX - 10, BY + 10, 11, 16, (74, 80, 94), 2)
        # single clean upgrade arrow badge, clear of the weapon
        AX, AY = CX + 20, CY - 23
        glow(AX, AY, 15, GOLD, 18)
        arrow = [(AX, AY - 15), (AX + 12, AY - 2), (AX + 5.5, AY - 2), (AX + 5.5, AY + 13),
                 (AX - 5.5, AY + 13), (AX - 5.5, AY - 2), (AX - 12, AY - 2)]
        poly([(a + 1.6, b + 2.4) for a, b in arrow], (104, 68, 6))
        poly(arrow, GOLD)
        poly([(AX - 1.2, AY - 11), (AX + 5.5, AY - 3), (AX - 1.2, AY - 3)],
             _mix(GOLD, WH, 0.55))

    elif key == "orbit":                                 # ORBITAL EVOLUTION
        ellipse(CX - 48, CY - 24, 96, 48, _sh(CYAN, 0.42), 3)
        glow(CX, CY, 24, CYAN, 44)
        circle(CX, CY + 3, 21, (10, 44, 52))
        circle(CX, CY, 20, _mix(CYAN, (8, 52, 70), 0.5))
        circle(CX, CY - 4, 12, _mix(CYAN, WHITE, 0.25))
        circle(CX - 6, CY - 8, 5, (226, 252, 255))
        for a in (0.35, 2.44, 4.53):
            ox = CX + math.cos(a) * 48
            oy = CY + math.sin(a) * 24
            hilt = [(ox - 4, oy + 14), (ox + 4, oy + 14), (ox + 4, oy + 3), (ox - 4, oy + 3)]
            poly([(p[0] + 1, p[1] + 2) for p in hilt], (52, 34, 14))
            poly(hilt, (146, 96, 46))
            rect(ox - 8, oy + 1, 16, 4, GOLD, 1.4)
            bl = [(ox - 5, oy + 1), (ox - 3, oy - 22), (ox + 2, oy - 26), (ox + 5, oy + 1)]
            poly([(p[0] + 1.5, p[1] + 2) for p in bl], (58, 64, 76))
            poly(bl, (196, 204, 218))
            poly([(ox - 3.5, oy), (ox - 2, oy - 20), (ox + 0.5, oy - 22), (ox, oy)],
                 (250, 253, 255))
        for a in (1.2, 3.1, 5.2):
            circle(CX + math.cos(a) * 34, CY + math.sin(a) * 17, 2.6, (200, 248, 255))
    else:
        circle(CX, CY, 26, STL_L, 4)
        line(CX, CY - 12, CX, CY + 6, STL_L, 5)
        circle(CX, CY + 15, 3.4, STL_L)

    return pygame.transform.smoothscale(s, (ICON_W, ICON_H))


# =========================================================
# SPAWN
# =========================================================
def spawn_position():
    side = random.randint(0, 3)
    if side == 0:
        return random.randint(0, WIDTH), -50
    if side == 1:
        return WIDTH + 50, random.randint(0, HEIGHT)
    if side == 2:
        return random.randint(0, WIDTH), HEIGHT + 50
    return -50, random.randint(0, HEIGHT)



def _zombie_count_minions():
    return sum(1 for z in zombies if not z.get("boss_key"))


def _can_spawn_minion(n=1):
    return _zombie_count_minions() + n <= MAX_MINIONS and len(zombies) + n <= MAX_ZOMBIES


def _trim_list(lst, cap):
    """Drop oldest entries when a list exceeds its soft cap."""
    overflow = len(lst) - cap
    if overflow > 0:
        del lst[:overflow]


def _spawn_minion(x, y, ztype="normal", hp=80, speed=2.0, damage=0.6, radius=18):
    if not _can_spawn_minion(1):
        return False
    zombies.append({
        "x": float(x), "y": float(y),
        "speed": speed, "health": hp, "max_health": hp,
        "damage": damage, "radius": radius, "type": ztype,
        "hit_flash_until": 0, "frozen_until": 0,
    })
    return True


# Named endgame bosses — all nine appear together on WAVE 100.
BOSS_ROSTER = [
    # key, display name, hp, speed, damage, radius, color body/dark/eye
    # Stats ~10x tougher (HP x10, contact damage x3, slightly faster)
    {"key": "horde_king", "name": "HORDE KING",
     "hp": 1200000, "speed": 1.45, "damage": 20.0, "radius": 60,
     "colors": ((255, 215, 50), (160, 100, 15), (255, 250, 180))},         # bright royal gold
    {"key": "plague_matriarch", "name": "PLAGUE MATRIARCH",
     "hp": 1000000, "speed": 1.55, "damage": 16.0, "radius": 56,
     "colors": ((80, 255, 40), (20, 100, 15), (180, 255, 90))},             # toxic lime green
    {"key": "cyber_colossus", "name": "CYBER COLOSSUS",
     "hp": 1500000, "speed": 1.10, "damage": 22.0, "radius": 64,
     "colors": ((55, 130, 210), (20, 50, 90), (0, 255, 255))},              # steel blue + cyan eyes
    {"key": "chrono_wraith", "name": "CHRONO WRAITH",
     "hp": 900000, "speed": 2.15, "damage": 17.0, "radius": 50,
     "colors": ((140, 40, 220), (40, 10, 80), (255, 220, 80))},             # deep violet + gold eyes
    {"key": "blood_moon_reaper", "name": "BLOOD MOON REAPER",
     "hp": 1100000, "speed": 1.80, "damage": 24.0, "radius": 54,
     "colors": ((220, 15, 30), (60, 0, 8), (255, 50, 50))},                 # pure blood crimson
    {"key": "swarm_heart", "name": "SWARM HEART",
     "hp": 1600000, "speed": 0.80, "damage": 14.0, "radius": 70,
     "colors": ((255, 30, 160), (110, 5, 70), (255, 180, 220))},            # hot magenta / pink
    {"key": "mirror_twin", "name": "MIRROR TWIN",
     "hp": 850000, "speed": 1.95, "damage": 18.0, "radius": 48,
     "colors": ((235, 245, 255), (130, 150, 180), (255, 255, 255))},        # chrome silver-white
    {"key": "frost_titan", "name": "FROST TITAN",
     "hp": 1400000, "speed": 1.30, "damage": 20.0, "radius": 62,
     "colors": ((140, 220, 255), (30, 100, 180), (255, 255, 255))},         # pure ice blue
    {"key": "necro_conductor", "name": "NECRO CONDUCTOR",
     "hp": 1050000, "speed": 1.45, "damage": 17.0, "radius": 56,
     "colors": ((100, 25, 150), (30, 5, 50), (255, 170, 30))},              # dark purple + amber eyes
]


def _make_named_boss(spec, x=None, y=None, scale=1.0):
    """Named boss with unique colors, accessories (boss_key), and powers."""
    if x is None or y is None:
        x, y = spawn_position()
    hp = max(800, int(spec["hp"] * scale))
    return {
        "x": float(x), "y": float(y),
        "speed": spec["speed"] * (0.92 + 0.08 * min(1.0, scale)),
        "health": hp, "max_health": hp,
        "damage": max(1.2, spec["damage"] * (0.55 + 0.45 * min(1.0, scale))),
        "radius": spec["radius"],
        "type": "boss",
        "boss_key": spec["key"],
        "boss_name": spec["name"],
        "colors": spec["colors"],
        "hit_flash_until": 0, "frozen_until": 0,
        "ability_cd": 0, "phase": 1, "special": 0,
    }


def spawn_wave():
    zombies.clear()

    # WAVE 100 — all 9 legendary bosses at once (endgame gauntlet)
    if wave == 100:
        positions = [
            (WIDTH * 0.15, HEIGHT * 0.20), (WIDTH * 0.50, HEIGHT * 0.12), (WIDTH * 0.85, HEIGHT * 0.20),
            (WIDTH * 0.10, HEIGHT * 0.50), (WIDTH * 0.50, HEIGHT * 0.50), (WIDTH * 0.90, HEIGHT * 0.50),
            (WIDTH * 0.20, HEIGHT * 0.82), (WIDTH * 0.50, HEIGHT * 0.88), (WIDTH * 0.80, HEIGHT * 0.82),
        ]
        for i, spec in enumerate(BOSS_ROSTER):
            px, py = positions[i % len(positions)]
            zombies.append(_make_named_boss(spec, px, py))
        return

    # WAVE 1000 — AntonXD (ultimate werewolf boss)
    if wave == 1000:
        zombies.append(_make_named_boss({
            "key": "blood_werewolf",
            "name": "AntonXD",
            "hp": 3500000,  # tough but killable
            "speed": 2.2,
            "damage": 28.0,
            "radius": 72,
            "colors": ((90, 70, 80), (30, 20, 28), (255, 50, 40)),
        }, WIDTH // 2, 120, scale=1.0))
        return

    amount = min(MAX_MINIONS - 5, 5 + int(wave * 2.0) + (wave // 5))

    for _ in range(amount):
        x, y = spawn_position()
        chance = random.random()

        tank_chance = 0.10 + min(0.20, wave * 0.012)
        fast_chance = tank_chance + 0.22 + min(0.24, wave * 0.016)
        if wave >= 4 and chance < tank_chance:
            zombie_type = "tank"
        elif wave >= 2 and chance < fast_chance:
            zombie_type = "fast"
        else:
            zombie_type = "normal"

        if zombie_type == "normal":
            hp = int((48 + wave * 8) * (1.0 + wave * 0.012))
            zombie = {
                "x": x, "y": y,
                "speed": 1.55 + wave * 0.055,
                "health": hp, "max_health": hp,
                "damage": 0.45 + wave * 0.012, "radius": 20, "type": "normal", "hit_flash_until": 0, "frozen_until": 0,
            }
        elif zombie_type == "fast":
            hp = int((36 + wave * 6) * (1.0 + wave * 0.010))
            zombie = {
                "x": x, "y": y,
                "speed": 2.85 + wave * 0.072,
                "health": hp, "max_health": hp,
                "damage": 0.34 + wave * 0.010, "radius": 16, "type": "fast", "hit_flash_until": 0, "frozen_until": 0,
            }
        else:
            hp = int((185 + wave * 26) * (1.0 + wave * 0.014))
            zombie = {
                "x": x, "y": y,
                "speed": 0.95 + wave * 0.032,
                "health": hp, "max_health": hp,
                "damage": 0.9 + wave * 0.02, "radius": 28, "type": "tank", "hit_flash_until": 0, "frozen_until": 0,
            }

        zombies.append(zombie)

    # Keep original: regular bosses every 5 waves
    if wave % 5 == 0:
        bosses = 1 + wave // 20
        for _ in range(bosses):
            x, y = spawn_position()
            # ~10x tougher regular bosses
            hp = int((12500 + wave * 1700) * (1.0 + wave * 0.02))
            zombies.append({
                "x": x, "y": y,
                "speed": 0.95 + wave * 0.035,
                "health": hp, "max_health": hp,
                "damage": 5.0 + wave * 0.10, "radius": 48, "type": "boss", "hit_flash_until": 0,
                "frozen_until": 0, "ability_cd": 0, "phase": 1,
            })

    # Every 10 waves: different named boss (colors + accessories + powers)
    # Wave 10/20/30...  Wave 100 = all 9 handled above
    if wave >= 10 and wave % 10 == 0:
        idx = ((wave // 10) - 1) % len(BOSS_ROSTER)
        spec = BOSS_ROSTER[idx]
        # Stronger scale so mid-run named bosses hit much harder (~10x roster HP already)
        scale = min(1.0, 0.35 + (wave / 100.0) * 0.65)
        zombies.append(_make_named_boss(spec, scale=scale))


# =========================================================
# SHOOTING
# =========================================================
def shoot():
    mouse_x, mouse_y = pygame.mouse.get_pos()
    base_angle = math.atan2(mouse_y - player_y, mouse_x - player_x)

    # ADMIN AIMBOT: hard-lock directly onto the nearest live zombie.
    # Normal players keep the softer built-in aim assist.
    if aimbot_enabled:
        target = get_aimbot_target()
        if target is not None:
            base_angle = math.atan2(target["y"] - player_y, target["x"] - player_x)
    elif (AIM_ASSIST or control_mode == "mobile") and zombies:
        best = None
        best_dist = (AIM_ASSIST_RANGE * (1.35 if control_mode == "mobile" else 1.0)) + 1
        for target in zombies:
            tx = target["x"] - player_x
            ty = target["y"] - player_y
            dist = math.hypot(tx, ty)
            if dist > AIM_ASSIST_RANGE:
                continue
            target_angle = math.atan2(ty, tx)
            diff = abs((target_angle - base_angle + math.pi) % (2 * math.pi) - math.pi)
            if diff <= AIM_ASSIST_ANGLE and dist < best_dist:
                best = target
                best_dist = dist
        if best is not None:
            target_angle = math.atan2(best["y"] - player_y, best["x"] - player_x)
            pull = 0.92 if control_mode == "mobile" else 0.72
            base_angle += (
                ((target_angle - base_angle + math.pi) % (2 * math.pi) - math.pi)
            ) * pull

    if werewolf_until and pygame.time.get_ticks() < werewolf_until:
        claw_slash(base_angle, heavy=False)
        return
    if is_melee_class():
        katana_slash(base_angle)
        return

    if gun_level == 1:
        # Pistol: precise single shot.
        angles = [base_angle]
    elif gun_level == 2:
        # Dual pistols: exactly 2 bullets.
        angles = [base_angle - 0.06, base_angle + 0.06]
    elif gun_level == 3:
        # Shotgun: wide pellet spread.
        angles = [base_angle - 0.18, base_angle - 0.06, base_angle + 0.06, base_angle + 0.18]
    elif gun_level == 4:
        # SMG: tight 3-round burst with slight wander.
        angles = [
            base_angle + random.uniform(-0.05, 0.05),
            base_angle + random.uniform(-0.08, 0.08),
            base_angle + random.uniform(-0.05, 0.05),
        ]
    elif gun_level == 5:
        # RPG: single heavy rocket.
        angles = [base_angle]
    elif gun_level == 6:
        # Minigun: hail of rounds with barrel wander.
        angles = [base_angle + random.uniform(-0.12, 0.12)]
    elif gun_level == 7:
        # Flamethrower: wide cone of burning fuel (5 streams).
        angles = [base_angle - 0.32, base_angle - 0.16, base_angle,
                  base_angle + 0.16, base_angle + 0.32]
    else:
        # Plasma / fallback
        angles = [base_angle]

    muzzle_distance = 58
    for angle in angles:
        sx = player_x + math.cos(angle) * muzzle_distance
        sy = player_y + math.sin(angle) * muzzle_distance
        critical = random.random() < crit_chance
        kind = {5: "rocket", 7: "flame", 8: "plasma"}.get(gun_level, "normal")
        bullet = {
            "x": sx,
            "y": sy,
            "dx": math.cos(angle) * bullet_speed,
            "dy": math.sin(angle) * bullet_speed,
            "damage": damage * (crit_multiplier if critical else 1.0),
            "critical": critical,
            "explosive": gun_level in (5, 8),
            "explosion_radius": 95 if gun_level == 5 else (72 if gun_level == 8 else 0),
            "pierce": pierce + (3 if kind == "flame" else 0),
            "hits": 0,
            "kind": kind,
        }
        if kind == "flame":
            # Flamethrower: short range cone, solid DPS, burns through packs
            bullet["dx"] *= 0.72
            bullet["dy"] *= 0.72
            bullet["damage"] *= 0.72
            bullet["explosive"] = False
            bullet["explosion_radius"] = 0
            bullet["life"] = 26
        elif kind == "rocket":
            bullet["dx"] *= 0.85
            bullet["dy"] *= 0.85
            bullet["damage"] *= 1.35
        bullets.append(bullet)

    # gun SFX
    if gun_level == 7:
        play_sfx("flame", 0.25)
    elif gun_level == 5:
        play_sfx("shoot_heavy", 0.35)
    elif gun_level >= 6:
        play_sfx("shoot", 0.15)
    else:
        play_sfx("shoot", 0.22)



def claw_slash(base_angle, arc=None, reach_bonus=0, heavy=False):
    """Werewolf-only claw attack. No katana — dual claws, blood trails, high lifesteal."""
    global health
    now = pygame.time.get_ticks()
    reach = 155 + reach_bonus + (30 if heavy else 0)
    half_arc = arc if arc is not None else 1.25
    critical = random.random() < max(crit_chance, 0.28)
    hit_damage = damage * (crit_multiplier if critical else 1.0) * (1.9 if heavy else 1.45)
    # dual claw arcs (left + right)
    for off, col in ((-0.32, (220, 40, 40)), (0.32, (255, 90, 50))):
        slashes.append({
            "x": float(player_x), "y": float(player_y),
            "angle": base_angle + off, "reach": reach, "arc": half_arc * 0.85,
            "time": now, "critical": critical, "element": "claw",
            "color": col,
        })
    # center bite arc
    slashes.append({
        "x": float(player_x), "y": float(player_y),
        "angle": base_angle, "reach": reach * 0.75, "arc": half_arc * 0.5,
        "time": now, "critical": critical, "element": "claw",
        "color": (255, 200, 80),
    })
    hit_any = False
    healed = 0
    for zombie in zombies[:]:
        if zombie.get("ally"):
            continue
        zx = zombie["x"] - player_x
        zy = zombie["y"] - player_y
        dist = math.hypot(zx, zy)
        if dist > reach + zombie["radius"]:
            continue
        diff = abs((math.atan2(zy, zx) - base_angle + math.pi) % (2 * math.pi) - math.pi)
        if diff > half_arc and dist > zombie["radius"] + 30:
            continue
        hit_any = True
        dmg = hit_damage
        if now < zombie.get("shield_until", 0):
            dmg *= 0.4
        zombie["health"] -= dmg
        zombie["hit_flash_until"] = now + 110
        # bleed mark
        explosions.append({
            "x": zombie["x"], "y": zombie["y"], "radius": 22,
            "time": now, "type": "spirit",
        })
        healed += 1
        if zombie["health"] <= 0:
            kill_zombie(zombie)
            health = min(max_health, health + 10)
    if hit_any:
        trigger_hit_effect(now, 5 if heavy else 4)
        health = min(max_health, health + min(18, healed * 6))


def katana_slash(base_angle, arc=None, reach_bonus=0):
    """Reaper multi-blade slash. Blade count / element follows gun_level table."""
    now = pygame.time.get_ticks()
    # Werewolf never uses katana — claw_slash handles attacks
    if werewolf_until and now < werewolf_until:
        claw_slash(base_angle, arc=arc, reach_bonus=reach_bonus)
        return
    blade_count = 1 if gun_level == 1 else (2 if gun_level == 2 else 3)
    if gun_level >= 8:
        element = "bankai"
    elif gun_level >= 7:
        element = "haki"
    elif gun_level >= 4:
        element = "fire"
    else:
        element = "normal"
    elem_mult = {"normal": 1.15, "fire": 1.35, "haki": 1.55, "bankai": 1.85}.get(element, 1.15)
    reach = 118 + gun_level * 12 + reach_bonus
    half_arc = arc if arc else 0.85 + min(0.50, gun_level * 0.06)
    critical = random.random() < max(crit_chance, 0.18)
    hit_damage = damage * (crit_multiplier if critical else 1.0) * elem_mult
    offsets = [0.0]
    if blade_count == 2:
        offsets = [-0.22, 0.22]
    elif blade_count >= 3:
        offsets = [-0.28, 0.0, 0.28]
    for off in offsets:
        slashes.append({
            "x": float(player_x), "y": float(player_y),
            "angle": base_angle + off, "reach": reach, "arc": half_arc * 0.9,
            "time": now, "critical": critical, "element": element,
        })
    hit_any = False
    for zombie in zombies[:]:
        zx = zombie["x"] - player_x
        zy = zombie["y"] - player_y
        dist = math.hypot(zx, zy)
        if dist > reach + zombie["radius"]:
            continue
        diff = abs((math.atan2(zy, zx) - base_angle + math.pi) % (2 * math.pi) - math.pi)
        if diff > half_arc and dist > zombie["radius"] + 26:
            continue
        hit_any = True
        dmg = hit_damage * (1.0 + 0.12 * (blade_count - 1))
        if now < zombie.get("shield_until", 0):
            dmg *= 0.35
        zombie["health"] -= dmg
        zombie["hit_flash_until"] = now + 90
        if element in ("fire", "bankai") and random.random() < 0.35:
            explosions.append({
                "x": zombie["x"], "y": zombie["y"], "radius": 28 + gun_level * 2,
                "time": now, "type": "spirit",
            })
        chill = freeze_chance + (0.25 if selected_character == "Frozen" else 0.0)
        if chill and random.random() < chill:
            zombie["frozen_until"] = now + 1800
        if zombie["health"] <= 0:
            kill_zombie(zombie)
    if hit_any:
        trigger_hit_effect(now, 3 + (1 if element in ("haki", "bankai") else 0))



# =========================================================
# ORBIT AUTO-GUN SHOOTING
# =========================================================
def orbit_auto_shoot(current_time):
    global orbit_last_shot
    if orbit_type != "auto" or not zombies or orbit_count <= 0:
        return
    if current_time - orbit_last_shot < orbit_shoot_delay:
        return

    positions = orbit_positions()
    # Each orbit gun chooses a target independently, preferring the closest zombie to its muzzle.
    for index, (ox, oy, _) in enumerate(positions):
        target = min(zombies, key=lambda z: math.hypot(z["x"] - ox, z["y"] - oy))
        angle = math.atan2(target["y"] - oy, target["x"] - ox)
        spread = (index - (orbit_count - 1) / 2) * 0.035
        angle += spread
        orbit_bullets.append({
            "x": ox, "y": oy,
            "dx": math.cos(angle) * 13, "dy": math.sin(angle) * 13,
            "damage": orbit_damage,
            "life": 900,
            "trail": [],
        })
    orbit_last_shot = current_time


# =========================================================
# ZOMBIE DEATH / REWARDS
# =========================================================
def apply_zombie_damage(zombie, amount, current_time):
    """Apply damage respecting boss shields."""
    if current_time < zombie.get("shield_until", 0):
        amount *= 0.35
    zombie["health"] -= amount
    zombie["hit_flash_until"] = current_time + 75
    return zombie["health"] <= 0


def kill_zombie(zombie):

    global score, xp, kills, health

    if zombie not in zombies:
        return

    zombies.remove(zombie)
    kills += 1
    play_sfx("damage", 0.22)

    if zombie.get("boss_key"):
        # Named legendary bosses — huge payout + 20 gems
        score += 2500
        xp += int(800 * (1.0 + xp_bonus))
        add_coins(int(350 * (1.0 + coin_bonus)))
        add_gems(20)
    else:
        base = {"normal": (10, 20, 5), "fast": (15, 25, 7), "tank": (30, 45, 15)}.get(
            zombie["type"], (500, 250, 100))
        score += base[0]
        xp += int(base[1] * (1.0 + xp_bonus))
        add_coins(int(base[2] * (1.0 + coin_bonus)))

    if lifesteal and not named_bosses_alive():
        health = min(max_health, health + lifesteal)

    if random.random() < med_drop_chance and len(meds) < MAX_MEDS:
        if not (named_bosses_alive() and random.random() < 0.7):
            meds.append({"x": zombie["x"], "y": zombie["y"]})




def draw_named_boss(screen, zombie, x, y, radius, body_c, dark_c, eye_c, current_time, hit):
    """Fully unique silhouette per boss — not a reskinned zombie."""
    bk = zombie.get("boss_key")
    bob = int(math.sin(current_time * 0.01 + x * 0.02) * 3)
    yb = y + bob
    # =========================================================
    # LEGENDARY BOSS PRESENTATION — VISUAL ONLY
    # Boss stats, attacks, abilities and hitboxes are unchanged.
    # =========================================================
    pulse = 0.5 + 0.5 * math.sin(current_time * 0.006)
    aura = WHITE if hit else body_c

    # Heavy ground shadow
    shadow = pygame.Surface((radius * 4 + 80, max(30, radius)), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, 150),
                        shadow.get_rect().inflate(-10, -8))
    screen.blit(shadow, (x - shadow.get_width() // 2, yb + radius - 2))

    # Layered animated aura
    for ring in range(3):
        rr = radius + 16 + ring * 9 + int(pulse * 5)
        alpha = max(35, 115 - ring * 28)
        glow = pygame.Surface((rr * 2 + 12, rr * 2 + 12), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*aura[:3], alpha), (rr + 6, rr + 6), rr, 2)
        screen.blit(glow, (x - rr - 6, yb - rr - 6))

    # Boss-specific energy colors
    accent_map = {
        "horde_king": (255, 205, 40),
        "plague_matriarch": (80, 255, 100),
        "cyber_colossus": (0, 220, 255),
        "chrono_wraith": (190, 100, 255),
        "blood_moon_reaper": (255, 45, 70),
        "swarm_heart": (255, 70, 180),
        "mirror_twin": (190, 220, 255),
        "frost_titan": (150, 235, 255),
        "necro_conductor": (255, 175, 45),
        "blood_werewolf": (255, 60, 50),
    }
    accent = accent_map.get(bk, body_c)

    # Rotating energy shards
    for i in range(10):
        a = current_time * 0.0018 + i * math.tau / 10
        rr = radius + 28 + int(math.sin(current_time * 0.004 + i) * 5)
        sx = int(x + math.cos(a) * rr)
        sy = int(yb + math.sin(a) * rr)
        sz = 3 + (i % 3)
        pts = [(sx, sy - sz * 2), (sx + sz, sy),
               (sx, sy + sz * 2), (sx - sz, sy)]
        pygame.draw.polygon(screen, accent, pts)
        pygame.draw.polygon(screen, WHITE, pts, 1)

    # Inner energy rings
    pygame.draw.circle(screen, accent, (x, yb), radius + 12, 2)
    pygame.draw.circle(screen, WHITE if hit else accent, (x, yb), radius + 5, 1)

    # Floating particles
    for i in range(14):
        a = current_time * 0.0025 + i * (math.tau / 14)
        rr = radius + 20 + ((i * 17) % 24)
        px = int(x + math.cos(a) * rr)
        py = int(yb + math.sin(a * 1.17) * rr * 0.72)
        pr = 2 + (i % 2)
        pygame.draw.circle(screen, accent, (px, py), pr)
        if i % 4 == 0:
            pygame.draw.circle(screen, WHITE, (px, py), 1)

    # Dark silhouette outline behind the existing boss art
    pygame.draw.circle(screen, (8, 8, 12), (x, yb), radius + 2, 3)

    if bk == "blood_werewolf":
        # Full legendary werewolf boss sprite (scaled)
        draw_werewolf(screen, x, yb, scale=max(1.35, radius / 48.0), boss=True)
        # Explicit HP bar so you can see it die
        bar_w = radius * 2 + 50
        bar_y = yb - radius - 36
        hp_frac = max(0.0, min(1.0, zombie["health"] / max(1, zombie["max_health"])))
        pygame.draw.rect(screen, (20, 0, 0), (x - bar_w // 2 - 2, bar_y - 2, bar_w + 4, 14))
        pygame.draw.rect(screen, (60, 10, 10), (x - bar_w // 2, bar_y, bar_w, 10))
        pygame.draw.rect(screen, (255, 50, 50), (x - bar_w // 2, bar_y, int(bar_w * hp_frac), 10))
        pygame.draw.rect(screen, GOLD, (x - bar_w // 2, bar_y, bar_w, 10), 2)
        nm = FONT_SMALL.render("AntonXD", True, GOLD)
        screen.blit(nm, (x - nm.get_width() // 2, bar_y - 22))
        return

    if bk == "horde_king":
        # GOLD KING — wide body, crown, red cape
        pygame.draw.ellipse(screen, (0, 0, 0), (x - radius - 8, yb + radius // 2, radius * 2 + 16, 18))
        pygame.draw.polygon(screen, (120, 20, 20), [
            (x - radius, yb), (x - radius - 30, yb + radius + 20),
            (x + radius + 30, yb + radius + 20), (x + radius, yb)])
        pygame.draw.rect(screen, dark_c, (x - radius, yb - radius // 2, radius * 2, int(radius * 1.4)), border_radius=8)
        pygame.draw.rect(screen, body_c, (x - radius + 4, yb - radius // 2 + 4, radius * 2 - 8, int(radius * 1.3) - 8), border_radius=6)
        # crown
        pts = [(x - 28, yb - radius), (x - 20, yb - radius - 28), (x - 10, yb - radius - 12),
               (x, yb - radius - 34), (x + 10, yb - radius - 12), (x + 20, yb - radius - 28), (x + 28, yb - radius)]
        pygame.draw.polygon(screen, (255, 215, 0), pts)
        pygame.draw.polygon(screen, (255, 255, 180), [(x - 16, yb - radius), (x, yb - radius - 20), (x + 16, yb - radius)])
        pygame.draw.circle(screen, (255, 40, 40), (x, yb - radius - 30), 5)
        # eyes
        pygame.draw.rect(screen, eye_c, (x - 18, yb - radius // 3, 12, 10))
        pygame.draw.rect(screen, eye_c, (x + 6, yb - radius // 3, 12, 10))
        for i in range(-2, 3):
            pygame.draw.circle(screen, (255, 230, 80), (x + i * 12, yb + 8), 5)

    elif bk == "plague_matriarch":
        # TOXIC green — gas mask, vials, spores
        pygame.draw.ellipse(screen, (0, 0, 0), (x - radius - 6, yb + radius // 2, radius * 2 + 12, 16))
        pygame.draw.rect(screen, dark_c, (x - radius, yb - radius // 2, radius * 2, int(radius * 1.35)), border_radius=10)
        pygame.draw.rect(screen, body_c, (x - radius + 5, yb - radius // 2 + 5, radius * 2 - 10, int(radius * 1.25) - 10), border_radius=8)
        # gas mask
        pygame.draw.ellipse(screen, (30, 50, 30), (x - 22, yb - radius // 2 - 6, 44, 32))
        pygame.draw.circle(screen, (40, 255, 60), (x - 10, yb - radius // 2 + 6), 8)
        pygame.draw.circle(screen, (40, 255, 60), (x + 10, yb - radius // 2 + 6), 8)
        pygame.draw.rect(screen, (20, 40, 20), (x - 6, yb - radius // 2 + 14, 12, 14))
        for i in range(-2, 3):
            pygame.draw.rect(screen, (20, 60, 20), (x + i * 14 - 5, yb + radius // 3, 10, 18), border_radius=2)
            pygame.draw.rect(screen, (120, 255, 80), (x + i * 14 - 3, yb + radius // 3 + 4, 6, 10))
        for i in range(6):
            a = current_time * 0.005 + i * 1.0
            pygame.draw.circle(screen, (150, 255, 80),
                               (int(x + math.cos(a) * (radius + 16)), int(yb + math.sin(a) * (radius + 12))), 4)

    elif bk == "cyber_colossus":
        # STEEL BLUE robot
        pygame.draw.rect(screen, (10, 20, 40), (x - radius - 4, yb - radius // 2 - 4, radius * 2 + 8, int(radius * 1.5) + 8), border_radius=4)
        pygame.draw.rect(screen, dark_c, (x - radius, yb - radius // 2, radius * 2, int(radius * 1.5)), border_radius=3)
        pygame.draw.rect(screen, body_c, (x - radius + 6, yb - radius // 2 + 6, radius * 2 - 12, int(radius * 1.4) - 12), border_radius=2)
        # antennas
        pygame.draw.line(screen, (180, 200, 220), (x - 12, yb - radius // 2), (x - 12, yb - radius - 24), 4)
        pygame.draw.line(screen, (180, 200, 220), (x + 12, yb - radius // 2), (x + 12, yb - radius - 18), 4)
        pygame.draw.circle(screen, (0, 255, 255), (x - 12, yb - radius - 26), 6)
        pygame.draw.circle(screen, (0, 200, 255), (x + 12, yb - radius - 20), 5)
        # reactor
        pygame.draw.circle(screen, (10, 30, 50), (x, yb + 4), 18)
        pygame.draw.circle(screen, (0, 255, 255), (x, yb + 4), 13)
        pygame.draw.circle(screen, WHITE, (x, yb + 4), 5)
        for side in (-1, 1):
            pygame.draw.rect(screen, (40, 60, 90), (x + side * (radius + 4) - 8, yb - 12, 16, 36), border_radius=3)
            pygame.draw.rect(screen, (0, 255, 255), (x + side * (radius + 4) - 4, yb - 6, 8, 12))
        pygame.draw.rect(screen, (0, 255, 255), (x - 14, yb - radius // 3, 10, 10))
        pygame.draw.rect(screen, (0, 255, 255), (x + 4, yb - radius // 3, 10, 10))

    elif bk == "chrono_wraith":
        # VIOLET ghost — translucent, clock halo
        s = pygame.Surface((radius * 3, radius * 3), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (*body_c, 160), (radius // 2, radius // 3, radius * 2, int(radius * 1.6)))
        screen.blit(s, (x - radius * 3 // 2, yb - radius))
        pygame.draw.circle(screen, (200, 120, 255), (x, yb), radius + 16, 2)
        for i in range(12):
            a = current_time * 0.004 + i * (math.tau / 12)
            pygame.draw.circle(screen, (255, 220, 80),
                               (int(x + math.cos(a) * (radius + 16)), int(yb + math.sin(a) * (radius + 16))), 4)
        pygame.draw.polygon(screen, (255, 230, 100), [(x - 10, yb - 4), (x + 10, yb - 4), (x, yb + 8)])
        pygame.draw.polygon(screen, (255, 200, 60), [(x - 10, yb + 20), (x + 10, yb + 20), (x, yb + 8)])
        pygame.draw.rect(screen, eye_c, (x - 16, yb - radius // 3, 10, 8))
        pygame.draw.rect(screen, eye_c, (x + 6, yb - radius // 3, 10, 8))
        for t in range(1, 5):
            pygame.draw.circle(screen, (140, 60, 200), (x - t * 14, yb), max(3, 10 - t * 2), 1)

    elif bk == "blood_moon_reaper":
        # CRIMSON hooded reaper with dual blades
        pygame.draw.polygon(screen, (20, 0, 5), [
            (x - 34, yb + 4), (x - 28, yb - radius - 10), (x, yb - radius - 40),
            (x + 28, yb - radius - 10), (x + 34, yb + 4)])
        pygame.draw.rect(screen, dark_c, (x - radius + 4, yb - radius // 3, radius * 2 - 8, int(radius * 1.2)), border_radius=6)
        pygame.draw.rect(screen, body_c, (x - radius + 8, yb - radius // 3 + 4, radius * 2 - 16, int(radius * 1.1) - 8), border_radius=4)
        pygame.draw.circle(screen, (255, 30, 50), (x, yb - radius - 44), 14)
        pygame.draw.circle(screen, (80, 0, 10), (x, yb - radius - 44), 8)
        pygame.draw.line(screen, (230, 230, 240), (x - radius - 6, yb + 10), (x - radius - 36, yb - 36), 5)
        pygame.draw.line(screen, (255, 60, 80), (x - radius - 6, yb + 10), (x - radius - 36, yb - 36), 2)
        pygame.draw.line(screen, (230, 230, 240), (x + radius + 6, yb + 10), (x + radius + 36, yb - 36), 5)
        pygame.draw.line(screen, (255, 60, 80), (x + radius + 6, yb + 10), (x + radius + 36, yb - 36), 2)
        pygame.draw.rect(screen, (200, 10, 30), (x - radius + 6, yb + 10, radius * 2 - 12, 8))
        pygame.draw.rect(screen, eye_c, (x - 14, yb - radius // 4, 10, 8))
        pygame.draw.rect(screen, eye_c, (x + 4, yb - radius // 4, 10, 8))

    elif bk == "swarm_heart":
        # HOT PINK beating core
        pulse = 1.0 + 0.2 * math.sin(current_time * 0.012)
        pygame.draw.circle(screen, dark_c, (x, yb), int(radius * pulse))
        pygame.draw.circle(screen, body_c, (x, yb), int(radius * 0.75 * pulse))
        pygame.draw.circle(screen, (255, 200, 230), (x, yb), int(radius * 0.35 * pulse))
        for i in range(10):
            a = current_time * 0.006 + i * (math.tau / 10)
            ox = int(x + math.cos(a) * (radius + 14))
            oy = int(yb + math.sin(a) * (radius + 14))
            pygame.draw.circle(screen, (255, 80, 180), (ox, oy), 7)
            pygame.draw.line(screen, (180, 30, 100), (x, yb), (ox, oy), 2)
        pygame.draw.circle(screen, eye_c, (x - 10, yb - 8), 6)
        pygame.draw.circle(screen, eye_c, (x + 10, yb - 8), 6)

    elif bk == "mirror_twin":
        # CHROME silver reflective
        pygame.draw.rect(screen, (200, 220, 255), (x - radius - 2, yb - radius // 2 - 2, radius * 2 + 4, int(radius * 1.4) + 4), border_radius=6)
        pygame.draw.rect(screen, body_c, (x - radius, yb - radius // 2, radius * 2, int(radius * 1.4)), border_radius=5)
        pygame.draw.rect(screen, (255, 255, 255), (x - radius + 8, yb - radius // 2 + 8, radius * 2 - 16, 10))
        pygame.draw.ellipse(screen, (180, 200, 230), (x - 20, yb - radius // 2 - 4, 40, 30))
        pygame.draw.ellipse(screen, WHITE, (x - 14, yb - radius // 2 + 2, 28, 18))
        pygame.draw.line(screen, (60, 80, 120), (x, yb - radius // 2 + 2), (x, yb - radius // 2 + 18), 2)
        pygame.draw.circle(screen, (220, 230, 250), (x - radius, yb), 16)
        pygame.draw.circle(screen, (220, 230, 250), (x + radius, yb), 16)
        pygame.draw.circle(screen, WHITE, (x - radius, yb), 16, 3)
        pygame.draw.circle(screen, WHITE, (x + radius, yb), 16, 3)
        for i in range(5):
            a = current_time * 0.005 + i * 1.2
            sx = int(x + math.cos(a) * (radius + 20))
            sy = int(yb + math.sin(a) * (radius + 20))
            pygame.draw.polygon(screen, WHITE, [(sx, sy - 8), (sx + 6, sy), (sx, sy + 8), (sx - 6, sy)])

    elif bk == "frost_titan":
        # ICE BLUE crystal titan
        pygame.draw.rect(screen, (200, 240, 255), (x - radius - 4, yb - radius // 2 - 4, radius * 2 + 8, int(radius * 1.5) + 8), border_radius=4)
        pygame.draw.rect(screen, dark_c, (x - radius, yb - radius // 2, radius * 2, int(radius * 1.5)), border_radius=3)
        pygame.draw.rect(screen, body_c, (x - radius + 5, yb - radius // 2 + 5, radius * 2 - 10, int(radius * 1.4) - 10), border_radius=2)
        pygame.draw.polygon(screen, (200, 245, 255), [
            (x - 26, yb - radius), (x - 16, yb - radius - 30), (x - 6, yb - radius - 10),
            (x, yb - radius - 36), (x + 6, yb - radius - 10), (x + 16, yb - radius - 30), (x + 26, yb - radius)])
        pygame.draw.rect(screen, (180, 230, 255), (x - 20, yb - 4, 40, 28), border_radius=3)
        pygame.draw.rect(screen, WHITE, (x - 14, yb + 4, 28, 10))
        for side in (-1, 1):
            pygame.draw.polygon(screen, (160, 220, 255), [
                (x + side * radius, yb - 8),
                (x + side * (radius + 28), yb - 24),
                (x + side * (radius + 22), yb + 16)])
        pygame.draw.rect(screen, WHITE, (x - 16, yb - radius // 3, 12, 10))
        pygame.draw.rect(screen, WHITE, (x + 4, yb - radius // 3, 12, 10))
        for i in range(5):
            pygame.draw.circle(screen, WHITE,
                               (x + int(math.sin(current_time * 0.004 + i) * radius),
                                yb - radius - 8 - (current_time // 35 + i * 11) % 28), 3)

    elif bk == "necro_conductor":
        # DARK PURPLE + amber staff
        pygame.draw.polygon(screen, (40, 10, 60), [
            (x - radius, yb - 10), (x - radius - 20, yb + radius + 16),
            (x + radius + 20, yb + radius + 16), (x + radius, yb - 10)])
        pygame.draw.rect(screen, dark_c, (x - radius + 4, yb - radius // 2, radius * 2 - 8, int(radius * 1.3)), border_radius=6)
        pygame.draw.rect(screen, body_c, (x - radius + 8, yb - radius // 2 + 4, radius * 2 - 16, int(radius * 1.2) - 8), border_radius=4)
        # staff
        pygame.draw.line(screen, (120, 80, 40), (x + radius // 2, yb + 16), (x + radius // 2, yb - radius - 40), 6)
        pygame.draw.circle(screen, (240, 230, 200), (x + radius // 2, yb - radius - 44), 12)
        pygame.draw.circle(screen, (20, 10, 30), (x + radius // 2 - 4, yb - radius - 46), 3)
        pygame.draw.circle(screen, (20, 10, 30), (x + radius // 2 + 4, yb - radius - 46), 3)
        for side in (-1, 1):
            pygame.draw.polygon(screen, (220, 210, 190), [
                (x + side * (radius - 4), yb - 20),
                (x + side * (radius + 16), yb - 28),
                (x + side * (radius - 4), yb - 4)])
        for i in range(8):
            a = current_time * 0.003 + i * (math.tau / 8)
            pygame.draw.circle(screen, (255, 170, 40),
                               (int(x + math.cos(a) * (radius + 14)), int(yb + math.sin(a) * (radius + 14))), 4)
        pygame.draw.rect(screen, eye_c, (x - 14, yb - radius // 3, 10, 8))
        pygame.draw.rect(screen, eye_c, (x + 4, yb - radius // 3, 10, 8))

    else:
        # fallback generic boss
        pygame.draw.rect(screen, body_c, (x - radius, yb - radius // 2, radius * 2, int(radius * 1.3)), border_radius=6)
        pygame.draw.rect(screen, eye_c, (x - 12, yb - radius // 3, 10, 8))
        pygame.draw.rect(screen, eye_c, (x + 2, yb - radius // 3, 10, 8))

    # HP bar + name
    bar_w = radius * 2 + 20
    pygame.draw.rect(screen, (40, 0, 0), (x - bar_w // 2, yb - radius - 18, bar_w, 8))
    pygame.draw.rect(screen, (255, 60, 60), (x - bar_w // 2, yb - radius - 18,
        int(bar_w * max(0, zombie["health"] / max(1, zombie["max_health"]))), 8))
    pygame.draw.rect(screen, GOLD, (x - bar_w // 2, yb - radius - 18, bar_w, 8), 1)
    if zombie.get("boss_name"):
        nm = FONT_TINY.render(zombie["boss_name"], True, body_c)
        screen.blit(nm, (x - nm.get_width() // 2, yb - radius - 36))



# =========================================================
# FRIENDS + GIFTS
# =========================================================
def get_friends():
    data = _load_accounts()
    rec = data.get(current_username) or {}
    return list(rec.get("friends") or [])


def get_friend_requests():
    data = _load_accounts()
    rec = data.get(current_username) or {}
    return list(rec.get("requests") or [])


def search_players(query):
    q = (query or "").strip().lower()
    if len(q) < 1:
        return []
    data = _load_accounts()
    out = []
    for name in data:
        if name != current_username and q in name.lower():
            out.append(name)
    return out[:12]


def send_friend_request(target):
    global friend_message
    target = (target or "").strip()
    if not current_username:
        friend_message = "LOGIN REQUIRED"; return False
    if not target or target == current_username:
        friend_message = "INVALID NAME"; return False
    data = _load_accounts()
    if target not in data:
        friend_message = "PLAYER NOT FOUND"; return False
    me = data.setdefault(current_username, {"password": "", "role": "player"})
    them = data[target]
    me.setdefault("friends", []); me.setdefault("requests", [])
    them.setdefault("friends", []); them.setdefault("requests", [])
    if target in me["friends"]:
        friend_message = "ALREADY FRIENDS"; return False
    if current_username in them.get("requests", []):
        friend_message = "REQUEST ALREADY SENT"; return False
    them.setdefault("requests", []).append(current_username)
    _save_accounts(data)
    friend_message = "REQUEST SENT TO " + target
    return True


def accept_friend_request(from_user):
    global friend_message
    data = _load_accounts()
    if not current_username or current_username not in data:
        return False
    me = data[current_username]
    me.setdefault("friends", []); me.setdefault("requests", [])
    if from_user not in me["requests"]:
        friend_message = "NO REQUEST"; return False
    me["requests"] = [u for u in me["requests"] if u != from_user]
    if from_user not in me["friends"]:
        me["friends"].append(from_user)
    if from_user in data:
        data[from_user].setdefault("friends", [])
        if current_username not in data[from_user]["friends"]:
            data[from_user]["friends"].append(current_username)
        data[from_user]["requests"] = [u for u in data[from_user].get("requests", []) if u != current_username]
    _save_accounts(data)
    friend_message = "NOW FRIENDS WITH " + from_user
    return True


def remove_friend(name):
    global friend_message
    data = _load_accounts()
    if not current_username or current_username not in data:
        return False
    me = data[current_username]
    me["friends"] = [f for f in me.get("friends", []) if f != name]
    if name in data:
        data[name]["friends"] = [f for f in data[name].get("friends", []) if f != current_username]
    _save_accounts(data)
    friend_message = "REMOVED " + name
    return True


def gift_to_friend(friend, kind, amount):
    global gems, coins, friend_message
    friend = (friend or "").strip()
    try:
        amount = int(amount)
    except (TypeError, ValueError):
        friend_message = "INVALID AMOUNT"; return False
    if amount <= 0:
        friend_message = "AMOUNT MUST BE > 0"; return False
    if friend not in get_friends():
        friend_message = "NOT YOUR FRIEND"; return False
    kind = (kind or "gems").lower()
    if kind == "gems":
        if gems < amount:
            friend_message = "NOT ENOUGH GEMS"; return False
        gems -= amount
    elif kind == "coins":
        if coins < amount:
            friend_message = "NOT ENOUGH COINS"; return False
        coins -= amount
    else:
        friend_message = "GIFT GEMS OR COINS"; return False
    save_profile()
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", friend)
    fpath = os.path.join(SAVES_DIR, safe + ".json")
    try:
        if os.path.isfile(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                pdata = json.load(f)
        else:
            pdata = {"coins": 0, "gems": 0, "unlocked": ["Survivor"]}
        if kind == "gems":
            pdata["gems"] = int(pdata.get("gems", 0)) + amount
        else:
            pdata["coins"] = int(pdata.get("coins", 0)) + amount
        os.makedirs(SAVES_DIR, exist_ok=True)
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(pdata, f, indent=2)
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        friend_message = "GIFT FAILED"; return False
    friend_message = "GIFTED %d %s TO %s" % (amount, kind.upper(), friend)
    return True


def draw_friends_screen():
    draw_zombie_bg(screen, pygame.time.get_ticks())
    center_text(screen, FONT_TITLE, "FRIENDS", (WIDTH // 2, 55), GOLD)
    panel = pygame.Rect(80, 100, WIDTH - 160, 520)
    draw_panel(screen, panel, (10, 13, 18), (70, 90, 110), 3)
    mx, my = pygame.mouse.get_pos()
    for idx, label in enumerate(("LIST", "SEARCH", "GIFT")):
        r = pygame.Rect(120 + idx * 160, 120, 140, 40)
        draw_button(screen, r, label, r.collidepoint(mx, my) or friends_tab == idx)
    if not current_username:
        center_text(screen, FONT_SMALL, "LOGIN TO USE FRIENDS", (WIDTH // 2, 300), RED)
    elif friends_tab == 0:
        center_text(screen, FONT_SMALL, "YOUR FRIENDS", (WIDTH // 2, 180), CYAN)
        fl = get_friends(); y = 210
        if not fl:
            center_text(screen, FONT_TINY, "NO FRIENDS YET — USE SEARCH", (WIDTH // 2, y), STONE_LIGHT); y += 30
        for name in fl[:10]:
            screen.blit(FONT_SMALL.render(name, True, WHITE), (140, y))
            draw_button(screen, pygame.Rect(WIDTH - 280, y - 4, 120, 32), "REMOVE", pygame.Rect(WIDTH - 280, y - 4, 120, 32).collidepoint(mx, my))
            y += 36
        y += 10
        center_text(screen, FONT_SMALL, "REQUESTS", (WIDTH // 2, y), GOLD); y += 28
        reqs = get_friend_requests()
        if not reqs:
            center_text(screen, FONT_TINY, "NO PENDING REQUESTS", (WIDTH // 2, y), STONE_LIGHT)
        for name in reqs[:6]:
            screen.blit(FONT_SMALL.render(name, True, WHITE), (140, y))
            draw_button(screen, pygame.Rect(WIDTH - 280, y - 4, 120, 32), "ACCEPT", pygame.Rect(WIDTH - 280, y - 4, 120, 32).collidepoint(mx, my))
            y += 36
    elif friends_tab == 1:
        center_text(screen, FONT_SMALL, "SEARCH PLAYERS", (WIDTH // 2, 180), CYAN)
        box = pygame.Rect(WIDTH // 2 - 200, 210, 400, 48)
        pygame.draw.rect(screen, (18, 22, 30), box, border_radius=8)
        pygame.draw.rect(screen, CYAN, box, 2, border_radius=8)
        screen.blit(FONT_SMALL.render(friend_search or "TYPE USERNAME...", True, WHITE if friend_search else STONE_LIGHT), (box.x + 14, box.y + 12))
        results = search_players(friend_search); y = 280
        for name in results:
            screen.blit(FONT_SMALL.render(name, True, WHITE), (WIDTH // 2 - 180, y))
            draw_button(screen, pygame.Rect(WIDTH // 2 + 60, y - 4, 140, 32), "ADD", pygame.Rect(WIDTH // 2 + 60, y - 4, 140, 32).collidepoint(mx, my))
            y += 38
        if friend_search and not results:
            center_text(screen, FONT_TINY, "NO MATCHES", (WIDTH // 2, 300), STONE_LIGHT)
    else:
        center_text(screen, FONT_SMALL, "GIFT TO A FRIEND", (WIDTH // 2, 180), CYAN)
        center_text(screen, FONT_TINY, "YOUR GEMS: %d   •   COINS: %s" % (gems, f"{coins:,}"), (WIDTH // 2, 210), GOLD)
        fl = get_friends(); y = 250
        for name in fl[:8]:
            screen.blit(FONT_SMALL.render(name, True, WHITE), (140, y))
            draw_button(screen, pygame.Rect(WIDTH - 420, y - 4, 130, 32), "GEM x" + gift_amount, pygame.Rect(WIDTH - 420, y - 4, 130, 32).collidepoint(mx, my))
            draw_button(screen, pygame.Rect(WIDTH - 270, y - 4, 130, 32), "COIN x" + gift_amount, pygame.Rect(WIDTH - 270, y - 4, 130, 32).collidepoint(mx, my))
            y += 38
        if not fl:
            center_text(screen, FONT_TINY, "ADD FRIENDS FIRST", (WIDTH // 2, 300), STONE_LIGHT)
        center_text(screen, FONT_TINY, "PRESS 1-9 TO SET GIFT AMOUNT", (WIDTH // 2, 520), STONE_LIGHT)
    if friend_message:
        center_text(screen, FONT_TINY, friend_message, (WIDTH // 2, 545), CYAN)
    draw_button(screen, pygame.Rect(WIDTH // 2 - 120, 570, 240, 40), "BACK", pygame.Rect(WIDTH // 2 - 120, 570, 240, 40).collidepoint(mx, my))


# =========================================================
# INTRO / PAUSE UI
# =========================================================
_BTN_CACHE = {}


def _button_skin(w, h, hovered):
    """Cached modern button plate: rounded, bevelled, gradient, gold glow on hover."""
    key = (w, h, hovered)
    if key in _BTN_CACHE:
        return _BTN_CACHE[key]
    pad = 16
    surf = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    bx, by = pad, pad
    rad = min(14, h // 2)

    # soft drop shadow
    for i in range(7, 0, -1):
        a = int(20 * (i / 7.0))
        pygame.draw.rect(surf, (0, 0, 0, a), (bx - i + 2, by - i + 5, w + i * 2, h + i * 2),
                         border_radius=rad + i)
    # outer glow when hovered
    if hovered:
        for i in range(10, 0, -1):
            a = int(15 * (i / 10.0) ** 1.6)
            pygame.draw.rect(surf, (*GOLD, a), (bx - i, by - i, w + i * 2, h + i * 2),
                             border_radius=rad + i)

    top = (74, 84, 104) if hovered else (48, 55, 70)
    bot = (30, 35, 47) if hovered else (22, 26, 35)
    plate = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        f = (y / max(1, h - 1)) ** 1.15
        pygame.draw.line(plate, _mix(top, bot, f), (0, y), (w, y))
    # top gloss
    gloss = pygame.Surface((w, h), pygame.SRCALPHA)
    gh = max(4, int(h * 0.46))
    for y in range(gh):
        a = int(52 * (1.0 - y / gh) ** 1.5)
        pygame.draw.line(gloss, (255, 255, 255, a), (0, y), (w, y))
    plate.blit(gloss, (0, 0))
    # rounded mask
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=rad)
    plate.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(plate, (bx, by))

    # borders: bright top bevel, dark bottom, accent frame
    pygame.draw.rect(surf, (*(GOLD if hovered else (92, 104, 124)), 255), (bx, by, w, h), 2, border_radius=rad)
    pygame.draw.line(surf, (255, 255, 255, 90), (bx + rad, by + 1), (bx + w - rad, by + 1), 2)
    pygame.draw.line(surf, (0, 0, 0, 110), (bx + rad, by + h - 2), (bx + w - rad, by + h - 2), 2)
    # small accent dots on the sides
    tick = GOLD if hovered else (108, 120, 142)
    pygame.draw.circle(surf, tick, (bx + 12, by + h // 2), 3)
    pygame.draw.circle(surf, tick, (bx + w - 12, by + h // 2), 3)

    _BTN_CACHE[key] = (surf, pad)
    return _BTN_CACHE[key]


def draw_button(surface, rect, text, hovered=False):
    skin, pad = _button_skin(rect.w, rect.h, hovered)
    surface.blit(skin, (rect.x - pad, rect.y - pad))
    label = FONT.render(text, True, GOLD if hovered else WHITE)
    if label.get_width() > rect.w - 22:
        label = FONT_SMALL.render(text, True, GOLD if hovered else WHITE)
    shadow = label.copy()
    shadow.fill((0, 0, 0, 190), special_flags=pygame.BLEND_RGBA_MULT)
    cx = rect.centerx - label.get_width() // 2
    cy = rect.centery - label.get_height() // 2
    surface.blit(shadow, (cx + 2, cy + 2))
    surface.blit(label, (cx, cy))


def draw_panel(surface, rect, fill=(14,18,24), border=(65,75,80), width=3):
    pygame.draw.rect(surface,(3,4,7),(rect.x+7,rect.y+7,rect.w,rect.h),border_radius=12)
    pygame.draw.rect(surface,fill,rect,border_radius=12)
    pygame.draw.rect(surface,border,rect,width,border_radius=12)

def center_text(surface,font,text,center,color=WHITE):
    img=font.render(text,True,color); surface.blit(img,(center[0]-img.get_width()//2,center[1]-img.get_height()//2))

def draw_coin_badge(surface,x,y):
    pygame.draw.circle(surface,GOLD,(x,y),18); pygame.draw.circle(surface,(255,235,120),(x,y),12,2)
    center_text(surface,FONT_TINY,"$",(x,y),BLACK)

# =========================================================
# ATMOSPHERIC BACKGROUNDS  (cached static art + live layers)
# =========================================================
_BG_CACHE = {}


def _vgrad(w, h, top, bottom, power=1.0):
    surf = pygame.Surface((w, h))
    for y in range(h):
        f = (y / max(1, h - 1)) ** power
        pygame.draw.line(surf, _mix(top, bottom, f), (0, y), (w, y))
    return surf


def _vignette(w, h, strength=170, radius=0.78):
    """Cached dark corner falloff."""
    v = pygame.Surface((w, h), pygame.SRCALPHA)
    steps = 46
    for i in range(steps):
        f = i / float(steps)
        a = int(strength * (f ** 2.4))
        inset_x = int(w * 0.5 * (1 - radius) * (1 - f) - w * 0.06 * f)
        inset_y = int(h * 0.5 * (1 - radius) * (1 - f) - h * 0.06 * f)
        pygame.draw.rect(v, (0, 0, 0, max(0, a // steps * 3)),
                         (inset_x, inset_y, w - inset_x * 2, h - inset_y * 2),
                         width=max(2, int(h * 0.02)), border_radius=int(h * 0.12))
    return v


def _build_menu_bg():
    """Night graveyard skyline — drawn once and reused."""
    rnd = random.Random(20260823)
    HORIZON = 452
    s = _vgrad(WIDTH, HEIGHT, (9, 10, 18), (33, 21, 26), 1.5)

    # stars
    for _ in range(150):
        sx, sy = rnd.randrange(WIDTH), rnd.randrange(HORIZON - 90)
        b = rnd.randint(70, 210)
        r = 1 if rnd.random() < 0.82 else 2
        pygame.draw.circle(s, (b, b, min(255, b + 18)), (sx, sy), r)

    # moon + halo
    mx, my, mr = 892, 118, 56
    halo = pygame.Surface((mr * 8, mr * 8), pygame.SRCALPHA)
    c = mr * 4
    for n in range(30, 0, -1):
        pygame.draw.circle(halo, (188, 200, 225, int(46 * ((30 - n) / 30.0) ** 2.3)),
                           (c, c), int(mr * 3.4 * n / 30))
    s.blit(halo, (mx - c, my - c))
    pygame.draw.circle(s, (206, 212, 228), (mx, my), mr)
    pygame.draw.circle(s, (226, 230, 242), (mx - 8, my - 10), mr - 10)
    for cx_, cy_, cr in ((-20, 12, 11), (14, -18, 8), (22, 20, 6), (-4, -6, 5), (30, -2, 4)):
        pygame.draw.circle(s, (186, 192, 210), (mx + cx_, my + cy_), cr)
    # thin cloud bands over the moon
    for i, (cy_, cw, ch, a) in enumerate(((104, 300, 16, 40), (140, 380, 12, 30), (76, 220, 10, 24))):
        band = pygame.Surface((cw, ch * 3), pygame.SRCALPHA)
        pygame.draw.ellipse(band, (150, 150, 175, a), (0, 0, cw, ch * 3))
        s.blit(band, (mx - cw // 2 - 40 + i * 30, cy_))

    # far skyline
    x = -30
    while x < WIDTH + 40:
        bw = rnd.randint(46, 104)
        bh = rnd.randint(70, 210)
        top = HORIZON - 66 - bh
        pygame.draw.rect(s, (17, 17, 27), (x, top, bw, bh + 70))
        if rnd.random() < 0.45:
            pygame.draw.rect(s, (17, 17, 27), (x + bw // 3, top - rnd.randint(14, 40),
                                               max(6, bw // 4), 44))
        for wy in range(top + 12, HORIZON - 60, 20):
            for wx in range(x + 8, x + bw - 8, 16):
                if rnd.random() < 0.16:
                    lit = rnd.choice([(196, 154, 60), (150, 120, 52), (92, 120, 140)])
                    pygame.draw.rect(s, lit, (wx, wy, 5, 7))
        x += bw + rnd.randint(2, 16)

    # haze band on the horizon
    haze = pygame.Surface((WIDTH, 120), pygame.SRCALPHA)
    for y in range(120):
        pygame.draw.line(haze, (70, 46, 52, int(70 * (1 - abs(y - 60) / 60.0))),
                         (0, y), (WIDTH, y))
    s.blit(haze, (0, HORIZON - 96))

    # ground
    ground = _vgrad(WIDTH, HEIGHT - HORIZON, (26, 24, 26), (12, 11, 14), 0.7)
    s.blit(ground, (0, HORIZON))
    for _ in range(420):
        gx = rnd.randrange(WIDTH)
        gy = rnd.randint(HORIZON, HEIGHT - 1)
        f = (gy - HORIZON) / float(HEIGHT - HORIZON)
        b = rnd.randint(18, 44)
        pygame.draw.circle(s, (b + 8, b, b - 2), (gx, gy), 1 if f < 0.5 else 2)
    for _ in range(26):  # grass tufts
        gx = rnd.randrange(WIDTH)
        gy = rnd.randint(HORIZON + 8, HEIGHT - 6)
        for d in (-3, 0, 3):
            pygame.draw.line(s, (36, 48, 34), (gx + d, gy), (gx + d * 2, gy - rnd.randint(5, 11)), 1)

    # iron fence along the horizon
    pygame.draw.rect(s, (14, 14, 18), (0, HORIZON - 8, WIDTH, 7))
    for fx in range(-6, WIDTH + 12, 22):
        pygame.draw.rect(s, (16, 16, 21), (fx, HORIZON - 52, 5, 46))
        pygame.draw.polygon(s, (16, 16, 21), [(fx - 2, HORIZON - 50), (fx + 2, HORIZON - 62),
                                              (fx + 7, HORIZON - 50)])
    pygame.draw.rect(s, (20, 20, 26), (0, HORIZON - 40, WIDTH, 4))

    # tombstones
    for tx, ty, tw, th, lean in ((92, 512, 54, 74, -3), (206, 486, 40, 54, 2), (330, 540, 62, 88, 1),
                                 (700, 494, 44, 60, -2), (826, 536, 58, 82, 3), (990, 500, 38, 52, -1)):
        stone = pygame.Surface((tw + 12, th + 14), pygame.SRCALPHA)
        pygame.draw.rect(stone, (0, 0, 0, 120), (6, 10, tw, th))
        pygame.draw.rect(stone, (44, 44, 52), (0, 4, tw, th), border_radius=tw // 2)
        pygame.draw.rect(stone, (62, 62, 72), (3, 7, tw - 8, th - 10), border_radius=tw // 2)
        pygame.draw.rect(stone, (34, 34, 42), (0, 4, tw, th), 2, border_radius=tw // 2)
        pygame.draw.rect(stone, (30, 30, 38), (tw // 2 - 9, 20, 18, 5))
        pygame.draw.rect(stone, (30, 30, 38), (tw // 2 - 3, 14, 6, 20))
        for ln in range(2):
            pygame.draw.line(stone, (30, 30, 38), (10, 44 + ln * 9), (tw - 12, 44 + ln * 9), 2)
        s.blit(pygame.transform.rotate(stone, lean), (tx, ty - th))
        pygame.draw.ellipse(s, (16, 16, 19), (tx - 6, ty - 8, tw + 22, 16))

    # dead trees
    def branch(x0, y0, ang, ln, w, depth):
        if depth == 0 or ln < 5:
            return
        x1 = x0 + math.cos(ang) * ln
        y1 = y0 + math.sin(ang) * ln
        pygame.draw.line(s, (13, 13, 17), (int(x0), int(y0)), (int(x1), int(y1)), max(1, int(w)))
        branch(x1, y1, ang - rnd.uniform(0.28, 0.62), ln * 0.72, w * 0.64, depth - 1)
        branch(x1, y1, ang + rnd.uniform(0.28, 0.62), ln * 0.72, w * 0.64, depth - 1)

    branch(148, 470, -math.pi / 2 - 0.06, 106, 13, 6)
    branch(958, 476, -math.pi / 2 + 0.08, 92, 11, 6)
    branch(520, 462, -math.pi / 2, 60, 7, 5)

    s.blit(_vignette(WIDTH, HEIGHT, 190, 0.72), (0, 0))
    return s


def draw_zombie_bg(surface, t):
    """Animated menu / login backdrop. `t` may be ms or seconds."""
    ms = t * 1000.0 if t < 5000 else float(t)

    static = _BG_CACHE.get("menu")
    if static is None:
        static = _build_menu_bg()
        _BG_CACHE["menu"] = static
    surface.blit(static, (0, 0))

    # drifting fog banks
    fog = _BG_CACHE.get("fog")
    if fog is None:
        small = pygame.Surface((WIDTH // 2, 60), pygame.SRCALPHA)
        rnd = random.Random(77)
        for _ in range(34):
            fx = rnd.randrange(WIDTH // 2)
            fy = rnd.randint(4, 34)
            fw = rnd.randint(70, 190)
            fh = rnd.randint(12, 28)
            pygame.draw.ellipse(small, (130, 134, 152, rnd.randint(10, 22)), (fx, fy, fw, fh))
        # upscaling a low-res layer gives soft, blurred fog edges
        fog = pygame.transform.smoothscale(small, (WIDTH * 2, 120))
        _BG_CACHE["fog"] = fog
    for row, (fy, spd, a) in enumerate(((392, 0.011, 150), (474, 0.019, 190), (566, 0.030, 120))):
        ox = -int((ms * spd) % WIDTH)
        layer = fog if a >= 190 else fog.copy()
        if a < 190:
            layer.set_alpha(a)
        surface.blit(layer, (ox, fy))
        surface.blit(layer, (ox + WIDTH, fy))

    # rising embers / dust motes
    for i in range(30):
        life = (ms * (0.00006 + (i % 5) * 0.000021) + i * 0.137) % 1.0
        ex = (i * 173 + 40 + math.sin(ms * 0.0007 + i) * 26) % WIDTH
        ey = HEIGHT + 18 - life * (HEIGHT * 0.86)
        a = int(200 * math.sin(life * math.pi))
        r = 2 if i % 4 else 3
        if a > 6:
            em = pygame.Surface((r * 6, r * 6), pygame.SRCALPHA)
            col = (255, 178, 92) if i % 3 else (156, 200, 255)
            pygame.draw.circle(em, (*col, a // 4), (r * 3, r * 3), r * 3)
            pygame.draw.circle(em, (*col, a), (r * 3, r * 3), r)
            surface.blit(em, (int(ex) - r * 3, int(ey) - r * 3))

    # slow lightning-free sky pulse near the horizon
    pulse = 0.5 + 0.5 * math.sin(ms * 0.00042)
    hz = pygame.Surface((WIDTH, 70), pygame.SRCALPHA)
    hz.fill((92, 40, 44, int(16 + 18 * pulse)))
    surface.blit(hz, (0, 388))


def draw_glass_panel(surface, rect, accent=GOLD, alpha=232):
    """Frosted dark panel with an accent frame and soft outer glow."""
    # additive blending ignores alpha, so scale the COLOUR down instead
    glow = pygame.Surface((rect.w + 80, rect.h + 80), pygame.SRCALPHA)
    for n in range(14, 0, -1):
        f = (14 - n) / 14.0
        col = _sh(accent, 0.030 * (f ** 1.8) + 0.004)
        pygame.draw.rect(glow, col, (40 - n * 2.6, 40 - n * 2.6,
                                     rect.w + n * 5.2, rect.h + n * 5.2),
                         3, border_radius=16 + n * 2)
    surface.blit(glow, (rect.x - 40, rect.y - 40), special_flags=pygame.BLEND_RGB_ADD)

    body = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    top = _mix((20, 23, 31), accent, 0.030)
    for y in range(rect.h):
        f = y / float(rect.h)
        pygame.draw.line(body, (*_mix(top, (9, 10, 14), f ** 0.8), alpha), (0, y), (rect.w, y))
    mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, rect.w, rect.h), border_radius=16)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surface.blit(body, rect.topleft)

    pygame.draw.rect(surface, _sh(accent, 0.55), rect, 3, border_radius=16)
    pygame.draw.rect(surface, (255, 255, 255, 30), rect.inflate(-8, -8), 1, border_radius=12)
    pygame.draw.line(surface, _sh(accent, 0.8), (rect.x + 26, rect.y + 4),
                     (rect.right - 26, rect.y + 4), 3)


def _build_arena_bg():
    """Cracked asphalt arena floor, generated once."""
    rnd = random.Random(4242)
    base = (36, 33, 41)
    s = pygame.Surface((WIDTH, HEIGHT))
    s.fill(base)

    # soft low-frequency mottling (upscaled noise, no checkerboard)
    noise = pygame.Surface((WIDTH // 25, HEIGHT // 25))
    for ny in range(noise.get_height()):
        for nx in range(noise.get_width()):
            v = rnd.randint(-5, 5)
            noise.set_at((nx, ny), (base[0] + v, base[1] + v, base[2] + v + 1))
    s.blit(pygame.transform.smoothscale(noise, (WIDTH, HEIGHT)), (0, 0))
    # grain
    for _ in range(11000):
        gx, gy = rnd.randrange(WIDTH), rnd.randrange(HEIGHT)
        v = rnd.randint(-11, 13)
        s.set_at((gx, gy), (max(0, base[0] + v), max(0, base[1] + v), max(0, base[2] + v)))

    # tile seams
    for x in range(0, WIDTH + 1, 50):
        pygame.draw.line(s, (26, 24, 30), (x, 0), (x, HEIGHT))
        pygame.draw.line(s, (45, 42, 52), (x + 1, 0), (x + 1, HEIGHT))
    for y in range(0, HEIGHT + 1, 50):
        pygame.draw.line(s, (26, 24, 30), (0, y), (WIDTH, y))
        pygame.draw.line(s, (45, 42, 52), (0, y + 1), (WIDTH, y + 1))

    # cracks
    for _ in range(16):
        cx, cy = rnd.randrange(WIDTH), rnd.randrange(HEIGHT)
        ang = rnd.uniform(0, math.tau)
        pts = [(cx, cy)]
        for _ in range(rnd.randint(5, 11)):
            ang += rnd.uniform(-0.7, 0.7)
            ln = rnd.randint(14, 44)
            cx += math.cos(ang) * ln
            cy += math.sin(ang) * ln
            pts.append((cx, cy))
        pygame.draw.lines(s, (17, 16, 20), False, pts, 3)
        pygame.draw.lines(s, (44, 42, 50), False, [(p[0] + 1, p[1] + 1) for p in pts], 1)

    # dried blood stains
    for _ in range(11):
        bx, by = rnd.randrange(60, WIDTH - 60), rnd.randrange(60, HEIGHT - 60)
        stain = pygame.Surface((150, 150), pygame.SRCALPHA)
        for _ in range(rnd.randint(5, 9)):
            ox, oy = rnd.randint(-28, 28), rnd.randint(-24, 24)
            pygame.draw.circle(stain, (54, 13, 15, rnd.randint(22, 40)), (75 + ox, 75 + oy),
                               rnd.randint(10, 24))
        for _ in range(rnd.randint(8, 16)):
            ox, oy = rnd.randint(-58, 58), rnd.randint(-52, 52)
            pygame.draw.circle(stain, (60, 15, 17, rnd.randint(18, 34)), (75 + ox, 75 + oy),
                               rnd.randint(2, 5))
        s.blit(stain, (bx - 75, by - 75))

    # hazard chevrons in the corners
    for corner in ((0, 0), (WIDTH - 150, HEIGHT - 44)):
        for i in range(6):
            pygame.draw.polygon(s, (52, 45, 22),
                                [(corner[0] + i * 26, corner[1] + 42),
                                 (corner[0] + i * 26 + 16, corner[1] + 42),
                                 (corner[0] + i * 26 + 30, corner[1] + 4),
                                 (corner[0] + i * 26 + 14, corner[1] + 4)])

    # drain grate
    gx, gy = 168, 552
    pygame.draw.rect(s, (18, 17, 21), (gx - 30, gy - 22, 60, 44), border_radius=5)
    pygame.draw.rect(s, (46, 44, 52), (gx - 30, gy - 22, 60, 44), 3, border_radius=5)
    for i in range(5):
        pygame.draw.rect(s, (11, 11, 14), (gx - 24, gy - 16 + i * 8, 48, 4), border_radius=2)

    # faded painted circle in the middle
    pygame.draw.circle(s, (48, 45, 39), (WIDTH // 2, HEIGHT // 2), 132, 4)
    pygame.draw.circle(s, (43, 40, 36), (WIDTH // 2, HEIGHT // 2), 118, 2)

    s.blit(_vignette(WIDTH, HEIGHT, 150, 0.84), (0, 0))
    return s


def draw_arena_bg(surface, t=0):
    """Gameplay floor: cached asphalt + live top danger strip."""
    art = _BG_CACHE.get("arena")
    if art is None:
        art = _build_arena_bg()
        _BG_CACHE["arena"] = art
    surface.blit(art, (0, 0))

    pulse = 0.5 + 0.5 * math.sin(t * 0.003)
    bar = pygame.Surface((WIDTH, 8), pygame.SRCALPHA)
    bar.fill((_mix((92, 26, 92), (168, 62, 168), pulse)))
    surface.blit(bar, (0, 0))
    pygame.draw.line(surface, (_mix((150, 60, 150), (230, 140, 230), pulse)), (0, 8), (WIDTH, 8), 2)


# =========================================================
# CHARACTER PORTRAIT ART  (high-detail, supersampled, cached)
# =========================================================
CHAR_ACCENT = {
    "Survivor": (70, 170, 255),      # sky blue
    "Ninja": (255, 45, 85),          # neon crimson
    "Engineer": (255, 200, 40),      # bright amber
    "Time Lord": (190, 110, 255),    # void violet
    "Frozen": (90, 230, 255),        # ice cyan
    "Scientist": (120, 255, 90),     # toxic green
    "Magician": (210, 70, 255),      # arcane magenta
    "Reaper": (180, 210, 255),       # spirit silver-blue
    "Storm Sovereign": (100, 220, 255),  # storm cyan
    "Executor": (255, 60, 40),            # blood-gold overlord
    "Priest": (255, 230, 120),            # holy gold
}
CHAR_SKIN = {
    "Survivor": (235, 185, 140),
    "Ninja": (210, 160, 120),
    "Engineer": (240, 195, 145),
    "Time Lord": (225, 190, 165),
    "Frozen": (195, 225, 245),
    "Scientist": (235, 200, 155),
    "Magician": (220, 175, 145),
    "Reaper": (240, 225, 210),
    "Storm Sovereign": (230, 240, 255),
    "Executor": (245, 220, 200),
    "Priest": (240, 220, 195),
}
CHAR_SUIT = {
    "Survivor": ((55, 120, 75), (32, 72, 45)),       # olive field ops
    "Ninja": ((28, 28, 38), (12, 12, 18)),           # shadow black
    "Engineer": ((200, 140, 30), (130, 85, 15)),     # hazard orange-gold
    "Time Lord": ((70, 40, 120), (35, 18, 70)),      # chrono purple
    "Frozen": ((40, 100, 145), (20, 55, 90)),        # deep ice blue
    "Scientist": ((55, 95, 55), (30, 55, 30)),       # lab green
    "Magician": ((90, 35, 130), (50, 15, 75)),       # mage purple
    "Reaper": ((22, 26, 38), (10, 12, 18)),          # void black
    "Storm Sovereign": ((20, 36, 60), (8, 16, 30)),  # storm navy
    "Executor": ((40, 12, 12), (18, 6, 6)),           # crimson void
    "Priest": ((230, 230, 240), (160, 160, 180)),     # sacred white
}
_PORTRAIT_CACHE = {}


def _sh(c, f):
    return (max(0, min(255, int(c[0] * f))), max(0, min(255, int(c[1] * f))), max(0, min(255, int(c[2] * f))))


def _mix(a, b, t):
    return (int(a[0] + (b[0] - a[0]) * t), int(a[1] + (b[1] - a[1]) * t), int(a[2] + (b[2] - a[2]) * t))


def _render_portrait_art(name, size, skin_name=None):
    """Draw a detailed bust portrait into a square SRCALPHA surface of `size` px."""
    SS = 3
    D = size * SS
    k = D / 200.0                      # 200 unit design space
    art = pygame.Surface((D, D), pygame.SRCALPHA)
    accent, skin, suit, suit_d = class_palette(name, skin_name)
    skin_hi = _mix(skin, WHITE, 0.30)
    skin_sh = _sh(skin, 0.72)
    skin_deep = _sh(skin, 0.55)

    def P(x, y):
        return (int(x * k), int(y * k))

    def R_(x, y, w, h):
        return pygame.Rect(int(x * k), int(y * k), max(1, int(w * k)), max(1, int(h * k)))

    def L(x1, y1, x2, y2, col, w):
        pygame.draw.line(art, col, P(x1, y1), P(x2, y2), max(1, int(w * k)))

    def PG(pts, col):
        pygame.draw.polygon(art, col, [P(*p) for p in pts])

    def CI(x, y, r, col, w=0):
        pygame.draw.circle(art, col, P(x, y), max(1, int(r * k)), 0 if w == 0 else max(1, int(w * k)))

    # ---------- backdrop: vertical gradient + accent glow ----------
    top = _mix((8, 10, 15), accent, 0.16)
    bot = (5, 6, 9)
    for i in range(D):
        t = i / max(1, D - 1)
        pygame.draw.line(art, _mix(top, bot, t * t), (0, i), (D, i))
    glow = pygame.Surface((D, D), pygame.SRCALPHA)
    for i in range(26, 0, -1):
        a = int(52 * (i / 26.0) ** 2.4)
        pygame.draw.circle(glow, (*accent, a), P(100, 86), int((26 - i + 6) * 2.6 * k))
    art.blit(glow, (0, 0))
    # floor light streak
    st = pygame.Surface((D, D), pygame.SRCALPHA)
    pygame.draw.ellipse(st, (*accent, 34), R_(18, 168, 164, 44))
    art.blit(st, (0, 0))

    # ---------- torso / shoulders ----------
    PG([(100, 128), (150, 150), (166, 205), (34, 205), (50, 150)], suit_d)
    PG([(100, 132), (144, 152), (156, 205), (44, 205), (56, 152)], suit)
    # shoulder highlight
    PG([(56, 152), (100, 132), (100, 142), (62, 162)], _mix(suit, WHITE, 0.16))
    PG([(144, 152), (100, 132), (100, 142), (138, 162)], _sh(suit, 0.86))
    # chest V / collar opening
    PG([(100, 190), (78, 138), (122, 138)], _sh(suit_d, 0.7))
    PG([(100, 176), (86, 140), (114, 140)], _mix(skin, suit_d, 0.55))
    # collar
    PG([(78, 137), (100, 178), (92, 136)], _mix(suit, WHITE, 0.10))
    PG([(122, 137), (100, 178), (108, 136)], _sh(suit, 0.9))
    L(78, 137, 100, 178, _sh(suit_d, 0.6), 2.2)
    L(122, 137, 100, 178, _sh(suit_d, 0.6), 2.2)
    # accent trim on shoulders
    L(58, 156, 96, 137, accent, 2.4)
    L(142, 156, 104, 137, accent, 2.4)

    # ---------- neck ----------
    PG([(88, 112), (112, 112), (114, 136), (86, 136)], skin_sh)
    PG([(90, 112), (108, 112), (108, 132), (92, 132)], _sh(skin, 0.85)) if False else None
    pygame.draw.ellipse(art, skin_deep, R_(86, 108, 28, 16))

    # ---------- head ----------
    HX, HY, HRX, HRY = 100, 82, 40, 45
    pygame.draw.ellipse(art, skin, R_(HX - HRX, HY - HRY, HRX * 2, HRY * 2))
    # jaw taper
    PG([(HX - 34, HY + 20), (HX + 34, HY + 20), (HX + 20, HY + 44), (HX - 20, HY + 44)], skin)
    pygame.draw.ellipse(art, skin, R_(HX - 26, HY + 16, 52, 34))
    # ears
    pygame.draw.ellipse(art, skin_sh, R_(HX - 44, HY - 4, 12, 20))
    pygame.draw.ellipse(art, skin_sh, R_(HX + 32, HY - 4, 12, 20))
    pygame.draw.ellipse(art, skin_deep, R_(HX - 41, HY + 1, 6, 11))
    pygame.draw.ellipse(art, skin_deep, R_(HX + 35, HY + 1, 6, 11))
    # shading: right side + under jaw
    sh_s = pygame.Surface((D, D), pygame.SRCALPHA)
    pygame.draw.ellipse(sh_s, (*_sh(skin, 0.55), 120), R_(HX + 8, HY - 40, 40, 84))
    pygame.draw.ellipse(sh_s, (*_sh(skin, 0.5), 90), R_(HX - 24, HY + 26, 48, 22))
    art.blit(sh_s, (0, 0))
    # highlight: upper-left
    hi_s = pygame.Surface((D, D), pygame.SRCALPHA)
    pygame.draw.ellipse(hi_s, (*skin_hi, 105), R_(HX - 34, HY - 34, 34, 40))
    pygame.draw.ellipse(hi_s, (*skin_hi, 70), R_(HX - 22, HY + 4, 16, 14))
    art.blit(hi_s, (0, 0))

    masked = name in ("Ninja", "Reaper", "Storm Sovereign")

    # ---------- eyes ----------
    eye_glow = {"Time Lord": GOLD, "Frozen": CYAN, "Magician": (200, 130, 255)}.get(name)
    if name == "Reaper":
        eye_glow = _mix(accent, (255, 60, 44), 0.62)
    for sx in (-1, 1):
        ex = HX + sx * 15
        ey = HY + 1
        # socket shadow
        pygame.draw.ellipse(art, skin_deep, R_(ex - 11, ey - 8, 22, 15))
        pygame.draw.ellipse(art, (246, 248, 252), R_(ex - 10, ey - 6.5, 20, 13))
        iris = eye_glow if eye_glow else _mix(accent, (40, 60, 90), 0.25)
        CI(ex + sx * 1, ey, 5.4, _sh(iris, 0.55))
        CI(ex + sx * 1, ey, 4.4, iris)
        CI(ex + sx * 1, ey, 2.1, (12, 12, 16))
        CI(ex + sx * 1 - 1.8, ey - 2.0, 1.5, (255, 255, 255))
        # upper lid line + lashes
        pygame.draw.arc(art, _sh(skin, 0.45), R_(ex - 10, ey - 8, 20, 16), 0.35, 2.8, max(1, int(2.0 * k)))
        if eye_glow:
            g = pygame.Surface((D, D), pygame.SRCALPHA)
            for i in range(8, 0, -1):
                pygame.draw.circle(g, (*eye_glow, int(26 * (i / 8.0) ** 2)), P(ex + sx, ey), int((10 - i) * 1.7 * k))
            art.blit(g, (0, 0))
        # eyebrow
        brow = {"Survivor": (58, 38, 26), "Ninja": (20, 20, 24), "Engineer": (66, 44, 28),
                "Time Lord": (120, 96, 54), "Frozen": (150, 200, 226), "Scientist": (110, 106, 100),
                "Magician": (200, 196, 204)}.get(name, (58, 54, 58))
        PG([(ex - 11, ey - 12), (ex + 10, ey - 15 + sx * 1), (ex + 10, ey - 11 + sx * 1), (ex - 11, ey - 8)], brow)

    # nose
    PG([(HX - 4, HY + 6), (HX + 5, HY + 6), (HX + 2, HY + 17), (HX - 3, HY + 17)], _sh(skin, 0.88))
    PG([(HX + 1, HY + 8), (HX + 6, HY + 17), (HX + 1, HY + 17)], skin_sh)
    CI(HX - 4, HY + 18, 1.6, skin_deep)
    CI(HX + 4, HY + 18, 1.6, skin_deep)

    if not masked:
        # mouth
        pygame.draw.arc(art, _sh(skin, 0.42), R_(HX - 11, HY + 18, 22, 16), 3.45, 6.0, max(1, int(2.4 * k)))
        pygame.draw.ellipse(art, _mix(skin, (170, 90, 90), 0.45), R_(HX - 9, HY + 24, 18, 5))
        # chin shadow
        pygame.draw.arc(art, _sh(skin, 0.62), R_(HX - 9, HY + 28, 18, 12), 3.5, 5.9, max(1, int(1.6 * k)))

    # ---------- per-character hair / headgear ----------
    if name == "Survivor":
        hair = (62, 40, 26)
        PG([(HX - 41, HY - 14), (HX - 34, HY - 42), (HX, HY - 50), (HX + 34, HY - 41), (HX + 41, HY - 12),
            (HX + 30, HY - 26), (HX, HY - 33), (HX - 30, HY - 25)], hair)
        PG([(HX - 36, HY - 30), (HX - 8, HY - 48), (HX + 6, HY - 44), (HX - 22, HY - 26)], _mix(hair, WHITE, 0.18))
        # bandana
        PG([(HX - 42, HY - 34), (HX + 42, HY - 32), (HX + 42, HY - 19), (HX - 42, HY - 21)], RED)
        PG([(HX - 42, HY - 34), (HX + 42, HY - 32), (HX + 42, HY - 27), (HX - 42, HY - 29)], _mix(RED, WHITE, 0.28))
        L(HX - 40, HY - 24, HX + 40, HY - 22, _sh(RED, 0.6), 1.8)
        PG([(HX + 40, HY - 28), (HX + 62, HY - 18), (HX + 58, HY - 8), (HX + 40, HY - 18)], _sh(RED, 0.8))
        # stubble + scar
        s2 = pygame.Surface((D, D), pygame.SRCALPHA)
        pygame.draw.ellipse(s2, (40, 32, 26, 46), R_(HX - 22, HY + 16, 44, 30))
        art.blit(s2, (0, 0))
        L(HX + 20, HY - 4, HX + 26, HY + 12, _mix(skin, (150, 70, 70), 0.55), 1.8)

    elif name == "Ninja":
        # hood
        PG([(HX - 46, HY + 6), (HX - 42, HY - 34), (HX, HY - 52), (HX + 42, HY - 34), (HX + 46, HY + 6),
            (HX + 38, HY - 6), (HX, HY - 14), (HX - 38, HY - 6)], (22, 24, 31))
        PG([(HX - 40, HY - 26), (HX - 6, HY - 48), (HX + 4, HY - 44), (HX - 28, HY - 20)], (40, 43, 54))
        # lower face mask
        PG([(HX - 40, HY + 8), (HX + 40, HY + 8), (HX + 30, HY + 34), (HX, HY + 46), (HX - 30, HY + 34)], (24, 26, 33))
        L(HX - 34, HY + 16, HX + 34, HY + 16, (46, 49, 60), 1.8)
        L(HX, HY + 12, HX, HY + 44, (14, 15, 19), 1.6)
        # headband
        PG([(HX - 46, HY - 26), (HX + 46, HY - 24), (HX + 46, HY - 10), (HX - 46, HY - 12)], RED)
        PG([(HX - 46, HY - 26), (HX + 46, HY - 24), (HX + 46, HY - 19), (HX - 46, HY - 21)], _mix(RED, WHITE, 0.3))
        CI(HX, HY - 18, 7, (240, 240, 245))
        CI(HX, HY - 18, 4.4, RED)
        PG([(HX - 46, HY - 20), (HX - 28, HY - 20), (HX - 28, HY - 12), (HX - 46, HY - 12)], _sh(RED, 0.75))
        PG([(HX + 28, HY - 20), (HX + 46, HY - 20), (HX + 46, HY - 12), (HX + 28, HY - 12)], _sh(RED, 0.75))
        # tails
        PG([(HX + 44, HY - 20), (HX + 76, HY + 4), (HX + 68, HY + 15), (HX + 42, HY - 12)], _sh(RED, 0.85))
        PG([(HX + 44, HY - 15), (HX + 72, HY + 19), (HX + 62, HY + 25), (HX + 42, HY - 5)], _sh(RED, 0.65))

    elif name == "Engineer":
        # hair tuft
        PG([(HX - 38, HY - 18), (HX, HY - 44), (HX + 38, HY - 18), (HX, HY - 28)], (68, 46, 30))
        # goggles pushed on forehead
        PG([(HX - 44, HY - 30), (HX + 44, HY - 28), (HX + 44, HY - 16), (HX - 44, HY - 18)], (48, 40, 34))
        for sx in (-1, 1):
            gx = HX + sx * 17
            CI(gx, HY - 23, 10, (28, 26, 30))
            CI(gx, HY - 23, 8, (70, 130, 150))
            CI(gx - 2, HY - 26, 3.2, (200, 240, 250))
            CI(gx, HY - 23, 10, (150, 152, 158), 1.6)
        # hard hat
        pygame.draw.ellipse(art, _sh(GOLD, 0.72), R_(HX - 52, HY - 42, 104, 22))
        pygame.draw.ellipse(art, GOLD, R_(HX - 50, HY - 44, 100, 18))
        pygame.draw.ellipse(art, _sh(GOLD, 0.9), R_(HX - 36, HY - 72, 72, 46))
        pygame.draw.ellipse(art, GOLD, R_(HX - 34, HY - 72, 68, 42))
        pygame.draw.ellipse(art, _mix(GOLD, WHITE, 0.45), R_(HX - 28, HY - 68, 26, 16))
        L(HX, HY - 70, HX, HY - 32, _sh(GOLD, 0.7), 3.0)
        # hi-vis stripes on suit
        L(64, 168, 78, 205, (232, 240, 245), 4.0)
        L(136, 168, 122, 205, (232, 240, 245), 4.0)

    elif name == "Time Lord":
        hair = (128, 104, 60)
        PG([(HX - 40, HY - 16), (HX - 32, HY - 42), (HX, HY - 50), (HX + 32, HY - 42), (HX + 40, HY - 16),
            (HX + 28, HY - 28), (HX, HY - 34), (HX - 28, HY - 28)], hair)
        # crown
        PG([(HX - 44, HY - 28), (HX + 44, HY - 26), (HX + 44, HY - 14), (HX - 44, HY - 16)], _sh(GOLD, 0.75))
        PG([(HX - 44, HY - 28), (HX + 44, HY - 26), (HX + 44, HY - 21), (HX - 44, HY - 23)], _mix(GOLD, WHITE, 0.4))
        for i, ox in enumerate((-32, -16, 0, 16, 32)):
            h = 20 if ox == 0 else (14 if abs(ox) == 16 else 10)
            PG([(HX + ox - 7, HY - 27), (HX + ox + 7, HY - 27), (HX + ox, HY - 27 - h)], GOLD)
            CI(HX + ox, HY - 25 - h * 0.55, 2.6, CYAN if ox == 0 else RED)
        # clock emblem on chest
        CI(100, 168, 15, _sh(GOLD, 0.7))
        CI(100, 168, 12.5, (24, 22, 34))
        CI(100, 168, 12.5, GOLD, 1.6)
        L(100, 168, 100, 160, GOLD, 1.8)
        L(100, 168, 106, 171, GOLD, 1.6)
        gl = pygame.Surface((D, D), pygame.SRCALPHA)
        for i in range(10, 0, -1):
            pygame.draw.circle(gl, (*GOLD, int(20 * (i / 10.0) ** 2)), P(100, 168), int((14 - i) * 2.2 * k))
        art.blit(gl, (0, 0))

    elif name == "Frozen":
        # frosted hair
        PG([(HX - 41, HY - 14), (HX - 32, HY - 44), (HX, HY - 52), (HX + 32, HY - 44), (HX + 41, HY - 14),
            (HX + 28, HY - 28), (HX, HY - 36), (HX - 28, HY - 28)], (168, 214, 238))
        PG([(HX - 34, HY - 32), (HX - 6, HY - 50), (HX + 4, HY - 46), (HX - 24, HY - 26)], (222, 244, 252))
        # ice crown spikes
        for ox, h in ((-30, 20), (-15, 30), (0, 40), (15, 30), (30, 20)):
            PG([(HX + ox - 8, HY - 26), (HX + ox + 8, HY - 26), (HX + ox, HY - 26 - h)], (150, 224, 245))
            PG([(HX + ox - 3, HY - 26), (HX + ox + 2, HY - 26), (HX + ox, HY - 26 - h * 0.85)], (232, 252, 255))
        # frost on cheeks
        fr = pygame.Surface((D, D), pygame.SRCALPHA)
        for sx in (-1, 1):
            for i in range(5):
                pygame.draw.circle(fr, (235, 252, 255, 90), P(HX + sx * (22 + i * 2), HY + 12 + i * 3), int(2.4 * k))
        art.blit(fr, (0, 0))
        # icy armor plates
        PG([(62, 158), (100, 146), (138, 158), (132, 178), (68, 178)], (86, 150, 190))
        L(62, 158, 100, 146, (206, 240, 252), 2.0)
        L(138, 158, 100, 146, (206, 240, 252), 2.0)

    elif name == "Scientist":
        hair = (128, 126, 124)
        PG([(HX - 41, HY - 12), (HX - 33, HY - 44), (HX, HY - 51), (HX + 33, HY - 44), (HX + 41, HY - 12),
            (HX + 30, HY - 26), (HX, HY - 34), (HX - 30, HY - 26)], hair)
        PG([(HX - 34, HY - 30), (HX - 4, HY - 49), (HX + 6, HY - 44), (HX - 24, HY - 24)], (176, 176, 178))
        # round glasses
        for sx in (-1, 1):
            gx = HX + sx * 15
            lens = pygame.Surface((D, D), pygame.SRCALPHA)
            pygame.draw.circle(lens, (150, 200, 225, 70), P(gx, HY + 1), int(13 * k))
            art.blit(lens, (0, 0))
            CI(gx, HY + 1, 13, (206, 210, 218), 2.4)
            L(gx - 6, HY - 6, gx + 1, HY - 9, (245, 248, 252), 1.6)
        L(HX - 3, HY + 1, HX + 3, HY + 1, (206, 210, 218), 2.0)
        L(HX - 28, HY - 1, HX - 42, HY - 5, (206, 210, 218), 2.0)
        L(HX + 28, HY - 1, HX + 42, HY - 5, (206, 210, 218), 2.0)
        # lab coat lapels + tie + pen
        PG([(100, 178), (86, 140), (114, 140)], (58, 72, 96))
        PG([(100, 176), (94, 146), (106, 146)], (86, 140, 200))
        L(122, 150, 126, 168, (70, 180, 120), 3.0)
        # test tube
        PG([(140, 162), (150, 162), (150, 190), (140, 190)], (210, 226, 236))
        PG([(141, 176), (149, 176), (149, 189), (141, 189)], (110, 220, 140))

    elif name == "Magician":
        hair = (206, 202, 212)
        PG([(HX - 40, HY - 12), (HX - 32, HY - 40), (HX, HY - 48), (HX + 32, HY - 40), (HX + 40, HY - 12),
            (HX + 28, HY - 24), (HX, HY - 32), (HX - 28, HY - 24)], hair)
        # wizard hat
        PG([(HX - 58, HY - 24), (HX + 58, HY - 22), (HX + 52, HY - 12), (HX - 52, HY - 14)], _sh(PURPLE, 0.6))
        PG([(HX - 58, HY - 24), (HX + 58, HY - 22), (HX + 54, HY - 30), (HX - 54, HY - 32)], PURPLE)
        PG([(HX - 34, HY - 30), (HX + 34, HY - 28), (HX + 12, HY - 84), (HX - 4, HY - 88)], PURPLE)
        PG([(HX - 34, HY - 30), (HX - 8, HY - 29), (HX + 2, HY - 86), (HX - 4, HY - 88)], _mix(PURPLE, WHITE, 0.22))
        PG([(HX + 12, HY - 50), (HX + 30, HY - 49), (HX + 26, HY - 38), (HX + 16, HY - 38)], _sh(PURPLE, 0.55))
        # hat band + gem
        PG([(HX - 40, HY - 34), (HX + 40, HY - 32), (HX + 38, HY - 42), (HX - 38, HY - 44)], (34, 22, 52))
        PG([(HX - 6, HY - 34), (HX + 6, HY - 34), (HX + 9, HY - 40), (HX, HY - 46), (HX - 9, HY - 40)], CYAN)
        # sparkles
        sp = pygame.Surface((D, D), pygame.SRCALPHA)
        for sx, sy, r in ((44, 44, 4.2), (156, 60, 3.4), (36, 100, 2.8), (162, 118, 3.8), (150, 30, 2.6)):
            for i in range(6, 0, -1):
                pygame.draw.circle(sp, (220, 160, 255, int(30 * (i / 6.0) ** 2)), P(sx, sy), int(r * i * 0.6 * k))
            pygame.draw.line(sp, (245, 225, 255, 230), P(sx - r, sy), P(sx + r, sy), max(1, int(1.4 * k)))
            pygame.draw.line(sp, (245, 225, 255, 230), P(sx, sy - r), P(sx, sy + r), max(1, int(1.4 * k)))
        art.blit(sp, (0, 0))
        # cloak clasp
        CI(100, 158, 7, GOLD)
        CI(100, 158, 4, PURPLE)

    elif name == "Reaper":
        # ---------------- ANIME SHINIGAMI ----------------
        HAIR = _mix((226, 232, 246), accent, 0.20)
        HAIR_D = _sh(HAIR, 0.58)
        HAIR_L = _mix(HAIR, WHITE, 0.55)
        BAND = _mix((228, 52, 56), accent, 0.14)
        BAND_D = _sh(BAND, 0.6)

        # katana slung behind the shoulder (drawn first so the body covers the hilt)
        L(HX + 20, HY + 80, HX + 84, HY - 34, (14, 15, 19), 6.4)
        L(HX + 22, HY + 78, HX + 82, HY - 32, _mix(accent, WHITE, 0.6), 3.0)
        L(HX + 12, HY + 92, HX + 28, HY + 66, (40, 28, 22), 6.4)
        CI(HX + 24, HY + 76, 5, GOLD)

        # back hair: sharp spikes fanning out behind the head
        for a0, ln in ((-2.75, 46), (-2.35, 54), (-1.95, 58), (-1.55, 56),
                       (-1.15, 58), (-0.75, 54), (-0.35, 46)):
            tipx = HX + math.cos(a0) * ln
            tipy = HY + math.sin(a0) * ln + 4
            PG([(HX + math.cos(a0 - 0.22) * 30, HY + math.sin(a0 - 0.22) * 30),
                (tipx, tipy),
                (HX + math.cos(a0 + 0.22) * 30, HY + math.sin(a0 + 0.22) * 30)], HAIR_D)
        # side locks framing the cheeks
        PG([(HX - 40, HY - 22), (HX - 30, HY - 26), (HX - 26, HY + 34), (HX - 38, HY + 18)], HAIR_D)
        PG([(HX + 40, HY - 22), (HX + 30, HY - 26), (HX + 26, HY + 34), (HX + 38, HY + 18)], HAIR_D)
        PG([(HX - 38, HY - 20), (HX - 31, HY - 24), (HX - 28, HY + 24), (HX - 36, HY + 12)], HAIR)
        PG([(HX + 38, HY - 20), (HX + 31, HY - 24), (HX + 28, HY + 24), (HX + 36, HY + 12)], HAIR)

        # ---- big anime eyes, painted over the default ones ----
        for sx in (-1, 1):
            ex, ey = HX + sx * 16, HY - 2
            # socket clean-up so the base eye never peeks out
            pygame.draw.ellipse(art, skin, R_(ex - 14, ey - 14, 28, 26))
            # eye white
            PG([(ex - 12, ey - 6), (ex - 2, ey - 11), (ex + 11, ey - 6),
                (ex + 8, ey + 8), (ex - 8, ey + 8)], (250, 251, 255))
            pygame.draw.ellipse(art, (250, 251, 255), R_(ex - 11, ey - 9, 22, 18))
            # iris: tall anime oval with a gradient
            IR = _mix((255, 64, 62), accent, 0.22)
            pygame.draw.ellipse(art, _sh(IR, 0.45), R_(ex - 7, ey - 9, 14, 18))
            pygame.draw.ellipse(art, IR, R_(ex - 6, ey - 7, 12, 15))
            pygame.draw.ellipse(art, _mix(IR, WHITE, 0.4), R_(ex - 5, ey + 1, 10, 6))
            # pupil + catch lights
            pygame.draw.ellipse(art, (16, 12, 18), R_(ex - 2.6, ey - 5, 5.2, 11))
            CI(ex - 3.2, ey - 5.2, 2.6, (255, 255, 255))
            CI(ex + 3.0, ey + 3.4, 1.5, (255, 255, 255))
            # thick upper lash line + outer flick
            PG([(ex - 13, ey - 7), (ex - 2, ey - 13), (ex + 12, ey - 7),
                (ex + 12, ey - 4), (ex - 2, ey - 9), (ex - 13, ey - 4)], (22, 18, 26))
            PG([(ex + sx * 12, ey - 8), (ex + sx * 19, ey - 13), (ex + sx * 14, ey - 4)], (22, 18, 26))
            # lower lid
            L(ex - 8, ey + 8, ex + 8, ey + 8, _sh(skin, 0.55), 1.6)
            # sharp brow
            PG([(ex - sx * 13, ey - 19), (ex + sx * 12, ey - 24),
                (ex + sx * 12, ey - 20), (ex - sx * 13, ey - 16)], HAIR_D)
            # eye shine
            eg = pygame.Surface((D, D), pygame.SRCALPHA)
            for i in range(8, 0, -1):
                pygame.draw.circle(eg, (*IR, int(20 * (i / 8.0) ** 2)), P(ex, ey), int((9 - i) * 2.2 * k))
            art.blit(eg, (0, 0))

        # small anime mouth
        L(HX - 5, HY + 30, HX + 5, HY + 30, _sh(skin, 0.5), 1.8)
        PG([(HX - 4, HY + 30), (HX + 4, HY + 30), (HX, HY + 35)], _mix(skin, (168, 88, 92), 0.5))
        # cheek blush
        bl = pygame.Surface((D, D), pygame.SRCALPHA)
        pygame.draw.ellipse(bl, (*_mix(skin, (240, 120, 120), 0.6), 70), R_(HX - 34, HY + 8, 18, 9))
        pygame.draw.ellipse(bl, (*_mix(skin, (240, 120, 120), 0.6), 70), R_(HX + 16, HY + 8, 18, 9))
        art.blit(bl, (0, 0))

        # ---- front bangs: sharp anime spikes over the forehead ----
        PG([(HX - 42, HY - 18), (HX - 36, HY - 46), (HX - 12, HY - 50), (HX - 20, HY - 18)], HAIR_D)
        PG([(HX - 22, HY - 18), (HX - 8, HY - 50), (HX + 12, HY - 48), (HX + 4, HY - 16)], HAIR_D)
        PG([(HX + 2, HY - 17), (HX + 16, HY - 48), (HX + 38, HY - 42), (HX + 42, HY - 16)], HAIR_D)
        PG([(HX - 40, HY - 20), (HX - 34, HY - 44), (HX - 16, HY - 47), (HX - 22, HY - 21)], HAIR)
        PG([(HX - 20, HY - 21), (HX - 7, HY - 47), (HX + 9, HY - 45), (HX + 2, HY - 19)], HAIR)
        PG([(HX + 4, HY - 20), (HX + 17, HY - 45), (HX + 36, HY - 40), (HX + 40, HY - 19)], HAIR)
        # glossy hair highlight band
        PG([(HX - 30, HY - 36), (HX - 6, HY - 43), (HX - 4, HY - 38), (HX - 28, HY - 31)], HAIR_L)
        PG([(HX + 8, HY - 41), (HX + 30, HY - 35), (HX + 29, HY - 30), (HX + 8, HY - 36)], HAIR_L)
        # crown spikes: long, thin, sharply tapered
        for a0, ln, tilt in ((-2.70, 72, -0.34), (-2.40, 60, -0.26), (-2.08, 74, -0.16),
                             (-1.76, 58, -0.06), (-1.44, 70, 0.06), (-1.10, 56, 0.16),
                             (-0.76, 64, 0.26), (-0.46, 50, 0.34)):
            tipx = HX + math.cos(a0 + tilt * 0.5) * ln
            tipy = HY + math.sin(a0 + tilt * 0.5) * ln - 6
            PG([(HX + math.cos(a0 - 0.30) * 34, HY + math.sin(a0 - 0.30) * 34),
                (tipx, tipy),
                (HX + math.cos(a0 + 0.30) * 34, HY + math.sin(a0 + 0.30) * 34)], HAIR_D)
            PG([(HX + math.cos(a0 - 0.24) * 32, HY + math.sin(a0 - 0.24) * 32),
                (tipx, tipy),
                (HX + math.cos(a0 + 0.24) * 32, HY + math.sin(a0 + 0.24) * 32)], HAIR)
            L(HX + math.cos(a0) * 34, HY + math.sin(a0) * 34, tipx, tipy, HAIR_L, 1.3)

        # ---- headband with trailing ribbon (over the bangs) ----
        PG([(HX - 41, HY - 24), (HX + 41, HY - 24), (HX + 40, HY - 11), (HX - 40, HY - 11)], BAND_D)
        PG([(HX - 40, HY - 23), (HX + 40, HY - 23), (HX + 39, HY - 16), (HX - 39, HY - 16)], BAND)
        L(HX - 40, HY - 13, HX + 40, HY - 13, _sh(BAND_D, 0.75), 1.6)
        CI(HX, HY - 18, 6.4, _mix(BAND, WHITE, 0.4))
        CI(HX, HY - 18, 3.2, (30, 22, 26))
        PG([(HX - 40, HY - 22), (HX - 72, HY - 40), (HX - 66, HY - 30), (HX - 39, HY - 12)], BAND_D)
        PG([(HX - 41, HY - 21), (HX - 69, HY - 38), (HX - 66, HY - 33), (HX - 40, HY - 14)], BAND)
        PG([(HX - 46, HY - 26), (HX - 78, HY - 22), (HX - 72, HY - 13), (HX - 44, HY - 18)], BAND_D)

        # ---- scarf over the shoulders ----
        PG([(HX - 34, HY + 44), (HX + 34, HY + 44), (HX + 40, HY + 62), (HX - 40, HY + 62)], _sh(BAND_D, 0.85))
        PG([(HX - 32, HY + 46), (HX + 32, HY + 46), (HX + 36, HY + 57), (HX - 36, HY + 57)], BAND)
        PG([(HX + 30, HY + 50), (HX + 62, HY + 66), (HX + 54, HY + 78), (HX + 28, HY + 60)], BAND_D)
        PG([(HX + 30, HY + 52), (HX + 58, HY + 66), (HX + 54, HY + 72), (HX + 29, HY + 58)], BAND)
        L(HX - 30, HY + 52, HX + 30, HY + 52, _mix(BAND, WHITE, 0.3), 1.6)

        # ---- anime speed lines + petals in the backdrop ----
        sp = pygame.Surface((D, D), pygame.SRCALPHA)
        for i in range(9):
            yy = 24 + i * 19
            pygame.draw.line(sp, (255, 255, 255, 26), P(6, yy), P(30 + (i % 3) * 12, yy - 6), max(1, int(1.4 * k)))
            pygame.draw.line(sp, (255, 255, 255, 26), P(194, yy + 8), P(168 - (i % 3) * 12, yy + 2),
                             max(1, int(1.4 * k)))
        art.blit(sp, (0, 0))
        pt = pygame.Surface((D, D), pygame.SRCALPHA)
        for px, py, pr in ((28, 150, 4), (170, 60, 3.4), (40, 52, 3), (158, 148, 4.2), (60, 186, 3)):
            pygame.draw.ellipse(pt, (*_mix(BAND, WHITE, 0.35), 150),
                                (int((px - pr) * k), int((py - pr * 0.6) * k),
                                 int(pr * 2 * k), int(pr * 1.2 * k)))
        art.blit(pt, (0, 0))

    # ---------- global rim light + vignette ----------
    rim = pygame.Surface((D, D), pygame.SRCALPHA)
    pygame.draw.arc(rim, (*_mix(accent, WHITE, 0.35), 150), R_(HX - HRX - 2, HY - HRY - 2, HRX * 2 + 4, HRY * 2 + 4),
                    1.5, 3.5, max(1, int(2.6 * k)))
    art.blit(rim, (0, 0))
    vig = pygame.Surface((D, D), pygame.SRCALPHA)
    for i in range(22):
        a = int(9 + i * 3.2)
        pygame.draw.circle(vig, (0, 0, 0, a), (D // 2, D // 2), D // 2 - i * max(1, int(1.6 * k)), max(1, int(2 * k)))
    art.blit(vig, (0, 0))

    # ---------- circular mask ----------
    mask = pygame.Surface((D, D), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (D // 2, D // 2), D // 2 - int(1 * k))
    art.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    return pygame.transform.smoothscale(art, (size, size))


def draw_character_portrait(surface, name, cx, cy, scale=1.0, selected=False, skin_name=None):
    if name not in CHAR_ACCENT:
        name = "Survivor"
    r = max(20, int(85 * scale))
    size = r * 2
    skin_name = skin_name or equipped_skin_name(name)
    key = (name, size, skin_name)
    art = _PORTRAIT_CACHE.get(key)
    if art is None:
        art = _render_portrait_art(name, size, skin_name)
        _PORTRAIT_CACHE[key] = art
    accent = class_palette(name, skin_name)[0]

    t = pygame.time.get_ticks()
    # outer glow (animated when selected)
    pulse = 0.5 + 0.5 * math.sin(t * 0.0032)
    layers = 12 if selected else 6
    g = pygame.Surface((size + 60, size + 60), pygame.SRCALPHA)
    for i in range(layers, 0, -1):
        a = int((34 if selected else 16) * (i / float(layers)) ** 2.2 * (0.65 + 0.35 * pulse))
        pygame.draw.circle(g, (*accent, a), (g.get_width() // 2, g.get_height() // 2), r + int((layers - i) * 2.2) + 4)
    surface.blit(g, (cx - g.get_width() // 2, cy - g.get_height() // 2))

    # drop shadow
    sh = pygame.Surface((size + 20, size + 20), pygame.SRCALPHA)
    pygame.draw.circle(sh, (0, 0, 0, 110), (sh.get_width() // 2, sh.get_height() // 2), r + 4)
    surface.blit(sh, (cx - sh.get_width() // 2, cy - sh.get_height() // 2 + max(3, r // 18)))

    surface.blit(art, (cx - r, cy - r))

    # frame rings
    pygame.draw.circle(surface, _sh(accent, 0.45), (cx, cy), r + 1, max(2, r // 26))
    pygame.draw.circle(surface, accent, (cx, cy), r, max(2, r // 34))
    if selected:
        pygame.draw.circle(surface, _mix(accent, WHITE, 0.45), (cx, cy), r + max(5, r // 12), max(2, r // 30))
        # rotating tick marks
        for i in range(12):
            ang = t * 0.0008 + i * math.pi / 6
            rr = r + max(5, r // 12)
            x1, y1 = cx + math.cos(ang) * (rr - 3), cy + math.sin(ang) * (rr - 3)
            x2, y2 = cx + math.cos(ang) * (rr + 5), cy + math.sin(ang) * (rr + 5)
            pygame.draw.line(surface, accent, (int(x1), int(y1)), (int(x2), int(y2)), max(2, r // 40))


# Shared hitboxes: drawing AND click detection both use these.
CHAR_BUY_RECT = pygame.Rect(540, 492, 235, 52)
SKIN_BUY_RECT = pygame.Rect(795, 492, 235, 52)
CHAR_LEFT_RECT = pygame.Rect(15, 300, 60, 70)
CHAR_RIGHT_RECT = pygame.Rect(WIDTH - 75, 300, 60, 70)
CHAR_BACK_RECT = pygame.Rect(45, 618, 200, 48)
SKIN_LEFT_RECT = pygame.Rect(70, 500, 44, 44)
SKIN_RIGHT_RECT = pygame.Rect(406, 500, 44, 44)


def clamp_skin_index():
    """Keep the skin cursor inside the current class's skin list."""
    global skin_index
    names = class_list()
    name = names[character_index % len(names)]
    skin_index %= len(class_skin_list(name))


def draw_character_screen():
    global skin_index
    t = pygame.time.get_ticks(); draw_zombie_bg(screen, t)
    center_text(screen, FONT_TITLE, "CLASS SELECT", (WIDTH // 2, 58), GOLD)
    coinbox = pygame.Rect(WIDTH - 220, 25, 185, 55)
    draw_panel(screen, coinbox, (20, 23, 30), GOLD, 2)
    draw_coin_badge(screen, coinbox.x + 28, coinbox.centery)
    center_text(screen, FONT, f"{coins:,}", (coinbox.x + 112, coinbox.centery), WHITE)

    names = class_list()
    name = names[character_index % len(names)]
    price = CHARACTER_PRICES[name]
    ability, desc = CHARACTER_ABILITIES[name]
    owned = name in unlocked_characters
    skins = class_skin_list(name)
    skin_index %= len(skins)
    skin = skins[skin_index]
    has_skin = skin_owned(name, skin)
    skin_on = equipped_skin_name(name) == skin["name"]
    mx, my = pygame.mouse.get_pos()

    # ---------------- preview panel ----------------
    preview = pygame.Rect(45, 135, 430, 470)
    draw_panel(screen, preview)
    center_text(screen, FONT_SMALL, "CLASS PREVIEW", (preview.centerx, 164), STONE_LIGHT)
    draw_character_portrait(screen, name, preview.centerx, 316, 1.22, True, skin["name"])
    center_text(screen, FONT_NAME, name.upper(), (preview.centerx, 442), WHITE)
    role = CLASS_ROLES.get(name, "SURVIVOR")
    center_text(screen, FONT_SMALL, role, (preview.centerx, 472), CYAN)
    if name in ADMIN_CLASSES:
        tag = pygame.Rect(preview.centerx - 102, 190, 204, 26)
        pygame.draw.rect(screen, (60, 20, 24), tag, border_radius=8)
        pygame.draw.rect(screen, GOLD, tag, 2, border_radius=8)
        center_text(screen, FONT_TINY, "ADMIN ONLY CLASS", tag.center, GOLD)

    # skin picker row
    for rect, sym in ((SKIN_LEFT_RECT, "<"), (SKIN_RIGHT_RECT, ">")):
        hov = rect.collidepoint(mx, my)
        pygame.draw.rect(screen, (18, 22, 29), rect, border_radius=9)
        pygame.draw.rect(screen, GOLD if hov else STONE_LIGHT, rect, 2, border_radius=9)
        center_text(screen, FONT, sym, rect.center, WHITE)
    acc = class_palette(name, skin["name"])[0]
    sw = pygame.Rect(preview.centerx - 125, 505, 250, 34)
    pygame.draw.rect(screen, (14, 16, 22), sw, border_radius=8)
    pygame.draw.rect(screen, acc, sw, 2, border_radius=8)
    center_text(screen, FONT_SMALL, skin["name"], sw.center, WHITE)
    if skin_on:
        skin_state, skin_col = "SKIN EQUIPPED", CYAN
    elif has_skin:
        skin_state, skin_col = "SKIN OWNED", GREEN
    else:
        skin_state, skin_col = f"SKIN LOCKED  •  {skin['price']:,} COINS", GOLD
    center_text(screen, FONT_TINY, skin_state, (preview.centerx, 556), skin_col)
    center_text(screen, FONT_TINY, f"SKIN {skin_index + 1} / {len(skins)}   •   Q / E", (preview.centerx, 578), STONE_LIGHT)

    # ---------------- info panel ----------------
    info = pygame.Rect(515, 135, 540, 470)
    draw_panel(screen, info)
    center_text(screen, FONT_TINY, "SPECIAL ABILITY", (info.centerx, 166), STONE_LIGHT)
    center_text(screen, FONT_NAME, ability, (info.centerx, 204), GOLD)
    center_text(screen, FONT_ABILITY, desc, (info.centerx, 244), WHITE)
    stats = CHARACTER_STATS[name]
    center_text(screen, FONT_TINY, stats["passive"], (info.centerx, 274), CYAN)
    stat_labels = [("HP", stats["hp"] / 130.0), ("SPEED", stats["speed"] / 7.0),
                   ("DAMAGE", stats["damage"] / 1.3), ("ARMOR", stats["armor"] / 0.10)]
    for i, (label, val) in enumerate(stat_labels):
        yy = 308 + i * 32
        screen.blit(FONT_TINY.render(label, True, STONE_LIGHT), (info.x + 40, yy - 5))
        pygame.draw.rect(screen, (25, 30, 38), (info.x + 125, yy, 285, 12), border_radius=5)
        pygame.draw.rect(screen, GOLD if label in ("DAMAGE", "ARMOR") else CYAN,
                         (info.x + 125, yy, max(6, int(285 * min(1, val))), 12), border_radius=5)
    pygame.draw.line(screen, (50, 55, 65), (info.x + 35, 448), (info.right - 35, 448), 2)

    class_price_text = "FREE" if price == 0 else f"{price:,} COINS"
    center_text(screen, FONT_SMALL, f"CLASS  •  {class_price_text}", (CHAR_BUY_RECT.centerx, 470), GOLD)
    skin_price_text = "FREE" if skin["price"] == 0 else f"{skin['price']:,} COINS"
    center_text(screen, FONT_SMALL, f"SKIN  •  {skin_price_text}", (SKIN_BUY_RECT.centerx, 470),
                GREEN if has_skin else GOLD)

    class_label = "EQUIPPED" if selected_character == name else ("EQUIP" if owned else
                  ("BUY CLASS" if coins >= price else "LOCKED"))
    draw_button(screen, CHAR_BUY_RECT, class_label, CHAR_BUY_RECT.collidepoint(mx, my))
    skin_label = "SKIN ON" if skin_on else ("EQUIP SKIN" if has_skin else
                 ("BUY SKIN" if coins >= skin["price"] else "LOCKED"))
    draw_button(screen, SKIN_BUY_RECT, skin_label, SKIN_BUY_RECT.collidepoint(mx, my))

    status = "EQUIPPED" if selected_character == name else ("OWNED" if owned else "LOCKED")
    center_text(screen, FONT_SMALL, status, (info.centerx, 574),
                CYAN if selected_character == name else (GREEN if owned else GOLD))

    for rect, sym in ((CHAR_LEFT_RECT, "<"), (CHAR_RIGHT_RECT, ">")):
        pygame.draw.rect(screen, (18, 22, 29), rect, border_radius=10)
        pygame.draw.rect(screen, GOLD if rect.collidepoint(mx, my) else STONE_LIGHT, rect, 3, border_radius=10)
        center_text(screen, FONT_BIG, sym, rect.center, WHITE)
    draw_button(screen, CHAR_BACK_RECT, "BACK", CHAR_BACK_RECT.collidepoint(mx, my))
    center_text(screen, FONT_TINY,
                "A / D = CLASS   •   Q / E = SKIN", (676, 630), STONE_LIGHT)
    center_text(screen, FONT_TINY,
                "ENTER = BUY CLASS   •   S = BUY SKIN   •   ESC = BACK", (676, 658), STONE_LIGHT)
    if shop_flash and pygame.time.get_ticks() - shop_flash[1] < 1400:
        center_text(screen, FONT_SMALL, shop_flash[0], (WIDTH // 2, 612),
                    GREEN if "!" in shop_flash[0] else RED)


# =========================================================
# ARMORY  (weapon skins)
# =========================================================
ARM_LEFT_RECT = pygame.Rect(700, 556, 60, 44)
ARM_RIGHT_RECT = pygame.Rect(970, 556, 60, 44)
ARM_BUY_RECT = pygame.Rect(700, 500, 330, 50)
ARM_BACK_RECT = pygame.Rect(45, 618, 200, 48)


def draw_armory_screen():
    global gun_skin_index
    t = pygame.time.get_ticks(); draw_zombie_bg(screen, t)
    center_text(screen, FONT_TITLE, "ARMORY", (WIDTH // 2, 58), GOLD)
    coinbox = pygame.Rect(WIDTH - 220, 25, 185, 55)
    draw_panel(screen, coinbox, (20, 23, 30), GOLD, 2)
    draw_coin_badge(screen, coinbox.x + 28, coinbox.centery)
    center_text(screen, FONT, f"{coins:,}", (coinbox.x + 112, coinbox.centery), WHITE)

    gun_skin_index %= len(GUN_SKINS)
    skin = GUN_SKINS[gun_skin_index]
    key = skin["key"]
    owned = key in owned_gun_skins or skin["price"] == 0
    equipped = equipped_gun_skin == key
    melee = is_melee_class()
    mx, my = pygame.mouse.get_pos()

    # ---------------- preview panel ----------------
    left = pygame.Rect(45, 135, 610, 470)
    draw_panel(screen, left)
    center_text(screen, FONT_SMALL, "WEAPON PREVIEW", (left.centerx, 166), STONE_LIGHT)
    center_text(screen, FONT_NAME, skin["name"], (left.centerx, 206), skin["accent"])

    # big hero weapon: top tier of the current chain
    hero_level = max(1, min(GUN_MAX_LEVEL, gun_level if gun_level else 1))
    art = _gun_art(hero_level, melee, key)
    scale = min(2.6, 440.0 / art.get_width())
    big = pygame.transform.smoothscale(art, (int(art.get_width() * scale), int(art.get_height() * scale)))
    glow = pygame.Surface((big.get_width() + 80, big.get_height() + 80), pygame.SRCALPHA)
    for i in range(9, 0, -1):
        pygame.draw.ellipse(glow, (*skin["accent"], int(9 * (i / 9.0) ** 2)),
                            (40 - i * 4, 40 - i * 3, big.get_width() + i * 8, big.get_height() + i * 6))
    screen.blit(glow, glow.get_rect(center=(left.centerx, 290)))
    screen.blit(big, big.get_rect(center=(left.centerx, 290)))
    tier_name = (BLADE_TIER_NAMES if melee else GUN_TIER_NAMES)[hero_level]
    center_text(screen, FONT_SMALL, f"TIER {hero_level}  •  {tier_name}", (left.centerx, 372), WHITE)

    # the whole evolution chain as thumbnails
    center_text(screen, FONT_TINY, "WEAPON EVOLUTION CHAIN", (left.centerx, 408), STONE_LIGHT)
    for i in range(1, 9):
        cell = pygame.Rect(left.x + 22 + (i - 1) * 71, 428, 64, 78)
        cur = (i == gun_level)
        pygame.draw.rect(screen, (14, 17, 23), cell, border_radius=8)
        pygame.draw.rect(screen, skin["accent"] if cur else (54, 58, 68), cell, 2, border_radius=8)
        thumb = _gun_art(i, melee, key)
        ts = min(56.0 / thumb.get_width(), 40.0 / thumb.get_height())
        th = pygame.transform.smoothscale(thumb, (max(8, int(thumb.get_width() * ts)),
                                                  max(6, int(thumb.get_height() * ts))))
        screen.blit(th, th.get_rect(center=(cell.centerx, cell.y + 30)))
        center_text(screen, FONT_TINY, str(i), (cell.centerx, cell.bottom - 14),
                    GOLD if cur else STONE_LIGHT)
    chain_note = "BLADE TIERS" if melee else "PICK SMG OR RPG AT TIER 3"
    center_text(screen, FONT_TINY, f"EACH TIER = +50% DAMAGE   •   {chain_note}",
                (left.centerx, 528), STONE_LIGHT)
    center_text(screen, FONT_TINY, f"CURRENT RUN WEAPON  •  {gun_name()}", (left.centerx, 566), CYAN)

    # ---------------- skin list ----------------
    right = pygame.Rect(675, 135, 380, 340)
    draw_panel(screen, right)
    center_text(screen, FONT_SMALL, "WEAPON SKINS", (right.centerx, 166), STONE_LIGHT)
    for i, entry in enumerate(GUN_SKINS):
        row = pygame.Rect(right.x + 20, 192 + i * 46, 340, 40)
        sel = (i == gun_skin_index)
        have = entry["key"] in owned_gun_skins or entry["price"] == 0
        pygame.draw.rect(screen, (24, 28, 36) if sel else (16, 19, 25), row, border_radius=8)
        pygame.draw.rect(screen, entry["accent"] if sel else (48, 52, 62), row, 2, border_radius=8)
        chip = pygame.Rect(row.x + 8, row.y + 8, 24, 24)
        pygame.draw.rect(screen, entry["steel"], chip, border_radius=5)
        pygame.draw.rect(screen, entry["accent"], chip, 2, border_radius=5)
        screen.blit(FONT_TINY.render(entry["name"], True, WHITE if have else STONE_LIGHT), (row.x + 42, row.y + 5))
        if equipped_gun_skin == entry["key"]:
            tail, tcol = "EQUIPPED", CYAN
        elif have:
            tail, tcol = "OWNED", GREEN
        else:
            tail, tcol = f"{entry['price']:,}", GOLD
        img = FONT_TINY.render(tail, True, tcol)
        screen.blit(img, (row.right - 12 - img.get_width(), row.y + 5))
        if not have:
            screen.blit(FONT_TINY.render("LOCKED", True, (120, 96, 60)), (row.x + 42, row.y + 21))

    label = "EQUIPPED" if equipped else ("EQUIP SKIN" if owned else
            ("BUY SKIN" if coins >= skin["price"] else "NOT ENOUGH COINS"))
    draw_button(screen, ARM_BUY_RECT, label, ARM_BUY_RECT.collidepoint(mx, my))
    for rect, sym in ((ARM_LEFT_RECT, "<"), (ARM_RIGHT_RECT, ">")):
        pygame.draw.rect(screen, (18, 22, 29), rect, border_radius=9)
        pygame.draw.rect(screen, GOLD if rect.collidepoint(mx, my) else STONE_LIGHT, rect, 2, border_radius=9)
        center_text(screen, FONT, sym, rect.center, WHITE)
    if equipped:
        price_line, price_col = "SKIN EQUIPPED", CYAN
    elif owned:
        price_line, price_col = "SKIN OWNED", GREEN
    else:
        price_line, price_col = ("FREE" if skin["price"] == 0 else f"{skin['price']:,} COINS"), GOLD
    center_text(screen, FONT_SMALL, price_line, (right.centerx, 578), price_col)
    draw_button(screen, ARM_BACK_RECT, "BACK", ARM_BACK_RECT.collidepoint(mx, my))
    center_text(screen, FONT_TINY, "A / D = SKIN   •   ENTER = BUY / EQUIP   •   ESC = BACK",
                (676, 644), STONE_LIGHT)
    if shop_flash and pygame.time.get_ticks() - shop_flash[1] < 1400:
        center_text(screen, FONT_SMALL, shop_flash[0], (WIDTH // 2, 612),
                    GREEN if "!" in shop_flash[0] else RED)


# =========================================================
# LEADERBOARD  (most rounds / most kills)
# =========================================================
LEADERBOARD_MAX_ENTRIES = 400
LEADERBOARD_ROWS = 8

# Shared hitboxes: drawing AND click detection both use these.
LB_TAB_ROUNDS = pygame.Rect(200, 106, 300, 48)
LB_TAB_KILLS = pygame.Rect(600, 106, 300, 48)
LB_PANEL = pygame.Rect(55, 172, 990, 432)
LB_BACK = pygame.Rect(WIDTH // 2 - 115, 622, 230, 50)

MEDALS = ((255, 214, 80), (206, 212, 222), (198, 132, 72))


def load_leaderboard():
    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return [e for e in data if isinstance(e, dict)]
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        pass
    return []


def save_leaderboard(entries):
    try:
        with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
            json.dump(entries[-LEADERBOARD_MAX_ENTRIES:], f, indent=2)
    except OSError:
        pass


def _lb_int(entry, key):
    try:
        return int(entry.get(key, 0))
    except (TypeError, ValueError):
        return 0


def leaderboard_best_runs(metric):
    """Best single run per player, ranked by `metric` ('wave' or 'kills')."""
    best = {}
    for e in load_leaderboard():
        user = str(e.get("username") or "GUEST")
        cur = best.get(user)
        if cur is None or (_lb_int(e, metric), _lb_int(e, "score")) > (_lb_int(cur, metric), _lb_int(cur, "score")):
            best[user] = e
    rows = list(best.values())
    rows.sort(key=lambda e: (_lb_int(e, metric), _lb_int(e, "score"), _lb_int(e, "wave")), reverse=True)
    return rows


def record_run(username, wave_reached, kill_count, run_score, character):
    """Store a finished run and report whether it set a personal best."""
    entries = load_leaderboard()
    user = str(username or "GUEST")
    prev_wave = max([_lb_int(e, "wave") for e in entries if e.get("username") == user] or [0])
    prev_kills = max([_lb_int(e, "kills") for e in entries if e.get("username") == user] or [0])
    entries.append({
        "username": user,
        "wave": int(wave_reached),
        "kills": int(kill_count),
        "score": int(run_score),
        "character": str(character),
        "date": time.strftime("%d %b %Y"),
    })
    save_leaderboard(entries)
    return int(wave_reached) > prev_wave, int(kill_count) > prev_kills


def record_current_run():
    global best_run_flags
    best_run_flags = record_run(current_username, wave, kills, score, selected_character)


def _lb_right(font, text, right_x, y, color):
    img = font.render(text, True, color)
    screen.blit(img, (right_x - img.get_width(), y))


def draw_leaderboard_screen():
    t = pygame.time.get_ticks()
    draw_zombie_bg(screen, t)
    mx, my = pygame.mouse.get_pos()

    center_text(screen, FONT_TITLE, "LEADERBOARD", (WIDTH // 2, 56), GOLD)

    metric = "wave" if leaderboard_tab == 0 else "kills"
    for idx, (rect, label) in enumerate(((LB_TAB_ROUNDS, "MOST ROUNDS"), (LB_TAB_KILLS, "MOST KILLS"))):
        active = (idx == leaderboard_tab)
        fill = (34, 40, 52) if active else (16, 19, 25)
        pygame.draw.rect(screen, fill, rect, border_radius=10)
        pygame.draw.rect(screen, GOLD if active else (rect.collidepoint(mx, my) and STONE_LIGHT or (54, 60, 70)),
                         rect, 3, border_radius=10)
        center_text(screen, FONT_SMALL, label, rect.center, WHITE if active else STONE_LIGHT)
        if active:
            pygame.draw.line(screen, GOLD, (rect.x + 14, rect.bottom - 5), (rect.right - 14, rect.bottom - 5), 3)

    draw_glass_panel(screen, LB_PANEL, GOLD)

    # header
    hy = LB_PANEL.y + 20
    screen.blit(FONT_TINY.render("#", True, STONE_LIGHT), (LB_PANEL.x + 30, hy))
    screen.blit(FONT_TINY.render("PLAYER", True, STONE_LIGHT), (LB_PANEL.x + 90, hy))
    screen.blit(FONT_TINY.render("CHARACTER", True, STONE_LIGHT), (LB_PANEL.x + 330, hy))
    _lb_right(FONT_TINY, "ROUND", LB_PANEL.x + 600, hy, GOLD if metric == "wave" else STONE_LIGHT)
    _lb_right(FONT_TINY, "KILLS", LB_PANEL.x + 712, hy, GOLD if metric == "kills" else STONE_LIGHT)
    _lb_right(FONT_TINY, "SCORE", LB_PANEL.x + 838, hy, STONE_LIGHT)
    _lb_right(FONT_TINY, "DATE", LB_PANEL.x + 962, hy, STONE_LIGHT)
    pygame.draw.line(screen, (52, 58, 68), (LB_PANEL.x + 25, hy + 26), (LB_PANEL.right - 25, hy + 26), 2)

    rows = leaderboard_best_runs(metric)
    if not rows:
        center_text(screen, FONT, "NO RUNS RECORDED YET", (LB_PANEL.centerx, LB_PANEL.centery - 20), STONE_LIGHT)
        center_text(screen, FONT_SMALL, "PLAY A ROUND — YOUR RESULT LANDS HERE AUTOMATICALLY",
                    (LB_PANEL.centerx, LB_PANEL.centery + 20), STONE_LIGHT)
    else:
        for i, entry in enumerate(rows[:LEADERBOARD_ROWS]):
            ry = hy + 46 + i * 45
            row = pygame.Rect(LB_PANEL.x + 20, ry - 6, LB_PANEL.w - 40, 40)
            mine = str(entry.get("username")) == current_username and current_username
            if mine:
                hl = pygame.Surface((row.w, row.h), pygame.SRCALPHA)
                hl.fill((*CYAN, 26))
                screen.blit(hl, row.topleft)
                pygame.draw.rect(screen, CYAN, row, 2, border_radius=6)
            elif i % 2 == 0:
                hl = pygame.Surface((row.w, row.h), pygame.SRCALPHA)
                hl.fill((255, 255, 255, 8))
                screen.blit(hl, row.topleft)

            rank_col = MEDALS[i] if i < 3 else STONE_LIGHT
            if i < 3:
                pygame.draw.circle(screen, rank_col, (LB_PANEL.x + 40, ry + 13), 15)
                pygame.draw.circle(screen, _sh(rank_col, 0.6), (LB_PANEL.x + 40, ry + 13), 15, 2)
                center_text(screen, FONT_SMALL, str(i + 1), (LB_PANEL.x + 40, ry + 13), (20, 18, 14))
            else:
                center_text(screen, FONT_SMALL, str(i + 1), (LB_PANEL.x + 40, ry + 13), rank_col)

            name = str(entry.get("username") or "GUEST")[:14]
            screen.blit(FONT_SMALL.render(name, True, GOLD if i == 0 else WHITE), (LB_PANEL.x + 90, ry + 4))

            char = str(entry.get("character") or "-")
            ccol = CHAR_ACCENT.get(char, STONE_LIGHT)
            pygame.draw.circle(screen, ccol, (LB_PANEL.x + 318, ry + 13), 6)
            screen.blit(FONT_SMALL.render(char.upper()[:12], True, ccol), (LB_PANEL.x + 330, ry + 4))

            _lb_right(FONT_SMALL, str(_lb_int(entry, "wave")), LB_PANEL.x + 600, ry + 4,
                      GOLD if metric == "wave" else WHITE)
            _lb_right(FONT_SMALL, str(_lb_int(entry, "kills")), LB_PANEL.x + 712, ry + 4,
                      GOLD if metric == "kills" else WHITE)
            _lb_right(FONT_SMALL, f"{_lb_int(entry, 'score'):,}", LB_PANEL.x + 838, ry + 4, CYAN)
            _lb_right(FONT_TINY, str(entry.get("date") or ""), LB_PANEL.x + 962, ry + 8, STONE_LIGHT)

        # personal summary for players outside the visible top rows
        if current_username:
            my_rank = next((n for n, e in enumerate(rows, 1) if str(e.get("username")) == current_username), None)
            if my_rank and my_rank > LEADERBOARD_ROWS:
                me = rows[my_rank - 1]
                center_text(screen, FONT_SMALL,
                            f"YOU  •  RANK {my_rank}  •  ROUND {_lb_int(me,'wave')}  •  {_lb_int(me,'kills')} KILLS",
                            (LB_PANEL.centerx, LB_PANEL.bottom - 24), CYAN)

    draw_button(screen, LB_BACK, "BACK", LB_BACK.collidepoint(mx, my))
    center_text(screen, FONT_TINY, "TAB / ← → = SWITCH BOARD   •   ESC = BACK", (WIDTH // 2, 684), STONE_LIGHT)


# Shared main-menu hitboxes (drawing AND click detection use these).
MENU_PANEL = pygame.Rect(330, 200, 440, 404)
MENU_BUTTONS = [
    (pygame.Rect(385, 220, 330, 40), "PLAY"),
    (pygame.Rect(385, 266, 330, 40), "MULTIPLAYER"),
    (pygame.Rect(385, 312, 330, 40), "CLASSES"),
    (pygame.Rect(385, 358, 330, 40), "ARMORY"),
    (pygame.Rect(385, 404, 330, 40), "FRIENDS"),
    (pygame.Rect(385, 450, 330, 40), "LEADERBOARD"),
    (pygame.Rect(385, 496, 330, 40), "MODE"),
    (pygame.Rect(385, 542, 330, 40), "QUIT"),
]


def draw_intro_screen():
    t=pygame.time.get_ticks(); draw_zombie_bg(screen,t)
    pulse=1+0.018*math.sin(t*.005); font=pygame.font.SysFont("arialblack",int(82*pulse),bold=True)
    img=font.render("ZOMBIE SURVIVAL",True,GOLD); sh=font.render("ZOMBIE SURVIVAL",True,(28,16,4)); r=img.get_rect(center=(WIDTH//2,105)); screen.blit(sh,(r.x+6,r.y+7)); screen.blit(img,r)
    center_text(screen,FONT_SMALL,"SURVIVE THE NIGHT  •  SLAY THE HORDE",(WIDTH//2,168),(168,180,172))
    center_text(screen, FONT_TINY, "PRESENTED BY ANTON SAVIN SIBU", (WIDTH // 2, 192), GOLD)
    draw_glass_panel(screen,MENU_PANEL,GOLD)
    center_text(screen,FONT_SMALL,f"CLASS  •  {selected_character.upper()}  ({CLASS_ROLES.get(selected_character,'SURVIVOR')})",(WIDTH//2,220),CYAN)
    mx,my=pygame.mouse.get_pos()
    for rect,label in MENU_BUTTONS:
        show = label
        if label == "MODE":
            show = "MODE: " + ("MOBILE" if control_mode == "mobile" else "LAPTOP")
        draw_button(screen, rect, show, rect.collidepoint(mx, my))
    draw_coin_badge(screen,55,55); screen.blit(FONT.render(f"{coins:,}",True,WHITE),(82,40))
    pygame.draw.polygon(screen, (80, 200, 255), [(55, 95), (67, 88), (79, 95), (67, 108)])
    screen.blit(FONT.render(str(gems), True, CYAN), (82, 88))
    if control_mode == "mobile":
        hint = "MOBILE: STICK MOVE  •  TAP RIGHT TO SHOOT  •  ABILITY BTN  •  AUTO AIM"
    elif is_admin and selected_character == "Reaper":
        hint = "LAPTOP: WASD MOVE  •  HOLD LMB SHOOT  •  Q / E / R POWERS  •  P PAUSE"
    else:
        hint = "LAPTOP: WASD MOVE  •  HOLD LMB SHOOT  •  Q ABILITY  •  P PAUSE"
    center_text(screen, FONT_TINY, hint, (WIDTH // 2, 615), STONE_LIGHT)
    if is_admin: center_text(screen,FONT_TINY,f"{ADMIN_TAG}  {ADMIN_DISPLAY_NAME}  •  F1 PANEL  •  F7 TITLE",(WIDTH//2,645),GOLD)


def draw_pause_screen():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((5, 5, 10, 220))
    screen.blit(overlay, (0, 0))

    title = FONT_HUGE.render("PAUSED", True, GOLD)
    screen.blit(title, (
        WIDTH // 2 - title.get_width() // 2, 145
    ))

    resume_rect = pygame.Rect(WIDTH // 2 - 150, 290, 300, 70)
    quit_rect = pygame.Rect(WIDTH // 2 - 150, 390, 300, 70)
    mx, my = pygame.mouse.get_pos()

    draw_button(screen, resume_rect, "RESUME", resume_rect.collidepoint(mx, my))
    draw_button(screen, quit_rect, "QUIT", quit_rect.collidepoint(mx, my))

    hint = FONT_SMALL.render("PRESS P OR ESC TO RESUME   •   F1 ADMIN (ADMIN ONLY)", True, WHITE)
    screen.blit(hint, (
        WIDTH // 2 - hint.get_width() // 2, 510
    ))


# =========================================================
# CHARACTER POWERS
# =========================================================
def ability_ready(current_time):
    if admin_no_cooldown and is_admin:
        return True
    return current_time >= ability_cooldown


def activate_character_power(current_time):
    global ability_cooldown, ability_duration_until, shadow_clone, turret
    global player_x, player_y, health, rewind_fx_until
    global rewind_active, rewind_path, rewind_index, rewind_next, rewind_target_hp

    if not ability_ready(current_time) or intro_screen or character_screen or armory_screen or paused or game_over:
        return

    # Cooldowns (skipped when admin nocd is on)
    if admin_no_cooldown and is_admin:
        if selected_character == "Engineer" and turret is not None:
            return
        ability_cooldown = 0
    elif selected_character == "Engineer":
        if turret is not None:
            return
        ability_cooldown = current_time + 22000
    elif selected_character == "Time Lord":
        ability_cooldown = current_time + 10000
    elif selected_character == "Magician":
        ability_cooldown = current_time + 8500
    elif selected_character == "Reaper":
        ability_cooldown = current_time + 6000
    else:
        ability_cooldown = current_time + 9000

    # class accent colors for power FX
    _pow_col = {
        "Survivor": (120, 220, 140),
        "Ninja": (100, 220, 255),
        "Engineer": (255, 180, 60),
        "Time Lord": (180, 120, 255),
        "Frozen": (140, 220, 255),
        "Scientist": (120, 255, 80),
        "Magician": (220, 120, 255),
        "Priest": (255, 230, 120),
    }.get(selected_character, (120, 220, 255))
    spawn_power_anim(player_x, player_y, current_time, color=_pow_col, style="ring", size=130, life=650)

    if selected_character == "Survivor":
        if not named_bosses_alive():
            health = min(max_health, health + 35)

    elif selected_character == "Ninja":
        # One stable shadow clone at a time. A fresh Q never creates a second clone.
        # The clone starts beside the player and remains bounded to the map.
        if shadow_clone is None:
            shadow_clone = {
                "x": float(player_x + 42), "y": float(player_y),
                "health": 25, "max_health": 25, "damage": 22,
                "until": current_time + 18000, "hit_timer": current_time,
                "hit_taken_timer": 0,
            }

    elif selected_character == "Engineer":
        # Place the turret at the mouse position. Keep it inside the map.
        mx, my = pygame.mouse.get_pos()
        turret = {
            "x": float(max(55, min(WIDTH - 55, mx))),
            "y": float(max(80, min(HEIGHT - 55, my))),
            "health": 30, "max_health": 30,
            "damage": 24 + wave * 2, "range": 390,
            "hit_timer": current_time, "hit_taken_timer": 0,
            "fire_delay": 320, "rotation": 0.0,
            "splash": 42, "level": 1,
            "shot_flash": 0,
        }

    elif selected_character == "Time Lord":
        # SLOW TIME REWIND — walk backward through ~3s of history, then freeze
        path = []
        if time_history:
            want = current_time - 3000
            snaps = list(time_history)
            if snaps:
                best_i = 0
                best_d = abs(snaps[0][3] - want)
                for i, s in enumerate(snaps):
                    d = abs(s[3] - want)
                    if d < best_d:
                        best_i, best_d = i, d
                # play from newest back to past (visual rewind)
                path = list(reversed(snaps[best_i:]))
                if not path:
                    path = [snaps[best_i]]
        if path:
            rewind_path = path
            rewind_index = 0
            rewind_next = current_time
            rewind_target_hp = float(path[-1][2])
            rewind_active = True
            rewind_fx_until = current_time + 1600
        ability_duration_until = current_time + 4500
        for zombie in zombies:
            zombie["frozen_until"] = ability_duration_until
        explosions.append({"x": player_x, "y": player_y, "radius": 150, "time": current_time, "type": "spirit"})

    elif selected_character == "Frozen":
        # Freeze nearby zombies for 3 seconds.
        ability_duration_until = current_time + 3000
        for zombie in zombies:
            if math.hypot(zombie["x"] - player_x, zombie["y"] - player_y) < 260:
                zombie["frozen_until"] = ability_duration_until

    elif selected_character == "Scientist":
        # Throw a toxic potion vial toward the mouse — shatters into poison smoke.
        mx, my = pygame.mouse.get_pos()
        angle = math.atan2(my - player_y, mx - player_x)
        poison_bombs.append({
            "x": float(player_x), "y": float(player_y),
            "dx": math.cos(angle) * 12.5, "dy": math.sin(angle) * 12.5,
            "radius": 150, "damage": 70,
            "until": current_time + 1600, "blast": False,
            "potion": True, "spin": 0.0,
        })

    elif selected_character == "Magician":
        # Become untouchable/invisible for 5 seconds.
        ability_duration_until = current_time + 6500

    elif selected_character == "Reaper":
        # Fallback if non-admin somehow reaches here — still anime-flavoured.
        for i in range(6):
            katana_slash(i * (math.tau / 6.0), arc=1.05, reach_bonus=80)


ADMIN_POWERS = [
    {"key": "q", "name": "SENKAI TEMPEST", "cd": 5500,
     "desc": "Eight flash-step spirit slashes erupt in a full circle, then a soul shockwave."},
    {"key": "e", "name": "KUROSHIO REND", "cd": 12000,
     "desc": "3-MOVE CHAIN: dash strike → triple crescents → ground rupture."},
    {"key": "r", "name": "BANKAI", "cd": 25000,
     "desc": "Time stops while you flash-step and shred the whole horde."},
    {"key": "f", "name": "WEREWOLF", "cd": 45000,
     "desc": "Transform into a werewolf for 20 seconds. Claws only. New Q/E/R."},
]

WEREWOLF_POWERS = [
    {"key": "q", "name": "BLOOD HOWL", "cd": 4000,
     "desc": "Howl: stun + shred everything nearby with claws."},
    {"key": "e", "name": "LUNAR POUNCE", "cd": 7000,
     "desc": "Leap to cursor, claw tornado on landing."},
    {"key": "r", "name": "PACK RAMPAGE", "cd": 14000,
     "desc": "Frenzy: 5 rapid claw bursts + huge lifesteal."},
    {"key": "f", "name": "WEREWOLF", "cd": 45000,
     "desc": "Already transformed."},
]

STORM_POWERS = [
    {"key": "q", "name": "THUNDER CALL", "cd": 4500,
     "desc": "Ring of lightning strikes around you."},
    {"key": "e", "name": "CHAIN BOLT", "cd": 7000,
     "desc": "Bouncing lightning that chains through the horde."},
    {"key": "r", "name": "TEMPEST DOMAIN", "cd": 22000,
     "desc": "Storm field: slow + continuous lightning for 5s."},
    {"key": "f", "name": "JUDGMENT", "cd": 11000,
     "desc": "3-MOVE: mega-bolt → shockwave → sky spears."},
]

EXECUTOR_POWERS = [
    {"key": "q", "name": "ERASURE", "cd": 4000,
     "desc": "Delete nearby zombies with void pulses."},
    {"key": "e", "name": "JUDGMENT RAY", "cd": 6500,
     "desc": "Fire a piercing annihilation beam."},
    {"key": "r", "name": "OMEGA BURST", "cd": 16000,
     "desc": "Screen-wide execution wave + huge heal."},
    {"key": "f", "name": "OVERLORD FORM", "cd": 40000,
     "desc": "Transform 25s: massive damage, armor, speed."},
]


def admin_power_ready(key, current_time):
    if admin_no_cooldown and is_admin:
        return True
    return current_time >= admin_power_cd.get(key, 0)


def use_storm_power(key, current_time):
    # cast anim injected after ready check below

    """Storm Sovereign kit — ranged lightning admin (not melee)."""
    global health, player_x, player_y, storm_domain_until
    if selected_character != "Storm Sovereign":
        return
    if intro_screen or character_screen or armory_screen or paused or game_over or upgrade_screen:
        return
    if not admin_power_ready(key, current_time):
        return
    cds = {"q": 4500, "e": 7000, "r": 22000, "f": 11000}
    if admin_no_cooldown:
        admin_power_cd[key] = 0
    else:
        admin_power_cd[key] = current_time + cds.get(key, 8000)

    mx, my = pygame.mouse.get_pos()
    angle = math.atan2(my - player_y, mx - player_x)
    wave_scale = 1.0 + min(2.5, wave * 0.04)

    spawn_power_anim(player_x, player_y, current_time, color=(100, 200, 255), style="ring", size=150, life=700)
    if key == "q":
        # THUNDER CALL — ring of vertical lightning strikes
        for i in range(10):
            a = i * (math.tau / 10.0)
            tx = player_x + math.cos(a) * 150
            ty = player_y + math.sin(a) * 150
            storm_bolts.append({
                "x0": tx, "y0": ty - 90, "x1": tx, "y1": ty + 20,
                "time": current_time, "life": 280, "damage": damage * 2.2 * wave_scale,
                "radius": 42, "kind": "strike",
            })
            explosions.append({"x": tx, "y": ty, "radius": 50, "time": current_time, "type": "spirit"})
        for z in zombies[:]:
            if math.hypot(z["x"] - player_x, z["y"] - player_y) < 180 + z["radius"]:
                z["health"] -= damage * 1.8 * wave_scale
                z["hit_flash_until"] = current_time + 120
                z["frozen_until"] = max(z.get("frozen_until", 0), current_time + 500)
                if z["health"] <= 0:
                    kill_zombie(z)
        trigger_hit_effect(current_time, 7)

    elif key == "e":
        # CHAIN BOLT — bouncing lightning toward cursor, chains between zombies
        storm_bolts.append({
            "x": float(player_x), "y": float(player_y),
            "dx": math.cos(angle) * 22, "dy": math.sin(angle) * 22,
            "time": current_time, "life": 900, "damage": damage * 2.6 * wave_scale,
            "radius": 28, "kind": "chain", "hit": set(), "bounces": 6,
        })
        # side forks
        for spread in (-0.35, 0.35):
            a = angle + spread
            storm_bolts.append({
                "x": float(player_x), "y": float(player_y),
                "dx": math.cos(a) * 18, "dy": math.sin(a) * 18,
                "time": current_time, "life": 700, "damage": damage * 1.8 * wave_scale,
                "radius": 22, "kind": "chain", "hit": set(), "bounces": 3,
            })
        trigger_hit_effect(current_time, 6)

    elif key == "r":
        # TEMPEST DOMAIN — long storm field, slow + constant damage
        storm_domain_until = current_time + 5000
        for z in zombies:
            z["frozen_until"] = max(z.get("frozen_until", 0), current_time + 1200)
        for i in range(16):
            a = i * (math.tau / 16.0)
            tx = player_x + math.cos(a) * 200
            ty = player_y + math.sin(a) * 200
            storm_bolts.append({
                "x0": player_x, "y0": player_y, "x1": tx, "y1": ty,
                "time": current_time, "life": 600, "damage": damage * 1.4 * wave_scale,
                "radius": 30, "kind": "strike",
            })
        explosions.append({"x": player_x, "y": player_y, "radius": 280, "time": current_time, "type": "spirit"})
        trigger_hit_effect(current_time, 9)

    elif key == "f":
        # JUDGMENT — 3-move chain: aimed mega-bolt, shockwave, sky spears
        # 1) mega bolt
        storm_bolts.append({
            "x": float(player_x), "y": float(player_y),
            "dx": math.cos(angle) * 26, "dy": math.sin(angle) * 26,
            "time": current_time, "life": 1000, "damage": damage * 4.0 * wave_scale,
            "radius": 40, "kind": "chain", "hit": set(), "bounces": 2,
        })
        # 2) shockwave around player
        for z in zombies[:]:
            d = math.hypot(z["x"] - player_x, z["y"] - player_y)
            if d < 220 + z["radius"]:
                z["health"] -= damage * 2.5 * wave_scale * max(0.4, 1 - d / 240)
                z["hit_flash_until"] = current_time + 140
                if z["health"] <= 0:
                    kill_zombie(z)
        explosions.append({"x": player_x, "y": player_y, "radius": 230, "time": current_time, "type": "spirit"})
        # 3) sky spears on densest cluster / toward cursor
        for i in range(7):
            ox = player_x + math.cos(angle) * (60 + i * 40) + random.uniform(-30, 30)
            oy = player_y + math.sin(angle) * (60 + i * 40) + random.uniform(-30, 30)
            storm_bolts.append({
                "x0": ox, "y0": oy - 110, "x1": ox, "y1": oy + 30,
                "time": current_time + i * 40, "life": 320, "damage": damage * 2.0 * wave_scale,
                "radius": 36, "kind": "strike",
            })
        trigger_hit_effect(current_time, 8)



def end_executor_form():
    """Restore combat stats after Overlord Form ends. Speed was never permanently changed."""
    global executor_until, executor_bonus, damage, damage_reduction, shoot_delay
    if not executor_bonus:
        executor_until = 0
        return
    damage = executor_bonus.get("damage", damage)
    damage_reduction = executor_bonus.get("armor", damage_reduction)
    shoot_delay = executor_bonus.get("delay", shoot_delay)
    executor_bonus = {}
    executor_until = 0
    explosions.append({
        "x": player_x, "y": player_y, "radius": 120,
        "time": pygame.time.get_ticks(), "type": "spirit",
    })


def draw_executor_form(surface, x, y):
    """Overlord transformation visual — golden-crimson armor + void crown."""
    t = pygame.time.get_ticks()
    bob = int(math.sin(t * 0.012) * 3)
    pulse = 0.5 + 0.5 * math.sin(t * 0.03)
    accent = (255, 60, 40)
    gold = (255, 210, 60)
    suit = (40, 12, 12)
    suit_l = (90, 30, 30)
    # aura
    for rad, a in ((90, 40), (75, 55), (60, 70)):
        ring = pygame.Surface((rad * 2 + 12, rad * 2 + 12), pygame.SRCALPHA)
        pygame.draw.circle(ring, (*accent, int(a * pulse)), (rad + 6, rad + 6), rad, 3)
        surface.blit(ring, ring.get_rect(center=(x, y)))
    for i in range(12):
        ang = t * 0.004 + i * (math.tau / 12)
        px = int(x + math.cos(ang) * (55 + 10 * math.sin(t * 0.01 + i)))
        py = int(y + math.sin(ang) * 30 - 6)
        pygame.draw.circle(surface, gold if i % 2 == 0 else accent, (px, py), 2 + (i % 2))
    # body
    pygame.draw.ellipse(surface, (0, 0, 0), (x - 40, y + 28, 80, 22))
    body = pygame.Rect(x - 22, y - 8 + bob, 44, 44)
    pygame.draw.rect(surface, (8, 4, 4), body.inflate(8, 8), border_radius=8)
    pygame.draw.rect(surface, suit, body, border_radius=6)
    pygame.draw.rect(surface, suit_l, (x - 14, y + 8 + bob, 28, 16), border_radius=3)
    pygame.draw.circle(surface, gold, (x, y + 10 + bob), 6)
    pygame.draw.circle(surface, accent, (x, y + 10 + bob), 3)
    # head
    head = pygame.Rect(x - 16, y - 36 + bob, 32, 30)
    pygame.draw.rect(surface, (8, 4, 4), head.inflate(4, 4), border_radius=4)
    pygame.draw.rect(surface, (245, 220, 200), head, border_radius=3)
    # crown
    pygame.draw.polygon(surface, gold, [
        (x - 18, y - 34 + bob), (x - 12, y - 52 + bob), (x - 4, y - 38 + bob),
        (x, y - 56 + bob), (x + 4, y - 38 + bob), (x + 12, y - 52 + bob), (x + 18, y - 34 + bob)])
    pygame.draw.circle(surface, accent, (x, y - 50 + bob), 4)
    # eyes
    pygame.draw.rect(surface, accent, (x - 10, y - 26 + bob, 7, 5))
    pygame.draw.rect(surface, accent, (x + 3, y - 26 + bob, 7, 5))
    # arms toward mouse
    mx, my = pygame.mouse.get_pos()
    ang = math.atan2(my - y, mx - x)
    for side in (-1, 1):
        hx = x + int(math.cos(ang) * 30 + side * math.cos(ang + 1.57) * 12)
        hy = y + int(math.sin(ang) * 30 + side * math.sin(ang + 1.57) * 12) + bob
        pygame.draw.line(surface, suit, (x, y + bob), (hx, hy), 10)
        pygame.draw.circle(surface, gold, (hx, hy), 8)
        pygame.draw.circle(surface, accent, (hx, hy), 4)
    # timer
    left = max(0, executor_until - t)
    frac = left / 25000.0
    pygame.draw.circle(surface, accent, (x, y - 72), 14, 2)
    if frac > 0:
        pygame.draw.arc(surface, gold, (x - 14, y - 86, 28, 28), -1.57, -1.57 + math.tau * frac, 4)
    lab = FONT_TINY.render("OVERLORD", True, gold)
    surface.blit(lab, (x - lab.get_width() // 2, y - 96))


def use_executor_power(key, current_time):
    """Executor kit — OP erasure arts + Overlord transformation."""
    global health, player_x, player_y, executor_until, executor_bonus
    global player_speed, damage, damage_reduction, shoot_delay
    if selected_character != "Executor":
        return
    if intro_screen or character_screen or armory_screen or paused or game_over or upgrade_screen:
        return
    if not admin_power_ready(key, current_time):
        return
    # while transformed, F is ignored
    if key == "f" and executor_until and current_time < executor_until:
        return
    power = next((p for p in EXECUTOR_POWERS if p["key"] == key), None)
    if not power:
        return
    if admin_no_cooldown and is_admin:
        admin_power_cd[key] = 0
    else:
        admin_power_cd[key] = current_time + power["cd"]

    mx, my = pygame.mouse.get_pos()
    angle = math.atan2(my - player_y, mx - player_x)
    form_mult = 2.5 if (executor_until and current_time < executor_until) else 1.0

    if key == "q":
        # ERASURE — void pulses around player
        for i in range(14):
            a = i * (math.tau / 14)
            explosions.append({
                "x": player_x + math.cos(a) * 90, "y": player_y + math.sin(a) * 90,
                "radius": 55, "time": current_time, "type": "spirit",
            })
        for z in zombies[:]:
            d = math.hypot(z["x"] - player_x, z["y"] - player_y)
            if d < 220 + z["radius"]:
                z["health"] -= damage * 4.0 * form_mult
                z["hit_flash_until"] = current_time + 120
                if z["health"] <= 0:
                    kill_zombie(z)
        health = min(max_health, health + 15)
        trigger_hit_effect(current_time, 7)
        return

    if key == "e":
        # JUDGMENT RAY — long piercing beam toward cursor
        for step in range(18):
            px = player_x + math.cos(angle) * (30 + step * 28)
            py = player_y + math.sin(angle) * (30 + step * 28)
            explosions.append({"x": px, "y": py, "radius": 28, "time": current_time, "type": "spirit"})
            for z in zombies[:]:
                if math.hypot(z["x"] - px, z["y"] - py) < z["radius"] + 30:
                    z["health"] -= damage * 3.2 * form_mult
                    z["hit_flash_until"] = current_time + 100
                    if z["health"] <= 0:
                        kill_zombie(z)
        trigger_hit_effect(current_time, 6)
        return

    if key == "r":
        # OMEGA BURST — full-field execution wave
        explosions.append({"x": player_x, "y": player_y, "radius": 400, "time": current_time, "type": "spirit"})
        explosions.append({"x": player_x, "y": player_y, "radius": 220, "time": current_time, "type": "spirit"})
        for z in zombies[:]:
            z["health"] -= damage * 6.0 * form_mult
            z["hit_flash_until"] = current_time + 160
            z["frozen_until"] = max(z.get("frozen_until", 0), current_time + 600)
            if z["health"] <= 0:
                kill_zombie(z)
        health = min(max_health, health + 60)
        trigger_hit_effect(current_time, 10)
        return

    if key == "f":
        # OVERLORD FORM — 25s transformation
        if current_time < executor_until:
            return
        executor_bonus = {
            "speed": player_speed,  # base speed kept; boost only while form is active
            "damage": damage,
            "armor": damage_reduction,
            "delay": shoot_delay,
        }
        executor_until = current_time + 25000
        # SPEED: applied only in movement while transformed (not permanent)
        damage = int(executor_bonus["damage"] * 3.5)
        damage_reduction = min(0.85, executor_bonus["armor"] + 0.30)
        shoot_delay = max(55, int(executor_bonus["delay"] * 0.35))
        health = min(max_health, health + 100)
        explosions.append({"x": player_x, "y": player_y, "radius": 300, "time": current_time, "type": "spirit"})
        for z in zombies[:]:
            if math.hypot(z["x"] - player_x, z["y"] - player_y) < 240 + z["radius"]:
                z["health"] -= damage * 2.5
                z["hit_flash_until"] = current_time + 140
                if z["health"] <= 0:
                    kill_zombie(z)
        trigger_hit_effect(current_time, 10)
        return


def use_admin_power(key, current_time):
    """Reaper arts / Storm / Executor overlord kit."""
    global bankai_until, bankai_next, health, player_x, player_y
    global werewolf_until, werewolf_bonus, player_speed, damage, damage_reduction, shoot_delay
    global executor_until, executor_bonus
    if selected_character == "Storm Sovereign":
        use_storm_power(key, current_time)
        return
    if selected_character == "Executor":
        use_executor_power(key, current_time)
        return
    if selected_character != "Reaper":
        return
    if intro_screen or character_screen or armory_screen or paused or game_over or upgrade_screen:
        return
    if not admin_power_ready(key, current_time):
        return

    # ---- WEREWOLF form powers (no katana) ----
    if werewolf_until and current_time < werewolf_until and key in ("q", "e", "r"):
        power = next(p for p in WEREWOLF_POWERS if p["key"] == key)
        if admin_no_cooldown:
            admin_power_cd[key] = 0
        else:
            admin_power_cd[key] = current_time + power["cd"]

        spawn_power_anim(player_x, player_y, current_time, color=(255, 80, 40), style="burst", size=150, life=700)
        if key == "q":
            # BLOOD HOWL — stun ring + claw shred
            for i in range(12):
                claw_slash(i * (math.tau / 12.0), arc=1.2, reach_bonus=70, heavy=True)
            for z in zombies[:]:
                d = math.hypot(z["x"] - player_x, z["y"] - player_y)
                if d < 240 + z["radius"]:
                    z["health"] -= damage * 2.4
                    z["hit_flash_until"] = current_time + 160
                    z["frozen_until"] = max(z.get("frozen_until", 0), current_time + 1400)
                    if z["health"] <= 0:
                        kill_zombie(z)
            health = min(max_health, health + 25)
            explosions.append({"x": player_x, "y": player_y, "radius": 260, "time": current_time, "type": "spirit"})
            trigger_hit_effect(current_time, 9)
            return

        if key == "e":
            # LUNAR POUNCE — leap to cursor + claw tornado
            mx, my = pygame.mouse.get_pos()
            angle = math.atan2(my - player_y, mx - player_x)
            dist = min(280, math.hypot(mx - player_x, my - player_y))
            nx = max(30, min(WIDTH - 30, player_x + math.cos(angle) * dist))
            ny = max(40, min(HEIGHT - 35, player_y + math.sin(angle) * dist))
            for step in range(8):
                t = step / 7.0
                px = player_x + (nx - player_x) * t
                py = player_y + (ny - player_y) * t
                explosions.append({"x": px, "y": py, "radius": 40, "time": current_time, "type": "spirit"})
                for z in zombies[:]:
                    if math.hypot(z["x"] - px, z["y"] - py) < z["radius"] + 36:
                        z["health"] -= damage * 1.8
                        z["hit_flash_until"] = current_time + 100
                        if z["health"] <= 0:
                            kill_zombie(z)
            player_x, player_y = nx, ny
            for i in range(10):
                claw_slash(i * (math.tau / 10.0), arc=1.3, reach_bonus=90, heavy=True)
            health = min(max_health, health + 20)
            explosions.append({"x": player_x, "y": player_y, "radius": 200, "time": current_time, "type": "spirit"})
            trigger_hit_effect(current_time, 8)
            return

        if key == "r":
            # PACK RAMPAGE — 5 rapid claw bursts
            for burst in range(5):
                for i in range(8):
                    claw_slash(i * (math.tau / 8.0) + burst * 0.2, arc=1.35, reach_bonus=100, heavy=True)
            for z in zombies[:]:
                d = math.hypot(z["x"] - player_x, z["y"] - player_y)
                if d < 300 + z["radius"]:
                    z["health"] -= damage * 3.5
                    z["hit_flash_until"] = current_time + 180
                    if z["health"] <= 0:
                        kill_zombie(z)
            health = min(max_health, health + 50)
            explosions.append({"x": player_x, "y": player_y, "radius": 320, "time": current_time, "type": "spirit"})
            explosions.append({"x": player_x, "y": player_y, "radius": 160, "time": current_time, "type": "spirit"})
            trigger_hit_effect(current_time, 10)
            return

    # F during werewolf: ignore (already transformed)
    if key == "f" and werewolf_until and current_time < werewolf_until:
        return

    power = next((p for p in ADMIN_POWERS if p["key"] == key), None)
    if power is None:
        return
    if admin_no_cooldown:
        admin_power_cd[key] = 0
    else:
        admin_power_cd[key] = current_time + power["cd"]

    spawn_power_anim(player_x, player_y, current_time, color=(180, 40, 255), style="burst", size=150, life=700)
    if key == "q":
        # SENKAI TEMPEST — dense ring of spirit blade sweeps + delayed second wave
        for i in range(8):
            katana_slash(i * (math.tau / 8.0), arc=0.95, reach_bonus=95)
        # inner tight ring for anime density
        for i in range(4):
            katana_slash(i * (math.tau / 4.0) + 0.4, arc=1.15, reach_bonus=55)
        # soul shockwave: damage + light heal from harvest
        harvested = 0
        for zombie in zombies[:]:
            d = math.hypot(zombie["x"] - player_x, zombie["y"] - player_y)
            if d < 210 + zombie["radius"]:
                zombie["health"] -= damage * 1.8
                zombie["hit_flash_until"] = current_time + 140
                zombie["frozen_until"] = max(zombie.get("frozen_until", 0), current_time + 900)
                harvested += 1
                if zombie["health"] <= 0:
                    kill_zombie(zombie)
        if harvested and not named_bosses_alive():
            health = min(max_health, health + min(40, harvested * 4))
        explosions.append({
            "x": player_x, "y": player_y, "radius": 200,
            "time": current_time, "type": "spirit",
        })
        trigger_hit_effect(current_time, 8)

    elif key == "e":
        # KUROSHIO REND — 3-move combo (moved from F)
        mx, my = pygame.mouse.get_pos()
        angle = math.atan2(my - player_y, mx - player_x)

        # MOVE 1: flash-step dash toward cursor + heavy slash
        dash = 140
        nx = max(30, min(WIDTH - 30, player_x + math.cos(angle) * dash))
        ny = max(40, min(HEIGHT - 35, player_y + math.sin(angle) * dash))
        for step in range(6):
            t = step / 5.0
            px = player_x + (nx - player_x) * t
            py = player_y + (ny - player_y) * t
            explosions.append({"x": px, "y": py, "radius": 36, "time": current_time, "type": "spirit"})
            for z in zombies[:]:
                if math.hypot(z["x"] - px, z["y"] - py) < z["radius"] + 28:
                    z["health"] -= damage * 1.6
                    z["hit_flash_until"] = current_time + 100
                    if z["health"] <= 0:
                        kill_zombie(z)
        player_x, player_y = nx, ny
        katana_slash(angle, arc=1.1, reach_bonus=70)

        # MOVE 2: triple piercing crescents
        for spread, spd, rad, mul in (
            (-0.28, 17.0, 70.0, 2.4),
            (0.0, 19.0, 88.0, 3.0),
            (0.28, 17.0, 70.0, 2.4),
        ):
            a = angle + spread
            moon_waves.append({
                "x": float(player_x), "y": float(player_y),
                "dx": math.cos(a) * spd, "dy": math.sin(a) * spd,
                "angle": a, "damage": damage * mul, "radius": rad,
                "time": current_time, "until": current_time + 1600, "hit": set(),
                "anime": True,
            })

        # MOVE 3: ground rupture
        for z in zombies[:]:
            d = math.hypot(z["x"] - player_x, z["y"] - player_y)
            if d < 260 + z["radius"]:
                falloff = max(0.4, 1.0 - d / 280.0)
                z["health"] -= damage * 2.8 * falloff
                z["hit_flash_until"] = current_time + 140
                z["frozen_until"] = max(z.get("frozen_until", 0), current_time + 700)
                if z["health"] <= 0:
                    kill_zombie(z)
        explosions.append({"x": player_x, "y": player_y, "radius": 250, "time": current_time, "type": "spirit"})
        explosions.append({"x": player_x, "y": player_y, "radius": 120, "time": current_time, "type": "spirit"})
        trigger_hit_effect(current_time, 8)

    elif key == "r":
        bankai_until = current_time + 4200
        bankai_next = current_time
        for z in zombies:
            z["frozen_until"] = max(z.get("frozen_until", 0), bankai_until)
        trigger_hit_effect(current_time, 9)

    elif key == "f":
        # WEREWOLF TRANSFORMATION        global werewolf_until, werewolf_bonus, player_speed, damage, damage_reduction, shoot_delay
        if current_time < werewolf_until:
            return  # already transformed
        # store base stats once
        werewolf_bonus = {
            "speed": player_speed,  # base speed kept; boost only while form is active
            "damage": damage,
            "armor": damage_reduction,
            "delay": shoot_delay,
        }
        werewolf_until = current_time + 20000  # 20 seconds
        # SPEED: applied only in movement while transformed (not permanent)
        damage = int(werewolf_bonus["damage"] * 2.4)
        damage_reduction = min(0.82, werewolf_bonus["armor"] + 0.28)
        shoot_delay = max(70, int(werewolf_bonus["delay"] * 0.40))
        health = min(max_health, health + 80)
        # transform shockwave + claw ring
        explosions.append({"x": player_x, "y": player_y, "radius": 280, "time": current_time, "type": "spirit"})
        explosions.append({"x": player_x, "y": player_y, "radius": 140, "time": current_time, "type": "spirit"})
        for i in range(10):
            claw_slash(i * (math.tau / 10.0), arc=1.3, reach_bonus=80, heavy=True)
        for z in zombies[:]:
            if math.hypot(z["x"] - player_x, z["y"] - player_y) < 200 + z["radius"]:
                z["health"] -= damage * 2.0
                z["hit_flash_until"] = current_time + 140
                z["frozen_until"] = max(z.get("frozen_until", 0), current_time + 800)
                if z["health"] <= 0:
                    kill_zombie(z)
        trigger_hit_effect(current_time, 10)



def end_werewolf_form():
    """Restore combat stats after werewolf ends. Speed was never permanently changed."""
    global werewolf_until, werewolf_bonus, damage, damage_reduction, shoot_delay
    if not werewolf_bonus:
        werewolf_until = 0
        return
    damage = werewolf_bonus.get("damage", damage)
    damage_reduction = werewolf_bonus.get("armor", damage_reduction)
    shoot_delay = werewolf_bonus.get("delay", shoot_delay)
    werewolf_bonus = {}
    werewolf_until = 0
    explosions.append({
        "x": player_x, "y": player_y, "radius": 100,
        "time": pygame.time.get_ticks(), "type": "spirit",
    })


def update_admin_powers(current_time):
    """Move moon-fang waves and drive the bankai flash-step barrage."""
    global player_x, player_y, bankai_until, bankai_next, werewolf_until
    if werewolf_until and current_time >= werewolf_until:
        end_werewolf_form()
    if executor_until and current_time >= executor_until:
        end_executor_form()

    # ---- GETSUGA / MOON FANG: piercing anime crescents ----
    for wave in moon_waves[:]:
        # delayed afterimage waves wait before moving
        if wave.get("delay") and current_time < wave["delay"]:
            continue
        wave["x"] += wave["dx"]
        wave["y"] += wave["dy"]
        if current_time >= wave["until"] or not (-160 < wave["x"] < WIDTH + 160) \
                or not (-160 < wave["y"] < HEIGHT + 160):
            moon_waves.remove(wave)
            continue
        if wave.get("enemy"):
            if math.hypot(wave["x"] - player_x, wave["y"] - player_y) < wave["radius"] + 20:
                if id(wave) not in wave["hit"]:
                    wave["hit"].add(id(wave))
                    damage_player(wave.get("enemy_dmg", 18), current_time)
            continue
        for zombie in zombies[:]:
            if id(zombie) in wave["hit"]:
                continue
            if math.hypot(zombie["x"] - wave["x"], zombie["y"] - wave["y"]) > wave["radius"] + zombie["radius"]:
                continue
            wave["hit"].add(id(zombie))
            zombie["health"] -= wave["damage"]
            zombie["hit_flash_until"] = current_time + 130
            # anime chain: light freeze + splash on spirit crescents
            if wave.get("anime"):
                zombie["frozen_until"] = max(zombie.get("frozen_until", 0), current_time + 700)
                for other in zombies[:]:
                    if other is zombie or id(other) in wave["hit"]:
                        continue
                    if math.hypot(other["x"] - zombie["x"], other["y"] - zombie["y"]) < 55:
                        other["health"] -= wave["damage"] * 0.35
                        other["hit_flash_until"] = current_time + 90
                        wave["hit"].add(id(other))
                        if other["health"] <= 0:
                            kill_zombie(other)
            if zombie["health"] <= 0:
                kill_zombie(zombie)
        trigger_hit_effect(current_time, 1)

    # ---- BANKAI: frozen time + automatic flash-step slashes ----
    if current_time < bankai_until:
        for z in zombies:
            z["frozen_until"] = max(z.get("frozen_until", 0), bankai_until)
        if zombies and current_time >= bankai_next:
            bankai_next = current_time + 110
            target = min(zombies, key=lambda z: math.hypot(z["x"] - player_x, z["y"] - player_y))
            angle = math.atan2(target["y"] - player_y, target["x"] - player_x)
            stand = target["radius"] + 30
            player_x = max(30, min(WIDTH - 30, target["x"] - math.cos(angle) * stand))
            player_y = max(30, min(HEIGHT - 30, target["y"] - math.sin(angle) * stand))
            saved = damage
            try:
                globals()["damage"] = saved * 2.0
                katana_slash(angle, arc=1.15, reach_bonus=45)
                # secondary afterimage cut
                katana_slash(angle + 0.55, arc=0.7, reach_bonus=20)
            finally:
                globals()["damage"] = saved
    elif bankai_until:
        bankai_until = 0


def draw_moon_waves(surface, current_time):
    """Anime crescent projectile: filled fang of energy with speed lines and sparks."""
    acc = _cmix(gun_palette()["accent"], (255, 255, 255), 0.35)
    for wave in moon_waves:
        if wave.get("delay") and current_time < wave["delay"]:
            continue
        r = wave["radius"]
        anime = wave.get("anime", False)
        grow = min(1.0, (current_time - wave["time"]) / (90.0 if anime else 110.0) + (0.55 if anime else 0.45))
        R = r * grow * (1.12 if anime else 1.0)
        size = int(R * 2 + 80)
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        cc = size // 2
        a = wave["angle"]

        def crescent(outer, inner, spread, col, alpha):
            pts = []
            N = 20
            for i in range(N + 1):
                t = -spread + 2 * spread * i / N
                pts.append((cc + math.cos(a + t) * outer, cc + math.sin(a + t) * outer))
            for i in range(N + 1):
                t = spread - 2 * spread * i / N
                taper = 1.0 - 0.45 * abs(t / spread) ** 2
                rr = inner + (outer - inner) * (1.0 - taper)
                pts.append((cc + math.cos(a + t) * rr, cc + math.sin(a + t) * rr))
            pygame.draw.polygon(s, (*col, alpha), pts)

        crescent(R, R * 0.52, 1.16, _cmix(acc, (0, 0, 0), 0.25), 170)
        crescent(R * 0.97, R * 0.62, 1.02, acc, 235)
        crescent(R * 0.93, R * 0.74, 0.86, (255, 255, 255), 250)
        # sharp fang tips
        for sgn in (-1, 1):
            t = sgn * 1.24
            pygame.draw.polygon(s, (*acc, 220), [
                (cc + math.cos(a + t) * R * 1.06, cc + math.sin(a + t) * R * 1.06),
                (cc + math.cos(a + t * 0.86) * R, cc + math.sin(a + t * 0.86) * R),
                (cc + math.cos(a + t * 0.9) * R * 0.66, cc + math.sin(a + t * 0.9) * R * 0.66)])
        # trailing speed lines behind the fang
        for i in range(6):
            off = (i - 2.5) * 0.3 * R
            bx = cc + math.cos(a + math.pi / 2) * off
            by = cc + math.sin(a + math.pi / 2) * off
            ln = 30 + (i % 3) * 22
            pygame.draw.line(s, (*acc, 120),
                             (bx - math.cos(a) * R * 0.15, by - math.sin(a) * R * 0.15),
                             (bx - math.cos(a) * (R * 0.15 + ln), by - math.sin(a) * (R * 0.15 + ln)), 3)
        glow = pygame.Surface((size, size), pygame.SRCALPHA)
        for i in range(9, 0, -1):
            pygame.draw.circle(glow, _sh(acc, 0.10 * (i / 9.0) ** 2), (cc, cc), int(R * 0.5 + i * 6))
        s.blit(glow, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        surface.blit(s, s.get_rect(center=(int(wave["x"]), int(wave["y"]))))


def draw_bankai_overlay(surface, current_time):
    """Dark vignette + vertical speed lines while bankai is active."""
    if current_time >= bankai_until:
        return
    left = bankai_until - current_time
    ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    ov.fill((10, 6, 22, 90))
    acc = _cmix(gun_palette()["accent"], (255, 255, 255), 0.4)
    for i in range(34):
        x = (i * 37 + (current_time // 6) % 37) % WIDTH
        h = 90 + (i * 53) % 260
        y = (i * 91 + (current_time // 3)) % HEIGHT
        pygame.draw.line(ov, (*acc, 46), (x, y), (x, y + h), 2)
    surface.blit(ov, (0, 0))
    if left > 3300 or left < 260:
        fl = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        fl.fill((*acc, 70))
        surface.blit(fl, (0, 0))
    label = FONT_BIG.render("BANKAI", True, acc)
    surface.blit(label, label.get_rect(center=(WIDTH // 2, 78)))





def update_storm_powers(current_time):
    """Move/chain lightning bolts and apply Tempest Domain ticks."""
    global storm_domain_until, health
    # Domain aura tick
    if current_time < storm_domain_until:
        if random.random() < 0.25:
            for z in zombies[:]:
                d = math.hypot(z["x"] - player_x, z["y"] - player_y)
                if d < 260 + z["radius"]:
                    z["health"] -= max(4, damage * 0.15)
                    z["hit_flash_until"] = current_time + 60
                    if z["health"] <= 0:
                        kill_zombie(z)
            if random.random() < 0.4:
                a = random.random() * math.tau
                tx = player_x + math.cos(a) * random.uniform(40, 240)
                ty = player_y + math.sin(a) * random.uniform(40, 240)
                storm_bolts.append({
                    "x0": tx, "y0": ty - 70, "x1": tx, "y1": ty + 15,
                    "time": current_time, "life": 200, "damage": damage * 0.9,
                    "radius": 28, "kind": "strike",
                })

    for bolt in storm_bolts[:]:
        age = current_time - bolt["time"]
        if age > bolt["life"]:
            if bolt in storm_bolts:
                storm_bolts.remove(bolt)
            continue
        if bolt["kind"] == "strike":
            if age > 40 and not bolt.get("hit_done"):
                bolt["hit_done"] = True
                cx = (bolt["x0"] + bolt["x1"]) * 0.5
                cy = (bolt["y0"] + bolt["y1"]) * 0.5
                for z in zombies[:]:
                    if math.hypot(z["x"] - cx, z["y"] - cy) < bolt["radius"] + z["radius"]:
                        z["health"] -= bolt["damage"]
                        z["hit_flash_until"] = current_time + 90
                        if z["health"] <= 0:
                            kill_zombie(z)
        elif bolt["kind"] == "chain":
            bolt["x"] += bolt["dx"]
            bolt["y"] += bolt["dy"]
            if not (-80 < bolt["x"] < WIDTH + 80 and -80 < bolt["y"] < HEIGHT + 80):
                if bolt in storm_bolts:
                    storm_bolts.remove(bolt)
                continue
            for z in zombies[:]:
                if id(z) in bolt["hit"]:
                    continue
                if math.hypot(z["x"] - bolt["x"], z["y"] - bolt["y"]) < bolt["radius"] + z["radius"]:
                    bolt["hit"].add(id(z))
                    z["health"] -= bolt["damage"]
                    z["hit_flash_until"] = current_time + 100
                    z["frozen_until"] = max(z.get("frozen_until", 0), current_time + 400)
                    if z["health"] <= 0:
                        kill_zombie(z)
                    # bounce to next nearest
                    bounces = bolt.get("bounces", 0)
                    if bounces > 0:
                        bolt["bounces"] = bounces - 1
                        others = [o for o in zombies if id(o) not in bolt["hit"]]
                        if others:
                            nxt = min(others, key=lambda o: math.hypot(o["x"] - bolt["x"], o["y"] - bolt["y"]))
                            ang = math.atan2(nxt["y"] - bolt["y"], nxt["x"] - bolt["x"])
                            spd = math.hypot(bolt["dx"], bolt["dy"])
                            bolt["dx"] = math.cos(ang) * spd
                            bolt["dy"] = math.sin(ang) * spd
                    break


def draw_storm_effects(surface, current_time):
    if current_time < storm_domain_until:
        pulse = 0.5 + 0.5 * math.sin(current_time * 0.01)
        r = int(250 + 20 * pulse)
        ring = pygame.Surface((r * 2 + 8, r * 2 + 8), pygame.SRCALPHA)
        pygame.draw.circle(ring, (80, 180, 255, 35), (r + 4, r + 4), r, 4)
        pygame.draw.circle(ring, (180, 240, 255, 50), (r + 4, r + 4), int(r * 0.7), 2)
        surface.blit(ring, ring.get_rect(center=(int(player_x), int(player_y))))
    for bolt in storm_bolts:
        age = current_time - bolt["time"]
        fade = max(0.0, 1.0 - age / max(1, bolt["life"]))
        if bolt["kind"] == "strike":
            if age < 0:
                continue
            col = (180, 230, 255)
            pygame.draw.line(surface, col,
                             (int(bolt["x0"]), int(bolt["y0"])),
                             (int(bolt["x1"]), int(bolt["y1"])), max(2, int(5 * fade)))
            pygame.draw.line(surface, WHITE,
                             (int(bolt["x0"]), int(bolt["y0"])),
                             (int(bolt["x1"]), int(bolt["y1"])), max(1, int(2 * fade)))
            cx = int((bolt["x0"] + bolt["x1"]) * 0.5)
            cy = int((bolt["y0"] + bolt["y1"]) * 0.5)
            pygame.draw.circle(surface, (120, 200, 255), (cx, cy), max(3, int(10 * fade)), 1)
        else:
            x, y = int(bolt["x"]), int(bolt["y"])
            pygame.draw.circle(surface, (100, 210, 255), (x, y), 8)
            pygame.draw.circle(surface, WHITE, (x, y), 4)
            # trail
            for t in range(1, 4):
                pygame.draw.circle(surface, (80, 160, 255),
                                   (int(x - bolt["dx"] * t * 0.35), int(y - bolt["dy"] * t * 0.35)),
                                   max(2, 7 - t * 2))


def named_bosses_alive():
    return any(z.get("boss_key") for z in zombies)


def update_named_bosses(current_time):
    """Special abilities for the Wave-100 legendary bosses."""
    global player_x, player_y
    for z in zombies[:]:
        key = z.get("boss_key")
        if not key:
            continue
        if current_time < z.get("frozen_until", 0):
            continue

        ratio = z["health"] / max(1, z["max_health"])
        if ratio <= 0.5 and z.get("phase", 1) == 1:
            z["phase"] = 2
            z["speed"] *= 1.55
            z["damage"] *= 1.6
            explosions.append({
                "x": z["x"], "y": z["y"], "radius": 140,
                "time": current_time, "type": "spirit",
            })
            trigger_hit_effect(current_time, 6)

        if current_time < z.get("ability_cd", 0):
            continue

        phase = z.get("phase", 1)

        if key == "horde_king":
            # ROAR: knockback ring + spawn pack
            z["ability_cd"] = current_time + (4000 if phase == 1 else 2800)
            if math.hypot(player_x - z["x"], player_y - z["y"]) < 160:
                ang = math.atan2(player_y - z["y"], player_x - z["x"])
                player_x = max(30, min(WIDTH - 30, player_x + math.cos(ang) * 55))
                player_y = max(40, min(HEIGHT - 35, player_y + math.sin(ang) * 55))
                damage_player(12, current_time)
            for _ in range(3 if phase == 1 else 5):
                if not _can_spawn_minion():
                    break
                _spawn_minion(z["x"] + random.uniform(-70, 70), z["y"] + random.uniform(-70, 70),
                              "normal", 70 + wave // 2, 2.2, 0.6, 18)
            explosions.append({"x": z["x"], "y": z["y"], "radius": 120, "time": current_time})

        elif key == "plague_matriarch":
            # Toxic volleys + lingering smoke (NO self-heal)
            z["ability_cd"] = current_time + (3600 if phase == 1 else 2400)
            for _ in range(1 if phase == 1 else 2):
                if len(poison_clouds) >= MAX_POISON_CLOUDS:
                    break
                ox = z["x"] + random.uniform(-40, 40)
                oy = z["y"] + random.uniform(-40, 40)
                poison_clouds.append({
                    "x": ox, "y": oy, "radius": 100 + phase * 20,
                    "damage": 16 + phase * 4, "time": current_time,
                    "until": current_time + 5000, "tick": current_time,
                })
            ang = math.atan2(player_y - z["y"], player_x - z["x"])
            poison_bombs.append({
                "x": float(z["x"]), "y": float(z["y"]),
                "dx": math.cos(ang) * 10, "dy": math.sin(ang) * 10,
                "radius": 120, "damage": 55, "until": current_time + 1400,
                "blast": False, "potion": True, "spin": 0.0, "enemy": True,
            })

        elif key == "cyber_colossus":
            # Shield pulse + rocket barrage
            z["ability_cd"] = current_time + (3000 if phase == 1 else 2000)
            z["shield_until"] = current_time + 1200  # reduced damage window handled in hits
            ang = math.atan2(player_y - z["y"], player_x - z["x"])
            n = 3 if phase == 1 else 5
            for i in range(n):
                a = ang + (i - (n - 1) / 2) * 0.18
                bullets.append({
                    "x": z["x"], "y": z["y"],
                    "dx": math.cos(a) * 8.5, "dy": math.sin(a) * 8.5,
                    "damage": 0, "critical": False, "explosive": True,
                    "explosion_radius": 50, "pierce": 0, "hits": 0,
                    "kind": "normal", "life": 100, "enemy": True, "enemy_dmg": 20,
                })

        elif key == "chrono_wraith":
            # Blink + time shatter (freeze adds, dash strike)
            z["ability_cd"] = current_time + (4500 if phase == 1 else 3000)
            ang = random.uniform(0, math.tau)
            z["x"] = max(40, min(WIDTH - 40, player_x + math.cos(ang) * (90 if phase == 1 else 60)))
            z["y"] = max(50, min(HEIGHT - 50, player_y + math.sin(ang) * (90 if phase == 1 else 60)))
            if math.hypot(player_x - z["x"], player_y - z["y"]) < 80:
                damage_player(16, current_time)
            globals()["frost_slow_until"] = max(frost_slow_until, current_time + 900)
            for o in zombies:
                if o is not z and not o.get("boss_key"):
                    o["frozen_until"] = max(o.get("frozen_until", 0), current_time + 900)

        elif key == "blood_moon_reaper":
            # Cross moon fangs + spin slash zone
            z["ability_cd"] = current_time + (3800 if phase == 1 else 2600)
            ang = math.atan2(player_y - z["y"], player_x - z["x"])
            for spread in (-0.5, -0.2, 0.2, 0.5) if phase == 2 else (-0.3, 0.0, 0.3):
                a = ang + spread
                moon_waves.append({
                    "x": float(z["x"]), "y": float(z["y"]),
                    "dx": math.cos(a) * 12, "dy": math.sin(a) * 12,
                    "angle": a, "damage": 0, "radius": 58.0,
                    "time": current_time, "until": current_time + 1300, "hit": set(),
                    "enemy": True, "enemy_dmg": 24, "anime": True,
                })
            if math.hypot(player_x - z["x"], player_y - z["y"]) < 100:
                damage_player(14, current_time)

        elif key == "swarm_heart":
            # Pulse spawn + pull player inward
            z["ability_cd"] = current_time + (3200 if phase == 1 else 2200)
            if math.hypot(player_x - z["x"], player_y - z["y"]) < 220:
                ang = math.atan2(z["y"] - player_y, z["x"] - player_x)
                player_x += math.cos(ang) * 8
                player_y += math.sin(ang) * 8
            for _ in range(4 if phase == 1 else 6):
                if not _can_spawn_minion():
                    break
                sx, sy = spawn_position()
                _spawn_minion(sx, sy, "fast", 50 + wave // 2, 2.5, 0.5, 15)

        elif key == "mirror_twin":
            # Decoys + mirror shot toward player
            z["ability_cd"] = current_time + (5500 if phase == 1 else 3500)
            decoys = sum(1 for o in zombies if o.get("boss_name") == "MIRROR DECOY")
            if decoys < 4:
                for _ in range(1 if phase == 1 else 2):
                    if decoys >= 4 or len(zombies) >= MAX_ZOMBIES:
                        break
                    zombies.append({
                        "x": z["x"] + random.uniform(-90, 90),
                        "y": z["y"] + random.uniform(-90, 90),
                        "speed": z["speed"] * 1.1, "health": 180, "max_health": 180,
                        "damage": z["damage"] * 0.45, "radius": z["radius"],
                        "type": "boss", "boss_key": None, "boss_name": "MIRROR DECOY",
                        "colors": z.get("colors"), "hit_flash_until": 0, "frozen_until": 0,
                        "ability_cd": current_time + 999999, "phase": 1,
                    })
                    decoys += 1
            ang = math.atan2(player_y - z["y"], player_x - z["x"])
            for spread in (-0.12, 0.12):
                a = ang + spread
                bullets.append({
                    "x": z["x"], "y": z["y"],
                    "dx": math.cos(a) * 11, "dy": math.sin(a) * 11,
                    "damage": 0, "critical": False, "explosive": False,
                    "pierce": 0, "hits": 0, "kind": "plasma", "life": 80,
                    "enemy": True, "enemy_dmg": 15,
                })

        elif key == "frost_titan":
            # Ice spike cross + arena slow
            z["ability_cd"] = current_time + (4000 if phase == 1 else 2700)
            globals()["frost_slow_until"] = max(frost_slow_until, current_time + 2200)
            ang0 = math.atan2(player_y - z["y"], player_x - z["x"])
            for i in range(4):
                a = ang0 + i * (math.pi / 2)
                bullets.append({
                    "x": z["x"], "y": z["y"],
                    "dx": math.cos(a) * 9, "dy": math.sin(a) * 9,
                    "damage": 0, "critical": False, "explosive": False,
                    "pierce": 2, "hits": 0, "kind": "normal", "life": 70,
                    "enemy": True, "enemy_dmg": 18,
                })
            explosions.append({
                "x": z["x"], "y": z["y"], "radius": 100,
                "time": current_time, "type": "spirit",
            })

        elif key == "necro_conductor":
            # Raise dead + lightning line toward player
            z["ability_cd"] = current_time + (4800 if phase == 1 else 3200)
            for _ in range(2 if phase == 1 else 3):
                if not _can_spawn_minion():
                    break
                sx, sy = spawn_position()
                _spawn_minion(sx, sy, "tank", 180 + wave, 1.1, 1.0, 26)
            # beam damage if player is roughly in line
            ang = math.atan2(player_y - z["y"], player_x - z["x"])
            # sample points along beam
            for step in range(1, 12):
                bx = z["x"] + math.cos(ang) * step * 40
                by = z["y"] + math.sin(ang) * step * 40
                if math.hypot(bx - player_x, by - player_y) < 28:
                    damage_player(10, current_time)
                    break
            explosions.append({
                "x": z["x"] + math.cos(ang) * 120, "y": z["y"] + math.sin(ang) * 120,
                "radius": 40, "time": current_time, "type": "spirit",
            })

        elif key == "blood_werewolf":
            # LUNAR HOWL + CLAW LUNGES + SUMMON WOLF PACK (AntonXD)
            z["ability_cd"] = current_time + (3800 if phase == 1 else 2600)
            if math.hypot(player_x - z["x"], player_y - z["y"]) < 180:
                ang = math.atan2(player_y - z["y"], player_x - z["x"])
                player_x = max(30, min(WIDTH - 30, player_x + math.cos(ang) * 55))
                player_y = max(40, min(HEIGHT - 35, player_y + math.sin(ang) * 55))
                damage_player(14 if phase == 1 else 20, current_time)
            ang = math.atan2(player_y - z["y"], player_x - z["x"])
            z["x"] += math.cos(ang) * (12 if phase == 1 else 18)
            z["y"] += math.sin(ang) * (12 if phase == 1 else 18)
            for spread in (-0.5, 0.0, 0.5):
                a = ang + spread
                moon_waves.append({
                    "x": float(z["x"]), "y": float(z["y"]),
                    "dx": math.cos(a) * 13, "dy": math.sin(a) * 13,
                    "angle": a, "damage": 0, "radius": 64.0,
                    "time": current_time, "until": current_time + 1400, "hit": set(),
                    "enemy": True, "enemy_dmg": 22 if phase == 1 else 32, "anime": True,
                })
            for _ in range(2 if phase == 1 else 4):
                if not _can_spawn_minion():
                    break
                _spawn_minion(z["x"] + random.uniform(-80, 80), z["y"] + random.uniform(-80, 80),
                              "fast", 90 + wave // 3, 3.0, 0.7, 16)
            explosions.append({"x": z["x"], "y": z["y"], "radius": 160, "time": current_time, "type": "spirit"})
            trigger_hit_effect(current_time, 7)


frost_slow_until = 0





PRIEST_POWERS = [
    {"key": "q", "name": "CRUCIFIX", "cd": 3500,
     "desc": "Plant a holy crucifix mine. Touching zombies convert and fight for you."},
    {"key": "e", "name": "HOLY WATER", "cd": 7000,
     "desc": "Splash holy water: damage foes, convert nearby, send allies into ninja frenzy."},
]

        
def use_priest_power(key, current_time):
    """Priest dual kit: Q Crucifix mine, E Holy Water."""
    global health
    if selected_character != "Priest":
        return
    if intro_screen or character_screen or armory_screen or paused or game_over or upgrade_screen:
        return
    if not admin_power_ready(key, current_time):
        return
    power = next((p for p in PRIEST_POWERS if p["key"] == key), None)
    if not power:
        return
    if admin_no_cooldown and is_admin:
        admin_power_cd[key] = 0
    else:
        admin_power_cd[key] = current_time + power["cd"]

    mx, my = pygame.mouse.get_pos()
    ang = math.atan2(my - player_y, mx - player_x)
    if key == "q":
        spawn_power_anim(player_x, player_y, current_time, color=(255, 230, 120), style="holy", size=110, life=700)
    else:
        spawn_power_anim(player_x, player_y, current_time, color=(120, 200, 255), style="burst", size=140, life=750)

    if key == "q":
        # CRUCIFIX mine at cursor
        dist = min(220, math.hypot(mx - player_x, my - player_y))
        lx = float(max(30, min(WIDTH - 30, player_x + math.cos(ang) * dist)))
        ly = float(max(40, min(HEIGHT - 35, player_y + math.sin(ang) * dist)))
        if len(crucifixes) >= 12:
            crucifixes.pop(0)
        crucifixes.append({
            "x": lx, "y": ly,
            "time": current_time,
            "until": current_time + 18000,
            "radius": 34,
            "armed": True,
        })
        explosions.append({"x": lx, "y": ly, "radius": 40, "time": current_time, "type": "spirit"})
        return

    if key == "e":
        # HOLY WATER — throw splash at cursor
        dist = min(260, math.hypot(mx - player_x, my - player_y))
        lx = float(max(30, min(WIDTH - 30, player_x + math.cos(ang) * dist)))
        ly = float(max(40, min(HEIGHT - 35, player_y + math.sin(ang) * dist)))
        explosions.append({"x": lx, "y": ly, "radius": 120, "time": current_time, "type": "spirit"})
        explosions.append({"x": lx, "y": ly, "radius": 70, "time": current_time, "type": "spirit"})
        # puddle marker (short-lived convert zone)
        crucifixes.append({
            "x": lx, "y": ly,
            "time": current_time,
            "until": current_time + 5000,
            "radius": 70,
            "armed": True,
            "holy_water": True,
        })
        for z in zombies[:]:
            d = math.hypot(z["x"] - lx, z["y"] - ly)
            if d > 110 + z.get("radius", 16):
                continue
            if z.get("ally"):
                # berserk buff — ninja-style
                z["ally_until"] = max(z.get("ally_until", current_time), current_time + 12000)
                z["speed"] = max(z.get("speed", 1.5), 3.2)
                z["damage"] = max(z.get("damage", 5), 18)
                z["ninja_mode"] = True
                z["hit_flash_until"] = current_time + 120
            elif not z.get("boss_key"):
                # damage + chance to convert
                z["health"] -= max(25, damage * 1.8)
                z["hit_flash_until"] = current_time + 120
                if z["health"] <= 0:
                    kill_zombie(z)
                elif d < 75 + z.get("radius", 16):
                    z["ally"] = True
                    z["ally_until"] = current_time + 16000
                    z["ally_hit"] = 0
                    z["ninja_mode"] = True
                    z["speed"] = max(2.8, z.get("speed", 1.5) * 1.4)
                    z["damage"] = max(14, z.get("damage", 1) * 3.0)
                    z["health"] = min(z.get("max_health", z["health"]) * 1.2, z["health"] + 30)
            else:
                z["health"] -= max(20, damage * 1.2)
                z["hit_flash_until"] = current_time + 100
                if z["health"] <= 0:
                    kill_zombie(z)
        health = min(max_health, health + 12)
        trigger_hit_effect(current_time, 5)
        return


def update_crucifixes_and_allies(current_time):
    """Priest crucifix mines convert zombies into allies that fight enemies."""
    # Expire mines
    for c in crucifixes[:]:
        if current_time >= c.get("until", 0):
            crucifixes.remove(c)

    # Convert: enemy zombie touches armed crucifix
    for c in crucifixes[:]:
        if not c.get("armed", True):
            continue
        for z in zombies[:]:
            if z.get("ally"):
                continue
            if z.get("boss_key"):
                continue  # named bosses cannot be converted
            if math.hypot(z["x"] - c["x"], z["y"] - c["y"]) < c.get("radius", 34) + z.get("radius", 16):
                z["ally"] = True
                z["ally_until"] = current_time + 16000
                z["ally_hit"] = 0
                z["ninja_mode"] = True
                play_sfx("convert", 0.3)
                # holy buff — ninja clone style fighter
                z["health"] = min(z.get("max_health", z["health"]) * 1.25, z["health"] + 40)
                z["max_health"] = max(z.get("max_health", z["health"]), z["health"])
                z["speed"] = max(2.8, z.get("speed", 1.5) * 1.35)
                z["damage"] = max(12, z.get("damage", 1) * 2.8)
                z["hit_flash_until"] = current_time + 200
                c["armed"] = False
                if c in crucifixes:
                    crucifixes.remove(c)
                explosions.append({"x": z["x"], "y": z["y"], "radius": 50, "time": current_time, "type": "spirit"})
                break

    # Ally AI — ninja-style: dash, lunge, rapid strikes (like shadow clone)
    for z in zombies[:]:
        if not z.get("ally"):
            continue
        if current_time >= z.get("ally_until", 0):
            if z in zombies:
                zombies.remove(z)
            continue
        if current_time < z.get("frozen_until", 0):
            continue
        enemies = [o for o in zombies if not o.get("ally") and o is not z]
        if not enemies:
            # idle orbit near player
            ang = current_time * 0.003 + id(z) * 0.1
            z["x"] = player_x + math.cos(ang) * 50
            z["y"] = player_y + math.sin(ang) * 40
            continue
        target = min(enemies, key=lambda o: math.hypot(o["x"] - z["x"], o["y"] - z["y"]))
        ang = math.atan2(target["y"] - z["y"], target["x"] - z["x"])
        dist = math.hypot(target["x"] - z["x"], target["y"] - z["y"])
        ninja = True  # all Priest allies fight like ninja clone
        # dash / chase like ninja clone
        step = min(4.5, dist)
        spd = max(2.8, z.get("speed", 1.5) * 1.4)
        z["x"] += math.cos(ang) * min(step, spd)
        z["y"] += math.sin(ang) * min(step, spd)
        z["x"] = max(20, min(WIDTH - 20, z["x"]))
        z["y"] = max(30, min(HEIGHT - 30, z["y"]))
        # ninja-style rapid lunge strikes
        hit_range = z.get("radius", 16) + target.get("radius", 16) + 16
        hit_cd = 300
        if dist < hit_range:
            if current_time - z.get("ally_hit", 0) >= hit_cd:
                dmg = max(12, z.get("damage", 5) * 1.5)
                if current_time < target.get("shield_until", 0):
                    dmg *= 0.4
                target["health"] -= dmg
                target["hit_flash_until"] = current_time + 90
                z["ally_hit"] = current_time
                explosions.append({
                    "x": target["x"], "y": target["y"], "radius": 20,
                    "time": current_time, "type": "spirit",
                })
                if target["health"] <= 0:
                    kill_zombie(target)


def draw_crucifixes(surface, current_time):
    """Draw planted holy crucifix mines."""
    for c in crucifixes:
        x, y = int(c["x"]), int(c["y"])
        pulse = 0.5 + 0.5 * math.sin(current_time * 0.008 + x * 0.01)
        gold = (255, 230, 120)
        # glow
        glow = pygame.Surface((70, 70), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 230, 120, int(50 + 40 * pulse)), (35, 35), 28)
        surface.blit(glow, (x - 35, y - 35), special_flags=pygame.BLEND_RGBA_ADD)
        # cross
        pygame.draw.rect(surface, (40, 30, 10), (x - 4, y - 22, 8, 40))
        pygame.draw.rect(surface, (40, 30, 10), (x - 14, y - 10, 28, 8))
        pygame.draw.rect(surface, gold, (x - 3, y - 21, 6, 38))
        pygame.draw.rect(surface, gold, (x - 13, y - 9, 26, 6))
        pygame.draw.circle(surface, (255, 255, 200), (x, y - 18), 4)
        # range ring when armed
        if c.get("armed", True):
            col = (120, 200, 255) if c.get("holy_water") else gold
            pygame.draw.circle(surface, col, (x, y), int(c.get("radius", 34)), 1)
            if c.get("holy_water"):
                # water puddle
                puddle = pygame.Surface((90, 50), pygame.SRCALPHA)
                pygame.draw.ellipse(puddle, (100, 180, 255, 70), puddle.get_rect())
                surface.blit(puddle, (x - 45, y - 10))


def update_character_power(current_time):
    global health, character_heal_timer, shadow_clone, turret

    update_named_bosses(current_time)
    update_crucifixes_and_allies(current_time)

    if selected_character == "Reaper":
        update_admin_powers(current_time)
    if selected_character == "Storm Sovereign":
        update_storm_powers(current_time)

    # NANO REGEN upgrade.
    global regen_timer
    if regen_amount and current_time >= regen_timer:
        if not named_bosses_alive():
            health = min(max_health, health + regen_amount)
        regen_timer = current_time + 2500

    # Survivor passive regeneration.
    if selected_character == "Survivor" and current_time >= character_heal_timer:
        if not named_bosses_alive():
            health = min(max_health, health + 3)
        character_heal_timer = current_time + 3000

    # Engineer turret: smart target lock + rapid projectile + splash damage.
    if turret:
        if turret["health"] <= 0:
            turret = None
        elif zombies:
            foes = [z for z in zombies if not z.get("ally")]
            if foes:
                target = min(foes, key=lambda z: math.hypot(z["x"] - turret["x"], z["y"] - turret["y"]))
                distance = math.hypot(target["x"] - turret["x"], target["y"] - turret["y"])
                if distance <= turret["range"]:
                    turret["rotation"] = math.atan2(target["y"] - turret["y"], target["x"] - turret["x"])
                    if current_time - turret["hit_timer"] >= turret.get("fire_delay", 320):
                        a = turret["rotation"]
                        turret_bullets.append({
                            "x": turret["x"] + math.cos(a) * 22,
                            "y": turret["y"] + math.sin(a) * 22,
                            "dx": math.cos(a) * 14, "dy": math.sin(a) * 14,
                            "damage": turret["damage"],
                            "splash": turret.get("splash", 42),
                            "life": 900,
                        })
                        turret["hit_timer"] = current_time
                        turret["shot_flash"] = current_time + 70

    # Ninja shadow clone attacks the nearest zombie.
    if shadow_clone:
        if current_time >= shadow_clone["until"] or shadow_clone["health"] <= 0:
            shadow_clone = None
        elif zombies:
            foes = [z for z in zombies if not z.get("ally")]
            if not foes:
                target = None
            else:
                target = min(foes, key=lambda z: math.hypot(z["x"] - shadow_clone["x"], z["y"] - shadow_clone["y"]))
            if target is None:
                angle = 0.0
            else:
                angle = math.atan2(target["y"] - shadow_clone["y"], target["x"] - shadow_clone["x"])
            # Stable chase: cap movement and keep the clone inside the playable map.
            distance = math.hypot(target["x"] - shadow_clone["x"], target["y"] - shadow_clone["y"])
            if distance > target["radius"] + 18:
                shadow_clone["x"] += math.cos(angle) * min(3.0, distance)
                shadow_clone["y"] += math.sin(angle) * min(3.0, distance)
            shadow_clone["x"] = max(28, min(WIDTH - 28, shadow_clone["x"]))
            shadow_clone["y"] = max(38, min(HEIGHT - 38, shadow_clone["y"]))
            if math.hypot(target["x"] - shadow_clone["x"], target["y"] - shadow_clone["y"]) < target["radius"] + 18:
                if current_time - shadow_clone["hit_timer"] >= 450 and target in zombies:
                    target["health"] -= shadow_clone["damage"]
                    target["hit_flash_until"] = current_time + 75
                    shadow_clone["hit_timer"] = current_time
                    if target["health"] <= 0 and target in zombies:
                        kill_zombie(target)

    # Scientist toxic potion: flies, shatters, leaves lasting poison smoke clouds.
    for bomb in poison_bombs[:]:
        if bomb.get("blast"):
            if current_time - bomb["blast_time"] >= 280:
                poison_bombs.remove(bomb)
            continue

        bomb["x"] += bomb["dx"]
        bomb["y"] += bomb["dy"]
        bomb["dx"] *= 0.955
        bomb["dy"] *= 0.955
        bomb["spin"] = bomb.get("spin", 0) + 0.35

        hit_zombie = None
        for zombie in zombies[:]:
            if math.hypot(zombie["x"] - bomb["x"], zombie["y"] - bomb["y"]) < zombie["radius"] + 14:
                hit_zombie = zombie
                break

        if hit_zombie is not None or current_time >= bomb["until"] or \
                abs(bomb["dx"]) + abs(bomb["dy"]) < 0.8:
            bomb["blast"] = True
            bomb["blast_time"] = current_time
            explosions.append({
                "x": bomb["x"], "y": bomb["y"], "radius": bomb["radius"],
                "time": current_time, "type": "poison",
            })
            if bomb.get("enemy"):
                if math.hypot(player_x - bomb["x"], player_y - bomb["y"]) <= bomb["radius"] + 20:
                    damage_player(max(8, bomb["damage"] * 0.35), current_time)
                poison_clouds.append({
                    "x": bomb["x"], "y": bomb["y"],
                    "radius": bomb["radius"] * 0.75,
                    "damage": 12, "time": current_time,
                    "until": current_time + 4000, "tick": current_time,
                })
            else:
                for zombie in zombies[:]:
                    blast_distance = math.hypot(zombie["x"] - bomb["x"], zombie["y"] - bomb["y"])
                    if blast_distance <= bomb["radius"] + zombie["radius"]:
                        falloff = max(0.4, 1.0 - blast_distance / max(1, bomb["radius"]))
                        zombie["health"] -= bomb["damage"] * falloff
                        zombie["hit_flash_until"] = current_time + 100
                        trigger_hit_effect(current_time, 3)
                        if zombie["health"] <= 0:
                            kill_zombie(zombie)
                poison_clouds.append({
                    "x": bomb["x"], "y": bomb["y"],
                    "radius": bomb["radius"] * 0.85,
                    "damage": 9 + wave * 0.6,
                    "time": current_time,
                    "until": current_time + 5500,
                    "tick": current_time,
                })

    # Poison smoke clouds: continuous damage to zombies inside
    for cloud in poison_clouds[:]:
        if current_time >= cloud["until"]:
            poison_clouds.remove(cloud)
            continue
        if current_time - cloud["tick"] >= 280:
            cloud["tick"] = current_time
            if math.hypot(player_x - cloud["x"], player_y - cloud["y"]) <= cloud["radius"] + 18:
                if named_bosses_alive():
                    damage_player(max(2, cloud["damage"] * 0.25), current_time)
            for zombie in zombies[:]:
                if math.hypot(zombie["x"] - cloud["x"], zombie["y"] - cloud["y"]) <= cloud["radius"] + zombie["radius"]:
                    zombie["health"] -= cloud["damage"]
                    zombie["hit_flash_until"] = current_time + 60
                    if zombie["health"] <= 0:
                        kill_zombie(zombie)



def draw_character_power_effects(surface, current_time):
    draw_power_anims(surface, current_time)
    draw_crucifixes(surface, current_time)

    if turret:
        tx, ty = int(turret["x"]), int(turret["y"])
        angle = turret.get("rotation", 0.0)
        # Range ring, platform, shield and rotating cannon.
        pygame.draw.circle(surface, (50, 130, 130), (tx, ty), int(turret.get("range", 390)), 1)
        pygame.draw.circle(surface, (20, 35, 40), (tx, ty), 31)
        pygame.draw.circle(surface, BLACK, (tx, ty), 31, 4)
        pygame.draw.circle(surface, GOLD, (tx, ty), 24, 3)
        pygame.draw.circle(surface, (70, 80, 90), (tx, ty), 16)
        bx = tx + int(math.cos(angle) * 31)
        by = ty + int(math.sin(angle) * 31)
        pygame.draw.line(surface, BLACK, (tx, ty), (bx, by), 15)
        pygame.draw.line(surface, METAL, (tx, ty), (bx, by), 9)
        pygame.draw.circle(surface, CYAN, (tx, ty), 7)
        if current_time < turret.get("shot_flash", 0):
            fx = tx + int(math.cos(angle) * 47); fy = ty + int(math.sin(angle) * 47)
            pygame.draw.circle(surface, GOLD, (fx, fy), 10)
        hpw = 58
        pygame.draw.rect(surface, BLACK, (tx - hpw // 2, ty - 49, hpw, 8))
        pygame.draw.rect(surface, HEALTH_COLOR, (tx - hpw // 2, ty - 49, int(hpw * max(0, turret["health"]) / turret["max_health"]), 8))
        label = FONT_TINY.render(f"AUTO TURRET  {turret['health']}/{turret['max_health']}", True, GOLD)
        surface.blit(label, (tx - label.get_width() // 2, ty + 38))

    for tb in turret_bullets:
        pygame.draw.circle(surface, GOLD, (int(tb["x"]), int(tb["y"])), 5)
        pygame.draw.circle(surface, WHITE, (int(tb["x"]), int(tb["y"])), 2)

    if shadow_clone:
        cx, cy = int(shadow_clone["x"]), int(shadow_clone["y"])
        draw_player(surface, cx, cy, selected_character)
        pygame.draw.circle(surface, CYAN, (cx, cy), 31, 2)
        hpw = 46
        pygame.draw.rect(surface, BLACK, (cx - hpw // 2, cy - 50, hpw, 7))
        pygame.draw.rect(surface, CYAN, (cx - hpw // 2, cy - 50, int(hpw * max(0, shadow_clone["health"]) / shadow_clone.get("max_health", 5)), 7))
        label = FONT_TINY.render(f"CLONE {shadow_clone['health']}/{shadow_clone.get('max_health', 5)}", True, CYAN)
        surface.blit(label, (cx - label.get_width() // 2, cy + 38))

    for bomb in poison_bombs:
        if bomb.get("blast"):
            continue
        bx, by = int(bomb["x"]), int(bomb["y"])
        # glass potion vial
        pygame.draw.ellipse(surface, (40, 90, 50), (bx - 7, by - 11, 14, 18))
        pygame.draw.ellipse(surface, (120, 255, 90), (bx - 5, by - 8, 10, 12))
        pygame.draw.rect(surface, (180, 220, 200), (bx - 4, by - 14, 8, 5), border_radius=2)
        pygame.draw.circle(surface, (200, 255, 160), (bx - 2, by - 4), 2)

    for cloud in poison_clouds:
        age = current_time - cloud["time"]
        life = max(0.0, 1.0 - age / max(1, cloud["until"] - cloud["time"]))
        cx, cy = int(cloud["x"]), int(cloud["y"])
        r = int(cloud["radius"] * (0.85 + 0.15 * math.sin(current_time * 0.004)))
        smoke = pygame.Surface((r * 2 + 20, r * 2 + 20), pygame.SRCALPHA)
        cc = smoke.get_width() // 2
        for i in range(5, 0, -1):
            a = int(28 * life * (i / 5.0))
            pygame.draw.circle(smoke, (80, 200, 60, a), (cc + int(math.sin(current_time * 0.003 + i) * 6),
                                                          cc + int(math.cos(current_time * 0.002 + i) * 4)), int(r * i / 5))
        pygame.draw.circle(smoke, (150, 255, 90, int(50 * life)), (cc, cc), max(8, r // 3))
        surface.blit(smoke, smoke.get_rect(center=(cx, cy)))

    if selected_character == "Time Lord" and current_time < ability_duration_until:
        pygame.draw.circle(surface, GOLD, (int(player_x), int(player_y)), 55, 3)
    elif selected_character == "Frozen" and current_time < ability_duration_until:
        pygame.draw.circle(surface, CYAN, (int(player_x), int(player_y)), 45, 3)
    elif selected_character == "Magician" and current_time < ability_duration_until:
        pygame.draw.circle(surface, PURPLE, (int(player_x), int(player_y)), 30, 3)


# =========================================================
# RESET
# =========================================================
def reset_game():
    global player_x, player_y, health, max_health
    global damage, shoot_delay, player_speed, bullet_speed, gun_level
    global executor_until, executor_bonus, werewolf_until, werewolf_bonus
    global crit_chance, crit_multiplier, damage_reduction, upgrade_rerolls, upgrade_pick_count
    global has_smg, has_rpg, explosions
    global xp, level, xp_needed, wave, score, kills, run_recorded, best_run_flags
    global game_over, upgrade_screen, gun_choice_screen
    global paused
    global orbit_type, orbit_count, orbit_angle, orbit_damage
    global orbit_last_shot, orbit_shoot_delay
    global player_flash_until, last_player_hit_time
    global screen_shake_until, screen_shake_strength
    global ability_cooldown, ability_duration_until, character_heal_timer, shadow_clone, turret, poison_bombs, poison_clouds
    global mp_player_dead, mp_team_lives, mp_difficulty
    global bullet_size, upgrade_levels
    global lifesteal, regen_amount, regen_timer, pierce, shrapnel, thorns
    global freeze_chance, coin_bonus, xp_bonus, med_drop_chance

    upgrade_levels = {}
    bullet_size = 5
    lifesteal = 0
    regen_amount = 0
    regen_timer = 0
    pierce = 0
    shrapnel = 0
    thorns = 0
    freeze_chance = 0.0
    coin_bonus = 0.0
    xp_bonus = 0.0
    med_drop_chance = 0.22

    player_x = WIDTH // 2
    player_y = HEIGHT // 2
    mp_player_dead = False
    if mp_difficulty == "normal": mp_team_lives = 6
    elif mp_difficulty == "hardcore": mp_team_lives = 3
    else: mp_team_lives = 1
    stats = CHARACTER_STATS.get(selected_character, CHARACTER_STATS["Survivor"])
    max_health = stats["hp"]
    health = max_health
    damage = int(25 * stats["damage"])
    shoot_delay = int(250 * stats["fire"])
    if is_melee_class():
        # Katana swings land instantly, so they cost a little extra recovery time.
        damage = int(damage * 1.9)
        shoot_delay = 300
    crit_chance = 0.08
    crit_multiplier = 1.75
    damage_reduction = stats["armor"]
    upgrade_rerolls = 2
    upgrade_pick_count = 0
    player_speed = stats["speed"]
    bullet_speed = 14
    gun_level = 1
    has_smg = False
    has_rpg = False
    explosions = []
    power_fx.clear()

    orbit_type = "none"
    orbit_count = 0
    orbit_angle = 0.0
    orbit_radius = 78
    orbit_speed = 0.055
    orbit_damage = 18
    orbit_last_shot = 0
    orbit_shoot_delay = 520
    orbit_trail.clear()
    orbit_target_memory.clear()

    player_flash_until = 0
    last_player_hit_time = 0
    screen_shake_until = 0
    screen_shake_strength = 0
    ability_cooldown = 0
    # clear transform state (stats already reset from CHARACTER_STATS above)
    executor_bonus = {}
    werewolf_bonus = {}
    executor_until = 0
    werewolf_until = 0
    time_history.clear()
    time_history_last = 0
    rewind_active = False
    rewind_path = []
    rewind_index = 0
    rewind_fx_until = 0
    ability_duration_until = 0
    character_heal_timer = 0
    shadow_clone = None
    turret = None
    poison_bombs.clear()
    poison_clouds.clear()
    crucifixes.clear()

    xp = 0
    level = 1
    xp_needed = 100
    wave = 1
    score = 0
    kills = 0
    run_recorded = False

    bullets.clear()
    slashes.clear()
    moon_waves.clear()
    storm_bolts.clear()
    global bankai_until, bankai_next, storm_domain_until
    bankai_until = 0
    bankai_next = 0
    storm_domain_until = 0
    werewolf_until = 0
    werewolf_bonus = {}
    for _k in admin_power_cd:
        admin_power_cd[_k] = 0
    orbit_bullets.clear()
    turret_bullets.clear()
    zombies.clear()
    meds.clear()
    orbit_hit_cooldowns.clear()

    game_over = False
    upgrade_screen = False
    gun_choice_screen = False
    paused = False
    spawn_wave()


# Game state is reset when PLAY is pressed.


# =========================================================
# ADMIN PANEL
# =========================================================
def _admin_execute_command(command):
    """Run one safe, explicit admin command. No shell/system execution is allowed."""
    global coins, unlocked_characters, selected_character, wave
    global xp, level, xp_needed, health, max_health, damage, shoot_delay
    global player_speed, bullet_speed, gun_level, has_smg, has_rpg
    global orbit_type, orbit_count, orbit_damage, orbit_shoot_delay, orbit_last_shot
    global ability_cooldown, ability_duration_until, admin_power_cd
    global aimbot_enabled, upgrade_rerolls, admin_no_cooldown, is_admin

    raw = command.strip()
    if raw.startswith("/"):
        raw = raw[1:].strip()
    parts = raw.split()
    if not parts:
        return ""
    cmd = parts[0].lower().lstrip("/")
    arg = " ".join(parts[1:])

    if cmd == "help":
        return ("give money [n] | give admin [user] | give power | nocd | cooldown | "
                "money [n] | xp [n] | skip | aimbot_on/off | unlock | kill | max | heal | freeze | boss")
    if cmd == "aimbot":
        aimbot_enabled = not aimbot_enabled
        return "AIMBOT: " + ("ON" if aimbot_enabled else "OFF")
    if cmd == "aimbot_on":
        aimbot_enabled = True
        return "AIMBOT: ON"
    if cmd == "aimbot_off":
        aimbot_enabled = False
        return "AIMBOT: OFF"

    if cmd == "give":
        if len(parts) < 2:
            return "USAGE: give money [amount] | give admin [username] | give power"
        what = parts[1].lower()
        if what in ("money", "coins", "cash"):
            num = parts[2].replace(",", "").lstrip("+") if len(parts) > 2 else "1000000"
            if not num.lstrip("-").isdigit():
                return "USAGE: give money <amount>"
            amount = int(num)
            coins += amount
            save_profile()
            return f"GAVE MONEY: +{amount:,}  (now {coins:,})"
        if what in ("admin", "adminpower", "admin_power"):
            target = current_username
            if what == "admin" and len(parts) >= 3 and parts[2].lower() not in ("power", "powers"):
                target = parts[2]
            data = _load_accounts()
            found = None
            for name in data:
                if name.lower() == (target or "").lower():
                    found = name
                    break
            if found is None:
                return f"ACCOUNT NOT FOUND: {target}"
            data[found]["role"] = "admin"
            _save_accounts(data)
            if found.lower() == (current_username or "").lower():
                is_admin = True
            return f"GAVE ADMIN POWER TO: {found}"
        if what in ("power", "powers", "reaper"):
            is_admin = True
            unlocked_characters.add("Reaper")
            unlocked_characters.add("Storm Sovereign")
            selected_character = "Reaper"
            ability_cooldown = 0
            for _k in admin_power_cd:
                admin_power_cd[_k] = 0
            admin_no_cooldown = True
            gun_level = max(gun_level, 8)
            damage = max(damage, 200)
            save_profile()
            return "GAVE ADMIN POWER: Reaper + Storm Sovereign unlocked"
        if what in ("storm", "sovereign"):
            is_admin = True
            unlocked_characters.add("Storm Sovereign")
            selected_character = "Storm Sovereign"
            ability_cooldown = 0
            for _k in admin_power_cd:
                admin_power_cd[_k] = 0
            admin_no_cooldown = True
            gun_level = max(gun_level, 6)
            damage = max(damage, 180)
            save_profile()
            return "GAVE ADMIN POWER: Storm Sovereign + no cooldown"
        return "USAGE: give money [n] | give admin [user] | give power"

    if cmd in ("nocd", "nocooldown", "no_cooldown"):
        admin_no_cooldown = not admin_no_cooldown
        if admin_no_cooldown:
            ability_cooldown = 0
            for _k in admin_power_cd:
                admin_power_cd[_k] = 0
        return "NO COOLDOWN: " + ("ON" if admin_no_cooldown else "OFF")
    if cmd in ("cooldown", "cd", "resetcd"):
        ability_cooldown = 0
        for _k in admin_power_cd:
            admin_power_cd[_k] = 0
        return "COOLDOWNS CLEARED"

    if cmd == "reroll":
        if upgrade_screen and upgrade_rerolls > 0:
            upgrade_rerolls -= 1
            return "UPGRADE CARDS REROLLED"
        return "NO REROLL AVAILABLE"
    if cmd == "money":
        amount = int(parts[1]) if len(parts) > 1 and parts[1].replace(",","").lstrip("-").isdigit() else 1000000
        coins += amount
        save_profile()
        return f"MONEY: +{amount:,}"
    if cmd == "unlock":
        global owned_class_skins, owned_gun_skins
        unlocked_characters.update(CHARACTER_PRICES.keys())
        for _c in CHARACTER_PRICES:
            owned_class_skins.setdefault(_c, set()).update(sk["name"] for sk in class_skin_list(_c))
        owned_gun_skins.update(GUN_SKIN_KEYS)
        save_profile()
        return "ALL UNLOCKED"
    if cmd == "kill":
        count = len(zombies)
        for z in zombies[:]:
            kill_zombie(z)
        return f"KILLED {count}"
    if cmd == "xp":
        if len(parts) < 2:
            return "USAGE: xp <amount>"
        num = parts[1].replace(",","").lstrip("+")
        if not num.lstrip("-").isdigit():
            return "USAGE: xp <amount>"
        amount = int(num)
        xp += amount
        return f"XP: +{amount:,}"
    if cmd == "max":
        gun_level = 8 if is_melee_class() else 5
        has_rpg = True
        damage = max(damage, 200)
        shoot_delay = min(shoot_delay, 60)
        bullet_speed = max(bullet_speed, 26)
        orbit_type = "auto"
        orbit_count = 6
        orbit_damage = max(orbit_damage, 70)
        orbit_shoot_delay = 250
        save_profile()
        return "WEAPONS MAXED"
    if cmd == "heal":
        health = max_health
        return "HEALTH RESTORED"
    if cmd == "freeze":
        until = pygame.time.get_ticks() + 5000
        for z in zombies:
            z["frozen_until"] = until
        return "ZOMBIES FROZEN 5s"
    if cmd == "boss":
        bx, by = spawn_position()
        boss_hp = 5000 + wave * 400
        zombies.append({
            "x": bx, "y": by, "speed": 0.9 + wave * 0.02,
            "health": boss_hp, "max_health": boss_hp, "damage": 3.0,
            "radius": 48, "type": "boss", "hit_flash_until": 0, "frozen_until": 0,
        })
        return "BOSS SPAWNED"
    if cmd == "skip":
        # skip [n] — jump forward n waves (default 5). Cap at wave 1000.
        try:
            n = int(arg) if arg else 5
        except ValueError:
            return "USAGE: skip [waves]  e.g. skip 100  or  skip 999"
        n = max(1, min(999, n))
        wave = min(1000, wave + n)
        spawn_wave()
        return f"SKIPPED +{n} → WAVE {wave}"
    if cmd == "reset":
        coins = 0
        unlocked_characters = {"Survivor"}
        selected_character = "Survivor"
        save_profile()
        return "SAVE RESET"
    if cmd == "nightmare":
        return "NIGHTMARE SET"
    if cmd == "kickall":
        return "KICK-ALL" if mp_connected and mp_is_host else "NOT HOST"
    if cmd == "broadcast":
        if not arg:
            return "USAGE: broadcast <msg>"
        if mp_connected and mp_is_host:
            mp_send({"action": "message", "message": "ADMIN: " + arg})
            return "SENT"
        return "NOT HOST"
    if cmd == "accounts":
        data = _load_accounts()
        names = [f"{n} ({r.get('role','player')})" for n, r in data.items()]
        return "ACCOUNTS: " + ", ".join(names[:10])
    return "UNKNOWN — type help"


def admin_panel():
    """Standalone admin command screen. F1 opens it from any main-game state."""
    if not is_admin:
        return

    command = ""
    history = ["ADMIN COMMAND CENTER READY", "Type help for commands."]
    input_box = pygame.Rect(100, 565, 900, 55)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_F1):
                    return
                elif event.key == pygame.K_BACKSPACE:
                    command = command[:-1]
                elif event.key == pygame.K_RETURN:
                    result = _admin_execute_command(command)
                    if command.strip():
                        history.append("> " + command.strip())
                    if result:
                        history.append(result)
                    history = history[-8:]
                    command = ""
                elif event.unicode and event.unicode.isprintable() and len(command) < 100:
                    command += event.unicode

        draw_zombie_bg(screen, pygame.time.get_ticks())
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))
        panel = pygame.Rect(65, 45, WIDTH - 130, 620)
        draw_panel(screen, panel, (9, 12, 18), GOLD, 3)
        center_text(screen, FONT_BIG, "ADMIN COMMAND CENTER", (WIDTH // 2, 90), GOLD)
        center_text(screen, FONT_TINY, f"{ADMIN_TAG}  {ADMIN_DISPLAY_NAME}   •   F1 / ESC = RETURN   •   F7 TITLE",
                    (WIDTH // 2, 135), GOLD)

        y = 175
        for line in history:
            screen.blit(FONT_TINY.render(line[:115], True, WHITE), (105, y))
            y += 40

        pygame.draw.rect(screen, (18, 22, 29), input_box, border_radius=8)
        pygame.draw.rect(screen, CYAN, input_box, 3, border_radius=8)
        screen.blit(FONT_SMALL.render("> " + command, True, WHITE), (input_box.x + 14, input_box.y + 16))
        center_text(screen, FONT_TINY, "COMMANDS: help • skip • aimbot_on/off • money • unlock • kill • xp • max • heal • freeze • boss • reset • reroll",
                    (WIDTH // 2, 645), STONE_LIGHT)
        pygame.display.flip()
        clock.tick(60)


# =========================================================
# AIMBOT + PLAYER NAME HELPERS
# =========================================================
def get_aimbot_target():
    """Return the nearest live zombie inside aimbot range."""
    if not aimbot_enabled or not zombies:
        return None
    best = None
    best_d = aimbot_range
    for z in zombies:
        if z.get("health", 0) <= 0:
            continue
        d = math.hypot(z["x"] - player_x, z["y"] - player_y)
        if d < best_d:
            best = z
            best_d = d
    return best


def draw_player_name(surface):
    """Draw name above player. Admin: line1 🧟ADMIN, line2 AntonXD (toggle with F7)."""
    if not current_username:
        return
    if is_admin and admin_title_visible:
        # Section 1: 🧟ADMIN
        tag = FONT_TINY.render(ADMIN_TAG, True, GOLD)
        tag_sh = FONT_TINY.render(ADMIN_TAG, True, BLACK)
        tx = int(player_x - tag.get_width() / 2)
        ty = int(player_y - 88)
        surface.blit(tag_sh, (tx + 2, ty + 2))
        surface.blit(tag, (tx, ty))
        # Section 2: AntonXD
        name = ADMIN_DISPLAY_NAME
        col = GOLD
        y = int(player_y - 68)
    elif is_admin:
        # Title hidden — still show username quietly
        name = current_username
        col = WHITE
        y = int(player_y - 67)
    else:
        name = current_username
        col = WHITE
        y = int(player_y - 67)
    label = FONT_TINY.render(name, True, col)
    shadow = FONT_TINY.render(name, True, BLACK)
    x = int(player_x - label.get_width() / 2)
    surface.blit(shadow, (x + 2, y + 2))
    surface.blit(label, (x, y))


def draw_aimbot_indicator(surface):
    if not aimbot_enabled:
        return
    target = get_aimbot_target()
    if target:
        tx, ty = int(target["x"]), int(target["y"])
        r = int(target.get("radius", 18)) + 10
        pygame.draw.circle(surface, RED, (tx, ty), r, 3)
        pygame.draw.line(surface, RED, (int(player_x), int(player_y)), (tx, ty), 2)
        pygame.draw.line(surface, GOLD, (tx - r - 5, ty), (tx + r + 5, ty), 1)
        pygame.draw.line(surface, GOLD, (tx, ty - r - 5), (tx, ty + r + 5), 1)



# =========================================================
# LAPTOP / MOBILE CONTROLS
# =========================================================
# Virtual stick + action buttons for mobile mode (mouse/touch as pointer).
_mobile_stick_active = False
_mobile_stick_dx = 0.0
_mobile_stick_dy = 0.0
_mobile_stick_origin = (120, HEIGHT - 120)

MOBILE_STICK_BASE = pygame.Rect(40, HEIGHT - 200, 160, 160)
MOBILE_SHOOT_BTN = pygame.Rect(WIDTH - 170, HEIGHT - 180, 130, 130)
MOBILE_ABILITY_BTN = pygame.Rect(WIDTH - 170, HEIGHT - 330, 130, 90)
MOBILE_PAUSE_BTN = pygame.Rect(WIDTH - 100, 16, 80, 44)


def mobile_pointer_in(rect, pos):
    return rect.collidepoint(pos)


def update_mobile_input(mouse_pos, mouse_down):
    """Read virtual stick + return (move_x, move_y, shooting, ability_pressed)."""
    global _mobile_stick_active, _mobile_stick_dx, _mobile_stick_dy
    mx, my = mouse_pos
    shooting = False
    ability = False

    if mouse_down and MOBILE_STICK_BASE.collidepoint(mx, my):
        _mobile_stick_active = True
    if not mouse_down:
        _mobile_stick_active = False
        _mobile_stick_dx = 0.0
        _mobile_stick_dy = 0.0

    if _mobile_stick_active:
        cx, cy = MOBILE_STICK_BASE.center
        dx = mx - cx
        dy = my - cy
        dist = math.hypot(dx, dy)
        max_r = 55
        if dist > max_r and dist > 0:
            dx = dx / dist * max_r
            dy = dy / dist * max_r
            dist = max_r
        if dist > 8:
            _mobile_stick_dx = dx / max_r
            _mobile_stick_dy = dy / max_r
        else:
            _mobile_stick_dx = 0.0
            _mobile_stick_dy = 0.0

    if mouse_down and MOBILE_SHOOT_BTN.collidepoint(mx, my):
        shooting = True
    if mouse_down and MOBILE_ABILITY_BTN.collidepoint(mx, my):
        ability = True

    return _mobile_stick_dx, _mobile_stick_dy, shooting, ability


def draw_mobile_controls(surface, current_time):
    if control_mode != "mobile":
        return
    # stick base
    pygame.draw.circle(surface, (20, 24, 32), MOBILE_STICK_BASE.center, 70)
    pygame.draw.circle(surface, (70, 80, 95), MOBILE_STICK_BASE.center, 70, 3)
    cx, cy = MOBILE_STICK_BASE.center
    knob_x = cx + int(_mobile_stick_dx * 55)
    knob_y = cy + int(_mobile_stick_dy * 55)
    pygame.draw.circle(surface, (90, 200, 220), (knob_x, knob_y), 28)
    pygame.draw.circle(surface, WHITE, (knob_x, knob_y), 28, 2)
    center_text(surface, FONT_TINY, "MOVE", (cx, cy + 88), STONE_LIGHT)

    # shoot button
    pygame.draw.circle(surface, (120, 40, 40), MOBILE_SHOOT_BTN.center, 58)
    pygame.draw.circle(surface, RED, MOBILE_SHOOT_BTN.center, 58, 3)
    center_text(surface, FONT_SMALL, "FIRE", MOBILE_SHOOT_BTN.center, WHITE)

    # ability button
    ready = current_time >= ability_cooldown
    col = CYAN if ready else STONE
    pygame.draw.rect(surface, (20, 30, 40), MOBILE_ABILITY_BTN, border_radius=16)
    pygame.draw.rect(surface, col, MOBILE_ABILITY_BTN, 3, border_radius=16)
    center_text(surface, FONT_TINY, "ABILITY" if ready else "WAIT", MOBILE_ABILITY_BTN.center, WHITE)

    # pause
    pygame.draw.rect(surface, (30, 34, 42), MOBILE_PAUSE_BTN, border_radius=8)
    pygame.draw.rect(surface, GOLD, MOBILE_PAUSE_BTN, 2, border_radius=8)
    center_text(surface, FONT_TINY, "II", MOBILE_PAUSE_BTN.center, WHITE)


# =========================================================
# MAIN LOOP
# =========================================================
login_screen()
load_profile()
running = True

while running:
    clock.tick(FPS)
    current_time = pygame.time.get_ticks()
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Music: intro on menus, battle track while playing
    if intro_screen or character_screen or armory_screen or multiplayer_screen or friends_screen or leaderboard_screen:
        set_music("intro")
    elif game_over:
        set_music("intro")
    else:
        set_music("game")

    # Save the finished run to the leaderboard exactly once.
    if game_over and not run_recorded:
        run_recorded = True
        record_current_run()

    # =====================================================
    # EVENTS
    # =====================================================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            continue

        if event.type == pygame.KEYDOWN:
            # ADMIN SCREEN: available from ANY main-game state (intro, gameplay, pause,
            # upgrades, multiplayer view, and game-over).
            if event.key == pygame.K_F1 and is_admin:
                admin_panel()
                continue
            if event.key == pygame.K_F6 and is_admin:
                aimbot_enabled = not aimbot_enabled
                continue
            if event.key == pygame.K_F7 and is_admin:
                admin_title_visible = not admin_title_visible
                continue
            # Leaderboard overlay (sits on top of the intro menu)
            if leaderboard_screen:
                if event.key in (pygame.K_TAB, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d):
                    leaderboard_tab = 1 - leaderboard_tab
                elif event.key in (pygame.K_ESCAPE, pygame.K_b, pygame.K_RETURN):
                    leaderboard_screen = False
                continue

            if friends_screen:
                if event.key in (pygame.K_ESCAPE, pygame.K_b):
                    friends_screen = False
                    intro_screen = True
                    friend_message = ""
                elif event.key == pygame.K_TAB:
                    friends_tab = (friends_tab + 1) % 3
                elif friends_tab == 1:
                    if event.key == pygame.K_BACKSPACE:
                        friend_search = friend_search[:-1]
                    elif event.key == pygame.K_RETURN and friend_search.strip():
                        send_friend_request(friend_search.strip())
                    elif event.unicode and event.unicode.isprintable() and len(friend_search) < 20 and not event.unicode.isspace():
                        friend_search += event.unicode
                elif friends_tab == 2 and event.unicode.isdigit():
                    gift_amount = event.unicode
                continue

            # Intro controls
            if intro_screen:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    intro_screen = False
                    reset_game()
                elif event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_c:
                    character_screen = True
                    intro_screen = False
                elif event.key == pygame.K_m:
                    multiplayer_screen = True
                    intro_screen = False
                elif event.key in (pygame.K_l, pygame.K_TAB):
                    leaderboard_screen = True
                continue

            if multiplayer_screen:
                if mp_join_entry and not mp_connected:
                    if event.key == pygame.K_BACKSPACE:
                        mp_code = mp_code[:-1]
                    elif event.key == pygame.K_RETURN:
                        if len(mp_code) == 6: mp_join_room(mp_code); mp_join_entry = False
                        else: mp_status = "ENTER 6 CHARACTERS"
                    elif event.unicode.isalnum() and len(mp_code) < 6:
                        mp_code += event.unicode.upper()
                    continue
                if mp_is_host and mp_connected and not mp_join_entry:
                    if event.key == pygame.K_1:
                        mp_difficulty = "normal"; mp_team_lives = 6
                    elif event.key == pygame.K_2:
                        mp_difficulty = "hardcore"; mp_team_lives = 3
                    elif event.key == pygame.K_3:
                        mp_difficulty = "nightmare"; mp_team_lives = 1
                if event.key == pygame.K_ESCAPE:
                    mp_leave(); multiplayer_screen = False; intro_screen = True
                elif event.key == pygame.K_RETURN and mp_is_host and mp_connected:
                    mp_start_game()
                continue

            if character_screen:
                _n=len(class_list())
                if event.key in (pygame.K_LEFT, pygame.K_a): character_index=(character_index-1)%_n; skin_index=0
                elif event.key in (pygame.K_RIGHT, pygame.K_d): character_index=(character_index+1)%_n; skin_index=0
                elif event.key == pygame.K_q: skin_index-=1; clamp_skin_index()
                elif event.key == pygame.K_e: skin_index+=1; clamp_skin_index()
                elif event.key == pygame.K_s: buy_or_equip_class_skin()
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE): buy_or_equip_current()
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_b:
                    character_screen=False; intro_screen=True
                continue

            if armory_screen:
                if event.key in (pygame.K_LEFT, pygame.K_a): gun_skin_index=(gun_skin_index-1)%len(GUN_SKINS)
                elif event.key in (pygame.K_RIGHT, pygame.K_d): gun_skin_index=(gun_skin_index+1)%len(GUN_SKINS)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE): buy_or_equip_gun_skin()
                elif event.key in (pygame.K_ESCAPE, pygame.K_b):
                    armory_screen=False; intro_screen=True
                continue

            # Character power
            # Reaper Shinigami arts: Q / E / R (all three must work)
            if selected_character in ("Reaper", "Storm Sovereign", "Executor") and event.key in (pygame.K_q, pygame.K_e, pygame.K_r, pygame.K_f):
                use_admin_power({pygame.K_q: "q", pygame.K_e: "e", pygame.K_r: "r", pygame.K_f: "f"}[event.key], current_time)
                continue
            if selected_character == "Priest" and event.key in (pygame.K_q, pygame.K_e):
                use_priest_power({pygame.K_q: "q", pygame.K_e: "e"}[event.key], current_time)
                continue
            if event.key == pygame.K_q:
                activate_character_power(current_time)
                continue

            # Pause / resume
            if event.key in (pygame.K_p, pygame.K_ESCAPE):
                if not upgrade_screen and not game_over and not gun_choice_screen:
                    paused = not paused
                continue

            if paused:
                if event.key == pygame.K_q:
                    running = False
                continue

            # Upgrade screens
            if upgrade_screen:
                if gun_choice_screen:
                    if event.key == pygame.K_1 and not has_smg:
                        choose_special_gun("smg")
                        gun_choice_screen = False
                        upgrade_screen = False
                    elif event.key == pygame.K_2 and not has_rpg:
                        choose_special_gun("rpg")
                        gun_choice_screen = False
                        upgrade_screen = False
                else:
                    key_to_index = {
                        pygame.K_1: 0,
                        pygame.K_2: 1,
                        pygame.K_3: 2,
                    }
                    if event.key == pygame.K_r and upgrade_rerolls > 0:
                        if coins >= 20:
                            coins -= 20
                            upgrade_rerolls -= 1
                            upgrade_options = create_upgrade_options()
                            save_profile()
                        continue
                    if event.key in key_to_index:
                        index = key_to_index[event.key]
                        upgrade = upgrade_options[index]
                        if upgrade == "gun" and gun_level == 3 and not is_melee_class():
                            gun_choice_screen = True
                        else:
                            apply_upgrade(upgrade)
                            upgrade_screen = False
                continue

            if game_over:
                if event.key == pygame.K_r:
                    reset_game()
                elif event.key == pygame.K_q:
                    running = False
                continue

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if leaderboard_screen:
                if LB_TAB_ROUNDS.collidepoint(mouse_x,mouse_y): leaderboard_tab=0
                elif LB_TAB_KILLS.collidepoint(mouse_x,mouse_y): leaderboard_tab=1
                elif LB_BACK.collidepoint(mouse_x,mouse_y): leaderboard_screen=False
                continue

            if friends_screen:
                for idx in range(3):
                    if pygame.Rect(120 + idx * 160, 120, 140, 40).collidepoint(mouse_x, mouse_y):
                        friends_tab = idx
                if pygame.Rect(WIDTH // 2 - 120, 570, 240, 40).collidepoint(mouse_x, mouse_y):
                    friends_screen = False
                    intro_screen = True
                    friend_message = ""
                elif friends_tab == 0:
                    y = 210
                    fl = get_friends()
                    if not fl:
                        y += 30
                    for name in fl[:10]:
                        if pygame.Rect(WIDTH - 280, y - 4, 120, 32).collidepoint(mouse_x, mouse_y):
                            remove_friend(name)
                        y += 36
                    y += 38
                    for name in get_friend_requests()[:6]:
                        if pygame.Rect(WIDTH - 280, y - 4, 120, 32).collidepoint(mouse_x, mouse_y):
                            accept_friend_request(name)
                        y += 36
                elif friends_tab == 1:
                    y = 280
                    for name in search_players(friend_search):
                        if pygame.Rect(WIDTH // 2 + 60, y - 4, 140, 32).collidepoint(mouse_x, mouse_y):
                            send_friend_request(name)
                        y += 38
                elif friends_tab == 2:
                    y = 250
                    for name in get_friends()[:8]:
                        if pygame.Rect(WIDTH - 420, y - 4, 130, 32).collidepoint(mouse_x, mouse_y):
                            gift_to_friend(name, "gems", gift_amount)
                        elif pygame.Rect(WIDTH - 270, y - 4, 130, 32).collidepoint(mouse_x, mouse_y):
                            gift_to_friend(name, "coins", gift_amount)
                        y += 38
                continue

            if intro_screen:
                for _rect,_label in MENU_BUTTONS:
                    if not _rect.collidepoint(mouse_x,mouse_y):
                        continue
                    if _label=="PLAY": intro_screen=False; reset_game()
                    elif _label=="MULTIPLAYER": multiplayer_screen=True; intro_screen=False
                    elif _label=="CLASSES": character_screen=True; intro_screen=False; skin_index=0
                    elif _label=="ARMORY": armory_screen=True; intro_screen=False
                    elif _label=="LEADERBOARD": leaderboard_screen=True
                    elif _label=="FRIENDS":
                        friends_screen=True; intro_screen=False; friend_message=""
                    elif _label=="MODE":
                        control_mode = "mobile" if control_mode == "laptop" else "laptop"
                    elif _label=="QUIT": running=False
                    break
                continue

            if multiplayer_screen:
                if not mp_connected:
                    create=pygame.Rect(330,205,440,65); join=pygame.Rect(330,285,440,65); back=pygame.Rect(330,465,440,65)
                    if create.collidepoint(mouse_x,mouse_y): mp_create_room()
                    elif join.collidepoint(mouse_x,mouse_y):
                        # Simple code entry via keyboard handled below; clicking JOIN activates entry mode.
                        mp_status = "TYPE 6-CHAR ROOM CODE, THEN PRESS ENTER"
                        mp_join_entry = True
                    elif back.collidepoint(mouse_x,mouse_y): multiplayer_screen=False; intro_screen=True
                else:
                    if mp_is_host and pygame.Rect(330,400,440,65).collidepoint(mouse_x,mouse_y): mp_start_game()
                    elif pygame.Rect(330,520,440,55).collidepoint(mouse_x,mouse_y): mp_leave(); multiplayer_screen=False; intro_screen=True
                continue

            if character_screen:
                _n=len(class_list())
                if CHAR_LEFT_RECT.collidepoint(mouse_x,mouse_y): character_index=(character_index-1)%_n; skin_index=0
                elif CHAR_RIGHT_RECT.collidepoint(mouse_x,mouse_y): character_index=(character_index+1)%_n; skin_index=0
                elif SKIN_LEFT_RECT.collidepoint(mouse_x,mouse_y): skin_index-=1; clamp_skin_index()
                elif SKIN_RIGHT_RECT.collidepoint(mouse_x,mouse_y): skin_index+=1; clamp_skin_index()
                elif CHAR_BUY_RECT.collidepoint(mouse_x,mouse_y): buy_or_equip_current()
                elif SKIN_BUY_RECT.collidepoint(mouse_x,mouse_y): buy_or_equip_class_skin()
                elif CHAR_BACK_RECT.collidepoint(mouse_x,mouse_y): character_screen=False; intro_screen=True
                continue

            if armory_screen:
                if ARM_LEFT_RECT.collidepoint(mouse_x,mouse_y): gun_skin_index=(gun_skin_index-1)%len(GUN_SKINS)
                elif ARM_RIGHT_RECT.collidepoint(mouse_x,mouse_y): gun_skin_index=(gun_skin_index+1)%len(GUN_SKINS)
                elif ARM_BUY_RECT.collidepoint(mouse_x,mouse_y): buy_or_equip_gun_skin()
                elif ARM_BACK_RECT.collidepoint(mouse_x,mouse_y): armory_screen=False; intro_screen=True
                else:
                    for _i in range(len(GUN_SKINS)):
                        if pygame.Rect(695,192+_i*46,340,40).collidepoint(mouse_x,mouse_y):
                            gun_skin_index=_i; break
                continue

            if paused:
                resume_rect = pygame.Rect(WIDTH // 2 - 150, 290, 300, 70)
                quit_rect = pygame.Rect(WIDTH // 2 - 150, 390, 300, 70)
                if resume_rect.collidepoint(mouse_x, mouse_y):
                    paused = False
                elif quit_rect.collidepoint(mouse_x, mouse_y):
                    # QUIT -> Intro menu instead of closing the program.
                    paused = False
                    game_over = False
                    character_screen = False
                    intro_screen = True
                continue

            if game_over:
                restart_rect = pygame.Rect(WIDTH // 2 - 190, HEIGHT // 2 + 70, 380, 70)
                quit_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 155, 300, 65)
                if restart_rect.collidepoint(mouse_x, mouse_y):
                    reset_game()
                elif quit_rect.collidepoint(mouse_x, mouse_y):
                    # QUIT -> Intro menu instead of closing the program.
                    paused = False
                    game_over = False
                    character_screen = False
                    intro_screen = True
                continue

            if upgrade_screen:
                if gun_choice_screen:
                    choice_w, choice_h, gap = 300, 260, 50
                    total = choice_w * 2 + gap
                    start = (WIDTH - total) // 2
                    y = 300
                    smg_rect = pygame.Rect(start, y, choice_w, choice_h)
                    rpg_rect = pygame.Rect(start + choice_w + gap, y, choice_w, choice_h)
                    if smg_rect.collidepoint(mouse_x, mouse_y) and not has_smg:
                        choose_special_gun("smg")
                        gun_choice_screen = False
                        upgrade_screen = False
                    elif rpg_rect.collidepoint(mouse_x, mouse_y) and not has_rpg:
                        choose_special_gun("rpg")
                        gun_choice_screen = False
                        upgrade_screen = False
                else:
                    for i, rect in enumerate(upgrade_card_rects()):
                        if i < len(upgrade_options) and rect.collidepoint(mouse_x, mouse_y):
                            upgrade = upgrade_options[i]
                            if upgrade == "gun" and gun_level == 3 and not is_melee_class():
                                gun_choice_screen = True
                            else:
                                apply_upgrade(upgrade)
                                upgrade_screen = False
                            break

                    reroll_rect = pygame.Rect(WIDTH - 210, 635, 180, 40)
                    if reroll_rect.collidepoint(mouse_x, mouse_y) and upgrade_rerolls > 0 and coins >= 20:
                        coins -= 20
                        upgrade_rerolls -= 1
                        upgrade_options = create_upgrade_options()
                        save_profile()
                continue

            # Normal gameplay shooting
            if not game_over:
                if current_time - last_shot >= shoot_delay:
                    shoot()
                    last_shot = current_time

    # =====================================================
    # UPDATE GAME
    # =====================================================
    if not intro_screen and not character_screen and not armory_screen and not paused and not game_over and not upgrade_screen and not gun_choice_screen and not mp_player_dead:
        # -------------------------------------------------
        # MOVEMENT
        # -------------------------------------------------
        keys = pygame.key.get_pressed()
        move_x = 0
        move_y = 0
        mobile_shooting = False
        mobile_ability = False

        if control_mode == "mobile":
            md = pygame.mouse.get_pressed()[0]
            move_x, move_y, mobile_shooting, mobile_ability = update_mobile_input(
                (mouse_x, mouse_y), md
            )
            # pause via on-screen button
            if md and MOBILE_PAUSE_BTN.collidepoint(mouse_x, mouse_y):
                paused = True
            if mobile_ability:
                if selected_character in ("Reaper", "Storm Sovereign", "Executor"):
                    if admin_power_ready("q", current_time):
                        use_admin_power("q", current_time)
                    elif admin_power_ready("e", current_time):
                        use_admin_power("e", current_time)
                    elif admin_power_ready("f", current_time):
                        use_admin_power("f", current_time)
                    elif admin_power_ready("r", current_time):
                        use_admin_power("r", current_time)
                elif selected_character == "Priest":
                    if admin_power_ready("q", current_time):
                        use_priest_power("q", current_time)
                    elif admin_power_ready("e", current_time):
                        use_priest_power("e", current_time)
                else:
                    activate_character_power(current_time)
        else:
            if keys[pygame.K_w]:
                move_y -= 1
            if keys[pygame.K_s]:
                move_y += 1
            if keys[pygame.K_a]:
                move_x -= 1
            if keys[pygame.K_d]:
                move_x += 1

        if move_x or move_y:
            length = math.hypot(move_x, move_y)
            if length > 0:
                move_x /= length
                move_y /= length
            spd = player_speed
            # Transform speed ONLY while form is active — never in normal form
            if executor_until and current_time < executor_until:
                spd *= 2.0
            elif werewolf_until and current_time < werewolf_until:
                spd *= 2.1
            if current_time < frost_slow_until:
                spd *= 0.45
            player_x += move_x * spd
            player_y += move_y * spd

        player_x = max(30, min(WIDTH - 30, player_x))
        player_y = max(40, min(HEIGHT - 35, player_y))

        # Time Lord: history sample + slow rewind playback
        if selected_character == "Time Lord":
            if rewind_active:
                if current_time >= rewind_next:
                    if rewind_index < len(rewind_path):
                        snap = rewind_path[rewind_index]
                        player_x = float(snap[0])
                        player_y = float(snap[1])
                        # ease HP toward past value
                        health = min(max_health, health + max(0, (rewind_target_hp - health) * 0.12))
                        explosions.append({
                            "x": player_x, "y": player_y, "radius": 26 + rewind_index,
                            "time": current_time, "type": "spirit",
                        })
                        rewind_index += 1
                        rewind_next = current_time + 50  # ~50ms per step = slow rewind
                    else:
                        health = min(max_health, max(health, rewind_target_hp))
                        rewind_active = False
                        explosions.append({
                            "x": player_x, "y": player_y, "radius": 130,
                            "time": current_time, "type": "spirit",
                        })
            elif current_time - time_history_last >= 90:
                time_history.append((float(player_x), float(player_y), float(health), current_time))
                while len(time_history) > TIME_HISTORY_MAX:
                    time_history.pop(0)
                time_history_last = current_time

        is_shooting = mobile_shooting if control_mode == "mobile" else pygame.mouse.get_pressed()[0]
        # In mobile mode, also allow tapping empty space on the right half to shoot
        if control_mode == "mobile" and pygame.mouse.get_pressed()[0]:
            if mouse_x > WIDTH * 0.45 and not MOBILE_STICK_BASE.collidepoint(mouse_x, mouse_y) \
                    and not MOBILE_ABILITY_BTN.collidepoint(mouse_x, mouse_y) \
                    and not MOBILE_PAUSE_BTN.collidepoint(mouse_x, mouse_y):
                is_shooting = True
        mp_send_state(current_time, is_shooting)

        # -------------------------------------------------
        # SHOOTING (laptop: hold LMB | mobile: FIRE pad / right tap)
        # -------------------------------------------------
        if is_shooting:
            if current_time - last_shot >= shoot_delay:
                shoot()
                last_shot = current_time

        # -------------------------------------------------
        # ENTITY CAPS (anti-lag)
        # -------------------------------------------------
        _trim_list(bullets, MAX_BULLETS)
        _trim_list(orbit_bullets, MAX_ORBIT_BULLETS)
        _trim_list(explosions, MAX_EXPLOSIONS)
        _trim_list(poison_clouds, MAX_POISON_CLOUDS)
        _trim_list(moon_waves, MAX_MOON_WAVES)
        _trim_list(meds, MAX_MEDS)
        _trim_list(slashes, MAX_SLASHES)
        _trim_list(storm_bolts, 40)
        if len(zombies) > MAX_ZOMBIES:
            # Prefer removing oldest non-boss minions
            extras = len(zombies) - MAX_ZOMBIES
            remove_ids = []
            for z in zombies:
                if extras <= 0:
                    break
                if not z.get("boss_key"):
                    remove_ids.append(z)
                    extras -= 1
            for z in remove_ids:
                if z in zombies:
                    zombies.remove(z)

        # -------------------------------------------------
        # ORBIT ROTATION
        # -------------------------------------------------
        orbit_angle = (orbit_angle + orbit_speed) % math.tau

        # -------------------------------------------------
        # ORBIT AUTO GUNS
        # -------------------------------------------------
        orbit_auto_shoot(current_time)

        # -------------------------------------------------
        # MAIN BULLETS
        # -------------------------------------------------
        for bullet in bullets[:]:
            bullet["x"] += bullet["dx"]
            bullet["y"] += bullet["dy"]

            if "life" in bullet:
                bullet["life"] -= 1
                bullet["dx"] *= 0.94
                bullet["dy"] *= 0.94
                if bullet["life"] <= 0:
                    if bullet in bullets:
                        bullets.remove(bullet)
                    continue

            if (
                bullet["x"] < -50 or bullet["x"] > WIDTH + 50
                or bullet["y"] < -50 or bullet["y"] > HEIGHT + 50
            ):
                bullets.remove(bullet)

        # KATANA SLASH ARCS
        for slash in slashes[:]:
            if current_time - slash["time"] > 220:
                slashes.remove(slash)

        # -------------------------------------------------
        # RPG EXPLOSIONS
        # -------------------------------------------------
        for explosion in explosions[:]:
            if current_time - explosion["time"] >= 220:
                explosions.remove(explosion)

        # -------------------------------------------------
        # ORBIT BULLETS
        # -------------------------------------------------
        for bullet in orbit_bullets[:]:
            bullet["x"] += bullet["dx"]
            bullet["y"] += bullet["dy"]

            if (
                bullet["x"] < -50 or bullet["x"] > WIDTH + 50
                or bullet["y"] < -50 or bullet["y"] > HEIGHT + 50
            ):
                orbit_bullets.remove(bullet)

        # -------------------------------------------------
        # ZOMBIES
        # -------------------------------------------------
        magician_hidden = (selected_character == "Magician" and current_time < ability_duration_until)

        for zombie in zombies[:]:
            # Converted allies are controlled in update_crucifixes_and_allies
            if zombie.get("ally"):
                continue
            if current_time >= zombie.get("frozen_until", 0):
                if magician_hidden:
                    if shadow_clone:
                        target_x, target_y = shadow_clone["x"], shadow_clone["y"]
                        angle = math.atan2(target_y - zombie["y"], target_x - zombie["x"])
                        zombie["x"] += math.cos(angle) * zombie["speed"]
                        zombie["y"] += math.sin(angle) * zombie["speed"]
                else:
                    # Prefer fighting Priest allies / ninja clone / turret (like ninja bait)
                    allies = [a for a in zombies if a.get("ally") and a is not zombie]
                    if allies:
                        nearest_ally = min(allies, key=lambda a: math.hypot(a["x"] - zombie["x"], a["y"] - zombie["y"]))
                        target_x, target_y = nearest_ally["x"], nearest_ally["y"]
                    elif shadow_clone and shadow_clone["health"] > 0:
                        target_x, target_y = shadow_clone["x"], shadow_clone["y"]
                    elif turret and turret["health"] > 0:
                        target_x, target_y = turret["x"], turret["y"]
                    else:
                        target_x, target_y = player_x, player_y
                    angle = math.atan2(target_y - zombie["y"], target_x - zombie["x"])
                    zombie["x"] += math.cos(angle) * zombie["speed"]
                    zombie["y"] += math.sin(angle) * zombie["speed"]

            if not magician_hidden:
                distance = math.hypot(player_x - zombie["x"], player_y - zombie["y"])
                if distance < zombie["radius"] + 20:
                    damage_player(zombie["damage"], current_time)

            # Enemy zombies can damage Priest allies (duel like vs ninja clone)
            for ally in zombies[:]:
                if not ally.get("ally"):
                    continue
                ad = math.hypot(ally["x"] - zombie["x"], ally["y"] - zombie["y"])
                if ad < zombie["radius"] + ally.get("radius", 16) + 6:
                    if current_time - zombie.get("ally_attack_cd", 0) >= 350:
                        ally["health"] -= max(3, zombie.get("damage", 1) * 2)
                        ally["hit_flash_until"] = current_time + 80
                        zombie["ally_attack_cd"] = current_time
                        if ally["health"] <= 0 and ally in zombies:
                            zombies.remove(ally)

            # Shadow Clone has its own 5 HP and each zombie hit removes 1 HP.
            if shadow_clone and shadow_clone["health"] > 0:
                clone_distance = math.hypot(shadow_clone["x"] - zombie["x"], shadow_clone["y"] - zombie["y"])
                if clone_distance < zombie["radius"] + 18 and current_time - shadow_clone.get("hit_taken_timer", 0) >= 300:
                    shadow_clone["health"] -= 1
                    shadow_clone["hit_taken_timer"] = current_time
                    trigger_hit_effect(current_time, 2)
                    if shadow_clone["health"] <= 0:
                        shadow_clone = None

            # Each zombie contact deals exactly 1 turret HP damage.
            if turret and turret["health"] > 0:
                turret_distance = math.hypot(turret["x"] - zombie["x"], turret["y"] - zombie["y"])
                if turret_distance < zombie["radius"] + 24 and current_time - turret.get("hit_taken_timer", 0) >= 300:
                    turret["health"] -= 1
                    turret["hit_taken_timer"] = current_time
                    trigger_hit_effect(current_time, 2)
                    if turret["health"] <= 0:
                        turret = None

        # -------------------------------------------------
        # ORBIT WEAPON COLLISION
        # Automatic damage when knife/axe/katana touches zombie.
        # A short cooldown prevents one weapon from deleting HP
        # every single frame while overlapping.
        # -------------------------------------------------
        if orbit_type in ("knife", "axe", "katana"):
            for index, (ox, oy, _) in enumerate(orbit_positions()):
                for zombie in zombies[:]:
                    if zombie.get("ally"):
                        continue
                    distance = math.hypot(
                        ox - zombie["x"],
                        oy - zombie["y"]
                    )
                    # Keep the orbit weapon collision active. The knife is
                    # longer than its center point, so give it a useful hitbox.
                    if orbit_type == "knife":
                        hit_distance = zombie["radius"] + 27
                    elif orbit_type == "katana":
                        hit_distance = zombie["radius"] + 24
                    elif orbit_type == "axe":
                        hit_distance = zombie["radius"] + 28
                    else:
                        hit_distance = zombie["radius"] + 18

                    if distance < hit_distance:
                        key = (id(zombie), index)
                        last_hit = orbit_hit_cooldowns.get(key, 0)

                        if current_time - last_hit >= 250:
                            od = orbit_damage
                            if current_time < zombie.get("shield_until", 0):
                                od *= 0.35
                            zombie["health"] -= od
                            zombie["hit_flash_until"] = current_time + 75
                            orbit_hit_cooldowns[key] = current_time
                            trigger_hit_effect(current_time, 2)

                            if zombie["health"] <= 0:
                                kill_zombie(zombie)

        # -------------------------------------------------
        # MAIN BULLET COLLISION
        # -------------------------------------------------
        for bullet in bullets[:]:
            if bullet.get("enemy"):
                if math.hypot(bullet["x"] - player_x, bullet["y"] - player_y) < 28:
                    damage_player(bullet.get("enemy_dmg", 12), current_time)
                    if bullet in bullets:
                        bullets.remove(bullet)
                continue
            for zombie in zombies[:]:
                if zombie.get("ally"):
                    continue
                distance = math.hypot(
                    bullet["x"] - zombie["x"],
                    bullet["y"] - zombie["y"]
                )

                if distance < zombie["radius"] + bullet_size:
                    if bullet.get("explosive"):
                        radius = bullet["explosion_radius"]
                        explosions.append({
                            "x": bullet["x"],
                            "y": bullet["y"],
                            "radius": radius,
                            "time": current_time,
                        })
                        play_sfx("explode", 0.32)

                        # RPG splash damage hits every zombie in the blast.
                        for target in zombies[:]:
                            blast_distance = math.hypot(
                                bullet["x"] - target["x"],
                                bullet["y"] - target["y"]
                            )
                            if blast_distance <= radius + target["radius"]:
                                falloff = max(0.35, 1 - blast_distance / max(1, radius))
                                target["health"] -= bullet["damage"] * falloff
                                target["hit_flash_until"] = current_time + 75
                                trigger_hit_effect(current_time, 2)
                                if target["health"] <= 0:
                                    kill_zombie(target)
                    else:
                        dmg = bullet["damage"]
                        if current_time < zombie.get("shield_until", 0):
                            dmg *= 0.35
                        zombie["health"] -= dmg
                        zombie["hit_flash_until"] = current_time + 75
                        if random.random() < 0.35:
                            play_sfx("damage", 0.2)
                        chill = freeze_chance + (0.25 if selected_character == "Frozen" else 0.0)
                        if chill and random.random() < chill:
                            zombie["frozen_until"] = current_time + 1800
                        trigger_hit_effect(current_time, 2)

                        # SHRAPNEL ROUNDS: small burst around the impact.
                        if shrapnel:
                            burst_r = 46 + shrapnel * 22
                            explosions.append({"x": bullet["x"], "y": bullet["y"],
                                               "radius": burst_r, "time": current_time})
                            for other in zombies[:]:
                                if other is zombie:
                                    continue
                                bd = math.hypot(bullet["x"] - other["x"], bullet["y"] - other["y"])
                                if bd <= burst_r + other["radius"]:
                                    other["health"] -= bullet["damage"] * (0.22 + 0.12 * shrapnel)
                                    other["hit_flash_until"] = current_time + 75
                                    if other["health"] <= 0:
                                        kill_zombie(other)

                        if zombie["health"] <= 0:
                            kill_zombie(zombie)

                    # RAILGUN ROUNDS: keep flying through a few bodies.
                    hits = bullet.get("hits", 0) + 1
                    bullet["hits"] = hits
                    if bullet.get("explosive") or hits > bullet.get("pierce", 0):
                        if bullet in bullets:
                            bullets.remove(bullet)
                        break
                    continue

        # -------------------------------------------------
        # ORBIT AUTO-GUN BULLET COLLISION
        # -------------------------------------------------
        for bullet in orbit_bullets[:]:
            for zombie in zombies[:]:
                distance = math.hypot(
                    bullet["x"] - zombie["x"],
                    bullet["y"] - zombie["y"]
                )

                if distance < zombie["radius"] + 5:
                    zombie["health"] -= bullet["damage"]
                    zombie["hit_flash_until"] = current_time + 75
                    trigger_hit_effect(current_time, 2)

                    if bullet in orbit_bullets:
                        orbit_bullets.remove(bullet)

                    if zombie["health"] <= 0:
                        kill_zombie(zombie)
                    break

        # -------------------------------------------------
        # ENGINEER TURRET PROJECTILES
        # -------------------------------------------------
        for tb in turret_bullets[:]:
            tb["x"] += tb["dx"]
            tb["y"] += tb["dy"]
            tb["life"] -= 16
            hit = None
            for zombie in zombies[:]:
                if math.hypot(tb["x"] - zombie["x"], tb["y"] - zombie["y"]) < zombie["radius"] + 7:
                    hit = zombie
                    break
            if hit is not None:
                for target in zombies[:]:
                    d = math.hypot(tb["x"] - target["x"], tb["y"] - target["y"])
                    if d <= tb["splash"] + target["radius"]:
                        falloff = max(0.35, 1.0 - d / max(1, tb["splash"]))
                        target["health"] -= tb["damage"] * falloff
                        target["hit_flash_until"] = current_time + 90
                        if target["health"] <= 0:
                            kill_zombie(target)
                explosions.append({"x": tb["x"], "y": tb["y"], "radius": tb["splash"], "time": current_time, "type": "turret"})
                if tb in turret_bullets: turret_bullets.remove(tb)
            elif tb["life"] <= 0 or not (-40 < tb["x"] < WIDTH + 40 and -40 < tb["y"] < HEIGHT + 40):
                if tb in turret_bullets: turret_bullets.remove(tb)

        # -------------------------------------------------
        # MEDS
        # -------------------------------------------------
        for med in meds[:]:
            distance = math.hypot(
                player_x - med["x"],
                player_y - med["y"]
            )

            if distance < 30:
                # No healing during the Wave-100 boss gauntlet
                if not named_bosses_alive():
                    health = min(max_health, health + 25)
                add_coins(3)
                meds.remove(med)
                play_sfx("pickup", 0.25)

        # -------------------------------------------------
        # CHARACTER POWER UPDATE
        # -------------------------------------------------
        update_character_power(current_time)

        # -------------------------------------------------
        # LEVEL UP
        # -------------------------------------------------
        if xp >= xp_needed:
            xp -= xp_needed
            level += 1
            xp_needed = int(xp_needed * 1.25)
            upgrade_rerolls = 2
            upgrade_options = create_upgrade_options()
            upgrade_screen = True
            play_sfx("levelup", 0.35)

        # -------------------------------------------------
        # NEXT WAVE
        # -------------------------------------------------
        # Allies (Priest converts) must NOT block wave clear
        enemy_left = sum(1 for z in zombies if not z.get("ally"))
        if enemy_left == 0 and not upgrade_screen:
            # dismiss leftover allies so the field is clean for the next wave
            for z in zombies[:]:
                if z.get("ally") and z in zombies:
                    zombies.remove(z)
            wave += 1
            if mp_connected and mp_started and mp_player_dead and mp_team_lives > 0:
                mp_player_dead = False
                health = max_health
                player_x = WIDTH // 2
                player_y = HEIGHT // 2
            spawn_wave()

        # -------------------------------------------------
        # GAME OVER
        # -------------------------------------------------
        if health <= 0:
            health = 0
            if not (mp_connected and mp_started):
                game_over = True
            elif mp_team_lives <= 0:
                game_over = True

    # =====================================================
    # AIM / HELD GUN POSITION
    # =====================================================
    angle = math.atan2(mouse_y - player_y, mouse_x - player_x)
    gun_x = player_x + math.cos(angle) * 48
    gun_y = player_y + math.sin(angle) * 48

    # =====================================================
    # BACKGROUND
    # =====================================================
    draw_arena_bg(screen, current_time)

    # =====================================================
    # MEDS
    # =====================================================
    for med in meds:
        mx = int(med["x"])
        my = int(med["y"])
        pygame.draw.rect(screen, GREEN, (mx - 12, my - 12, 24, 24))
        pygame.draw.rect(screen, WHITE, (mx - 3, my - 9, 6, 18))
        pygame.draw.rect(screen, WHITE, (mx - 9, my - 3, 18, 6))

    # =====================================================
    # ZOMBIES — ENHANCED PIXEL CREATURES
    # =====================================================
    if _ZOMBIE_SHADOW is None:
        _ZOMBIE_SHADOW = pygame.Surface((72, 28), pygame.SRCALPHA)
        pygame.draw.ellipse(_ZOMBIE_SHADOW, (0, 0, 0, 90), _ZOMBIE_SHADOW.get_rect())
    _zcount = len(zombies)
    _fast_minions = _zcount > 28  # lag guard: simpler minion sprites when crowded
    for zombie in zombies:
        x = int(zombie["x"])
        y = int(zombie["y"])
        radius = int(zombie["radius"])
        ztype = zombie["type"]
        hit = current_time < zombie.get("hit_flash_until", 0)
        frozen = current_time < zombie.get("frozen_until", 0)
        is_named = bool(zombie.get("boss_key"))
        is_ally = bool(zombie.get("ally"))

        palette = {
            "normal": ((68, 180, 82), (35, 105, 45), (170, 245, 110)),
            "fast": ((215, 125, 55), (125, 60, 30), (255, 205, 95)),
            "tank": ((135, 78, 175), (70, 38, 105), (205, 135, 240)),
            "boss": ((220, 55, 70), (115, 20, 35), (255, 125, 135)),
        }
        if zombie.get("colors"):
            body_c, dark_c, eye_c = zombie["colors"]
        else:
            body_c, dark_c, eye_c = palette.get(ztype, palette["normal"])
        if frozen:
            body_c, dark_c, eye_c = CYAN, (40, 110, 150), WHITE
        if hit:
            body_c = dark_c = eye_c = WHITE
        if is_ally:
            body_c, dark_c, eye_c = (255, 230, 120), (180, 150, 40), (255, 255, 200)

        # Named bosses get fully unique sprites (not shared zombie body)
        if is_named:
            draw_named_boss(screen, zombie, x, y, radius, body_c, dark_c, eye_c, current_time, hit)
            continue

        # Fast minion path: body + head + eyes + HP (still looks like a zombie, not a circle)
        if _fast_minions and not is_named and ztype != "boss":
            screen.blit(_ZOMBIE_SHADOW, _ZOMBIE_SHADOW.get_rect(center=(x, y + radius // 2 + 10)))
            bw = max(14, int(radius * 1.4))
            bh = max(12, int(radius * 1.15))
            pygame.draw.rect(screen, dark_c, (x - bw // 2 - 1, y - bh // 4 - 1, bw + 2, bh + 2), border_radius=4)
            pygame.draw.rect(screen, body_c, (x - bw // 2, y - bh // 4, bw, bh), border_radius=3)
            hw = max(12, int(radius * 1.2))
            hh = max(10, int(radius * 1.0))
            pygame.draw.rect(screen, body_c, (x - hw // 2, y - radius - hh // 3, hw, hh), border_radius=3)
            es = max(3, radius // 5)
            pygame.draw.rect(screen, eye_c, (x - radius // 3, y - radius // 2, es, es))
            pygame.draw.rect(screen, eye_c, (x + radius // 6, y - radius // 2, es, es))
            if zombie["health"] < zombie["max_health"]:
                bar_w = max(18, radius * 2)
                pygame.draw.rect(screen, RED, (x - bar_w // 2, y - radius - 10, bar_w, 3))
                pygame.draw.rect(screen, GREEN, (x - bar_w // 2, y - radius - 10,
                    int(bar_w * max(0, zombie["health"] / max(1, zombie["max_health"]))), 3))
            continue

        bob = int(math.sin(current_time * 0.009 + zombie["x"] * 0.03) * 2)
        screen.blit(_ZOMBIE_SHADOW, _ZOMBIE_SHADOW.get_rect(center=(x, y + radius // 2 + 12)))

        # Arms first, giving the zombies a much stronger silhouette.
        arm_len = int(radius * (1.15 if ztype != "boss" else 1.3))
        arm_w = max(7, radius // 3)
        pygame.draw.line(screen, BLACK,
                         (x - radius // 2, y + bob),
                         (x - arm_len, y + radius // 2 + bob), arm_w + 4)
        pygame.draw.line(screen, body_c,
                         (x - radius // 2, y + bob),
                         (x - arm_len, y + radius // 2 + bob), arm_w)
        pygame.draw.line(screen, BLACK,
                         (x + radius // 2, y + bob),
                         (x + arm_len, y + radius // 2 + bob), arm_w + 4)
        pygame.draw.line(screen, body_c,
                         (x + radius // 2, y + bob),
                         (x + arm_len, y + radius // 2 + bob), arm_w)

        # Hands / claws
        for hx, hy in (
            (x - arm_len, y + radius // 2 + bob),
            (x + arm_len, y + radius // 2 + bob),
        ):
            pygame.draw.rect(screen, BLACK, (hx - 7, hy - 6, 14, 12))
            pygame.draw.rect(screen, dark_c, (hx - 5, hy - 4, 10, 8))
            for claw in (-4, 0, 4):
                pygame.draw.line(screen, eye_c, (hx + claw, hy + 3),
                                 (hx + claw - 2, hy + 9), 2)

        # Body
        body_w = int(radius * 1.55)
        body_h = int(radius * 1.35)
        body_rect = pygame.Rect(x - body_w // 2, y - radius // 4 + bob,
                                body_w, body_h)
        pygame.draw.rect(screen, BLACK, body_rect.inflate(6, 6), border_radius=7)
        pygame.draw.rect(screen, dark_c, body_rect, border_radius=6)
        pygame.draw.rect(screen, body_c,
                         (body_rect.x + 4, body_rect.y + 4,
                          body_rect.w - 8, body_rect.h - 8), border_radius=4)

        # Head
        head_w = int(radius * 1.45)
        head_h = int(radius * 1.25)
        head = pygame.Rect(x - head_w // 2, y - radius - radius // 3 + bob,
                           head_w, head_h)
        pygame.draw.rect(screen, BLACK, head.inflate(6, 6), border_radius=5)
        pygame.draw.rect(screen, body_c, head, border_radius=4)
        pygame.draw.rect(screen, dark_c,
                         (head.x + 4, head.y + 4, head.w - 8, head.h // 3),
                         border_radius=2)

        # Ragged hair / ears
        pygame.draw.rect(screen, dark_c, (head.x - 4, head.y + 3, 7, head.h - 3))
        pygame.draw.rect(screen, dark_c, (head.right - 3, head.y + 5, 7, head.h - 5))

        # Eyes
        eye_y = head.centery - 1
        eye_size = max(4, radius // 5)
        pygame.draw.rect(screen, BLACK,
                         (x - radius // 2 - 2, eye_y - eye_size // 2,
                          eye_size + 3, eye_size + 3))
        pygame.draw.rect(screen, BLACK,
                         (x + radius // 2 - eye_size + 2, eye_y - eye_size // 2,
                          eye_size + 3, eye_size + 3))
        pygame.draw.rect(screen, eye_c,
                         (x - radius // 2, eye_y, eye_size, eye_size))
        pygame.draw.rect(screen, eye_c,
                         (x + radius // 2 - eye_size, eye_y, eye_size, eye_size))

        # Mouth + teeth
        mouth = pygame.Rect(x - max(7, radius // 3), head.bottom - max(12, radius // 3),
                            max(14, radius * 2 // 3), max(7, radius // 4))
        pygame.draw.rect(screen, BLACK, mouth)
        for tooth_x in range(mouth.x + 3, mouth.right - 2, max(5, radius // 6)):
            pygame.draw.rect(screen, WHITE, (tooth_x, mouth.y + 1, 3, 4))

        # Type-specific scars / armor
        if ztype == "fast":
            pygame.draw.line(screen, WHITE, (x - radius, y - radius),
                             (x - radius // 2, y - radius // 2), 2)
            pygame.draw.line(screen, WHITE, (x + radius, y - radius),
                             (x + radius // 2, y - radius // 2), 2)
        elif ztype == "tank":
            pygame.draw.rect(screen, STONE, (x - radius, y - 5, radius * 2, 12), border_radius=3)
            pygame.draw.rect(screen, STONE_LIGHT, (x - radius + 5, y - 2, radius * 2 - 10, 5))
        elif ztype == "boss":
            pygame.draw.rect(screen, GOLD, (x - radius - 5, y - radius - 12,
                                             radius * 2 + 10, 6))
            pygame.draw.rect(screen, RED, (x - radius - 5, y - radius - 12,
                                             int((radius * 2 + 10) * max(
                                                 0, zombie["health"] / zombie["max_health"]
                                             )), 6))
            if zombie.get("boss_name"):
                nm = FONT_TINY.render(zombie["boss_name"], True, GOLD)
                screen.blit(nm, (x - nm.get_width() // 2, y - radius - 32))
            # Unique boss accessories / gear
            bk = zombie.get("boss_key")
            if bk == "horde_king":
                # Golden crown + jeweled pauldron cape + bone necklace
                pygame.draw.polygon(screen, GOLD, [
                    (x - 20, y - radius - 4), (x - 14, y - radius - 20), (x - 6, y - radius - 8),
                    (x, y - radius - 26), (x + 6, y - radius - 8), (x + 14, y - radius - 20),
                    (x + 20, y - radius - 4)])
                pygame.draw.polygon(screen, (255, 240, 120), [
                    (x - 16, y - radius - 4), (x, y - radius - 18), (x + 16, y - radius - 4)])
                pygame.draw.circle(screen, RED, (x, y - radius - 22), 4)
                # cape
                pygame.draw.polygon(screen, (160, 40, 20), [
                    (x - radius + 4, y), (x - radius - 18, y + radius + 10),
                    (x + radius + 18, y + radius + 10), (x + radius - 4, y)])
                # necklace
                for i in range(-2, 3):
                    pygame.draw.circle(screen, (255, 220, 80), (x + i * 8, y + 10), 3)

            elif bk == "plague_matriarch":
                # Gas-mask, toxic vials belt, dripping spores
                pygame.draw.rect(screen, (40, 70, 40), (x - 16, y - radius // 2 - 4, 32, 18), border_radius=4)
                pygame.draw.circle(screen, (120, 255, 80), (x - 7, y - radius // 2 + 4), 5)
                pygame.draw.circle(screen, (120, 255, 80), (x + 7, y - radius // 2 + 4), 5)
                pygame.draw.rect(screen, (60, 90, 50), (x - 4, y - radius // 2 + 10, 8, 10))
                # vial belt
                for i in range(-2, 3):
                    pygame.draw.rect(screen, (30, 80, 30), (x + i * 12 - 4, y + radius // 2, 8, 14), border_radius=2)
                    pygame.draw.rect(screen, (100, 255, 90), (x + i * 12 - 2, y + radius // 2 + 3, 4, 8))
                # floating spores
                for i in range(5):
                    ang = current_time * 0.004 + i * 1.2
                    sx = int(x + math.cos(ang) * (radius + 14))
                    sy = int(y + math.sin(ang) * (radius + 10))
                    pygame.draw.circle(screen, (150, 255, 100), (sx, sy), 3 + (i % 2))

            elif bk == "cyber_colossus":
                # Antenna, chest reactor, arm cannons, shield ring
                pygame.draw.line(screen, METAL, (x - 8, y - radius), (x - 8, y - radius - 22), 3)
                pygame.draw.line(screen, METAL, (x + 8, y - radius), (x + 8, y - radius - 18), 3)
                pygame.draw.circle(screen, CYAN, (x - 8, y - radius - 24), 4)
                pygame.draw.circle(screen, (0, 200, 255), (x + 8, y - radius - 20), 3)
                # chest core
                pygame.draw.circle(screen, (20, 40, 60), (x, y + 2), 14)
                pygame.draw.circle(screen, CYAN, (x, y + 2), 10)
                pygame.draw.circle(screen, WHITE, (x, y + 2), 4)
                # arm cannons
                for side in (-1, 1):
                    pygame.draw.rect(screen, (50, 70, 90), (x + side * (radius + 2) - 6, y - 8, 12, 28), border_radius=3)
                    pygame.draw.rect(screen, CYAN, (x + side * (radius + 2) - 3, y - 4, 6, 10))
                if current_time < zombie.get("shield_until", 0):
                    pygame.draw.circle(screen, CYAN, (x, y), radius + 14, 3)
                    pygame.draw.circle(screen, (100, 220, 255), (x, y), radius + 18, 1)

            elif bk == "chrono_wraith":
                # Hourglass amulet, clock halo, afterimage trails
                pygame.draw.circle(screen, (180, 100, 255), (x, y), radius + 12, 2)
                for i in range(8):
                    a = current_time * 0.003 + i * (math.tau / 8)
                    pygame.draw.circle(screen, (255, 230, 120),
                                       (int(x + math.cos(a) * (radius + 12)),
                                        int(y + math.sin(a) * (radius + 12))), 3)
                # hourglass
                pygame.draw.polygon(screen, (255, 220, 100), [
                    (x - 8, y - 6), (x + 8, y - 6), (x, y + 4)])
                pygame.draw.polygon(screen, (255, 200, 80), [
                    (x - 8, y + 14), (x + 8, y + 14), (x, y + 4)])
                # ghost trail dots
                for t in range(1, 4):
                    pygame.draw.circle(screen, (160, 80, 220), (x - t * 12, y), max(2, 8 - t * 2), 1)

            elif bk == "blood_moon_reaper":
                # Hood, dual katanas, blood moon halo
                pygame.draw.polygon(screen, (40, 5, 12), [
                    (x - 26, y - 2), (x - 22, y - radius - 8), (x, y - radius - 30),
                    (x + 22, y - radius - 8), (x + 26, y - 2)])
                pygame.draw.circle(screen, (255, 40, 60), (x, y - radius - 36), 10)
                pygame.draw.circle(screen, (120, 10, 20), (x, y - radius - 36), 6)
                # dual blades
                pygame.draw.line(screen, (220, 220, 230), (x - radius - 8, y + 8), (x - radius - 28, y - 28), 4)
                pygame.draw.line(screen, (255, 80, 100), (x - radius - 8, y + 8), (x - radius - 28, y - 28), 2)
                pygame.draw.line(screen, (220, 220, 230), (x + radius + 8, y + 8), (x + radius + 28, y - 28), 4)
                pygame.draw.line(screen, (255, 80, 100), (x + radius + 8, y + 8), (x + radius + 28, y - 28), 2)
                # sash
                pygame.draw.rect(screen, (180, 20, 40), (x - radius + 4, y + 8, radius * 2 - 8, 6))

            elif bk == "swarm_heart":
                # Beating core, orbiting minion orbs, vein lines
                pulse = 1.0 + 0.15 * math.sin(current_time * 0.01)
                core_r = int((radius // 3) * pulse)
                pygame.draw.circle(screen, (120, 0, 50), (x, y), core_r + 6)
                pygame.draw.circle(screen, (255, 40, 140), (x, y), core_r)
                pygame.draw.circle(screen, (255, 200, 230), (x, y), max(3, core_r // 2))
                for i in range(8):
                    a = current_time * 0.005 + i * (math.tau / 8)
                    ox = int(x + math.cos(a) * (radius + 10))
                    oy = int(y + math.sin(a) * (radius + 10))
                    pygame.draw.circle(screen, (255, 100, 180), (ox, oy), 5)
                    pygame.draw.line(screen, (180, 40, 100), (x, y), (ox, oy), 1)

            elif bk == "mirror_twin":
                # Mirror mask, chrome pauldrons, reflection shards
                pygame.draw.ellipse(screen, (200, 220, 255), (x - 18, y - radius - 2, 36, 28))
                pygame.draw.ellipse(screen, (240, 250, 255), (x - 14, y - radius + 2, 28, 20))
                pygame.draw.line(screen, (80, 100, 140), (x, y - radius + 2), (x, y - radius + 20), 2)
                # pauldrons
                pygame.draw.circle(screen, (180, 200, 230), (x - radius, y), 12)
                pygame.draw.circle(screen, (180, 200, 230), (x + radius, y), 12)
                pygame.draw.circle(screen, WHITE, (x - radius, y), 12, 2)
                pygame.draw.circle(screen, WHITE, (x + radius, y), 12, 2)
                # shards
                for i in range(4):
                    a = current_time * 0.004 + i * 1.5
                    sx = int(x + math.cos(a) * (radius + 16))
                    sy = int(y + math.sin(a) * (radius + 16))
                    pygame.draw.polygon(screen, (220, 235, 255), [
                        (sx, sy - 6), (sx + 5, sy), (sx, sy + 6), (sx - 5, sy)])

            elif bk == "frost_titan":
                # Ice crown, frozen armor plates, crystal arms
                pygame.draw.polygon(screen, (200, 240, 255), [
                    (x - 22, y - radius - 2), (x - 14, y - radius - 22), (x - 6, y - radius - 8),
                    (x, y - radius - 28), (x + 6, y - radius - 8), (x + 14, y - radius - 22),
                    (x + 22, y - radius - 2)])
                pygame.draw.polygon(screen, WHITE, [
                    (x - 10, y - radius - 2), (x, y - radius - 16), (x + 10, y - radius - 2)])
                # chest ice plate
                pygame.draw.rect(screen, (160, 220, 255), (x - 16, y - 4, 32, 22), border_radius=3)
                pygame.draw.rect(screen, (220, 250, 255), (x - 12, y, 24, 8))
                # crystal arms
                for side in (-1, 1):
                    pygame.draw.polygon(screen, (150, 220, 255), [
                        (x + side * radius, y - 6),
                        (x + side * (radius + 22), y - 18),
                        (x + side * (radius + 18), y + 10)])
                # snow particles
                for i in range(4):
                    pygame.draw.circle(screen, WHITE,
                                       (x + int(math.sin(current_time * 0.003 + i) * radius),
                                        y - radius - 10 - (current_time // 40 + i * 13) % 30), 2)

            elif bk == "necro_conductor":
                # Staff with skull, bone shoulder spikes, purple cloak, rune ring
                pygame.draw.line(screen, (100, 70, 40), (x + radius // 2, y + 10), (x + radius // 2, y - radius - 36), 5)
                pygame.draw.circle(screen, (240, 230, 210), (x + radius // 2, y - radius - 40), 10)
                pygame.draw.circle(screen, (20, 10, 30), (x + radius // 2 - 3, y - radius - 42), 2)
                pygame.draw.circle(screen, (20, 10, 30), (x + radius // 2 + 3, y - radius - 42), 2)
                pygame.draw.circle(screen, (255, 180, 40), (x + radius // 2, y - radius - 52), 5)
                # cloak
                pygame.draw.polygon(screen, (60, 20, 100), [
                    (x - radius + 6, y - 4), (x - radius - 14, y + radius + 12),
                    (x + radius + 14, y + radius + 12), (x + radius - 6, y - 4)])
                # bone spikes
                for side in (-1, 1):
                    pygame.draw.polygon(screen, (230, 220, 200), [
                        (x + side * 10, y - radius // 2),
                        (x + side * (radius + 8), y - radius // 2 - 12),
                        (x + side * 14, y - radius // 2 + 10)])
                # rune ring
                pygame.draw.circle(screen, (180, 100, 255), (x, y), radius + 10, 2)
                for i in range(6):
                    a = current_time * 0.004 + i * (math.tau / 6)
                    pygame.draw.circle(screen, (255, 200, 80),
                                       (int(x + math.cos(a) * (radius + 10)),
                                        int(y + math.sin(a) * (radius + 10))), 3)

        # Health bar for every zombie; boss gets a larger one.
        bar_w = max(34, radius * 2)
        bar_h = 5
        hp = max(0.0, min(1.0, zombie["health"] / max(1, zombie["max_health"])))
        bx = x - bar_w // 2
        by = head.top - 12
        pygame.draw.rect(screen, BLACK, (bx - 2, by - 2, bar_w + 4, bar_h + 4))
        pygame.draw.rect(screen, RED, (bx, by, bar_w, bar_h))
        pygame.draw.rect(screen, GREEN, (bx, by, int(bar_w * hp), bar_h))
        if is_ally:
            pygame.draw.circle(screen, (255, 230, 120), (x, y), radius + 8, 2)
            tag = FONT_TINY.render("ALLY", True, (255, 230, 120))
            screen.blit(tag, (x - tag.get_width() // 2, by - 16))

    # =====================================================
    # BULLETS
    # =====================================================
    # KATANA SLASH ARCS
    for slash in slashes:
        age = current_time - slash["time"]
        p = min(1.0, max(0.0, age / 220.0))
        fade = (1.0 - p) ** 1.5
        if fade <= 0.02:
            continue
        elem = slash.get("element", "normal")
        if elem == "fire":
            acc = (255, 140, 40)
        elif elem == "haki":
            acc = (160, 100, 255)
        elif elem == "bankai":
            acc = (255, 50, 40)
        elif elem == "claw":
            acc = slash.get("color", (255, 70, 40))
        else:
            acc = _cmix(gun_palette()["accent"], (255, 255, 255), 0.22)
        reach = slash["reach"]
        size = int(reach * 2 + 40)
        arc_s = pygame.Surface((size, size), pygame.SRCALPHA)
        cc = size // 2
        # the blade sweeps from one edge of the arc to the other
        sweep = slash["arc"] * 2.0
        lead = slash["angle"] - slash["arc"] + sweep * min(1.0, p * 1.6)
        steps = 30
        for i in range(steps):
            a = lead - sweep * 0.55 * (i / steps)
            alpha = int(255 * fade * (1.0 - i / steps) ** 1.2)
            if alpha <= 2:
                continue
            w = max(3, int(13 * (1.0 - i / steps)))
            inner = reach * 0.34
            pygame.draw.line(arc_s, (*acc, alpha),
                             (cc + math.cos(a) * inner, cc + math.sin(a) * inner),
                             (cc + math.cos(a) * reach, cc + math.sin(a) * reach), w)
        # crescent band riding the outer edge so the sweep reads instantly
        band = max(3, int(7 * fade) + 3)
        pygame.draw.arc(arc_s, (*acc, int(230 * fade)),
                        (cc - reach, cc - reach, reach * 2, reach * 2),
                        -lead, -lead + sweep * 0.55, band)
        pygame.draw.arc(arc_s, (255, 255, 255, int(190 * fade)),
                        (cc - reach * 0.97, cc - reach * 0.97, reach * 1.94, reach * 1.94),
                        -lead, -lead + sweep * 0.4, max(2, band - 2))
        # bright leading edge
        pygame.draw.line(arc_s, (255, 255, 255, int(255 * fade)),
                         (cc + math.cos(lead) * reach * 0.34, cc + math.sin(lead) * reach * 0.34),
                         (cc + math.cos(lead) * reach, cc + math.sin(lead) * reach), 4)
        if slash.get("critical"):
            pygame.draw.arc(arc_s, (255, 90, 80, int(150 * fade)),
                            (cc - reach, cc - reach, reach * 2, reach * 2),
                            -slash["angle"] - slash["arc"], -slash["angle"] + slash["arc"], 3)
        screen.blit(arc_s, arc_s.get_rect(center=(int(slash["x"]), int(slash["y"]))))

    if moon_waves:
        draw_moon_waves(screen, current_time)
    if bankai_until and current_time < bankai_until:
        draw_bankai_overlay(screen, current_time)
    if storm_bolts or (storm_domain_until and pygame.time.get_ticks() < storm_domain_until):
        draw_storm_effects(screen, current_time)

    for bullet in bullets:
        bx, by = int(bullet["x"]), int(bullet["y"])
        kind = bullet.get("kind", "normal")
        if kind == "flame":
            life = max(0, bullet.get("life", 0))
            p = 1.0 - life / 18.0
            r = int(7 + 15 * p)
            fl = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            cc = fl.get_width() // 2
            pygame.draw.circle(fl, (200, 60, 20, max(0, int(120 * (1 - p)))), (cc, cc), r)
            pygame.draw.circle(fl, (255, 150, 40, max(0, int(170 * (1 - p)))), (cc, cc), int(r * 0.68))
            pygame.draw.circle(fl, (255, 236, 170, max(0, int(210 * (1 - p)))), (cc, cc), max(2, int(r * 0.34)))
            screen.blit(fl, fl.get_rect(center=(bx, by)))
        elif kind == "plasma":
            pl = pygame.Surface((44, 44), pygame.SRCALPHA)
            for i in range(8, 0, -1):
                pygame.draw.circle(pl, (90, 220, 255, int(26 * (i / 8.0) ** 2)), (22, 22), i * 3)
            pygame.draw.circle(pl, (190, 245, 255), (22, 22), max(3, bullet_size))
            pygame.draw.circle(pl, WHITE, (22, 22), max(2, bullet_size - 2))
            screen.blit(pl, pl.get_rect(center=(bx, by)))
        elif bullet.get("explosive"):
            # Pixel rocket.
            pygame.draw.rect(screen, BLACK, (bx - 7, by - 4, 14, 8))
            pygame.draw.rect(screen, RED, (bx - 5, by - 3, 10, 6))
            pygame.draw.rect(screen, GOLD, (bx - 9, by - 2, 4, 4))
        else:
            pygame.draw.rect(
                screen,
                BULLET_COLOR,
                (bx - bullet_size, by - bullet_size, bullet_size * 2, bullet_size * 2),
            )

    for explosion in explosions:
        age = current_time - explosion["time"]
        progress = min(1.0, age / 260.0)
        radius = max(4, int(explosion["radius"] * progress))
        if explosion.get("type") == "poison":
            pygame.draw.circle(screen, PURPLE, (int(explosion["x"]), int(explosion["y"])), radius, 5)
            pygame.draw.circle(screen, CYAN, (int(explosion["x"]), int(explosion["y"])), max(3, radius // 2), 3)
        elif explosion.get("type") == "spirit":
            cx, cy = int(explosion["x"]), int(explosion["y"])
            acc = _cmix(gun_palette()["accent"], (255, 255, 255), 0.4)
            fade = 1.0 - progress
            ring = pygame.Surface((radius * 2 + 40, radius * 2 + 40), pygame.SRCALPHA)
            cc = ring.get_width() // 2
            for i in range(6, 0, -1):
                pygame.draw.circle(ring, (*acc, int(40 * fade * i / 6)), (cc, cc), int(radius * i / 6), max(2, 8 - i))
            pygame.draw.circle(ring, (255, 255, 255, int(180 * fade)), (cc, cc), max(8, radius // 3), 3)
            screen.blit(ring, ring.get_rect(center=(cx, cy)))
        else:
            pygame.draw.circle(screen, GOLD, (int(explosion["x"]), int(explosion["y"])), radius, 4)
            pygame.draw.circle(screen, RED, (int(explosion["x"]), int(explosion["y"])), max(3, radius // 2), 3)

    for bullet in orbit_bullets:
        pygame.draw.rect(
            screen,
            CYAN,
            (int(bullet["x"]) - 4, int(bullet["y"]) - 4, 8, 8)
        )

    # =====================================================
    # ORBIT WEAPONS
    # =====================================================
    for ox, oy, orbit_a in orbit_positions():
        draw_orbit_weapon(screen, ox, oy, orbit_a)

    # =====================================================
    # PLAYER + HELD GUN
    # =====================================================
    draw_character_power_effects(screen, current_time)
    if not (selected_character == "Magician" and current_time < ability_duration_until):
        draw_player(screen, player_x, player_y)
    draw_player_name(screen)
    draw_aimbot_indicator(screen)
    draw_held_gun(screen, gun_x, gun_y, angle)
    if not intro_screen and not character_screen and not armory_screen and not multiplayer_screen:
        draw_mobile_controls(screen, current_time)
    if is_admin:
        admin_lines = [
            ADMIN_TAG + "  " + ADMIN_DISPLAY_NAME if admin_title_visible else "TITLE: OFF",
            "F1 = ADMIN  •  F7 = TITLE " + ("ON" if admin_title_visible else "OFF"),
            "F6 = AIMBOT " + ("ON" if aimbot_enabled else "OFF"),
        ]
        for i, txt in enumerate(admin_lines):
            status = FONT_TINY.render(txt, True, GOLD if i == 0 else CYAN)
            screen.blit(status, (WIDTH - status.get_width() - 20, HEIGHT - 70 + i * 22))

    # =====================================================
    # UI
    # =====================================================
    pygame.draw.rect(screen, (55, 55, 55), (20, 20, 300, 28))
    pygame.draw.rect(
        screen, HEALTH_COLOR,
        (20, 20, int(300 * health / max_health), 28)
    )
    health_text = FONT_SMALL.render(
        f"HP {int(health)} / {max_health}", True, WHITE
    )
    screen.blit(health_text, (25, 22))

    pygame.draw.rect(screen, (50, 50, 60), (20, 58, 300, 16))
    pygame.draw.rect(
        screen, XP_COLOR,
        (20, 58, int(300 * xp / xp_needed), 16)
    )

    level_text = FONT_SMALL.render(f"LEVEL {level}", True, WHITE)
    screen.blit(level_text, (330, 53))

    gun_text = FONT_SMALL.render(
        f"GUN LV.{gun_level}: {gun_name()}", True, WHITE
    )
    screen.blit(gun_text, (20, 90))
    aim_text = FONT_TINY.render(
        ("AIMBOT LOCK: ON" if aimbot_enabled else ("AIM ASSIST: ON" if AIM_ASSIST else "AIM ASSIST: OFF")),
        True, RED if aimbot_enabled else (CYAN if AIM_ASSIST else STONE_LIGHT)
    )
    screen.blit(aim_text, (20, 142))
    combat_text = FONT_TINY.render(
        f"CRIT {int(crit_chance*100)}%  •  ARMOR {int(damage_reduction*100)}%",
        True, GOLD
    )
    screen.blit(combat_text, (20, 165))

    orbit_text = FONT_SMALL.render(
        f"ORBIT: {orbit_name()}", True, CYAN
    )
    screen.blit(orbit_text, (20, 116))

    wave_text = FONT.render(f"WAVE {wave}", True, WHITE)
    screen.blit(
        wave_text,
        (WIDTH - wave_text.get_width() - 25, 20)
    )
    if wave == 100:
        ban = FONT_SMALL.render("ALL 9 BOSSES — ENDGAME GAUNTLET", True, RED)
        screen.blit(ban, (WIDTH - ban.get_width() - 25, 48))
    if wave == 1000:
        ban = FONT_SMALL.render("AntonXD — WAVE 1000 BOSS", True, (255, 80, 60))
        screen.blit(ban, (WIDTH - ban.get_width() - 25, 48))

    score_text = FONT_SMALL.render(f"SCORE: {score}", True, WHITE)
    screen.blit(
        score_text,
        (WIDTH - score_text.get_width() - 25, 58)
    )
    
    kills_text = FONT_SMALL.render(f"KILLS: {kills}", True, GOLD)
    screen.blit(kills_text, (WIDTH - kills_text.get_width() - 25, 84))

    pause_hint = FONT_SMALL.render("P = PAUSE", True, WHITE)
    screen.blit(pause_hint, (WIDTH - pause_hint.get_width() - 25, 112))

    power_text = ""
    power_ready = False
    if selected_character == "Reaper" and werewolf_until and pygame.time.get_ticks() < werewolf_until:
        left_w = (werewolf_until - pygame.time.get_ticks()) / 1000.0
        ww = FONT_SMALL.render("WEREWOLF FORM  %.1fs" % left_w, True, (255, 120, 80))
        screen.blit(ww, (WIDTH // 2 - ww.get_width() // 2, 100))
    if selected_character == "Executor" and executor_until and pygame.time.get_ticks() < executor_until:
        left_e = (executor_until - pygame.time.get_ticks()) / 1000.0
        ew = FONT_SMALL.render("OVERLORD FORM  %.1fs" % left_e, True, (255, 210, 60))
        screen.blit(ew, (WIDTH // 2 - ew.get_width() // 2, 100))
    if selected_character in ("Reaper", "Storm Sovereign", "Executor", "Priest"):
        if selected_character == "Reaper" and werewolf_until and pygame.time.get_ticks() < werewolf_until:
            power_list = WEREWOLF_POWERS
        elif selected_character == "Reaper":
            power_list = ADMIN_POWERS
        elif selected_character == "Executor":
            power_list = EXECUTOR_POWERS
        elif selected_character == "Priest":
            power_list = PRIEST_POWERS
        else:
            power_list = STORM_POWERS
        for i, p in enumerate(power_list):
            left = admin_power_cd.get(p["key"], 0) - current_time
            if p["key"] == "r" and bankai_until and current_time < bankai_until:
                txt = "R BANKAI ACTIVE %.1fs" % ((bankai_until - current_time) / 1000.0)
                col = GOLD
            elif left <= 0:
                txt = "%s = %s" % (p["key"].upper(), p["name"])
                col = CYAN
            else:
                txt = "%s %s: %ds" % (p["key"].upper(), p["name"], left // 1000 + 1)
                col = STONE_LIGHT
            surf = FONT_SMALL.render(txt, True, col)
            screen.blit(surf, (WIDTH - surf.get_width() - 25, 140 + i * 26))
        power_ready = False
        power_text = None
    else:
        power_ready = current_time >= ability_cooldown
    if power_text is None:
        pass
    elif selected_character == "Engineer":
        if turret:
            power_text = f"Q TURRET ACTIVE  •  {max(0, (ability_cooldown-current_time)//1000 + 1)}s"
        else:
            power_text = "Q = PLACE TURRET" if power_ready else f"Q TURRET COOLDOWN: {max(0, (ability_cooldown-current_time)//1000 + 1)}s"
    else:
        power_text = "Q = POWER READY" if power_ready else f"Q POWER: {max(0, (ability_cooldown-current_time)//1000 + 1)}s"
    if power_text is not None:
        power_color = CYAN if power_ready else STONE_LIGHT
        power_surface = FONT_SMALL.render(power_text, True, power_color)
        screen.blit(power_surface, (WIDTH - power_surface.get_width() - 25, 140))

    # =====================================================
    # UPGRADE MENU
    # =====================================================
    if upgrade_screen:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 6, 12, 235))
        screen.blit(overlay, (0, 0))

        title = FONT_BIG.render("LEVEL UP!", True, GOLD)
        screen.blit(
            title,
            (WIDTH // 2 - title.get_width() // 2, 65)
        )

        subtitle = FONT_SMALL.render(
            f"CHOOSE YOUR UPGRADE   •   LEVEL {level}   •   REROLL: {upgrade_rerolls} [R]  (20 COINS)",
            True, WHITE
        )
        screen.blit(
            subtitle,
            (WIDTH // 2 - subtitle.get_width() // 2, 130)
        )

        if gun_choice_screen:
            choice_title = FONT_BIG.render("CHOOSE YOUR GUN", True, GOLD)
            screen.blit(
                choice_title,
                (WIDTH // 2 - choice_title.get_width() // 2, 190)
            )

            choice_w, choice_h, gap = 300, 260, 50
            total = choice_w * 2 + gap
            start = (WIDTH - total) // 2
            y = 300

            for index, (name, key, owned) in enumerate([
                ("SMG", "1", has_smg),
                ("RPG", "2", has_rpg),
            ]):
                x = start + index * (choice_w + gap)
                rect = pygame.Rect(x, y, choice_w, choice_h)
                hovered = rect.collidepoint(mouse_x, mouse_y)
                pygame.draw.rect(screen, BLACK, (x + 8, y + 8, choice_w, choice_h))
                pygame.draw.rect(screen, WOOD_LIGHT if hovered else WOOD, rect)
                pygame.draw.rect(screen, GOLD if hovered else WOOD_DARK, rect, 6)

                color = WOOD_DARK if owned else WHITE
                name_text = FONT.render(name, True, color)
                screen.blit(name_text, (x + choice_w // 2 - name_text.get_width() // 2, y + 55))
                info = "ALREADY OWNED" if owned else ("FAST FIRE" if name == "SMG" else "EXPLOSIVE SPLASH")
                info_text = FONT_SMALL.render(info, True, color)
                screen.blit(info_text, (x + choice_w // 2 - info_text.get_width() // 2, y + 120))
                key_text = FONT_SMALL.render(f"PRESS {key}", True, GOLD)
                screen.blit(key_text, (x + choice_w // 2 - key_text.get_width() // 2, y + 185))

        else:
            draw_upgrade_cards(mouse_x, mouse_y)

            instruction = FONT_SMALL.render(
                "CLICK A CARD  •  1 / 2 / 3 TO PICK  •  R = REROLL (20 COINS)",
                True, WHITE
            )
            screen.blit(
                instruction,
                (WIDTH // 2 - instruction.get_width() // 2, 645)
            )
            reroll_rect = pygame.Rect(WIDTH - 210, 635, 180, 40)
            pygame.draw.rect(screen, STONE, reroll_rect, border_radius=6)
            pygame.draw.rect(screen, GOLD if upgrade_rerolls > 0 else STONE_LIGHT, reroll_rect, 2, border_radius=6)
            reroll_text = FONT_TINY.render(
                f"REROLL 20c [{upgrade_rerolls}]",
                True, WHITE if upgrade_rerolls > 0 else STONE_LIGHT
            )
            screen.blit(reroll_text, (
                reroll_rect.centerx - reroll_text.get_width() // 2,
                reroll_rect.centery - reroll_text.get_height() // 2
            ))

    # =====================================================
    # GAME OVER (must be outside upgrade_screen so it always shows)
    # =====================================================
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 210))
        screen.blit(overlay, (0, 0))

        # red vignette pulse
        pulse = 0.55 + 0.45 * math.sin(pygame.time.get_ticks() * 0.006)
        vignette = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(vignette, (120, 10, 20, int(40 * pulse)), (0, 0, WIDTH, HEIGHT), 18)
        screen.blit(vignette, (0, 0))

        title = FONT_HUGE.render("GAME OVER", True, RED)
        screen.blit(
            title,
            (
                WIDTH // 2 - title.get_width() // 2,
                HEIGHT // 2 - 140,
            )
        )
        title2 = FONT_HUGE.render("GAME OVER", True, WHITE)
        screen.blit(
            title2,
            (
                WIDTH // 2 - title2.get_width() // 2 + 2,
                HEIGHT // 2 - 138,
            )
        )

        result = FONT.render(
            f"ROUND {wave}   •   {kills} KILLS   •   SCORE {score}", True, WHITE
        )
        screen.blit(
            result,
            (
                WIDTH // 2 - result.get_width() // 2,
                HEIGHT // 2 - 30,
            )
        )

        char_line = FONT_SMALL.render(
            f"{selected_character.upper()}  •  GUN LV.{gun_level}: {gun_name()}", True, GOLD
        )
        screen.blit(
            char_line,
            (WIDTH // 2 - char_line.get_width() // 2, HEIGHT // 2 + 8),
        )

        if best_run_flags[0] or best_run_flags[1]:
            bl = []
            if best_run_flags[0]: bl.append("BEST ROUND")
            if best_run_flags[1]: bl.append("BEST KILLS")
            center_text(screen, FONT_SMALL, "NEW PERSONAL " + " + ".join(bl) + "!",
                        (WIDTH // 2, HEIGHT // 2 + 40), GOLD)

        restart_rect = pygame.Rect(WIDTH // 2 - 190, HEIGHT // 2 + 70, 380, 70)
        quit_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 155, 300, 65)
        mx, my = pygame.mouse.get_pos()
        draw_button(screen, restart_rect, "RESTART  [R]", restart_rect.collidepoint(mx, my))
        draw_button(screen, quit_rect, "MENU  [Q]", quit_rect.collidepoint(mx, my))
        center_text(screen, FONT_TINY, "PRESS R TO RESTART  •  Q FOR MENU",
                    (WIDTH // 2, HEIGHT // 2 + 240), STONE_LIGHT)

    if multiplayer_screen and mp_started:
        multiplayer_screen = False
        intro_screen = False
        reset_game()

    if not intro_screen and not character_screen and not armory_screen and not paused and not game_over:
        draw_remote_players(screen)
        draw_multiplayer_lives(screen)

    if friends_screen:
        draw_friends_screen()
    elif character_screen:
        draw_character_screen()
    elif armory_screen:
        draw_armory_screen()
    elif multiplayer_screen:
        draw_multiplayer_screen()
    elif intro_screen:
        if leaderboard_screen:
            draw_leaderboard_screen()
        else:
            draw_intro_screen()
    elif paused:
        draw_pause_screen()

    # Tiny camera shake after a hit.
    if (
        not intro_screen
        and not paused
        and current_time < screen_shake_until
    ):
        shake_x = random.randint(-screen_shake_strength, screen_shake_strength)
        shake_y = random.randint(-screen_shake_strength, screen_shake_strength)
        frame = screen.copy()
        screen.fill(BG)
        screen.blit(frame, (shake_x, shake_y))

    pygame.display.flip()

save_profile()
pygame.quit()
sys.exit()
