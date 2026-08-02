import functools
import locale

import pygame as pg
import numpy
import math
from math import radians
import random
import os
import json
import time
import datetime
import sys
# NN TSS remake plan
#   M1, new map. takes place during Solar War. Becomes a prologue
#   M2,
#   M3,
#   M4,
#   M5,
#   M6,
#   M7,
#   M8,
#   M9, removed. Svenus is moved into the Lover side level with the doppelganger
#   M10, the agency investigate the government office
#   M11,
#   M12,
#   M13,
#   M14,

# Fun.py is not fun
# Here is many functions that are used a lot in the other files

start_october = (10, 1)
current_date = (datetime.datetime.now().month, datetime.datetime.now().day)
start_november = (11, 1)

VERSION = "1.0"
DEBUG_MODE =  False             # Use that to have access to debug functions
APOSTROPHE = "'"
DEFAULT_KEY_PRESSED, DEFAULT_KEY_COOLDOWN = 10, 7  # Could make these 2 a setting
pg.display.set_caption(f"THR-1's Assault - {VERSION}")
DECODING = locale.getpreferredencoding()
SPOOKY_DAY = start_october <= current_date <= start_november
DELTA_TIME = [60/17]


# |Testing|-------------------------------------------------------------------------------------------------------------
def print_to_error_stream(*a):
    print(*a, file = sys.stderr)


def timeme(method):
    # Keep this for testing, use it as a decorator
    def wrapper(*args, **kw):
        startTime = int(time.time_ns())
        # startTime = datetime.datetime.now().microsecond / 1000
        result = method(*args, **kw)
        endTime = int(time.time_ns())
        # endTime = datetime.datetime.now().microsecond / 1000
        print(endTime - startTime)
        return result

    return wrapper


@timeme
def test():
    for x in range(100000):
        pg.math.clamp(1, 2, 4)


@timeme
def test2():
    for x in range(100000):
        pg.math.clamp(1, 2, 4)

# |Saving stuff|--------------------------------------------------------------------------------------------------------
def dict_to_json(filename, dictionary):
    # This function make stuff go in a json file
    with open(filename, "w", encoding='utf-8') as outfile:
        # json.dump(dictionary, outfile)
        json.dump(dictionary, outfile, indent=6)


def get_from_json(filename, requested_info):
    # This function gets you stuff from a json file
    with open(filename, encoding='utf-8') as json_file:
        data = json.load(json_file)
        if requested_info == "Everything":
            return data
        return data[requested_info]


def get_image(img):
    return pg.image.load(os.path.join(img)).convert_alpha()


# |Settings|------------------------------------------------------------------------------------------------------------
def get_default_inputs():
    return {"Right": False, "Left": False, "Down": False, "Up": False, "Dash": False,
            "Shoot": False, "Alt fire": False, "Reload": False,
            "Interact": False, "Skill 1": False, "Skill 2": False,
            "Order Hold": False, "Order Follow": False, "Order Attack": False, "Order Act Free": False}


# For when I need a big number
BIG_INT = sys.maxsize
KEYBOARD_BOND_INPUT = ["Right", "Left", "Down", "Up", "Dash",
                       "Reload",
                       "Interact", "Skill 1", "Skill 2",
                       "Order Hold", "Order Follow", "Order Attack", "Order Act Free"]
MOUSE_BOND_INPUT = ["Shoot", "Alt fire"]
DEFAULT_KEY_BINDS = {"Keyboard": {"Up": pg.K_w, "Right": pg.K_d, "Left": pg.K_a, "Down": pg.K_s, "Dash": pg.K_SPACE,
                                  "Reload": pg.K_r,
                                  "Skill 1": pg.K_1, "Skill 2": pg.K_2, "Interact": pg.K_e,
                                  "Order Hold": pg.K_z, "Order Follow": pg.K_x, "Order Attack": pg.K_c, "Order Act Free": pg.K_v},
                     "Mouse": {"Shoot": 0, "Alt fire": 2},
                     "System": {"Pause": pg.K_ESCAPE, "Screenshot": pg.K_3}}
DEFAULT_CONTROLLER_BINDS = {
    "Move": "Stick Left", "Dash": ["Stick Left Press"], "Aim": "Stick Right",
    "Alt fire": ["Trigger Left"], "Shoot": ["Trigger Right"],
    "Interact": ["Button Right"], "Reload": ["Button Bottom"],
    "Skill 1": ["Button Top"], "Skill 2": ["Button Left"],
    "Order Hold": ["D-pad Up"], "Order Follow": ["D-pad Right"], "Order Attack": ["D-pad Down"], "Order Act Free": ["D-pad Left"],
    "Up": [], "Down": [], "Left": [], "Right": [],
    "Pause": ["Button Start"], "Screenshot": ["Button Select"]}

SYSTEM_CONTROLS = {"Pause": 27, "Screenshot": pg.K_BACKSPACE}
SYSTEM_CONTROLS_INPUT = {"Pause": False, "Screenshot": False}
ALL_CONTROLLERS = [[pg.joystick.Joystick(x) for x in range(pg.joystick.get_count())]]
EMPTY_SAVE_FILE = {
    # |Missions finished, available missions are based on the finished ones, save time it took to finish the mission
    "Version": VERSION,
    "Character weapons unlocked": {
        "Lord": [], "Emperor": [], "Wizard": [], "Sovereign": [], "Duke": [], "Jester": [], "Condor": [],
        "Curtis": [], "Lawrence": [], "Mark": [], "Vivianne": []
    },
    "Zoar unlocked": False,
    "Faction mission count": [0, 0, 0, 0, 0, 0],
    "Databank entries unlocked": [
        "21st Century Timeline", "2021 - 2040", "2041 - 2060", "2061 - 2080", "2081 - 2099",
        "Annals",
            "2100", "Solar War | January - April", "Solar War | May - August", "Solar War | September - December",
            "2101", "Solar War | January - April", "Solar War | May - August", "Solar War | September - December",
            "2102", "End of the Solar War", "Human FTLT system integration",
            "2103", "Humans Move to Zoar",
            "2105", "Pirate attack on Zoar",
        "Enemies",
            "Asset Protecting & Collection Dept.",
            "Burning Winds Band",
            "C8 Mercenary Army",
            "Misc.",
        "Organizations",
            "Armed groups", "Asset Protecting & Collection Dept.", "Burning Winds Band", "C8 Mercenary Army",
        "Mercenary Teams",
            "THR-1", "Overview", "Leopold LORD Storch", "Kai EMPEROR", "Jeanne WIZARD McNeil", "Corrine SOVEREIGN", "Zander DUKE", "M4-D1C JESTER", "Vincent CONDOR Varga",
            "Zoar Colony's Gun Shop", "Overview", # "Curtis Miller", "Vivianne Miller", "Lawrence Reed", "Mark",
		"Weapon Manufacturer",
            "Socrates",
            "Novak & Boyko",
            "CFCR",
            "ASUM",
            "Old English Armoury",
            "Factory Munition Ballistics",
        "Dickinson Technologies", "Manhunter Ammunitions",
        "Weapon",
            "Handgun", # "Big Iron", "War and Peace",
            "Rifle", "St-Maurice", #: ["St-Maurice Youth Model", "St-Laurent Gen 1", "Type 47 Rifle", "Cowboy's Repeater", "Mark's Rifle", "Type 30 Rifle", "Vivianne's Rifle", "Combat Rifle",
     		"Sub Machine Gun", "Type 41 SMG",
     		"Shotgun", "Jeanne's Family Shotgun", # "Type 23 Shotgun", "Standard Shotgun", "Vivianne's Shotgun", "Desert Shotgun",
     		"Energy", # "Custom Mk18 Laser cutter", "Laser Carbine", "Laser Rifle", "Heavy Laser", "Marker Laser", "Plasma Spray", "Plasma Rifle", "Laser Shotgun",
            "Melee", "Chain Axe", # "Oversized stun baton", "Corrine's Hands", "Hook Swords", "Hunk of Steel", "Vivianne's Leg", "Gun Hammer", "Pile Bunker",
     		"Combo", "GunBlade", # "Gun and Ballistic Knife", "Lawrence's Cutlass & Flintlock", "Captain's Axe & Blunderbuss",
     		"Heavy", "Saloum Mk-2", "Fortress Machine Gun", # "GMG-04B", "Musket .360", "Buggy Gun", "Missile Pod", "ARWS", "Flamethrower", "Napalm Grenade Launcher", "Bulwark Minigun",
     		"Gear", "Epicurean Medic Rifle", # "Crippled Laddie FCS Radio", "Mk16 Flare Mortar", "Nihilist Stretcher", "Stoic Shield generator", "C4", "Radar", "Smoke Dispenser", "Binoculars", "Artillery Radio"
    ]
}

# Just to check that every settings files are there
try:
    get_from_json("Settings.json", "Everything")
except FileNotFoundError:
    print_to_error_stream("File Setting.json missing, creating a new one")
    dict_to_json("Settings.json", {"SFX": 5.0, "Music": 5.0, "Voice": 5.0, "Screen shake": 1.0, "Language": 0})

try:
    get_from_json("Key binds.json", "Everything")
except FileNotFoundError:
    print_to_error_stream("Key binds.json not found, creating new one")
    dict_to_json("Key binds.json", DEFAULT_KEY_BINDS)

try:
    get_from_json("Controller binds.json", "Everything")
except FileNotFoundError:
    print_to_error_stream("Controller binds.json not found, creating new one")
    dict_to_json("Controller binds.json", DEFAULT_CONTROLLER_BINDS)

zoom_amount = 0.9
SCREEN_SHAKE_MOD = [round(get_from_json("Settings.json", "Screen shake"))]
FRAME_MAX_SIZE = [630, 450]  # Use this to affect how zoomed out the game renders
FRAME_MAX_SIZE[0] *= zoom_amount
FRAME_MAX_SIZE[1] *= zoom_amount
FRAME_MAX_SIZE = [round(FRAME_MAX_SIZE[0]), round(FRAME_MAX_SIZE[1])]


def update_render_zoom(num):
    FRAME_MAX_SIZE[0], FRAME_MAX_SIZE[1] = 630, 450  # Use this to affect how zoomed out the game renders
    FRAME_MAX_SIZE[0] *= num
    FRAME_MAX_SIZE[1] *= num
    FRAME_MAX_SIZE[0], FRAME_MAX_SIZE[1] = round(FRAME_MAX_SIZE[0]), round(FRAME_MAX_SIZE[1])


def meme(num):
    return "eovdedn"[num % 2:: 2]   # unironically using that for memes


# |Sound effects|-------------------------------------------------------------------------------------------------------
class Sound:
    def __init__(self, pos, duration, radius, source="Unknown", strength=0):
        self.up_time = 0
        self.pos = pos
        self.duration = duration
        self.radius = radius
        # Optional stuff
        self.source = source
        self.strength = strength

    def go_down(self):
        self.up_time += 1
        self.duration -= 1


def play_music(music_to_play, use_intro=False, check_if_busy=False):
    # music_to_play is the name of song in music_dict
    # particule is there to place the particule that gives the song name, and it's author
    # use_intro is used to play any song with that have a start that doesn't loop, mainly boss themes
    if music_to_play not in music_dict or music_dict[music_to_play]["Music"] == "":
        print_to_error_stream(f"{music_to_play} does not exist")
        return

    if check_if_busy and pg.mixer.music.get_busy() or CURRENT_TRACK_INFO[1] == music_to_play:
        return

    # Play the music
    if use_intro and use_intro in music_dict:
        pg.mixer.music.load(music_dict[use_intro]["Music"])
        pg.mixer.music.play()
        pg.mixer.music.queue(music_dict[music_to_play]["Music"], loops=-1)
    else:
        pg.mixer.music.load(music_dict[music_to_play]["Music"])
        pg.mixer.music.play(-1)

    # Set the volume
    volume_to_use = music_dict[music_to_play]["Volume"] * 0.5
    pg.mixer.music.set_volume(volume_to_use * (get_from_json("Settings.json", "Music") / 10))
    CURRENT_TRACK_INFO[0] = volume_to_use
    CURRENT_TRACK_INFO[1] = music_to_play


def stop_music():
    pg.mixer.music.fadeout(600)
    CURRENT_TRACK_INFO[1] = "No track"


def play_sound(sound_to_play, sound_type="SFX", modified_volume=0, fadeout=0, absolute_volume=-1):
    # Play the noise
    sounds_dict[sound_to_play]["Sound"].play()

    # Change the volume
    volume_to_use = sounds_dict[sound_to_play]["Volume"] * (get_from_json("Settings.json", sound_type) / 10)
    if modified_volume != 0:
        volume_to_use = modified_volume * (get_from_json("Settings.json", sound_type) / 10)
    if absolute_volume != -1:
        volume_to_use = absolute_volume
    sounds_dict[sound_to_play]["Sound"].set_volume(volume_to_use * 0.5)

    # Handles fadeout
    if fadeout != 0:
        # Fadeout must be between 0 and 1
        fadeout_time = round(sounds_dict[sound_to_play]["Sound"].get_length() * 1000 * fadeout)
        sounds_dict[sound_to_play]["Sound"].fadeout(fadeout_time)


# This is a way to save the current volume of the music playing
CURRENT_TRACK_INFO = [0, "No track"]

music_dict = {
    "Menu": {"Music": 'Sounds/Music/Menu theme.wav', "Volume": 1, "Author": "", "Name": ""},
    "Mission 1": {"Music": 'Sounds/Music/Mission theme.wav', "Volume": 1, "Author": "", "Name": ""},
    "Mission 2": {"Music": 'Sounds/Music/Mission theme.wav', "Volume": 1, "Author": "", "Name": ""},
    "Mission 3": {"Music": 'Sounds/Music/Mission theme.wav', "Volume": 1, "Author": "", "Name": ""},
    "Boss - THR-1": {"Music": 'Sounds/Music/THR-1 Boss theme.wav', "Volume": 1, "Author": "", "Name": ""},
    "Boss - Curtis": {"Music": 'Sounds/Music/Zoar Boss theme.wav', "Volume": 1, "Author": "", "Name": ""},
    "Boss - Rigel": {"Music": 'Sounds/Music/Final Boss theme.wav', "Volume": 1, "Author": "", "Name": ""},
}


QUIET, MEDIUM, LOUD = 0.5, 0.75, 1
opt = lambda a : f'Sounds/Sound effects{a}' # Baby's first lambda function
make_sound = lambda a, b : {"Sound": pg.mixer.Sound(os.path.join(opt(a))), "Volume": b}
sounds_dict = {
    "Template": make_sound('/Gun/small arms.ogg', 1),
    "Silence": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Gun/small arms.ogg')), "Volume": 0},
    # Menu sound effects
    "Menu move": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Menu/Move.ogg')), "Volume": 1},
    "Menu confirm": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Menu/Confirm.ogg')), "Volume": 1},
    "Menu back": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Menu/Confirm.ogg')), "Volume": 1},
    # Firing
    "Crit Shoot": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Firearms/Crit.ogg')), "Volume": 1},

    "Small arms": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Gun/small arms.ogg')), "Volume": 1},
    "Small arms 2": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Gun/small arms.ogg')), "Volume": 0.3},
    "Quack": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Gun/Quack1.ogg')), "Volume": 1},
    "Revolver": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Gun/revolver.ogg')), "Volume": 1},
    "Revolver shoot": {
        "Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Gun/revolver shoot.ogg')), "Volume": 0.85},
    "Revolver reload": {
        "Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Gun/revolver reload.ogg')), "Volume": 1},
    "Shotgun": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Gun/small arms.ogg')), "Volume": 1},
    "Rifle": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Gun/Bigger gun.ogg')), "Volume": 1},
    "Rifle 2": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Gun/rifle1.ogg')), "Volume": 1},
    "Pile Bunker Hit": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Gun/rifle1.ogg')), "Volume": 1},
    "Rifle lever shoot": {
        "Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Gun/lever action shoot.ogg')), "Volume": 0.85},

    "Rocket launcher": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Firearms/Rocket Launcher.ogg')), "Volume": 1},
    "Toaster Shoot": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Gun/Toaster Shoot.ogg')),
                      "Volume": 0.4},

    "Laser": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Gun/laser.ogg')), "Volume": 1},
    "Laser 2": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Gun/laser_2.ogg')), "Volume": 1},
    "Fire": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Gun/small arms.ogg')), "Volume": 1},

    "Slash": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Gun/small arms.ogg')), "Volume": 1},
    "Blunt": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Gun/small arms.ogg')), "Volume": 1},
    "Trust": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Gun/small arms.ogg')), "Volume": 1},
    # Reload
    "Reload Pistol 1": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Gun/reload1.ogg')), "Volume": 0.35},
    "Reload Rifle 1": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Gun/reload2.ogg')), "Volume": 0.55},
    "Reload Enemy 1": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Gun/reload2.ogg')), "Volume": 0.05},

    # Jam
    "Jamming": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Gun/no_ammo_ping_1.ogg')), "Volume": 1},

    # Melee
    "Melee hit 1": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Melee/melee_hit_1.ogg')), "Volume": 1},
    "Melee miss 1": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Melee/melee_miss_1.ogg')), "Volume": 1},

    # Grenade
    "flashbang": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Flashbang 1.ogg')), "Volume": 0.075},

    # Skills
    "Skill 1": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Skill_1.ogg')), "Volume": 0.5},
    # Big whoosh
    "Skill 2": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Skill_2.ogg')), "Volume": 0.5},
    # Small whoosh
    "Skill 3": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Skill_3.ogg')), "Volume": 0.5},
    # Long and quiet whoosh
    "Skill 4": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Skill_4.ogg')), "Volume": 0.35},
    # Small loud whoosh
    "Skill 5": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Skill_5.ogg')), "Volume": 0.5},
    # Long weird sound
    "Skill 6": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Skill_6.ogg')), "Volume": 0.25},
    # Loud whoosh with fadeout
    "Skill 7": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Skill_7.ogg')), "Volume": 0.25},
    # whoosh fade in and fadeout
    "Bullet bending": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Bullet bend.ogg')), "Volume": 0.3},
    # w=Noise,W=48000,f=814.676,b=0,r=0.4,s=451,z=Down,l=0.5,e=Sine,N=6,F=5000,E=0
    "Chain": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Chain.ogg')), "Volume": 0.8},
    "Chain click": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Chain_click.ogg')), "Volume": 0.8},
    "Chain boss": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Chain_boss.ogg')), "Volume": 1},
    "Charge": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Skill_charge.ogg')), "Volume": 1},
    "Charge 2": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Skill_charge_2.ogg')), "Volume": 1},
    # ||
    "Explosion": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Explosion.ogg')), "Volume": 0.25},
    "Fire 1": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Fire_1.ogg')), "Volume": 0.05},
    "Sardine Blows Up": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Sardine_Blows_Up.ogg')), "Volume": 0.6},

    # Electricity
    "Electricity 1": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Electricity_1.ogg')), "Volume": 0.5},
    "Electricity 2": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Electricity_2.ogg')), "Volume": 0.5},

    # Hitting
    "Hitting 1": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Hitting 1.ogg')), "Volume": 0.5},
    "Hitting 2": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Hitting 2.ogg')), "Volume": 0.5},
    "Hitting 3": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Hitting 3.ogg')), "Volume": 0.5},

    # Bullet hit
    "Bullet hit 1": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Bullet_hit_1.ogg')), "Volume": 0.2},
    "Bullet hit 2": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Bullet_hit_2.ogg')), "Volume": 0.25},
    "Bullet hit 3": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Cling.ogg')), "Volume": 0.25},
    "Bullet hit 4": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Bullet_hit_4.ogg')), "Volume": 0.5},
    "Grenade 2": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Incendiary_Grenade.ogg')), "Volume": 0.8},
    "Grenade 3": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Smoke_Grenade.ogg')), "Volume": 0.8},
    "Grenade hit wall": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Grenade_hit_wall.ogg')),
                         "Volume": 0.5},
    # Anomaly
    "Slime death": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Anomaly_5.ogg')), "Volume": 0.9},
    "Slime split": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Anomaly_3.ogg')), "Volume": 0.8},
    "Snake shoot": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Snake Shoot.ogg')), "Volume": 0.8},
    "Snake split": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Snake split.ogg')), "Volume": 0.8},
    # |Boss attacks|----------------------------------------------------------------------------------------------------
    "Mary Wall": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Bosses/Mary_wall.ogg')), "Volume": 1},

    "Son combo 1": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Bosses/Son attack 1.ogg')),
                    "Volume": 0.15},
    # w=Noise,W=22050,f=135.471,v=69.478,V=22.104,t=204.337,T=0.307,_=0.07,d=41.092,D=0.274,p=1.113,A=0.1,r=0.2,s=12,S=9.651,g=0.237,l=0.469,N=20,F=1401.377,B=Fixed,E=46434
    "Son combo 2": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Bosses/Son attack 2.ogg')),
                    "Volume": 0.15},
    "Son combo 3": {"Sound": pg.mixer.Sound(os.path.join(opt('/Bosses/Son attack 3.ogg'))), "Volume": 0.15},
    "Son dash": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Bosses/Son dash.ogg')), "Volume": 0.15},
    "Son slash": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Bosses/Son slash.ogg')), "Volume": 0.15},

    "Wheel switch": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Bosses/Wheel_switch.ogg')),
                     "Volume": 0.5},
    "Attack big": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Bosses/Big_attack.ogg')), "Volume": 0.5},
    "Magician 1": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Thunder_1.ogg')), "Volume": 0.5},
    "Magician 2": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Thunder_2.ogg')), "Volume": 0.5},
    "Magician 3": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Thunder_3.ogg')), "Volume": 0.5},
    "Magician 4": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Thunder_4.ogg')), "Volume": 0.5},
    "Magician 5": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Thunder_5.ogg')), "Volume": 0.5},
    "Vulture Armour": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Vulture_Armour.ogg')), "Volume": 0.95},

    "Betel 1": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Bosses/Betelgeuse_1.ogg')), "Volume": 0.95},
    "Betel 2": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Bosses/Betelgeuse_2.ogg')), "Volume": 0.95},
    "Betel 3": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Bosses/Betelgeuse_3.ogg')), "Volume": 0.95},
    "Betel 4": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Bosses/Betelgeuse_4.ogg')), "Volume": 0.95},
    "Betel 5": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Bosses/Betelgeuse_5.ogg')), "Volume": 1.5},
    "Betel 6": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Bosses/Betelgeuse_6.ogg')), "Volume": 0.95},
    "Betel Death": {"Sound": pg.mixer.Sound(os.path.join(opt('/Bosses/Betelgeuse_death.ogg'))), "Volume": 0.95},
    "Betel Death BIGGER": {"Sound": pg.mixer.Sound(os.path.join(opt('/Bosses/Betelgeuse_death_bigger.ogg'))), "Volume": 0.95},

    "Com 1": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Bosses/Combustion_1.ogg')), "Volume": 0.125},
    "Com 2": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Bosses/Combustion_2.ogg')), "Volume": 0.15},
    "Dive 1": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Bosses/Dive_1.ogg')), "Volume": 0.125},
    "Dive 2": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Bosses/Dive_2.ogg')), "Volume": 0.15},
    "Quake": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Bosses/Quake.ogg')), "Volume": 1},
    "Empress 1": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Friction_1.ogg')), "Volume": 0.5},
    "Empress 2": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Friction_2.ogg')), "Volume": 0.5},
    "Charging": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Bosses/Charging.ogg')), "Volume": 2},
    "Sword launch": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Sword launch.ogg')), "Volume": 1},
    # |Dodge|-----------------------------------------------------------------------------------------------------------
    # When I get good ones, I'll use it for the "D" player skills
    "Player dash": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Skill_2.ogg')), "Volume": 0.5},
    "Dodge": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Dodge_1.ogg')), "Volume": 0.15},
    # w=Noise,f=108.165,v=132.722,V=5.695,t=1.76,T=0.215,_=0.226,d=4.635,D=0.12,p=1.732,A=0.1,b=0.1,r=0.5,c=28,C=3.188,s=4,S=9.509,z=Down,g=0.096,l=0.421,e=Sine,N=33,F=296.918,E=53060
    "Dodge Retreat": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Dodge_1.ogg')), "Volume": 0.15},
    "Dodge Approach": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Dodge_1.ogg')), "Volume": 0.15},

    # |Environment|-----------------------------------------------------------------------------------------------------
    "Bullet hitting wall 1": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Bullet_hitting_wall.ogg')),
                              "Volume": 0.5},

    "Wall hit 1": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Bullet_hitting_wall.ogg')),
                   "Volume": 0.5},
    # |Misc|------------------------------------------------------------------------------------------------------------
    "Ping": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Ping.ogg')), "Volume": 0.7},
    # |Player sound|----------------------------------------------------------------------------------------------------
    "Curtis Hit": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Player/Hurt.ogg')), "Volume": 1},
    "Curtis Walk 1": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Player/Walk 1.ogg')), "Volume": 0.25},
    "Curtis Walk 2": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Player/Walk 2.ogg')), "Volume": 0.25},
    "Curtis Slide": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Player/Slide.ogg')), "Volume": 0.35},
    "Curtis Switch": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Player/player_switch.ogg')),
                      "Volume": 0.25},
    "Corrine Ping": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Player/Ping.ogg')), "Volume": 0.9},
    "Jeanne Building": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Player/Jeanne Building.ogg')), "Volume": 0.9},
    "Zander Smoke": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Player/Zander Smoke.ogg')), "Volume": 1.3},
    "Vincent Unbreaking": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Player/Vincent Unbreaking.ogg')), "Volume": 0.9},
    "Vincent Armour Break": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Player/Vincent Armour Break.ogg')), "Volume": 0.9},
    "Beast Mode": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Player/Beast Mode.ogg')), "Volume": 0.9},
    "Jeanne Buff": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Player/Jeanne Buff.ogg')), "Volume": 0.9},

    # New sounds!

    "Artillery 1": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Gun/Artillery 1.ogg')), "Volume": 1.1},
    "Artillery 2": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/Gun/Artillery 2.ogg')), "Volume": 1.3},

    "Gun Silenced": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Firearms/Rifle_Silenced.ogg')), "Volume": 1},
    "Shotgun 1 Shooting": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Firearms/Shotgun_Shoot_Pump.ogg')), "Volume": 0.8},
    "Shotgun 2 Shooting": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Firearms/Shotgun.ogg')), "Volume": 0.8},
    "Shotgun 1 Pump": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Firearms/Shotgun_Pumped_1.ogg')), "Volume": 0.8},
    "Rifle 1 Shooting": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Firearms/Rifle_1.ogg')), "Volume": 0.8},
    "Rifle 2 Shooting": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Firearms/Rifle_2.ogg')), "Volume": 1},
    "Safety": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Firearms/Safety_Click.ogg')), "Volume": 0.4},

    "Hover Tank Canon": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/New Boss/Hover Tank Cannon.ogg')), "Volume": 1.2},

    "Armoured Shield Generator Railgun": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/New Boss/Armoured Shield Generator Railgun.ogg')), "Volume": 1.2},

    "Mech Booster": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/New Boss/Mech Booster.ogg')), "Volume": 0.6},
    "Magma Blade": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/New Boss/Magma Blade.ogg')), "Volume": 1.2},
    "Mech Cannon": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/New Boss/Mech Cannon.ogg')), "Volume": 1.2},
    "Mech Minigun": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/New Boss/Mech Minigun.ogg')), "Volume": 1.2},
    "Mech Missile": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/New Boss/Mech Missile.ogg')), "Volume": 0.8},

    "Gilgamesh Sword L": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/New Boss/Gilgamesh Sword Light.ogg')), "Volume": 1},
    "Gilgamesh Sword M": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/New Boss/Gilgamesh Sword.ogg')), "Volume": 1},
    "Gilgamesh Sword H": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/New Boss/Gilgamesh Sword Heavy.ogg')), "Volume": 1},

    "Rigel Laser barrage": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/New Boss/Rigel Laser barrage.ogg')), "Volume": 1},
    "Rigel Plasma": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/New Boss/Rigel Plasma.ogg')), "Volume": 1},
    "Rigel Plasma Shoot": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/New Boss/Rigel Plasma Shoot.ogg')), "Volume": 1},
    "Rigel Shoulder Bash": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/New Boss/Rigel Shoulder Bash.ogg')), "Volume": 1},
    "Rigel Lance Swipe": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/New Boss/Rigel Lance Swipe.ogg')), "Volume": 1.75},
    "Rigel Giga Thrust": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Sound effects/New Boss/Rigel Giga Thrust.ogg')), "Volume": 1.75},
    # "Shot gun 2 Shooting": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Firearms/Shotgun.ogg')), "Volume": 0.8},

    "Armoured Shield Generator Charging": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Voice/Armoured Shield Generator Charging.ogg')), "Volume": 2},
    "Armoured Shield Generator Aiming": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Voice/Armoured Shield Generator Aiming.ogg')), "Volume": 2.3},
    "Armoured Shield Generator Fire": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Voice/Armoured Shield Generator Fire.ogg')), "Volume": 2},

    "Attack Helicopter Attack": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Voice/Attack Helicopter Attack.ogg')), "Volume": 0.9},
    "Attack Helicopter Death Scream": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Voice/Attack Helicopter Death Scream.ogg')), "Volume": 0.9},
    "Attack Helicopter Fire": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Voice/Attack Helicopter Fire.ogg')), "Volume": 0.9},
    "Attack Helicopter Nails": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Voice/Attack Helicopter Nails.ogg')), "Volume": 0.9},
    "Attack Helicopter Locked On": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Voice/Attack Helicopter Locked On.ogg')), "Volume": 0.9},

    "Bloodhound Burn": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Voice/Bloodhound Burn.ogg')), "Volume": 1},
    "Bloodhound Take That": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Voice/Bloodhound Take That.ogg')), "Volume": 1},
    "Bloodhound And That": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Voice/Bloodhound And That.ogg')), "Volume": 1},
    "Bloodhound Disappear": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Voice/Bloodhound Disappear.ogg')), "Volume": 1},
    "Bloodhound RATATATATA": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Voice/Bloodhound RATATATATA.ogg')), "Volume": 1},

    "Hover Tank Eat That": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Voice/Hover Tank Eat That.ogg')), "Volume": 1.3},
    "Hover Tank Get Some": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Voice/Hover Tank Get Some.ogg')), "Volume": 1.3},
    "Hover Tank Get In My Way": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Voice/Hover Tank Get In My Way.ogg')), "Volume": 1.3},
    "Hover Tank Take That": {"Sound": pg.mixer.Sound(os.path.join('Sounds/Voice/Hover Tank Take That.ogg')), "Volume": 1.3},
}


def sound_test(self, win, CLOCK):
    win_width, win_height = win.get_size()
    # Pause music
    pg.mixer.music.pause()

    sound_list = []
    for sound in sounds_dict:
        sound_list.append(sound)

    player = self
    # Select the fight
    key_pressed = DEFAULT_KEY_PRESSED
    key_cooldown = DEFAULT_KEY_COOLDOWN
    chosen_option = 0
    test_volume = 5
    # fight_to_load = sound_list[chosen_option]

    controller = PseudoPlayer()
    while True:
        # Select
        keys = pg.key.get_pressed()
        needed_in_menu_and_game(win, keys)
        controller.get_input(keys)

        if key_pressed == 0:
            # Select noise
            if controller.input["Up"] and chosen_option > 0:
                chosen_option -= 1
                key_pressed = key_cooldown
            if controller.input["Down"] and chosen_option < len(sound_list) - 1:
                chosen_option += 1
                key_pressed = key_cooldown
            # Change volume
            if controller.input["Left"] and test_volume > 0.25:
                test_volume -= 0.25
                key_pressed = key_cooldown
            if controller.input["Right"] and test_volume < 10:
                test_volume += 0.25
                key_pressed = key_cooldown
            # Play volume
            if controller.input['Interact']:
                # Confirm
                play_sound(sound_list[chosen_option], "SFX", modified_volume=test_volume / 10)
                key_pressed = key_cooldown * 3
            # Get out of there
            if SYSTEM_CONTROLS_INPUT["Pause"]:
                break
        else:
            key_pressed -= 1
        # draw
        win.fill(UI_COLOUR_BACKGROUND)
        win.blit(UI_FONT.render("Sound test", True, UI_COLOUR_FONT), (0, 25))
        win.blit(UI_FONT.render(f"{write_control(player, 'Pause')} Exit", True, UI_COLOUR_TUTORIAL),
                 (0, 35))
        win.blit(UI_FONT.render(f"{write_control(player, 'Interact')} play sound", True,
                                UI_COLOUR_TUTORIAL), (0, 75))
        win.blit(UI_FONT.render(f"{write_control(player, 'Up', is_move=True)}"
                                f"{write_control(player, 'Down', fucking_hell=False)} select sound", True,
                                UI_COLOUR_TUTORIAL), (0, 85))
        win.blit(UI_FONT.render(
            f"{write_control(player, 'Left', is_move=True)}"
            f"{write_control(player, 'Right', fucking_hell=False)}, change volume", True, UI_COLOUR_TUTORIAL), (0, 125))
        win.blit(UI_FONT.render(f"[{test_volume / 10}] Test Volume", True, UI_COLOUR_FONT), (0, 135))

        pg.draw.rect(win, UI_COLOUR_FONT, (0, 0, key_pressed * 2, 10))

        pg.draw.rect(win, UI_COLOUR_HIGHLIGHT, (125, win_height // 3, 125, 10))
        name_offset = 15
        for x in enumerate(sound_list):
            y_pos = win_height // 3 + (name_offset * x[0]) - chosen_option * name_offset
            win.blit(UI_FONT.render(x[1], True, UI_COLOUR_FONT), (125, y_pos))

        pg.display.update()
        CLOCK.tick(60)
    pg.mixer.music.unpause()


# |Colours|-------------------------------------------------------------------------------------------------------------
# Keeping colours used here like that helps keep the colour pallet consistant
# Grayscale
WALL_COLOUR = [25, 25, 25]
BLACK = (0, 0, 0)
DARK = (40, 40, 40)
DARK_GRAY, GRAY, LIGHT_GRAY = (60, 60, 60), (122, 122, 122), (205, 205, 205)
WHITE = (255, 255, 255)

# Actual colours
AMBER, AMBER_LIGHT = (255, 176, 0), (255, 204, 0)
LIGHT_GREEN, GREEN, MED_GREEN, DARK_GREEN, DARKER_GREEN = (65, 255, 65), (0, 255, 0), (0, 192, 0), (0, 125, 0), (0, 62, 0)
DARK_GREEN_ALT = (0, 128, 64)
LIGHT_RED, RED, MED_RED, DARK_RED, DARKER_RED = (255, 65, 65), (255, 0, 0), (192, 0, 0), (125, 0, 0), (62, 0, 0)
ORANGE = (230, 140, 0)
DARK_ORANGE = (115, 70, 0)
BROWN = (165, 104, 42)
MAGENTA, PURPLE = (255, 0, 255), (230, 0, 175)
LIGHT_BLUE, BLUE, DARK_BLUE, DARKER_BLUE = (125, 200, 220), (0, 0, 255), (0, 0, 125), (0, 0, 62)
BLUISH_GRAY = (102, 102, 142)

LIGHT_TEAL, TEAL, DARK_TEAL, DARKER_TEAL = (128, 255, 255), (0, 255, 255), (0, 128, 128), (0, 62, 62)
OUTLINE_TEAL = (0, 160, 160)
OUTLINE_ENEMIES_FACTION_1 = (0, 0, 160)
OUTLINE_ENEMIES_FACTION_2 = (0, 160, 0)
OUTLINE_ENEMIES_FACTION_3 = (160, 0, 0)

LIGHTNING = (175, 175, 255)
YELLOW = (255, 236, 32)
YELLOW_LIGHT = (255, 255, 122)
PARRIED_COLOUR = (0, 255, 255)
WATER_NORMAL = (43, 127, 178)
WATER_WASTE = (70, 123, 91)
FIRE = (255, 50, 0)
FIRE_GREEN = (50, 255, 0)

RIGEL_ENERGY = (125//4*3, 200//4*3, 220//4*3)

# UI colours
UI_COLOUR_FONT, UI_COLOUR_HIGHLIGHT, UI_COLOUR_BACKDROP, UI_COLOUR_BACKGROUND = WHITE, GRAY, DARK, (12, 12, 12)
UI_COLOUR_TUTORIAL = AMBER_LIGHT
UI_COLOUR_NEW_BACKGROUND = (26, 26, 26)
UI_COLOUR_NEW_BACKDROP = (141, 101, 13)
UI_COLOUR_CONTRAST = (51, 255, 0)

EXPLOSION_COLORS = [AMBER_LIGHT, AMBER, ORANGE, ORANGE, DARK, DARK_GRAY, RED]
BULLET_HIGHLIGHT = (255, 255, 122)

PLAYER_OUTLINE_COLOUR = [RED, BLUE, GREEN, YELLOW]


# |Fonts|---------------------------------------------------------------------------------------------------------------
# Add the font file for consistency

# FONT_NAME = ["system"]
# FONT_NAME = ["Courier"]
# FONT_NAME = ["system"]
# FONT_NAME = ["Lucida Console"] # Consolas
# FONT_NAME = ["Consolas"]
FONT_NAME = ["Sprites/JetBrainsMono-SemiBold.ttf"]
get_font = lambda a, b :  pg.font.SysFont(a, b)
FONTS = {"big": get_font(FONT_NAME[0], 50),
         "med": get_font(FONT_NAME[0], 25),
         "fuk": get_font(FONT_NAME[0], 20),
         "sma": get_font(FONT_NAME[0], 15),
         "dia": get_font(FONT_NAME[0], 30)}
UI_FONT = get_font(FONT_NAME[0], 18)


def create_temp_font_1(height, font_name=FONT_NAME[0]):
    return get_font(font_name, height //  25)
    # return get_font(FONT_NAME[0], round(height // 25 * 0.7777777777777778 * 0.75))


def create_temp_font_2(height, font_name=FONT_NAME[0]):
    return get_font(font_name, height // 30)


def create_temp_font_3(height, font_name=FONT_NAME[0]):
    return get_font(font_name, height //  15)


def create_temp_font_4(height, font_name=FONT_NAME[0]):
    return get_font(font_name, height //  8)


def create_temp_font_5(height, font_name=FONT_NAME[0]):
    return get_font(font_name, height //  18)


def create_temp_font_6(height, font_name=FONT_NAME[0]):
    return get_font(font_name, height // 40)


# for ctf in [create_temp_font_1, create_temp_font_2, create_temp_font_3, create_temp_font_4, create_temp_font_5]:
#     print(ctf(450).render("K", True, WHITE).get_height())

# 14        18
# 11
# 22
# 42
# 19

# |Sprites|-------------------------------------------------------------------------------------------------------------
def swap(swap_img, old_colour, new_colour):
    # To swap with and have transparency
    # place (0, 0, 0) at the end of old_colour and (0, 0, 0, 0) at the end of new_colour
    # sawp_img should not have transparency

    # Based on DaFluffyPotato code
    # Changes : the 2 function have been fused, the function is more flexible with inputs
    for colour_swap in range(len(old_colour)):
        img_copy = pg.Surface(swap_img.get_size())
        img_copy.fill((0, 0, 0))
        img_copy.fill(new_colour[colour_swap])
        swap_img.set_colorkey(old_colour[colour_swap])
        img_copy.blit(swap_img, (0, 0))
        swap_img = img_copy
    swap_img.set_colorkey((0, 0, 0))
    return swap_img


def get_outline(sprite: pg.Surface, colour=BLACK):
    # Optimize this when possible, something could be done in the sprite to help
    # Yeah I am not doing that
    sprite = sprite.copy()
    mask = pg.mask.from_surface(sprite)
    outline = mask.outline()
    outline_sprite = pg.Surface(sprite.get_rect().size).convert_alpha()
    outline_sprite.fill((0, 0, 0, 0))
    for p in outline:
        # outline_sprite.set_at(p, colour)
        outline_sprite.set_at([p[0]-1, p[1]], colour)
        outline_sprite.set_at([p[0]+1, p[1]], colour)
        outline_sprite.set_at([p[0], p[1]-1], colour)
        outline_sprite.set_at([p[0], p[1]+1], colour)
    outline_sprite.blit(sprite, (0, 0))
    return outline_sprite


ENTITY_SHADOW = get_image('Sprites/Entity Shadow.png')
ENTITY_SHADOW_SIZE_2 = pg.transform.scale2x(ENTITY_SHADOW)

PHONETIC_ALPHABET = [
    'Alpha', 'Bravo', 'Charlie', 'Delta', 'Echo', 'Foxtrot', 'Golf', 'Hotel', 'India', 'Juliet', 'Kilo', 'Lima', 'Mike',
    'November', 'Oscar', 'Papa', 'Québec', 'Romeo', 'Sierra', 'Tango', 'Uniform', 'Victor', 'Whiskey', 'X-Ray', 'Yanky',
    'Zulu'
]
JUST_THE_ALPHABET = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
# Weapon selection sprites
get_sprite_stack_list = lambda img, height: [img.subsurface((0, img.get_height() - height * (x + 1), img.get_width(), height)) for x in range(img.get_height()//height)]
SPRITE_FORTRESS_APC = get_sprite_stack_list(get_image('Sprites/Vehicles/Fortress APC.png'), 86)
SPRITE_FORTRESS_APC_CHASSIS = get_sprite_stack_list(get_image('Sprites/Vehicles/Fortress APC - Chassis.png'), 86)
SPRITE_FORTRESS_APC_TURRET = get_sprite_stack_list(get_image('Sprites/Vehicles/Fortress APC - Turret.png'), 45)
SPRITE_ENFORCER = get_sprite_stack_list(get_image('Sprites/Vehicles/Enforcer.png'), 20)

SPRITE_SAND_BUGGY = get_sprite_stack_list(get_image('Sprites/Vehicles/Sand Buggy.png'), 77)
SPRITE_SAND_BUGGY_TURRET = get_sprite_stack_list(get_image('Sprites/Vehicles/Sand Buggy Turret.png'), 34)
SAND_BUGGY_FRONT_BASE = get_image('Sprites/Vehicles/Sand Buggy Wheels Front.png')
SPRITE_SAND_BUGGY_FRONT = [
    get_sprite_stack_list(SAND_BUGGY_FRONT_BASE.subsurface((0, 0, 40, SAND_BUGGY_FRONT_BASE.get_height())), 15),
    get_sprite_stack_list(SAND_BUGGY_FRONT_BASE.subsurface((40, 0, 40, SAND_BUGGY_FRONT_BASE.get_height())), 15),
    get_sprite_stack_list(SAND_BUGGY_FRONT_BASE.subsurface((80, 0, 40, SAND_BUGGY_FRONT_BASE.get_height())), 15),
    get_sprite_stack_list(SAND_BUGGY_FRONT_BASE.subsurface((120, 0, 40, SAND_BUGGY_FRONT_BASE.get_height())), 15),
]
SAND_BUGGY_WHEEL_BASE = get_image('Sprites/Vehicles/Sand Buggy Wheels.png')
SPRITE_SAND_BUGGY_WHEEL = [
    get_sprite_stack_list(SAND_BUGGY_WHEEL_BASE.subsurface(0, 0, 44, SAND_BUGGY_WHEEL_BASE.get_height()), 77),
    get_sprite_stack_list(SAND_BUGGY_WHEEL_BASE.subsurface(44, 0, 44, SAND_BUGGY_WHEEL_BASE.get_height()), 77),
    get_sprite_stack_list(SAND_BUGGY_WHEEL_BASE.subsurface(88, 0, 44, SAND_BUGGY_WHEEL_BASE.get_height()), 77),
    get_sprite_stack_list(SAND_BUGGY_WHEEL_BASE.subsurface(132, 0, 44, SAND_BUGGY_WHEEL_BASE.get_height()), 77),
]

# 15
SPRITE_BULWARK = get_sprite_stack_list(get_image('Sprites/Vehicles/Bulwark.png'), 16)
BULWARK_BASE = get_image('Sprites/Vehicles/Bulwarks.png')
SPRITE_BULWARKS = [
    get_sprite_stack_list(BULWARK_BASE.subsurface(0, 0, 16, 464), 16),
    get_sprite_stack_list(BULWARK_BASE.subsurface(16, 0, 16, 464), 16),
    get_sprite_stack_list(BULWARK_BASE.subsurface(32, 0, 16, 464), 16),
    get_sprite_stack_list(BULWARK_BASE.subsurface(48, 0, 16, 464), 16),
    get_sprite_stack_list(BULWARK_BASE.subsurface(64, 0, 16, 464), 16)
]
SPRITE_CARDBOARD_BOX = get_sprite_stack_list(get_image('Sprites/Vehicles/Corrine Cardboard Box.png'), 24)
SPRITE_BULLET_HOLES = get_image('Sprites/Effect/Bullet hole.png')

# Bosses
SPRITE_ARMORED_GENERATOR_CHASSIS = get_sprite_stack_list(get_image('Sprites/Vehicles/Armed Shield Generator.png'), 86)
SPRITE_ARMORED_GENERATOR_TURRET = get_sprite_stack_list(get_image('Sprites/Vehicles/Armed Sheild Generator - Turret.png'), 110)

SPRITE_HOVER_TANK_CHASSIS = get_sprite_stack_list(get_image('Sprites/Vehicles/Hover Tank - Chassis.png'), 160)
SPRITE_HOVER_TANK_TURRET = get_sprite_stack_list(get_image('Sprites/Vehicles/Hover Tank - Turret.png'), 160)
SPRITE_HOVER_TANK_GUN = get_sprite_stack_list(get_image('Sprites/Vehicles/Hover Tank - Machine Gun.png'), 160)

SPRITE_ATTACK_HELICOPTER = get_sprite_stack_list(get_image('Sprites/Vehicles/Attack helicopter.png'), 128)
SPRITE_ATTACK_HELICOPTER_BLADE= get_sprite_stack_list(get_image('Sprites/Vehicles/Attack helicopter - Blade.png'), 118)

SPRITE_AA_SITE_MISSILE = get_sprite_stack_list(get_image('Sprites/Vehicles/AA Site - Missile.png'), 50)
SPRITE_AA_SITE_GENERATOR = get_sprite_stack_list(get_image('Sprites/Vehicles/AA Site - Energy Generator.png'), 50)
SPRITE_AA_SITE_SHIELD = get_sprite_stack_list(get_image('Sprites/Vehicles/AA Site - Shield Generator.png'), 30)

SPRITE_AA_SITE_LASER = get_sprite_stack_list(get_image('Sprites/Vehicles/AA Site - Laser.png'), 50)
SPRITE_AA_SITE_TURRET = get_sprite_stack_list(get_image('Sprites/Vehicles/AA Site - Laser Turret.png'), 12)

SPRITE_AA_SITE_FACTORY_SHEET = get_image('Sprites/Vehicles/AA Site - Drone Factory.png')
SPRITE_AA_SITE_FACTORY = [
    get_sprite_stack_list(SPRITE_AA_SITE_FACTORY_SHEET.subsurface((0 + 50 * p, 0, 50, 1250)), 50) for p in range(13)
]


# |Radio transmission sprites|-----------------------------------------------------------------------------------------
def desheetator_radio(sprite_sheet, height):
    return [
        sprite_sheet.subsurface((000, height, 64, 64)),  # 0 Normal
        sprite_sheet.subsurface((+64, height, 64, 64)),  # 1 Happy
        sprite_sheet.subsurface((128, height, 64, 64)),  # 2 Surprised
        sprite_sheet.subsurface((192, height, 64, 64)),  # 3 Angry
        sprite_sheet.subsurface((256, height, 64, 64)),  # 4 Worried
        sprite_sheet.subsurface((320, height, 64, 64)),  # 5 Sad
    ]


SPRITE_RADIO_DEV = pg.image.load(os.path.join("Sprites/Dev Comment.png")).convert_alpha()
SPRITE_SHEET_RADIO = pg.image.load(os.path.join("Sprites/Radio Portrait Sprite Sheet.png")).convert()

# Allies and Curtis
SPRITE_RADIO_MAKOTO = desheetator_radio(SPRITE_SHEET_RADIO, 768)

SPRITE_RADIO_VIVIANNE = desheetator_radio(SPRITE_SHEET_RADIO, 0)
SPRITE_RADIO_CURTIS = desheetator_radio(SPRITE_SHEET_RADIO, 64)
SPRITE_RADIO_LAWRENCE = desheetator_radio(SPRITE_SHEET_RADIO, 128)
SPRITE_RADIO_MARK = desheetator_radio(SPRITE_SHEET_RADIO, 128 + 64)

SPRITE_RADIO_EMPLOYER = desheetator_radio(SPRITE_SHEET_RADIO, 256)

SPRITE_RADIO_LORD = desheetator_radio(SPRITE_SHEET_RADIO, 256 + 64)
SPRITE_RADIO_EMPEROR = desheetator_radio(SPRITE_SHEET_RADIO, 256 + 64 + 64)
SPRITE_RADIO_WIZARD = desheetator_radio(SPRITE_SHEET_RADIO, 256 + 64 + 64 + 64)
SPRITE_RADIO_SOVEREIGN = desheetator_radio(SPRITE_SHEET_RADIO, 256 + 64 + 64 + 64 + 64)
SPRITE_RADIO_DUKE = desheetator_radio(SPRITE_SHEET_RADIO, 256 + 64 + 64 + 64 + 64 + 64)
SPRITE_RADIO_JESTER = desheetator_radio(SPRITE_SHEET_RADIO, 256 + 64 + 64 + 64 + 64 + 64 + 64)
SPRITE_RADIO_CONDOR = desheetator_radio(SPRITE_SHEET_RADIO, 256 + 64 + 64 + 64 + 64 + 64 + 64 + 64)


def desheetator(sprite_sheet, thiccness=32):
    # This function transform the sprite sheet into something usable by the game
    output = [{"Walk": []},
              {"Walk": []},
              {"Walk": []},
              {"Walk": []},
              {"Walk": []},
              {"Walk": []}]


    for direction_count, direction in enumerate(output):
        # Need to rework that so that it works properly with the other animations
        for frame_count, animation in enumerate(direction):
            try:
                y_pos = {"Walk": 0,
                         }[animation]
            except KeyError:
                # rint("We got an issue captain")
                y_pos = sprite_sheet.get_height() // (thiccness * 6) - 1

            for frame in range(sprite_sheet.get_width() // thiccness):
                sprite = sprite_sheet.subsurface((thiccness * frame,
                                                  thiccness * direction_count + thiccness * 6 * y_pos,
                                                  thiccness, thiccness))
                # Removes empty sprites, animations have different animation length
                if pg.transform.average_color(sprite) != (0, 0, 0, 0):
                    output[direction_count][animation].append(sprite)

    # Returns the processed sheet
    return output


# |Environment Sprites|-------------------------------------------------------------------------------------------------
def colour_swap_tile_set(base_tile_set, old_colour, new_colour):
    new_tile_set = []
    for x in base_tile_set:
        new_tile_set.append(swap(x.copy(), old_colour, new_colour))
    return new_tile_set


# Tile sets
def tile_set_creator(base_tiles):
    return [
        base_tiles.subsurface((TILES_SIZE, TILES_SIZE, TILES_SIZE, TILES_SIZE)),
        base_tiles.subsurface((00, 00, TILES_SIZE, TILES_SIZE)),
        base_tiles.subsurface((TILES_SIZE, 00, TILES_SIZE, TILES_SIZE)),
        base_tiles.subsurface((TILES_SIZE * 2, 00, TILES_SIZE, TILES_SIZE)),
        base_tiles.subsurface((00, TILES_SIZE, TILES_SIZE, TILES_SIZE)),
        base_tiles.subsurface((TILES_SIZE * 2, TILES_SIZE, TILES_SIZE, TILES_SIZE)),
        base_tiles.subsurface((00, TILES_SIZE * 2, TILES_SIZE, TILES_SIZE)),
        base_tiles.subsurface((TILES_SIZE, TILES_SIZE * 2, TILES_SIZE, TILES_SIZE)),
        base_tiles.subsurface((TILES_SIZE * 2, TILES_SIZE * 2, TILES_SIZE, TILES_SIZE))
    ]


def overlay_applier_but_better(base, overlay):
    # overlay_applier does not exist
    new_tile_set = []
    overlay = tile_set_creator(overlay)
    for x in enumerate(base):
        merged = x[1].copy()
        merged.blit(overlay[x[0]], (0, 0))
        new_tile_set.append(merged)
    return new_tile_set


TILES_SIZE = 32
TILE_BORDER = pg.image.load("Sprites/Environment/Tiles/Border.png").convert_alpha()
# Bases
TILES_INDUSTRIAL = get_image('Sprites/Environment/Industrial.png')
TILES_ENTRY_GATE = get_image('Sprites/Environment/Industrial Gate.png')
TILES_RED_DESERT = get_image('Sprites/Environment/Sand.png')
TILES_SAND_CAVES = get_image('Sprites/Environment/Sand Cave.png')
TILES_IRON_MINES = get_image('Sprites/Environment/Iron Mines.png')
TILES_SALT_FLATS = get_image('Sprites/Environment/Salt Flat.png')

# Tile sets
TILE_SET_INDUSTRIAL_FLOOR = tile_set_creator(TILES_INDUSTRIAL)
TILE_SET_INDUSTRIAL_WALL = tile_set_creator(TILES_INDUSTRIAL.subsurface((96, 0, 96, 96)))

TILE_SET_ENTRY_GATE_FLOOR = tile_set_creator(TILES_ENTRY_GATE)
TILE_SET_ENTRY_GATE_WALL = tile_set_creator(TILES_ENTRY_GATE.subsurface((96, 0, 96, 96)))

TILE_SET_RED_DESERT_FLOOR = tile_set_creator(TILES_RED_DESERT)
TILE_SET_RED_DESERT_WALL = tile_set_creator(TILES_RED_DESERT.subsurface((96, 0, 96, 96)))

TILE_SET_SAND_CAVES_FLOOR = tile_set_creator(TILES_SAND_CAVES)
TILE_SET_SAND_CAVES_WALL = tile_set_creator(TILES_SAND_CAVES.subsurface((96, 0, 96, 96)))

TILE_SET_IRON_MINES_FLOOR = tile_set_creator(TILES_IRON_MINES)
TILE_SET_IRON_MINES_WALL = tile_set_creator(TILES_IRON_MINES.subsurface((96, 0, 96, 96)))

TILE_SET_SALT_FLATS_FLOOR = tile_set_creator(TILES_SALT_FLATS)
TILE_SET_SALT_FLATS_WALL = tile_set_creator(TILES_SALT_FLATS.subsurface((96, 0, 96, 96)))
# 96, 32


# |Item sprites|--------------------------------------------------------------------------------------------------------
SPRITE_EMPTY = pg.image.load(os.path.join('Sprites/Weapon/Anime.png')).convert_alpha()
# SPRITE_LEAF = pg.image.load(os.path.join('Sprites/Effect/Leaf.png')).convert_alpha()
# SPRITE_LANDMINE = pg.image.load(os.path.join('Sprites/Items/Claymore.png')).convert_alpha()
SPRITE_RIOT_SHIELD = pg.image.load(os.path.join('Sprites/Items/Riot Shield.png')).convert_alpha()
SPRITES_RIOT_SHIELD = [
    SPRITE_RIOT_SHIELD.subsurface((32, 00, 16, 32)),
    SPRITE_RIOT_SHIELD.subsurface((16, 00, 16, 32)),
    SPRITE_RIOT_SHIELD.subsurface((00, 00, 16, 32)),
    SPRITE_RIOT_SHIELD.subsurface((00, 32, 16, 32)),
    SPRITE_RIOT_SHIELD.subsurface((16, 32, 16, 32)),
    SPRITE_RIOT_SHIELD.subsurface((32, 32, 16, 32))
]

# |Mission sprites|-----------------------------------------------------------------------------------------------------
# |Random Sprites|------------------------------------------------------------------------------------------------------
SPRITE_LAWRENCE_SWORD = pg.image.load(os.path.join("Sprites/Weapon/Son's Cutlass.png")).convert_alpha()
SPRITE_LORD_GAUNTLET = get_image('Sprites/Effect/Gauntlet.png')
SPRITE_DUKE_AXE = get_image("Sprites/Weapon/THR-1/Chain Axe - Axe.png")
SPRITE_CURTIS_WAR = get_image("Sprites/Weapon/War.png")

SPRITE_STUNNED = [pg.image.load(os.path.join("Sprites/Effect/Stunned 1.png")).convert_alpha(),
                  pg.image.load(os.path.join("Sprites/Effect/Stunned 2.png")).convert_alpha()]


def none(arg1=1, arg2=2, arg3=3):
    # It does jack shit and is the single most used function in the whole damn game
    pass


get_random_element_from_list = lambda l : l[random.randint(0, len(l)-1)]


# |Shadows|-------------------------------------------------------------------------------------------------------------
class ShadowBasic:
    def __init__(self, pos, dimensions, duration=1):
        self.pos = pos
        self.dimensions = dimensions
        self.duration = duration
        # self.draw = None


class ShadowCircle(ShadowBasic):
    def draw(self, surface_shadow, round_scrolling, camera_rect, colour=WHITE):
        pg.draw.circle(surface_shadow, colour,
                       [self.pos[0] + round_scrolling[0], self.pos[1] + round_scrolling[1]], self.dimensions)


class ShadowRect(ShadowBasic):
    def draw(self, surface_shadow, round_scrolling, camera_rect, colour=WHITE):
        pg.draw.rect(surface_shadow, colour,
                     (self.pos[0] + round_scrolling[0], self.pos[1] + round_scrolling[1],
                      self.dimensions[0], self.dimensions[1]))


str_to_list = lambda s: [c for c in s]
# |Various screens for game stuff|--------------------------------------------------------------------------------------
class PseudoPlayer:
    def __init__(self):
        # This class can be used have control over the various menus when you can get them from the player class
        self.control = get_from_json("Key binds.json", "Keyboard")

        try:
            self.controller_control = get_from_json("Controller binds.json", "Everything")
        except FileNotFoundError:
            print_to_error_stream("Controller binds.json not found, creating new one")
            dict_to_json("Controller binds.json", DEFAULT_CONTROLLER_BINDS)
            self.controller_control = DEFAULT_CONTROLLER_BINDS
            if len(ALL_CONTROLLERS[0]) > 0:
                print_to_error_stream("Notice - Default controller binds are loaded")

        self.input = get_default_inputs()
        self.mouse_control = {}
        self.input_mode = "Keyboard"

    def get_input(self, keys):
        keyboard_mouse_input(self, keys, False)
        input_copy = self.input.copy()

        keyboard = False
        for keyboard_input in input_copy:
            if input_copy[keyboard_input]:
                keyboard = True
                break

        controller_input(self, True)

        if keyboard:
            self.input_mode = "Keyboard"
        if self.input != input_copy:
            self.input_mode = "Controller"


class UniversalMenuLogic:
    def __init__(self, options, width=1, key_binds={"Select Up": "Up", "Select Down": "Down",
                                           "Select Left": "Left", "Select Right": "Right",
                                           "Confirm": "Interact", "Return": "Reload"}, default_return=-1):
        self.key_pressed = DEFAULT_KEY_PRESSED
        self.key_cooldown = DEFAULT_KEY_COOLDOWN
        self.controller = PseudoPlayer()
        self.key_binds = key_binds
        self.keys = []

        self.options = options # The complex part
        # [
        #   {255, 176, 0
        #       "Name": <display name>,
        #       "Value": <number or string>,
        #       "On select": <function that happens when you choose an option>,
        #       "Render func": <string that correspond to the render function for the option>
        #   Optional
        #       "Slider": {"Limits": [<lower limit>, <upper limit>], "Mod": <int>, "Display mod": <int>},
        #   },
        #   ...
        # ]
        self.selected_option = 0
        self.max_option = len(self.options) - 1
        self.menu_mode = "Normal"
        self.pressing = False
        self.width = width
        self.colour_high_vis = AMBER
        self.colour_med_vis = UI_COLOUR_NEW_BACKDROP
        self.colour_controls = UI_COLOUR_TUTORIAL
        self.colour_low_vis = UI_COLOUR_NEW_BACKGROUND
        self.default_return = default_return

    def cooldown(self):
        self.key_pressed = self.key_cooldown
        play_sound("Menu move", "SFX")
        self.controller = PseudoPlayer()
        ppp = get_from_json("Key binds.json", "System")
        self.max_option = len(self.options) - 1 # Remove this line and the game will crash in the shop menu
        for i in ppp:
            SYSTEM_CONTROLS[i] = ppp[i]

    # |Menu Methods|----------------------------------------------------------------------------------------------------
    def menu_mode_normal(self, WIN, CLOCK):
        # Move on Y
        if self.controller.input[self.key_binds["Select Up"]]:
            self.cooldown()
            if self.selected_option > 0:
                self.selected_option -= 1
            elif self.selected_option == 0 and not self.pressing:
                self.selected_option = self.max_option
                self.key_pressed *= 2
            self.pressing = True

        elif self.controller.input[self.key_binds["Select Down"]]:
            self.cooldown()
            if self.max_option > self.selected_option:
                self.selected_option += 1
            elif self.max_option == self.selected_option and not self.pressing:
                self.selected_option = 0
                self.key_pressed *= 2
            self.pressing = True

        else:
            self.pressing = False

        # Do something
        if self.controller.input[self.key_binds["Confirm"]]:
            selected_option_data = self.options[self.selected_option]
            play_sound("Menu confirm", "SFX")
            if selected_option_data["On select"] == "Return":
                return selected_option_data["Value"]
            self.menu_mode = selected_option_data["On select"]
            self.key_pressed = self.key_cooldown
        if self.controller.input[self.key_binds["Return"]]:
            return self.options[self.default_return]["Value"]
        return False

    def menu_mode_slider(self, WIN, CLOCK):
        option = self.options[self.selected_option]
        mod = option["Slider"]["Mod"]
        # Modify values
        if self.controller.input[self.key_binds["Select Left"]] and option["Slider"]["Limits"][0] + mod <= option["Value"]:
            option["Value"] -= mod
            self.cooldown()
        if self.controller.input[self.key_binds["Select Right"]] and option["Slider"]["Limits"][1] - mod >= option["Value"]:
            option["Value"] += mod
            self.cooldown()

        # Do something
        if self.controller.input[self.key_binds["Return"]] or self.controller.input[self.key_binds["Confirm"]]:
            play_sound("Menu back")
            self.menu_mode = "Normal"
            self.cooldown()
        self.options[self.selected_option] = option
        return False

    def menu_mode_slider_one_step(self, WIN, CLOCK):
        option = self.options[self.selected_option]
        mod = option["Slider"]["Mod"]

        option["Value"] += mod
        if option["Value"] > option["Slider"]["Limits"][1]:
            option["Value"] = option["Slider"]["Limits"][0]

        self.cooldown()
        self.menu_mode = "Normal"
        self.options[self.selected_option] = option
        return False

    def menu_mode_choose(self, WIN, CLOCK):
        option = self.options[self.selected_option]
        choose = option["Choose"]   # "Choose": {"List": list}
        # Modify values
        if self.controller.input[self.key_binds["Select Left"]] and 0 < option["Value"]:
            option["Value"] -= 1
            self.cooldown()
        if self.controller.input[self.key_binds["Select Right"]] and len(choose["List"])-1 > option["Value"]:
            option["Value"] += 1
            self.cooldown()

        # Do something
        if self.controller.input[self.key_binds["Return"]] or self.controller.input[self.key_binds["Confirm"]]:
            play_sound("Menu back")
            self.menu_mode = "Normal"
            self.cooldown()
        self.options[self.selected_option] = option
        return False

    def menu_mode_key_input(self, WIN, CLOCK):
        option = self.options[self.selected_option]
        mode = option["Key Input"]["Mode"]
        key_change = False
        mouse_key = pg.mouse.get_pressed(3)
        # Look for inputs
        if mode in ["Keyboard", "System"]:
            for i in keyboard_input_ref:
                for k in i:
                    if self.keys[k]:
                        option["Value"] = k
                        key_change = True
                        break
        else:
            for k in range(len(mouse_key)):
                if mouse_key[k]:
                    option["Value"] = k
                    key_change = True
                    break

        # Do something when you get an input
        if key_change:
            play_sound("Menu back")
            self.menu_mode = "Normal"
            self.cooldown()
            self.options[self.selected_option] = option
        return False

    def act(self, WIN, CLOCK):
        self.keys = pg.key.get_pressed()
        needed_in_menu_and_game(WIN, self.keys)
        self.controller.get_input(self.keys)

        if self.key_pressed == 0:
            return {
                "Normal": self.menu_mode_normal,
                "Slider": self.menu_mode_slider,
                "Slider One Step": self.menu_mode_slider_one_step,
                "Choose": self.menu_mode_choose,
                "Key Input": self.menu_mode_key_input,
            }[self.menu_mode](WIN, CLOCK)
        else:
            self.key_pressed -= 1
        return False

    # |Draw Methods|----------------------------------------------------------------------------------------------------
    def draw_text_only(self, surface, op, pos, font):
        colour = self.colour_high_vis
        if op == self.options[self.selected_option]:
            colour = self.colour_low_vis
        surface.blit(font.render(write_textline(f"{op['Name']}", send_back=True), True, colour), pos)

    def draw_slider(self, surface, op, pos, font):
        colour = self.colour_high_vis
        if op == self.options[self.selected_option]:
            colour = self.colour_low_vis
        surface.blit(font.render(write_textline(f"{op['Name']}", send_back=True), True, colour), pos)

        bar_x = pos[0] + 110
        bar_width = 100
        pg.draw.rect(surface, (37, 42, 38), (pos[0], pos[1]+12, bar_width + 110, 2))
        value = round(op['Value'], 1)
        colour = self.colour_med_vis
        if self.menu_mode == "Slider" and op == self.options[self.selected_option]:
            colour = self.colour_high_vis
        bar_shown = bar_width * (value / op['Slider']['Limits'][1])
        font_colour = self.colour_low_vis
        x_mod = 0
        if bar_shown < 18:
            font_colour = self.colour_high_vis
            x_mod = bar_shown

        pg.draw.rect(surface, UI_COLOUR_BACKDROP, (bar_x, pos[1], bar_width, 10))
        pg.draw.rect(surface, colour, (bar_x, pos[1],
                                       # bar_width * (value * op['Slider']["Display mod"]),
                                       bar_shown,
                                       10))
        # Write the value
        surface.blit(font.render(f"{value * op['Slider']['Display mod']}", True, font_colour), (bar_x + x_mod, pos[1]))

    def draw_choose(self, surface, op, pos, font):
        option = self.options[self.selected_option]
        colour = self.colour_high_vis
        if op == option:
            colour = self.colour_low_vis
        surface.blit(font.render(write_textline(f"{op['Name']}", send_back=True), True, colour), pos)

        colour = self.colour_low_vis
        for other_values in self.options:
            if other_values["Value"] != op["Value"]: continue
            if other_values == op: continue
            colour = RED
            break
        if self.menu_mode == "Choose" and op == option:
            colour = self.colour_high_vis
        bar_x = pos[0] + 110
        surface.blit(font.render(op["Choose"]["List"][op["Value"]], True, colour), [bar_x, pos[1]])
        if 0 < op["Value"]:
            surface.blit(font.render("<", True, colour), [bar_x-8, pos[1]])
        if len(op["Choose"]["List"])-1 > op["Value"]:
            surface.blit(font.render(">", True, colour), [bar_x+100, pos[1]])

    def draw_key_input(self, surface, op, pos, font):
        colour = self.colour_high_vis
        option = self.options[self.selected_option]
        if op == option:
            colour =  self.colour_low_vis
        # add cases to handle mouse
        surface.blit(font.render(write_textline(f"{op['Name']}", send_back=True), True, colour), pos)

        colour =  self.colour_low_vis
        for other_values in self.options:
            if other_values["Value"] != op["Value"]: continue
            if other_values == op: continue
            colour = RED
            break

        if self.menu_mode == "Key Input" and op == option:
            colour = self.colour_high_vis


        bar_x = pos[0] + 110
        mode = op["Key Input"]["Mode"]
        if mode in ["Keyboard", "System"]:
            surface.blit(font.render(pg.key.name(op["Value"]).capitalize(), True, colour), [bar_x, pos[1]])
            return
        surface.blit(font.render(f'{["Left", "Middle", "Right"][op["Value"]]} Mouse', True, colour), [bar_x, pos[1]])

    def draw(self, surface, base_pos, draw_move=True):
        font = create_temp_font_1(450)
        # Draw instructions
        if draw_move:
            surface.blit(font.render(
                f"{write_control(self.controller, 'Up', is_move=True)}"
                f"{write_control(self.controller, 'Down', fucking_hell=False)}"
                f"{write_control(self.controller, 'Left', fucking_hell=False)}"
                f"{write_control(self.controller, 'Right', fucking_hell=False)}"
                f", {write_textline('Select')}", True, self.colour_controls), base_pos)
        surface.blit(font.render(
            f"{write_control(self.controller, self.key_binds['Return'])} {write_textline('Menu Go Back')}, "
            f"{write_control(self.controller, self.key_binds['Confirm'])} {write_textline('Menu Choose')}", True, self.colour_controls),
            (base_pos[0], base_pos[1] + 15)
        )
        # Draw options
        y = base_pos[1] + 30

        for count, op in enumerate(self.options):
            # surface.blit(self.sprites[int(count == self.selected_option)], (base_pos[0] - 2, y - 2))
            if count == self.selected_option:
                pg.draw.rect(surface, self.colour_high_vis, (base_pos[0] - 2, y - 2, 80 + 24 * self.width, 10 + 4))
            {
                "Text only": self.draw_text_only,
                "Slider": self.draw_slider,
                "Choose": self.draw_choose,
                "Key Input": self.draw_key_input
            }[op["Render func"]](surface, op, [base_pos[0], y], font)
            y += 18


class UICommunicationLog:
    def __init__(self, comms, pos, speed=3, offset=20, text_offset=60, font_func=create_temp_font_2):
        self.pos = pos
        self.elements_to_show = comms
        # {"Sender": "THR-1", "Message": str_to_list("I AM MAKING MAC AND CHEESE AND NOBODY CAN STOP ME!")},
        self.speed = speed
        self.offset = offset
        self.text_offset = text_offset
        self.transmission_list = []
        self.font_func = font_func
        self.font = self.font_func(450, font_name="Sprites/JetBrainsMono-SemiBold.ttf")
        self.cooldown = 0
        self.font_colour = AMBER

    def act(self):
        if self.cooldown <= 0:
            if self.elements_to_show:
                to_show = self.elements_to_show[0]
                if to_show["Sender"] != "":
                    # Create new transmission
                    self.transmission_list.append({"Sender": to_show["Sender"], "Message": ""})
                    to_show["Sender"] = ""
                    self.cooldown = self.speed * 3
                elif to_show["Message"]:
                    self.transmission_list[-1]["Message"] += to_show["Message"][0]
                    to_show["Message"].pop(0)
                    self.cooldown = self.speed
                else:
                    self.elements_to_show.pop(0)
                    self.cooldown = self.speed * 20
        self.cooldown -= 1

    def draw(self, surface_to_draw, z=1):
        self.font = self.font_func(int(450 * z), font_name="Sprites/JetBrainsMono-SemiBold.ttf")

        y1 = self.pos[1]
        x1 = self.pos[0]
        x2 =  self.pos[0] + self.text_offset
        text_h = self.offset
        negative_height = len(self.transmission_list) * text_h * z

        for count, x in enumerate(self.transmission_list):
            sender = x["Sender"]
            message = x["Message"]

            surface_to_draw.blit(self.font.render(sender, True, self.font_colour), (x1 * z, y1 - negative_height + count * text_h * z))
            surface_to_draw.blit(self.font.render(message, True, self.font_colour), (x2 * z, y1 - negative_height + count * text_h * z))


def confirmation_popup(WIN, CLOCK, pos, options, text="", do_crt=True, popup_width=256):
    menu_logic = UniversalMenuLogic(
        options
    )
    menu_overlay = pg.image.load(os.path.join("Sprites/UI/Overlay.png")).convert_alpha()
    frame_1 = some_bullshit_for_transitions(WIN)
    draw = True
    text_lines = split_text(text, limit=80)
    while True:
        do_shit = menu_logic.act(WIN, CLOCK)
        if do_shit:
            return do_shit
        # |Draw|--------------------------------------------------------------------------------------------------------
        if draw:
            width, height = 630, 450
            # frame = pg.Surface((630, 450))
            frame = pg.Surface((630, 450))
            surface_to_draw = frame
            WIN.fill(BLACK)

            temp_ui_font = create_temp_font_1(height)
            surface_to_draw.fill(UI_COLOUR_BACKGROUND)

            surface_to_draw.blit(frame_1, (0, 0))

            # width, height
            # 80+24, 10+4
            # +100

            height_mod = 0
            if text != "":
                #
                height_mod = 18 * len(text_lines)
            popup_height = 17 * len(menu_logic.options) + 30 + height_mod
            popup_uni = pg.Surface((popup_width, popup_height))
            popup_uni.fill(UI_COLOUR_NEW_BACKGROUND)
            menu_logic.draw(popup_uni, [0, height_mod])
            if text != "":
                # text_lines
                for count, text_line in enumerate(text_lines):
                    rendered_text = temp_ui_font.render(text_line, True, AMBER)
                    popup_uni.blit(rendered_text, [20, count * 18])

            surface_to_draw.blit(popup_uni, pos)
            pg.draw.rect(surface_to_draw, AMBER, (pos[0] - 2, pos[1] - 2, popup_width + 4, popup_height + 4), width=2)

            if do_crt:
                crt(surface_to_draw)
                surface_to_draw.blit(menu_overlay, [0, 0])
            scale_render(WIN, surface_to_draw, CLOCK)
            pg.display.update()
            CLOCK.tick(60)


def title_screen(WIN, CLOCK, controls):
    logo = pg.image.load(os.path.join("Sprites/Logo.png")).convert_alpha()
    menu_overlay = pg.image.load(os.path.join("Sprites/UI/Overlay.png")).convert_alpha()

    options = [
        {"Name": "Start", "Value": "Start", "On select": "Return", "Render func": "Text only"},
    ]
    menu_logic = UniversalMenuLogic(options)

    chosen_option = 0
    colour = [0, 0, 0]
    time_spent_on_menu = 0
    modifier = 1
    time_colour = 0
    x_mod = 0
    starting_intro = 0
    draw = True
    intro_start_time = 85 * 19
    # intro_start_time = 60
    transition_time = 90
    while True:
        # Restarts the intro after a bit
        do_shit = menu_logic.act(WIN, CLOCK)
        if do_shit:
            return

        time_spent_on_menu += 1
        # |Draw|--------------------------------------------------------------------------------------------------------
        if draw:
            # This is to make it scale
            # win_width, win_height = width, height
            win_width, win_height = 630, 450
            layout_zero = [0, 0]

            # frame = pg.Surface(FRAME_MAX_SIZE)
            frame = pg.Surface((630, 450))
            surface_to_draw = frame
            WIN.fill(BLACK)

            surface_to_draw.fill(UI_COLOUR_BACKGROUND)
            menu_logic.draw(surface_to_draw, [315-124/2, 250], draw_move=False)

            # Write the name of the game and the current version
            surface_to_draw.blit(logo, [315 - logo.get_width()/2, 100])

            surface_to_draw.blit(FONTS["sma"].render(f"{write_textline('Version')}: {VERSION}", True, AMBER),
                                 [15 + layout_zero[0], 450-25])

            crt(surface_to_draw)
            surface_to_draw.blit(menu_overlay, [0, 0])
            scale_render(WIN, surface_to_draw, CLOCK)
            pg.display.update()
            CLOCK.tick(60)

        if starting_intro and time_spent_on_menu >= intro_start_time + transition_time:
            game_intro(WIN, CLOCK, controls, PseudoPlayer())

            # Reset the thing
            time_spent_on_menu, modifier, time_colour, x_mod = 0, 1, 0, 0


def main_menu(WIN, CLOCK):
    transition = True
    frame_1 = some_bullshit_for_transitions(WIN)

    win_copy = WIN.copy()

    menu_sprite = pg.image.load(os.path.join("Sprites/UI/Settings Screen.png")).convert_alpha()
    menu_overlay = pg.image.load(os.path.join("Sprites/UI/Overlay.png")).convert_alpha()

    options = [
        {"Name": "Start Run", "Value": "Start", "On select": "Return", "Render func": "Text only"},
        {"Name": "Versus Mode", "Value": "Versus", "On select": "Return", "Render func": "Text only"},
        # {"Name": "Tutorials", "Value": "Tutorials", "On select": "Return", "Render func": "Text only"},
        {"Name": "Options", "Value": "Options", "On select": "Return", "Render func": "Text only"},
        {"Name": "Credits", "Value": "Credits", "On select": "Return", "Render func": "Text only"},
        {"Name": "Databank", "Value": "Databank", "On select": "Return", "Render func": "Text only"},
        {"Name": "Quit Game", "Value": "Return", "On select": "Return", "Render func": "Text only"},
    ]
    menu_logic = UniversalMenuLogic(options)
    x_mod = -210-63
    draw = True
    while True:
        if x_mod < 0:
            x_mod += 21
        # Select
        do_shit = menu_logic.act(WIN, CLOCK)
        if do_shit:
            if do_shit == "Start":
                player_party = party_selection_menu(WIN, CLOCK)
                if player_party != "Return":
                    # return_value = do_shit
                    return_value = player_party
                    break
                win_copy = WIN.copy()
                transition, frame_1 = menu_transition_start(WIN)
            if do_shit == "Versus":
                return_value = "Versus"
                break

            if do_shit == "Options":
                settings_menu(WIN, CLOCK)
            if do_shit == "Credits":
                game_credits(WIN, CLOCK)
                win_copy = WIN.copy()
                transition, frame_1 = menu_transition_start(WIN)
            if do_shit == "Databank":
                encyclopedia_menu(WIN, CLOCK)
                # pg.mixer.music.pause()
                win_copy = WIN.copy()
                transition, frame_1 = menu_transition_start(WIN)
            if do_shit == "Return":
                sys.exit()
            menu_logic.cooldown()

        # |Draw|--------------------------------------------------------------------------------------------------------
        if draw:
            # width, height = WIN.get_size()
            width, height = 630, 450
            frame = pg.Surface((630, 450))
            surface_to_draw = frame
            WIN.fill(BLACK)

            temp_ui_font = create_temp_font_1(height)
            surface_to_draw.fill(UI_COLOUR_BACKGROUND)

            surface_to_draw.blit(menu_sprite, [x_mod, 0])
            surface_to_draw.blit(temp_ui_font.render(write_textline("Main title"), True, AMBER), (25 + x_mod, 25))
            menu_logic.draw(surface_to_draw, [30 + x_mod, 50])

            crt(surface_to_draw)
            surface_to_draw.blit(menu_overlay, [0, 0])
            scale_render(WIN, surface_to_draw, CLOCK)
            if transition:
                transition = False
                menu_transition_doom_screen_melt(WIN, CLOCK, WIN, win_copy)
                play_music("Menu")

            pg.display.update()
        CLOCK.tick(60)

    return return_value


def party_selection_menu(WIN, CLOCK):
    # Choose which input to modify
    transition = True
    frame_1 = some_bullshit_for_transitions(WIN)
    win_copy = WIN.copy()
    menu_overlay = pg.image.load(os.path.join("Sprites/UI/Overlay.png")).convert_alpha()
    thr1_sprite = pg.image.load(os.path.join("Sprites/UI/Party Selection/THR-1.png")).convert_alpha()
    thr1_sprite_unselected = pg.image.load(os.path.join("Sprites/UI/Party Selection/THR-1.png")).convert_alpha()
    thr1_sprite_unselected.set_alpha(128)
    zoar_sprite = pg.image.load(os.path.join("Sprites/UI/Party Selection/Zoar.png")).convert_alpha()
    zoar_sprite_unselected = pg.image.load(os.path.join("Sprites/UI/Party Selection/Zoar.png")).convert_alpha()
    zoar_sprite_unselected.set_alpha(128)
    zoar_unlocked = get_from_json("Save.json", "Zoar unlocked")

    menu_sprite = pg.image.load(os.path.join("Sprites/UI/Selection Screen.png")).convert_alpha()

    options = [
        {"Name": "THR-1", "Value": "THR-1", "On select": "Return", "Render func": "Text only"},
        {"Name": "Return", "Value": "Return", "On select": "Return", "Render func": "Text only"},
        {"Name": "Zoar", "Value": "Zoar Colonists", "On select": "Return", "Render func": "Text only"},
    ]

    menu_logic = UniversalMenuLogic(options, key_binds={"Select Up": "Left", "Select Down": "Right",
                                           "Select Left": "Left", "Select Right": "Right",
                                           "Confirm": "Interact", "Return": "Reload"}, width=2, default_return=1)

    x_mod = 0
    draw = True
    while True:
        # Select
        do_shit = menu_logic.act(WIN, CLOCK)
        if do_shit:
            if do_shit == "Zoar Colonists" and not zoar_unlocked:
                pass
            else:
                return do_shit

        # |Draw|--------------------------------------------------------------------------------------------------------
        if draw:
            width, height = 630, 450
            frame = pg.Surface((630, 450))
            surface_to_draw = frame
            WIN.fill(BLACK)

            surface_to_draw.fill(UI_COLOUR_BACKGROUND)
            surface_to_draw.blit(menu_sprite, [x_mod, 0])

            thr1 = thr1_sprite_unselected
            if menu_logic.options[menu_logic.selected_option]["Value"] == "THR-1":
                thr1 = thr1_sprite
            surface_to_draw.blit(thr1, [0+8, 450-296-96])

            col = (AMBER[0]//2, AMBER[1]//2, AMBER[2]//2)
            if menu_logic.options[menu_logic.selected_option]["Value"] == "Return":
                col = AMBER
            temp_ui_font = create_temp_font_1(height)

            text = temp_ui_font.render(write_textline("Party Select Screen return"), True, BLACK)
            rect_width, rect_height = text.get_width() * 1.5, text.get_height() * 1.5
            x, y = 315, 340
            pg.draw.rect(surface_to_draw, col, (x - rect_width // 2, y - rect_height // 2, rect_width, rect_height))
            surface_to_draw.blit(text, (x - text.get_width() // 2, y - text.get_height() // 2))

            zoar = zoar_sprite_unselected
            zoar_selected = False
            if menu_logic.options[menu_logic.selected_option]["Value"] == "Zoar Colonists":
                zoar_selected = True
                if zoar_unlocked:
                    zoar = zoar_sprite
            surface_to_draw.blit(zoar, [630-192-8, 450-296-96])

            if not zoar_unlocked:
                col = (AMBER[0] // 2, AMBER[1] // 2, AMBER[2] // 2)
                if menu_logic.options[menu_logic.selected_option]["Value"] == "Zoar Colonists":
                    col = AMBER
                text = temp_ui_font.render(write_textline("Party Select Zoar not unlocked"),
                                        True, BLACK)
                rect_width, rect_height = text.get_width() * 1.05, text.get_height() * 1.5
                x, y = 515, 260
                pg.draw.rect(surface_to_draw, col, (x - rect_width // 2, y - rect_height // 2, rect_width, rect_height))
                surface_to_draw.blit(
                    text, [x  - text.get_width() // 2, y - text.get_height() // 2])

            surface_to_draw.blit(menu_overlay, [0, 0])
            # Add controls
            crt(surface_to_draw)
            scale_render(WIN, surface_to_draw, CLOCK)
            if transition:
                transition = False
                menu_transition_doom_screen_melt(WIN, CLOCK, WIN, win_copy)
            pg.display.update()
        CLOCK.tick(60)


def settings_menu(WIN, CLOCK, also_pause=False):
    pg.mixer.music.pause()
    back_to_title = False
    frame_1 = some_bullshit_for_transitions(WIN)
    transition = False
    win_copy = WIN.copy()
    frame_1.set_alpha(128)
    menu_sprite = pg.image.load(os.path.join("Sprites/UI/Settings Screen.png")).convert_alpha()
    menu_overlay = pg.image.load(os.path.join("Sprites/UI/Overlay.png")).convert_alpha()

    # To prevent errors
    try:
        settings_value = get_from_json("Settings.json", "Everything")
    except FileNotFoundError:
        print_to_error_stream("File Setting.json missing, creating a new one")
        settings_value = {"SFX": 5.0, "Music": 5.0, "Voice": 5.0, "Screen shake": 1.0, "Language": 0}
        dict_to_json("Settings.json", settings_value)

    options = [
        {"Name": "SFX", "Value": settings_value["SFX"], "On select": "Slider", "Render func": "Slider",
            "Slider": {"Limits": [0, 10], "Mod": 0.5, "Display mod": 1}},
        {"Name": "Music", "Value": settings_value["Music"], "On select": "Slider", "Render func": "Slider",
            "Slider": {"Limits": [0, 10], "Mod": 0.5, "Display mod": 1}},
        {"Name": "Voice", "Value": settings_value["Voice"], "On select": "Slider", "Render func": "Slider",
         "Slider": {"Limits": [0, 10], "Mod": 0.5, "Display mod": 1}},
        {"Name": "Screen shake", "Value": settings_value["Screen shake"], "On select": "Slider", "Render func": "Slider",
            "Slider": {"Limits": [0.01, 5], "Mod": 0.5, "Display mod": 1}},
        # {"Name": "Language", "Value": settings_value["Language"], "On select": "Slider", "Render func": "Slider", "Slider": {"Limits": [0, 1], "Mod": 0.01, "Display mod": 1}},
        {"Name": "Rebind", "Value": "Rebind", "On select": "Return", "Render func": "Text only"},
        {"Name": "Menu Quit", "Value": "Quit", "On select": "Return", "Render func": "Text only"},
    ]
    if also_pause:
        options = [
            {"Name": "SFX", "Value": settings_value["SFX"], "On select": "Slider", "Render func": "Slider",
             "Slider": {"Limits": [0, 10], "Mod": 0.5, "Display mod": 1}},
            {"Name": "Music", "Value": settings_value["Music"], "On select": "Slider", "Render func": "Slider",
             "Slider": {"Limits": [0, 10], "Mod": 0.5, "Display mod": 1}},
            {"Name": "Voice", "Value": settings_value["Voice"], "On select": "Slider", "Render func": "Slider",
             "Slider": {"Limits": [0, 10], "Mod": 0.5, "Display mod": 1}},
            {"Name": "Screen shake", "Value": settings_value["Screen shake"], "On select": "Slider",
             "Render func": "Slider",
             "Slider": {"Limits": [0.01, 10], "Mod": 0.5, "Display mod": 1}},
            {"Name": "Language", "Value": settings_value["Language"], "On select": "Slider", "Render func": "Slider",
             "Slider": {"Limits": [0, 1], "Mod": 0.01, "Display mod": 1}},
            {"Name": "Rebind", "Value": "Rebind", "On select": "Return", "Render func": "Text only"},
            {"Name": "Quit", "Value": "Return", "On select": "Return", "Render func": "Text only"},
            {"Name": "Menu Quit", "Value": "Quit", "On select": "Return", "Render func": "Text only"},
        ]
#         options.append({"Name": "Quit", "Value": "Return", "On select": "Return", "Render func": "Text only"})
    menu_logic = UniversalMenuLogic(options)
    x_mod = -210
    draw = True
    while True:
        if x_mod < 0:
            x_mod += 21
        # Select
        do_shit = menu_logic.act(WIN, CLOCK)
        if do_shit:
            if do_shit == "Rebind":
                rebind_menu_master(WIN, CLOCK)

            if do_shit in ["Return", "Quit"]:
                back_to_title = do_shit == "Return"
                break
            menu_logic.cooldown()

        # |Draw|--------------------------------------------------------------------------------------------------------
        if draw:
            # width, height = WIN.get_size()
            width, height = 630, 450
            frame = pg.Surface((630, 450))
            surface_to_draw = frame
            WIN.fill(BLACK)

            temp_ui_font = create_temp_font_1(height)
            surface_to_draw.fill(UI_COLOUR_BACKGROUND)

            surface_to_draw.blit(frame_1, (0, 0))
            surface_to_draw.blit(menu_sprite, [x_mod, 0])
            surface_to_draw.blit(temp_ui_font.render(write_textline("Settings title"), True, AMBER), (25 + x_mod, 25))
            menu_logic.draw(surface_to_draw, [30 + x_mod, 50])

            crt(surface_to_draw)
            surface_to_draw.blit(menu_overlay, [0, 0])

            scale_render(WIN, surface_to_draw, CLOCK)
            if transition:
                transition = False
                menu_transition_doom_screen_melt(WIN, CLOCK, WIN, win_copy)
            pg.display.update()
        CLOCK.tick(60)
    for x in range(10):
        x_mod -= 21
        if draw:
            # width, height = WIN.get_size()
            width, height = 630, 450
            frame = pg.Surface((630, 450))
            surface_to_draw = frame
            WIN.fill(BLACK)

            temp_ui_font = create_temp_font_1(height)
            surface_to_draw.fill(UI_COLOUR_BACKGROUND)

            surface_to_draw.blit(frame_1, (0, 0))
            surface_to_draw.blit(menu_sprite, [x_mod, 0])
            surface_to_draw.blit(temp_ui_font.render(write_textline("Settings title"), True, UI_COLOUR_FONT), (25 + x_mod, 25))
            menu_logic.draw(surface_to_draw, [30 + x_mod, 50])

            scale_render(WIN, surface_to_draw, CLOCK)
            if transition:
                transition = False
                menu_transition_doom_screen_melt(WIN, CLOCK, WIN, win_copy)
            crt(surface_to_draw)
            surface_to_draw.blit(menu_overlay, [0, 0])
            pg.display.update()
        CLOCK.tick(60)
    # Saves
    dict_to_json("Settings.json", {"SFX": menu_logic.options[0]["Value"],
                                   "Music": menu_logic.options[1]["Value"],
                                   "Voice": menu_logic.options[2]["Value"],
                                   "Screen shake": menu_logic.options[3]["Value"],
                                   "Language": 0
                                   })
    # {"SFX": 5.0, "Voice": 5.0, "Music": 5.0, "Render zoom": 1.0, "Screen shake": 1.0,
    #                   "Language": 0}

    # Handle music volume changes
    pg.mixer.music.set_volume(CURRENT_TRACK_INFO[0] * (get_from_json("Settings.json", "Music") / 10))
    pg.mixer.music.unpause()

    # Handle zoom changes
    # Handle screen shake change
    SCREEN_SHAKE_MOD[0] = round(get_from_json("Settings.json", "Screen shake"))
    return back_to_title


def rebind_menu_master(WIN, CLOCK):
    # Choose which input to modify
    pg.mixer.music.pause()

    menu_sprite = pg.image.load(os.path.join("Sprites/UI/Settings Screen.png")).convert_alpha()
    menu_overlay = pg.image.load(os.path.join("Sprites/UI/Overlay.png")).convert_alpha()

    options = [
        {"Name": "Keyboard & Mouse", "Value": "Keyboard & Mouse", "On select": "Return", "Render func": "Text only"},
        {"Name": "Controller", "Value": "Controller", "On select": "Return", "Render func": "Text only"},
        {"Name": "Quit menu", "Value": "Quit", "On select": "Return", "Render func": "Text only"},
    ]
    menu_logic = UniversalMenuLogic(options, width=2)
    x_mod = -210-63
    draw = True
    while True:
        if x_mod < 0:
            x_mod += 21
        # Select
        do_shit = menu_logic.act(WIN, CLOCK)
        if do_shit:
            if do_shit == "Keyboard & Mouse":
                rebind_menu_keyboard_mouse(WIN, CLOCK)
            if do_shit == "Controller":
                rebind_menu_controller(WIN, CLOCK)
            if do_shit == "Quit":
                break
            menu_logic.cooldown()

        # |Draw|--------------------------------------------------------------------------------------------------------
        if draw:
            # width, height = WIN.get_size()
            width, height = 630, 450
            frame = pg.Surface((630, 450))
            surface_to_draw = frame
            WIN.fill(BLACK)

            temp_ui_font = create_temp_font_1(height)
            surface_to_draw.fill(UI_COLOUR_BACKGROUND)

            surface_to_draw.blit(menu_sprite, [x_mod, 0])
            surface_to_draw.blit(temp_ui_font.render(write_textline("Main title"), True, AMBER), (25 + x_mod, 25))
            menu_logic.draw(surface_to_draw, [30 + x_mod, 50])

            crt(surface_to_draw)
            surface_to_draw.blit(menu_overlay, [0, 0])
            scale_render(WIN, surface_to_draw, CLOCK)
            pg.display.update()
        CLOCK.tick(60)


keyboard_input_ref = [
            [pg.K_ESCAPE, pg.K_F1, pg.K_F2, pg.K_F3, pg.K_F4, pg.K_F5, pg.K_F6, pg.K_F7, pg.K_F8, pg.K_F9, pg.K_F10,
             pg.K_F11, pg.K_F12, pg.K_PRINTSCREEN, pg.K_SCROLLOCK, pg.K_PAUSE],
            [pg.K_BACKQUOTE, pg.K_1, pg.K_2, pg.K_3, pg.K_4, pg.K_5, pg.K_6, pg.K_7, pg.K_8, pg.K_9, pg.K_0, pg.K_MINUS,
             pg.K_EQUALS, pg.K_BACKSPACE],
            [pg.K_TAB, pg.K_q, pg.K_w, pg.K_e, pg.K_r, pg.K_t, pg.K_y, pg.K_u, pg.K_i, pg.K_o, pg.K_p, pg.K_LEFTBRACKET,
             pg.K_RIGHTBRACKET, pg.K_BACKSLASH],
            [pg.K_CAPSLOCK, pg.K_a, pg.K_s, pg.K_d, pg.K_f, pg.K_g, pg.K_h, pg.K_j, pg.K_k, pg.K_l, pg.K_SEMICOLON,
             pg.K_QUOTE, pg.K_RETURN],
            [pg.K_LSHIFT, pg.K_z, pg.K_x, pg.K_c, pg.K_v, pg.K_b, pg.K_n, pg.K_m, pg.K_COMMA, pg.K_PERIOD, pg.K_SLASH,
             pg.K_RSHIFT, pg.K_UP, pg.K_KP1],
            [pg.K_LCTRL, pg.K_LSUPER, pg.K_LALT, pg.K_SPACE, pg.K_RALT, pg.K_LEFT, pg.K_DOWN, pg.K_RIGHT, pg.K_KP0,
             pg.K_KP_PERIOD]
        ]


def rebind_menu_keyboard_mouse(WIN, CLOCK):
    controller_sprite_sheet = get_image("Sprites/UI/Rebind Menu/Keyboard and mouse.png")
    main_keyboard = controller_sprite_sheet.subsurface((0, 0, 224, 72))
    key_8x8 = controller_sprite_sheet.subsurface((0, 72, 8, 8))
    key_10x8 = controller_sprite_sheet.subsurface((0, 72, 10, 8))
    key_11x8 = controller_sprite_sheet.subsurface((0, 72, 11, 8))
    key_12x8 = controller_sprite_sheet.subsurface((0, 72, 12, 8))
    key_13x8 = controller_sprite_sheet.subsurface((0, 72, 13, 8))
    key_18x8 = controller_sprite_sheet.subsurface((0, 72, 18, 8))
    key_19x8 = controller_sprite_sheet.subsurface((0, 72, 19, 8))
    key_23x8 = controller_sprite_sheet.subsurface((0, 72, 23, 8))
    key_59x8 = controller_sprite_sheet.subsurface((0, 72, 59, 8))    # Space bar lol
    key_8x18 = controller_sprite_sheet.subsurface((0, 80, 8, 18))

    # temp = advanced_image_to_map_geometry(main_keyboard, colours_to_check=[(255, 255, 255)], animate=False, size_mod=32)
    points = [
        [[5, 7], [20, 7], [30, 7], [40, 7], [50, 7], [65, 7], [75, 7], [85, 7], [95, 7], [110, 7], [120, 7], [130, 7],  [140, 7], [151, 7], [161, 7], [171, 7]],
        [[5, 17], [15, 17], [25, 17], [35, 17], [45, 17], [55, 17], [65, 17], [75, 17], [85, 17], [95, 17], [105, 17],  [115, 17], [125, 17], [135, 17, key_13x8], [151, 17], [161, 17], [171, 17], [182, 17], [192, 17], [202, 17], [212, 17]],
        [[5, 27, key_10x8], [17, 27], [27, 27], [37, 27], [47, 27], [57, 27], [67, 27], [77, 27], [87, 27], [97, 27], [107, 27], [117, 27], [127, 27], [137, 27,key_11x8], [151, 27], [161, 27], [171, 27], [182, 27], [192, 27], [202, 27], [212, 27, key_8x18]],
        [[5, 37, key_12x8], [19, 37], [29, 37], [39, 37], [49, 37], [59, 37], [69, 37], [79, 37], [89, 37], [99, 37], [109, 37], [119, 37], [129, 37, key_19x8], [182, 37], [192, 37], [202, 37]],
        [[5, 47, key_18x8], [25, 47], [35, 47], [45, 47], [55, 47], [65, 47], [75, 47], [85, 47], [95, 47], [105, 47], [115, 47], [125, 47, key_23x8], [161, 47], [182, 47], [192, 47], [202, 47], [212, 47, key_8x18]],
        [[5, 57, key_10x8], [17, 57, key_10x8], [29, 57, key_10x8], [41, 57, key_59x8], [102, 57, key_10x8], [114, 57, key_10x8], [126, 57, key_10x8], [138, 57, key_10x8], [151, 57], [161, 57], [171, 57], [182, 57, key_18x8], [202, 57]]
    ]
    main_mouse = controller_sprite_sheet.subsurface((96, 72, 32, 56))
    mouse_left = controller_sprite_sheet.subsurface((96+32, 72, 16, 24))
    mouse_middle = controller_sprite_sheet.subsurface((96+48, 72, 16, 24))
    mouse_right = controller_sprite_sheet.subsurface((96+64, 72, 16, 24))

    pg.mixer.music.pause()
    frame_1 = some_bullshit_for_transitions(WIN)
    transition = False
    win_copy = WIN.copy()
    frame_1.set_alpha(128)
    menu_sprite = pg.image.load(os.path.join("Sprites/UI/Settings Screen.png")).convert_alpha()
    menu_overlay = pg.image.load(os.path.join("Sprites/UI/Overlay.png")).convert_alpha()
    draw = True
    i_am_not_putting_this_if_statement_this_shit_is_unreadable = True

    # Sprites to draw the keyboard and mouse
    options = [
        {"Name": "Up", "Value": 0, "On select": "Key Input", "Render func": "Key Input", "Key Input": {"Mode": "Keyboard"}},
        {"Name": "Left", "Value": 0, "On select": "Key Input", "Render func": "Key Input", "Key Input": {"Mode": "Keyboard"}},
        {"Name": "Right", "Value": 0, "On select": "Key Input", "Render func": "Key Input", "Key Input": {"Mode": "Keyboard"}},
        {"Name": "Down", "Value": 0, "On select": "Key Input", "Render func": "Key Input", "Key Input": {"Mode": "Keyboard"}},
        {"Name": "Dash", "Value": 0, "On select": "Key Input", "Render func": "Key Input", "Key Input": {"Mode": "Keyboard"}},

        {"Name": "Shoot", "Value": 0, "On select": "Key Input", "Render func": "Key Input", "Key Input": {"Mode": "Mouse"}},
        {"Name": "Alt fire", "Value": 0, "On select": "Key Input", "Render func": "Key Input", "Key Input": {"Mode": "Mouse"}},
        {"Name": "Reload", "Value": 0, "On select": "Key Input", "Render func": "Key Input", "Key Input": {"Mode": "Keyboard"}},
        {"Name": "Interact", "Value": 0, "On select": "Key Input", "Render func": "Key Input", "Key Input": {"Mode": "Keyboard"}},

        {"Name": "Skill 1", "Value": 0, "On select": "Key Input", "Render func": "Key Input", "Key Input": {"Mode": "Keyboard"}},
        {"Name": "Skill 2", "Value": 0, "On select": "Key Input", "Render func": "Key Input", "Key Input": {"Mode": "Keyboard"}},

        {"Name": "Order Hold", "Value": 0, "On select": "Key Input", "Render func": "Key Input", "Key Input": {"Mode": "Keyboard"}},
        {"Name": "Order Follow", "Value": 0, "On select": "Key Input", "Render func": "Key Input", "Key Input": {"Mode": "Keyboard"}},
        {"Name": "Order Attack", "Value": 0, "On select": "Key Input", "Render func": "Key Input", "Key Input": {"Mode": "Keyboard"}},
        {"Name": "Order Act Free", "Value": 0, "On select": "Key Input", "Render func": "Key Input", "Key Input": {"Mode": "Keyboard"}},

        {"Name": "Pause", "Value": 0, "On select": "Key Input", "Render func": "Key Input", "Key Input": {"Mode": "Keyboard"}},

        {"Name": "Quit without save", "Value": "Quit no save", "On select": "Return", "Render func": "Text only"},
        {"Name": "Quit", "Value": "Quit", "On select": "Return", "Render func": "Text only"},
    ]
    # get the current binds
    key_binds = get_from_json("Key binds.json", "Keyboard")
    mouse_binds = get_from_json("Key binds.json", "Mouse")
    system_binds = get_from_json("Key binds.json", "System")
    for bind_type in [key_binds, mouse_binds, system_binds]:
        for input_bind in bind_type:
            for op in options:
                if op["Name"] == input_bind:
                    op["Value"] = bind_type[input_bind]
                    break

    save = False
    menu_logic = UniversalMenuLogic(options)
    while True:
        do_shit = menu_logic.act(WIN, CLOCK)
        keyboard_input = [
            keyboard_input_ref[0].copy(),
            keyboard_input_ref[1].copy(),
            keyboard_input_ref[2].copy(),
            keyboard_input_ref[3].copy(),
            keyboard_input_ref[4].copy(),
            keyboard_input_ref[5].copy(),
        ]
        mouse_input = [False, False, False]
        if do_shit:
            if do_shit == "Quit":
                save = True
                break
            if do_shit == "Quit no save":
                break
            if do_shit == "Bitching":
                pass

        # Display where the keys are
        current_option = menu_logic.options[menu_logic.selected_option]
        target = current_option["Value"]
        for y, row in enumerate(keyboard_input):
            for x, keeee in enumerate(row):
                keyboard_input[y][x] = target == keeee
        if "Key Input" in current_option:
            if current_option["Key Input"]["Mode"] == "Mouse":
                mouse_input[current_option["Value"]] = True

        # |Draw|--------------------------------------------------------------------------------------------------------
        if draw:
            # width, height = WIN.get_size()
            width, height = 630, 450
            frame = pg.Surface((630, 450))
            surface_to_draw = frame
            WIN.fill(BLACK)
            temp_ui_font = create_temp_font_6(height)
            surface_to_draw.fill(UI_COLOUR_BACKGROUND)

            surface_to_draw.blit(frame_1, (0, 0))
            surface_to_draw.blit(menu_sprite, [0, 0])
            menu_logic.draw(surface_to_draw, [30, 50])
            # Draw keyboard here
            if i_am_not_putting_this_if_statement_this_shit_is_unreadable:
                c_zero = [288, 150]
                surface_to_draw.blit(main_keyboard, [c_zero[0], c_zero[1]])
                for y, row in enumerate(keyboard_input):
                    for x, p in enumerate(row):
                        pp = points[y][x]
                        if keyboard_input[y][x]:
                            sprite = key_8x8
                            if len(pp) == 3:
                                sprite = pp[2]
                            surface_to_draw.blit(sprite, [c_zero[0] + pp[0], c_zero[1] + pp[1]])
                        # nam = pg.key.name(keyboard_input_ref[y][x]).capitalize()[:2]
                        # surface_to_draw.blit(temp_ui_font.render(nam, True, UI_COLOUR_NEW_BACKDROP),
                        #     [c_zero[0] + pp[0], c_zero[1] + pp[1]])

                surface_to_draw.blit(main_mouse, [c_zero[0] + 250, c_zero[1] + 10])
                if mouse_input[0]: surface_to_draw.blit(mouse_left, [c_zero[0] + 250, c_zero[1] + 10])
                if mouse_input[1]: surface_to_draw.blit(mouse_middle, [c_zero[0] + 258, c_zero[1] + 10])
                if mouse_input[2]: surface_to_draw.blit(mouse_right, [c_zero[0] + 266, c_zero[1] + 10])
            crt(surface_to_draw)
            surface_to_draw.blit(menu_overlay, [0, 0])

            scale_render(WIN, surface_to_draw, CLOCK)
            if transition:
                transition = False
                menu_transition_doom_screen_melt(WIN, CLOCK, WIN, win_copy)
            pg.display.update()
        CLOCK.tick(60)

    if save:
        new_binds = {
              "Keyboard": {
                    "Up": 119,
                    "Right": 100,
                    "Left": 97,
                    "Down": 115,
                    "Dash": 32,
                    "Reload": 114,
                    "Skill 1": 49,
                    "Skill 2": 50,
                    "Interact": 101,
                    "Order Hold": 122,
                    "Order Follow": 120,
                    "Order Attack": 99,
                    "Order Act Free": 118
              },
              "Mouse": {
                    "Shoot": 0,
                    "Alt fire": 2
              },
              "System": {
                    "Pause": 27,
                    "Screenshot": 51
              }
        }
        for bind_type in new_binds:
            for input_type in new_binds[bind_type]:
                for op in options:
                    if op["Name"] == input_type:
                        new_binds[bind_type][input_type] = op["Value"]
                        break
        dict_to_json("Key binds.json", new_binds)
    #


def rebind_menu_controller(WIN, CLOCK):
    pg.mixer.music.pause()
    back_to_title = False
    frame_1 = some_bullshit_for_transitions(WIN)
    transition = False
    win_copy = WIN.copy()
    frame_1.set_alpha(128)
    menu_sprite = pg.image.load(os.path.join("Sprites/UI/Settings Screen.png")).convert_alpha()
    menu_overlay = pg.image.load(os.path.join("Sprites/UI/Overlay.png")).convert_alpha()
    draw = True
    i_am_not_putting_this_if_statement_this_shit_is_unreadable = True

    # Sprites to draw the controller
    controller_sprite_sheet = get_image("Sprites/UI/Rebind Menu/Controller.png")
    main_body = controller_sprite_sheet.subsurface((0, 24, 248, 168))
    left_trigger = controller_sprite_sheet.subsurface((0, 0, 24, 8))
    right_trigger = controller_sprite_sheet.subsurface((24, 0, 24, 8))
    left_shoulder = controller_sprite_sheet.subsurface((0, 8, 56, 16))
    right_shoulder = controller_sprite_sheet.subsurface((56, 8, 56, 16))
    dpad_up = controller_sprite_sheet.subsurface((128, 0, 8, 16))
    dpad_left = controller_sprite_sheet.subsurface((136, 16, 16, 8))
    dpad_right = controller_sprite_sheet.subsurface((144, 0, 16, 8))
    dpad_down = controller_sprite_sheet.subsurface((160, 8, 8, 16))
    stick_inactive = controller_sprite_sheet.subsurface((168, 0, 24, 24))
    stick_active = controller_sprite_sheet.subsurface((192, 0, 24, 24))
    button_middle = controller_sprite_sheet.subsurface((112, 16, 16, 8))
    button_inactive = controller_sprite_sheet.subsurface((216, 0, 16, 16))
    button_active = controller_sprite_sheet.subsurface((232, 0, 16, 16))

    gamepad_index = 0
    buttons = [
    "Button Left", "Button Top", "Button Bottom", "Button Right", "Button Select", "Button Start",
    "Shoulder Left", "Shoulder Right", "Trigger Left", "Trigger Right", "Stick Left Press", "Stick Right Press",
    "D-pad Up", "D-pad Left", "D-pad Right", "D-pad Down"
    ]
    sticks = ["Stick Left", "Stick Right"]
    options = [
        {"Name": "Move", "Value": 0, "On select": "Choose", "Render func": "Choose", "Choose": {"List": sticks}},
        {"Name": "Aim", "Value": 0, "On select": "Choose", "Render func": "Choose", "Choose": {"List": sticks}},
        {"Name": "Dash", "Value": 0, "On select": "Choose", "Render func": "Choose", "Choose": {"List": buttons}},

        {"Name": "Shoot", "Value": 0, "On select": "Choose", "Render func": "Choose", "Choose": {"List": buttons}},
        {"Name": "Alt fire", "Value": 0, "On select": "Choose", "Render func": "Choose", "Choose": {"List": buttons}},
        {"Name": "Reload", "Value": 0, "On select": "Choose", "Render func": "Choose", "Choose": {"List": buttons}},
        {"Name": "Interact", "Value": 0, "On select": "Choose", "Render func": "Choose", "Choose": {"List": buttons}},

        {"Name": "Skill 1", "Value": 0, "On select": "Choose", "Render func": "Choose", "Choose": {"List": buttons}},
        {"Name": "Skill 2", "Value": 0, "On select": "Choose", "Render func": "Choose", "Choose": {"List": buttons}},

        {"Name": "Order Hold", "Value": 0, "On select": "Choose", "Render func": "Choose", "Choose": {"List": buttons}},
        {"Name": "Order Follow", "Value": 0, "On select": "Choose", "Render func": "Choose", "Choose": {"List": buttons}},
        {"Name": "Order Attack", "Value": 0, "On select": "Choose", "Render func": "Choose", "Choose": {"List": buttons}},
        {"Name": "Order Act Free", "Value": 0, "On select": "Choose", "Render func": "Choose", "Choose": {"List": buttons}},

        {"Name": "Pause", "Value": 0, "On select": "Choose", "Render func": "Choose", "Choose": {"List": buttons}},


        {"Name": "Quit without save", "Value": "Quit no save", "On select": "Return", "Render func": "Text only"},
        {"Name": "Quit", "Value": "Quit", "On select": "Return", "Render func": "Text only"},
    ]
    #
    current_controller_binds = get_from_json("Controller binds.json", "Everything")
    # Pain is in the for loop
    for p in current_controller_binds:
        if not current_controller_binds[p]:
            continue
        if type(current_controller_binds[p]) == str:
            for o in options:
                if o["Name"] != p:
                    continue
                num = 0
                for count, aaaaa in enumerate(sticks):
                    if aaaaa == current_controller_binds[p]:
                        num = count
                o["Value"] = num
            continue
        for pp in current_controller_binds[p]:
            for o in options:
                if o["Name"] != p:
                    continue
                num = 0
                for count, aaaaa in enumerate(buttons):
                    if aaaaa == pp:
                        num = count
                o["Value"] = num

    save = False
    menu_logic = UniversalMenuLogic(options)
    time_spent = 0
    while True:
        time_spent += 1
        keys = pg.key.get_pressed()
        needed_in_menu_and_game(WIN, keys)

        gamepads = ALL_CONTROLLERS[0]
        threshold_stick, threshold_trigger = 0.2, 0.2
        # Check if there's any controllers
        try:
            gamepads[gamepad_index].init()
        except IndexError:
            pass
        controller_keys = {
            "Button Left": False, "Button Top": False, "Button Bottom": False, "Button Right": False,
            "Button Select": False, "Button Start": False,
            "Shoulder Left": False, "Shoulder Right": False, "Trigger Left": False, "Trigger Right": False,
            "Stick Left": [0, 0], "Stick Right": [0, 0], "Stick Left Press": False, "Stick Right Press": False,
            "D-pad Up": False, "D-pad Left": False, "D-pad Right": False, "D-pad Down": False
        }
        do_shit = menu_logic.act(WIN, CLOCK)
        if do_shit:
            if do_shit == "Quit":
                save = True
                break
            if do_shit == "Quit no save":
                break
            if do_shit == "Bitching":
                try:
                    controller_keys = get_keys_from_controller(gamepads, gamepad_index=0)
                except IndexError:
                    controller_keys = {
                        "Button Left": False, "Button Top": False, "Button Bottom": False, "Button Right": False,
                        "Button Select": False, "Button Start": False,
                        "Shoulder Left": False, "Shoulder Right": False, "Trigger Left": False, "Trigger Right": False,
                        "Stick Left": [0, 0], "Stick Right": [0, 0], "Stick Left Press": False,
                        "Stick Right Press": False,
                        "D-pad Up": False, "D-pad Left": False, "D-pad Right": False, "D-pad Down": False
                    }

        current_option = menu_logic.options[menu_logic.selected_option]
        if "Choose" in current_option:
            input_to_display = current_option["Choose"]["List"][current_option["Value"]]
            value = True
            if input_to_display in sticks:
                value = move_with_vel_angle([0, 0], 1, time_spent*4)
            controller_keys[input_to_display] = value

        # |Draw|--------------------------------------------------------------------------------------------------------
        if draw:
            # width, height = WIN.get_size()
            width, height = 630, 450
            frame = pg.Surface((630, 450))
            surface_to_draw = frame
            WIN.fill(BLACK)
            temp_ui_font = create_temp_font_1(height)
            surface_to_draw.fill(UI_COLOUR_BACKGROUND)

            surface_to_draw.blit(frame_1, (0, 0))
            surface_to_draw.blit(menu_sprite, [0, 0])
            menu_logic.draw(surface_to_draw, [30, 50])
            # Draw controller
            if i_am_not_putting_this_if_statement_this_shit_is_unreadable:
                c_zero = [288, 128]
                surface_to_draw.blit(main_body, [c_zero[0], c_zero[1]])
                if controller_keys["Button Top"]: surface_to_draw.blit(button_active, [c_zero[0] + 162, c_zero[1]+14])
                if controller_keys["Button Left"]: surface_to_draw.blit(button_active, [c_zero[0] + 150, c_zero[1]+26])
                if controller_keys["Button Right"]: surface_to_draw.blit(button_active, [c_zero[0] + 174, c_zero[1]+26])
                if controller_keys["Button Bottom"]: surface_to_draw.blit(button_active, [c_zero[0] + 162, c_zero[1]+38])

                if controller_keys["Button Select"]: surface_to_draw.blit(button_middle, [c_zero[0] + 104, c_zero[1]+38])
                if controller_keys["Button Start"]: surface_to_draw.blit(button_middle, [c_zero[0] + 128, c_zero[1]+38])
                # Shoulder trigger
                if controller_keys["Shoulder Left"]: surface_to_draw.blit(left_shoulder, [c_zero[0] + 32, c_zero[1]+8])
                if controller_keys["Shoulder Right"]: surface_to_draw.blit(right_shoulder, [c_zero[0] + 160, c_zero[1]+8])
                if controller_keys["Trigger Left"]: surface_to_draw.blit(left_trigger, [c_zero[0] + 56, c_zero[1]])
                if controller_keys["Trigger Right"]: surface_to_draw.blit(right_trigger, [c_zero[0] + 168, c_zero[1]])
                if controller_keys["D-pad Up"]: surface_to_draw.blit(dpad_up, [c_zero[0] + 94, c_zero[1]+54])
                if controller_keys["D-pad Left"]: surface_to_draw.blit(dpad_left, [c_zero[0] + 78, c_zero[1] + 70])
                if controller_keys["D-pad Right"]: surface_to_draw.blit(dpad_right, [c_zero[0] + 102, c_zero[1] + 70])
                if controller_keys["D-pad Down"]: surface_to_draw.blit(dpad_down, [c_zero[0] + 94, c_zero[1] + 78])

                left_stick_zero = [77 + controller_keys["Stick Left"][0] * 10, 33 + controller_keys["Stick Left"][1] * 10]
                stick_sprite = stick_inactive
                if abs(controller_keys["Stick Left"][0]) > threshold_stick or abs(controller_keys["Stick Left"][1]) > threshold_stick:
                    stick_sprite = stick_active
                surface_to_draw.blit(stick_sprite, [c_zero[0] + left_stick_zero[0] - 11, c_zero[1] + left_stick_zero[1] - 11])
                shit_ass = button_inactive
                if controller_keys["Stick Left Press"]:
                    shit_ass = button_active
                surface_to_draw.blit(shit_ass,
                                     [c_zero[0] + left_stick_zero[0] - 7, c_zero[1] + left_stick_zero[1] - 7])

                right_stick_zero = [149 + controller_keys["Stick Right"][0] * 10, 73 + controller_keys["Stick Right"][1] * 10]
                stick_sprite = stick_inactive
                if abs(controller_keys["Stick Right"][0]) > threshold_stick or abs(
                        controller_keys["Stick Right"][1]) > threshold_stick:
                    stick_sprite = stick_active
                surface_to_draw.blit(stick_sprite,
                                     [c_zero[0] + right_stick_zero[0] - 11, c_zero[1] + right_stick_zero[1] - 11])
                shit_ass = button_inactive
                if controller_keys["Stick Right Press"]:
                    shit_ass = button_active
                surface_to_draw.blit(shit_ass,
                                     [c_zero[0] + right_stick_zero[0] - 7, c_zero[1] + right_stick_zero[1] - 7])

            crt(surface_to_draw)
            surface_to_draw.blit(menu_overlay, [0, 0])
            scale_render(WIN, surface_to_draw, CLOCK)
            if transition:
                transition = False
                menu_transition_doom_screen_melt(WIN, CLOCK, WIN, win_copy)
            pg.display.update()
        CLOCK.tick(60)

    if save:
        new_binds = {
            "Move": "Stick Left", "Dash": [],
            "Aim": "Stick Right", "Alt fire": [], "Shoot": [], "Interact": [], "Reload": [],
            "Skill 1": [], "Skill 2": [],
            "Order Hold": [], "Order Follow": [], "Order Attack": [], "Order Act Free": [],
            "Up": [], "Down": [], "Left": [], "Right": [],
            "Pause": [], "Screenshot": []}
        # Go through options and get
        for new_input in menu_logic.options:
            if new_input["Name"] not in new_binds:
                continue
            if new_input["Name"] in ["Move", "Aim"]:
                new_binds[new_input["Name"]] = sticks[new_input["Value"]]
                continue
            new_binds[new_input["Name"]] = [buttons[new_input["Value"]]]
        dict_to_json("Controller binds.json", new_binds)
    #


def game_intro(WIN, CLOCK, controls, player):
    menu_overlay = pg.image.load(os.path.join("Sprites/UI/Overlay.png")).convert_alpha()
    key_pressed = DEFAULT_KEY_PRESSED * 4
    controller = PseudoPlayer()
    temp_ui_font =  create_temp_font_2(450, font_name="Sprites/JetBrainsMono-SemiBold.ttf")
    # Curtis is 20, Curtis was 15 at the start of the war
    # Vivianne is 19 Vivianne was 14 at the start of the war
    b = "Secretary" # use a bird name, she is part of the Nest but
    elements_to_show =[
        # {"Sender": "SYS", "Message": "Incoming FTL transmission from user ID: "},
        {"Sender": "SYS", "Message": str_to_list(f"FTL transmission from user '{b}' to user group 'THR-1'")},
        {"Sender": b, "Message": str_to_list("Leopold, Kai. I have a contract for your group.")},

        {"Sender": b, "Message": str_to_list("Around 2 months ago")},
        {"Sender": b, "Message": str_to_list("A massive energy surge has been recorded on the planet you've been vacationing on.")},
        {"Sender": b, "Message": str_to_list("My client want something related to this.")},
        {"Sender": b, "Message": str_to_list("He just recently learned about this.")},

        {"Sender": b, "Message": str_to_list("And others are already there, on their way to claim this thing.")},
        {"Sender": b, "Message": str_to_list("There's fighting between all of them. Take advantage of the chaos to advance.")},

        {"Sender": b, "Message": str_to_list("The others have tried to get it by air but they have been shot down.")},
        {"Sender": b, "Message": str_to_list("You'll need to get to the objective by a ground route.")},

        {"Sender": b, "Message": str_to_list("The goal is to claim the objective by any means necessary.")},

        {"Sender": b, "Message": str_to_list("We'll pay for supplies based on performances.")},
        {"Sender": b, "Message": str_to_list("But you'll only get paid when the objective is safely in my hands.")},
        {"Sender": b, "Message": str_to_list("Reward is 5M $SS. Are you in?")},

        {"Sender": "SYS", "Message": str_to_list("FTL transmission finished.")},
        {"Sender": "SYS", "Message": str_to_list("Send response? Y/N")},
        {"Sender": "THR-1", "Message": str_to_list("Y")},
        {"Sender": "THR-1", "Message": str_to_list("We'll do it.")},
        # {"Sender": "THR-1", "Message": str_to_list("I AM MAKING MAC AND CHEESE AND NOBODY CAN STOP ME!")},
    ]
    menu_render = UICommunicationLog(elements_to_show, [20, 200])
    # transmission_list = []
    # cooldown = 0
    end_timer = 120
    while elements_to_show or end_timer > 0:
        frame = pg.Surface((630, 450))
        surface_to_draw = frame
        WIN.fill(BLACK)
        surface_to_draw.fill(UI_COLOUR_BACKGROUND)
        menu_render.act()
        if not menu_render.elements_to_show:
            end_timer -= 1
        menu_render.draw(surface_to_draw)


        # |! KEEP EVERYTHING BELOW !|
        # Let the player skip
        keys = pg.key.get_pressed()
        needed_in_menu_and_game(WIN, keys)
        controller.get_input(keys)
        no_input = True
        for i in controller.input:
            if controller.input[i]:
                no_input = False
                break

        if key_pressed == 0:
            if not no_input:
                return
        elif no_input:
            key_pressed -= 1

        crt(surface_to_draw)
        surface_to_draw.blit(menu_overlay, [0, 0])
        scale_render(WIN, surface_to_draw, CLOCK)
        pg.display.update()
        CLOCK.tick(60)


def story_event(WIN, CLOCK, party, event_to_play):
    transition, frame_1 = menu_transition_start(WIN)
    controller = PseudoPlayer()
    event_script = {
        "THR-1":
            {
                "Start": [
                    {"Name": "", "Text": [""], "Image": get_image('Sprites/Story/THR-1/Start 1.png')},
                    {"Name": "LORD", "Text": ["Secretary sent us a job contract."], "Image": get_image('Sprites/Story/THR-1/Start 2.png')},
                    {"Name": "EMPEROR", "Text": ["It's been a while since she talked to us."], "Image": False},
                    {"Name": "WIZARD", "Text": ["It wouldn't hurt to look at it?"], "Image": False},
                    {"Name": "LORD", "Text": ["1 million!"], "Image": get_image('Sprites/Story/THR-1/Start 3.png')},
                    {"Name": "WIZARD", "Text": ["Is she thinking we're stupid, she'd be overpaying us."], "Image": False},
                    {"Name": "EMPEROR", "Text": ["It might not be a trap, I think she's out of options."], "Image": False},
                    {"Name": "EMPEROR", "Text": ["We could take the contract. If it gets too dicey we bail out."], "Image": False},
                    {"Name": "WIZARD", "Text": ["I guess we could..."], "Image": False},
                    {"Name": "LORD", "Text": ["Let's do that!"], "Image": get_image('Sprites/Story/THR-1/Start 4.png')},
                ],
                "Event 1": [
                    {"Name": "EMPEROR", "Text": ["Don't you find this job strange?"], "Image": get_image('Sprites/Story/THR-1/Event 1 1.png')},
                    {"Name": "LORD", "Text": ["Beside how it came out of nowhere, no."], "Image": False},
                    {"Name": "EMPEROR", "Text": ["After that job, she said she's done working with us."], "Image": False},
                    {"Name": "LORD", "Text": ["I think it's like you said; she's out of options."], "Image": get_image('Sprites/Story/THR-1/Event 1 2.png')},
                    {"Name": "EMPEROR", "Text": ["I'm starting to reconsider the job."], "Image": False},
                    {"Name": "LORD", "Text": ["I'm not too concerned about this."], "Image": False},
                    {"Name": "LORD", "Text": ["It's totally shady, but we did worse in the past."], "Image": get_image('Sprites/Story/THR-1/Event 1 3.png')},
                    {"Name": "EMPEROR", "Text": ["Maybe we should ask ourselves if we're being taken advantage of."], "Image": get_image('Sprites/Story/THR-1/Event 1 4.png')},
                ],
                "Event 2": [
                    {"Name": "EMPEROR", "Text": ["What's that?!"], "Image": get_image('Sprites/Story/THR-1/Event 2 1.png')},
                    {"Name": "EMPEROR", "Text": ["Documents?"], "Image": get_image('Sprites/Story/THR-1/Event 2 2.png')},
                    {"Name": "Written on the first page", "Text": ["Project Orion: Betelgeuse Plan..."], "Image": False},
                    {"Name": "EMPEROR", "Text": ["Didn't Vincent mention something like that?"], "Image": False},
                    {"Name": "CONDOR", "Text": ["Kai, we are about to move! Get back"], "Image": get_image('Sprites/Story/THR-1/Event 2 3.png')},
                    {"Name": "EMPEROR", "Text": ["I'm on my way! I found intel I want you to check!"], "Image": False},
                ],
                "Ending Win": [
                    {"Name": "", "Text": [], "Image": get_image('Sprites/Story/THR-1/Win 1.png')},
                    {"Name": "EMPEROR", "Text": ["There's something she is not telling us."], "Image": False},
                    {"Name": "EMPEROR", "Text": ["Let's see if I get answers."], "Image": get_image('Sprites/Story/THR-1/Win 2.png')},
                    {"Name": "EMPEROR", "Text": ["Project Orion?"], "Image": get_image('Sprites/Story/THR-1/Win 3.png')},
                    {"Name": "EMPEROR", "Text": ["She has to be hiding something."], "Image": get_image('Sprites/Story/THR-1/Win 4.png')},
                    {"Name": "EMPEROR", "Text": ["I know from Condor that the Betelgeuse plan failed"], "Image": get_image('Sprites/Story/THR-1/Win 5.png')},
                    {"Name": "EMPEROR", "Text": ["Are they going to use the anomaly has a weapon?"], "Image": get_image('Sprites/Story/END WIN.png')},
                ],
                "Ending Loss": [
                    {"Name": "Secretary", "Text": ["I was expecting better results..."], "Image": get_image('Sprites/Story/THR-1/Loss 1.png')},
                    {"Name": "Secretary", "Text": ["But it's not unsalvageable..."], "Image": get_image('Sprites/Story/THR-1/Loss 2.png')},
                    {"Name": "Secretary", "Text": ["You proved yourselves useful enough..."], "Image": get_image('Sprites/Story/THR-1/Loss 3.png')},
                    {"Name": "Secretary", "Text": ["Of course, you're not getting any rewards. But I'll see if I can cover some of your costs"], "Image": get_image('Sprites/Story/END LOSS.png')}
                ],
            },
        "Zoar": {
                "Start": [
                    {"Name": "Vivianne", "Text": ["Curtis started to have headaches not long after replacing my leg."], "Image": get_image('Sprites/Story/Zoar/Start 1.png')},
                    {"Name": "Vivianne", "Text": ["He also told me about a dream he keeps having."], "Image": False},
                    {"Name": "Vivianne", "Text": ["It's about a mountain in the desert."], "Image": get_image('Sprites/Story/Zoar/Start 2.png')},
                    {"Name": "Vivianne", "Text": ["There's a small salt flat there."], "Image": get_image('Sprites/Story/Zoar/Start 3.png')},
                    {"Name": "Vivianne", "Text": ["Something there is calling for him."], "Image": get_image('Sprites/Story/Zoar/Start 4.png')},
                    {"Name": "Vivianne", "Text": ["Makoto told us that a mercenary army was deployed to investigate an anomaly in the desert."], "Image": False},
                    {"Name": "Vivianne", "Text": ["Curtis is convinced that it's what was calling him."], "Image": False},
                    {"Name": "Vivianne", "Text": [" We are leaving tomorrow with Lawrence and Mark to figure this thing out."], "Image": False},
                ],
                "Event 1": [
                    {"Name": "Vivianne", "Text": ["Do you have a moment Mark?"], "Image": get_image('Sprites/Story/Zoar/Event 1 1.png')},
                    {"Name": "Mark", "Text": ["Yes."], "Image": False},
                    {"Name": "Vivianne", "Text": ["I think Curtis is losing his mind..."], "Image": get_image('Sprites/Story/Zoar/Event 1 2.png')},
                    {"Name": "Vivianne", "Text": ["Since I got attacked at the shop."], "Image": False},
                    {"Name": "Mark", "Text": ["He's your brother, it's normal to worry about him."], "Image": get_image('Sprites/Story/Zoar/Event 1 3.png')},
                    {"Name": "Mark", "Text": ["But I wouldn't."], "Image": False},
                    {"Name": "Vivianne", "Text": ["How can think that?!"], "Image": False},
                    {"Name": "Mark", "Text": ["He can handle himself."], "Image": False},
                    {"Name": "Mark", "Text": ["We should both know that."], "Image": False},
                    {"Name": "", "Text": [], "Image": get_image('Sprites/Story/Zoar/Event 1 4.png')},
                    {"Name": "Vivianne", "Text": ["But I can't help it"], "Image": get_image('Sprites/Story/Zoar/Event 1 5.png')},
                ],
                "Event 2": [
                    {"Name": "Lawrence", "Text": ["Come on, I can tell you wish to talk with me."], "Image": get_image('Sprites/Story/Zoar/Event 2 1.png')},
                    {"Name": "Vivianne", "Text": ["Yeah..."], "Image": False},
                    {"Name": "Vivianne", "Text": ["Aren't you bothered about Curtis?"], "Image": get_image('Sprites/Story/Zoar/Event 2 2.png')},
                    {"Name": "Vivianne", "Text": ["What he's going through can't be normal."], "Image": False},
                    {"Name": "Lawrence", "Text": ["Something latent in him might be awakening."], "Image": False},
                    {"Name": "Vivianne", "Text": ["Something latent?"], "Image": get_image('Sprites/Story/Zoar/Event 2 3.png')},
                    {"Name": "Lawrence", "Text": ["You must have head about psychics at some point."], "Image": False},
                    {"Name": "Lawrence", "Text": ["Curtis might be like that."], "Image": False},
                    {"Name": "Lawrence", "Text": ["Anyway, we have to keep moving if we want to figure it out."], "Image": False},
                    {"Name": "Vivianne", "Text": ["You're right."], "Image": False},
                ],
                "Ending Win": [
                    {"Name": "Curtis", "Text": ["I've been feeling great for the past few days. The headaches and visions are gone."], "Image": get_image('Sprites/Story/Zoar/Win 1.png')},
                    {"Name": "Curtis", "Text": ["I wasn't able to realize how worried Vivianne was about me."], "Image": False},
                    {"Name": "Curtis", "Text": ["I feel bad for that."], "Image": False},
                    {"Name": "Curtis", "Text": ["But now strange things are happening to me."], "Image": False},
                    {"Name": "Curtis", "Text": ["I see people enter the shop before they set their foot in."], "Image": get_image('Sprites/Story/Zoar/Win 2.png')},
                    {"Name": "Curtis", "Text": ["I can tell exactly where my bullets will land before touching the trigger."], "Image": get_image('Sprites/Story/Zoar/Win 3.png')},
                    {"Name": "Curtis", "Text": ["I knew what Vivianne would tell me on the radio before she says a word."], "Image": get_image('Sprites/Story/Zoar/Win 4.png')},
                    {"Name": "Curtis", "Text": ["I'm now asking myself..."], "Image": get_image('Sprites/Story/Zoar/Win 5.png')},
                    {"Name": "Curtis", "Text": ["Am I still truly human?"], "Image": get_image('Sprites/Story/END WIN.png')},
                ],
                "Ending Loss": [
                    {"Name": "Vivianne", "Text": ["In the end we never found what was calling my brother."], "Image": get_image('Sprites/Story/Zoar/Loss 1.png')},
                    {"Name": "Vivianne", "Text": ["We only met a mercenary team, fought with them before leaving."], "Image": False},
                    {"Name": "Vivianne", "Text": ["Whatever was calling Curtis stopped"], "Image": False},
                    {"Name": "Vivianne", "Text": ["He keeps looking at the desert during the night"], "Image": get_image('Sprites/Story/Zoar/Loss 2.png')},
                    {"Name": "Vivianne", "Text": ["He told me that he wonders what it was."], "Image": get_image('Sprites/Story/Zoar/Loss 2 A.png')},
                    {"Name": "Vivianne", "Text": ["and why  he's hearing voices talking among themselves"], "Image": get_image('Sprites/Story/Zoar/Loss 2 B.png')},
                    {"Name": "Vivianne", "Text": ["He's lucid at least. I guess that's our new normal..."], "Image": get_image('Sprites/Story/Zoar/Loss 3.png')},
                    {"Name": "", "Text": [], "Image": get_image('Sprites/Story/END LOSS.png')}
                ],
        }
    }[party][event_to_play]

    sprite_zero = [40, 107.5//2]
    sprites = []
    text_to_write = ""
    draw = True
    fade_mod = 4

    skip = True

    for e in event_script:
        # Fade in square
        if e["Image"]:
            for x in range(256//fade_mod):
                keys = pg.key.get_pressed()
                needed_in_menu_and_game(WIN, keys)
                controller.get_input(keys)

                if controller.input["Interact"] and not skip:
                    skip = True
                    e["Image"].set_alpha(256)
                    break
                elif skip and not controller.input["Interact"]:
                    skip = False

                if draw:
                    width, height = 630, 450
                    frame = pg.Surface((630, 450))
                    surface_to_draw = frame
                    WIN.fill(BLACK)

                    temp_ui_font = create_temp_font_1(height)
                    temp_ui_font_2 = create_temp_font_5(height)
                    # surface_to_draw.fill(UI_COLOUR_BACKGROUND)

                    pg.draw.rect(surface_to_draw, (140, 100, 13), [sprite_zero[0]-2, sprite_zero[1]-2, 554, 279])
                    pg.draw.rect(surface_to_draw, (26, 26, 26), [sprite_zero[0], sprite_zero[1], 550, 275])
                    for s in sprites:
                        surface_to_draw.blit(s, sprite_zero)
                    e["Image"].set_alpha(x * fade_mod + fade_mod)
                    surface_to_draw.blit(e["Image"], sprite_zero)
                    # text_to_write
                    name = temp_ui_font_2.render(e["Name"], True, AMBER)
                    surface_to_draw.blit(name, (315 - name.get_width() // 2, 335))
                    text = temp_ui_font.render(text_to_write, True, AMBER)
                    surface_to_draw.blit(text, (315 - text.get_width() // 2, 360))

                    # 550, 275
                    crt(surface_to_draw)
                    scale_render(WIN, surface_to_draw, CLOCK)
                    transition = menu_transition_handler(WIN, CLOCK, frame_1, transition)
                    pg.display.update()
                CLOCK.tick(60)

            sprites.append(e["Image"])

        loaded_text = [str_to_list(l) for l in e["Text"]]
        text_to_write = ""
        timer = 0
        time_to_die = 25
        while time_to_die > 0:
            keys = pg.key.get_pressed()
            needed_in_menu_and_game(WIN, keys)
            controller.get_input(keys)

            if controller.input["Interact"] and not skip:
                skip = True
                break
            elif skip and not controller.input["Interact"]:
                skip = False

            # Play text
            if timer % 8 == 0:
                if loaded_text:
                    if loaded_text[0]:
                        text_to_write += loaded_text[0][0]
                        loaded_text[0].pop(0)
                    else:
                        loaded_text.pop(0)
                        if loaded_text:
                            text_to_write = ""
                else:
                    time_to_die -= 1

            # Give option to get out
            if draw:
                width, height = 630, 450
                frame = pg.Surface((630, 450))
                surface_to_draw = frame
                WIN.fill(BLACK)

                temp_ui_font = create_temp_font_1(height)
                temp_ui_font_2 = create_temp_font_5(height)

                pg.draw.rect(surface_to_draw, (140, 100, 13), [sprite_zero[0]-2, sprite_zero[1]-2, 554, 279])
                pg.draw.rect(surface_to_draw, (26, 26, 26), [sprite_zero[0], sprite_zero[1], 550, 275])
                for s in sprites:
                    surface_to_draw.blit(s, sprite_zero)
                # text_to_write
                name = temp_ui_font_2.render(e["Name"], True, AMBER)
                surface_to_draw.blit(name, (315 - name.get_width() // 2, 335))
                text = temp_ui_font.render(text_to_write, True, AMBER)
                surface_to_draw.blit(text, (315 - text.get_width() // 2, 360))

                # 550, 275
                crt(surface_to_draw)
                scale_render(WIN, surface_to_draw, CLOCK)
                transition = menu_transition_handler(WIN, CLOCK, frame_1, transition)
                pg.display.update()
            CLOCK.tick(60)
            timer += 1




def pygame_splash_screen(WIN, CLOCK):
    width, height = 630, 450
    stage = 100
    controller = PseudoPlayer()
    sprite = pg.image.load(os.path.join("Sprites/pygame_ce_tiny.png")).convert_alpha()
    colour = [170, 238, 187]
    text_colour = [DARK[0], DARK[1], DARK[2]]
    draw = True
    while colour != [12, 12, 12] and stage > 0:
        keys = pg.key.get_pressed()
        needed_in_menu_and_game(WIN, keys)
        controller.get_input(keys)
        if colour == [12, 12, 12]:
            stage -= 1
        for x in range(3):
            if colour[x] > UI_COLOUR_BACKGROUND[x]:
                colour[x] -= 2

                if colour[x] < UI_COLOUR_BACKGROUND[x]:
                    colour[x] = UI_COLOUR_BACKGROUND[x]

                if text_colour[x] < 255:
                    text_colour[x] += 2

                    if text_colour[x] > 255:
                        text_colour[x] = 255
        for x in controller.input:
            if controller.input[x]:
                return
        # |Draw|--------------------------------------------------------------------------------------------------------
        if draw:
            frame = pg.Surface((width, height))
            surface_to_draw = frame
            WIN.fill(BLACK)
            surface_to_draw.fill(colour)

            surface_to_draw.blit(sprite, [315 - sprite.get_width() // 2, 225 - sprite.get_height() // 2])

            text = FONTS["med"].render(f"Made with", True, text_colour)
            #text_2 = FONTS["med"].render(f"and love.", True, UI_COLOUR_FONT)
            surface_to_draw.blit(text, [315 - text.get_width() // 2, 110])
            # surface_to_draw.blit(text_2, [315 - text_2.get_width() // 2, 290])

            scale_render(WIN, surface_to_draw, CLOCK)
            pg.display.update()
            CLOCK.tick(60)


def my_own_shit(WIN, CLOCK):
    width, height = 630, 450
    pos = [0, 225]
    angle, stage = 20, 1
    controller = PseudoPlayer()
    sprite = pg.image.load(os.path.join("Sprites/Dev Comment Alt.png")).convert_alpha()
    # 1, move to the right
    # 2, bounce on the ground
    draw = True
    while not stage >= 4.0:
        keys = pg.key.get_pressed()
        needed_in_menu_and_game(WIN, keys)
        controller.get_input(keys)

        if stage == 1:  # Move it toward the right
            pos[0] += 9
            angle -= 0.2985
            if pos[0] > width - 32:
                stage, angle = 2, 0
                play_sound('Menu confirm')
        elif stage == 2:  # Make it bounce toward the middle
            bouncer = (pos[0] - width // 2) / 4
            num = (83 + bouncer) * abs(math.sin(bouncer / 12))
            pos[1] = 225 - num
            if num < 7:  # Sound
                play_sound('Menu confirm')
            pos[0] -= 4
            angle += 9.8622063
            if pos[0] < width // 2:
                stage = 3
        elif stage >= 3:  # Keep it standing still for a little bit
            angle = 0
            stage += 0.01

        for x in controller.input:
            if controller.input[x]:
                return
        # |Draw|--------------------------------------------------------------------------------------------------------
        if draw:
            frame = pg.Surface((width, height))
            surface_to_draw = frame
            WIN.fill(BLACK)
            surface_to_draw.fill(UI_COLOUR_BACKGROUND)

            blitRotate(surface_to_draw, sprite, pos, [32, 32], angle)
            text = FONTS["med"].render(f"A game by", True, UI_COLOUR_FONT)
            text_2 = FONTS["med"].render(f"Le Seigneur des Patates", True, UI_COLOUR_FONT)
            surface_to_draw.blit(text, [315 - text.get_width() // 2, 260])
            surface_to_draw.blit(text_2, [315 - text_2.get_width() // 2, 290])

            scale_render(WIN, surface_to_draw, CLOCK)
            pg.display.update()
            CLOCK.tick(60)


def game_credits(WIN, clock):
    key_pressed = DEFAULT_KEY_PRESSED
    key_cooldown = DEFAULT_KEY_COOLDOWN * 2
    controller = PseudoPlayer()

    scrolling_amount = 0
    scrolling_default_mod = 0.4
    scrolling_mod = scrolling_default_mod
    draw = True
    seperator = "-----"
    real_credits = [
        [seperator, "Main Development", seperator], "",
        "Seigneur des Patates",
        "", "",
        [seperator, "Additional Help", seperator], "",
        ["AngKaiser", "Voice Acting"],
        ["a_little_slow", "Beta Testing"],
        ["am bardo", "Beta Testing"],
        write_textline("Credits Thanks")
    ]
    while True:
        # |Menu Logic|--------------------------------------------------------------------------------------------------
        keys = pg.key.get_pressed()
        needed_in_menu_and_game(WIN, keys)
        controller.get_input(keys)

        # Allow to get out
        if key_pressed == 0:
            if controller.input["Interact"]:
                scrolling_mod = scrolling_default_mod * 3
            else:
                scrolling_mod = scrolling_default_mod
                for x in controller.input:
                    if controller.input[x]:
                        return
        else:
            key_pressed -= 1

        if scrolling_amount < 400:
            scrolling_amount += scrolling_mod

        # |Draw|--------------------------------------------------------------------------------------------------------
        if draw:
            # This is to make it scale
            frame = pg.Surface((630, 450))
            surface_to_draw = frame
            WIN.fill(BLACK)
            # Draw the stuff for real
            surface_to_draw.fill(UI_COLOUR_BACKGROUND)

            # Render the text
            for y_mod, x in enumerate(real_credits):
                # Handles single columns
                if type(x) == str:
                    text = UI_FONT.render(x, True, UI_COLOUR_TUTORIAL)
                    surface_to_draw.blit(text, (630 // 2 - text.get_width() // 2,
                                                450 - scrolling_amount * 1 + y_mod * 15))
                # Handle multi columns
                elif type(x) == list:
                    base_x_pos = 630 // (1 + len(x))
                    for x_mod, temp in enumerate(x):
                        text = UI_FONT.render(temp, True, UI_COLOUR_TUTORIAL)
                        surface_to_draw.blit(text, (base_x_pos - (text.get_width() // 2),
                                                    450 - scrolling_amount * 1 + y_mod * 15))
                        base_x_pos += 630 // (1 + len(x))

            scale_render(WIN, surface_to_draw, clock)
            pg.display.update()
        clock.tick(60)


def mission_menu(WIN, CLOCK, missions_to_choose, party_info, run_info):
    # Render stuff
    transition, frame_1 = menu_transition_start(WIN)

    menu_sprite = pg.image.load(os.path.join("Sprites/UI/Settings Screen.png")).convert_alpha()
    menu_overlay = pg.image.load(os.path.join("Sprites/UI/Overlay.png")).convert_alpha()
    modifier_sprite = pg.image.load(os.path.join("Sprites/UI/Mission Modifiers.png")).convert_alpha()
    modifier_sprites = {
        "Skip mission": modifier_sprite.subsurface((0, 0, 32, 32)),
    "Lessen presence": modifier_sprite.subsurface((0, 32 * 1, 32, 32)),
    "Vehicle can deploy": modifier_sprite.subsurface((0, 32 * 2, 32, 32)),
    "Ambush Risk": modifier_sprite.subsurface((0, 32 * 3, 32, 32)),
    "Grunt party": modifier_sprite.subsurface((0, 32 * 4, 32, 32)),
    "Sandstorm": modifier_sprite.subsurface((0, 32 * 5, 32, 32)),
    "Landmines": modifier_sprite.subsurface((0, 32 * 6, 32, 32)),
    "Artillery Strike": modifier_sprite.subsurface((0, 32 * 7, 32, 32)),
    "Enemy armour": modifier_sprite.subsurface((0, 32 * 8, 32, 32)),
    "Lots of Elite": modifier_sprite.subsurface((0, 32 * 9, 32, 32)),
    "Increased presence": modifier_sprite.subsurface((0, 32 * 10, 32, 32)),
    "Unknown Forces": modifier_sprite.subsurface((0, 32 * 11, 32, 32)),
    "Boss rush": modifier_sprite.subsurface((0, 32 * 12, 32, 32)),
    }

    # Info needed for shit
    mission_names = []
    for n in missions_to_choose:
        mission_names.append(n["level"]["name"])

    options = [
    ]
    for mission in mission_names:
        options.append({"Name": mission, "Value": mission, "On select": "Return", "Render func": "Text only"},)

    options.append({"Name": "Shop", "Value": "Shop", "On select": "Return", "Render func": "Text only"},)
    options.append({"Name": "Give up", "Value": "Quit", "On select": "Return", "Render func": "Text only"},)
    menu_logic = UniversalMenuLogic(options)

    new_player_party_info = {}
    x_mod = -210-63
    draw = True
    timer = 0
    while True:
        timer += 1
        if x_mod < 0: x_mod += 21
        # Select
        do_shit = menu_logic.act(WIN, CLOCK)
        if do_shit:
            if do_shit in mission_names:
                out_party = character_menu(WIN, CLOCK, missions_to_choose, party_info, do_shit)

                if out_party: break

                frame_1 = some_bullshit_for_transitions(WIN)
                transition = True
            if do_shit == "Shop":
                # Do that later
                shop_menu(WIN, CLOCK, party_info, run_info)
                menu_logic.cooldown()
                transition, frame_1 = menu_transition_start(WIN)

            if do_shit == "Quit":
                if confirmation_popup(
                        WIN, CLOCK, [256+83, 83],
                        [
                            {"Name": "No", "Value": "No", "On select": "Return", "Render func": "Text only"},
                            {"Name": "Yes", "Value": "Yes", "On select": "Return", "Render func": "Text only"}
                        ],
                    text="Are you sure you want to give up?") == "Yes":
                    return {}, {}, party_info, [], True
            menu_logic.cooldown()

        # |Draw|--------------------------------------------------------------------------------------------------------
        if draw:
            width, height = 630, 450
            frame = pg.Surface((630, 450))
            surface_to_draw = frame
            WIN.fill(BLACK)

            temp_ui_font = create_temp_font_1(height)
            surface_to_draw.fill(UI_COLOUR_BACKGROUND)

            # Draw menu on the left
            surface_to_draw.blit(menu_sprite, [x_mod, 0])
            surface_to_draw.blit(temp_ui_font.render(write_textline("Mission title"), True, AMBER), (25 + x_mod, 25))
            menu_logic.draw(surface_to_draw, [30 + x_mod, 50])

            # Draw mission details
            if menu_logic.options[menu_logic.selected_option]["Value"] in mission_names:
                # Get mission details
                num = 0
                for count, name in enumerate(mission_names):
                    if name == menu_logic.options[menu_logic.selected_option]["Value"]:
                        num = count
                        break
                mission_details = missions_to_choose[num]

                # 320
                info_zero = [256+2, 128- 96-8]
                surface_to_draw.blit(temp_ui_font.render(mission_details['level']["name"], True, AMBER),
                                     (info_zero[0], info_zero[1]))
                if mission_details["level"]['modifiers'] != ["Skip mission"]:
                    surface_to_draw.blit(temp_ui_font.render(write_textline(f"FACTION_{mission_details['level']['faction']+1}"), True, AMBER),
                                         (info_zero[0], info_zero[1] + 20))

                    surface_to_draw.blit(temp_ui_font.render(mission_details["level"]['objective'], True, AMBER),
                                         (info_zero[0], info_zero[1] + 40))
                    enemy_count = len(mission_details["extra info"]['Enemy spawns'])
                    enemy_info = f'{enemy_count} potential hostile contact'
                    if mission_details["level"]['objective'] == "Defense":
                        enemy_info = f'{mission_details["level"]["free var"]["Defense info"]["Wave count"]} waves'

                    surface_to_draw.blit(temp_ui_font.render(enemy_info, True, AMBER), (info_zero[0], info_zero[1] + 60))

                    # Draw map of the mission
                    map_zero = [256+16, 128+16]
                    for wall in mission_details["level"]["map"]:
                        pg.draw.rect(surface_to_draw, UI_COLOUR_NEW_BACKDROP, [
                            wall.left // 16 + map_zero[0], wall.top // 16 + map_zero[1],
                            wall.width // 16, wall.height // 16])

                    # Draw spawn point
                    spawn_point = mission_details["extra info"]["Spawn"]
                    pg.draw.rect(surface_to_draw, AMBER_LIGHT, [
                        spawn_point[0] // 16 + map_zero[0], spawn_point[1] // 16 + map_zero[1], 2, 2
                    ])
                    # Draw where enemies could be
                    for enemy_spawn in mission_details["extra info"]['Enemy spawns']:
                        enemy_spawn_point = random_point_in_circle(
                            [enemy_spawn["Pos"][0] // 16 + map_zero[0], enemy_spawn["Pos"][1] // 16 + map_zero[1]],
                            5)
                        draw_transparent_circle(surface_to_draw, [enemy_spawn_point[0], enemy_spawn_point[1], 3],
                                                UI_COLOUR_NEW_BACKDROP, 96)

                    # Draw mission objective
                    if mission_details["level"]['objective'] == "Capture":
                        for point in mission_details["level"]['free var']["Cap points"]:
                            pg.draw.circle(surface_to_draw, AMBER, [
                                point["Pos"][0] // 16 + map_zero[0], point["Pos"][1] // 16 + map_zero[1]
                            ], 3)

                surface_to_draw.blit(temp_ui_font.render(f'{mission_details["extra info"]["Mission Reward"]} $', True, AMBER),
                                     (info_zero[0], info_zero[1] + 80))
                if mission_details['level']["modifiers"]:
                    mod_zero = info_zero[0] + 196+16, info_zero[1]
                    surface_to_draw.blit(temp_ui_font.render("Modifiers", True, AMBER), mod_zero)
                    for count, m_mod in enumerate(mission_details['level']["modifiers"]):
                        surface_to_draw.blit(modifier_sprites[m_mod],
                                             # (info_zero[0] + 164+32+16, mod_zero[1] + 18 + 32 * count))
                                             (mod_zero[0] , mod_zero[1] + 18 + 32 * count))
                        surface_to_draw.blit(temp_ui_font.render(m_mod, True, AMBER),
                                             (mod_zero[0] + 33, mod_zero[1] + 18 + 32 * count + 8))

            # Draw shop thing
            if menu_logic.options[menu_logic.selected_option]["Value"] == "Shop":
                temp_ui_font_2 = create_temp_font_5(height)
                info_zero = [256+83, 83]
                colour = [AMBER, [AMBER[0]//2, AMBER[1]//2, AMBER[2]//2]]
                surface_to_draw.blit(
                    temp_ui_font_2.render("Contact <Shopkeeper>?", True, colour[int(timer % 120 < 60)]),
                    (info_zero[0], info_zero[1]))

                for x in range(3):
                    pg.draw.rect(surface_to_draw, colour[int(not 60 * x < timer % 180 < 60 + 60 * x)], [
                        info_zero[0]+1 + 65 * x, info_zero[1] + 30, 55, 6])

            if menu_logic.options[menu_logic.selected_option]["Value"] == "Quit":
                temp_ui_font_2 = create_temp_font_5(height)
                info_zero = [256+83, 83]
                colour = [AMBER, [AMBER[0]//2, AMBER[1]//2, AMBER[2]//2]]
                surface_to_draw.blit(
                    temp_ui_font_2.render("Heading back to base?", True, colour[int(timer % 120 < 60)]),
                    (info_zero[0], info_zero[1]))

                for x in range(3):
                    pg.draw.rect(surface_to_draw, colour[int(not 60 * x < timer % 180 < 60 + 60 * x)], [
                        info_zero[0]+1 + 65 * x, info_zero[1] + 30, 55, 6])

            crt(surface_to_draw)
            surface_to_draw.blit(menu_overlay, [0, 0])
            scale_render(WIN, surface_to_draw, CLOCK)
            transition = menu_transition_handler(WIN, CLOCK, frame_1, transition)
            pg.display.update()
        CLOCK.tick(60)

    # Get the chosen mission
    chosen_mission = {}
    for x in missions_to_choose:
        if x["level"]["name"] == do_shit:
            chosen_mission = x
            break

    return chosen_mission["level"], chosen_mission["extra info"], party_info, out_party, False


def encyclopedia_menu(WIN, CLOCK):
    # Render stuff
    # pg.mixer.music.pause()
    transition, frame_1 = menu_transition_start(WIN)
    menu_sprite = pg.image.load(os.path.join("Sprites/UI/Encyclopedia Screen.png")).convert_alpha()
    menu_overlay = pg.image.load(os.path.join("Sprites/UI/Overlay.png")).convert_alpha()

    encyclopedia =  get_from_json("Encyclopedia.json", "Everything")
    unlocked_entries =  get_from_json("Save.json", "Databank entries unlocked")

    current_position = []
    previous_options = []

    not_disable_unlocks = True
    not_disable_unlocks = False
    options = [
    ]
    for op in encyclopedia:
        on_select = "Return"
        if op not in unlocked_entries and not_disable_unlocks:
            continue
        options.append({"Name": op, "Value": op, "On select": on_select, "Render func": "Text only"})

    options.append({"Name": "Exit databank", "Value": "Quit", "On select": "Return", "Render func": "Text only"})
    menu_logic = UniversalMenuLogic(options)
    menu_logic.width = 5.75
    font_colour = (0, 188, 13)
    backdrop_colour = (0, 101, 13)
    menu_logic.colour_high_vis = font_colour
    menu_logic.colour_med_vis = backdrop_colour
    menu_logic.colour_controls = (0, 244, 13)
    menu_logic.colour_low_vis = UI_COLOUR_NEW_BACKGROUND

    comms_log = UICommunicationLog([
        {"Sender": "SYS", "Message": str_to_list(
            get_random_element_from_list(["Booting up", "Nice ass", "Edging and Gooning"])
        )},
    ], [0, 444-321-3], speed=0, offset=15)
    comms_log.font_func = create_temp_font_1
    comms_log.font_colour = font_colour
    comms_log.text_offset = 35

    sprite_cache = {}

    timer = 0
    flashing_text_on = True
    draw = True
    while True:
        timer += 1

        # Select
        do_shit = menu_logic.act(WIN, CLOCK)
        if do_shit:
            if do_shit == "Quit":
                if not current_position:
                    break
                options = [
                ]

                current_position.pop(-1)

                encyclopedia_section = encyclopedia
                for p in current_position:
                    encyclopedia_section = encyclopedia_section[p]

                for op in encyclopedia_section:
                    if op not in unlocked_entries and not_disable_unlocks:
                        continue
                    options.append({"Name": op, "Value": op, "On select": "Return", "Render func": "Text only"})
                message = "Go back"
                if len(current_position) == 0:
                    message = "Exit databank"
                options.append({"Name": message, "Value": "Quit", "On select": "Return", "Render func": "Text only"})

                menu_logic.options = options
                menu_logic.selected_option = previous_options[-1]
                previous_options.pop(-1)

                log_message = f"Moving to Main section"
                if current_position:
                    log_message = f"Moving to {current_position[-1]}"
                comms_log.elements_to_show.append({"Sender": "SYS", "Message": str_to_list(log_message)})
            else:
                # Do the real shit here
                options = [
                ]
                #
                current_position.append(do_shit)

                encyclopedia_section = encyclopedia
                for p in current_position:
                    encyclopedia_section = encyclopedia_section[p]
                for op in encyclopedia_section:
                    if op not in unlocked_entries and not_disable_unlocks:
                        continue
                    # Text entries are strings, the rest is either a dict or list
                    on_select = "Return"
                    # Had an issue where you had to get into a category stored in a list to go into one stored in a dict
                    # This solution is so stupid, I can't believe that worked

                    try:
                        encyclopedia_section[op]
                    except TypeError:
                        on_select = "Normal"    # Should only be used for text entries, or everything fucks up
                    options.append({"Name": op, "Value": op, "On select": on_select, "Render func": "Text only"})
                options.append({"Name": "Go back", "Value": "Quit", "On select": "Return", "Render func": "Text only"})

                menu_logic.options = options
                previous_options.append(menu_logic.selected_option)
                menu_logic.selected_option = 0
                comms_log.elements_to_show.append({"Sender": "SYS", "Message": str_to_list(f"Moving to {current_position[-1]}")})

            menu_logic.cooldown()

        # |Draw|--------------------------------------------------------------------------------------------------------
        if draw:
            # width, height = WIN.get_size()
            width, height = 630, 450
            frame = pg.Surface((630, 450))
            surface_to_draw = frame
            WIN.fill(BLACK)

            temp_ui_font = create_temp_font_5(height)
            temp_ui_font_2 = create_temp_font_1(height)
            surface_to_draw.fill(UI_COLOUR_BACKGROUND)

            surface_to_draw.blit(menu_sprite, [0, 0])
            surface_to_draw.blit(temp_ui_font.render("D.A.V.E", True, font_colour),
                                 (40, 20))
            menu_logic.draw(surface_to_draw, [30, 50])

            current_entry = menu_logic.options[menu_logic.selected_option]
            line_id = ""
            for p in current_position:
                line_id += p
                line_id += "-"
            if current_entry["On select"] == "Normal":
                surface_to_draw.blit(temp_ui_font.render(current_entry["Name"], True, font_colour),
                                     (300, 30))
                line_id += current_entry["Value"]
                og_text = write_textline(line_id, send_back=True).split("||")
                count = 0
                for sub_text in og_text:
                    for x, text in enumerate(split_text(sub_text, limit=50)):
                        # Check if an image should be rendered
                        try:
                            if text[0] == "~":
                                if text in sprite_cache:
                                    sprite = sprite_cache[text]
                                else:
                                    sprite = get_image(f'Sprites/UI/Encyclopedia images/{text}.png')
                                    sprite_cache.update({text: sprite})
                                surface_to_draw.blit(sprite, (280, 70 + 14 * count))
                                count += sprite.get_height() / 11.5
                                continue
                        except IndexError:
                            # You mad?
                            pass
                        surface_to_draw.blit(temp_ui_font_2.render(text, True, font_colour), (280, 50 + 14 * count))
                        count += 1
            else:
                if timer % 75 == 0:
                    flashing_text_on = not flashing_text_on

                colour = backdrop_colour
                if flashing_text_on:
                    colour = font_colour
                surface_to_draw.blit(temp_ui_font.render("NO DISPLAY DATA", True, colour),
                                     (370, 150))

            comms_display = pg.Surface((249-24, 450-321))
            comms_display.fill((26, 26, 26))
            comms_log.act()
            comms_log.draw(comms_display)

            # crt(comms_display)
            surface_to_draw.blit(comms_display, (24, 321))

            crt(surface_to_draw)
            surface_to_draw.blit(menu_overlay, [0, 0])
            scale_render(WIN, surface_to_draw, CLOCK)
            transition = menu_transition_handler(WIN, CLOCK, frame_1, transition)
            pg.display.update()
        CLOCK.tick(60)


def character_menu_draw(WIN, CLOCK, out_party, menu_logic, transition, win_copy, menu_overlay, character_portraits, player_party):
    # width, height = WIN.get_size()
    width, height = 630, 450
    frame = pg.Surface((630, 450))
    surface_to_draw = frame
    WIN.fill(BLACK)

    temp_ui_font = create_temp_font_2(height, font_name="Sprites/JetBrainsMono-SemiBold.ttf")
    surface_to_draw.fill(UI_COLOUR_BACKGROUND)

    x = 25
    y = 106
    width = 140

    pos = [x - 2 + (width + 4) * len(out_party), y - 2]
    pg.draw.rect(surface_to_draw, UI_COLOUR_NEW_BACKGROUND, [pos[0] + 2, pos[1], width, 344])
    # Draw empty slots
    for count in range(4):
        pos = [x - 2 + (width + 4) * count, y - 2]
        pg.draw.rect(surface_to_draw, DARK_GRAY, [pos[0], pos[1], width + 4, 344], width=1)
        pg.draw.rect(surface_to_draw, BLACK, [pos[0] + 2, pos[1] + 2, 64, 64])

        # Shit on top make it less empty
        pg.draw.rect(surface_to_draw, DARK_GRAY, [pos[0]+2, pos[1] - 70, width , 16], width=1)

    # Draw in current slot, selection and character info
    pos = [x - 2 + (width + 4) * len(out_party), y - 2]
    pg.draw.rect(surface_to_draw, AMBER, [pos[0], pos[1], width + 4, 344], width=1)
    menu_logic.draw(surface_to_draw, [pos[0] + 2, y + 64])
    portrait = menu_logic.options[menu_logic.selected_option]['Value']
    if portrait in character_portraits:
        surface_to_draw.blit(character_portraits[portrait], [pos[0] + 2, pos[1] + 2])
        info = player_party[portrait]
        for c, t in enumerate([
            'Health:',
            f'{info["Health"]}/{info["Info"]["health"]}',
            'Armour:',
            f'{info["Info"]["armour"]}'
        ]):
            surface_to_draw.blit(temp_ui_font.render(t, True, AMBER), [pos[0] + 68, pos[1] + 14 * c + 4])

    # Draw already selected party members
    for count, character in enumerate(out_party):
        pos = [x - 2 + (width + 4) * count, y - 2]

        info = player_party[character[0]]
        pg.draw.rect(surface_to_draw, UI_COLOUR_NEW_BACKGROUND, [pos[0] - 2, pos[1] - 2, width + 4, 344])
        surface_to_draw.blit(character_portraits[character[0]], [pos[0] + 2, pos[1] + 2])
        pg.draw.rect(surface_to_draw, AMBER, [pos[0], pos[1], width + 4, 344], width=1)

        for c, t in enumerate([
            'Health:',
            f'{info["Health"]}/{info["Info"]["health"]}',
            'Armour:',
            f'{info["Info"]["armour"]}'
        ]):
            surface_to_draw.blit(temp_ui_font.render(t, True, AMBER), (pos[0] + 68, pos[1] + 14 * c + 4))

        # Write name, role, input and weapon in versus mode
        surface_to_draw.blit(temp_ui_font.render(write_textline(f"CHAR-DESC-{character[0]}"), True, AMBER),
                             (pos[0] + 2, pos[1] + 68))
        surface_to_draw.blit(temp_ui_font.render(write_textline(f"CHAR-ROLE-{character[0]}"), True, AMBER),
                             (pos[0] + 2, pos[1] + 64 + 14))
        surface_to_draw.blit(temp_ui_font.render("Input", True, AMBER),
                             (pos[0] + 2, pos[1] + 64 + 24))
        surface_to_draw.blit(temp_ui_font.render(character[1], True, AMBER),
                             (pos[0] + 2, pos[1] + 64 + 38))
        if character[2]:
            surface_to_draw.blit(temp_ui_font.render(f"{character[2]}", True, AMBER), (pos[0] + 2, pos[1] + 64 + 52))

    crt(surface_to_draw)
    surface_to_draw.blit(menu_overlay, [0, 0])
    scale_render(WIN, surface_to_draw, CLOCK)
    if transition:
        transition = False
        menu_transition_doom_screen_melt(WIN, CLOCK, WIN, win_copy)
    pg.display.update()
    return transition


def character_menu(WIN, CLOCK, missions_to_choose, player_party, mission_name):
    character_portraits = {
        # THR-1
        "Lord": SPRITE_RADIO_LORD[0],
        "Emperor": SPRITE_RADIO_EMPEROR[0],
        "Wizard": SPRITE_RADIO_WIZARD[0],
        "Sovereign": SPRITE_RADIO_SOVEREIGN[0],
        "Duke": SPRITE_RADIO_DUKE[0],
        "Jester": SPRITE_RADIO_JESTER[0],
        "Condor": SPRITE_RADIO_CONDOR[0],
        # Zoar Colonists
        "Curtis": SPRITE_RADIO_CURTIS[0],
        "Lawrence": SPRITE_RADIO_LAWRENCE[0],
        "Mark": SPRITE_RADIO_MARK[0],
        "Vivianne": SPRITE_RADIO_VIVIANNE[0],
    }
    chosen_mission = missions_to_choose[0]
    for count, e in enumerate(missions_to_choose):
        if e["level"]["name"] == mission_name:
            chosen_mission = e
            break
    # Render stuff
    frame_1 = some_bullshit_for_transitions(WIN)
    transition = True
    win_copy = WIN.copy()
    frame_1.set_alpha(128)
    menu_sprite = pg.image.load(os.path.join("Sprites/UI/Settings Screen.png")).convert_alpha()
    menu_overlay = pg.image.load(os.path.join("Sprites/UI/Overlay.png")).convert_alpha()
    out_party = []  # List of who goes out, along with input methods

    party_limit = 4
    viable_character_num = 0
    for c in player_party:
        if player_party[c]["Health"] > 0:
            viable_character_num += 1
    if viable_character_num < 4:
        party_limit = viable_character_num

    # Get input methods
    input_method_pool = ["Keyboard & Mouse"]
    for count, i in enumerate(ALL_CONTROLLERS[0]):
        if count >= 4:
            break
        input_method_pool.append(f"Controller {count+1}")
    input_method_pool.append("COM")

    draw = True
    keep_going = True
    while len(out_party) < party_limit and keep_going:

        options = []
        for c in player_party:
            if player_party[c]["Health"] > 0:
                # Make sure no repeat happens
                if not check_for_repeat_in_list(out_party, 0, c):
                    name = player_party[c]["Name"]
                    options.append({"Name": name, "Value": name, "On select": "Return", "Render func": "Text only"})
        text = "Exit Menu"
        if len(out_party) > 0:
            text = "Cancel"
            options.append({"Name": "Skip", "Value": "Skip", "On select": "Return", "Render func": "Text only"})
        options.append({"Name": text, "Value": "Return", "On select": "Return", "Render func": "Text only"})


        menu_logic = UniversalMenuLogic(options)
        while True:
            # Select
            do_shit = menu_logic.act(WIN, CLOCK)
            if do_shit:
                if do_shit == "Return":
                    if len(out_party) > 0:
                        # Add back the last
                        out_party.pop(-1)
                    else:
                        return []
                    break
                elif do_shit == "Skip":
                    keep_going = False
                    break
                else:
                    input_method_option = []
                    for i in input_method_pool:
                        if len(out_party) == 0 and i == "COM":
                            continue
                        if not check_for_repeat_in_list(out_party, 1, i) or i == "COM":
                            input_method_option.append(
                                {"Name": i, "Value": i, "On select": "Return", "Render func": "Text only"})
                    input_method_option.append(
                        {"Name": "Cancel", "Value": "Return", "On select": "Return", "Render func": "Text only"})

                    input_method = confirmation_popup(WIN, CLOCK, [315 - 128, 300], input_method_option,
                                                      text="Choose input type")

                    if input_method != "Return":
                        out_party.append([do_shit, input_method, False])
                        break
                menu_logic.cooldown()

            # |Draw|--------------------------------------------------------------------------------------------------------
            if draw:
                transition = character_menu_draw(WIN, CLOCK, out_party, menu_logic, transition, win_copy, menu_overlay,
                                    character_portraits, player_party)
            CLOCK.tick(60)

    # Check if the mission uses the APC
    # Give popup to make player choose who drives the APC
    ask_for_apc = chosen_mission["level"]['objective'] in ["Defense", "Escort"] or "Vehicle can deploy" in chosen_mission["level"]['modifiers']
    if ask_for_apc:
        apc_options = []
        for count, p in enumerate(out_party):
            apc_options.append({"Name": p[0], "Value": count+1, "On select": "Return", "Render func": "Text only"})

        if chosen_mission["level"]['objective'] not in ["Defense", "Escort"]:
            apc_options.append({"Name": "No one", "Value": -1, "On select": "Return", "Render func": "Text only"})

        who_drives_the_apc = confirmation_popup(WIN, CLOCK, [350, 100], apc_options, text="Who drives the APC?")
        if who_drives_the_apc != -1:
            out_party[who_drives_the_apc-1][2] = True

    return out_party


weapon_ownership_table = {
        "Lord": ["Saloum Mk-2", "GMG-04B", "Big Iron"],
        "Emperor": ["GunBlade", "Corrine's Old Rifle", "Oversized stun baton"],
        "Wizard": ["Jeanne's Family Shotgun", "Custom Mk18 Laser cutter", "Crippled Laddie FCS Radio"],
        "Sovereign": ["St-Maurice", "St-Laurent Gen 1", "Mk16 Flare Mortar"],
        "Duke": ["Chain Axe", "Hook Swords", "Gun and Ballistic Knife"],
        "Jester": ["Epicurean Medic Rifle", "Nihilist Stretcher", "Stoic Shield generator"],
        "Condor": ["Type 41 SMG", "Type 23 Shotgun", "Type 47 Rifle"],
        # Zoar Colonists
        "Curtis": ["Standard Shotgun", "War and Peace", "Hunk of Steel"],
        "Lawrence": ["Lawrence's Cutlass & Flintlock", "Captain's Axe & Blunderbuss", "Musket .360"],
        "Mark": ["Mark's Rifle", "Type 30 Rifle", "C4"],
        "Vivianne": ["Vivianne's Rifle", "Vivianne's Shotgun", "Vivianne's Leg"],
}

def weapons_menu(WIN, CLOCK, party_info, run_info, exit_message="Continue", from_shop=False):
    options = []

    # transition = True
    # frame_1 = some_bullshit_for_transitions(WIN)
    # Look for unlocked weapons
    unlocked_weapons = get_from_json("Save.json", "Character weapons unlocked")
    party_members_with_no_weapon_alts = 0
    og_weapons = {}
    for party_member in party_info:
        info = unlocked_weapons[party_member]
        mod = 1
        up_limit = 2
        if not info:
            party_members_with_no_weapon_alts += 1
            continue
        if 1 in info and 2 not in info:
            up_limit = 1
        if 2 in info and 1 not in info:
            mod = 2
            up_limit = 2
        value = 0
        for count, w in enumerate(weapon_ownership_table[party_member]):
            if w == party_info[party_member]["Info"]["weapon"]:
                value = count
                og_weapons.update({party_member: value})
        #  Get value based on weapon
        options.append({"Name": party_member, "Value": value, "On select": "Slider One Step", "Render func": "Slider",
                        "Slider": {"Limits": [0, up_limit], "Mod": mod, "Display mod": 1}}, )
    options.append({"Name": exit_message, "Value": "Return", "On select": "Return", "Render func": "Text only"})

    if party_members_with_no_weapon_alts == len(party_info):
        return

    base_pos = [64, 16]
    bar_width = 200

    character_portraits = {
        # THR-1
        "Lord": pg.transform.scale(SPRITE_RADIO_LORD[0], (48, 48)),
        "Emperor": pg.transform.scale(SPRITE_RADIO_EMPEROR[0], (48, 48)),
        "Wizard": pg.transform.scale(SPRITE_RADIO_WIZARD[0], (48, 48)),
        "Sovereign": pg.transform.scale(SPRITE_RADIO_SOVEREIGN[0], (48, 48)),
        "Duke": pg.transform.scale(SPRITE_RADIO_DUKE[0], (48, 48)),
        "Jester": pg.transform.scale(SPRITE_RADIO_JESTER[0], (48, 48)),
        "Condor": pg.transform.scale(SPRITE_RADIO_CONDOR[0], (48, 48)),
        # Zoar Colonists
        "Curtis": pg.transform.scale(SPRITE_RADIO_CURTIS[0], (48, 48)),
        "Lawrence": pg.transform.scale(SPRITE_RADIO_LAWRENCE[0], (48, 48)),
        "Mark": pg.transform.scale(SPRITE_RADIO_MARK[0], (48, 48)),
        "Vivianne": pg.transform.scale(SPRITE_RADIO_VIVIANNE[0], (48, 48)),
    }

    # Up down. choose the character
    # Sides choose the weapon.
    # Check for unlocks
    frame_1 = some_bullshit_for_transitions(WIN)
    transition = True
    win_copy = WIN.copy()
    frame_1.set_alpha(128)
    menu_overlay = pg.image.load(os.path.join("Sprites/UI/Overlay.png")).convert_alpha()

    menu_logic = UniversalMenuLogic(options)
    draw = True
    while True:
        # Select
        do_shit = menu_logic.act(WIN, CLOCK)
        if do_shit:
            if do_shit in ["Return", "Quit"] and allow_change:
                break
            menu_logic.cooldown()

        cost = 0
        allow_change = True
        if from_shop:
            for e in menu_logic.options:
                if e["Name"] not in og_weapons:
                    continue
                if og_weapons[e["Name"]] == e["Value"]:
                    continue
                p_cost = 500
                if e["Name"] == "Emperor":
                    if "Seduced Shopkeeper" in run_info["Upgrades"]:
                        p_cost = 0
                cost += p_cost
        if run_info["Funds"] < cost:
            allow_change = False
        # |Draw|--------------------------------------------------------------------------------------------------------
        if draw:
            frame = pg.Surface((630, 450))
            surface_to_draw = frame
            WIN.fill(BLACK)

            surface_to_draw.fill(UI_COLOUR_BACKGROUND)

            font = create_temp_font_1(450)

            # Draw instructions
            surface_to_draw.blit(font.render(
                        f"{write_control(menu_logic.controller, 'Up', is_move=True)}"
                        f"{write_control(menu_logic.controller, 'Down', fucking_hell=False)}, "
                        f"{write_textline('Select')}, "
                        f"{write_control(menu_logic.controller, menu_logic.key_binds['Return'])} Continue, "
                        f"{write_control(menu_logic.controller, menu_logic.key_binds['Confirm'])} {write_textline('Menu Choose')}",
                True, UI_COLOUR_TUTORIAL), base_pos)

            # Display how much it would cost to change the weapons, Check for upgrades because of Seduced Shopkeeper
            if from_shop:
                text = f"Total: {cost}"
                y_mod = 0
                for count, op in enumerate(menu_logic.options):
                    if op["Render func"] == "Slider":
                        # if not allow_change and op["Value"] != og_weapons[op["Name"]]:
                        if op["Value"] != og_weapons[op["Name"]]:

                            p_cost = 500
                            if op["Name"] == "Emperor":
                                if "Seduced Shopkeeper" in run_info["Upgrades"]:
                                    p_cost = "Special favour"
                            surface_to_draw.blit(font.render(
                                f"{weapon_ownership_table[op['Name']][round(op['Value'], 1)]} - {p_cost}",
                                True, AMBER), [400, base_pos[1] + 15 + y_mod])
                            y_mod += 15

                if not allow_change:
                    text = f"Total: {cost} - Not enough funds"
                surface_to_draw.blit(font.render(text, True, AMBER), [400, base_pos[1] + 47 + 105 - 15])
                pg.draw.rect(surface_to_draw, (37, 42, 38), (400, base_pos[1] + 47 + 105, 110, 2))

            # Draw options
            y = base_pos[1] + 15
            for count, op in enumerate(menu_logic.options):
                pos = [base_pos[0], y]
                colour = AMBER

                # Show the cursor
                if count == menu_logic.selected_option:
                    pg.draw.rect(surface_to_draw, UI_COLOUR_NEW_BACKDROP, (base_pos[0] - 2, y - 2, 315, 48))

                surface_to_draw.blit(font.render(write_textline(f"{op['Name']}", send_back=True), True, colour), pos)

                if op["Render func"] == "Slider":
                    if not allow_change and op["Value"] != og_weapons[op["Name"]] and not (op["Name"] == "Emperor" and "Seduced Shopkeeper" in run_info["Upgrades"]):
                        colour = RED

                    # Draw portraits to help identify
                    surface_to_draw.blit(character_portraits[op['Name']], (pos[0]-52, pos[1]-2))

                    surface_to_draw.blit(font.render(write_textline(f"{op['Name']}", send_back=True), True, AMBER), pos)

                    bar_x = pos[0] + 110
                    value = round(op['Value'], 1)
                    x_mod = 0

                    pg.draw.rect(surface_to_draw, UI_COLOUR_BACKDROP, (bar_x, pos[1]-1, bar_width, 14))
                    # Write the value
                    surface_to_draw.blit(font.render(f"{weapon_ownership_table[op['Name']][value]}", True,colour),
                                 (bar_x + x_mod, pos[1]))

                    pp_list = [0]
                    for piss in unlocked_weapons[op['Name']]:
                        pp_list.append(piss)
                    pp_list.sort()
                    for count, e in enumerate(pp_list):
                        col = UI_COLOUR_BACKDROP
                        if op['Value'] == e:
                            col = colour
                        pg.draw.rect(surface_to_draw, col, (bar_x + 66 * count + 3, pos[1] + 16, 62, 8))
                pg.draw.rect(surface_to_draw, (37, 42, 38), (pos[0], pos[1] + 47, bar_width + 110, 2))
                y += 51

            crt(surface_to_draw)
            surface_to_draw.blit(menu_overlay, [0, 0])

            scale_render(WIN, surface_to_draw, CLOCK)
            if transition:
                transition = False
                menu_transition_doom_screen_melt(WIN, CLOCK, WIN, win_copy)
            pg.display.update()
        CLOCK.tick(60)

    # Rewrite run info to switch the weapons.
    for party_member in party_info:
        for op in menu_logic.options:
            if op["Name"] == party_member:
                num = op["Value"]
                party_info[party_member]["Info"]["weapon"] = weapon_ownership_table[party_member][num]
                continue


def versus_arena_menu(WIN, CLOCK, missions_to_choose, party_info):
    # Render stuff

    transition, frame_1 = menu_transition_start(WIN)

    menu_sprite = pg.image.load(os.path.join("Sprites/UI/Settings Screen.png")).convert_alpha()
    menu_overlay = pg.image.load(os.path.join("Sprites/UI/Overlay.png")).convert_alpha()

    # Info needed for shit
    mission_names = []
    for n in missions_to_choose:
        mission_names.append(n["level"]["name"])

    options = [
    ]
    for mission in mission_names:
        options.append({"Name": mission, "Value": mission, "On select": "Return", "Render func": "Text only"},)

    options.append({"Name": "Go back to main menu", "Value": "Quit", "On select": "Return", "Render func": "Text only"},)
    menu_logic = UniversalMenuLogic(options)
    menu_logic.width = 2.8

    new_player_party_info = {}
    x_mod = -210-63
    draw = True
    while True:
        if x_mod < 0:
            x_mod += 21
        # Select
        do_shit = menu_logic.act(WIN, CLOCK)
        if do_shit:
            if do_shit in mission_names:
                # Character select, use the character selection menu modified to let you choose weapons
                out_party = versus_character_menu(WIN, CLOCK, missions_to_choose, party_info, do_shit)

                if out_party:
                    # return_value = do_shit
                    # return_value = new_player_party_info
                    break
            if do_shit == "Quit":
                return {}, {}, party_info, [], True
            menu_logic.cooldown()

        # |Draw|--------------------------------------------------------------------------------------------------------
        if draw:
            # width, height = WIN.get_size()
            width, height = 630, 450
            frame = pg.Surface((630, 450))
            surface_to_draw = frame
            WIN.fill(BLACK)

            temp_ui_font = create_temp_font_1(height)
            surface_to_draw.fill(UI_COLOUR_BACKGROUND)

            # surface_to_draw.blit(frame_1, (0, 0))
            surface_to_draw.blit(menu_sprite, [x_mod, 0])
            surface_to_draw.blit(temp_ui_font.render(write_textline("Mission title"), True, AMBER), (25 + x_mod, 25))
            menu_logic.draw(surface_to_draw, [30 + x_mod, 50])

            if menu_logic.options[menu_logic.selected_option]["Value"] in mission_names:
                # Get mission details
                num = 0
                for count, name in enumerate(mission_names):
                    if name == menu_logic.options[menu_logic.selected_option]["Value"]:
                        num = count
                        break
                mission_details = missions_to_choose[num]

                # 320
                info_zero = [256+16, 128- 96-8]
                surface_to_draw.blit(temp_ui_font.render(mission_details['level']["name"], True, AMBER),
                                     (info_zero[0], info_zero[1]))
                if mission_details["level"]['modifiers'] != ["Skip mission"]:
                    # Draw map of the mission
                    map_zero = [256+16, 48+16]
                    for wall in mission_details["level"]["map"]:
                        pg.draw.rect(surface_to_draw, UI_COLOUR_NEW_BACKDROP, [
                            wall.left // 16 + map_zero[0], wall.top // 16 + map_zero[1],
                            wall.width // 16, wall.height // 16])

                    # Draw spawn point
                    for spawn_point in mission_details["extra info"]["Spawn"]:
                        pg.draw.rect(surface_to_draw, AMBER_LIGHT, [
                            spawn_point[0] // 16 + map_zero[0], spawn_point[1] // 16 + map_zero[1], 2, 2
                        ])

            crt(surface_to_draw)
            surface_to_draw.blit(menu_overlay, [0, 0])
            scale_render(WIN, surface_to_draw, CLOCK)
            transition = menu_transition_handler(WIN, CLOCK, frame_1, transition)
            pg.display.update()
        CLOCK.tick(60)

    # Get the chosen mission
    chosen_mission = {}
    for x in missions_to_choose:
        if x["level"]["name"] == do_shit:
            chosen_mission = x
            break

    return chosen_mission["level"], chosen_mission["extra info"], party_info, out_party, False


def versus_character_menu(WIN, CLOCK, missions_to_choose, player_party, mission_name):
    unlocked_weapons = get_from_json("Save.json", "Character weapons unlocked")
    character_portraits = {
        # THR-1
        "Lord": SPRITE_RADIO_LORD[0],
        "Emperor": SPRITE_RADIO_EMPEROR[0],
        "Wizard": SPRITE_RADIO_WIZARD[0],
        "Sovereign": SPRITE_RADIO_SOVEREIGN[0],
        "Duke": SPRITE_RADIO_DUKE[0],
        "Jester": SPRITE_RADIO_JESTER[0],
        "Condor": SPRITE_RADIO_CONDOR[0],
        # Zoar Colonists
        "Curtis": SPRITE_RADIO_CURTIS[0],
        "Lawrence": SPRITE_RADIO_LAWRENCE[0],
        "Mark": SPRITE_RADIO_MARK[0],
        "Vivianne": SPRITE_RADIO_VIVIANNE[0],
    }
    chosen_mission = missions_to_choose[0]
    for count, e in enumerate(missions_to_choose):
        if e["level"]["name"] == mission_name:
            chosen_mission = e
            break
    # Render stuff
    # pg.mixer.music.pause()
    frame_1 = some_bullshit_for_transitions(WIN)
    transition = True

    win_copy = WIN.copy()
    frame_1.set_alpha(128)
    menu_sprite = pg.image.load(os.path.join("Sprites/UI/Settings Screen.png")).convert_alpha()
    menu_overlay = pg.image.load(os.path.join("Sprites/UI/Overlay.png")).convert_alpha()
    out_party = []  # List of who goes out, along with input methods

    party_limit = 4
    viable_character_num = 0
    for c in player_party:
        if player_party[c]["Health"] > 0:
            viable_character_num += 1
    if viable_character_num < 4:
        party_limit = viable_character_num

    # Get input methods
    input_method_pool = ["Keyboard & Mouse"]
    for count, i in enumerate(ALL_CONTROLLERS[0]):
        if count >= 4:
            break
        input_method_pool.append(f"Controller {count+1}")
    input_method_pool.append("COM")

    draw = True
    keep_going = True
    while len(out_party) < party_limit and keep_going:

        options = []
        for c in player_party:
            name = player_party[c]["Name"]
            options.append({"Name": name, "Value": name, "On select": "Return", "Render func": "Text only"})
        text = "Exit Menu"
        if len(out_party) > 0:
            text = "Cancel"
            if len(out_party) >= 2:
                options.append({"Name": "Skip", "Value": "Skip", "On select": "Return", "Render func": "Text only"})
        options.append({"Name": text, "Value": "Return", "On select": "Return", "Render func": "Text only"})

        menu_logic = UniversalMenuLogic(options)
        while True:
            # Select
            do_shit = menu_logic.act(WIN, CLOCK)
            if do_shit:
                if do_shit == "Return":
                    if len(out_party) > 0:
                        # Add back the last
                        out_party.pop(-1)
                    else:
                        return []
                    break
                elif do_shit == "Skip":
                    keep_going = False
                    break
                else:
                    # Builds the pop up to choose input type
                    input_method_option = []
                    for i in input_method_pool:
                        if len(out_party) == 0 and i == "COM":
                            continue

                        allow_non_com_input = True
                        for used_input_method in out_party:
                            if i == used_input_method[1] and i != "COM":
                                allow_non_com_input = False
                                break
                        if allow_non_com_input:
                            input_method_option.append(
                                {"Name": i, "Value": i, "On select": "Return", "Render func": "Text only"})
                    input_method_option.append(
                        {"Name": "Cancel", "Value": "Return", "On select": "Return", "Render func": "Text only"})
                    input_method = confirmation_popup(WIN, CLOCK, [315 - 128, 300], input_method_option,
                                                      text="Choose input type")
                    # Check for alt weapons
                    chosen_weapon = 0
                    if unlocked_weapons[do_shit]:
                        weapon_options = [
                            {"Name": f"{weapon_ownership_table[do_shit][0]}", "Value": 1, "On select": "Return",
                             "Render func": "Text only"}
                        ]

                        for i in unlocked_weapons[do_shit]:
                            weapon_options.append(
                                {"Name": f"{weapon_ownership_table[do_shit][i]}", "Value": i+1, "On select": "Return",
                                 "Render func": "Text only"})

                        chosen_weapon = confirmation_popup(WIN, CLOCK, [315 - 128, 300], weapon_options,
                                                          text="Choose weapon")

                    if input_method != "Return":
                        out_party.append([do_shit, input_method, weapon_ownership_table[do_shit][chosen_weapon-1]])

                        break
                menu_logic.cooldown()

            # |Draw|--------------------------------------------------------------------------------------------------------
            if draw:

                transition = character_menu_draw(WIN, CLOCK, out_party, menu_logic, transition, win_copy, menu_overlay,
                                    character_portraits, player_party)
            CLOCK.tick(60)
    return out_party


def versus_end_menu(WIN, CLOCK, party_info, status):
    stop_music()
    b = "Secretary" # use a bird name, she is part of the Nest but

    elements_to_show = [
                 {"Sender": "SYS", "Message": str_to_list(f"FIGHT IS OVER.")},
             ]
    elements_to_show_2 =[]
    menu_overlay = pg.image.load(os.path.join("Sprites/UI/Overlay.png")).convert_alpha()
    key_pressed = DEFAULT_KEY_PRESSED * 4

    frame_1 = some_bullshit_for_transitions(WIN)
    transition = True
    win_copy = WIN.copy()
    controller = PseudoPlayer()

    menu_render = UICommunicationLog(elements_to_show, [15, 300], speed=1)
    menu_render_2 = UICommunicationLog(elements_to_show_2, [280, 280], speed=1)
    end_timer = 60 * 60
    while end_timer > 0:
        frame = pg.Surface((630, 450))
        surface_to_draw = frame
        WIN.fill(BLACK)
        surface_to_draw.fill(UI_COLOUR_BACKGROUND)
        menu_render.act()
        menu_render.draw(surface_to_draw)
        menu_render_2.act()
        menu_render_2.draw(surface_to_draw)
        # Let the player skip
        keys = pg.key.get_pressed()
        needed_in_menu_and_game(WIN, keys)
        controller.get_input(keys)
        no_input = True
        for i in controller.input:
            if controller.input[i]:
                no_input = False
                break
        if key_pressed == 0:
            if not no_input:
                break
        elif no_input:
            key_pressed -= 1
        pg.draw.rect(surface_to_draw, AMBER_LIGHT, (12, 450 - 40, 606 * (end_timer / (60 * 60)), 4))
        crt(surface_to_draw)
        surface_to_draw.blit(menu_overlay, [0, 0])
        scale_render(WIN, surface_to_draw, CLOCK)

        if transition:
            transition = False
            menu_transition_doom_screen_melt(WIN, CLOCK, WIN, win_copy)
            play_music("Menu")
        pg.display.update()
        CLOCK.tick(60)
        end_timer -= 1


UPGRADE_SHEET = get_image('Sprites/UI/Upgrades Sheet.png')

BLUE_BALL_UPGRADES = ["Dashing Blue Balls", "Kicking Blue Balls", "Busting Blue Balls", "Brittle Blue Balls", "Kicking Blue Balls", "Tail & Blue Balls", "Unbreaking Blue Balls",
                      "Burning Blue Balls", "Blue Ballin", "Marked Blue Balls"]
COST_Z, COST_L, COST_LM, COST_M, COST_MH, COST_H  = 0, 200, 500, 1000, 1500, 2000
UPGRADE_INFO = {
# "Friendly Fire On": {'Tier': 1, 'Cost': 0, 'Owner': 'Party', 'name': 'Friendly Fire On', 'effect': 'effect_none', 'trigger': 'trigger_standing_still'},
# "Free Healthcare": {'Tier': 3, 'Cost': 20000, 'Owner': 'Party', 'Condition': {'Require': ['Friendly Fire On']}, 'name': 'Free Healthcare', 'effect': 'effect_none', 'trigger': 'trigger_standing_still'},
# "Driving License": {
#     'Tier': 1, 'Cost': 1, 'Owner': 'Party', 'Icon': UPGRADE_SHEET.subsurface(80, 560, 40, 40),
#     'name': 'Driving License', 'effect': 'effect_none', 'trigger': 'trigger_when_loaded'},
"Awareness": {
    'Tier': 1, 'Cost': COST_LM, 'Owner': 'Party', 'Icon': UPGRADE_SHEET.subsurface(0, 480, 40, 40),
    'name': 'Awareness', 'effect': 'effect_awareness', 'trigger': 'trigger_when_loaded'},

"Lucky Shot": {
    'Tier': 1, 'Cost': COST_LM, 'Owner': 'Party', 'Icon': UPGRADE_SHEET.subsurface(0, 520, 40, 40),
    'name': 'Lucky Shot', 'effect': 'effect_lucky_shot', 'trigger': 'trigger_when_loaded'},
"Safe Bet": {
    'Tier': 2, 'Cost': COST_M, 'Owner': 'Party', 'Condition': {'Require': ['Lucky Shot'], 'No': 'All in'}, 'Icon': UPGRADE_SHEET.subsurface(40, 520, 40, 40),
    'name': 'Safe Bet', 'effect': 'effect_safe_bet', 'trigger': 'trigger_when_loaded'},
"All in": {
    'Tier': 2, 'Cost': COST_M, 'Owner': 'Party', 'Condition': {'Require': ['Lucky Shot'], 'No': 'Safe Bet'}, 'Icon': UPGRADE_SHEET.subsurface(120, 520, 40, 40),
    'name': 'All in', 'effect': 'effect_all_in', 'trigger': 'trigger_when_loaded'},
"Risk Management": {
    'Tier': 3, 'Cost': COST_M, 'Owner': 'Party', 'Condition': {'Require': ['Safe Bet']}, 'Icon': UPGRADE_SHEET.subsurface(80, 520, 40, 40),
    'name': 'Risk Management', 'effect': 'effect_risk_management', 'trigger': 'trigger_when_loaded'},
"Double Down": {
    'Tier': 3, 'Cost': COST_M, 'Owner': 'Party', 'Condition': {'Require': ['All in']}, 'Icon': UPGRADE_SHEET.subsurface(160, 520, 40, 40),
    'name': 'Double Down', 'effect': 'effect_double_down', 'trigger': 'trigger_when_loaded'},

"Seeking Blue Balls": {
    'Tier': 2, 'Cost': COST_M, 'Owner': 'Party', 'Condition': {'Require': BLUE_BALL_UPGRADES , 'No': 'Bouncing Blue Balls'}, 'Icon': UPGRADE_SHEET.subsurface(0, 720, 40, 40),
    'name': 'Seeking Blue Balls', 'effect': 'effect_give_blue_balls', 'trigger': 'trigger_when_loaded'},
"Bouncing Blue Balls": {
    'Tier': 2, 'Cost': COST_M, 'Owner': 'Party', 'Condition': {'Require': BLUE_BALL_UPGRADES , 'No': 'Seeking Blue Balls'}, 'Icon': UPGRADE_SHEET.subsurface(40, 720, 40, 40),
    'name': 'Bouncing Blue Balls', 'effect': 'effect_give_blue_balls', 'trigger': 'trigger_when_loaded'},
"Speeding Blue Balls": {
    'Tier': 2, 'Cost': COST_M, 'Owner': 'Party', 'Condition': {'Require': BLUE_BALL_UPGRADES}, 'Icon': UPGRADE_SHEET.subsurface(80, 720, 40, 40),
    'name': 'Speeding Blue Balls', 'effect': 'effect_give_blue_balls', 'trigger': 'trigger_when_loaded'},
"Piercing Blue Balls": {
    'Tier': 2, 'Cost': COST_M, 'Owner': 'Party', 'Condition': {'Require': BLUE_BALL_UPGRADES, 'No': 'Durable Blue Balls'}, 'Icon': UPGRADE_SHEET.subsurface(120, 720, 40, 40),
    'name': 'Piercing Blue Balls', 'effect': 'effect_give_blue_balls', 'trigger': 'trigger_when_loaded'},
"Durable Blue Balls": {
    'Tier': 2, 'Cost': COST_M, 'Owner': 'Party', 'Condition': {'Require': BLUE_BALL_UPGRADES, 'No': 'Piercing Blue Balls'}, 'Icon': UPGRADE_SHEET.subsurface(160, 720, 40, 40),
    'name': 'Durable Blue Balls', 'effect': 'effect_give_blue_balls', 'trigger': 'trigger_when_loaded'},
"Homing Blue Balls": {
    'Tier': 3, 'Cost': COST_MH, 'Owner': 'Party', 'Condition': {'Require': ['Seeking Blue Balls']}, 'Icon': UPGRADE_SHEET.subsurface(0, 760, 40, 40),
    'name': 'Homing Blue Balls', 'effect': 'effect_give_blue_balls', 'trigger': 'trigger_when_loaded'},
"Bouncy Blue Balls": {
    'Tier': 3, 'Cost': COST_MH, 'Owner': 'Party', 'Condition': {'Require': ['Bouncing Blue Balls']}, 'Icon': UPGRADE_SHEET.subsurface(40, 760, 40, 40),
    'name': 'Bouncy Blue Balls', 'effect': 'effect_give_blue_balls', 'trigger': 'trigger_when_loaded'},

"Additional Body Armour": {
    'Tier': 1, 'Cost': COST_M, 'Owner': 'Party', 'Icon': UPGRADE_SHEET.subsurface(40, 480, 40, 40),
    'name': 'Additional Body Armour', 'effect': 'effect_additional_body_armour', 'trigger': 'trigger_when_loaded'},

"Reinforced Plates": {
    'Tier': 2, 'Cost': COST_M, 'Owner': 'Party', 'Condition': {'Require': ['Additional Body Armour'], 'No': ["Fire Retardant Armour", "Anti Boom Boom Armour", "Anti Laser Coating"]},
    'Icon': UPGRADE_SHEET.subsurface(80, 480, 40, 40), 'name': 'Reinforced Plates', 'effect': 'effect_reinforced_plates', 'trigger': 'trigger_when_loaded'},
"Fire Retardant Armour": {
    'Tier': 2, 'Cost': COST_M, 'Owner': 'Party', 'Condition': {'Require': ['Additional Body Armour'], 'No': ["Reinforced Plates", "Anti Boom Boom Armour", "Anti Laser Coating"]},
    'Icon': UPGRADE_SHEET.subsurface(120, 480, 40, 40), 'name': 'Reinforced Plates', 'effect': 'effect_fire_retardant_armour', 'trigger': 'trigger_when_loaded'},
"Anti Boom Boom Armour": {
    'Tier': 2, 'Cost': COST_M, 'Owner': 'Party', 'Condition': {'Require': ['Additional Body Armour'], 'No': ["Reinforced Plates", "Fire Retardant Armour", "Anti Laser Coating"]},
    'Icon': UPGRADE_SHEET.subsurface(160, 480, 40, 40), 'name': 'Reinforced Plates', 'effect': 'effect_anti_boom_boom_armour', 'trigger': 'trigger_when_loaded'},
"Anti Laser Coating": {
    'Tier': 2, 'Cost': COST_M, 'Owner': 'Party', 'Condition': {'Require': ['Additional Body Armour'], 'No': ["Reinforced Plates", "Fire Retardant Armour", "Anti Boom Boom Armour"]},
    'Icon': UPGRADE_SHEET.subsurface(200, 480, 40, 40), 'name': 'Anti Laser Coating', 'effect': 'effect_anti_laser_coating', 'trigger': 'trigger_when_loaded'},

"Breaking Limits": {
    'Tier': 3, 'Cost': COST_H * 1.5, 'Owner': 'Party', 'Icon': UPGRADE_SHEET.subsurface(240, 480, 40, 40),
    'name': 'Breaking Limits', 'effect': 'effect_none', 'trigger': 'trigger_when_loaded'},

"Skill Issue": {
    'Tier': 2, 'Cost': COST_LM, 'Owner': 'Party', 'Icon': UPGRADE_SHEET.subsurface(0, 560, 40, 40),
    'Condition': {'No': ["Skill Solution"]},
    'name': 'Skill Issue', 'effect': 'effect_skill_issue', 'trigger': 'trigger_when_loaded'},
"Skill Solution": {
    'Tier': 2, 'Cost': COST_LM, 'Owner': 'Party', 'Icon': UPGRADE_SHEET.subsurface(40, 560, 40, 40),
    'Condition': {'No': ["Skill Issue"]},
    'name': 'Skill Solution', 'effect': 'effect_skill_solution', 'trigger': 'trigger_when_loaded'},


# Lord
"3rd Degree Burn": {
    'Tier': 1, 'Cost': COST_LM, 'Owner': 'Lord', 'Condition': {'No': 'Shrapnel'}, 'Icon': UPGRADE_SHEET.subsurface(0, 0, 40, 40),
    'name': '3rd Degree Burn', 'effect': 'effect_3rd_degree', 'trigger': 'trigger_on_hit_effect'},
"Shrapnel": {
    'Tier': 1, 'Cost': COST_MH, 'Owner': 'Lord', 'Condition': {'No': '3rd Degree Burn'}, 'Icon': UPGRADE_SHEET.subsurface(40, 0, 40, 40),
    'name': 'Shrapnel', 'effect': 'effect_shrapnel', 'trigger': 'trigger_on_hit_effect'},
"Giga ton Punch": {
    'Tier': 1, 'Cost': COST_LM, 'Owner': 'Lord', 'Icon': UPGRADE_SHEET.subsurface(80, 0, 40, 40),
    'name': 'Giga ton Punch', 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},
"Taunt": {
    'Tier': 1, 'Cost': COST_L, 'Owner': 'Lord', 'Icon': UPGRADE_SHEET.subsurface(120, 0, 40, 40),
    'name': 'Taunt', 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},
"Rubber grenades": {
    'Tier': 2, 'Cost': COST_M, 'Owner': 'Lord', 'Condition': {'Require': ['3rd Degree Burn', 'Shrapnel']}, 'Icon': UPGRADE_SHEET.subsurface(160, 0, 40, 40),
    'name': 'Rubber grenades', 'effect': 'effect_rubber_grenades', 'trigger': 'trigger_on_hit_effect'},
"Bigger Booms": {
    'Tier': 2, 'Cost': COST_M, 'Owner': 'Lord', 'Condition': {'Require': ['3rd Degree Burn', 'Shrapnel']}, 'Icon': UPGRADE_SHEET.subsurface(200, 0, 40, 40),
    'name': 'Bigger Booms', 'effect': 'effect_bigger_booms', 'trigger': 'trigger_when_loaded'},
"Can't touch me": {
    'Tier': 2, 'Cost': COST_MH, 'Owner': 'Lord', 'Condition': {'Require': ['Taunt', 'Giga ton Punch']}, 'Icon': UPGRADE_SHEET.subsurface(240, 0, 40, 40),
    'name': "Can't touch me", 'effect': 'effect_cant_touch_me', 'trigger': 'trigger_max_agro'},
"Remote Detonation": {
    'Tier': 3, 'Cost': COST_MH, 'Owner': 'Lord', 'Condition': {'Require': ['Rubber grenades', 'Bigger Booms', "Can't touch me"]}, 'Icon': UPGRADE_SHEET.subsurface(280, 0, 40, 40),
    'name': 'Remote Detonation', 'effect': 'effect_remote_detonation', 'trigger': 'trigger_interact_key'},
"Super Duper Ultimate Death Defying Plus Ultra Supreme Heavenly Beast Mode DELUXE": {
    'Tier': 3, 'Cost': COST_H, 'Owner': 'Lord', 'Icon': UPGRADE_SHEET.subsurface(320, 0, 40, 40),
    'name': 'Super Duper Ultimate Death Defying Plus Ultra Supreme Heavenly Beast Mode DELUXE', 'effect': 'effect_sduddpushbmd', 'trigger': 'trigger_when_loaded'},
"Dashing Blue Balls": {
    'Tier': 2, 'Cost': COST_MH, 'Owner': 'Lord', 'Icon': UPGRADE_SHEET.subsurface(360, 0, 40, 40),
    'name': 'Dashing Blue Balls', 'effect': 'effect_dashing_blue_balls', 'trigger': 'trigger_dash'},

# Emperor
"Kick and Run": {
    'Tier': 1, 'Cost': COST_M, 'Owner': 'Emperor', 'Icon': UPGRADE_SHEET.subsurface(0, 40, 40, 40),
    'name': 'Kick and Run', 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},
"Seduced Shopkeeper": { #
    'Tier': 1, 'Cost': COST_Z, 'Owner': 'Emperor', 'Icon': UPGRADE_SHEET.subsurface(40, 40, 40, 40),
    'name': 'Seduced Shopkeeper', 'effect': 'effect_none', 'trigger': 'trigger_when_loaded'},
"Overly Prepared": {# Gives  bonuses at the start of a mission
    'Tier': 1, 'Cost': COST_LM, 'Owner': 'Emperor', 'Icon': UPGRADE_SHEET.subsurface(80, 40, 40, 40),
    'name': 'Emperor Tier 1 2', 'effect': 'effect_overly_prepared', 'trigger': 'trigger_when_loaded'},
"Kick to the Balls": {
    'Tier': 2, 'Cost': COST_M, 'Owner': 'Emperor', 'Icon': UPGRADE_SHEET.subsurface(120, 40, 40, 40),
    'name': 'Kick to the Balls', 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},
"Skilled": {
    'Tier': 2, 'Cost': COST_M, 'Owner': 'Emperor', 'Icon': UPGRADE_SHEET.subsurface(160, 40, 40, 40),
    'name': 'Skilled', 'effect': 'effect_skill_skilled', 'trigger': 'trigger_when_loaded'},
"Bad Luck?": {
    'Tier': 2, 'Cost': COST_LM, 'Owner': 'Emperor', 'Icon': UPGRADE_SHEET.subsurface(200, 40, 40, 40),
    'name': 'Bad Luck?', 'effect': 'effect_bad_luck', 'trigger': 'trigger_when_loaded'},
"Mastermind": {
    'Tier': 2, 'Cost': COST_M, 'Owner': 'Emperor', 'Icon': UPGRADE_SHEET.subsurface(240, 40, 40, 40),
    'name': 'Mastermind', 'effect': 'effect_mastermind', 'trigger': 'trigger_mastermind'},
"Alpha Buff": {
    'Tier': 3, 'Cost': COST_L, 'Owner': 'Emperor', 'Icon': UPGRADE_SHEET.subsurface(280, 40, 40, 40),
    'name': 'Alpha Buff', 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},
"Omega Buff": {
    'Tier': 3, 'Cost': COST_MH, 'Owner': 'Emperor', 'Icon': UPGRADE_SHEET.subsurface(320, 40, 40, 40),
    'name': 'Omega Buff', 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},
"Kicking Blue Balls": {
    'Tier': 2, 'Cost': COST_M, 'Owner': 'Emperor', 'Icon': UPGRADE_SHEET.subsurface(360, 40, 40, 40),
    'name': 'Kicking Blue Balls', 'effect': 'effect_kicking_blue_balls', 'trigger': 'trigger_kicking_blue_balls'},

# Wizard
"Overclocked": {
    'Tier': 1, 'Cost': COST_LM, 'Owner': 'Wizard', 'Icon': UPGRADE_SHEET.subsurface(0, 80, 40, 40),
    'name': 'Overclocked', 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},
"Sturdy Building": {
    'Tier': 1, 'Cost': COST_L, 'Owner': 'Wizard', 'Icon': UPGRADE_SHEET.subsurface(40, 80, 40, 40),
    'name': 'Sturdy Building', 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},
"Self Destruct": {
    'Tier': 2, 'Cost': COST_LM, 'Owner': 'Wizard', 'Condition': {'Require': ['Overclocked']}, 'Icon': UPGRADE_SHEET.subsurface(120, 80, 40, 40),
    'name': 'Self Destruct', 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},
"Field Repair": {
    'Tier': 2, 'Cost': COST_M, 'Owner': 'Wizard', 'Condition': {'Require': ['Overclocked', 'Sturdy Building']}, 'Icon': UPGRADE_SHEET.subsurface(160, 80, 40, 40),
    'name': 'Field Repair', 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},
"Special Coating": {
    'Tier': 2, 'Cost': COST_M, 'Owner': 'Wizard', 'Condition': {'Require': ['Overclocked', 'Sturdy Building']}, 'Icon': UPGRADE_SHEET.subsurface(200, 80, 40, 40),
    'name': 'Special Coating', 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},
"Resupply": {
    'Tier': 2, 'Cost': COST_M, 'Owner': 'Wizard', 'Condition': {'Require': ['Sturdy Building']}, 'Icon': UPGRADE_SHEET.subsurface(240, 80, 40, 40),
    'name': 'Resupply', 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},
"Engineering Mayhem": {
    'Tier': 3, 'Cost': COST_MH, 'Owner': 'Wizard', 'Condition': {'Require': ['Self Destruct', 'Field Repair', 'Special Coating', 'Resupply']}, 'Icon': UPGRADE_SHEET.subsurface(320, 80, 40, 40),
    'name': 'Engineering Mayhem', 'effect': 'effect_engineering_mayhem', 'trigger': 'trigger_when_loaded'},
"Short Temper": {
    'Tier': 1, 'Cost': COST_M, 'Owner': 'Wizard', 'Icon':UPGRADE_SHEET.subsurface(80, 80, 40, 40),
    'name': 'Short Temper', 'effect': 'effect_short_temper', 'trigger': 'trigger_on_hit'},
"Wrench Wench": {
    'Tier': 2, 'Cost': COST_M, 'Owner': 'Wizard', 'Condition': {'Require': ['Short Temper']}, 'Icon': UPGRADE_SHEET.subsurface(280, 80, 40, 40),
    'name': 'Wrench Wench', 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},
"Action Girl": {
    'Tier': 3, 'Cost': COST_MH, 'Owner': 'Wizard', 'Condition': {'Require': ['Wrench Wench']}, 'Icon': UPGRADE_SHEET.subsurface(400, 80, 40, 40),
    'name': 'Action Girl', 'effect': 'effect_action_girl', 'trigger': 'trigger_when_loaded'},
"Busting Blue Balls": {
    'Tier': 2, 'Cost': COST_LM, 'Owner': 'Wizard', 'Icon': UPGRADE_SHEET.subsurface(360, 80, 40, 40),
    'name': 'Busting Blue Balls', 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},

# Sovereign
"Trick shot": {
    'Tier': 1, 'Cost': COST_L, 'Owner': 'Sovereign', 'Icon': UPGRADE_SHEET.subsurface(0, 160, 40, 40),
    'name': 'Trick shot', 'effect': 'effect_trick_shot', 'trigger': 'trigger_on_hit_effect'},
"Scavenge": {
    'Tier': 1, 'Cost': COST_L, 'Owner': 'Sovereign', 'Icon': UPGRADE_SHEET.subsurface(40, 160, 40, 40),
    'name': 'Scavenge', 'effect': 'effect_scavenge', 'trigger': 'trigger_on_hit_effect'},
"Duck and Cover": {
    'Tier': 1, 'Cost': COST_LM, 'Owner': 'Sovereign', 'Icon': UPGRADE_SHEET.subsurface(80, 160, 40, 40),
    'name': 'Duck and Cover', 'effect': 'effect_duck_and_cover', 'trigger': 'trigger_dash'},
"Stick more in": {
    'Tier': 2, 'Cost': COST_M, 'Owner': 'Sovereign',  'Condition': {'Require': ["Trick shot", "Scavenge"]}, 'Icon': UPGRADE_SHEET.subsurface(120, 160, 40, 40),
    'name': 'Stick more in', 'effect': 'effect_stick_more_in', 'trigger': 'trigger_when_loaded'},
"I See You!": {
    'Tier': 2, 'Cost': COST_MH, 'Owner': 'Sovereign',  'Condition': {'Require': ["Trick shot", "Scavenge"]}, 'Icon': UPGRADE_SHEET.subsurface(160, 160, 40, 40),
    'name': 'I See You!', 'effect': 'effect_i_see_you', 'trigger': 'trigger_on_hit_effect'},
"Nothing to see!": {
    'Tier': 2, 'Cost': COST_M, 'Owner': 'Sovereign',  'Condition': {'Require': ["Duck and Cover"]}, 'Icon': UPGRADE_SHEET.subsurface(200, 160, 40, 40),
    'name': 'Nothing to see!', 'effect': 'effect_nothing_to_see', 'trigger': 'trigger_when_loaded'},
"Safety Corner": {
    'Tier': 2, 'Cost': COST_MH, 'Owner': 'Sovereign',  'Condition': {'Require': ["Duck and Cover"]}, 'Icon': UPGRADE_SHEET.subsurface(240, 160, 40, 40),
    'name': 'Nothing to see!', 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},
"Mini Rambo": {
    'Tier': 3, 'Cost': COST_H, 'Owner': 'Sovereign',  'Condition': {'Require': ["Stick more in", "I See You!"]},
    'Icon': UPGRADE_SHEET.subsurface(280, 160, 40, 40),
    'name': 'Mini Rambo', 'effect': 'effect_action_girl', 'trigger': 'trigger_when_loaded'},
"Eagle Eye": {
    'Tier': 3, 'Cost': COST_MH, 'Owner': 'Sovereign',  'Condition': {'Require': ["Nothing to see!", "Safety Corner"]},
    'Icon': UPGRADE_SHEET.subsurface(320, 160, 40, 40),
    'name': 'Eagle Eye', 'effect': 'effect_eagle_eye', 'trigger': 'trigger_when_loaded'},
"Exposed Blue Balls": {
    'Tier': 2, 'Cost': COST_H, 'Owner': 'Sovereign', 'Icon': UPGRADE_SHEET.subsurface(360, 160, 40, 40),
    'name': 'Exposed Blue Balls', 'effect': 'effect_exposed_blue_balls', 'trigger': 'trigger_exposed_blue_balls'},

# Duke
"Stun Strike": {
    'Tier': 1, 'Cost': COST_L, 'Owner': 'Duke', 'Condition': {'No': "Poison Strike"}, 'Icon': UPGRADE_SHEET.subsurface(0, 200, 40, 40),
    'name': 'Stun Strike', 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},
"Poison Strike": {
    'Tier': 1, 'Cost': COST_L, 'Owner': 'Duke', 'Condition': {'No': "Stun Strike"}, 'Icon': UPGRADE_SHEET.subsurface(40, 200, 40, 40),
    'name': 'Poison Strike', 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},
"Shadow Walk": {
    'Tier': 1, 'Cost': COST_L, 'Owner': 'Duke', 'Icon': UPGRADE_SHEET.subsurface(80, 200, 40, 40),
    'name': 'Shadow Walk', 'effect': 'effect_shadow_walk', 'trigger': 'trigger_when_loaded'},
"Discombobulate": {
    'Tier': 2, 'Cost': COST_LM, 'Owner': 'Duke', 'Condition': {'Require': ["Stun Strike"]}, 'Icon': UPGRADE_SHEET.subsurface(120, 200, 40, 40),
    'name': 'Discombobulate', 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},
"Concussion": {
    'Tier': 2, 'Cost': COST_LM, 'Owner': 'Duke', 'Condition': {'Require': ["Stun Strike"]}, 'Icon': UPGRADE_SHEET.subsurface(160, 200, 40, 40),
    'name': 'Concussion', 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},
"Infection": {
    'Tier': 2, 'Cost': COST_LM, 'Owner': 'Duke', 'Condition': {'Require': ["Poison Strike"]}, 'Icon': UPGRADE_SHEET.subsurface(200, 200, 40, 40),
    'name': 'Infection', 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},
"Neurotoxin": {
    'Tier': 2, 'Cost': COST_LM, 'Owner': 'Duke', 'Condition': {'Require': ["Poison Strike"]}, 'Icon': UPGRADE_SHEET.subsurface(240, 200, 40, 40),
    'name': 'Neurotoxin', 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},
"Piercing Strike": {
    'Tier': 3, 'Cost': COST_M, 'Owner': 'Duke',
    'Condition': {'Require': ["Discombobulate", "Concussion", "Infection", "Neurotoxin"]},  'Icon': UPGRADE_SHEET.subsurface(280, 200, 40, 40),
    'name': 'Piercing Strike', 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},
"Out of Sight Out of Mind": {
    'Tier': 3, 'Cost': COST_MH, 'Owner': 'Duke', 'Condition': {'Require': ["Shadow Walk"]},'Icon': UPGRADE_SHEET.subsurface(320, 200, 40, 40),
    'name': 'Out of Sight Out of Mind', 'effect': 'effect_out_of_sight_out_of_mind', 'trigger': 'trigger_not_targeted'},
"Tail & Blue Balls": {
    'Tier': 2, 'Cost': COST_LM, 'Owner': 'Duke', 'Icon': UPGRADE_SHEET.subsurface(360, 200, 40, 40),
    'name': 'Tail & Blue Balls', 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},

# Jester
"Surge Protection": {
    'Tier': 1, 'Cost': COST_LM, 'Owner': 'Jester', 'Icon': UPGRADE_SHEET.subsurface(0, 120, 40, 40),
    'name': 'Surge Protection', 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},
"Profanity Update": {
    'Tier': 1, 'Cost': COST_LM, 'Owner': 'Jester', 'Icon': UPGRADE_SHEET.subsurface(40, 120, 40, 40),
    'name': 'Profanity Update', 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},
"Super Kidnapping": {
    'Tier': 2, 'Cost': COST_L, 'Owner': 'Jester', 'Icon': UPGRADE_SHEET.subsurface(80, 120, 40, 40),
    'name': 'Super Kidnapping', 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},
"Power Boost": {
    'Tier': 2, 'Cost': COST_MH, 'Owner': 'Jester', 'Condition': {'Require': ['Profanity Update', 'Surge Protection']}, 'Icon': UPGRADE_SHEET.subsurface(120, 120, 40, 40),
    'name': 'Power Boost', 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},
"OUT OF MY WAY!": {
    'Tier': 2, 'Cost': COST_M, 'Owner': 'Jester', 'Condition': {'Require': ['Profanity Update', 'Surge Protection']}, 'Icon': UPGRADE_SHEET.subsurface(160, 120, 40, 40),
    'name': 'OUT OF MY WAY!', 'effect': 'effect_out_of_my_way', 'trigger': 'trigger_dash'},
"S41-Lor Firmware": {
    'Tier': 2, 'Cost': COST_M, 'Owner': 'Jester', 'Condition': {'Require': ['Profanity Update', 'Surge Protection']}, 'Icon': UPGRADE_SHEET.subsurface(200, 120, 40, 40),
    'name': 'S41-Lor Firmware', 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},
"Electronic Swearfare": {
    'Tier': 2, 'Cost': COST_LM, 'Owner': 'Jester', 'Condition': {'Require': ['Profanity Update', 'Surge Protection']}, 'Icon': UPGRADE_SHEET.subsurface(240, 120, 40, 40),
    'name': 'Electronic Swearfare', 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},
"Improved Hardware": {
    'Tier': 3, 'Cost': COST_MH, 'Owner': 'Jester', 'Condition': {'No': 'Improved Software', 'Require': ['Power Boost', 'OUT OF MY WAY!', 'S41-Lor Firmware', 'Electronic Swearfare']}, 'Icon': UPGRADE_SHEET.subsurface(280, 120, 40, 40),
    'name': 'Improved Hardware', 'effect': 'effect_improved_hardware', 'trigger': 'trigger_when_loaded'},
"Improved Software": {
    'Tier': 3, 'Cost': COST_MH, 'Owner': 'Jester', 'Condition': {'No': 'Improved Hardware', 'Require': ['Power Boost', 'OUT OF MY WAY!', 'S41-Lor Firmware', 'Electronic Swearfare']}, 'Icon': UPGRADE_SHEET.subsurface(320, 120, 40, 40),
    'name': 'Improved Software', 'effect': 'effect_improved_software', 'trigger': 'trigger_when_loaded'},
"Brittle Blue Balls": {
    'Tier': 2, 'Cost': COST_LM, 'Owner': 'Jester', 'Icon': UPGRADE_SHEET.subsurface(360, 120, 40, 40),
    'name': 'Brittle Blue Balls', 'effect': 'effect_brittle_blue_balls', 'trigger': 'trigger_on_hit'},

# Condor
"Ricochet": {
    'Tier': 1, 'Cost': COST_LM, 'Owner': 'Condor',
    'Icon': UPGRADE_SHEET.subsurface(0, 240, 40, 40),
    'name': 'Ricochet', 'effect': 'effect_ricochet', 'trigger': 'trigger_on_hit_effect'},
"Spread": {
    'Tier': 1, 'Cost': COST_LM, 'Owner': 'Condor', 'Icon': UPGRADE_SHEET.subsurface(40, 240, 40, 40),
    'name': 'Spread', 'effect': 'effect_spread', 'trigger': 'trigger_on_hit_effect'},
"Guardian": {
    'Tier': 1, 'Cost': COST_L, 'Owner': 'Condor', 'Icon': UPGRADE_SHEET.subsurface(80, 240, 40, 40),
    'name': 'Guardian', 'effect': 'effect_guardian', 'trigger': 'trigger_standing_still'},
"Pierce": {
    'Tier': 2, 'Cost': COST_M, 'Owner': 'Condor',
    'Condition': {'Require': ["Ricochet"]},  'Icon': UPGRADE_SHEET.subsurface(120, 240, 40, 40),
    'name': 'Pierce', 'effect': 'effect_pierce', 'trigger': 'trigger_when_loaded'},
"Intimidation": {
    'Tier': 2, 'Cost': COST_M, 'Owner': 'Condor',
    'Condition': {'Require': ["Ricochet", "Spread"]}, 'Icon': UPGRADE_SHEET.subsurface(160, 240, 40, 40),
    'name': 'Intimidation', 'effect': 'effect_intimidation', 'trigger': 'trigger_on_hit_effect'},
"Fear": {
    'Tier': 2, 'Cost': COST_M, 'Owner': 'Condor',
    'Condition': {'Require': ["Spread"]}, 'Icon': UPGRADE_SHEET.subsurface(200, 240, 40, 40),
    'name': 'Fear', 'effect': 'effect_fear', 'trigger': 'trigger_on_hit_effect'},
"Menace": {
    'Tier': 2, 'Cost': COST_MH, 'Owner': 'Condor',
    'Condition': {'Require': ["Spread"]}, 'Icon': UPGRADE_SHEET.subsurface(240, 240, 40, 40),
    'name': 'Menace', 'effect': 'effect_menace', 'trigger': 'trigger_none'},
"Bullying": {
    'Tier': 3, 'Cost': COST_H, 'Owner': 'Condor',
    'Condition': {'Require': ["Pierce", "Intimidation"]}, 'Icon': UPGRADE_SHEET.subsurface(280, 240, 40, 40),
    'name': 'Bullying', 'effect': 'effect_bullying', 'trigger': 'trigger_on_hit_effect'},
"Terror": {
    'Tier': 3, 'Cost': COST_MH, 'Owner': 'Condor',
    'Condition': {'Require': ["Intimidation", "Menace", "Fear"]}, 'Icon': UPGRADE_SHEET.subsurface(320, 240, 40, 40),
    'name': 'Terror', 'effect': 'effect_terror', 'trigger': 'trigger_targeted_return_enemies'},
"Unbreaking Blue Balls": {
    'Tier': 2, 'Cost': COST_LM, 'Owner': 'Condor', 'Icon': UPGRADE_SHEET.subsurface(360, 240, 40, 40),
    'name': 'Unbreaking Blue Balls', 'effect': 'effect_unbreaking_blue_balls', 'trigger': 'trigger_last_stand'},

# Curtis
"III, L'Impératrice": {
    'Tier': 1, 'Cost': 1000, 'Owner': 'Curtis', 'Icon': UPGRADE_SHEET.subsurface(0, 280, 40, 40),
    'name': f"III, L'Impératrice", 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},
"X, La Roue de Fortune": {
    'Tier': 1, 'Cost': 1000, 'Owner': 'Curtis', 'Icon': UPGRADE_SHEET.subsurface(40, 280, 40, 40),
    'name': 'X, La Roue de Fortune', 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},
"VII, Le Chariot": {
    'Tier': 1, 'Cost': COST_H, 'Owner': 'Curtis', 'Icon': UPGRADE_SHEET.subsurface(80, 280, 40, 40),
    'name': 'VII, Le Chariot', 'effect': 'effect_chariot', 'trigger': 'trigger_dash'},
"VI, L'Amoureux": {
    'Tier': 2, 'Cost': 1000, 'Owner': 'Curtis', 'Icon': UPGRADE_SHEET.subsurface(120, 280, 40, 40),
    'name': "VI, L'Amoureux", 'effect': 'effect_lovers', 'trigger': 'trigger_when_loaded'},
"VIII, La Justice": {
    'Tier': 2, 'Cost': 1000, 'Owner': 'Curtis', 'Icon': UPGRADE_SHEET.subsurface(160, 280, 40, 40),
    'name': 'VIII, La Justice', 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},
"XI, La Force": {
    'Tier': 2, 'Cost': 1000, 'Owner': 'Curtis', 'Icon': UPGRADE_SHEET.subsurface(200, 280, 40, 40),
    'name': 'XI, La Force', 'effect': 'effect_out_of_my_way', 'trigger': 'trigger_dash'},
"XIV, Tempérance": {
    'Tier': 2, 'Cost': 1000, 'Owner': 'Curtis', 'Icon': UPGRADE_SHEET.subsurface(240, 280, 40, 40),
    'name': 'XIV, Tempérance', 'effect': 'effect_temperance', 'trigger': 'trigger_on_hit_effect'},
"XIII, La Mort": {
    'Tier': 3, 'Cost': 1000, 'Owner': 'Curtis', 'Icon': UPGRADE_SHEET.subsurface(280, 280, 40, 40),
    'name': 'XIII, La Mort', 'effect': 'effect_death', 'trigger': 'trigger_on_hit_effect'},
"XII, Le Pendu": {
    'Tier': 3, 'Cost': 1000, 'Owner': 'Curtis', 'Icon': UPGRADE_SHEET.subsurface(320, 280, 40, 40),
    'name': 'XII, Le Pendu', 'effect': 'effect_hanged_man', 'trigger': 'trigger_low_health'},
"XX, Le Jugement": {
    'Tier': 3, 'Cost': 1000, 'Owner': 'Curtis', 'Condition': {'Require': ["XIII, La Mort", "XII, Le Pendu"]}, 'Icon': UPGRADE_SHEET.subsurface(360, 280, 40, 40),
    'name': 'XX, Le Jugement', 'effect': 'effect_give_blue_balls', 'trigger': 'trigger_when_loaded'},

# Lawrence
"Cremation": {
    'Tier': 1, 'Cost': 1000, 'Owner': 'Lawrence', 'Icon': UPGRADE_SHEET.subsurface(0, 320, 40, 40),
    'name': "Cremation", 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},
"Salamander": {
    'Tier': 1, 'Cost': 1000, 'Owner': 'Lawrence', 'Icon': UPGRADE_SHEET.subsurface(40, 320, 40, 40),
    'name': "Salamander", 'effect': 'effect_salamander', 'trigger': 'trigger_when_loaded'},
"Slow Burn": {
    'Tier': 2, 'Cost': 1000, 'Owner': 'Lawrence',
    'Condition': {'Require': ["Cremation"]}, 'Icon': UPGRADE_SHEET.subsurface(120, 320, 40, 40),
    'name': "Slow Burn", 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},
"Spontaneous Combustion": {
    'Tier': 2, 'Cost': 1000, 'Owner': 'Lawrence',
    'Condition': {'Require': ["Cremation"]}, 'Icon': UPGRADE_SHEET.subsurface(160, 320, 40, 40),
    'name': "Spontaneous Combustion", 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},
"Dragon's Breath": {
    'Tier': 2, 'Cost': 1000, 'Owner': 'Lawrence',
    'Condition': {'Require': ["Salamander"]}, 'Icon': UPGRADE_SHEET.subsurface(200, 320, 40, 40),
    'name': "Dragon's Breath", 'effect': 'effect_dragon_breath', 'trigger': 'trigger_dragon_breath'},
"Inferno": {
    'Tier': 3, 'Cost': 1000, 'Owner': 'Lawrence',
    'Condition': {'Require': ["Slow Burn", "Spontaneous Combustion", "Dragon's Breath"]}, 'Icon': UPGRADE_SHEET.subsurface(280, 320, 40, 40),
    'name': "Inferno", 'effect': 'effect_inferno', 'trigger': 'trigger_every_2_sec'},

"Carcass": {    # Projectiles now damage over time
    'Tier': 2, 'Cost': 1000, 'Owner': 'Lawrence',
    'Condition': {'No': 'Grapeshot'}, 'Icon': UPGRADE_SHEET.subsurface(240, 320, 40, 40),
    'name': "Carcass", 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},
"Grapeshot": {  # Increase spread, increase bullet count
    'Tier': 2, 'Cost': 1000, 'Owner': 'Lawrence',
    'Condition': {'No': 'Carcass'}, 'Icon': UPGRADE_SHEET.subsurface(80, 320, 40, 40),
    'name': "Grapeshot", 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},
"Hellfire": {   # Projectiles now inflict burn
    'Tier': 3, 'Cost': 1000, 'Owner': 'Lawrence',
    'Condition': {'Require': ["Carcass", "Grapeshot"]}, 'Icon': UPGRADE_SHEET.subsurface(320, 320, 40, 40),
    'name': "Hellfire", 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},
"Burning Blue Balls": {
    'Tier': 2, 'Cost': 1000, 'Owner': 'Lawrence', 'Icon': UPGRADE_SHEET.subsurface(360, 320, 40, 40),
    'name': "Burning Blue Balls", 'effect': 'effect_burning_blue_balls', 'trigger': 'trigger_on_hit_effect'},

# Mark
"Low Pressure Reloader": {
    'Tier': 1, 'Cost': 1000, 'Owner': 'Mark', 'Icon': UPGRADE_SHEET.subsurface(0, 360, 40, 40),
    'name': "Low Pressure Reloader", 'effect': 'effect_low_pressure_reloader', 'trigger': 'trigger_reloading'},
"Like a Shadow": {
    'Tier': 2, 'Cost': 1000, 'Owner': 'Mark', 'Icon': UPGRADE_SHEET.subsurface(120, 360, 40, 40),
    'name': "Like a Shadow", 'effect': 'effect_like_a_shadow', 'trigger': 'trigger_when_loaded'},
"Slow mark": {
    'Tier': 1, 'Cost': 1000, 'Owner': 'Mark', 'Icon': UPGRADE_SHEET.subsurface(40, 360, 40, 40),
    'name': "Slow mark", 'effect': 'effect_slow_mark', 'trigger': 'trigger_reloading'},
"Burning mark": {
    'Tier': 1, 'Cost': 1000, 'Owner': 'Mark', 'Icon': UPGRADE_SHEET.subsurface(80, 360, 40, 40),
    'name': "Burning mark", 'effect': 'effect_burning_mark', 'trigger': 'trigger_on_hit_effect'},
"Get Out": {
    'Tier': 2, 'Cost': 1000, 'Owner': 'Mark', 'Icon': UPGRADE_SHEET.subsurface(160, 360, 40, 40),
    'name': "Get Out", 'effect': 'effect_get_out', 'trigger': 'trigger_on_hit_effect'},
"Disable weapon mark": {
    'Tier': 2, 'Cost': 1000, 'Owner': 'Mark', 'Icon': UPGRADE_SHEET.subsurface(200, 360, 40, 40),
    'name': "Disable weapon mark", 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},
"Helping mark": {
    'Tier': 2, 'Cost': 1000, 'Owner': 'Mark', 'Icon': UPGRADE_SHEET.subsurface(240, 360, 40, 40),
    'name': "Helping mark", 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},
"Stun mark": {
    'Tier': 3, 'Cost': 1000, 'Owner': 'Mark', 'Icon': UPGRADE_SHEET.subsurface(320, 360, 40, 40),
    'name': "Stun mark", 'effect': 'effect_stun_mark', 'trigger': 'trigger_on_hit_effect'},
"And Stay Back": {
    'Tier': 3, 'Cost': 1000, 'Owner': 'Mark', 'Icon': UPGRADE_SHEET.subsurface(280, 360, 40, 40),
    'name': "And Stay Back", 'effect': 'effect_and_stay_back', 'trigger': 'trigger_on_hit_effect'},
"Marked Blue Balls": {
    'Tier': 2, 'Cost': 1000, 'Owner': 'Mark', 'Icon': UPGRADE_SHEET.subsurface(360, 360, 40, 40),
    'name': "Marked Blue Balls", 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},

# Vivianne
"Birna & Sardine": {
    'Tier': 1, 'Cost': 1000, 'Owner': 'Vivianne', 'Icon': UPGRADE_SHEET.subsurface(0, 400, 40, 40),
    'name': "Birna & Sardine", 'effect': 'effect_add_summon', 'trigger': 'trigger_when_loaded'},
"Elektra": {
    'Tier': 1, 'Cost': 1000, 'Owner': 'Vivianne', 'Icon': UPGRADE_SHEET.subsurface(40, 400, 40, 40),
    'name': "Elektra", 'effect': 'effect_add_summon', 'trigger': 'trigger_when_loaded'},
"Agatha": {
    'Tier': 1, 'Cost': 1000, 'Owner': 'Vivianne', 'Icon': UPGRADE_SHEET.subsurface(80, 400, 40, 40),
    'name': "Agatha", 'effect': 'effect_add_summon', 'trigger': 'trigger_when_loaded'},
"Azura": {
    'Tier': 2, 'Cost': 1000, 'Owner': 'Vivianne', 'Icon': UPGRADE_SHEET.subsurface(120, 400, 40, 40),
    'name': "Azura", 'effect': 'effect_add_summon', 'trigger': 'trigger_when_loaded'},
"M (Marisa)": {
    'Tier': 2, 'Cost': 1000, 'Owner': 'Vivianne', 'Icon': UPGRADE_SHEET.subsurface(160, 400, 40, 40),
    'name': "M (Marisa)", 'effect': 'effect_add_summon', 'trigger': 'trigger_when_loaded'},
"Sierra": {
    'Tier': 2, 'Cost': 1000, 'Owner': 'Vivianne', 'Icon': UPGRADE_SHEET.subsurface(200, 400, 40, 40),
    'name': "Sierra", 'effect': 'effect_add_summon', 'trigger': 'trigger_when_loaded'},
"Speed Dial": {
    'Tier': 2, 'Cost': 1000, 'Owner': 'Vivianne', 'Icon': UPGRADE_SHEET.subsurface(240, 400, 40, 40),
    'name': "Speed Dial", 'effect': 'effect_speed_dial', 'trigger': 'trigger_when_loaded'},
"Conference Call": {
    'Tier': 2, 'Cost': 1000, 'Owner': 'Vivianne', 'Icon': UPGRADE_SHEET.subsurface(280, 400, 40, 40),
    'name': "Conference Call", 'effect': 'effect_conference_call', 'trigger': 'trigger_when_loaded'},
"Makoto": {
    'Tier': 3, 'Cost': 1000, 'Owner': 'Vivianne', 'Icon': UPGRADE_SHEET.subsurface(320, 400, 40, 40),
    'name': "Makoto", 'effect': 'effect_add_summon', 'trigger': 'trigger_when_loaded'},
"Blue Ballin": {
    'Tier': 2, 'Cost': 1000, 'Owner': 'Vivianne', 'Icon': UPGRADE_SHEET.subsurface(360, 400, 40, 40),
    'name': "Blue Ballin", 'effect': 'effect_skill_activate', 'trigger': 'trigger_when_loaded'},
}


def update_available_upgrades(run_info):
    invalid_upgrades = []
    for upgrade in run_info["Upgrade pool"]:
        if "Condition" in UPGRADE_INFO[upgrade] and "Breaking Limits" not in run_info["Upgrades"]:
            condition = UPGRADE_INFO[upgrade]["Condition"]

            if "No" in condition:
                if type(condition["No"]) != list:
                    condition["No"] = [condition["No"]]

                for ass_cheeks in condition["No"]:
                    if ass_cheeks in run_info["Upgrades"]:
                        invalid_upgrades.append(upgrade)
                        break

            if "Require" in condition:
                allow = False
                for requirement in condition["Require"]:
                    if requirement in run_info["Upgrades"]:
                        allow = True
                        break
                if not allow:
                    continue
    num = 8
    num_invalids = len(invalid_upgrades)

    if len(run_info["Upgrade pool"]) - num_invalids < 8:
        num = len(run_info["Upgrade pool"]) - num_invalids
    while len(run_info["Available upgrades"]) < num:
        tested_upgrade = get_random_element_from_list(run_info["Upgrade pool"])
        # Might be able to fix the upgrade condition issue here
        if tested_upgrade not in run_info["Available upgrades"] and tested_upgrade not in invalid_upgrades:
            run_info["Available upgrades"].append(tested_upgrade)


def remove_available_upgrade(run_info, upgrade_to_remove):
    for count, useless in enumerate(run_info["Available upgrades"]):
        if useless == upgrade_to_remove:
            run_info["Available upgrades"].pop(count)
            break


def update_upgrade_pool(run_info, party_info):
    upgrade_record = {
        "Party": {"T1": 0, "T2": 0, "T3": 0},
        "Lord": {"T1": 0, "T2": 0, "T3": 0},
        "Emperor": {"T1": 0, "T2": 0, "T3": 0},
        "Wizard": {"T1": 0, "T2": 0, "T3": 0},
        "Sovereign": {"T1": 0, "T2": 0, "T3": 0},
        "Duke": {"T1": 0, "T2": 0, "T3": 0},
        "Jester": {"T1": 0, "T2": 0, "T3": 0},
        "Condor": {"T1": 0, "T2": 0, "T3": 0},

        "Curtis": {"T1": 0, "T2": 0, "T3": 0},
        "Lawrence": {"T1": 0, "T2": 0, "T3": 0},
        "Vivianne": {"T1": 0, "T2": 0, "T3": 0},
        "Mark": {"T1": 0, "T2": 0, "T3": 0},
        "APC": {"T1": 0, "T2": 0, "T3": 0},
    }
    new_upgrade_pool = []
    char_names = ["Party"]
    for e in party_info:
        char_names.append(e)
    for character in char_names:
        if character not in party_info and character != "Party":
            continue
        for tier in [1, 2, 3]:
            for upgrade in UPGRADE_INFO:
                if UPGRADE_INFO[upgrade]["Owner"] != character:
                    continue
                if UPGRADE_INFO[upgrade]["Tier"] != tier:
                    continue

                if upgrade in run_info["Upgrades"]:
                    upgrade_record[character][f"T{tier}"] += 1
                    continue
                if "Condition" in UPGRADE_INFO[upgrade] and "Breaking Limits" not in run_info["Upgrades"]:
                    condition = UPGRADE_INFO[upgrade]["Condition"]

                    if "No" in condition:
                        if type(condition["No"]) != list:
                            condition["No"] = [condition["No"]]

                        for ass_cheeks in condition["No"]:
                            if ass_cheeks in run_info["Upgrades"]:
                                remove_available_upgrade(run_info, upgrade)
                                break

                    if "Require" in condition:
                        allow = False
                        for requirement in condition["Require"]:
                            if requirement in run_info["Upgrades"]:
                                allow = True
                                break
                        if not allow:
                            continue
                if f"T{tier}" == "T1":
                    new_upgrade_pool.append(upgrade)
                if f"T{tier}" == "T2" and upgrade_record[character]["T1"] > 0:
                    new_upgrade_pool.append(upgrade)
                if f"T{tier}" == "T3" and upgrade_record[character]["T2"] > 0:
                    new_upgrade_pool.append(upgrade)
    return new_upgrade_pool


def shop_menu(WIN, CLOCK, party_info, run_info):
    # I despise writing UI code

    # Render stuff
    transition, frame_1 = menu_transition_start(WIN)

    # menu_sprite = pg.image.load(os.path.join("Sprites/UI/Settings Screen.png")).convert_alpha()
    menu_overlay = pg.image.load(os.path.join("Sprites/UI/Overlay.png")).convert_alpha()
    services_icon = UPGRADE_SHEET.subsurface((400-80, 800-40, 40, 40))
    exit_icon = UPGRADE_SHEET.subsurface((400-40, 800-40, 40, 40))

    options = []
    # Merchant is bad at it's job
    # Merchant drops products from the edge of space to the clients
    # Has loans to pay off for the spaceship
    for op in run_info["Available upgrades"]:
        options.append({"Name": op, "Value": op, "On select": "Return", "Render func": "Text only"}, )
    #
    options.append({"Name": "Other services", "Value": "Other services", "On select": "Return", "Render func": "Text only"})
    options.append({"Name": "Leave", "Value": "Quit", "On select": "Return", "Render func": "Text only"})
    menu_logic = UniversalMenuLogic(options, key_binds={"Select Up": "Left", "Select Down": "Right",
                                           "Select Left": "Up", "Select Right": "Down",
                                           "Confirm": "Interact", "Return": "Reload"})

    shopkeeper = "SKR"
    shopkeeper_animation_info = {"Current": "Blink", "Timer": 0, "Delay": 0}
    shopkeeper_sprite_sheet = get_image('Sprites/Shopkeeper animations.png')
    get_frames = lambda y : [shopkeeper_sprite_sheet.subsurface(x * 64, y * 64, 64, 64) for x in range(12)]
    shopkeeper_sprites = {
        "Blink": get_frames(0)
    }
    elements_to_show =[
        {"Sender": "SYS", "Message": str_to_list("")},
        {"Sender": shopkeeper, "Message": str_to_list("Whatcha need?")},
    ]
    w = 128
    comms_log = UICommunicationLog(elements_to_show, [32+w, 150], speed=0, offset=15)
    comms_log.font_func = create_temp_font_1

    other_services_txt_og = (f"Other services"
                             f"||"
                             f"||Full Heal||COST: 2750||Fully heal every party member who are not KO."
                             f"||"
                             f"||Change Weapons||COST: 500 per weapon switched||Switch out weapons for party members."
                             f"||"
                             f"||Reroll Upgrades||COST: 500||Change currently available upgrades.").split("||")
    other_services_lines = []
    for lines in other_services_txt_og:
        for txt_line in split_text(lines, limit=34):
            other_services_lines.append(txt_line)

    popup_pos = [28 + 36+200, 28 + 40]
    draw = True
    while True:
        # Select
        do_shit = menu_logic.act(WIN, CLOCK)
        if menu_logic.controller.input[menu_logic.key_binds["Select Left"]] and menu_logic.selected_option >=5:
            menu_logic.selected_option -= 5
            menu_logic.cooldown()
        if menu_logic.controller.input[menu_logic.key_binds["Select Right"]] and \
                menu_logic.selected_option < 5 < len(menu_logic.options):
            menu_logic.selected_option += 5
            menu_logic.cooldown()
            if menu_logic.selected_option > len(menu_logic.options) - 1:
                menu_logic.selected_option = len(menu_logic.options) - 1
        if do_shit:
            if do_shit == "Quit":
                break
            if do_shit == "Other services":
                shop_services = confirmation_popup(
                        WIN, CLOCK, [popup_pos[0]-200, popup_pos[1]],
                        [
                            {"Name": "Heal teammates", "Value": "Full Heal", "On select": "Return", "Render func": "Text only"},
                            {"Name": "Change weapons", "Value": "Change weapons", "On select": "Return", "Render func": "Text only"},
                            {"Name": "Reroll Upgrades", "Value": "Reroll Upgrades", "On select": "Return", "Render func": "Text only"},
                            {"Name": "Go Back", "Value": "AAAA", "On select": "Return", "Render func": "Text only"},
                        ],
                        text="Extra services"
                    )
                if shop_services == "Full Heal":
                    if run_info["Funds"] >= 2750:
                        confirm_you_want_to_buy = confirmation_popup(
                            WIN, CLOCK, popup_pos,
                            [
                                {"Name": "Yes", "Value": "Yes", "On select": "Return", "Render func": "Text only"},
                                {"Name": "No", "Value": "No", "On select": "Return", "Render func": "Text only"},
                            ],
                            text=f"Heal everybody for 2750?"
                        ) == "Yes"
                        if confirm_you_want_to_buy:
                            for p in party_info:
                                if party_info[p]["Health"] > 0:
                                    party_info[p]["Health"] = party_info[p]["Info"]["health"]

                                    comms_log.elements_to_show.append(
                                        {"Sender": "SYS",
                                         "Message": str_to_list(f"{p} healed ")}
                                    )
                            run_info["Funds"] -= 2750
                    else:
                        confirmation_popup(
                            WIN, CLOCK, popup_pos,
                            [
                                {"Name": "Okay", "Value": "No", "On select": "Return", "Render func": "Text only"},
                            ],
                            text="Not enough money."
                        )
                if shop_services == "Change weapons":
                    weapons_menu(WIN, CLOCK, party_info, run_info, from_shop=True)
                    transition, frame_1 = menu_transition_start(WIN)
                if shop_services == "Reroll Upgrades":
                    if run_info["Funds"] >= 500:
                        confirm_you_want_to_buy = confirmation_popup(
                            WIN, CLOCK, popup_pos,
                            [
                                {"Name": "Yes", "Value": "Yes", "On select": "Return", "Render func": "Text only"},
                                {"Name": "No", "Value": "No", "On select": "Return", "Render func": "Text only"},
                            ],
                            text=f"Heal everybody for 500?"
                        ) == "Yes"
                        if confirm_you_want_to_buy:
                            #
                            run_info["Available upgrades"] = []
                            update_available_upgrades(run_info)
                            options = []
                            for op in run_info["Available upgrades"]:
                                options.append(
                                    {"Name": op, "Value": op, "On select": "Return", "Render func": "Text only"}, )
                            options.append({"Name": "Other services", "Value": "Other services", "On select": "Return",
                                            "Render func": "Text only"})
                            options.append(
                                {"Name": "Leave", "Value": "Quit", "On select": "Return", "Render func": "Text only"})
                            menu_logic.options = options
                            run_info["Funds"] -= 500
                    else:
                        confirmation_popup(
                            WIN, CLOCK, popup_pos,
                            [
                                {"Name": "Okay", "Value": "No", "On select": "Return", "Render func": "Text only"},
                            ],
                            text="We don't make credit, come back richer."
                        )
            else:
                if run_info["Funds"] >= UPGRADE_INFO[do_shit]["Cost"]:
                    confirm_you_want_to_buy = confirmation_popup(
                        WIN, CLOCK, popup_pos,
                        [
                            {"Name": "Yes", "Value": "Yes", "On select": "Return", "Render func": "Text only"},
                            {"Name": "No", "Value": "No", "On select": "Return", "Render func": "Text only"},
                        ],
                        text=f"Buy {do_shit} for {UPGRADE_INFO[do_shit]["Cost"]}?"
                    ) == "Yes"
                    if confirm_you_want_to_buy:
                        # Update upgrade pool
                        run_info["Upgrades"].append(do_shit)
                        remove_available_upgrade(run_info, do_shit)
                        run_info["Upgrade pool"] = update_upgrade_pool(run_info, party_info)

                        # Update available upgrades
                        update_available_upgrades(run_info)
                        options = []
                        for op in run_info["Available upgrades"]:
                            options.append({"Name": op, "Value": op, "On select": "Return", "Render func": "Text only"}, )
                        options.append({"Name": "Other services", "Value": "Other services", "On select": "Return", "Render func": "Text only"})
                        options.append({"Name": "Leave", "Value": "Quit", "On select": "Return", "Render func": "Text only"})
                        menu_logic.options = options

                        # Remove funds
                        run_info["Funds"] -= UPGRADE_INFO[do_shit]["Cost"]

                        # Add transmissions to the comms log
                        sender =  UPGRADE_INFO[do_shit]["Owner"]
                        transmission = f"Shop-{sender}-Bought-{random.randint(1, 4)}"
                        if sender == "Party":
                            if run_info["Player party"] == "THR-1":
                                sender = get_random_element_from_list(["Lord", "Emperor", "Wizard", "Sovereign", "Duke", "Jester", "Condor"])
                            else:
                                sender = get_random_element_from_list(["Curtis", "Lawrence", "Mark", "Vivianne"])
                            transmission = f"Shop-{sender}-Party-Bought-{random.randint(1, 2)}"

                        comms_log.elements_to_show.append(
                            {"Sender": sender, "Message": str_to_list(write_textline(transmission))}
                        )
                        comms_log.elements_to_show.append(
                            {"Sender": shopkeeper, "Message": str_to_list(write_textline(f"{transmission}-Shopkeeper"))}
                        )
                else:
                    confirmation_popup(
                        WIN, CLOCK, popup_pos,
                        [
                            {"Name": "Okay", "Value": "No", "On select": "Return", "Render func": "Text only"},
                        ],
                        text="We don't make credit, come back richer."
                    )

                # reset upgrade pool
            menu_logic.cooldown()

        # |Draw|--------------------------------------------------------------------------------------------------------
        if draw:
            # width, height = WIN.get_size()
            width, height = 630, 450
            frame = pg.Surface((630, 450))
            surface_to_draw = frame
            WIN.fill(BLACK)
            temp_ui_font = create_temp_font_1(height)
            temp_ui_font_2 = create_temp_font_2(height)
            surface_to_draw.fill(UI_COLOUR_BACKGROUND)

            # Draw icons
            shop_display = pg.Surface((376, 258))
            pg.draw.rect(shop_display, UI_COLOUR_BACKDROP, [0, 0, 376-12, 258-12], width=4)
            for count, p in enumerate(menu_logic.options):
                offset = [
                    [0, 0], [64, 0], [128, 0], [196, 0], [256, 0],
                    [0, 96], [64, 96], [128, 96], [196, 96], [256, 96]
                ]
                colour = UI_COLOUR_BACKDROP
                if count == menu_logic.selected_option:
                    colour = UI_COLOUR_NEW_BACKDROP
                pg.draw.rect(shop_display, colour, [28 + offset[count][0], 28 + offset[count][1], 48, 48], width=3)
                # Add sprite
                if p["Value"] in UPGRADE_INFO:
                    if "Icon" in UPGRADE_INFO[p["Value"]]:
                        shop_display.blit(UPGRADE_INFO[p["Value"]]["Icon"], (32 + offset[count][0], 32 + offset[count][1]))

                    shop_display.blit(temp_ui_font_2.render(f"{UPGRADE_INFO[p['Value']]['Owner']}", True, AMBER),
                                      (32 + offset[count][0] - 4, 32 + offset[count][1] + 44))

                elif p["Value"] == "Other services":
                    shop_display.blit(services_icon, (32 + offset[count][0], 32 + offset[count][1]))
                    shop_display.blit(temp_ui_font_2.render(f"Services", True, AMBER),
                                      (32 + offset[count][0] - 4, 32 + offset[count][1] + 44))
                else:
                    shop_display.blit(exit_icon, (32 + offset[count][0], 32 + offset[count][1]))
                    shop_display.blit(temp_ui_font_2.render(f"Exit shop", True, AMBER),
                                      (32 + offset[count][0] - 4, 32 + offset[count][1] + 44))

            # Option details display
            details_display = pg.Surface((254-12, 258-12))
            pg.draw.rect(details_display, UI_COLOUR_BACKDROP, (0, 0, 254-12, 258-12), width=4)
            info_zero = [8, 8]
            details_display.blit(temp_ui_font.render(f"PARTY FUNDS: {run_info['Funds']}", True, AMBER), (info_zero[0], info_zero[1]))

            try:
                current_option = menu_logic.options[menu_logic.selected_option]
            except IndexError:
                current_option = menu_logic.options[len(menu_logic.options)-1]

            if current_option["Value"] not in ["Other services", "Quit"]:
                details_display.blit(temp_ui_font.render(f"NAME: {current_option['Value']}", True, AMBER), (info_zero[0], info_zero[1]+14+8))
                details_display.blit(temp_ui_font.render(f"COST: {UPGRADE_INFO[current_option['Value']]['Cost']}", True, AMBER), (info_zero[0], info_zero[1]+28+8))
                details_display.blit(temp_ui_font.render(f"USER: {UPGRADE_INFO[current_option['Value']]['Owner']}", True, AMBER), (info_zero[0], info_zero[1]+42+8))
                # Writes description
                for count, text in enumerate(split_text(write_textline(f'Upgrade-Desc-{current_option['Value']}', send_back=True), limit=28)):
                    details_display.blit(temp_ui_font.render(text, True, AMBER), (info_zero[0], info_zero[1] + 76 + 14 * count))

                # Writes any upgrades that is not compatible  with
                if "Breaking Limits" not in run_info["Upgrades"]:
                    upgrade = UPGRADE_INFO[current_option["Value"]]
                    #                     details_display.blit(temp_ui_font.render(text, True, AMBER), (info_zero[0], info_zero[1] + 76 + 14 * count))
                    if "Condition" in upgrade:
                        if "No" in upgrade["Condition"]:
                            if type(upgrade["Condition"]["No"]) != list:
                                upgrade["Condition"]["No"] = [upgrade["Condition"]["No"]]
                            count += 2
                            details_display.blit(temp_ui_font.render("Cannot be used with:", True, AMBER),
                                                 (info_zero[0], info_zero[1] + 76 + 14 * count + 14))

                            for ass_cheeks in upgrade["Condition"]["No"]:
                                count += 1
                                details_display.blit(temp_ui_font.render(f"- {ass_cheeks}", True, AMBER),
                                                     (info_zero[0], info_zero[1] + 76 + 14 * count + 14))



            elif current_option["Value"] == "Other services":
                # details_display.blit(temp_ui_font.render(f"{current_option['Value']}", True, AMBER), (info_zero[0], info_zero[1]+14+8))
                # details_display.blit(temp_ui_font.render(f"COST: {2750}", True, AMBER), (info_zero[0], info_zero[1]+28+8))

                # for count, text in enumerate(split_text("Fully heals party members who are not KO", limit=28)):
                for count, text in enumerate(other_services_lines):
                    details_display.blit(temp_ui_font.render(text, True, AMBER), (info_zero[0], info_zero[1] + 14 + 14 * count))
                    # details_display.blit(temp_ui_font.render(text, True, AMBER), (info_zero[0], info_zero[1] + 58 + 14 * count))

            else:
                details_display.blit(temp_ui_font.render(f"{current_option['Value']}", True, AMBER), (info_zero[0], info_zero[1]+22))

            # Comms
            comms_display = pg.Surface((630-24, 192-12))
            pg.draw.rect(comms_display, UI_COLOUR_BACKDROP, (0, 0, 630-24, 192-12), width=4)
            comms_log.act()
            comms_log.draw(comms_display)

            if shopkeeper_animation_info["Delay"] == 0:
                shopkeeper_animation_info["Timer"] += 1
            else:
                shopkeeper_animation_info["Delay"] -= 1
                if shopkeeper_animation_info["Delay"] == 0:
                    shopkeeper_animation_info["Timer"] += 1
            frame_num = shopkeeper_animation_info["Timer"] // 6 % 12
            frame_to_draw = shopkeeper_sprites[shopkeeper_animation_info["Current"]][frame_num]
            if shopkeeper_animation_info["Delay"] == 0 and frame_num == 11:
                shopkeeper_animation_info["Delay"] = random.randint(5, 30)
            comms_display.blit(pg.transform.scale(frame_to_draw, (w, w)), (16, 16))
            pg.draw.rect(comms_display, UI_COLOUR_NEW_BACKDROP, (12, 12, w + 8, w + 8), width=4)

            crt(shop_display)
            surface_to_draw.blit(shop_display, (12, 12))
            crt(details_display)
            surface_to_draw.blit(details_display, (376, 12))
            crt(comms_display)
            surface_to_draw.blit(comms_display, (12, 258))

            surface_to_draw.blit(menu_overlay, [0, 0])
            scale_render(WIN, surface_to_draw, CLOCK)
            transition = menu_transition_handler(WIN, CLOCK, frame_1, transition)
            pg.display.update()
        CLOCK.tick(60)

    return run_info


def end_menu(WIN, CLOCK, status_line, elements_to_show, comment_line, elements_to_show_2=[{"Sender": "", "Message": str_to_list("")}]):
    if CURRENT_TRACK_INFO[1] != "Menu":
        stop_music()
    menu_overlay = pg.image.load(os.path.join("Sprites/UI/Overlay.png")).convert_alpha()
    key_pressed = DEFAULT_KEY_PRESSED * 4

    frame_1 = some_bullshit_for_transitions(WIN)
    transition = True
    win_copy = WIN.copy()
    controller = PseudoPlayer()

    status = UICommunicationLog(status_line, [-30, 60], speed=5, font_func=create_temp_font_3)
    menu_render = UICommunicationLog(elements_to_show, [15, 300], speed=1)
    menu_render_2 = UICommunicationLog(elements_to_show_2, [280, 280], speed=1)
    comments = UICommunicationLog(comment_line, [15, 330], speed=3, font_func=create_temp_font_1, text_offset=100)
    end_timer_start_value = 60*30
    end_timer = end_timer_start_value
    # Give it something other than text to show
    bonuses_window = False
    bonuses_window_width = 3
    bonuses_window_height = 0
    while end_timer > 0:
        frame = pg.Surface((630, 450))
        surface_to_draw = frame
        WIN.fill(BLACK)
        surface_to_draw.fill(UI_COLOUR_BACKGROUND)
        if bonuses_window:
            if bonuses_window != 200:
                bonuses_window += 1
            if bonuses_window < 100:
                bonuses_window_width += 3
            if 200 > bonuses_window > 100 and bonuses_window_height < len(elements_to_show_2)*20:
                bonuses_window_height += 4

            pg.draw.rect(surface_to_draw, AMBER_LIGHT, (275, 274-bonuses_window_height, bonuses_window_width, bonuses_window_height), width=2)

        if menu_render.transmission_list and not bonuses_window and elements_to_show_2:
            bonuses_window = 1
        for count, ass in enumerate([status, menu_render, menu_render_2, comments]):
            if count > 0 and status.elements_to_show:  # make the mission/contract status render first
                continue
            if count == 2 and bonuses_window != 200: # make the window render first
                continue
            if count == 3 and menu_render.elements_to_show: # make comment render last
                continue

            ass.act()
            ass.draw(surface_to_draw)

        # Let the player skip
        keys = pg.key.get_pressed()
        needed_in_menu_and_game(WIN, keys)
        controller.get_input(keys)
        no_input = True
        for i in controller.input:
            if controller.input[i]:
                no_input = False
                break
        if key_pressed == 0:
            if not no_input:
                break
        elif no_input:
            key_pressed -= 1
        pg.draw.rect(surface_to_draw, AMBER_LIGHT, (12, 450-40, 606 * (end_timer / end_timer_start_value), 4))
        crt(surface_to_draw)
        surface_to_draw.blit(menu_overlay, [0, 0])
        scale_render(WIN, surface_to_draw, CLOCK)

        if transition:
            transition = False
            menu_transition_doom_screen_melt(WIN, CLOCK, WIN, win_copy)
            play_music("Menu")
        pg.display.update()
        CLOCK.tick(60)
        end_timer -= 1


def end_mission_menu(WIN, CLOCK, party_info, status, run_info, level, extra_info, deployed_team, surviving_deployed_team, entities, time_spent):
    b = "Secretary" # use a bird name, she is part of the Nest but
    if "Curtis" in party_info:
        b = "Big_Scaly_6"

    p1 = {
        "Win": "COMPLETED",
        "Loss": "FAILED"
    }[status]
    elements_to_show =[
        {"Sender": "SYS", "Message": str_to_list(f"PARTY STATUS")},
    ]
    for x in party_info:
        p_diddy = party_info[x]
        message = f"HEALTH STATUS {p_diddy['Health']} / {p_diddy['Info']['health']}"
        if p_diddy['Health'] == 0:
            message = p_diddy['Death message']
        elements_to_show.append(
            {"Sender": f"{p_diddy['Name']}", "Message": str_to_list(message)}
        )
    # elements_to_show.append(
    #     {"Sender": "SYS", "Message": str_to_list(f"FTLT '{b}' to 'THR-1'")},
    # )
    extra_message = {
            "Big_Scaly_6": {
                "Win": "Good job, you're getting closer to the anomaly!",
                "Loss": "Sad but we can't win all the time..."}[status],
            "Secretary": {
                "Win": "Objective completed, funds are transferred.",
                "Loss": "I expected better of you. Get lost."
            }[status]
        }[b]

    end_mission_bonuses = []
    if status != "Loss":
        # Bonus
        mod = 0

        # No lost team member
        if len(deployed_team) == len(surviving_deployed_team) and len(deployed_team) > 1:
            end_mission_bonuses.append(
                {"Sender": "SYS", "Message": str_to_list(f"Bonus Reward - No casualties, x 0.1")},
            )
            mod += 0.1

        # No spent ammo
        no_spent_ammo = 0
        for x in surviving_deployed_team:
            for y in entities["entities"]:
                if y.name == x and y.team == "Players":
                    if y.weapon.ammo + y.weapon.ammo_pool == y.weapon.max_ammo_pool + y.weapon.max_ammo:
                        no_spent_ammo += 1
                    break
        if no_spent_ammo > 0:
            end_mission_bonuses.append(
                {"Sender": "SYS", "Message": str_to_list(f"Bonus Reward - Unused ammo, x {no_spent_ammo * 0.1}")},
            )
            mod += no_spent_ammo * 0.1

        # Time
        escort_time_to_beat = 0
        if extra_info["Type"] == "Escort":
            escort_time_to_beat = len(level['free var']['APC path']) * 2
        time_to_beat = {
            "Defeat Elite Unit": 90,
            "Capture":  40 * (round(extra_info["Current mission"]*0.30) + 1) + 30,
            "Seek and Destroy": round(len(extra_info["Enemy spawns"]) * 7.5),
            "Eliminate Commander": 40 * (round(extra_info["Current mission"]*0.30) + 1) + 30,
            "Defense": [2, 2, 3, 3, 0,
                          4, 4, 5, 5, 0,
                          6, 6, 7, 7, 0][extra_info["Current mission"]-1]*50,
            "Escort": escort_time_to_beat
        }[extra_info["Type"]] * 60

        if time_spent < time_to_beat:
            end_mission_bonuses.append(
                {"Sender": "SYS", "Message": str_to_list(f"Bonus Reward - Quick completion, x 0.3")},
            )
            mod += 0.3

        # Solo
        if len(deployed_team) == 1:
            end_mission_bonuses.append(
                {"Sender": "SYS", "Message": str_to_list(f"Bonus Reward - Solo deployment, x 0.2")},
            )
            mod += 0.1

        # Enemies wiped out
        if extra_info["Type"] not in ["Seek and Destroy", "Defense", "Defeat Elite Unit"]:
            allow_bonus = True
            for e in entities["entities"]:
                if e.team != "Players":
                    allow_bonus = False
                    break
            if allow_bonus:
                end_mission_bonuses.append(
                    {"Sender": "SYS", "Message": str_to_list(f"Bonus Reward - Hostiles wiped out, x 0.3")},
                )
                mod += 0.3

        # Give total modifier
        if mod > 0:
            end_mission_bonuses.append(
                {"Sender": "SYS", "Message": str_to_list(f"Total bonus modifier, x {mod}")},
            )
        run_info["Funds"] += extra_info["Mission Reward"] * mod
        run_info["Funds"] = round(run_info["Funds"])
        end_mission_bonuses.append(
            {"Sender": "SYS", "Message": str_to_list(f"Payout, {extra_info['Mission Reward']} + {extra_info['Mission Reward'] * mod} bonus")},
        )

    end_menu(WIN, CLOCK, [{"Sender": " ", "Message": str_to_list(f"MISSION STATUS: {p1}")}], elements_to_show,
             [{"Sender": f"{b}", "Message": str_to_list(f"{extra_message}")}], end_mission_bonuses)
    # popups here when you unlock shit


def end_run_menu(WIN, CLOCK, run_info, party_info, status):
    # temp_ui_font =  create_temp_font_2(450, font_name="Sprites/JetBrainsMono-SemiBold.ttf")

    b = "Secretary" # use a bird name, she is part of the Nest but
    if "Curtis" in party_info:
        b = "Big_Scaly_6"
    p1 = {'Win': 'COMPLETED', 'Loss': 'FAILED'}[status]
    if status == "Loss":
        run_info['Funds'] = 0
    alive_count = 0
    for x in party_info:
        if party_info[x]['Health'] > 0:
            alive_count += 1
    elements_to_show =[

        {"Sender": "SYS", "Message": str_to_list(f"HEALTHY MEMBERS   : {alive_count}/{len(party_info)}")},
        {"Sender": "SYS", "Message": str_to_list(f"MISSION COMPLETED : {run_info['Missions completed']}")},
        {"Sender": "SYS", "Message": str_to_list(f"TOTAL EARNINGS    : {run_info['Funds']}")},
        {"Sender": "SYS", "Message": str_to_list(f"UPGRADES BOUGHT   : {len(run_info['Upgrades'])}")},
]

    end_menu(WIN, CLOCK, [{"Sender": " ", "Message": str_to_list(f"CONTRACT STATUS: {p1}")}], elements_to_show, [        {"Sender": f"{b}", "Message": str_to_list(

        {
            "Big_Scaly_6": {
                "Win": "Great, you're all done! Let's celebrate at the bar!",
                "Loss": "Sad but we can't win all the time..."}[status],
            "Secretary": {
                "Win": "Contract completed. Delivering reward.",
                "Loss": "I expected better, get lost."
            }[status]
        }[b]
    )}])


# ???
def check_for_repeat_in_list(list_to_check, index_to_check, check_for_repeat):
    for repeat in list_to_check:
        if repeat[index_to_check] == check_for_repeat:
            return True
    return False


def loading_screen(WIN, CLOCK):
    # This is not really a loading screen, it's just there so the game doesn't look stupid while generating levels
    transition, frame_1 = menu_transition_start(WIN)

    surface_to_draw = pg.Surface((630, 450))
    WIN.fill(BLACK)
    surface_to_draw.fill(UI_COLOUR_BACKGROUND)
    surface_to_draw.blit(get_image('Sprites/UI/Loading Screen.png'), [0, 0])
    font = create_temp_font_1(450, font_name="Sprites/JetBrainsMono-SemiBold.ttf")
    surface_to_draw.blit(font.render(write_textline("Loading screen"), True, AMBER), (25, 375))

    scale_render(WIN, surface_to_draw, CLOCK)
    menu_transition_handler(WIN, CLOCK, frame_1, transition)
    pg.display.update()


# |Menu effects|--------------------------------------------------------------------------------------------------------
def some_bullshit_for_transitions(screen):
    surface_copy = screen.copy()
    width, height = screen.get_size()
    slide_width, slide_height = FRAME_MAX_SIZE  # 1.4

    # Get the smallest of the 2 dimensions
    if width != slide_width or height != slide_height:
        if width > height * 1.4:
            slide_width = slide_width * height / slide_height
            slide_height = height
        elif width < height:
            slide_height = slide_height * width / slide_width
            slide_width = width
        if width < height * 1.4:
            slide_width = slide_width * height / slide_height
            slide_height = height
        elif width > height:
            slide_height = slide_height * width / slide_width
            slide_width = width

    # This was added to handle the render zoom
    if slide_width > width or slide_height > height:
        if width > height * 1.4:
            slide_width = slide_width * height / slide_height
            slide_height = height
        elif width < height * 1.4:
            slide_height = slide_height * width / slide_width
            slide_width = width

    # Draw the stuff
    #  (width // 2 - slide_width // 2, height // 2 - slide_height // 2)
    x = width // 2 - slide_width // 2
    y = height // 2 - slide_height // 2
    surface_copy = surface_copy.subsurface(x, y, slide_width, slide_height)
    return pg.transform.scale(surface_copy, (630, 450))
    #


def menu_transition_doom_screen_melt(WIN, CLOCK, frame_1, frame_2):
    # colour = DARKER_GREEN
    colour = UI_COLOUR_BACKGROUND
    width, height = WIN.get_size()
    slide_width, slide_height = FRAME_MAX_SIZE  # 1.4

    frame_1 = some_bullshit_for_transitions(frame_1)    # Background
    frame_2 = some_bullshit_for_transitions(frame_2)

    slices = []
    slice_height = frame_2.get_height()
    divider = 7
    for new_slice in range(630 // divider):
        slices.append([frame_2.subsurface(divider * new_slice, 0, divider, slice_height), random.randint(-8, 0)])

    timer = 0
    # max_time = slice_height + 8
    max_time = 60
    while timer < max_time:
        timer += 1
        needed_in_menu_and_game(WIN, pg.key.get_pressed())

        # |Draw|--------------------------------------------------------------------------------------------------------
        WIN.fill(BLACK)
        frame = pg.Surface((630, 450))
        surface_to_draw = frame

        surface_to_draw.blit(frame_1, (0, 0))
        for count, slice_to_draw in enumerate(slices):
            slice_to_draw[1] += 1
            t = 0
            if slice_to_draw[1] > 0:
                t = slice_to_draw[1] * 9
            surface_to_draw.blit(slice_to_draw[0], (divider * count, t))

        # is_everything_down = True
        # for slice_to_draw in slices:
        #     if slice_to_draw[1] * 9 < 450:
         #        is_everything_down = False
        #         break

        # if is_everything_down:
        #     break

        scale_render(WIN, surface_to_draw, CLOCK)
        pg.display.update()
        CLOCK.tick(60)
    #


menu_transition_start = lambda s : (True, some_bullshit_for_transitions(s))


def menu_transition_handler(WIN, CLOCK, win_copy, transition):
    if transition:
        transition = False
        menu_transition_doom_screen_melt(WIN, CLOCK, WIN, win_copy)
    # transition, frame_1 = True, some_bullshit_for_transitions(WIN)
    # transition = menu_transition_handler(WIN, CLOCK, frame_1, transition)
    return transition


def crt(WIN):
    # img = pg.transform.laplacian(WIN.copy())
    img = WIN.copy()
    img.set_alpha(64*random.random())
    WIN.blit(img, (random.uniform(-3, 3), 0))
    width = WIN.get_width()
    for y in range(WIN.get_height()//2):
        draw_transparent_rect(WIN, (0, y*2+random.random(), width, 2), GRAY, 8*random.random())


# |Blit/draw functions|-------------------------------------------------------------------------------------------------
def scrolling_manager(scrolling, scrolling_target, WIN_WIDTH, WIN_HEIGHT, scrolling_speed=3.75):
    if not scrolling_speed:
        return scrolling
    # I am satisfied with the scrolling right now
    dist = distance_between(scrolling_target, scrolling) / 50
    scrolling_speed *= dist

    if scrolling[0] < scrolling_target[0]:
        scrolling[0] += scrolling_speed
    elif scrolling[0] > scrolling_target[0]:
        scrolling[0] -= scrolling_speed
    if scrolling[1] < scrolling_target[1]:
        scrolling[1] += scrolling_speed
    elif scrolling[1] > scrolling_target[1]:
        scrolling[1] -= scrolling_speed

    # Corrects the scrolling if close enough, this keep it smooth
    for x in range(2):
        if scrolling_target[x] - scrolling_speed < scrolling[x] < scrolling_target[x] + scrolling_speed:
            scrolling[x] = scrolling_target[x]
    return scrolling


def blitRotate(surf, image, pos, originPos, angle):
    # This is used to draw weapons
    # offset from pivot to center
    image_rect = image.get_rect(topleft=(pos[0] - originPos[0], pos[1] - originPos[1]))
    offset_center_to_pivot = pg.math.Vector2(pos) - image_rect.center

    # roatated offset from pivot to center
    rotated_offset = offset_center_to_pivot.rotate(-angle)

    # rotated image center
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)

    # get a rotated image
    rotated_image = pg.transform.rotate(image, angle)
    rotated_image_rect = rotated_image.get_rect(center=rotated_image_center)

    # rotate and blit the image
    surf.blit(rotated_image, rotated_image_rect)


def blitRotate2(surf, image, topleft, angle):
    # not sure if I use this
    rotated_image = pg.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft=topleft).center)

    surf.blit(rotated_image, new_rect.topleft)
    # pg.draw.rect(surf, (255, 0, 0), new_rect, 2)


def draw_environment_from_tile_set(WIN, top_left_corner, width, height, rounded_scrolling, mode,
                                   tile_set=TILE_SET_INDUSTRIAL_FLOOR, modified_index=(1, 2, 3, 4, 0, 5, 6, 7, 8)):
    # This function uses a tile set to render a rectangular area
    # It was first made to draw buildings
    if mode == "UI":
        return

    internal_width = round((width - TILES_SIZE * 2) // TILES_SIZE)

    if mode in ("Foreground", "All"):

        # Draw the top layer
        # Draw the left corner
        WIN.blit(tile_set[modified_index[0]],
                 [top_left_corner[0] + rounded_scrolling[0],
                  top_left_corner[1] + rounded_scrolling[1]])
        # Draw the middle
        for x in range(internal_width):
            WIN.blit(tile_set[modified_index[1]],
                     [top_left_corner[0] + TILES_SIZE + (x * TILES_SIZE) + rounded_scrolling[0],
                      top_left_corner[1] + rounded_scrolling[1]])
        # Draw the right corner
        WIN.blit(tile_set[modified_index[2]],
                 [top_left_corner[0] + width - TILES_SIZE + rounded_scrolling[0],
                  top_left_corner[1] + rounded_scrolling[1]])

        # Draw the middle layers
        for y in range(round((height - TILES_SIZE * 2) // TILES_SIZE)):
            # Draw the left side
            WIN.blit(tile_set[modified_index[3]],
                     [top_left_corner[0] + rounded_scrolling[0],
                      top_left_corner[1] + TILES_SIZE + (y * TILES_SIZE) + rounded_scrolling[1]])
            # Draw the middle
            for x in range(internal_width):
                WIN.blit(tile_set[modified_index[4]],
                         [top_left_corner[0] + TILES_SIZE + (x * TILES_SIZE) + rounded_scrolling[0],
                          top_left_corner[1] + TILES_SIZE + (y * TILES_SIZE) + rounded_scrolling[1]])
            # Draw the right side
            WIN.blit(tile_set[modified_index[5]],
                     [top_left_corner[0] + width - TILES_SIZE + rounded_scrolling[0],
                      top_left_corner[1] + TILES_SIZE + (y * TILES_SIZE) + rounded_scrolling[1]])

    if mode in ("Background", "All"):
        # Draws the bottom layer
        for x in range(internal_width):
            WIN.blit(tile_set[modified_index[7]],
                     [top_left_corner[0] + TILES_SIZE + (x * TILES_SIZE) + rounded_scrolling[0],
                      top_left_corner[1] + height - TILES_SIZE + rounded_scrolling[1]])
        # Draw the sides
        WIN.blit(tile_set[modified_index[6]],
                 [top_left_corner[0] + rounded_scrolling[0],
                  top_left_corner[1] + height - TILES_SIZE + rounded_scrolling[1]])
        WIN.blit(tile_set[modified_index[8]],
                 [top_left_corner[0] + width - TILES_SIZE + rounded_scrolling[0],
                  top_left_corner[1] + height - TILES_SIZE + rounded_scrolling[1]])


def draw_transparent_rect(WIN, rect, colour, alpha_level):
    s = pg.Surface((rect[2], rect[3]))  # the size of your rect
    s.set_alpha(alpha_level)  # alpha level
    s.fill(colour)
    WIN.blit(s, (rect[0], rect[1]))


def draw_transparent_circle(WIN, circle, colour, alpha_level, width=0):
    # the variable circle used to be called "rect" which is retarted
    s = pg.Surface((circle[2], circle[2])).convert_alpha()  # the diameter of the circle
    circle_radius = circle[2] / 2  # Radius of the circle
    s.fill([0, 0, 0, 0])
    pg.draw.circle(s,
                   (colour[0], colour[1], colour[2]),
                   [circle_radius, circle_radius],
                   circle_radius, width=width)
    s.set_alpha(alpha_level)  # alpha level
    WIN.blit(s, (circle[0], circle[1]))


def draw_arc(WIN, colour, pos, base_angle, length, half_of_angle_width, width=100000):
    angle_1 = radians(base_angle * -1 - half_of_angle_width + 180)  # rad
    angle_2 = radians(base_angle * -1 + half_of_angle_width + 180)
    half_range = length / 2
    arc_rect = (pos[0] - half_range, pos[1] - half_range, length, length)
    pg.draw.arc(WIN, colour, arc_rect, angle_1, angle_2, width)


def draw_transparent_arc(WIN, colour, pos, base_angle, length, half_of_angle_width, alpha_level, width=100000):
    angle_1 = radians(base_angle * -1 - half_of_angle_width + 180)  # rad
    angle_2 = radians(base_angle * -1 + half_of_angle_width + 180)
    half_range = length / 2
    arc_rect = (0, 0, length, length)
    # arc_rect = (pos[0] - half_range, pos[1] - half_range, length, length)

    s = pg.Surface((length, length)).convert_alpha()  # the diameter of the circle
    s.fill([0, 0, 0, 0])
    pg.draw.arc(s, colour, arc_rect, angle_1, angle_2, width)

    s.set_alpha(alpha_level)  # alpha level
    WIN.blit(s, (pos[0] - half_range, pos[1] - half_range))


def draw_transparent_poly(WIN, points, colour, alpha_level, scrolling, width=0):
    first_point = points[0]
    points_x, points_y = [], []
    for p in points:
        points_x.append(p[0])
        points_y.append(p[1])
    width, height = (max(points_x) - min(points_x)), (max(points_y) - min(points_y))
    # width, height = 512, 512
    # Add scrolling beforehand
    # the variable circle used to be called "rect" which is retarted
    s = pg.Surface((width, height)).convert_alpha()  # the diameter of the circle
    s.fill([0, 0, 0, 0])
    # pg.draw.polygon(s, (colour[0], colour[1], colour[2]), points, width=width)
    points = [[int(p[0])-min(points_x), int(p[1])-min(points_y)] for p in points]
    # pg.draw.polygon(s, colour, [[int(p[0])-min(points_x), int(p[1])-min(points_y)] for p in points])
    pg.draw.polygon(s, colour, points)

    s.set_alpha(alpha_level)  # alpha level

    # WIN.blit(s, (points[0][0] + scrolling[0], points[0][1] + scrolling[1]))
    WIN.blit(s, (min(points_x) + scrolling[0], min(points_y) + scrolling[1]))


def draw_sprite(WIN, sprite, pos, scrolling):
    WIN.blit(sprite, [pos[0] + scrolling[0], pos[1] + scrolling[1]])


def write_text_multi_colours(WIN, pos, font_type, text_list):
    # Use this to write stuff of different colours on the same line
    # text_lists = [["str", colour], ...]
    x_mod = 0
    for text in text_list:
        stuff_to_write = FONTS[font_type].render(text[0], True, text[1])
        WIN.blit(stuff_to_write, [pos[0] + x_mod, pos[1]])
        x_mod += stuff_to_write.get_width()


def write_control(player, input_to_check, is_move=False, fucking_hell=True):
    gamepads = ALL_CONTROLLERS[0]
    # Check if there's any controllers
    if player.input_mode == "Controller":
        if is_move:
            return f"[{player.controller_control['Move']}]"
        elif fucking_hell:
            valid_inputs = player.controller_control[input_to_check]
            string_to_return = valid_inputs
            if type(player.controller_control[input_to_check]) == list:
                string_to_return = ""
                valid_inputs_len = len(valid_inputs)
                for count, temp_string in enumerate(valid_inputs):
                    string_to_return += temp_string
                    if count < valid_inputs_len - 1:
                        string_to_return += ", "
            return f"[{string_to_return}]"
    else:
        if input_to_check in SYSTEM_CONTROLS:
            return f"[{pg.key.name(SYSTEM_CONTROLS[input_to_check]).capitalize()}]"
        elif input_to_check in player.mouse_control:
            text = ["Left mouse", "Middle mouse", "Right mouse", "Mouse 4", "Mouse 5"
                    ][player.mouse_control[input_to_check]]
            return f"[{text}]"
        elif input_to_check == "Aim":
            return "[Mouse]"
        # player.control
        return f"[{pg.key.name(player.control[input_to_check]).capitalize()}]"
    return ""


def get_entity_direction(angle):
    return int(5 - (angle + 180) // (360 / 6))


def draw_weapon_on_back(WIN, self, weapon_angle, weapon_x_mod, weapon_y_mod, weapon_angle_mod, scrolling):
    # Still a bit weird, but way better than what it used to be
    sprite = self.weapons[1 - self.switch_weapon].sprite
    sprite_width = sprite.get_width() // 2
    sprite_height = sprite.get_height() // 2
    origin = [sprite_width, sprite_height]

    blitRotate(WIN, pg.transform.flip(sprite, True, -90 < weapon_angle < 90),
               [self.pos[0] + weapon_x_mod + scrolling[0], self.pos[1] - sprite_height + weapon_y_mod + scrolling[1]],
               origin, -90 + weapon_angle_mod)


def draw_entity(self, scrolling, WIN, entity_direction):
    frame_to_get = 0
    action_type = "Walk"
    allow_change = False
    if not self.standing_still:
        if self.sliding:
            allow_change = True
            action_type = "Sliding"
        elif self.running:
            allow_change = True
            # action_type = "Dash"
        elif self.walking:
            allow_change = True

    # Make the counters go up
    for counter in self.animation_counter:
        if action_type == counter:
            self.animation_counter[counter] += 1
        else:
            self.animation_counter[counter] = 0
    # Sliding need a special case to handle its animation
    if allow_change:
        frame_to_get = self.animation_counter[action_type] // 7 % (
                len(self.sprites[entity_direction][action_type]) - 1) + 1

    # Draws the player
    sprite_drawn = self.sprites[entity_direction][action_type][frame_to_get]
    WIN.blit(sprite_drawn, (self.pos[0] - 16 + scrolling[0], self.pos[1] - 16 + scrolling[1]))


# Add a cache
# @functools.lru_cache(typed=True)
def draw_spritestack(WIN, sprites, pos, angle, height_diff=0.5):
    for i, sprite in enumerate(sprites):
        rotated_sprite = pg.transform.rotate(sprite, -angle)
        WIN.blit(rotated_sprite, (pos[0] - rotated_sprite.get_width() // 2, pos[1] - rotated_sprite.get_height() // 2 - height_diff * i))
    return pos[0] + rotated_sprite.get_width() // 2, pos[1] + rotated_sprite.get_height() // 2 - height_diff * i


def write_text(WIN, font, text, colour, pos, scrolling):
    WIN.blit(FONTS[font].render(text, True, colour), [pos[0] + scrolling[0], pos[1] + scrolling[1]])


def split_text(text, limit=20):
    text_list = []
    splinted_text = text.split(" ")
    while splinted_text:
        new_string = ""
        while splinted_text:
            if len(new_string) - 1 + len(splinted_text[0]) > limit and new_string != "":
                break
            new_string += f" {splinted_text[0]}"
            splinted_text.pop(0)
        new_string = ''.join(new_string.split(' ', 1))
        text_list.append(new_string)

    return text_list


def scale_render(WIN, surface_to_draw, CLOCK):
    # Scale the slide
    # surface_to_draw = pg.transform.laplacian(surface_to_draw)
    width, height = WIN.get_size()
    slide_width, slide_height = FRAME_MAX_SIZE  # 1.4

    # Get the smallest of the 2 dimensions
    if width != slide_width or height != slide_height:
        if width > height * 1.4:
            slide_width = slide_width * height / slide_height
            slide_height = height
        elif width < height:
            slide_height = slide_height * width / slide_width
            slide_width = width
        if width < height * 1.4:
            slide_width = slide_width * height / slide_height
            slide_height = height
        elif width > height:
            slide_height = slide_height * width / slide_width
            slide_width = width

    # This was added to handle the render zoom
    if slide_width > width or slide_height > height:
        if width > height * 1.4:
            slide_width = slide_width * height / slide_height
            slide_height = height
        elif width < height * 1.4:
            slide_height = slide_height * width / slide_width
            slide_width = width

    # Draw the stuff
    surface_to_draw = pg.transform.scale(surface_to_draw, (slide_width, slide_height))
    WIN.blit(surface_to_draw, (width // 2 - slide_width // 2, height // 2 - slide_height // 2))
    WIN.blit(FONTS["sma"].render(f"FPS {round(CLOCK.get_fps())}", True, UI_COLOUR_FONT),
             (width * 0.925, height * 0.95))
    # WIN.blit(surface_to_draw, (0, 0))


def find_scrolling_target(scrolling_target_entities):
    if not scrolling_target_entities:
        return [0, 0]
    length = len(scrolling_target_entities)
    width = FRAME_MAX_SIZE[0] / 2
    height = FRAME_MAX_SIZE[1] / 2
    if length == 1:
        en_titties = scrolling_target_entities[0]
        return [-en_titties.pos[0] + FRAME_MAX_SIZE[0] / 2, -en_titties.pos[1] + FRAME_MAX_SIZE[1] / 2]
    # Goes up to 4
    x, y = [], []
    for titties in scrolling_target_entities:
        x.append(titties.pos[0])
        y.append(titties.pos[1])
    mid = [(sum(x)) / length * -1 + width, (sum(y)) / length * -1 + height]

    avg = []
    titty = scrolling_target_entities[0]
    for titties in scrolling_target_entities:
        avg.append(distance_between(titty.pos, titties.pos))
    # num = numpy.average(avg)
    # update_render_zoom(0.925)
    num = numpy.average(avg) * 0.005
    if num < 0.9:
        num = 0.9
    if num > 1.41:
        num = 1.41
    update_render_zoom(num)
    return mid


# |Stuff between 2 points|----------------------------------------------------------------------------------------------
def angle_between(target_point, origin_point):
    return math.degrees(math.atan2(origin_point[1] - target_point[1], origin_point[0] - target_point[0]))


def distance_between(p1, p2):
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])


def midpoint_between(p1, p2):
    return [(p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2]


def num_between(p1, p2):
    if p1 < p2:
        return p2 - p1
    return p1 - p2


# |Math related functions|----------------------------------------------------------------------------------------------
def random_point_in_circle(center, radius):
    # Get a random angle and radius
    alpha = 2 * math.pi * random.random()
    r = radius * math.sqrt(random.random())
    # Calculate coordinates

    return [r * math.cos(alpha) + center[0], r * math.sin(alpha) + center[1]]


def random_point_in_cone(center, radius, angle, deviation):
    return move_with_vel_angle(center, radius * random.random(), random.uniform(angle - deviation, angle + deviation))


def random_point_in_donut(center, distances):
    # Get a random angle
    angle = random.uniform(-180, 180)
    distance = random.uniform(distances[0], distances[1])
    # return [center[0] - distance * math.cos(angle * math.pi / 180),
    #         center[1] - distance * math.sin(angle * math.pi / 180)]
    return move_with_vel_angle(center, distance, angle)


def get_number_of_thing_in_a_damn_circle(entities, target_type, radius, center_x, center_y):
    things_in_the_damn_circle = 0
    for things in entities[target_type]:
        if check_point_in_circle(radius, center_x, center_y, things.pos[0], things.pos[1]):
            things_in_the_damn_circle += 1
    return things_in_the_damn_circle


def move_with_vel_angle(base_pos, vel, angle):
    # I could switch math.pi to 3
    angle = angle * math.pi / 180
    return [base_pos[0] - vel * math.cos(angle), base_pos[1] - vel * math.sin(angle)]


# |Check if x is in y|--------------------------------------------------------------------------------------------------
def dot_prod_with_shared_start(start, end1, end2):
    # Return True if the directed angle from (end1 - start) to (end2 - start) is within (0, pi / 4).
    return (end1[0] - start[0]) * (end2[0] - start[0]) + (end1[1] - start[1]) * (end2[1] - start[1])


def check_point_in_rotated_rectangle(vertices, point):
    # Returns True if the point is inside the rectangle. False otherwise.
    # v0, v1, v2, v3 = vertices
    return all(dot_prod_with_shared_start(vertices[i - 1], v, point) > 0 for i, v in enumerate(vertices))


def check_point_in_circle(radius, center_x, center_y, x, y):
    return distance_between([x, y], [center_x, center_y]) < radius


def check_point_in_circle_new(radius, center, point):
    return distance_between(point, center) < radius


def check_point_in_donut(radius, center_x, center_y, x, y):
    return radius[0] < distance_between([x, y], [center_x, center_y]) < radius[1]


def check_point_in_cone(radius, center_x, center_y, x, y, direction, angle):
    radius = int(radius)
    angle_to_check = angle_between([x, y], [center_x, center_y])
    if math.sqrt((center_x - x) ** 2 + (center_y - y) ** 2) < radius ^ 2:
        smaller_angle = direction - angle
        bigger_angle = direction + angle
        # if the direction the AI is looking at is near -180/180
        if 180 - angle < direction or direction < -180 + angle:
            if 180 - angle < angle_to_check or angle_to_check < -180 + angle:
                return True

        if smaller_angle < angle_to_check < bigger_angle:
            return True
    return False


def check_point_in_donut_cone(radius, radius_small, center_x, center_y, x, y, direction, angle):
    radius = int(radius)
    angle_to_check = angle_between([x, y], [center_x, center_y])
    if check_point_in_donut([radius_small, radius], center_x, center_y, x, y):
    # if math.sqrt((center_x - x) ** 2 + (center_y - y) ** 2) < radius ^ 2:
        smaller_angle = direction - angle
        bigger_angle = direction + angle
        # if the direction the AI is looking at is near -180/180
        if 180 - angle < direction or direction < -180 + angle:
            if 180 - angle < angle_to_check or angle_to_check < -180 + angle:
                return True

        if smaller_angle < angle_to_check < bigger_angle:
            return True
    return False


def check_angle_between_range(angle, t_angle):
    smaller_angle = angle - 30
    bigger_angle = angle + 30
    # if the direction the AI is looking at is near -180/180
    if 180 - 30 < t_angle or t_angle < -180 + 30:
        if 180 - 30 < t_angle or t_angle < -180 + 30:
            return True

    if smaller_angle < t_angle < bigger_angle:
        return True


def collision_rect_circle(left, top, width, height, center_x, center_y, radius):
    rect_x, rect_y = left + width / 2, top + height / 2
    dist_x, dist_y = abs(center_x - rect_x), abs(center_y - rect_y)

    if dist_x > (width / 2 + radius) or dist_y > (height / 2 + radius):
        return False

    if dist_x <= width / 2 or dist_y <= height / 2:
        return True

    return (dist_x - width / 2) + (dist_y - height / 2) <= (radius ** 2)


def collision_circle_circle(pos_1, radius_1, pos_2, radius_2):
    return distance_between(pos_1, pos_2) <= radius_1 + radius_2


def collision_rect_laser(rect, laser_pos, laser_angle, laser_length):
    return rect.clipline(laser_pos, move_with_vel_angle(laser_pos, laser_length, laser_angle))


def find_triangle_area(p_1, p_2, p_3):
    a, b, c = distance_between(p_1, p_2), distance_between(p_2, p_3), distance_between(p_3, p_1)
    # a, b, c = 5, 6, 7
    # Given: A = 5, B = 6, C = 7 	Start with the given side lengths of the triangle.
    # s = (5 + 6 + 7) ÷ 2 	Calculate the semi-perimeter.
    s = (a + b + c) / 2
    # s = 9 	The semi-perimeter is 9.
    return math.sqrt(s * (s - a) * (s - b) * (s - c))


def collision_circle_laser(circle_center, line_start, line_end, radius):
    # coding math shit drunk thanks to https://areacalculators.com/area-of-irregular-shapes-calculator/ and
    # https://www.baeldung.com/cs/circle-line-segment-collision-detection
    return (2 * find_triangle_area(circle_center, line_start, line_end)) / distance_between(line_start, line_end) <= radius


def find_closest_in_circle(self, entities, targeting_range, target_type):
    # was probably the single most copied and pasted code in this game until it became a function
    dist = targeting_range
    target = False
    for e in entities[target_type]:
        if self.team == e.team: continue
        if check_point_in_circle(dist, self.pos[0], self.pos[1], e.pos[0], e.pos[1]):
            dist = round(math.hypot(e.pos[0] - self.pos[0], e.pos[1] - self.pos[1]))
            target = [e.pos[0], e.pos[1]]
    return target


def find_closest_bullet_type_in_circle(self, bullets, targeting_range, target_type, bullet_type):
    # was probably the single most copied and pasted code in this game until it became a function
    dist = targeting_range
    target = False
    for e in bullets[target_type]:
        if type(e) == bullet_type:
            if check_point_in_circle(dist, self.pos[0], self.pos[1], e.pos[0], e.pos[1]):
                dist = round(math.hypot(e.pos[0] - self.pos[0], e.pos[1] - self.pos[1]))
                target = e
    return target


def find_closest_bullet_types_in_circle(self, entities, targeting_range, bullet_types):
    # was probably the single most copied and pasted code in this game until it became a function
    dist = targeting_range
    target = False
    for e in entities["bullets"]:
        if type(e) not in bullet_types or e.team == self.team:
            continue
        if check_point_in_circle(dist+e.radius, self.pos[0], self.pos[1], e.pos[0], e.pos[1]):
            target = e
            break
    return target


def find_closest_in_donut(self, entities, targeting_range, target_type):
    dist = targeting_range[1]
    target = False
    for e in entities[target_type]:
        if check_point_in_donut([targeting_range[0], dist], self.pos[0], self.pos[1], e.pos[0], e.pos[1]):
            dist = round(math.hypot(e.pos[0] - self.pos[0], e.pos[1] - self.pos[1]))
            target = [e.pos[0], e.pos[1]]
    return target


def find_closest_in_circle_just_enemies_no_boss(self, entities, targeting_range, send_entity=False):
    dist = targeting_range
    target = False
    for e in entities["entities"]:
        if self.team == e.team:
            continue
        if not e.is_boss:
            if check_point_in_circle(dist, self.pos[0], self.pos[1], e.pos[0], e.pos[1]):
                dist = round(math.hypot(e.pos[0] - self.pos[0], e.pos[1] - self.pos[1]))
                target = [e.pos[0], e.pos[1]]
                if send_entity:
                    target = e
    return target


def get_stretcher_target(self, entities, targeting_range):
    dist = targeting_range
    target = False
    for e in entities["entities"]:
        if e.name in ["Lord", "Emperor", "Wizard", "Sovereign", "Duke", "Jester", "Condor"]:
            continue
        if not e.is_boss:
            if check_point_in_circle(dist, self.pos[0], self.pos[1], e.pos[0], e.pos[1]):
                dist = round(math.hypot(e.pos[0] - self.pos[0], e.pos[1] - self.pos[1]))
                target = e
    return target


def get_stretcher_target_super_kidnapping(self, entities, targeting_range):
    dist = targeting_range
    target = False
    for e in entities["entities"]:
        if e.namea in ["Lord", "Emperor", "Wizard", "Sovereign", "Duke", "Jester", "Condor"]:
            continue
        if check_point_in_circle(dist, self.pos[0], self.pos[1], e.pos[0], e.pos[1]):
            dist = round(math.hypot(e.pos[0] - self.pos[0], e.pos[1] - self.pos[1]))
            target = e
    return target


def find_closest_in_circle_check_name(self, entities, targeting_range, name, send_entity=False):
    dist = targeting_range
    target = False
    for e in entities["enemies"]:
        if e.name != name:
            continue

        if e.pos == self.pos:
            continue

        if check_point_in_circle(dist, self.pos[0], self.pos[1], e.pos[0], e.pos[1]):
            dist = round(math.hypot(e.pos[0] - self.pos[0], e.pos[1] - self.pos[1]))
            target = [e.pos[0], e.pos[1]]
            if send_entity:
                target = e
    return target


def find_closest_in_circle_mouse(self, entities, targeting_range, target_type):
    # This version should only be used by the player
    dist = targeting_range
    target = False
    for e in entities[target_type]:
        if check_point_in_circle(dist, self.mouse_pos[0], self.mouse_pos[1], e.pos[0], e.pos[1]):
            dist = round(math.hypot(e.pos[0] - self.mouse_pos[0], e.pos[1] - self.mouse_pos[1]))
            target = [e.pos[0], e.pos[1]]
    return target


def find_closest_in_cone(self, entities, targeting_range, target_type, angle, targeting_angle):
    dist = targeting_range
    target = False
    for e in entities["entities"]:
        if e.team == self.team:
            continue
        if check_point_in_cone(dist, self.pos[0], self.pos[1], e.pos[0], e.pos[1], angle, targeting_angle):
            # check_point_in_circle(dist, self.pos[0], self.pos[1], e.pos[0], e.pos[1]):
            dist = round(math.hypot(e.pos[0] - self.pos[0], e.pos[1] - self.pos[1]))
            target = e.pos.copy()
    return target


# |Game stuff|----------------------------------------------------------------------------------------------------------
def keyboard_mouse_input(self, keys, mouse_key):
    for input_check in KEYBOARD_BOND_INPUT:
        self.input[input_check] = keys[self.control[input_check]]

    # Check for input from the mouse
    if not mouse_key:
        return
    for input_check in MOUSE_BOND_INPUT:
        self.input[input_check] = mouse_key[self.mouse_control[input_check]]


def get_keys_from_controller(gamepads, gamepad_index=0):
    gamepads[gamepad_index].init()
    gamepad = gamepads[gamepad_index]
    buttons, axes, dpads = gamepad.get_numbuttons(), gamepad.get_numaxes(), gamepad.get_numhats()

    # This gets the inputs from the controller
    button_a, button_b, button_x, button_y = False, False, False, False
    button_l, button_r, button_start, button_select = False, False, False, False
    threshold_stick, threshold_trigger = 0.2, 0.2
    trigger_l, trigger_r = 0, 0
    stick_l, stick_l_pressed, stick_r, stick_r_pressed = [0, 0], False, [0, 0], False
    d_pad = []

    for event in pg.event.get():
        # This somehow make the whole thing work
        if event.type == pg.JOYBUTTONDOWN:
            pass
        elif event.type == pg.JOYBUTTONUP:
            pass
        elif event.type == pg.JOYAXISMOTION:
            pass
        elif event.type == pg.JOYHATMOTION:
            pass

    # get gamepad inputs
    for i in range(buttons):
        if gamepad.get_button(i):
            if i == 0:
                button_a = True
            elif i == 1:
                button_b = True
            elif i == 2:
                button_x = True
            elif i == 3:
                button_y = True
            elif i == 4:
                button_l = True
            elif i == 5:
                button_r = True
            elif i == 6:
                button_select = True
            elif i == 7:
                button_start = True
            elif i == 8:
                stick_l_pressed = True
            elif i == 9:
                stick_r_pressed = True

    # get axes values
    for i in range(axes):
        axis = gamepad.get_axis(i)
        if i == 0 and (abs(gamepad.get_axis(0)) > threshold_stick or abs(gamepad.get_axis(1)) > threshold_stick):
            stick_l[0] = axis
        elif i == 1 and (abs(gamepad.get_axis(0)) > threshold_stick or abs(gamepad.get_axis(1)) > threshold_stick):
            stick_l[1] = axis
        elif i == 2 and (abs(gamepad.get_axis(2)) > threshold_stick or abs(gamepad.get_axis(3)) > threshold_stick):
            stick_r[0] = axis
        elif i == 3 and (abs(gamepad.get_axis(2)) > threshold_stick or abs(gamepad.get_axis(3)) > threshold_stick):
            stick_r[1] = axis
        elif i == 4 and axis > threshold_trigger:
            trigger_l = axis
        elif i == 5 and axis > threshold_trigger:
            trigger_r = axis

    # get dpad values
    for i in range(dpads):
        d_pad = gamepad.get_hat(i)

    return {
        # Buttons
        "Button Left": button_x, "Button Top": button_y, "Button Bottom": button_a, "Button Right": button_b,
        "Button Select": button_select, "Button Start": button_start,
        # Shoulder trigger
        "Shoulder Left": button_l, "Shoulder Right": button_r, "Trigger Left": trigger_l, "Trigger Right": trigger_r,
        # Stick
        "Stick Left": stick_l, "Stick Right": stick_r,
        "Stick Left Press": stick_l_pressed, "Stick Right Press": stick_r_pressed,
        # D-pad
        "D-pad Up": d_pad[1] > 0, "D-pad Left": d_pad[0] < 0, "D-pad Right": d_pad[0] > 0, "D-pad Down": d_pad[1] < 0
    }


def controller_input(self, in_menu=False, gamepad_index=0):
    for event in pg.event.get():
        # This somehow make the whole thing work
        if event.type == pg.JOYBUTTONDOWN:
            pass
        elif event.type == pg.JOYBUTTONUP:
            pass
        elif event.type == pg.JOYAXISMOTION:
            pass
        elif event.type == pg.JOYHATMOTION:
            pass
    gamepads = ALL_CONTROLLERS[0]
    threshold_stick, threshold_trigger = 0.2, 0.2
    # Check if there's any controllers
    if not len(gamepads) > 0:
        return False
    try:
        gamepads[gamepad_index].init()
    except IndexError:
        print_to_error_stream("Mission controller")

    # This should be moved in self.control and Key binds.json
    inputs_binds = self.controller_control

    # This handles potential errors caused by removing or plug in the controller
    try:
        input_translation = get_keys_from_controller(gamepads, gamepad_index=gamepad_index)
    except IndexError:
        input_translation = {
            # Buttons
            "Button Left": False, "Button Top": False, "Button Bottom": False, "Button Right": False,
            "Button Select": False, "Button Start": False,
            # Shoulder trigger
            "Shoulder Left": False, "Shoulder Right": False, "Trigger Left": False, "Trigger Right": False,
            # Stick
            "Stick Left": [0, 0], "Stick Right": [0, 0],
            "Stick Left Press": False, "Stick Right Press": False,
            # D-pad
            "D-pad Up": False, "D-pad Left": False, "D-pad Right": False, "D-pad Down": False
        }

    movement_stick, aim_stick = input_translation[inputs_binds["Move"]], input_translation[inputs_binds["Aim"]]

    # This transfer the inputs to the player
    # Handles stick input
    self.input["Left"] = movement_stick[0] < -threshold_stick or self.input["Left"]
    self.input["Right"] = movement_stick[0] > threshold_stick or self.input["Right"]
    self.input["Up"] = movement_stick[1] < -threshold_stick or self.input["Up"]
    self.input["Down"] = movement_stick[1] > threshold_stick or self.input["Down"]

    # Handle the rest of the inputs
    # for input_type in inputs_binds:
    for input_type in self.input:
        # Skip inputs that are sticks
        if input_type in ["Move", "Aim"]:
            continue
        # Handle all the different input types
        if input_type in ["Pause", "Screenshot"]:
            for bind in inputs_binds[input_type]:
                SYSTEM_CONTROLS_INPUT[input_type] = bool(input_translation[bind])
            continue
        for bind in inputs_binds[input_type]:
            self.input[input_type] = bool(input_translation[bind]) or self.input[input_type]
            # print(f"{input_type} - {bind} - {self.input[input_type]}")

    if in_menu:
        for i in self.input:
            if self.input[i]:
                return True
        return False

    # Find a way to somehow make it only move when it's moved
    if abs(aim_stick[0]) > threshold_stick or abs(aim_stick[1]) > threshold_stick:
        self.controller_angle = angle_between(aim_stick, [0, 0])
        # self.mouse_pos = move_with_vel_angle(self.pos, 10, self.direction_angle)
    self.mouse_pos = move_with_vel_angle(self.pos, 96, self.controller_angle)
    self.angle = angle_between(self.mouse_pos, self.pos)

    return True


def system_input_handler(keys):
    # Might use this to handle the pause and screenshot
    SYSTEM_CONTROLS_INPUT["Screenshot"] = keys[SYSTEM_CONTROLS["Screenshot"]]
    SYSTEM_CONTROLS_INPUT["Pause"] = keys[SYSTEM_CONTROLS["Pause"]]


def damage_calculation(self, damage_received, damage_type, ignore_no_damage=False, no_iframes=False, no_sound=True, ignore_armour=False, ignore_res=False, death_message="Defeated by unknown cause"):
    if self.status["No damage"] == 0 or ignore_no_damage:
        if not ignore_res: # Might be possible to optimize
            res_mod = 1
            if self.status["High res"] != 0:
                res_mod = 0.5
            elif self.status["Low res"] != 0:
                res_mod = 2
            damage_received = round(damage_received * self.resistances[damage_type] * res_mod)
        if damage_received < 0:
            self.health -= damage_received
            if self.health > self.max_health:
                self.health = self.max_health
            # This never happens
            return 0

        self.status["No damage"] = 8 * (1 - no_iframes)  # Gives everyone invincibility frames
        if self.armour > 0 and not ignore_armour:
            self.armour -= damage_received

            if self.armour <= 0:
                damage_received = self.armour * -1 // 2
                self.armour = 0
                self.armour_break = True
            else:
                damage_received = 0

        true_damage = damage_received
        self.health -= true_damage
        self.damage_taken = True
        if self.health <= 0:
            self.health = 0
            self.free_var.update({"Death message": death_message})
        if no_sound:
            return true_damage

        sound = {"Physical": "Bullet hit 1",
                 "Fire": "Bullet hit 2",
                 "Explosion": "Bullet hit 1",
                 "Energy": "Bullet hit 3",
                 "Melee": "Bullet hit 4"}[damage_type]

        # if self.name == "Curtis":
        if self.is_player:
            sound = "Curtis Hit"
        play_sound(sound, "SFX")
        return true_damage


def aim_system(self, current_weapon):
    if self.status["Stunned"]:
        return

    # Value Limiter
    self.aim_angle = angle_value_limiter(move_angle(self.angle, self.aim_angle, current_weapon.handle))


def move_angle_toward_target_angle(real_angle, target_angle, rate):
    invert_aim = 1
    if not -(180 - rate) + target_angle < real_angle < 180 - rate + target_angle:
        invert_aim = -1

    # Adjust angle
    if real_angle < target_angle:
        real_angle += rate * invert_aim
        if real_angle > target_angle:
            real_angle = target_angle
    elif real_angle > target_angle:
        real_angle += -rate * invert_aim
        if real_angle < target_angle:
            real_angle = target_angle

    return angle_value_limiter(real_angle)


def move_angle(real_angle, current_angle, rate):
    invert_aim = 1
    if not -(180 - rate) + real_angle < current_angle < 180 - rate + real_angle:
        invert_aim = -1

    # Adjust angle
    if current_angle < real_angle:
        current_angle += rate * invert_aim
        if current_angle > real_angle:
            current_angle = real_angle
    elif current_angle > real_angle:
        current_angle += -rate * invert_aim
        if current_angle < real_angle:
            current_angle = real_angle
    return current_angle


def angle_value_limiter(real_angle):
    # Value Limiter
    if real_angle > 180:
        real_angle = -180 + (real_angle - 180)
    if real_angle < -180:
        real_angle = 180 - (real_angle + 180)
    return real_angle


# |Wall colisions and level geometry|-----------------------------------------------------------------------------------
def wall_between(p1, p2, level):
    # Check the points
    for wall in level["map"]:
        if wall.clipline(p1, p2):
            return True
    return False


def collision_check(self, walls):   # New version
    future_rect = self.collision_box.copy()
    future_rect.move(self.vel[0], self.vel[1])
    thick = self.thiccness // 2 + 1

    # Does the collisions
    for wall in walls:
        if future_rect.colliderect(wall):
            top_left = wall.collidepoint(future_rect.topleft)
            top_right = wall.collidepoint(future_rect.topright)
            bottom_left = wall.collidepoint(future_rect.bottomleft)
            bottom_right = wall.collidepoint(future_rect.bottomright)

            top_side = top_left and top_right
            bottom_side = bottom_left and bottom_right
            right_side = bottom_right and top_right
            left_side = bottom_left and top_left

            all_side = top_side and bottom_side and right_side and left_side

            if all_side:
                self.vel[0] *= -1
                self.vel[1] *= -1
            else:
                if top_side and not bottom_side:
                    self.pos[1] = wall.bottom + thick
                if bottom_side and not top_side:
                    self.pos[1] = wall.top - thick

                if right_side and not left_side:
                    self.pos[0] = wall.left - thick
                if left_side and not right_side:
                    self.pos[0] = wall.right + thick

            self.collision_box = pg.Rect(self.pos[0] - self.thiccness / 2, self.pos[1] - self.thiccness / 2,
                                         self.thiccness, self.thiccness)
            future_rect = self.collision_box.copy()
            future_rect.move(self.vel[0], self.vel[1])
    #


def collision_check_no_physics(collision_box, walls):
    for wall in walls:
        if collision_box.colliderect(wall):
            return True
    return False


# |Entities shared functions|-------------------------------------------------------------------------------------------
# If players, enemies and bosses do the same thing in the code, I'll put the code here to make changes easier
STATUS_EFFECT_ZERO = {
    # Buff
    "No damage": 0,  # Cannot take damage in this state
    "High res": 0,  # Cannot take damage in this state
    "Low res": 0,  # Cannot take damage in this state
    "Healing": 0,  # Give health overtime
    "No Jam": 0,  # Weapons won't jam
    "Perfect Aim": 0,  # Act as if the weapon has an accuracy of zero
    "No Recoil": 0,  # Act as if the weapon has a recoil of zero
    "Crit boost": 0,  # Double crit chance
    "Bullet x3": 0,  # Shoot more bullets
    "Bullet damage up": 0,  # All bullets shot do more damage
    "Bullet speed up": 0,  # All bullets shot are faster
    "Bullet duration up": 0,  # All bullets shot last longer
    "Bullet radius up": 0,  # All bullets shot are bigger
    "Fuller auto": 0,  # Firing rate is equal to 0
    "Less auto": 0,  # Firing rate is doubled
    "Stealth": 0,  # Enemies have a lower targeting range
    "Visible": 0,
    "Dash recovery up": 0,
    "No debuff": 0,
    # Situational
    "Low friction": 0,  # Friction is lowered
    # Debuff
    "Burning": 0,  # Damage over time
    "Damage Over time": 0,  # Damage over time
    "Stunned": 0,  # Can't do shit
    "High Jam": 0,  # Double jam chances
    "No crit": 0,  # Cannot do crit
    "Low Aim": 0,  # Act as if the weapon had double accuracy and spread
    "Bullet speed down": 0,  # All bullets shot are slower
    "Bullet duration down": 0,  # All bullets shot have less duration
    "Bullet radius down": 0,  # All bullets shot are smaller
    "High friction": 0,  # Slow movement
    # Stuff that's barely used
    "Forced Slide": 0,
    "Double speed": 0,
    "Slowness": 0,
    # The least used status effect, it's just a cooldown for Vivianne
    "Dash": 0,
    "Last Stand": 0
}
BUFFS_NAMES = [
"High res",
    "Perfect Aim",
    "No Recoil",
    "Crit boost",
    "Bullet x3",
    "Bullet duration up",
    "Bullet radius up",
    "Stealth",
    "Dash recovery up"
]
DEBUFFS_NAMES = [
    "Burning", "Damage Over time", "Stunned", "High Jam", "No crit", "Low Aim", "Bullet speed down",
    "Bullet duration down", "Bullet radius down", "High friction", "Slowness", "Low res", "Visible", "Less auto"
]
# Use that to keep colour effects related to status effect consistant
STATUS_EFFECT_COLOUR = {
    "No damage": (229, 229, 2),
    "High res": (229, 229, 2),
    "Low res": (255 - 229, 255 - 229, 255 - 2),
    "Healing": (0, 255, 0),
    "No Jam": (0, 255, 255), "Perfect Aim": (0, 125, 0),
    "No Recoil": (0, 255, 123), "Crit boost": (0, 162, 232),
    "Bullet x3": (250, 0, 250), "Bullet damage up": LIGHT_RED,
    "Bullet speed up": (255, 0, 125), "Bullet duration up": (255, 125, 0),
    "Bullet radius up": (255, 125, 125), "Fuller auto": RED,
    "Stealth": BLACK, "Low friction": (200, 200, 255),
    "Less auto": LIGHT_BLUE,
    "Visible": WHITE,
    "Burning": DARK_RED,
    "Damage Over time": WHITE,
    "Stunned": (255, 100, 100),
    "High Jam": WHITE,
    "No crit": WHITE,
    "Low Aim": WHITE,
    "Bullet speed down": WHITE,
    "Bullet duration down": WHITE,
    "Bullet radius down": WHITE,
    "High friction": (55, 55, 55),
    "Forced Slide": WHITE,
    "Double speed": LIGHT_BLUE,
    "Slowness": WHITE,
    "Dash recovery up": WHITE,
    "No debuff": WHITE,
    "Last Stand": WHITE,
    "Dash": (96, 96, 192),
}


def jam_manager(self, current_weapon):
    if current_weapon.jam_rate >= random.random() and self.status["No Jam"] == 0 and self.status["High Jam"] == 0 or \
            current_weapon.jam_rate * 2 >= random.random() and self.status["No Jam"] == 0 and self.status["High Jam"] \
            > 0:
        # Jamming sound
        play_sound(current_weapon.jamming_sound, "SFX")
        # Make the gun jam
        self.shot_allowed = False
        self.no_shoot_state = current_weapon.jam_duration
        return True
    return False


def stunned_manager(self):
    if self.status["Stunned"] > 0:
        for x in self.input:
            self.input[x] = False
        # if not self.is_hostile:
        #    for x in self.mouse_input:
        #        self.mouse_input[x] = False
    #


def stunned_manager_player(self):
    if self.status["Stunned"] > 0:
        for x in self.input:
            self.input[x] = False


def status_manager(self, entities):
    if self.status["No debuff"] > 0:
        for s in [
            "Burning", "Damage Over time", "Stunned", "High Jam",
            "Bullet speed down", "Bullet duration down", "Bullet radius down", "High friction", "Slowness"
        ]:
            self.status[s] = 0

    # Make work healing
    if self.status["Healing"] > 0:
        if self.health < self.max_health:
            self.health += 1
        if self.health > self.max_health:
            self.health = self.max_health

    if self.status["Burning"] > 0:
        entities["particles"].append(Particles.FireParticle([self.pos[0], self.pos[1]]))
        damage_calculation(self, 2, "Fire", death_message="Burned to a crisp")

    if self.status["Damage Over time"] > 0:
        damage_calculation(self, 1, "Physical")
        # damage_calculation(self, 1, "Physical", no_iframes=True)

    if self.status["No damage"] == 0:
        self.damage_taken = False

    # Make status effects go down
    for effect in self.status:
        if self.status[effect] > 0: self.status[effect] -= 1
    #


def bullet_x3_manager(bullets_per_shot, bullet_x3):
    modifier = 1
    if bullet_x3 > 0:
        modifier = 3
    return bullets_per_shot * modifier


def crit_manager(self, entities, current_weapon, guarantee_crit=False):
    mod = 1 + int(self.status["Crit boost"] > 0)
    if current_weapon.crit_rate * mod >= random.random() or guarantee_crit:
        entities["bullets"][-1].damage *= current_weapon.crit_multiplier
        entities["bullets"][-1].colour = LIGHT_BLUE
        self.crit = True
    #


def bullet_status_manager(self, entities):
    last_bullet_shot = entities["bullets"][-1]
    # Buffs
    # Perfect aim
    if self.status["Perfect Aim"] > 0:
        last_bullet_shot.angle = self.aim_angle + random.uniform(
            -self.weapon.spread, self.weapon.spread)

    if self.status["Bullet damage up"] > 0:
        last_bullet_shot.damage *= 2
    # Bullet speed up
    if self.status["Bullet speed up"] > 0:
        last_bullet_shot.speed *= 2
    # Bullet duration up
    if self.status["Bullet duration up"] > 0:
        last_bullet_shot.duration *= 3
    # Bullet radius up
    if self.status["Bullet radius up"] > 0:
        last_bullet_shot.radius *= 2

    # Debuffs
    if self.status["Low Aim"]:
        combined_accuracy = self.weapon.spread + self.weapon.accuracy * 2
        last_bullet_shot.angle = self.angle + random.uniform(
            -combined_accuracy, combined_accuracy)
    # Bullet speed up
    if self.status["Bullet speed down"] > 0:
        last_bullet_shot.speed *= 0.5
    # Bullet duration up
    if self.status["Bullet duration down"] > 0:
        last_bullet_shot.duration //= 3
    # Bullet radius up
    if self.status["Bullet radius down"] > 0:
        last_bullet_shot.radius *= 0.5


def after_shooting_manager(self, current_weapon):
    # Make the ammo go down
    current_weapon.ammo -= current_weapon.ammo_cost

    # Make the fire rate work
    self.no_shoot_state = current_weapon.fire_rate
    if self.status["Less auto"] > 0:
        self.no_shoot_state = round(current_weapon.fire_rate * 1.5)
    if self.status["Fuller auto"] > 0:
        self.no_shoot_state = 0

    # Add recoil
    if self.status["No Recoil"] == 0:
        self.aim_angle += random.uniform(-current_weapon.recoil, current_weapon.recoil)


def movement_player(self, entities):
    # Eventually I need to add alternatives to sliding
    # Get the base movement speed
    speed = self.speed
    self.running = False
    self.walking = False

    max_vel = self.vel_max
    # vel_max = self.vel_max
    sound_rate = 20
    sound_volume = 1
    # Increase speed if the player is running

    # Handle double speed and slowness status
    if self.status["Slowness"]:
        max_vel *= 0.5
    if self.status["Double speed"]:
        max_vel *= 2

    # Checks for which direction the player must move
    # Rework it so that you are not faster when walking in diagonal, this should be fixed now
    vel_limit_x, vel_limit_y = not abs(self.vel[0]) > max_vel, not abs(self.vel[1]) > max_vel
    allow_correction = False
    dash_vel = [0, 0]
    if self.input["Up"] and vel_limit_y:
        self.vel[1] -= speed
        dash_vel[1] -= speed
        allow_correction = True
    if self.input["Down"] and vel_limit_y:
        self.vel[1] += speed
        dash_vel[1] += speed

        allow_correction = True
    if self.input["Left"] and vel_limit_x:
        self.vel[0] -= speed
        dash_vel[0] -= speed

        allow_correction = True
    if self.input["Right"] and vel_limit_x:
        self.vel[0] += speed
        dash_vel[0] += speed
        allow_correction = True

    if not check_point_in_circle(max_vel, 0, 0, self.vel[0], self.vel[1]) and allow_correction:
        self.vel = move_with_vel_angle([0, 0], max_vel, angle_between(self.vel, [0, 0]))
    self.walking = allow_correction

    self.standing_still = False
    if self.vel == [0, 0]:
        self.standing_still = True
    elif self.cutscene_mode:
        # This makes entities use their walking animation during cutscenes
        self.walking = True

    # Play sound for when the player walks
    if not self.standing_still and self.time % sound_rate == 0:
        play_sound(f"Curtis Walk {random.randint(1, 2)}", "SFX", modified_volume=sound_volume)

    # Dash mechanic
    if self.dash_cooldown <= 0 and not self.standing_still and self.input["Dash"]:
        # Handle dash here
        play_sound("Player dash", modified_volume=0.25)
        dash_angle = angle_between(dash_vel, [0, 0])
        self.dash_cooldown = self.dash_charge_time
        if self.status["Dash recovery up"] > 0:
            self.dash_cooldown //= 2
        self.vel = move_with_vel_angle(self.vel, self.dash_speed/self.friction, dash_angle)
        for x in range(4):
            angle = dash_angle - 15 - 3.25 * 2 + x * 7.5 * 2
            entities["particles"].append(
                Particles.RandomParticle2(
                move_with_vel_angle([self.pos[0], self.pos[1]], -4, angle),
                    WHITE, 1.5 + random.uniform(0, 2), 24, angle))

        if self.status["No damage"] < self.dash_iframes:
            self.status["No damage"] += self.dash_iframes
    self.dash_cooldown -= 1
    #


def movement_entity(self):
    speed = self.speed
    self.running = False
    self.walking = False
    if self.status["Forced Slide"] == 0:

        max_vel = self.vel_max

        # Increase speed if the player is running
        if "Dash" in self.input:  # It's easier than fixing everything
            if self.input["Dash"]:
                speed = self.speed * 1.5
                max_vel = self.vel_max * 1.5
                self.running = True

        # Handle double speed and slowness status
        if self.status["Slowness"]:
            max_vel *= 0.5
        if self.status["Double speed"]:
            max_vel *= 2

        # Checks for which direction the player must move
        # Rework it so that you are not faster when walking in diagonal, this should be fixed now
        vel_limit_x, vel_limit_y = not abs(self.vel[0]) > max_vel, not abs(self.vel[1]) > max_vel
        allow_correction = False

        if self.input["Up"] and vel_limit_y:
            self.vel[1] -= speed
            allow_correction = True
        if self.input["Down"] and vel_limit_y:
            self.vel[1] += speed
            allow_correction = True
        if self.input["Left"] and vel_limit_x:
            self.vel[0] -= speed
            allow_correction = True
        if self.input["Right"] and vel_limit_x:
            self.vel[0] += speed
            allow_correction = True

        # Might keep that
        if not check_point_in_circle(max_vel, 0, 0, self.vel[0], self.vel[1]) and allow_correction:
            self.vel = move_with_vel_angle([0, 0], max_vel, angle_between(self.vel, [0, 0]))
        self.walking = allow_correction

        self.standing_still = False
        if self.vel == [0, 0]:
            self.standing_still = True
        elif self.cutscene_mode:
            # This makes entities use their walking animation during cutscenes
            self.walking = True


def movement_output(self, level):
    if self.status["High friction"] > 0:
        self.vel = [self.vel[0] * 0.25, self.vel[1] * 0.25]

    # This give the direction the entity moves towards,
    # when using it for anything you should check if the entity is even moving
    self.direction_angle = angle_between(self.vel, [0, 0])

    collision_check(self, level["map"])
    # Make the guy move
    self.pos[0] += self.vel[0]
    self.pos[1] += self.vel[1]
    self.collision_box = pg.Rect(self.pos[0] - self.thiccness / 2, self.pos[1] - self.thiccness / 2,
                                 self.thiccness, self.thiccness)

    # |Friction handling|-----------------------------------------------------------------------------------------------
    friction_strength = self.friction
    if self.status["Forced Slide"]:  # Some enemies will slide
        friction_strength = 0.025
    if self.status["Low friction"] > 0:
        friction_strength = 0
    for i in range(2):
        if self.vel[i] != 0:
            if self.vel[i] >= 0 + friction_strength:
                self.vel[i] -= friction_strength
            elif self.vel[i] <= 0 - friction_strength:
                self.vel[i] += friction_strength
            else:
                self.vel[i] = 0
    #


# |Cutscene mode|-------------------------------------------------------------------------------------------------------
CUTSCENE_SKIP_TIMER = [0]


def cutscene_mode(self, entities, bullets):
    # Structure
    #   [
    #       {"stage": int, "task": [[string, ...], ...], "condition": [string, ...]}
    #   ]

    if not self.cutscene_mode:
        return

    if self.is_player:
        # Check for inputs from the player, if it goes past a certain amount of time it'll skip,
        # it needs a particle to show how long it's been pressed for
        if True in [self.input['Interact'], self.input["Reload"]]:
            CUTSCENE_SKIP_TIMER[0] += 1
        else:
            CUTSCENE_SKIP_TIMER[0] -= 1

        if CUTSCENE_SKIP_TIMER[0] > 0:
            entities["UI particles"].append(Particles.CutsceneSkip(CUTSCENE_SKIP_TIMER[0]))
            if CUTSCENE_SKIP_TIMER[0] == 60:
                play_sound("Menu confirm", "SFX")
                # make it skip everything
                for t in ["players", "enemies"]:
                    for e in entities[t]:
                        for x in range(len(e.cutscene_mode)):
                            for task in e.cutscene_mode[x]["task"]:
                                if task[0] == "Music":
                                    play_music(task[1], entities, particule=task[2], use_intro=task[3])
                                    task[-1] = False
                        e.cutscene_mode = []
                return

    # Prevent the player or AI from making moves
    for i in self.input:
        self.input[i] = False
    if self.is_ally or self.is_player:
        self.mouse_pos = self.pos
        for i in self.mouse_input:
            self.mouse_input[i] = False
    if self.no_shoot_state <= 45 and not self.is_player:
        self.no_shoot_state = 45
    else:
        self.no_shoot_state += 1

    # Does the cutscene
    if self.cutscene_mode[0]["stage"] <= entities["cutscene stage"]:
        for task in self.cutscene_mode[0]["task"]:
            # All these could be put in a switch case or a dict
            # Goto              ["Goto", [target x, target y], modifier]
            # Look at           ["Look at", target]
            # Aim at            ["Aim at", target]
            # Speak             ["Speak", text, colour]
            # Noise             ["Noise", sound_to_play, sound_type, True]
            # Music             ["Music", music_to_play, particle, music_intro, True]
            # Shoot             ["Shoot", BulletClassInstance, [distance, angle], BulletTarget, True]
            # Boss card         ["Boss card", [Top text, Bottom text], True]
            # Dialogue          ["Dialogue", cutscene_to_play, True]
            # Free Var          ["Free Var", var_to_affect, [mode]]
            if task[0] == "Goto":
                if distance_between(task[1], self.pos) > task[2] * self.speed:
                    self.vel = move_with_vel_angle([0, 0], self.speed * task[2], angle_between(task[1], self.pos))
            elif task[0] == "Look at":
                point = task[1]
                if type(point) in (int, float):
                    point = move_with_vel_angle(self.pos, 20, point)
                self.angle = angle_between(point, self.pos)
                if self.is_ally or self.is_player:
                    self.mouse_pos = move_with_vel_angle(self.pos, 50, self.angle)
            elif task[0] == "Aim at":
                point = task[1]
                if type(point) in (int, float):
                    point = move_with_vel_angle(self.pos, 20, point)
                self.aim_angle = angle_between(point, self.pos)
            elif task[0] == "Speak":
                entities["particles"].append(
                    Particles.FloatingTextType2([self.pos[0], self.pos[1] - 16], 18, task[1], task[2], 1))
            elif task[0] == "Noise":
                if task[-1]:
                    play_sound(task[1], task[2])
                    task[-1] = False
            elif task[0] == "Music":
                if task[-1]:
                    play_music(task[1], entities, False, False)
                    task[-1] = False
            elif task[0] == "Shoot":
                if task[-1]:
                    bullets[task[3]].append(task[1])
                    bullets[task[3]][-1].pos = move_with_vel_angle(self.pos, task[2][0], task[2][1])
                    task[-1] = False
            elif task[0] == "Boss card":
                if task[-1]:
                    entities["UI particles"].append(Particles.MissionTitleCard(task[1][0], task[1][1]))
                    task[-1] = False
            elif task[0] == "Dialogue":
                if task[-1]:
                    entities["dialogue to play"]["During"].append(task[1])
                    task[-1] = False
            elif task[0] == "Free Var":
                # ["Free Var", var_to_affect, [mode]]

                # ["=", value]
                # ["+", value]
                # ["-", value]
                # ["+=", value, target_value]
                # ["-=", value, target_value]
                free_var_mod = self.free_var[task[1]]
                if type(free_var_mod) in [str, int, float]:
                    if task[2][0] == "=":
                        self.free_var[task[1]] = task[2][1]
                    elif task[2][0] == "+":
                        self.free_var[task[1]] += task[2][1]
                    elif task[2][0] == "-":
                        self.free_var[task[1]] -= task[2][1]
                    elif task[2][0] == "+=":
                        self.free_var[task[1]] += task[2][1]
                        if self.free_var[task[1]] >= task[2][2]:
                            self.free_var[task[1]] = task[2][2]
                    elif task[2][0] == "-=":
                        self.free_var[task[1]] -= task[2][1]
                        if self.free_var[task[1]] <= task[2][2]:
                            self.free_var[task[1]] = task[2][2]
                # ["=", [value, target]]
                # ["+", [value, target]]
                # ["-", [value, target]]
                # ["+=", [value, target], target_value]
                # ["-=", [value, target], target_value]
                else:
                    dist = task[2][1][0]
                    if task[2][0] == "=":
                        self.free_var[task[1]][dist] = task[2][1][1]
                    elif task[2][0] == "+":
                        self.free_var[task[1]][dist] += task[2][1][1]
                    elif task[2][0] == "-":
                        self.free_var[task[1]][dist] -= task[2][1][1]
                    elif task[2][0] == "+=":
                        self.free_var[task[1]][dist] += task[2][1][1]
                        if self.free_var[task[1]][dist] >= task[2][2]:
                            self.free_var[task[1]][dist] = task[2][2]
                    elif task[2][0] == "-=":
                        self.free_var[task[1]][dist] -= task[2][1][1]
                        if self.free_var[task[1]][dist] <= task[2][2]:
                            self.free_var[task[1]][dist] = task[2][2]

        # check condition
        #   if the condition is fulfilled, the current "stage" of the entity gets removed, and it goes to the next one
        condition_complete = False
        # These could be moved to separate functions and be accessed with a dictionary
        # Timer         "condition": ["Timer", time]
        # Position      "condition": ["Position", radius, [center of target pos]]
        if self.cutscene_mode[0]["condition"][0] == "Timer":
            if self.cutscene_mode[0]["condition"][1] <= 0:
                condition_complete = True
            self.cutscene_mode[0]["condition"][1] -= 1
        elif self.cutscene_mode[0]["condition"][0] == "Position":
            pos = [self.cutscene_mode[0]["condition"][2][0], self.cutscene_mode[0]["condition"][2][1]]
            if check_point_in_circle(self.cutscene_mode[0]["condition"][1], pos[0], pos[1], self.pos[0], self.pos[1]):
                condition_complete = True

        # Removes the current stage
        if condition_complete:
            self.cutscene_mode.pop(0)

        # Make the cutscene stage advance
        allow_cutscene_to_advance = True
        for t in ["players", "enemies"]:
            for e in entities[t]:
                if e.cutscene_mode:  # This single line can let this become fun
                    if not e.cutscene_mode[0]["stage"] > entities["cutscene stage"]:
                        allow_cutscene_to_advance = False
                        break
        if allow_cutscene_to_advance:
            entities["cutscene stage"] += 1


# |Misc.|---------------------------------------------------------------------------------------------------------------
def write_time(time):
    microsecond = time
    second = microsecond // 60
    microsecond -= second * 60
    minute = second // 60
    second -= minute * 60
    return f'{minute}:{second}.{round(100 / 60 * microsecond)}'


@functools.lru_cache(typed=False)
def write_textline(line_id, send_back=False, change_lang=False):
    # Line id
    #   context_level_name
    #   level   :
    #       HU  Hub
    #       M?  mission ?
    #       ME  menu
    #       AR  arena
    #       FI  fishing
    #   context :
    #       RT  radio transmission
    #       CS  Cutscene
    #       ME  Menu
    #       DI  Dialogue
    #       TP  Pause menu tip
    #       TL  Mission Title
    #       UI  User interface
    #   name    :
    #       anything that make sense, number them
    # UI elements have to load it on each frame
    # If it comes from a game event it only loads when it was made
    try:
        lang = change_lang
        if type(lang) != int:
            lang = get_from_json('Settings.json', "Language")
        file = [
            'Translations/Translation_English.json',
            'Translations/Translation_French.json',
            'Translations/Translation_German.json',
            'Translations/Translation_Polish.json',
            'Translations/Translation_Russian.json',
            'Translations/Translation_Spanish.json',
        ][lang]
        with open(file, encoding='utf-8') as json_file:
            return json.load(json_file)[line_id].encode("utf_8").decode("utf_8")
    except KeyError:
        return_text = "Key error"
        print(line_id)
        if send_back:
            return_text = line_id
        return return_text


def update_translation_files():
    print("I AM GONNNAAAAAAAAAAAAAA")
    with open("Translations/Translation_English.json", encoding='utf-8') as json_file:
        based_translation = json.load(json_file)

    for t in ['Translation_French.json',
              'Translation_German.json',
              'Translation_Polish.json',
              'Translation_Russian.json',
              'Translation_Spanish.json']:
        with open(f'Translations/{t}', encoding='utf-8') as json_file_2:
            cringe_translation = json.load(json_file_2)
        new_cringe_translation = {}
        for l in based_translation:
            if l not in cringe_translation:
                new_cringe_translation.update({l: ""})
                continue
            new_cringe_translation.update({l: cringe_translation[l]})
        dict_to_json(f'Translations/{t}', new_cringe_translation)
        print({'Translation_French.json': "C",
              'Translation_German.json': "O",
              'Translation_Polish.json': "O",
              'Translation_Russian.json': "M",
              'Translation_Spanish.json': "I'VE COOMED SO MUCH"}[t])
        #


def needed_in_menu_and_game(WIN, keys):
    # Handle events
    for event in pg.event.get():
        if event.type not in [pg.QUIT, pg.JOYDEVICEADDED, pg.JOYDEVICEREMOVED, pg.WINDOWFOCUSLOST, pg.VIDEORESIZE]:
            continue
        elif event.type == pg.QUIT:
            sys.exit()
        elif event.type == pg.VIDEORESIZE:
            width, height = event.size
            if width < 630:
                width = 630
            if height < 450:
                height = 450

            # WIN_WIDTH, WIN_HEIGHT = 630, 450
            # ORIGINAL_WIDTH, ORIGINAL_HEIGHT = WIN_WIDTH, WIN_HEIGHT
            WIN = pg.display.set_mode((width, height), pg.RESIZABLE)
        elif event.type == pg.WINDOWFOCUSLOST:
            return True
        elif event.type == pg.JOYDEVICEADDED or event.type == pg.JOYDEVICEREMOVED:
            ALL_CONTROLLERS.pop(0)
            ALL_CONTROLLERS.append([pg.joystick.Joystick(x) for x in range(pg.joystick.get_count())])

    # if SYSTEM_CONTROLS_INPUT["Screenshot"] or random.randint(0, 300) == 1:
    if SYSTEM_CONTROLS_INPUT["Screenshot"]:
        screenshot(WIN)
    system_input_handler(keys)


def screenshot(win):
    chungus = datetime.datetime.now()
    year = chungus.year
    month = chungus.month
    day = chungus.day
    hour = chungus.hour
    minute = chungus.minute
    second = chungus.second
    # microsecond = chungus.microsecond
    print("Screenshot taken")

    pg.image.save(win, f"Screenshots/THR-1's Assault {year}-{month}-{day} {hour}-{minute}-{second}.png")


def create_sotg(win):
    win_width, win_height = win.get_size()
    mod = 3

    win = pg.display.set_mode((120 * mod, 64 * mod), pg.RESIZABLE)
    temp_ui_font = create_temp_font_3(win_height)
    win.blit(pg.transform.scale(pg.image.load('!Dev stuff/sotg.png'), (128 * mod, 64 * mod)), (0, 0))

    # text = "Status of the game 32"
    text = "Version 1.0 is out!"
    # text = ""
    win.blit(temp_ui_font.render("No Name TSS", True, WHITE), (6 * mod, 1 * mod + 4))
    win.blit(temp_ui_font.render(text, True, WHITE), (6 * mod, 10 * mod + 4))
    win.blit(temp_ui_font.render("Last Major Update", True, WHITE), (6 * mod, 20 * mod + 4))
    win.blit(temp_ui_font.render("", True, WHITE), (6 * mod, 30 * mod + 4))

    pg.display.update()
    pg.image.save(win, f"!Dev stuff/{text}.png")
    win = pg.display.set_mode((win_width, win_height), pg.RESIZABLE)


def hub_npc_path_making(start_point, end_point, connections, points, path_to):
    current_location = start_point
    fail_safe_on = False
    # List that keeps track of points used
    fuck_off = []
    # while current_location != end_point:
    for p in range(3): # Changed to that to avoid infinite loops
        if current_location == end_point:
            break
        control_dist = 14290
        new_location = current_location
        # Go through  connected points
        for possible_next_point in connections[current_location]:
            # Check if it gets closer to the next one
            test_dist = distance_between(points[end_point], points[possible_next_point])
            if test_dist < control_dist and possible_next_point not in fuck_off or fail_safe_on:
                control_dist = test_dist
                new_location = possible_next_point
                fail_safe_on = False
        if new_location != current_location:
            current_location = new_location
            path_to.append(new_location)
            fuck_off.append(new_location)
        else:
            pass
            # fail_safe_on = True
    if current_location == end_point:
        path_to = [end_point]
    return path_to


def entity_path_making(self, start_point, end_point, connections, points):
    end_point_pos = points[end_point]
    path_to = []
    control_dist = BIG_INT

    # Go through each connection of the start point
    for c in connections[start_point]:
        potential_path = [c]
        current_point = c

        # For the next 2 points
        for p in range(2):
            tee_hee = BIG_INT
            for test_point in connections[current_point]:
                # Make sure test_point is not a previous one
                point_valid = True
                for old_connection in potential_path:
                    if test_point in connections[old_connection]:
                        point_valid = False
                        break

                    if test_point == start_point:
                        point_valid = False
                        break
                if not point_valid:
                    continue
                test_hee = distance_between(points[test_point], end_point_pos)
                if test_hee > tee_hee:
                    continue
                tee_hee = test_hee
                # Add point to path
                current_point = test_point
                potential_path.append(test_point)
                break

        # get test dist than check if path get's closer to target point
        test_dist = distance_between(points[potential_path[-1]], end_point_pos)
        if test_dist < control_dist:
            control_dist = test_dist
            path_to = potential_path

    return path_to


def entity_path_making_old(self, start_point, end_point, connections, points, path_to):
    current_location = start_point

    # while current_location != end_point:
    # for p in range(1): # Changed to that to avoid infinite loops
    # if current_location == end_point:
    #     break
    control_dist = 14290
    new_location = current_location
    # Go through  connected points
    for possible_next_point in connections[current_location]:
        # Check if it gets closer to the next one
        test_dist = distance_between(points[end_point], points[possible_next_point])
        if test_dist < control_dist and possible_next_point not in self.pathfinding_old_positions:
            control_dist = test_dist
            new_location = possible_next_point
    #if control_dist < 64 and new_location not in self.pathfinding_old_positions:
    if control_dist < 64 and new_location not in self.pathfinding_old_positions:
        self.pathfinding_old_positions.append(new_location)

    current_location = new_location
    path_to.append(new_location)
    if len(self.pathfinding_old_positions) > 5:
        self.pathfinding_old_positions.pop(0)
    return path_to


def hub_npc_path_making_escort(start_point, end_point, connections, points, path_to):
    current_location = start_point
    fail_safe_on = False
    # List that keeps track of points used
    fuck_off = []
    fail_count = 0
    while current_location != end_point:
        control_dist = 14290
        new_location = current_location
        # Go through  connected points
        for possible_next_point in connections[current_location]:
            # Check if it gets closer to the next one
            test_dist = distance_between(points[end_point], points[possible_next_point])
            if test_dist < control_dist and possible_next_point not in fuck_off or fail_safe_on:
                control_dist = test_dist
                new_location = possible_next_point
                fail_safe_on = False
                fail_count = 0
        if new_location != current_location:
            current_location = new_location
            path_to.append(new_location)
            fuck_off.append(new_location)
        else:
            fail_count += 1
            if fail_count > 10:
                print("Whoops, something broke")
                return path_to
            # fail_safe_on = True
    return path_to


def line(x1, y1, x2, y2):
    d0, d1 = x2 - x1, y2 - y1
    count = max(abs(d1 + 1), abs(d0 + 1))
    if d0 == 0:
        return (numpy.full(count, x1), numpy.round(numpy.linspace(y1, y2, count)).astype(numpy.int32))
    if d1 == 0:
        return numpy.round(numpy.linspace(x1, x2, count)).astype(numpy.int32), numpy.full(count, y1)
    return numpy.round(numpy.linspace(x1, x2, count)).astype(numpy.int32), \
           numpy.round(numpy.linspace(y1, y2, count)).astype(numpy.int32)


def waypoint_connection_pathfinding_creator(planning_image):
    # This function is there to make it easier for me to make the paths for the NPCs in the hub

    # Get position of the way points
    waypoints = [[int(pg.Rect(wall).centerx / 32), int(pg.Rect(wall).centery / 32)] for wall in advanced_image_to_map_geometry(
        planning_image, colours_to_check=[(255, 255, 0)])]

    # Start making the graph
    waypoint_name_dict = {}
    for count, point_to_add in enumerate(waypoints):
        waypoint_name_dict.update({f"{count}": [point_to_add[0], point_to_add[1]]})

    # Get all valid connections
    connection_dict = {}
    for point_to_check in waypoint_name_dict:
        valid_connection = []
        start_point = waypoint_name_dict[point_to_check]
        for potential_connection in waypoint_name_dict:
            end_point = waypoint_name_dict[potential_connection]
            # Make sure it's not checking for a connection with the same point
            if point_to_check == potential_connection:
                continue
            # Goes through all the pixel between the 2 points
            points_between = line(start_point[0], start_point[1], end_point[0], end_point[1])
            points_between = [points_between[0].tolist(), points_between[1].tolist()]
            # if one is white go to the next potential connection
            is_wall_good = True
            for potential_wall in enumerate(points_between[0]):
                potential_white_point = [points_between[0][potential_wall[0]], points_between[1][potential_wall[0]]]
                if planning_image.get_at(potential_white_point) == (255, 255, 255):
                    is_wall_good = False
                    break
            # Length check?
            p1 = [points_between[0][0], points_between[1][0]]
            p2 = [points_between[0][-1], points_between[1][-1]]
            dist = distance_between(p1, p2)
            is_wall_good = dist < 18 and is_wall_good # 18

            if is_wall_good:
                valid_connection.append(potential_connection)
        connection_dict.update({point_to_check: valid_connection})
    # Convert the waypoints to in game coordinates
    new_bullshit = {}
    for point_to_check in waypoint_name_dict:
        new_bullshit.update({point_to_check: [waypoint_name_dict[point_to_check][0] * 32 + 16,
                                              waypoint_name_dict[point_to_check][1] * 32 + 16]})
    # "<id>": [<x>, <y>],"<id>": [<id of connected points>]
    return {'points': new_bullshit, 'connections': connection_dict}


def find_rects_giga_chad(map_geometry, width, height, animate=False):
    # This thing will have to be remade for new projects
    output = [

    ]
    biggest_side = [height, 1]
    if height < width:
        biggest_side = [width, 1]
    # Go through all the map to look for a white square
    for x in range(width):
        for y in range(height):
            # If it finds a white square
            if map_geometry[y][x] == 1:
                # z = 0
                # Get size of square

                # for z in range(biggest_side[0] - [y, x][biggest_side[1]]):
                for z in range(height - y):
                    # Check if it's the max size of the square, if yes, add it to output
                    # Modify that so that it checks the whole square
                    # if y + z >= height or x + z >= width:
                    #     output.append([x, y, z, z])
                    #     break
                    if y + z >= height:
                        output.append([x, y, 1, z])
                        break
                    # Check if there's an empty point
                    points_to_check = [map_geometry[y + z][x]]
                    for temp in range(z):
                        points_to_check.append(map_geometry[y + temp][x])
                        # points_to_check.append(map_geometry[y + z][x + temp])

                    if 0 in points_to_check:
                        output.append([x, y, 1, z])
                        break
                # Remove the square
                # for remove_y in range(z):
                #     for remove_x in range(z):
                #         map_geometry[y + remove_y][x + remove_x] = 0
                for remove_y in range(z):
                    map_geometry[y + remove_y][x] = 0
                #
        if animate:
            screen = animate[0]
            clock = animate[1]
            keys = pg.key.get_pressed()
            needed_in_menu_and_game(screen, keys)

            screen.fill(BLACK)
            for colour, wall in enumerate(output):
                pg.draw.rect(screen, (128, (colour * 25) % 255, (colour * 50) % 255),
                             [wall[0] * 2, wall[1] * 2, wall[2] * 2, wall[3] * 2])
            pg.display.update()
            clock.tick(90)

    # Check through all the squares
    # Doing the check more times makes it optimize squares more
    new_output = []
    for i_like_whiskey in range(7):
        for rect in output:
            for num, rect_to_check in enumerate(output):
                # Fuse them together
                if rect == rect_to_check:
                    continue
                same_x = rect[0] == rect_to_check[0]
                same_y = rect[1] == rect_to_check[1]
                same_width = rect[2] == rect_to_check[2]
                same_height = rect[3] == rect_to_check[3]

                # Same Y, the 2 touch on the right side of the first, same height
                r_side = same_y and rect[0] + rect[2] == rect_to_check[0] and same_height
                # Same X, the 2 touch on the bottom side of the first, same width
                b_side = same_x and rect[1] + rect[3] == rect_to_check[1] and same_width

                remove = False
                if r_side:
                    rect[2] += rect_to_check[2]
                    remove = True
                if b_side:
                    rect[3] += rect_to_check[3]
                    remove = True

                if remove:
                    output[num] = [0, 0, 0, 0]

            if animate:
                screen = animate[0]
                clock = animate[1]
                keys = pg.key.get_pressed()
                needed_in_menu_and_game(screen, keys)

                screen.fill(BLACK)
                for colour, wall in enumerate(output):
                    pg.draw.rect(screen, (128, (colour * 25) % 255, (colour * 50) % 255),
                                 [wall[0] * 2, wall[1] * 2, wall[2] * 2, wall[3] * 2])
                pg.display.update()
                clock.tick(90)

        # Remove overlapping rects
        new_output = []
        for rect_collision in output:
            if rect_collision != [0, 0, 0, 0]:
                new_output.append(rect_collision)
        # output = new

    return new_output


def image_to_map_geometry(map_image, animate=False):
    map_geometry = [
    ]
    zero = [0, 0]
    width, height = map_image.get_width(), map_image.get_height()
    # Convert the image to something the functions can use
    for y in range(height):
        x_list = []
        for x in range(width):
            num = 0
            if map_image.get_at((x, y)) == (255, 255, 255):
                num = 1
            if map_image.get_at((x, y)) == (255, 0, 255):
                zero = [x, y]
                if map_image.get_at((x - 1, y)) == (255, 255, 255):
                    if map_image.get_at((x + 1, y)) == (255, 255, 255):
                        if map_image.get_at((x, y - 1)) == (255, 255, 255):
                            if map_image.get_at((x, y + 1)) == (255, 255, 255):
                                num = 1
            x_list.append(num)
        map_geometry.append(x_list)
    # Creating map geometry
    # retrieving the column size of array
    output = find_rects_giga_chad(map_geometry, len(map_geometry[0]), len(map_geometry), animate=animate)

    # This make them usable for level geometry
    for temp in range(len(output)):
        rect = output[temp]
        output[temp] = ((rect[0] - zero[0]) * 32,
                        (rect[1] - zero[1]) * 32,
                        rect[2] * 32, rect[3] * 32)
    return output


def advanced_image_to_map_geometry(map_image, colours_to_check=[(255, 255, 255)], animate=False, size_mod=32):
    map_geometry = [
    ]
    width, height = map_image.get_width(), map_image.get_height()
    # Convert the image to something the functions can use
    for y in range(height):
        x_list = []
        for x in range(width):
            num = 0
            if map_image.get_at((x, y)) in colours_to_check:
                num = 1
            x_list.append(num)
        map_geometry.append(x_list)
    # Creating map geometry,  retrieving the column size of array
    output = find_rects_giga_chad(map_geometry, len(map_geometry[0]), len(map_geometry), animate=animate)

    # This make them usable for level geometry
    for temp in range(len(output)):
        rect = output[temp]
        output[temp] = ((rect[0]) * size_mod, (rect[1]) * size_mod, rect[2] * size_mod, rect[3] * size_mod)
    return output


def get_image_colour_list(image):
    return_list = []
    for y in range(image.get_height()):
        for x in range(image.get_width()):
            return_list.append(image.get_at((x, y)))
    return return_list


# |Level Generation|----------------------------------------------------------------------------------------------------
enemy_type_values = {
    "Grunt": 0.25,
    "Shock": 0.75,
    "Support": 3,
    "Specialist 1": 1.75,
    "Specialist 2": 1.75,
    "Elite": 5
}
ENEMY_TYPE_TO_FACTION_UNIT = [
    {"VIP": "Manager",
     "Grunt": "Body Guard",
     "Shock": "Heavy Sniper",
     "Support": "Radar Operator",
     "Specialist 1": "Missile Operator",
     "Specialist 2": "Marksman",
     "Elite": "Enforcer",
     "Boss 1": "Armed Shield Generator",
     "Boss 2": "Energy Generator"
     },
    {"VIP": "Sculptor",
     "Grunt": "Skirmisher",
     "Shock": "BoomStick",
     "Support": "Smoker",
     "Specialist 1": "Snare",
     "Specialist 2": "Crusher",
     "Elite": "Assassin",
     "Boss 1": "Hover Tank",
     "Boss 2": "Gilgamesh"
     },
    {"VIP": "Commanding Officer",
     "Grunt": "Infantry",
     "Shock": "Flamer",
     "Support": "Spotter",
     "Specialist 1": "Artilleryman",
     "Specialist 2": "Grenadier",
     "Elite": "Bulwark",
     "Boss 1": "Fire Support Mech",
     "Boss 2": "Attack Helicopter"
     },
    {"True Final Boss": "Rigel",
     "Alt Zoar Final boss": "THR-1",
     "Alt THR-1 Final boss": "Zoar",
     }
]
# Manufacturer
def enemy_squad_generator(current_mission, faction=0, modified_point_budget=0):
    # Returns a list of enemies to spawn
    point_budget = round(current_mission * 1.5) + 2
    point_budget = int(math.exp2(current_mission*0.35) * 0.125 + 2)
    if modified_point_budget > 0:
        point_budget = modified_point_budget
    enemy_squad = []
    # Get valid enemies to spawn
    while point_budget > 0:
        enemies_within_budget = []
        for e in enemy_type_values:
            # Elite enemies only spawn past the first 2 missions
            if e == "Elite" and current_mission <= 2:
                continue
            # Check if the enemy type is within the budget
            if enemy_type_values[e] <= point_budget:
                enemies_within_budget.append(e)
                if e != "Elite" and random.random() > 0.45:
                    enemies_within_budget.append(e)

        if not enemies_within_budget:
            break
            # return [], 0
        # Randomly select enemy type
        num = get_random_element_from_list(enemies_within_budget)
        faction_unit = ENEMY_TYPE_TO_FACTION_UNIT[faction][num]

        if faction_unit in enemy_squad and random.random() < 0.45:
           continue

        if faction_unit == ENEMY_TYPE_TO_FACTION_UNIT[faction]["Grunt"] and random.random() < 0.45:
           continue
        point_budget -= enemy_type_values[num]
        enemy_squad.append(faction_unit)

    return enemy_squad, point_budget


# @timeme
def map_generator(current_mission, testing=False, defense_mode=False, level_objective="Defense"):
    w = (255, 255, 255, 255)
    full_wall = [w, w, w, w, w, w, w, w]

    # Get all segments based on mission number
    map_set = "1, Industrial Park"
    if current_mission < 5:
        map_set = "1, Industrial Park"
    elif current_mission < 10:
        map_set = "2, Red Desert"
    elif current_mission < 15:
        map_set = "3, Iron Mines"
    # map_set = "1, Industrial Park"
    # map_set = "2, Red Desert"
    # map_set = "3, Iron Mines"
    segment_bank = []
    for x in os.listdir(f'Maps/{map_set}'):
        if x == 'Master segment list.png':
            segment_bank = []
            master_segment_image = pg.image.load(f'Maps/{map_set}/{x}').convert()
            for img_y in range(master_segment_image.get_height()//8):
                for img_x in range(master_segment_image.get_width()//8):
                    segment_bank.append(master_segment_image.subsurface((img_x * 8, img_y * 8, 8, 8)))
            break
        if os.path.splitext(f'Maps/{map_set}/{x}')[1] in [".png"]:
            segment_bank.append(pg.image.load(f'Maps/{map_set}/{x}').convert())

    # Get size of the map
    if not defense_mode:
        mum = 10 + current_mission//3 * 3
        if level_objective == "Seek and Destroy":
            mum = round(mum * 0.7)

        min_size, max_size = 4, {"odd": mum - 1, "even": mum}[meme(mum)]
        if max_size - min_size <= min_size:
            max_size = max_size + min_size + 1
        if min_size % 2 != 0:
            min_size += 1
        if max_size % 2 != 0:
            max_size += 1
        # print(f"{max_size=}")
        num = random.randint(min_size, max_size - min_size)
        map_width = {"odd": num-1, "even": num}[meme(num)]
        map_height = max_size - map_width
    else:
        map_height, map_width = 4, 4

    get_seg_side = lambda seg_img, side: seg_img.subsurface(side)
    columns = []

    # Generate the map
    map_sprite = pg.Surface((map_width * 8, map_height * 8))
    for y in range(map_height):
        rows = []
        for x in range(map_width):
            # Get sides that must match
            top_side = False
            left_side = False
            right_side = False
            bottom_side = False
            try:
                if y == 0:
                    top_side = full_wall
                else:
                    top_side = get_image_colour_list(get_seg_side(columns[y-1][x], (0, 7, 8, 1)))
                if x == 0:
                    left_side = full_wall
                else:
                    left_side = get_image_colour_list(get_seg_side(rows[x-1], (7, 0, 1, 8)))
                if x == map_width-1:
                    right_side = full_wall
                if y == map_height-1:
                    bottom_side = full_wall
            except IndexError:
                # print(rows)
                quit()
            # get_image_colour_list(get_seg_side())

            # Find segment with matching sides
            valid_segments = []
            for count, seg in enumerate(segment_bank):
                seg_top_side = get_image_colour_list(get_seg_side(seg, (0, 0, 8, 1)))
                seg_left_side = get_image_colour_list(get_seg_side(seg, (0, 0, 1, 8)))
                seg_right_side = get_image_colour_list(get_seg_side(seg, (7, 0, 1, 8)))
                seg_bottom_side = get_image_colour_list(get_seg_side(seg, (0, 7, 8, 1)))

                # Put checks here
                if seg_top_side != top_side:
                    continue
                if seg_left_side != left_side:
                    continue
                if right_side:
                    if seg_right_side != right_side:
                        continue
                if bottom_side:
                    if seg_bottom_side != bottom_side:
                        continue
                valid_segments.append(seg)
            # Choose segment randomly
            if testing:
                testing[0].fill((0, 0, 0))
                testing[0].blit(
                    pg.transform.scale_by(map_sprite, 4),
                    (0, 0))
                pg.display.update()
                testing[1].tick(30)
            try:
                rows.append(valid_segments[random.randint(0, len(valid_segments) - 1)])
            except ValueError:
                print_to_error_stream("We got a fuck up while making the map")
                screenshot(map_sprite)

            try:
                map_sprite.blit(rows[-1], (x * 8, y * 8))
            except IndexError:
                print_to_error_stream("We got a fuck up while making the map")
                screenshot(map_sprite)

        columns.append(rows.copy())

    # Remove bubbles
    proto_bubbles = [pg.Rect(wall) for wall in advanced_image_to_map_geometry(
        map_sprite, colours_to_check=[(0, 0, 0), (255, 0, 255), (255, 255, 0)], animate=False, size_mod=1)]
    potential_bubbles = []
    # Put every square in its own list
    # Go through all list
    # Check other lists to see if there's contact between rects
    check_overlap = lambda rect_1, rect_2: (
                rect_1.top < rect_2.bottom < rect_1.bottom or rect_1.top < rect_2.top < rect_1.bottom or
                rect_2.top < rect_1.bottom < rect_2.bottom or rect_2.top < rect_1.top < rect_2.bottom)
    while proto_bubbles:
        potential_bubbles.append([proto_bubbles[0]])
        proto_bubbles.pop(0)
        for pb in potential_bubbles:
            for bubble_rect in pb:
                # print(bubble_rect)
                for count, aaa in enumerate(proto_bubbles):
                    # if bubble_rect.colliderect(aaa):
                    # print(f"Rect test {bubble_rect.x + bubble_rect.width == aaa.x and check_overlap(bubble_rect, aaa)}")

                    if bubble_rect.x+bubble_rect.width == aaa.x and check_overlap(bubble_rect, aaa):
                        pb.append(proto_bubbles[count])
                        proto_bubbles.pop(count)

    # Check if potential bubbles touches each other and should be combined
    # You have to go through that unholy thing a few times just to make sure it gets everything
    for fuck_it_we_ball in range(10):
        for count, bubble_list in enumerate(potential_bubbles):
            for list_being_checked, check_list in enumerate(potential_bubbles):
                if list_being_checked == count:
                    continue
                combine = False
                try:
                    for aaa in check_list:
                        for bubble_rect in potential_bubbles[count]:
                            if bubble_rect.x + bubble_rect.width == aaa.x and check_overlap(bubble_rect, aaa):
                                combine = True
                                break
                        if combine:
                            break
                    if combine:
                        for ppp in check_list:
                            potential_bubbles[count].append(ppp)
                        potential_bubbles.pop(list_being_checked)
                except IndexError:
                    pass    # This shit is so ass

    # Find the biggest bubble
    bubble_sizes = []
    for bubble in potential_bubbles:
        area = 0
        for rect in bubble:
            area += rect.width * rect.height
        bubble_sizes.append(area)
    biggest_bubble = 0
    size_control = 0
    for count, caseoh in enumerate(bubble_sizes):
        if size_control < caseoh:
            size_control = caseoh
            biggest_bubble = count

    for count, bubble in enumerate(potential_bubbles):
        if count == biggest_bubble:
            continue
        for rect in bubble:
            pg.draw.rect(map_sprite, (255, 255, 255), rect)

    # Remove
    y_www = map_sprite.get_height()
    for y in range(y_www):
        for x in range(map_sprite.get_width()):
            if y == 0:
                continue
            pos = (x, y_www - y)
            if map_sprite.get_at(pos) == (0, 255, 255, 255):
                if map_sprite.get_at((x, y_www - y + 1)) == w:
                    map_sprite.set_at(pos, w)

    if testing:
        for x in range(90):
            testing[0].fill((0, 0, 0))
            testing[0].blit(pg.transform.scale_by(map_sprite, 4), (0, 0))

            # White     (255, 255, 255)     Walls
            # Teal      (0, 255, 255)       Walls, sprite
            # Black     (0, 0, 0)           Ground
            # Magenta   (255, 0, 255)       Ground, Spawn Point
            # Yellow    (255, 255, 0)       Ground, Objective Zone
            pg.display.update()
            testing[1].tick(30)

    # Make final sprite
    final_sprite = pg.Surface((map_width * 8 + 2, map_height * 8 + 2))
    final_sprite.fill((128, 41, 128))
    final_sprite.blit(map_sprite, (1, 1))
    # screenshot(final_sprite)
    return final_sprite


def level_generator(possible_levels, party_info, run_info, current_mission=1, mission_type="", faction=0):
    # point_budget = int(current_mission * (current_mission*0.25) + 8)
    point_budget = int(math.exp2(current_mission*0.5)+ 14)
    enemy_floor = current_mission * 5 + 5
    mission_reward = 1000
    # point_budget = 0
    # print(point_budget)
    # enemy_cap = round(point_budget * (2.25 - random.random() * 0.5))
    elite_limit = round(point_budget / 5 * 0.25)
    enemy_spawns = []
    level = {
        'name': '??', 'mission number': current_mission, 'faction': faction,
        'objective': ["Capture", "Seek and Destroy", "Eliminate Commander", "Defense", "Escort"][random.randint(0, 4)],

        # APC missions (Escort, Defense)
        'map': [],
        'events': [
            ['Mission start', {'rects': [], 'Conditions': 'trigger_check_mission_start'}, True, ['mission_start']]
            # ['Every frame', {'rects': [], 'Conditions': 'trigger_check_constant'}, False, ['mission_1_every_frame']]
        ],
        'level_finished': False,
        'pathfinding': None, # {
            # 'points': {},  # "<id>": [<x>, <y>]
            # 'connections': {}  # "<id>": [<id of connected points>]
        # },
        'rendering': {
            "Segments": [
            # {
            #   'Rect': pg.Rect,
            #   'Walls': [],
            #   'Floor': [],
            # }
            ],
            "Tile set": {"Wall": TILE_SET_IRON_MINES_WALL, "Floor": TILE_SET_IRON_MINES_FLOOR}
        },
        'objective points': [],
        'modifiers': [],
        'free var': {}
    }
    # Check if it's a boss mission
    if current_mission in [5, 10, 15]:
        level['objective'] = "Defeat Elite Unit"
    # Choose tile set based on which current mission
    if current_mission < 5:
        level["rendering"]["Tile set"] = {"Wall": TILE_SET_INDUSTRIAL_WALL, "Floor": TILE_SET_INDUSTRIAL_FLOOR}
    elif current_mission == 5:
        level["rendering"]["Tile set"] = {"Wall": TILE_SET_ENTRY_GATE_WALL, "Floor": TILE_SET_ENTRY_GATE_FLOOR}
    elif current_mission < 10:
        level["rendering"]["Tile set"] = {"Wall": TILE_SET_RED_DESERT_WALL, "Floor": TILE_SET_RED_DESERT_FLOOR}
    elif current_mission == 10:
        level["rendering"]["Tile set"] = {"Wall": TILE_SET_SAND_CAVES_WALL, "Floor": TILE_SET_SAND_CAVES_FLOOR}
    elif current_mission < 15:
        level["rendering"]["Tile set"] = {"Wall": TILE_SET_IRON_MINES_WALL, "Floor": TILE_SET_IRON_MINES_FLOOR}
    elif current_mission == 15:
        level["rendering"]["Tile set"] = {"Wall": TILE_SET_SALT_FLATS_WALL, "Floor": TILE_SET_SALT_FLATS_FLOOR}
    # level["rendering"]["Tile set"] = {"Wall": TILE_SET_RED_DESERT_WALL, "Floor": TILE_SET_RED_DESERT_FLOOR}

    # Generate mission name
    if current_mission != 15:
        name = write_textline(f"{level['objective']} Name {random.randint(0, 15)}")
        possible_missions_name = []
        for pp in possible_levels:
            possible_missions_name.append(pp["level"]["name"])
        while name in possible_missions_name:
            name = write_textline(f"{level['objective']} Name {random.randint(0, 15)}")
        level["name"] = name
    else:
        if run_info["Time spend in mission"]/60/60 < 20:
            level["name"] = write_textline("Finale 1")
        else:
            if "Curtis" not in party_info:
                level["name"] = write_textline("Finale 2")
            else:
                level["name"] = write_textline("Finale 3")

    # Bosses get their own generator
    if level["objective"] == "Defense":
        level_map = map_generator(current_mission, defense_mode=True, level_objective=level['objective'])
    elif level["objective"] == "Defeat Elite Unit":
        # Get random maps
        segment_bank = []
        for x in os.listdir(f'Maps/{current_mission}'):
            if os.path.splitext(f'Maps/{current_mission}/{x}')[1] in [".png"]:
                segment_bank.append(pg.image.load(f'Maps/{current_mission}/{x}').convert())
        level_map = get_random_element_from_list(segment_bank)
    else:
        level_map = map_generator(current_mission, level_objective=level['objective'])
    level.update({"width height": [level_map.get_width() * 32, level_map.get_height() * 32]})
    # White     (255, 255, 255)     Walls
    # Teal      (0, 255, 255)       Walls, sprite
    # Green     (0, 255, 0)         Walls Ground, alt wall sprite
    # Black     (0, 0, 0)           Ground
    # Magenta   (255, 0, 255)       Ground, Spawn Point
    # Yellow    (255, 255, 0)       Ground, Objective Zone
    # Blue      (0, 0, 255)
    # Red       (255, 0, 0)

    if mission_type != "":
        level['objective'] = mission_type

    # |Generate Map|----------------------------------------------------------------------------------------------------
    # Generate walls
    level["map"] = [pg.Rect(wall) for wall in advanced_image_to_map_geometry(level_map, colours_to_check=[
        (255, 255, 255), (0, 255, 255)])]

    # Generate pathfinding
    level["pathfinding"] = waypoint_connection_pathfinding_creator(level_map)

    # Get spawn point
    possible_spawn_points = [pg.Rect(wall) for wall in advanced_image_to_map_geometry(level_map,                                                                                      colours_to_check=[(255, 0, 255)])]
    chosen_spawn_point = possible_spawn_points[random.randint(0, len(possible_spawn_points) - 1)]
    spawn_point = [chosen_spawn_point.centerx, chosen_spawn_point.centery]

    # |Modifiers|-------------------------------------------------------------------------------------------------------
    # Skip mission
    if current_mission in []: # 6, 10
        #   Skip the mission. Can set you in debt. Everybody gets put to max health.
        #   Only happens if there is just 2 or less teammates with health over 50% and before starting mission 6 or 11.
        #   No other modifiers
        party_with_health = 0
        for party in party_info:
            if party_info[party]["Health"] > 0:
                party_with_health += 1
        add_skip = party_with_health <= 2
        for m_check in possible_levels:
            if m_check["level"]['modifiers'] == ["Skip mission"]:
                add_skip = False
                break
        if add_skip and random.random() < 0.34 + 0.33 * faction:
            # make it load a new level that's the mission status
            level_map = get_image("Maps/Mission Skip.png")
            level["map"] = [pg.Rect(wall) for wall in advanced_image_to_map_geometry(level_map, colours_to_check=[
                (255, 255, 255), (0, 255, 255)])]
            level["events"] = [
                ['Goal', {'rects': [], 'Conditions': 'trigger_check_constant'}, True, ['skip_mission']]
                ]
            # Generate pathfinding
            level["pathfinding"] = waypoint_connection_pathfinding_creator(level_map)
            # Get spawn point
            possible_spawn_points = [pg.Rect(wall) for wall in
                                     advanced_image_to_map_geometry(level_map, colours_to_check=[(255, 0, 255)])]
            chosen_spawn_point = possible_spawn_points[random.randint(0, len(possible_spawn_points) - 1)]
            spawn_point = [chosen_spawn_point.centerx, chosen_spawn_point.centery]
            level['modifiers'] = ["Skip mission"]
            point_budget = -1
            enemy_floor = -1

            mission_reward *= -0.75
    if current_mission != 15 and random.random() < 0.8 and level['modifiers'] != ["Skip mission"]:
        boss_mission = level['objective'] == "Defeat Elite Unit"
        for x in range(round((current_mission//5+1)*pg.math.clamp(random.random(), 0.44, 1))):
            modifier = random.random()
            # Lessen presence
            if "Lessen presence" not in level['modifiers'] and modifier < 0.075 and not boss_mission and "Increased presence" not in level['modifiers']:
                level['modifiers'].append("Lessen presence")
                #   Half as many enemies spawn.
                #   More likely to happen on the faction you did missions against the most
                mission_reward *= 0.5
                enemy_floor = round(enemy_floor * 0.75)
                point_budget = round(point_budget * 0.75)
                continue
            # Vehicle can deploy
            if "Vehicle can deploy" not in level['modifiers'] and modifier < 0.2  and level['objective'] not in ["Defense", "Escort"]:
                #   You can deploy the APC on a mission who doesn't require it. Only lose reward if you deploy the APC.
                level['modifiers'].append("Vehicle can deploy")
                mission_reward *= 0.9
                continue
            # Ambush Risk
            if "Ambush Risk" not in level['modifiers'] and modifier < 0.25:
                #   A big group of enemies will spawn unexpectedly.
                #   More likely with faction 2 >.
                level["events"].append(
                    ['Ambush', {"rects": [], "Conditions": 'trigger_check_timer'}, False, ['ambush'], {"Timer": 60 * (15 + random.randint(2, 5) * 0)}])
                    # ['Ambush', {"rects": [], "Conditions": 'trigger_check_timer'}, False, ['ambush'], {"Timer": 2}])
                level['modifiers'].append("Ambush Risk")
                mission_reward *= 1.2
                continue
            # Grunt party
            if "Grunt party" not in level['modifiers'] and modifier < 0.325 and not boss_mission and "Lots of Elite" not in level['modifiers']:
                #   Spawn no specialists or support and few shock troopers. You get lots of Grunts tho.
                level['modifiers'].append("Grunt party")
                mission_reward *= 1
                enemy_floor = round(enemy_floor * 1.75)
                point_budget = round(point_budget * 1.75)
                continue
            # Sandstorm
            if "Sandstorm" not in level['modifiers'] and modifier < 0.425 and current_mission < 10:
                #   Vision range is reduced.
                level['modifiers'].append("Sandstorm")
                level["events"].append(
                    ['Sandstorm', {'rects': [], 'Conditions': 'trigger_check_constant'}, False,
                     ['sandstorm'], {}])
                mission_reward *= 1.25
                continue
            # Landmines
            if "Landmines" not in level['modifiers'] and modifier < 0.475:
                #   Landmines are placed in operation zone.
                #   More likely on missions where the APC can be used. (Fortress can deploy contributes to increased rate)
                level['modifiers'].append("Landmines")
                level["events"].append(
                    ['Landmines', {"rects": [], "Conditions": 'trigger_check_mission_start'}, True,
                     ['landmines'], {}])
                mission_reward *= 1.33
                continue
            # Artillery Strikes
            if "Artillery Strike" not in level['modifiers'] and modifier < 0.575:
                #   Artillery attacks all time.
                #   More likely on faction 3 =.
                level['modifiers'].append("Artillery Strike")
                level["events"].append(
                    ['Boom boom', {'rects': [], 'Conditions': 'trigger_check_constant'}, False,
                     ['artillery_strike'], {}])
                mission_reward *= 1.5
                continue
            # Enemy armour # Cancelling it for performances
            # if "Enemy armour" not in level['modifiers'] and modifier < 0.625 and current_mission > 5 and not boss_mission:
                #   Faction's Level 5 boss spawns.
                #   The faction who owns the level 5 boss you fought can't get this modifier. Can occur after mission 10
            #     level['modifiers'].append("Enemy armour")
            #    mission_reward *= 1.75
            #     continue
            # Lots of Elite
            if "Lots of Elite" not in level['modifiers'] and modifier < 0.65 and not boss_mission and "Grunt party" not in level['modifiers']:
                #   Spawn rate of enemy elite units doubles
                level['modifiers'].append("Lots of Elite")
                mission_reward *= 2
                continue
            # Increased presence
            if "Increased presence" not in level['modifiers'] and modifier < 0.95 and not boss_mission and "Lessen presence" not in level['modifiers']:
                #   Double enemy spawns.
                level['modifiers'].append("Increased presence")
                enemy_floor = round(enemy_floor * 1.5)
                point_budget = round(point_budget * 1.5)
                mission_reward *= 2
                continue
            # Unknown Forces
            if "Unknown Forces" not in level['modifiers'] and modifier > 0.95 and not boss_mission and False:
                #   Either Curtis' party or Padraig appears.
                #   When playing  as Zoar Colonists, THR-1 replaces Curtis' party
                level['modifiers'].append("Unknown Forces")
                mission_reward *= 2
                continue
            # Boss rush
            if "Boss rush" not in level['modifiers'] and modifier > 0.95 and boss_mission and False:
                #   Fight all bosses for the stage one after the other. No heal in between
                level['modifiers'].append("Boss rush")
                mission_reward *= 4
                continue

    # |Objectives|------------------------------------------------------------------------------------------------------
    # Generate objective zones
    possible_objective_zone = [pg.Rect(wall) for wall in advanced_image_to_map_geometry(
        level_map, colours_to_check=[(255, 255, 0)])]

    default_enemy_spawns = True
    # Scrapped Intel mission type because it was too much like Capture and
    if level['modifiers'] != ["Skip mission"]:
        if level["objective"] == "Capture":
            level["events"].append(['Goal', {'rects': [], 'Conditions': 'trigger_check_constant'}, False, ['capture_zone']])
            # Find an amount of capture points
            level["free var"].update({"Cap points": []})

            how_many_points = round(current_mission*0.30) + 1
            for point_to_get in range(how_many_points):
                num = random.randint(0, len(possible_objective_zone)-1)
                rect = possible_objective_zone[num].center
                while distance_between(rect, spawn_point) < 320:
                    possible_objective_zone.pop(num)
                    num = random.randint(0, len(possible_objective_zone) - 1)
                    rect = possible_objective_zone[num].center
                    # print("Capture point too close to spawn")
                level["free var"]["Cap points"].append({"Pos": [rect[0], rect[1]], "Cap gauge": 0, "Captured": False})
                level['objective points'].append([rect[0], rect[1]])

                possible_objective_zone.pop(num)
                # "Cap points": [{"Pos": [x, y], "Cap gauge": 0, "Captured": False}]
        if level["objective"] == "Seek and Destroy":
            point_budget = round(point_budget * 0.7)
            level["events"].append(['Goal', {'rects': [], 'Conditions': 'trigger_check_zero_enemies'}, True, ['win']])
        if level["objective"] == "Eliminate Commander":
            # Double point budget
            point_budget = round(point_budget * 1.3)
            # Get commander spawn zone
            commander_spawn = get_random_element_from_list(possible_objective_zone)
            control_dist = 0
            for potential_spawn_point in possible_objective_zone:
                test_dist = distance_between(spawn_point, [potential_spawn_point.centerx, potential_spawn_point.centery])
                if test_dist > control_dist:
                    control_dist = test_dist
                    commander_spawn = potential_spawn_point
            # Add the commander
            enemy_spawns.append({"Pos": [commander_spawn.centerx, commander_spawn.centery],
                                 "Type": ENEMY_TYPE_TO_FACTION_UNIT[faction]["VIP"]})
            level['objective points'].append([commander_spawn.centerx, commander_spawn.centery])
            # Add security detail, use generate_enemy_squad
            squad, budget = enemy_squad_generator(current_mission, faction)
            for e in squad:
                enemy_spawns.append({"Pos": [commander_spawn.centerx, commander_spawn.centery], "Type": e})
            # Add event to check for commander death
            level["events"].append(['Goal', {'rects': [], 'Conditions': 'trigger_check_zero_vip'}, True, ['win']])
        if level["objective"] == "Defense":
            default_enemy_spawns = False

            wave_count = [2, 2, 3, 3, 0,
                          4, 4, 5, 5, 0,
                          6, 6, 7, 7, 0][current_mission-1]

            level["events"].append(
                ['Goal', {'rects': [], 'Conditions': 'trigger_check_under_specified_amount_enemies'}, False,
                 ['defense_mission'], {"Specified amount": 3}])
            level["free var"].update({"Defense info": {"Current wave": 0, "Wave count": wave_count}})
        if level["objective"] == "Escort":
            # Generate a path to follow
            escort_destination = get_random_element_from_list(possible_objective_zone)
            control_dist = 0
            for potential_spawn_point in possible_objective_zone:
                test_dist = distance_between(spawn_point, [potential_spawn_point.centerx, potential_spawn_point.centery])
                if test_dist > control_dist:
                    control_dist = test_dist
                    escort_destination = potential_spawn_point
            # Add the commander # 'points': new_bullshit, 'connections'
            escort_destination = [escort_destination.centerx, escort_destination.centery]
            points = level["pathfinding"]["points"]
            connections = level["pathfinding"]["connections"]
            # Find waypoints
            current_location = '0'
            control_dist = BIG_INT
            for p in points:
                test_dist = distance_between(points[p], spawn_point)
                if test_dist < control_dist:
                    current_location = p
                    control_dist = test_dist

            # Get the target destination
            end_point = '0'
            control_dist = BIG_INT
            for p in points:
                if p == current_location:
                    continue
                test_dist = distance_between(points[p], escort_destination)
                if test_dist < control_dist:
                    end_point = p
                    control_dist = test_dist
            path = hub_npc_path_making_escort(current_location, end_point, connections, points, [current_location])
            level['free var']['APC path'] = [points[p] for p in path]
            # Add win condition
            level["events"].append(['Goal', {'rects': [], 'Conditions': 'trigger_check_apc_reached_goal'}, True, ['win']])
            pass
        if level["objective"] == "Defeat Elite Unit":
            # Get commander spawn zone
            commander_spawn = get_random_element_from_list(possible_objective_zone)
            control_dist = 0
            for potential_spawn_point in [pg.Rect(wall) for wall in advanced_image_to_map_geometry(
            level_map, colours_to_check=[(255, 128, 0)])]:
                test_dist = distance_between(spawn_point, [potential_spawn_point.centerx, potential_spawn_point.centery])
                if test_dist > control_dist:
                    control_dist = test_dist
                    commander_spawn = potential_spawn_point

            # Add the commander
            if current_mission != 15:
                boss_to_fight = "Boss 1"
                if current_mission == 10:
                    boss_to_fight = "Boss 2"
                enemy_spawns.append({"Pos": [commander_spawn.centerx, commander_spawn.centery],
                                     "Type": ENEMY_TYPE_TO_FACTION_UNIT[faction][boss_to_fight]})
            else:
                # Get mission name
                if level['name'] == write_textline("Finale 1"): # Load Rigel
                    enemy_spawns.append({"Pos": [commander_spawn.centerx, commander_spawn.centery], "Type": "Rigel"})
                    level['faction'] = 3
                if level['name'] == write_textline("Finale 2"): # Load Curtis
                    enemy_spawns.append({"Pos": [commander_spawn.centerx, commander_spawn.centery], "Type": "Curtis"})
                    level['faction'] = 4
                if level['name'] == write_textline("Finale 3"): # Load THR-1 team
                    for x in ["Lord", "Emperor", "Wizard", "Jester"]:
                        enemy_spawns.append({"Pos": [commander_spawn.centerx, commander_spawn.centery], "Type": x})
                    level['faction'] = 5

            level['objective points'].append([commander_spawn.centerx, commander_spawn.centery])
            # Add event to check for commander death
            level["events"].append(['Goal', {'rects': [], 'Conditions': 'trigger_check_zero_boss'}, True, ['win']])
            default_enemy_spawns = False
            # Set boss spawn
    else:
        default_enemy_spawns = False
    # |Generate enemy spawns|-------------------------------------------------------------------------------------------
    if default_enemy_spawns:
        point_budget_total = point_budget
        # Get potential enemy spawns
        potential_enemy_spawn_zones = [pg.Rect(wall) for wall in advanced_image_to_map_geometry(
            level_map, colours_to_check=[(0, 0, 0), (255, 0, 255)])]

        # Get info to spawn enemies
        valid_potential_enemy_spawn_zones = []
        for x in potential_enemy_spawn_zones:
            if distance_between(x.center, spawn_point) < 256:
                continue
            valid_potential_enemy_spawn_zones.append(x)

        valid_enemy_spawn_zones = []
        for x in valid_potential_enemy_spawn_zones:
            allow = True
            for y in valid_enemy_spawn_zones:
                if distance_between(x.center, y) < 256 * random.random():
                    allow = False
                    break
            if allow:
                valid_enemy_spawn_zones.append([x.centerx, x.centery])

        # if "Enemy armour" in level['modifiers']:
        #     enemy_spawns.append({"Pos": get_random_element_from_list(valid_enemy_spawn_zones),
        #                          "Type": ENEMY_TYPE_TO_FACTION_UNIT[faction]["Boss 1"]})
        squad, budget = enemy_squad_generator(current_mission, faction, modified_point_budget=point_budget)
        for e in squad:
            unit_type = e
            if "Lots of Elite" in level['modifiers'] and random.random() < 0.4:
                unit_type = ENEMY_TYPE_TO_FACTION_UNIT[faction]["Elite"]
            if "Grunt party" in level['modifiers'] and \
                (unit_type in [
                    ENEMY_TYPE_TO_FACTION_UNIT[faction]["Support"],
                    ENEMY_TYPE_TO_FACTION_UNIT[faction]["Specialist 1"],
                    ENEMY_TYPE_TO_FACTION_UNIT[faction]["Specialist 2"]
                ] or random.random() < 0.33):
                unit_type = ENEMY_TYPE_TO_FACTION_UNIT[faction]["Grunt"]
            enemy_spawns.append({"Pos": get_random_element_from_list(valid_enemy_spawn_zones), "Type": unit_type})

        while len(enemy_spawns) < enemy_floor:
            unit_type = "Grunt"
            if "Lots of Elite" in level['modifiers'] and random.random() < 0.4:
                unit_type = "Elite"
            enemy_spawns.append({"Pos": get_random_element_from_list(valid_enemy_spawn_zones),
                                 "Type": ENEMY_TYPE_TO_FACTION_UNIT[faction][unit_type]})
        #

        if 5 < current_mission < 10 and random.random() > 0.9:
            level["events"].append(
                ['Secret mission trigger', {'rects': [], 'Conditions': 'trigger_check_constant'}, False, []])
    # 	Add items to mission ?

    # |Generate render|-------------------------------------------------------------------------------------------------
    # Divide map in segment and generate zones for render
    width, height = level_map.get_width() - 2, level_map.get_height() - 2
    segment_size = 16
    convert_wall = lambda wall, p : pg.Rect(wall[0] + p[0] * 32 - 32, wall[1] + p[1] * 32 - 32, wall[2], wall[3])

    for y in range(height // segment_size):
        for x in range(width // segment_size):#
            pos = [(x * segment_size) + 1,
                   (y * segment_size) + 1]

            segment = pg.surface.Surface((segment_size + 2, segment_size + 2))
            segment.fill((255, 0, 128))
            segment.blit(level_map.subsurface(pos[0], pos[1], segment_size, segment_size), (1, 1))
            # pg.image.save(segment, f"!Dev stuff/!!!{x}-{y}.png")

            level["rendering"]["Segments"].append({
                'Rect': pg.Rect(pos[0] * 32, pos[1] * 32, segment_size * 32, segment_size * 32),
                'Walls': [
                    convert_wall(wall, pos) for wall in advanced_image_to_map_geometry(segment, colours_to_check=[(0, 255, 255)])],
                'Floor': [convert_wall(wall, pos) for wall in advanced_image_to_map_geometry(segment, colours_to_check=[(0, 0, 0), (255, 0, 255), (255, 255, 0), (255, 128, 0)])]
                                                   })
    # Add noise

    # |Compile extra info|----------------------------------------------------------------------------------------------
    extra_info = {"Spawn": spawn_point, "Enemy spawns": enemy_spawns, "Mission Reward": round(mission_reward), "Type": level["objective"], "Current mission": current_mission}

    return level, extra_info


def versus_level_generator(possible_levels, party_info, map_name, current_mission=1, mission_type="", faction=0):
    # point_budget = int(current_mission * (current_mission*0.25) + 8)
    point_budget = int(math.exp2(current_mission*0.5)+ 14)
    enemy_floor = current_mission * 5 + 5
    # point_budget = 0
    # print(point_budget)
    # enemy_cap = round(point_budget * (2.25 - random.random() * 0.5))
    elite_limit = round(point_budget / 5 * 0.25)
    enemy_spawns = []
    level = {
        'name': map_name.split('.')[0].split('VS_')[1], 'mission number': current_mission, 'faction': faction,
        'objective': "Versus",

        # APC missions (Escort, Defense)
        'map': [],
        'events': [
            # ['Mission start', {'rects': [], 'Conditions': 'trigger_check_mission_start'}, True, ['mission_start']]
            ['Every frame', {'rects': [], 'Conditions': 'trigger_check_constant'}, False, ['versus_every_frame']]
        ],
        'level_finished': False,
        'pathfinding': None, # {
            # 'points': {},  # "<id>": [<x>, <y>]
            # 'connections': {}  # "<id>": [<id of connected points>]
        # },
        'rendering': {
            "Segments": [
            # {
            #   'Rect': pg.Rect,
            #   'Walls': [],
            #   'Floor': [],
            # }
            ],
            "Tile set": {"Wall": TILE_SET_IRON_MINES_WALL, "Floor": TILE_SET_IRON_MINES_FLOOR}
        },
        'objective points': [],
        'modifiers': [],
        'free var': {}
    }
    level["rendering"]["Tile set"] = {"Wall": TILE_SET_INDUSTRIAL_WALL, "Floor": TILE_SET_INDUSTRIAL_FLOOR}

    # Bosses get their own generator
    level_map = pg.image.load(f'Maps/Versus mode/{map_name}').convert()
    level.update({"width height": [level_map.get_width() * 32, level_map.get_height() * 32]})
    # White     (255, 255, 255)     Walls
    # Teal      (0, 255, 255)       Walls, sprite
    # Green     (0, 255, 0)         Walls Ground, alt wall sprite
    # Black     (0, 0, 0)           Ground
    # Magenta   (255, 0, 255)       Ground, Spawn Point
    # Yellow    (255, 255, 0)       Ground, Objective Zone
    # Blue      (0, 0, 255)
    # Red       (255, 0, 0)

    # |Generate Map|----------------------------------------------------------------------------------------------------
    # Generate walls
    level["map"] = [pg.Rect(wall) for wall in advanced_image_to_map_geometry(level_map, colours_to_check=[
        (255, 255, 255), (0, 255, 255)])]

    # Generate pathfinding
    level["pathfinding"] = waypoint_connection_pathfinding_creator(level_map)

    # Get spawn point
    possible_spawn_points = [[pg.Rect(wall).centerx, pg.Rect(wall).centery] for wall in advanced_image_to_map_geometry(level_map, colours_to_check=[(255, 0, 255)])]

    # |Modifiers|-------------------------------------------------------------------------------------------------------

    # |Objectives|------------------------------------------------------------------------------------------------------
    # Generate objective zones
    possible_objective_zone = [pg.Rect(wall) for wall in advanced_image_to_map_geometry(
        level_map, colours_to_check=[(255, 255, 0)])]


    # |Generate render|-------------------------------------------------------------------------------------------------
    # Divide map in segment and generate zones for render
    width, height = level_map.get_width() - 2, level_map.get_height() - 2
    segment_size = 8
    convert_wall = lambda wall, p : pg.Rect(wall[0] + p[0] * 32 - 32, wall[1] + p[1] * 32 - 32, wall[2], wall[3])

    for y in range(height // segment_size):
        for x in range(width // segment_size):#
            pos = [(x * segment_size) + 1,
                   (y * segment_size) + 1]

            segment = pg.surface.Surface((segment_size + 2, segment_size + 2))
            segment.fill((255, 0, 128))
            segment.blit(level_map.subsurface(pos[0], pos[1], segment_size, segment_size), (1, 1))
            # pg.image.save(segment, f"!Dev stuff/!!!{x}-{y}.png")

            level["rendering"]["Segments"].append({
                'Rect': pg.Rect(pos[0] * 32, pos[1] * 32, segment_size * 32, segment_size * 32),
                'Walls': [
                    convert_wall(wall, pos) for wall in advanced_image_to_map_geometry(segment, colours_to_check=[(0, 255, 255)])],
                'Floor': [convert_wall(wall, pos) for wall in advanced_image_to_map_geometry(segment, colours_to_check=[(0, 0, 0), (255, 0, 255), (255, 255, 0), (255, 128, 0)])]
                                                   })
    # Add noise

    # |Compile extra info|----------------------------------------------------------------------------------------------
    extra_info = {"Spawn": possible_spawn_points, "Enemy spawns": enemy_spawns, "Mission Reward": round(0), "Type": level["objective"], "Current mission": current_mission}

    return level, extra_info


UNLOCK_POPUP_POS = [50, 150]
UNLOCK_POPUP_WIDTH = 530

def enemy_entry_unlock(enemy_type, faction, save_data, WIN, CLOCK):
    enemy_entry = ENEMY_TYPE_TO_FACTION_UNIT[faction][enemy_type]
    if enemy_entry not in save_data["Databank entries unlocked"]:
        save_data["Databank entries unlocked"].append(enemy_entry)
        confirmation_popup(
            WIN, CLOCK, UNLOCK_POPUP_POS,
            [{"Name": "Continue", "Value": "No", "On select": "Return", "Render func": "Text only"}],
            text=f"Entry '{enemy_entry}' added to Databank in '{'Root\Enemies' + ["\Asset Protecting & Collection Dept.",
                                                                                  "\Burning Winds Band",
                                                                                   "\C8 Mercenary Army"][faction]}'", popup_width=UNLOCK_POPUP_WIDTH)
        if enemy_type in ["Boss 1", "Boss 2", "True Final Boss", "Alt Zoar Final boss", "Alt THR-1 Final boss"]:
            return
        gun = {
            "Manager": "Laser Carbine",
            "Body Guard": "Laser Rifle",
            "Heavy Sniper": "Heavy Laser",
            "Radar Operator": "Radar",
            "Missile Operator": "Missile Pod",
            "Marksman": "Marker Laser",
            "Enforcer": "ARWS",
            "Sculptor": "Plasma Spray",
            "Skirmisher": "Plasma Rifle",
            "BoomStick": "Laser Shotgun",
            "Smoker": "Smoke Dispenser",
            "Snare": "Desert Shotgun",
            "Crusher": "Gun Hammer",
            "Assassin": "Pile Bunker",
            "Infantry": "Combat Rifle",
            "Flamer": "Flamethrower",
            "Spotter": "Binoculars",
            "Artilleryman": "Artillery Radio",
            "Grenadier": "Napalm Grenade Launcher",
            "Bulwark": "Bulwark Minigun",
            "Commanding Officer": "Combat Rifle",
            "Super Bulwark": "Bulwark Minigun",
        }[enemy_entry]
        weapon_entry_unlock(gun, save_data, WIN, CLOCK)



def boss_entry_unlock(boss, faction, save_data, WIN, CLOCK):
    if boss not in save_data["Databank entries unlocked"]:
        save_data["Databank entries unlocked"].append(boss)
        confirmation_popup(
            WIN, CLOCK, UNLOCK_POPUP_POS,
            [{"Name": "Continue", "Value": "No", "On select": "Return", "Render func": "Text only"}],
            text=f"Entry '{boss}' added to Databank in '{'Root\Enemies' + ["\Asset Protecting & Collection Dept.",
                                                                                  "\Burning Winds Band",
                                                                                   "\C8 Mercenary Army",
                                                                                  "\Misc."][faction]}'", popup_width=UNLOCK_POPUP_WIDTH)


def weapon_entry_unlock(gun, save_data, WIN, CLOCK):
    if gun not in save_data["Databank entries unlocked"]:
        entries = {
		"\Handgun": ["Big Iron", "War and Peace"],
		"\Rifle": ["St-Maurice Youth Model", "St-Maurice", "St-Laurent Gen 1", "Type 47 Rifle", "Cowboy's Repeater", "Mark's Rifle", "Type 30 Rifle", "Vivianne's Rifle", "Combat Rifle"],
		"\Sub Machine Gun": ["Type 41 SMG"],
		"\Shotgun": ["Jeanne's Family Shotgun", "Type 23 Shotgun", "Standard Shotgun", "Vivianne's Shotgun", "Desert Shotgun"],
		"\Energy": ["Custom Mk18 Laser cutter", "Laser Carbine", "Laser Rifle", "Heavy Laser", "Marker Laser", "Plasma Spray", "Plasma Rifle", "Laser Shotgun"],
		"\Melee": ["Oversized stun baton", "Corrine's Hands", "Chain Axe", "Hook Swords", "Hunk of Steel", "Vivianne's Leg", "Gun Hammer", "Pile Bunker"],
		"\Combo": ["GunBlade", "Gun and Ballistic Knife", "Lawrence's Cutlass & Flintlock", "Captain's Axe & Blunderbuss"],
		"\Heavy": ["Saloum Mk-2", "GMG-04B", "Fortress Machine Gun", "Musket .360", "Buggy Gun", "Missile Pod", "ARWS", "Flamethrower", "Napalm Grenade Launcher", "Bulwark Minigun"],
		"\Gear": ["Crippled Laddie FCS Radio", "Mk16 Flare Mortar", "Epicurean Medic Rifle", "Nihilist Stretcher", "Stoic Shield generator", "C4", "Radar", "Smoke Dispenser", "Binoculars", "Artillery Radio"]
	    }
        entry_type = "\Handgun"
        for weapon_type in entries:
            if gun in entries[weapon_type]:
                entry_type = weapon_type
        save_data["Databank entries unlocked"].append(gun)
        confirmation_popup(
            WIN, CLOCK, UNLOCK_POPUP_POS,
            [{"Name": "Continue", "Value": "No", "On select": "Return", "Render func": "Text only"}],
            text=f"Entry '{gun}' added to Databank in '{'Root\Weapon'+entry_type}'", popup_width=UNLOCK_POPUP_WIDTH)
        manufacturer = {
            "Old West Firearms & Replicas": ["Big Iron", "Cowboy's Repeater"],
            "Toolkit Manufacturing": ["Crippled Laddie FCS Radio", "Mk16 Flare Mortar", "C4", "Custom Mk18 Laser cutter"]}
        unlocked_manufacturer = False
        for weapon_type in manufacturer:
            if gun in manufacturer[weapon_type]:
                unlocked_manufacturer = weapon_type
        if unlocked_manufacturer:
            if unlocked_manufacturer not in save_data["Databank entries unlocked"]:
                save_data["Databank entries unlocked"].append(unlocked_manufacturer)
                confirmation_popup(
                    WIN, CLOCK, UNLOCK_POPUP_POS,
                    [{"Name": "Continue", "Value": "No", "On select": "Return", "Render func": "Text only"}],
                    text=f"Entry '{unlocked_manufacturer}' added to Databank in 'Root\Organizations\Weapon Manufacturer'", popup_width=UNLOCK_POPUP_WIDTH)


import Particles    # Doing this so I can get all the stuff I need from fun
