import pygame as pg
import random
import math
import sys


import Fun
import Bullets
import Skills
import Particles
import Weapons
import MechRenderer
import Items
import Event


from Fun import none, enemy_entry_unlock


class Entity(Fun.Adam):
    __slots__=[
        # Targeting
        'stealth_counter', 'stealth_mod', 'target', 'targeting_angle', 'targeting_range', 'wall_hack',

        # Agro
        'agro', 'agro_decrease_rate', 'did_agro_raise',

        # Admin
        'name', 'faction', 'owner', 'team', 'ai_state', 'ai_weapon_range_mod', 'ai_type', 'is_target', 'is_ally',
        'is_boss', 'is_player', 'is_targeted', 'is_targeting', 'og_info', 'time', 'status', 'no_shoot_state',

        # Defense
        'damage_taken', 'armour', 'armour_break', 'max_armour', 'max_health', 'resistances', 'health',

        # Offense
        'crit', 'bullets_shot', 'reloading', 'shooting', 'shot_allowed', 'weapon', 'aim_angle', 'angle',

        # Func
        'func_act', 'func_draw', 'func_input', 'on_death',

        # Draw n shit
        'force_draw', 'sprite_height', 'sprites', 'draw_aim_line', 'draw_angle', 'draw_rotated_dist', 'draw_targeting_range',
        'driving', 'weapon_draw_dist', 'z', 'cutscene_mode', 'animation_counter',

        # Input
        'control', 'controller_angle', 'controller_control', 'input', 'input_mode', 'mouse_control', 'mouse_pos',

        'free_var', 'order_builder', 'skills', 'sound_mod', 'thiccness', 'upgrades',

        # Movement
        'direction_angle', 'friction', 'pathfinding_old_positions', 'pos','speed', 'running', 'vel', 'vel_max',
        'walking', 'standing_still', 'collision_box',
        'dash_allowed', 'dash_charge_time', 'dash_cooldown', 'dash_iframes', 'dash_speed',

        # Advanced Movement
        'stamina', 'max_stamina', 'stamina_regen_rate', 'stamina_recovery_timer', 'stamina_recovery_time',
        'sprint_speed', 'dash_cost', 'roll_time', 'roll_timer', "sprint_cost", "still_regen", "super_roll_vel_mod"
    ]
    def __init__(self, info, team="Players", pos=[0, 0], start_angle=0, check_halloween=True):
        Fun.Adam.__init__(self)
        info = info.copy()
        self.og_info = info.copy()
        self.name = info["name"]
        self.team = team
        self.is_ally = False
        self.is_player = False
        self.is_boss = False
        self.crit = False
        self.owner = False
        self.ai_type = "We balling in here"
        if "type" in info:
            self.ai_type = info["type"]
        self.faction = "Factionless"
        if 'faction' in info:
            self.faction = info["faction"]
        self.ai_weapon_range_mod = 1
        if 'weapon range mod' in info:
            self.ai_weapon_range_mod = info["weapon range mod"]

        # |Health and armour|-------------------------------------------------------------------------------------------
        self.max_health = info["health"]
        self.health = self.max_health
        self.max_armour = info["armour"]
        self.armour = info["armour"]
        self.resistances = info["damage resistances"].copy()
        self.damage_taken = False
        self.armour_break = False

        # |Animation|---------------------------------------------------------------------------------------------------
        self.sprites = False
        if "sprites" in info:
            self.sprites = info["sprites"]
        if type(self.sprites) == str:
            if check_halloween:
                if Fun.SPOOKY_DAY and self.name in player_repertory:
                    self.sprites = self.sprites.split(".")[0]
                    self.sprites += " - Halloween.png"
            sprite = Fun.get_image(self.sprites)
            print()
            self.sprite_height = 32
            if "Sprite Height" in info:
                self.sprite_height = info["Sprite Height"]
            self.sprites = Fun.desheetator(sprite, thiccness=self.sprite_height)
            if "Outline" in info["free var"]:
                colour = info["free var"]["Outline"]
                if "Is VIP" in info["free var"]:
                    colour = Fun.AMBER
                for count_2, d in enumerate(self.sprites):
                    for count, s in enumerate(d["Walk"]):
                        self.sprites[count_2]["Walk"][count] = Fun.get_outline(s, colour=colour)

        self.draw_aim_line = False
        self.animation_counter = {"Standing": 0,  # Should stay at 0
                                  "Walk": 0}
        self.force_draw = False
        # These are not handled by the player
        self.weapon_draw_dist, self.draw_angle, self.draw_rotated_dist, self.weapon_draw_angle = 0, 0, 0, 0
        self.draw_targeting_range = 0

        # |Position|----------------------------------------------------------------------------------------------------
        self.pos = pos
        self.thiccness = info["thickness"]
        self.collision_box = pg.Rect(self.pos[0] - self.thiccness // 2, self.pos[1] - self.thiccness // 2,
                                     self.thiccness, self.thiccness)
        self.mouse_pos = [0, 0]
        self.angle = start_angle
        self.controller_angle = start_angle
        self.aim_angle = self.angle

        self.pathfinding_old_positions = []
        # |Movement|----------------------------------------------------------------------------------------------------
        self.standing_still = True
        self.walking = False
        self.running = False
        self.dash_allowed = True

        self.vel = [0, 0]
        self.vel_max = info["vel max"]
        self.speed = info["speed"]
        self.friction = info["friction"]
        self.direction_angle = Fun.angle_between([self.pos[0] + self.vel[0], self.pos[1] + self.vel[1]], self.pos)

        self.dash_cooldown = 0
        self.dash_speed = 0
        self.dash_iframes = 0
        self.dash_charge_time = 0
        if "dash" in info:
            self.dash_speed = info["dash"]["speed"]
            self.dash_iframes = info["dash"]["i-frames"]
            self.dash_charge_time = info["dash"]["charge"]

        # Advanced movement stats
        self.stamina = 0
        self.max_stamina = 100
        self.stamina_recovery_time = 0
        self.roll_time = 0

        self.stamina_regen_rate = 0.5       # Rate at which stamina is regenerated while moving
        self.still_regen = 0.7              # Rate at which stamina is regenerated while standing still
        self.stamina_recovery_timer = 90    # Delay before stamina can be used again after it was all spent

        self.sprint_speed = 1.5             # Speed of your sprint
        self.sprint_cost = 0.1              # Cost as a percent of the max stamina to sprint

        # dash_speed                          Speed of a dash
        # dash_iframes                        How many invulnerability frames gained during a dash
        # dash_charge_time                    Cooldown between dashes
        self.dash_cost = 0.33               # Cost as a percent of the max stamina to dash

        self.roll_timer = 30                # Delay before the player can move again after rolling
        self.roll_inv_mod = 0               # Does nothing
        self.roll_vel_mod = 1               # Increases or decreases a roll's speed
        self.super_roll_vel_mod = 1.4       # Increases or decreases a super roll's speed. Usually faster.
        self.roll_speed_cost = 1.45         # How fast you must be going to be allowed to roll

        if "advanced movement" in info:
            pass
            #

        # |Inputs|------------------------------------------------------------------------------------------------------
        self.control = Fun.PseudoPlayer().control
        self.mouse_control = Fun.get_from_json("Key binds.json", "Mouse")
        self.controller_control = Fun.get_from_json("Controller binds.json", "Everything")

        self.input = Fun.get_default_inputs()
        self.input_mode = "Keyboard"
        if "Input mode" in info:
            self.input_mode = "Controller"

        # |Weapons|-----------------------------------------------------------------------------------------------------
        self.weapon = info["weapon"]    # Make it use a string to get the weapon
        if type(self.weapon) == str:
            self.weapon = Weapons.BasicWeapon(Weapons.weapon_repertory[self.weapon])

        self.no_shoot_state = 60
        self.shot_allowed = True
        self.reloading = False
        self.shooting = False

        # |Functions|---------------------------------------------------------------------------------------------------
        self.func_input = info["func input"]
        if type(self.func_input) == str:
            try:
                self.func_input = getattr(sys.modules[__name__], self.func_input)
            except AttributeError:
                self.func_input = getattr(Entity_Input_Funcs, self.func_input)

        self.func_act = info["func act"]
        if type(self.func_act) == str:
            try:
                self.func_act = getattr(sys.modules[__name__], self.func_act)
            except AttributeError:
                self.func_act = getattr(Entity_Act_Funcs, self.func_act)

        self.func_draw = info["func draw"]
        if type(self.func_draw) == str:
            try:
                self.func_draw = getattr(sys.modules[__name__], self.func_draw)
            except AttributeError:
                self.func_draw = getattr(Entity_Draw_Funcs, self.func_draw)

        self.on_death = info["on death"]
        if type(self.on_death) == str:
            try:
                self.on_death = getattr(sys.modules[__name__], self.on_death)
            except AttributeError:
                self.on_death = getattr(Entity_On_Death, self.on_death)


        # |Targeting|---------------------------------------------------------------------------------------------------
        self.ai_state = "Follow"    # For allies, Follow, Hold, Attack, Freely
        self.targeting_range = info["targeting range"]
        self.stealth_mod = 1        # 0 - 1
        if "stealth mod" in info:
            self.stealth_mod = info["stealth mod"]
        self.stealth_counter = 1    # 0 - 1
        if "stealth counter" in info:
            self.stealth_counter = info["stealth counter"]
        self.is_targeting = False  # Track if the enemy has a target
        self.is_targeted = False  # Track if the enemy has a target
        self.is_target = False
        self.targeting_angle = info["targeting angle"]
        self.wall_hack = info["wall hack"]  # This allows enemies to see you though walls
        self.target = []
        self.agro = 0
        self.did_agro_raise = 0
        self.agro_decrease_rate = 1
        self.order_builder = {
            "Current order": False,
            "Cooldown": 0,
            "Time limit": 120,
            "Allow input": True
        }

        # |Skills|------------------------------------------------------------------------------------------------------
        self.skills = []
        if "skills" in info:
            self.skills = info["skills"].copy()
        for count, s in enumerate(self.skills):
            skill_dict = s
            if type(skill_dict) == str:
                skill_dict = Skills.skill_repertory[skill_dict].copy()
            self.skills[count] = Skills.Skill(skill_dict)

        # |Misc|--------------------------------------------------------------------------------------------------------
        self.status = Fun.STATUS_EFFECT_ZERO.copy()
        self.time = 0
        self.cutscene_mode = []
        self.sound_mod = 1
        self.driving = 0
        if "driving" in info:
            self.driving = info["driving"]
        self.free_var = info["free var"].copy()

        self.bullets_shot = []
        self.upgrades = []
        # ||-

    def get_input(self, entities, level):
        self.draw_aim_line = False
        self.time += 1
        # Check for input form the Keyboard
        self.input = Fun.get_default_inputs()

        self.func_input(self, entities, level)

        # Cinematic mode
        Fun.cutscene_mode(self, entities, level)
        # self.angle = Fun.angle_between(self.mouse_pos, self.pos)

    def act(self, entities, level):
        self.z = self.pos[1]

        # Reset variables
        # self.shooting = False
        self.crit = False
        self.bullets_shot = []

        self.func_act(self, entities, level)

        for upgrade in self.upgrades:
            upgrade.act(entities, level)

        agro_system(self)
        self.is_targeted = False

    def shoot_bullet(self, entities, level, guarantee_crit=False):

        # Fun.play_sound(self.weapon.gunshot_sound, "SFX", modified_volume=self.weapon.volume)
        self.shooting = True
        entities["sounds"].append(Fun.Sound(
            Fun.move_with_vel_angle(self.pos, 20, self.aim_angle),
            Fun.sounds_dict[self.weapon.gunshot_sound]["Sound"].get_length() * 60,
            (500 * self.weapon.volume + 50) * self.sound_mod,
            source=self.team, strength=2))
        self.agro += self.weapon.agro_gain
        if self.agro > 100:
            self.agro = 100
        self.did_agro_raise = 60 * 3
        # Spawn the bullets
        for b in range(Fun.bullet_x3_manager(self.weapon.bullets_per_shot, self.status["Bullet x3"])):
            Bullets.spawn_bullet(self, entities, self.weapon.bullet_type, Fun.move_with_vel_angle(self.pos, 20, self.aim_angle),
                                 self.aim_angle + random.uniform(-self.weapon.accuracy,
                                                                 self.weapon.accuracy) + random.uniform(
                                     -self.weapon.spread, self.weapon.spread), self.weapon.bullet_info)

            # Critical shots
            Fun.crit_manager(self, entities, self.weapon, guarantee_crit)
            # |Status effects management|-------------------------------------------------------------------
            Fun.bullet_status_manager(self, entities)
        sound = self.weapon.gunshot_sound
        if self.crit:
            sound = "Crit Shoot"
            # Fun.play_sound("Crit Shoot", "SFX", modified_volume=self.weapon.volume)
        Fun.play_sound(sound, "SFX", modified_volume=self.weapon.volume)
        # else:
        #     Fun.play_sound(self.weapon.gunshot_sound, "SFX", modified_volume=self.weapon.volume)

        Fun.after_shooting_manager(self, self.weapon)
        #

    def draw(self, screen, scrolling, players, level):
        if self in players or self.status["Visible"] > 0 or self.force_draw:
            self.draw_actual(screen, scrolling)
            return
        # Skip hidden enemies
        if self.status["Stealth"] > 0: return
        # Only draw enemies who can be seen by a player
        for ee in players:
            # Get stealth range modifier
            detection_modifier = pg.math.clamp(self.stealth_mod * ee.stealth_counter, -20, 1)
            if not (Fun.distance_between(self.pos, ee.pos) < ee.targeting_range // 10 * detection_modifier or
                    Fun.check_point_in_cone(
                        ee.targeting_range * detection_modifier, ee.pos[0], ee.pos[1],
                        self.pos[0], self.pos[1],
                        ee.angle, ee.targeting_angle)):
                continue
            if Fun.wall_between(self.pos, ee.pos, level): continue
            self.draw_actual(screen, scrolling)
            break

    def draw_actual(self, screen, scrolling):
        self.func_draw(self, screen, scrolling)
        self.draw_bottom_health_bar(screen, scrolling)

    def draw_bottom_health_bar(self, surface_to_draw, round_scrolling):
        x_pos = self.pos[0] - 16 + round_scrolling[0]
        y_pos = (self.pos[1] + 10) + self.thiccness // 2 + round_scrolling[1]

        width = 32
        health_height = 4
        armour_height = 2

        # Draws the health bar
        pg.draw.rect(surface_to_draw, Fun.RED, (x_pos, y_pos, width * (self.health / self.max_health), health_height))
        try:
            pg.draw.rect(surface_to_draw, Fun.GREEN, (x_pos, y_pos, width * (self.armour / self.max_armour), armour_height))
        except ZeroDivisionError:
            pass
        for count, skill in enumerate(self.skills):
            val = pg.math.clamp(255 * skill.recharge / skill.recharge_max, 0, 255)
            mod = 0
            if skill.active:
                mod = val
            pg.draw.rect(surface_to_draw, (mod, mod, val),
                         (x_pos + 16 * count, y_pos+health_height, 16, 2))
        if self.status["Stunned"] > 0:
            sprite = Fun.SPRITE_STUNNED[(self.status["Stunned"] // 6) % 2]
            surface_to_draw.blit(sprite, [self.pos[0] + round_scrolling[0] - sprite.get_width() / 2,
                                          self.pos[1] - 15 + round_scrolling[1]])

    def death(self, entities, level, scrolling_target_entities):
        self.on_death(self, entities, level)
        if (self.team != "Players" or self.team in ["Player 0", "Player 1", "Player 2", "Player 3", "Player 4"]) or self.health > 0:
            return
        for count, p in enumerate(scrolling_target_entities):
            if p == self:
                scrolling_target_entities.pop(count)
                return

    def draw_player(self, scrolling, WIN, player_direction):
        # Use this as a base for the animation function for the rest of the entities
        # Get the action (walk, dash)
        frame_to_get = 0
        action_type = "Walk"
        # Make the counters go up
        for counter in self.animation_counter:
            if action_type == counter:
                self.animation_counter[counter] += 1
            else:
                self.animation_counter[counter] = 0
        # Sliding need a special case to handle its animation
        if not self.standing_still:
            # print(player_direction)
            if len(self.sprites[player_direction][action_type]) > 1:
                frame_to_get = self.animation_counter[action_type] // 7 % (
                        len(self.sprites[player_direction][action_type]) - 1) + 1

        # Draws the player
        sprite_drawn = self.sprites[player_direction][action_type][frame_to_get]
        WIN.blit(sprite_drawn, (self.pos[0] - self.sprite_height // 2 + scrolling[0], self.pos[1] - self.sprite_height // 2 + scrolling[1]))

    def draw_player_rotate(self, scrolling, WIN, player_direction, rotation):
        # Use this as a base for the animation function for the rest of the entities
        # Get the action (walk, dash)
        frame_to_get = 0
        action_type = "Walk"
        # Make the counters go up
        for counter in self.animation_counter:
            if action_type == counter:
                self.animation_counter[counter] += 1
            else:
                self.animation_counter[counter] = 0
        # Sliding need a special case to handle its animation
        if not self.standing_still:
            # print(player_direction)
            if len(self.sprites[player_direction][action_type]) > 1:
                frame_to_get = self.animation_counter[action_type] // 7 % (
                        len(self.sprites[player_direction][action_type]) - 1) + 1

        # Draws the player
        sprite_drawn = self.sprites[player_direction][action_type][frame_to_get]
        Fun.blitRotate(WIN, sprite_drawn,
                       [self.pos[0] + scrolling[0],
                        self.pos[1] + scrolling[1]],
                       [
                           self.sprite_height // 2,
                           self.sprite_height // 2
                       ],
                       rotation)
    #


# |Utility|-------------------------------------------------------------------------------------------------------------
def dodging(self, entities, bullets, search_range=100, bullet_minimum=2, random_chance=(3, 0),
            dodge_angles=(60, 120), dodge_vel=15, invulnerability_time=25):
    if not random.randint(0, random_chance[0]) <= random_chance[1] or self.status["No damage"] != 0:
        return
    # Check if there bullets close to the boss, if the boss in invincible and a thing to make it a bit random
    if Fun.get_number_of_thing_in_a_damn_circle(
            entities, "bullets", search_range, self.pos[0], self.pos[1]) > bullet_minimum:
        # Does the dodging part
        dodge_angle = self.angle + random.randint(dodge_angles[0], dodge_angles[1]) * (-1 * random.randint(0, 1))
        self.vel[0] += dodge_vel * math.cos(dodge_angle * math.pi / 180)
        self.vel[1] += dodge_vel * math.sin(dodge_angle * math.pi / 180)
        self.status["No damage"] += invulnerability_time

        return True
    return False


def universal_pathfinding(self, level, pos):
    if not Fun.wall_between(self.pos, pos, level):
        return False
    # Use the pathfinding function
    connections, points = level['pathfinding']['connections'], level['pathfinding']['points']

    # Get current location
    current_location = '0'
    control_dist = Fun.BIG_INT
    for p in points:
        test_dist = Fun.distance_between(points[p], self.pos)
        if test_dist < control_dist:
            current_location = p
            control_dist = test_dist

    # Get the target destination
    end_point = '0'
    control_dist = Fun.BIG_INT
    for p in points:
        test_dist = Fun.distance_between(points[p], pos)
        if test_dist < control_dist:
            end_point = p
            control_dist = test_dist
    path = Fun.entity_path_making(self, current_location, end_point, connections, points)
    if not path:
        return False
    point = points[path[0]]
    return point


def pathfinding(self, level):
    if not Fun.wall_between(self.pos, self.target.pos, level):
        return False
    # 'pathfinding': None, # {
    #             # 'points': {},  # "<id>": [<x>, <y>]
    #             # 'connections': {}  # "<id>": [<id of connected points>]
    #         # }
    # Use the pathfinding function
    connections = level['pathfinding']['connections']
    points = level['pathfinding']['points']

    # Get current location
    current_location = '0'
    control_dist = Fun.BIG_INT
    for p in points:
        test_dist = Fun.distance_between(points[p], self.pos)
        if test_dist < control_dist:
            current_location = p
            control_dist = test_dist

    # Get the target destination
    end_point = '0'
    control_dist = Fun.BIG_INT
    for p in points:
        if p == current_location:
            continue
        test_dist = Fun.distance_between(points[p], self.target.pos)
        if test_dist < control_dist:
            end_point = p
            control_dist = test_dist

    return points[Fun.entity_path_making(self, current_location, end_point, connections, points, [])[0]]


def start_up_lag_handler(self, target_time, key="Startup lag"):
    # This little thing make it way easier to have startup lag
    if self.free_var[key] >= target_time:
        self.free_var[key] = 0
        return True
    self.free_var[key] += 1
    return False


def entity_dodge_bullets(self, entities, look_range, bullets_to_dodge=(Bullets.Bullet, Bullets.Fire, Bullets.Missile, Bullets.Artillery)):
    bullet_to_dodge = Fun.find_closest_bullet_types_in_circle(self, entities, look_range, bullets_to_dodge)
    if bullet_to_dodge:
        # dodge_pos = Fun.move_with_vel_angle(self.pos, bullet_to_dodge.radius, bullet_to_dodge.angle  - 75)
        dodge_pos = bullet_to_dodge.pos

        self.input["Right"] = self.pos[0] > dodge_pos[0]
        self.input["Left"] = self.pos[0] < dodge_pos[0]
        self.input["Down"] = self.pos[1] > dodge_pos[1]
        self.input["Up"] = self.pos[1] < dodge_pos[1]


def agro_system(self):
    if self.did_agro_raise > 0:
        self.did_agro_raise -= self.agro_decrease_rate
    elif self.agro > 0 and self.time % 4 == 0:
        self.agro -= 1


import Entity_Input_Funcs
import Entity_Act_Funcs
import Entity_Draw_Funcs
import Entity_On_Death


ENEMY_NO_OWNER = Entity({"name": "Nest Trooper",
         "faction": "FAC-1",
         "type": "VIP",
         "targeting range": 0,
         "targeting angle": 0,
         "wall hack": False,
         "health": 1,
         "armour": 0,
         "damage resistances": {"Physical": 0, "Fire": 0, "Explosion": 0, "Energy": 0, "Melee": 0, "Healing": 0},
         "thickness": 0,
         "vel max": 0,
         "speed": 0,
         "friction": 0,
         "weapon": "Unarmed",
         "func input": "enemy_input_nest_trooper",
         "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_basic",
         "sprites": "Sprites/Enemies/Nest Commander.png",
         "on death": "none",
         "free var": {}
         }, team="Enemies", pos=[0, 0], start_angle=0, check_halloween=False)
# |Repertories|---------------------------------------------------------------------------------------------------------
# Entity stats
H_LO, H_LM, H_MO, H_MH, H_HO = 60, 90, 130, 170, 200        # Max Health
A_LO, A_LM, A_MO, A_MH, A_HO = 40, 60, 90, 120, 140         # Max Armour
V_LO, V_LM, V_MO, V_MH, V_HO = 2, 3, 4, 5, 5.75             # Max Speed
R_LO, R_LM, R_MO, R_MH, R_HO = 256, 384, 512, 640, 768      # Vision range
D_LO, D_LM, D_MO, D_MH, D_HO = 15, 30, 45, 60, 75           # Targeting angle
S_LO, S_LM, S_MO, S_MH, S_HO = 1, 0.85, 0.65, 0.55, 0.45    # Stealth mod
C_LO , C_LM, C_MO, C_MH, C_HO = 1, 2, 4, 6, 10               # Stealth Counter
T_LO, T_LM, T_MO, T_MH, T_HO = 8, 12, 16, 24, 32            # Size, thickness

# Dash speed
DS_LO, DS_LM, DS_MO, DS_MH, DS_HO = 9, 11, 13, 15, 17
DI_LO, DI_LM, DI_MO, DI_MH, DI_HO = 0, 0, 0, 0, 0
DR_LO, DR_LM, DR_MO, DR_MH, DR_HO = 0, 0, 0, 0, 0

# Driving
DRIVE_LO, DRIVE_LM, DRIVE_MO, DRIVE_MH, DRIVE_HO = 0, 1, 2, 3, 4
NO_RESIT = {"Physical": 1,  "Fire": 1,    "Explosion": 1,  "Energy": 1,       "Melee": 1, "Healing": 0}   # M/H
# Resistances M Average 0.85
LO_RESIT = {"Physical": 0.7,  "Fire": 1,    "Explosion": 0.7,  "Energy": 1,       "Melee": 1, "Healing": -1}   # M/H
EM_RESIT = {"Physical": 1,    "Fire": 0.8,  "Explosion": 0.8,  "Energy": 0.8,     "Melee": 1, "Healing": -1}   # M
WI_RESIT = {"Physical": 0.95, "Fire": 0.7,  "Explosion": 0.75, "Energy": 0.8,     "Melee": 1, "Healing": -1}   # M/H
SO_RESIT = {"Physical": 1,    "Fire": 1,    "Explosion": 1,    "Energy": 1,       "Melee": 1, "Healing": -1}   # L
DU_RESIT = {"Physical": 0.7,  "Fire": 1,    "Explosion": 1,    "Energy": 0.7,     "Melee": 1, "Healing": -1}   # M
JE_RESIT = {"Physical": 0.5,  "Fire": 0.4,  "Explosion": 0.7,  "Energy": 0.4,     "Melee": 1, "Healing": 0}    # H
CO_RESIT = {"Physical": 0.6,  "Fire": 0.9,  "Explosion": 0.8,  "Energy": 0.6,     "Melee": 1, "Healing": -1}   # M/H
FO_RESIT = {"Physical": 0.6,  "Fire": 0.2,  "Explosion": 0.6,  "Energy": 0.3,     "Melee": 1, "Healing": 0}   # M/H

CU_RESIT = {"Physical": 0.75, "Fire": 0.85, "Explosion": 0.9,  "Energy": 0.9,     "Melee": 1, "Healing": -1}   # M
LA_RESIT = {"Physical": 0.8,  "Fire": 0.8,  "Explosion": 0.9,  "Energy": 0.9,     "Melee": 1, "Healing": -1}   # M
MA_RESIT = {"Physical": 0.9,  "Fire": 0.8,  "Explosion": 0.9,  "Energy": 0.8,     "Melee": 1, "Healing": -1}   # M
VI_RESIT = {"Physical": 0.9,  "Fire": 0.9,  "Explosion": 0.8,  "Energy": 0.8,     "Melee": 1, "Healing": -1}   # M


IN_RESIT = {"Physical": 0,    "Fire": 0,    "Explosion": 0,  "Energy": 0,     "Melee": 0, "Healing": -1}   # M

VIVIANNE_SUMMON_LIVE_TIME = 800
# HEALING_PRIORITY_LIST = {"Wizard": -1, "Emperor": 0, "Lord": 1, "Duke": 2, "Condor": 3, "Jester": 4, "Sovereign": 5}
player_repertory = {
    # THR-1
    #               MHlt    MArm    Resits  Spd     VisRg   SltMod  SltCntr Size    Driving DshSpd  DshInv  DshReco
    # Lord	        M/H     M       M/H     M       M/H     L--     L/M     M/H     M       H       L/M     M       Generates tons of agro, all weapons do AoE damage
    "Lord": {
        "name": "Lord",
        "health": H_MH, "armour": A_MO, "damage resistances": LO_RESIT,
        "sprites": "Sprites/Player/THR-1/Lord.png",

        "thickness": T_MH, "vel max": V_MO, "speed": 2.2, "friction": 1.5,
        "dash": {"speed": DS_HO, "i-frames": 12, "charge": 35},
        # Weapons
        "weapon": "Saloum Mk-2", "skills": ["Gauntlet Punch", "Beast Mode"],
        # AI
        "func input": "test_ally_input", "func act": "player_act", "func draw": "player_draw", "on death": "lord_on_death",
        "targeting range": R_MH, "targeting angle": D_LM, "wall hack": False,
        "driving": DRIVE_MO,
        "free var": {"Ally waypoint": [0, 0]}
    },
    # Emperor	    M       L/M     M       M/H     H       M       M/H     M       M       M       H       H       Jack of all trades
    "Emperor": {
        "name": "Emperor",
        "health": H_MO, "armour": A_LM, "damage resistances": EM_RESIT, "sprites": "Sprites/Player/THR-1/Emperor.png",
        "thickness": T_MO,
        "vel max": V_MH,
        "speed": 2.2,
        "friction": 1.5,
        "dash": {"speed": DS_MO, "i-frames": 12, "charge": 35},
        # Weapons
        "weapon": "GunBlade", "skills": ["Stun Kick", "Mega Buff" ],
        # AI
        "func input": "test_ally_input", "func act": "player_act", "func draw": "player_draw", "on death": "none",
        "targeting range": R_HO, "targeting angle": D_MO, "stealth mod": S_MO, "stealth counter": C_MH,
        "wall hack": False,
        "driving": DRIVE_MO,
        "free var": {"Ally waypoint": [0, 0], "Startup lag": 0, "Startup time": 60, "Kicked": 0}
    },
    # Wizard        L/M     M       M/H     M       M       L/M     M       M       H       M       H       M       Area denial
    "Wizard": {
        "name": "Wizard",
        "health": H_LM, "armour": A_MO, "damage resistances": WI_RESIT, "sprites": "Sprites/Player/THR-1/Wizard.png",
        "thickness": T_MO,
        "vel max": V_MO, "speed": 2.2, "friction": 1.5,
        "dash": {"speed": DS_MO, "i-frames": 12, "charge": 35},
        # Weapons
        "weapon": "Jeanne's Family Shotgun", "skills": ["Building", "All Guns Blazing"],
        # AI
        "func input": "test_ally_input", "func act": "player_act", "func draw": "player_draw", "on death": "none",
        "targeting range": R_MO, "targeting angle": D_MH, "stealth mod": S_LM, "stealth counter": C_MO,
        "wall hack": False,
        "driving": DRIVE_HO,
        "free var": {"Ally waypoint": [0, 0]}
    },
    # Sovreig       L/M     L/M     L       M/H     H++     M/H     H       L       L       L/M     L       M       Sniper recon
    "Sovereign": {
        "name": "Sovereign",
        "health": H_LM, "armour": A_LM, "damage resistances": SO_RESIT, "sprites": "Sprites/Player/THR-1/Sovereign.png",
        "thickness": T_LO,
        "vel max": V_MH,
        "speed": 2.2,
        "friction": 1.5,
        "dash": {"speed": DS_LM, "i-frames": 12, "charge": 35},
        # Weapons
        "weapon": "St-Maurice", "skills": ["Cardboard box", "Detect Targets"],
        # AI
        "func input": "test_ally_input", "func act": "player_act", "func draw": "player_draw", "on death": "none",
        "targeting range": R_HO * 1.5, "targeting angle": D_LM, "stealth mod": S_MH, "stealth counter": C_HO,
        "wall hack": False,
        "driving": DRIVE_LO,
        "free var": {"Ally waypoint": [0, 0], "Detect Targets Duration": 3 * 60, "Exposed blue ball timer": 0}
    },
    # Duke	        M       L/M     M       H       M       H       M       L/M     L/M     H       H       H	    Plays with agro
    "Duke": {
        "name": "Duke",
        "health": H_MO, "armour": A_LM, "damage resistances": DU_RESIT,
        "sprites": "Sprites/Player/THR-1/Duke.png",
        "thickness": T_LM,
        "vel max": V_HO,
        "speed": 2.2,
        "friction": 1.5,
        "dash": {"speed": DS_HO, "i-frames": 12, "charge": 35},
        # Weapons
        "weapon": "Chain Axe", "skills": ["Tail Swipe", "Smoke Screen"],
        # AI
        "func input": "test_ally_input", "func act": "player_act", "func draw": "player_draw", "on death": "none",
        "targeting range": R_MO, "targeting angle": D_HO, "stealth mod": S_HO, "stealth counter": C_HO,
        "driving": DRIVE_LM,
        "wall hack": False,
        "free var": {"Ally waypoint": [0, 0]}
    },
    # Jester	    L--     H++     H       L       L/M     L/M     H++     M/H     L/M     L--     H++     L       Primary support. Helps them not dying
    "Jester": {
        "name": "Jester",
        "health": int(H_LO * 0.5), "armour": A_MH * 2, "damage resistances": JE_RESIT,
        "sprites": "Sprites/Player/THR-1/Jester.png",
        "thickness": T_MH,
        "vel max": V_LO,
        "speed": 2.2,
        "friction": 0.5,
        "dash": {"speed": DS_LO * 0.4, "i-frames": 12, "charge": 35},

        # Weapons
        "weapon": "Epicurean Medic Rifle", "skills": ["Discharge", "Robot Fuck Off"],
        # AI
        "func input": "jester_input", "func act": "player_act", "func draw": "player_draw", "on death": "none",
        "targeting range": R_LM, "targeting angle": D_MH, "stealth mod": S_LM, "stealth counter": C_HO * 1.2,
        "wall hack": False,
        "driving": DRIVE_LM,
        "free var": {"Ally waypoint": [0, 0]}
    },
    # Condor        H       H       M/H     L/M     M       L       L/M     M/H     M/H     M       L       L       Tank and cause debuffs
    "Condor": {
        "name": "Condor",
        "health": H_HO, "armour": A_HO, "damage resistances": CO_RESIT,
        "sprites": "Sprites/Player/THR-1/Condor.png",

        "thickness": T_MH,
        "vel max": V_LM,
        "speed": 2.2,
        "friction": 0.8,
        "dash": {"speed": DS_LO, "i-frames": 12, "charge": 35},
        # Weapons
        "weapon": "Type 41 SMG", "skills": ["Armour Breaker", "Last Stand"],
        # AI
        "func input": "test_ally_input", "func act": "player_act", "func draw": "player_draw", "on death": "condor_on_death",
        "targeting range": R_MO, "targeting angle": D_MO, "stealth mod": S_LO, "stealth counter": C_LM,
        "driving": DRIVE_MH,
        "wall hack": False,
        "free var": {"Ally waypoint": [0, 0]}
    },

    # Fortress APC
    "Fortress": {
        "name": "Fortress",
        "health": H_HO * 3, "armour": A_HO *  3, "damage resistances": FO_RESIT,
        "sprites": "Sprites/Player/THR-1/Condor.png",

        "thickness": 60,
        "vel max": V_MO,
        "speed": 2.2,
        "friction": 0.8,
        "dash": {"speed": DS_HO, "i-frames": 0, "charge": 35},
        # Weapons
        "weapon": "Fortress Machine Gun", "skills": ["Mortar", "Repairs"],
        # AI
        "func input": "fortress_input", "func act": "fortress_act", "func draw": "fortress_draw", "on death": "fortress_on_death",
        "targeting range": R_MO, "targeting angle": 180, "stealth mod": S_LO, "stealth counter": C_LM,
        "wall hack": False,
        "driving": DRIVE_HO,
        "free var": {"Ally waypoint": [0, 0], "Move angle": 0, "IS AN APC": "Fortress"}
    },

    # Zoar Colonists
    #               MHlt    MArm    Resits  Spd     VisRg   SltMod  SltCntr Size    Driving DshSpd  DshInv  DshReco
    # Curtis        M       M       M       H++     H       M/H     M       M       L       H++     H++     H++     Great at fighting. Pressing reload with a gun that can't be reloaded switch the gun
    "Curtis": {
        "name": "Curtis",
        "wall hack": False,
        "targeting angle": 90, "targeting range": 512,
        "health": 200,
        "armour": 50,
        "damage resistances": CU_RESIT,
        "weapon": "Standard Shotgun",

        "thickness": 16,
        "vel max": 6.25,
        "speed": 1.17,
        "friction": 1.15,
        "dash": {"speed": DS_HO, "i-frames": 24, "charge": 25},

        "sprites": "Sprites/Player/Curtis.png",

        "skills": ["Kick", "Le Mat"],
        "func input": "test_ally_input",
        "func act": "player_act",
        "func draw": "player_draw",
        "on death": none,
        "free var": {"Ally waypoint": [0, 0]}
    },
    # Law.	        H       H       M       H       M       H       M       M       L       M/H     M/H     M/H     AoE attacks
    "Lawrence": {
        "name": "Lawrence",
        "health": 350,
        "armour": 75,
        "damage resistances": LA_RESIT,
        "sprites": "Sprites/Player/Lawrence.png",

        "thickness": 20,
        "vel max": 5.25,
        "speed": 1.5,
        "friction": 1.25,
        "dash": {"speed": 16, "i-frames": 24, "charge": 25},

        # Weapons
        # "weapon": "Lawrence's handgun",
        "weapon": "Lawrence's Cutlass & Flintlock",
        # Skills
        "skills": ["Flame Canyon", "Flame Burst"],
        # AI
        "func input": "test_ally_input",
        "func act": "player_act",
        "func draw": "player_draw",
        "on death": "none",
        "targeting range": 750,
        "targeting angle": 33,
        "wall hack": False,
        "free var": {"Ally waypoint": [0, 0], "Aim time": 0, "Startup lag": 0, "Startup time": 60},
    },
    # Mark          M       L/M     M       M       H++     H       H++     M       H       M       M       M	Sniper, causes debuffs on his targets
    "Mark": {
        "name": "Mark",
        "health": 250,
        "armour": 50,
        "damage resistances": MA_RESIT,
        "sprites": "Sprites/Player/Mark.png",

        # Speed stuff
        "thickness": 16,
        "vel max": 3,
        "speed": 1.3,
        "friction": 1,
        "dash": {"speed": 9, "i-frames": 12, "charge": 35},
        # Weapons
        "weapon": "Mark's Rifle", "skills": ["Target Locator", "Smoke Grenade"],
        # AI
        "func input": "test_ally_input",
        "func act": "player_act",
        "func draw": "player_draw",
        "on death": "none",
        "targeting range": 750,
        "targeting angle": 33,
        "wall hack": False,
        "free var": {"Ally waypoint": [0, 0]}
    },
    # Viv.          L/M     M       M       M       M       M       M/H     M       H       M       M       M       Primary support. Make weapons work better
    "Vivianne": {
        "name": "Vivianne",
        "health": 250,
        "armour": 50,
        "damage resistances": VI_RESIT,
        "sprites": "Sprites/Player/Vivianne.png",

        "thickness": 15,
        "vel max": 4.4,
        "speed": 2.2,
        "friction": 1.5,
        "dash": {"speed": 8, "i-frames": 12, "charge": 35},

        # Weapons
        "weapon": "Vivianne's Rifle",
        "skills": ["Rat Shot", "Reaper Rounds"],
        # AI
        "func input": "test_ally_input",
        "func act": "vivianne_act",
        "func draw": "player_draw",
        "on death": "none",
        "targeting range": 750,
        "targeting angle": 33,
        "wall hack": False,
        "free var": {"Ally waypoint": [0, 0], "Summon cooldown time": 360, "Summon cooldown": 0, "Summon limit": 1,
                     "Summon pool": [], "Active summons": []}
    },

    "Curtis (Vertical)": {
        "name": "Curtis",
        "wall hack": False,
        "targeting angle": 90, "targeting range": 512,
        "health": 200,
        "armour": 50,
        "damage resistances": CU_RESIT,
        "weapon": "Standard Shotgun",

        "thickness": 16,
        "vel max": 6.25,
        "speed": 1.17,
        "friction": 1.15,
        "dash": {"speed": DS_HO, "i-frames": 24, "charge": 25},

        "sprites": "Sprites/Player/Curtis.png",

        "skills": ["Kick", "Le Mat"],
        "func input": "test_ally_input",
        "func act": "player_act_vertical",
        "func draw": "player_draw",
        "on death": none,
        "free var": {
            "Ally waypoint": [0, 0],
            "Vertical phys": {
                "Time jumping": 0,  # How long the player has been jumping for
                "Stored speed": 0,  # How long the player pressed down to jump. Goes down after accel window. Give speed to the jump as it goes down
                "Jumping": False,

                "Accel Window": 4, # how long the player can press to jump higher
                "Jump speed": 2,
                "Fall speed": 0.6,   # Kicks in when player has no more stored speed
                "Ground friction": 1.15,
                "Air friction": 0.4,

                "Dash mod": 0.6,
                "Dash count": 0,
                "Dash limit": 2
            }
        }
    },

    # Nest Agent
    "Agent Cardinal": {
        "name": "Agent Cardinal",
        "health": H_MH, "armour": A_MO, "damage resistances": LO_RESIT,
        "sprites": "Sprites/Player/Nest Agent.png",

        "thickness": T_MH,

        "vel max": 6.25,
        "speed": 1.17,
        "friction": 1.15,
        "dash": {"speed": DS_HO, "i-frames": 12, "charge": 35},
        # Weapons
        "weapon": "Nest Battle Rifle", "skills": ["RPG!", "Beast Mode"],
        # AI
        "func input": "test_ally_input", "func act": "nest_agent_act", "func draw": "player_draw_advanced_movement", "on death": none,
        "targeting range": R_MH, "targeting angle": D_LM, "wall hack": False,
        "driving": DRIVE_MO,
        "free var": {
            "Ally waypoint": [0, 0],
            "Weapon sprite": Fun.get_image("Sprites/Weapon/NEST/Nest Battle Rifle.png"),
            "RPG sprite": Fun.get_image("Sprites/Weapon/NEST/RPG.png")
        }
    },

    # Agency
    # 2 input func
    #   player, just use player inputs
    #   com, follows player uses the player's field of view to target enemies
    #   com is stored in the player
    # 1 act func
    #   switching is bound to the skill inputs
    #   makes the com do stuff
    # use regular draw func
    


    "Sand Buggy": {
        "name": "Sand Buggy",
        "health": H_HO * 2, "armour": A_HO * 2, "damage resistances": FO_RESIT,
        "sprites": "Sprites/Player/THR-1/Condor.png",

        "thickness": 60,
        "vel max": V_HO,
        "speed": 0.9,
        "friction": 0.65,
        "dash": {"speed": DS_LO, "i-frames": 0, "charge": 15},
        # Weapons
        "weapon": "Buggy Gun", "skills": ["Drift", "Rocket Burst"],
        # AI
        "func input": "fortress_input", "func act": "buggy_act", "func draw": "buggy_draw",
        "on death": "fortress_on_death",
        "targeting range": R_MH, "targeting angle": 180, "stealth mod": S_LM, "stealth counter": C_MH,
        "wall hack": False,
        "driving": DRIVE_HO,
        "free var": {"Ally waypoint": [0, 0], "Move angle": 0, "Target Move angle": 0, "Move vel": 0, "IS AN APC": "Sand Buggy"}
    },

    # Vivianne summons
    # Birna & Sardine
    "Birna & Sardine": {
        "name": "Birna & Sardine",
        "health": 250, "armour": 1, "damage resistances": VI_RESIT,
        "sprites": "Sprites/Player/Tomboy/Birna.png", "Sprite Height": 40,

        "thickness": 15,
        "vel max": 4.4,
        "speed": 2.2,
        "friction": 1.5,
        "dash": {"speed": 12, "i-frames": 20, "charge": 25},

        # Weapons
        "weapon": "Sardine's Bucket",
        "skills": [],

        # AI
        "func input": "birna_input",
        "func act": "vivianne_summons_act",
        "func draw": "birna_draw",
        "on death": "vivianne_summons_on_death",
        "targeting range": 750,
        "targeting angle": 33,
        "wall hack": False,
        "free var": {"Life Limit": VIVIANNE_SUMMON_LIVE_TIME, "NO DEATH MESSAGE": True}
    },
    # Elektra
    "Elektra": {
        "name": "Elektra",
        "health": 250, "armour": 1, "damage resistances": VI_RESIT,
        "sprites": "Sprites/Player/Tomboy/Elektra.png",

        "thickness": 15,
        "vel max": 0,
        "speed": 0,
        "friction": 5.5,
        "dash": {"speed": 8, "i-frames": 12, "charge": 35},

        # Weapons
        "weapon": "Type 56 Carbine",
        "skills": [],

        # AI
        "func input": "elektra_input",
        "func act": "vivianne_summons_act",
        "func draw": "elektra_draw",
        "on death": "vivianne_summons_on_death",
        "targeting range": 750,
        "targeting angle": 140,
        "wall hack": False,
        "free var": {"Life Limit": 360, "NO DEATH MESSAGE": True}
    },
    # Agatha
    "Agatha": {
        "name": "Agatha",
        "health": 300, "armour": 1,
        "damage resistances": {
            "Physical": 0.5, "Fire": 0.5, "Explosion": 0.5, "Energy": 0.5, "Melee": 0.5, "Healing": -1},
        "sprites": "Sprites/Player/Tomboy/Agatha.png",

        "thickness": 15,
        "vel max": 4.4,
        "speed": 2.2,
        "friction": 1.5,
        "dash": {"speed": 8, "i-frames": 12, "charge": 35},

        # Weapons
        "weapon": "Agatha's Fist",
        "skills": [],

        # AI
        "func input": "agatha_input",
        "func act": "vivianne_summons_act",
        "func draw": "player_draw",
        "on death": "vivianne_summons_on_death",
        "targeting range": 750,
        "targeting angle": 140,
        "wall hack": False,
        "free var": {"Life Limit": VIVIANNE_SUMMON_LIVE_TIME, "NO DEATH MESSAGE": True}
    },
    # Azura
    "Azura": {
        "name": "Azura",
        "health": 250, "armour": 1, "damage resistances": VI_RESIT,
        "sprites": "Sprites/Player/Tomboy/Azura.png",

        "thickness": 15,
        "vel max": 4.4,
        "speed": 2.2,
        "friction": 1,
        "dash": {"speed": 12, "i-frames": 14, "charge": 24},

        # Weapons
        "weapon": "Azura's Fist",
        "skills": [],

        # AI
        "func input": "azura_input",
        "func act": "vivianne_summons_act",
        "func draw": "player_draw",
        "on death": "vivianne_summons_on_death",
        "targeting range": 750,
        "targeting angle": 33,
        "wall hack": False,
        "free var": {"Life Limit": VIVIANNE_SUMMON_LIVE_TIME, "NO DEATH MESSAGE": True}
    },
    # M (Marisa)
    "M (Marisa)": {
        "name": "M (Marisa)",
        "health": 250, "armour": 1, "damage resistances": VI_RESIT,
        "sprites": "Sprites/Player/Tomboy/M.png",

        "thickness": 15,
        "vel max": 4.4,
        "speed": 2.2,
        "friction": 1.5,
        "dash": {"speed": 8, "i-frames": 12, "charge": 35},

        # Weapons
        "weapon": "M's Spear",
        "skills": [],

        # AI
        "func input": "m_input",
        "func act": "vivianne_summons_act",
        "func draw": "player_draw",
        "on death": "vivianne_summons_on_death",
        "targeting range": 750,
        "targeting angle": 33,
        "wall hack": False,
        "free var": {"Life Limit": VIVIANNE_SUMMON_LIVE_TIME, "NO DEATH MESSAGE": True}
    },
    # Sierra
    "Sierra": {
        "name": "Sierra",
        "health": 250, "armour": 1, "damage resistances": VI_RESIT,
        "sprites": "Sprites/Player/Tomboy/Sierra.png",

        "thickness": 15,
        "vel max": 4.4,
        "speed": 2.2,
        "friction": 1.5,
        "dash": {"speed": 8, "i-frames": 12, "charge": 35},

        # Weapons
        "weapon": "Anti-Material Rifle",
        "skills": [],

        # AI
        "func input": "sierra_input",
        "func act": "vivianne_summons_act",
        "func draw": "player_draw",
        "on death": "vivianne_summons_on_death",
        "targeting range": 750,
        "targeting angle": 180,
        "wall hack": False,
        "free var": {"Life Limit": VIVIANNE_SUMMON_LIVE_TIME * 1.75, "NO DEATH MESSAGE": True,
                     "Ammo": {"Anti-Material Rifle": 5, "Shotgun": 8, "Pistol": 18}}
    },
    # Makoto
    "Makoto": {
        "name": "Makoto",
        "health": 250, "armour": 1, "damage resistances": VI_RESIT,
        "sprites": "Sprites/Player/Tomboy/Makoto.png",

        "thickness": 15,
        "vel max": 4.4,
        "speed": 2.2,
        "friction": 1.5,
        "dash": {"speed": 8, "i-frames": 12, "charge": 35},

        # Weapons
        "weapon": "Iguana's tail",
        "skills": [],

        # AI
        "func input": "makoto_input",
        "func act": "vivianne_summons_act",
        "func draw": "player_draw",
        "on death": "vivianne_summons_on_death",
        "targeting range": 750,
        "targeting angle": 33,
        "wall hack": False,
        "free var": {"Life Limit": VIVIANNE_SUMMON_LIVE_TIME, "NO DEATH MESSAGE": True}
    },
    "Spectator": {
        "name": "Spectator",
        "wall hack": False,
        "targeting angle": 180, "targeting range": 512 * 2, "stealth mod": 0.1, "stealth counter": 100,
        "health": 1,
        "armour": 1,
        "damage resistances": IN_RESIT,
        "weapon": "Standard Shotgun",

        "thickness": 16,
        "vel max": 6.25,
        "speed": 1.17,
        "friction": 1.15,
        "dash": {"speed": DS_HO, "i-frames": 24, "charge": 25},

        "sprites": "Sprites/Player/Curtis.png",

        "skills": [],
        "func input": "test_ally_input",
        "func act": "player_act",
        "func draw": none,
        "on death": none,
        "free var": {"Ally waypoint": [0, 0]}
    },
}

# Resistances   set to 1 mean no resistance
F1_RESIT_L = {"Physical": 1,    "Fire": 1,    "Explosion": 1,    "Energy": 0.80,    "Melee": 1,     "Healing": 0}
F1_RESIT_M = {"Physical": 0.80, "Fire": 1,    "Explosion": 1,    "Energy": 0.60,    "Melee": 1,     "Healing": 0}
F1_RESIT_H = {"Physical": 0.66, "Fire": 0.75, "Explosion": 1,    "Energy": 0.25,    "Melee": 1,     "Healing": 0}

F2_RESIT_L = {"Physical": 1,    "Fire": 1,    "Explosion": 1,    "Energy": 1,       "Melee": 1,     "Healing": 0}
F2_RESIT_M = {"Physical": 1,    "Fire": 1,    "Explosion": 1,    "Energy": 1,       "Melee": 1,     "Healing": 0}
F2_RESIT_H = {"Physical": 1,    "Fire": 1,    "Explosion": 1,    "Energy": 1,       "Melee": 1,     "Healing": 0}

F3_RESIT_L = {"Physical": 1,    "Fire": 1,    "Explosion": 0.66, "Energy": 1,       "Melee": 1,     "Healing": 0}
F3_RESIT_M = {"Physical": 0.75, "Fire": 1,    "Explosion": 0.5,  "Energy": 1,       "Melee": 1,     "Healing": 0}
F3_RESIT_F = {"Physical": 0.75, "Fire": 0.25, "Explosion": 0.8,  "Energy": 1,       "Melee": 1,     "Healing": 0}
F3_RESIT_H = {"Physical": 0.5,  "Fire": 0.25, "Explosion": 0.33, "Energy": 0.4,     "Melee": 1,     "Healing": 0}

NO_RESIT_L = {"Physical": 1,    "Fire": 1,    "Explosion": 1,    "Energy": 1,       "Melee": 1,     "Healing": 0}

GILG_RESIT = {"Physical": 0.6,  "Fire": 0.6,  "Explosion": 0.6,  "Energy": 0.6,     "Melee": 1.2, "Healing": 0}


# No Name TSS resistance profiles
RESISTANCES_NORMAL = {"Physical": 1, "Fire": 1, "Explosion": 1, "Energy": 1, "Melee": 1}
RESISTANCES_FUCKING_INVINCIBLE = {"Physical": 0, "Fire": 0, "Explosion": 0, "Energy": 0, "Melee": 0}
RESISTANCES_BOMB_SUIT = {"Physical": 0.75, "Fire": 1.5, "Explosion": 0.125, "Energy": 1, "Melee": 1}
RESISTANCES_ASBESTOS_SUIT = {"Physical": 1.25, "Fire": 0.125, "Explosion": 1, "Energy": 1.25, "Melee": 1}
RESISTANCES_ARMOURED = {"Physical": 0.75, "Fire": 0.75, "Explosion": 0.75, "Energy": 1.25, "Melee": 1}
RESISTANCES_MACHINE = {"Physical": 1, "Fire": 0.25, "Explosion": 1.25, "Energy": 0.25, "Melee": 1}
# Boss
RESISTANCES_BOSS_DEFAULT = {"Physical": 1, "Fire": 1, "Explosion": 1, "Energy": 1, "Melee": 2}
RESISTANCES_MINIBOSS_DEFAULT = {"Physical": 1.5, "Fire": 1.5, "Explosion": 1.5, "Energy": 1.5, "Melee": 3}
RESISTANCES_BOSS_HIEROPHANT = {"Physical": 1, "Fire": 0.4, "Explosion": 1.25, "Energy": 0.4, "Melee": 2}
RESISTANCES_BOSS_EMPEROR_EMPRESS_PHASE1 = {"Physical": 0.8, "Fire": 1, "Explosion": 1, "Energy": 0.9, "Melee": 1.7}
RESISTANCES_BOSS_EMPEROR_EMPRESS_PHASE2 = {"Physical": 0.7, "Fire": 0.8, "Explosion": 0.8, "Energy": 0.7, "Melee": 1.5}
RESISTANCES_CRAB = {"Physical": 0.6, "Fire": 0.6, "Explosion": 0.6, "Energy": 0.6, "Melee": 1}
# Ally resistances
RESISTANCES_ALLY_DEFAULT = {"Physical": 1, "Fire": 1, "Explosion": 1, "Energy": 1, "Melee": 1}
RESISTANCES_DOPPELGANGER = {"Physical": 2, "Fire": 2, "Explosion": 2, "Energy": 2, "Melee": 2}
RESISTANCES_MAKOTO = {"Physical": 0.9, "Fire": 1, "Explosion": 1, "Energy": 1, "Melee": 0.9}


enemy_repertory = {
    #                   MHlt	MArm	Resits	Spd 	VisRg	SltMod	SltCntr	Size
    # |Circle|----------------------------------------------------------------------------------------------------------
    # Manager
    "Manager":
        {"name": "Manager",
         "faction": "FAC-1",
         "type": "Grunt",
         "targeting range": R_MH, "targeting angle": 25, "stealth mod": S_MH, "stealth counter": C_LM,
         "wall hack": False,
         "health": H_MO, "armour": A_LO, "damage resistances": F1_RESIT_L,
         "thickness": T_MO,
         "vel max": V_MO,
         "speed": 1.5,
         "friction": 1.5,
         "weapon": "Laser Carbine",

         "func input": "enemy_input_faction_1_body_guard",
         "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_sniper",
         "sprites": "Sprites/Enemies/Manager.png",
         "on death": "none",
         "free var": {"Startup lag": 0, "Startup time": 50, "Is VIP": True}
         },
    # BodyGuard	        M	    L	    L       M	    M/H	    L/M	    M	    M	    Escorts Heavy Sniper
    "Body Guard":
        {"name": "Body Guard",
         "faction": "FAC-1",
         "type": "Grunt",
         "targeting range": R_MH, "targeting angle": 25, "stealth mod": S_MH, "stealth counter": C_LM,
         "wall hack": False,
         "health": H_MO, "armour": A_LO, "damage resistances": F1_RESIT_L,
         "thickness": T_MO,
         "vel max": V_MO,
         "speed": 1.5,
         "friction": 1.5,
         "weapon": "Laser Rifle",

         "func input": "enemy_input_faction_1_body_guard",
         "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_sniper",
         "sprites": "Sprites/Enemies/Body Guard.png",
         "on death": "none",
         "free var": {"Startup lag": 0, "Startup time": 60}
         },
    # Heavy Sniper      M	    M	    M	    L/M	    H	    L	    M	    M/H	    Main damage source
    "Heavy Sniper":
        {"name": "Heavy Sniper",
              "faction": "FAC-1",
              "type": "Shock",
              "targeting range": R_HO, "targeting angle": 25, "stealth mod": S_LO, "stealth counter": C_MO,
              "wall hack": False,
              "health": H_MO, "armour": A_MO, "damage resistances": F1_RESIT_M,
              "thickness": T_MH,
              "vel max": V_LM,
              "speed": 1.5,
              "friction": 1.5,
              "weapon": "Heavy Laser",

              "func input": "enemy_input_faction_1_heavy_sniper",
              "func act": "enemy_act_type_1",
              "func draw": "enemy_draw_sniper",
              "sprites": "Sprites/Enemies/Heavy Sniper.png",
              "on death": "none",
              "free var": {"Startup lag": 0, "Startup time": 120, "aim line colour": [1, 2]}
              },
    # Radar Operator    L/M	    L/M	    L	    M/H	    H++	    L	    L	    M	    Share detected target for MsslOp
    "Radar Operator":
        {"name": "Radar Operator",
         "faction": "FAC-1",
         "type": "Support",
         "targeting range": R_HO * 1.2, "targeting angle": 25, "stealth mod": S_LO, "stealth counter": C_LO,
         "wall hack": False,
         "health": H_LM, "armour": A_LM, "damage resistances": F1_RESIT_L,
         "thickness": T_MO,
         "vel max": V_MH,
         "speed": 1.5,
         "friction": 1.5,
         "weapon": "Radar",

         "func input": "enemy_input_faction_1_radar",
         "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_basic",
         "sprites": "Sprites/Enemies/Radar Operator.png",
         "on death": "none",
         "free var": {}
         },
    # Missile Operator  M	    M	    M	    L/M	    M	    L	    L/M	    M	    Uses missiles
    "Missile Operator":
        {"name": "Radio Operator",
         "faction": "FAC-1",
         "type": "Specialist",
         "targeting range": R_MO, "targeting angle": 60,  "stealth mod": S_LO, "stealth counter": C_LM,
         "wall hack": False,
         "health": H_MO, "armour": A_MO, "damage resistances": F1_RESIT_M,
         "thickness": T_MO,
         "vel max": V_LM,
         "speed": 1.5,
         "friction": 1.5,
         "weapon": "Missile Pod",

         "func input": "enemy_input_faction_1_missile",
         "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_basic",
         "sprites": "Sprites/Enemies/Missile Operator.png",
         "on death": "none",
         "free var": {"missile target": False}
         },
    # Marksman	        M	    M	    L	    M	    M/H	    M	    H	    M	    Mark players. Marked players' location is always known
    "Marksman":
        {"name": "Marksman",
         "faction": "FAC-1",
         "type": "Specialist 2",
         "targeting range": R_HO, "targeting angle": 25, "stealth mod": S_MO, "stealth counter": C_HO,
         "wall hack": False,
         "health": H_MO, "armour": A_MO, "damage resistances": F1_RESIT_L,
         "thickness": T_MO,
         "vel max": V_MO,
         "speed": 1.5,
         "friction": 1.5,
         "weapon": "Marker Laser",

         "func input": "enemy_input_faction_1_basic",
         "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_sniper",
         "sprites": "Sprites/Enemies/Marksman.png",
         "on death": "none",
         "free var": {"Startup lag": 0, "Startup time": 90, "aim line colour": [2]}
         },
    # Enforcer	        H	    M/H	    H	    L	    M/H	    L--	    M	    H	    Multiple attacks for all ranges
    "Enforcer":
        {"name": "Enforcer",
         "faction": "FAC-1",
         "type": "Elite",
         "targeting range": R_MH, "targeting angle": 25, "stealth mod": S_LO * 1.2, "stealth counter": C_MO,
         "wall hack": False,
         "health": H_HO, "armour": H_MH, "damage resistances": F1_RESIT_H,
         "thickness": T_HO,
         "vel max": V_LO,
         "speed": V_LO,
         "friction": V_LO,
         "weapon": "ARWS",

         "func input": "enemy_input_faction_1_basic",
         "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_enforcer",
         "on death": "enforcer_on_death",
         "free var": {"Startup lag": 0, "Startup time": 60, "missile target": False}
         },
    # Armored Shield Generator
    "Armed Shield Generator": {
        "name": "Armed Shield Generator", "faction": "FAC-1",
        # "health": H_HO * 20, "armour": 0, "damage resistances": FO_RESIT,
        "health": 1, "armour": 0, "damage resistances": FO_RESIT,
        "sprites": "Sprites/Player/THR-1/Condor.png",

        "thickness": 60, "vel max": V_MO, "speed": 2.2, "friction": 0.7,
        "dash": {"speed": DS_MO * 0.6, "i-frames": 0, "charge": 35},
        # Weapons
        "weapon": "Shield Generator Railgun",
        # AI
        "func input": "armoured_shield_generator_input", "func act": "armoured_shield_generator_act",
        "func draw": "armoured_shield_generator_draw",
        "on death": "armoured_shield_generator_on_death",
        "targeting range": R_MO, "targeting angle": 180, "stealth mod": S_LO, "stealth counter": C_LM,
        "wall hack": False,
        "free var": {"Move angle": 0,
                     "Machine Gun Angle": -90, "Allow machine gun": False,

                     "Startup lag missile": 0,
                     "Startup lag railgun": 0,
                     "Startup lag tesla": 0,

                     "IS BOSS": True, "Grenade Shakedown": 600, "Grenade Shakedown angle": 0, "Run people over": 250,
                     "Startup lag": 0, "Startup time": 240}
    },
    # AA Site
    # AA laser            Targets last position of a player. Infinite range
    "AA Laser": {
        "name": "AA Laser", "faction": "FAC-1",
        "health": H_HO * 9, "armour": 0, "damage resistances": FO_RESIT,
        "sprites": "Sprites/Player/THR-1/Condor.png",

        "thickness": 60, "vel max": 0, "speed": 0, "friction": 0.7,
        "dash": {"speed": 0, "i-frames": 0, "charge": 0},
        # Weapons
        "weapon": "Hover Tank Cannon",
        # AI
        "func input": "aa_site_input", "func act": "aa_site_act_aa_laser", "func draw": "aa_site_draw_aa_laser",
        "on death": "aa_site_on_death",
        "targeting range": R_HO, "targeting angle": 180, "stealth mod": S_LO, "stealth counter": C_LM,
        "wall hack": True,
        "free var": {"AA Site": True, "Pos history": [], "History limit": 100, "Draw angle": 0}
    },
    # Drone builder       Launches drones
    "Drone builder": {
        "name": "Drone builder", "faction": "FAC-1",
        "health": H_HO * 9, "armour": 0, "damage resistances": FO_RESIT,
        "sprites": "Sprites/Player/THR-1/Condor.png",

        "thickness": 60, "vel max": 0, "speed": 0, "friction": 0.7,
        "dash": {"speed": 0, "i-frames": 0, "charge": 0},
        # Weapons
        "weapon": "Hover Tank Cannon",
        # AI
        "func input": "aa_site_input", "func act": "aa_site_act_drone_factory",
        "func draw": "aa_site_draw_drone_factory",
        "on death": "aa_site_on_death",
        "targeting range": R_MO, "targeting angle": 180, "stealth mod": S_LO, "stealth counter": C_LM,
        "wall hack": False,
        "free var": {"AA Site": True, "Startup lag": 0}
    },
    # Missile Battery     Launches missiles, they have low speed and high manoeuvrability
    "Missile Battery": {
        "name": "Missile Battery", "faction": "FAC-1",
        "health": H_HO * 9, "armour": 0, "damage resistances": FO_RESIT,
        "sprites": "Sprites/Player/THR-1/Condor.png",

        "thickness": 60, "vel max": 0, "speed": 0, "friction": 0.7,
        "dash": {"speed": 0, "i-frames": 0, "charge": 0},
        # Weapons
        "weapon": "Hover Tank Cannon",
        # AI
        "func input": "aa_site_input", "func act": "aa_site_act_missile_battery",
        "func draw": "aa_site_draw_missile_battery",
        "on death": "aa_site_on_death",
        "targeting range": R_MO, "targeting angle": 180, "stealth mod": S_LO, "stealth counter": C_LM,
        "wall hack": False,
        "free var": {"AA Site": True, "Startup lag": 0, "Pos history": []}
    },
    # Shield Generator    Give other building a shield. If the shield takes too much damage they get disabled for a time
    "Shield Generator": {
        "name": "Shield Generator", "faction": "FAC-1",
        "health": H_HO * 6, "armour": 0, "damage resistances": FO_RESIT,
        "sprites": "Sprites/Player/THR-1/Condor.png",

        "thickness": 60, "vel max": 0, "speed": 0, "friction": 0.7,
        "dash": {"speed": 0, "i-frames": 0, "charge": 0},
        # Weapons
        "weapon": "Hover Tank Cannon",
        # AI
        "func input": "aa_site_input", "func act": "aa_site_act_shield_generator",
        "func draw": "aa_site_draw_shield_generator",
        "on death": "aa_site_on_death_shield_generator",
        "targeting range": R_MO, "targeting angle": 180, "stealth mod": S_LO, "stealth counter": C_LM,
        "wall hack": False,
        "free var": {"AA Site": True, "Shield cooldown": 320, "Shield Target": False, "Previous Shield Target": False}
    },
    # Energy Generator    If destroyed, kills the boss. Highest amount of health
    "Energy Generator": {
        "name": "Energy Generator", "faction": "FAC-1",
        "health": H_HO * 15, "armour": 0, "damage resistances": FO_RESIT,
        "sprites": "Sprites/Player/THR-1/Condor.png",

        "thickness": 60, "vel max": 0, "speed": 0, "friction": 0.7,
        "dash": {"speed": 0, "i-frames": 0, "charge": 0},
        # Weapons
        "weapon": "Hover Tank Cannon",
        # AI
        "func input": "aa_site_input", "func act": "aa_site_act_init", "func draw": "aa_site_draw_energy_generator",
        "on death": "aa_site_on_death_energy_generator",
        "targeting range": R_MO, "targeting angle": 180, "stealth mod": S_LO, "stealth counter": C_LM,
        "wall hack": False,
        "free var": {"IS BOSS": True, "Startup lag": 0, "Startup time": 240, "Pos history": []}
    },
    "Drone": {"name": "Drone",
         "faction": "FAC-1",
         "type": "Special",
         "targeting range": R_MO, "targeting angle": 60, "stealth mod": S_MO, "stealth counter": C_LO,
         "wall hack": False,
         "health": 1, "armour": 0, "damage resistances": NO_RESIT,
         "thickness": T_LO, "vel max": V_HO, "speed": 1.5, "friction": 1.5,
         "weapon": "Drone Gun",
         "func input": "enemy_input_faction_1_drone", "func act": "enemy_act_type_2", "func draw": "enemy_draw_no_gun",
         "sprites": "Sprites/Enemies/Drone.png", "on death": "none", "Sprite Height": 8,
         "free var": {"Is ASS": True}
         },
    # |Triangle|--------------------------------------------------------------------------------------------------------
    "Sculptor": {"name": "Sculptor",
         "faction": "FAC-2",
         "type": "Grunt",
         "targeting range": R_MO, "targeting angle": 60, "stealth mod": S_MO, "stealth counter": C_LO,
         "wall hack": False,
         "health": H_MO, "armour": A_LM, "damage resistances": F2_RESIT_H,
         "thickness": T_LO, "vel max": V_HO, "speed": 1.5, "friction": 1.5,
         "weapon": "Plasma Spray",
         "func input": "enemy_input_faction_2_basic", "func act": "enemy_act_type_1", "func draw": "enemy_draw_basic",
         "sprites": "Sprites/Enemies/Sculptor.png", "on death": "none",
         "free var": {"Is VIP": True}
         },
    # Skirmisher	    L/M	    L--	    M       M/H	    M	    H       M/H	    L/M	    No armour, low range. FAST. Dodges to stay alive
    "Skirmisher": {"name": "Skirmisher",
         "faction": "FAC-2",
         "type": "Grunt",
         "targeting range": R_MO, "targeting angle": 60, "stealth mod": S_HO, "stealth counter": C_MH,
         "wall hack": False,
         "health": H_LM, "armour": 0, "damage resistances": F2_RESIT_M,
         "thickness": T_LM, "vel max": V_HO, "speed": 1.5, "friction": 1.5,
         "weapon": "Plasma Rifle",
         "func input": "enemy_input_faction_2_basic",
         "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_basic",
         "sprites": "Sprites/Enemies/Skirmisher.png",
         "on death": "none",
         "free var": {}
         },
    # BoomStick	        M	    L/M	    M       M	    M	    M	    M	    M	    Slower, high damage
    "BoomStick": {"name": "BoomStick",
         "faction": "FAC-2",
         "type": "Shock",
         "targeting range": R_MO, "targeting angle": 60, "stealth mod": S_MO, "stealth counter": C_MO,
         "wall hack": False,
         "health": H_MO, "armour": A_LM, "damage resistances": F2_RESIT_M,
         "thickness": T_MO, "vel max": V_MO, "speed": 1.5, "friction": 1.5,
         "weapon": "Laser Shotgun",
         "func input": "enemy_input_faction_2_boomstick",
         "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_basic",
         "sprites": "Sprites/Enemies/BoomStick.png",
         "on death": "none",
         "free var": {"Startup lag": 0, "Startup time": 60}
         },
    # Smoker	        M	    L/M	    L       M/H	    M	    M	    M/H	    M	    Throws smoke grenades to conceal other enemies
    "Smoker": {"name": "Smoker",
         "faction": "FAC-2",
         "type": "Grunt",
         "targeting range": R_MO, "targeting angle": 60, "stealth mod": S_MO, "stealth counter": C_MH,
         "wall hack": False,
         "health": H_MO, "armour": A_LM, "damage resistances": F2_RESIT_L,
         "thickness": T_MO, "vel max": V_MH, "speed": 1.5, "friction": 1.5,
         "weapon": "Smoke Dispenser",
         "func input": "enemy_input_faction_2_smoker",
         "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_basic",
         "sprites": "Sprites/Enemies/Smoker.png",
         "on death": "none",
         "free var": {}
         },
    # Snare	            M	    L/M	    L       L/M	    M	    M	    M	    M	    Debuffs players, no idea how
    "Snare": {"name": "Snare",
         "faction": "FAC-2",
         "type": "Grunt",
         "targeting range": R_MO, "targeting angle": 60, "stealth mod": S_LO, "stealth counter": C_HO,
         "wall hack": False,
         "health": H_MH, "armour": A_MO, "damage resistances": F2_RESIT_H,
         "thickness": T_LM, "vel max": V_HO*1.25, "speed": 1.5, "friction": 1.5,
         "weapon": "Desert Shotgun",
         "func input": "enemy_input_faction_2_basic",
         "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_basic",
         "sprites": "Sprites/Enemies/Snare.png",
         "on death": "none",
         "free var": {}
         },
    # Crusher	        M/H	    M/H	    H       M	    L/M	    M	    M	    M/H	    Destroys armour
    "Crusher": {"name": "Crusher",
         "faction": "FAC-2",
         "type": "Grunt",
         "targeting range": R_LM, "targeting angle": 60, "stealth mod": S_MO, "stealth counter": C_MO,
         "wall hack": False,
         "health": H_MH, "armour": A_MH, "damage resistances": F2_RESIT_H,
         "thickness": T_MH, "vel max": V_HO, "speed": 1.5, "friction": 1.5,
         "weapon": "Gun Hammer",
         "func input": "enemy_input_faction_2_crusher",
         "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_basic",
         "sprites": "Sprites/Enemies/Crusher.png",
         "on death": "none",
         "free var": {}
         },
    # Assassin	        M/H	    M	    M       H	    M	    H	    M/H	    M	    Tries to flank the player
    "Assassin": {"name": "Assassin",
         "faction": "FAC-2",
         "type": "Grunt",
         "targeting range": R_MO, "targeting angle": 60, "stealth mod": S_HO, "stealth counter": C_MH,
         "wall hack": False,
         "health": H_MH, "armour": A_MO, "damage resistances": F2_RESIT_M,
         "thickness": T_MO, "vel max": V_HO, "speed": 1.5, "friction": 1.5,
         "weapon": "Pile Bunker",
         "func input": "enemy_input_faction_2_assassin",
         "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_advanced_gun",
         "sprites": "Sprites/Enemies/Assassin.png",
         "on death": "none",
         "free var": {}
         },
    "Hover Tank": {
        "name": "Hover Tank", "faction": "FAC-2",
        "health": H_HO * 20, "armour": 0, "damage resistances": FO_RESIT,
        # "health": 1, "armour": 0, "damage resistances": FO_RESIT,
        "sprites": "Sprites/Player/THR-1/Condor.png",

        "thickness": 60, "vel max": V_MO, "speed": 2.2, "friction": 0.7,
        "dash": {"speed": DS_MO * 0.6, "i-frames": 0, "charge": 35},
        # Weapons
        "weapon": "Hover Tank Cannon",
        # AI
        "func input": "hover_tank_input", "func act": "hover_tank_act", "func draw": "hover_tank_draw",
        "on death": "hover_tank_on_death",
        "targeting range": R_MO, "targeting angle": 180, "stealth mod": S_LO, "stealth counter": C_LM,
        "wall hack": False,
        "free var": {"Move angle": 0,
                     "Machine Gun Angle": -90, "Allow machine gun": False,
                     "IS BOSS": True, "Grenade Shakedown": 600, "Grenade Shakedown angle": 0, "Run people over": 250,
                     "Startup lag": 0, "Startup time": 240}
    },
    "Gilgamesh": {
        "name": "Gilgamesh", "faction": "FAC-2",
        "health": H_HO * 22, "armour": 0, "damage resistances": GILG_RESIT,
        "sprites": "Sprites/Enemies/Gilgamesh.png", "Sprite Height": 40,

        "thickness": 28, "vel max": V_HO, "speed": 8, "friction": 4,
        "dash": {"speed": DS_MO * 0.6, "i-frames": 0, "charge": 35},
        # Weapons
        "weapon": "Desert's Wind",
        # AI
        "func input": "gilgamesh_input", "func act": "gilgamesh_act", "func draw": "enemy_draw_advanced_gun",
        "on death": "gilgamesh_on_death",
        "targeting range": R_MO, "targeting angle": 180, "stealth mod": S_LO, "stealth counter": C_LM,
        "wall hack": False,
        "free var": {"IS BOSS": True,
                     "Current attack": "Divorce Spiral",
                     "Current sword attack": "Trishot",
                     "Startup lag sword": 0,
                     "Startup lag": 0,
                     "Pattern pos": [0, 0]}
    },

    # |Square|----------------------------------------------------------------------------------------------------------
    "Infantry": {"name": "Infantry",
         "faction": "FAC-3",
         "type": "Grunt",
         "targeting range": R_MO, "targeting angle": 60, "stealth mod": S_LO, "stealth counter": C_MO,
         "wall hack": False,
         "health": H_MH, "armour": A_MH, "damage resistances": F3_RESIT_M,
         "thickness": T_MO, "vel max": V_LO, "speed": 1.5, "friction": 1.5,
         "weapon": "Combat Rifle",
         "func input": "enemy_input_faction_3_basic",
         "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_basic",
         "sprites": "Sprites/Enemies/Infantry.png",
         "on death": "none",
         "free var": {}
         },
    # Flamer	        M/H	    M/H	    M	    L	    M	    L--	    M	    M/H	    Uses a flamethrower to counter close range attacks.
    "Flamer": {"name": "Flamer",
         "faction": "FAC-3",
         "type": "Shock",
         "targeting range": R_MO, "targeting angle": 60, "stealth mod": S_LO, "stealth counter": C_MO,
         "wall hack": False,
         "health": H_MH, "armour": A_MH, "damage resistances": F3_RESIT_F,
         "thickness": T_MO, "vel max": V_LO, "speed": 1.5, "friction": 1.5,
         "weapon": "Flamethrower",
         "func input": "enemy_input_faction_3_basic", "func act": "enemy_act_type_1", "func draw": "enemy_draw_basic",
         "sprites": "Sprites/Enemies/Flamer.png",
         "on death": "none",
         "free var": {}
         },
    # Spotter	        M/H	    M	    L	    L/M	    M/H	    L/M	    L/M	    M	    Can see through walls. Share targets.
    "Spotter": {"name": "Spotter",
         "faction": "FAC-3",
         "type": "Support",
         "targeting range": R_MH, "targeting angle": 60, "stealth mod": S_LO, "stealth counter": C_MO,
         "wall hack": True,
         "health": H_MH, "armour": A_MO, "damage resistances": F3_RESIT_L,
         "thickness": T_MO, "vel max": V_LO, "speed": 1.5, "friction": 1.5,
         "weapon": "Binoculars",
         "func input": "enemy_input_faction_3_spotter", "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_basic",
         "sprites": "Sprites/Enemies/Spotter.png",
         "on death": "none",
         "free var": {}
         },
    # Artilleryman      M/H	    M	    M	    L/M	    L/M	    L	    M	    L/M	    Causes artillery strikes
    "Artilleryman": {"name": "Artilleryman",
         "faction": "FAC-3",
         "type": "Specialist 1",
         "targeting range": R_LM, "targeting angle": 60, "stealth mod": S_LO, "stealth counter": C_MO,
         "wall hack": False,
         "health": H_MH, "armour": A_MO, "damage resistances": F3_RESIT_M,
         "thickness": T_LM, "vel max": V_LO, "speed": 1.5, "friction": 1.5,
         "weapon": "Artillery Radio",
         "func input": "enemy_input_faction_3_artilleryman", "func act": "enemy_act_type_1", "func draw": "enemy_draw_basic",
         "sprites": "Sprites/Enemies/Artilleryman.png",
         "on death": "none",
         "free var": {}
         },
    # Grenadier	        M/H	    M/H	    M	    L/M	    M	    L	    L/M	    M/H	    Uses incendiary grenades to deny area
    "Grenadier": {"name": "Grenadier",
         "faction": "FAC-3",
         "type": "Specialist 2",
         "targeting range": R_MO, "targeting angle": 60, "stealth mod": S_LO, "stealth counter": C_MO,
         "wall hack": False,
         "health": H_MH, "armour": A_MH, "damage resistances": F3_RESIT_M,
         "thickness": T_MO, "vel max": V_LO, "speed": 1.5, "friction": 1.5,
         "weapon": "Napalm Grenade Launcher",
         "func input": "enemy_input_faction_3_grenade", "func act": "enemy_act_type_1", "func draw": "enemy_draw_basic",
         "sprites": "Sprites/Enemies/Grenadier.png",
         "on death": "none",
         "free var": {}
         },
    # Bulwark	        H	    H++	    H	    L--	    M	    L--	    M	    H++	    Use minigun. Slow. Scary.
    "Bulwark": {"name": "Bulwark",
         "faction": "FAC-3",
         "type": "Elite",
         "targeting range": R_MO, "targeting angle": D_HO, "stealth mod": S_LO, "stealth counter": C_MO,
         "wall hack": False, "health": H_HO, "armour": round(A_HO*1.5), "damage resistances": F3_RESIT_H,
         "thickness": T_HO,
         "vel max": V_LO * 0.8, "speed": V_LO * 0.8, "friction": V_LO * 0.8,
         "weapon": "Bulwark Minigun",

         "func input": "enemy_input_faction_3_bulwark",
         "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_bulwark",
         "sprites": "Sprites/Enemies/Bulwark.png", "on death": "none",
         "free var": {}
         },
    "Commanding Officer": {"name": "Commanding Officer",
         "faction": "FAC-3",
         "type": "VIP",
         "targeting range": R_MH, "targeting angle": D_MO, "stealth mod": S_LO, "stealth counter": C_MO,
         "wall hack": False,
         "health": H_HO, "armour": H_LM, "damage resistances": F3_RESIT_L,
         "thickness": T_MO,
         "vel max": V_LM, "speed": 1.5, "friction": 1.5,
         "weapon": "Combat Rifle",

         "func input": "enemy_input_faction_3_basic", "func act": "enemy_act_type_1", "func draw": "enemy_draw_basic",
         "sprites": "Sprites/Enemies/Commanding Officer.png", "on death": "none",
         "free var": {"Is VIP": True}
         },
    "Super Bulwark": {"name": "Super Bulwark",
         "faction": "FAC-3",
         "type": "Elite",
         "targeting range": R_HO, "targeting angle": D_HO, "stealth mod": S_HO, "stealth counter": C_HO,
         "wall hack": False, "health": H_HO * 2, "armour": round(A_HO * 2), "damage resistances": F3_RESIT_H,
         "thickness": T_HO,
         "vel max": V_HO, "speed": V_LO, "friction": V_LO * 0.8,
         "weapon": "Super Bulwark Minigun",

         "func input": "enemy_input_faction_3_bulwark",
         "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_bulwark",
         "sprites": "Sprites/Enemies/Bulwark.png", "on death": "none",
         "free var": {"IS BOSS": True}
         },
    "Fire Support Mech":
        {"name": "Fire Support Mech",
         "faction": "FAC-3",
         "type": "Elite",
         "targeting range": R_MO, "targeting angle": D_HO, "stealth mod": S_LO, "stealth counter": C_MO,
         "wall hack": False, "health": H_HO * 22, "armour": 0, "damage resistances": F3_RESIT_H,
         "thickness": 48,
         "vel max": V_LO * 0.8, "speed": V_LO * 0.8, "friction": V_LO * 0.8,
         "weapon": "Bloodhound Weaponry",

         "func input": "bloodhound_input",
         "func act": "bloodhound_act",
         "func draw": "bloodhound_draw",
         # "func draw": "enemy_draw_basic",
         "sprites": "Sprites/Enemies/Bulwark.png", "on death": "bloodhound_on_death",
         "free var": {
             "IS BOSS": True,
             "Mech": MechRenderer.Mech(MechRenderer.bloodhound_mech, MechRenderer.bloodhound_palette, [0, -350]),
             "Move angle": -90,
             "Turn speed": 2,
             "Startup lag": 0,
             "Startup lag boost": 0,
             "Current attack": "Canon",
             "Boost type": []
         }
         },
    # Attack Helicopter
    "Attack Helicopter": {
        "name": "Attack Helicopter", "faction": "FAC-3",
        "health": H_HO * 20, "armour": 0, "damage resistances": FO_RESIT,
        # "health": 1, "armour": 0, "damage resistances": FO_RESIT,
        "sprites": "Sprites/Player/THR-1/Condor.png",

        "thickness": 60, "vel max": V_MO, "speed": 6.2, "friction": 4,
        "dash": {"speed": DS_MO * 0.6, "i-frames": 0, "charge": 35},
        # Weapons
        "weapon": "Attack Helicopter Weaponry",
        # AI
        "func input": "attack_helicopter_input", "func act": "attack_helicopter_act", "func draw": "attack_helicopter_draw",
        "on death": "attack_helicopter_on_death",
        "targeting range": R_MO, "targeting angle": 180, "stealth mod": S_LO, "stealth counter": C_LM,
        "wall hack": False,
        "free var": {"Move angle": 0, "Rocket type": "HE",
                     "Machine Gun Angle": -90, "Allow machine gun": False,
                     "IS BOSS": True, "Grenade Shakedown": 600, "Grenade Shakedown angle": 0, "Run people over": 250,
                     "Startup lag": 0, "Startup time": 240}
    },

    # |Others|----------------------------------------------------------------------------------------------------------
    # Rigel
    "Rigel":
        {"name": "Rigel",
         "faction": "Anomaly",
         "type": "Elite",
         "targeting range": R_MO, "targeting angle": D_HO, "stealth mod": S_LO, "stealth counter": C_MO,
         "wall hack": False, "health": H_HO * 12, "armour": 0, "damage resistances": F3_RESIT_H,
         # "wall hack": False, "health": 1, "armour": 0, "damage resistances": F3_RESIT_H,
         "thickness": 48,
         "vel max": V_LO * 0.8, "speed": V_LO * 0.8, "friction": V_LO * 0.8,
         "weapon": "Bloodhound Weaponry",

         "func input": "rigel_input",
         "func act": "rigel_act",
         "func draw": "rigel_draw",
         "sprites": "Sprites/Enemies/Bulwark.png", "on death": "rigel_on_death",
         "free var": {
             "IS BOSS": True,
             "Mech": MechRenderer.Mech(MechRenderer.rigel_mech, MechRenderer.rigel_palette, [0, -350]),
             "Move angle": -90,
             "Turn speed": 2,
             "Startup lag": 0,
             "Startup lag boost": 0,
             "Current attack": "Shoulder Bash",
             "Phase": 1,
             "Boost type": [],
             "Pos history": {
                 "1": {"Target": None, "History": []},
                 "2": {"Target": None, "History": []},
                 "3": {"Target": None, "History": []},
             },
             "Segments": {
                 "1": {"Pos": [0, 0], "Angle": 0},
                 "2": {"Pos": [0, 0], "Angle": 0},
                 "3": {"Pos": [0, 0], "Angle": 0},
             },
             "Missile Circus": 0,
             "Anti Missile Circus Spam": False,
             "Invert Raining Hell": False,
             "History limit": 15
         }
         },
    # Curtis
    "Curtis (Boss)": {
        "name": "Curtis", "faction": "Zoar Colonists",
        # "health": 200*4, "armour": 50, "damage resistances": CU_RESIT,
        "health": 1, "armour": 1, "damage resistances": CU_RESIT,
        "sprites": "Sprites/Player/Curtis.png",

        "dash": {"speed": DS_HO, "i-frames": 24, "charge": 25},
        # Weapons
        "targeting angle": 180, "targeting range": 512,

        "thickness": 16,
        "vel max": 6.25,
        "speed": 1.17,
        "friction": 1.15,

        "weapon": "Curtis' Arsenal",
        "skills": ["Kick Boss"],
        # AI
        "func input": "curtis_input", "func act": "curtis_act", "func draw": "enemy_draw_basic",
        "on death": "none",
        "stealth mod": S_LO, "stealth counter": C_LM,
        "wall hack": False,
        "free var": {"IS BOSS": True,
                     "Stamina": 300,
                     "Current attack": "Flower Volley",
                     "Startup lag": 0,
                     "Pattern pos": [0, 0]}
    },

    # THR-1 enemy version
    "Lord (Boss)": {
        "name": "Lord", "faction": "THR-1",
        "health": H_MH, "armour": A_MO, "damage resistances": LO_RESIT,
        "sprites": "Sprites/Player/THR-1/Lord.png",

        "thickness": T_MH, "vel max": V_MO, "speed": 2.2, "friction": 1.5,
        "dash": {"speed": DS_HO, "i-frames": 12, "charge": 35},
        # Weapons
        "weapon": "Saloum Mk-2", "skills": ["Gauntlet Punch", "Beast Mode"],
        # AI
        "func input": "lord_boss_input", "func act": "player_act", "func draw": "enemy_draw_basic", "on death":" thr_1_on_death",
        "targeting range": R_MH, "targeting angle": D_LM, "wall hack": False,
        "driving": DRIVE_MO,
        "free var": {"Ally waypoint": [0, 0], "IS BOSS": True}
    },
    # Emperor	    M       L/M     M       M/H     H       M       M/H     M       M       M       H       H       Jack of all trades
    "Emperor (Boss)": {
        "name": "Emperor", "faction": "THR-1",
        "health": H_MO, "armour": A_LM, "damage resistances": EM_RESIT, "sprites": "Sprites/Player/THR-1/Emperor.png",
        "thickness": T_MO,
        "vel max": V_MH,
        "speed": 2.2,
        "friction": 1.5,
        "dash": {"speed": DS_MO, "i-frames": 12, "charge": 35},
        # Weapons
        "weapon": "GunBlade", "skills": ["Stun Kick", "Mega Buff"],
        # AI
        "func input": "emperor_boss_input", "func act": "player_act", "func draw": "emperor_boss_draw", "on death":" thr_1_on_death",
        "targeting range": R_HO, "targeting angle": D_MO, "stealth mod": S_MO, "stealth counter": C_MH,
        "wall hack": True,
        "driving": DRIVE_MO,
        "free var": {"Ally waypoint": [0, 0], "Startup lag": 0, "Startup time": 60, "Kicked": 0, "Startup lag kick": 0, "kick cooldown": 120}
    },
    # Wizard        L/M     M       M/H     M       M       L/M     M       M       H       M       H       M       Area denial
    "Wizard (Boss)": {
        "name": "Wizard", "faction": "THR-1",
        "health": H_LM, "armour": A_MO, "damage resistances": WI_RESIT, "sprites": "Sprites/Player/THR-1/Wizard.png",
        "thickness": T_MO,
        "vel max": V_MO, "speed": 2.2, "friction": 1.5,
        "dash": {"speed": DS_MO, "i-frames": 12, "charge": 35},
        # Weapons
        "weapon": "Jeanne's Family Shotgun", "skills": ["Building", "All Guns Blazing"],
        # AI
        "func input": "wizard_boss_input", "func act": "player_act", "func draw": "enemy_draw_basic", "on death":" thr_1_on_death",
        "targeting range": R_MO, "targeting angle": D_MH, "stealth mod": S_LM, "stealth counter": C_MO,
        "wall hack": True,
        "driving": DRIVE_HO,
        "free var": {"Ally waypoint": [0, 0]}
    },
    # Sovreign       L/M     L/M     L       M/H     H++     M/H     H       L       L       L/M     L       M       Sniper recon
    "Sovereign (Boss)": {
        "name": "Sovereign", "faction": "THR-1",
        "health": H_LM, "armour": A_LM, "damage resistances": SO_RESIT, "sprites": "Sprites/Player/THR-1/Sovereign.png",
        "thickness": T_LO,
        "vel max": V_MH,
        "speed": 2.2,
        "friction": 1.5,
        "dash": {"speed": DS_LM, "i-frames": 12, "charge": 35},
        # Weapons
        "weapon": "St-Maurice", "skills": ["Cardboard box", "Detect Targets"],
        # AI
        "func input": "sovereign_boss_input", "func act": "player_act", "func draw": "enemy_draw_basic", "on death":" thr_1_on_death",
        "targeting range": R_HO * 1.5, "targeting angle": D_LM, "stealth mod": S_MH, "stealth counter": C_HO,
        "wall hack": True,
        "driving": DRIVE_LO,
        "free var": {"Ally waypoint": ENEMY_NO_OWNER, "Detect Targets Duration": 3 * 60, "Exposed blue ball timer": 0, "Startup lag": 0, "Startup time": 60}
    },
    # Duke	        M       L/M     M       H       M       H       M       L/M     L/M     H       H       H	    Plays with agro
    "Duke (Boss)": {
        "name": "Duke", "faction": "THR-1",
        "health": H_MO, "armour": A_LM, "damage resistances": DU_RESIT,
        "sprites": "Sprites/Player/THR-1/Duke.png",
        "thickness": T_LM,
        "vel max": V_HO,
        "speed": 2.2,
        "friction": 1.5,
        "dash": {"speed": DS_HO, "i-frames": 12, "charge": 35},
        # Weapons
        "weapon": "Chain Axe", "skills": ["Tail Swipe", "Smoke Screen"],
        # AI
        "func input": "duke_boss_input", "func act": "player_act", "func draw": "enemy_draw_basic", "on death":" thr_1_on_death",
        "targeting range": R_MO, "targeting angle": D_HO, "stealth mod": S_HO, "stealth counter": C_HO,
        "driving": DRIVE_LM,
        "wall hack": True,
        "free var": {"Ally waypoint": ENEMY_NO_OWNER}
    },
    # Jester	    L--     H++     H       L       L/M     L/M     H++     M/H     L/M     L--     H++     L       Primary support. Helps them not dying
    "Jester (Boss)": {
        "name": "Jester", "faction": "THR-1",
        "health": int(H_LO * 0.5), "armour": A_MH * 2, "damage resistances": JE_RESIT,
        "sprites": "Sprites/Player/THR-1/Jester.png",
        "thickness": T_MH,
        "vel max": V_LO,
        "speed": 2.2,
        "friction": 0.5,
        "dash": {"speed": DS_LO * 0.4, "i-frames": 12, "charge": 35},

        # Weapons
        "weapon": "Epicurean Medic Rifle", "skills": ["Discharge", "Robot Fuck Off"],
        # AI
        "func input": "jester_boss_input", "func act": "player_act", "func draw": "enemy_draw_basic", "on death":" thr_1_on_death",
        "targeting range": R_LM, "targeting angle": D_MH, "stealth mod": S_LM, "stealth counter": C_HO * 1.2,
        "wall hack": True,
        "driving": DRIVE_LM,
        "free var": {"Ally waypoint": [0, 0], "Startup lag": 0}
    },
    # Condor        H       H       M/H     L/M     M       L       L/M     M/H     M/H     M       L       L       Tank and cause debuffs
    "Condor (Boss)": {
        "name": "Condor", "faction": "THR-1",
        "health": H_HO, "armour": A_HO, "damage resistances": CO_RESIT,
        "sprites": "Sprites/Player/THR-1/Condor.png",

        "thickness": T_MH,
        "vel max": V_LM,
        "speed": 2.2,
        "friction": 0.8,
        "dash": {"speed": DS_LO, "i-frames": 12, "charge": 35},
        # Weapons
        "weapon": "Type 41 SMG", "skills": ["Armour Breaker", "Last Stand"],
        # AI
        "func input": "condor_boss_input", "func act": "player_act", "func draw": "enemy_draw_basic", "on death": "condor_boss_on_death",
        "targeting range": R_MO, "targeting angle": D_MO, "stealth mod": S_LO, "stealth counter": C_LM,
        "driving": DRIVE_MH,
        "wall hack": True,
        "free var": {"Ally waypoint": ENEMY_NO_OWNER}
    },
    # |No Name TSS|-----------------------------------------------------------------------------------------------------
    "Fish": {
        'name': 'Fish',
        'faction': 'Test',
        'type': 'long range',

        'targeting range': 0,
        'targeting angle': 0,
        'wall hack': False,

        'health': 120,
        'armour': 0,
        'damage resistances': {'Physical': 1, 'Fire': 1, 'Explosion': 1, 'Energy': 1, 'Melee': 1},

        'thickness': 15,
        'vel max': 5,
        'speed': 1.25,
        'friction': 1.25,
        'weapon': 'Fish weapon',

        'func input': 'enemy_input_fish',
        'func act': 'fish_act',
        'func draw': 'enemy_draw_basic',
        'sprites': 'Sprites/Enemies/Fish.png',
        'on death': 'on_death_fish',
        'free var': {'Health last frame': 120},
    },
    "Fish 2": {
        'name': 'Fish 2',
        'faction': 'Test',
        'type': 'long range',

        'targeting range': 224,
        'targeting angle': 100,
        'wall hack': False,

        'health': 120,
        'armour': 0,
        'damage resistances': {'Physical': 0, 'Fire': 0, 'Explosion': 0, 'Energy': 0, 'Melee': 0},

        'thickness': 15,
        'vel max': 5, 'speed': 1.25,
        'friction': 1.25,
        'weapon': 'Fish weapon 2',

        'func input': 'enemy_input_fish_2',
        'func act': 'enemy_act_type_1',
        'func draw': 'enemy_draw_basic',
        'sprites': 'Sprites/Enemies/Fish.png',
        'on death': 'on_death_fish',
        'free var': {'Stat to change': 'Speed'},
    },

    # Morgan's Pirates
    "Pirate Swordsman": {
        'name': 'Pirate',
        'faction': 'Pirate',
        'type': 'close range',

        'targeting range': 400,
        'targeting angle': 15,
        'wall hack': False,

        'health': H_LM,
        'armour': A_LO,
        'damage resistances': {'Physical': 1, 'Fire': 1, 'Explosion': 1, 'Energy': 1, 'Melee': 1},

        'thickness': 15,
        'vel max': 4,
        'speed': 1.5,
        'friction': 1.5,
        'weapon': 'Pirate Sword',

        'func input': 'enemy_input_crazies_type_1',
        'func act': 'enemy_act_type_1',
        'func draw': 'enemy_draw_basic',
        'sprites': 'Sprites/Enemies/Pirate Swordman.png',
        'on death': 'none',
        'free var': {}
    },
    "Pirate Axeman": {
        'name': 'Pirate',
        'faction': 'Pirate',
        'type': 'close range',

        'targeting range': 400,
        'targeting angle': 15,
        'wall hack': False,

        'health': H_LM,
        'armour': A_LM,
        'damage resistances': {'Physical': 1, 'Fire': 1, 'Explosion': 1, 'Energy': 1, 'Melee': 1},

        'thickness': 15,
        'vel max': 3,
        'speed': 1.5,
        'friction': 1.5,
        'weapon': 'Pirate Axe',

        'func input': 'enemy_input_crazies_type_1',
        'func act': 'enemy_act_type_1',
        'func draw': 'enemy_draw_basic',
        'sprites': 'Sprites/Enemies/Pirate Axeman.png',
        'on death': 'none',
        'free var': {}
    },
    "Pirate Grunt": {
        'name': 'Pirate',
        'faction': 'Pirate',
        'type': 'close range',

        'targeting range': 450,
        'targeting angle': 15,
        'wall hack': False,

        'health': H_LO,
        'armour': A_LO,
        'damage resistances': {'Physical': 1, 'Fire': 1, 'Explosion': 1, 'Energy': 1, 'Melee': 1},

        'thickness': 15,
        'vel max': 3,
        'speed': 1.5,
        'friction': 1.5,
        'weapon': 'Pirate Semi-auto',

        'weapon range mod': 1,
        'func input': 'enemy_input_grunt_type_1',
        'func act': 'enemy_act_type_1',
        'func draw': 'enemy_draw_basic',
        'sprites': 'Sprites/Enemies/Pirate Grunt.png',
        'on death': 'none',
        'free var': {}},
    "Pirate Shotgunner": {
        'name': 'Pirate',
        'faction': 'Pirate',
        'type': 'close range',

        'targeting range': 400,
        'targeting angle': 15,
        'wall hack': False,

        'health': H_LO,
        'armour': A_LO,
        'damage resistances': {'Physical': 1, 'Fire': 1, 'Explosion': 1, 'Energy': 1, 'Melee': 1},

        'thickness': 15,
        'vel max': 6,
        'speed': 1.25,
        'friction': 1.25,
        'weapon': 'Pirate Shotgun',

        'weapon range mod': 1.75,
        'func input': 'enemy_input_shotgunner_type_1',
        'func act': 'enemy_act_type_1',
        'func draw': 'enemy_draw_basic',
        'sprites': 'Sprites/Enemies/Pirate Shotgunner.png',
        'on death': 'none',
        'free var': {},
    },
    "Pirate Defensive Shotgunner": {
        'name': 'Pirate',
        'faction': 'Pirate',
        'type': 'close range',

        'targeting range': 300,
        'targeting angle': 15,
        'wall hack': False,

        'health': H_LO,
        'armour': A_LO,
        'damage resistances': {'Physical': 1, 'Fire': 1, 'Explosion': 1, 'Energy': 1, 'Melee': 1},

        'thickness': 15,
        'vel max': 6,
        'speed': 1.25,
        'friction': 1.25,
        'weapon': 'Pirate Shotgun',

        'func input': 'enemy_input_shotgunner_type_2',
        'func act': 'enemy_act_type_1',
        'func draw': 'enemy_draw_basic',
        'sprites': 'Sprites/Enemies/Pirate Shotgunner.png',
        'on death': 'none',
        'free var': {}, },
    "Pirate Sniper": {
        'name': 'Pirate',
        'faction': 'Pirate',
        'type': 'long range',

        'targeting range': 600,
        'targeting angle': 15,
        'wall hack': False,

        'health': H_LO,
        'armour': A_LO,
        'damage resistances': {'Physical': 1, 'Fire': 1, 'Explosion': 1, 'Energy': 1, 'Melee': 1},
        'thickness': 15, 'vel max': 3, 'speed': 1.25, 'friction': 1.25,
        'weapon': 'Pirate Rifle',

        'func input': 'enemy_input_sniper_type_1',
        'func act': 'enemy_act_type_1',
        'func draw': 'enemy_draw_basic',
        'sprites': 'Sprites/Enemies/Pirate Sniper.png',
        'on death': 'none',
        'free var': {'Startup lag': 0, 'Startup time': 120}
},
    "Pirate Railgunner": {
        'name': 'Pirate',
        'faction': 'Pirate',
        'type': 'long range',

        'targeting range': 600,
        'targeting angle': 15,
        'wall hack': True,

        'health': H_MO,
        'armour': A_LO,
        'damage resistances': {'Physical': 1, 'Fire': 1, 'Explosion': 1, 'Energy': 1, 'Melee': 1},

        'thickness': 15,
        'vel max': 3,
        'speed': 1.25,
        'friction': 1.25,
        'weapon': 'Pirate Railgun',

        'func input': 'enemy_input_sniper_type_1',
        'func act': 'enemy_act_type_1',
        'func draw': 'enemy_draw_basic',
        'sprites': 'Sprites/Enemies/Pirate Railgunner.png',
        'on death': 'none',
        'free var': {'Startup lag': 0, 'Startup time': 120},
    },
    "Pirate Demolisher": {
        'name': 'Pirate',
        'faction': 'Pirate',
        'type': 'long range',

        'targeting range': 600,
        'targeting angle': 15,
        'wall hack': False,

        'health': H_MO,
        'armour': A_MH,
        'damage resistances': {'Physical': 0.75, 'Fire': 1.5, 'Explosion': 0.125, 'Energy': 1, 'Melee': 1},

        'thickness': 15,
        'vel max': 5,
        'speed': 1.25,
        'friction': 1.25,
        'weapon': 'Pirate RocketL.',

        'func input': 'enemy_input_sniper_type_1',
        'func act': 'enemy_act_type_1',
        'func draw': 'enemy_draw_basic',
        'sprites': 'Sprites/Enemies/Pirate Demolisher.png',
        'on death': 'none',
        'free var': {'Startup lag': 0, 'Startup time': 120}
    },
    "Pirate Flamer": {
        'name': 'Pirate',
        'faction': 'Pirate',
        'type': 'close range',

        'targeting range': 550,
        'targeting angle': 15,
        'wall hack': False,

        'health': H_MH,
        'armour': 0,
        'damage resistances': {'Physical': 1, 'Fire': 1, 'Explosion': 1, 'Energy': 1, 'Melee': 1},

        'thickness': 15,
        'vel max': 5,
        'speed': 1.25,
        'friction': 1.25,
        'weapon': 'Pirate Flame Thrower',

        'weapon range mod': 1.75,
        'func input': 'enemy_input_shotgunner_type_1',
        'func act': 'enemy_act_type_1',
        'func draw': 'enemy_draw_basic',
        'sprites': 'Sprites/Enemies/Pirate Flamer.png',
        'on death': 'none',
        'free var': {},
    },
    "Pirate Buffer 1": {
        'name': 'Pirate',
        'faction': 'Pirate',
        'type': 'long range',

        'targeting range': 600,
        'targeting angle': 15,
        'wall hack': False,

        'health': H_MH,
        'armour': A_LO,
        'damage resistances': {'Physical': 1, 'Fire': 1, 'Explosion': 1, 'Energy': 1, 'Melee': 1},

        'thickness': 15,
        'vel max': 5,
        'speed': 1.25,
        'friction': 1.25,
        'weapon': 'Pirate Handgun',

        'func input': 'enemy_input_buffer_type_1',
        'func act': 'enemy_act_type_1',
        'func draw': 'enemy_draw_basic',
        'sprites': 'Sprites/Enemies/Pirate Buffer 1.png',
        'on death': 'none',
        'free var': {},
    },
    "Pirate Blunderbusser": {
        'name': 'Pirate',
        'faction': 'Pirate',
        'type': 'close range',

        'targeting range': 450,
        'targeting angle': 15,
        'wall hack': False,

        'health': H_MO,
        'armour': A_MO,
        'damage resistances': {'Physical': 1, 'Fire': 1, 'Explosion': 1, 'Energy': 1, 'Melee': 1},

        'thickness': 15,
        'vel max': 5,
        'speed': 1.25,
        'friction': 1.25,
        'weapon': 'Pirate Blunderbuss',

        'func input': 'enemy_input_buffer_type_1',
        'func act': 'enemy_act_type_1',
        'func draw': 'enemy_draw_basic',
        'sprites': 'Sprites/Enemies/Pirate Blunderbusser.png',
        'on death': 'none',
        'free var': {},
    },

    # NEST
    "Nest Trooper": {
        'name': 'Nest Trooper',
        'faction': 'Nest',
        'type': 'close range',

        'targeting range': 450,
        'targeting angle': 25,
        'wall hack': False,

        'health': H_LM,
        'armour': A_LM,
        'damage resistances': {'Physical': 1, 'Fire': 1, 'Explosion': 1, 'Energy': 1, 'Melee': 1},

        'thickness': 16,
        'vel max': 3.25,
        'speed': 1.5,
        'friction': 1.5,
        'weapon': 'Nest Machine Gun',

        'func input': 'enemy_input_nest_trooper',
        'func act': 'enemy_act_type_1',
        'func draw': 'enemy_draw_basic',
        'sprites': 'Sprites/Enemies/Nest Trooper.png',
        'on death': 'none',
        'free var': {'Formation': ['None', 0]}
    },
    "Nest Shotgunner": {
        'name': 'Nest Shotgunner',
        'faction': 'Nest',
        'type': 'close range',

        'targeting range': 450,
        'targeting angle': 25,
        'wall hack': False,

        'health': H_LM,
        'armour': A_LM,
        'damage resistances': {'Physical': 1, 'Fire': 1, 'Explosion': 1, 'Energy': 1, 'Melee': 1},

        'thickness': 16,
        'vel max': 3.25,
        'speed': 1.5,
        'friction': 1.5,
        'weapon': 'Nest Shotgun',

        'func input': 'enemy_input_nest_trooper',
        'func act': 'enemy_act_type_1',
        'func draw': 'enemy_draw_basic',
        'sprites': 'Sprites/Enemies/Nest Shotgunner.png',
        'on death': 'none',
        'free var': {'Formation': ['None', 0]}
    },
    "Nest Sniper": {
        'name': 'Nest Sniper',
        'faction': 'Nest',
        'type': 'long range',

        'targeting range': 600,
        'targeting angle': 15,
        'wall hack': False,

        'health': H_LM,
        'armour': A_LM,
        'damage resistances': {'Physical': 1, 'Fire': 1, 'Explosion': 1, 'Energy': 1, 'Melee': 1},

        'thickness': 16,
        'vel max': 3,
        'speed': 1.25,
        'friction': 1.25,
        'weapon': 'Nest Rifle',

        'func input': 'enemy_input_nest_sniper',
        'func act': 'enemy_act_type_1',
        'func draw': 'enemy_draw_basic',
        'sprites': 'Sprites/Enemies/Nest Sniper.png',
        'on death': 'none',
        'free var': {'Startup lag': 0, 'Startup time': 180, 'Formation': ['None', 0]}
    },
    "Nest Shield": {
        'name': 'Nest Shield',
        'faction': 'Nest',
        'type': 'close range',

        'targeting range': 450,
        'targeting angle': 25,
        'wall hack': False,

        'health': H_LM,
        'armour': A_MH,
        'damage resistances': {'Physical': 1, 'Fire': 1, 'Explosion': 1, 'Energy': 1, 'Melee': 1},

        'thickness': 16,
        'vel max': 3.25,
        'speed': 1.5,
        'friction': 1.5,
        'weapon': 'Nest Riot Pistol',

        'func input': 'enemy_input_nest_shield',
        'func act': 'enemy_act_type_1',
        'func draw': 'enemy_draw_basic',
        'sprites': 'Sprites/Enemies/Nest Shield.png',
        'on death': 'none',
        'free var': {'Formation': ['None', 0]}
    },
    "Nest Commander": {
        'name': 'Nest Commander',
        'faction': 'Nest',
        'type': 'close range',

        'targeting range': 450,
        'targeting angle': 25,
        'wall hack': False,

        'health': H_MO,
        'armour': A_MO,
        'damage resistances': {'Physical': 1, 'Fire': 1, 'Explosion': 1, 'Energy': 1, 'Melee': 1},

        'thickness': 16,
        'vel max': 2.75,
        'speed': 1.5,
        'friction': 1.5,
        'weapon': 'Nest Commander PDW',

        'func input': 'enemy_input_nest_commander',
        'func act': 'enemy_act_type_1',
        'func draw': 'enemy_draw_basic',
        'sprites': 'Sprites/Enemies/Nest Commander.png',
        'on death': 'none',
        'free var': {'Formation': ['None', 0]}
    },
    "Nest Flamer": {
        'name': 'Nest Flamer',
        'faction': 'Nest',
        'type': 'close range',

        'targeting range': 450,
        'targeting angle': 25,
        'wall hack': False,

        'health': H_MO,
        'armour': A_LM,
        'damage resistances': {'Physical': 1, 'Fire': 1, 'Explosion': 1, 'Energy': 1, 'Melee': 1},

        'thickness': 16,
        'vel max': 1.25,
        'speed': 0.25,
        'friction': 0.21,
        'weapon': 'Nest Flame Thrower',

        'func input': 'enemy_input_nest_flamer',
        'func act': 'enemy_act_type_1',
        'func draw': 'enemy_draw_basic',
        'sprites': 'Sprites/Enemies/Nest Flamer.png',
        'on death': 'none',
        'free var': {'Formation': ['None', 0]}
    },
    "Nest Heavy Trooper": {
        'name': 'Nest Heavy Trooper',
        'faction': 'Nest',
        'type': 'close range',

        'targeting range': 450,
        'targeting angle': 25,
        'wall hack': False,

        'health': H_MH,
        'armour': A_MO,
        'damage resistances': {'Physical': 1, 'Fire': 1, 'Explosion': 1, 'Energy': 1, 'Melee': 1},

        'thickness': 16,
        'vel max': 2,
        'speed': 0.125,
        'friction': 0.115,
        'weapon': 'Nest Heavy Machine Gun',

        'func input': 'enemy_input_nest_trooper',
        'func act': 'enemy_act_type_1',
        'func draw': 'enemy_draw_basic',
        'sprites': 'Sprites/Enemies/Nest Heavy Trooper.png',
        'on death': 'none',
        'free var': {'Formation': ['None', 0]}
    },
    "Nest Railgunner": {
        'name': 'Nest Railgunner',
        'faction': 'Nest',
        'type': 'long range',

        'targeting range': 600,
        'targeting angle': 15,
        'wall hack': True,

        'health': H_MO,
        'armour': A_MO,
        'damage resistances': {'Physical': 1, 'Fire': 1, 'Explosion': 1, 'Energy': 1, 'Melee': 1},

        'thickness': 16,
        'vel max': 3,
        'speed': 1.25,
        'friction': 1.25,
        'weapon': 'Nest Railgun',

        'func input': 'enemy_input_nest_sniper',
        'func act': 'enemy_act_type_1',
        'func draw': 'enemy_draw_basic',
        'sprites': 'Sprites/Enemies/Nest Railgunner.png',
        'on death': 'none',
        'free var': {'Startup lag': 0, 'Startup time': 180, 'Formation': ['None', 0]}
    },
    "Nest Demolisher": {
        'name': 'Nest Demolisher',
        'faction': 'Nest',
        'type': 'close range',

        'targeting range': 450,
        'targeting angle': 25,
        'wall hack': False,

        'health': H_MO,
        'armour': A_MH,
        'damage resistances': {'Physical': 1, 'Fire': 1, 'Explosion': 1, 'Energy': 1, 'Melee': 1},

        'thickness': 16,
        'vel max': 3.25,
        'speed': 1.5,
        'friction': 1.5,
        'weapon': 'Nest Grenade Launcher',

        'func input': 'enemy_input_nest_demolisher',
        'func act': 'enemy_act_type_1',
        'func draw': 'enemy_draw_basic',
        'sprites': 'Sprites/Enemies/Nest Demolisher.png',
        'on death': 'none',
        'free var': {'Formation': ['None', 0]}
    },
    "Nest Bunker": {
        'name': 'Nest Bunker',
        'faction': 'Nest',
        'type': 'close range',

        'targeting range': 200,
        'targeting angle': 35,
        'wall hack': False,

        'health': H_MO,
        'armour': A_MH,
        'damage resistances': {'Physical': 1, 'Fire': 1, 'Explosion': 1, 'Energy': 1, 'Melee': 1},

        'thickness': 16,
        'vel max': 3.25,
        'speed': 1.5,
        'friction': 1.5,
        'weapon': 'Nest Heavy Machine Gun Bunker',

        'func input': 'enemy_input_nest_bunker',
        'func act': 'enemy_act_type_1',
        'func draw': 'enemy_draw_basic',
        'sprites': 'Sprites/Enemies/Nest Bunker.png',
        'on death': 'none',
        'free var': {}
    },
    "Nest Cloaker": {
        'name': 'Nest Cloaker',
        'faction': 'Nest',
        'type': 'close range',

        'targeting range': 450,
        'targeting angle': 40,
        'wall hack': False,

        'health': H_MO,
        'armour': 0,
        'damage resistances': {'Physical': 1, 'Fire': 1, 'Explosion': 1, 'Energy': 1, 'Melee': 1},

        'thickness': 16,
        'vel max': 2.75,
        'speed': 1.5,
        'friction': 1.5,
        'weapon': 'Nest Knife',

        'func input': 'enemy_input_nest_cloaker',
        'func act': 'enemy_act_type_1',
        'func draw': 'enemy_draw_basic',
        'sprites': 'Sprites/Enemies/Nest Cloaker.png',
        'on death': 'none',
        'free var': {'Formation': ['None', 0]}
    },

    # Street Gangs of Zoar
    "Gang Pipe": {
        'name': 'Gang',
        'faction': 'Street Gang',
        'type': 'close range',

        'targeting range': 400,
        'targeting angle': 15,
        'wall hack': False,

        'health': 45,
        'armour': 0,
        'damage resistances': {'Physical': 1, 'Fire': 1, 'Explosion': 1, 'Energy': 1, 'Melee': 1},

        'thickness': 15,
        'vel max': 3,
        'speed': 1.5,
        'friction': 1.5,
        'weapon': 'Gang Pipe',

        'func input': 'enemy_input_crazies_type_1',
        'func act': 'enemy_act_type_1',
        'func draw': 'enemy_draw_basic',
        'sprites': 'Sprites/Enemies/Gang Pipe.png',
        'on death': 'none',
        'free var': {},
    },
    "Gang Grunt": {
        'name': 'Gang',
        'faction': 'Street Gang',
        'type': 'close range',

        'targeting range': 450,
        'targeting angle': 15,
        'wall hack': False,

        'health': 45,
        'armour': 0,
        'damage resistances': {'Physical': 1, 'Fire': 1, 'Explosion': 1, 'Energy': 1, 'Melee': 1},

        'thickness': 15,
        'vel max': 3,
        'speed': 1.5,
        'friction': 1.5,
        'weapon': 'Gang Semi-auto',

        'func input': 'enemy_input_grunt_type_1',
        'func act': 'enemy_act_type_1',
        'func draw': 'enemy_draw_basic',
        'sprites': 'Sprites/Enemies/Gang Grunt.png',
        'on death': 'none',
        'free var': {},
    },
    "Gang Shotgunner": {
        'name': 'Gang',
        'faction': 'Street Gang',
        'type': 'close range',

        'targeting range': 400,
        'targeting angle': 15,
        'wall hack': False,

        'health': 40,
        'armour': 0,
        'damage resistances': {'Physical': 1, 'Fire': 1, 'Explosion': 1, 'Energy': 1, 'Melee': 1},

        'thickness': 15,
        'vel max': 5,
        'speed': 1.25,
        'friction': 1.25,
        'weapon': 'Gang Shotgun',

        'func input': 'enemy_input_grunt_type_1',
        'func act': 'enemy_act_type_1',
        'func draw': 'enemy_draw_basic',
        'sprites': 'Sprites/Enemies/Gang Shotgunner.png',
        'on death': 'none',
        'free var': {}, },
    "Gang Defensive Shotgunner": {
        'name': 'Gang',
        'faction': 'Street Gang',
        'type': 'close range',

        'targeting range': 300,
        'targeting angle': 15,
        'wall hack': False,

        'health': 40,
        'armour': 0,
        'damage resistances': {'Physical': 1, 'Fire': 1, 'Explosion': 1, 'Energy': 1, 'Melee': 1},
        'thickness': 15,
        'vel max': 5,
        'speed': 1.25,
        'friction': 1.25,
        'weapon': 'Gang Shotgun',

        'func input': 'enemy_input_shotgunner_type_2',
        'func act': 'enemy_act_type_1',
        'func draw': 'enemy_draw_basic',
        'sprites': 'Sprites/Enemies/Gang Shotgunner.png',
        'on death': 'none',
        'free var': {}
    },
    "Gang Sniper": {
        'name': 'Gang',
        'faction': 'Street Gang',
        'type': 'long range',

        'targeting range': 500,
        'targeting angle': 15,
        'wall hack': False,

        'health': 40,
        'armour': 0,
        'damage resistances': {'Physical': 1, 'Fire': 1, 'Explosion': 1, 'Energy': 1, 'Melee': 1},
        'thickness': 15,
        'vel max': 5,
        'speed': 1.25,
        'friction': 1.25,
        'weapon': 'Gang Rifle',

        'func input': 'enemy_input_sniper_type_1',
        'func act': 'enemy_act_type_1',
        'func draw': 'enemy_draw_basic',
        'sprites': 'Sprites/Enemies/Gang Sniper.png',
        'on death': 'none',
        'free var': {'Startup lag': 0, 'Startup time': 90},
    },
    # Gang Heavy    # Uses gun with under barrel
    "Gang Biker": {
        'name': 'Gang',
        'faction': 'Street Gang',
        'type': 'close range',

        'targeting range': 450,
        'targeting angle': 15,
        'wall hack': False,

        'health': H_MO,
        'armour': A_LO,
        'damage resistances': {'Physical': 1, 'Fire': 1, 'Explosion': 1, 'Energy': 1, 'Melee': 1},

        'thickness': 15,
        "vel max": V_HO,
        "speed": 1.4,
        "friction": 0.35,
        'weapon': 'Gang Compact SMG',
        "driving": DRIVE_HO,

        'func input': 'enemy_input_moped',
        'func act': 'moped_act',
        'func draw': 'enemy_draw_gang_moped',
        'sprites': 'Sprites/Enemies/Gang Grunt.png',
        "weapon range mod": 1.5,
        'on death': 'on_death_kamikaze',
        'free var': {"Move angle": 0, "Target Move angle": 0, "Move vel": 0},
    },

    # Goon Faction
    # Grunt
    # Shotgunner
    # Sniper
    # Bruiser

    # Pasta Cook
    # Pizza Cook

    # *Woman*
    # Padre

    # Anomaly
    "Monolith": {
        'name': 'Monolith',
        'faction': 'Anomalies',
        'type': 'long range',

        'targeting range': 320,
        'targeting angle': 3,
        'wall hack': False,

        'health': H_HO,
        'armour': A_HO,
        'damage resistances': {'Physical': 1, 'Fire': 1, 'Explosion': 1, 'Energy': 1, 'Melee': 1},

        'thickness': 15,
        'vel max': 5,
        'speed': 1.25,
        'friction': 1.25,
        'weapon': 'Monolith',

        'func input': 'enemy_input_monolith',
        'func act': 'enemy_act_type_1',
        'func draw': 'enemy_draw_basic',
        'sprites': 'Sprites/Enemies/A1.png',
        'on death': 'none',
        'free var': {}
    },
    "Eye": {
        'name': 'Eye',
        'faction': 'Anomalies',
        'type': 'long range',

        'targeting range': 320,
        'targeting angle': 3,
        'wall hack': True,

        'health': H_HO,
        'armour': A_LO,
        'damage resistances': {'Physical': 1, 'Fire': 1, 'Explosion': 1, 'Energy': 1, 'Melee': 1},

        'thickness': 15,
        'vel max': 5,
        'speed': 1.25,
        'friction': 1.25,
        'weapon': 'Eye',

        'func input': 'enemy_input_eye',
        'func act': 'enemy_act_type_1',
        'func draw': 'enemy_draw_basic',
        'sprites': 'Sprites/Enemies/A2.png',
        'on death': 'none',
        'free var': {}
    },
    "Void": {
        'name': 'Void',
        'faction': 'Anomalies',
        'type': 'long range',

        'targeting range': 9223372036854775807,
        'targeting angle': 180,
        'wall hack': True,

        'health': H_LM,
        'armour': 0,
        'damage resistances': {'Physical': 1, 'Fire': 1, 'Explosion': 1, 'Energy': 1, 'Melee': 1},

        'thickness': 15,
        'vel max': 5,
        'speed': 1.25,
        'friction': 1.25,
        'weapon': 'Void',

        'func input': 'enemy_input_void',
        'func act': 'void_act',
        'func draw': 'enemy_draw_basic',
        'sprites': 'Sprites/Enemies/A3.png',
        'on death': 'none',
        'free var': {}
    },
    "Spook": {
        'name': 'Spook',
        'faction': 'Anomalies',
        'type': 'long range',

        'targeting range': 9223372036854775807,
        'targeting angle': 180,
        'wall hack': True,

        'health': 1,
        'armour': 0,
        'damage resistances': {'Physical': 1, 'Fire': 1, 'Explosion': 1, 'Energy': 1, 'Melee': 1},

        'thickness': 15,
        'vel max': 5,
        'speed': 1.25,
        'friction': 1.25,
        'weapon': 'Spook',

        'func input': 'enemy_input_void',
        'func act': 'void_act',
        'func draw': 'enemy_draw_basic',
        'sprites': 'Sprites/Enemies/SPOOK.png',
        'on death': 'none',
        'free var': {},
    },
    "Slime": {
        'name': 'Slime',
        'faction': 'Anomalies',
        'type': 'long range',

        'targeting range': 960,
        'targeting angle': 360,
        'wall hack': False,

        'health': H_LM,
        'armour': 0,
        'damage resistances': {'Physical': 1, 'Fire': 1, 'Explosion': 1, 'Energy': 1, 'Melee': 1},

        'thickness': 40,
        'vel max': 4,
        'speed': 0.015,
        'friction': 0.00125,
        'weapon': 'Eye',

        'func input': 'enemy_input_slime',
        'func act': 'enemy_act_type_1',
        'func draw': 'enemy_draw_slime',
        'sprites': 'Sprites/Enemies/A4.png',
        'on death': 'on_death_slime',
        'free var': {}
    },
    "Snake": {
        'name': 'Snake',
        'faction': 'Anomalies',
        'type': 'close range',

        'targeting range': 9223372036854775807,
        'targeting angle': 360,
        'wall hack': True,

        'health': H_MH,
        'armour': 0,
        'damage resistances': {'Physical': 1, 'Fire': 1, 'Explosion': 1, 'Energy': 1, 'Melee': 1},

        'thickness': 16,
        'vel max': 4,
        'speed': 4,
        'friction': 1.5,
        'weapon': 'Snake',

        'func input': 'enemy_input_snake',
        'func act': 'snake_act',
        'func draw': 'enemy_draw_basic',
        'sprites': 'Sprites/Enemies/A5.png',
        'on death': 'on_death_snake',
        'free var': {'Move Angle': 0, 'Delay mod': 0, 'Pos history': []}
    },

    # CommieBots
    "CommieBot.Hammer": {"name": "CommieBot.Hammer",
         "faction": "CommieBot",
         "type": "close range",
         "targeting range": 350,
         "targeting angle": 15,
         "wall hack": False,

         "health": H_MO,
         "armour": A_LO,

         "damage resistances": RESISTANCES_MACHINE,
         "thickness": 20,
         "vel max": 1,
         "speed": 1,
         "friction": 1,
         "weapon": "Hammer",
         "func input": "enemy_input_commie_type_1",
         "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_basic",
         "sprites": "Sprites/Enemies/Commiebot.Hammer.png",
         "on death": "none",
         "free var": {}},
    "CommieBot.Sickle": {"name": "CommieBot.Sickle",
         "faction": "CommieBot",
         "type": "close range",
         "targeting range": 350,
         "targeting angle": 15,
         "wall hack": False,
         "health": H_LO,
         "armour": 0,
         "damage resistances": RESISTANCES_MACHINE,
         "thickness": 15,
         "vel max": 5,
         "speed": 1.5,
         "friction": 1.5,
         "weapon": "Sickle",
         "func input": "enemy_input_commie_type_1",
         "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_basic",
         "sprites": "Sprites/Enemies/Commiebot.Sickle.png",
         "on death": "none",
         "free var": {}},
    "CommieBot.Kamikaze": {"name": "CommieBot.Kamikaze",
         "faction": "CommieBot",
         "type": "close range",
         "targeting range": 350,
         "targeting angle": 15,
         "wall hack": False,
         "health": H_LO,
         "armour": 0,
         "damage resistances": RESISTANCES_MACHINE,
         "thickness": 15,
         "vel max": 7,
         "speed": 2,
         "friction": 2,
         "weapon": "Sickle",
         "func input": "enemy_input_commie_type_1",
         "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_basic",
         "sprites": "Sprites/Enemies/Commiebot.Kamikaze.png",
         "on death": "on_death_kamikaze",
         "free var": {}},
    "CommieBot.Rifle": {"name": "CommieBot.Rifle",
         "faction": "CommieBot",
         "type": "close range",
         "targeting range": 550,
         "targeting angle": 15,
         "wall hack": False,
         "health": H_LM,
         "armour": 0,
         "damage resistances": RESISTANCES_MACHINE,

         "thickness": 15,
         "vel max": 3,
         "speed": 1.5,
         "friction": 1.5,

         "weapon": "Enemy Soviet Rifle",
         "func input": "enemy_input_commie_type_1",
         "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_basic",
         "sprites": "Sprites/Enemies/Commiebot.Rifle.png",
         "on death": "none",
         "free var": {}},
    "CommieBot.Molotov": {"name": "CommieBot.Molotov",
         "faction": "CommieBot",
         "type": "close range",

         "targeting range": 550,
         "targeting angle": 15,
         "wall hack": False,

         "health": H_LM,
         "armour": 0,
         "damage resistances": RESISTANCES_MACHINE,

         "thickness": 15,
         "vel max": 2,
         "speed": 1.5,
         "friction": 1.5,
         "weapon": "Enemy Molotov",

         "func input": "enemy_input_commie_type_1",
         "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_basic",
         "sprites": "Sprites/Enemies/Commiebot.Molotov.png",
         "on death": "none",
         "free var": {}},
    "CommieBot.Tank": {"name": "CommieBot.Tank",
         "faction": "CommieBot",
         "type": "close range",
         "targeting range": 350,
         "targeting angle": 15,
         "wall hack": False,

         "health": H_HO,
         "armour": A_HO,

         "damage resistances": RESISTANCES_MACHINE,
         "thickness": 20,
         "vel max": 1,
         "speed": 1,
         "friction": 1,
         "weapon": "Commie.Tank Cannon",
         "func input": "enemy_input_commie_type_1",
         "func act": "enemy_act_type_1",
         "func draw": "commie_bot_tank_draw",
         "sprites": "Sprites/Enemies/Commiebot.Hammer.png",
         "on death": "none",
         "free var": {}},
}


def how_many_attacks_to_kill_everyone(damage, damage_type):
    for repertory in [player_repertory, enemy_repertory]:
        print("___")
        for count, e in enumerate(repertory):
            health = repertory[e]["health"] + repertory[e]["armour"]
            attack_count = 0
            while health > 0:
                health -= damage * repertory[e]["damage resistances"][damage_type]
                attack_count += 1
            if count % 7 == 0:
                print(count)
            print(f'{repertory[e]["name"]} takes {attack_count} attacks')



unified_entity_repertory = {}
for x in [player_repertory, enemy_repertory]:
    for y in x:
        unified_entity_repertory.update({y: x[y]})


def fake_render(boss, WIN, CLOCK):
    bosses_to_draw = []
    for count, b in enumerate(boss):
        bosses_to_draw.append(Entity(enemy_repertory[b]))
        bosses_to_draw[-1].pos = [
            [-2, 0],
            [-55, -25],
            [-55, 25],
            [60, 25],
            [45, -35],
            [10, -45],
            [30, -12],
        ][count]
        bosses_to_draw[-1].angle = random.randint(-135, -45)
    for b in bosses_to_draw:
        b.aim_angle = b.angle + random.randint(-35, 35)
    bosses_to_draw[-1].free_var["Move angle"] = -130
    # boss_to_draw.free_var["Move angle"] -= 33
    # boss_to_draw.aim_angle -= 130 -90
    bosses_to_draw[-1].aim_angle = -145
    # bosses_to_draw[-1].time = 2
    bosses_to_draw[-1].angle = -160
    # bosses_to_draw[-1].free_var["Move angle"] = -145
    # bosses_to_draw[-1].free_var["Move angle"] = -145
    # bosses_to_draw[-1].free_var["Machine Gun Angle"] = -105
    # bosses_to_draw[-1].draw_angle = 125

    screenshot_taken = False

    while True:
        # Select

        keys = pg.key.get_pressed()
        Fun.needed_in_menu_and_game(WIN, keys)
        # |Draw|--------------------------------------------------------------------------------------------------------
        frame = pg.Surface((630//2, 450//2))
        surface_to_draw = frame
        WIN.fill(Fun.BLACK)

        surface_to_draw.fill(Fun.UI_COLOUR_BACKGROUND)

        for b in bosses_to_draw:
            # b.draw(surface_to_draw, [630//4, 450//4], )
            b.draw_actual(surface_to_draw, [630//4, 450//4])
        # boss_to_draw.pos[0] += 1
        # boss_to_draw.pos[1] += 1
        Fun.scale_render(WIN, surface_to_draw, CLOCK)
        pg.display.flip()
        CLOCK.tick(60)
        if not screenshot_taken:
            Fun.screenshot(WIN)
            screenshot_taken = True


def fake_render_mech_parts(boss, WIN, CLOCK):
    bosses_to_draw = []
    for count, b in enumerate(boss):
        bosses_to_draw.append(b)
        print(b)

    screenshot_taken = False

    while True:
        # Select

        keys = pg.key.get_pressed()
        Fun.needed_in_menu_and_game(WIN, keys)
        # |Draw|--------------------------------------------------------------------------------------------------------
        frame = pg.Surface((630//2, 450//2))
        surface_to_draw = frame
        WIN.fill(Fun.BLACK)

        surface_to_draw.fill(Fun.UI_COLOUR_BACKGROUND)

        for count, b in enumerate(bosses_to_draw):
            # b.draw(surface_to_draw, [630//4, 450//4])
            # b.draw(surface_to_draw, [630//4, 450//4])
            Fun.draw_spritestack(frame, b, [
            [630//4 + -96, 450//4],
            [630//4 + -32, 450//4],
            [630//4 + 32, 450//4],
            [630//4 + 96, 450//4],
        ][count], -75, height_diff=0.7)
        # boss_to_draw.pos[0] += 1
        # boss_to_draw.pos[1] += 1
        Fun.scale_render(WIN, surface_to_draw, CLOCK)
        pg.display.flip()
        CLOCK.tick(60)
        if not screenshot_taken:
            Fun.screenshot(WIN)
            screenshot_taken = True
#

everyone = [
    # 'Manager', 'Body Guard', 'Heavy Sniper', 'Radar Operator', 'Missile Operator', 'Marksman', 'Enforcer', 'Armed Shield Generator', 'AA Laser', 'Drone builder', 'Missile Battery', 'Shield Generator', 'Energy Generator', 'Drone',
    # 'Sculptor', 'Skirmisher', 'BoomStick', 'Smoker', 'Snare', 'Crusher', 'Assassin', 'Hover Tank', 'Gilgamesh',
    # 'Infantry', 'Flamer', 'Spotter', 'Artilleryman', 'Grenadier', 'Bulwark', 'Commanding Officer', 'Super Bulwark', 'Fire Support Mech', 'Attack Helicopter',
    # 'Rigel', 'Curtis',
    # 'Lord', 'Emperor', 'Wizard', 'Sovereign', 'Duke', 'Jester', 'Condor',
    # 'Fish', 'Fish 2',

    # 'Pirate Swordsman', 'Pirate Axeman', 'Pirate Grunt', 'Pirate Shotgunner', 'Pirate Defensive Shotgunner', 'Pirate Sniper', 'Pirate Railgunner', 'Pirate Demolisher', 'Pirate Flamer', 'Pirate Buffer 1', 'Pirate Blunderbusser',

    # 'Nest Trooper', 'Nest Shotgunner', 'Nest Sniper', 'Nest Shield', 'Nest Commander', 'Nest Flamer', 'Nest Heavy Trooper', 'Nest Railgunner', 'Nest Demolisher', 'Nest Bunker', 'Nest Cloaker',

    # 'Gang Pipe', 'Gang Grunt', 'Gang Shotgunner', 'Gang Defensive Shotgunner', 'Gang Sniper',

    # 'Monolith', 'Eye','Void', 'Spook', 'Slime', 'Snake',

    # 'CommieBot.Hammer', 'CommieBot.Sickle', 'CommieBot.Kamikaze', 'CommieBot.Rifle', 'CommieBot.Molotov'
]
