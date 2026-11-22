import random
import Fun
import Bullets
import Particles

from Entity import start_up_lag_handler



# ||THR-1's Assault||---------------------------------------------------------------------------------------------------
# |Gilgamesh|-----------------------------------------------------------------------------------------------------------
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


# |Fire Support Mech|---------------------------------------------------------------------------------------------------
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

# |Rigel|

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
