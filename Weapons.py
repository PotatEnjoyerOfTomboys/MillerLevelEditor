import math

import pygame as pg
import random
import sys


import Bullets
import Skills
import Items
import Particles
import Fun
from Fun import none
# Pan Piano


class BasicWeapon:
    __slots__=['accuracy', 'agro_gain', 'alt_fire', 'ammo', 'ammo_cost', 'ammo_pool', 'ammo_sprite', 'bullet_info', 'bullet_type', 'bullets_per_shot', 'crit_multiplier', 'crit_rate', 'fire_rate', 'free_var', 'full_auto', 'gunshot_sound', 'handle', 'jam_duration', 'jam_rate', 'jamming_sound', 'laser_sight', 'max_ammo', 'max_ammo_pool', 'mods', 'name', 'passive', 'range', 'recoil', 'reload_sound', 'reload_style', 'reload_time', 'spread', 'sprite', 'volume', 'weight']
    def __init__(self, weapon):
        self.name = weapon["name"]
        #
        self.sprite = weapon["sprite"]
        if type(self.sprite) == str:
            self.sprite = Fun.get_image(self.sprite)

        self.ammo_sprite = AMMO_BAR_SPRITES["Misc"]
        if "ammo sprite" in weapon:
            self.ammo_sprite = AMMO_BAR_SPRITES[weapon["ammo sprite"]]
        # "weakref"
        # Sounds system
        self.gunshot_sound = weapon["gunshot sound"]
        self.reload_sound = weapon["reloading sound"]
        self.jamming_sound = weapon["jamming sound"]
        self.volume = weapon["sound level"]
        # Bullet
        self.bullet_type = weapon["bullet type"]  # Type of projectile shot
        if type(self.bullet_type) == str:
            try:
                self.bullet_type = Bullets.string_to_bullet_class[self.bullet_type] # Work toward removing that
            except KeyError:
                self.bullet_type = getattr(Bullets, self.bullet_type)
        self.bullets_per_shot = weapon["bullets per shot"]  # Bullets shot
        self.bullet_info = [weapon["bullet info"][0],  # Speed
                            weapon["bullet info"][1],  # Duration
                            weapon["bullet info"][2],  # Radius
                            weapon["bullet info"][3],  # Damage
                            weapon["bullet info"][4].copy()]  # Extra info
        # Weapon
        self.accuracy = weapon["accuracy"]  # Change the angle of the bullet shot
        self.spread = weapon["spread"]  # Change the angle of the bullet shot, again
        self.handle = weapon["handle"]  # Speed at which the weapon goes to the "true" angle
        self.recoil = weapon["recoil"]  # How much the aim angle can change after each shot
        self.fire_rate = weapon["fire rate"]  # Time between each bullet shot
        self.full_auto = weapon["full auto"]
        self.reload_time = weapon["reload time"]  # Time to shoot after reloading
        self.reload_style = "Normal"
        if "Reload style" in weapon:
            self.reload_style = weapon["Reload style"]
        # Ammo
        self.max_ammo = weapon["max ammo"]  # magazine capacity capacity
        self.ammo = self.max_ammo  # Current ammo
        self.ammo_pool = weapon["ammo pool"]  #
        self.max_ammo_pool = self.ammo_pool  # Used for resupply
        self.ammo_cost = weapon["ammo cost"]  #
        # Random shit
        self.crit_rate = weapon["crit rate"]
        self.crit_multiplier = weapon["crit multiplier"]
        self.jam_rate = weapon["jam rate"]
        self.jam_duration = weapon["jam duration"]
        # Special effects
        self.laser_sight = weapon["laser sight"]

        # Need a way to get those from a string
        self.alt_fire = weapon["alt fire"]
        if type(self.alt_fire) == str:
            try:
                self.alt_fire = getattr(Skills, self.alt_fire)
            except AttributeError:
                self.alt_fire = getattr(sys.modules[__name__], self.alt_fire)
        self.passive = weapon["passive"]
        if type(self.passive) == str:
            try:
                self.passive = getattr(Skills, self.passive)
            except AttributeError:
                self.passive = getattr(sys.modules[__name__], self.passive)


        self.agro_gain = 1
        if "agro" in weapon:
            self.agro_gain = weapon["agro"]
        # Weight system
        self.weight = 1
        # Only add mods if the weapon type allows it
        self.mods = []
        self.range = self.bullet_info[0] * self.bullet_info[1] + self.bullet_info[2]
        if "range" in weapon:
            self.range = weapon["range"]
        # Took me a while to choose to add them here
        self.free_var = {}
        if "free var" in weapon:
            self.free_var = weapon["free var"]

    def reload(self):
        if self.ammo == self.max_ammo:
            return 0, False

        reload_time = self.reload_time
        if self.reload_style == "Normal":
            # If there's more ammo in the ammo pool then the max magazine capacity
            #   Remove the difference between current ammo and the magazine capacity,
            #   then set the ammo to the max magazine capacity
            ammo_reloaded = self.max_ammo - self.ammo
            if self.ammo_pool >= ammo_reloaded:
                self.ammo_pool -= ammo_reloaded
                self.ammo = self.max_ammo
            else:
                self.ammo = self.ammo_pool
                self.ammo_pool = 0
            # Play the reloading sound
        elif self.reload_style == "Partial":
            modifier = 1
            if self.ammo_pool >= self.max_ammo:
                modifier = self.max_ammo - self.ammo
                self.ammo_pool -= self.max_ammo - self.ammo
                self.ammo = self.max_ammo
            else:
                modifier = self.ammo_pool
                self.ammo = self.ammo_pool
                self.ammo_pool = 0
            reload_time *= modifier
        elif self.reload_style == "One at a time":
            if 0 < self.ammo_pool:
                self.ammo += 1
                self.ammo_pool -= 1
        Fun.play_sound(self.reload_sound, "SFX")
        return reload_time, True

    def fill_up(self):
        self.ammo = self.max_ammo
        self.ammo_pool = self.max_ammo_pool


LAWRENCE_FLINTLOCK = Fun.get_image("Sprites/Weapon/Son's Pistol.png")
LAWRENCE_CUTLASS = Fun.get_image("Sprites/Weapon/Son's Cutlass.png")
LAWRENCE_BLUNDERBUSS = Fun.get_image("Sprites/Weapon/Captain's Blunderbuss.png")
LAWRENCE_AXE = Fun.get_image("Sprites/Weapon/Boarding Axe.png")
ZANDER_PISTOL = Fun.get_image("Sprites/Weapon/THR-1/Gun Fu.png")
ZANDER_KNIFE = Fun.get_image("Sprites/Weapon/THR-1/Gun Fu - Knife.png")
# |Weapon functions|----------------------------------------------------------------------------------------------------
def melee_system(self, entities, level, basic_attacks=(Fun.none, Fun.none), charged_attack=Fun.none,
                 basic_threshold=10, charged_threshold=50):
    # You use that one in a melee weapon's passive effect to have multiple attack
    weapon_free_var = f"{self.weapon.name}"
    threshold_mod = 1
    if self.status["Fuller auto"] > 0:
        threshold_mod = 2
    # Make sure that the free var exist
    if weapon_free_var not in self.free_var:
        self.free_var.update({weapon_free_var: {"Press time": 0, "Combo stage": 0, "No press time": 0,
                                                "basic threshold": basic_threshold,
                                                "charged threshold": charged_threshold}})

    real_basic_threshold = basic_threshold
    if type(real_basic_threshold) == list:
        real_basic_threshold = real_basic_threshold[self.free_var[weapon_free_var]["Combo stage"]]

    # Keep track of how long the key is pressed
    key_released = False
    if self.input["Shoot"]:
        self.free_var[weapon_free_var]["No press time"] = 0
        if self.free_var[weapon_free_var]["Press time"] < charged_threshold:
            self.free_var[weapon_free_var]["Press time"] += 1

        # Show how charged the hit is
        colour = Fun.DARK
        if self.free_var[weapon_free_var]["Press time"] == charged_threshold // threshold_mod:
            colour = Fun.ORANGE
        elif self.free_var[weapon_free_var]["Press time"] > real_basic_threshold // threshold_mod:
            colour = Fun.AMBER_LIGHT

        entities["particles"].append(Particles.LineParticle([self.pos[0] - self.thiccness, self.pos[1] + 15], colour, 1,
                                                      self.free_var[weapon_free_var]["Press time"] / 2, 90))
    elif self.free_var[weapon_free_var]["Press time"] > 0:
        key_released = True
    else:
        self.free_var[weapon_free_var]["No press time"] += 1
        # Reset combo if you don't press enough
        if self.free_var[weapon_free_var]["No press time"] > 90:
            self.free_var[weapon_free_var]["Combo stage"] = 0

    # Perform attacks if the key is released with enough charge
    if key_released:

        # Handle charge attacks
        if self.free_var[weapon_free_var]["Press time"] >= charged_threshold // threshold_mod:
            charged_attack(self, entities, level)
            entities["sounds"].append(Fun.Sound(
                Fun.move_with_vel_angle(self.pos, 20, self.aim_angle), 60, 175, source=self.team, strength=2))
            self.agro += self.weapon.agro_gain
            self.free_var[weapon_free_var]["Combo stage"] = 0

        # Handle the combo part
        elif self.free_var[weapon_free_var]["Press time"] >= real_basic_threshold // threshold_mod:
            basic_attacks[self.free_var[weapon_free_var]["Combo stage"]](self, entities, level)
            entities["sounds"].append(Fun.Sound(
                Fun.move_with_vel_angle(self.pos, 20, self.aim_angle), 60, 125, source=self.team, strength=1))
            self.agro += self.weapon.agro_gain
            # Cycle through basic attacks
            self.free_var[weapon_free_var]["Combo stage"] += 1
            if self.free_var[weapon_free_var]["Combo stage"] > len(basic_attacks) - 1:
                self.free_var[weapon_free_var]["Combo stage"] = 0

        self.free_var[weapon_free_var]["Press time"] = 0
    return key_released, self.free_var[weapon_free_var]


def variable_handling_rate(self, entities, level, rate=16, min_handle=0.0):
    # Yes, I did reuse the hunk of steel passive
    self.weapon.handle = pg.math.clamp(
        Fun.distance_between(Fun.move_with_vel_angle(self.pos, 45, self.aim_angle),
                             Fun.move_with_vel_angle(self.pos, 45, self.angle)
                             ) / rate, min_handle, 90)


def rev_up(self, entities, level, rev_up_rate=2, rev_down_rate=1, rev_up_target=2):
    # Does the effects
    # if self.no_shoot_state == 0:
    #     self.weapon.free_var["Allowed to go down"] = True
    if self.weapon.ammo != 0 and self.shot_allowed and self.no_shoot_state == 0:
        if self.input["Shoot"]:

            # Make fire rate go down
            if self.weapon.fire_rate > rev_up_target:
                self.weapon.fire_rate -= rev_up_rate

                # Prevent it from going under the target
                if self.weapon.fire_rate < rev_up_target:
                    self.weapon.fire_rate = rev_up_target

        # if self.weapon.free_var["Allowed to go down"]:
        else:
            # Make fire rate go up when not shooting
            if self.weapon.fire_rate < self.weapon.free_var["Normal fire rate"]:
                self.weapon.fire_rate += rev_down_rate

                # Prevent it from going over the target
                if self.weapon.fire_rate > self.weapon.free_var["Normal fire rate"]:
                    self.weapon.fire_rate = self.weapon.free_var["Normal fire rate"]


# |Lord|----------------------------------------------------------------------------------------------------------------
# Saloum Mk-2
def missile_launcher_passive(self, entities, level):
    # Could add a sound effect for when it has a lock but is not shot
    if self.no_shoot_state == 0 and self.weapon.ammo > 0:
        center = Fun.find_closest_in_cone(self, entities, self.weapon.range, "Enemies", self.angle, 25)

        for e in entities["entities"]:
            if e.team == self.team:
                continue
            if e.status["Stealth"] > 0:
                continue
            if Fun.distance_between(e.pos, self.pos) <= self.weapon.range:
                if not Fun.wall_between(e.pos, self.pos, level):
                    entities["UI particles"].append(Particles.MissileLockOn(
                        e.pos, 1, locked=e.pos == center, colour=[Fun.DARK_GREEN, Fun.GREEN][int(e.pos == center)])
                    )


def big_iron_alt(self, entities, bullets):
    self.draw_aim_line = True
    if self.status["Perfect Aim"] in (1, 0):
        self.status["Perfect Aim"] = 2
    if self.status["Forced Slide"] == 0:
        if self.status["High friction"] in (1, 0):
            self.status["High friction"] = 2
    if self.dash_cooldown == 0:
        self.dash_cooldown = 1
    #


# |Emperor|-------------------------------------------------------------------------------------------------------------
def gunblade(self, entities, level):
    if "Side gun" in self.free_var:
        if self.free_var["Side gun"] % 5 == 0 or self.status["Fuller auto"] > 0 and self.free_var["Side gun"] % 3 == 0:
            # Send a bullet
            Fun.play_sound("Rifle 1 Shooting")
            angle = self.aim_angle + random.uniform(-5, 5)
            base_pos = Fun.move_with_vel_angle(self.pos, 20, angle)
            Bullets.spawn_bullet(
                self, entities, Bullets.Bullet, base_pos, angle,
                [6, 50, 2.5, 18, {"Piercing": False, "Smoke": False}])
        self.free_var["Side gun"] -= 1
        if self.free_var["Side gun"] == 0:
            self.free_var.pop("Side gun")
        return

    if self.input["Alt fire"] and self.no_shoot_state == 0 and self.weapon.ammo > 0:
        self.draw_angle = 0
        #
        pos = Fun.move_with_vel_angle(self.pos, 20, self.angle)

        angle = self.angle
        entities["particles"].append(Particles.LineParticle(pos, Fun.GREEN, 1, 7 * 30, angle))


        if self.status["Perfect Aim"] in (1, 0):
            self.status["Perfect Aim"] = 2
        if self.input["Shoot"]:
            # [6, 80, 5, 30, {"Piercing": True, "Smoke": False}]

            Bullets.spawn_bullet(
                self, entities,
                Bullets.Bullet,
                pos,
                self.angle,
                [7, 30, 5, 30, {"Piercing": True, "Smoke": False}])
            Fun.play_sound("Rifle 2 Shooting")
            self.no_shoot_state = 90
            self.weapon.ammo -= 1
            self.shot_allowed = False
            entities["sounds"].append(Fun.Sound(
                Fun.move_with_vel_angle(self.pos, 20, self.aim_angle),
                Fun.sounds_dict[self.weapon.gunshot_sound]["Sound"].get_length() * 60,
                350,
                source=self.team, strength=2))
            self.weapon_draw_dist = -10
            self.draw_angle = random.randint(1, 8) * -2
        return

    if self.no_shoot_state > 0:
        return
    # Now that one is used with a reversed grip, which is kind of stupid
    key_released, weapon_info = melee_system(self, entities, level,
                                             basic_attacks=[gunblade_combo_1, gunblade_combo_2, gunblade_combo_3],
                                             charged_attack=gunblade_charged,
                                             basic_threshold=[4, 4, 18], charged_threshold=80)
    if weapon_info["Press time"] > 0 and not key_released:
        if weapon_info["Combo stage"] == 0:
            self.weapon_draw_dist = weapon_info["Press time"] * -0.25
            self.draw_angle = 90 + weapon_info["Press time"]

    if self.draw_angle < 90:
        self.draw_angle += 5
    if self.weapon_draw_dist > 0:
        self.weapon_draw_dist -= 2
    if self.weapon_draw_dist < 0:
        self.weapon_draw_dist += 2
    if self.draw_rotated_dist > 0:
        self.draw_rotated_dist -= 2


def gunblade_combo_1(self, entities, level):
    self.draw_angle = -20
    # self.aim_angle = self.angle - 50
    for x in range(7):
        angle = self.aim_angle + x * 10 - 15
        Bullets.spawn_bullet(self, entities, Bullets.Melee, Fun.move_with_vel_angle(self.pos, 25, angle),
                             angle, [8, 12, 16, 60, {"Always Counter": True}])
    # Bullets.spawn_bullet(self, entities, Bullets.RazorWind, Fun.move_with_vel_angle(self.pos, 20, self.aim_angle),
    #                      self.aim_angle, [4, 15, 30, 20, {"Colour": Fun.WHITE, "Angle modifier": 100,
    #                                                              "Segment amount": 1}])
    Fun.play_sound("Hitting 1", "SFX")


def gunblade_combo_2(self, entities, level):
    self.draw_angle = -40
    # self.aim_angle = self.angle + 50
    for x in range(7):
        angle = self.aim_angle - x * 10 + 15
        Bullets.spawn_bullet(self, entities, Bullets.Melee, Fun.move_with_vel_angle(self.pos, 25, angle),
                             angle, [8, 12, 16, 60, {"Always Counter": True}])
    Fun.play_sound("Hitting 1", "SFX")


def gunblade_combo_3(self, entities, level):
    # Fun.play_sound("Rifle", "SFX")
    # for x in range(20):
    #     angle = self.aim_angle + random.uniform(-14, 14)
    #     base_pos = Fun.move_with_vel_angle(self.pos, 20, angle)
    #     Bullets.spawn_bullet(self, entities, Bullets.Bullet, [base_pos[0], base_pos[1]],
    #         angle, [2 + random.random(), 50, 2.5, 5, {"Piercing": True, "Smoke": False}])
    #     if x % 3 == 0:
    #         entities["particles"].append(Fun.Smoke(
    #             Fun.move_with_vel_angle(base_pos, random.randint(5, 100), random.uniform(-15, 15) + self.aim_angle)))
    angle = self.aim_angle
    Bullets.spawn_bullet(self, entities, Bullets.RazorWind, Fun.move_with_vel_angle(self.pos, 25, angle),
                         angle,  [9, 30, 70, 80, {"Colour": Fun.WHITE, "Angle modifier": 130,
                                                                 "Segment amount": 1}])
    self.weapon_draw_dist = 30
    Fun.play_sound("Skill 2", "SFX")

    self.draw_angle = 0


def gunblade_charged(self, entities, level):
    self.free_var.update({"Side gun": 60})
    self.draw_rotated_dist = 12
    self.draw_angle = 90
    self.weapon_draw_dist = 8


def stun_baton(self, entities, level):
    if self.no_shoot_state > 0:
        return
    # Now that one is used with a reversed grip, which is kind of stupid
    key_released, weapon_info = melee_system(self, entities, level,
                                             basic_attacks=[stun_baton_combo_1, stun_baton_combo_2, stun_baton_combo_3],
                                             charged_attack=stun_baton_charged,
                                             basic_threshold=[4, 4, 18], charged_threshold=50)
    if weapon_info["Press time"] > 0 and not key_released:
        if weapon_info["Combo stage"] in [0, 1]:
            self.draw_angle = weapon_info["Press time"] * [1, -1][weapon_info["Combo stage"]] * 2
        if weapon_info["Combo stage"] == 2:
            self.weapon_draw_dist = -weapon_info["Press time"] * 0.5

    if self.draw_angle < 0:
        self.draw_angle += 3
    if self.draw_angle > 0:
        self.draw_angle -= 3
    if self.weapon_draw_dist > 0:
        self.weapon_draw_dist -= 2


def stun_baton_combo_1(self, entities, level):
    self.draw_angle = -120
    for x in range(24):
        angle = self.aim_angle + x * 3 - 36
        Bullets.spawn_bullet(self, entities, Bullets.Electric, Fun.move_with_vel_angle(self.pos, 25, angle),
                             angle, [0, 60, round(7 + (6 * x / 24)), 20, {"Angle modifier": 30, # "Split rate": 2,
                                                    "Target": "enemies", "On hit": [Bullets.on_hit_stun_baton]}])
    Fun.play_sound("Hitting 1", "SFX")


def stun_baton_combo_2(self, entities, level):
    self.draw_angle = 120
    for x in range(24):
        angle = self.aim_angle - x * 3 + 36
        Bullets.spawn_bullet(self, entities, Bullets.Electric, Fun.move_with_vel_angle(self.pos, 25, angle),
                             angle, [0, 60, round(7 + (6 * x / 24)), 20, {"Angle modifier": 30, # "Split rate": 2,
                                                    "Target": "enemies", "On hit": [Bullets.on_hit_stun_baton]}])
    Fun.play_sound("Hitting 1", "SFX")


def stun_baton_combo_3(self, entities, level):
    self.weapon_draw_dist = 30
    for x in range(12):
        angle = self.aim_angle + x * 3 - 36
        Bullets.spawn_bullet(self, entities, Bullets.SplittingElectric, Fun.move_with_vel_angle(self.pos, 25, angle),
                             angle, [0, 60, round(8 + (6 * x / 12)), 20, {"Angle modifier": 30, "Split rate": 2,
                                                    "Target": "enemies", "On hit": [Bullets.on_hit_stun_baton]}])
    Fun.play_sound("Electricity 1", "SFX")
    self.draw_angle = 0


def stun_baton_charged(self, entities, level):
    self.draw_angle = 120 * [1, -1, 1][self.free_var[f"{self.weapon.name}"]["Combo stage"]]
    for x in range(24):
        angle = self.aim_angle - x * 8 + 48 * 2
        Bullets.spawn_bullet(self, entities, Bullets.Electric, Fun.move_with_vel_angle(self.pos, 35, angle),
                             angle, [0, 120, 4, 10, {"Angle modifier": 30, # "Split rate": 2,
                                                    "Target": "enemies", "On hit": [Bullets.on_hit_stun_baton]}])
    Fun.play_sound("Hitting 1", "SFX")


# |Wizard|--------------------------------------------------------------------------------------------------------------
def jeanne_shotgun_passive(self, entities, bullets):
    self.weapon.full_auto = self.status["Fuller auto"] == 0
    if self.input["Shoot"] and self.weapon.ammo != 0 and self.shot_allowed and self.no_shoot_state == 0:
        if self.is_player:
            entities["screen shake"] = [15, 3, self.aim_angle, 15]
        if not self.weapon.full_auto:
            return
        self.vel = Fun.move_with_vel_angle(self.vel, -15, self.aim_angle)


def laser_cutter_passive(self, entities, level):
    # Empty the mag
    variable_handling_rate(self, entities, level, rate=12, min_handle=0.75)
    if 0 < self.weapon.ammo < self.weapon.max_ammo:
        self.input["Shoot"] = False
        if not self.input["Alt fire"]:
            self.input["Shoot"] = True
        else:
            self.weapon.free_var["Charged shot"] += 1
            self.weapon.ammo -= 1
            for x in range(self.weapon.free_var["Charged shot"]//6):
                pos = Fun.random_point_in_circle(Fun.move_with_vel_angle(self.pos, 20, self.aim_angle), 4)
                entities["particles"].append(
                    Particles.RandomParticle2(
                        pos,
                        [(128, 255, 255), (125, 200, 220), (85, 220, 160)][x % 3],
                        1.5 + random.uniform(0, 2),
                        round(10 + 10 * random.random()),
                        360 * random.random(), size=[1, 2, 4][x % 3])
                )
    # Give a charging sound
    if self.weapon.free_var["Charged shot"] > 0 and not self.input["Alt fire"]:
        Bullets.spawn_bullet(
            self, entities, Bullets.Bullet, Fun.move_with_vel_angle(self.pos, 20, self.aim_angle), self.aim_angle,
            [2 + 2 * self.weapon.free_var["Charged shot"] / 120,
             30 + 15 * self.weapon.free_var["Charged shot"],
             4 + 16 * self.weapon.free_var["Charged shot"] / 120,
             20,
             {"Piercing": True, "Colour": (107, 165, 153), "Damage type": "Energy"}])
        self.weapon.free_var["Charged shot"] = 0
        Fun.play_sound("Electricity 1")


def laser_cutter_alt(self, entities, level):
    pass
    # Empty the mag
    # variable_handling_rate(self, entities, level, rate=12, min_handle=0.75)
    # if 0 < self.weapon.ammo < self.weapon.max_ammo:
    #     self.input["Shoot"] = True


def radio_alt(self, entities, level):
    if self.input["Shoot"] and self.no_shoot_state == 0 and self.shot_allowed and self.weapon.ammo > 0:
        self.no_shoot_state = 30
        Fun.play_sound("Artillery 2")
        # ArtilleryFlare
        Bullets.spawn_bullet(
            self, entities,
            [
                Bullets.Artillery,
                Bullets.ArtillerySmoke,
                Bullets.ArtilleryFlare,
             ][self.weapon.free_var["Ammo"]],
            self.mouse_pos.copy(), self.angle,
            self.weapon.bullet_info)
        # self.shot_allowed = False
        self.weapon.ammo -= 1
        self.input["Shoot"] = False


def radio_passive(self, entities, level):
    # if self.input["Shoot"]:
    if self.input["Shoot"] and self.no_shoot_state == 0 and self.shot_allowed and self.weapon.ammo > 0:
        # entities["background particles"].append(Fun.GrowingCircleTransparent(
        #     self.mouse_pos, Fun.BLUE, 0, 1, 64, 4, alpha=62))

        if self.weapon.free_var["Switch cooldown"] > 0:
            self.weapon.free_var["Switch cooldown"] -= 1
        elif self.input["Interact"] and self.weapon.free_var["Switch cooldown"] == 0:
            self.weapon.free_var["Ammo"] = (self.weapon.free_var["Ammo"] + 1) % 3
            self.weapon.free_var["Switch cooldown"] = 30
        # UI

        entities["UI particles"].append(Particles.CrippleLaddieUI(self))
        # Add some more UI elements to indicate which shell type is getting used
        # Used to make Crippled Laddie shoot various shell types (Smoke, Illumination, Anti-Pers)


# |Sovereign|-----------------------------------------------------------------------------------------------------------
def st_maurice_alt(self, entities, level):
    self.draw_aim_line = True
    for p in ["Perfect Aim", "No Recoil"]:
        if self.status[p] in (1, 0): self.status[p] = 2
    self.status["Stealth"] = 0
    self.vel = [0, 0]
    #


def st_laurent_passive(self, entities, level):
    # Slow down Corrine
    pass


def st_laurent_alt(self, entities, level):
    # Drop the weapon
    Items.spawn_item(entities, "Dropped Weapon", Fun.move_with_vel_angle(self.pos, 20, self.aim_angle), self=self)
    entities["items"][-1].free_var["Weapon"] = self.weapon
    # entities["items"][-1].vel = Fun.move_with_vel_angle(self.pos, 2, self.aim_angle)

    self.weapon = BasicWeapon(weapon_repertory["Unarmed"])


def unarmed_passive(self, entities, level):
    self.status["Double speed"] += 1

    if self.no_shoot_state > 0:
        return
    # Now that one is used with a reversed grip, which is kind of stupid
    key_released, weapon_info = melee_system(self, entities, level,
                                             basic_attacks=[unarmed_combo_1, unarmed_combo_2],
                                             charged_attack=unarmed_charged,
                                             basic_threshold=[7, 7], charged_threshold=30)
    if weapon_info["Press time"] > 0 and not key_released:
        self.weapon_draw_dist = weapon_info["Press time"] * -0.25
        self.draw_angle = weapon_info["Press time"] * [-1, 1][weapon_info["Combo stage"]]

    if self.draw_angle < 0:
        self.draw_angle += 5
    if self.draw_angle > 0:
        self.draw_angle -= 5
    if self.weapon_draw_dist > 0:
        self.weapon_draw_dist -= 2
    if self.weapon_draw_dist < 0:
        self.weapon_draw_dist += 2
    # if self.draw_rotated_dist > 0:
    #     self.draw_rotated_dist -= 2


def unarmed_combo_1(self, entities, level):
    self.weapon_draw_dist = 30
    self.draw_angle = -60

    angle = self.aim_angle
    Bullets.spawn_bullet(self, entities, Bullets.Melee, Fun.move_with_vel_angle(self.pos, 25, angle+30),
                         self.aim_angle, [8, 6, 16, 20, {"Always Counter": True}])
    Fun.play_sound("Hitting 1", "SFX")


def unarmed_combo_2(self, entities, level):
    self.weapon_draw_dist = 30
    self.draw_angle = 60
    angle = self.aim_angle
    Bullets.spawn_bullet(self, entities, Bullets.Melee, Fun.move_with_vel_angle(self.pos, 25, angle-30),
                         self.aim_angle, [8, 6, 16, 20, {"Always Counter": True}])
    # Bullets.spawn_bullet(self, entities, Bullets.RazorWind, Fun.move_with_vel_angle(self.pos, 20, self.aim_angle),
    #                      self.aim_angle, [4, 15, 30, 20, {"Colour": Fun.WHITE, "Angle modifier": 100,
    #                                                              "Segment amount": 1}])
    Fun.play_sound("Hitting 1", "SFX")


def unarmed_charged(self, entities, level):
    self.draw_angle = -20
    # self.aim_angle = self.angle - 50
    for x in range(7):
        angle = self.aim_angle + x * 10 - 30
        Bullets.spawn_bullet(self, entities, Bullets.Melee, Fun.move_with_vel_angle(self.pos, 25, angle),
                             angle, [8, 6, 16, 20, {"Always Counter": True}])
    # Bullets.spawn_bullet(self, entities, Bullets.RazorWind, Fun.move_with_vel_angle(self.pos, 20, self.aim_angle),
    #                      self.aim_angle, [4, 15, 30, 20, {"Colour": Fun.WHITE, "Angle modifier": 100,
    #                                                              "Segment amount": 1}])
    Fun.play_sound("Hitting 1", "SFX")


def flare_mortar_passive(self, entities, level):
    # if self.input["Shoot"]:
    if self.input["Shoot"] and self.no_shoot_state == 0 and self.shot_allowed and self.weapon.ammo > 0:

        # UI
        entities["UI particles"].append(Particles.GrowingCircleTransparent(
                        self.mouse_pos, (55, 11, 72), 1, 1, 64, 0, alpha=125))


def flare_mortar_alt(self, entities, level):
    if self.input["Shoot"] and self.no_shoot_state == 0 and self.shot_allowed and self.weapon.ammo > 0:
        self.no_shoot_state = 30
        # ArtilleryFlare
        Bullets.spawn_bullet(
            self, entities, Bullets.ArtilleryFlare, self.mouse_pos.copy(), self.angle, self.weapon.bullet_info
        )
        Bullets.spawn_bullet(
            self, entities, Bullets.Artillery, self.mouse_pos.copy(), self.angle, self.weapon.bullet_info
        )
        # self.shot_allowed = False
        self.weapon.ammo -= 1
        self.input["Shoot"] = False


# |Duke|----------------------------------------------------------------------------------------------------------------
def ax_chain_passive(self, entities, level):
    #              "Charge time": 0,
    #              "Axe pos": [0, 0],
    #              "Target pos": [0, 0],
    #              "old charge time": 0
    chain_axe = self.weapon
    base_pos = Fun.move_with_vel_angle(self.pos, 20, self.aim_angle + 20)
    axe_angle = self.aim_angle + 20
    axe_dist = 1
    axe_pos = Fun.move_with_vel_angle(base_pos, axe_dist, axe_angle)
    if chain_axe.free_var["Press time"] < 0:
        self.input["Shoot"] = False

    # When pressing, charges the next shoot
    if self.input["Shoot"]:
        chain_axe.free_var["Press time"] += 1 * (1 + int(self.status["Fuller auto"] > 0))
        axe_dist = chain_axe.free_var["Press time"] // 2
        if axe_dist > 64:
            axe_dist = 64

        p = chain_axe.free_var["Press time"]
        if p > 600:
            p = 600
        mod = math.exp2(p) * 0.5
        if mod > 32:
            mod = 32
        axe_angle = chain_axe.free_var["Press time"] * mod

        axe_pos = Fun.move_with_vel_angle(base_pos, axe_dist, axe_angle)
        Bullets.spawn_bullet( self, entities, Bullets.Melee, axe_pos, self.angle,
                              [0, 1, 12, 10, {"Colour": Fun.WHITE, "Damage type": "Melee"}])
        # .ignore_res
        # Fuller auto makes it charge faster
    elif chain_axe.free_var["Press time"] > 0 and not self.input["Shoot"]:
        # Releasing throws the axe
        if chain_axe.free_var["Press time"] > 120:
            chain_axe.free_var["Press time"] = 120

        chain_axe.free_var["old charge time"] = chain_axe.free_var["Press time"]
        chain_axe.free_var["Press time"] *= -1

        axe_pos = Fun.move_with_vel_angle(base_pos, axe_dist, axe_angle)

        chain_axe.free_var["Axe pos"] = axe_pos
        chain_axe.free_var["Target pos"] = Fun.move_with_vel_angle(
            self.pos, chain_axe.free_var["Press time"] * 1.06, self.aim_angle)

        # Give agro here
        self.agro += abs(chain_axe.free_var["Press time"] // 3)
        self.did_agro_raise = 30

        # Play sound
        entities["sounds"].append(Fun.Sound(axe_pos, 60, 175, source=self.team, strength=1))
    elif chain_axe.free_var["Press time"] < 0:
        # Handle the axe being thrown
        chain_axe.free_var["Press time"] += 1
        # get current pos of the axe
        axe_angle = Fun.angle_between(chain_axe.free_var["Axe pos"], chain_axe.free_var["Target pos"])

        axe_dist = Fun.distance_between(chain_axe.free_var["Target pos"], chain_axe.free_var["Axe pos"])
        mod = (1 - abs(chain_axe.free_var["Press time"]) / chain_axe.free_var["old charge time"]) * 0.6
        chain_axe.free_var["old charge time"] = chain_axe.free_var["Press time"]
        axe_dist *= mod

        axe_pos = Fun.move_with_vel_angle(base_pos, axe_dist, axe_angle)
        #
        Bullets.spawn_bullet( self, entities, Bullets.Melee, axe_pos, self.angle,
                              [0, 1, 16, 25, {"Colour": Fun.WHITE, "Damage type": "Melee"}])
        # .ignore_res
        if mod >= 1.1:
            # Handle Upgrades
            # 		Some melee attacks can stun enemies
            # L/M	Poison Strike
            # 		Enemies hit recieve a damage over time effect, they also take slightly more damage for other sources
            if "Stun Strike" in self.free_var:
                entities["bullets"][-1].on_hit.append(Bullets.on_hit_stun_strike)
            if "Poison Strike" in self.free_var:
                # .status["Low res"] "Damage Over time"
                entities["bullets"][-1].on_hit.append(Bullets.on_hit_poison_strike)
        if "Piercing Strike" in self.free_var:
            entities["bullets"][-1].ignore_res = True


        if self.input["Alt fire"]:
            chain_axe.free_var["Press time"] = 0

    #
    entities["background particles"].append(Particles.LineParticleAlt(
        # [base_pos[0] - chain_axe.sprite.get_width() // 2, base_pos[1] - chain_axe.sprite.get_height() // 2],
        Fun.move_with_vel_angle(self.pos, 6 + self.weapon_draw_dist, self.aim_angle),
        [axe_pos[0] - Fun.SPRITE_DUKE_AXE.get_width() // 2, axe_pos[1] - Fun.SPRITE_DUKE_AXE.get_height() // 2],
        Fun.GRAY, 1, width=1))

    entities["particles"].append(Particles.AfterImageRotated(
        axe_pos, pg.transform.flip(Fun.SPRITE_DUKE_AXE, True, -90 < axe_angle < 90), 1, axe_angle))


def hook_sword(self, entities, level):
    if self.no_shoot_state > 0:
        entities["particles"].append(
            Particles.SecondPistolParticle(
                Fun.move_with_vel_angle(self.pos, 6 + self.weapon_draw_dist, self.aim_angle),
                pg.transform.flip(self.weapon.sprite, False, True), self.reloading,
                self.weapon.reload_time, self.no_shoot_state, self.aim_angle)
        )
        return

    # Alt is a grab
    if self.input["Alt fire"]:

        target = Fun.get_stretcher_target(self, entities, 64)
        if target:
            self.weapon_draw_dist = 14
            if not self.weapon.free_var["Victim"]:
                self.weapon.free_var["Victim"] = target
                self.weapon.free_var["input func"] = target.func_input
                self.weapon.free_var["Victim"].func_input = none
                self.weapon.free_var["team"] = target.team
                self.weapon.free_var["Victim"].team = "No Name Team"

            # Place the target in front of the player and stun it
            target.pos = Fun.move_with_vel_angle(self.pos, 40, self.aim_angle)
            # target.agro += 1

        else:
            self.no_shoot_state = 100
        return
    elif self.weapon.free_var["Victim"]:
        self.weapon.free_var["Victim"].func_input = self.weapon.free_var["input func"]
        self.weapon.free_var["Victim"].team = self.weapon.free_var["team"]
        self.weapon.free_var["Victim"] = False

    # Charged, wide thing where the swords hook together
    key_released, weapon_info = melee_system(self, entities, level,
                                             basic_attacks=[hook_sword_combo_1, hook_sword_combo_2, hook_sword_combo_3],
                                             charged_attack=hook_sword_charged,
                                             basic_threshold=[4, 4, 8], charged_threshold=50)
    hook_angle = self.aim_angle
    if weapon_info["Press time"] > 0 and not key_released:
        if weapon_info["Combo stage"] == 0:
            self.weapon_draw_dist = -weapon_info["Press time"] * 1.5
        if weapon_info["Combo stage"] in [1, 2]:
            hook_angle = self.aim_angle + weapon_info["Press time"] * 2
        if weapon_info["Combo stage"] == 2:
            self.draw_angle = weapon_info["Press time"] * 2
            hook_angle = self.aim_angle + weapon_info["Press time"] * 2

    if self.draw_angle < 0:
        self.draw_angle += 3
    if self.draw_angle > 0:
        self.draw_angle -= 3
    if self.weapon_draw_dist > 0:
        self.weapon_draw_dist -= 2
    if self.weapon_draw_dist < 0:
        self.weapon_draw_dist += 2
    if self.weapon.free_var["Second sword dist"] > 0:
        self.weapon.free_var["Second sword dist"] -= 2
    if self.weapon.free_var["Second sword dist"] < 0:
        self.weapon.free_var["Second sword dist"] += 2
    # print(self.weapon_draw_dist)
    entities["particles"].append(
        Particles.SecondPistolParticle(
            Fun.move_with_vel_angle(self.pos, 6 + self.weapon.free_var["Second sword dist"], self.aim_angle),
            pg.transform.flip(self.weapon.sprite, False, True), self.reloading,
            self.weapon.reload_time, self.no_shoot_state, hook_angle + 8)
    )


def hook_sword_combo_1(self, entities, level):
    self.weapon_draw_dist = 48
    Bullets.spawn_bullet(self, entities, Bullets.Melee, Fun.move_with_vel_angle(self.pos, 25, 30),
                         self.aim_angle, [8, 6, 24, 40, {"Always Counter": True}])
    if "Piercing Strike" in self.free_var:
        entities["bullets"][-1].ignore_res = True
    Fun.play_sound("Hitting 1", "SFX")


def hook_sword_combo_2(self, entities, level):
    self.weapon.free_var["Second sword dist"] = 120
    Bullets.spawn_bullet(self, entities, Bullets.Melee, Fun.move_with_vel_angle(self.pos, 25, 30),
                         self.aim_angle, [8, 6, 32, 20, {"Always Counter": True}])
    if "Piercing Strike" in self.free_var:
        entities["bullets"][-1].ignore_res = True

    Fun.play_sound("Hitting 1", "SFX")


def hook_sword_combo_3(self, entities, level):
    Bullets.spawn_bullet(self, entities, Bullets.Melee, Fun.move_with_vel_angle(self.pos, 25, 30),
                         self.aim_angle, [8, 6, 48, 60, {"Always Counter": True}])
    if "Stun Strike" in self.free_var:
        entities["bullets"][-1].on_hit.append(Bullets.on_hit_stun_strike)
    if "Poison Strike" in self.free_var:
        entities["bullets"][-1].on_hit.append(Bullets.on_hit_poison_strike)
    if "Piercing Strike" in self.free_var:
        entities["bullets"][-1].ignore_res = True

    Fun.play_sound("Electricity 1", "SFX")
    self.draw_angle = 0


def hook_sword_charged(self, entities, level):
    for x in range(32):
        entities["particles"].append(Particles.Smoke(Fun.random_point_in_cone(self.pos, 15, self.angle, 110)))

    # Lowers agro to a -10
    self.did_agro_raise = 0
    if self.agro > 5:
        self.agro -= 5
    Fun.play_sound("Hitting 1", "SFX")


def knife_pistol_alt(self, entities, level):
    # self.input["Shoot"] = False
    self.weapon.free_var["Knife Angle"] = self.angle
    self.aim_angle = self.angle + 30
    self.weapon.free_var["Charge time"] += 1
    if self.weapon.free_var["Charge time"] == 45:
        for x in range(9):
            pos = Fun.random_point_in_circle(self.pos, 16)
            entities["particles"].append(
                Particles.RandomParticle1(pos, Fun.DARK_RED, -2, round(10 + 10 * random.random()), size=(2, 4))
            )
        # Visual effect
    if self.weapon.free_var["Charge time"] > 45:
        entities["background particles"].append(Particles.LineParticle(
            Fun.move_with_vel_angle(self.pos, 25, self.weapon.free_var["Knife Angle"]),
            Fun.BLUE, 1, 6*35, self.weapon.free_var["Knife Angle"], 1, 0))
    #


def knife_pistol_passive(self, entities, level):
    # self.input["Shoot"] = False
    if not self.input["Alt fire"]:
        if self.weapon.free_var["Charge time"] > 0:
            if self.weapon.free_var["Charge time"] > 45:
                # Projectile
                Bullets.spawn_bullet(
                    self, entities,
                    Bullets.RazorWind,
                    Fun.move_with_vel_angle(self.pos, 25, self.weapon.free_var["Knife Angle"]),
                    self.weapon.free_var["Knife Angle"],
                    [6, 35, 20, 40,
                     {"Colour": Fun.WHITE, "Angle modifier": 160, "Segment amount": 1, "Damage type": "Melee"}])

                Fun.play_sound("Skill 4", "SFX")
                if "Stun Strike" in self.free_var:
                    entities["bullets"][-1].on_hit.append(Bullets.on_hit_stun_strike)
                if "Poison Strike" in self.free_var:
                    # .status["Low res"] "Damage Over time"
                    entities["bullets"][-1].on_hit.append(Bullets.on_hit_poison_strike)
            else:
                # Slash
                Bullets.spawn_bullet(
                    self, entities,
                    Bullets.LaserDanmaku2,
                    self.pos,
                    self.aim_angle - 180,
                    [0, 10, 60, 40,
                     {"Colour": Fun.WHITE, "Angle deviation": 30,  "Damage type": "Melee"}])

            if "Piercing Strike" in self.free_var:
                entities["bullets"][-1].ignore_res = True

            self.weapon.free_var["Charge time"] = 0
        self.weapon.free_var["Knife Angle"] = self.aim_angle + 30

    angle = self.weapon.free_var["Knife Angle"]
    entities["particles"].append(
        Particles.SecondPistolParticle(
            Fun.move_with_vel_angle(self.pos, 6 + self.weapon_draw_dist, angle),
            ZANDER_KNIFE, self.reloading,
            self.weapon.reload_time, self.no_shoot_state, angle)
    )


# |M3-D1C|--------------------------------------------------------------------------------------------------------------
def medic_rifle_alt(self, entities, level):
    if self.weapon.ammo >= 3:
        angle = self.aim_angle
        Bullets.spawn_bullet(self, entities, Bullets.GrenadeType7, Fun.move_with_vel_angle(self.pos, 25, angle),
                             angle,
                             [2, 120, 8, 50,
                              {"Secondary explosion": {"Radius": 32 * 2, "No Debuff": True},
                               "Colour": Fun.LIGHT_GREEN}])
        self.no_shoot_state = self.weapon.fire_rate * 3
        self.shot_allowed = False
    # [5, 120, 4, 10, {"Secondary explosion": {"Radius": 32, "No Debuff": False}, "Colour": Fun.LIGHT_GREEN}]


def stretcher_passive(self, entities, level):
    if self.input["Shoot"]:
        if "Super Kidnapping" in self.free_var:
            target = Fun.get_stretcher_target_super_kidnapping(self, entities, 50)
        else:
            target = Fun.get_stretcher_target(self, entities, 50)

        if target:
            if not self.weapon.free_var["Victim"]:
                self.weapon.free_var["Victim"] = target
                self.weapon.free_var["input func"] = target.func_input
                self.weapon.free_var["Victim"].func_input = none
                self.weapon.free_var["team"] = target.team
                self.weapon.free_var["Victim"].team = "No Name Team"

            # Place the target in front of the player and stun it
            target.pos = Fun.move_with_vel_angle(self.pos, 20, self.aim_angle)
            target.agro += 1
            # target.status["Stunned"] = 45

        else:
            self.no_shoot_state = 100
    elif self.weapon.free_var["Victim"]:
        self.weapon.free_var["Victim"].func_input = self.weapon.free_var["input func"]
        self.weapon.free_var["Victim"].team = self.weapon.free_var["team"]
        self.weapon.free_var["Victim"] = False


def shield_generator_passive(self, entities, level):
    pos_1 = Fun.move_with_vel_angle(self.pos, 60, self.aim_angle - 65)
    pos_2 = Fun.move_with_vel_angle(self.pos, 60, self.aim_angle + 65)
    colour = Fun.GRAY
    duration = 1
    dest = "background particles"
    width = 1
    if self.input["Shoot"] and self.no_shoot_state == 0 and self.shot_allowed and self.weapon.ammo > 0:
        for b in entities["bullets"]:
            if b.team == self.team:
                continue
            if b.laser_based:
                continue
            if Fun.collision_circle_laser(b.pos, pos_1, pos_2, b.radius+3):
                b.duration = 0
                for x in range(3):
                    pos = Fun.random_point_in_circle(b.pos, 4)
                    entities["particles"].append(
                        Particles.RandomParticle1(pos, [(128, 255, 255), (125, 200, 220), (85, 220, 160)][x], [2, -2, 2][x], round(10 + 10 * random.random()),
                                            size=(1, 2))
                    )
        colour = [(128, 255, 255), (125, 200, 220), (85, 220, 160)][(self.time//6) % 3]
        duration = self.weapon.fire_rate*8
        dest = "particles"
        width = 3
    elif not self.input["Shoot"] and self.no_shoot_state == 0 and self.shot_allowed and self.weapon.ammo < self.weapon.max_ammo:
        self.weapon.ammo += 2
        if self.weapon.ammo > self.weapon.max_ammo:
            self.weapon.ammo = self.weapon.max_ammo

    entities[dest].append(Particles.LineParticleAlt(pos_1, pos_2, colour, duration, width=width))


# |Condor|--------------------------------------------------------------------------------------------------------------
def condor_dual_smg_passive(self, entities, level):
    entities["particles"].append(
        Particles.SecondPistolParticle(self.pos, self.weapon.sprite,
                                 self.reloading, self.weapon.reload_time,
                                 self.no_shoot_state, self.aim_angle))


def riot_shotgun_passive(self, entities, level):
    if not self.input["Alt fire"]:
        # Get the direction
        player_direction = Fun.get_entity_direction(self.angle + 180)

        entities["particles"].append(Particles.AfterImage(
            Fun.move_with_vel_angle(self.pos, -16, self.angle), Fun.SPRITES_RIOT_SHIELD[player_direction], 1))
    variable_handling_rate(self, entities, level, rate=12, min_handle=0.75)
    if self.weapon.free_var["Charge cooldown"] > 0:
        self.weapon.free_var["Charge cooldown"] -= 1


def riot_shotgun_alt(self, entities, level):
    # Get the direction
    player_direction = Fun.get_entity_direction(self.aim_angle)

    # Place the Shield
    Items.spawn_item(entities, "Riot Shield", Fun.move_with_vel_angle(self.pos, 16, self.angle), self=self)
    entities["items"][-1].free_var["Sprite"] = player_direction

    charge = self.input["Shoot"]
    # Prevent the player from doing some other actions
    self.input["Shoot"], self.input["Reload"] = False, False
    self.input["Sk1"], self.input["Sk2"] = False, False

    if self.weapon.free_var["Charge cooldown"] <= 0:
        if charge:
            Items.spawn_item(entities, "M3-D1C OUT OF MY WAY", self.pos.copy(), self=self)
            uptime = 30
            entities["items"][-1].life_time = uptime
            self.weapon.free_var["Charge cooldown"] = uptime
            self.vel = Fun.move_with_vel_angle([0, 0], 17, self.aim_angle)
            Fun.play_sound("Hitting 3")
            return

        # Other effect
        if self.status["High friction"] >= 1:
            self.status["High friction"] += 1
        else:
            self.status["High friction"] = 2


def three_round_burst(self, entities, bullets):
    self.weapon.full_auto = False
    self.weapon.fire_rate = 2
    if self.weapon.ammo % 3 != 0:
        self.weapon.full_auto = True
        self.shot_allowed = True
        self.input["Shoot"] = True
        if (self.weapon.ammo - 1) % 3 == 0:
            self.weapon.fire_rate = 20


# |Fortress|------------------------------------------------------------------------------------------------------------
def fortress_alt(self, entities, level):
    pass


def fortress_passive(self, entities, level):
    if self.input["Alt fire"]:
        angle = self.free_var["Move angle"] + 226 - 180
        pos = [self.pos[0], self.pos[1] - 16]
        pos = Fun.move_with_vel_angle(pos, 22.6274, angle)
        pos = Fun.move_with_vel_angle(pos, 20, self.aim_angle)
        self.angle = Fun.angle_between(self.mouse_pos, pos)
    variable_handling_rate(self, entities, level, rate=12, min_handle=0.75)


# |Curtis|--------------------------------------------------------------------------------------------------------------
def standard_shotgun_passive(self, entities, level):
    if self.input["Interact"] and self.no_shoot_state == 0 and self.weapon.ammo == self.weapon.max_ammo:
        switch_weapon = BasicWeapon(weapon_repertory["Cowboy's Repeater"])
        switch_weapon.ammo_pool = self.weapon.ammo_pool
        self.no_shoot_state = 30
        self.weapon = switch_weapon
        if "Damage boost" in self.free_var:
            self.weapon.bullet_info[3] *= 2
        return

    if "Standard Shotgun Attack" in self.free_var:
        if self.no_shoot_state == 0:
            self.free_var.pop("Standard Shotgun Attack")
            angle = self.aim_angle
            pos = Fun.move_with_vel_angle(self.pos, 20, self.aim_angle)
            self.weapon.ammo -= 1
            Fun.play_sound("Rifle 2")
            for b in range(15):
                Bullets.spawn_bullet(
                    self, entities,
                    Bullets.Bullet,
                    Fun.move_with_vel_angle(pos, -14 + b * 2, angle + 90),
                    angle,
                    [4 + 2 * random.random(), 60, 4, round(self.weapon.bullet_info[3] * 0.8), {'Colour': Fun.ORANGE}])


def standard_shotgun_alt(self, entities, level):
    if self.weapon.ammo > 1:
        self.no_shoot_state = 30
        self.vel = Fun.move_with_vel_angle(self.vel, -3, self.angle)
        self.status["Forced Slide"] += 15
        self.free_var.update({"Standard Shotgun Attack": True})
        Fun.play_sound(self.weapon.reload_sound)
        self.weapon.ammo -= 1


def cowboy_repeater_passive(self, entities, level):
    if self.input["Interact"] and self.no_shoot_state == 0 and self.weapon.ammo == self.weapon.max_ammo:
        switch_weapon = BasicWeapon(weapon_repertory["Standard Shotgun"])
        switch_weapon.ammo_pool = self.weapon.ammo_pool
        self.no_shoot_state = 30

        self.weapon = switch_weapon
        if "Damage boost" in self.free_var:
            self.weapon.bullet_info[3] *= 2
        return

    # Alt fire
    # Check for input
    # Increase gauge
    # Look for targets

    # Check if gauge is filled
    # Shoot at targets


def cowboy_repeater_alt(self, entities, level):
    # Give it a new alt fire
    # charged burst, but it in passive
    pass


def war_and_peace_alt(self, entities, level):
    pass


def war_and_peace_passive(self, entities, level):
    angle = self.weapon.free_var["War angle"]
    entities["particles"].append(
        Particles.SecondPistolParticle(
            Fun.move_with_vel_angle(self.pos, 6 + self.weapon_draw_dist, angle),
            Fun.SPRITE_CURTIS_WAR, self.reloading,
            self.weapon.reload_time, self.no_shoot_state, angle)
    )
    if self.input["Shoot"] and self.no_shoot_state == 0 and self.shot_allowed and self.weapon.ammo > 0:
        self.shoot_bullet(entities, level)
        self.bullets_shot[0].angle = angle
        self.bullets_shot[0].pos = Fun.move_with_vel_angle(self.pos, 20, angle)

    if self.input["Alt fire"]:
        if self.status["Stunned"]: return
        # Value Limiter
        self.weapon.free_var["War angle"] = Fun.angle_value_limiter(
            Fun.move_angle(self.angle, self.weapon.free_var["War angle"], self.weapon.handle * 8)
        )


def hunk_of_steel_passive(self, entities, level):
    if self.no_shoot_state != 0:
        return

    if self.input["Alt fire"]:
        self.draw_angle = 90
        self.draw_rotated_dist = 14
        self.weapon_draw_dist = 8
        if self.weapon.free_var["Charge cooldown"] > 0:
            self.weapon.free_var["Charge cooldown"] -= 1
        return
    # self.draw_angle = 0

    key_released, weapon_info = melee_system(self, entities, level,
                                             basic_attacks=[hunk_of_steel_combo_1,
                                                            hunk_of_steel_combo_2,
                                                            hunk_of_steel_combo_3
                                                            ],
                                             charged_attack=hunk_of_steel_charged,
                                             basic_threshold=[14, 14, 36], charged_threshold=60)

    # entities["particles"].append(Fun.LineParticle(self.pos, Fun.GREEN, 1, 6 * 80, self.weapon.free_var["Sword target angle"] + self.angle))

    allow_angle_change = True
    if self.weapon.free_var["Angle ref"]:
        self.aim_angle = self.weapon.free_var["Angle ref"].angle + 90 * self.weapon.free_var["Mod"] - self.weapon.free_var["Angle ref"].angle_deviation * self.weapon.free_var["Mod"] # reverse this on second combo stage
        if self.weapon.free_var["Angle ref"].duration == 0:
            self.weapon.free_var["Angle ref"] = False
        allow_angle_change = False

    if weapon_info["Press time"] > 0 and not key_released:
        if weapon_info["Combo stage"] in [0, 1] and allow_angle_change:
            self.draw_angle = weapon_info["Press time"] * [1, -1][weapon_info["Combo stage"]] * 2
            # self.weapon.free_var["Sword target angle"] = weapon_info["Press time"] * [1, -1][weapon_info["Combo stage"]] * 2.5
            # print(self.draw_angle)
        if weapon_info["Combo stage"] == 2:
            self.weapon_draw_dist = -weapon_info["Press time"] * 0.5

    if allow_angle_change:
        if self.draw_angle < 0:
            self.draw_angle += 3
        if self.draw_angle > 0:
            self.draw_angle -=3
    if self.weapon_draw_dist > 0:
        self.weapon_draw_dist -= 2
    if self.weapon_draw_dist < 0:
        self.weapon_draw_dist += 2
    if self.weapon_draw_dist < 0:
        self.weapon_draw_dist += 2
    if self.draw_rotated_dist > 0:
        self.draw_rotated_dist -= 2


def hunk_of_steel_combo_1(self, entities, level):
    # self.draw_angle = -120
    self.draw_angle = 0
    self.status["Low friction"] += 25
    self.vel = Fun.move_with_vel_angle([0, 0], 6, self.aim_angle + 15)
    self.weapon.free_var["Mod"] = 1

    deviation = 25
    Bullets.spawn_bullet(
        self, entities, Bullets.LaserDanmaku2,
        self.pos, self.aim_angle - 180,
        [0, 10, 60, 250,
         {"Colour": Fun.WHITE, "Angle deviation": deviation, "Damage type": "Melee"}])
    self.weapon.free_var["Angle ref"] = entities["bullets"][-1]

    Fun.play_sound("Hitting 1", "SFX")


def hunk_of_steel_combo_2(self, entities, level):
    # self.draw_angle = 120
    self.draw_angle = 0
    self.status["Low friction"] += 25
    self.vel = Fun.move_with_vel_angle([0, 0], 6, self.aim_angle - 15)

    deviation = -25
    self.weapon.free_var["Mod"] = -1
    Bullets.spawn_bullet(
        self, entities,
        Bullets.LaserDanmaku2,
        self.pos,
        self.aim_angle + 180,
        [0, 10, 60, 250,
         {"Colour": Fun.WHITE, "Angle deviation": deviation, "Damage type": "Melee"}])
    self.weapon.free_var["Angle ref"] = entities["bullets"][-1]
    Fun.play_sound("Hitting 1", "SFX")


def hunk_of_steel_combo_3(self, entities, level):
    self.vel = Fun.move_with_vel_angle([0, 0], 12, self.aim_angle)
    self.status["Low friction"] += 25

    self.weapon.free_var["Sword target angle"] = 0
    self.weapon_draw_dist = 30
    Bullets.spawn_bullet(
        self, entities,
        Bullets.RazorWind,
        Fun.move_with_vel_angle(self.pos, 25, self.aim_angle),
        self.aim_angle,
        [6, 35, 60, 250,
         {"Colour": Fun.WHITE, "Angle modifier": 170, "Segment amount": 1, "Damage type": "Melee"}])

    Fun.play_sound("Hitting 2")
    self.draw_angle = 0


def hunk_of_steel_charged(self, entities, level):
    self.draw_angle = 0
    self.status["Low friction"] += 50
    self.vel = Fun.move_with_vel_angle([0, 0], 12, self.aim_angle)
    self.weapon.free_var["Mod"] = 1

    deviation = 15
    Bullets.spawn_bullet(
        self, entities, Bullets.LaserDanmaku2,
        self.pos, self.aim_angle - 180,
        [0, 90, 60, 250,
         {"Colour": Fun.WHITE, "Angle deviation": deviation, "Damage type": "Melee"}])
    self.weapon.free_var["Angle ref"] = entities["bullets"][-1]

    Fun.play_sound("Hitting 3")


def hunk_of_steel_alt(self, entities, bullets):

    Items.spawn_item(entities, "Hunk of steel", Fun.move_with_vel_angle(self.pos, 16, self.angle), self=self)
    charge = self.input["Shoot"]
    self.input["Shoot"] = False
    self.input["Sk1"], self.input["Sk2"] = False, False

    if self.weapon.free_var["Charge cooldown"] <= 0:
        if charge:
            Items.spawn_item(entities, "M3-D1C OUT OF MY WAY", self.pos.copy(), self=self)
            uptime = 30
            entities["items"][-1].life_time = uptime
            self.weapon.free_var["Charge cooldown"] = uptime
            self.vel = Fun.move_with_vel_angle([0, 0], 17, self.aim_angle)
            Fun.play_sound("Hitting 3")
            return

        # Other effect
        if self.status["High friction"] >= 1:
            self.status["High friction"] += 1
        else:
            self.status["High friction"] = 2


# |Lawrence|------------------------------------------------------------------------------------------------------------
# Cutlass & Flintlock
def cutlass_flintlock(self, entities, level):
    if self.input["Alt fire"] and self.no_shoot_state == 0:
        self.vel = [0, 0]
        self.aim_angle = self.angle + 75
        pos = Fun.move_with_vel_angle(self.pos, 20, self.angle)

        angle = self.angle
        entities["particles"].append(Particles.LineParticle(pos, Fun.GREEN, 1, 6 * 80, angle))

        entities["particles"].append(Particles.AfterImageRotated(
            Fun.move_with_vel_angle(self.pos, 15, angle),
            pg.transform.flip(LAWRENCE_FLINTLOCK, True, -90 < angle < 90),
            1, angle))

        if self.status["Perfect Aim"] in (1, 0):
            self.status["Perfect Aim"] = 2
        if self.input["Shoot"]:
            # [6, 80, 5, 30, {"Piercing": True, "Smoke": False}]
            on_hit_list = []
            if "Carcass" in self.free_var:
                on_hit_list.append(Bullets.on_hit_carcass)
            if "Hellfire" in self.free_var:
                on_hit_list.append(Bullets.on_hit_hellfire)
            angle_mod = 0
            bullet_count = 1
            if "Grapeshot" in self.free_var:
                angle_mod = 20
                bullet_count = 3
            for x in range(bullet_count):
                Bullets.spawn_bullet(
                    self, entities,
                    Bullets.Bullet,
                    pos,
                    self.angle + random.uniform(-angle_mod, angle_mod),
                    [6, 80, 5, 30, {"Piercing": True, "Smoke": False}])
                entities["bullets"][-1].on_hit = on_hit_list
            Fun.play_sound("Rifle 2")
            self.no_shoot_state = 300
        return
    # Draw flintlock
    angle = self.angle + 45
    entities["particles"].append(Particles.AfterImageRotated(
        Fun.move_with_vel_angle(self.pos, 15, angle),
        pg.transform.flip(LAWRENCE_FLINTLOCK, True, -90 < angle < 90),
        1, angle))
    # Melee logic
    key_released, weapon_info = melee_system(
        self, entities, level, basic_attacks=(
            cutlass_combo_1, cutlass_combo_2, cutlass_combo_3, cutlass_combo_4),
        charged_attack=cutlass_charged,
        basic_threshold=5, charged_threshold=50)
    if weapon_info["Press time"] > 0:
        if weapon_info["Combo stage"] == 0:
            self.weapon_draw_dist = weapon_info["Press time"] * -0.25
        else:
            self.aim_angle = self.angle + weapon_info["Press time"] * [3, -3][weapon_info["Combo stage"] % 2]

    if self.weapon_draw_dist < 0:
        self.weapon_draw_dist += 2


def cutlass_combo_1(self, entities, bullets):
    self.aim_angle = self.angle
    target = Fun.find_closest_in_cone(self, entities, 256, "Players", self.aim_angle, 33)
    mod = 1
    if "Dragon Breath" in self.free_var:
        mod = 2
    fire_mod = 1
    duration_mod = 1
    on_hit_list = []
    if "Cremation" in self.free_var: # , "On hit": on_hit_list
        on_hit_list = [Bullets.on_hit_cremation]
    if "Spontaneous Combustion" in self.free_var:
        duration_mod = 0.5
        fire_mod = 2
    if "Slow Burn" in self.free_var:
        duration_mod = 2
    angle = self.aim_angle
    dist = 6
    if target:
        angle = Fun.angle_between(target, self.pos)
        dist = Fun.distance_between(target, self.pos) * 0.3
        if dist > 8:
            dist = 8
    self.vel = Fun.move_with_vel_angle([0, 0], dist, angle)
    Fun.play_sound("Skill 2", "SFX")
    for x in range(7):
        Bullets.spawn_bullet(
            self, entities,
            Bullets.Napalm,
            Fun.move_with_vel_angle(self.pos, 20, angle),
            angle + random.uniform(-4, 4),
            [random.uniform(2, 5), 180, random.uniform(4, 7),
             10 * mod * fire_mod, {"Particle allowed": x % 2 == 0,
                  "Burn chance": 0.4,
                  "Burn duration": 30 * duration_mod,
                  "Colour": Fun.LIGHT_BLUE, "On hit": on_hit_list
                  }])
    Fun.play_sound("Son slash", "SFX")


def cutlass_combo_2(self, entities, bullets):
    self.aim_angle = self.angle
    mod = 1
    if "Dragon Breath" in self.free_var:
        mod = 2
    Bullets.spawn_bullet(
        self, entities,
        Bullets.Melee,
        Fun.move_with_vel_angle(self.pos, 25, self.aim_angle),
        self.aim_angle,
        [0, 4, 30, 30 * mod, {}])

    fire_mod = 1
    duration_mod = 1
    on_hit_list = []
    if "Cremation" in self.free_var: # , "On hit": on_hit_list
        on_hit_list = [Bullets.on_hit_cremation]
    if "Spontaneous Combustion" in self.free_var:
        duration_mod = 0.5
        fire_mod = 2
    if "Slow Burn" in self.free_var:
        duration_mod = 2

    for x in range(7):
        angle = self.aim_angle - 7 * 4 + 7 * x
        Bullets.spawn_bullet(
            self, entities,
            Bullets.Napalm,
            Fun.move_with_vel_angle(self.pos, 20, angle),
            angle + random.uniform(-4, 4),
            [1 + 3 * random.random(), 320, random.uniform(6, 9),
             10 * mod * fire_mod, {"Particle allowed": x % 2 == 0,
                  "Burn chance": 0.4,
                  "Burn duration": 30 * duration_mod,
                  "Colour": Fun.LIGHT_BLUE, "On hit": on_hit_list
                  }])
    Fun.play_sound("Hitting 1", "SFX")


def cutlass_combo_3(self, entities, bullets):
    self.aim_angle = self.angle
    mod = 1
    if "Dragon Breath" in self.free_var:
        mod = 2
    Bullets.spawn_bullet(
        self, entities,
        Bullets.Melee,
        Fun.move_with_vel_angle(self.pos, 25, self.aim_angle),
        self.aim_angle,
        [0, 4, 30, 30 * mod, {}])

    fire_mod = 1
    duration_mod = 1
    on_hit_list = []
    if "Cremation" in self.free_var: # , "On hit": on_hit_list
        on_hit_list = [Bullets.on_hit_cremation]
    if "Spontaneous Combustion" in self.free_var:
        duration_mod = 0.5
        fire_mod = 2
    if "Slow Burn" in self.free_var:
        duration_mod = 2

    for y in [15, -15]:
        for x in range(7):
            angle = self.aim_angle + y
            Bullets.spawn_bullet(
                self, entities,
                Bullets.Napalm,
                Fun.move_with_vel_angle(self.pos, 20, angle),
                angle + random.uniform(-4, 4),
                [random.uniform(2, 5), 180, random.uniform(4, 7),
                 10 * mod * fire_mod, {"Particle allowed": x % 2 == 0,
                      "Burn chance": 0.4,
                      "Burn duration": 30 * duration_mod,
                      "Colour": Fun.LIGHT_BLUE, "On hit": on_hit_list
                      }])
    Fun.play_sound("Hitting 1", "SFX")


def cutlass_combo_4(self, entities, bullets):
    self.aim_angle = self.angle
    mod = 1
    if "Dragon Breath" in self.free_var:
        mod = 2
    Bullets.spawn_bullet(
        self, entities,
        Bullets.Melee,
        Fun.move_with_vel_angle(self.pos, 25, self.aim_angle),
        self.aim_angle,
        [0, 4, 30, 30 * mod, {}])

    fire_mod = 1
    duration_mod = 1
    on_hit_list = []
    if "Cremation" in self.free_var: # , "On hit": on_hit_list
        on_hit_list = [Bullets.on_hit_cremation]
    if "Spontaneous Combustion" in self.free_var:
        duration_mod = 0.5
        fire_mod = 2
    if "Slow Burn" in self.free_var:
        duration_mod = 2

    for x in range(11):
        angle = self.aim_angle - 5 * 6 + 5 * x
        Bullets.spawn_bullet(
            self, entities,
            Bullets.Napalm,
            Fun.move_with_vel_angle(self.pos, 20, angle),
            angle + random.uniform(-4, 4),
            [1 + 3 * random.random(), 320, random.uniform(6, 9),
             10 * mod * fire_mod, {"Particle allowed": x % 2 == 0,
                  "Burn chance": 0.4,
                  "Burn duration": 30 * duration_mod,
                  "Colour": Fun.LIGHT_BLUE, "On hit": on_hit_list
                  }])

    Fun.play_sound("Hitting 1", "SFX")


def cutlass_charged(self, entities, bullets):
    mod = 1
    if "Dragon Breath" in self.free_var:
        mod = 2
    self.weapon_draw_dist = 0
    self.aim_angle = self.angle

    fire_mod = 1
    duration_mod = 1
    on_hit_list = []
    if "Cremation" in self.free_var: # , "On hit": on_hit_list
        on_hit_list = [Bullets.on_hit_cremation]
    if "Spontaneous Combustion" in self.free_var:
        duration_mod = 0.5
        fire_mod = 2
    if "Slow Burn" in self.free_var:
        duration_mod = 2
    for y in range(3):
        for x in range(7):
            angle = self.aim_angle - 5 * 3 + 5 * x
            Bullets.spawn_bullet(
                self, entities,
                Bullets.Napalm,
                Fun.move_with_vel_angle(self.pos, 20, angle),
                angle + random.uniform(-4, 4),
                [4 + 3 * random.random() * y, 180, random.uniform(4, 7),
                 10 * mod * fire_mod, {"Particle allowed": x % 2 == 0,
                      "Burn chance": 0.4,
                      "Burn duration": 30 * duration_mod,
                      "Colour": Fun.LIGHT_BLUE, "On hit": on_hit_list
                      }])

    Fun.play_sound("Skill 1", "SFX")


def axe_blunderbuss(self, entities, level):
    mod = 1
    if "Dragon Breath" in self.free_var:
        mod = 2
    if self.input["Alt fire"] and self.no_shoot_state == 0:
        self.vel = [0, 0]
        self.aim_angle = self.angle + 75
        pos = Fun.move_with_vel_angle(self.pos, 20, self.angle)

        angle = self.angle
        entities["particles"].append(Particles.LineParticle(pos, Fun.GREEN, 1, 6 * 80, angle))

        entities["particles"].append(Particles.AfterImageRotated(
            Fun.move_with_vel_angle(self.pos, 15, angle),
            pg.transform.flip(LAWRENCE_BLUNDERBUSS, True, -90 < angle < 90),
            1, angle))

        if self.status["Perfect Aim"] in (1, 0):
            self.status["Perfect Aim"] = 2

        # Blunderbuss attack
        if self.input["Shoot"]:
            on_hit_list = []
            if "Carcass" in self.free_var:
                on_hit_list.append(Bullets.on_hit_carcass)
            if "Hellfire" in self.free_var:
                on_hit_list.append(Bullets.on_hit_hellfire)
            angle_mod = 15
            bullet_count = 1
            if "Grapeshot" in self.free_var:
                angle_mod = 35
                bullet_count = 3
            for x in range(12*bullet_count):
                Bullets.spawn_bullet(
                    self, entities, Bullets.Bullet,
                    pos.copy(), self.angle + random.uniform(-angle_mod, angle_mod),
                    [3 + 3 * random.random(), 80, 5, 30 * mod, {"Piercing": True, "Smoke": True}])
                entities["bullets"][-1].wall_physics = Bullets.base_grenade_wall_hit
                entities["bullets"][-1].on_hit = on_hit_list
            Fun.play_sound("Rifle 2")
            self.no_shoot_state = 300
        return

    # Draw blunderbuss
    angle = self.angle + 45
    entities["particles"].append(Particles.AfterImageRotated(
        Fun.move_with_vel_angle(self.pos, 15, angle),
        pg.transform.flip(LAWRENCE_BLUNDERBUSS, True, -90 < angle < 90),
        1, angle))
    # Melee logic
    key_released, weapon_info = melee_system(
        self, entities, level, basic_attacks=(
            axe_combo_1, axe_combo_2, axe_combo_3),
        charged_attack=axe_charged,
        basic_threshold=20, charged_threshold=60)
    if weapon_info["Press time"] > 0:
        if weapon_info["Combo stage"] == 0:
            self.weapon_draw_dist = weapon_info["Press time"] * -0.25
        else:
            self.aim_angle = self.angle + weapon_info["Press time"] * [3, -3][weapon_info["Combo stage"] % 2]

    if self.weapon_draw_dist < 0:
        self.weapon_draw_dist += 2


def axe_combo_1(self, entities, bullets):
    mod = 1
    if "Dragon Breath" in self.free_var:
        mod = 2

    angle = self.aim_angle

    fire_mod = 1
    duration_mod = 1
    on_hit_list = []
    if "Cremation" in self.free_var: # , "On hit": on_hit_list
        on_hit_list = [Bullets.on_hit_cremation]
    if "Spontaneous Combustion" in self.free_var:
        duration_mod = 0.5
        fire_mod = 2
    if "Slow Burn" in self.free_var:
        duration_mod = 2

    self.vel = Fun.move_with_vel_angle([0, 0], -5, angle)
    Fun.play_sound("Skill 2", "SFX")
    for x in range(48):
        Bullets.spawn_bullet(
            self, entities,
            Bullets.Napalm,
            Fun.move_with_vel_angle(self.pos, 20, angle),
            angle + random.uniform(-110, 110),
            [random.uniform(1, 3), 180, random.uniform(11, 14),
             30 * mod * fire_mod, {"Particle allowed": x % 3 == 0,
                  "Burn chance": 0.4,
                  "Burn duration": 30 * duration_mod,
                  "Colour": Fun.LIGHT_RED, "On hit": on_hit_list
                  }])
    Fun.play_sound("Son slash", "SFX")


def axe_combo_2(self, entities, bullets):
    mod = 1
    if "Dragon Breath" in self.free_var:
        mod = 2
    self.aim_angle = self.angle
    angle = self.aim_angle
    Bullets.spawn_bullet(
        self, entities,
        Bullets.Melee,
        Fun.move_with_vel_angle(self.pos, 25, self.aim_angle),
        self.aim_angle,
        [0, 4, 30, 30 * mod, {}])

    fire_mod = 1
    duration_mod = 1
    on_hit_list = []
    if "Cremation" in self.free_var: # , "On hit": on_hit_list
        on_hit_list = [Bullets.on_hit_cremation]
    if "Spontaneous Combustion" in self.free_var:
        duration_mod = 0.5
        fire_mod = 2
    if "Slow Burn" in self.free_var:
        duration_mod = 2

    for x in range(15):

        Bullets.spawn_bullet(
            self, entities,
            Bullets.Napalm,
            Fun.move_with_vel_angle(self.pos, 20, angle),
            angle + random.uniform(-8, 8),
            [3 + 6 * random.random(), 480, random.uniform(12, 16),
             20 * mod * fire_mod, {"Particle allowed": x % 3 == 0,
                  "Burn chance": 0.4,
                  "Burn duration": 30 * duration_mod,
                  "Colour": Fun.LIGHT_RED, "On hit": on_hit_list
                  }])
    Fun.play_sound("Hitting 1", "SFX")


def axe_combo_3(self, entities, bullets):
    mod = 1
    if "Dragon Breath" in self.free_var:
        mod = 2
    self.aim_angle = self.angle

    Bullets.spawn_bullet(
        self, entities,
        Bullets.Melee,
        Fun.move_with_vel_angle(self.pos, 25, self.aim_angle),
        self.aim_angle,
        [0, 4, 30 * mod, 30, {}])

    fire_mod = 1
    duration_mod = 1
    on_hit_list = []
    if "Cremation" in self.free_var: # , "On hit": on_hit_list
        on_hit_list = [Bullets.on_hit_cremation]
    if "Spontaneous Combustion" in self.free_var:
        duration_mod = 0.5
        fire_mod = 2
    if "Slow Burn" in self.free_var:
        duration_mod = 2

    for x in range(72):
        angle = self.aim_angle  + random.uniform(-140, 140)
        Bullets.spawn_bullet(
            self, entities,
            Bullets.Napalm,
            Fun.move_with_vel_angle(self.pos, 20, angle),
            angle,
            [4 * random.random(), 480, random.uniform(12, 16),
             20 * mod * fire_mod, {"Particle allowed": x % 6 == 0,
                  "Burn chance": 0.4,
                  "Burn duration": 30 * duration_mod,
                  "Colour": Fun.LIGHT_RED, "On hit": on_hit_list
                }])
    Fun.play_sound("Hitting 1", "SFX")


def axe_charged(self, entities, bullets):
    mod = 1
    if "Dragon Breath" in self.free_var:
        mod = 2
    self.weapon_draw_dist = 0
    self.aim_angle = self.angle
    angle = self.aim_angle

    fire_mod = 1
    duration_mod = 1
    on_hit_list = []
    if "Cremation" in self.free_var: # , "On hit": on_hit_list
        on_hit_list = [Bullets.on_hit_cremation]
    if "Spontaneous Combustion" in self.free_var:
        duration_mod = 0.5
        fire_mod = 2
    if "Slow Burn" in self.free_var:
        duration_mod = 2

    for y in range(7):
        for x in range(4):
            Bullets.spawn_bullet(
                self, entities,
                Bullets.Napalm,
                Fun.move_with_vel_angle(self.pos, 20, angle),
                angle + random.uniform(-110, 110),
                [random.uniform(1, 3), 180, random.uniform(2, 10),
                 30 * mod * fire_mod, {"Particle allowed": x % 3 == 0,
                      "Burn chance": 0.4,
                      "Burn duration": 30 * duration_mod,
                      "Colour": Fun.LIGHT_RED, "On hit": on_hit_list
                      }])

        Bullets.spawn_bullet(
            self, entities,
            Bullets.GrenadeType2,
            Fun.move_with_vel_angle(self.pos, 20, angle),
            angle + random.uniform(-110, 110),
            [5, 100, 4, 10 * mod, {"Incendiary": {
                "Amount of Bullets": 16,
                "Speed": 2,
                "Duration": 90,
                "Radius": 4,
                "Damage": 5 * mod * fire_mod,
                "Fire property": {"Particle allowed": True, "Burn chance": 1, "Burn duration": 30 * duration_mod, "Colour": Fun.FIRE, "On hit": on_hit_list}},
                "Colour": Fun.LIGHT_RED
            }])
    Fun.play_sound("Skill 1", "SFX")


def musket_360(self, entities, level):
    mod = 1
    if "Dragon Breath" in self.free_var:
        mod = 2
    if self.input["Alt fire"] and self.no_shoot_state == 0:
        self.weapon_draw_dist = -4
        self.draw_angle = 0

        self.vel = [0, 0]
        pos = Fun.move_with_vel_angle(self.pos, 20, self.aim_angle)

        angle = self.aim_angle
        entities["particles"].append(Particles.LineParticle(pos, Fun.GREEN, 1, 6 * 80, angle))

        if self.input["Shoot"]:
            on_hit_list = []
            if "Carcass" in self.free_var:
                on_hit_list.append(Bullets.on_hit_carcass)
            if "Hellfire" in self.free_var:
                on_hit_list.append(Bullets.on_hit_hellfire)
            angle_mod = 0
            bullet_count = 1
            if "Grapeshot" in self.free_var:
                angle_mod = 15
                bullet_count = 3
            for x in range(bullet_count):
                Bullets.spawn_bullet(
                    self, entities,
                    Bullets.Bullet,
                    pos,
                    self.aim_angle + random.uniform(-angle_mod, angle_mod),
                    self.weapon.bullet_info)
                entities["bullets"][-1].damage *= mod
                entities["bullets"][-1].on_hit = on_hit_list
            Fun.play_sound("Rifle 2")
            self.no_shoot_state = 300
        return

    melee_system(self, entities, level,
                 basic_attacks=[spear_combo_1, spear_combo_2, spear_combo_3],
                 charged_attack=spear_charged,
                 basic_threshold=6, charged_threshold=30)

    if self.weapon_draw_dist > 0:
        self.weapon_draw_dist -= 2
    else:
        if self.draw_angle > 0:
            self.draw_angle -= 5


def spear_combo_1(self, entities, level):
    mod = 1
    if "Dragon Breath" in self.free_var:
        mod = 2
    self.weapon_draw_dist = 20
    Bullets.spawn_bullet(
        self, entities,
        Bullets.RazorWind,
        Fun.move_with_vel_angle(self.pos, 25, self.aim_angle),
        self.aim_angle,
        [6, 25, 30, 40 * mod, {"Colour": Fun.WHITE, "Angle modifier": 150, "Segment amount": 1, "Damage type": "Melee"}])

    Fun.play_sound("Skill 4", "SFX")
    self.vel = Fun.move_with_vel_angle(self.vel, 8, self.angle)


def spear_combo_2(self, entities, level):
    mod = 1
    if "Dragon Breath" in self.free_var:
        mod = 2
    self.weapon_draw_dist = 20
    Bullets.spawn_bullet(
        self, entities,
        Bullets.RazorWind,
        Fun.move_with_vel_angle(self.pos, 25, self.aim_angle),
        self.aim_angle,
        [7, 25, 30, 40 * mod, {"Colour": Fun.WHITE, "Angle modifier": 150, "Segment amount": 1, "Damage type": "Melee"}])
    Fun.play_sound("Skill 4", "SFX")
    self.vel = Fun.move_with_vel_angle(self.vel, 8, self.angle)


def spear_combo_3(self, entities, level):
    mod = 1
    if "Dragon Breath" in self.free_var:
        mod = 2
    self.weapon_draw_dist = 20
    Bullets.spawn_bullet(
        self, entities,
        Bullets.RazorWind,
        Fun.move_with_vel_angle(self.pos, 25, self.aim_angle),
        self.aim_angle,
        [8, 25, 30, 40 * mod, {"Colour": Fun.WHITE, "Angle modifier": 150, "Segment amount": 1, "Damage type": "Melee"}])

    Fun.play_sound("Skill 4", "SFX")
    self.vel = Fun.move_with_vel_angle(self.vel, 12, self.angle)


def spear_charged(self, entities, level):
    mod = 1
    if "Dragon Breath" in self.free_var:
        mod = 2
    # self.draw_angle = 180
    self.draw_angle = 130
    self.weapon_draw_dist = 50

    fire_mod = 1
    duration_mod = 1
    on_hit_list = []
    if "Cremation" in self.free_var:
        on_hit_list = [Bullets.on_hit_cremation]
    if "Spontaneous Combustion" in self.free_var:
        duration_mod = 0.5
        fire_mod = 2
    if "Slow Burn" in self.free_var:
        duration_mod = 2

    self.aim_angle = self.angle
    for y in range(3):
        for x in range(14):
            angle = self.aim_angle - 2 * 3 + x
            Bullets.spawn_bullet(
                self, entities,
                Bullets.Napalm,
                Fun.move_with_vel_angle(self.pos, 20, angle),
                angle + random.uniform(-4, 4),
                [4 + 3 * random.random() * y, 180, random.uniform(7, 12),
                 20 * mod * fire_mod, {"Particle allowed": x % 2 == 0,
                      "Burn chance": 0.6,
                      "Burn duration": 60 * duration_mod,
                      "Colour": Fun.LIGHT_GREEN,
                      "On hit": on_hit_list
                      }])

    Fun.play_sound("Skill 1", "SFX")

    # pos = Fun.move_with_vel_angle(self.pos, 80, self.aim_angle)
    # radius = 35

    # bullets["enemies"].append(Bullets.Melee(pos, self.aim_angle, [0, 2, radius, 20, {}]))
    # Fun.random_particle_2_circle(entities, pos, 2.3333333333333333333333333333333, 15, 18, colour=Fun.YELLOW, size=5)
    Fun.play_sound("Hitting 2", "SFX")


# |Mark|----------------------------------------------------------------------------------------------------------------
# Rifle
def mark_rifle_alt(self, entities, level):
    self.draw_aim_line = True
    if self.status["Perfect Aim"] in (1, 0):
        self.status["Perfect Aim"] = 2
    if self.status["Forced Slide"] == 0:
        if self.status["High friction"] in (1, 0):
            self.status["High friction"] = 2
    #


def c4_passive(self, entities, level):
    if self.input["Reload"] and self.no_shoot_state == 0:
        for c4 in self.weapon.free_var["C4 out"]:
            c4.duration = 0
        self.weapon.free_var["C4 out"] = []


# |Vivianne|------------------------------------------------------------------------------------------------------------
def vivianne_rifle(self, entities, bullets):
    if self.input["Reload"]:
        self.input["Reload"] = False
        self.reloading = True
        self.no_shoot_state = self.weapon.reload_time // 2
        if 0 <= self.angle <= 120:
            # Normal load
            vivianne_rifle_normal(self)
        elif 0 >= self.angle >= -120:
            # Slug
            vivianne_rifle_flechettes(self)
        else:
            # Napalm Round
            vivianne_rifle_boom(self)
        Fun.play_sound("Menu confirm")

    # Draw shit
    for x in range(3):
        angle = 120 * x
        pos = Fun.move_with_vel_angle(self.pos, 20, angle)
        entities["particles"].append(Particles.LineParticle(pos, Fun.WHITE, 1, 25, angle, width=2))

        pos = Fun.move_with_vel_angle(self.pos, 40, angle - 60)
        entities["particles"].append(Particles.GrowingSquare((pos[0] - 4, pos[1] - 4, 8, 8), Fun.DARK, [0, 0], 1))

    pos = Fun.move_with_vel_angle(self.pos, 40, 180)
    # Napalm rounds
    entities["particles"].append(Particles.GrowingSquare((pos[0] - 2, pos[1] - 3, 4, 6), Fun.RED, [0, 0], 1))

    pos = Fun.move_with_vel_angle(self.pos, 40, 60)
    entities["particles"].append(Particles.GrowingSquare((pos[0] - 2, pos[1] - 3, 4, 6), Fun.ORANGE, [0, 0], 1))

    pos = Fun.move_with_vel_angle(self.pos, 40, -60)
    entities["particles"].append(Particles.GrowingSquare((pos[0] - 2, pos[1] - 3, 4, 6), Fun.AMBER, [0, 0], 1))

    entities["particles"].append(
        Particles.FloatingTextType2([self.pos[0], self.pos[1] - 48], 18,
                              f'{Fun.write_control(self, "Reload")} {Fun.write_textline("Vivianne guns instruction")}',
                              Fun.UI_COLOUR_TUTORIAL, 1))


def vivianne_rifle_normal(self):
    self.weapon.bullet_type = Bullets.Bullet
    self.weapon.bullets_per_shot = 1
    self.weapon.bullet_info = [self.weapon.bullet_info[0], 60, 3, 14,
                                        {"Piercing": True, "Smoke": False}]
    self.weapon.spread = 2
    self.weapon.range = self.weapon.bullet_info[0] * self.weapon.bullet_info[1]


def vivianne_rifle_flechettes(self):
    self.weapon.bullet_type = Bullets.Flechette
    self.weapon.bullets_per_shot = 3
    self.weapon.bullet_info = [self.weapon.bullet_info[0], 70, 7, 10, {}]
    self.weapon.spread = 6
    self.weapon.range = self.weapon.bullet_info[0] * self.weapon.bullet_info[1]
    # Change that one too


def vivianne_rifle_boom(self):
    self.weapon.bullet_type = Bullets.ExplosionPrimaryType1
    self.weapon.bullets_per_shot = 1
    self.weapon.bullet_info = [self.weapon.bullet_info[0], 50, 3, 8,
                                        {"Secondary explosion": {"Duration": 8, "Growth": 2, "Damage mod": 0.25}}]
    self.weapon.spread = 2
    self.weapon.range = self.weapon.bullet_info[0] * self.weapon.bullet_info[1]


def vivianne_shotgun(self, entities, bullets):
    if self.input["Reload"]:
        self.input["Reload"] = False
        self.reloading = True
        self.no_shoot_state = self.weapon.reload_time * 2
        if 0 <= self.angle <= 120:
            # Normal load
            vivianne_rounds_normal(self)
        elif 0 >= self.angle >= -120:
            # Slug
            vivianne_rounds_slug(self)
        else:
            # Napalm Round
            vivianne_rounds_napalm(self)
        Fun.play_sound("Menu confirm")

    # Draw shit
    for x in range(3):
        angle = 120 * x
        pos = Fun.move_with_vel_angle(self.pos, 20, angle)
        entities["particles"].append(Particles.LineParticle(pos, Fun.WHITE, 1, 25, angle, width=2))

        pos = Fun.move_with_vel_angle(self.pos, 40, angle - 60)
        entities["particles"].append(Particles.GrowingSquare((pos[0] - 4, pos[1] - 4, 8, 8), Fun.DARK, [0, 0], 1))

    pos = Fun.move_with_vel_angle(self.pos, 40, 180)
    # Napalm rounds
    entities["particles"].append(Particles.GrowingSquare((pos[0] - 2, pos[1] - 3, 4, 6), Fun.RED, [0, 0], 1))

    pos = Fun.move_with_vel_angle(self.pos, 40, 60)
    # Normal
    entities["particles"].append(Particles.GrowingSquare((pos[0] - 1, pos[1] - 3, 2, 2), Fun.AMBER, [0, 0], 1))
    entities["particles"].append(Particles.GrowingSquare((pos[0] - 3, pos[1], 2, 2), Fun.AMBER, [0, 0], 1))
    entities["particles"].append(Particles.GrowingSquare((pos[0] + 1, pos[1], 2, 2), Fun.AMBER, [0, 0], 1))

    pos = Fun.move_with_vel_angle(self.pos, 40, -60)
    # Slug
    entities["particles"].append(Particles.GrowingSquare((pos[0] - 2, pos[1] - 3, 4, 6), Fun.GREEN, [0, 0], 1))

    entities["particles"].append(
        Particles.FloatingTextType2([self.pos[0], self.pos[1] - 48], 18,
                              f'{Fun.write_control(self, "Reload")} {Fun.write_textline("Vivianne guns instruction")}',
                              Fun.UI_COLOUR_TUTORIAL, 1))


def vivianne_rounds_normal(self):
    self.weapon.bullet_type = Bullets.Bullet
    self.weapon.bullets_per_shot = 12
    self.weapon.bullet_info = [5, self.weapon.bullet_info[1], 3, 20,
                                        {"Piercing": False, "Smoke": False}]
    self.weapon.spread = 12
    self.weapon.range = self.weapon.bullet_info[0] * self.weapon.bullet_info[1]


def vivianne_rounds_slug(self):
    self.weapon.bullet_type = Bullets.Bullet
    self.weapon.bullets_per_shot = 1
    self.weapon.bullet_info = [9, self.weapon.bullet_info[1], 8, 50,
                                        {"Piercing": True, "Smoke": True}]
    self.weapon.spread = 2
    self.weapon.range = self.weapon.bullet_info[0] * self.weapon.bullet_info[1]


def vivianne_rounds_napalm(self):
    self.weapon.bullet_type = Bullets.Fire
    self.weapon.bullets_per_shot = 18
    self.weapon.bullet_info = [5, self.weapon.bullet_info[1], 7, 14,
                                        {"Particle allowed": True, "Burn chance": 1,
                                                           "Burn duration": 30, "Colour": Fun.FIRE, "On hit": []}]
    self.weapon.spread = 36
    self.weapon.range = self.weapon.bullet_info[0] * self.weapon.bullet_info[1]


def vivianne_leg(self, entities, bullets):
    key_released, weapon_info = melee_system(self, entities, bullets,
                                             basic_attacks=[vivianne_leg_combo_1, vivianne_leg_combo_2],
                                             charged_attack=vivianne_leg_charged,
                                             basic_threshold=5, charged_threshold=60)
    if weapon_info["Press time"] > 0:
        self.aim_angle = self.angle + weapon_info["Press time"] * [2.5, -2.5][weapon_info["Combo stage"]]


def vivianne_leg_combo_1(self, entities, bullets):
    self.aim_angle = self.angle

    pos = Fun.move_with_vel_angle(self.pos, 25, self.aim_angle)
    radius = 32

    Bullets.spawn_bullet(self, entities, Bullets.Melee, pos, self.aim_angle, [0, 6, radius, 10, {}])

    for b in entities["bullets"]:
        if b.team == self.team:
            continue
        if b.laser_based:
            continue
        if Fun.collision_circle_circle(pos, radius, b.pos, b.radius):
            Bullets.spawn_blue_balls(
                self, entities, b.pos.copy(), self.angle,
                [b.og_info[0] * 1.5, b.og_info[1], b.radius * 1.75, b.damage, {"Colour": Fun.DARK_BLUE}])
            b.duration = 0

    for y in range(2):
        for x in range(7):
            angle = self.aim_angle - 5 * 3 + 5 * x + random.uniform(-30, 30)
            entities["particles"].append(Particles.RandomParticle2(
                Fun.move_with_vel_angle(self.pos, 6, angle),
                Fun.WHITE, 4, 15, angle, size=3))

    Fun.play_sound("Hitting 2", "SFX")


def vivianne_leg_combo_2(self, entities, bullets):
    self.aim_angle = self.angle

    pos = Fun.move_with_vel_angle(self.pos, 25, self.aim_angle)
    radius = 32

    Bullets.spawn_bullet(self, entities, Bullets.Melee, pos, self.aim_angle, [0, 6, radius, 10, {}])

    for b in entities["bullets"]:
        if b.team == self.team:
            continue
        if b.laser_based:
            continue
        if Fun.collision_circle_circle(pos, radius, b.pos, b.radius):
            Bullets.spawn_blue_balls(
                self, entities, b.pos.copy(), self.angle,
                [b.og_info[0] * 1.5, b.og_info[1], b.radius * 1.75, b.damage, {"Colour": Fun.DARK_BLUE}])
            b.duration = 0

    for y in range(2):
        for x in range(7):
            angle = self.aim_angle - 5 * 3 + 5 * x + random.uniform(-30, 30)
            entities["particles"].append(Particles.RandomParticle2(
                Fun.move_with_vel_angle(self.pos, 6, angle),
                Fun.WHITE, 4, 15, angle, size=3))

    Fun.play_sound("Hitting 2", "SFX")


def vivianne_leg_charged(self, entities, bullets):
    self.aim_angle = self.angle

    pos = Fun.move_with_vel_angle(self.pos, 25, self.aim_angle)
    radius = 64

    Bullets.spawn_bullet(self, entities, Bullets.Melee, pos, self.aim_angle,
                         [0, 6, radius, 30, {"On hit": [Bullets.on_hit_sun]}])

    for b in entities["bullets"]:
        if b.team == self.team:
            continue
        if b.laser_based:
            continue
        if Fun.collision_circle_circle(pos, radius, b.pos, b.radius):
            Bullets.spawn_blue_balls(
                self, entities, b.pos.copy(), self.angle,
                [b.og_info[0] * 1.5, b.og_info[1], b.radius * 1.75, b.damage, {"Colour": Fun.DARK_BLUE}])
            b.duration = 0
    for y in range(6):
        for x in range(7):
            angle = self.aim_angle - 5 * 3 + 5 * x + random.uniform(-30, 30)
            entities["particles"].append(Particles.RandomParticle2(
                Fun.move_with_vel_angle(self.pos, 6, angle),
                Fun.WHITE, 4, 15, angle, size=3))

    Fun.play_sound("Hitting 3", "SFX")


def vivianne_leg_alt(self, entities, bullets):
    # Drop the weapon
    pos = self.pos.copy()
    Items.spawn_item(entities, "Dropped Weapon", pos.copy(), self=self)
    entities["items"][-1].free_var["Weapon"] = self.weapon
    entities["items"][-1].vel = Fun.move_with_vel_angle([0, 0], 8, self.aim_angle)
    Bullets.spawn_bullet(
        self, entities, Bullets.BulletSlowing, pos, self.aim_angle, [6, 60, 12, 300, {"Damage type": "Melee"}]
    )

    Fun.play_sound("Sword launch")
    self.weapon = BasicWeapon(weapon_repertory["Unarmed"])


def buggy_gun_passive(self, entities, bullets):
    # Fun.move_with_vel_angle(self.pos, 20, self.free_var["Move angle"])
    #  Fun.angle_value_limiter(
    # Fun.angle_value_limiter(self.aim_angle)
    pass


# |Enemy Weapons|-------------------------------------------------------------------------------------------------------
def radar_passive(self, entities, level):
    for b in entities["bullets"]:
        if b.team != self.team: continue
        if Fun.distance_between(b.owner.pos, self.pos) > 128: continue
        if type(b) != Bullets.Missile: continue
        if b.duration != 1 and b.manoeuvrability > 0: continue
        b.manoeuvrability = 0
        b.duration = 30
        b.speed = 6
        b.slowdown_rate = 0.2

        for p in range(2):
            entities["particles"].append(Particles.Smoke(
                Fun.random_point_in_circle(b.pos, 8)))
    # Give visual effect to indicate who benefits


def laser_rifle_passive(self, entities, level):
    variable_handling_rate(self, entities, level, rate=30)


def laser_carbine_passive(self, entities, level):
    variable_handling_rate(self, entities, level, rate=20)


# ARWS
def arws_passive(self, entities, level):
    variable_handling_rate(self, entities, level, rate=40)
    # summons missiles from time to time
    if self.free_var['Startup lag'] > 0 and self.free_var['Startup lag'] % 60 == 0:
        for x in range(2):
            angle = self.aim_angle + [-45, 45][x]
            Bullets.spawn_bullet(
                self, entities,
                Bullets.Missile,
                Fun.move_with_vel_angle(self.pos, 20, angle),
                angle,
                [2 + 3 * random.random(), 180, 4, 3, {"Targeting range": 512,
                                 "Targeting angle": 60,
                                 "Target": "enemies",
                                 "Secondary explosion": {"Duration": 5,
                                                         "Growth": 2,
                                                         "Damage mod": 0.75}}])


def gun_hammer_passive(self, entities, level):
    key_released, weapon_info = melee_system(
        self, entities, level, basic_attacks=[gun_hammer_combo_1],
        charged_attack=none,
        basic_threshold=130, charged_threshold=5000)
    if weapon_info["Press time"] > 0:
        self.aim_angle = self.angle + weapon_info["Press time"]


def gun_hammer_combo_1(self, entities, level):
    Bullets.spawn_bullet(
        self, entities, Bullets.Melee3, Fun.move_with_vel_angle(self.pos, 20, self.angle), self.angle,
        [0, 20, 1, 30, {"Growth": 4, "Damage type": "Physical"}])
    # Needs an effect


def pile_bunker_passive(self, entities, level):
    basic_tres = 90
    key_released, weapon_info = melee_system(
        self, entities, level, basic_attacks=[pile_bunker_combo_1],
        charged_attack=none,
        basic_threshold=basic_tres, charged_threshold=5000)
    # if weapon_info["Press time"] < basic_tres // 2:
    if weapon_info["Press time"] == 0:
        self.status["Stealth"] = 2
    elif weapon_info["Press time"] <= basic_tres // 2:
        self.weapon_draw_dist -= 1
    elif weapon_info["Press time"] >= basic_tres // 2:
        self.weapon_draw_dist = -45
        if weapon_info["Press time"] == basic_tres // 2: Fun.play_sound("Jamming")
        # Noise
        self.vel = [0, 0]
        self.input["Up"] = False
        self.input["Down"] = False
        self.input["Right"] = False
        self.input["Left"] = False
    else:
        if self.weapon_draw_dist > 0:
            self.weapon_draw_dist -= 2
        if self.weapon_draw_dist < 0:
            self.weapon_draw_dist += 2


def pile_bunker_combo_1(self, entities, level):
    Bullets.spawn_bullet(
        self, entities, Bullets.RazorWind, Fun.move_with_vel_angle(self.pos, 20, self.angle), self.angle,
        [5, 20, 32, 100, {"Colour": Fun.WHITE, "Angle modifier": 150, "Segment amount": 1}])
    Fun.play_sound("Pile Bunker Hit")
    self.weapon_draw_dist = 0


def binoculars_passive(self, entities, level):
    for e in entities["entities"]:
        if e.team != self.team: continue
        if Fun.distance_between(e.pos, self.pos) > 320: continue
        if e.target and not e.name == "Artilleryman": continue
        e.target = self.target


def artillery_radio_passive(self, entities, level):
    if self.target and self.no_shoot_state == 0:
        Fun.play_sound("Artillery 1")
        Bullets.spawn_bullet(
            self, entities, Bullets.Artillery, self.target.pos.copy(), self.angle,
            self.weapon.bullet_info)
        self.no_shoot_state = self.weapon.reload_time


def bulwark_passive(self, entities, level):
    rev_up(self, entities, level, rev_up_rate=4, rev_up_target=2)
    variable_handling_rate(self, entities, level, rate=10, min_handle=0.75)


def hover_tank_cannon_passive(self, entities, level):
    self.status["Visible"] = 2
    # if self.vel != [0, 0] and self.time % 8 == 0:
        # Fun.play_sound("Chain click")
    if self.input["Shoot"] and self.weapon.ammo != 0 and self.shot_allowed and self.no_shoot_state == 0:
        self.vel = Fun.move_with_vel_angle(self.vel, -10, self.aim_angle)
        for a in [-15, -7.5, 0, 7.5, 15]:
            for b in range(7):
                Bullets.spawn_bullet(
                    self, entities, Bullets.BulletSlowing,
                    Fun.move_with_vel_angle(self.pos, 32, self.aim_angle+a),
                    self.aim_angle + random.uniform(-8, 8)+a,
                    [5 + 5 * random.random(), 320, 7, 8, {"Piercing": False, "Smoke": False, "Colour": (107, 165, 153),
                                                      "Slowdown rate": random.random() / 3}])

        Fun.play_sound("Hitting 3", "SFX")
        for b in [150, -150]:
            for c in range(1):
                entities["particles"].append(Particles.Smoke(
                        Fun.move_with_vel_angle(self.pos, 28 + 32 * random.random(),
                                                self.free_var["Move angle"] + random.uniform(-16, 16) + b),

                    ))
    # variable_handling_rate(self, entities, level, rate=20, min_handle=0.5)


def attack_helicopter_weaponry_passive(self, entities, level):
    pass
    # self.status["Visible"] = 2
    # if self.vel != [0, 0] and self.time % 8 == 0:
        # Fun.play_sound("Chain click")s
    # variable_handling_rate(self, entities, level, rate=20, min_handle=0.5)


def sardine_passive(self, entities, level):
    if self.time % 90 == 89:
        # Spawn Sardine
        Items.spawn_item(entities, "Sardine", Fun.move_with_vel_angle(self.pos, 20, self.aim_angle), self=self)
        entities["items"][-1].free_var["Angle"] = Fun.angle_between(self.owner.pos, self.pos)
        entities["items"][-1].owner = self.owner


def m_spear(self, entities, level):
    if self.no_shoot_state == 0:
        if self.input["Alt fire"]:
            self.draw_angle += 20
            angle = self.aim_angle + self.draw_angle
            Bullets.spawn_bullet(
                self, entities, Bullets.Bullet, Fun.move_with_vel_angle(self.pos, 60, angle),
                angle, [0, 1, 15, 10, {"Colour": Fun.WHITE}]
            )
            return
        if self.input["Shoot"]:
            self.vel = Fun.move_with_vel_angle([0, 0], 4, self.aim_angle)
            Bullets.spawn_bullet(
                self, entities, Bullets.RazorWind, Fun.move_with_vel_angle(self.pos, 30, self.aim_angle),
                self.aim_angle, [3, 25, 25, 20, {"Angle modifier": 165, "Colour": Fun.WHITE}]
            )
            # sound here
            self.no_shoot_state = self.weapon.fire_rate

    # if self.draw_angle > 0:
    #     self.draw_angle -= 10


def agatha_passive(self, entities, level):
    if self.no_shoot_state != 0:
        return

    if self.input["Alt fire"]:
        self.draw_angle = 90
        self.draw_rotated_dist = 14
        self.weapon_draw_dist = 8
        if self.weapon.free_var["Charge cooldown"] > 0:
            self.weapon.free_var["Charge cooldown"] -= 1
        return
    # self.draw_angle = 0

    key_released, weapon_info = melee_system(self, entities, level,
                                             basic_attacks=[agatha_combo_1,
                                                            agatha_combo_2,
                                                            agatha_combo_3
                                                            ],
                                             charged_attack=Fun.none,
                                             basic_threshold=[32, 32, 96], charged_threshold=200)

    # entities["particles"].append(Fun.LineParticle(self.pos, Fun.GREEN, 1, 6 * 80, self.weapon.free_var["Sword target angle"] + self.angle))

    # allow_angle_change = True
    # if self.weapon.free_var["Angle ref"]:
        # self.aim_angle = self.weapon.free_var["Angle ref"].angle + 90 * self.weapon.free_var["Mod"] - self.weapon.free_var["Angle ref"].angle_deviation * self.weapon.free_var["Mod"] # reverse this on second combo stage
    #     if self.weapon.free_var["Angle ref"].duration == 0:
    #         self.weapon.free_var["Angle ref"] = False
    #     allow_angle_change = False

    # if weapon_info["Press time"] > 0 and not key_released:
    #     if weapon_info["Combo stage"] in [0, 1] and allow_angle_change:
    #         self.draw_angle = weapon_info["Press time"] * [1, -1][weapon_info["Combo stage"]] * 2
            # self.weapon.free_var["Sword target angle"] = weapon_info["Press time"] * [1, -1][weapon_info["Combo stage"]] * 2.5
            # print(self.draw_angle)
    #     if weapon_info["Combo stage"] == 2:
     #        self.weapon_draw_dist = -weapon_info["Press time"] * 0.5


def agatha_combo_1(self, entities, level):
    self.vel = Fun.move_with_vel_angle([0, 0], 2, self.aim_angle + 15)

    # Bullets.spawn_bullet(
    #     self, entities, Bullets.LaserDanmaku2, self.pos, self.aim_angle - 180,
    #     [0, 10, 60, 250, {"Colour": Fun.WHITE, "Angle deviation": deviation, "Damage type": "Melee"}])
    Bullets.spawn_bullet(
        self, entities,
        Bullets.RazorWind,
        Fun.move_with_vel_angle(self.pos, 25, self.aim_angle),
        self.aim_angle,
        [6, 7, 30, 125,
         {"Colour": Fun.WHITE, "Angle modifier": 100, "Segment amount": 1, "Damage type": "Melee"}])
    self.weapon.free_var["Angle ref"] = entities["bullets"][-1]

    Fun.play_sound("Hitting 1", "SFX")


def agatha_combo_2(self, entities, level):
    self.vel = Fun.move_with_vel_angle([0, 0], 2, self.aim_angle - 15)

    # Bullets.spawn_bullet(
    #     self, entities, Bullets.LaserDanmaku2, self.pos, self.aim_angle + 180,
    #     [0, 10, 60, 250, {"Colour": Fun.WHITE, "Angle deviation": deviation, "Damage type": "Melee"}])
    Bullets.spawn_bullet(
        self, entities,
        Bullets.RazorWind,
        Fun.move_with_vel_angle(self.pos, 25, self.aim_angle),
        self.aim_angle,
        [6, 7, 30, 125,
         {"Colour": Fun.WHITE, "Angle modifier": 100, "Segment amount": 1, "Damage type": "Melee"}])
    Fun.play_sound("Hitting 1", "SFX")


def agatha_combo_3(self, entities, level):
    self.vel = Fun.move_with_vel_angle([0, 0], 8, self.aim_angle)
    # self.status["Low friction"] += 25
    # self.weapon_draw_dist = 30
    Bullets.spawn_bullet(
        self, entities,
        Bullets.RazorWind,
        Fun.move_with_vel_angle(self.pos, 25, self.aim_angle),
        self.aim_angle,
        [6, 7, 30, 125,
         {"Colour": Fun.WHITE, "Angle modifier": 100, "Segment amount": 1, "Damage type": "Melee"}])

    Fun.play_sound("Hitting 2")


def azura_passive(self, entities, level):
    if self.input["Dash"] and self.dash_cooldown <= self.dash_charge_time:
        print("Does this shit work")
        Items.spawn_item(entities, "M3-D1C OUT OF MY WAY", self.pos.copy(), self=self)
        entities["items"][-1].life_time = abs(self.dash_cooldown)


AMMO_BAR_SPRITE_SHEET = Fun.get_image("Sprites/UI/Ammo.png")
AMMO_BAR_SPRITES = {
    "Pistol Large": AMMO_BAR_SPRITE_SHEET.subsurface((0, 0, 16, 8)),
    "Pistol Small": AMMO_BAR_SPRITE_SHEET.subsurface((16, 0, 8, 8)),

    "Rifle Large": AMMO_BAR_SPRITE_SHEET.subsurface((0, 8, 32, 8)),
    "Rifle Medium": AMMO_BAR_SPRITE_SHEET.subsurface((32, 8, 24, 8)),
    "Rifle Small": AMMO_BAR_SPRITE_SHEET.subsurface((56, 8, 16, 8)),

    "Rimmed Large": AMMO_BAR_SPRITE_SHEET.subsurface((0, 16, 24, 8)),
    "Rimmed Tapered": AMMO_BAR_SPRITE_SHEET.subsurface((32, 16, 24, 8)),
    "Rimfire": AMMO_BAR_SPRITE_SHEET.subsurface((56, 16, 8, 8)), # Unsused

    "Shotshell Large": AMMO_BAR_SPRITE_SHEET.subsurface((0, 24, 24, 8)),
    "Shotshell Medium": AMMO_BAR_SPRITE_SHEET.subsurface((24, 24, 16, 8)),
    "Shotshell Small": AMMO_BAR_SPRITE_SHEET.subsurface((40, 24, 16, 8)),

    "Lead Ball Large": AMMO_BAR_SPRITE_SHEET.subsurface((0, 32, 8, 8)),
    "Lead Ball Small": AMMO_BAR_SPRITE_SHEET.subsurface((8, 32, 8, 8)),

    "Missile": AMMO_BAR_SPRITE_SHEET.subsurface((0, 40, 16, 8)),
    "Grenade": AMMO_BAR_SPRITE_SHEET.subsurface((16, 40, 16, 8)),
    "Misc": AMMO_BAR_SPRITE_SHEET.subsurface((32, 40, 8, 8)),
    "None": AMMO_BAR_SPRITE_SHEET.subsurface((32, 40, 1, 1)),
}
# |Weapon Repertories|--------------------------------------------------------------------------------------------------
weapon_repertory = {
    # |THR-1|-----------------------------------------------------------------------------------------------------------
    # |Lord|------------------------------------------------------------------------------------------------------------
    "Saloum Mk-2":
        {"name": "Saloum Mk-2",
         "ammo sprite": "Missile",
         "class": "Rocket Launcher",
         "sprite": "Sprites/Weapon/THR-1/Saloum Mk-2.png",
         "gunshot sound": "Rocket launcher",
         "reloading sound": "Reload Pistol 1",
         "jamming sound": "Jamming",
         "sound level": 1,
         "accuracy": 3,
         "spread": 2,
         "handle": 5,
         "recoil": 50,
         "full auto": True,
         "fire rate": 15,
         "reload time": 60,
         "bullet type": "Missile",
         "bullets per shot": 1,
         "ammo cost": 1,
         "bullet info": [8, 80, 4, 80, {"Targeting range": 200,
                                        "Targeting angle": 25,
                                        "Manoeuvrability": 8,
                                        "Target": "enemies",
                                        "Secondary explosion": {"Duration": 10,
                                                                "Growth": 4,
                                                                "Damage mod": 1}}],
         "max ammo": 3,
         "ammo pool": 80,
         "crit rate": 0,
         "crit multiplier": 1.5,
         "jam rate": 0,
         "jam duration": 0,
         "laser sight": False,
         "alt fire": "none",
         "passive": "missile_launcher_passive",
         "agro": 4},
    "GMG-04B":
        {"name": "GMG-04B",
         "ammo sprite": "Grenade",
         "class": "Throwable",
         "sprite": "Sprites/Weapon/THR-1/GMG-04B.png",
         "gunshot sound": "Small arms",
         "reloading sound": "Reload Pistol 1",
         "jamming sound": "Jamming",
         "sound level": 0.5,
         "accuracy": 3,
         "spread": 2,
         "handle": 8,
         "recoil": 50,
         "full auto": True,
         "fire rate": 25,
         "reload time": 180,
         "bullet type": "Grenade",
         "bullets per shot": 1,
         "ammo cost": 1,
         "bullet info": [6, 100, 4, 50, {"Secondary explosion": {"Duration": 5,
                                                                 "Growth": 10,
                                                                 "Damage mod": 1}}],
         "max ammo": 32,
         "ammo pool": 256,
         "crit rate": 0,
         "crit multiplier": 1,
         "jam rate": 0,
         "jam duration": 0,
         "laser sight": False,
         "alt fire": "none",
         "passive": "none"},
    "Big Iron":
        {"name": "Big Iron",
         "ammo sprite": "Rimmed Large",
         "class": "Revolver",
         "sprite": "Sprites/Weapon/THR-1/Big iron.png",
         "gunshot sound": "Revolver shoot",
         "reloading sound": "Revolver reload",
         "jamming sound": "Jamming",
         "sound level": 1,
         "accuracy": 0,
         "spread": 0,
         "handle": 5,
         "recoil": 100,
         "full auto": False,
         "fire rate": 30,
         "reload time": 35,
         "Reload style": "One at a time",
         "bullet type": "ExplosionPrimaryType1",
         "bullets per shot": 1,
         "ammo cost": 1,
         "bullet info": [12, 200, 8, 100, {"Secondary explosion": {"Duration": 8,
                                                                 "Growth": 6,
                                                                 "Damage mod": 1},
                                           "On hit": [Bullets.on_hit_big_iron]}],
         "max ammo": 5,
         "ammo pool": 100,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0.005,
         "jam duration": 10,
         "laser sight": False,
         "alt fire": "big_iron_alt",
         "passive": "none"},
    # |Emperor|---------------------------------------------------------------------------------------------------------
    "GunBlade":
        {"name": "GunBlade",
         "ammo sprite": "Pistol Large",
         "class": "Slash",
         "sprite": "Sprites/Weapon/THR-1/GunBlade.png",
         "gunshot sound": "Silence",
         "reloading sound": "Silence",
         "jamming sound": "Silence",
         "sound level": 0,
         "accuracy": 0,
         "spread": 0,
         "handle": 4,
         "recoil": 0,
         "full auto": False,
         "fire rate": 0,
         "reload time": 10,
         "bullet type": "Melee",
         "bullets per shot": 0,
         "ammo cost": 0,
         "bullet info": [96, 1, 20, 30, {}],
         "max ammo": 7,
         "ammo pool": 140,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0,
         "jam duration": 0,
         "laser sight": True,
         "alt fire": "none",
         "passive": "gunblade"},
    "Corrine's Old Rifle":
        {"name": "Corrine's Old Rifle",
         "ammo sprite": "Rifle Medium",
         "class": "Rifle",
         "sprite": "Sprites/Weapon/THR-1/Corrine's Old Rifle.png",
         "gunshot sound": "Rifle",
         "reloading sound": "Reload Pistol 1",
         "jamming sound": "Jamming",
         "sound level": 0.9,
         "accuracy": 5,
         "spread": 3,
         "handle": 8,
         "recoil": 50,
         "full auto": False,
         "fire rate": 20,
         "reload time": 60,
         "bullet type": "Bullet",
         "bullets per shot": 1,
         "ammo cost": 1,
         "bullet info": [7, 80, 5, 25, {"Piercing": True, "On hit": [Bullets.on_hit_weaken]}],
         "max ammo": 10,
         "ammo pool": 200,
         "crit rate": 0,
         "crit multiplier": 2.5,
         "jam rate": 0.05,
         "jam duration": 10,
         "laser sight": False,
         "alt fire": "none",
         "passive": "none"},
    "Oversized stun baton":
        {"name": "Oversized stun baton",
         "ammo sprite": "None",
         "class": "Slash",
         "sprite": "Sprites/Weapon/THR-1/Oversized stun baton.png",
         "gunshot sound": "Silence",
         "reloading sound": "Silence",
         "jamming sound": "Silence",
         "sound level": 0,
         "accuracy": 0,
         "spread": 0,
         "handle": 4,
         "recoil": 0,
         "full auto": False,
         "fire rate": 0,
         "reload time": 10,
         "bullet type": "Melee",
         "bullets per shot": 0,
         "ammo cost": 0,
         "bullet info": [96, 1, 20, 30, {}],
         "max ammo": 7,
         "ammo pool": 140,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0,
         "jam duration": 0,
         "laser sight": False,
         "alt fire": "none",
         "passive": "stun_baton"},
    # |Wizard|----------------------------------------------------------------------------------------------------------
    "Jeanne's Family Shotgun":
        {"name": "Jeanne's Family Shotgun",
         "ammo sprite": "Shotshell Large",
         "class": "Shotgun",
         "sprite": "Sprites/Weapon/THR-1/Jeanne Gun.png",
         "gunshot sound": "Shotgun 1 Shooting",
         "reloading sound": "Reload Pistol 1",
         "jamming sound": "Jamming",
         "sound level": 0.86,
         "accuracy": 4,
         "spread": 20,
         "handle": 6,
         "recoil": 60,
         "full auto": True,
         "fire rate": 20,
         "reload time": 35,
         "bullet type": "Bullet",
         "bullets per shot": 10,
         "ammo cost": 1,
         "bullet info": [5.4, 35, 3, 40, {"Piercing": True, "Smoke": False}],
         "max ammo": 10,
         "ammo pool": 150,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0.05,
         "jam duration": 10,
         "laser sight": False,
         "alt fire": "none",
         "passive": "jeanne_shotgun_passive"},
    "Custom Mk18 Laser cutter":
        {"name": "Custom Mk18 Laser cutter",
         "ammo sprite": "Misc",
         "class": "Rifle",
         "sprite": "Sprites/Weapon/THR-1/Custom Mk18 Laser cutter.png",
         "gunshot sound": "Skill 3",
         "reloading sound": "Reload Enemy 1",
         "jamming sound": "Reload Enemy 1",
         "sound level": 0,
         "accuracy": 0,
         "spread": 0,
         "handle": 0.5,
         "recoil": 0,
         "full auto": True,
         "fire rate": 0,
         "reload time": 60,
         "bullet type": "Laser",
         "bullets per shot": 1,
         "ammo cost": 1,
         "bullet info": [0, 12, 96, 70, {"Colour": Fun.LIGHT_BLUE, "Damage type": "Melee"}],
         "max ammo": 120,
         "ammo pool": 6000,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0,
         "jam duration": 10,
         "laser sight": True,
         "alt fire": "laser_cutter_alt",
         "passive": "laser_cutter_passive", "free var": {"Charged shot": 0}},
    "Crippled Laddie FCS Radio":
        {"name": "Crippled Laddie FCS Radio",
         "ammo sprite": "Misc",
         "class": "Rifle",
         "sprite": "Sprites/Weapon/THR-1/Crippled Laddie FCS Radio.png",
         "gunshot sound": "Silence",
         "reloading sound": "Silence",
         "jamming sound": "Silence",
         "sound level": 0,
         "accuracy": 0,
         "spread": 0,
         "handle": 0.5,
         "recoil": 0,
         "full auto": True,
         "fire rate": 0,
         "reload time": 240,
         "bullet type": "Artillery",
         "bullets per shot": 0,
         "ammo cost": 0,
         "bullet info": [0, 90, 96, 50, {"Secondary explosion":{"Duration": 10, "Strength": 120, "Radius":128}, "Colour": Fun.RED}],
         "max ammo": 5,
         "ammo pool": 100,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0,
         "jam duration": 10,
         "laser sight": False,
         "range": 512,
         "alt fire": "radio_alt",
         "passive": "radio_passive",
         "free var": {"Switch cooldown": 0, "Ammo": 0}},
    # |Sovereign|-------------------------------------------------------------------------------------------------------
    "St-Maurice":
        {"name": "St-Maurice",
         "ammo sprite": "Rifle Medium",
         "class": "Rifle",
         "sprite": "Sprites/Weapon/THR-1/St-Maurice.png",
         "gunshot sound": "Gun Silenced",
         "reloading sound": "Reload Pistol 1",
         "jamming sound": "Jamming",
         "sound level": 0.1,
         "accuracy": 5,
         "spread": 3,
         "handle": 7,
         "recoil": 90,
         "full auto": False,
         "fire rate": 20,
         "reload time": 100,
         "bullet type": "Bullet",
         "bullets per shot": 1,
         "ammo cost": 1,
         "bullet info": [9, 55, 5, 50, {"Piercing": True, "Smoke": False}],
         "max ammo": 5,
         "ammo pool": 200,
         "crit rate": 0,
         "crit multiplier": 2.5,
         "jam rate": 0.05,
         "jam duration": 10,
         "laser sight": False,
         "alt fire": "st_maurice_alt",
         "passive": "none"},
    "St-Laurent Gen 1":
        {"name": "St-Laurent Gen 1",
         "ammo sprite": "Rifle Large",
         "class": "Rifle",
         "sprite": "Sprites/Weapon/THR-1/St-Laurent Gen 1.png",
         "gunshot sound": "Rifle 2",
         "reloading sound": "Reload Rifle 1",
         "jamming sound": "Jamming",
         "sound level": 4,
         "accuracy": 0,
         "spread": 0,
         "handle": 2,
         "recoil": 200,
         "full auto": False,
         "fire rate": 45,
         "reload time": 120,
         "bullet type": "Bullet",
         "bullets per shot": 1,
         "ammo cost": 1,
         "bullet info": [8, 100, 8, 300, {"Piercing": True, "Smoke": True}],
         "max ammo": 1,
         "ammo pool": 100,
         "crit rate": 0,
         "crit multiplier": 1,
         "jam rate": 0.05,
         "jam duration": 15,
         "laser sight": False,
         "alt fire": "st_laurent_alt",
         "passive": "st_laurent_passive",
         "agro": 50},
    "Unarmed":
        {"name": "Unarmed",
         "ammo sprite": "None",
         "class": "Fist",
         "sprite": "Sprites/Weapon/THR-1/Corrine's Fists.png",
         "gunshot sound": "Silence",
         "reloading sound": "Silence",
         "jamming sound": "Silence",
         "sound level": 0,
         "accuracy": 0,
         "spread": 0,
         "handle": 25,
         "recoil": 0,
         "full auto": False,
         "fire rate": 3,
         "reload time": 1,
         "bullet type": "Melee",
         "bullets per shot": 0,
         "ammo cost": 0,
         "bullet info": [5, 2, 20, 5, {"Start sound": "Melee miss 1"}],
         "max ammo": 1,
         "ammo pool": 0,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0,
         "jam duration": 0,
         "laser sight": False,
         "alt fire": "none",
         "passive": "unarmed_passive"},
    "Mk16 Flare Mortar":
        {"name": "Mk16 Flare Mortar",
         "ammo sprite": "Misc",
         "class": "Rifle",
         "sprite": "Sprites/Weapon/THR-1/Mk16 Flare Mortar.png",
         "gunshot sound": "Silence",
         "reloading sound": "Silence",
         "jamming sound": "Silence",
         "sound level": 0,
         "accuracy": 0,
         "spread": 0,
         "handle": 0.5,
         "recoil": 0,
         "full auto": True,
         "fire rate": 0,
         "reload time": 60,
         "bullet type": "Artillery",
         "bullets per shot": 0,
         "ammo cost": 0,
         "bullet info": [0, 45, 48, 50, {"Secondary explosion":{"Duration": 10, "Strength": 120, "Radius": 64}, "Colour": Fun.RED}],
         "max ammo": 1,
         "ammo pool": 100,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0,
         "jam duration": 10,
         "laser sight": False,
         "range": 512,
         "alt fire": "flare_mortar_alt",
         "passive": "flare_mortar_passive",
         "free var": {}},
    # |Duke|------------------------------------------------------------------------------------------------------------
    "Chain Axe":
        {"name": "Chain Axe",
         "ammo sprite": "None",
         "class": "Fist",
         "sprite": "Sprites/Weapon/THR-1/Chain Axe - handle.png",
         "gunshot sound": "Silence",
         "reloading sound": "Silence",
         "jamming sound": "Silence",
         "sound level": 0,
         "accuracy": 0,
         "spread": 0,
         "handle": 25,
         "recoil": 0,
         "full auto": False,
         "fire rate": 3,
         "reload time": 1,
         "bullet type": "Melee",
         "bullets per shot": 0,
         "ammo cost": 0,
         "bullet info": [5, 2, 20, 5, {"Start sound": "Melee miss 1"}],
         "max ammo": 1,
         "ammo pool": 0,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0,
         "jam duration": 0,
         "laser sight": False,
         "alt fire": "none",
         "passive": "ax_chain_passive",
         "free var": {
             "Press time": 0,
             "Axe pos": [0, 0],
             "Target pos": [0, 0],
             "old charge time": 0
         }},
    "Hook Swords":
        {"name": "Hook Swords",
         "ammo sprite": "None",
         "class": "Slash",
         "sprite": "Sprites/Weapon/THR-1/Hook Sword.png",
         "gunshot sound": "Silence",
         "reloading sound": "Silence",
         "jamming sound": "Silence",
         "sound level": 0,
         "accuracy": 0,
         "spread": 0,
         "handle": 4,
         "recoil": 0,
         "full auto": False,
         "fire rate": 0,
         "reload time": 10,
         "bullet type": "Melee",
         "bullets per shot": 0,
         "ammo cost": 0,
         "bullet info": [96, 1, 20, 30, {}],
         "max ammo": 7,
         "ammo pool": 140,
         "range": 256,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0,
         "jam duration": 0,
         "laser sight": False,
         "alt fire": "none",
         "passive": "hook_sword",
         "free var": {"Victim": False, "Second sword dist": 0}},
    "Gun and Ballistic Knife":
        {"name": "Gun and Ballistic Knife",
         "ammo sprite": "Pistol Small",
         "class": "Slash",
         "sprite": "Sprites/Weapon/THR-1/Gun Fu.png",
         "gunshot sound": "Silence",
         "reloading sound": "Silence",
         "jamming sound": "Silence",
         "sound level": 0.2,
         "accuracy": 6,
         "spread": 3,
         "handle": 12,
         "recoil": 5,
         "full auto": False,
         "fire rate": 2,
         "reload time": 10,
         "bullet type": "Bullet",
         "bullets per shot": 1,
         "ammo cost": 1,
         "bullet info": [8, 35, 3, 24, {}],
         "max ammo": 80,
         "ammo pool": 2000,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0,
         "jam duration": 0,
         "laser sight": False,
         "alt fire": "knife_pistol_alt",
         "passive": "knife_pistol_passive",
         "free var": {"Charge time": 0, "Knife Angle": 0}},
    # |Jester|----------------------------------------------------------------------------------------------------------
    "Epicurean Medic Rifle":
        {"name": "Epicurean Medic Rifle",
         "ammo sprite": "Grenade",
         "class": "Semi-auto",
         "sprite": "Sprites/Weapon/THR-1/Epicurean Medic Rifle.png",
         "gunshot sound": "Small arms",
         "reloading sound": "Reload Pistol 1",
         "jamming sound": "Jamming",
         "sound level": 0.8,
         "accuracy": 3,
         "spread": 2,
         "handle": 6,
         "recoil": 100,
         "full auto": True,
         "fire rate": 20,
         "reload time": 100,
         "bullet type": "GrenadeType7",
         "bullets per shot": 1,
         "ammo cost": 1,
         "bullet info": [5, 120, 4, 10, {"Secondary explosion": {"Radius": 32, "No Debuff": False}, "Colour": Fun.LIGHT_GREEN}],
         "max ammo": 30,
         "ammo pool": 90,
         "crit rate": 0,
         "crit multiplier": 1,
         "jam rate": 0,
         "jam duration": 0,
         "laser sight": False,
         "alt fire": "medic_rifle_alt",
         "passive": "none"},
    "Nihilist Stretcher":
        {"name": "Nihilist Stretcher",
         "ammo sprite": "None",
         "class": "Flame",
         "sprite": "Sprites/Weapon/THR-1/Nihilist Stretcher.png",
         "gunshot sound": "Silence",
         "reloading sound": "Silence",
         "jamming sound": "Silence",
         "sound level": 0,
         "accuracy": 0,
         "spread": 0,
         "handle": 8,
         "recoil": 0,
         "full auto": True,
         "fire rate": 0,
         "reload time": 0,
         "bullet type": "Fire",
         "bullets per shot": 0,
         "ammo cost": 0,
         "bullet info": [0, 0, 0, 0, {"Particle allowed": True, "Burn chance": 0.25, "Burn duration": 30,
                                       "Colour": Fun.RED}],
         "max ammo": 1,
         "ammo pool": 0,
         "crit rate": 0,
         "crit multiplier": 0,
         "jam rate": 0,
         "jam duration": 0,
         "range": 40,
         "laser sight": False,
         "alt fire": "none",
         "passive": "stretcher_passive",
         "free var": {"Victim": False, "input func": none, "team": False}},
    "Stoic Shield generator":
        {"name": "Stoic Shield generator",
         "ammo sprite": "Misc",
         "class": "Semi-auto",
         "sprite": "Sprites/Weapon/THR-1/Shield Generator.png",
         "gunshot sound": "Small arms",
         "reloading sound": "Reload Pistol 1",
         "jamming sound": "Jamming",
         "sound level": 0.8,
         "accuracy": 0,
         "spread": 0,
         "handle": 5,
         "recoil": 0,
         "full auto": True,
         "fire rate": 1,
         "reload time": 100,
         "bullet type": "GrenadeType7",
         "bullets per shot": 0,
         "ammo cost": 1,
         "bullet info": [5, 120, 4, 10, {"Secondary explosion": {"Radius": 32, "No Debuff": False}, "Colour": Fun.LIGHT_GREEN}],
         "max ammo": 160,
         "ammo pool": 0,
         "crit rate": 0,
         "crit multiplier": 1,
         "jam rate": 0,
         "jam duration": 0,
         "laser sight": False,
         "alt fire": "none",
         "passive": "shield_generator_passive"},
    # |Condor|----------------------------------------------------------------------------------------------------------
    "Type 41 SMG":
        {"name": "Type 41 SMG",
         "ammo sprite": "Pistol Small",
         "class": "Semi-auto",
         "sprite": "Sprites/Weapon/THR-1/Type 41 SMG.png",
         "gunshot sound": "Rifle 1 Shooting",
         "reloading sound": "Reload Pistol 1",
         "jamming sound": "Jamming",
         "sound level": 0.7,
         "accuracy": 10,
         "spread": 8,
         "handle": 8,
         "recoil": 45,
         "full auto": True,
         "fire rate": 2,
         "reload time": 55,
         "bullet type": "Bullet",
         "bullets per shot": 2,
         "ammo cost": 2,
         "bullet info": [8, 35, 3, 8, {"Piercing": False, "Smoke": False}],
         "max ammo": 60,
         "ammo pool": 1200,
         "crit rate": 0,
         "crit multiplier": 1,
         "jam rate": 0,
         "jam duration": 0,
         "laser sight": False,
         "alt fire": "none",
         "passive": "condor_dual_smg_passive"},
    "Type 23 Shotgun":
        {"name": "Type 23 Shotgun",
         "ammo sprite": "Shotshell Large",
         "class": "Shotgun",
         "sprite": "Sprites/Weapon/THR-1/Type 23 Shotgun.png",
         "gunshot sound": "Shotgun 2 Shooting",
         "reloading sound": "Reload Pistol 1",
         "jamming sound": "Jamming",
         "sound level": 1,
         "accuracy": 4,
         "spread": 12,
         "handle": 4,
         "recoil": 50,
         "full auto": True,
         "fire rate": 15,
         "reload time": 60 / 10,
         "Reload style": "Partial",
         "bullet type": "Bullet",
         "bullets per shot": 8,
         "ammo cost": 1,
         "bullet info": [8, 30, 5, 20, {"Piercing": False, "Smoke": False}],
         #
         #
         # "spread": 24,
         # "handle": 6,
         # "recoil": 60,
         # "bullets per shot": 10,
         # "bullet info": [6, 15, 3, 40, {"Piercing": True, "Smoke": False}],
         #
         "max ammo": 10,
         "ammo pool": 200,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0.075,
         "jam duration": 15,
         "laser sight": False,
         "alt fire": "riot_shotgun_alt",
         "passive": "riot_shotgun_passive",
         "free var": {"Charge cooldown": 0}},
    "Type 47 Rifle":
        {"name": "Type 47 Rifle",
         "ammo sprite": "Rifle Small",
         "class": "Semi-auto",
         "sprite": "Sprites/Weapon/THR-1/Type 47 Rifle.png",
         "gunshot sound": "Small arms",
         "reloading sound": "Reload Pistol 1",
         "jamming sound": "Jamming",
         "sound level": 0.8,
         "accuracy": 1,
         "spread": 1,
         "handle": 6,
         "recoil": 40,
         "full auto": True,
         "fire rate": 2,
         "reload time": 50,
         "bullet type": "Flechette",
         "bullets per shot": 1,
         "ammo cost": 1,
         "bullet info": [8, 70, 8, 15, {}],
         "max ammo": 30,
         "ammo pool": 300,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0.0025,
         "jam duration": 10,
         "laser sight": False,
         "alt fire": "none",
         "passive": "three_round_burst"},
    # |Fortress|--------------------------------------------------------------------------------------------------------
    "Fortress Machine Gun":
        {"name": "Fortress Machine Gun",
         "ammo sprite": "Rifle Large",
         "class": "Semi-auto",
         "sprite": "Sprites/Weapon/Anime.png",
         "gunshot sound": "Rifle 1 Shooting",
         "reloading sound": "Reload Enemy 1",
         "jamming sound": "Reload Enemy 1",
         "sound level": 0,
         "accuracy": 2,
         "spread": 4,
         "handle": 3,
         "recoil": 0,
         "full auto": True,
         "fire rate": 8,
         "reload time": 100,
         "bullet type": "Bullet",
         "bullets per shot": 1,
         "ammo cost": 1,
         "bullet info": [7, 50, 3, 50, {"Piercing": False, "Smoke": False}],
         "max ammo": 100,
         "ammo pool": 25000,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0,
         "jam duration": 0,
         "laser sight": False,
         "alt fire": "fortress_alt",
         "passive": "fortress_passive",
         "agro": 6},
    # |Curtis|----------------------------------------------------------------------------------------------------------
    "Standard Shotgun":
        {"name": "Standard Shotgun",
         "ammo sprite": "Shotshell Medium",
         "class": "Shotgun",
         "sprite": "Sprites/Weapon/Standard Shotgun.png",
         "gunshot sound": "Shotgun 1 Shooting",
         "reloading sound": "Reload Pistol 1",
         "jamming sound": "Jamming",
         "sound level": 0.7,
         "accuracy": 4,
         "spread": 30,
         "handle": 8,
         "recoil": 50,
         "full auto": False,
         "fire rate": 20,
         "reload time": 60 // 8,
         "Reload style": "Partial",
         "bullet type": "Bullet",
         "bullets per shot": 10,
         "ammo cost": 1,
         "bullet info": [4, 35, 3, 20, {"Piercing": False, "Smoke": False}],
         "max ammo": 8,
         "ammo pool": 200,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0.05,
         "jam duration": 10,
         "laser sight": False,
         "alt fire": "standard_shotgun_alt",  # ??????
         "passive": "standard_shotgun_passive",
         "agro": 5},
    "Cowboy's Repeater":
        {"name": "Cowboy's Repeater",
         "ammo sprite": "Rimmed Tapered",
         "class": "Rifle",
         "sprite": "Sprites/Weapon/Cowboy Repeater.png",
         "gunshot sound": "Rifle 1 Shooting",
         "reloading sound": "Reload Pistol 1",
         "jamming sound": "Jamming",
         "sound level": 0.7,
         "accuracy": 8,
         "spread": 3,
         "handle": 13,
         "recoil": 50,
         "full auto": False,
         "fire rate": 25,
         "reload time": 15,
         "Reload style": "Partial",
         "bullet type": "Bullet",
         "bullets per shot": 1,
         "ammo cost": 1,
         "bullet info": [9.4, 60, 5, 35, {"Piercing": False, "Smoke": False}],
         "max ammo": 8,
         "ammo pool": 200,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0.0125,
         "jam duration": 30,
         "laser sight": False,
         "alt fire": "cowboy_repeater_alt",
         "passive": "cowboy_repeater_passive",
         "agro": 5,
         "free var": {
             "Targets": [],
             "Gauge": 0
         }
         },
    "War and Peace":
        {"name": "War and Peace",
         "ammo sprite": "Pistol Large",
         "class": "Pistol",
         "sprite": "Sprites/Weapon/Peace.png",
         "gunshot sound": "Small arms",
         "reloading sound": "Reload Pistol 1",
         "jamming sound": "Jamming",
         "sound level": 1,
         "accuracy": 5,
         "spread": 2,
         "handle": 2,
         "recoil": 0,
         "full auto": True,
         "fire rate": 8,
         "reload time": 20,
         "bullet type": "Bullet",
         "bullets per shot": 2,
         "ammo cost": 1,
         "bullet info": [8, 20, 3, 30, {"Piercing": True}],
         "max ammo": 14,
         "ammo pool": 20000,
         "crit rate": 0,
         "crit multiplier": 5,
         "jam rate": 0.01,
         "jam duration": 10,
         "laser sight": False,
         "alt fire": "war_and_peace_alt",
         "passive": "war_and_peace_passive",
         "free var": {"War angle": 0}},
    "Hunk of Steel":
        {"name": "Hunk of Steel",
         "ammo sprite": "None",
         "class": "Blunt",
         "sprite": "Sprites/Weapon/Hunk of Steel.png",
         "gunshot sound": "Silence",
         "reloading sound": "Silence",
         "jamming sound": "Silence",
         "sound level": 0,
         "accuracy": 0,
         "spread": 0,
         "handle": 6,
         "recoil": 0,
         "full auto": True,
         "fire rate": 0,
         "reload time": 1,
         "bullet type": "Melee",
         "bullets per shot": 0,
         "ammo cost": 0,
         "bullet info": [0, 2, 25, 70, {}],
         "range": 256,
         "max ammo": 1,
         "ammo pool": 0,
         "crit rate": 0.25,
         "crit multiplier": 2,
         "jam rate": 0,
         "jam duration": 0,
         "laser sight": False,
         "alt fire": "hunk_of_steel_alt",
         "passive": "hunk_of_steel_passive",
         "free var": {"Angle ref": False, "Mod": 1, "Charge cooldown": 0}},
    # |Lawrence|--------------------------------------------------------------------------------------------------------
    "Lawrence's Cutlass & Flintlock":
        {"name": "Lawrence's Cutlass & Flintlock",
         "ammo sprite": "Lead Ball Large",
         "class": "Melee ",
         "sprite": "Sprites/Weapon/Son's Cutlass.png",
         "gunshot sound": "Silence",
         "reloading sound": "Silence",
         "jamming sound": "Silence",
         "sound level": 0,
         "accuracy": 0,
         "spread": 0,
         "handle": 4,
         "recoil": 0,
         "full auto": True,
         "fire rate": 0,
         "reload time": 1,
         "bullet type": "Melee",
         "bullets per shot": 0,
         "ammo cost": 0,
         "bullet info": [160, 1, 20, 0, {"Colour": Fun.LIGHT_BLUE}],
         "max ammo": 1,
         "ammo pool": 0,
         "crit rate": 0,
         "crit multiplier": 0,
         "jam rate": 0,
         "jam duration": 0,
         "laser sight": False,
         "alt fire": "none",
         "passive": "cutlass_flintlock",
         "agro": 2,
         "free var": {"Colour": Fun.LIGHT_BLUE}},
    "Captain's Axe & Blunderbuss":
        {"name": "Captain's Axe & Blunderbuss",
         "ammo sprite": "Lead Ball Large",
         "class": "Melee ",
         "sprite": "Sprites/Weapon/Boarding Axe.png",
         "gunshot sound": "Silence",
         "reloading sound": "Silence",
         "jamming sound": "Silence",
         "sound level": 0,
         "accuracy": 0,
         "spread": 0,
         "handle": 4,
         "recoil": 0,
         "full auto": True,
         "fire rate": 0,
         "reload time": 1,
         "bullet type": "Melee",
         "bullets per shot": 0,
         "ammo cost": 0,
         "bullet info": [160, 1, 20, 0, {"Colour": Fun.FIRE}],
         "max ammo": 1,
         "ammo pool": 0,
         "crit rate": 0,
         "crit multiplier": 0,
         "jam rate": 0,
         "jam duration": 0,
         "laser sight": False,
         "alt fire": "none",
         "passive": "axe_blunderbuss",
         "agro": 2,
         "free var": {"Colour": Fun.FIRE}},
    "Musket .360":
        {"name": "Musket .360",
         "ammo sprite": "Lead Ball Small",
         "class": "Rifle",
         "sprite": "Sprites/Weapon/Musket .360.png",
         "gunshot sound": "Silence",
         "reloading sound": "Silence",
         "jamming sound": "Silence",
         "sound level": 0.0,
         "accuracy": 5,
         "spread": 5,
         "handle": 10,
         "recoil": 0,
         "full auto": True,
         "fire rate": 0,
         "reload time": 35,
         "bullet type": "Bullet",
         "bullets per shot": 0,
         "ammo cost": 0,
         "bullet info": [8, 80, 7, 40, {"Piercing": True, "Smoke": True}],
         "max ammo": 1,
         "ammo pool": 100,
         "crit rate": 0,
         "crit multiplier": 2,
         "Reload style": "One at a time",
         "jam rate": 0.05,
         "jam duration": 10,
         "laser sight": False,
         "alt fire": "none",
         "passive": "musket_360",
         "free var": {"Colour": Fun.LIGHT_GREEN}},
    # |Mark|------------------------------------------------------------------------------------------------------------
    "Mark's Rifle":
        {"name": "Mark's Real Rifle",
         "ammo sprite": "Rifle Medium",
         "class": "Rifle",
         "sprite": "Sprites/Weapon/Mark's Real Rifle.png",
         "gunshot sound": "Gun Silenced",
         "reloading sound": "Reload Rifle 1",
         "jamming sound": "Jamming",
         "sound level": 0.25,
         "accuracy": 1.98,
         "spread": 1,
         "handle": 8.64,
         "recoil": 20,
         "full auto": False,
         "fire rate": 20,
         "reload time": 60,
         "bullet type": "Bullet",
         "bullets per shot": 1,
         "ammo cost": 1,
         "bullet info": [9.31, 100, 3, 40, {"Piercing": True, "Smoke": False}],
         "max ammo": 10,
         "ammo pool": 100,
         "crit rate": 0,
         "crit multiplier": 1,
         "jam rate": 0.001,
         "jam duration": 10,
         "laser sight": False,
         "alt fire": "mark_rifle_alt",
         "passive": "none"},
    "Type 30 Rifle":
        {"name": "Type 30 Rifle",
         "ammo sprite": "Rifle Medium",
         "class": "Semi-auto",
         "sprite": "Sprites/Weapon/Type 30 Rifle.png",
         "gunshot sound": "Small arms",
         "reloading sound": "Reload Pistol 1",
         "jamming sound": "Jamming",
         "sound level": 0.8,
         "accuracy": 0.5,
         "spread": 0.25,
         "handle": 6,
         "recoil": 20,
         "full auto": True,
         "fire rate": 6,
         "reload time": 50,
         "bullet type": "Bullet",
         "bullets per shot": 1,
         "ammo cost": 1,
         "bullet info": [8, 90, 3.33, 10, {"On hit": [Bullets.on_hit_weaken]}],
         "max ammo": 30,
         "ammo pool": 300,
         "crit rate": 0,
         "crit multiplier": 3,
         "jam rate": 0.0025,
         "jam duration": 10,
         "laser sight": False,
         "alt fire": "none",
         "passive": "none"},
    "C4":
        {"name": "C4",
         "ammo sprite": "Misc",
         "description": "",
         "class": "Throwable",
         "sprite": "Sprites/Weapon/C4.png",
         "gunshot sound": "Small arms",
         "reloading sound": "Reload Pistol 1",
         "jamming sound": "Jamming",
         "sound level": 0.5,
         "accuracy": 3,
         "spread": 4,
         "handle": 12,
         "recoil": 36,
         "full auto": False,
         "fire rate": 5,
         "reload time": 60,
         "bullet type": "C4",
         "bullets per shot": 1,
         "ammo cost": 1,
         "bullet info": [2, 6000, 4, 100, {"Secondary explosion": {"Duration": 12,
                                                                   "Growth": 8,
                                                                  "Damage mod": 1}}],
         "max ammo": 10,
         "ammo pool": 200,
         "crit rate": 0,
         "crit multiplier": 1,
         "jam rate": 0,
         "jam duration": 0,
         "laser sight": False,
         "alt fire": "none",
         "passive": "c4_passive",
         "agro": 4,
         "free var": {"C4 out": []}},
    # |Viviane|---------------------------------------------------------------------------------------------------------
    "Vivianne's Rifle":
        {"name": "Vivianne's Rifle",
         "ammo sprite": "Rifle Medium",
         "class": "?????",
         "sprite": "Sprites/Weapon/Vivianne Rifle.png",
         "gunshot sound": "Rifle 1 Shooting",
         "reloading sound": "Reload Pistol 1",
         "jamming sound": "Jamming",
         "sound level": 0.7,
         "accuracy": 2,
         "spread": 2,
         "handle": 6,
         "recoil": 20,
         "full auto": True,
         "fire rate": 10,
         "reload time": 70,
         "bullet type": "Bullet",
         "bullets per shot": 1,
         "ammo cost": 1,
         "bullet info": [6.5, 50, 3, 14, {"Piercing": True,
                                          "Smoke": False}],
         "max ammo": 30,
         "ammo pool": 3000,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0,
         "jam duration": 0,
         "laser sight": False,
         "alt fire": "vivianne_rifle",
         "passive": "none"},
    "Vivianne's Shotgun":
        {"name": "Vivianne's Shotgun",
         "ammo sprite": "Shotshell Small",
         "description": "What are you doing with my shotgun?",
         "class": "?????",
         "sprite": "Sprites/Weapon/Vivianne Shotgun.png",
         "gunshot sound": "Shotgun",
         "reloading sound": "Reload Pistol 1",
         "jamming sound": "Jamming",
         "sound level": 0.7,
         "accuracy": 12,
         "spread": 24,
         "handle": 6,
         "recoil": 70,
         "full auto": True,
         "fire rate": 34,
         "reload time": 7,
         "Reload style": "Partial",
         "bullet type": "Bullet",
         "bullets per shot": 12,
         "ammo cost": 1,
         "bullet info": [5, 35, 3, 20, {"Piercing": False, "Smoke": False}],
         "max ammo": 6,
         "ammo pool": 6000,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0,
         "jam duration": 0,
         "laser sight": False,
         "alt fire": "vivianne_shotgun",
         "passive": "none"},
    "Vivianne's Leg":
        {"name": "Vivianne's Leg",  # Make it great at countering bullets
         "ammo sprite": "None",
         "class": "Blunt",
         "sprite": "Sprites/Weapon/Vivianne's Leg.png",
         "gunshot sound": "Silence",
         "reloading sound": "Silence",
         "jamming sound": "Silence",
         "sound level": 0,
         "accuracy": 0,
         "spread": 0,
         "handle": 3,
         "recoil": 0,
         "full auto": False,
         "fire rate": 0,
         "reload time": 1,
         "bullet type": "Melee",
         "bullets per shot": 0,
         "ammo cost": 0,
         "bullet info": [0, 2, 15, 30, {}],
         "max ammo": 1,
         "ammo pool": 0,
         "crit rate": 0,
         "crit multiplier": 2,
         "range": 256,
         "jam rate": 0,
         "jam duration": 0,
         "laser sight": False,
         "alt fire": "vivianne_leg_alt",
         "passive": "vivianne_leg"},
    # Buggy
    "Buggy Gun":
        {"name": "Buggy Gun",
         "ammo sprite": "Rifle Medium",
         "description": "",
         "class": "Semi-auto",
         "sprite": "Sprites/Weapon/THR-1/Unarmed.png",
         "gunshot sound": "Small arms",
         "reloading sound": "Reload Enemy 1",
         "jamming sound": "Reload Enemy 1",
         "sound level": 0,
         "accuracy": 2,
         "spread": 4,
         "handle": 3,
         "recoil": 0,
         "full auto": True,
         "fire rate": 8,
         "reload time": 100,
         "bullet type": "Bullet",
         "bullets per shot": 1,
         "ammo cost": 1,
         "bullet info": [7, 50, 3, 50, {"Piercing": False, "Smoke": False}],
         "max ammo": 100,
         "ammo pool": 25000,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0,
         "jam duration": 0,
         "laser sight": True,
         "alt fire": "none",
         "passive": "buggy_gun_passive"},
    # Vivianne summons weapons
    # Type 56 Carbine
    "Type 56 Carbine":
        {"name": "Type 56 Carbine",
         "class": "?????",
         "sprite": "Sprites/Weapon/Tomboy/Type 56 Carbine.png",
         "gunshot sound": "Rifle 1 Shooting",
         "reloading sound": "Reload Pistol 1",
         "jamming sound": "Jamming",
         "sound level": 0.7,
         "accuracy": 2,
         "spread": 0.5,
         "handle": 6,
         "recoil": 20,
         "full auto": False,
         "fire rate": 24,
         "reload time": 70,
         "bullet type": "Bullet",
         "bullets per shot": 1,
         "ammo cost": 1,
         "bullet info": [6.5, 65, 4, 20, {"Piercing": False, "Smoke": False}],
         "max ammo": 10,
         "ammo pool": 3000,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0,
         "jam duration": 0,
         "laser sight": False,
         "alt fire": "none",
         "passive": "none"},

    "Anti-Material Rifle":
        {"name": "Anti-Material Rifle",
         "description": "",
         "class": "Rifle",
         "sprite": "Sprites/Weapon/Tomboy/Anti-Material Rifle.png",
         "gunshot sound": "Rifle 2",
         "reloading sound": "Reload Rifle 1",
         "jamming sound": "Jamming",
         "sound level": 4,
         "accuracy": 0,
         "spread": 0,
         "handle": 5,
         "recoil": 15,
         "full auto": False,
         "fire rate": 35,
         "reload time": 120,
         "bullet type": "Bullet",
         "bullets per shot": 1,
         "ammo cost": 1,
         "bullet info": [8, 100, 8, 300, {"Piercing": True, "Smoke": True}],
         "max ammo": 5,
         "ammo pool": 100,
         "crit rate": 0,
         "crit multiplier": 1,
         "jam rate": 0.05,
         "jam duration": 15,
         "laser sight": False,
         "alt fire": "none",
         "passive": "none",
         "agro": 50},
    "Shotgun":
        {"name": "Shotgun",
         "class": "Shotgun",
         "sprite": "Sprites/Weapon/Tomboy/Shotgun.png",
         "gunshot sound": "Shotgun 1 Shooting",
         "reloading sound": "Reload Pistol 1",
         "jamming sound": "Jamming",
         "sound level": 0.7,
         "accuracy": 4,
         "spread": 30,
         "handle": 8,
         "recoil": 50,
         "full auto": False,
         "fire rate": 10,
         "reload time": 60 // 8,
         "Reload style": "Partial",
         "bullet type": "Bullet",
         "bullets per shot": 10,
         "ammo cost": 1,
         "bullet info": [4, 35, 3, 20, {"Piercing": False, "Smoke": False}],
         "max ammo": 8,
         "ammo pool": 200,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0.05,
         "jam duration": 10,
         "laser sight": False,
         "alt fire": "none",  # ??????
         "passive": "none",
         "agro": 5},
    "Pistol":
        {"name": "Pistol",
         "description": "",
         "class": "Pistol",
         "sprite": "Sprites/Weapon/Peace.png",
         "gunshot sound": "Small arms",
         "reloading sound": "Reload Pistol 1",
         "jamming sound": "Jamming",
         "sound level": 1,
         "accuracy": 5,
         "spread": 2,
         "handle": 2,
         "recoil": 0,
         "full auto": True,
         "fire rate": 4,
         "reload time": 20,
         "bullet type": "Bullet",
         "bullets per shot": 2,
         "ammo cost": 1,
         "bullet info": [8, 20, 3, 30, {"Piercing": True}],
         "max ammo": 18,
         "ammo pool": 20000,
         "crit rate": 0,
         "crit multiplier": 5,
         "jam rate": 0.01,
         "jam duration": 10,
         "laser sight": False,
         "alt fire": "war_and_peace_alt",
         "passive": "war_and_peace_passive",
         "free var": {"War angle": 0}},

    "M's Spear":
        {"name": "M's Spear",
         "description": "",
         "class": "Rifle",
         "sprite": "Sprites/Weapon/Tomboy/M's Spear.png",
         "gunshot sound": "Silence",
         "reloading sound": "Silence",
         "jamming sound": "Silence",
         "sound level": 0.0,
         "accuracy": 5,
         "spread": 5,
         "handle": 10,
         "recoil": 0,
         "full auto": True,
         "fire rate": 20,
         "reload time": 0,
         "bullet type": "Bullet",
         "bullets per shot": 0,
         "ammo cost": 0,
         "bullet info": [1, 96, 1, 0, {"Piercing": True, "Smoke": True}],
         "max ammo": 1,
         "ammo pool": 100,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0.05,
         "jam duration": 10,
         "laser sight": False,
         "alt fire": "none",
         "passive": "m_spear",
         "free var": {"Spin counter": 0},
         "agro": 20},
    "Iguana's tail":
        {"name": "Iguana's tail",
         "sprite": "Sprites/Weapon/Tomboy/Iguana's tail.png",
         "gunshot sound": "Revolver shoot",
         "reloading sound": "Revolver reload",
         "jamming sound": "Jamming",
         "sound level": 1,
         "accuracy": 4,
         "spread": 4,
         "handle": 12,
         "recoil": 60,
         "full auto": True,
         "fire rate": 8,
         "reload time": 90 // 6,
         "Reload style": "Partial",
         "bullet type": "Bullet",
         "bullets per shot": 1,
         "ammo cost": 1,
         "bullet info": [6, 120, 4, 15, {"Piercing": True, "Smoke": True, "On hit": [Bullets.on_hit_iguanas_tail]}],
         "max ammo": 6,
         "ammo pool": 90,
         "crit rate": 0.025,
         "crit multiplier": 2,
         "jam rate": 0.05,
         "jam duration": 20,
         "laser sight": False,
         "alt fire": "none",
         "passive": "none"},
    "Sardine's Bucket":
        {"name": "Sardine's Bucket",
         "class": "Semi-auto",
         "sprite": "Sprites/Weapon/Anime.png",
         "gunshot sound": "Rifle 1 Shooting",
         "reloading sound": "Reload Enemy 1",
         "jamming sound": "Reload Enemy 1",
         "sound level": 0,
         "accuracy": 2,
         "spread": 4,
         "handle": 3,
         "recoil": 0,
         "full auto": True,
         "fire rate": 8,
         "reload time": 100,
         "bullet type": "Bullet",
         "bullets per shot": 0,
         "ammo cost": 0,
         "bullet info": [7, 50, 3, 50, {"Piercing": False, "Smoke": False}],
         "max ammo": 100,
         "ammo pool": 25000,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0,
         "jam duration": 0,
         "laser sight": False,
         "alt fire": "none",
         "passive": "sardine_passive",
         "agro": 0},
    "Agatha's Fist":
        {"name": "Agatha's Fist",
         "description": "",
         "class": "Blunt",
         "sprite": "Sprites/Weapon/Anime.png",
         "gunshot sound": "Silence",
         "reloading sound": "Silence",
         "jamming sound": "Silence",
         "sound level": 0,
         "accuracy": 0,
         "spread": 0,
         "handle": 6,
         "recoil": 0,
         "full auto": True,
         "fire rate": 0,
         "reload time": 1,
         "bullet type": "Melee",
         "bullets per shot": 0,
         "ammo cost": 0,
         "bullet info": [0, 2, 25, 70, {}],
         "range": 6 * 7,
         "max ammo": 1,
         "ammo pool": 0,
         "crit rate": 0.25,
         "crit multiplier": 2,
         "jam rate": 0,
         "jam duration": 0,
         "laser sight": False,
         "alt fire": "none",
         "passive": "agatha_passive",
         "free var": {"Angle ref": False, "Mod": 1, "Charge cooldown": 0}},
    "Azura's Fist":
        {"name": "Azura's Fist",
         "description": "",
         "class": "Blunt",
         "sprite": "Sprites/Weapon/Anime.png",
         "gunshot sound": "Silence",
         "reloading sound": "Silence",
         "jamming sound": "Silence",
         "sound level": 0,
         "accuracy": 0,
         "spread": 0,
         "handle": 6,
         "recoil": 0,
         "full auto": True,
         "fire rate": 0,
         "reload time": 1,
         "bullet type": "Melee",
         "bullets per shot": 0,
         "ammo cost": 0,
         "bullet info": [0, 2, 25, 70, {}],
         "range": 6 * 7,
         "max ammo": 1,
         "ammo pool": 0,
         "crit rate": 0.25,
         "crit multiplier": 2,
         "jam rate": 0,
         "jam duration": 0,
         "laser sight": False,
         "alt fire": "none",
         "passive": "azura_passive",
         "free var": {"Angle ref": False, "Mod": 1, "Charge cooldown": 0}},
    # |Enemy weapons|---------------------------------------------------------------------------------------------------
    # |Circle|----------------------------------------------------------------------------------------------------------
    "Laser Carbine":  # Laser Rifle, Has a laser pointer.
        {"name": "Laser Carbine",
         "class": "Semi-auto",
         "sprite": "Sprites/Enemies/Weapons/Laser Carbine.png",
         "gunshot sound": "Small arms",
         "reloading sound": "Reload Enemy 1",
         "jamming sound": "Reload Enemy 1",
         "sound level": 0.6,
         "accuracy": 0,
         "spread": 0,
         "handle": 6,
         "recoil": 0,
         "full auto": True,
         "fire rate": 0,
         "reload time": 15,
         "bullet type": "Laser",
         "bullets per shot": 1,
         "ammo cost": 1,
         "bullet info": [0, 12, 256, 8, {"Colour": (107, 153, 165)}],  # (116, 164, 171)
         "max ammo": 1,
         "ammo pool": 25000,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0,
         "jam duration": 0,
         "laser sight": True,
         "alt fire": "none",
         "passive": "laser_carbine_passive",
         "agro": 2},
    "Laser Rifle":      # Laser Rifle, Has a laser pointer.
        {"name": "Laser Rifle",
         "class": "Semi-auto",
         "sprite": "Sprites/Enemies/Weapons/Laser Rifle.png",
         "gunshot sound": "Small arms",
         "reloading sound": "Reload Enemy 1",
         "jamming sound": "Reload Enemy 1",
         "sound level": 0.6,
         "accuracy": 0,
         "spread": 0,
         "handle": 6,
         "recoil": 0,
         "full auto": True,
         "fire rate": 0,
         "reload time": 25,
         "bullet type": "Laser",
         "bullets per shot": 1,
         "ammo cost": 1,
         "bullet info": [0, 12, 256, 8, {"Colour": (107, 153, 165)}], # (116, 164, 171)
         "max ammo": 1,
         "ammo pool": 25000,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0,
         "jam duration": 0,
         "laser sight": True,
         "alt fire": "none",
         "passive": "laser_rifle_passive",
         "agro": 2},
    "Heavy Laser":      # Heavy Laser, Has a laser pointer. Has variable handle rate
        {"name": "Heavy Laser",
         "class": "Semi-auto",
         "sprite": "Sprites/Enemies/Weapons/Heavy Laser.png",
         "gunshot sound": "Small arms",
         "reloading sound": "Reload Enemy 1",
         "jamming sound": "Reload Enemy 1",
         "sound level": 0.80,
         "accuracy": 0,
         "spread": 0,
         "handle": 3,
         "recoil": 0,
         "full auto": True,
         "fire rate": 0,
         "reload time": 45,
         "bullet type": "Laser",
         "bullets per shot": 1,
         "ammo cost": 1,
         "bullet info": [0, 16, 640, 12, {"Colour": (116, 164, 171)}],  # (116, 164, 171)
         "max ammo": 1,
         "ammo pool": 25000,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0,
         "jam duration": 0,
         "laser sight": True,
         "alt fire": "none",
         "passive": "variable_handling_rate",
         "agro": 2},
    "Radar":            # Radar, Sends a ping at regular intervals to detect new targets
        {"name": "Radar",
         "class": "Semi-auto",
         "sprite": "Sprites/Weapon/Anime.png",
         "gunshot sound": "Small arms",
         "reloading sound": "Reload Enemy 1",
         "jamming sound": "Reload Enemy 1",
         "sound level": 0,
         "accuracy": 0,
         "spread": 0,
         "handle": 3,
         "recoil": 0,
         "full auto": True,
         "fire rate": 0,
         "reload time": 0,
         "bullet type": "Laser",
         "bullets per shot": 0,
         "ammo cost": 0,
         "bullet info": [0, 0, 0, 0, {"Colour": (107, 153, 165)}],  # (116, 164, 171)
         "max ammo": 1,
         "ammo pool": 0,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0,
         "jam duration": 0,
         "laser sight": True,
         "alt fire": "none",
         "passive": "radar_passive",
         "agro": 1},
    "Missile Pod":      # Missile Pod, Fires salvos of missiles
        {"name": "Missile Pod",
         "class": "Semi-auto",
         "sprite": "Sprites/Enemies/Weapons/Missile Pod.png",
         "gunshot sound": "Small arms",
         "reloading sound": "Reload Enemy 1",
         "jamming sound": "Reload Enemy 1",
         "sound level": 1,
         "accuracy": 0,
         "spread": 0,
         "handle": 3,
         "recoil": 0,
         "full auto": True,
         "fire rate": 10,
         "reload time": 140,
         "bullet type": "Missile",
         "bullets per shot": 1,
         "ammo cost": 1,
         "bullet info": [4, 240, 4, 5, {"Targeting range": 512,
                                         "Targeting angle": 60,
                                         "Secondary explosion": {"Duration": 5,
                                                                 "Growth": 2,
                                                                 "Damage mod": 0.75}}],  # (116, 164, 171)
         "max ammo": 6,
         "ammo pool": 25000,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0,
         "jam duration": 0,
         "laser sight": True,
         "alt fire": "none",
         "passive": "none",
         "agro": 2},
    "Marker Laser":     # Marker Laser, Hitting a target marks it. Making their location always known
        {"name": "Marker Laser",
         "class": "Semi-auto",
         "sprite": "Sprites/Enemies/Weapons/Marker Laser.png",
         "gunshot sound": "Small arms",
         "reloading sound": "Reload Enemy 1",
         "jamming sound": "Reload Enemy 1",
         "sound level": 0.4,
         "accuracy": 0,
         "spread": 0,
         "handle": 3,
         "recoil": 0,
         "full auto": True,
         "fire rate": 0,
         "reload time": 25,
         "bullet type": "Laser",
         "bullets per shot": 1,
         "ammo cost": 1,
         "bullet info": [0, 12, 640, 8, {"Colour": (0, 0, 55), "On hit": [Bullets.on_hit_marked]}],
         "max ammo": 1,
         "ammo pool": 25000,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0,
         "jam duration": 0,
         "laser sight": True,
         "alt fire": "none",
         "passive": "variable_handling_rate",
         "agro": 2},
    "ARWS":  # All Range Weapon System, Fires both lasers and missiles. Blows up when killed cause fuk you
        {"name": "ARWS",
         "class": "Semi-auto",
         "sprite": "Sprites/Enemies/Weapons/ARWS.png",
         "gunshot sound": "Small arms",
         "reloading sound": "Reload Enemy 1",
         "jamming sound": "Reload Enemy 1",
         "sound level": 1,
         "accuracy": 0,
         "spread": 0,
         "handle": 3,
         "recoil": 0,
         "full auto": True,
         "fire rate": 0,
         "reload time": 90,
         "bullet type": "Laser",
         "bullets per shot": 1,
         "ammo cost": 1,
         "bullet info": [0, 32, 320, 20, {"Colour": (107, 153, 165)}],
         "max ammo": 1,
         "ammo pool": 25000,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0,
         "jam duration": 0,
         "laser sight": True,
         "alt fire": "none",
         "passive": "arws_passive",
         "agro": 2},
    "Drone Gun":
        {"name": "Drone Gun",
         "description": "",
         "class": "?????",
         "sprite": "Sprites/Enemies/Weapons/Plasma Spray.png",
         "gunshot sound": "Shotgun",
         "reloading sound": "Reload Pistol 1",
         "jamming sound": "Jamming",
         "sound level": 0.7,
         "accuracy": 1, "spread": 24,
         "handle": 6, "recoil": 20,
         "full auto": True, "fire rate": 28, "reload time": 0,
         "bullet type": "Bullet",
         "bullets per shot": 1,
         "ammo cost": 0, "max ammo": 1, "ammo pool": 0,
         "bullet info": [4, 90, 6, 5,
                         {"Piercing": False, "Smoke": False, "Colour": (107, 165, 153), "Damage type": "Energy"}],
         "crit rate": 0, "crit multiplier": 2,
         "jam rate": 0, "jam duration": 0,
         "laser sight": False, "alt fire": "none", "passive": "none"},
    # |Triangle|--------------------------------------------------------------------------------------------------------
    # Plasma Rifle, Bullets are slow
    "Plasma Spray":
        {"name": "Plasma Spray",
         "description": "",
         "class": "?????",
         "sprite": "Sprites/Enemies/Weapons/Plasma Spray.png",
         "gunshot sound": "Shotgun",
         "reloading sound": "Reload Pistol 1",
         "jamming sound": "Jamming",
         "sound level": 0.7,
         "accuracy": 1, "spread": 24,
         "handle": 6, "recoil": 20,
         "full auto": True, "fire rate": 2, "reload time": 180,
         "bullet type": "Bullet",
         "bullets per shot": 1,
         "ammo cost": 1, "max ammo": 30, "ammo pool": 3000,
         "bullet info": [3.5, 90, 6, 4, {"Piercing": False, "Smoke": False, "Colour": (107, 165, 153), "Damage type": "Energy"}],
         "crit rate": 0, "crit multiplier": 2,
         "jam rate": 0, "jam duration": 0,
         "laser sight": False, "alt fire": "none", "passive": "none"},
    "Plasma Rifle":
        {"name": "Plasma Rifle",
         "description": "",
         "class": "?????",
         "sprite": "Sprites/Enemies/Weapons/Plasma Rifle.png",
         "gunshot sound": "Shotgun",
         "reloading sound": "Reload Pistol 1",
         "jamming sound": "Jamming",
         "sound level": 0.7,
         "accuracy": 1,
         "spread": 1,
         "handle": 6,
         "recoil": 20,
         "full auto": True,
         "fire rate": 50,
         "reload time": 120,
         "bullet type": "Bullet",
         "bullets per shot": 1,
         "ammo cost": 1,
         "bullet info": [3.5, 90, 8, 4, {"Piercing": False, "Smoke": False, "Colour": (107, 165, 153), "Damage type": "Energy"}],
         "max ammo": 30,
         "ammo pool": 3000,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0,
         "jam duration": 0,
         "laser sight": False,
         "alt fire": "none",
         "passive": "none"},
    # Laser Shotgun, It's a laser shotgun. Shoots multiple lasers
    "Laser Shotgun":  # Laser Rifle, Has a laser pointer.
        {"name": "Laser Shotgun",
         "class": "Semi-auto",
         "sprite": "Sprites/Enemies/Weapons/Laser Shotgun.png",
         "gunshot sound": "Small arms",
         "reloading sound": "Reload Enemy 1",
         "jamming sound": "Reload Enemy 1",
         "sound level": 0.6,
         "accuracy": 0,
         "spread": 15,
         "handle": 4,
         "recoil": 0,
         "full auto": True,
         "fire rate": 0,
         "reload time": 60,
         "bullet type": "Laser",
         "bullets per shot": 16,
         "ammo cost": 1,
         "bullet info": [0, 12, 96, 8, {"Colour": (107, 165, 153)}],
         "max ammo": 1,
         "ammo pool": 25000,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0,
         "jam duration": 0,
         "laser sight": True,
         "alt fire": "none",
         "passive": "none",
         "agro": 2},
    # Smoke Dispenser, Shoots smoke grenades, deals no damage
    "Smoke Dispenser":
        {"name": "Smoke Dispenser",
         "description": "",
         "class": "Throwable",
         "sprite": "Sprites/Enemies/Weapons/Smoke Dispenser.png",
         "gunshot sound": "Small arms",
         "reloading sound": "Reload Pistol 1",
         "jamming sound": "Jamming",
         "sound level": 0.5,
         "accuracy": 3,
         "spread": 45,
         "handle": 8,
         "recoil": 50,
         "full auto": False,
         "fire rate": 60,
         "reload time": 120,
         "Reload style": "Partial",
         "bullet type": "GrenadeType3",
         "bullets per shot": 2,
         "ammo cost": 1,
         "bullet info": [5, 30, 4, 0, {"Smoke": {
             "Duration": 50,
             "Radius": 48,
         }}],
         "max ammo": 3,
         "ammo pool": 6000,
         "crit rate": 0,
         "crit multiplier": 1,
         "jam rate": 0,
         "jam duration": 0,
         "laser sight": False,
         "alt fire": "none",
         "passive": "none"},
    # Snare
    "Desert Shotgun":
        {"name": "Desert Shotgun",
         "description": "",
         "class": "?????",
         "sprite": "Sprites/Enemies/Weapons/Desert Shotgun.png",
         "gunshot sound": "Shotgun",
         "reloading sound": "Reload Pistol 1",
         "jamming sound": "Jamming",
         "sound level": 0.7,
         "accuracy": 1,
         "spread": 20,
         "handle": 6,
         "recoil": 20,
         "full auto": True,
         "fire rate": 50,
         "reload time": 120,
         "bullet type": "Bullet",
         "bullets per shot": 16,
         "ammo cost": 1,
         "bullet info": [5, 40, 2, 2, {"Piercing": False, "Smoke": False, "On hit": [Bullets.on_hit_marked]}],
         "max ammo": 2,
         "ammo pool": 3000,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0,
         "jam duration": 0,
         "laser sight": False,
         "alt fire": "none",
         "passive": "none",
         "agro": 4},    # Need a way to have random speed on bullets
    # Gun Hammer, Creates shock waves that crushes armour
    "Gun Hammer":
        {"name": "Gun Hammer",
         "description": "",
         "class": "Slash",
         "sprite": "Sprites/Enemies/Weapons/Gun Hammer.png",
         "gunshot sound": "Silence",
         "reloading sound": "Silence",
         "jamming sound": "Silence",
         "sound level": 0,
         "accuracy": 0,
         "spread": 0,
         "handle": 4,
         "recoil": 0,
         "full auto": False,
         "fire rate": 0,
         "reload time": 10,
         "bullet type": "Melee3",
         "bullets per shot": 0,
         "ammo cost": 0,
         "bullet info": [96, 1, 20, 30, {}],
         "max ammo": 7,
         "ammo pool": 140,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0,
         "jam duration": 0,
         "laser sight": False,
         "alt fire": "none",
         "passive": "gun_hammer_passive"},
    # Pile Bunker, makes a loud clink before making the attack. Can one shot weaker characters
    "Pile Bunker":
        {"name": "Pile Bunker",
         "description": "",
         "class": "Slash",
         "sprite": "Sprites/Enemies/Weapons/Pile Bunker.png",
         "gunshot sound": "Silence",
         "reloading sound": "Silence",
         "jamming sound": "Silence",
         "sound level": 0,
         "accuracy": 0,
         "spread": 0,
         "handle": 4,
         "recoil": 0,
         "full auto": False,
         "fire rate": 0,
         "reload time": 10,
         "bullet type": "Melee3",
         "bullets per shot": 0,
         "ammo cost": 0,
         "bullet info": [96, 1, 20, 30, {}],
         "max ammo": 7,
         "ammo pool": 140,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0,
         "jam duration": 0,
         "laser sight": False,
         "alt fire": "none",
         "passive": "pile_bunker_passive"},
    # |Square|----------------------------------------------------------------------------------------------------------
    # Combat Rifle, Really has nothing special
    "Combat Rifle":
        {"name": "Combat Rifle",
         "description": "",
         "class": "?????",
         "sprite": "Sprites/Enemies/Weapons/Combat Rifle.png",
         "gunshot sound": "Shotgun",
         "reloading sound": "Reload Pistol 1",
         "jamming sound": "Jamming",
         "sound level": 0.7,
         "accuracy": 1,
         "spread": 1,
         "handle": 6,
         "recoil": 20,
         "full auto": True,
         "fire rate": 15,
         "reload time": 160,
         "bullet type": "Bullet",
         "bullets per shot": 1,
         "ammo cost": 1,
         "bullet info": [5.5, 32, 3, 4, {"Piercing": False, "Smoke": False}],
         "max ammo": 30,
         "ammo pool": 3000,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0,
         "jam duration": 0,
         "laser sight": False,
         "alt fire": "none",
         "passive": "none"},
    # Flamethrower, Doesn't have much spread
    "Flamethrower":
        {"name": "Flamethrower",
         "description": "",
         "class": "Flame",
         "sprite": "Sprites/Enemies/Weapons/Flame Thrower.png",
         "gunshot sound": "Fire",
         "reloading sound": "Reload Pistol 1",
         "jamming sound": "Jamming",
         "sound level": 0.5,
         "accuracy": 0,
         "spread": 3,
         "handle": 8,
         "recoil": 0,
         "full auto": True,
         "fire rate": 1,
         "reload time": 240,
         "bullet type": "Fire",
         "bullets per shot": 2,
         "ammo cost": 1,
         "bullet info": [4, 40, 4, 2, {"Particle allowed": True, "Burn chance": 1, "Burn duration": 30,
                                       "Colour": Fun.FIRE}],
         "max ammo": 100,
         "ammo pool": 5000,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0.0025,
         "jam duration": 10,
         "laser sight": False,
         "alt fire": "none",
         "passive": "none"},
    # Binocular, Has the "share targets" effect
    "Binoculars":
        {"name": "Binoculars",
         "description": "",
         "class": "Flame",
         "sprite": "Sprites/Weapon/Anime.png",
         "gunshot sound": "Fire",
         "reloading sound": "Reload Pistol 1",
         "jamming sound": "Jamming",
         "sound level": 0.5,
         "accuracy": 0,
         "spread": 0,
         "handle": 8,
         "recoil": 0,
         "full auto": True,
         "fire rate": 0,
         "reload time": 300,
         "bullet type": "Artillery",
         "bullets per shot": 0,
         "ammo cost": 0,
         "bullet info": [0, 90, 64, 50, {"secondary_explosion": {"Duration": 20},
                                         "Colour": Fun.RED}],
         "max ammo": 1,
         "ammo pool": 5000,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0.0025,
         "jam duration": 10,
         "laser sight": False,
         "alt fire": "none",
         "passive": "binoculars_passive"},
    # Artillery Radio, Calls in the artillery strikes
    "Artillery Radio":
        {"name": "Artillery Radio",
         "description": "",
         "class": "Flame",
         "sprite": "Sprites/Enemies/Weapons/Artillery Radio.png",
         "gunshot sound": "Fire",
         "reloading sound": "Reload Pistol 1",
         "jamming sound": "Jamming",
         "sound level": 0.5,
         "accuracy": 0,
         "spread": 0,
         "handle": 8,
         "recoil": 0,
         "full auto": True,
         "fire rate": 0,
         "reload time": 300,
         "bullet type": "Artillery",
         "bullets per shot": 0,
         "ammo cost": 0,
         "bullet info": [0, 90, 64, 50, {"Secondary explosion": {"Duration": 20}, "Colour": Fun.RED}],
         "max ammo": 1,
         "ammo pool": 5000,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0.0025,
         "jam duration": 10,
         "laser sight": False,
         "alt fire": "none",
         "passive": "artillery_radio_passive"},
    # Grenade Launcher, Grenades leave napalm
    "Napalm Grenade Launcher":
        {"name": "Napalm Grenade Launcher",
         "description": "",
         "class": "Throwable",
         "sprite": "Sprites/Enemies/Weapons/Grenade Launcher.png",
         "gunshot sound": "Small arms",
         "reloading sound": "Reload Pistol 1",
         "jamming sound": "Jamming",
         "sound level": 0.5,
         "accuracy": 3,
         "spread": 2,
         "handle": 8,
         "recoil": 50,
         "full auto": False,
         "fire rate": 60,
         "reload time": 120 / 6,
         "Reload style": "Partial",
         "bullet type": "GrenadeType2",
         "bullets per shot": 1,
         "ammo cost": 1,
         "bullet info": [5, 100, 4, 10, {"Incendiary": {
             "Amount of Bullets": 16,
             "Speed": 2,
             "Duration": 90,
             "Radius": 4,
             "Damage": 5,
             "Fire property": {"Particle allowed": True, "Burn chance": 1, "Burn duration": 30, "Colour": Fun.FIRE}},
             "Colour": Fun.FIRE
         }],
         "max ammo": 6,
         "ammo pool": 6000,
         "crit rate": 0,
         "crit multiplier": 1,
         "jam rate": 0,
         "jam duration": 0,
         "laser sight": False,
         "alt fire": "none",
         "passive": "none"},
    # Bulwark Minigun, Doesn't need to reload, has spin up time
    "Bulwark Minigun":  # After mission N
        {"name": "Bulwark Minigun",
         "description": "",
         "class": "Semi-auto",
         "sprite": "Sprites/Enemies/Weapons/Bulwark Minigun.png",
         "gunshot sound": "Small arms",
         "reloading sound": "Reload Pistol 1",
         "jamming sound": "Jamming",
         "sound level": 0.75,
         "accuracy": 8,
         "spread": 8,
         "handle": 2,
         "recoil": 3,
         "full auto": True,
         "fire rate": 60,
         "reload time": 180,
         "bullet type": "Flechette",
         "bullets per shot": 1,
         "ammo cost": 0,
         "bullet info": [8, 25, 8, 6, {"Colour": Fun.WHITE, "Damage type": "Physical", "No ignore armour": True}],
         "max ammo": 2400,
         "ammo pool": 2400,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0.00125,
         "jam duration": 90,
         "laser sight": False,
         "alt fire": "none",
         "passive": "bulwark_passive",
         "free var": {"Allowed to go down": False,
                      "Normal fire rate": 60}
         },
    # |Bosses|----------------------------------------------------------------------------------------------------------
    "Shield Generator Railgun":
        {"name": "Shield Generator Railgun",
         "description": "",
         "class": "Semi-auto",
         "sprite": "Sprites/Enemies/Weapons/Bulwark Minigun.png",
         "gunshot sound": "Small arms",
         "reloading sound": "Reload Pistol 1",
         "jamming sound": "Jamming",
         "sound level": 0.75,
         "accuracy": 8,
         "spread": 8,
         "handle": 6,
         "recoil": 3,
         "full auto": True,
         "fire rate": 0,
         "reload time": 0,
         "bullet type": "Bullet",
         "bullets per shot": 0,
         "ammo cost": 0,
         "bullet info": [8, 25, 8, 6, {"Colour": Fun.WHITE, "Damage type": "Physical", "No ignore armour": True}],
         "max ammo": 2400,
         "ammo pool": 2400,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0.00125,
         "jam duration": 90,
         "laser sight": False,
         "alt fire": "none",
         "passive": "none",
         "free var": {}
         },
    "Hover Tank Cannon":
        {"name": "Hover Tank Cannon",
         "description": "",
         "class": "Semi-auto",
         "sprite": "Sprites/Enemies/Weapons/Bulwark Minigun.png",
         "gunshot sound": "Hover Tank Canon",
         "reloading sound": "Reload Pistol 1",
         "jamming sound": "Jamming",
         "sound level": 0.75,
         "accuracy": 8,
         "spread": 8,
         "handle": 3,
         "recoil": 3,
         "full auto": True,
         "fire rate": 0,
         "reload time": 0,
         "bullet type": "Bullet",
         "bullets per shot": 0,
         "ammo cost": 0,
         "bullet info": [8, 25, 8, 6, {"Colour": Fun.WHITE, "Damage type": "Physical", "No ignore armour": True}],
         "max ammo": 2400,
         "ammo pool": 2400,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0.00125,
         "jam duration": 90,
         "laser sight": False,
         "alt fire": "none",
         "passive": "hover_tank_cannon_passive",
         "free var": {}
         },
    "Desert's Wind":
        {"name": "Desert's Wind",
         "description": "",
         "class": "Semi-auto",
         "sprite": "Sprites/Enemies/Weapons/Desert's Wind.png",
         "gunshot sound": "Small arms",
         "reloading sound": "Reload Pistol 1",
         "jamming sound": "Jamming",
         "sound level": 0.75,
         "accuracy": 8,
         "spread": 8,
         "handle": 3,
         "recoil": 3,
         "full auto": True,
         "fire rate": 0,
         "reload time": 0,
         "bullet type": "Bullet",
         "bullets per shot": 0,
         "ammo cost": 0,
         "bullet info": [8, 25, 8, 6, {"Colour": Fun.WHITE, "Damage type": "Physical", "No ignore armour": True}],
         "max ammo": 2400,
         "ammo pool": 2400,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0.00125,
         "jam duration": 90,
         "laser sight": False,
         "alt fire": "none",
         "passive": "hover_tank_cannon_passive",
         "free var": {}
         },
    "Bloodhound Weaponry":
        {"name": "Bloodhound Weaponry",
         "description": "",
         "class": "Semi-auto",
         "sprite": "Sprites/Enemies/Weapons/Bulwark Minigun.png",
         "gunshot sound": "Small arms",
         "reloading sound": "Reload Pistol 1",
         "jamming sound": "Jamming",
         "sound level": 0.75,
         "accuracy": 8,
         "spread": 8,
         "handle": 180,
         "recoil": 3,
         "full auto": True,
         "fire rate": 0,
         "reload time": 0,
         "bullet type": "Bullet",
         "bullets per shot": 0,
         "ammo cost": 0,
         "bullet info": [8, 25, 8, 6, {"Colour": Fun.WHITE, "Damage type": "Physical", "No ignore armour": True}],
         "max ammo": 2400,
         "ammo pool": 2400,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0.00125,
         "jam duration": 90,
         "laser sight": False,
         "alt fire": "none",
         "passive": "attack_helicopter_weaponry_passive",
         "free var": {}
         },
    "Attack Helicopter Weaponry":
        {"name": "Attack Helicopter Weaponry",
         "description": "",
         "class": "Semi-auto",
         "sprite": "Sprites/Enemies/Weapons/Bulwark Minigun.png",
         "gunshot sound": "Small arms",
         "reloading sound": "Reload Pistol 1",
         "jamming sound": "Jamming",
         "sound level": 0.75,
         "accuracy": 8,
         "spread": 8,
         "handle": 3,
         "recoil": 3,
         "full auto": True,
         "fire rate": 0,
         "reload time": 0,
         "bullet type": "Bullet",
         "bullets per shot": 0,
         "ammo cost": 0,
         "bullet info": [8, 25, 8, 6, {"Colour": Fun.WHITE, "Damage type": "Physical", "No ignore armour": True}],
         "max ammo": 2400,
         "ammo pool": 2400,
         "crit rate": 0,
         "crit multiplier": 2,
         "jam rate": 0.00125,
         "jam duration": 90,
         "laser sight": False,
         "alt fire": "none",
         "passive": "attack_helicopter_weaponry_passive",
         "free var": {}
         },
    "Curtis' Arsenal":
        {"name": "War and Peace",
         "description": "",
         "class": "Pistol",
         "sprite": "Sprites/Weapon/Peace.png",
         "gunshot sound": "Small arms",
         "reloading sound": "Reload Pistol 1",
         "jamming sound": "Jamming",
         "sound level": 1,
         "accuracy": 5,
         "spread": 2,
         "handle": 10,
         "recoil": 0,
         "full auto": True,
         "fire rate": 8,
         "reload time": 20,
         "bullet type": "Bullet",
         "bullets per shot": 2,
         "ammo cost": 1,
         "bullet info": [8, 20, 3, 30, {"Piercing": True}],
         "max ammo": 14,
         "ammo pool": 20000,
         "crit rate": 0,
         "crit multiplier": 5,
         "jam rate": 0.01,
         "jam duration": 10,
         "laser sight": False,
         "alt fire": "war_and_peace_alt",
         "passive": "war_and_peace_passive",
         "free var": {"Peace angle": 0, "War angle": 0}},
}