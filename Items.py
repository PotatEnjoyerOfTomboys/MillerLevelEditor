import pygame as pg
import random
import math

import Bullets
import Fun
import Particles
import copy

# from Bullets import Bullet


def spawn_item(entities, item_name, pos, self=False):
    if self:
        entities["items"].append(ItemGen2(item_repertory[item_name].copy(), pos, team=self.team, owner=self))
        return
    entities["items"].append(ItemGen2(item_repertory[item_name].copy(), pos))


class ItemGen2:
    # Like the old item class, but way better
    def __init__(self, info, pos, team="Neutral", owner=None):
        info = info.copy()

        # Identification
        self.name = info["name"]
        self.team = team
        self.owner = owner

        # Movement
        self.pos = pos
        self.vel = [0, 0]
        self.friction = 1
        if "friction" in info:
            self.friction = info["friction"]
        self.thiccness = info["thickness"]  # Size of the item
        self.collision_box = pg.Rect(self.pos[0] - self.thiccness // 2, self.pos[1] - self.thiccness // 2,
                                     self.thiccness, self.thiccness)

        # Render
        self.draw_func = Fun.none
        if "draw" in info:
            self.draw_func = info["draw"]
        self.animation_counter = 0
        self.sprites = info["sprites"]
        self.direction_angle = 0

        # Behaviour
        self.act_func = info["act"]
        self.life_time = -1     # Timer to make some items not permanent
        self.time = 0
        if "life time" in info:
            self.life_time = info["life time"]
        self.alive = True
        self.free_var = copy.deepcopy(info["free var"])
        self.bullets_shot = []

    def time_is_ticking(self):
        self.life_time -= self.alive
        self.alive = self.life_time != 0
        return self.alive

    def move(self, level):
        self.direction_angle = Fun.angle_between(self.vel, [0, 0])
        Fun.collision_check(self, level["map"])
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.collision_box = pg.Rect(self.pos[0] - self.thiccness / 2, self.pos[1] - self.thiccness / 2,
                                     self.thiccness, self.thiccness)
        # |Friction handling|-----------------------------------------------------------------------------------------------
        friction_strength = self.friction
        for i in range(2):
            if self.vel[i] != 0:
                if self.vel[i] > 0 + friction_strength:
                    self.vel[i] -= friction_strength
                elif self.vel[i] < 0 - friction_strength:
                    self.vel[i] += friction_strength
                else:
                    self.vel[i] = 0

    def act(self, entities, level):
        self.time += 1
        self.act_func(self, entities, level)
        if self.vel != [0, 0]: self.move(level)

    def draw(self, WIN, scrolling):
        self.draw_func(self, WIN, scrolling)


# |Weapon Related|------------------------------------------------------------------------------------------------------
def rev_up(item, self, entities, bullets):
    # ["Normal fire rate"]
    # ["Weapon slot"]
    # ["Rev up rate"]
    # ["Rev up target"]
    # ["Allowed to go down"]
    if self.switch_weapon == item.free_var["Weapon slot"]:
        # Keep the item alive
        item.status = 1
        # Does the effects
        if self.no_shoot_state == 0:
            item.free_var["Allowed to go down"] = True

        if item.free_var["Allowed to go down"]:
            if self.mouse_input["Fire"] and self.equipped_weapon.ammo != 0 and self.shot_allowed:

                # Make fire rate go down
                if self.equipped_weapon.fire_rate > item.free_var["Rev up target"]:
                    self.equipped_weapon.fire_rate -= item.free_var["Rev up rate"]

                    # Prevent it from going under the target
                    if self.equipped_weapon.fire_rate < item.free_var["Rev up target"]:
                        self.equipped_weapon.fire_rate = item.free_var["Rev up target"]
                    item.free_var["Allowed to go down"] = False

            # Make fire rate go up when not shooting
            elif self.equipped_weapon.fire_rate < item.free_var["Normal fire rate"]:
                self.equipped_weapon.fire_rate += item.free_var["Rev up rate"]

                # Prevent it from going over the target
                if self.equipped_weapon.fire_rate > item.free_var["Normal fire rate"]:
                    self.equipped_weapon.fire_rate = item.free_var["Normal fire rate"]

    else:
        self.weapons[item.free_var['Weapon slot']].fire_rate = item.free_var["Normal fire rate"]
        item.status = 0
    #


# |Gen 2 items|---------------------------------------------------------------------------------------------------------
def riot_shield(self, entities, level):
    self.time_is_ticking()
    for b in entities["bullets"]:
        if b.team == self.team:
            continue
        if b.melee or b.explosion or b.laser or b.laser_based or type(b) == Bullets.Artillery:
            continue
        if Fun.collision_rect_circle(self.pos[0] - self.thiccness // 2, self.pos[1] - self.thiccness // 2,
                                     self.thiccness, self.thiccness,
                                     b.pos[0], b.pos[1], b.radius):
            b.duration = 0
            Particles.sparks_2(entities, self.pos, b.angle + 180,
                         colour=b.colour, angle_deviation=6, duration_range=(4, 13), size=2)


def riot_shield_draw(self, WIN, scrolling):
    WIN.blit(
        self.sprites[self.free_var["Sprite"]],
        (self.pos[0] - 8 + scrolling[0],
         self.pos[1] -8 + scrolling[1])
    )
    #


def smoke_grenade(self, entities, level):
    self.time_is_ticking()
        # Handles the visual side
        # if self.status % 12 == 0:
    if self.time % 16 == 0:
        for p in range(round(self.free_var["Radius"] * 0.25)):
            entities["particles"].append(Particles.Smoke(
                Fun.random_point_in_circle(self.pos, self.free_var["Radius"]),
                duration=(self.time // 4, self.time // 3)
            ))
    # Give the stealth status effect
    for e in entities["entities"]:
        if Fun.check_point_in_circle(self.free_var["Radius"],
                                        self.pos[0], self.pos[1], e.pos[0], e.pos[1]):
            if e.status["Stealth"] == 0:
                e.status["Stealth"] += 1
    #


def jeanne_turret_act(self, entities, level):
    jeanne_cover_act(self, entities, level)
    bullet_info = self.free_var["Bullet info"]

    # Targeting
    dist = bullet_info[0] * bullet_info[1]
    target = False
    for e in entities["entities"]:
        if e.team == self.team:
            continue
        control_dist = Fun.distance_between(self.pos, e.pos)
        if control_dist <= dist:
            if not Fun.wall_between(e.pos, self.pos, level):
                dist = control_dist
                target = e

    # Shoot people
    if target:
        # Move gun
        target_angle = Fun.angle_between(target.pos, self.pos)
        invert_aim = 1
        if not -(180 - self.free_var["Handle"]) + target_angle < self.free_var["Angle"] < 180 - self.free_var["Handle"] + target_angle:
            invert_aim = -1

        # Adjust angle
        if self.free_var["Angle"] < target_angle:
            self.free_var["Angle"] += self.free_var["Handle"] * invert_aim
            if self.free_var["Angle"] > target_angle:
                self.free_var["Angle"] = target_angle
        elif self.free_var["Angle"] > target_angle:
            self.free_var["Angle"] += -self.free_var["Handle"] * invert_aim
            if self.free_var["Angle"] < target_angle:
                self.free_var["Angle"] = target_angle

        # Value Limiter
        if self.free_var["Angle"] > 180:
            self.free_var["Angle"] = -180 + (self.free_var["Angle"] - 180)
        if self.free_var["Angle"] < -180:
            self.free_var["Angle"] = 180 - (self.free_var["Angle"] + 180)

        # Shoot
        if self.time % self.free_var["Fire rate"] == 0:
            Bullets.spawn_bullet(
                self.owner, entities, self.free_var["Bullet type"],
                Fun.move_with_vel_angle(self.pos, 20, self.free_var["Angle"]),
                self.free_var["Angle"] + random.uniform(-2, 2), self.free_var["Bullet info"])
            self.free_var["Ammo"] -= 1
            Fun.play_sound("Small arms")
            self.alive = self.free_var["Ammo"] > 0
            entities["sounds"].append(Fun.Sound(self.pos, 60, 175, source=self.team, strength=2))
    #


def jeanne_turret_draw(self, WIN, scrolling):
    WIN.blit(Fun.ENTITY_SHADOW, (self.pos[0] - 16 + scrolling[0], self.pos[1] + 1 + scrolling[1]),
             special_flags=pg.BLEND_RGBA_SUB)
    WIN.blit(
        self.sprites[-1],
        (self.pos[0] - 8 + scrolling[0],
         self.pos[1] -8 + scrolling[1])
    )
    WIN.blit(
        self.sprites[Fun.get_entity_direction(self.free_var["Angle"])],
        (self.pos[0] - 8 + scrolling[0],
         self.pos[1] - 12 + scrolling[1])
    )
    #


def jeanne_cover_act(self, entities, level):
    for b in entities["bullets"]:
        if b.team == self.team:
            continue
        if b.laser_based:
            continue
        thick = self.thiccness
        if "Special Coating" in self.free_var and b.damage_type in ["Fire", "Energy"]:
            continue

        if Fun.collision_rect_circle(self.pos[0] - thick // 2, self.pos[1] - thick // 2, thick, thick,
                                         b.pos[0], b.pos[1], b.radius):
            b.duration = 0
            if self.free_var["IFrames"] == 0:
                self.free_var["Health"] -= 1
                self.free_var["IFrames"] = 8
            number_of_particle = 18
            for particles_to_add in range(360 // number_of_particle):
                entities["particles"].append(Particles.RandomParticle2(
                    [self.pos[0], self.pos[1]], Fun.DARK_RED, 1 + 2 * random.random(), random.randint(15, 60),
                                                            particles_to_add * number_of_particle,
                    size=Fun.get_random_element_from_list([1, 2, 4])))
            self.vel = Fun.move_with_vel_angle(self.vel, b.damage, b.angle)
    self.alive = self.free_var["Health"] > 0
    if not self.alive:
        # Add effects for on destruction effects
        if "Self Destruct" in self.free_var:
            Bullets.spawn_bullet(
                self.owner, entities, Bullets.ExplosionSecondary,
                self.pos, 0, [0, 25, 4, 25, {'Duration': 20, 'Growth': 5, 'Damage mod': 1}])
        if "Busting Blue Balls" in self.free_var:
            for x in range(12):
                ran = random.random()
                Bullets.spawn_blue_balls(
                    self.owner, entities,
                    self.owner.pos.copy(),
                    # self.owner.direction_angle + 20 * x ,
                    360 * ran,
                    [3.5, 60, 4 + 3 * ran * random.random(), 10, {"Colour": Fun.DARK_BLUE}])
        if "Wrench Wench" in self.free_var:

            e = self.owner
            for x in range(5):
                pos = Fun.random_point_in_circle(e.pos, 16)
                entities["particles"].append(
                    Particles.RandomParticle1(pos, Fun.RED, -2, round(10 + 10 * random.random()),
                                        size=(2, 4))
                )
            magazine_ammo_back = round(e.weapon.max_ammo * 0.5)
            over_magazine = e.weapon.ammo + magazine_ammo_back > e.weapon.max_ammo
            if over_magazine:
                diff = e.weapon.ammo + magazine_ammo_back - e.weapon.max_ammo
                e.weapon.ammo_pool += diff
                magazine_ammo_back -= diff

            e.weapon.ammo += magazine_ammo_back


    if self.free_var["IFrames"] > 0:
        self.free_var["IFrames"] -= 1


def jeanne_cover_draw(self, WIN, scrolling):
    WIN.blit(
        self.sprites[-1],
        (self.pos[0] - 8 + scrolling[0],
         self.pos[1] -8 + scrolling[1])
    )
    #


def jeanne_demolition_charge_act(self, entities, level):
    if self.owner.input["Interact"] and self.time > 30:
        self.life_time = 180
        self.free_var["Blowing up"] = True
    if self.free_var["Blowing up"]:
        if self.time_is_ticking():
            # Show timer
            entities["particles"].append(
                Particles.FloatingTextType2([self.pos[0], self.pos[1] - 16], 18,
                                      f'{Fun.write_time(self.life_time)}',
                                      Fun.WHITE, 1))
        else:
            # Blow up
            self.free_var["Blowing up"] = False
            Bullets.spawn_bullet(
                self.owner, entities, Bullets.ExplosionSecondary,
                self.pos, 0, [0, 25, 4, 75, {'Duration': 25, 'Growth': 4, 'Damage mod': 1}])
    #


def jeanne_demolition_charge_draw(self, WIN, scrolling):
    WIN.blit(Fun.ENTITY_SHADOW, (self.pos[0] - 16 + scrolling[0], self.pos[1] + 1 + scrolling[1]),
             special_flags=pg.BLEND_RGBA_SUB)
    WIN.blit(
        self.sprites[-1],
        (self.pos[0] - 8 + scrolling[0],
         self.pos[1] -8 + scrolling[1])
    )


def zandr_speen(self, entities, level):
    self.owner.angle += self.time * 12
    self.owner.direction_angle += self.time * 12
    self.time_is_ticking()


def jester_out_of_my_way(self, entities, level):
    damage = round(abs(self.owner.vel[0]) + abs(self.owner.vel[1])) * 4
    if damage > 60:
        damage = 60
    for e in entities["entities"]:
        if e.team == self.team: continue
        if self.owner.collision_box.colliderect(e.collision_box):
            e.vel = Fun.move_with_vel_angle(e.vel, 2, Fun.angle_between(e.collision_box.center, self.pos))

            Fun.damage_calculation(e, damage, "Melee", death_message="Ran over, by a pedestrian?")
    self.time_is_ticking()


def landmine(self, entities, level):
    radius = self.free_var["Radius"]
    # "Time" "Radius" "Target"
    #              "Explosion info": [0, 5, 10, 10,
    #                                 {"Duration": 12,
    #                                  "Growth": 4,
    #                                  "Damage mod": 1}]
    for e in entities["entities"]:
        if e.team != "Players":
            continue
        if Fun.check_point_in_circle(radius, self.pos[0], self.pos[1], e.pos[0], e.pos[1]):
            self.free_var["Time"] += 1
            #   0 - 60      3
            #  61 - 120     2
            # 121 - 180     1
            # 181 - 240     0
            num = 3 - self.free_var["Time"] // 15
            entities["UI particles"].append(
                Particles.FloatingTextType2([self.pos[0], self.pos[1] - 8], 18,
                                      f"{num}", [Fun.RED, Fun.ORANGE, Fun.YELLOW, Fun.WHITE][num], 1))
            if self.free_var["Time"] >= 60:
                self.alive = False
                Bullets.spawn_bullet(self, entities, Bullets.ExplosionSecondary, self.pos, 0,
                                     self.free_var["Explosion info"])
            return
    self.free_var["Time"] = 0


def landmine_draw(self, WIN, scrolling):
    WIN.blit(Fun.ENTITY_SHADOW, (self.pos[0] - 16 + scrolling[0], self.pos[1] + 1 + scrolling[1]),
             special_flags=pg.BLEND_RGBA_SUB)
    WIN.blit(
        self.sprites[-1],
        (self.pos[0] - 8 + scrolling[0],
         self.pos[1] + scrolling[1])
    )


def dropped_weapon(self, entities, level):
    if self.collision_box.colliderect(self.owner.collision_box) and self.time > 60:
        self.owner.weapon = self.free_var["Weapon"]
        self.owner.weapon_draw_dist = 0
        self.owner.draw_angle = 0
        self.alive = False


def dropped_weapon_draw(self, WIN, scrolling):
    WIN.blit(Fun.ENTITY_SHADOW, (self.pos[0] - 16 + scrolling[0], self.pos[1] + 1 + scrolling[1]),
             special_flags=pg.BLEND_RGBA_SUB)
    WIN.blit(
        self.free_var["Weapon"].sprite,
        (self.pos[0] - 8 + scrolling[0],
         self.pos[1] + scrolling[1])
    )


def mark(self, entities, level):
    self.alive = self.free_var["Victim"].health > 0
    for b in entities["bullets"]:
        if b.team != self.team:
            continue
        if b.laser_based:
            continue
        thick = self.thiccness
        if Fun.collision_rect_circle(self.pos[0] - thick // 2, self.pos[1] - thick // 2, thick, thick,
                                         b.pos[0], b.pos[1], b.radius):
            self.alive = False
            b.duration = 0
            number_of_particle = 18
            for particles_to_add in range(360 // number_of_particle):
                entities["particles"].append(Particles.RandomParticle2(
                    [self.pos[0], self.pos[1]], self.free_var["Colour"],
                    1 + 2 * random.random(), random.randint(15, 60),
                    particles_to_add * number_of_particle,
                    size=Fun.get_random_element_from_list([1, 2, 4])))
            self.free_var["Payload"](self.free_var["Victim"])
            if "Marked Blue Balls" in self.owner.free_var:
                pos = self.free_var["Victim"].pos
                for x in range(4):
                    angle = self.owner.angle + 90 * x
                    Bullets.spawn_blue_balls(self.owner, entities, Fun.move_with_vel_angle(pos, 80, angle -180), angle,
                                             [7, 60, 4, 20, {"Colour": Fun.DARK_BLUE}])

    # Add particles
    pos = self.free_var["Victim"].pos
    for p in range(6):
        entities["particles"].append(Particles.FireParticle(Fun.move_with_vel_angle(pos, self.thiccness * 1.25, 360 * random.random()), self.free_var["Colour"]))


# 	Slow mark          -|- Disable weapon mark 	---	-|-	Stun Mark
# 	Burning mark       -|-	Helping mark	---	---	-|-
def payload_slow(self):
    if "IS BOSS" not in self.free_var:
        self.vel = [0, 0]
    self.status["Slowness"] += 80
    self.status["High friction"] += 40


def payload_burning(self):
    self.status["Burning"] += 40


def payload_disable(self):
    if "IS BOSS" in self.free_var:
        return
    if "Startup lag" in self.free_var:
        self.free_var["Startup lag"] = 0
    self.weapon.ammo = 0
    self.no_shoot_state = 80


def payload_helping(self):
    self.thiccness *= 1.3


def payload_stun(self):
    self.status["Stunned"] += 90
    if "Startup lag" in self.free_var:
        self.free_var["Startup lag"] = 0


def sardine(self, entities, level):
    self.time_is_ticking()
    # Follow target, when in range, starts blow up animation
    if self.free_var["Blow up counter"] == -1:
        target = Bullets.missile_seek(self, entities, 360, self.free_var["Angle"], 75)
        if target:
            self.free_var["Angle"] = Fun.angle_between(target.pos, self.pos)
            self.vel = Fun.move_with_vel_angle([0, 0], 3, self.free_var["Angle"])
            if Fun.distance_between(target.pos, self.pos) < 32:
                self.free_var["Blow up counter"] = 24
        if self.time > self.life_time - 24:
            self.free_var["Blow up counter"] = 24

        # Add some goo
        if self.time % 2 == 0:
            entities["background particles"].append(
                Particles.SquareTransparent([self.pos[0], self.pos[1], random.randint(5, 10), random.randint(1, 3)], (93, 167, 133),
                                            self.life_time, random.randint(64, 160), centered=True)
            )
        # self.animation_counter = self.time // 4 % 4
        self.animation_counter = self.time // 4 % 3
    else:
        # Countdown and boom
        self.animation_counter = self.free_var["Blow up counter"] // 8 % 3
        self.free_var["Blow up counter"] -= 1
        if self.free_var["Blow up counter"] == 0:
            # Sound effects
            Fun.play_sound("Sardine Blows Up")
            Bullets.spawn_bullet(self, entities, Bullets.Melee3, self.pos, 0,
                                 [0, 7, 2, 30, {"Colour": (93, 167, 133), "Growth": 8}])
            self.alive = False


def sardine_draw(self, WIN, scrolling):

    # pg.draw.circle(WIN, (93, 167, 133), [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]], 4)
    # 93, 167, 133
    # self.animation_counter = 0
    # enemy_direction = Fun.get_entity_direction(self.free_var["Angle"])
    WIN.blit(
        self.sprites[Fun.get_entity_direction(self.free_var["Angle"])]["Walk"][self.animation_counter],
        (self.pos[0] - 4 + scrolling[0],
         self.pos[1] - 4+ scrolling[1])
    )


def ballin(self, entities, level):
    if not self.time_is_ticking():
        # some particles
        pass
    # Move
    speed_mod = self.life_time / 120
    self.pos = Fun.move_with_vel_angle(self.free_var["True pos"], 3 * speed_mod, self.free_var["Angle"])
    self.free_var["True pos"] = self.pos.copy()
    self.pos[1] -= 4 * math.sin(self.time * speed_mod * 0.2)
    self.collision_box = pg.Rect(self.pos[0] - self.thiccness / 2, self.pos[1] - self.thiccness / 2,
                                 self.thiccness, self.thiccness)

    # Spawn blue balls
    if self.collision_box.colliderect(self.owner.collision_box):
        for x in range(10):
            Bullets.spawn_blue_balls(
                self.owner, entities,
                [self.owner.pos[0], self.owner.pos[1]],
                self.free_var["Angle"] + 36 * x,
                [4, 230, 7, 30, {"Colour": Fun.DARK_BLUE}])
        self.life_time = 0
        self.alive = False


def ballin_draw(self, WIN, scrolling):
    pg.draw.circle(WIN, Fun.ORANGE, [self.pos[0] + scrolling[0],
                                      self.pos[1] + scrolling[1]], 4)


def justice_homing(self, entities, level):
    self.alive = self.free_var["Bullet"].duration > 0
    manoeuvrability = 4

    self.free_var["Target"] = Bullets.missile_seek(self.free_var["Bullet"], entities,
                                                   320, self.free_var["Bullet"].angle, 45)
    if self.free_var["Target"]:
        target_angle = Fun.angle_between(self.free_var["Target"].pos, self.free_var["Bullet"].pos)
        invert_aim = 1
        if not -(
                180 - manoeuvrability) + target_angle < self.free_var["Bullet"].angle < 180 - manoeuvrability + target_angle:
            invert_aim = -1

        # Adjust angle
        if self.free_var["Bullet"].angle < target_angle:
            self.free_var["Bullet"].angle += manoeuvrability * invert_aim
            if self.free_var["Bullet"].angle > target_angle:
                self.free_var["Bullet"].angle = target_angle
        elif self.free_var["Bullet"].angle > target_angle:
            self.free_var["Bullet"].angle += -manoeuvrability * invert_aim
            if self.free_var["Bullet"].angle < target_angle:
                self.free_var["Bullet"].angle = target_angle

        # Value Limiter
        if self.free_var["Bullet"].angle > 180:
            self.free_var["Bullet"].angle = -180 + (self.free_var["Bullet"].angle - 180)
        if self.free_var["Bullet"].angle < -180:
            self.free_var["Bullet"].angle = 180 - (self.free_var["Bullet"].angle + 180)

        # Add particles
        pos = self.free_var["Bullet"].pos
        for p in range(6):
            entities["particles"].append(Particles.FireParticle(Fun.move_with_vel_angle(pos, self.thiccness * 1.25, 360 * random.random()), Fun.YELLOW))


# print("Sardine")
# for p in Fun.desheetator(Fun.get_image("Sprites/Player/Tomboy/Sardine.png"), 8):
#     print(p)
#     print(len(p))
item_repertory = {
    # |Cover|-----------------------------------------------------------------------------------------------------------
    # |Skill|-----------------------------------------------------------------------------------------------------------
    "Mark": {
        "name": "Mark",
        "friction": 0, "thickness": 0,
        "act": mark,
        "draw": Fun.none,
        "sprites": [],
        "life time": -1,
        "free var": {   # Modify everything here to change effects
            "Victim": None,
            "Colour": Fun.WHITE,
            "Payload": Fun.none
        }
    },
    "Justice": {
        "name": "Justice",
        "friction": 0, "thickness": 0,
        "act": justice_homing,
        "draw": Fun.none,
        "sprites": [],
        "life time": -1,
        "free var": {   # Modify everything here to change effects
            "Bullet": None,
            "Target": None
        }
    },
    "Riot Shield": {
        "name": "Riot Shield",
        "friction": 10,
        "thickness": 16,
        "act": riot_shield,
        "draw": riot_shield_draw,
        "sprites": Fun.SPRITES_RIOT_SHIELD.copy(),
        "life time": 2,
        "free var": {
            "Sprite": 0,
        }
    },
    "Sardine": {
        "name": "Sardine",
        "friction": 1, "thickness": 8,
        "act": sardine,
        "draw": sardine_draw,
        "sprites": Fun.desheetator(Fun.get_image("Sprites/Player/Tomboy/Sardine.png"), 8),
        "life time": 120,
        "free var": {
            "Angle": 0,
            "Blow up counter": -1
        }
    },
    "Ballin": {
        "name": "Ballin",
        "friction": 0, "thickness": 8,
        "act": ballin,
        "draw": ballin_draw,
        "sprites": [],
        "life time": 120,
        "free var": {
            "Angle": None,
            "True pos": [0, 0]
        }
    },
    "Hunk of steel": {
        "name": "Hunk of steel",
        "friction": 10,
        "thickness": 16,
        "act": riot_shield,
        "draw": Fun.none,
        "sprites": False,
        "life time": 2,
        "free var": {
            "Sprite": 0,
        }
    },
    # {"name": "Riot Shield",
    #                                          "thickness": 20,
    #                                          "ai": Items.riot_shield,
    #                                          "effect": False,
    #                                          "bullet effect": False,
    #                                          "free variable": {"target": "players"},
    #                                          "sprites": [Fun.SPRITES_RIOT_SHIELD[player_direction]]},
    #                                         [self.pos[0] - 15 * math.cos(self.aim_angle * math.pi / 180),
    #                                          self.pos[1] - 15 * math.sin(self.aim_angle * math.pi / 180)]))
    "Smoke Grenade": {
        "name": "Smoke Grenade",
        "friction": 0,
        "thickness": 1,
        "act": smoke_grenade,
        "draw": Fun.none,
        "sprites": [],
        "life time": 360,
        "free var": {
            "Radius": 80
        }
    },
    "Jeanne Turret": {
        "name": "Jeanne Turret",
        "friction": 10,
        "thickness": 16,
        "act": jeanne_turret_act,
        "draw": jeanne_turret_draw,
        "sprites": [
            Fun.get_image('Sprites/Items/Jeanne Turret.png').subsurface((00, 00, 16, 16)),
            Fun.get_image('Sprites/Items/Jeanne Turret.png').subsurface((16, 00, 16, 16)),
            Fun.get_image('Sprites/Items/Jeanne Turret.png').subsurface((32, 00, 16, 16)),
            Fun.get_image('Sprites/Items/Jeanne Turret.png').subsurface((48, 00, 16, 16)),
            Fun.get_image('Sprites/Items/Jeanne Turret.png').subsurface((64, 00, 16, 16)),
            Fun.get_image('Sprites/Items/Jeanne Turret.png').subsurface((80, 00, 16, 16)),
            Fun.get_image('Sprites/Items/Jeanne Turret.png').subsurface((96, 00, 16, 16)),
        ],
        "life time": -1,
        "free var": {
            "Health": 5,
            "IFrames": 0,
            "Angle": 0,
            "Handle": 4,
            "Ammo": 25,
            "Fire rate": 18,
            "Bullet info": [7, 40, 4, 15, {"Piercing": False, "Smoke": False}],
            "Bullet type": Bullets.Bullet
            }
        },
    "Jeanne Cover": {
        "name": "Jeanne Cover",
        "friction": 10,
        "thickness": 16,
        "act": jeanne_cover_act,
        "draw": jeanne_cover_draw,
        "sprites": [
            Fun.get_image('Sprites/Items/Jeanne Cover.png'),
        ],
        "life time": -1,
        "free var": {
            "Health": 20,
            "IFrames": 0,
        }
    },
    "Jeanne Demolition Charge": {
        "name": "Jeanne Demolition Charge",
        "friction": 10,
        "thickness": 16,
        "act": jeanne_demolition_charge_act,
        "draw": jeanne_demolition_charge_draw,
        "sprites": [
            Fun.get_image('Sprites/Items/Jeanne Demolition Charge.png'),
        ],
        "life time": -1,
        "free var": {
            "Blowing up": False
        }
    },
    "Zan'dr speen": {
        "name": "Zan'dr speen",
        "friction": 0, "thickness": 0,
        "act": zandr_speen,
        "draw": Fun.none,
        "sprites": [
        ],
        "life time": 30,
        "free var": {}
    },
    "Landmine": {
        "name": "Landmine",
        "friction": 10,
        "thickness": 16,
        "act": landmine,
        "draw": landmine_draw,
        "sprites": [
            Fun.get_image('Sprites/Items/Landmine.png'),
        ],
        "life time": -1,
        "free var": {
            "Time": 0, "Radius": 64,
            "Explosion info": [0, 5, 10, 10, {"Duration": 12, "Growth": 4, "Damage mod": 1}]
        }},
    "Dropped Weapon": {
        "name": "Dropped Weapon",
        "friction": 0.14,
        "thickness": 16,
        "act": dropped_weapon,
        "draw": dropped_weapon_draw,
        "sprites": [],
        "life time": -1,
        "free var": {
            "Weapon": {}
        }},
    "M3-D1C OUT OF MY WAY": {
        "name": "M3-D1C OUT OF MY WAY",
        "friction": 0, "thickness": 0,
        "act": jester_out_of_my_way,
        "draw": Fun.none,
        "sprites": [
        ],
        "life time": 30,
        "free var": {}
    },
}

