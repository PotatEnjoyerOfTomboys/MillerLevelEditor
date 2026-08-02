from random import uniform

import pygame as pg
import random
import math
import sys

import Fun
import Bullets
import Skills
import Particles
import Weapons
import Items
import Event


from Fun import none, enemy_entry_unlock
from Event import MissionEvent, loss_of_apc, trigger_constant


class Entity:
    __slots__=['agro', 'agro_decrease_rate', 'ai_state', 'aim_angle', 'angle', 'animation_counter', 'is_target', 'armour', 'armour_break', 'bullets_shot', 'collision_box', 'control', 'controller_angle', 'controller_control', 'crit', 'cutscene_mode', 'damage_taken', 'dash_allowed', 'dash_charge_time', 'dash_cooldown', 'dash_iframes', 'dash_speed', 'did_agro_raise', 'direction_angle', 'draw_aim_line', 'draw_angle', 'draw_rotated_dist', 'draw_targeting_range', 'driving', 'force_draw', 'free_var', 'friction', 'func_act', 'func_draw', 'func_input', 'health', 'input', 'input_mode', 'is_ally', 'is_boss', 'is_player', 'is_targeted', 'is_targeting', 'max_armour', 'max_health', 'mouse_control', 'mouse_pos', 'name', 'no_shoot_state', 'og_info', 'on_death', 'order_builder', 'pathfinding_old_positions', 'pos', 'reloading', 'resistances', 'running', 'shooting', 'shot_allowed', 'skills', 'sound_mod', 'speed', 'sprites', 'standing_still', 'status', 'stealth_counter', 'stealth_mod', 'target', 'targeting_angle', 'targeting_range', 'team', 'thiccness', 'time', 'upgrades', 'vel', 'vel_max', 'walking', 'wall_hack', 'weapon', 'weapon_draw_dist', 'owner', 'sprite_height']
    def __init__(self, info, team="Players", pos=[0, 0], start_angle=0):
        info = info.copy()
        self.og_info = info.copy()
        self.name = info["name"]
        self.team = team
        self.is_ally = False
        self.is_player = False
        self.is_boss = False
        self.crit = False
        self.owner = False

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
            if Fun.SPOOKY_DAY and self.name in player_repertory:
                self.sprites = self.sprites.split(".")[0]
                self.sprites += " - Halloween.png"
            sprite = Fun.get_image(self.sprites)
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
        self.weapon_draw_dist, self.draw_angle, self.draw_rotated_dist = 0, 0, 0
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
            self.func_input = getattr(sys.modules[__name__], self.func_input)
        self.func_act = info["func act"]
        if type(self.func_act) == str:
            self.func_act = getattr(sys.modules[__name__], self.func_act)
        self.func_draw = info["func draw"]
        if type(self.func_draw) == str:
            self.func_draw = getattr(sys.modules[__name__], self.func_draw)

        self.on_death = info["on death"]
        if type(self.on_death) == str:
            self.on_death = getattr(sys.modules[__name__], self.on_death)

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

    def draw(self, screen, scrolling):
        self.func_draw(self, screen, scrolling)
        #

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
            frame_to_get = self.animation_counter[action_type] // 7 % (
                    len(self.sprites[player_direction][action_type]) - 1) + 1

        # Draws the player
        sprite_drawn = self.sprites[player_direction][action_type][frame_to_get]
        WIN.blit(sprite_drawn, (self.pos[0] - self.sprite_height // 2 + scrolling[0], self.pos[1] - self.sprite_height // 2 + scrolling[1]))
    #


# print([p for p in dir(Entity)])


def draw_aim_line(self, entities):
    if not self.draw_aim_line:
        return
        # Get the max angle
        #
        #         "Startup lag": 0,
        #         "Startup time": 120
    draw_pos = Fun.move_with_vel_angle(self.pos, 20, self.aim_angle)
    angle = self.aim_angle
    drawing_pos = Fun.move_with_vel_angle(draw_pos, 20, angle)
    length = self.weapon.range + 20

    # Draw the lines
    mod = self.free_var["Startup lag"]/self.free_var["Startup time"]

    colour_index = [1]
    if "aim line colour" in self.free_var:
        colour_index = self.free_var["aim line colour"]
    bg_colour = [0, 0, 0]
    fg_colour = [0, 0, 0]
    for i in colour_index:
        bg_colour[i] = 125
    for i in colour_index:
        fg_colour[i] = 255 * mod

    entities["background particles"].append(Particles.LineParticle(drawing_pos, bg_colour, 1, length, angle, 1, 0))

    entities["background particles"].append(Particles.LineParticle(
        drawing_pos, fg_colour, 1, length * mod, angle, 3,
        0))


def draw_weapon(self, WIN, scrolling):
    draw_pos = [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]]
    angle_to_add = 0
    if self.reloading:
        angle_to_add = (360 / self.weapon.reload_time) * self.no_shoot_state

    # self.draw_angle
    drawing_pos = Fun.move_with_vel_angle(draw_pos, 6 + self.weapon_draw_dist, self.aim_angle)
    drawing_pos = Fun.move_with_vel_angle(drawing_pos, self.draw_rotated_dist, self.aim_angle + self.draw_angle)
    origin = [0, self.weapon.sprite.get_height() // 2]

    Fun.blitRotate(WIN, pg.transform.flip(self.weapon.sprite, True, -90 < self.aim_angle < 90),
                   drawing_pos, origin, 180 - self.aim_angle + angle_to_add + self.draw_angle)


# |Player inputs|-------------------------------------------------------------------------------------------------------
def player_act(self, entities, level):
    # |Aim system|--------------------------------------------------------------------------------------------------
    Fun.aim_system(self, self.weapon)
    # |Movement Input|----------------------------------------------------------------------------------------------
    Fun.movement_player(self, entities)
    # Fun.movement_entity(self)

    # |GunPlay|-----------------------------------------------------------------------------------------------------
    entities["UI particles"].append(Particles.AimPoint(self.mouse_pos))
    # if self.weapon.ammo == 0 and self.weapon.ammo_cost > 0:
    #     entities["UI particles"].append(
    #         Fun.FloatingTextType2([self.mouse_pos[0], self.mouse_pos[1] - 12],
    #                               18, Fun.write_textline("Input type Reload"), Fun.UI_COLOUR_TUTORIAL, 1)
    #     )
    self.weapon.passive(self, entities, level)
    if self.no_shoot_state == 0:
        # Reset variables
        self.reloading = False

        # Alternative fire
        # print(self.input)
        if self.input["Alt fire"]:
            self.weapon.alt_fire(self, entities, level)

        # |Main fire|-----------------------------------------------------------------------------------------------
        if self.input["Shoot"]:
            if self.weapon.ammo != 0 and self.shot_allowed:
                # |Main fire|-------------------------------------------------------------------------------------------
                self.shoot_bullet(entities, level)
                # tell if the trigger was pressed
                if not self.weapon.full_auto:
                    self.shot_allowed = False
            # if the trigger is not pressed and the weapon is not a full auto, allow to shoot for the next trigger press
            elif self.weapon.ammo == 0 and self.shot_allowed:
                Fun.play_sound(self.weapon.jamming_sound, "SFX")
                self.shot_allowed = False
        else:
            self.shot_allowed = True

        # |Reload|--------------------------------------------------------------------------------------------------
        if self.input["Reload"] and self.weapon.ammo_pool > 0:
            self.no_shoot_state, self.reloading = self.weapon.reload()

    else:
        self.no_shoot_state -= 1

    # |Skills|------------------------------------------------------------------------------------------------------
    Skills.skills_manager(self, entities, level)

    # |Status effects|----------------------------------------------------------------------------------------------
    # ha ha, Fun go brr
    Fun.status_manager(self, entities)

    # |Movement Output|---------------------------------------------------------------------------------------------
    # Make the player move
    Fun.movement_output(self, level)
    if self.draw_aim_line or self.weapon.laser_sight:
        entities["background particles"].append(Particles.LineParticle(
            Fun.move_with_vel_angle(self.pos, 20, self.aim_angle), Fun.BLUE, 1, self.weapon.range-20, self.aim_angle, 2, 0))
    # Give orders
    if self.order_builder["Cooldown"] <= 0:
        if self.order_builder["Current order"]:
            self.order_builder["Time limit"] -= 1
            # Write
            mod = 10
            pos = [self.pos[0] + 16, self.pos[1] - 48]
            entities["particles"].append(Particles.FloatingTextType3(pos.copy(), 18, self.order_builder["Current order"], Fun.AMBER, 1))
            pos[1] += mod
            for x in [
                f"{Fun.write_control(self, "Order Hold")}All Teammate",
                f"{Fun.write_control(self, "Order Follow")}Teammate 1",
                f"{Fun.write_control(self, "Order Attack")}Teammate 2",
                f"{Fun.write_control(self, "Order Act Free")}Teammate 3"]:
                pos[1] += mod
                entities["particles"].append(Particles.FloatingTextType3(pos.copy(), 18, x, Fun.AMBER, 1))
            pos[1] += mod
            entities["particles"].append(Particles.GrowingSquare([pos[0], pos[1], 120, 8], Fun.UI_COLOUR_NEW_BACKDROP, [0, 0], 1))
            entities["particles"].append(Particles.GrowingSquare([pos[0], pos[1], self.order_builder["Time limit"]//3, 8], Fun.AMBER_LIGHT, [0, 0], 1))

            # Choose who to give the order to
            if self.order_builder["Allow input"]:
                if self.input["Order Hold"]:
                    give_order(self, entities, [1, 2, 3])
                if self.input["Order Follow"]:
                    give_order(self, entities, [1])
                if self.input["Order Attack"]:
                    give_order(self, entities, [2])
                if self.input["Order Act Free"]:
                    give_order(self, entities, [3])
            elif not (self.input["Order Hold"] or self.input["Order Follow"] or self.input["Order Attack"] or self.input["Order Act Free"]):
                self.order_builder["Allow input"] = True

            # Reset if time out
            if self.order_builder["Time limit"] < 0:
                self.order_builder["Current order"] = False
                self.order_builder["Cooldown"] = 120
        else:
            # Choose the order
            opt = False
            if self.input["Order Hold"]:
                opt = True
                self.order_builder["Current order"] = "Hold"
            if self.input["Order Follow"]:
                opt = True
                self.order_builder["Current order"] = "Follow"
            if self.input["Order Attack"]:
                opt = True
                self.order_builder["Current order"] = "Attack"
            if self.input["Order Act Free"]:
                opt = True
                self.order_builder["Current order"] = "Freely"

            # Add cooldown
            if opt:

                self.order_builder["Allow input"] = False
                self.order_builder["Time limit"] =  120 * 3

    else:
        self.order_builder["Cooldown"] -= 1

    if self.armour_break:
        # Need a sound effect
        self.armour_break = False
        number_of_particle = 18
        for particles_to_add in range(360 // number_of_particle):
            entities["background particles"].append(Particles.RandomParticle2(
                [self.pos[0], self.pos[1]], Fun.GREEN, 2 * random.random(), random.randint(15, 45),
                                                        particles_to_add * number_of_particle,
                size=Fun.get_random_element_from_list([3, 4, 6])))


def vivianne_act(self, entities, level):
    player_act(self, entities, level)
    # Summon mechanic
    # "Summon cooldown time": 360, "Summon cooldown": 0, "Summon limit": 1, "Summon pool": [], "Active summons": []
    if self.free_var["Summon pool"]:
        summon_allowed = len(self.free_var["Active summons"]) < self.free_var["Summon limit"]
        if self.free_var["Summon cooldown"] == 0:
            if self.input["Interact"]:
                if summon_allowed:
                    # Select summon to spawn
                    valid_pool = []
                    for summon in self.free_var["Summon pool"]:
                        if summon not in self.free_var["Active summons"]:
                            valid_pool.append(summon)

                    if valid_pool:
                        Particles.random_particle_2_circle(entities, self.pos, 2.3333333333333333333333333333333, 15, 18,
                                                     colour=Fun.YELLOW, size=5)
                        selected_summon = player_repertory[Fun.get_random_element_from_list(valid_pool)]
                        entities["entities"].append(
                            Entity(
                                selected_summon,
                                pos=Fun.random_point_in_donut(self.pos, [2, 8]),
                                start_angle=self.aim_angle
                            ))
                        self.free_var["Active summons"].append(selected_summon["name"])
                        self.free_var["Summon cooldown"] = self.free_var["Summon cooldown time"]
                        entities["entities"][-1].owner = self
        else:
            self.free_var["Summon cooldown"] -= 1
        # Draw shit
        # "UI particles"    square, colour, growth, duration
        entities["UI particles"].append(Particles.Square([self.pos[0]+16, self.pos[1] - 8, 1, 4], Fun.DARK, 1))
        entities["UI particles"].append(Particles.Square([self.pos[0]+16, self.pos[1] - 4, 4, 4], Fun.DARK, 1))
        entities["UI particles"].append(Particles.Square([self.pos[0]+16, self.pos[1], 3, 4], Fun.DARK, 1))
        entities["UI particles"].append(Particles.Square([self.pos[0]+16, self.pos[1] + 4, 4, 4], Fun.DARK, 1))
        cooldown_time = 32 - round(32 * self.free_var["Summon cooldown"] / self.free_var["Summon cooldown time"])

        col = Fun.GRAY
        if summon_allowed:
            col = Fun.LIGHT_GRAY
        for x in range(4):
            p = cooldown_time - 4
            if p < 0:
                p += abs(p)
            dif = cooldown_time - p
            cooldown_time = p
            entities["UI particles"].append(Particles.Square([
                self.pos[0] + 16,
                self.pos[1] + [-8, -4, 0, 4][x],
                [1, 4, 3, 4][x],
                dif], col, 1))


def vivianne_summons_act(self, entities, level):
    # |Aim system|------------------------------------------------------------------------------------------------------
    Fun.aim_system(self, self.weapon)
    # |Movement Input|--------------------------------------------------------------------------------------------------
    Fun.movement_player(self, entities)

    # |GunPlay|---------------------------------------------------------------------------------------------------------
    self.weapon.passive(self, entities, level)
    if self.no_shoot_state == 0:
        # Reset variables
        self.reloading = False
        self.shooting = False

        # Alternative fire
        if self.input["Alt fire"]:
            self.weapon.alt_fire(self, entities, level)

        # |Main fire|---------------------------------------------------------------------------------------------------
        if self.input["Shoot"]:
            if self.weapon.ammo != 0 and self.shot_allowed:
                # |Main fire|-------------------------------------------------------------------------------------------
                self.shoot_bullet(entities, level)

                # tell if the trigger was pressed
                if not self.weapon.full_auto:
                    self.shot_allowed = False
            # if the trigger is not pressed and the weapon is not a full auto, allow to shoot for the next trigger press
            elif self.weapon.ammo == 0 and self.shot_allowed:
                Fun.play_sound(self.weapon.jamming_sound, "SFX")
                self.shot_allowed = False
        else:
            self.shot_allowed = True

        # |Reload|------------------------------------------------------------------------------------------------------
        if self.input["Reload"] and self.weapon.ammo_pool > 0:
            self.no_shoot_state, self.reloading = self.weapon.reload()
    else:
        self.no_shoot_state -= 1

    # |Status effects|--------------------------------------------------------------------------------------------------
    Fun.status_manager(self, entities)
    # |Movement Output|-------------------------------------------------------------------------------------------------
    # Make the player move
    Fun.movement_output(self, level)
    if self.draw_aim_line or self.weapon.laser_sight:
        entities["background particles"].append(Particles.LineParticle(
            Fun.move_with_vel_angle(self.pos, 20, self.aim_angle), Fun.BLUE, 1, self.weapon.range-20, self.aim_angle, 2, 0))

    self.force_draw = True
    if self.free_var["Life Limit"] == self.time:
        self.health = 0
        # vivianne_summons_on_death(self, entities, level)



def fortress_act(self, entities, level):
    vehicle_escort(self, level)
    angle = self.free_var["Move angle"] + 226 - 180
    pos = [self.pos[0], self.pos[1] - 16]
    pos = Fun.move_with_vel_angle(pos, 22.6274, angle)
    pos = Fun.move_with_vel_angle(pos, 20, self.aim_angle)
    # |Movement Input|----------------------------------------------------------------------------------------------
    self.running = False
    self.walking = False

    max_vel = self.vel_max

    # Handle double speed and slowness status
    if self.status["Slowness"]:
        max_vel *= 0.5
    if self.status["Double speed"]:
        max_vel *= 2

    # Checks for which direction the player must move
    # Rework it so that you are not faster when walking in diagonal, this should be fixed now
    if self.dash_cooldown <= 0:
        allow_correction = False
        speed = 0
        if self.input["Up"]:
            speed = 1
            allow_correction = True
        if self.input["Down"]:
            speed = -1
            allow_correction = True
        if self.input["Left"]:
            self.free_var["Move angle"] -= 3
        if self.input["Right"]:
            self.free_var["Move angle"] += 3
        self.vel = Fun.move_with_vel_angle(self.vel, self.speed * speed, self.free_var["Move angle"])

        if not Fun.check_point_in_circle(max_vel, 0, 0, self.vel[0], self.vel[1]) and allow_correction:
            self.vel = Fun.move_with_vel_angle([0, 0], max_vel * speed, self.free_var["Move angle"])
        self.walking = allow_correction

        if self.free_var["Move angle"] > 180:
            self.free_var["Move angle"] = -180 + (self.free_var["Move angle"] - 180)
        if self.free_var["Move angle"] < -180:
            self.free_var["Move angle"] = 180 - (self.free_var["Move angle"] + 180)

    self.standing_still = False
    if self.vel == [0, 0]:
        self.standing_still = True
    elif self.cutscene_mode:
        # This makes entities use their walking animation during cutscenes
        self.walking = True

    # Dash mechanic
    if self.dash_cooldown <= 0 and not self.standing_still and self.input["Dash"]:
        # Handle dash here
        Fun.play_sound("Player dash", modified_volume=0.25)
        dash_angle = self.free_var["Move angle"]
        self.dash_cooldown = self.dash_charge_time
        if self.status["Dash recovery up"] > 0:
            self.dash_cooldown //= 2
        self.vel = Fun.move_with_vel_angle(self.vel, self.dash_speed / self.friction * speed, dash_angle)
        for x in range(4):
            angle = dash_angle - 15 - 3.25 * 2 + x * 7.5 * 2
            entities["particles"].append(
                Particles.RandomParticle2(
                    Fun.move_with_vel_angle([self.pos[0], self.pos[1]], -4, angle),
                    Fun.WHITE, 1.5 + random.uniform(0, 2), 24, angle))

        if self.status["No damage"] < self.dash_iframes:
            self.status["No damage"] += self.dash_iframes
    self.dash_cooldown -= 1

    # |GunPlay|-----------------------------------------------------------------------------------------------------
    angle = self.aim_angle
    drawing_pos = pos
    length = self.weapon.range + 20

    # Draw the lines
    entities["background particles"].append(Particles.LineParticle(drawing_pos, Fun.RED, 1, length, angle, 1, 0))

    entities["UI particles"].append(Particles.AimPoint(self.mouse_pos))
    self.weapon.passive(self, entities, level)
    if self.no_shoot_state == 0:
        # Reset variables
        self.reloading = False

        if self.input["Alt fire"]:
            self.weapon.alt_fire(self, entities, level)

        # |Main fire|-----------------------------------------------------------------------------------------------
        if self.input["Shoot"]:
            if self.weapon.ammo != 0 and self.shot_allowed:
                # |Main fire|-------------------------------------------------------------------------------------------
                self.shoot_bullet(entities, level)

                # tell if the trigger was pressed
                if not self.weapon.full_auto:
                    self.shot_allowed = False
            # if the trigger is not pressed and the weapon is not a full auto, allow to shoot for the next trigger press
            elif self.weapon.ammo == 0 and self.shot_allowed:
                Fun.play_sound(self.weapon.jamming_sound, "SFX")
                self.shot_allowed = False
        else:
            self.shot_allowed = True

        # |Reload|--------------------------------------------------------------------------------------------------
        if self.input["Reload"] and self.weapon.ammo_pool > 0:
            self.no_shoot_state, self.reloading = self.weapon.reload()
    else:
        self.no_shoot_state -= 1

    Fun.aim_system(self, self.weapon)

    # |Skills|------------------------------------------------------------------------------------------------------
    Skills.skills_manager(self, entities, level)

    # |Status effects|----------------------------------------------------------------------------------------------
    # ha ha, Fun go brr
    Fun.status_manager(self, entities)

    # |Movement Output|---------------------------------------------------------------------------------------------
    # Make the player move
    Fun.movement_output(self, level)
    for e in entities["entities"]:
        if e == self: continue
        if self.collision_box.colliderect(e.collision_box):
            e.vel = Fun.move_with_vel_angle(e.vel, 2, Fun.angle_between(e.collision_box.center, self.pos))
            if e.team != self.team:
                Fun.damage_calculation(e, round(abs(self.vel[0]) + abs(self.vel[1])) * 5, "Melee", death_message="Ran over")
            pass
    if self.draw_aim_line or self.weapon.laser_sight:
        entities["background particles"].append(Particles.LineParticle(
            Fun.move_with_vel_angle(self.pos, 20, self.aim_angle), Fun.BLUE, 1, self.weapon.range-20, self.aim_angle, 2, 0))
    # Give orders
    if self.order_builder["Cooldown"] <= 0:
        if self.order_builder["Current order"]:
            self.order_builder["Time limit"] -= 1
            # Write
            mod = 10
            pos = [self.pos[0] + 16, self.pos[1] - 48]
            entities["particles"].append(Particles.FloatingTextType3(pos.copy(), 18, self.order_builder["Current order"], Fun.AMBER, 1))
            pos[1] += mod
            for x in [
                f"{Fun.write_control(self, "Order Hold")}All Teammate",
                f"{Fun.write_control(self, "Order Follow")}Teammate 1",
                f"{Fun.write_control(self, "Order Attack")}Teammate 2",
                f"{Fun.write_control(self, "Order Act Free")}Teammate 3"]:
                pos[1] += mod
                entities["particles"].append(Particles.FloatingTextType3(pos.copy(), 18, x, Fun.AMBER, 1))
            pos[1] += mod
            entities["particles"].append(Particles.GrowingSquare([pos[0], pos[1], 120, 8], Fun.UI_COLOUR_NEW_BACKDROP, [0, 0], 1))
            entities["particles"].append(Particles.GrowingSquare([pos[0], pos[1], self.order_builder["Time limit"]//3, 8], Fun.AMBER_LIGHT, [0, 0], 1))

            # Choose who to give the order to
            if self.order_builder["Allow input"]:
                if self.input["Order Hold"]:
                    give_order(self, entities, [1, 2, 3])
                if self.input["Order Follow"]:
                    give_order(self, entities, [1])
                if self.input["Order Attack"]:
                    give_order(self, entities, [2])
                if self.input["Order Act Free"]:
                    give_order(self, entities, [3])
            elif not (self.input["Order Hold"] or self.input["Order Follow"] or self.input["Order Attack"] or self.input["Order Act Free"]):
                self.order_builder["Allow input"] = True

            # Reset if time out
            if self.order_builder["Time limit"] < 0:
                self.order_builder["Current order"] = False
                self.order_builder["Cooldown"] = 240
        else:
            # Choose the order
            opt = False
            if self.input["Order Hold"]:
                opt = True
                self.order_builder["Current order"] = "Hold"
            if self.input["Order Follow"]:
                opt = True
                self.order_builder["Current order"] = "Follow"
            if self.input["Order Attack"]:
                opt = True
                self.order_builder["Current order"] = "Attack"
            if self.input["Order Act Free"]:
                opt = True
                self.order_builder["Current order"] = "Freely"

            # Add cooldown
            if opt:

                self.order_builder["Allow input"] = False
                self.order_builder["Time limit"] =  120 * 3

    else:
        self.order_builder["Cooldown"] -= 1

    if self.armour_break:
        # Need a sound effect
        self.armour_break = False
        number_of_particle = 18
        for particles_to_add in range(360 // number_of_particle):
            entities["background particles"].append(Particles.RandomParticle2(
                [self.pos[0], self.pos[1]], Fun.GREEN, 2 * random.random(), random.randint(15, 45),
                                                        particles_to_add * number_of_particle,
                size=Fun.get_random_element_from_list([3, 4, 6])))


def buggy_act(self, entities, level):
    vehicle_escort(self, level)
    angle = self.free_var["Move angle"] + 226 - 180
    pos = [self.pos[0], self.pos[1] - 16]
    pos = Fun.move_with_vel_angle(pos, 22.6274, angle)
    pos = Fun.move_with_vel_angle(pos, 20, self.aim_angle)
    # |Movement Input|----------------------------------------------------------------------------------------------
    self.running = False
    self.walking = False

    max_vel = self.vel_max

    # Handle double speed and slowness status
    if self.status["Slowness"]:
        max_vel *= 0.5
    if self.status["Double speed"]:
        max_vel *= 2

    # Checks for which direction the player must move
    # Rework it so that you are not faster when walking in diagonal, this should be fixed now
    if self.dash_cooldown <= 0:
        allow_correction = False
        speed = 0
        if self.input["Up"]:
            speed = 1
            allow_correction = True
        if self.input["Down"]:
            speed = -1
            allow_correction = True

        mod = 0.7
        angle_type = "Move angle"
        if self.skills[0].recharge == 0:
            angle_type = "Target Move angle"
            mod = 2
        self.free_var["Move vel"] = abs(self.vel[0]) + abs(self.vel[1])

        # Fun.move_angle_toward_target_angle(real_angle, target_angle, rate)
        turn_vel = self.free_var["Move vel"] * 0.8
        if self.free_var["Move vel"] > 0 and turn_vel < 1:
            turn_vel = 1
        if turn_vel > 4:
            turn_vel = 4
        if self.input["Left"]:
            self.free_var["Target Move angle"] -= turn_vel
        if self.input["Right"]:
            self.free_var["Target Move angle"] += turn_vel
        self.free_var["Target Move angle"] = Fun.angle_value_limiter(self.free_var["Target Move angle"])
        self.free_var["Move angle"] = Fun.move_angle_toward_target_angle(self.free_var["Move angle"], self.free_var["Target Move angle"], turn_vel * mod)

        self.vel = Fun.move_with_vel_angle(self.vel, self.speed * speed, self.free_var[angle_type])
        if not Fun.check_point_in_circle(max_vel, 0, 0, self.vel[0], self.vel[1]) and allow_correction:
            self.vel = Fun.move_with_vel_angle([0, 0], max_vel * speed, self.free_var[angle_type])
        self.walking = allow_correction
    #
    self.standing_still = False
    if self.vel == [0, 0]:
        self.standing_still = True
    elif self.cutscene_mode:
        # This makes entities use their walking animation during cutscenes
        self.walking = True

    # Dash mechanic
    if self.dash_cooldown <= 0 and not self.standing_still and self.input["Dash"]:
        # Handle dash here
        Fun.play_sound("Player dash", modified_volume=0.25)
        dash_angle = self.free_var["Move angle"]
        self.dash_cooldown = self.dash_charge_time
        if self.status["Dash recovery up"] > 0:
            self.dash_cooldown //= 2
        self.vel = Fun.move_with_vel_angle(self.vel, self.dash_speed / self.friction * speed, dash_angle)
        for x in range(4):
            angle = dash_angle - 15 - 3.25 * 2 + x * 7.5 * 2
            entities["particles"].append(
                Particles.RandomParticle2(
                    Fun.move_with_vel_angle([self.pos[0], self.pos[1]], -4, angle),
                    Fun.WHITE, 1.5 + random.uniform(0, 2), 24, angle))

        if self.status["No damage"] < self.dash_iframes:
            self.status["No damage"] += self.dash_iframes
    self.dash_cooldown -= 1

    # |GunPlay|-----------------------------------------------------------------------------------------------------
    length = self.weapon.range + 20

    # Draw the lines
    entities["background particles"].append(Particles.LineParticle(self.pos, Fun.RED, 1, length, self.free_var["Move angle"], 1, 0))

    entities["UI particles"].append(Particles.AimPoint(self.mouse_pos))
    self.weapon.passive(self, entities, level)
    if self.no_shoot_state == 0:
        # Reset variables
        self.reloading = False

        if self.input["Alt fire"]:
            self.weapon.alt_fire(self, entities, level)

        # |Main fire|-----------------------------------------------------------------------------------------------
        if self.input["Shoot"]:
            if self.weapon.ammo != 0 and self.shot_allowed:
                # |Main fire|-------------------------------------------------------------------------------------------
                self.shoot_bullet(entities, level)

                # tell if the trigger was pressed
                if not self.weapon.full_auto:
                    self.shot_allowed = False
            # if the trigger is not pressed and the weapon is not a full auto, allow to shoot for the next trigger press
            elif self.weapon.ammo == 0 and self.shot_allowed:
                Fun.play_sound(self.weapon.jamming_sound, "SFX")
                self.shot_allowed = False
        else:
            self.shot_allowed = True

        # |Reload|--------------------------------------------------------------------------------------------------
        if self.input["Reload"] and self.weapon.ammo_pool > 0:
            self.no_shoot_state, self.reloading = self.weapon.reload()
    else:
        self.no_shoot_state -= 1

    Fun.aim_system(self, self.weapon)

    # |Skills|------------------------------------------------------------------------------------------------------
    Skills.skills_manager(self, entities, level)

    # |Status effects|----------------------------------------------------------------------------------------------
    # ha ha, Fun go brr
    Fun.status_manager(self, entities)

    # |Movement Output|---------------------------------------------------------------------------------------------
    # Make the player move
    Fun.movement_output(self, level)
    for e in entities["entities"]:
        if e == self: continue
        if self.collision_box.colliderect(e.collision_box):
            e.vel = Fun.move_with_vel_angle(e.vel, 2, Fun.angle_between(e.collision_box.center, self.pos))
            if e.team != self.team:
                Fun.damage_calculation(e, round(abs(self.vel[0]) + abs(self.vel[1])) * 5, "Melee", death_message="Ran over")
            pass
    if self.draw_aim_line or self.weapon.laser_sight:
        pos = Fun.move_with_vel_angle(self.pos, -24, self.free_var["Move angle"])
        entities["background particles"].append(Particles.LineParticle(
            [pos[0], pos[1]-14], Fun.BLUE, 1, self.weapon.range-20,
            self.aim_angle, 2, 0))
    # Give orders
    if self.order_builder["Cooldown"] <= 0:
        if self.order_builder["Current order"]:
            self.order_builder["Time limit"] -= 1
            # Write
            mod = 10
            pos = [self.pos[0] + 16, self.pos[1] - 48]
            entities["particles"].append(Particles.FloatingTextType3(pos.copy(), 18, self.order_builder["Current order"], Fun.AMBER, 1))
            pos[1] += mod
            for x in [
                f"{Fun.write_control(self, "Order Hold")}All Teammate",
                f"{Fun.write_control(self, "Order Follow")}Teammate 1",
                f"{Fun.write_control(self, "Order Attack")}Teammate 2",
                f"{Fun.write_control(self, "Order Act Free")}Teammate 3"]:
                pos[1] += mod
                entities["particles"].append(Particles.FloatingTextType3(pos.copy(), 18, x, Fun.AMBER, 1))
            pos[1] += mod
            entities["particles"].append(Particles.GrowingSquare([pos[0], pos[1], 120, 8], Fun.UI_COLOUR_NEW_BACKDROP, [0, 0], 1))
            entities["particles"].append(Particles.GrowingSquare([pos[0], pos[1], self.order_builder["Time limit"]//3, 8], Fun.AMBER_LIGHT, [0, 0], 1))

            # Choose who to give the order to
            if self.order_builder["Allow input"]:
                if self.input["Order Hold"]:
                    give_order(self, entities, [1, 2, 3])
                if self.input["Order Follow"]:
                    give_order(self, entities, [1])
                if self.input["Order Attack"]:
                    give_order(self, entities, [2])
                if self.input["Order Act Free"]:
                    give_order(self, entities, [3])
            elif not (self.input["Order Hold"] or self.input["Order Follow"] or self.input["Order Attack"] or self.input["Order Act Free"]):
                self.order_builder["Allow input"] = True

            # Reset if time out
            if self.order_builder["Time limit"] < 0:
                self.order_builder["Current order"] = False
                self.order_builder["Cooldown"] = 240
        else:
            # Choose the order
            opt = False
            if self.input["Order Hold"]:
                opt = True
                self.order_builder["Current order"] = "Hold"
            if self.input["Order Follow"]:
                opt = True
                self.order_builder["Current order"] = "Follow"
            if self.input["Order Attack"]:
                opt = True
                self.order_builder["Current order"] = "Attack"
            if self.input["Order Act Free"]:
                opt = True
                self.order_builder["Current order"] = "Freely"

            # Add cooldown
            if opt:

                self.order_builder["Allow input"] = False
                self.order_builder["Time limit"] =  120 * 3

    else:
        self.order_builder["Cooldown"] -= 1

    if self.armour_break:
        # Need a sound effect
        self.armour_break = False
        number_of_particle = 18
        for particles_to_add in range(360 // number_of_particle):
            entities["background particles"].append(Particles.RandomParticle2(
                [self.pos[0], self.pos[1]], Fun.GREEN, 2 * random.random(), random.randint(15, 45),
                                                        particles_to_add * number_of_particle,
                size=Fun.get_random_element_from_list([3, 4, 6])))


# Keyboard input
def player_input_keyboard(self, entities, level):
    Fun.keyboard_mouse_input(self, pg.key.get_pressed(), pg.mouse.get_pressed(3))

    width, height = pg.display.get_surface().get_size()
    slide_width, slide_height = Fun.FRAME_MAX_SIZE  # 1.4
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
    if slide_width > width or slide_height > height:
        if width > height * 1.4:
            slide_width = slide_width * height / slide_height
            slide_height = height
        elif width < height * 1.4:
            slide_height = slide_height * width / slide_width
            slide_width = width
    mouse_pos = pg.mouse.get_pos()
    render_rect = (width // 2 - slide_width // 2, height // 2 - slide_height // 2, slide_width, slide_height)
    self.mouse_pos = [(mouse_pos[0] - render_rect[0]) * (Fun.FRAME_MAX_SIZE[0] / slide_width) - entities["scrolling"][0],
                      (mouse_pos[1] - render_rect[1]) * (Fun.FRAME_MAX_SIZE[1] / slide_height) - entities["scrolling"][1]]
    self.angle = Fun.angle_between(self.mouse_pos, self.pos)
    Fun.stunned_manager(self)


# Controller input
def player_input_controller_1(self, entities, level):
    Fun.controller_input(self, gamepad_index=0)
    Fun.stunned_manager(self)


def player_input_controller_2(self, entities, level):
    Fun.controller_input(self, gamepad_index=1)
    Fun.stunned_manager(self)


def player_input_controller_3(self, entities, level):
    Fun.controller_input(self, gamepad_index=2)
    Fun.stunned_manager(self)


def player_input_controller_4(self, entities, level):
    Fun.controller_input(self, gamepad_index=3)
    Fun.stunned_manager(self)


def give_order(self, entities, targets):
    self.order_builder["Cooldown"] = 240
    allies_found = 0
    for x in entities["entities"]:
        # Make sure to not give the order to an enemy
        if x.team != self.team:
            continue
        # or the player 1
        if x == self:
            continue
        allies_found += 1
        # Check if the ally is the intended target
        if allies_found in targets:
            x.ai_state = self.order_builder["Current order"]
            # Special case for follow
            if self.order_builder["Current order"] == "Follow":
                x.free_var["Ally waypoint"] = self
            # Special case for hold
            if self.order_builder["Current order"] == "Hold":
                x.free_var["Ally waypoint"] = self.mouse_pos.copy()
    self.order_builder["Current order"] = False


# |Pathfinding|---------------------------------------------------------------------------------------------------------
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


# |General use|---------------------------------------------------------------------------------------------------------
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


# Component
def entity_get_aim_move_target(self, target):
    aim_target = self.target.pos.copy()
    self.angle = Fun.angle_between(aim_target, self.pos)
    return aim_target, target.copy(), Fun.distance_between(target, self.pos)


def entity_maintain_weapon_range(self, og_dist, move_target, get_closer, get_away=64):
    if og_dist > get_closer:
        self.input["Right"] = self.pos[0] < move_target[0]
        self.input["Left"] = self.pos[0] > move_target[0]
        self.input["Down"] = self.pos[1] < move_target[1]
        self.input["Up"] = self.pos[1] > move_target[1]

    if og_dist < get_away:
        self.input["Right"] = self.pos[0] > move_target[0]
        self.input["Left"] = self.pos[0] < move_target[0]
        self.input["Down"] = self.pos[1] > move_target[1]
        self.input["Up"] = self.pos[1] < move_target[1]


def entity_shoot_no_startup_lag(self, og_dist, engage_range):
    self.input["Shoot"] = self.weapon.ammo > 0 and og_dist < engage_range


def entity_shoot_with_startup_lag(self, og_dist, engage_range):
    if self.weapon.ammo > 0 and og_dist < engage_range and self.free_var['Startup lag'] == 0 and self.status["Stunned"] == 0:
        self.free_var['Startup lag'] += 1


def entity_shoot_startup_handler(self):
    if self.free_var['Startup lag'] > 0:
        self.draw_aim_line = True
        self.input["Shoot"] = start_up_lag_handler(self, self.free_var["Startup time"])
        if not self.target:
            self.free_var['Startup lag'] = 0


def entity_shoot_melee(self, og_dist, engage_range):
    pass


def entity_spread_apart(self, entities, spread_dist=32):
    for e in entities["entities"]:
        if 0 < Fun.distance_between(e.pos, self.pos) < spread_dist:
            self.input["Right"] = self.pos[0] > e.pos[0]
            self.input["Left"] = self.pos[0] < e.pos[0]
            self.input["Down"] = self.pos[1] > e.pos[1]
            self.input["Up"] = self.pos[1] < e.pos[1]
            break


def entity_escort_ally(self, entities, level, escort_list=("VIP", "Shock"), escort_dist=48, look_dist=512):
    for e in entities["entities"]:
        if e.name not in escort_list:
            continue
        if Fun.wall_between(e.pos, self.pos, level):
            continue
        if look_dist > Fun.distance_between(e.pos, self.pos) > escort_dist:
            self.input["Right"] = self.pos[0] < e.pos[0]
            self.input["Left"] = self.pos[0] > e.pos[0]
            self.input["Down"] = self.pos[1] < e.pos[1]
            self.input["Up"] = self.pos[1] > e.pos[1]
        return


def entity_dash_when_targeted(self, no_shoot_threshold=0, threshold=0.3):
    if self != self.target.target:
        return
    self.input["Dash"] = self.target.no_shoot_state <= no_shoot_threshold and random.random() < threshold


def entity_move_toward_point(self, move_target, dist):
    if dist < Fun.distance_between(self.pos, move_target):
        self.input["Right"] = self.pos[0] < move_target[0]
        self.input["Left"] = self.pos[0] > move_target[0]
        self.input["Down"] = self.pos[1] < move_target[1]
        self.input["Up"] = self.pos[1] > move_target[1]


def entity_get_enemy_count(self, entities, goal=10, dist=256, entity_type="entities"):
    enemy_count = 0
    for e in entities[entity_type]:
        if e.team == self.team:
            continue
        if Fun.distance_between(e.pos, self.pos) < dist:
            enemy_count += 1
            if enemy_count > goal:
                break
    return enemy_count > goal


def entity_get_ally_count(self, entities, goal=10, dist=256, entity_type="entities"):
    enemy_count = 0
    for e in entities[entity_type]:
        if e.team != self.team:
            continue
        if Fun.distance_between(e.pos, self.pos) < dist:
            enemy_count += 1
            if enemy_count > goal:
                break
    return enemy_count > goal


def entity_find_main_group(self, entities, dist=128):
    allies = []
    for count, e in enumerate(entities["entities"]):
        if count > 3: break
        if e.team != self.team: continue
        allies.append(e)

    main_group = self.pos.copy()
    control_num = 0
    for a in allies:
        if not a.is_player: continue
        temp = 0
        for aa in allies:
            if Fun.distance_between(a.pos, aa.pos) < dist:
                temp += 1
        if control_num < temp:
            main_group = a.pos.copy()

    return main_group


def entity_find_teammate(self, entities, target="Sovereign", check_limit=3):
    for count, e in enumerate(entities["entities"]):
        if count > check_limit: break
        if e.team != self.team: continue
        if e.name != target: continue
        return e.pos.copy()
    return False


def fortress_move_toward_point(self, move_target, dist):
    if dist < Fun.distance_between(self.pos, move_target):
        angle = Fun.angle_between(move_target, self.pos)
        self.input["Right"] = self.free_var["Move angle"] < angle
        self.input["Left"] = self.free_var["Move angle"] > angle

        if not -(180 - 4) + angle < self.free_var["Move angle"] < 180 - 4 + angle:
            self.input["Right"] = self.free_var["Move angle"] > angle
            self.input["Left"] = self.free_var["Move angle"] < angle

        self.input["Down"] = False
        mod = [5, 6, 7, 8, 10][self.driving]
        self.input["Up"] = angle - mod < self.free_var["Move angle"] < angle + mod


def fortress_move_away_point(self, move_target, dist):
    if dist > Fun.distance_between(self.pos, move_target):
        angle = Fun.angle_between(move_target, self.pos)
        self.input["Right"] = self.free_var["Move angle"] < angle
        self.input["Left"] = self.free_var["Move angle"] > angle

        if not -(180 - 4) + angle < self.free_var["Move angle"] < 180 - 4 + angle:
            self.input["Right"] = self.free_var["Move angle"] > angle
            self.input["Left"] = self.free_var["Move angle"] < angle

        self.input["Down"] = angle - 12 < self.free_var["Move angle"] < angle + 12
        self.input["Up"] = False
        # self.input["Up"] = angle - mod < self.free_var["Move angle"] < angle + mod


def buggy_move_toward_point(self, move_target, dist):
    if dist < Fun.distance_between(self.pos, move_target):
        angle = Fun.angle_between(move_target, self.pos)
        self.input["Right"] = self.free_var["Move angle"] < angle
        self.input["Left"] = self.free_var["Move angle"] > angle

        if not -(180 - 4) + angle < self.free_var["Move angle"] < 180 - 4 + angle:
            self.input["Right"] = self.free_var["Move angle"] > angle
            self.input["Left"] = self.free_var["Move angle"] < angle

        self.input["Down"] = False
        mod = [8, 10, 12, 14, 16][self.driving]
        self.input["Up"] = angle - mod < self.free_var["Move angle"] < angle + mod or (self.input["Right"] or self.input["Left"]) and self.time % 3 != 0


def buggy_move_away_point(self, move_target, dist):
    if dist > Fun.distance_between(self.pos, move_target):
        angle = Fun.angle_between(move_target, self.pos)
        self.input["Left"] = self.free_var["Move angle"] < angle
        self.input["Right"] = self.free_var["Move angle"] > angle

        if not -(180 - 4) + angle < self.free_var["Move angle"] < 180 - 4 + angle:
            self.input["Left"] = self.free_var["Move angle"] > angle
            self.input["Right"] = self.free_var["Move angle"] < angle

        self.input["Up"] = False
        mod = [8, 10, 12, 14, 16][self.driving]
        self.input["Down"] = angle - mod < self.free_var["Move angle"] < angle + mod or (self.input["Right"] or self.input["Left"]) and self.time % 3 != 0


# |Targeting|-----------------------------------------------------------------------------------------------------------
def entity_target_detection(self, entities, level):
    # Used by the enemy AI able to find targets
    # Might make them capable of patrolling

    if self.time % 240 == 0 or not self.target:
        self.is_target = False
        self.target = False
        target_check = self.targeting_range
        # I might have to remake the whole targeting system
        control_agro = -25
        for p in entities["entities"]:
            if p.health <= 0 or self.team == p.team:
                continue
            if control_agro > p.agro:
                continue

            if not Fun.wall_between(self.pos, p.pos, level) or self.wall_hack or p.status["Visible"] > 0:
                if p.status["Stealth"] > 0 and not p.status["Visible"] > 0:
                    continue
                detection_modifier = p.stealth_mod * self.stealth_counter

                if detection_modifier > 1: detection_modifier = 1
                if p.status["Visible"] > 0: detection_modifier = 1

                # Check if the potential target is in detection range
                if Fun.check_point_in_cone(target_check // 6 * detection_modifier,
                        self.pos[0], self.pos[1], p.pos[0], p.pos[1],
                        self.angle, self.targeting_angle * 3) or \
                        Fun.check_point_in_cone(target_check * detection_modifier,
                                            self.pos[0], self.pos[1], p.pos[0], p.pos[1],
                                            self.angle, self.targeting_angle)\
                        or Fun.check_point_in_circle(target_check // 10, self.pos[0], self.pos[1], p.pos[0], p.pos[1]):
                    self.target = p
                    self.is_target = True
                    control_agro = p.agro

        # Check for sounds
        if not self.target:
            for sound in entities["sounds"]:
                if self.team == sound.source:
                    continue
                if Fun.check_point_in_circle(sound.radius, sound.pos[0], sound.pos[1], self.pos[0], self.pos[1]):
                    self.angle = Fun.angle_between(sound.pos, self.pos)
    target_angle = 0
    target_pos = False
    wall_in = False

    if self.target:
        self.target.is_targeted = True
        # If the target is dead, reset targeting
        if self.target.health <= 0:
            self.target = False
            return target_pos, target_angle, wall_in

        target_angle = self.target.angle
        target_pos = self.target.pos.copy()
        # Pathfinding
        # results = pathfinding(self, level)
        results = universal_pathfinding(self, level, target_pos)
        if results:
            # entities["particles"].append(Fun.GrowingCircle(results, Fun.WHITE, 0, 1, 32, 8))
            target_pos = results
            wall_in = True

    return target_pos, target_angle, wall_in


def entity_target_detection_healer(self, entities, level):
    # Used by the enemy AI able to find targets
    # Might make them capable of patrolling

    if self.time % 240 == 0 or not self.target:
        self.is_target = False
        self.target = False
        target_check = self.targeting_range
        # I might have to remake the whole targeting system
        control_health = 1
        for p in entities["entities"]:
            if self.team != p.team and p != self:
                continue
            if control_health < p.health / p.max_health:
                continue
            if not Fun.wall_between(self.pos, p.pos, level) or self.wall_hack:

                # Check if the potential target is in detection range
                if Fun.check_point_in_cone(target_check // 6,
                        self.pos[0], self.pos[1], p.pos[0], p.pos[1], self.angle, self.targeting_angle * 3) or \
                        Fun.check_point_in_cone(target_check,
                                            self.pos[0], self.pos[1], p.pos[0], p.pos[1],
                                            self.angle, self.targeting_angle)\
                        or Fun.check_point_in_circle(target_check // 10, self.pos[0], self.pos[1], p.pos[0], p.pos[1]):
                    self.target = p
                    self.is_target = True
                    control_health = p.health / p.max_health
    target_angle = 0
    target_pos = False
    wall_in = False

    if self.target:
        # If the target is dead, reset targeting
        if self.target.health <= 0:
            self.target = False
            return target_pos, target_angle, wall_in

        target_angle = self.target.angle
        target_pos = self.target.pos.copy()
        # Pathfinding
        # results = pathfinding(self, level)
        results = universal_pathfinding(self, level, target_pos)
        if results:
            # entities["particles"].append(Fun.GrowingCircle(results, Fun.WHITE, 0, 1, 32, 8))
            target_pos = results
            wall_in = True

    return target_pos, target_angle, wall_in


def entity_target_simple(self, entities, level):
    # Used by the enemy AI able to find targets
    # Might make them capable of patrolling

    if self.time % 240 == 0 or not self.target:
        self.is_target = False
        self.target = False
        target_check = self.targeting_range
        # I might have to remake the whole targeting system
        control_agro = -25
        for p in entities["entities"]:
            if p.health <= 0 or self.team == p.team:
                continue
            if control_agro > p.agro:
                continue

            if p.status["Stealth"] > 0 and not p.status["Visible"] > 0:
                continue
            detection_modifier = p.stealth_mod * self.stealth_counter

            if detection_modifier > 1: detection_modifier = 1
            if p.status["Visible"] > 0: detection_modifier = 1

            # Check if the potential target is in detection range
            if Fun.check_point_in_cone(target_check // 6 * detection_modifier,
                    self.pos[0], self.pos[1], p.pos[0], p.pos[1],
                    self.angle, self.targeting_angle * 3) or \
                    Fun.check_point_in_cone(target_check * detection_modifier,
                                        self.pos[0], self.pos[1], p.pos[0], p.pos[1],
                                        self.angle, self.targeting_angle)\
                    or Fun.check_point_in_circle(target_check // 10, self.pos[0], self.pos[1], p.pos[0], p.pos[1]):
                self.target = p
                self.is_target = True
                control_agro = p.agro

        # Check for sounds
        if not self.target:
            for sound in entities["sounds"]:
                if self.team == sound.source:
                    continue
                if Fun.check_point_in_circle(sound.radius, sound.pos[0], sound.pos[1], self.pos[0], self.pos[1]):
                    self.angle = Fun.angle_between(sound.pos, self.pos)
    target_angle = 0
    target_pos = False
    wall_in = False

    if self.target:
        self.target.is_targeted = True
        # If the target is dead, reset targeting
        if self.target.health <= 0:
            self.target = False
            return target_pos, target_angle, wall_in

        target_angle = self.target.angle
        target_pos = self.target.pos.copy()
        # Pathfinding
        # results = pathfinding(self, level)
        results = universal_pathfinding(self, level, target_pos)
        if results:
            # entities["particles"].append(Fun.GrowingCircle(results, Fun.WHITE, 0, 1, 32, 8))
            target_pos = results
            wall_in = True
    return target_pos, target_angle, wall_in


def agro_system(self):
    if self.did_agro_raise > 0:
        self.did_agro_raise -= self.agro_decrease_rate
    elif self.agro > 0 and self.time % 4 == 0:
        self.agro -= 1


# |Ally fire control|---------------------------------------------------------------------------------------------------
def basic_fire_control(self, entities, level, target, wall_in):
    self.input["Shoot"] = random.randint(0, self.weapon.fire_rate) == 0 and \
                          Fun.check_point_in_circle_new(self.weapon.range * 0.8, self.pos, target) and \
                          not wall_in
    # Reloading
    self.input["Reload"] = self.weapon.ammo == 0 and self.weapon.ammo_pool > 0


def lord_fire_control(self, entities, level, target, wall_in):
    basic_fire_control(self, entities, level, target, wall_in)

    self.input["Skill 2"] = entity_get_enemy_count(self, entities, goal=5, dist=256) and \
                            self.ai_state in ["Hold", "Attack", "Freely"]
    self.input["Skill 1"] = Fun.distance_between(target, self.pos) < 128


def gunblade_fire_control(self, entities, level, target, wall_in):
    if not melee_fire_control(self, entities, level, target, wall_in):
        self.input["Reload"] = self.weapon.ammo == 0 and self.weapon.ammo_pool > 0
        entity_shoot_with_startup_lag(self, Fun.distance_between(target, self.pos), 7 * 30)
        if self.free_var['Startup lag'] > 0:
            # self.draw_aim_line = self.weapon.laser_sight
            self.input["Alt fire"] = True
            self.input["Shoot"] = start_up_lag_handler(self, self.free_var["Startup time"])
        return
    self.input["Skill 1"] = True
    self.input["Skill 2"] = entity_get_enemy_count(self, entities, goal=5, dist=256)


def emperor_gun_fire_control(self, entities, level, target, wall_in):
    if not basic_fire_control(self, entities, level, target, wall_in):
        self.input["Reload"] = self.weapon.ammo == 0 and self.weapon.ammo_pool > 0
        entity_shoot_with_startup_lag(self, Fun.distance_between(target, self.pos), 7 * 30)
        if self.free_var['Startup lag'] > 0:
            # self.draw_aim_line = self.weapon.laser_sight
            self.input["Alt fire"] = True
            self.input["Shoot"] = start_up_lag_handler(self, self.free_var["Startup time"])
        return
    self.input["Skill 1"] = True
    self.input["Skill 2"] = entity_get_enemy_count(self, entities, goal=5, dist=256)


def wizard_fire_control(self, entities, level, target, wall_in):
    basic_fire_control(self, entities, level, target, wall_in)

    skill_1 = self.skills[0]
    if skill_1.recharge >= skill_1.recharge_max:
        self.input["Shoot"] = False
        self.input["Skill 1"] = True
        self.input["Interact"] = random.random() < 0.25


def wizard_radio_fire_control(self, entities, level, target, wall_in):
    basic_fire_control(self, entities, level, target, wall_in)
    self.input["Alt fire"] = self.input["Shoot"]
    # Add an option to switch ammo type?

    skill_1 = self.skills[0]
    if skill_1.recharge >= skill_1.recharge_max:
        self.input["Shoot"] = False
        self.input["Skill 1"] = True
        self.input["Interact"] = random.random() < 0.25


def mortar_fire_control(self, entities, level, target, wall_in):
    basic_fire_control(self, entities, level, target, wall_in)
    self.input["Alt fire"] = self.input["Shoot"]


def condor_fire_control(self, entities, level, target, wall_in):
    basic_fire_control(self, entities, level, target, wall_in)
    self.input["Skill 1"] = Fun.distance_between(target, self.pos) < 128 and self.target.armour > 0


def condor_shotgun_fire_control(self, entities, level, target, wall_in):
    basic_fire_control(self, entities, level, target, wall_in)
    self.input["Alt fire"] = Fun.distance_between(target, self.pos) < 96
    self.input["Skill 1"] = Fun.distance_between(target, self.pos) < 128 and self.target.armour > 0


def melee_fire_control(self, entities, level, target, wall_in):
    if Fun.distance_between(target, self.pos) <= self.weapon.range:
        # combo_stage = self.free_var[self.weapon.name]["Combo stage"]
        try:
            basic_thres = self.free_var[self.weapon.name]["basic threshold"]
            if type(basic_thres) == list:
                basic_thres = basic_thres[self.free_var[self.weapon.name]["Combo stage"]]
            self.input["Shoot"] = self.free_var[self.weapon.name]["Press time"] < basic_thres  # - 10 * combo_stage
        except KeyError:
            return False
        return True
    return False


def melee_fire_control_no_stopping(self, entities, level, target, wall_in):
    try:
        if Fun.distance_between(target, self.pos) <= self.weapon.range or self.free_var[self.weapon.name]["Press time"] > 0:
        # combo_stage = self.free_var[self.weapon.name]["Combo stage"]
            basic_thres = self.free_var[self.weapon.name]["basic threshold"]
            if type(basic_thres) == list:
                basic_thres = basic_thres[self.free_var[self.weapon.name]["Combo stage"]]
            self.input["Shoot"] = self.free_var[self.weapon.name]["Press time"] < basic_thres # or self.free_var[f"{self.weapon.name}"]["Press time"] > 0 # - 10 * combo_stage

            return True
        return False
    except KeyError:
        return False


def chain_axe_fire_control(self, entities, level, target, wall_in):
    dist = Fun.distance_between(target, self.pos)
    if dist <= 128:
        self.input["Shoot"] = self.weapon.free_var["Press time"] < dist
    else:
        # smoke screen when he's targeted and not in range to attack
        allow = False
        for e in entities["entities"]:
            if e.target != self:
                continue
            allow = True
            break
        self.input["Skill 2"] = allow


def hook_swords_fire_control(self, entities, level, target, wall_in):
    dist = Fun.distance_between(target, self.pos)
    melee_fire_control(self, entities, level, target, wall_in)
    if not dist <= 128:
        # smoke screen when he's targeted and not in range to attack
        allow = False
        for e in entities["entities"]:
            if e.target != self:
                continue
            allow = True
            break
        self.input["Skill 2"] = allow


def gun_fu_fire_control(self, entities, level, target, wall_in):
    dist = Fun.distance_between(target, self.pos)
    if dist <= self.weapon.range:
        self.input["Shoot"] = self.time % self.weapon.fire_rate * 3 == 0
        self.input["Alt fire"] = dist <= 128
    else:
        # smoke screen when he's targeted and not in range to attack
        allow = False
        for e in entities["entities"]:
            if e.target != self:
                continue
            allow = True
            break
        self.input["Skill 2"] = allow


def medic_rifle_fire_control(self, entities, level, target, wall_in):
    if self.target.health < self.target.max_health - self.weapon.bullet_info[3]:
        self.input["Shoot"] = random.randint(0, self.weapon.fire_rate) == 0 and \
                              Fun.check_point_in_circle_new(self.weapon.range * 0.33, self.pos, target) and \
                              not wall_in
    # Reloading
    self.input["Reload"] = self.weapon.ammo == 0 and self.weapon.ammo_pool > 0


def stretcher_fire_control(self, entities, level, target, wall_in):
    self.input["Shoot"] = Fun.check_point_in_circle_new(self.weapon.range * 1.1, self.pos, target)
    # Reloading
    # self.input["Reload"] = self.weapon.ammo == 0 and self.weapon.ammo_pool > 0


def shield_generator_fire_control(self, entities, level, target, wall_in):
    self.input["Shoot"] = random.randint(0, self.weapon.fire_rate) == 0 and \
                          Fun.check_point_in_circle_new(self.weapon.range * 0.8, self.pos, target) and \
                          not wall_in
    # Reloading
    # self.input["Reload"] = self.weapon.ammo == 0 and self.weapon.ammo_pool > 0


def war_and_peace_fire_control(self, entities, level, target, wall_in):
    self.input["Shoot"] = random.randint(0, self.weapon.fire_rate) == 0 and \
                          Fun.check_point_in_circle_new(self.weapon.range, self.pos, target) and \
                          not wall_in
    self.input["Alt fire"] = Fun.check_point_in_circle_new(self.weapon.range * 1.2, self.pos, target)
    # Reloading
    self.input["Reload"] = self.weapon.ammo == 0 and self.weapon.ammo_pool > 0


def cutlass_fire_control(self, entities, level, target, wall_in):
    if not melee_fire_control(self, entities, level, target, wall_in):
        self.input["Reload"] = self.weapon.ammo == 0 and self.weapon.ammo_pool > 0
        entity_shoot_with_startup_lag(self, Fun.distance_between(target, self.pos), 6 * 80)
        if self.free_var['Startup lag'] > 0:
            # self.draw_aim_line = self.weapon.laser_sight
            self.input["Alt fire"] = True
            self.input["Shoot"] = start_up_lag_handler(self, self.free_var["Startup time"])
    self.input["Skill 1"] = True
    self.input["Skill 2"] = entity_get_enemy_count(self, entities, goal=5, dist=256)


def vivianne_fire_control(self, entities, level, target, wall_in):
    self.input["Shoot"] = random.randint(0, self.weapon.fire_rate) == 0 and \
                          Fun.check_point_in_circle_new(self.weapon.range * 0.8, self.pos, target) and \
                          not wall_in
    # Reloading
    self.input["Reload"] = self.weapon.ammo == 0 and self.weapon.ammo_pool > 0
    self.input["Skill 1"] = entity_get_enemy_count(self, entities, goal=2, dist=512) and random.random() < 0.5
    self.input["Skill 2"] = not self.input["Skill 1"]


def vivianne_melee_fire_control(self, entities, level, target, wall_in):
    melee_fire_control(self, entities, level, target, wall_in)
    self.input["Skill 1"] = entity_get_enemy_count(self, entities, goal=2, dist=512) and random.random() < 0.5
    self.input["Skill 2"] = not self.input["Skill 1"]


def c4_fire_control(self, entities, level, target, wall_in):
    self.input["Shoot"] = random.randint(0, self.weapon.fire_rate*8) == 0 and \
                          Fun.check_point_in_circle_new(self.weapon.range * 0.8, self.pos, target) and \
                          not wall_in
    # Reloading
    self.input["Reload"] = self.weapon.ammo == Fun.get_random_element_from_list([7, 4, 0]) and self.weapon.ammo_pool > 0


def fortress_fire_control(self, entities, level, target, wall_in):
    basic_fire_control(self, entities, level, target, wall_in)
    if self.driving == 4:
        if Fun.distance_between(self.pos, target) < 128:
            self.input["Dash"] = self.angle - 9 < self.free_var["Move angle"] < self.angle + 9


def buggy_fire_control(self, entities, level, target, wall_in):
    self.input["Shoot"] = random.randint(0, self.weapon.fire_rate) == 0 and \
                          Fun.check_point_in_cone(
                              self.weapon.range * 0.8, self.pos[0], self.pos[1],
                              target[0], target[1], self.free_var["Move angle"], 30) and \
                          not wall_in
    # Reloading
    self.input["Reload"] = self.weapon.ammo == 0 and self.weapon.ammo_pool > 0
    if self.driving == 4:
        if Fun.distance_between(self.pos, target) < 128:
            self.input["Dash"] = self.angle - 9 < self.free_var["Move angle"] < self.angle + 9


ALLY_FIRE_CONTROL = {
    "Lord": {
        "Saloum Mk-2": lord_fire_control,
        "GMG-04B": lord_fire_control,
        "Big Iron": lord_fire_control},
    "Emperor": {
        "GunBlade": gunblade_fire_control,
        "Corrine's Old Rifle": emperor_gun_fire_control,
        "Oversized stun baton": gunblade_fire_control},
    "Wizard": {
        "Jeanne's Family Shotgun": wizard_fire_control,
        "Custom Mk18 Laser cutter": wizard_fire_control,
        "Crippled Laddie FCS Radio": wizard_radio_fire_control},
    "Sovereign": {
        "St-Maurice": basic_fire_control,
        "St-Laurent Gen 1": basic_fire_control,
        "Mk16 Flare Mortar": mortar_fire_control},
    "Duke": {
        "Chain Axe": chain_axe_fire_control,
        "Hook Swords": hook_swords_fire_control,
        "Gun and Ballistic Knife": gun_fu_fire_control},
    "Jester": {
        "Epicurean Medic Rifle": medic_rifle_fire_control,
        "Nihilist Stretcher": stretcher_fire_control,
        "Stoic Shield generator": shield_generator_fire_control},
    "Condor": {
        "Type 41 SMG": condor_fire_control,
        "Type 23 Shotgun": condor_shotgun_fire_control, # Give a way to use the shield later.
        "Type 47 Rifle": condor_fire_control},

    "Curtis": {
        "Standard Shotgun": basic_fire_control,
        "War and Peace": war_and_peace_fire_control,
        "Hunk of Steel": melee_fire_control},

    "Doppelgänger": {
        "Standard Shotgun": basic_fire_control,
        "War and Peace": war_and_peace_fire_control,
        "Hunk of Steel": melee_fire_control},
    "Lawrence": {
        "Lawrence's Cutlass & Flintlock": cutlass_fire_control,
        "Captain's Axe & Blunderbuss": cutlass_fire_control,
        "Musket .360": cutlass_fire_control},
    "Mark": {
        "Mark's Real Rifle": basic_fire_control,
        "Type 30 Rifle": basic_fire_control,
        "C4": c4_fire_control},
    "Vivianne": {
        "Vivianne's Rifle": vivianne_fire_control,
        "Vivianne's Shotgun": vivianne_fire_control,
        "Vivianne's Leg": vivianne_melee_fire_control},

    "Fortress": {"Fortress Machine Gun": fortress_fire_control},
    "Sand Buggy": {"Buggy Gun": buggy_fire_control},
}


# |Ally Skill Control|--------------------------------------------------------------------------------------------------
def basic_skill_control(self, entities, level):
    pass


def wizard_skill_control(self, entities, level):
    lord_in_beast_mode = False
    enemy_count = 0
    for e in entities["entities"]:
        if e.team == self.team:
            if e.name == "Lord":
                if e.skills[1].active:
                    lord_in_beast_mode = True
                    break
            continue
        if Fun.distance_between(e.pos, self.pos) < 512:
            enemy_count += 1
            if enemy_count > 10:
                break

    self.input["Skill 2"] = lord_in_beast_mode or enemy_count > 10


def sovereign_skill_control(self, entities, level):
    allow_skill_1 = True
    for e in entities["entities"]:
        if e.target == self:
            allow_skill_1 = False
            break

    self.input["Skill 1"] = self.reloading and allow_skill_1
    self.input["Skill 2"] = not self.target


def duke_skill_control(self, entities, level):
    # tail swipe when there multiple bullets around the area of effect,
    self.input["Skill 1"] = entity_get_enemy_count(self, entities, goal=2, dist=64, entity_type="bullets")


def jester_skill_control(self, entities, level):
    enemies_around = entity_get_enemy_count(self, entities, goal=0, dist=128, entity_type="entities")

    allow_discharge = "Surge Protection" in self.free_var or not entity_get_ally_count(self, entities, goal=1, dist=128, entity_type="entities")
    self.input["Skill 1"] = allow_discharge and enemies_around
    self.input["Skill 2"] = enemies_around


def condor_skill_control(self, entities, level):
    self.input["Skill 2"] = self.health <= self.max_health * 0.075


def curtis_skill_control(self, entities, level):
    # tail swipe when there multiple bullets around the area of effect,
    self.input["Skill 1"] = entity_get_enemy_count(self, entities, goal=0, dist=80, entity_type="bullets")


def mark_skill_control(self, entities, level):
    allow_skill_1 = False
    for e in entities["entities"]:
        if e.target == self:
            allow_skill_1 = True
            break

    self.input["Skill 1"] = not self.target
    self.input["Skill 2"] = allow_skill_1


def fortress_skill_control(self, entities, level):
    if self.driving < 3: return
    self.input["Skill 2"] = not entity_get_enemy_count(self, entities, goal=0, dist=256)


# Handle skills that Are not handled by fire control
ALLY_SKILL_CONTROL = {
    "Lord": basic_skill_control,
    "Emperor": basic_skill_control,
    "Wizard": wizard_skill_control,
    "Sovereign": sovereign_skill_control,
    "Duke": duke_skill_control,
    "Jester": jester_skill_control,
    "Condor": condor_skill_control,

    "Curtis": curtis_skill_control,
    "Doppelgänger": curtis_skill_control,
    "Lawrence": basic_skill_control,
    "Mark": mark_skill_control,
    "Vivianne": basic_skill_control
}


# THR-1 Boss act func
def lord_boss_input(self, entities, level):
    if self.time < 60 * 5: return
    self.input = Fun.get_default_inputs()
    # Make it stay on the position to hold
    self.angle = Fun.angle_between(self.mouse_pos, self.pos)

    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    if target:
        aim_target = self.target.pos.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)
        ALLY_FIRE_CONTROL[self.name][self.weapon.name](self, entities, level, target, wall_in)
        entity_dash_when_targeted(self)
        move_target = universal_pathfinding(self, level, self.target.pos)
        aaa = bool(move_target)
        if not move_target:
            move_target = self.target.pos
        self.mouse_pos = self.target.mouse_pos.copy()
        entity_move_toward_point(self, move_target, 48)
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True
    else:
        m_target = self.pos.copy()
        for e in entities["entities"]:
            if e.team == self.team: continue
            if Fun.distance_between(self.pos, e.pos) > 320:
                m_target = e.pos.copy()
        move_target = universal_pathfinding(self, level, m_target)
        aaa = bool(move_target)
        if not move_target:
            move_target = m_target
        self.mouse_pos = m_target

        entity_move_toward_point(self, move_target, 128)
        if not aaa: entity_spread_apart(self, entities)
    # entity_dodge_bullets(self, entities, 64)
    ALLY_SKILL_CONTROL[self.name](self, entities, level)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def emperor_boss_input(self, entities, level):
    if self.time < 60 * 5: return
    self.input = Fun.get_default_inputs()
    # Make it stay on the position to hold
    self.angle = Fun.angle_between(self.mouse_pos, self.pos)

    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    if target:
        aim_target = self.target.pos.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)

        if not melee_fire_control(self, entities, level, target, wall_in):
            self.input["Reload"] = self.weapon.ammo == 0 and self.weapon.ammo_pool > 0
            entity_shoot_with_startup_lag(self, Fun.distance_between(target, self.pos), 7 * 30)
            if self.free_var['Startup lag'] > 0:
                self.input["Alt fire"] = True
                self.input["Shoot"] = start_up_lag_handler(self, self.free_var["Startup time"])
        else:
            self.input["Skill 2"] = entity_get_enemy_count(self, entities, goal=5, dist=256)
        entity_dash_when_targeted(self)
        move_target = universal_pathfinding(self, level, self.target.pos)
        aaa = bool(move_target)
        if not move_target:
            move_target = self.target.pos
        self.mouse_pos = self.target.mouse_pos.copy()
        dist = Fun.distance_between(self.pos, self.target.pos)
        if dist < 96:
            print(f"{dist=}")

            if self.free_var["Startup lag kick"] == 0 and self.free_var["kick cooldown"] == 0:
                self.free_var["Startup lag kick"] += 1
        entity_move_toward_point(self, move_target, 48)
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True
    else:
        m_target = self.pos.copy()
        for e in entities["entities"]:
            if e.team == self.team: continue
            if Fun.distance_between(self.pos, e.pos) > 320:
                m_target = e.pos.copy()
        move_target = universal_pathfinding(self, level, m_target)
        aaa = bool(move_target)
        if not move_target:
            move_target = m_target
        self.mouse_pos = m_target

        entity_move_toward_point(self, move_target, 128)
        if not aaa: entity_spread_apart(self, entities)

    if self.free_var["kick cooldown"] == 0 and self.free_var["Startup lag kick"] != 0 :
        self.input["Skill 1"] = start_up_lag_handler(self, 90, key="Startup lag kick")
        if self.input["Skill 1"]:
            self.free_var["kick cooldown"] = 120
    else:
        self.free_var["kick cooldown"] -=1

    # entity_dodge_bullets(self, entities, 64)
    entity_spread_apart(self, entities)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def emperor_boss_draw(self, WIN, scrolling):
    # That one has animations
    if self.status["Stealth"] > 0:
        return
    # Draw the enemy
    WIN.blit(Fun.ENTITY_SHADOW, (self.pos[0]-16 + scrolling[0], self.pos[1] + 11 + scrolling[1]), special_flags=pg.BLEND_RGBA_SUB)
    enemy_direction = Fun.get_entity_direction(self.angle)
    # Fun.draw_entity(self, scrolling, WIN, enemy_direction)
    self.draw_player(scrolling, WIN, enemy_direction)

    # Draw the gun
    angle_to_add = 0
    if self.reloading:
        angle_to_add = (360 / self.weapon.reload_time) * self.no_shoot_state

    Fun.blitRotate(WIN, pg.transform.flip(self.weapon.sprite, True, -90 < self.aim_angle < 90),
                   Fun.move_with_vel_angle([self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]], 10,
                                           self.aim_angle),
                   [0, 0], 180 - self.aim_angle + angle_to_add)

    if self.free_var["Startup lag kick"]:
        pos = Fun.move_with_vel_angle(self.pos, 16, self.angle)
        pos[0] += scrolling[0]
        pos[1] += scrolling[1]
        mod = self.free_var["Startup lag kick"]/90
        Fun.draw_transparent_arc(WIN, Fun.DARK_RED, pos, self.angle, 128, 45, 96, width=100000)
        Fun.draw_transparent_arc(WIN, Fun.DARK_RED, pos, self.angle, 128*mod, 45, 96, width=100000)


def wizard_boss_input(self, entities, level):
    if self.time < 60 * 5: return
    self.input = Fun.get_default_inputs()
    self.input = Fun.get_default_inputs()
    # Make it stay on the position to hold

    main_group = entity_find_main_group(self, entities, dist=256)
    move_target = universal_pathfinding(self, level, main_group)
    aaa = bool(move_target)
    if not move_target:
        move_target = main_group
    mod_move_target = move_target.copy()
    self.mouse_pos = main_group.copy()
    self.angle = Fun.angle_between(self.mouse_pos, self.pos)

    target, target_angle, wall_in = entity_target_simple(self, entities, level)

    if target:
        aim_target = self.target.pos.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)
        ALLY_FIRE_CONTROL[self.name][self.weapon.name](self, entities, level, target, wall_in)
        entity_dash_when_targeted(self)
        mod_move_target = Fun.move_with_vel_angle(move_target, 128, self.angle - 180)
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True

    entity_move_toward_point(self, move_target, 96)
    entity_move_toward_point(self, mod_move_target, 32)
    # if not aaa: entity_spread_apart(self, entities)
    entity_dodge_bullets(self, entities, 64)
    ALLY_SKILL_CONTROL[self.name](self, entities, level)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def sovereign_boss_input(self, entities, level):
    if self.time < 60 * 5: return
    self.input = Fun.get_default_inputs()
    # Make it stay on the position to hold
    move_target = universal_pathfinding(self, level, self.free_var["Ally waypoint"].pos)
    aaa = bool(move_target)
    if not move_target:
        move_target = self.free_var["Ally waypoint"].pos
    self.mouse_pos = self.free_var["Ally waypoint"].mouse_pos.copy()
    self.angle = Fun.angle_between(self.mouse_pos, self.pos)

    target, target_angle, wall_in = entity_target_simple(self, entities, level)

    if target:
        aim_target = self.target.pos.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)
        # basic_fire_control(self, entities, level, target, wall_in)

        entity_shoot_with_startup_lag(self, Fun.distance_between(target, self.pos), self.weapon.range * 0.9)
        entity_dash_when_targeted(self)
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True

    entity_shoot_startup_handler(self)
    entity_move_toward_point(self, move_target, 224)
    if not aaa: entity_spread_apart(self, entities)
    entity_dodge_bullets(self, entities, 64)
    ALLY_SKILL_CONTROL[self.name](self, entities, level)

    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def duke_boss_input(self, entities, level):
    if self.time < 60 * 5: return
    self.input = Fun.get_default_inputs()
    # Make it stay on the position to hold

    # Try to find Corrine
    main_group = entity_find_teammate(self, entities, target="Sovereign", check_limit=8)
    dist = 32
    if not main_group:
        main_group = self.free_var["Ally waypoint"].pos
        dist = 120

    move_target = universal_pathfinding(self, level, main_group)
    if not move_target:
        move_target = main_group
    mod_move_target = move_target.copy()
    self.mouse_pos = main_group.copy()
    self.angle = Fun.angle_between(self.mouse_pos, self.pos)

    target, target_angle, wall_in = entity_target_simple(self, entities, level)

    if target:
        aim_target = self.target.pos.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)
        ALLY_FIRE_CONTROL[self.name][self.weapon.name](self, entities, level, target, wall_in)
        entity_dash_when_targeted(self)
        mod_move_target = Fun.move_with_vel_angle(move_target, 128, self.angle)
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True

    entity_move_toward_point(self, move_target, 96)
    entity_move_toward_point(self, mod_move_target, 32)
    # if not aaa: entity_spread_apart(self, entities)
    entity_dodge_bullets(self, entities, dist)
    ALLY_SKILL_CONTROL[self.name](self, entities, level)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def jester_boss_input(self, entities, level):
    if self.time < 60 * 5: return
    self.input = Fun.get_default_inputs()
    # Make it stay on the position to hold

    target, target_angle, wall_in = entity_target_detection_healer(self, entities, level)

    if target:
        aim_target = self.target.pos.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)
        medic_rifle_fire_control(self, entities, level, target, wall_in)
        entity_dash_when_targeted(self)

        move_target = universal_pathfinding(self, level, self.target.pos)
        aaa = bool(move_target)
        if not move_target:
            move_target = self.target.pos
        self.mouse_pos = self.target.mouse_pos.copy()
        entity_move_toward_point(self, move_target, 48)
        if not aaa: entity_spread_apart(self, entities, spread_dist=48)

    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True

    entity_dodge_bullets(self, entities, 64)
    jester_skill_control(self, entities, level)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def condor_boss_input(self, entities, level):
    if self.time < 60 * 5: return
    self.input = Fun.get_default_inputs()
    # Make it stay on the position to hold

    main_group = entity_find_main_group(self, entities, dist=256)
    move_target = universal_pathfinding(self, level, main_group)
    aaa = bool(move_target)
    if not move_target:
        move_target = main_group
    mod_move_target = move_target.copy()
    self.mouse_pos = main_group.copy()
    self.angle = Fun.angle_between(self.mouse_pos, self.pos)

    target, target_angle, wall_in = entity_target_simple(self, entities, level)

    if target:
        aim_target = self.target.pos.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)
        ALLY_FIRE_CONTROL[self.name][self.weapon.name](self, entities, level, target, wall_in)
        entity_dash_when_targeted(self)
        mod_move_target = Fun.move_with_vel_angle(move_target, 128, self.angle)
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True

    entity_move_toward_point(self, move_target, 96)
    entity_move_toward_point(self, mod_move_target, 32)
    # if not aaa: entity_spread_apart(self, entities)
    entity_dodge_bullets(self, entities, 64)
    ALLY_SKILL_CONTROL[self.name](self, entities, level)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def thr_1_on_death(self, entities, level):
    if "IS BOSS" in self.free_var:
        for e in entities["entities"]:
            if e.team != self.team:
                continue
            if "IS BOSS" in e.free_var:
                continue
            e.free_var.update({"IS BOSS": True})


def condor_boss_on_death(self, entities, level):
    if self.status["Last Stand"] > 0:
        self.health = round(self.max_health * 0.33)
        self.status["No damage"] = 60 * 3
        self.status["No debuff"] = 60 * 3
        self.status["Last Stand"] = 0

        number_of_particle = 18
        for particles_to_add in range(360 // number_of_particle):
            entities["particles"].append(Particles.RandomParticle2(
                [self.pos[0], self.pos[1]], Fun.DARK_RED, 1 + 3 * random.random(), random.randint(45, 90),
                                                        particles_to_add * number_of_particle,
                size=Fun.get_random_element_from_list([3, 4, 6])))

        Fun.play_sound("Skill 7")
        return
    thr_1_on_death(self, entities, level)


# |Ally input|----------------------------------------------------------------------------------------------------------
def test_ally_input(self, entities, level):
    self.input = Fun.get_default_inputs()
    {"Follow": ally_sub_input_follow,
     "Hold": ally_sub_input_hold,
     "Attack": ally_sub_input_attack,
     "Freely": ACT_FREELY_DICT[self.name]}[self.ai_state](self, entities, level)


def ally_sub_input_follow(self, entities, level):
    # Make it stay on the position to hold
    move_target = universal_pathfinding(self, level, self.free_var["Ally waypoint"].pos)
    aaa = bool(move_target)
    if not move_target:
        move_target = self.free_var["Ally waypoint"].pos
    self.mouse_pos = self.free_var["Ally waypoint"].mouse_pos.copy()
    self.angle = Fun.angle_between(self.mouse_pos, self.pos)

    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    if target:
        aim_target = self.target.pos.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)
        ALLY_FIRE_CONTROL[self.name][self.weapon.name](self, entities, level, target, wall_in)
        entity_dash_when_targeted(self)
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True

    entity_move_toward_point(self, move_target, 48)
    if not aaa: entity_spread_apart(self, entities)
    entity_dodge_bullets(self, entities, 64)
    ALLY_SKILL_CONTROL[self.name](self, entities, level)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def ally_sub_input_hold(self, entities, level):
    move_target = universal_pathfinding(self, level, self.free_var["Ally waypoint"])

    if not move_target:
        move_target = self.free_var["Ally waypoint"]
    self.mouse_pos = move_target.copy()

    target, target_angle, wall_in = entity_target_detection(self, entities, level)
    # Make it stay on the position to hold
    if target:
        aim_target = self.target.pos.copy()
        self.mouse_pos = aim_target.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)
        # modify position of target for some ia types
        ALLY_FIRE_CONTROL[self.name][self.weapon.name](self, entities, level, target, wall_in)
        entity_dash_when_targeted(self)

    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True

    entity_move_toward_point(self, move_target, 16)
    # entity_spread_apart(self, entities)
    entity_dodge_bullets(self, entities, 64)
    ALLY_SKILL_CONTROL[self.name](self, entities, level)
    # Stunned status manager
    Fun.stunned_manager(self)
    return target, target_angle


def ally_sub_input_attack(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    if target:
        aim_target = self.target.pos.copy()
        # move_target = target.copy()
        self.mouse_pos = aim_target.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)

        ALLY_FIRE_CONTROL[self.name][self.weapon.name](self, entities, level, target, wall_in)
        entity_dash_when_targeted(self)
        entity_move_toward_point(self, aim_target, self.weapon.range * 0.8)

    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True

    # entity_spread_apart(self, entities)
    entity_dodge_bullets(self, entities, 32)
    ALLY_SKILL_CONTROL[self.name](self, entities, level)

    # Stunned status manager
    Fun.stunned_manager(self)
    return target, target_angle


def jester_input(self, entities, level):
    self.input = Fun.get_default_inputs()
    # When he gets new weapons, use a dict to choose sub inputs
    #
    {"Follow": {
        "Epicurean Medic Rifle": jester_sub_input_follow,
        "Nihilist Stretcher": ally_sub_input_follow,
        "Stoic Shield generator": ally_sub_input_follow}[self.weapon.name],
     "Hold": {
        "Epicurean Medic Rifle": jester_sub_input_hold,
        "Nihilist Stretcher": ally_sub_input_hold,
        "Stoic Shield generator": ally_sub_input_hold}[self.weapon.name],
     "Attack": {
        "Epicurean Medic Rifle": jester_sub_input_attack,
        "Nihilist Stretcher": ally_sub_input_attack,
        "Stoic Shield generator": ally_sub_input_attack}[self.weapon.name],
     "Freely": ACT_FREELY_DICT[self.name]}[self.ai_state](self, entities, level)


def jester_sub_input_follow(self, entities, level):
    # Make it stay on the position to hold
    move_target = universal_pathfinding(self, level, self.free_var["Ally waypoint"].pos)
    aaa = bool(move_target)
    if not move_target:
        move_target = self.free_var["Ally waypoint"].pos
    self.mouse_pos = self.free_var["Ally waypoint"].mouse_pos.copy()
    self.angle = Fun.angle_between(self.mouse_pos, self.pos)

    target, target_angle, wall_in = entity_target_detection_healer(self, entities, level)

    if target:
        aim_target = self.target.pos.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)
        ALLY_FIRE_CONTROL[self.name][self.weapon.name](self, entities, level, target, wall_in)
        entity_dash_when_targeted(self)
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True

    entity_move_toward_point(self, move_target, 48)
    if not aaa: entity_spread_apart(self, entities)
    entity_dodge_bullets(self, entities, 64)
    ALLY_SKILL_CONTROL[self.name](self, entities, level)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def jester_sub_input_hold(self, entities, level):
    move_target = universal_pathfinding(self, level, self.free_var["Ally waypoint"])

    if not move_target:
        move_target = self.free_var["Ally waypoint"]
    self.mouse_pos = move_target.copy()

    target, target_angle, wall_in = entity_target_detection_healer(self, entities, level)
    # Make it stay on the position to hold
    if target:
        aim_target = self.target.pos.copy()
        self.mouse_pos = aim_target.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)
        # modify position of target for some ia types
        ALLY_FIRE_CONTROL[self.name][self.weapon.name](self, entities, level, target, wall_in)
        entity_dash_when_targeted(self)

    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True

    entity_move_toward_point(self, move_target, 16)
    # entity_spread_apart(self, entities)
    entity_dodge_bullets(self, entities, 64)
    ALLY_SKILL_CONTROL[self.name](self, entities, level)
    # Stunned status manager
    Fun.stunned_manager(self)
    return target, target_angle


def jester_sub_input_attack(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection_healer(self, entities, level)

    if target:
        aim_target = self.target.pos.copy()
        move_target = target.copy()
        self.mouse_pos = aim_target.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)

        ALLY_FIRE_CONTROL[self.name][self.weapon.name](self, entities, level, target, wall_in)
        entity_dash_when_targeted(self)

    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True

    entity_spread_apart(self, entities)
    entity_dodge_bullets(self, entities, 64)
    ALLY_SKILL_CONTROL[self.name](self, entities, level)

    # Stunned status manager
    Fun.stunned_manager(self)
    return target, target_angle


# Act freely functions
def ally_sub_input_roam(self, entities, level):
    self.input = Fun.get_default_inputs()
    # Make it stay on the position to hold
    self.angle = Fun.angle_between(self.mouse_pos, self.pos)

    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    if target:
        aim_target = self.target.pos.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)
        ALLY_FIRE_CONTROL[self.name][self.weapon.name](self, entities, level, target, wall_in)
        entity_dash_when_targeted(self)
        move_target = universal_pathfinding(self, level, self.target.pos)
        aaa = bool(move_target)
        if not move_target:
            move_target = self.target.pos
        self.mouse_pos = self.target.mouse_pos.copy()
        entity_move_toward_point(self, move_target, 48)
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True
    else:
        m_target = self.pos.copy()
        for e in entities["entities"]:
            if e.team == self.team: continue
            if Fun.distance_between(self.pos, e.pos) > 320:
                m_target = e.pos.copy()
        move_target = universal_pathfinding(self, level, m_target)
        aaa = bool(move_target)
        if not move_target:
            move_target = m_target
        self.mouse_pos = m_target

        entity_move_toward_point(self, move_target, 128)
        if not aaa: entity_spread_apart(self, entities)
    entity_dodge_bullets(self, entities, 64)
    ALLY_SKILL_CONTROL[self.name](self, entities, level)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def ally_sub_input_focus_objective(self, entities, level):
    self.input = Fun.get_default_inputs()
    # Make it stay on the position to hold
    self.angle = Fun.angle_between(self.mouse_pos, self.pos)

    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    if target:
        aim_target = self.target.pos.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)
        ALLY_FIRE_CONTROL[self.name][self.weapon.name](self, entities, level, target, wall_in)
        entity_dash_when_targeted(self)
        move_target = universal_pathfinding(self, level, self.target.pos)
        aaa = bool(move_target)
        if not move_target:
            move_target = self.target.pos
        self.mouse_pos = self.target.mouse_pos.copy()
        entity_move_toward_point(self, move_target, 48)
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True
    else:
        if level['objective points']:
            m_target = level['objective points'][0]
            dist = 32
        else:
            dist = 128
            m_target = self.pos.copy()
            for e in entities["entities"]:
                if e.team == self.team: continue
                if Fun.distance_between(self.pos, e.pos) > 320:
                    m_target = e.pos.copy()
                    break
        move_target = universal_pathfinding(self, level, m_target)
        aaa = bool(move_target)
        if not move_target:
            move_target = m_target
        self.mouse_pos = m_target

        entity_move_toward_point(self, move_target, dist)
        if not aaa: entity_spread_apart(self, entities)

    entity_dodge_bullets(self, entities, 64)
    ALLY_SKILL_CONTROL[self.name](self, entities, level)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def ally_sub_input_wizard(self, entities, level):
    self.input = Fun.get_default_inputs()
    # Make it stay on the position to hold

    main_group = entity_find_main_group(self, entities, dist=256)
    move_target = universal_pathfinding(self, level, main_group)
    aaa = bool(move_target)
    if not move_target:
        move_target = main_group
    mod_move_target = move_target.copy()
    self.mouse_pos = main_group.copy()
    self.angle = Fun.angle_between(self.mouse_pos, self.pos)

    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    if target:
        aim_target = self.target.pos.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)
        ALLY_FIRE_CONTROL[self.name][self.weapon.name](self, entities, level, target, wall_in)
        entity_dash_when_targeted(self)
        mod_move_target = Fun.move_with_vel_angle(move_target, 128, self.angle - 180)
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True

    entity_move_toward_point(self, move_target, 96)
    entity_move_toward_point(self, mod_move_target, 32)
    # if not aaa: entity_spread_apart(self, entities)
    entity_dodge_bullets(self, entities, 64)
    ALLY_SKILL_CONTROL[self.name](self, entities, level)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def ally_sub_input_sniper(self, entities, level):
    self.input = Fun.get_default_inputs()
    # Make it stay on the position to hold
    move_target = universal_pathfinding(self, level, self.free_var["Ally waypoint"].pos)
    aaa = bool(move_target)
    if not move_target:
        move_target = self.free_var["Ally waypoint"].pos
    self.mouse_pos = self.free_var["Ally waypoint"].mouse_pos.copy()
    self.angle = Fun.angle_between(self.mouse_pos, self.pos)

    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    if target:
        aim_target = self.target.pos.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)
        ALLY_FIRE_CONTROL[self.name][self.weapon.name](self, entities, level, target, wall_in)
        entity_dash_when_targeted(self)
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True

    entity_move_toward_point(self, move_target, 224)
    if not aaa: entity_spread_apart(self, entities)
    entity_dodge_bullets(self, entities, 64)
    ALLY_SKILL_CONTROL[self.name](self, entities, level)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def ally_sub_input_duke(self, entities, level):
    self.input = Fun.get_default_inputs()
    # Make it stay on the position to hold

    # Try to find Corrine
    main_group = entity_find_teammate(self, entities, target="Sovereign")
    dist = 32
    if not main_group:
        main_group = self.free_var["Ally waypoint"].pos
        dist = 120

    move_target = universal_pathfinding(self, level, main_group)
    aaa = bool(move_target)
    if not move_target:
        move_target = main_group
    mod_move_target = move_target.copy()
    self.mouse_pos = main_group.copy()
    self.angle = Fun.angle_between(self.mouse_pos, self.pos)

    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    if target:
        aim_target = self.target.pos.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)
        ALLY_FIRE_CONTROL[self.name][self.weapon.name](self, entities, level, target, wall_in)
        entity_dash_when_targeted(self)
        mod_move_target = Fun.move_with_vel_angle(move_target, 128, self.angle)
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True

    entity_move_toward_point(self, move_target, 96)
    entity_move_toward_point(self, mod_move_target, 32)
    # if not aaa: entity_spread_apart(self, entities)
    entity_dodge_bullets(self, entities, dist)
    ALLY_SKILL_CONTROL[self.name](self, entities, level)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def ally_sub_input_jester(self, entities, level):
    self.input = Fun.get_default_inputs()
    # Make it stay on the position to hold

    target, target_angle, wall_in = entity_target_detection_healer(self, entities, level)

    if target:
        aim_target = self.target.pos.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)
        ALLY_FIRE_CONTROL[self.name][self.weapon.name](self, entities, level, target, wall_in)
        entity_dash_when_targeted(self)

        move_target = universal_pathfinding(self, level, self.target.pos)
        aaa = bool(move_target)
        if not move_target:
            move_target = self.target.pos
        self.mouse_pos = self.target.mouse_pos.copy()
        entity_move_toward_point(self, move_target, 48)
        if not aaa: entity_spread_apart(self, entities, spread_dist=48)

    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True

    entity_dodge_bullets(self, entities, 64)
    ALLY_SKILL_CONTROL[self.name](self, entities, level)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def ally_sub_input_condor(self, entities, level):
    self.input = Fun.get_default_inputs()
    # Make it stay on the position to hold

    main_group = entity_find_main_group(self, entities, dist=256)
    move_target = universal_pathfinding(self, level, main_group)
    aaa = bool(move_target)
    if not move_target:
        move_target = main_group
    mod_move_target = move_target.copy()
    self.mouse_pos = main_group.copy()
    self.angle = Fun.angle_between(self.mouse_pos, self.pos)

    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    if target:
        aim_target = self.target.pos.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)
        ALLY_FIRE_CONTROL[self.name][self.weapon.name](self, entities, level, target, wall_in)
        entity_dash_when_targeted(self)
        mod_move_target = Fun.move_with_vel_angle(move_target, 128, self.angle)
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True

    entity_move_toward_point(self, move_target, 96)
    entity_move_toward_point(self, mod_move_target, 32)
    # if not aaa: entity_spread_apart(self, entities)
    entity_dodge_bullets(self, entities, 64)
    ALLY_SKILL_CONTROL[self.name](self, entities, level)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def ally_sub_input_lawrence(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    self.input = Fun.get_default_inputs()
    if target:
        aim_target = self.target.pos.copy()
        move_target = target.copy()
        self.mouse_pos = aim_target.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)
        ALLY_FIRE_CONTROL[self.name][self.weapon.name](self, entities, level, target, wall_in)
        entity_maintain_weapon_range(self, Fun.distance_between(target, self.pos), move_target, 256, get_away=192)
        entity_dash_when_targeted(self, no_shoot_threshold=50, threshold=0.75)

    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True

    entity_spread_apart(self, entities)
    entity_dodge_bullets(self, entities, 64)
    ALLY_SKILL_CONTROL[self.name](self, entities, level)

    # Stunned status manager
    Fun.stunned_manager(self)
    return target, target_angle


# Fortress
def vehicle_escort(self, level):
    if 'APC path' in level['free var']:
        if level['free var']['APC path']:
            move_target = level['free var']['APC path'][0]  # Get first point from the list
            if Fun.distance_between(move_target, self.pos) < self.thiccness:
                # Remove current point from the list
                level['free var']['APC path'].pop(0)
            if self.is_player: return
            if self.ai_state != "Hold":
                # Stops moving if there's enemies too close
                APC_MOVE_TO_POINT[self.free_var["IS AN APC"]](self, move_target, 8)


def fortress_input(self, entities, level):
    self.input = Fun.get_default_inputs()
    # If it doesn't act like a normal ally
    {"Follow": fortress_sub_input_follow,
     "Hold": fortress_sub_input_hold,
     "Attack": fortress_sub_input_attack,
     "Freely": fortress_sub_input_attack}[self.ai_state](self, entities, level)
    self.input["Alt fire"] = self.driving >= 2
    # Check if it has objectives to follow, if yes override every order expect hold
    #


APC_MOVE_TO_POINT = { # Add something to choose between weapons later
    "Fortress": fortress_move_toward_point,
    "Sand Buggy": buggy_move_toward_point
}


def fortress_sub_input_follow(self, entities, level):
    self.input = Fun.get_default_inputs()
    # Make it stay on the position to hold
    move_target = universal_pathfinding(self, level, self.free_var["Ally waypoint"].pos)
    aaa = bool(move_target)
    if not move_target:
        move_target = self.free_var["Ally waypoint"].pos
    self.mouse_pos = self.free_var["Ally waypoint"].mouse_pos.copy()
    self.angle = Fun.angle_between(self.mouse_pos, self.pos)

    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    if target:
        aim_target = self.target.pos.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)
        self.mouse_pos = aim_target.copy()
        fortress_fire_control(self, entities, level, target, wall_in)

        ALLY_FIRE_CONTROL[self.free_var["IS AN APC"]][self.weapon.name](self, entities, level, target, wall_in)
        self.input["Skill 1"] = self.driving >= 1

    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True

    fortress_skill_control(self, entities, level)
    APC_MOVE_TO_POINT[self.free_var["IS AN APC"]](self, move_target, 64)
    # fortress_move_toward_point(self, move_target, 64)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def fortress_sub_input_hold(self, entities, level):
    self.input = Fun.get_default_inputs()
    move_target = universal_pathfinding(self, level, self.free_var["Ally waypoint"])

    if not move_target:
        move_target = self.free_var["Ally waypoint"]
    self.mouse_pos = move_target.copy()

    target, target_angle, wall_in = entity_target_detection(self, entities, level)
    # Make it stay on the position to hold
    if target:
        aim_target = self.target.pos.copy()
        self.mouse_pos = aim_target.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)
        # modify position of target for some ia types
        ALLY_FIRE_CONTROL[self.free_var["IS AN APC"]][self.weapon.name](self, entities, level, target, wall_in)

    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True

    fortress_skill_control(self, entities, level)
    APC_MOVE_TO_POINT[self.free_var["IS AN APC"]](self, move_target, 64)
    # fortress_move_toward_point(self, move_target, 64)
    # Stunned status manager
    Fun.stunned_manager(self)
    return target, target_angle


def fortress_sub_input_attack(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    self.input = Fun.get_default_inputs()
    if target:
        aim_target = self.target.pos.copy()
        move_target = target.copy()
        self.mouse_pos = aim_target.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)

        ALLY_FIRE_CONTROL[self.free_var["IS AN APC"]][self.weapon.name](self, entities, level, target, wall_in)

        APC_MOVE_TO_POINT[self.free_var["IS AN APC"]](self, move_target, 64)
        # fortress_move_toward_point(self, move_target, 64)

    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True

    fortress_skill_control(self, entities, level)
    # Stunned status manager
    Fun.stunned_manager(self)
    return target, target_angle


def azura_input(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    if target:
        aim_target = self.target.pos.copy()
        # move_target = target.copy()
        self.mouse_pos = aim_target.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)

        if Fun.distance_between(target, self.pos) <= self.weapon.range:
            self.input["Dash"] = True
        # entity_dash_when_targeted(self)
        entity_move_toward_point(self, aim_target, self.weapon.range * 0.8)
    else:
        move_target = universal_pathfinding(self, level, self.owner.pos)
        if not move_target:
            move_target = self.owner.pos
        entity_move_toward_point(self, move_target, 48)

    # entity_spread_apart(self, entities)
    # entity_dodge_bullets(self, entities, 32)

    # Stunned status manager
    Fun.stunned_manager(self)
    return target, target_angle


def birna_input(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    if target:
        aim_target = self.target.pos.copy()
        # move_target = target.copy()
        self.mouse_pos = aim_target.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)

        # basic_fire_control(self, entities, level, target, wall_in)
        entity_dash_when_targeted(self)
        entity_move_toward_point(self, aim_target, self.weapon.range * 0.8)

    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True
    else:
        move_target = universal_pathfinding(self, level, self.owner.pos)
        # aaa = bool(move_target)
        if not move_target:
            move_target = self.owner .pos
        entity_move_toward_point(self, move_target, 48)

    # entity_spread_apart(self, entities)
    # entity_dodge_bullets(self, entities, 32)

    # Stunned status manager
    Fun.stunned_manager(self)
    return target, target_angle


def agatha_input(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    if target:
        aim_target = self.target.pos.copy()
        # move_target = target.copy()
        self.mouse_pos = aim_target.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)

        melee_fire_control(self, entities, level, target, wall_in)
        entity_dash_when_targeted(self)
        entity_move_toward_point(self, aim_target, self.weapon.range * 0.8)

    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True
    else:
        move_target = universal_pathfinding(self, level, self.owner.pos)
        if not move_target:
            move_target = self.owner .pos
        entity_move_toward_point(self, move_target, 48)

    # Stunned status manager
    Fun.stunned_manager(self)
    return target, target_angle


def m_input(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    if target:
        aim_target = self.target.pos.copy()
        # move_target = target.copy()
        self.mouse_pos = aim_target.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)

        basic_fire_control(self, entities, level, target, wall_in)
        entity_dash_when_targeted(self)
        entity_move_toward_point(self, aim_target, self.weapon.range * 0.8)

    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True
    else:
        move_target = universal_pathfinding(self, level, self.owner.pos)
        aaa = bool(move_target)
        if not move_target:
            move_target = self.owner .pos
        entity_move_toward_point(self, move_target, 48)

    # self.input["Alt fire"] = self.time > VIVIANNE_SUMMON_LIVE_TIME // 2
    # self.input["Shoot"] = not self.input["Alt fire"] or self.input["Shoot"]
    # print(self.input["Alt fire"])
    # entity_spread_apart(self, entities)
    self.input["Dash"] = Fun.find_closest_bullet_types_in_circle(self, entities, 32, (Bullets.Bullet, Bullets.Fire, Bullets.Missile, Bullets.Artillery))

    # Stunned status manager
    Fun.stunned_manager(self)
    return target, target_angle


def sierra_input(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    if target:
        aim_target = self.target.pos.copy()
        # move_target = target.copy()
        self.mouse_pos = aim_target.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)

        basic_fire_control(self, entities, level, target, wall_in)
        entity_dash_when_targeted(self)
        entity_move_toward_point(self, aim_target, self.weapon.range * 0.8)
    else:
        move_target = universal_pathfinding(self, level, self.owner.pos)
        aaa = bool(move_target)
        if not move_target:
            move_target = self.owner.pos
        entity_move_toward_point(self, move_target, 48)

    if self.input["Reload"]:
        # Switch gun
        if self.weapon.name == "Anti-Material Rifle":
            self.weapon = Weapons.BasicWeapon(Weapons.weapon_repertory["Shotgun"])
            self.reloading = True
            self.no_shoot_state = 30
        elif self.weapon.name == "Shotgun":
            self.weapon = Weapons.BasicWeapon(Weapons.weapon_repertory["Pistol"])
            self.reloading = True
            self.no_shoot_state = 30
        else:
            self.free_var["Life Limit"] = 10
            self.no_shoot_state = 10


    # entity_spread_apart(self, entities)
    entity_dodge_bullets(self, entities, 32)
    # Switch guns

    # Stunned status manager
    Fun.stunned_manager(self)
    return target, target_angle


def elektra_input(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    if target:
        aim_target = self.target.pos.copy()
        # move_target = target.copy()
        self.mouse_pos = aim_target.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)

        basic_fire_control(self, entities, level, target, wall_in)
        # entity_dash_when_targeted(self)
        # entity_move_toward_point(self, aim_target, self.weapon.range * 0.8)

    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True

    # entity_spread_apart(self, entities)
    # entity_dodge_bullets(self, entities, 32)

    # Stunned status manager
    Fun.stunned_manager(self)
    return target, target_angle


def makoto_input(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    if target:
        aim_target = self.target.pos.copy()
        # move_target = target.copy()
        self.mouse_pos = aim_target.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)

        basic_fire_control(self, entities, level, target, wall_in)
        entity_dash_when_targeted(self)
        # entity_move_toward_point(self, aim_target, self.weapon.range * 0.8)

    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True
    move_target = universal_pathfinding(self, level, self.owner.pos)
    aaa = bool(move_target)
    if not move_target:
        move_target = self.owner .pos
    entity_move_toward_point(self, move_target, 48)

    # entity_spread_apart(self, entities)
    entity_dodge_bullets(self, entities, 32)

    # Stunned status manager
    Fun.stunned_manager(self)
    return target, target_angle


# |Ally Draw|-----------------------------------------------------------------------------------------------------------
def player_draw(self, WIN, scrolling):
    # Draw the colision box
    # Get the sprite direction
    player_direction = Fun.get_entity_direction(self.angle) % 6
    weapon_angle = self.angle
    if not self.standing_still:
        player_direction = Fun.get_entity_direction(self.direction_angle) % 6

    # Affect the placement of the second weapon
    # weapon_x_mod, weapon_y_mod, weapon_angle_mod = 2, 4, 10

    # Draws the player
    WIN.blit(Fun.ENTITY_SHADOW, (self.pos[0] - 16 + scrolling[0], self.pos[1] + 11 + scrolling[1]),
             special_flags=pg.BLEND_RGBA_SUB)
    self.draw_player(scrolling, WIN, player_direction)

    # Draw the weapon
    draw_weapon(self, WIN, scrolling)


def birna_draw(self, WIN, scrolling):
    # Draw the colision box
    # Get the sprite direction
    player_direction = Fun.get_entity_direction(self.angle) % 6
    weapon_angle = self.angle
    if not self.standing_still:
        player_direction = Fun.get_entity_direction(self.direction_angle) % 6

    # Affect the placement of the second weapon
    # weapon_x_mod, weapon_y_mod, weapon_angle_mod = 2, 4, 10

    # Draws the player
    WIN.blit(Fun.ENTITY_SHADOW, (self.pos[0] - 16 + scrolling[0], self.pos[1] + 11 + scrolling[1]),
             special_flags=pg.BLEND_RGBA_SUB)

    frame_to_get = 0
    action_type = "Walk"
    # Make the counters go up
    for counter in self.animation_counter:
        if action_type == counter:
            self.animation_counter[counter] = 1
        else:
            self.animation_counter[counter] = 0
    # p = round(3 * self.no_shoot_state / self.weapon.fire_rate)
    # Sliding need a special case to handle its animation
    # if self.no_shoot_state > 0 and not self.reloading:
    # if self.shooting:
        # print(player_direction)
    #     frame_to_get = round(4 * (self.no_shoot_state / self.weapon.fire_rate)) % (
    #              len(self.sprites[player_direction]["Walk"]) - 1) + 1
        # frame_to_get = self.animation_counter[action_type] // 7 % (
        #         len(self.sprites[player_direction][action_type]) - 1) + 1
    frame_to_get = self.time // 7 % (len(self.sprites[player_direction][action_type]) - 1) + 1
    # Draws the player
    sprite_drawn = self.sprites[player_direction][action_type][frame_to_get]
    WIN.blit(sprite_drawn, (
    self.pos[0] - self.sprite_height // 2 + scrolling[0], self.pos[1] - self.sprite_height // 2 + scrolling[1]))

    # Draw the weapon
    draw_weapon(self, WIN, scrolling)


def elektra_draw(self, WIN, scrolling):
    # Draw the colision box
    # Get the sprite direction
    player_direction = Fun.get_entity_direction(self.angle) % 6
    weapon_angle = self.angle
    if not self.standing_still:
        player_direction = Fun.get_entity_direction(self.direction_angle) % 6

    # Affect the placement of the second weapon
    # weapon_x_mod, weapon_y_mod, weapon_angle_mod = 2, 4, 10

    # Draws the player
    WIN.blit(Fun.ENTITY_SHADOW, (self.pos[0] - 16 + scrolling[0], self.pos[1] + 11 + scrolling[1]),
             special_flags=pg.BLEND_RGBA_SUB)

    frame_to_get = 0
    action_type = "Walk"
    # Make the counters go up
    for counter in self.animation_counter:
        if action_type == counter:
            self.animation_counter[counter] = 1
        else:
            self.animation_counter[counter] = 0
    p = round(3 * self.no_shoot_state / self.weapon.fire_rate)
    # Sliding need a special case to handle its animation
    # if self.no_shoot_state > 0 and not self.reloading:
    if self.shooting:
        # print(player_direction)
        frame_to_get = round(4 * (self.no_shoot_state / self.weapon.fire_rate)) % (
                 len(self.sprites[player_direction]["Walk"]) - 1) + 1
        # frame_to_get = self.animation_counter[action_type] // 7 % (
        #         len(self.sprites[player_direction][action_type]) - 1) + 1

    # Draws the player
    sprite_drawn = self.sprites[player_direction][action_type][frame_to_get]
    WIN.blit(sprite_drawn, (
    self.pos[0] - self.sprite_height // 2 + scrolling[0], self.pos[1] - self.sprite_height // 2 + scrolling[1]))

    # Draw the weapon
    draw_weapon(self, WIN, scrolling)


def fortress_draw(self, WIN, scrolling):
    Fun.draw_spritestack(WIN, Fun.SPRITE_FORTRESS_APC_CHASSIS, [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]],
                         self.free_var["Move angle"] + 90, height_diff=0.5)
    # 226
    # angle = 226 + self.free_var["Move angle"]
    pos = [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1] - 16]
    pos = Fun.move_with_vel_angle(pos, 22.6274, self.free_var["Move angle"] + 226 - 180)
    Fun.draw_spritestack(WIN, Fun.SPRITE_FORTRESS_APC_TURRET, pos, self.aim_angle + 90, height_diff=0.5)


def buggy_draw(self, WIN, scrolling):
    # Fun.draw_spritestack(WIN, Fun.SPRITE_SAND_BUGGY, [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]],
    #                      self.free_var["Move angle"] + 90, height_diff=0.5)

    pos = [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]]
    angle = Fun.angle_value_limiter(self.free_var["Move angle"] + 90)

    # t_angle = Fun.angle_value_limiter(self.free_var["Target Move angle"] + 90)
    t_angle = Fun.pg.math.clamp(self.free_var["Target Move angle"] + 90, angle - 25, angle + 25)
    # t_angle = self.free_var["Target Move angle"] + 90
    # smaller_angle = angle - 30
    # bigger_angle = angle + 30
    # if the direction the AI is looking at is near -180/180
    # if 180 - 30 > angle and 180 - 30 > t_angle: t_angle = smaller_angle
    # elif smaller_angle < t_angle: t_angle = smaller_angle
    # if angle > -180 + 30 and t_angle > -180 + 30: t_angle = bigger_angle
    # elif t_angle < bigger_angle: t_angle = bigger_angle
    # check

    height_diff = 0.5
    sprites = Fun.SPRITE_SAND_BUGGY.copy()
    mod = 0
    if self.input["Down"]:
        mod = 3
    front_wheel_rotation = abs(mod - (round(self.time // 4 * self.free_var["Move vel"]) % 4))

    for count, s in enumerate(Fun.SPRITE_SAND_BUGGY_WHEEL[front_wheel_rotation]):
        sprites[count].blit(s, [0, 0])

    for i, sprite in enumerate(sprites):
        rotated_sprite = pg.transform.rotate(sprite, -angle)
        WIN.blit(rotated_sprite, (pos[0] - rotated_sprite.get_width() // 2, pos[1] - rotated_sprite.get_height() // 2 - height_diff * i))
        if i < len(Fun.SPRITE_SAND_BUGGY_FRONT[front_wheel_rotation]):
            rotated_sprite = pg.transform.rotate(Fun.SPRITE_SAND_BUGGY_FRONT[front_wheel_rotation][i], -t_angle)
            WIN.blit(rotated_sprite, Fun.move_with_vel_angle(
                (pos[0] - rotated_sprite.get_width() // 2, pos[1] - rotated_sprite.get_height() // 2 - height_diff * i), 28, angle - 90)
                     )

    pos = [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1] - 14]
    angle = self.free_var["Move angle"] - 180
    pos = Fun.move_with_vel_angle(pos, 24, angle)

    Fun.draw_spritestack(WIN, Fun.SPRITE_SAND_BUGGY_TURRET,
                         pos,
                         self.aim_angle + 90, height_diff=0.5)
    # SPRITE_SAND_BUGGY_TURRET


def cardboard_box_draw(self, WIN, scrolling):
    Fun.draw_spritestack(WIN, Fun.SPRITE_CARDBOARD_BOX, [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]],
                         self.skills[0].free_var["Draw angle"] + 90, height_diff=0.75)


# |Ally On Death|-------------------------------------------------------------------------------------------------------
def lord_on_death(self, entities, level):
    if 'Super Duper Ultimate Death Defying Plus Ultra Supreme Heavenly Beast Mode DELUXE' in self.free_var:
        # Lord cannot die during the duration, still takes damage but doesn't go under 1
        if self.skills[1].active:
            self.health = 1


def condor_on_death(self, entities, level):
    # print(self.status["Last Stand"])
    if self.status["Last Stand"] > 0:
        self.health = round(self.max_health * 0.33)
        self.status["No damage"] = 60 * 3
        self.status["No debuff"] = 60 * 3
        self.status["Last Stand"] = 0

        number_of_particle = 18
        for particles_to_add in range(360 // number_of_particle):
            entities["particles"].append(Particles.RandomParticle2(
                [self.pos[0], self.pos[1]], Fun.DARK_RED, 1 + 3 * random.random(), random.randint(45, 90),
                                                        particles_to_add * number_of_particle,
                size=Fun.get_random_element_from_list([3, 4, 6])))

        Fun.play_sound("Skill 7")
        for u in self.upgrades:
            if u.name == "Unbreaking Blue Balls":
                u.free_var = {"Last Stand": True}
                break
    # print(self.health)


def fortress_on_death(self, entities, level):
    level["events"].append(MissionEvent("", trigger_constant, True, [loss_of_apc]))


def vivianne_summons_on_death(self, entities, level):
    for count, active in enumerate(self.owner.free_var["Active summons"]):
        if active == self.name:
            self.owner.free_var["Active summons"].pop(count)
            break

    # Blue Ballin upgrade
    if "Blue Ballin" in self.owner.free_var:
        # "Ballin"
        Items.spawn_item(entities, "Ballin", Fun.move_with_vel_angle(self.pos, 20, self.aim_angle), self=self)
        entities["items"][-1].free_var["Angle"] = Fun.angle_between(self.owner.pos, self.pos)
        entities["items"][-1].free_var["True pos"] = self.pos
        entities["items"][-1].owner = self.owner


# |Enemy Input|---------------------------------------------------------------------------------------------------------
def enemy_input_nest_trooper(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    self.input = Fun.get_default_inputs()
    if target:
        aim_target = self.target.pos.copy()
        move_target = target.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)
        # modify position of target for some ia types

        og_dist = Fun.distance_between(target, self.pos)
        range_target = og_dist > self.weapon.range * 0.65
        if range_target:
            self.input["Right"] = self.pos[0] < move_target[0]
            self.input["Left"] = self.pos[0] > move_target[0]
            self.input["Down"] = self.pos[1] < move_target[1]
            self.input["Up"] = self.pos[1] > move_target[1]

        if og_dist < self.weapon.range * 0.3:
            self.input["Right"] = self.pos[0] > move_target[0]
            self.input["Left"] = self.pos[0] < move_target[0]
            self.input["Down"] = self.pos[1] > move_target[1]
            self.input["Up"] = self.pos[1] < move_target[1]

        # Check if something is in range
        if random.randint(0, self.weapon.fire_rate) == 0 and Fun.check_point_in_circle(
                self.weapon.range * 0.8, self.pos[0], self.pos[1], target[0], target[1]) and not wall_in:
            self.input["Shoot"] = True
        if self.weapon.weapon_class == "Melee":
            if Fun.distance_between(target, self.pos) <= self.weapon.range:
                # combo_stage = self.free_var[self.weapon.name]["Combo stage"]
                self.input["Shoot"] = self.free_var[self.weapon.name]["Press time"] < 40 #  - 10 * combo_stage

    entity_spread_apart(self, entities)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle
# Testing


def enemy_input_faction_1_basic(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)

        entity_maintain_weapon_range(self, og_dist, move_target, self.weapon.range * 0.65, get_away=64)
        entity_shoot_with_startup_lag(self, og_dist, self.weapon.range * 1.1)
        # Reloading
        if self.weapon.ammo == 0 and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
        self.input["Reload"] = True

    entity_shoot_startup_handler(self)

    entity_spread_apart(self, entities)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle
# Faction 1


def enemy_input_faction_1_body_guard(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)
    true_target = self.pos
    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)

        true_target = universal_pathfinding(self, level, move_target)
        if not true_target:
            true_target = move_target
            entity_maintain_weapon_range(self, og_dist, true_target, self.weapon.range * 0.65, get_away=64)
            entity_shoot_with_startup_lag(self, og_dist, self .weapon.range * 1.1)
        # Reloading
        if self.weapon.ammo == 0 and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
        self.input["Reload"] = True

    entity_shoot_startup_handler(self)
    entity_move_toward_point(self, true_target, 96)
    entity_spread_apart(self, entities)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def enemy_input_faction_1_heavy_sniper(self, entities, level):
    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    true_target = self.pos
    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)

        true_target = universal_pathfinding(self, level, move_target)
        if not true_target:
            true_target = move_target
            entity_maintain_weapon_range(self, og_dist, move_target, self.weapon.range * 0.65, get_away=64)
            entity_shoot_with_startup_lag(self, og_dist, self.weapon.range * 1.1)
        # Reloading
        if self.weapon.ammo == 0 and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
        self.input["Reload"] = True
    else:
        entity_dodge_bullets(self, entities, look_range=64)

    entity_shoot_startup_handler(self)

    entity_move_toward_point(self, true_target, 96)
    entity_spread_apart(self, entities)
    Fun.stunned_manager(self)
    return target, target_angle


def enemy_input_faction_1_radar(self, entities, level):
    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)

        entity_maintain_weapon_range(self, og_dist, move_target, 512, get_away=128)

    entity_escort_ally(self, entities, level, escort_list=["Missile Operator"], escort_dist=48, look_dist=128)
    entity_dodge_bullets(self, entities, look_range=64)

    entity_spread_apart(self, entities)
    Fun.stunned_manager(self)
    return target, target_angle


def enemy_input_faction_1_missile(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)
    true_target = self.pos
    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)

        true_target = universal_pathfinding(self, level, move_target)
        if not true_target:
            true_target = move_target
            entity_maintain_weapon_range(self, og_dist, move_target, self.weapon.range * 0.65, get_away=64)
            entity_shoot_no_startup_lag(self, og_dist, self.weapon.range * 1.1)

        # Reloading
        if self.weapon.ammo == 0 and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
        self.input["Reload"] = True

    entity_move_toward_point(self, true_target, 96)
    entity_spread_apart(self, entities)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def enemy_input_faction_1_drone(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)
    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)
        mod = 1
        # if self.reloading: mod = 3
        self.mouse_pos = self.target.pos
        entity_maintain_weapon_range(self, og_dist, move_target, self.weapon.range * 0.98 * mod, get_away=self.weapon.range * 0.75 * mod)
        entity_shoot_no_startup_lag(self, og_dist, self.weapon.range * 1.1)

    entity_spread_apart(self, entities)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def enemy_input_faction_2_basic(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)
    true_target = self.pos
    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)

        true_target = universal_pathfinding(self, level, move_target)
        if not true_target:
            true_target = move_target
            mod = 1
            # if self.reloading: mod = 3
            self.mouse_pos = self.target.pos
            entity_move_toward_point(self, true_target, 96)
            entity_maintain_weapon_range(self, og_dist, move_target, self.weapon.range * 0.98 * mod, get_away=self.weapon.range * 0.75 * mod)
            entity_shoot_no_startup_lag(self, og_dist, self.weapon.range * 1.1)
        entity_dodge_bullets(self, entities, 32)
        # Reloading
        if self.weapon.ammo == 0 and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
        self.input["Reload"] = True

    entity_spread_apart(self, entities)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def enemy_input_faction_2_boomstick(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)
    true_target = self.pos
    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)

        true_target = universal_pathfinding(self, level, move_target)
        if not true_target:
            true_target = move_target
            mod = 1
            if self.reloading: mod = 3
            self.mouse_pos = self.target.pos
            entity_move_toward_point(self, true_target, 96)
            entity_maintain_weapon_range(self, og_dist, move_target, self.weapon.range * 0.98 * mod, get_away=self.weapon.range * 0.75 * mod)
            entity_shoot_with_startup_lag(self, og_dist, self.weapon.range * 1.1)

        # Reloading
        if self.weapon.ammo == 0 and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
        self.input["Reload"] = True

    entity_shoot_startup_handler(self)
    entity_spread_apart(self, entities)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def enemy_input_faction_2_smoker(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)
    true_target = self.pos
    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)

        true_target = universal_pathfinding(self, level, move_target)
        if not true_target:
            true_target = move_target
            mod = 1
            # if self.reloading: mod = 3
            self.mouse_pos = self.target.pos
            entity_move_toward_point(self, true_target, 96)
            entity_maintain_weapon_range(self, og_dist, move_target, self.weapon.range * 0.98 * mod, get_away=self.weapon.range * 0.75 * mod)
            entity_shoot_no_startup_lag(self, og_dist, self.weapon.range * 1.1)
        entity_dodge_bullets(self, entities, 32)
        # Reloading
        if self.weapon.ammo == 0 and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
        self.input["Reload"] = True
    entity_escort_ally(self, entities, level, escort_list=("VIP", "BoomStick"), escort_dist=48, look_dist=256)

    entity_spread_apart(self, entities)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def enemy_input_faction_2_crusher(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)
    true_target = self.pos
    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)

        true_target = universal_pathfinding(self, level, move_target)
        if not true_target:
            true_target = move_target
            mod = 1
            # if self.reloading: mod = 3
            self.mouse_pos = self.target.pos
            entity_move_toward_point(self, true_target, 96)
            entity_maintain_weapon_range(self, og_dist, move_target, self.weapon.range * 0.66 * mod, get_away=self.weapon.range * 0.25 * mod)
            melee_fire_control(self, entities, level, target, wall_in)
        entity_dodge_bullets(self, entities, 32)
        # Reloading
        if self.weapon.ammo == 0 and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
        self.input["Reload"] = True

    entity_spread_apart(self, entities)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def enemy_input_faction_2_assassin(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)
    true_target = self.pos
    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)

        true_target = universal_pathfinding(self, level, move_target)
        if not true_target:
            true_target = move_target
            mod = 1
            # if self.reloading: mod = 3
            self.mouse_pos = self.target.pos
            entity_move_toward_point(self, Fun.move_with_vel_angle(true_target, 16, target_angle - 180), 80)
            entity_maintain_weapon_range(self, og_dist, move_target, self.weapon.range * 0.66 * mod, get_away=self.weapon.range * 0.25 * mod)
            #
            melee_fire_control_no_stopping(self, entities, level, target, wall_in)
        entity_dodge_bullets(self, entities, 32)
        # Reloading
        if self.weapon.ammo == 0 and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
        self.input["Reload"] = True

    entity_spread_apart(self, entities)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def enemy_input_faction_3_basic(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)
    true_target = self.pos
    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)

        true_target = universal_pathfinding(self, level, move_target)
        if not true_target:
            true_target = move_target
            mod = 1
            if self.reloading: mod = 3
            self.mouse_pos = self.target.pos
            entity_move_toward_point(self, true_target, 96)
            entity_maintain_weapon_range(self, og_dist, move_target, self.weapon.range * 0.98 * mod, get_away=self.weapon.range * 0.75 * mod)
            entity_shoot_no_startup_lag(self, og_dist, self.weapon.range * 1.1)

        # Reloading
        if self.weapon.ammo == 0 and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
        self.input["Reload"] = True

    entity_spread_apart(self, entities)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def enemy_input_faction_3_spotter(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)
    true_target = self.pos
    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)

        # true_target = universal_pathfinding(self, level, move_target)
        # if not true_target:
        #     true_target = move_target
            # entity_maintain_weapon_range(self, og_dist, move_target, self.weapon.range * 0.98, get_away=self.weapon.range * 0.75)
            # entity_shoot_no_startup_lag(self, og_dist, 256)
        #     self.input["Shoot"] = True
        #     entity_move_toward_point(self, true_target, 96)

        # Reloading

    entity_escort_ally(self, entities, level, escort_list=("VIP", "Artilleryman", "Bulwark"), escort_dist=48, look_dist=256)
    entity_spread_apart(self, entities)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def enemy_input_faction_3_artilleryman(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)
    true_target = self.pos
    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)

        true_target = universal_pathfinding(self, level, move_target)
        if not true_target:
            true_target = move_target
            # entity_maintain_weapon_range(self, og_dist, move_target, self.weapon.range * 0.98, get_away=self.weapon.range * 0.75)
            # entity_shoot_no_startup_lag(self, og_dist, 256)
            self.input["Shoot"] = True
            entity_move_toward_point(self, true_target, 96)

        # Reloading
        if self.weapon.ammo == 0 and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
        self.input["Reload"] = True

    entity_spread_apart(self, entities)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def enemy_input_faction_3_grenade(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)
    true_target = self.pos
    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)

        true_target = universal_pathfinding(self, level, move_target)
        if not true_target:
            true_target = move_target
            mod = 1
            if self.reloading: mod = 3
            self.mouse_pos = self.target.pos
            entity_move_toward_point(self, true_target, 96)
            entity_maintain_weapon_range(self, og_dist, move_target, 196 * 0.98 * mod, get_away=196 * 0.75 * mod)
            entity_shoot_no_startup_lag(self, og_dist, 196 * 1.1)

        # Reloading
        if self.weapon.ammo == 0 and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
        self.input["Reload"] = True

    entity_spread_apart(self, entities)
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def enemy_input_faction_3_bulwark(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)
    true_target = self.pos
    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)

        true_target = universal_pathfinding(self, level, move_target)
        if not true_target:
            true_target = move_target
            entity_maintain_weapon_range(self, og_dist, move_target, self.weapon.range * 1.2, get_away=64)
        entity_shoot_no_startup_lag(self, og_dist, self.weapon.range * 1.6)

        # Reloading
        if self.weapon.ammo == 0 and self.weapon.ammo_pool > 0:
            self.input["Reload"] = True
    elif self.weapon.ammo < self.weapon.max_ammo and self.weapon.ammo_pool > 0:
        self.input["Reload"] = True

    entity_move_toward_point(self, true_target, 96)
    entity_spread_apart(self, entities)
    # Stunning it doesn't disable it

    return target, target_angle


# |Enemy Act|-----------------------------------------------------------------------------------------------------------
def enemy_act_type_1(self, entities, level):
    # Get the inputs
    # target, target_angle = self.func_get_input(self, entities, {"enemies": []}, level)

    Fun.aim_system(self, self.weapon)

    # Do shit
    Fun.movement_entity(self)

    # I am placing the passive effects of enemies in the passive slot to not have to make more act functions
    self.weapon.passive(self, entities, level)
    self.crit = False
    # Gun
    if self.no_shoot_state == 0:
        self.reloading = False
        self.shooting = False
        if self.input["Alt fire"]:
            self.weapon.alt_fire(self, entities, level)
        if self.input["Shoot"] and self.weapon.ammo > 0:
            self.shooting = True
            self.shoot_bullet(entities, level)

        # Reloading
        if self.input["Reload"] and self.weapon.ammo_pool > 0:
            self.no_shoot_state, self.reloading = self.weapon.reload()
    else:
        self.shooting = False
        self.no_shoot_state -= 1

    # |Status effects|--------------------------------------------------------------------------------------------------
    Fun.status_manager(self, entities)

    # |Movement output|-------------------------------------------------------------------------------------------------
    Fun.movement_output(self, level)
    draw_aim_line(self, entities)
    if self.armour_break:
        # Need a sound effect
        self.armour_break = False


def enemy_act_type_2(self, entities, level):
    # Get the inputs
    # target, target_angle = self.func_get_input(self, entities, {"enemies": []}, level)

    Fun.aim_system(self, self.weapon)

    # Do shit
    Fun.movement_entity(self)

    self.crit = False
    # Gun
    if self.no_shoot_state == 0:
        self.reloading = False
        self.shooting = False
        if self.input["Shoot"] and self.weapon.ammo > 0:
            self.shooting = True
            self.shoot_bullet(entities, level)

    else:
        self.shooting = False
        self.no_shoot_state -= 1

    # |Status effects|--------------------------------------------------------------------------------------------------
    Fun.status_manager(self, entities)

    # |Movement output|-------------------------------------------------------------------------------------------------
    Fun.movement_output(self, level)


# |Enemy Draw|----------------------------------------------------------------------------------------------------------
def enemy_draw_basic(self, WIN, scrolling):
    # That one has animations
    if self.status["Stealth"] > 0:
        return
    # Draw the enemy
    WIN.blit(Fun.ENTITY_SHADOW, (self.pos[0]-16 + scrolling[0], self.pos[1] + 11 + scrolling[1]), special_flags=pg.BLEND_RGBA_SUB)
    enemy_direction = Fun.get_entity_direction(self.angle)
    # Fun.draw_entity(self, scrolling, WIN, enemy_direction)
    self.draw_player(scrolling, WIN, enemy_direction)

    # Draw the gun
    angle_to_add = 0
    if self.reloading:
        angle_to_add = (360 / self.weapon.reload_time) * self.no_shoot_state

    Fun.blitRotate(WIN, pg.transform.flip(self.weapon.sprite, True, -90 < self.aim_angle < 90),
                   Fun.move_with_vel_angle([self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]], 10,
                                           self.aim_angle),
                   [0, 0], 180 - self.aim_angle + angle_to_add)


def enemy_draw_no_gun(self, WIN, scrolling):
    # That one has animations
    if self.status["Stealth"] > 0:
        return
    # Draw the enemy
    WIN.blit(Fun.ENTITY_SHADOW, (self.pos[0]-16 + scrolling[0], self.pos[1] + 11 + scrolling[1]), special_flags=pg.BLEND_RGBA_SUB)
    enemy_direction = Fun.get_entity_direction(self.angle)
    # Fun.draw_entity(self, scrolling, WIN, enemy_direction)
    self.draw_player(scrolling, WIN, enemy_direction)


def enemy_draw_advanced_gun(self, WIN, scrolling):
    # That one has animations
    if self.status["Stealth"] > 0:
        return
    # Draw the enemy
    WIN.blit(Fun.ENTITY_SHADOW, (self.pos[0]-16 + scrolling[0], self.pos[1] + 11 + scrolling[1]), special_flags=pg.BLEND_RGBA_SUB)
    enemy_direction = Fun.get_entity_direction(self.angle)
    # Fun.draw_entity(self, scrolling, WIN, enemy_direction)
    self.draw_player(scrolling, WIN, enemy_direction)

    # Draw the gun
    draw_weapon(self, WIN, scrolling)


def enemy_draw_sniper(self, WIN, scrolling):
    enemy_draw_basic(self, WIN, scrolling)
    #


def enemy_draw_enforcer(self, WIN, scrolling):
    # That one has animations
    if self.status["Stealth"] > 0:
        return
    # Draw the enemy

    WIN.blit(Fun.ENTITY_SHADOW, (self.pos[0]-16 + scrolling[0], self.pos[1] + 11 + scrolling[1]), special_flags=pg.BLEND_RGBA_SUB)
    Fun.draw_spritestack(WIN, Fun.SPRITE_ENFORCER, [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]+8],
                         self.aim_angle + 90, height_diff=0.75)

    # Draw the gun
    angle_to_add = 0
    if self.reloading:
        angle_to_add = (360 / self.weapon.reload_time) * self.no_shoot_state

    Fun.blitRotate(WIN, pg.transform.flip(self.weapon.sprite, True, -90 < self.aim_angle < 90),
                   Fun.move_with_vel_angle([self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]], 10,
                                           self.aim_angle),
                   [0, 0], 180 - self.aim_angle + angle_to_add)
    #


def enemy_draw_bulwark(self, WIN, scrolling):
    # That one has animations
    if self.status["Stealth"] > 0:
        return
    # Draw the enemy

    WIN.blit(Fun.ENTITY_SHADOW, (self.pos[0]-16 + scrolling[0], self.pos[1] + 11 + scrolling[1]), special_flags=pg.BLEND_RGBA_SUB)
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
        frame_to_get = self.animation_counter[action_type] // 8 % 4
    Fun.draw_spritestack(WIN, Fun.SPRITE_BULWARKS[frame_to_get], [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]+10],
                         self.aim_angle + 90, height_diff=0.75)

    # Draw the gun
    angle_to_add = 0
    if self.reloading:
        angle_to_add = (360 / self.weapon.reload_time) * self.no_shoot_state

    Fun.blitRotate(WIN, pg.transform.flip(self.weapon.sprite, True, -90 < self.aim_angle < 90),
                   Fun.move_with_vel_angle([self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]], 4,
                                           self.aim_angle),
                   [0, 0], 180 - self.aim_angle + angle_to_add)
    #


# |On Death|------------------------------------------------------------------------------------------------------------
def enforcer_on_death(self, entities, level):
    Bullets.spawn_bullet(
        self, entities, Bullets.ExplosionSecondary, self.pos,
        0, [0, 30, 0, 20, {"Damage mod": 1, "Growth": 2, "Duration": 30}]
    )


# |Bosses|--------------------------------------------------------------------------------------------------------------
# Armoured Shield Generator
#   Laser cannon
def armoured_shield_generator_input(self, entities, level):

    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    # Find machine gun angle
    p_targets = {}
    for e in entities["entities"]:
        if e.team == self.team:
            continue
        if e.agro >= 0 and e.status["Stealth"] == 0:
            key = f"{e.agro}"
            if key not in p_targets:
                p_targets.update({key: [e]})
            else:
                p_targets[key].append(e)
    keys = list(p_targets.keys())
    keys.sort()
    self.free_var["Allow machine gun"] = False
    if p_targets:
        mod = -2
        if len(keys) == 1:
            mod = -1
        aaa = keys[mod]
        mg_target = p_targets[aaa][0]
        mg_target = mg_target.pos
        self.free_var["Allow machine gun"] = Fun.distance_between(mg_target, [self.pos[0], self.pos[1]-18]) < 40 * 7
        self.free_var["Machine Gun Angle"] = Fun.angle_value_limiter(
            Fun.move_angle(
                Fun.angle_between(mg_target, [self.pos[0], self.pos[1]-18]), self.free_var["Machine Gun Angle"], 7
            ))

    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)
        aim_target = self.target.pos.copy()

        entity_shoot_with_startup_lag(self, og_dist, 320)

    closest_target = Fun.find_closest_in_circle(self, entities, 512, "entities")
    if closest_target:
        fortress_move_toward_point(self, closest_target, 40 * 7)
        fortress_move_away_point(self, closest_target, 25 * 7)

        angle = Fun.angle_between(closest_target, self.pos)
        self.input["Right"] = self.free_var["Move angle"] < angle
        self.input["Left"] = self.free_var["Move angle"] > angle

        if not -(180 - 4) + angle < self.free_var["Move angle"] < 180 - 4 + angle:
            self.input["Right"] = self.free_var["Move angle"] > angle
            self.input["Left"] = self.free_var["Move angle"] < angle

        if self.free_var["Run people over"] <= 0:
            self.free_var["Run people over"] = 250
            self.input["Dash"] = True
        else:
            self.free_var["Run people over"] -=1

    entity_shoot_startup_handler(self)
    # Stunned status manager
    # Fun.stunned_manager(self)
    return target, target_angle


def armoured_shield_generator_act(self, entities, level):
    radius, radius_small = 90, 120
    for x in range(10):
        entities["particles"].append(
            Particles.RandomParticle0(
                Fun.move_with_vel_angle(self.pos, random.randint(radius, radius_small),
                                        self.free_var["Move angle"] + random.uniform(-48, 48)),
                [(128, 255 // 2, 255), (125, 200 // 2, 220), (85, 220 // 2, 220)][(self.time // 6) % 3],
                random.randint(4, 16), size=(1, 5)))

    for b in entities["bullets"]:
        if b.team == self.team:
            continue
        if type(b) in [Bullets.Laser, Bullets.Artillery, Bullets.ArtilleryFlare, Bullets.ArtillerySmoke]:
            continue
        if Fun.check_point_in_cone(radius, self.pos[0], self.pos[1], b.pos[0], b.pos[1],
                                         self.free_var["Move angle"], 48):
            # if Fun.distance_between(b.pos, self.pos) >= radius_small:
            b.duration = 0
            number_of_particle = 9
            for particles_to_add in range(360 // number_of_particle):
                entities["background particles"].append(Particles.RandomParticle2(
                    [b.pos[0], b.pos[1]], [(128, 255 // 2, 255), (125, 200 // 2, 220), (85, 220 // 2, 220)][((self.time + particles_to_add) // 6) % 3],
                    2 * random.random(), random.randint(15, 45),
                                                     particles_to_add * number_of_particle,
                    size=Fun.get_random_element_from_list([3, 4, 6])))

    angle = self.free_var["Move angle"] + 226 - 180
    pos = [self.pos[0], self.pos[1] - 16]
    pos = Fun.move_with_vel_angle(pos, 22.6274, angle)
    pos = Fun.move_with_vel_angle(pos, 20, self.aim_angle)
    turret_pos = Fun.move_with_vel_angle(
                    [self.pos[0], self.pos[1] - 30 * 0.75],
                    22.6274, self.free_var["Move angle"] + 226 - 180)
    # |Movement Input|----------------------------------------------------------------------------------------------
    self.running = False
    self.walking = False

    max_vel = self.vel_max

    # Handle double speed and slowness status
    if self.status["Slowness"]:
        max_vel *= 0.5
    if self.status["Double speed"]:
        max_vel *= 2

    # Checks for which direction the player must move
    if self.dash_cooldown <= 0:
        allow_correction = False
        speed = 0
        if self.input["Up"]:
            speed = 1
            allow_correction = True
        if self.input["Down"]:
            speed = -1
            allow_correction = True
        if self.input["Left"]:
            self.free_var["Move angle"] -= 0.8
        if self.input["Right"]:
            self.free_var["Move angle"] += 0.8
        self.vel = Fun.move_with_vel_angle(self.vel, self.speed * speed, self.free_var["Move angle"])

        if not Fun.check_point_in_circle(max_vel, 0, 0, self.vel[0], self.vel[1]) and allow_correction:
            self.vel = Fun.move_with_vel_angle([0, 0], max_vel * speed, self.free_var["Move angle"])
        self.walking = allow_correction

        self.free_var["Move angle"] = Fun.angle_value_limiter(self.free_var["Move angle"])
        # self.aim_angle = Fun.angle_value_limiter(self.aim_angle)

    self.standing_still = False
    if self.vel == [0, 0]:
        self.standing_still = True
    elif self.cutscene_mode:
        # This makes entities use their walking animation during cutscenes
        self.walking = True

    # Dash mechanic
    if self.dash_cooldown <= 0 and not self.standing_still and self.input["Dash"]:
        # Handle dash here
        Fun.play_sound("Player dash", modified_volume=0.25)
        dash_angle = self.free_var["Move angle"]
        self.dash_cooldown = self.dash_charge_time
        if self.status["Dash recovery up"] > 0:
            self.dash_cooldown //= 2
        self.vel = Fun.move_with_vel_angle(self.vel, self.dash_speed / self.friction * speed, dash_angle)
        for x in range(4):
            angle = dash_angle - 15 - 3.25 * 2 + x * 7.5 * 2
            entities["particles"].append(
                Particles.RandomParticle2(
                    Fun.move_with_vel_angle([self.pos[0], self.pos[1]], -4, angle),
                    Fun.WHITE, 1.5 + random.uniform(0, 2), 24, angle))

        if self.status["No damage"] < self.dash_iframes:
            self.status["No damage"] += self.dash_iframes
    self.dash_cooldown -= 1

    # |GunPlay|-----------------------------------------------------------------------------------------------------
    self.weapon.passive(self, entities, level)

    if self.target:
        self.angle = Fun.angle_between(self.target.pos, turret_pos)

        # Missile attack
        if start_up_lag_handler(self, 300, key="Startup lag missile"):
            pass
        elif self.free_var["Startup lag missile"] > 240:
            angle = self.free_var["Move angle"] + {
                "odd": -50, "even": 50
            }[Fun.meme(self.free_var["Startup lag missile"])]
            Bullets.spawn_bullet(
                self, entities,
                Bullets.Missile,
                Fun.move_with_vel_angle(Fun.move_with_vel_angle(self.pos, -20, self.free_var["Move angle"]), 30, angle),
                angle,
                [2 + 3 * random.random(), 180, 4, 3, {"Targeting range": 512,
                                                      "Targeting angle": 60,
                                                      "Target": "enemies",
                                                      "Secondary explosion": {"Duration": 5,
                                                                              "Growth": 2,
                                                                              "Damage mod": 0.75}}])
            if self.free_var["Startup lag missile"] % 4 == 0:
                # Fun.play_sound("Safety")
                Fun.play_sound("Com 1", modified_volume=1.4)

        # Railgun attack
        if start_up_lag_handler(self, 550, key="Startup lag railgun"):
            Fun.play_sound("Armoured Shield Generator Railgun", modified_volume=1.2)
            Bullets.spawn_bullet(
                self, entities,
                Bullets.LaserDanmaku2,
                Fun.move_with_vel_angle(turret_pos, 30, self.aim_angle),
                self.aim_angle,
                [0, 300, 1, 60, {'Colour': Fun.LIGHT_BLUE, "Growth": 32, "Bullet mod": [
                    {
                        "Target time": 295,
                        "speed": 40,
                        "Growth": 0
                    }
                ]}])
        elif self.free_var["Startup lag railgun"] > 350:
            if self.free_var["Startup lag railgun"] == 351:
                Fun.play_sound("Armoured Shield Generator Charging", "Voice")
            colour_pool = [Fun.YELLOW_LIGHT]
            if self.free_var["Startup lag railgun"] > 425:
                if self.free_var["Startup lag railgun"] == 426:
                    print("Aiming!!!!")
                    Fun.play_sound("Armoured Shield Generator Aiming", "Voice")
                if self.free_var["Startup lag railgun"] == 530:
                    Fun.play_sound("Armoured Shield Generator Fire", "Voice")
                colour_pool.append(Fun.ORANGE)
                Fun.play_sound("Charging", modified_volume=0.9)
            for x in range(2):
                dist = 64 * random.random()
                angle = self.aim_angle + random.uniform(-30, 30)
                pos = [turret_pos[0], turret_pos[1]]
                entities["particles"].append(Particles.RandomParticle2(Fun.move_with_vel_angle(pos, dist, angle),
                    Fun.get_random_element_from_list(colour_pool),
                    2, dist // 2,
                    angle + 180,
                    size=Fun.get_random_element_from_list([1, 2, 4])))

        # Tesla Coil attack
    else:
        self.free_var["Startup lag missile"] = 0
        self.free_var["Startup lag railgun"] = 0
        self.free_var["Startup lag tesla"] = 0

    Fun.aim_system(self, self.weapon)

    # |Status effects|--------------------------------------------------------------------------------------------------
    # ha ha, Fun go brr
    Fun.status_manager(self, entities)

    # |Movement Output|-------------------------------------------------------------------------------------------------
    # Make the player move
    Fun.movement_output(self, level)
    damage = round(abs(self.vel[0]) + abs(self.vel[1])) * 2
    if damage > 40:
        damage = 40
    for e in entities["entities"]:
        if e == self: continue
        if self.collision_box.colliderect(e.collision_box):
            e.vel = Fun.move_with_vel_angle(e.vel, 2, Fun.angle_between(e.collision_box.center, self.pos))
            if e.team != self.team:
                Fun.damage_calculation(e, damage, "Melee", death_message="Ran over")
            pass

    if self.draw_aim_line or self.weapon.laser_sight:
        entities["background particles"].append(Particles.LineParticle(
            Fun.move_with_vel_angle(turret_pos, 20, self.aim_angle), Fun.BLUE, 1, self.weapon.range-20, self.aim_angle, 2, 0))


def armoured_shield_generator_draw(self, WIN, scrolling):
    h_mod = 0.75

    pos = [self.pos[0], self.pos[1] + 8]
    Fun.draw_spritestack(WIN, Fun.SPRITE_ARMORED_GENERATOR_CHASSIS, [pos[0] + scrolling[0], pos[1] + scrolling[1]],
                         self.free_var["Move angle"] + 90, height_diff=h_mod)
    # 226
    # angle = 226 + self.free_var["Move angle"]e
    pos = [pos[0] + scrolling[0], pos[1] + scrolling[1] - 30 * h_mod]
    angle = self.free_var["Move angle"] + 226 - 180
    pos = Fun.move_with_vel_angle(pos, 22.6274, angle)
    Fun.draw_spritestack(WIN, Fun.SPRITE_ARMORED_GENERATOR_TURRET, pos, self.aim_angle + 90, height_diff=h_mod)


def armoured_shield_generator_on_death(self, entities, level):
    entities["UI particles"].append(
        Particles.ArmouredShieldGeneratorDeathParticle(self.pos, 300, self.free_var["Move angle"], self.aim_angle))


# AA Site
def aa_site_input(self, entities, level):
    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    return target, target_angle


def aa_site_act_init(self, entities, level):
    # Spawn other buildings
    # Swap act function
    pos = []
    for x in range(4):
        angle = 360 * random.random()
        new_pos = Fun.move_with_vel_angle(self.pos, 128 + 128 * random.random(), angle)
        if pos:
            keep_going = True
            while len(pos) > 0 and keep_going:
                keep_going = False
                for p in pos:
                     if Fun.check_point_in_circle(196, p[0], p[1], new_pos[0], new_pos[1]):
                         keep_going = True
                         break
                if keep_going:
                    angle += 180
                    new_pos = Fun.move_with_vel_angle(self.pos, 128 + 128 * random.random(), 360 * random.random())
                    angle = 360 * random.random()
        pos.append(new_pos)
    self.force_draw = True
    entities["entities"].append(Entity(enemy_repertory["AA Laser"], team=self.team, pos=pos[0], start_angle=random.randint(-180, 180)))
    entities["entities"][-1].force_draw = True
    entities["entities"].append(Entity(enemy_repertory["Missile Battery"], team=self.team, pos=pos[1], start_angle=random.randint(-180, 180)))
    entities["entities"][-1].force_draw = True
    entities["entities"].append(Entity(enemy_repertory["Shield Generator"], team=self.team, pos=pos[3], start_angle=random.randint(-180, 180)))
    entities["entities"][-1].force_draw = True
    entities["entities"].append(Entity(enemy_repertory["Drone builder"], team=self.team, pos=pos[2], start_angle=random.randint(-180, 180)))
    entities["entities"][-1].force_draw = True
    self.func_act = aa_site_act_energy_generator


# Need an anti-vehicular manslaughter mechanic
def aa_site_act_energy_generator(self, entities, level):
    # Check for other buildings
    build_count = 0
    for e in entities["entities"]:
        if e.team != self.team:
            continue
        if "AA Site" in e.free_var:
           build_count += 1
    # if no buildings, kill itself
    if build_count == 0:
        Fun.damage_calculation(self, Fun.BIG_INT, "Melee", ignore_no_damage=True, no_iframes=True, ignore_res=True, ignore_armour=True, death_message=f"Took {Fun.BIG_INT} damage")

    Fun.status_manager(self, entities)


def aa_site_on_death(self, entities, level):
    entities["particles"].append(Particles.NewExplosionEffect([self.pos[0], self.pos[1]],
                                                              duration=90,
                                                              particles=17,
                                                              radius=4,
                                                              particle_growth=3))
    Fun.play_sound("Explosion", "SFX")


def aa_site_on_death_energy_generator(self, entities, level):
    aa_site_on_death(self, entities, level)
    for e in entities["entities"]:
        if e.team != self.team:
            continue
        if "AA Site" in e.free_var or "Is ASS" in e.free_var:
            Fun.damage_calculation(e, Fun.BIG_INT, "Melee", ignore_no_damage=True, no_iframes=True, ignore_res=True, ignore_armour=True, death_message=f"Took {Fun.BIG_INT} damage")
        if "AA Site" in e.free_var:
            Bullets.spawn_bullet(self, entities, Bullets.ExplosionSecondary, e.pos, self.angle,
                                 [0, 5, 2, 0, {"Duration": 12, "Growth": 8,"Damage mod": 0}])


def aa_site_act_shield_generator(self, entities, level):
    # Check if a building has a shield.
    apply_shield = False
    if not self.free_var["Shield Target"]:
        apply_shield = True
    else:
        if self.free_var["Shield Target"].health <= 0:
            self.free_var["Shield Target"] = False
            apply_shield = True
        elif self.free_var["Shield Target"].armour <= 0:
            apply_shield = True
        else:
            # Visual effect
            for x in range(round(self.free_var["Shield Target"].armour // 10 * random.random())+4):
                entities["particles"].append(
                    Particles.RandomParticle0(
                        Fun.move_with_vel_angle(self.free_var["Shield Target"].pos, 48, 360 * random.random()),
                        [(128, 255//2, 255), (125, 200//2, 220), (85, 220//2, 220)][(self.time//6) % 3],
                        random.randint(6, 32), size=(1, 5)))

    Fun.status_manager(self, entities)

    if apply_shield:
        if self.free_var["Shield cooldown"] > 0:
            self.free_var["Shield cooldown"] -= 1
            # print(self.free_var["Shield cooldown"])
            return
        self.free_var["Shield cooldown"] = 320
        # If no, look for buildings with lowest health by % and give shield. Go on cooldown afterward
        target_pool = []
        lowest_hp_percent = 1
        for e in entities["entities"]:
            if e in [self, self.free_var["Previous Shield Target"]] or \
                    not ("AA Site" in e.free_var or "IS BOSS" in e.free_var):
                continue

            test_value = round(e.health / e.max_health, 2)
            if test_value == lowest_hp_percent:
                target_pool.append(e)
            if test_value < lowest_hp_percent:
                target_pool = [e]
                lowest_hp_percent = test_value
        if target_pool:
            self.free_var["Shield Target"] = Fun.get_random_element_from_list(target_pool)
            self.free_var["Shield Target"].armour = self.free_var["Shield Target"].health // 8
            self.free_var["Previous Shield Target"] = self.free_var["Shield Target"]
            for x in range(self.free_var["Shield Target"].armour // 5 + 4):
                entities["particles"].append(
                    Particles.RandomParticle2(
                        self.pos,
                        [(128, 255//2, 255), (125, 200//2, 220), (85, 220//2, 220)][(self.time//6) % 3],
                        3 + 5 * random.random(),
                        random.randint(6, 32), 360 * random.random()))


def aa_site_act_drone_factory(self, entities, level):
    # Spawn drones at a regular interval
    Fun.status_manager(self, entities)
    drone_count = 0
    for e in entities["entities"]:
        if "Is ASS" in e.free_var:
            drone_count += 1

    if drone_count < 12:
        if start_up_lag_handler(self, 60):
            #
            pos = Fun.move_with_vel_angle(self.pos, 16, self.angle)
            for x in range(8):
                entities["particles"].append(Particles.Smoke(Fun.random_point_in_circle(self.pos, 5)))
            entities["entities"].append(Entity(enemy_repertory["Drone"], team=self.team, pos=pos,
                                               start_angle=random.randint(-180, 180)))


def aa_site_act_missile_battery(self, entities, level):
    # Spawn missiles at a regular interval
    Fun.status_manager(self, entities)
    start_delay, interval_time, interval_amount = 90, 24, 4
    speed = 2
    missile_info = [speed, 320, 4, 10, {"Targeting range": 320,
                         "Targeting angle": 35,
                         "Manoeuvrability": 5,
                         "Target": "players",
                         "Secondary explosion": {"Duration": 10, "Growth": 6, "Damage mod": 1}}]
    angle = 360 * random.random()
    if self.target:
        angle = Fun.angle_between(self.target.pos, self.pos)

    if start_up_lag_handler(self, start_delay + interval_time * interval_amount):
        Fun.play_sound("Mech Missile")
        for x in range(3):
            Bullets.spawn_bullet(
                self, entities, Bullets.Missile, [self.pos[0], self.pos[1]],
                angle + random.uniform(-7, 7), missile_info)
    elif self.free_var["Startup lag"] > start_delay and self.free_var["Startup lag"] % interval_time == 0:
        Bullets.spawn_bullet(
                self, entities, Bullets.Missile, [self.pos[0], self.pos[1]],
                angle, missile_info)
        Fun.play_sound("Mech Missile")


def aa_site_on_death_shield_generator(self, entities, level):
    aa_site_on_death(self, entities, level)
    if self.free_var["Shield Target"]:
        self.free_var["Shield Target"].armour = 0


def aa_site_act_aa_laser(self, entities, level):
    if self.target and self.time > 300:
        self.free_var["Pos history"].append(self.target.pos.copy())
        # Make laser
        pos = [self.pos[0], self.pos[1] - 10]
        angle = Fun.angle_between(self.free_var["Pos history"][0], pos)
        self.free_var["Draw angle"] = angle
        dist = Fun.distance_between(pos, self.free_var["Pos history"][0])
        Bullets.spawn_bullet(self, entities, Bullets.Laser, pos,
                             angle, [0, 12, dist, 8, {"Colour": (107, 153, 165)}])
        entities["particles"].append(Particles.FireParticle(
            Fun.move_with_vel_angle(pos, dist, angle),
            colour=(107, 153, 165)))

    self.free_var["History limit"] = round(100 * self.health / self.max_health) + 10

    if len(self.free_var["Pos history"]) > self.free_var["History limit"]:
        self.free_var["Pos history"].pop(0)
    if len(self.free_var["Pos history"]) >= self.free_var["History limit"]:
        self.free_var["Pos history"].pop(0)

    Fun.status_manager(self, entities)


def aa_site_draw_energy_generator(self, WIN, scrolling):
    h_mod = 1
    Fun.draw_spritestack(WIN, Fun.SPRITE_AA_SITE_GENERATOR,
                            [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]],
                             self.angle, height_diff=h_mod)


def aa_site_draw_shield_generator(self, WIN, scrolling):
    h_mod = 1
    Fun.draw_spritestack(WIN, Fun.SPRITE_AA_SITE_SHIELD,
                            [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]],
                             self.angle, height_diff=h_mod)


def aa_site_draw_drone_factory(self, WIN, scrolling):
    h_mod = 1
    animation_state = round(self.free_var["Startup lag"] / 5)
    Fun.draw_spritestack(WIN, Fun.SPRITE_AA_SITE_FACTORY[animation_state],
                            [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]],
                             self.angle, height_diff=h_mod)


def aa_site_draw_missile_battery(self, WIN, scrolling):
    h_mod = 1
    Fun.draw_spritestack(WIN, Fun.SPRITE_AA_SITE_MISSILE,
                            [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]],
                             self.angle, height_diff=h_mod)


def aa_site_draw_aa_laser(self, WIN, scrolling):
    h_mod = 1
    Fun.draw_spritestack(WIN, Fun.SPRITE_AA_SITE_LASER,
                            [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]],
                             self.angle, height_diff=h_mod)

    Fun.draw_spritestack(WIN, Fun.SPRITE_AA_SITE_TURRET,
                            [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1] - len(Fun.SPRITE_AA_SITE_TURRET)],
                             self.free_var["Draw angle"] + 90, height_diff=h_mod)


# Hover Tank
def hover_tank_input(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    # Find machine gun angle
    p_targets = {}
    for e in entities["entities"]:
        if e.team == self.team:
            continue
        if e.agro >= 0 and e.status["Stealth"] == 0:
            key = f"{e.agro}"
            if key not in p_targets:
                p_targets.update({key: [e]})
            else:
                p_targets[key].append(e)
    keys = list(p_targets.keys())
    keys.sort()
    self.free_var["Allow machine gun"] = False
    if p_targets:
        mod = -2
        if len(keys) == 1:
            mod = -1
        aaa = keys[mod]
        mg_target = p_targets[aaa][0]
        mg_target = mg_target.pos
        self.free_var["Allow machine gun"] = Fun.distance_between(mg_target, [self.pos[0], self.pos[1]-18]) < 40 * 7
        self.free_var["Machine Gun Angle"] = Fun.angle_value_limiter(
            Fun.move_angle(
                Fun.angle_between(mg_target, [self.pos[0], self.pos[1]-18]), self.free_var["Machine Gun Angle"], 7
            ))

    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)
        aim_target = self.target.pos.copy()

        # basic_fire_control(self, entities, level, target, wall_in)
        entity_shoot_with_startup_lag(self, og_dist, 320)

    closest_target = Fun.find_closest_in_circle(self, entities, 512, "entities")
    if closest_target:
        fortress_move_toward_point(self, closest_target, 40 * 7)
        # fortress_move_away_point(self, closest_target, 25 * 7)

        if self.free_var["Run people over"] <= 0:
            self.free_var["Run people over"] = 250
            self.input["Dash"] = True
            # if  Fun.sounds_dict["Hover Tank Get Some"]["Sound"].get_num_channels() == 0:
            #     Fun.play_sound("Hover Tank Get In My Way", "Voice")
        else:
            self.free_var["Run people over"] -=1

    entity_shoot_startup_handler(self)
    # Stunned status manager
    # Fun.stunned_manager(self)
    return target, target_angle


def hover_tank_act(self, entities, level):
    angle = self.free_var["Move angle"] + 226 - 180
    pos = [self.pos[0], self.pos[1] - 16]
    pos = Fun.move_with_vel_angle(pos, 22.6274, angle)
    pos = Fun.move_with_vel_angle(pos, 20, self.aim_angle)
    # |Movement Input|----------------------------------------------------------------------------------------------
    self.running = False
    self.walking = False

    max_vel = self.vel_max

    # Handle double speed and slowness status
    if self.status["Slowness"]:
        max_vel *= 0.5
    if self.status["Double speed"]:
        max_vel *= 2

    # Checks for which direction the player must move
    # Rework it so that you are not faster when walking in diagonal, this should be fixed now
    if self.dash_cooldown <= 0:
        allow_correction = False
        speed = 0
        if self.input["Up"]:
            speed = 1
            allow_correction = True
        if self.input["Down"]:
            speed = -1
            allow_correction = True
        if self.input["Left"]:
            self.free_var["Move angle"] -= 3
            self.aim_angle -= 3
        if self.input["Right"]:
            self.free_var["Move angle"] += 3
            self.aim_angle += 3
        self.vel = Fun.move_with_vel_angle(self.vel, self.speed * speed, self.free_var["Move angle"])

        if not Fun.check_point_in_circle(max_vel, 0, 0, self.vel[0], self.vel[1]) and allow_correction:
            self.vel = Fun.move_with_vel_angle([0, 0], max_vel * speed, self.free_var["Move angle"])
        self.walking = allow_correction

        self.free_var["Move angle"] = Fun.angle_value_limiter(self.free_var["Move angle"])
        self.aim_angle = Fun.angle_value_limiter(self.aim_angle)

    self.standing_still = False
    if self.vel == [0, 0]:
        self.standing_still = True

    # Dash mechanic
    if self.dash_cooldown <= 0 and not self.standing_still and self.input["Dash"]:
        # Handle dash here
        Fun.play_sound("Player dash", modified_volume=0.25)
        dash_angle = self.free_var["Move angle"]
        self.dash_cooldown = self.dash_charge_time
        if self.status["Dash recovery up"] > 0:
            self.dash_cooldown //= 2
        self.vel = Fun.move_with_vel_angle(self.vel, self.dash_speed / self.friction * speed, dash_angle)
        for x in range(4):
            angle = dash_angle - 15 - 3.25 * 2 + x * 7.5 * 2
            entities["particles"].append(
                Particles.RandomParticle2(
                    Fun.move_with_vel_angle([self.pos[0], self.pos[1]], -4, angle),
                    Fun.WHITE, 1.5 + random.uniform(0, 2), 24, angle))

        if self.status["No damage"] < self.dash_iframes:
            self.status["No damage"] += self.dash_iframes
    self.dash_cooldown -= 1

    # |GunPlay|-----------------------------------------------------------------------------------------------------
    # angle, drawing_pos, length = self.aim_angle, pos, self.weapon.range + 20
    # Draw the lines
    # entities["background particles"].append(Fun.LineParticle(drawing_pos, Fun.RED, 1, length, angle, 1, 0))

    # entities["UI particles"].append(Fun.AimPoint(self.mouse_pos))
    if self.free_var["Startup lag"] == 180 and Fun.sounds_dict["Hover Tank Take That"]["Sound"].get_num_channels() == 0 and Fun.sounds_dict["Hover Tank Eat That"]["Sound"].get_num_channels() == 0:
        Fun.play_sound("Hover Tank Get Some", "Voice")
    if self.free_var["Grenade Shakedown"] > 0:

        if self.time % 3 == 0 and self.free_var["Allow machine gun"]:
            if self.time % 6 == 0:
                Fun.play_sound("Small arms")
                if random.random() < 0.15:
                    self.vel = Fun.move_with_vel_angle(self.vel, 7, self.free_var["Move angle"] + 45 * [1, -1][
                        round(random.random())])
            Bullets.spawn_bullet(self, entities, Bullets.Bullet, [self.pos[0], self.pos[1]-18],
                                 self.free_var["Machine Gun Angle"] + random.uniform(-self.weapon.accuracy,
                                                                 self.weapon.accuracy) + random.uniform(
                                     -self.weapon.spread, self.weapon.spread), [7, 40, 2.25, 4, {"Piercing": False, "Smoke": False}])
        if self.no_shoot_state == 0:
            # Reset variables
            self.reloading = False

            if self.input["Alt fire"]:
                self.weapon.alt_fire(self, entities, level)

            # |Main fire|-----------------------------------------------------------------------------------------------
            if self.input["Shoot"]:
                if self.weapon.ammo != 0 and self.shot_allowed:
                    # |Main fire|-------------------------------------------------------------------------------------------
                    self.shoot_bullet(entities, level)
                    # tell if the trigger was pressed
                    if not self.weapon.full_auto:
                        self.shot_allowed = False
                # if the trigger is not pressed and the weapon is not a full auto, allow to shoot for the next trigger press
                elif self.weapon.ammo == 0 and self.shot_allowed:
                    Fun.play_sound(self.weapon.jamming_sound, "SFX")
                    self.shot_allowed = False
            else:
                self.shot_allowed = True

            # |Reload|--------------------------------------------------------------------------------------------------
            if self.input["Reload"] and self.weapon.ammo_pool > 0:
                self.no_shoot_state, self.reloading = self.weapon.reload()
        else:
            self.no_shoot_state -= 1
        self.free_var["Grenade Shakedown"] -= 1
        self.free_var["Grenade Shakedown angle"] = [self.free_var["Move angle"], self.aim_angle]
        p = self.aim_angle
        self.aim_angle = Fun.angle_value_limiter(Fun.move_angle(self.angle, self.aim_angle, self.weapon.handle))
        if round(p) != round(self.aim_angle) and self.time % 12 == 0:
            Fun.play_sound("Chain click")
    elif self.free_var["Grenade Shakedown"] > -180:
        print(self.free_var["Grenade Shakedown"] )
        if self.free_var["Grenade Shakedown"] == 0:
            Fun.sounds_dict["Hover Tank Take That"]["Sound"].stop()
            Fun.play_sound(Fun.get_random_element_from_list(["Hover Tank Take That", "Hover Tank Eat That"]), "Voice")

        self.free_var["Grenade Shakedown"] -= 1
        angle = self.free_var["Grenade Shakedown"] * 6 + self.free_var["Grenade Shakedown angle"][0]
        self.free_var["Move angle"] = angle
        self.aim_angle = self.free_var["Grenade Shakedown angle"][1] + self.free_var["Grenade Shakedown"] * 6
        if self.free_var["Grenade Shakedown"] % 2 == 0 and self.free_var["Grenade Shakedown"] < 60:
            Bullets.spawn_bullet(
                self, entities, Bullets.BulletSlowing,
                Fun.move_with_vel_angle(self.pos, 32, self.aim_angle),
                self.aim_angle + random.uniform(-8, 8),
                [5 + 5 * random.random(), 320, 7, 8, {"Piercing": False, "Smoke": False, "Colour": (107, 165, 153),
                                                      "Slowdown rate": random.random() / 3}])

        if abs(self.free_var["Grenade Shakedown"]) % 8 == 0:
            Bullets.spawn_bullet(
                self, entities, Bullets.GrenadeType1,
                Fun.move_with_vel_angle(self.pos, 32, angle),
                angle,
                [4, 200, 4, 20, {"Secondary explosion": {"Duration": 10, "Growth": 4,
                                                        "Damage mod": 0}}])
            if abs(self.free_var["Grenade Shakedown"]) % 16 == 0:
                Fun.play_sound("Betel 2")
        # Shoot grenades
    else:
        self.free_var["Grenade Shakedown"] = 800
    self.weapon.passive(self, entities, level)

    # |Status effects|----------------------------------------------------------------------------------------------
    # ha ha, Fun go brr
    Fun.status_manager(self, entities)

    # |Movement Output|---------------------------------------------------------------------------------------------
    # Make the player move
    Fun.movement_output(self, level)
    damage = round(abs(self.vel[0]) + abs(self.vel[1])) * 2
    if damage > 40:
        damage = 40
    for e in entities["entities"]:
        if e == self: continue
        if self.collision_box.colliderect(e.collision_box):
            e.vel = Fun.move_with_vel_angle(e.vel, 2, Fun.angle_between(e.collision_box.center, self.pos))
            if e.team != self.team:
                Fun.damage_calculation(e, damage, "Melee", death_message="Ran over")
            pass
    if self.draw_aim_line or self.weapon.laser_sight:
        entities["background particles"].append(Particles.LineParticle(
            Fun.move_with_vel_angle(self.pos, 20, self.aim_angle), Fun.BLUE, 1, self.weapon.range-20, self.aim_angle, 2, 0))
# Cannon        DA DUM *big shot sound*, GET SOME *big shot sound*
# Grenades      EAT THAT, TAKE THAT
# Run over      GET IN THE WAY, IN THE WAY


def hover_tank_draw(self, WIN, scrolling):
    h_mod = 0.75
    Fun.draw_spritestack(WIN, Fun.SPRITE_HOVER_TANK_CHASSIS, [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]],
                         self.free_var["Move angle"] + 90, height_diff=h_mod)
    Fun.draw_spritestack(WIN, Fun.SPRITE_HOVER_TANK_TURRET, [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1] - 17 * h_mod],
                         self.aim_angle + 90, height_diff=h_mod)
    Fun.draw_spritestack(WIN, Fun.SPRITE_HOVER_TANK_GUN, [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1] - 24 * h_mod],
                         self.free_var["Machine Gun Angle"] + 90, height_diff=h_mod)


def hover_tank_on_death(self, entities, level):
    entities["UI particles"].append(
        Particles.HoverTankDeathParticle(self.pos, 300, self.free_var["Move angle"], self.aim_angle, self.free_var["Machine Gun Angle"]))


# Gilgamesh
def gilgamesh_input(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)
        dist = 420
        if self.no_shoot_state != 0:
            dist = 64
        entity_maintain_weapon_range(self, og_dist, move_target, dist, get_away=64)

    # Stunned status manager
    Fun.stunned_manager(self)

    entity_dodge_bullets(self, entities, 24)
    return target, target_angle


def gilgamesh_act(self, entities, level):
    # |Movement Input|----------------------------------------------------------------------------------------------

    Fun.movement_entity(self)
    Fun.aim_system(self, self.weapon)
    # |Status effects|----------------------------------------------------------------------------------------------
    # ha ha, Fun go brr
    Fun.status_manager(self, entities)
    if self.no_shoot_state == 0:
        # Attack logic
        {
            "Divorce Spiral": gilgamesh_divorce_spiral,
            "Reverse Divorce Spiral": gilgamesh_reverse_divorce_spiral,
            "Wall": gilgamesh_wall,
            "Desert flower": gilgamesh_desert_flower,
            "Desert dune": gilgamesh_desert_dune,
        }[self.free_var["Current attack"]](self, entities, level)

    else:
        self.no_shoot_state -= 1
    {
        "Trishot": gilgamesh_attack_1,
        "Dual shot": gilgamesh_attack_2,
        "Hose": gilgamesh_attack_3,
    }[self.free_var["Current sword attack"]](self, entities, level)

    # |Movement Output|---------------------------------------------------------------------------------------------
    # Make the player move
    Fun.movement_output(self, level)
    damage = round(abs(self.vel[0]) + abs(self.vel[1])) * 2
    if damage > 40:
        damage = 40
    for e in entities["entities"]:
        if e == self: continue
        if self.collision_box.colliderect(e.collision_box):
            e.vel = Fun.move_with_vel_angle(e.vel, 2, Fun.angle_between(e.collision_box.center, self.pos))
            if e.team != self.team:
                Fun.damage_calculation(e, damage, "Melee", death_message="Ran over")
            pass
    if self.draw_aim_line or self.weapon.laser_sight:
        entities["background particles"].append(Particles.LineParticle(
            Fun.move_with_vel_angle(self.pos, 20, self.aim_angle), Fun.BLUE, 1, self.weapon.range-20, self.aim_angle, 2, 0))


def gilgamesh_on_death(self, entities, level):
    entities["UI particles"].append(
        Particles.GilgameshDeathParticle(self.pos, 300, self.angle, self.aim_angle, self.draw_angle, self.weapon, self.draw_rotated_dist, self.weapon_draw_dist))


def gilgamesh_attack_1(self, entities, level):
    if start_up_lag_handler(self, 120, key="Startup lag sword"):
        self.free_var["Current sword attack"] = "Dual shot"
        self.draw_angle = 0
        self.draw_rotated_dist = 0
        self.weapon_draw_dist = 0
        return
    elif self.free_var["Startup lag sword"] % 40 == 0:
        Fun.play_sound("Gilgamesh Sword M")

        for x in range(3):
            angle = self.angle - 30 + 30 * x
            Bullets.spawn_bullet(
                self, entities,
                Bullets.Bullet,
                Fun.move_with_vel_angle(self.pos, 20, angle),
                angle,
                [4, 600, 4,
                 20 , {"Particle allowed": True,
                      "Burn chance": 0,
                      "Burn duration": 0,
                       "Damage type": "Fire",
                      "Colour": (25, 235, 25)
                      }])

    if self.free_var["Startup lag sword"] % 40 < 30:
        self.draw_angle += 3
        # self.draw_rotated_dist += 0.2
        self.weapon_draw_dist -= 0.4
    else:
        self.draw_angle -= 12
        self.weapon_draw_dist += 1.6


def gilgamesh_attack_2(self, entities, level):
    if start_up_lag_handler(self, 120, key="Startup lag sword"):
        self.free_var["Current sword attack"] = "Hose"
        self.draw_angle = 0
        self.draw_rotated_dist = 0
        self.weapon_draw_dist = 0
        return
    elif self.free_var["Startup lag sword"] % 40 == 0:
        Fun.play_sound("Gilgamesh Sword H")
        for x in range(2):
            angle = self.angle - 30 + 60 * x
            Bullets.spawn_bullet(
                self, entities,
                Bullets.Bullet,
                Fun.move_with_vel_angle(self.pos, 20, angle),
                angle,
                [4, 600, 4,
                 20 , {"Particle allowed": True,
                      "Burn chance": 0,
                      "Burn duration": 0,
                       "Damage type": "Fire",
                      "Colour": (25, 235, 25)
                      }])
    self.draw_angle = self.free_var["Startup lag sword"] * 3 * 3


def gilgamesh_attack_3(self, entities, level):
    if start_up_lag_handler(self, 120, key="Startup lag sword"):
        self.free_var["Current sword attack"] = "Trishot"
        self.draw_angle = 0
        self.draw_rotated_dist = 0
        self.weapon_draw_dist = 0
        return
    elif self.free_var["Startup lag sword"] % 3 == 0:
        for x in range(2):
            angle = self.angle + random.randint(-12, 12)
            Bullets.spawn_bullet(
                self, entities,
                Bullets.Bullet,
                Fun.move_with_vel_angle(self.pos, 20, angle),
                angle,
                [4, 600, 4,
                20 , {"Particle allowed": True,
                          "Burn chance": 0,
                          "Burn duration": 0,
                           "Damage type": "Fire",
                          "Colour": (25, 235, 25)
                          }])
    if self.free_var["Startup lag sword"] % 20 <= 15:
        self.weapon_draw_dist -= 24 / 15
        if self.free_var["Startup lag sword"] % 20 == 15:
            Fun.play_sound("Gilgamesh Sword L")
    else:
        self.weapon_draw_dist += 32 / 5
    self.draw_angle = math.sin(self.free_var["Startup lag sword"]//20) * 12


def gilgamesh_divorce_spiral(self, entities, level):
    if start_up_lag_handler(self, 72):
        self.no_shoot_state = 21
        self.free_var["Current attack"] = "Wall"
    elif self.free_var["Startup lag"] % 4 == 0:
        angle = self.angle + 10 * self.free_var["Startup lag"] // 2
        Bullets.spawn_bullet(
            self, entities,
            Bullets.Bullet,
            Fun.move_with_vel_angle(self.free_var["Pattern pos"], 20, angle),
            angle,
            [0.75, 600, 4,
            20 , {"Particle allowed": True,
                    "Burn chance": 0,
                    "Burn duration": 0,
                       "Damage type": "Fire",
                    "Colour": Fun.YELLOW_LIGHT
                    }])

    if self.free_var["Startup lag"] == 0:
        self.free_var["Pattern pos"] = self.pos.copy()


def gilgamesh_reverse_divorce_spiral(self, entities, level):
    if start_up_lag_handler(self, 72):
        self.no_shoot_state = 21
        self.free_var["Current attack"] = "Wall"
    elif self.free_var["Startup lag"] % 4 == 0:
        angle = self.angle - 19 * self.free_var["Startup lag"] // 2
        Bullets.spawn_bullet(
            self, entities,
            Bullets.Bullet,
            Fun.move_with_vel_angle(self.free_var["Pattern pos"], 20, angle),
            angle,
            [0.75, 600, 4,
            20 , {"Particle allowed": True,
                    "Burn chance": 0,
                    "Burn duration": 0,
                       "Damage type": "Fire",
                    "Colour": Fun.YELLOW_LIGHT
                    }])

    if self.free_var["Startup lag"] == 0:
        self.free_var["Pattern pos"] = self.pos.copy()


def gilgamesh_desert_flower(self, entities, level):
    if start_up_lag_handler(self, 72):
        self.no_shoot_state = 21
        self.free_var["Current attack"] = Fun.get_random_element_from_list(["Divorce Spiral", "Reverse Divorce Spiral"])
    elif self.free_var["Startup lag"] % 24 == 0:
        for x in range(6):
            angle = self.angle + 60 * x
            mod = self.free_var["Startup lag"] // 24 * self.free_var["Startup lag"] // 24 * 5
            for y in [mod, mod * -1]:
                Bullets.spawn_bullet(
                    self, entities,
                    Bullets.Bullet,
                    Fun.move_with_vel_angle(self.free_var["Pattern pos"], 20, angle + y),
                    angle,
                    [1.15, 600, 4,
                     20, {"Particle allowed": True,
                          "Burn chance": 0,
                          "Burn duration": 0,
                          "Damage type": "Fire",
                          "Colour": Fun.YELLOW_LIGHT
                          }])


    if self.free_var["Startup lag"] == 0:
        self.free_var["Pattern pos"] = self.pos.copy()


def gilgamesh_desert_dune(self, entities, level):
    if start_up_lag_handler(self, 72):
        self.no_shoot_state = 21
        self.free_var["Current attack"] = Fun.get_random_element_from_list(["Divorce Spiral", "Reverse Divorce Spiral"])
    elif self.free_var["Startup lag"] % 24 == 0:
        for x in range(6):
            angle = self.angle - 5 * self.free_var["Startup lag"] // 24 + 20 * x

            Bullets.spawn_bullet(
                self, entities,
                Bullets.Bullet,
                Fun.move_with_vel_angle(self.free_var["Pattern pos"], 20, angle),
                angle,
                [0.75, 600, 4,
                20 , {"Particle allowed": True,
                        "Burn chance": 0,
                        "Burn duration": 0,
                           "Damage type": "Fire",
                        "Colour": Fun.YELLOW_LIGHT
                        }])
            Bullets.spawn_bullet(
                self, entities,
                Bullets.Bullet,
                Fun.move_with_vel_angle(self.free_var["Pattern pos"], 20, angle - 180),
                angle - 180,
                [0.75, 600, 4,
                20 , {"Particle allowed": True,
                        "Burn chance": 0,
                        "Burn duration": 0,
                           "Damage type": "Fire",
                        "Colour": Fun.YELLOW_LIGHT
                        }])
    if self.free_var["Startup lag"] == 0:
        self.free_var["Pattern pos"] = self.pos.copy()


def gilgamesh_wall(self, entities, level):
    if start_up_lag_handler(self, 22):
        self.no_shoot_state = 0
        self.free_var["Current attack"] = Fun.get_random_element_from_list(["Desert dune", "Desert flower"])

        for x in range(32):
            angle = self.angle
            Bullets.spawn_bullet(
                self, entities,
                Bullets.BulletSlowing,
                Fun.move_with_vel_angle(Fun.move_with_vel_angle(self.free_var["Pattern pos"], random.uniform(-48, 48), angle + 90), 20, angle),
                angle,
                [6, 600, 8,
                 20 , {"Slowdown rate": random.random() * 0.2,
                       "Particle allowed": True,
                    "Burn chance": 0,
                    "Burn duration": 0,
                      "Colour": Fun.YELLOW_LIGHT
                      }])
    if self.free_var["Startup lag"] == 0:
        self.free_var["Pattern pos"] = self.pos.copy()


# Fire Support Mech
def bloodhound_input(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)
        aim_target = self.target.pos.copy()

        entity_shoot_with_startup_lag(self, og_dist, 320)

    closest_target = Fun.find_closest_in_circle(self, entities, 512, "entities")
    if closest_target:
        fortress_move_toward_point(self, closest_target, 40 * 7)
        fortress_move_away_point(self, closest_target, 25 * 7)

        angle = Fun.angle_between(closest_target, self.pos)
        self.input["Right"] = self.free_var["Move angle"] < angle
        self.input["Left"] = self.free_var["Move angle"] > angle

        if not -(180 - 4) + angle < self.free_var["Move angle"] < 180 - 4 + angle:
            self.input["Right"] = self.free_var["Move angle"] > angle
            self.input["Left"] = self.free_var["Move angle"] < angle

    # Stunned status manager
    # Fun.stunned_manager(self)
    return target, target_angle


def bloodhound_act(self, entities, level):
    # |Movement Input|----------------------------------------------------------------------------------------------
    self.running = False
    self.walking = False

    max_vel = self.vel_max

    # Handle double speed and slowness status
    if self.status["Slowness"]:
        max_vel *= 0.5
    if self.status["Double speed"]:
        max_vel *= 2

    # Quick boost
    bloodhound_boost(self, entities, level)
    # Checks for which direction the player must move
    # Rework it so that you are not faster when walking in diagonal, this should be fixed now
    if self.dash_cooldown <= 0:
        allow_correction = False
        speed = 0
        if self.input["Up"]:
            speed = 1
            allow_correction = True
        if self.input["Down"]:
            speed = -1
            allow_correction = True
        if self.input["Left"]:
            self.free_var["Move angle"] -= self.free_var["Turn speed"]
        if self.input["Right"]:
            self.free_var["Move angle"] += self.free_var["Turn speed"]
        self.vel = Fun.move_with_vel_angle(self.vel, self.speed * speed, self.free_var["Move angle"])

        if not Fun.check_point_in_circle(max_vel, 0, 0, self.vel[0], self.vel[1]) and allow_correction:
            self.vel = Fun.move_with_vel_angle([0, 0], max_vel * speed, self.free_var["Move angle"])
        self.walking = allow_correction

        self.free_var["Move angle"] = Fun.angle_value_limiter(self.free_var["Move angle"])
        self.aim_angle = Fun.angle_value_limiter(self.aim_angle)

    self.standing_still = False
    if self.vel == [0, 0]:
        self.standing_still = True

    # Fun.aim_system(self, self.weapon)
    self.aim_angle = self.free_var["Move angle"]
    # |Status effects|----------------------------------------------------------------------------------------------
    # ha ha, Fun go brr
    Fun.status_manager(self, entities)
    if self.no_shoot_state == 0:
        # Attack logic
        {
            "Missile": bloodhound_hadean_missile,
            "Blade": bloodhound_magma_blade,
            "Minigun": bloodhound_lopolith_minigun,
            "Canon": bloodhound_canon
        } [self.free_var["Current attack"]](self, entities, level)

    else:
        self.no_shoot_state -= 1
        if self.no_shoot_state == 0:
            self.free_var["Mech"].reset_animations()

    # |Movement Output|---------------------------------------------------------------------------------------------
    # Make the player move
    Fun.movement_output(self, level)
    damage = round(abs(self.vel[0]) + abs(self.vel[1])) * 2
    if damage > 40:
        damage = 40
    for e in entities["entities"]:
        if e == self: continue
        if self.collision_box.colliderect(e.collision_box):
            e.vel = Fun.move_with_vel_angle(e.vel, 2, Fun.angle_between(e.collision_box.center, self.pos))
            if e.team != self.team:
                Fun.damage_calculation(e, damage, "Melee", death_message="Ran over")
            pass
    if self.draw_aim_line or self.weapon.laser_sight:
        entities["background particles"].append(Particles.LineParticle(
            Fun.move_with_vel_angle(self.pos, 20, self.aim_angle), Fun.BLUE, 1, self.weapon.range-20, self.aim_angle, 2, 0))


def bloodhound_draw(self, WIN, scrolling):
    self.free_var["Mech"].pos = [self.pos[0] + scrolling[0], self.pos[1] + 28 + scrolling[1]]
    self.free_var["Mech"].draw(WIN, self.free_var["Move angle"])
    self.free_var["Mech"].mech_parts["Leg"]["Animation state"] = -1

    frame_to_get = -1
    if not self.standing_still:
        # print(player_direction)
        # self.animation_counter["Walk"] += round((abs(self.vel[0]) + abs(self.vel[1])//4))
        self.animation_counter["Walk"] += 1
        frame_to_get = self.animation_counter["Walk"] // 7 % (6 - 1) + 1
    self.free_var["Mech"].mech_parts["Leg"]["Animation state"] = frame_to_get


def bloodhound_on_death(self, entities, level):
    entities["UI particles"].append(Particles.BloodHoundDeathParticle(self.pos, 1200, self.free_var["Mech"], self.free_var["Move angle"]))


def bloodhound_hadean_missile(self, entities, level):
    if start_up_lag_handler(self, 200):
        self.no_shoot_state = 10
        self.free_var["Current attack"] = Fun.get_random_element_from_list(["Minigun", "Blade", "Blade"])

    elif 30 <= self.free_var["Startup lag"] <= 190 and self.free_var["Startup lag"] % 10 == 0:
        if self.free_var["Startup lag"] % 40 == 0 and 40 < self.free_var["Startup lag"]:
            Fun.play_sound("Bloodhound And That", "Voice")

        # spawn fire
        angle = self.free_var["Mech"].mech_parts["Torso"]["Draw angle"] * -1 + self.free_var["Move angle"]
        Fun.play_sound("Mech Missile")
        Bullets.spawn_bullet(
            self, entities,
            Bullets.Missile,
            Fun.move_with_vel_angle(self.pos, -10, angle+20),
            angle + random.uniform(-20, 20),
            [2 + 3 * random.random(), 140, 4, 3, {"Targeting range": 512,
                                                  "Targeting angle": 60,
                                                  "Target": "players",
                                                  "Secondary explosion": {"Duration": 5,
                                                                          "Growth": 2,
                                                                          "Damage mod": 0.75}}])
    elif self.free_var["Startup lag"] == 29:
        Fun.play_sound("Bloodhound Take That", "Voice")
        for x in ["Side Boost L", "Side Boost R", "Side Boost L", "Side Boost R", "Side Boost L", "Side Boost R"]:
            self.free_var["Boost type"].append(x)


def bloodhound_lopolith_minigun(self, entities, level):
    animation = True
    if start_up_lag_handler(self, 240):
        self.no_shoot_state = 10
        self.free_var["Mech"].reset_animations()
        self.free_var["Current attack"] = Fun.get_random_element_from_list(["Canon", "Missile", "Missile"])
        animation = False

    elif 80 <= self.free_var["Startup lag"] < 230:
        if self.free_var["Startup lag"] == 80:
            self.free_var["Boost type"].append("Forward Boost")
        if self.free_var["Startup lag"] % 4 == 0:
            Fun.play_sound("Mech Minigun")

        # spawn fire
        angle = self.free_var["Mech"].mech_parts["Arm L"]["Draw angle"] * -1 + self.free_var["Move angle"]
        Bullets.spawn_bullet(
            self, entities,
            Bullets.Bullet,
            Fun.move_with_vel_angle(Fun.move_with_vel_angle(self.pos, -27, self.free_var["Move angle"] + 90 + self.free_var["Mech"].mech_parts["Torso"]["Draw angle"] * -1), 20, angle),
            angle + random.uniform(-2, 2),
            [7, 50, 2, 10, {"Piercing": True, "Smoke": False}])

    # if self.free_var["Startup lag"] == 1:
    if not self.free_var["Mech"].mech_animations["Torso"] and animation:
        # Load animations
        self.free_var["Mech"].mech_animations["Torso"].append({"Time": 60, "Angle Speed": 1.2})
        self.free_var["Mech"].mech_animations["Arm L"].append({"Time": 60, "Angle Speed": 1.2})

        self.free_var["Mech"].mech_animations["Torso"].append({"Time": 80, "Angle Speed": -1.2})
        self.free_var["Mech"].mech_animations["Arm L"].append({"Time": 80, "Angle Speed": -1.2})

        self.free_var["Mech"].mech_animations["Torso"].append({"Time": 40, "Angle Speed": 1.2})
        self.free_var["Mech"].mech_animations["Arm L"].append({"Time": 40, "Angle Speed": 1.2})

        self.free_var["Mech"].mech_animations["Torso"].append({"Time": 40, "Angle Speed": -1.2})
        self.free_var["Mech"].mech_animations["Arm L"].append({"Time": 40, "Angle Speed": -1.2})

        self.free_var["Mech"].mech_animations["Torso"].append({"Time": 20, "Angle Speed": 1.2})
        self.free_var["Mech"].mech_animations["Arm L"].append({"Time": 20, "Angle Speed": 1.2})


def bloodhound_magma_blade(self, entities, level):
    animation = True
    if start_up_lag_handler(self, 120):
        self.no_shoot_state = 10
        self.free_var["Mech"].reset_animations()
        self.free_var["Current attack"] = Fun.get_random_element_from_list(["Canon", "Canon", "Missile"])
        animation = False

    elif self.free_var["Startup lag"] == 80:
        Fun.play_sound("Bloodhound Burn", "Voice")

    elif 80 < self.free_var["Startup lag"] < 110:
        # spawn fire
        angle = self.free_var["Mech"].mech_parts["Arm R"]["Draw angle"] * -1 + self.free_var["Move angle"]
        Bullets.spawn_bullet(
            self, entities,
            Bullets.Napalm,
            Fun.move_with_vel_angle(Fun.move_with_vel_angle(self.pos, 40, self.free_var["Move angle"] + 90 + self.free_var["Mech"].mech_parts["Torso"]["Draw angle"] * -1), 10, angle),
            angle + random.uniform(-2, 2),
            [2 + 4 * random.random(), 180 + random.randint(0, 100), 14,
             20, {"Particle allowed": True,
                  "Burn chance": 0.8,
                  "Burn duration": 30,
                  "Colour": Fun.FIRE,
                  }])
    elif self.free_var["Startup lag"] == 70:
        Fun.play_sound("Magma Blade")

    # if self.free_var["Startup lag"] == 1:
    if not self.free_var["Mech"].mech_animations["Torso"] and animation:
        self.free_var["Boost type"].append(Fun.get_random_element_from_list(["Turn Boost L", "Turn Boost R"]))
        # Load animations
        self.free_var["Mech"].mech_animations["Torso"].append({"Time": 60, "Angle Speed": -1.2})
        self.free_var["Mech"].mech_animations["Arm R"].append({"Time": 60, "Angle Speed": -1.2})

        self.free_var["Mech"].mech_animations["Torso"].append({"Time": 40, "Angle Speed": 2.4})
        self.free_var["Mech"].mech_animations["Arm R"].append({"Time": 40, "Angle Speed": 2.4})

        self.free_var["Mech"].mech_animations["Torso"].append({"Time": 20, "Angle Speed": -1.2})
        self.free_var["Mech"].mech_animations["Arm R"].append({"Time": 20, "Angle Speed": -1.2})


def bloodhound_canon(self, entities, level):
    if start_up_lag_handler(self, 120):
        self.no_shoot_state = 10
        self.free_var["Current attack"] = Fun.get_random_element_from_list(["Minigun", "Minigun", "Blade"])
    elif self.free_var["Startup lag"] % 15 == 1:
        Fun.play_sound("Mech Cannon")
    elif self.free_var["Startup lag"] % 15 == 14:
        angle = self.free_var["Move angle"] + random.uniform(-25, 25)
        Bullets.spawn_bullet(
            self, entities,
            Bullets.Artillery,
            Fun.move_with_vel_angle(self.pos, self.free_var["Startup lag"] * 4, angle),
            angle,
            [2, 60, 50,
             30, {"Secondary explosion":{"Duration": 20, "Strength": 120, "Radius":64}, "Colour": Fun.DARK_RED, "Slowdown rate": 0.05}])
    elif self.free_var["Startup lag"] == 2:

        Fun.play_sound("Bloodhound Disappear", "Voice")
        self.free_var["Boost type"] = ["Backward Boost"]


def bloodhound_boost(self, entities, level):
    if not self.free_var["Boost type"]:
        return

    if start_up_lag_handler(self, 30, key="Startup lag boost"):
        self.free_var["Boost type"].pop(0)
        self.free_var["Turn speed"] = 2
        # self.free_var["Startup lag boost"] = -1
    elif self.free_var["Startup lag boost"] > 2:
        if "Turn" in self.free_var["Boost type"][0]:
            if self.free_var["Boost type"][0] == "Turn Boost L":
                self.input["Left"] = True
                self.input["Right"] = False
                side = 90
            if self.free_var["Boost type"][0] == "Turn Boost R":
                self.input["Left"] = False
                self.input["Right"] = True
                side = -90

            for y in range(4):
                angle = self.free_var["Move angle"] + side + random.uniform(-12.5, 12.5)
                entities["particles"].append(Particles.FireParticle(
                    Fun.move_with_vel_angle([self.pos[0], self.pos[1] + 28], random.uniform(7, 25), angle),
                    colour=Fun.FIRE))

            return
        self.input["Up"] = False
        self.input["Down"] = False
        self.input["Right"] = False
        self.input["Left"] = False
    elif self.free_var["Startup lag boost"] == 2:
        if "Turn" in self.free_var["Boost type"][0]:
            self.free_var["Turn speed"] = 6
            return
        Fun.play_sound("Mech Booster")  # Change sound
        side = {
            "Forward Boost": 0,
            "Side Boost R": 90,
            "Side Boost L": -90,
            "Backward Boost": 180,
        }[self.free_var["Boost type"][0]]
        self.vel = [0, 0]
        self.vel = Fun.move_with_vel_angle([0, 0], 25, side + self.free_var["Move angle"])

        # Boost effects
        if self.free_var["Boost type"][0] == "Backward Boost":
            for x in [33, -33]:
                for y in range(7):
                    angle = self.free_var["Move angle"] + x + random.uniform(-7.5, 7.5)
                    # entities["particles"].append(Particles.FireParticle(
                    #     Fun.move_with_vel_angle([self.pos[0], self.pos[1] + 28], random.uniform(6, 15), angle),
                    #     colour=Fun.FIRE))

                    entities["particles"].append(Particles.RandomParticle2(
                        Fun.move_with_vel_angle([self.pos[0], self.pos[1] + 28], random.uniform(6, 15), angle),
                        Fun.FIRE,
                        random.uniform(2, 4), 60, angle, size=random.randint(4, 8)))
            for x in range(9):
                angle = self.free_var["Move angle"] + side + random.uniform(80, 100) * [-1, 1][round(random.random())]
                entities["particles"].append(Particles.RandomParticle2(
                    Fun.move_with_vel_angle([self.pos[0], self.pos[1] + 28], random.uniform(6, 15), angle),
                    Fun.get_random_element_from_list([Fun.GRAY, Fun.LIGHT_GRAY, Fun.WHITE]),
                    random.uniform(3, 5), 35, angle, size=random.randint(3, 7)))
            return


        for y in range(14):
            angle = self.free_var["Move angle"] + side + random.uniform(-9.5, 9.5) + 180
            # entities["particles"].append(Particles.FireParticle(Fun.move_with_vel_angle([self.pos[0], self.pos[1] + 28], random.uniform(6, 15), angle), colour=Fun.FIRE))

            entities["particles"].append(Particles.RandomParticle2(
                Fun.move_with_vel_angle([self.pos[0], self.pos[1] + 28], random.uniform(6, 15), angle),
                Fun.FIRE,
                random.uniform(2, 4), 60, angle, size=random.randint(4, 8)))
        for x in range(9):
            angle = self.free_var["Move angle"] + side + random.uniform(80, 100) * [-1, 1][round(random.random())]
            entities["particles"].append(Particles.RandomParticle2(
                Fun.move_with_vel_angle([self.pos[0], self.pos[1] + 28], random.uniform(6, 15), angle),
                Fun.get_random_element_from_list([Fun.GRAY, Fun.LIGHT_GRAY, Fun.WHITE]),
                random.uniform(3, 5), 35, angle, size=random.randint(3, 7))
            # (Fun.move_with_vel_angle([self.pos[0], self.pos[1] + 28], random.uniform(6, 15), angle), colour=Fun.FIRE)
                                         )


# Attack Helicopter
#   Could add different missile patterns
def attack_helicopter_input(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    # Find machine gun angle
    p_targets = {}
    for e in entities["entities"]:
        if e.team == self.team:
            continue
        if e.agro >= 0 and e.status["Stealth"] == 0:
            key = f"{e.agro}"
            if key not in p_targets:
                p_targets.update({key: [e]})
            else:
                p_targets[key].append(e)
    keys = list(p_targets.keys())
    keys.sort()
    self.free_var["Allow machine gun"] = False
    if p_targets:
        mod = -2
        if len(keys) == 1:
            mod = -1
        aaa = keys[mod]
        mg_target = p_targets[aaa][0]
        mg_target = mg_target.pos
        self.free_var["Allow machine gun"] = Fun.distance_between(mg_target, [self.pos[0], self.pos[1]-18]) < 40 * 7
        self.free_var["Machine Gun Angle"] = Fun.angle_value_limiter(
            Fun.move_angle(
                Fun.angle_between(mg_target, [self.pos[0], self.pos[1]-18]), self.free_var["Machine Gun Angle"], 7
            ))

    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)
        aim_target = self.target.pos.copy()

        # # basic_fire_control(self, entities, level, target, wall_in)
        entity_shoot_with_startup_lag(self, og_dist, 320)

    closest_target = Fun.find_closest_in_circle(self, entities, 512+128, "entities")
    if closest_target:
        fortress_move_toward_point(self, closest_target, 40 * (2 + 5 * math.sin(self.time/30)))
        fortress_move_away_point(self, closest_target, 35 * 2)
        if self.free_var["Run people over"] <= 0:
            self.free_var["Run people over"] = 250
            self.input["Dash"] = True
        else:
            self.free_var["Run people over"] -=1

    entity_shoot_startup_handler(self)
    if self.free_var["Startup lag"] == 120:
        Fun.play_sound("Attack Helicopter Locked On")
    if self.free_var["Startup lag"] == 190:
        Fun.play_sound({"HE": "Attack Helicopter Attack",
                           "Incendiary": "Attack Helicopter Fire",
                           "Shrapnel": "Attack Helicopter Nails"
                           }[self.free_var["Rocket type"]])

    # Stunned status manager
    # Fun.stunned_manager(self)
    return target, target_angle


def attack_helicopter_act(self, entities, level):
    # pos = Fun.move_with_vel_angle(pos, 22.6274, angle)
    # pos = Fun.move_with_vel_angle(pos, 20, self.aim_angle)
    # |Movement Input|----------------------------------------------------------------------------------------------
    self.running = False
    self.walking = False

    max_vel = self.vel_max

    # Handle double speed and slowness status
    # if self.status["Slowness"]:
    #     max_vel *= 0.5
    # if self.status["Double speed"]:
    #     max_vel *= 2

    # Checks for which direction the player must move
    # Rework it so that you are not faster when walking in diagonal, this should be fixed now
    if self.dash_cooldown <= 0:
        allow_correction = False
        speed = 0
        if self.input["Up"]:
            speed = 1
            allow_correction = True
        if self.input["Down"]:
            speed = -1
            allow_correction = True
        if self.input["Left"]:
            self.free_var["Move angle"] -= 3
            self.aim_angle -= 3
        if self.input["Right"]:
            self.free_var["Move angle"] += 3
            self.aim_angle += 3
        self.free_var["Move angle"] = self.angle
        self.aim_angle = self.angle
        self.vel = Fun.move_with_vel_angle(self.vel, self.speed * speed, self.free_var["Move angle"])

        if not Fun.check_point_in_circle(max_vel, 0, 0, self.vel[0], self.vel[1]) and allow_correction:
            self.vel = Fun.move_with_vel_angle([0, 0], max_vel * speed, self.free_var["Move angle"])
        self.walking = allow_correction

        self.free_var["Move angle"] = Fun.angle_value_limiter(self.free_var["Move angle"])
        self.aim_angle = Fun.angle_value_limiter(self.aim_angle)

    self.standing_still = False
    if self.vel == [0, 0]:
        self.standing_still = True
    elif self.cutscene_mode:
        # This makes entities use their walking animation during cutscenes
        self.walking = True

    # |GunPlay|-----------------------------------------------------------------------------------------------------
    # angle, drawing_pos, length = self.aim_angle, pos, self.weapon.range + 20
    # Draw the lines
    # entities["background particles"].append(Fun.LineParticle(drawing_pos, Fun.RED, 1, length, angle, 1, 0))

    self.weapon.passive(self, entities, level)
    if self.time % 2 == 0 and self.free_var["Allow machine gun"]:
        if self.time % 4 == 0:
            Fun.play_sound("Small arms")
        angle = self.aim_angle + 16 * math.sin(self.time / 2)
        Bullets.spawn_bullet(self, entities, Bullets.Bullet,
                             Fun.move_with_vel_angle([self.pos[0], self.pos[1] - 6], 56, angle),
                             angle, [7, 70, 2.25, 4, {"Piercing": False, "Smoke": False}])
    if self.no_shoot_state == 0:
        # Reset variables
        self.reloading = False
        if self.input["Alt fire"]:
            self.weapon.alt_fire(self, entities, level)

        # |Main fire|-----------------------------------------------------------------------------------------------
        if self.input["Shoot"]:
            #
            # Fun.sounds_dict["Hover Tank Take That"]["Sound"].stop()
            # Fun.play_sound(Fun.get_random_element_from_list(["Hover Tank Take That", "Hover Tank Eat That"]), "Voice")
            if self.weapon.ammo != 0 and self.shot_allowed:
                # |Main fire|-------------------------------------------------------------------------------------------
                # Fires rockets (HE, Incendiary, Grapeshot)
                b_info = [5, 160, 4, 80,
                          {"Targeting range": 300, "Targeting angle": 5, "Manoeuvrability": 2,  "Target": "enemies",
                           "Secondary explosion": {
                               "HE": {"Duration": 10, "Growth": 6, "Damage mod": 1},
                               "Incendiary": {
                        "Amount of Bullets": 16,
                        "Bullet Info": [5, 90, 4, 5,
                                        {"Particle allowed": True, "Burn chance": 1, "Burn duration": 30,
                                         "Colour": Fun.FIRE}]
                    },
                               "Shrapnel": {
                        "Amount of Bullets": 16,
                        "Bullet Info": [5, 90, 4, 5,
                                        {}],
                        "Angle range": 33
                    }
                           }[self.free_var["Rocket type"]]
                           }
                          ]

                b_class = {"HE": Bullets.Missile,
                           "Incendiary": Bullets.MissileIncendiary,
                           "Shrapnel": Bullets.MissileShrapnel
                           }[self.free_var["Rocket type"]]

                for x in range(8):
                    Bullets.spawn_bullet(
                        self, entities, b_class,
                        Fun.move_with_vel_angle(self.pos, (x // 2) * 8,
                                                [-90 + self.aim_angle, 90 + self.aim_angle][x % 2]),
                        self.aim_angle + [0, 0, -7.5, 7.5, -15, 15, -22.5, 22.5][x], b_info)
                    # self.slowdown_rate = 1 - random.random() * 2


                self.free_var["Rocket type"] = Fun.get_random_element_from_list(
                    {
                        "HE": ["Incendiary", "Shrapnel"],
                        "Incendiary": ["HE", "Shrapnel"],
                        "Shrapnel": ["HE", "Incendiary"]
                     }[self.free_var["Rocket type"]])
                # tell if the trigger was pressed
                if not self.weapon.full_auto:
                    self.shot_allowed = False
            # if the trigger is not pressed and the weapon is not a full auto, allow to shoot for the next trigger press
            elif self.weapon.ammo == 0 and self.shot_allowed:
                Fun.play_sound(self.weapon.jamming_sound, "SFX")
                self.shot_allowed = False
        else:
            self.shot_allowed = True

        # |Reload|--------------------------------------------------------------------------------------------------
        if self.input["Reload"] and self.weapon.ammo_pool > 0:
            self.no_shoot_state, self.reloading = self.weapon.reload()
    else:
        self.no_shoot_state -= 1
    p = self.aim_angle
    self.aim_angle = Fun.angle_value_limiter(Fun.move_angle(self.angle, self.aim_angle, self.weapon.handle))
    if round(p) != round(self.aim_angle) and self.time % 12 == 0:
        Fun.play_sound("Chain click")

    # Flares
    # if self.time % 180 == 0:
    #     for b in entities["bullets"]:
    #         if b.team == self.team:
    #             continue
    #         if "Manoeuvrability" in b.og_info[4]:
    #             if b.target_pos != self.pos:
    #                 continue
    #             # Flares effect
    #             if random.random() < 0.75:
    #                 #
    #                 b.team = self.team

    # |Status effects|----------------------------------------------------------------------------------------------
    # ha ha, Fun go brr
    Fun.status_manager(self, entities)

    # |Movement Output|---------------------------------------------------------------------------------------------
    # Make the player move
    if self.status["High friction"] > 0:
        self.vel = [self.vel[0] * 0.25, self.vel[1] * 0.25]

    # This give the direction the entity moves towards,
    # when using it for anything you should check if the entity is even moving
    self.direction_angle = Fun.angle_between(self.vel, [0, 0])

    # collision_check(self, level["map"])
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


def attack_helicopter_draw(self, WIN, scrolling):
    h_mod = 0.75
    WIN.blit(Fun.ENTITY_SHADOW_SIZE_2, Fun.move_with_vel_angle(
        (self.pos[0] - 32 + scrolling[0], self.pos[1] + 11 + scrolling[1]), 20, self.aim_angle),
        special_flags=pg.BLEND_RGBA_SUB)

    Fun.draw_spritestack(WIN, Fun.SPRITE_ATTACK_HELICOPTER, [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]],
                         self.aim_angle + 90, height_diff=h_mod)

    Fun.draw_spritestack(WIN, Fun.SPRITE_ATTACK_HELICOPTER_BLADE, Fun.move_with_vel_angle(
        [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1] - 37 * h_mod], 20, self.aim_angle),
                         self.time * 13.5, height_diff=h_mod)


def attack_helicopter_on_death(self, entities, level):
    Fun.play_sound("Attack Helicopter Death Scream", "Voice")
    entities["UI particles"].append(
        Particles.AttackHelicopterDeathParticle(self.pos, 300, self.aim_angle, self.time))


# Rigel
def rigel_input(self, entities, level):
    if self.no_shoot_state > 0:
        return
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)

        entity_shoot_with_startup_lag(self, og_dist, 320)

    closest_target = Fun.find_closest_in_circle(self, entities, 512, "entities")
    self.target = None
    if closest_target:
        if self.free_var["Current attack"] not in ["Shoulder Bash", "Lance Swipe", "Giga Thrust"]:
            fortress_move_toward_point(self, closest_target, 40 * 7)
            fortress_move_away_point(self, closest_target, 25 * 7)

        angle = Fun.angle_between(closest_target, self.pos)
        self.input["Right"] = self.free_var["Move angle"] < angle
        self.input["Left"] = self.free_var["Move angle"] > angle
        # self.target = closest_target
        if not -(180 - 4) + angle < self.free_var["Move angle"] < 180 - 4 + angle:
            self.input["Right"] = self.free_var["Move angle"] > angle
            self.input["Left"] = self.free_var["Move angle"] < angle

    # Stunned status manager
    # Fun.stunned_manager(self)
    return target, target_angle


def rigel_act(self, entities, level):
    # |Movement Input|----------------------------------------------------------------------------------------------
    self.running = False
    self.walking = False

    max_vel = self.vel_max

    if self.dash_cooldown <= 0:
        allow_correction = False
        speed = 0
        if self.input["Up"]:
            speed = 1
            allow_correction = True
        if self.input["Down"]:
            speed = -1
            allow_correction = True
        if self.input["Left"]:
            self.free_var["Move angle"] -= self.free_var["Turn speed"]
        if self.input["Right"]:
            self.free_var["Move angle"] += self.free_var["Turn speed"]
        self.vel = Fun.move_with_vel_angle(self.vel, self.speed * speed, self.free_var["Move angle"])

        if not Fun.check_point_in_circle(max_vel, 0, 0, self.vel[0], self.vel[1]) and allow_correction:
            self.vel = Fun.move_with_vel_angle([0, 0], max_vel * speed, self.free_var["Move angle"])
        self.walking = allow_correction

        self.free_var["Move angle"] = Fun.angle_value_limiter(self.free_var["Move angle"])
        self.aim_angle = Fun.angle_value_limiter(self.aim_angle)

    self.standing_still = False
    if self.vel == [0, 0]:
        self.standing_still = True

    # Fun.aim_system(self, self.weapon)
    self.aim_angle = self.free_var["Move angle"]
    # |Status effects|----------------------------------------------------------------------------------------------
    # ha ha, Fun go brr
    Fun.status_manager(self, entities)
    for x in self.free_var["Segments"]:
        self.free_var["Segments"][x]["Angle"] = self.free_var["Move angle"] - self.free_var["Mech"].mech_parts["Arm L"]["Draw angle"]
    if self.no_shoot_state == 0:
        # Attack logic
        {
            "Shoulder Bash": rigel_shoulder_bash,
            "Lance Swipe": rigel_lance_swipe,
            "Giga Thrust": rigel_giga_thrust,

            "Laser Barrage": rigel_laser_barrage,
            "Plasma": rigel_plasma,
            "Missile Circus": rigel_missile_circus,
            "Raining Hell": rigel_raining_hell
        } [self.free_var["Current attack"]](self, entities, level)

    else:
        self.no_shoot_state -= 1

    # Handle Missile Circus
    if self.free_var["Missile Circus"] > 0:
        if self.free_var["Missile Circus"] % 4 == 0:
            Fun.play_sound("Mech Missile")
            angle = self.free_var["Move angle"] - 180 - random.uniform(-45, 45)
            mod = random.random()
            Bullets.spawn_bullet(
                self, entities,
                Bullets.Missile,
                Fun.move_with_vel_angle(self.pos, 40 * mod, angle),
                angle - 180,
                [2 + 3 * mod, 180, 4, 3, {"Targeting range": 512,
                                 "Targeting angle": 60,
                                 "Target": "enemies",
                                 "Secondary explosion": {"Duration": 5,
                                                         "Growth": 2,
                                                         "Damage mod": 0.75}}])
        self.free_var["Missile Circus"] -= 1

    # |Movement Output|---------------------------------------------------------------------------------------------
    # Make the player move
    Fun.movement_output(self, level)
    damage = round(abs(self.vel[0]) + abs(self.vel[1])) * 2
    if damage > 40:
        damage = 40
    for e in entities["entities"]:
        if e == self: continue
        if self.collision_box.colliderect(e.collision_box):
            e.vel = Fun.move_with_vel_angle(e.vel, 2, Fun.angle_between(e.collision_box.center, self.pos))
            if e.team != self.team:
                Fun.damage_calculation(e, damage, "Melee", death_message="Ran over")
            pass
    if self.draw_aim_line or self.weapon.laser_sight:
        entities["background particles"].append(Particles.LineParticle(
            Fun.move_with_vel_angle(self.pos, 20, self.aim_angle), Fun.BLUE, 1, self.weapon.range-20, self.aim_angle, 2, 0))


def rigel_draw(self, WIN, scrolling):
    self.free_var["Mech"].pos = [self.pos[0] + scrolling[0], self.pos[1] + 28 + scrolling[1]]

    WIN.blit(Fun.ENTITY_SHADOW_SIZE_2, [self.free_var["Mech"].pos[0] - 64 + scrolling[0], self.free_var["Mech"].pos[1] + 64 + scrolling[1]], special_flags=pg.BLEND_RGBA_SUB)

    self.free_var["Mech"].draw(WIN, self.free_var["Move angle"])

    self.free_var["Mech"].mech_parts["Leg"]["Animation state"] = -1
    #
    frame_to_get = -1
    if not self.standing_still:
        self.animation_counter["Walk"] += round((abs(self.vel[0]) + abs(self.vel[1])//4))
        self.animation_counter["Walk"] += 1
        frame_to_get = self.animation_counter["Walk"] // 7 % (5 - 1) + 1
    self.free_var["Mech"].mech_parts["Leg"]["Animation state"] = frame_to_get

    # Canons/wing
    for x in range(3):
        pos = Fun.move_with_vel_angle(self.pos, 33 + x * 10, self.free_var["Move angle"] - self.free_var["Mech"].mech_parts["Arm L"]["Draw angle"] - 80)
        pos[1] -= self.free_var["Mech"].mech_parts["Arm L"]["offset"][2] - 8
        self.free_var["Segments"][f"{x + 1}"]["Pos"] = pos

        Fun.blitRotate(WIN, RIGEL_SEGMENT,
                       [
                           self.free_var["Segments"][f"{x + 1}"]["Pos"][0] + scrolling[0],
                           self.free_var["Segments"][f"{x + 1}"]["Pos"][1] + scrolling[1]
                       ],
                       RIGEL_SEGMENT_ORIGIN, self.free_var["Segments"][f"{x+1}"]["Angle"] * -1 + 90)


def rigel_on_death(self, entities, level):
    if self.free_var["Phase"] == 1:
        entities["UI particles"].append(Particles.RigelIntro())
        # Switch to phase 2
        self.health = round(self.max_health * 1.75)
        self.max_health = self.health
        self.status["No damage"] = 60 * 3
        self.status["No debuff"] = 60 * 3
        self.no_shoot_state = 180
        self.free_var["History limit"] = 25
        self.free_var["Phase"] = 2

        number_of_particle = 18
        for particles_to_add in range(360 // number_of_particle):
            entities["particles"].append(Particles.RandomParticle2(
                [self.pos[0], self.pos[1]], Fun.DARK_RED, 1 + 3 * random.random(), random.randint(45, 90),
                                                        particles_to_add * number_of_particle,
                size=Fun.get_random_element_from_list([3, 4, 6])))
        return
    # Make death particle
    entities["UI particles"].append(Particles.RigelDeathParticle(self.pos, 1200, self.free_var["Mech"], self.free_var["Move angle"]))

    level["events"].append(
        MissionEvent("Finishing", Event.trigger_on_for, False, [Event.change_scrolling_target], free_var={"Timer": 60 * 5, "Manual target": self.pos}))


def rigel_shoulder_bash(self, entities, level):
    animation = self.free_var["Startup lag"] <= 1
    if start_up_lag_handler(self, 60+80):
        self.free_var["Current attack"] = "Lance Swipe"
        self.free_var["Anti Missile Circus Spam"] = False
        animation = False
    elif self.free_var["Startup lag"] == 10:
        Fun.play_sound("Rigel Shoulder Bash")
        self.vel = Fun.move_with_vel_angle([0, 0], 35, self.free_var["Move angle"])


    if self.free_var["Startup lag"] > 10:
        if self.free_var["Startup lag"] % 3 == 0:
            pass
    damage = 40
    for e in entities["entities"]:
        if e == self: continue
        if self.collision_box.colliderect(e.collision_box):
            e.vel = Fun.move_with_vel_angle(e.vel, 2, Fun.angle_between(e.collision_box.center, self.pos))
            if e.team != self.team:
                Fun.damage_calculation(e, damage, "Melee", death_message="Tried to commit insurance fraud")

    self.input["Up"] = False
    self.input["Down"] = False
    self.input["Right"] = False
    self.input["Left"] = False

    if not self.free_var["Mech"].mech_animations["Torso"] and animation:
        self.free_var["Mech"].start_animation("Torso", 10, -80, 0)
        self.free_var["Mech"].start_animation("Arm R", 10, -20, 0)
        self.free_var["Mech"].start_animation("Torso", 130, -80, -80)
        self.free_var["Mech"].start_animation("Arm R", 130, -20, -20)


def rigel_lance_swipe(self, entities, level):
    animation = self.free_var["Startup lag"] <= 1
    if start_up_lag_handler(self, 20):
        self.free_var["Current attack"] = "Giga Thrust"

    angle = self.free_var["Mech"].mech_parts["Arm R"]["Draw angle"] * -1 + self.free_var["Move angle"]
    for x in range(2):
        Bullets.spawn_bullet(
            self, entities,
            Bullets.Bullet,
            Fun.move_with_vel_angle(Fun.move_with_vel_angle(self.pos, 40, self.free_var["Move angle"] + 90 +
                                                            self.free_var["Mech"].mech_parts["Torso"]["Draw angle"] * -1),
                                    10, angle),
            angle + random.uniform(-2, 2),
            [1 + 2 * random.random(), 180 + random.randint(0, 100), 4 + round(6 * random.random()),
             20, {"Colour": Fun.RIGEL_ENERGY}])
    if not self.free_var["Mech"].mech_animations["Torso"] and animation:
        Fun.play_sound("Rigel Lance Swipe")
        self.free_var["Mech"].start_animation("Torso", 20, 60, -80)
        self.free_var["Mech"].start_animation("Arm R", 20, 40, -20)


def rigel_giga_thrust(self, entities, level):
    animation = self.free_var["Startup lag"] <= 1
    if start_up_lag_handler(self, 200):
        self.free_var["Current attack"] = Fun.get_random_element_from_list(["Laser Barrage", "Plasma"])

        animation = False
    elif self.free_var["Startup lag"] == 1 and self.target and self.free_var["Phase"] == 2:
        self.free_var["Move angle"] = Fun.angle_between(self.target, self.pos) + random.uniform(-5, 5)    # Evil
    elif self.free_var["Startup lag"] == 15:
        # Boost effects
        for y in range(14):
            angle = self.free_var["Move angle"] + random.uniform(-33, 33)

            entities["particles"].append(Particles.RandomParticle2(
                Fun.move_with_vel_angle([self.pos[0], self.pos[1] + 28], random.uniform(6, 15), angle),
                Fun.RIGEL_ENERGY,
                random.uniform(10, 25), Fun.get_random_element_from_list([60, 90]), angle, size=random.randint(3, 6)))

        self.vel = Fun.move_with_vel_angle([0, 0], 35, self.free_var["Move angle"])

    elif 20 < self.free_var["Startup lag"] < 120:
        # entities["background particles"].append(Particles.LineParticle( self.pos, Fun.RED, 1, 48, self.free_var["Move angle"], 2, 0))
        mod = 120
        for e in entities["entities"]:
            if e == self:
                continue
            if Fun.check_point_in_cone(64, self.pos[0], self.pos[1], e.pos[0], e.pos[1], self.free_var["Move angle"], 33):
                if e.status["Stunned"] <= mod:
                    e.status["Stunned"] = mod
                Fun.damage_calculation(e, 30, "Melee", death_message="Skewered by the final boss")
                e.vel = Fun.move_with_vel_angle([0, 0], 7 * e.friction, self.free_var["Move angle"] + Fun.get_random_element_from_list([-33, 33]))

    if not self.free_var["Mech"].mech_animations["Torso"] and animation:
        Fun.play_sound("Rigel Giga Thrust")
        self.free_var["Mech"].start_animation("Torso", 20, -80, 60)
        self.free_var["Mech"].start_animation("Arm R", 20, 80, 40)
        self.free_var["Mech"].start_animation("Torso", 50, -80, -80)
        self.free_var["Mech"].start_animation("Arm R", 50, 80, 80)
        self.free_var["Mech"].start_animation("Torso", 50, 0, -80)
        self.free_var["Mech"].start_animation("Arm R", 50, 0, 80)
        self.free_var["Mech"].start_animation("Torso", 100, 0, 0)
        self.free_var["Mech"].start_animation("Arm R", 100, 0, 0)


def rigel_laser_barrage(self, entities, level):
    if start_up_lag_handler(self, 90):
        Fun.sounds_dict["Rigel Laser barrage"]["Sound"].fadeout(15)
        self.free_var["Current attack"] = Fun.get_random_element_from_list(["Missile Circus", "Raining Hell"])
        if  self.free_var["Anti Missile Circus Spam"]:
            self.free_var["Current attack"] = "Raining Hell"
    if self.free_var["Startup lag"] == 1:
        Fun.play_sound("Rigel Laser barrage")
        # Initialize the attack
        self.free_var["Pos history"] = {
                 "1": {"Target": None, "History": []},
                 "2": {"Target": None, "History": []},
                 "3": {"Target": None, "History": []},
             }
        count = 0
        for e in entities["entities"]:
            if self == e:
                continue
            self.free_var["Pos history"][f"{count+1}"]["Target"] = e
            self.free_var["Pos history"][f"{count+1}"]["History"].append(e.pos.copy())
            count += 1
            if count == 3:
                break

    else:
        for l in self.free_var["Pos history"]:
            if self.free_var["Pos history"][l]["Target"] is None:
                continue
            laser = self.free_var["Pos history"][l]      # {"Target": None, "History": []}
            laser["History"].append(laser["Target"].pos.copy())

            # Make laser
            # pos = [self.pos[0], self.pos[1] - 10 * int(l)]
            pos = self.free_var["Segments"][l]["Pos"]
            angle = Fun.angle_between(laser["History"][0], pos)
            self.free_var["Draw angle"] = angle
            dist = Fun.distance_between(pos, laser["History"][0]) - laser["Target"].thiccness//2
            Bullets.spawn_bullet(self, entities, Bullets.Laser, pos, angle, [0, 2, dist, 2, {"Colour": Fun.RIGEL_ENERGY}])
            self.free_var["Segments"][l]["Angle"] = angle
            entities["particles"].append(Particles.FireParticle(Fun.move_with_vel_angle(pos, dist, angle), colour=Fun.RIGEL_ENERGY))

            if len(laser["History"]) > self.free_var["History limit"]:
                laser["History"].pop(0)
            if len(laser["History"]) >= self.free_var["History limit"]:
                laser["History"].pop(0)


def rigel_plasma(self, entities, level):
    angle = self.free_var["Move angle"] - self.free_var["Mech"].mech_parts["Arm L"]["Draw angle"]
    b_pos = Fun.move_with_vel_angle([self.free_var["Segments"]["1"]["Pos"][0],
                                     self.free_var["Segments"]["1"]["Pos"][1]], 45, angle)

    if start_up_lag_handler(self, 90):
        # Shoot the bullet with tracking
        Fun.play_sound("Rigel Plasma Shoot")
        self.free_var["Current attack"] = Fun.get_random_element_from_list(["Missile Circus", "Raining Hell"])
        if self.free_var["Anti Missile Circus Spam"]:
            self.free_var["Current attack"] = "Raining Hell"
        duration = 240

        if self.free_var["Phase"] == 2:
            duration = 480
        Bullets.spawn_bullet(
            self, entities,
            Bullets.BulletHoming,
            b_pos,
            angle,
            [3, duration, 45, 60, {
                "Colour": Fun.RIGEL_ENERGY, "Targeting range": 1024, "Targeting angle": 360
            }])
    else:
        if self.free_var["Startup lag"] == 2:
            Fun.play_sound("Rigel Plasma")
        # Make bullet bigger
        Bullets.spawn_bullet(
            self, entities,
            Bullets.Bullet,
            b_pos,
            0,
            [0, 4, self.free_var["Startup lag"] / 2, 30, {"Piercing": True, "Colour": Fun.RIGEL_ENERGY}])
        # Segments point at it
        for l in self.free_var["Segments"]:
            self.free_var["Segments"][l]["Angle"] = {
                "1": angle - self.free_var["Startup lag"],
                "2": angle,
                "3": angle + self.free_var["Startup lag"]
            }[l]


def rigel_missile_circus(self, entities, level):
    animation = True
    if start_up_lag_handler(self, 30):
        self.free_var["Anti Missile Circus Spam"] = True
        self.free_var["Missile Circus"] = 120
        self.free_var["Current attack"] = "Shoulder Bash"
        if self.free_var["Phase"] == 2:
            self.free_var["Missile Circus"] *= 2
            self.free_var["Current attack"] = Fun.get_random_element_from_list(["Laser Barrage", "Shoulder Bash"])
        animation = False

    if not self.free_var["Mech"].mech_animations["Torso"] and animation:
        pass


def rigel_raining_hell(self, entities, level):
    self.free_var["Pos history"] = {
        "1": {"Target": None, "History": []},
        "2": {"Target": None, "History": []},
        "3": {"Target": None, "History": []},
    }
    animation = True
    if start_up_lag_handler(self, 61):
        self.free_var["Current attack"] = "Shoulder Bash"

    elif self.free_var["Startup lag"] == 1 and self.free_var["Phase"] == 2:
        self.free_var["Invert Raining Hell"] = random.random() < 0.25

    elif self.free_var["Startup lag"] == 20 and not self.free_var["Invert Raining Hell"] or self.free_var["Startup lag"] == 60 and self.free_var["Invert Raining Hell"]:
        Fun.play_sound("Mech Cannon")
        for x in range(8):
            pos = Fun.move_with_vel_angle(self.pos, 128, x * 45)
            Bullets.spawn_bullet(
                    self, entities, Bullets.Artillery, pos, 0,
                    [0, 60, 48, 50, {"Secondary explosion":{"Duration": 20, "Strength": 120, "Radius":64}, "Colour": Fun.DARK_RED, "Slowdown rate": 0.05}])
    elif self.free_var["Startup lag"] == 40 and not self.free_var["Invert Raining Hell"] or self.free_var["Startup lag"] == 40 and self.free_var["Invert Raining Hell"]:
        Fun.play_sound("Mech Cannon")
        for x in range(16):
            pos = Fun.move_with_vel_angle(self.pos, 128 * 2, x * 22.5 + 11.5)
            Bullets.spawn_bullet(
                    self, entities, Bullets.Artillery, pos, 0,
                    [0, 60, 48, 50, {"Secondary explosion":{"Duration": 20, "Strength": 120, "Radius":64}, "Colour": Fun.DARK_RED, "Slowdown rate": 0.05}])
    elif self.free_var["Startup lag"] == 60 and not self.free_var["Invert Raining Hell"] or self.free_var["Startup lag"] == 20 and self.free_var["Invert Raining Hell"]:
        Fun.play_sound("Mech Cannon")
        for x in range(24):
            pos = Fun.move_with_vel_angle(self.pos, 128 * 3, x * 15)
            Bullets.spawn_bullet(
                    self, entities, Bullets.Artillery, pos, 0,
                [0, 60, 48, 50,
                 {"Secondary explosion": {"Duration": 20, "Strength": 120, "Radius": 64}, "Colour": Fun.DARK_RED,
                  "Slowdown rate": 0.05}])


# Curtis
def curtis_input(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    self.input = Fun.get_default_inputs()
    if target:
        aim_target, move_target, og_dist = entity_get_aim_move_target(self, target)
        dist = 420
        if self.no_shoot_state != 0:
            dist = 64
        entity_maintain_weapon_range(self, og_dist, move_target, dist, get_away=64)
        self.input["Skill 1"] = entity_get_enemy_count(self, entities, goal=0, dist=80, entity_type="bullets")

    # Stunned status manager
    Fun.stunned_manager(self)

    # Dash bullet thing
    if self.free_var["Stamina"] >= 50 and self.dash_cooldown <= 0:
        bullet_to_dodge = Fun.find_closest_bullet_types_in_circle(self, entities, 32, [
            Bullets.Bullet, Bullets.BulletSlowing, Bullets.Missile
        ])
        if bullet_to_dodge:
            dodge_pos = bullet_to_dodge.pos

            self.input["Right"] = self.pos[0] < dodge_pos[0]
            self.input["Left"] = self.pos[0] > dodge_pos[0]
            self.input["Down"] = self.pos[1] < dodge_pos[1]
            self.input["Up"] = self.pos[1] > dodge_pos[1]
            self.input["Dash"] = True
            self.free_var["Stamina"] -= 50
    return target, target_angle


def curtis_act(self, entities, level):
    if self.free_var["Stamina"] < 300:
        self.free_var["Stamina"] += 1

    # |Movement Input|----------------------------------------------------------------------------------------------
    speed = self.speed
    self.running = False
    self.walking = False

    max_vel = self.vel_max

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

    if not Fun.check_point_in_circle(max_vel, 0, 0, self.vel[0], self.vel[1]) and allow_correction:
        self.vel = Fun.move_with_vel_angle([0, 0], max_vel, Fun.angle_between(self.vel, [0, 0]))
    self.walking = allow_correction

    self.standing_still = False
    if self.vel == [0, 0]:
        self.standing_still = True

    # Dash mechanic
    if self.dash_cooldown <= 0 and self.input["Dash"]:
        # Handle dash here
        Fun.play_sound("Player dash", modified_volume=0.25)
        dash_angle = Fun.angle_between(dash_vel, [0, 0])
        self.dash_cooldown = self.dash_charge_time
        if self.status["Dash recovery up"] > 0:
            self.dash_cooldown //= 2
        self.vel = Fun.move_with_vel_angle(self.vel, self.dash_speed / self.friction, dash_angle)
        for x in range(4):
            angle = dash_angle - 15 - 3.25 * 2 + x * 7.5 * 2
            entities["particles"].append(
                Particles.RandomParticle2(
                    Fun.move_with_vel_angle([self.pos[0], self.pos[1]], -4, angle),
                    Fun.WHITE, 1.5 + random.uniform(0, 2), 24, angle))

        if self.status["No damage"] < self.dash_iframes:
            self.status["No damage"] += self.dash_iframes

        if self.health < self.max_health / 2:
            for x in range(3):
                Bullets.spawn_bullet(
                    self, entities, Bullets.HomingSword, Fun.random_point_in_circle(self.pos.copy(), 32), self.aim_angle,
                    [9, 60, 28, 20, {
                        "Swing Speed": 0,
                        "Swing Limit": [0, 0],
                        "Targeting range": 320,
                        "Targeting time": 20 * (x + 1), "Colour": Fun.BLUE
                    }])

    self.dash_cooldown -= 1
    Fun.aim_system(self, self.weapon)
    # |Status effects|----------------------------------------------------------------------------------------------
    # ha ha, Fun go brr
    Fun.status_manager(self, entities)
    if self.target or self.free_var["Startup lag"] > 0:
        if self.no_shoot_state == 0:
            # Attack logic
            {
                "Buckshot": curtis_buckshot,
                "Slug": curtis_slug,
                "Burst Ricochet": curtis_burst_ricochet,
                "Burst Long": curtis_burst_long,
                "Flower Volley": curtis_flower_volley,
                "Inverted Flower Volley": curtis_inverted_flower_volley,
            }[self.free_var["Current attack"]](self, entities, level)

        else:
            self.no_shoot_state -= 1
    else:
        self.free_var["Current attack"] = Fun.get_random_element_from_list(["Buckshot", "Slug", "Burst Ricochet", "Burst Long", "Flower Volley", "Inverted Flower Volley"])

    Skills.skills_manager(self, entities, level)
    # |Movement Output|---------------------------------------------------------------------------------------------
    # Make the player move
    Fun.movement_output(self, level)

    if self.draw_aim_line or self.weapon.laser_sight:
        entities["background particles"].append(Particles.LineParticle(
            Fun.move_with_vel_angle(self.pos, 20, self.aim_angle), Fun.BLUE, 1, self.weapon.range-20, self.aim_angle, 2, 0))


def curtis_buckshot(self, entities, level):
    if start_up_lag_handler(self, 30):
        angle = self.aim_angle
        pos = Fun.move_with_vel_angle(self.pos, 10, self.aim_angle)
        Fun.play_sound("Rifle 2")
        for b in range(32):
            Bullets.spawn_bullet(
                self, entities,
                Bullets.Bullet,
                Fun.move_with_vel_angle(pos, -64 + b * 4, angle + 90),
                angle + random.uniform(-2, 2),
                [4 + 3.5 * random.random(), 120, 4, 10, {'Colour': Fun.ORANGE}])
        self.free_var["Current attack"] = Fun.get_random_element_from_list(["Burst Ricochet", "Burst Long"])
        Fun.play_sound("Shotgun 2 Shooting")
    elif self.free_var["Startup lag"] == 1:
        Fun.play_sound("Shotgun 1 Pump")


def curtis_slug(self, entities, level):
    if start_up_lag_handler(self, 30):
        self.free_var["Current attack"] = Fun.get_random_element_from_list(["Burst Ricochet", "Burst Long"])

        angle = self.aim_angle
        pos = Fun.move_with_vel_angle(self.pos, 10, self.aim_angle)
        Bullets.spawn_bullet(
            self, entities,
            Bullets.Bullet,
            pos,
            angle,
            [8, 60, 9, 30, {'Colour': Fun.ORANGE}])
        for b in range(32):
            Bullets.spawn_bullet(
                self, entities,
                Bullets.Bullet,
                [pos[0], pos[1]],
                angle + random.uniform(-25, 25),
                [4 + 3.5 * random.random(), 60, 1 + 3 * random.random(), 10,
                 {'Colour': Fun.ORANGE, "Particle allowed": b % 3 == 0, "Burn chance": 0.25, "Burn duration": 30}])
        Fun.play_sound("Shotgun 2 Shooting")
    elif self.free_var["Startup lag"] == 1:
        Fun.play_sound("Shotgun 1 Pump")


def curtis_burst_ricochet(self, entities, level):
    if start_up_lag_handler(self, 61):
        self.free_var["Current attack"] = Fun.get_random_element_from_list(["Flower Volley", "Inverted Flower Volley"])

    elif self.free_var["Startup lag"] % 20 == 0:

        pos = Fun.move_with_vel_angle(self.pos, 10, self.aim_angle)
        Bullets.spawn_bullet(
            self, entities,
            Bullets.Bullet,
            pos,
            self.aim_angle + random.uniform(-4, 4),
            [11.4, 200, 5, 35, {"Piercing": True, "Smoke": False}])
        entities["bullets"][-1].wall_physics = Bullets.base_grenade_wall_hit
        Fun.play_sound("Rifle 1 Shooting")


def curtis_burst_long(self, entities, level):
    if start_up_lag_handler(self, 141):
        self.free_var["Current attack"] = Fun.get_random_element_from_list(["Flower Volley", "Inverted Flower Volley"])

    elif self.free_var["Startup lag"] % 10 == 0:

        pos = Fun.move_with_vel_angle(self.pos, 10, self.aim_angle)
        Bullets.spawn_bullet(
            self, entities,
            Bullets.Bullet,
            pos,
            self.aim_angle + random.uniform(-14, 14),
            [11.4, 200, 5, 35, {"Piercing": True, "Smoke": False}])
        Fun.play_sound("Rifle 1 Shooting")


def curtis_flower_volley(self, entities, level):
    # War == Left
    # Peace == Right
    if start_up_lag_handler(self, 20 + 70 + 1):
        self.free_var["Current attack"] = Fun.get_random_element_from_list(["Buckshot", "Slug"])
    elif self.free_var["Startup lag"] > 20:
        temp = self.free_var["Startup lag"] - 20
        if temp % 5 == 0:
            self.weapon.free_var["Peace angle"] += 10
            self.weapon.free_var["War angle"] -= 10

            bullet_info = [5, 200, 4, 20, {"Piercing": True, "Smoke": False}]

            pos = Fun.move_with_vel_angle(self.pos, 7, self.weapon.free_var["War angle"])
            Bullets.spawn_bullet(
                self, entities, Bullets.Bullet, pos, self.weapon.free_var["War angle"], bullet_info)
            pos = Fun.move_with_vel_angle(self.pos, 7, self.weapon.free_var["Peace angle"])
            Bullets.spawn_bullet(
                self, entities, Bullets.Bullet, pos, self.weapon.free_var["Peace angle"], bullet_info)

            Fun.play_sound("Rifle", "SFX")
    else:
        self.weapon.free_var["War angle"] = self.aim_angle + 30
        self.weapon.free_var["Peace angle"] = self.aim_angle - 30


def curtis_inverted_flower_volley(self, entities, bullets):
    if start_up_lag_handler(self, 20 + 70 + 1):
        self.free_var["Current attack"] = Fun.get_random_element_from_list(["Buckshot", "Slug"])
    elif self.free_var["Startup lag"] > 20:
        temp = self.free_var["Startup lag"] - 20
        if temp % 10 == 0:
            self.weapon.free_var["Peace angle"] -= 20
            self.weapon.free_var["War angle"] += 20

            bullet_info = [5, 200, 4, 20, {"Piercing": True, "Smoke": False}]

            pos = Fun.move_with_vel_angle(self.pos, 7, self.weapon.free_var["War angle"])
            Bullets.spawn_bullet(
                self, entities, Bullets.Bullet, pos, self.weapon.free_var["War angle"], bullet_info)
            entities["bullets"][-1].wall_physics = Bullets.base_grenade_wall_hit

            pos = Fun.move_with_vel_angle(self.pos, 7, self.weapon.free_var["Peace angle"])
            Bullets.spawn_bullet(
                self, entities, Bullets.Bullet, pos, self.weapon.free_var["Peace angle"], bullet_info)
            entities["bullets"][-1].wall_physics = Bullets.base_grenade_wall_hit

            Fun.play_sound("Rifle", "SFX")
    else:
        self.weapon.free_var["War angle"] = self.aim_angle + 30
        self.weapon.free_var["Peace angle"] = self.aim_angle - 30


ACT_FREELY_DICT = {
         "Lord": ally_sub_input_roam,
         "Emperor": ally_sub_input_focus_objective,
         "Wizard": ally_sub_input_wizard,
         "Sovereign": ally_sub_input_sniper,
         "Duke": ally_sub_input_duke,
         "Jester": ally_sub_input_jester,
         "Condor": ally_sub_input_condor,

         "Curtis": ally_sub_input_focus_objective,
         "Doppelgänger": ally_sub_input_focus_objective,
         "Lawrence": ally_sub_input_lawrence,
         "Mark": ally_sub_input_sniper,
         "Vivianne": ally_sub_input_wizard
     }
# |Repertories|---------------------------------------------------------------------------------------------------------
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
         }, team="Enemies", pos=[0, 0], start_angle=0)
# Entity stats
H_LO, H_LM, H_MO, H_MH, H_HO = 60, 90, 130, 170, 200        # Max Health
A_LO, A_LM, A_MO, A_MH, A_HO = 40, 60, 90, 120, 140         # Max Armour
V_LO, V_LM, V_MO, V_MH, V_HO = 2, 3, 4, 5, 5.75             # Max Speed
R_LO, R_LM, R_MO, R_MH, R_HO = 256, 384, 512, 640, 768      # Vision range
D_LO, D_LM, D_MO, D_MH, D_HO = 15, 30, 45, 60, 75           # Targeting angle
S_LO, S_LM, S_MO, S_MH, S_HO = 1, 0.85, 0.65, 0.55, 0.45    # Stealth mod
C_LO, C_LM, C_MO, C_MH, C_HO = 1, 2, 4, 6, 10               # Stealth Counter
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
        "func input": test_ally_input, "func act": player_act, "func draw": player_draw, "on death": lord_on_death,
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
        "func input": test_ally_input, "func act": player_act, "func draw": player_draw, "on death": "none",
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
        "func input": test_ally_input, "func act": player_act, "func draw": player_draw, "on death": "none",
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
        "func input": test_ally_input, "func act": player_act, "func draw": player_draw, "on death": "none",
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
        "func input": test_ally_input, "func act": player_act, "func draw": player_draw, "on death": "none",
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
        "func input": jester_input, "func act": player_act, "func draw": player_draw, "on death": "none",
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
        "func input": test_ally_input, "func act": player_act, "func draw": player_draw, "on death": "condor_on_death",
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
        "func input": test_ally_input,
        "func act": player_act,
        "func draw": player_draw,
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
        "func input": test_ally_input,
        "func act": player_act,
        "func draw": player_draw,
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
        "func input": test_ally_input,
        "func act": player_act,
        "func draw": player_draw,
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
        "func input": test_ally_input,
        "func act": vivianne_act,
        "func draw": player_draw,
        "on death": "none",
        "targeting range": 750,
        "targeting angle": 33,
        "wall hack": False,
        "free var": {"Ally waypoint": [0, 0], "Summon cooldown time": 360, "Summon cooldown": 0, "Summon limit": 1,
                     "Summon pool": [], "Active summons": []}
    },

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
        "func input": birna_input,
        "func act": vivianne_summons_act,
        "func draw": birna_draw,
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
        "func input": elektra_input,
        "func act": vivianne_summons_act,
        "func draw": elektra_draw,
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
        "func input": agatha_input,
        "func act": vivianne_summons_act,
        "func draw": player_draw,
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
        "func input": azura_input,
        "func act": vivianne_summons_act,
        "func draw": player_draw,
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
        "func input": m_input,
        "func act": vivianne_summons_act,
        "func draw": player_draw,
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
        "func input": sierra_input,
        "func act": vivianne_summons_act,
        "func draw": player_draw,
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
        "func input": makoto_input,
        "func act": vivianne_summons_act,
        "func draw": player_draw,
        "on death": "vivianne_summons_on_death",
        "targeting range": 750,
        "targeting angle": 33,
        "wall hack": False,
        "free var": {"Life Limit": VIVIANNE_SUMMON_LIVE_TIME, "NO DEATH MESSAGE": True}
    }
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
    "Drone":
        {"name": "Drone",
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
    #                   MHlt	MArm	Resits	Spd 	VisRg	SltMod	SltCntr	Size
    # |Triangle|--------------------------------------------------------------------------------------------------------
    "Sculptor":
        {"name": "Sculptor",
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
    "Skirmisher":
        {"name": "Skirmisher",
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
    "BoomStick":
        {"name": "BoomStick",
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
    "Smoker":
        {"name": "Smoker",
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
    "Snare":
        {"name": "Snare",
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
    "Crusher":
        {"name": "Crusher",
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
    "Assassin":
        {"name": "Assassin",
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

    #                   MHlt	MArm	Resits	Spd 	VisRg	SltMod	SltCntr	Size
    # |Square|----------------------------------------------------------------------------------------------------------
    # Infantry	        M/H	    M/H	    M	    L/M	    M	    L	    M	    M	    Basic and tough.
    "Infantry":
        {"name": "Infantry",
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
    "Flamer":
        {"name": "Flamer",
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
    "Spotter":
        {"name": "Spotter",
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
    "Artilleryman":
        {"name": "Artilleryman",
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
    "Grenadier":
        {"name": "Grenadier",
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
    "Bulwark":
        {"name": "Bulwark",
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
    "Commanding Officer":
        {"name": "Commanding Officer",
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
    # Fire Support Mech
    "Super Bulwark":
        {"name": "Super Bulwark",
         "faction": "FAC-3",
         "type": "Elite",
         "targeting range": R_MO, "targeting angle": D_HO, "stealth mod": S_LO, "stealth counter": C_MO,
         "wall hack": False, "health": H_HO, "armour": round(A_HO * 1.5), "damage resistances": F3_RESIT_H,
         "thickness": T_HO,
         "vel max": V_LO * 0.8, "speed": V_LO * 0.8, "friction": V_LO * 0.8,
         "weapon": "Bulwark Minigun",

         "func input": "enemy_input_faction_3_bulwark",
         "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_bulwark",
         "sprites": "Sprites/Enemies/Bulwark.png", "on death": "none",
         "free var": {"IS BOSS": True}
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
    # Curtis
    "Curtis": {
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
    "Lord": {
        "name": "Lord", "faction": "THR-1",
        "health": H_MH, "armour": A_MO, "damage resistances": LO_RESIT,
        "sprites": "Sprites/Player/THR-1/Lord.png",

        "thickness": T_MH, "vel max": V_MO, "speed": 2.2, "friction": 1.5,
        "dash": {"speed": DS_HO, "i-frames": 12, "charge": 35},
        # Weapons
        "weapon": "Saloum Mk-2", "skills": ["Gauntlet Punch", "Beast Mode"],
        # AI
        "func input": lord_boss_input, "func act": player_act, "func draw": enemy_draw_basic, "on death": thr_1_on_death,
        "targeting range": R_MH, "targeting angle": D_LM, "wall hack": False,
        "driving": DRIVE_MO,
        "free var": {"Ally waypoint": [0, 0], "IS BOSS": True}
    },
    # Emperor	    M       L/M     M       M/H     H       M       M/H     M       M       M       H       H       Jack of all trades
    "Emperor": {
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
        "func input": emperor_boss_input, "func act": player_act, "func draw": emperor_boss_draw, "on death": thr_1_on_death,
        "targeting range": R_HO, "targeting angle": D_MO, "stealth mod": S_MO, "stealth counter": C_MH,
        "wall hack": True,
        "driving": DRIVE_MO,
        "free var": {"Ally waypoint": [0, 0], "Startup lag": 0, "Startup time": 60, "Kicked": 0, "Startup lag kick": 0, "kick cooldown": 120}
    },
    # Wizard        L/M     M       M/H     M       M       L/M     M       M       H       M       H       M       Area denial
    "Wizard": {
        "name": "Wizard", "faction": "THR-1",
        "health": H_LM, "armour": A_MO, "damage resistances": WI_RESIT, "sprites": "Sprites/Player/THR-1/Wizard.png",
        "thickness": T_MO,
        "vel max": V_MO, "speed": 2.2, "friction": 1.5,
        "dash": {"speed": DS_MO, "i-frames": 12, "charge": 35},
        # Weapons
        "weapon": "Jeanne's Family Shotgun", "skills": ["Building", "All Guns Blazing"],
        # AI
        "func input": wizard_boss_input, "func act": player_act, "func draw": enemy_draw_basic, "on death": thr_1_on_death,
        "targeting range": R_MO, "targeting angle": D_MH, "stealth mod": S_LM, "stealth counter": C_MO,
        "wall hack": True,
        "driving": DRIVE_HO,
        "free var": {"Ally waypoint": [0, 0]}
    },
    # Sovreign       L/M     L/M     L       M/H     H++     M/H     H       L       L       L/M     L       M       Sniper recon
    "Sovereign": {
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
        "func input": sovereign_boss_input, "func act": player_act, "func draw": enemy_draw_basic, "on death": thr_1_on_death,
        "targeting range": R_HO * 1.5, "targeting angle": D_LM, "stealth mod": S_MH, "stealth counter": C_HO,
        "wall hack": True,
        "driving": DRIVE_LO,
        "free var": {"Ally waypoint": ENEMY_NO_OWNER, "Detect Targets Duration": 3 * 60, "Exposed blue ball timer": 0, "Startup lag": 0, "Startup time": 60}
    },
    # Duke	        M       L/M     M       H       M       H       M       L/M     L/M     H       H       H	    Plays with agro
    "Duke": {
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
        "func input": duke_boss_input, "func act": player_act, "func draw": enemy_draw_basic, "on death": thr_1_on_death,
        "targeting range": R_MO, "targeting angle": D_HO, "stealth mod": S_HO, "stealth counter": C_HO,
        "driving": DRIVE_LM,
        "wall hack": True,
        "free var": {"Ally waypoint": ENEMY_NO_OWNER}
    },
    # Jester	    L--     H++     H       L       L/M     L/M     H++     M/H     L/M     L--     H++     L       Primary support. Helps them not dying
    "Jester": {
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
        "func input": jester_boss_input, "func act": player_act, "func draw": enemy_draw_basic, "on death": thr_1_on_death,
        "targeting range": R_LM, "targeting angle": D_MH, "stealth mod": S_LM, "stealth counter": C_HO * 1.2,
        "wall hack": True,
        "driving": DRIVE_LM,
        "free var": {"Ally waypoint": [0, 0], "Startup lag": 0}
    },
    # Condor        H       H       M/H     L/M     M       L       L/M     M/H     M/H     M       L       L       Tank and cause debuffs
    "Condor": {
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
        "func input": condor_boss_input, "func act": player_act, "func draw": enemy_draw_basic, "on death": condor_boss_on_death,
        "targeting range": R_MO, "targeting angle": D_MO, "stealth mod": S_LO, "stealth counter": C_LM,
        "driving": DRIVE_MH,
        "wall hack": True,
        "free var": {"Ally waypoint": ENEMY_NO_OWNER}
    },
    "VIP":
        {"name": "Nest Trooper",
         "faction": "FAC-1",
         "type": "VIP",
         "targeting range": 450,
         "targeting angle": 25,
         "wall hack": False,
         "health": 200,
         "armour": 100,
         "damage resistances": NO_RESIT_L,
         "thickness": 16,
         "vel max": 3.25,
         "speed": 1.5,
         "friction": 1.5,
         "weapon": "Nest Heavy Machine Gun",

         "func input": "enemy_input_nest_trooper",
         "func act": "enemy_act_type_1",
         "func draw": "enemy_draw_basic",
         "sprites": "Sprites/Enemies/Nest Commander.png",
         "on death": "none",
         "free var": {
             "Is VIP": True
         }
         },
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
# how_many_attacks_to_kill_everyone(250, "Melee")
# "Physical" "Fire" "Explosion" "Energy" "Melee"

RIGEL_SEGMENT = Fun.get_image('Sprites/Segment.png')
RIGEL_SEGMENT_WIDTH = RIGEL_SEGMENT.get_width()
RIGEL_SEGMENT_HEIGHT = RIGEL_SEGMENT.get_height()
RIGEL_SEGMENT_ORIGIN = [RIGEL_SEGMENT_WIDTH * 0.5, RIGEL_SEGMENT_HEIGHT * 0]


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
    bosses_to_draw[-1].free_var["Move angle"] = -50
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
            b.draw(surface_to_draw, [630//4, 450//4])
        # boss_to_draw.pos[0] += 1
        # boss_to_draw.pos[1] += 1
        Fun.scale_render(WIN, surface_to_draw, CLOCK)
        pg.display.update()
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
        pg.display.update()
        CLOCK.tick(60)
        if not screenshot_taken:
            Fun.screenshot(WIN)
            screenshot_taken = True