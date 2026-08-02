import math
import pygame as pg
import random
import Fun
import Items
import Particles


def spawn_bullet(owner, entities, bullet_class, pos, angle, bullet_info):
    entities["bullets"].append(bullet_class(pos, angle, bullet_info, owner))
    owner.bullets_shot.append(entities["bullets"][-1])


class BasicBullet:
    def __init__(self, pos, angle, info, owner):
        self.owner = owner
        self.og_info = info
        self.original_angle = angle
        self.pos = pos
        self.angle = angle
        self.speed = info[0]
        self.duration = info[1]
        self.radius = info[2]
        self.damage = info[3]
        self.colour = Fun.AMBER_LIGHT
        self.visual_effect = basic_visual
        if "Colour" in info[4]:
            self.colour = info[4]["Colour"]
        self.on_hit = []
        if "On hit" in info[4]:
            self.on_hit = info[4]["On hit"]

        self.team = self.owner.team
        self.ignore_res = False

        self.wall_physics = normal_bullet_wall_hit
        self.free_var = {}

    def hit_wall(self, entities, level):
        self.wall_physics(self, level,  entities)

    def move_with_vel(self):
        angle = self.angle * math.pi / 180
        self.pos[0] -= self.speed * math.cos(angle)
        self.pos[1] -= self.speed * math.sin(angle)

    def on_hit_handler(self, collision, entities, level):
        for on_hit_effect in self.on_hit:
            on_hit_effect(self, collision, entities, level)

    def draw(self, win, scrolling):
        if self.duration > 0:
            pg.draw.circle(win, self.colour, [self.pos[0] + scrolling[0],
                                              self.pos[1] + scrolling[1]], self.radius)
            # Highlight effect
            # highlight_radius = self.radius * 3
            # Fun.draw_transparent_circle(win, [self.pos[0] + scrolling[0] - highlight_radius / 2,
            #                                   self.pos[1] + scrolling[1] - highlight_radius / 2,  highlight_radius],
            #                             (255 - self.colour[0], 255 - self.colour[1], 255 - self.colour[2]),
            #                             # (255, 255, 255),
            #                             32, width=round(highlight_radius/4))


# |Blue Ball Stuff|-----------------------------------------------------------------------------------------------------
def spawn_blue_balls(owner, entities, pos, angle, bullet_info):
    entities["bullets"].append(BlueBall(pos, angle, bullet_info, owner))
    if "Blue Balls" in owner.free_var:
        for bb in owner.free_var["Blue Balls"]:
            {
                "Seeking Blue Balls": blue_ball_seeking,
                "Homing Blue Balls": blue_ball_homing,
                "Bouncing Blue Balls": blue_ball_bouncing,
                "Bouncy Blue Balls": blue_ball_bouncy,

                "Speeding Blue Balls": blue_ball_speeding,
                "Piercing Blue Balls": blue_ball_piercing,
                "Durable Blue Balls": blue_ball_durable,
                "XX, Le Jugement": blue_ball_judgement
            }[bb](entities["bullets"][-1])


def blue_ball_seeking(self):
    self.targeting_time = 60


def blue_ball_homing(self):
    self.targeting_time = 0
    self.manoeuvrability = 9
    self.pos = Fun.random_point_in_circle(self.pos, 16)


def blue_ball_speeding(self):
    self.slowdown_rate = self.radius * 0.0125  * -1


def blue_ball_piercing(self):
    self.piercing = True


def blue_ball_durable(self):
    self.duration = round(self.duration * 1.75)


def blue_ball_bouncing(self):
    self.wall_physics = base_grenade_wall_hit


def blue_ball_bouncy(self):
    self.wall_physics = bouncy_blue_wall_hit


def blue_ball_judgement(self):
    self.secondary_explosion = {"Duration": 5, "Growth": 2, "Damage mod": 0.75}


class BlueBall(BasicBullet):
    # Somewhat based on the Even Coolest bullet type
    def __init__(self, pos, angle, info, owner):
        BasicBullet.__init__(self, pos, angle, info, owner)
        self.fire = False
        self.explosion_primer = False
        self.explosion = False
        self.laser = False
        self.laser_based = False
        self.melee = False

        self.angle_deviation = 0
        self.piercing = False

        self.slowdown_rate = 0

        self.damage_type = "Melee"  # Change that

        self.targeting_time = 0
        self.targeting_range = 256
        self.manoeuvrability = 0
        self.targeting_angle = 360
        self.move_angle = self.angle
        self.target_pos = False
        self.secondary_explosion = False

    def act(self, entities, level):
        # Spends some time homing on a target
        if self.targeting_time > 0:

            target = Fun.find_closest_in_circle(self, entities, self.targeting_range, "entities")
            if target:
                self.move_angle = Fun.angle_between(target, self.pos)
            self.targeting_time -= 1
            if self.targeting_time == 0:
                Fun.play_sound("Sword launch")

        # Stuff
        elif self.duration > 0:
            # Make the bullet move based on the angle
            self.angle += self.angle_deviation

            # Move rotation center

            if self.manoeuvrability > 0:
                if self.duration % 3 == 0:
                    target = missile_seek(self, entities, self.targeting_range, self.angle,
                                          self.targeting_angle)
                    if target:
                        self.target_pos = target.pos
                if self.target_pos:

                    if self.duration % random.randint(5, 8) == 0:
                        entities["particles"].append(Particles.Smoke([self.pos[0], self.pos[1]], colour=Fun.DARK_BLUE))
                    self.angle = Fun.angle_between(self.target_pos, self.pos)

                    invert_aim = 1
                    if not -(
                            180 - self.manoeuvrability) + self.angle < self.move_angle < 180 - self.manoeuvrability + self.angle:
                        invert_aim = -1

                    # Adjust angle
                    if self.move_angle < self.angle:
                        self.move_angle += self.manoeuvrability * invert_aim
                        if self.move_angle > self.angle:
                            self.move_angle = self.angle
                    elif self.move_angle > self.angle:
                        self.move_angle += -self.manoeuvrability * invert_aim
                        if self.move_angle < self.angle:
                            self.move_angle = self.angle

                    # Value Limiter
                    if self.move_angle > 180:
                        self.move_angle = -180 + (self.move_angle - 180)
                    if self.move_angle < -180:
                        self.move_angle = 180 - (self.move_angle + 180)

            self.pos[0] -= self.speed * math.cos(self.move_angle * math.pi / 180)
            self.pos[1] -= self.speed * math.sin(self.move_angle * math.pi / 180)

            bullet_slowdown(self)

            # Check for collisions
            for collision in entities["entities"]:
                if self.owner.team == collision.team:
                    continue
                if Fun.collision_rect_circle(collision.collision_box.left, collision.collision_box.top,
                                             collision.collision_box.width, collision.collision_box.height,
                                             self.pos[0], self.pos[1], self.radius):
                    Fun.damage_calculation(collision, self.damage, self.damage_type, death_message="Got defeated by a Yokai")
                    self.on_hit_handler(collision, entities, level)

                    self.visual_effect(self, entities)

                    if not self.piercing:
                        self.duration = 1
            self.duration -= 1
        if self.duration == 0:
            if self.secondary_explosion:
                spawn_bullet(
                    self.owner, entities,
                    ExplosionSecondary,
                    self.pos,
                    self.angle,
                    [0, 5, self.radius, self.damage, self.secondary_explosion])
        #


missile = pg.image.load("Sprites/Bullets/Missile.png").convert_alpha()
grenade_1 = pg.image.load("Sprites/Bullets/Grenade.png").convert_alpha()
grenade_2 = pg.image.load("Sprites/Bullets/Grenade Incendiary.png").convert_alpha()
grenade_3 = pg.image.load("Sprites/Bullets/Grenade Smoke.png").convert_alpha()
grenade_4 = pg.image.load("Sprites/Bullets/Grenade Flashbang.png").convert_alpha()
grenade_5 = pg.image.load("Sprites/Bullets/Grenade Shrapnel.png").convert_alpha()
grenade_6 = pg.image.load("Sprites/Bullets/Grenade Mark.png").convert_alpha()
grenade_c4 = pg.image.load("Sprites/Weapon/C4.png").convert_alpha()


# This should make it easier to make some changes
def base_grenade_act(self, entities):
    # Make the bullet move based on the angle
    self.pos[0] -= self.speed * math.cos(self.angle * math.pi / 180)
    self.pos[1] -= self.speed * math.sin(self.angle * math.pi / 180)
    if self.speed > 0:
        self.speed -= 0.05
        if self.speed < 0:
            self.speed = 0

    # Check for collisions
    for collision in entities["entities"]:
        if collision.team == self.team:
            continue
        if Fun.collision_rect_circle(collision.collision_box.left, collision.collision_box.top,
                                     collision.collision_box.width, collision.collision_box.height,
                                     self.pos[0], self.pos[1], self.radius):
            Fun.damage_calculation(collision, self.damage, self.damage_type, death_message="Limbs blown up")
            self.duration = 1
            boom_visual(self, entities)

    self.duration -= 1


fire_ran_spread = [0, []]
for fire_randomizer in range(100):
    fire_ran_spread[1].append(random.uniform(-2, 2))


def fire_randomize_pos(self):
    # Make the bullet move based on the angle
    self.pos[0] -= fire_ran_spread[1][self.duration % 100]
    self.pos[1] -= fire_ran_spread[1][(self.duration + 55) % 100]
    self.pos = Fun.move_with_vel_angle(self.pos, self.speed, self.angle)


def bullet_slowdown(self):
    if self.speed > 0:
        self.speed -= self.slowdown_rate
        if self.speed < 0:
            self.speed = 0


# Wall hit physics
def normal_bullet_wall_hit(self, level, entities):
    for wall in level["map"]:
        if Fun.collision_rect_circle(wall.left, wall.top, wall.width, wall.height,
                                     self.pos[0], self.pos[1], self.radius):
            # Give effects when the bullets hit walls, mostly visual
            self.duration = 0
            Fun.play_sound("Bullet hitting wall 1", "SFX")
            entities["sounds"].append(  # [pos, duration, radius]
                Fun.Sound(self.pos, Fun.sounds_dict["Bullet hitting wall 1"]["Sound"].get_length() * 60, 500 * 0.5 + 50)
            )
            Particles.sparks(entities, self.pos, [self.duration, self.radius, self.speed], self.angle)
            if wall.left < self.pos[0] < wall.right and self.pos[1] > wall.bottom - 8:
                entities["background particles"].append(Particles.BulletHole([self.pos[0], wall.bottom - 8]))


def fire_bullet_wall_hit(self, level, entities):
    for wall in level["map"]:
        if Fun.collision_rect_circle(wall.left, wall.top, wall.width, wall.height,
                                     self.pos[0], self.pos[1],
                                     self.radius):
            # Give effects when the bullets hit walls, mostly visual
            self.duration = 0
            Particles.flame_burst(entities, self.pos,
                            [self.duration,
                             self.radius,
                             self.speed], self.angle, self.colour)


def explosive_bullet_wall_hit(self, level, entities):
    for wall in level["map"]:
        if Fun.collision_rect_circle(wall.left, wall.top, wall.width, wall.height,
                                     self.pos[0], self.pos[1],
                                     self.radius):
            self.duration = 1


def base_grenade_wall_hit(self, level, entities):
    # makes the projectile bounce off the wall
    for wall in level["map"]:
        if Fun.collision_rect_circle(wall.left, wall.top, wall.width, wall.height, self.pos[0], self.pos[1],
                                     self.radius):
            # Get the velocity has a list
            target = Fun.move_with_vel_angle([0, 0], self.speed, self.angle)
            Fun.play_sound("Grenade hit wall", "SFX")

            # Find in which direction the bullet must bounce
            if self.pos[0] - self.radius < wall.left or self.pos[0] + self.radius > wall.right:
                target[0] *= -1
            if self.pos[1] - self.radius < wall.top or self.pos[1] + self.radius > wall.bottom:
                target[1] *= -1

            # Get the final angle for the bullet
            final_target = [self.pos[0] + target[0], self.pos[1] + target[1]]
            self.angle = Fun.angle_between(final_target, self.pos)
            # Funny line
            # self.speed *= 2
            return


def bouncy_blue_wall_hit(self, level, entities):
    # makes the projectile bounce off the wall
    for wall in level["map"]:
        if Fun.collision_rect_circle(wall.left, wall.top, wall.width, wall.height, self.pos[0], self.pos[1],
                                     self.radius):
            # Get the velocity has a list
            target = Fun.move_with_vel_angle([0, 0], self.speed, self.angle)
            Fun.play_sound("Grenade hit wall", "SFX")

            # Find in which direction the bullet must bounce
            if self.pos[0] - self.radius < wall.left or self.pos[0] + self.radius > wall.right:
                target[0] *= -1
            if self.pos[1] - self.radius < wall.top or self.pos[1] + self.radius > wall.bottom:
                target[1] *= -1

            # Get the final angle for the bullet
            final_target = [self.pos[0] + target[0], self.pos[1] + target[1]]
            self.angle = Fun.angle_between(final_target, self.pos)
            # Funny line
            self.speed *= 1.25
            return


def bouncy_missile_wall_hit(self, level, entities):
    # self.move_angle
    # makes the projectile bounce off the wall
    for wall in level["map"]:
        if Fun.collision_rect_circle(wall.left, wall.top, wall.width, wall.height, self.pos[0], self.pos[1],
                                     self.radius):
            # Get the velocity has a list
            target = Fun.move_with_vel_angle([0, 0], self.speed, self.move_angle)
            Fun.play_sound("Grenade hit wall", "SFX")

            # Find in which direction the bullet must bounce
            if self.pos[0] - self.radius < wall.left or self.pos[0] + self.radius > wall.right:
                target[0] *= -1
            if self.pos[1] - self.radius < wall.top or self.pos[1] + self.radius > wall.bottom:
                target[1] *= -1

            # Get the final angle for the bullet
            final_target = [self.pos[0] + target[0], self.pos[1] + target[1]]
            self.move_angle = Fun.angle_between(final_target, self.pos)
            # Funny line
            # self.speed *= 2
            return


def condor_ricochet_wall_hit(self, level, entities):
    # self.move_angle
    # makes the projectile bounce off the wall
    for wall in level["map"]:
        if Fun.collision_rect_circle(wall.left, wall.top, wall.width, wall.height, self.pos[0], self.pos[1],
                                     self.radius):
            # Get the velocity has a list
            target = Fun.move_with_vel_angle([0, 0], self.speed, self.angle)
            Fun.play_sound("Grenade hit wall", "SFX")

            # Find in which direction the bullet must bounce
            if self.pos[0] - self.radius < wall.left or self.pos[0] + self.radius > wall.right:
                target[0] *= -1
            if self.pos[1] - self.radius < wall.top or self.pos[1] + self.radius > wall.bottom:
                target[1] *= -1

            # Get the final angle for the bullet
            final_target = [self.pos[0] + target[0], self.pos[1] + target[1]]
            self.angle = Fun.angle_between(final_target, self.pos)
            new_bullet_info = self.og_info.copy()
            self.duration += 15
            self.radius *= 0.75
            if self.radius < 2:
                continue
            new_bullet_info[1] = self.duration
            new_bullet_info[2] = self.radius
            angle = Fun.angle_value_limiter(self.angle + random.randint(-15, 15))
            spawn_bullet(self.owner, entities, type(self), Fun.move_with_vel_angle(self.pos, 20, angle),
                         angle, new_bullet_info)
            # if entities["bullets"][-1] not in self.owner.bullets_shot:
            #     self.owner.bullets_shot.append(entities["bullets"][-1])
            # Funny line
            # self.speed *= 2


def melee_bullet_wall_hit(self, level, entities):
    pass
    # for wall in level["map"]:
    #     if Fun.collision_rect_circle(wall.left, wall.top, wall.width, wall.height,
    #                                  self.pos[0], self.pos[1],
    #                                  self.radius):
    #         # Give effects when the bullets hit walls, mostly visual
    #         self.duration = 0


# On hit visual effects
def basic_visual(self, entities):
    for x in range(3):
        size = self.damage / 3 * random.random() + 1
        if size > 16:
            size = 16
        entities["particles"].append(Particles.RandomParticle2(
            self.pos.copy(), self.colour, self.speed * (0.25 + 0.5 * random.random()),
            random.randint(8, 32), self.angle + random.uniform(-7.5, 7.5), size=size))


def fire_visual(self, entities):
    for x in range(2):
        size = self.damage / 3 * random.random()
        entities["particles"].append(Particles.RandomParticle1(
            [self.pos[0] + random.randint(-3, 3), self.pos[1]], self.colour,
            self.speed * (0.25 + 0.5 * random.random()) * -1,
            random.randint(8, 32), size=[size, size]))


def boom_visual(self, entities):
    for x in range(3):
        size = self.damage / 3 * random.random()
        if size > 16:
            size = 16
        entities["particles"].append(Particles.RandomParticle2(
            self.pos.copy(), self.colour, self.speed * (1 + random.random()),
            random.randint(8, 32), self.angle + random.uniform(-7.5, 7.5), size=size))


def melee_visual(self, entities):
    pass


def laser_visual(self, entities, pos):
    for x in range(8):
        entities["particles"].append(Particles.LineParticle(
            pos.copy(),
            self.colour,
            random.randint(8, 32),
            self.damage / 3 * random.random(),
            self.angle + random.uniform(-7.5, 7.5) + (22.5 + x * 45),
            vel=2, width=1))


def electric_visual(self, entities):
    pass


def countered_visual(self, entities):
    Particles.random_particle_2_circle(entities, self.pos, random.uniform(1.5, 3), 20, 36,
                                 colour=Fun.PARRIED_COLOUR, size=4, angle_mod=self.angle)


def missile_seek(self, entities, targeting_range, angle, targeting_angle):
    dist = targeting_range
    target = False
    for e in entities["entities"]:
        if e.team == self.team or e.status["Stealth"] > 0:
            continue
        if Fun.check_point_in_cone(dist, self.pos[0], self.pos[1], e.pos[0], e.pos[1], angle, targeting_angle):
            # check_point_in_circle(dist, self.pos[0], self.pos[1], e.pos[0], e.pos[1]):
            dist = round(math.hypot(e.pos[0] - self.pos[0], e.pos[1] - self.pos[1]))
            target = e
    return target


# |On Hit functions|----------------------------------------------------------------------------------------------------
def on_hit_stun_baton(self, collision, entities, level):
    if collision.status["Stunned"] > 0:
        if collision.damage_taken and collision.status["No damage"] == 8:

            collision.status["Stunned"] += 15
            Particles.random_particle_2_circle(entities, collision.pos, 3, 25, 16, colour=Fun.YELLOW, size=3, angle_mod=180 * random.random())


def on_hit_marked(self, collision, entities, level):
    if collision.status["Visible"] <= 60:
        collision.status["Visible"] = 60
    entities["particles"].append(Particles.GrowingCircle(collision.pos, Fun.DARK_GREEN, 0, 60, collision.thiccness, 2))


def on_hit_scavenge(self, collision, entities, level):
    if collision.health <= 0:
        self.owner.weapon.ammo += 1


def on_hit_intimidation(self, collision, entities, level):
    # On hit, enemies have a 25% chance to get the inacuracy debuff for 10 sec
    if random.random() < 0.25:
        collision.status["Low Aim"] += 90

        for x in range(5):
            pos = Fun.random_point_in_circle(collision.pos, 16)
            entities["particles"].append(
                Particles.RandomParticle1(pos, Fun.GRAY, 2, round(10 + 10 * random.random()),
                                    size=(2, 4))
        )


def on_hit_fear(self, collision, entities, level):
    # On hit, enemies have a 25% chance to get the inacuracy debuff for 10 sec
    if random.random() < 0.25:
        collision.status["Less auto"] += 600

        for x in range(5):
            pos = Fun.random_point_in_circle(collision.pos, 16)
            entities["particles"].append(
                Particles.RandomParticle1(pos, Fun.LIGHT_BLUE, 2, round(10 + 10 * random.random()),
                                    size=(2, 4))
        )


def on_hit_spread(self, collision, entities, level):
    if collision.health <= 0:
        for e in entities["entities"]:
            if e.team == self.team:
                continue
            if Fun.distance_between(self.pos, e.pos) < 256:
                for debuff in Fun.DEBUFFS_NAMES:
                    e.status[debuff] += collision.status[debuff]


def on_hit_i_see_you(self, collision, entities, level):
    if "IS BOSS" in collision.free_var:
        return
    if collision.status["Visible"]:
        Fun.damage_calculation(collision, self.damage, self.damage_type, ignore_res=self.ignore_res, death_message="Got defeated by a Yokai",
                               ignore_no_damage=True, no_iframes=True)
        # Make sure the scavenge effect works
        if on_hit_scavenge in self.on_hit:
            on_hit_scavenge(self, collision, entities, level)


def on_hit_cremation(self, collision, entities, level):
    if collision.status["Visible"] <= 45:
        collision.status["Visible"] = 45


def on_hit_big_iron(self, collision, entities, level):
    Particles.random_particle_2_circle(entities, self.owner.pos, 3, 25, 36, colour=Fun.YELLOW, size=3, angle_mod=180 * random.random())
    self.owner.skills[0].recharge += self.owner.skills[0].recharge_max * 0.75
    if self.owner.skills[0].recharge > self.owner.skills[0].recharge_max:
        self.owner.skills[0].recharge = self.owner.skills[0].recharge_max


def on_hit_3rd_degree(self, collision, entities, level):
    if collision.status["Burning"] <= 60:
        collision.status["Burning"] += 60
    Particles.random_particle_2_circle(entities, collision.pos, 3, 25, 16, colour=Fun.FIRE, size=6, angle_mod=180 * random.random())


def on_hit_shrapnel(self, collision, entities, level):
    if not (collision.damage_taken and collision.status["No damage"] == 8):
        return
    for x in range(7 * 3):
        spawn_bullet(
            self, entities,
            Bullet,
            [self.pos[0], self.pos[1]],
            360 * random.random(),
            [random.uniform(2, 6), 70, random.uniform(2, 5),
             10, {"Piercing": True}])


def on_hit_stun_strike(self, collision, entities, level):
    if not (collision.damage_taken and collision.status["No damage"] == 8):
        return
    mod = 60
    if "Discombobulate" in self.owner.free_var:
        mod = 100
    if collision.status["Stunned"] <= mod:
        collision.status["Stunned"] = mod
    Particles.random_particle_2_circle(entities, self.pos, 3, 25, 16, colour=Fun.YELLOW, size=6, angle_mod=180 * random.random())
    if "Concussion" in self.owner.free_var:
        self.owner.agro -= 1


def on_hit_poison_strike(self, collision, entities, level):
    if not (collision.damage_taken and collision.status["No damage"] == 8):
        return
    if collision.status["Low res"] <= 180:
        collision.status["Low res"] = 180
    if collision.status["Damage Over time"] <= 300:
        collision.status["Damage Over time"] = 300
    if "Infection" in self.owner.free_var:
        if collision.status["Slowness"] <= 300:
            collision.status["Slowness"] = 300
            for x in range(3):
                pos = Fun.random_point_in_circle(collision.pos, 16)
                entities["particles"].append(
                    Particles.RandomParticle1(pos, Fun.GRAY, 2, round(10 + 10 * random.random()), size=(2, 4)))
    if "Neurotoxin" in self.owner.free_var:
        if collision.did_agro_raise == 0:
            collision.agro += 30
            collision.did_agro_raise = 60
            for x in range(3):
                pos = Fun.random_point_in_circle(collision.pos, 16)
                entities["particles"].append(
                    Particles.RandomParticle1(pos, Fun.DARK_RED, -2, round(10 + 10 * random.random()), size=(2, 4)))

    Particles.random_particle_2_circle(entities, self.pos, 3, 25, 16, colour=Fun.DARK_TEAL, size=6, angle_mod=180 * random.random())



def on_hit_weaken(self, collision, entities, level):
    if collision.status["Visible"] <= 45:
        collision.status["Visible"] = 45
    if collision.status["Low res"] <= 45:
        collision.status["Low res"] = 45


def on_hit_sun(self, collision, entities, level):
    if not (collision.damage_taken and collision.status["No damage"] == 8):
        return
    mod = 60
    if collision.status["Stunned"] <= mod:
        collision.status["Stunned"] = mod
    Particles.random_particle_2_circle(entities, self.pos, 3, 25, 16, colour=Fun.YELLOW, size=6, angle_mod=180 * random.random())


def on_hit_temperance(self, collision, entities, level):
    if not collision.armour_break:
        return
    self.owner.armour += 8

    if self.owner.armour > self.owner.max_armour:
        self.owner.armour = self.owner.max_armour


def on_hit_death(self, collision, entities, level):
    if collision.health > 0:
        return
    self.owner.health += 10

    if self.owner.health > self.owner.max_health:
        self.owner.health = self.owner.max_health


def on_hit_burning_blue_balls(self, collision, entities, level):
    if collision.status["Burning"] > 0:
        for x in range(2):
            spawn_blue_balls(
                self.owner, entities,
                Fun.random_point_in_donut(self.owner.pos, [16, 32]),
                self.angle + random.randint(-66, 66),
                [5, 100, 3, 10, {"Colour": Fun.DARK_BLUE}])


def on_hit_and_stay_back(self, collision, entities, level):
    if "IS BOSS" in collision.free_var:
        return
    collision.vel = Fun.move_with_vel_angle(collision.vel, self.speed * collision.friction, self.angle)


def on_hit_burning_mark(self, collision, entities, level):
    if random.random() <= 0.25 and "Has Burning Mark" not in collision.free_var:
        collision.free_var.update({"Has Burning Mark": True})
        self.duration = 0
        Items.spawn_item(entities, "Mark", collision.pos, self.owner)
        entities["items"][-1].free_var["Victim"] = collision
        entities["items"][-1].free_var["Colour"] = Fun.ORANGE
        entities["items"][-1].thiccness = collision.thiccness * 1.2
        entities["items"][-1].free_var["Payload"] = Items.payload_burning
        for count, e in enumerate(self.on_hit):
            if e == on_hit_burning_mark:
                self.on_hit.pop(count)
                break


def on_hit_stun_mark(self, collision, entities, level):
    if self.owner.weapon.ammo == 0:
        Items.spawn_item(entities, "Mark", collision.pos, self.owner)
        entities["items"][-1].free_var["Victim"] = collision
        entities["items"][-1].free_var["Colour"] = Fun.YELLOW
        entities["items"][-1].thiccness = collision.thiccness * 1.2
        entities["items"][-1].free_var["Payload"] = Items.payload_stun


def on_hit_carcass(self, collision, entities, level):
    collision.status["Damage Over time"] += 60
    number_of_particle = 12
    for particles_to_add in range(360 // number_of_particle):
        entities["particles"].append(Particles.RandomParticle2(
            [collision.pos[0], collision.pos[1]], (146, 255, 110), 1 + 2 * random.random(), random.randint(5, 15),
            particles_to_add * number_of_particle, size=Fun.get_random_element_from_list([1, 2 ,4])))


def on_hit_hellfire(self, collision, entities, level):
    collision.status["Burning"] += 60
    for x in range(8):
        entities["particles"].append(Particles.FireParticle(collision.pos, self.owner.weapon.free_var["Colour"]))


def on_hit_iguanas_tail(self, collision, entities, level):
    if collision.damage_taken and collision.status["No damage"] == 8:
        collision.status["Stunned"] += 15
        # Particles.random_particle_2_circle(entities, collision.pos, 3, 25, 16, colour=Fun.YELLOW, size=3, angle_mod=180 * random.random())


# |The simplest projectile|---------------------------------------------------------------------------------------------
class Bullet(BasicBullet):
    def __init__(self, pos, angle, info, owner):
        BasicBullet.__init__(self, pos, angle, info, owner)
        self.fire = False
        self.explosion_primer = False
        self.explosion = False
        self.laser = False
        self.laser_based = False
        self.melee = False

        self.piercing = False
        if "Piercing" in info[4]:
            self.piercing = info[4]["Piercing"]
        self.smoke_effect = False
        if "Smoke" in info[4]:
            self.smoke_effect = info[4]["Smoke"]
        if "Damage type" in info[4]:
            self.damage_type = info[4]["Damage type"]
        else:
            self.damage_type = "Physical"

    def act(self, entities, level):
        if self.duration > 0:
            # Make the bullet move based on the angle

            self.move_with_vel()

            # Visual effect for bullets that go fast
            if self.smoke_effect and self.duration % random.randint(3, 5) == 0:
                entities["particles"].append(Particles.Smoke([self.pos[0], self.pos[1]]))

            # Check for collisions
            for collision in entities["entities"]:
                if self.owner.team == collision.team:
                    continue
                if Fun.collision_rect_circle(collision.collision_box.left, collision.collision_box.top,
                                             collision.collision_box.width, collision.collision_box.height,
                                             self.pos[0], self.pos[1], self.radius):
                    if Fun.damage_calculation(collision, self.damage, self.damage_type, ignore_res=self.ignore_res, death_message="Is Swiss cheese"):
                        self.visual_effect(self, entities)
                    self.on_hit_handler(collision, entities, level)


                    if not self.piercing:
                        self.duration = 0

            self.duration -= 1

        # pg.draw.circle(win, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
        # [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]], self.radius)


class BulletSlowing(BasicBullet):
    def __init__(self, pos, angle, info, owner):
        BasicBullet.__init__(self, pos, angle, info, owner)
        self.fire = False
        self.explosion_primer = False
        self.explosion = False
        self.laser = False
        self.laser_based = False
        self.melee = False

        self.piercing = False
        if "Piercing" in info[4]:
            self.piercing = info[4]["Piercing"]
        self.smoke_effect = False
        if "Smoke" in info[4]:
            self.smoke_effect = info[4]["Smoke"]
        if "Damage type" in info[4]:
            self.damage_type = info[4]["Damage type"]
        else:
            self.damage_type = "Physical"
        self.slowdown_rate = 0.05
        if "Slowdown rate" in info[4]:
            self.slowdown_rate = info[4]["Slowdown rate"]

    def act(self, entities, level):
        if self.duration > 0:
            self.move_with_vel()
            bullet_slowdown(self)

            # Check for collisions
            for collision in entities["entities"]:
                if self.owner.team == collision.team:
                    continue
                if Fun.collision_rect_circle(collision.collision_box.left, collision.collision_box.top,
                                             collision.collision_box.width, collision.collision_box.height,
                                             self.pos[0], self.pos[1], self.radius):
                    if Fun.damage_calculation(collision, self.damage, self.damage_type, death_message="Is Swiss cheese"):
                        self.visual_effect(self, entities)
                    self.on_hit_handler(collision, entities, level)
                    self.duration = 1

            self.duration -= 1

            # Visual effect for bullets that go fast
            if self.smoke_effect and self.duration % random.randint(3, 5) == 0:
                entities["particles"].append(Particles.Smoke([self.pos[0], self.pos[1]]))


class BulletHoming(Bullet):
    def __init__(self, pos, angle, info, owner):
        Bullet.__init__(self, pos, angle, info, owner)
        self.wall_physics = Fun.none

        # targeting stuff
        self.targeting_range = info[4]["Targeting range"]
        self.targeting_angle = info[4]["Targeting angle"]
        self.target = False

        self.manoeuvrability = 4
        if "Manoeuvrability" in info[4]:
            self.manoeuvrability = info[4]["Manoeuvrability"]

        self.move_angle = self.angle
        self.target_pos = False
        if "Damage type" in info[4]:
            self.damage_type = info[4]["Damage type"]
        else:
            self.damage_type = "Energy"

    def act(self, entities, level):
        if self.duration > 0:
            # Now the missiles have a "max locking angle"
            if self.duration % 3 == 0:
                target = missile_seek(self, entities, self.targeting_range, self.angle,
                                                  self.targeting_angle)
                if target:
                    self.target_pos = target.pos
            if self.target_pos:

                if self.duration % random.randint(5, 8) == 0:
                    entities["particles"].append(Particles.Smoke([self.pos[0], self.pos[1]], colour=[
                        Fun.WHITE, Fun.GRAY, self.colour
                    ][random.randint(0, 2)]
                                                           ))
                self.angle = Fun.angle_between(self.target_pos, self.pos)

                invert_aim = 1
                if not -(
                        180 - self.manoeuvrability) + self.angle < self.move_angle < 180 - self.manoeuvrability + self.angle:
                    invert_aim = -1

                # Adjust angle
                if self.move_angle < self.angle:
                    self.move_angle += self.manoeuvrability * invert_aim
                    if self.move_angle > self.angle:
                        self.move_angle = self.angle
                elif self.move_angle > self.angle:
                    self.move_angle += -self.manoeuvrability * invert_aim
                    if self.move_angle < self.angle:
                        self.move_angle = self.angle

                # Value Limiter
                if self.move_angle > 180:
                    self.move_angle = -180 + (self.move_angle - 180)
                if self.move_angle < -180:
                    self.move_angle = 180 - (self.move_angle + 180)

            # Make the bullet move based on the angle
            self.pos[0] -= self.speed * math.cos(self.move_angle * math.pi / 180)
            self.pos[1] -= self.speed * math.sin(self.move_angle * math.pi / 180)

            # Check for collisions
            for collision in entities["entities"]:
                if self.owner.team == collision.team:
                    continue

                if Fun.collision_rect_circle(collision.collision_box.left, collision.collision_box.top,
                                             collision.collision_box.width, collision.collision_box.height,
                                             self.pos[0], self.pos[1], self.radius):
                    Fun.damage_calculation(collision, self.damage, self.damage_type, death_message="Chased by a bullet")
                    self.on_hit_handler(collision, entities, level)

                    self.duration = 0
                    self.visual_effect(self, entities)

            self.duration -= 1

    def draw(self, win, scrolling):
        if self.duration > 0:
            pg.draw.circle(win, self.colour, [self.pos[0] + scrolling[0],
                                              self.pos[1] + scrolling[1]], self.radius)
            # Highlight effect
            highlight_radius = self.radius * 3
            Fun.draw_transparent_circle(win, [self.pos[0] + scrolling[0] - highlight_radius / 2,
                                                self.pos[1] + scrolling[1] - highlight_radius / 2,  highlight_radius],
                                        (255 - self.colour[0], 255 - self.colour[1], 255 - self.colour[2]), # (255, 255, 255),
                                        32, width=round(highlight_radius/4))


class BulletDanmaku(BasicBullet):
    def __init__(self, pos, angle, info, owner):
        BasicBullet.__init__(self, pos, angle, info, owner)
        self.fire = False
        self.explosion_primer = False
        self.explosion = False
        self.laser = False
        self.laser_based = False
        self.melee = False
        # {"Angle deviation": 0, "Slowdown rate": 0}
        self.angle_deviation = 0
        if "Angle deviation" in info[4]:
            self.angle_deviation = info[4]["Angle deviation"]

        self.slowdown_rate = 0
        if "Slowdown rate" in info[4]:
            self.slowdown_rate = info[4]["Slowdown rate"]

        if "Damage type" in info[4]:
            self.damage_type = info[4]["Damage type"]
        else:
            self.damage_type = "Physical"

    def act(self, entities, level):
        if self.duration > 0:
            # Make the bullet move based on the angle
            self.angle += self.angle_deviation
            self.pos = Fun.move_with_vel_angle(self.pos, self.speed, self.angle)

            bullet_slowdown(self)

            # Check for collisions
            for collision in entities["entities"]:
                if Fun.collision_rect_circle(collision.collision_box.left, collision.collision_box.top,
                                             collision.collision_box.width, collision.collision_box.height,
                                             self.pos[0], self.pos[1], self.radius):
                    if Fun.damage_calculation(collision, self.damage, self.damage_type, death_message="Got defeated by a Yokai"):
                        self.visual_effect(self, entities)
                    self.on_hit_handler(collision, entities, level)


                    self.duration = 0

            self.duration -= 1


# NOTTODO: Rewrite Danmaku bullets so that they don't crash the game, isn't a priority until I need them for a boss
# Not using that for bosses
class BulletDanmaku2(BasicBullet):
    # Coolest bullet type
    def __init__(self, pos, angle, info, owner):
        BasicBullet.__init__(self, pos, angle, info, owner)
        self.fire = False
        self.explosion_primer = False
        self.explosion = False
        self.laser = False
        self.laser_based = False
        self.melee = False
        self.angle_deviation = 0
        if "Angle deviation" in info[4]:
            self.angle_deviation = info[4]["Angle deviation"]

        self.slowdown_rate = 0
        if "Slowdown rate" in info[4]:
            self.slowdown_rate = info[4]["Slowdown rate"]

        if "Damage type" in info[4]:
            self.damage_type = info[4]["Damage type"]
        else:
            self.damage_type = "Physical"

        self.bullet_mod = []
        # Format [
        # {
        #   "Target time": 0,
        #   "Interval": 0,
        #   ""
        # }
        # ]
        if "Bullet mod" in info[4]:
            self.bullet_mod = info[4]["Bullet mod"]

    def modify(self, entities, modifier, target_type):
        # This is not very efficient,
        # self.bullet_mod
        if "deviation" in modifier:
            self.angle_deviation = modifier["deviation"]
        if "slowdown" in modifier:
            self.slowdown_rate = modifier["slowdown"]
        if "angle" in modifier:
            mod = modifier["angle"]
            if type(modifier["angle"]) == list:
                mod = Fun.angle_between(entities[target_type][mod[0]], self.pos)
            if modifier["angle"] == "Player":
                mod = Fun.angle_between(entities["players"][0].pos, self.pos)
            self.angle = mod
        if "speed" in modifier:
            self.speed = modifier["speed"]
        # print("WHAT IS THIS BULLSHIT")
        if "radius" in modifier:
            self.radius += modifier["radius"]

    def act(self, entities, level):
        if self.duration > 0:
            if self.bullet_mod:
                for modifiers in self.bullet_mod:
                    if "Target time" in modifiers:
                        if modifiers["Target time"] == self.duration:
                            self.modify(entities, modifiers, self.team)
                    elif "Interval" in modifiers:
                        if self.duration % modifiers["Interval"] == 0:
                            self.modify(entities, modifiers, self.team)
            # Make the bullet move based on the angle
            self.angle += self.angle_deviation
            self.pos = Fun.move_with_vel_angle(self.pos, self.speed, self.angle)

            bullet_slowdown(self)

            # Check for collisions
            for collision in entities["entities"]:
                if Fun.collision_rect_circle(collision.collision_box.left, collision.collision_box.top,
                                             collision.collision_box.width, collision.collision_box.height,
                                             self.pos[0], self.pos[1], self.radius):
                    if Fun.damage_calculation(collision, self.damage, self.damage_type, death_message="Got defeated by a Yokai"):
                        self.visual_effect(self, entities)

                    self.duration = 0

            self.duration -= 1


class BulletDanmaku3(BasicBullet):
    # Even Coolest bullet type
    def __init__(self, pos, angle, info, owner):
        BasicBullet.__init__(self, pos, angle, info, owner)
        self.fire = False
        self.explosion_primer = False
        self.explosion = False
        self.laser = False
        self.laser_based = False
        self.melee = False
        self.angle_deviation = 0
        if "Angle deviation" in info[4]:
            self.angle_deviation = info[4]["Angle deviation"]

        self.slowdown_rate = 0
        if "Slowdown rate" in info[4]:
            self.slowdown_rate = info[4]["Slowdown rate"]

        if "Damage type" in info[4]:
            self.damage_type = info[4]["Damage type"]
        else:
            self.damage_type = "Physical"

        self.bullet_mod = []
        # Format [
        # {
        #   "Target time": 0,
        #   "Interval": 0,
        #   ""
        # }
        # ]
        if "Bullet mod" in info[4]:
            self.bullet_mod = info[4]["Bullet mod"]

        # Rotation thing
        self.rotation_center = [pos[0], pos[1]]
        # {"Rotation radius": 64,
        #  "Rotation angle start": self.aim_angle + 60,
        #  "Rotation deviation": 15
        # }
        self.rotation_radius = 0
        if "Rotation radius" in info[4]:
            self.rotation_radius = info[4]["Rotation radius"]
        self.rotation_growth = 0
        if "Rotation growth" in info[4]:
            self.rotation_growth = info[4]["Rotation growth"]

        self.rotation_angle = angle
        if "Rotation angle start" in info[4]:
            self.rotation_angle = info[4]["Rotation angle start"]
        self.rotation_deviation = 0
        if "Rotation deviation" in info[4]:
            self.rotation_deviation = info[4]["Rotation deviation"]

    def modify(self, entities, modifier, target_type):
        # This is not very efficient,
        # self.bullet_mod
        if "deviation" in modifier:
            self.angle_deviation = modifier["deviation"]
        if "slowdown" in modifier:
            self.slowdown_rate = modifier["slowdown"]
        if "angle" in modifier:
            mod = modifier["angle"]
            if type(modifier["angle"]) == list:
                mod = Fun.angle_between(entities[target_type][mod[0]], self.rotation_center)
            if modifier["angle"] == "Player":
                mod = Fun.angle_between(entities["players"][0].pos, self.rotation_center)
            self.angle = mod
        if "speed" in modifier:
            self.speed = modifier["speed"]
        # print("WHAT IS THIS BULLSHIT")
        if "radius" in modifier:
            self.radius += modifier["radius"]

        if "Rotation growth" in modifier:
            self.rotation_growth = modifier["Rotation growth"]

    def act(self, entities, level):
        if self.duration > 0:
            if self.bullet_mod:
                for modifiers in self.bullet_mod:
                    if "Target time" in modifiers:
                        if modifiers["Target time"] == self.duration:
                            self.modify(entities, modifiers, self.team)
                    elif "Interval" in modifiers:
                        if self.duration % modifiers["Interval"] == 0:
                            self.modify(entities, modifiers, self.team)
            # Make the bullet move based on the angle
            self.angle += self.angle_deviation

            # Move rotation center
            self.rotation_center = Fun.move_with_vel_angle(self.rotation_center, self.speed, self.angle)

            # Get pos from rotation center
            self.pos = Fun.move_with_vel_angle(self.rotation_center, self.rotation_radius, self.rotation_angle )
            self.rotation_radius += self.rotation_growth
            self.rotation_angle += self.rotation_deviation

            bullet_slowdown(self)

            # Check for collisions
            for collision in entities["entities"]:
                if Fun.collision_rect_circle(collision.collision_box.left, collision.collision_box.top,
                                             collision.collision_box.width, collision.collision_box.height,
                                             self.pos[0], self.pos[1], self.radius):

                    if Fun.damage_calculation(collision, self.damage, self.damage_type, death_message="Got defeated by a Yokai"):

                        self.visual_effect(self, entities)
                    self.on_hit_handler(collision, entities, level)

                    self.duration = 0

            self.duration -= 1


class LaserDanmaku2(BasicBullet):
    # Coolest bullet type
    def __init__(self, pos, angle, info, owner):
        BasicBullet.__init__(self, pos, angle, info, owner)
        self.fire = False
        self.explosion_primer = False
        self.explosion = False
        self.laser = True
        self.laser_based = True
        self.melee = False
        self.angle_deviation = 0
        if "Angle deviation" in info[4]:
            self.angle_deviation = info[4]["Angle deviation"]

        self.slowdown_rate = 0
        if "Slowdown rate" in info[4]:
            self.slowdown_rate = info[4]["Slowdown rate"]

        self.damage_type = "Physical"
        if "Damage type" in info[4]:
            self.damage_type = info[4]["Damage type"]

        self.bullet_mod = []
        # Format [
        # {
        #   "Target time": 0,
        #   "Interval": 0,
        #   ""
        # }
        # ]
        if "Bullet mod" in info[4]:
            self.bullet_mod = info[4]["Bullet mod"]
        self.growth = 0
        if "Growth" in info[4]:
            self.growth = info[4]["Growth"]

    def modify(self, entities, modifier, target_type):
        # This is not very efficient,
        # self.bullet_mod
        if "deviation" in modifier:
            self.angle_deviation = modifier["deviation"]
        if "slowdown" in modifier:
            self.slowdown_rate = modifier["slowdown"]
        if "angle" in modifier:
            mod = modifier["angle"]
            if type(modifier["angle"]) == list:
                mod = Fun.angle_between(entities[target_type][mod[0]], self.pos)
            self.angle = mod
        if "angle rate" in modifier:
            self.angle += modifier["angle rate"]
        if "speed" in modifier:
            self.speed = modifier["speed"]
        if "radius" in modifier:
            self.radius = modifier["radius"]
        if "Growth" in modifier:
            self.growth = modifier["Growth"]

    def act(self, entities, level):
        if self.duration > 0:
            if self.bullet_mod:
                for modifiers in self.bullet_mod:
                    if "Target time" in modifiers:
                        if modifiers["Target time"] == self.duration:
                            self.modify(entities, modifiers, self.team)
                    elif "Interval" in modifiers:
                        if (self.duration % modifiers["Interval"]) == 0:
                            self.modify(entities, modifiers, self.team)
            # Make the bullet move based on the angle
            self.angle += self.angle_deviation

            bullet_slowdown(self)
            self.pos[0] -= self.speed * math.cos(self.angle * math.pi / 180)
            self.pos[1] -= self.speed * math.sin(self.angle * math.pi / 180)
            self.radius += self.growth
            # Check for collisions
            for collision in entities["entities"]:
                if collision.team == self.team:
                    continue
                # for point in self.points_to_check:
                if Fun.collision_rect_laser(collision.collision_box, self.pos, self.angle, self.radius):
                    self.visual_effect(self, entities)
                    Fun.damage_calculation(collision, self.damage, self.damage_type, death_message="Got zapped by a Yokai")
                    self.on_hit_handler(collision, entities, level)

            self.duration -= 1

    def draw(self, win, scrolling):
        if self.duration > 0:
            pg.draw.line(win, self.colour,
                         [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]],
                         Fun.move_with_vel_angle([self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]],
                                                 self.radius, self.angle), width=3)

    def hit_wall(self, entities, level):
        pass


# |Fire based projectiles|----------------------------------------------------------------------------------------------
class Fire(BasicBullet):
    def __init__(self, pos, angle, info, owner):
        BasicBullet.__init__(self, pos, angle, info, owner)
        self.wall_physics = fire_bullet_wall_hit
        self.fire = True
        self.explosion_primer = False
        self.explosion = False
        self.laser = False
        self.laser_based = False
        self.melee = False
        self.visual_effect = fire_visual

        self.particle_allow = info[4]["Particle allowed"]
        self.burn_chance = info[4]["Burn chance"]
        self.burn_duration = info[4]["Burn duration"]
        if "Damage type" in info[4]:
            self.damage_type = info[4]["Damage type"]
        else:
            self.damage_type = "Fire"

    def act(self, entities, level):
        if self.duration > 0:
            if self.particle_allow and self.duration % 2 == 0:
                entities["particles"].append(Particles.FireParticle([self.pos[0], self.pos[1]], colour=self.colour))

            fire_randomize_pos(self)

            # Check for collisions
            for collision in entities["entities"]:
                if collision.team == self.team:
                    continue
                if Fun.collision_rect_circle(collision.collision_box.left, collision.collision_box.top,
                                             collision.collision_box.width, collision.collision_box.height,
                                             self.pos[0], self.pos[1], self.radius):
                    Fun.damage_calculation(collision, self.damage, self.damage_type, death_message="Burned to a crisp")
                    self.visual_effect(self, entities)
                    self.on_hit_handler(collision, entities, level)
                    self.duration = 0



                    if random.uniform(0, 1) < self.burn_chance:
                        collision.status["Burning"] = self.burn_duration

            self.duration -= 1

    def draw(self, win, scrolling):
        if self.duration > 0:
            # Highlight effect
            Fun.draw_transparent_circle(win, [self.pos[0] + scrolling[0] - self.radius / 2,
                                              self.pos[1] + scrolling[1] - self.radius / 2,  self.radius],
                                        self.colour,
                                        # (255, 255, 255),
                                        64)

class Napalm(BasicBullet):
    def __init__(self, pos, angle, info, owner):
        BasicBullet.__init__(self, pos, angle, info, owner)
        self.wall_physics = fire_bullet_wall_hit

        self.fire = True
        self.explosion_primer = False
        self.explosion = False
        self.laser = False
        self.laser_based = False
        self.melee = False
        self.visual_effect = fire_visual

        self.particle_allow = info[4]["Particle allowed"]
        self.burn_chance = info[4]["Burn chance"]
        self.burn_duration = info[4]["Burn duration"]
        if "Damage type" in info[4]:
            self.damage_type = info[4]["Damage type"]
        else:
            self.damage_type = "Fire"

        self.slowdown_rate = 0.05
        if "Slowdown rate" in info[4]:
            self.slowdown_rate = info[4]["Slowdown rate"]

    def act(self, entities, level):
        if self.duration > 0:
            if self.particle_allow and self.duration % 2 == 0:
                entities["particles"].append(Particles.FireParticle([self.pos[0], self.pos[1]], colour=self.colour))
            # Make the bullet move based on the angle
            fire_randomize_pos(self)

            bullet_slowdown(self)
            # Check for collisions
            for collision in entities["entities"]:
                if self.owner.team == collision.team:
                    continue
                if Fun.collision_rect_circle(collision.collision_box.left, collision.collision_box.top,
                                             collision.collision_box.width, collision.collision_box.height,
                                             self.pos[0], self.pos[1], self.radius):
                    Fun.damage_calculation(collision, self.damage, self.damage_type, death_message="Hates the smell of napalm")
                    self.visual_effect(self, entities)

                    self.on_hit_handler(collision, entities, level)
                    if random.uniform(0, 1) < self.burn_chance:
                        collision.status["Burning"] = self.burn_duration
                    self.duration = 0

            self.duration -= 1

    def draw(self, win, scrolling):
        if self.duration > 0:
            # Highlight effect
            Fun.draw_transparent_circle(win, [self.pos[0] + scrolling[0] - self.radius / 2,
                                              self.pos[1] + scrolling[1] - self.radius / 2,  self.radius],
                                        self.colour,
                                        # (255, 255, 255),
                                        128)


class Flare(BasicBullet):
    def __init__(self, pos, angle, info, owner):
        BasicBullet.__init__(self, pos, angle, info, owner)
        self.wall_physics = fire_bullet_wall_hit

        self.fire = False
        self.explosion_primer = True
        self.explosion = False
        self.laser = False
        self.laser_based = False
        self.melee = False
        # explodes on contact or after a delay
        self.visual_effect = fire_visual
        self.secondary_explosion = info[4]["Secondary explosion"]
        self.secondary_explosion["Fire property"]["Colour"] = self.colour
        self.particle_allow = info[4]["Particle allowed"]
        self.burn_chance = info[4]["Burn chance"]
        self.burn_duration = info[4]["Burn duration"]
        if "Damage type" in info[4]:
            self.damage_type = info[4]["Damage type"]
        else:
            self.damage_type = "Fire"

    def act(self, entities, level):
        if self.duration > 0:
            if self.particle_allow and self.duration % 2 == 0:
                entities["particles"].append(Particles.FireParticle([self.pos[0], self.pos[1]], colour=self.colour))

            # Make the bullet move based on the angle
            fire_randomize_pos(self)

            # Check for collisions
            for collision in entities["entities"]:
                if Fun.collision_rect_circle(collision.collision_box.left, collision.collision_box.top,
                                             collision.collision_box.width, collision.collision_box.height,
                                             self.pos[0], self.pos[1], self.radius):
                    Fun.damage_calculation(collision, self.damage, self.damage_type, death_message="Flared up")
                    self.on_hit_handler(collision, entities, level)
                    self.duration = 1
                    self.visual_effect(self, entities)
                    if random.uniform(0, 1) < self.burn_chance:
                        collision.status["Burning"] = self.burn_duration

            self.duration -= 1
        if self.duration == 0:
            # Explode here
            for x in range(self.secondary_explosion["Amount of Bullets"]):

                spawn_bullet(
                    self.owner, entities,
                    ExplosionSecondary,
                    [self.pos[0], self.pos[1]],
                    self.angle + (360 / self.secondary_explosion["Amount of Bullets"] * x),
                    [self.speed * self.secondary_explosion["Speed mod"],
                     round(self.og_info[1] * self.secondary_explosion["Duration mod"]),
                     self.radius * self.secondary_explosion["Radius mod"],
                     round(self.damage * self.secondary_explosion["Damage mod"]),
                     self.secondary_explosion["Fire property"]])


# |Explosion based projectiles|-----------------------------------------------------------------------------------------
class ExplosionPrimaryType1(BasicBullet):
    def __init__(self, pos, angle, info, owner):
        BasicBullet.__init__(self, pos, angle, info, owner)
        self.wall_physics = explosive_bullet_wall_hit

        self.fire = False
        self.explosion_primer = True
        self.explosion = False
        self.laser = False
        self.laser_based = False
        self.melee = False
        # Type 1 explodes on contact or after a delay
        self.visual_effect = boom_visual

        self.secondary_explosion = info[4]["Secondary explosion"]
        if "Damage type" in info[4]:
            self.damage_type = info[4]["Damage type"]
        else:
            self.damage_type = "Explosion"

    def act(self, entities, level):
        if self.duration > 0:
            # Make the bullet move based on the angle
            self.pos[0] -= self.speed * math.cos(self.angle * math.pi / 180)
            self.pos[1] -= self.speed * math.sin(self.angle * math.pi / 180)

            # Check for collisions
            for collision in entities["entities"]:
                if self.owner.team == collision.team:
                    continue
                if Fun.collision_rect_circle(collision.collision_box.left, collision.collision_box.top,
                                             collision.collision_box.width, collision.collision_box.height,
                                             self.pos[0], self.pos[1], self.radius):
                    Fun.damage_calculation(collision, self.damage, self.damage_type, death_message="Limbs blown up")
                    self.on_hit_handler(collision, entities, level)
                    self.duration = 1
                    self.visual_effect(self, entities)

            self.duration -= 1
        if self.duration == 0:
            # Explode here
            spawn_bullet(
                self.owner, entities,
                ExplosionSecondary,
                self.pos,
                self.angle,
                [0, 5, self.radius, self.damage, self.secondary_explosion])


class ExplosionPrimaryType2(BasicBullet):
    def __init__(self, pos, angle, info, owner):
        BasicBullet.__init__(self, pos, angle, info, owner)
        self.wall_physics = explosive_bullet_wall_hit

        self.fire = False
        self.explosion_primer = False
        self.explosion = False
        self.laser = False
        self.laser_based = False
        self.melee = False
        self.visual_effect = boom_visual

        self.secondary_explosion = info[4]["Secondary explosion"]
        if "Damage type" in info[4]:
            self.damage_type = info[4]["Damage type"]
        else:
            self.damage_type = "Explosion"

    def act(self, entities, level):
        if self.duration > 0:
            # Make the bullet move based on the angle
            self.pos[0] -= self.speed * math.cos(self.angle * math.pi / 180)
            self.pos[1] -= self.speed * math.sin(self.angle * math.pi / 180)

            # Check for collisions
            for collision in entities["entities"]:
                if Fun.collision_rect_circle(collision.collision_box.left, collision.collision_box.top,
                                             collision.collision_box.width, collision.collision_box.height,
                                             self.pos[0], self.pos[1], self.radius):
                    Fun.damage_calculation(collision, self.damage, self.damage_type, death_message="Limbs blown up")
                    self.on_hit_handler(collision, entities, level)
                    # Explode here
                    spawn_bullet(
                        self.owner, entities,
                        ExplosionSecondary,
                        self.pos,
                        self.angle,
                        [0, 5, self.radius, self.damage, self.secondary_explosion])
                    self.duration = 0
                    self.visual_effect(self, entities)

            self.duration -= 1


class Missile(BasicBullet):
    def __init__(self, pos, angle, info, owner):
        BasicBullet.__init__(self, pos, angle, info, owner)
        self.wall_physics = explosive_bullet_wall_hit

        self.fire = False
        self.explosion_primer = True
        self.explosion = False
        self.laser = False
        self.laser_based = False
        self.melee = False
        # Type 2 only explode on contact
        # targeting stuff
        self.targeting_range = info[4]["Targeting range"]
        self.targeting_angle = info[4]["Targeting angle"]
        self.target = False
        self.visual_effect = boom_visual

        self.manoeuvrability = 4
        if "Manoeuvrability" in info[4]:
            self.manoeuvrability = info[4]["Manoeuvrability"]

        self.slowdown_rate = 0
        if "Slowdown rate" in info[4]:
            self.slowdown_rate = info[4]["Slowdown rate"]

        self.move_angle = self.angle
        self.secondary_explosion = info[4]["Secondary explosion"]
        self.target_pos = False
        if "Damage type" in info[4]:
            self.damage_type = info[4]["Damage type"]
        else:
            self.damage_type = "Explosion"

    def payload(self, collision, entities, level):
        spawn_bullet(
            self.owner, entities,
            ExplosionSecondary,
            self.pos,
            self.angle,
            [0, 5, self.radius, self.damage, self.secondary_explosion])

    def act(self, entities, level):
        if self.duration > 0:
            bullet_slowdown(self)
            # Now the missiles have a "max locking angle"
            if self.duration % 3 == 0:
                target = missile_seek(self, entities, self.targeting_range, self.angle,
                                                  self.targeting_angle)
                if target:
                    self.target_pos = target.pos
            if self.target_pos:

                if self.duration % random.randint(5, 8) == 0:
                    entities["particles"].append(Particles.Smoke([self.pos[0], self.pos[1]], colour=[
                        Fun.WHITE, Fun.GRAY, Fun.LIGHT_GRAY
                    ][random.randint(0, 2)]
                                                           ))
                self.angle = Fun.angle_between(self.target_pos, self.pos)

                invert_aim = 1
                if not -(
                        180 - self.manoeuvrability) + self.angle < self.move_angle < 180 - self.manoeuvrability + self.angle:
                    invert_aim = -1

                # Adjust angle
                if self.move_angle < self.angle:
                    self.move_angle += self.manoeuvrability * invert_aim
                    if self.move_angle > self.angle:
                        self.move_angle = self.angle
                elif self.move_angle > self.angle:
                    self.move_angle += -self.manoeuvrability * invert_aim
                    if self.move_angle < self.angle:
                        self.move_angle = self.angle

                # Value Limiter
                if self.move_angle > 180:
                    self.move_angle = -180 + (self.move_angle - 180)
                if self.move_angle < -180:
                    self.move_angle = 180 - (self.move_angle + 180)

                # if self.duration % 32 == 0:
                #     Fun.play_sound("Ping", "SFX")

            # Make the bullet move based on the angle
            self.pos[0] -= self.speed * math.cos(self.move_angle * math.pi / 180)
            self.pos[1] -= self.speed * math.sin(self.move_angle * math.pi / 180)

            # Check for collisions
            for collision in entities["entities"]:
                if self.owner.team == collision.team:
                    continue

                if Fun.collision_rect_circle(collision.collision_box.left, collision.collision_box.top,
                                             collision.collision_box.width, collision.collision_box.height,
                                             self.pos[0], self.pos[1], self.radius):
                    Fun.damage_calculation(collision, self.damage, self.damage_type, death_message="Limbs blown up")
                    self.on_hit_handler(collision, entities, level)
                    # Explode here
                    self.payload(collision, entities, level)

                    self.duration = 0
                    self.visual_effect(self, entities)

            self.duration -= 1
            if self.duration == 0:
                self.payload(None, entities, level)

    def draw(self, win, scrolling):
        if self.duration > 0:
            # missile
            pg.draw.circle(win, self.colour, [self.pos[0] + scrolling[0],
                                              self.pos[1] + scrolling[1]], self.radius)
            Fun.blitRotate2(win, missile,
                            [self.pos[0] - missile.get_width() // 2 + scrolling[0],
                             self.pos[1] - missile.get_height() // 2 + scrolling[1]],
                            180 - self.angle)
            # Shows what the missile is locking on
            if self.target_pos:
                center = self.target_pos

                pg.draw.rect(win, Fun.GREEN, [center[0] - 14 + scrolling[0],
                                              center[1] - 14 + scrolling[1],
                                              28,
                                              28], 2)
                pg.draw.lines(win, Fun.GREEN, True, (
                    [center[0] - 14 + scrolling[0], center[1] + scrolling[1]],
                    [center[0] + scrolling[0], center[1] - 14 + scrolling[1]],
                    [center[0] + 14 + scrolling[0], center[1] + scrolling[1]],
                    [center[0] + scrolling[0], center[1] + 14 + scrolling[1]],
                ), 1)


class MissileIncendiary(Missile):
    def payload(self, collision, entities, level):
        for x in range(self.secondary_explosion["Amount of Bullets"]):
            spawn_bullet(self.owner, entities, Napalm, self.pos.copy(), self.angle * 360 / self.secondary_explosion["Amount of Bullets"] * x, self.secondary_explosion["Bullet Info"])


class MissileShrapnel(Missile):
    def payload(self, collision, entities, level):
        for x in range(self.secondary_explosion["Amount of Bullets"]):
            spawn_bullet(self.owner, entities, BulletSlowing, self.pos.copy(),
                         random.uniform(self.angle - self.secondary_explosion["Angle range"],
                                        self.angle + self.secondary_explosion["Angle range"]),
                         self.secondary_explosion["Bullet Info"])

            self.slowdown_rate = 2 - random.random() * 4


class GrenadeType0(BasicBullet):
    # Use that one to give grenade physics to stuff that need it
    def __init__(self, pos, angle, info, owner):
        BasicBullet.__init__(self, pos, angle, info, owner)
        self.wall_physics = base_grenade_wall_hit
        self.fire = False
        self.explosion_primer = True
        self.explosion = False
        self.laser = False
        self.laser_based = False
        self.melee = False

    def act(self, entities, level):
        if self.duration > 0:
            self.pos[0] -= self.speed * math.cos(self.angle * math.pi / 180)
            self.pos[1] -= self.speed * math.sin(self.angle * math.pi / 180)
            if self.speed > 0:
                self.speed -= 0.05
                if self.speed < 0:
                    self.speed = 0
            self.duration -= 1
        if self.duration == 0:
            # Explode here
            self.duration -= 1

    def draw(self, win, scrolling):
        pass


class GrenadeType1(BasicBullet):
    def __init__(self, pos, angle, info, owner):
        BasicBullet.__init__(self, pos, angle, info, owner)
        self.wall_physics = base_grenade_wall_hit
        self.fire = False
        self.explosion_primer = True
        self.explosion = False
        self.laser = False
        self.laser_based = False
        self.melee = False
        # Type 1 explodes on contact or after a delay

        self.secondary_explosion = info[4]["Secondary explosion"]
        if "Damage type" in info[4]:
            self.damage_type = info[4]["Damage type"]
        else:
            self.damage_type = "Explosion"

    def act(self, entities, level):
        if self.duration > 0:
            base_grenade_act(self, entities)
        if self.duration == 0:
            # Explode here
            self.duration -= 1
            spawn_bullet(
                self.owner, entities,
                ExplosionSecondary,
                self.pos,
                self.angle,
                [0, self.secondary_explosion["Duration"], self.radius, self.damage, self.secondary_explosion])

    def draw(self, win, scrolling):
        if self.duration > 0:
            pg.draw.circle(win, self.colour, [self.pos[0] + scrolling[0],
                                              self.pos[1] + scrolling[1]], self.radius)
            Fun.blitRotate2(win, grenade_1,
                            [self.pos[0] - grenade_1.get_width() // 2 + scrolling[0],
                             self.pos[1] - grenade_1.get_height() // 2 + scrolling[1]],
                            180 - self.angle + self.duration * self.speed)


class GrenadeType2(BasicBullet):
    # Incendiary
    def __init__(self, pos, angle, info, owner):
        BasicBullet.__init__(self, pos, angle, info, owner)
        self.wall_physics = base_grenade_wall_hit

        self.fire = False
        self.explosion_primer = True
        self.explosion = False
        self.laser = False
        self.laser_based = False
        self.melee = False
        # Type 1 explodes on contact or after a delay

        self.secondary_explosion = info[4]["Incendiary"]
        if "Damage type" in info[4]:
            self.damage_type = info[4]["Damage type"]
        else:
            self.damage_type = "Fire"

    def act(self, entities, level):
        if self.duration > 0:
            base_grenade_act(self, entities)
        if self.duration == 0:
            # Explode here
            Fun.play_sound("Grenade 2", "SFX")
            for x in range(self.secondary_explosion["Amount of Bullets"]):
                angle = 360 * x / self.secondary_explosion["Amount of Bullets"]

                spawn_bullet(
                    self.owner, entities,
                    Napalm,
                    Fun.move_with_vel_angle(self.pos, self.secondary_explosion["Speed"] * 2, angle),
                    self.angle + (360 / self.secondary_explosion["Amount of Bullets"] * x),
                    [self.secondary_explosion["Speed"],
                     self.secondary_explosion["Duration"],
                     self.secondary_explosion["Radius"],
                     self.secondary_explosion["Damage"],
                     self.secondary_explosion["Fire property"]])


    def draw(self, win, scrolling):
        if self.duration > 0:
            pg.draw.circle(win, self.colour, [self.pos[0] + scrolling[0],
                                              self.pos[1] + scrolling[1]], self.radius)
            Fun.blitRotate2(win, grenade_2,
                            [self.pos[0] - grenade_2.get_width() // 2 + scrolling[0],
                             self.pos[1] - grenade_2.get_height() // 2 + scrolling[1]],
                            180 - self.angle + self.duration * self.speed)


class GrenadeType3(BasicBullet):
    # Smoke
    def __init__(self, pos, angle, info, owner):
        BasicBullet.__init__(self, pos, angle, info, owner)
        self.wall_physics = base_grenade_wall_hit

        self.fire = False
        self.explosion_primer = True
        self.explosion = False
        self.laser = False
        self.laser_based = False
        self.melee = False
        # Type 1 explodes on contact or after a delay

        self.secondary_explosion = info[4]["Smoke"]
        if "Damage type" in info[4]:
            self.damage_type = info[4]["Damage type"]
        else:
            self.damage_type = "Physical"

    def act(self, entities, level):
        if self.duration > 0:
            base_grenade_act(self, entities)
        if self.duration == 0:
            # Explode here
            Fun.play_sound("Grenade 3", "SFX")
            for p in range(self.secondary_explosion["Radius"] * 2):
                entities["particles"].append(Particles.Smoke(
                    Fun.random_point_in_circle(self.pos, self.secondary_explosion["Radius"]),
                    duration=(self.secondary_explosion["Duration"] - 50, self.secondary_explosion["Duration"])
                ))
            entities["items"].append(Items.ItemGen2({
                "name": "Smoke Grenade",
                "friction": 0,
                "thickness": 1,
                "act": Items.smoke_grenade,
                "draw": Fun.none,
                "sprites": [],
                "life time": 360,
                "free var": {
                    "Duration": self.secondary_explosion["Duration"],
                    "Radius": self.secondary_explosion["Radius"],
                }},
                                                self.pos))

    def draw(self, win, scrolling):
        if self.duration > 0:
            pg.draw.circle(win, self.colour, [self.pos[0] + scrolling[0],
                                              self.pos[1] + scrolling[1]], self.radius)
            Fun.blitRotate2(win, grenade_3,
                            [self.pos[0] - grenade_3.get_width() // 2 + scrolling[0],
                             self.pos[1] - grenade_3.get_height() // 2 + scrolling[1]],
                            180 - self.angle + self.duration * self.speed)


class GrenadeType4(BasicBullet):
    # Flashbang
    def __init__(self, pos, angle, info, owner):
        BasicBullet.__init__(self, pos, angle, info, owner)
        self.wall_physics = base_grenade_wall_hit

        self.fire = False
        self.explosion_primer = True
        self.explosion = False
        self.laser = False
        self.laser_based = False
        self.melee = False
        # Type 1 explodes on contact or after a delay

        self.secondary_explosion = info[4]["Flashbang"]

        if "Damage type" in info[4]:
            self.damage_type = info[4]["Damage type"]
        else:
            self.damage_type = "Physical"

    def act(self, entities, level):
        if self.duration > 0:
            base_grenade_act(self, entities)
        if self.duration == 0:
            # Explode here
            radius = self.secondary_explosion["Radius"]
            entities["particles"].append(Particles.GrowingCircleTransparent(
                self.pos, Fun.WHITE, 0, 4, radius, 0, alpha=62))
            entities["particles"].append(Particles.GrowingCircleTransparent(
                self.pos, Fun.WHITE, 0, 6, radius*0.7, 0, alpha=62))
            entities["particles"].append(Particles.GrowingCircleTransparent(
                self.pos, Fun.WHITE, 0, 9, radius*0.5, 0, alpha=62))
            for t in ["players", "enemies"]:
                for e in entities[t]:
                    if Fun.check_point_in_circle(self.secondary_explosion["Radius"],
                                                 self.pos[0], self.pos[1],
                                                 e.pos[0], e.pos[1]):
                        e.status["Stunned"] += self.secondary_explosion["Strength"]
                        if e.is_player:
                            dist = Fun.distance_between(e.pos, self.pos) * 2
                            dist = round(350 - dist)
                            if dist < 0:
                                dist = 0
                            entities["UI particles"].append(Particles.Flashbang(duration=dist))
                            Fun.play_sound("flashbang", "SFX", fadeout=dist / 350)

    def draw(self, win, scrolling):
        if self.duration > 0:
            pg.draw.circle(win, self.colour, [self.pos[0] + scrolling[0],
                                              self.pos[1] + scrolling[1]], self.radius)
            Fun.blitRotate2(win, grenade_4,
                            [self.pos[0] - grenade_4.get_width() // 2 + scrolling[0],
                             self.pos[1] - grenade_4.get_height() // 2 + scrolling[1]],
                            180 - self.angle + self.duration * self.speed)


class GrenadeType5(BasicBullet):
    # Shrapnel
    def __init__(self, pos, angle, info, owner):
        BasicBullet.__init__(self, pos, angle, info, owner)
        self.wall_physics = base_grenade_wall_hit

        self.fire = False
        self.explosion_primer = True
        self.explosion = False
        self.laser = False
        self.laser_based = False
        self.melee = False
        # Type 1 explodes on contact or after a delay

        self.secondary_explosion = info[4]["Shrapnel"]
        if "Damage type" in info[4]:
            self.damage_type = info[4]["Damage type"]
        else:
            self.damage_type = "Explosion"

    def act(self, entities, level):
        if self.duration > 0:
            base_grenade_act(self, entities)
        if self.duration == 0:
            # Explode here
            Fun.play_sound("Explosion")
            for x in range(self.secondary_explosion["Amount of Bullets"]):
                angle = 360 * x / self.secondary_explosion["Amount of Bullets"]
                spawn_bullet(
                    self.owner, entities,
                    Bullet,
                    Fun.move_with_vel_angle(self.pos, self.secondary_explosion["Speed"] * 2, angle),
                    self.angle + (360 / self.secondary_explosion["Amount of Bullets"] * x),
                    [self.secondary_explosion["Speed"] * random.random() + 1,
                     self.secondary_explosion["Duration"] * random.random() + 1,
                     self.secondary_explosion["Radius"] * random.random() + 1,
                     self.secondary_explosion["Damage"],
                     self.secondary_explosion["Bullet property"]])



    def draw(self, win, scrolling):
        if self.duration > 0:
            pg.draw.circle(win, self.colour, [self.pos[0] + scrolling[0],
                                              self.pos[1] + scrolling[1]], self.radius)
            Fun.blitRotate2(win, grenade_5,
                            [self.pos[0] - grenade_5.get_width() // 2 + scrolling[0],
                             self.pos[1] - grenade_5.get_height() // 2 + scrolling[1]],
                            180 - self.angle + self.duration * self.speed)


class GrenadeType6(BasicBullet):
    def __init__(self, pos, angle, info, owner):
        BasicBullet.__init__(self, pos, angle, info, owner)
        self.wall_physics = base_grenade_wall_hit
        self.fire = False
        self.explosion_primer = True
        self.explosion = False
        self.laser = False
        self.laser_based = False
        self.melee = False
        # Type 1 explodes on contact or after a delay

        self.secondary_explosion = info[4]["Secondary explosion"]
        if "Damage type" in info[4]:
            self.damage_type = info[4]["Damage type"]
        else:
            self.damage_type = "Explosion"

    def act(self, entities, level):
        if self.duration > 0:
            base_grenade_act(self, entities)
            # for b in bullets[{"enemies": "players", "players": "enemies"}[collision_to_check]]:
            for b in entities["bullets"]:
                # Check of the bullet should be parried
                if b.explosion or b.laser or b.laser_based or b.melee or b.pos == self.pos:
                    continue

                if Fun.collision_circle_circle(self.pos, self.radius, b.pos, b.radius):
                    self.duration = -900
        if self.duration == -900:
            # Explode here
            self.duration -= 1
            spawn_bullet(
                self.owner, entities,
                ExplosionSecondary,
                self.pos,
                self.angle,
                [0, self.secondary_explosion["Duration"], self.radius, self.damage, self.secondary_explosion])

    def draw(self, win, scrolling):
        if self.duration > 0:
            pg.draw.circle(win, self.colour, [self.pos[0] + scrolling[0],
                                              self.pos[1] + scrolling[1]], self.radius)
            Fun.blitRotate2(win, grenade_6,
                            [self.pos[0] - grenade_6.get_width() // 2 + scrolling[0],
                             self.pos[1] - grenade_6.get_height() // 2 + scrolling[1]],
                            180 - self.angle + self.duration * self.speed)


class GrenadeType7(BasicBullet):
    def __init__(self, pos, angle, info, owner):
        BasicBullet.__init__(self, pos, angle, info, owner)
        self.wall_physics = base_grenade_wall_hit
        self.fire = False
        self.explosion_primer = True
        self.explosion = False
        self.laser = False
        self.laser_based = False
        self.melee = False
        # Type 1 explodes on contact or after a delay
        expl_info = info[4]["Secondary explosion"]
        self.expl_radius = expl_info["Radius"]
        self.expl_apply_no_debuff = expl_info["No Debuff"]
        self.damage_type = "Healing"

    def act(self, entities, level):
        if self.duration > 0:
            base_grenade_act(self, entities)
        if self.duration == 0:
            entities["particles"].append(Particles.GrowingCircle(self.pos, Fun.GREEN, self.expl_radius / 10, 10, 0, 6))
            # Explode here
            self.duration -= 1
            # Give healing around
            if self.expl_apply_no_debuff:
                for e in entities["entities"]:
                    if e.team != self.team:
                        continue
                    if Fun.distance_between(e.pos, self.pos) <= self.expl_radius:
                        e.status["Healing"] += self.damage
                        e.status["No debuff"] += self.damage * 2
                return

            for e in entities["entities"]:
                if e.team != self.team:
                    continue
                if Fun.distance_between(e.pos, self.pos) <= self.expl_radius:
                    Fun.damage_calculation(e, self.damage, "Healing", death_message="Was an undead")

    def draw(self, win, scrolling):
        if self.duration > 0:
            pg.draw.circle(win, self.colour, [self.pos[0] + scrolling[0],
                                              self.pos[1] + scrolling[1]], self.radius)
            Fun.blitRotate2(win, grenade_1,
                            [self.pos[0] - grenade_1.get_width() // 2 + scrolling[0],
                             self.pos[1] - grenade_1.get_height() // 2 + scrolling[1]],
                            180 - self.angle + self.duration * self.speed)


class C4(BasicBullet):
    def __init__(self, pos, angle, info, owner):
        BasicBullet.__init__(self, pos, angle, info, owner)
        owner.weapon.free_var["C4 out"].append(self)
        self.wall_physics = base_grenade_wall_hit
        self.fire = False
        self.explosion_primer = True
        self.explosion = False
        self.laser = False
        self.laser_based = False
        self.melee = False
        # Type 1 explodes on contact or after a delay

        self.secondary_explosion = info[4]["Secondary explosion"]
        if "Damage type" in info[4]:
            self.damage_type = info[4]["Damage type"]
        else:
            self.damage_type = "Explosion"

    def act(self, entities, level):
        if self.duration > 0:

            # Make the bullet move based on the angle
            self.pos[0] -= self.speed * math.cos(self.angle * math.pi / 180)
            self.pos[1] -= self.speed * math.sin(self.angle * math.pi / 180)
            if self.speed > 0:
                self.speed -= 0.05
                if self.speed < 0:
                    self.speed = 0

                self.duration -= 1
        if self.duration == 0:
            # Explode here
            self.duration -= 1
            spawn_bullet(
                self.owner, entities,
                ExplosionSecondary,
                self.pos,
                self.angle,
                [0, self.secondary_explosion["Duration"], self.radius, self.damage, self.secondary_explosion])

    def draw(self, win, scrolling):
        if self.duration > 0:
            pg.draw.circle(win, self.colour, [self.pos[0] + scrolling[0],
                                              self.pos[1] + scrolling[1]], self.radius)
            Fun.blitRotate2(win, grenade_c4,
                            [self.pos[0] - grenade_c4.get_width() // 2 + scrolling[0],
                             self.pos[1] - grenade_c4.get_height() // 2 + scrolling[1]],
                            180 - self.angle + self.duration * self.speed)


class ExplosionSecondary(BasicBullet):
    def __init__(self, pos, angle, info, owner):
        BasicBullet.__init__(self, pos, angle, info, owner)
        self.og_info = info
        self.fire = False
        self.explosion_primer = False
        self.explosion = True  # Disable wall collisions
        self.laser = False
        self.laser_based = False
        self.melee = False
        self.pos = pos
        self.angle = angle
        self.speed = info[0]
        self.duration = info[4]["Duration"]
        self.starting_duration = self.duration
        self.radius = info[2]
        self.damage = info[3] * info[4]["Damage mod"]

        self.growth = info[4]["Growth"]
        if "Damage type" in info[4]:
            self.damage_type = info[4]["Damage type"]
        else:
            self.damage_type = "Explosion"

    def act(self, entities, level):
        if self.duration == self.starting_duration:
            # Cool explosion stuff
            entities["particles"].append(Particles.NewExplosionEffect([self.pos[0], self.pos[1]],
                                                                duration=round(self.duration * 4.5),
                                                                particles=3 + self.radius // 4,
                                                                radius=self.radius * 2,
                                                                particle_growth=self.growth))
            entities["particles"].append(Particles.GrowingCircle([self.pos[0], self.pos[1]], Fun.WHITE,
                                                           self.growth, self.duration, self.radius, 3))
            Fun.play_sound("Explosion", "SFX")
        if self.duration > 0:
            self.radius += self.growth
            # Check for collisions
            for collision in entities["entities"]:
                if Fun.collision_rect_circle(collision.collision_box.left, collision.collision_box.top,
                                                 collision.collision_box.width, collision.collision_box.height,
                                                 self.pos[0], self.pos[1], self.radius):
                    if self.owner.team == collision.team:
                        continue
                    Fun.damage_calculation(collision, self.damage, self.damage_type, death_message="Limbs blown up")
                    # Entities inside the explosion are pushed
                    push_angle = Fun.angle_between(collision.pos, self.pos)
                    pos = Fun.distance_between(collision.pos, self.pos)
                    push_strength = self.radius / (pos + 2)
                    if self.growth < 0:
                        push_strength *= 0.5
                        if pos < 32:
                            push_strength = 0
                            collision.vel = [0, 0]
                    collision.vel = Fun.move_with_vel_angle(collision.vel, self.growth * 1.25 * push_strength,
                                                                push_angle)

            self.duration -= 1

    def draw(self, win, scrolling):
        pass

    def hit_wall(self, entities, level):
        pass


class Artillery(BasicBullet):
    def __init__(self, pos, angle, info, owner):
        BasicBullet.__init__(self, pos, angle, info, owner)
        self.wall_physics = explosive_bullet_wall_hit

        self.fire = False
        self.explosion_primer = True
        self.explosion = False
        self.laser = False
        self.laser_based = True
        self.melee = False
        # Type 1 explodes on contact or after a delay
        self.visual_effect = boom_visual

        self.secondary_explosion = info[4]["Secondary explosion"]
        if "Damage type" in info[4]:
            self.damage_type = info[4]["Damage type"]
        else:
            self.damage_type = "Explosion"
        self.slowdown_rate = 0
        if "Slowdown rate" in info[4]:
            self.slowdown_rate = info[4]["Slowdown rate"]

    def act(self, entities, level):
        if self.duration > 0:
            # Make the bullet move based on the angle
            self.pos[0] -= self.speed * math.cos(self.angle * math.pi / 180)
            self.pos[1] -= self.speed * math.sin(self.angle * math.pi / 180)
            bullet_slowdown(self)

            self.duration -= 1
        if self.duration == 0:
            # Explode here
            Fun.play_sound("Explosion")
            spawn_bullet(
                self.owner, entities, Melee3, self.pos, self.angle,
                [0, self.secondary_explosion["Duration"], self.radius/self.secondary_explosion["Duration"], self.damage,
                 {"Damage type": self.damage_type, "Growth": self.radius/self.secondary_explosion["Duration"]}])

    def draw(self, win, scrolling):
        if self.duration > 0:
            Fun.draw_transparent_circle(
                win, [self.pos[0] + scrolling[0] - self.radius , self.pos[1] + scrolling[1] - self.radius, self.radius * 2],
                                        self.colour, 64)
            radius_2 = self.radius * (1 - self.duration / self.og_info[1])
            Fun.draw_transparent_circle(win, [self.pos[0] + scrolling[0] - radius_2, self.pos[1] + scrolling[1] - radius_2 ,
                                              radius_2 * 2],
                                        self.colour, 64)

    def hit_wall(self, entities, level):
        pass


class ArtilleryFlare(Artillery):
    def act(self, entities, level):
        if self.duration > 0:
            # Make the bullet move based on the angle
            self.pos[0] -= self.speed * math.cos(self.angle * math.pi / 180)
            self.pos[1] -= self.speed * math.sin(self.angle * math.pi / 180)
            bullet_slowdown(self)

            self.duration -= 1
        if self.duration == 0:
            if self.duration == 0:
                Fun.play_sound("Explosion")
                # Explode here
                radius = self.secondary_explosion["Radius"]
                entities["particles"].append(Particles.GrowingCircleTransparent(
                    self.pos, Fun.WHITE, 0, 4, radius, 0, alpha=62))
                entities["particles"].append(Particles.GrowingCircleTransparent(
                    self.pos, Fun.WHITE, 0, 6, radius * 0.7, 0, alpha=62))
                entities["particles"].append(Particles.GrowingCircleTransparent(
                    self.pos, Fun.WHITE, 0, 9, radius * 0.5, 0, alpha=62))
                for e in entities["entities"]:
                    if e.team == self.team:
                        continue
                    if Fun.check_point_in_circle(self.secondary_explosion["Radius"],
                                                     self.pos[0], self.pos[1],
                                                     e.pos[0], e.pos[1]):
                        e.status["Stunned"] += self.secondary_explosion["Strength"]
                        e.status["Visible"] += self.secondary_explosion["Strength"] * 3
                        # if e.is_player:
                        #     dist = Fun.distance_between(e.pos, self.pos) * 2
                        #     dist = round(350 - dist)
                        #     if dist < 0:
                        #        dist = 0
                        #     entities["UI particles"].append(Fun.Flashbang(duration=dist))
                        #     Fun.play_sound("flashbang", "SFX", fadeout=dist / 350)


class ArtillerySmoke(Artillery):
    def act(self, entities, level):
        if self.duration > 0:
            # Make the bullet move based on the angle
            self.pos[0] -= self.speed * math.cos(self.angle * math.pi / 180)
            self.pos[1] -= self.speed * math.sin(self.angle * math.pi / 180)
            bullet_slowdown(self)

            self.duration -= 1
        if self.duration == 0:
            # Explode here
            Fun.play_sound("Grenade 3")
            # for p in range(self.secondary_explosion["Radius"] * 2):
            #     entities["particles"].append(Fun.Smoke(
            #         Fun.random_point_in_circle(self.pos, self.secondary_explosion["Radius"]),
            #         duration=(self.secondary_explosion["Duration"] - 50, self.secondary_explosion["Duration"])
            #     ))
            entities["items"].append(Items.ItemGen2({
                "name": "Smoke Grenade",
                "friction": 0,
                "thickness": 1,
                "act": Items.smoke_grenade,
                "draw": Fun.none,
                "sprites": [],
                "life time": 360,
                "free var": {
                    "Duration": self.secondary_explosion["Duration"] * 60,
                    "Radius": self.secondary_explosion["Radius"],
                }},
                self.pos))


# |Hit Scan projectiles|------------------------------------------------------------------------------------------------
class Laser(BasicBullet):
    def __init__(self, pos, angle, info, owner):
        BasicBullet.__init__(self, pos, angle, info, owner)
        self.fire = False
        self.explosion_primer = False
        self.explosion = False
        self.laser = True
        self.laser_based = True
        self.melee = False
        # Radius is the length of the laser
        self.colour = Fun.RED
        if "Colour" in info[4]:
            self.colour = info[4]["Colour"]
        self.visual_effect = laser_visual
        if "Damage type" in info[4]:
            self.damage_type = info[4]["Damage type"]
        else:
            self.damage_type = "Energy"

    def act(self, entities, level):
        # Make the collision check work both ways
        if self.duration > 0:
            self.pos[0] -= self.speed * math.cos(self.angle * math.pi / 180)
            self.pos[1] -= self.speed * math.sin(self.angle * math.pi / 180)
            # Check for collisions
            for collision in entities["entities"]:
                if self.owner.team == collision.team:
                    continue
                # for point in self.points_to_check:
                if Fun.collision_rect_laser(collision.collision_box, self.pos, self.angle, self.radius):
                    self.visual_effect(self, entities, collision.pos)
                    Fun.damage_calculation(collision, self.damage, self.damage_type, death_message="Zapped")
                    self.on_hit_handler(collision, entities, level)
            self.duration -= 1

    def draw(self, win, scrolling):
        if self.duration > 0:
            pg.draw.line(win, self.colour,
                         [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]],
                         Fun.move_with_vel_angle([self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]],
                                                 self.radius, self.angle), width=3)

    def hit_wall(self, entities, level):
        pass


class Flechette(BasicBullet):
    def __init__(self, pos, angle, info, owner):
        BasicBullet.__init__(self, pos, angle, info, owner)
        self.fire = False
        self.explosion_primer = False
        self.explosion = False
        self.laser = True
        self.laser_based = True
        self.melee = False
        # Radius is the length of the laser
        if "Colour" in info[4]:
            self.colour = info[4]["Colour"]
        self.visual_effect = basic_visual
        if "Damage type" in info[4]:
            self.damage_type = info[4]["Damage type"]
        else:
            self.damage_type = "Physical"
        self.ignore_armour = not "No ignore armour" in info[4]

    def act(self, entities, level):
        if self.duration > 0:
            self.pos[0] -= self.speed * math.cos(self.angle * math.pi / 180)
            self.pos[1] -= self.speed * math.sin(self.angle * math.pi / 180)
            # Check for collisions
            for collision in entities["entities"]:
                if self.owner.team == collision.team:
                    continue
                if Fun.collision_rect_laser(collision.collision_box, self.pos, self.angle, self.radius):
                    self.visual_effect(self, entities)
                    Fun.damage_calculation(collision, self.damage, self.damage_type, ignore_armour=self.ignore_armour,
                                           ignore_res=self.ignore_res, death_message="Is Swiss cheese")
                    self.on_hit_handler(collision, entities, level)

            # if self.angle != self.original_angle or self.speed != 0:
            #     self.points_to_check = []
            #     for i in range(self.radius):
            #         self.points_to_check.append([self.pos[0] - i * math.cos(self.angle * math.pi / 180),
            #                                      self.pos[1] - i * math.sin(self.angle * math.pi / 180)])
            #     self.end_point = self.points_to_check[-1]
            #     self.original_angle = self.angle

            self.duration -= 1

    def draw(self, win, scrolling):
        if self.duration > 0:
            pg.draw.line(win, self.colour,
                         [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]],
                         Fun.move_with_vel_angle([self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]],
                                                 self.radius, self.angle), width=2)

    def hit_wall(self, entities, level):
        normal_bullet_wall_hit(self, level, entities)


class LaserWithCollision(BasicBullet):
    def __init__(self, pos, angle, info, owner):
        BasicBullet.__init__(self, pos, angle, info, owner)
        self.fire = False
        self.explosion_primer = False
        self.explosion = False
        self.laser = True
        self.laser_based = True
        self.melee = False
        self.speed = 0  # This variant cannot move or else it would break it all apart
        # Radius is the length of the laser
        self.colour = Fun.WHITE
        if "Colour" in info[4]:
            self.colour = info[4]["Colour"]
        self.visual_effect = laser_visual
        # self.points_to_check = []
        # for i in range(self.radius):
        #     self.points_to_check.append([self.pos[0] - i * math.cos(self.angle * math.pi / 180),
        #                                  self.pos[1] - i * math.sin(self.angle * math.pi / 180)])
        # self.end_point = self.points_to_check[-1]
        if "Damage type" in info[4]:
            self.damage_type = info[4]["Damage type"]
        else:
            self.damage_type = "Energy"
        self.new_lasers = []     # Pos, angle, length

    def act(self, entities, level):
        # Make the collision check work both ways
        if self.duration > 0:
            self.pos[0] -= self.speed * math.cos(self.angle * math.pi / 180)
            self.pos[1] -= self.speed * math.sin(self.angle * math.pi / 180)
            # Check for collisions
            for collision in entities["entities"]:
                # for point in self.points_to_check:
                if Fun.collision_rect_laser(collision.collision_box, self.pos, self.angle, self.radius):
                    self.visual_effect(self, entities, collision.pos)
                    Fun.damage_calculation(collision, self.damage, self.damage_type, death_message="Has a big hole to fill")
                    self.on_hit_handler(collision, entities, level)

            self.duration -= 1

    def draw(self, win, scrolling):
        if self.duration > 0:
            pg.draw.line(win, self.colour,
                         [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]],
                         Fun.move_with_vel_angle([self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]],
                                                 self.radius, self.angle), width=3)

    def hit_wall(self, entities, level):
        for wall in level["map"]:

            collision = Fun.collision_rect_laser(wall, self.pos, self.angle, self.radius)
            if collision:
                # Get the velocity has a list
                length = Fun.distance_between(collision[0], self.pos)

                self.radius = length
                return


class Melee(BasicBullet):
    def __init__(self, pos, angle, info, owner):
        BasicBullet.__init__(self, pos, angle, info, owner)
        self.wall_physics = melee_bullet_wall_hit

        self.fire = False
        self.explosion_primer = False
        self.explosion = False
        self.laser = False
        self.laser_based = False
        self.melee = True

        self.damage_type = "Melee"
        if "Damage type" in info[4]:
            self.damage_type = info[4]["Damage type"]
        self.always_counter = False
        if "Always Counter" in info[4]:
            self.always_counter = True

        self.allow_counter = True
        if "Counter not allowed" in info[4]:
            self.allow_counter = False

        self.visual_effect = melee_visual
        # Sound system
        # Make these take the info from the extra info
        if "Start sound" in info[4]:
            Fun.play_sound(info[4]["Start sound"], "SFX", modified_volume=0.8)
        # self.hit_sound = "Melee hit 1"

    def act(self, entities, level):
        if self.duration > 0:
            # Make the bullet move based on the angle
            self.pos[0] -= self.speed * math.cos(self.angle * math.pi / 180)
            self.pos[1] -= self.speed * math.sin(self.angle * math.pi / 180)

            # Add a visual effect and noise for the parry, might add an "angle requirement"

            # Check for collisions
            for collision in entities["entities"]:
                if self.owner.team == collision.team:
                    continue

                if Fun.collision_rect_circle(collision.collision_box.left, collision.collision_box.top,
                                             collision.collision_box.width, collision.collision_box.height,
                                             self.pos[0], self.pos[1], self.radius):
                    Fun.damage_calculation(collision, self.damage, self.damage_type, death_message="Brutalized in melee", ignore_res=self.ignore_res)
                    self.on_hit_handler(collision, entities, level)
                    self.visual_effect(self, entities)
                    self.duration = 0
                    # Fun.play_sound(self.hit_sound, "SFX")

            self.duration -= 1

    def draw(self, win, scrolling):
        if self.duration > 0:
            pg.draw.circle(win, (255, 207, 0), [self.pos[0] + scrolling[0],
                                                self.pos[1] + scrolling[1]], self.radius, 1)


class Melee2(BasicBullet):  # Loses speed like a grenade
    def __init__(self, pos, angle, info, owner):
        BasicBullet.__init__(self, pos, angle, info, owner)
        self.wall_physics = melee_bullet_wall_hit

        self.fire = False
        self.explosion_primer = False
        self.explosion = False
        self.laser = False
        self.laser_based = False
        self.melee = True
        self.visual_effect = melee_visual
        if "Damage type" in info[4]:
            self.damage_type = info[4]["Damage type"]
        else:
            self.damage_type = "Melee"

    def act(self, entities, level):
        if self.duration > 0:
            # Make the bullet move based on the angle
            self.pos[0] -= self.speed * math.cos(self.angle * math.pi / 180)
            self.pos[1] -= self.speed * math.sin(self.angle * math.pi / 180)
            # Slow downs the bullet
            if self.speed > 0:
                self.speed -= 0.05
                if self.speed < 0:
                    self.speed = 0

            # Check for collisions
            for collision in entities["entities"]:
                if Fun.collision_rect_circle(collision.collision_box.left, collision.collision_box.top,
                                             collision.collision_box.width, collision.collision_box.height,
                                             self.pos[0], self.pos[1], self.radius):
                    Fun.damage_calculation(collision, self.damage, self.damage_type, death_message="Brutalized in melee", ignore_res=self.ignore_res)
                    self.on_hit_handler(collision, entities, level)
                    self.duration = 0
                    self.visual_effect(self, entities)

            self.duration -= 1

    def draw(self, win, scrolling):
        if self.duration > 0:
            pg.draw.circle(win, (255, 207, 0), [self.pos[0] + scrolling[0],
                                                self.pos[1] + scrolling[1]], self.radius, 1)


class Melee3(BasicBullet):  # Loses speed like a grenade
    def __init__(self, pos, angle, info, owner):
        BasicBullet.__init__(self, pos, angle, info, owner)
        self.wall_physics = melee_bullet_wall_hit

        self.fire = False
        self.explosion_primer = False
        self.explosion = True
        self.laser = False
        self.laser_based = False
        self.melee = True
        self.visual_effect = melee_visual
        if "Damage type" in info[4]:
            self.damage_type = info[4]["Damage type"]
        else:
            self.damage_type = "Melee"

        self.growth = 1
        if "Growth" in info[4]:
            self.growth = info[4]["Growth"]

    def act(self, entities, level):
        if self.duration > 0:
            # Make the bullet move based on the angle
            self.pos[0] -= self.speed * math.cos(self.angle * math.pi / 180)
            self.pos[1] -= self.speed * math.sin(self.angle * math.pi / 180)

            # self.radius = self.og_info[2] + (self.og_info[1] - self.duration) * self.growth
            self.radius += self.growth

            # Add a visual effect and noise for the parry, might add an "angle requirement"
            # Check for collisions
            for collision in entities["entities"]:
                if self.owner.team == collision.team:
                    continue
                if Fun.collision_rect_circle(collision.collision_box.left, collision.collision_box.top,
                                             collision.collision_box.width, collision.collision_box.height,
                                             self.pos[0], self.pos[1], self.radius):
                    Fun.damage_calculation(collision, self.damage, self.damage_type, death_message="Brutalized in melee", ignore_res=self.ignore_res)
                    self.on_hit_handler(collision, entities, level)
                    # self.duration = 0
                    self.visual_effect(self, entities)

            self.duration -= 1

    def draw(self, win, scrolling):
        if self.duration > 0:
            pg.draw.circle(win, self.colour, [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]], self.radius, round(self.radius//3 + 0.2))


# The electric projectile is a small segment.
# The base of it move to the end of the previous segment at each 3 frame.

# Free variables
#   - Angle modifier
#       Range of how much the angle can change between segments

# Planned variants
#   - Normal
#       Segments move along an imaginary line
#   - Homing
#       Each segment tries to go the closest valid target
#   - Splitting
#       Act like the normal variant but, at the end of a segment, can randomly create more than one segment
class Electric(BasicBullet):
    def __init__(self, pos, angle, info, owner):
        BasicBullet.__init__(self, pos, angle, info, owner)
        self.fire = False
        self.explosion_primer = False
        self.explosion = False
        self.laser = False
        self.laser_based = True
        self.melee = False
        self.visual_effect = electric_visual

        # Electric
        self.angle_modifier = info[4]["Angle modifier"]  # Range of how much the angle can change between segments
        self.electric_angle = self.angle + random.uniform(-self.angle_modifier, self.angle_modifier)

        self.points_to_check = []
        for i in range(self.radius):
            self.points_to_check.append([self.pos[0] - i * math.cos(self.electric_angle * math.pi / 180),
                                         self.pos[1] - i * math.sin(self.electric_angle * math.pi / 180)])
        self.end_point = self.points_to_check[-1]
        self.colour = Fun.LIGHTNING
        if "Colour" in info[4]:
            self.colour = info[4]["Colour"]
        if "Damage type" in info[4]:
            self.damage_type = info[4]["Damage type"]
        else:
            self.damage_type = "Energy"

    def act(self, entities, level):
        if self.duration > 0:
            # Check it hits someone
            for collision in entities["entities"]:
                if collision.team == self.team:
                    continue
                for point in self.points_to_check:
                    if collision.collision_box.collidepoint(point):
                        self.visual_effect(self, entities)
                        Fun.damage_calculation(collision, self.damage, self.damage_type, death_message="Zapped")
                        self.on_hit_handler(collision, entities, level)
                        break

            # Handle the next segments
            if self.duration % 3 == 0:
                self.pos = self.end_point
                # Change electric angle with restriction
                direction_mod = 1
                if self.angle < self.electric_angle:
                    direction_mod = -1
                self.electric_angle += random.uniform(0, self.angle_modifier) * direction_mod

                # Update the hit scan
                self.points_to_check = []
                for i in range(self.radius):
                    self.points_to_check.append([self.pos[0] - i * math.cos(self.electric_angle * math.pi / 180),
                                                 self.pos[1] - i * math.sin(self.electric_angle * math.pi / 180)])
                self.end_point = self.points_to_check[-1]

            # Lower duration
            self.duration -= 1

    def draw(self, win, scrolling):
        if self.duration > 0:
            pg.draw.line(win, self.colour,
                         [self.pos[0] + scrolling[0],
                          self.pos[1] + scrolling[1]],
                         [self.end_point[0] + scrolling[0],
                          self.end_point[1] + scrolling[1]])

    def hit_wall(self, entities, level):
        pass


class HomingElectric(BasicBullet):
    def __init__(self, pos, angle, info, owner):
        BasicBullet.__init__(self, pos, angle, info, owner)
        self.fire = False
        self.explosion_primer = False
        self.explosion = False
        self.laser = False
        self.laser_based = True
        self.melee = False

        self.target = info[4]["Target"]
        self.targeting_range = info[4]["Targeting range"]
        self.visual_effect = electric_visual
        # Electric
        self.angle_modifier = info[4]["Angle modifier"]  # Range of how much the angle can change between segments
        self.electric_angle = self.angle + random.randint(-self.angle_modifier, self.angle_modifier)

        self.points_to_check = []
        for i in range(self.radius):
            self.points_to_check.append([self.pos[0] - i * math.cos(self.electric_angle * math.pi / 180),
                                         self.pos[1] - i * math.sin(self.electric_angle * math.pi / 180)])
        self.end_point = self.points_to_check[-1]
        self.colour = Fun.LIGHTNING
        if "Colour" in info[4]:
            self.colour = info[4]["Colour"]
        if "Damage type" in info[4]:
            self.damage_type = info[4]["Damage type"]
        else:
            self.damage_type = "Energy"

    def act(self, entities, level):
        if self.duration > 0:
            # Check it hits someone
            for collision in entities["entities"]:
                for point in self.points_to_check:
                    if collision.collision_box.collidepoint(point):
                        self.visual_effect(self, entities)
                        Fun.damage_calculation(collision, self.damage, self.damage_type, death_message="Zapped")
                        self.on_hit_handler(collision, entities, level)
                        break

            # Handle the next segments
            if self.duration % 3 == 0:
                self.pos = self.end_point

                # Homing capability
                target = Fun.find_closest_in_circle(self, entities, self.targeting_range, self.target)
                if target:
                    self.angle = Fun.angle_between(target, self.pos)
                    self.electric_angle = self.angle

                # Update the hit scan
                self.points_to_check = []
                for i in range(self.radius):
                    self.points_to_check.append([self.pos[0] - i * math.cos(self.electric_angle * math.pi / 180),
                                                 self.pos[1] - i * math.sin(self.electric_angle * math.pi / 180)])
                self.end_point = self.points_to_check[-1]

            # Lower duration
            self.duration -= 1

    def draw(self, win, scrolling):
        if self.duration > 0:
            pg.draw.line(win, self.colour,
                         [self.pos[0] + scrolling[0],
                          self.pos[1] + scrolling[1]],
                         [self.end_point[0] + scrolling[0],
                          self.end_point[1] + scrolling[1]])

    def hit_wall(self, entities, level):
        pass


class SplittingElectric(BasicBullet):
    def __init__(self, pos, angle, info, owner):
        BasicBullet.__init__(self, pos, angle, info, owner)
        self.fire = False
        self.explosion_primer = False
        self.explosion = False
        self.laser = False
        self.laser_based = True
        self.melee = False
        self.visual_effect = electric_visual

        # Electric
        self.angle_modifier = info[4]["Angle modifier"]  # Range of how much the angle can change between segments
        self.electric_angle = self.angle + random.randint(-self.angle_modifier, self.angle_modifier)
        self.split_rate = info[4]["Split rate"]
        self.target = info[4]["Target"]

        self.points_to_check = []
        for i in range(self.radius):
            self.points_to_check.append([self.pos[0] - i * math.cos(self.electric_angle * math.pi / 180),
                                         self.pos[1] - i * math.sin(self.electric_angle * math.pi / 180)])
        self.end_point = self.points_to_check[-1]

        self.colour = Fun.LIGHTNING
        if "Colour" in info[4]:
            self.colour = info[4]["Colour"]

        if "Damage type" in info[4]:
            self.damage_type = info[4]["Damage type"]
        else:
            self.damage_type = "Energy"

    def act(self, entities, level):
        if self.duration > 0:
            # Check it hits someone
            for collision in entities["entities"]:
                for point in self.points_to_check:
                    if collision.collision_box.collidepoint(point):
                        self.visual_effect(self, entities)
                        Fun.damage_calculation(collision, self.damage, self.damage_type, death_message="Zapped")
                        self.on_hit_handler(collision, entities, level)
                        break

            # Handle the next segments
            if self.duration % 3 == 0:
                self.pos = self.end_point
                # Change electric angle with no restriction
                self.electric_angle += random.randint(-self.angle_modifier, self.angle_modifier)

                # Splitting mechanic
                # Feel cute
                # might add a limit
                if random.randint(0, self.split_rate) == 0:
                    spawn_bullet(
                        self.owner, entities,
                        Electric,
                        [self.pos[0], self.pos[1]],
                        self.electric_angle,
                        [self.speed, self.duration, self.radius, self.damage,
                         {"Angle modifier": self.angle_modifier,
                          "Split rate": self.split_rate,
                          "Colour": self.colour}])
                # Update the hit scan
                self.points_to_check = []
                for i in range(self.radius):
                    self.points_to_check.append([self.pos[0] - i * math.cos(self.electric_angle * math.pi / 180),
                                                 self.pos[1] - i * math.sin(self.electric_angle * math.pi / 180)])
                self.end_point = self.points_to_check[-1]

            # Lower duration
            self.duration -= 1

    def draw(self, win, scrolling):
        if self.duration > 0:
            pg.draw.line(win, self.colour,
                         [self.pos[0] + scrolling[0],
                          self.pos[1] + scrolling[1]],
                         [self.end_point[0] + scrolling[0],
                          self.end_point[1] + scrolling[1]])

    def hit_wall(self, entities, level):
        pass


class Sword(BasicBullet):
    def __init__(self, pos, angle, info, owner):
        BasicBullet.__init__(self, pos, angle, info, owner)
        self.fire = False
        self.explosion_primer = False
        self.explosion = False
        self.laser = False
        self.laser_based = True
        self.melee = False

        # Sword shit
        self.sword_angle = self.angle
        self.swing_speed = info[4]["Swing Speed"]
        self.sword_limit = info[4]["Swing Limit"]
        if "Sword angle" in info[4]:
            self.sword_angle = info[4]["Sword angle"]

        self.points_to_check = []
        for i in range(self.radius):
            self.points_to_check.append([self.pos[0] - i * math.cos(self.sword_angle * math.pi / 180),
                                         self.pos[1] - i * math.sin(self.sword_angle * math.pi / 180)])
        self.end_point = self.points_to_check[-1]
        if "Damage type" in info[4]:
            self.damage_type = info[4]["Damage type"]
        else:
            self.damage_type = "Physical"

    def act(self, entities, level):
        if self.duration > 0:
            # Make the bullet move based on the angle
            self.pos[0] -= self.speed * math.cos(self.angle * math.pi / 180)
            self.pos[1] -= self.speed * math.sin(self.angle * math.pi / 180)

            # Check if the swords hits someone
            for collision in entities["entities"]:
                for point in self.points_to_check:
                    if collision.collision_box.collidepoint(point):
                        Fun.damage_calculation(collision, self.damage, self.damage_type, death_message="Slashed by summoned swords")
                        self.on_hit_handler(collision, entities, level)
                        break

            # Swing the sword
            self.sword_angle += self.swing_speed
            if self.sword_limit:
                if not self.angle - self.sword_limit[0] < self.sword_angle < self.angle + self.sword_limit[0]:
                    self.swing_speed *= -1

            # Update the hit scan
            self.points_to_check = []
            for i in range(self.radius):
                self.points_to_check.append([self.pos[0] - i * math.cos(self.sword_angle * math.pi / 180),
                                             self.pos[1] - i * math.sin(self.sword_angle * math.pi / 180)])
            self.end_point = self.points_to_check[-1]

            # Lower duration
            self.duration -= 1

    def draw(self, win, scrolling):
        if self.duration > 0:
            # Draw the blade of the sword
            middle_point = Fun.midpoint_between(self.pos, self.end_point)
            pg.draw.polygon(win, self.colour,
                            [
                                [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]],
                                [middle_point[0] - 1 * math.cos((self.sword_angle + 90) * math.pi / 180) + scrolling[0],
                                 middle_point[1] - 1 * math.sin((self.sword_angle + 90) * math.pi / 180) + scrolling[
                                     1]],
                                [self.end_point[0] + scrolling[0], self.end_point[1] + scrolling[1]],
                                [middle_point[0] - 1 * math.cos((self.sword_angle - 90) * math.pi / 180) + scrolling[
                                    0],
                                 middle_point[1] - 1 * math.sin((self.sword_angle - 90) * math.pi / 180) + scrolling[
                                     1]],

                            ], 1)
            # Draw the guard of the sword
            guard_pos = [self.pos[0] - (self.radius / 4) * math.cos(self.sword_angle * math.pi / 180),
                         self.pos[1] - (self.radius / 4) * math.sin(self.sword_angle * math.pi / 180)]
            pg.draw.line(win, self.colour,
                         [guard_pos[0] - 5 * math.cos((self.sword_angle - 90) * math.pi / 180) + scrolling[0],
                          guard_pos[1] - 5 * math.sin((self.sword_angle - 90) * math.pi / 180) + scrolling[1]],
                         [guard_pos[0] - 5 * math.cos((self.sword_angle + 90) * math.pi / 180) + scrolling[0],
                          guard_pos[1] - 5 * math.sin((self.sword_angle + 90) * math.pi / 180) + scrolling[1]]
                         )

    def hit_wall(self, entities, level):
        pass


class HomingSword(BasicBullet):
    def __init__(self, pos, angle, info, owner):
        BasicBullet.__init__(self, pos, angle, info, owner)
        self.fire = False
        self.explosion_primer = False
        self.explosion = False
        self.laser = False
        self.laser_based = True
        self.melee = False

        # Sword shit
        self.sword_angle = self.angle
        self.swing_speed = info[4]["Swing Speed"]
        self.sword_limit = info[4]["Swing Limit"]
        self.targeting_range = info[4]["Targeting range"]
        self.targeting_time = info[4]["Targeting time"]

        self.points_to_check = []
        for i in range(self.radius):
            self.points_to_check.append([self.pos[0] - i * math.cos(self.sword_angle * math.pi / 180),
                                         self.pos[1] - i * math.sin(self.sword_angle * math.pi / 180)])
        self.end_point = self.points_to_check[-1]
        if "Damage type" in info[4]:
            self.damage_type = info[4]["Damage type"]
        else:
            self.damage_type = "Physical"

    def act(self, entities, level):
        if self.targeting_time > 0:
            # Spends some time homing on a target
            target = Fun.find_closest_in_circle(self, entities, self.targeting_range, "entities")
            if target:
                self.angle = Fun.angle_between(target, self.pos)
                self.sword_angle = self.angle
            self.targeting_time -= 1
            self.points_to_check = []
            for i in range(self.radius):
                self.points_to_check.append([self.pos[0] - i * math.cos(self.sword_angle * math.pi / 180),
                                             self.pos[1] - i * math.sin(self.sword_angle * math.pi / 180)])
            self.end_point = self.points_to_check[-1]
            if self.targeting_time == 0:
                Fun.play_sound("Sword launch")
                pass

        elif self.duration > 0:
            # Make the bullet move based on the angle
            self.pos = Fun.move_with_vel_angle(self.pos, self.speed, self.angle)

            # Check if the swords hits someone
            for collision in entities["entities"]:
                for point in self.points_to_check:
                    if collision.collision_box.collidepoint(point):
                        Fun.damage_calculation(collision, self.damage, self.damage_type, death_message="Slashed by summoned swords")
                        self.on_hit_handler(collision, entities, level)
                        break

            # Swing the sword
            self.sword_angle += self.swing_speed
            if self.sword_limit:
                if not self.angle - self.sword_limit[0] < self.sword_angle < self.angle + self.sword_limit[0]:
                    self.swing_speed *= -1

            # Update the hit scan
            self.points_to_check = []
            for i in range(self.radius):
                self.points_to_check.append([self.pos[0] - i * math.cos(self.sword_angle * math.pi / 180),
                                             self.pos[1] - i * math.sin(self.sword_angle * math.pi / 180)])
            self.end_point = self.points_to_check[-1]

            self.duration -= 1

    def draw(self, win, scrolling):
        if self.duration > 0:
            # Draw the blade of the sword
            middle_point = Fun.midpoint_between(self.pos, self.end_point)
            pg.draw.polygon(win, self.colour,
                            [
                                [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]],
                                [middle_point[0] - 1 * math.cos((self.sword_angle + 90) * math.pi / 180) + scrolling[0],
                                 middle_point[1] - 1 * math.sin((self.sword_angle + 90) * math.pi / 180) + scrolling[
                                     1]],
                                [self.end_point[0] + scrolling[0], self.end_point[1] + scrolling[1]],
                                [middle_point[0] - 1 * math.cos((self.sword_angle - 90) * math.pi / 180) + scrolling[
                                    0],
                                 middle_point[1] - 1 * math.sin((self.sword_angle - 90) * math.pi / 180) + scrolling[
                                     1]],

                            ], 1)
            # Draw the guard of the sword
            guard_pos = [self.pos[0] - (self.radius / 4) * math.cos(self.sword_angle * math.pi / 180),
                         self.pos[1] - (self.radius / 4) * math.sin(self.sword_angle * math.pi / 180)]
            pg.draw.line(win, self.colour,
                         [guard_pos[0] - self.radius / 5 * math.cos((self.sword_angle - 90) * math.pi / 180) +
                          scrolling[0],
                          guard_pos[1] - self.radius / 5 * math.sin((self.sword_angle - 90) * math.pi / 180) +
                          scrolling[1]],
                         [guard_pos[0] - self.radius / 5 * math.cos((self.sword_angle + 90) * math.pi / 180) +
                          scrolling[0],
                          guard_pos[1] - self.radius / 5 * math.sin((self.sword_angle + 90) * math.pi / 180) +
                          scrolling[1]]
                         )

    def hit_wall(self, entities, level):
        pass


class RazorWind(BasicBullet):
    def __init__(self, pos, angle, info, owner):
        BasicBullet.__init__(self, pos, angle, info, owner)
        self.fire = False
        self.explosion_primer = False
        self.explosion = False
        self.laser = False
        self.laser_based = True
        self.melee = False

        self.angle_modifier = info[4]["Angle modifier"]
        # self.segment = info[4]["Segment amount"]    # used for now

        self.points_to_check = []
        self.end_points = []
        self.update_points()
        # self.width, self.height = 128, 128
        points_x, points_y = [pos[0]], [pos[1]]
        for p in self.end_points:
            points_x.append(p[0])
            points_y.append(p[1])
        self.width, self.height = (max(points_x) - min(points_x)), (max(points_y) - min(points_y))

        if "Damage type" in info[4]:
            self.damage_type = info[4]["Damage type"]
        else:
            self.damage_type = "Physical"

    def act(self, entities, level):
        if self.duration > 0:
            # Make the bullet move based on the angle
            self.pos = Fun.move_with_vel_angle(self.pos, self.speed, self.angle)

            # Check if the swords hits someone
            for collision in entities["entities"]:
                if collision.team == self.team:
                    continue
                for point in self.points_to_check:
                    if collision.collision_box.collidepoint(point):
                        Fun.damage_calculation(collision, self.damage, self.damage_type, ignore_res=self.ignore_res, death_message="Slashed by the wind")
                        self.on_hit_handler(collision, entities, level)
                        break

            # Update the hit scan
            self.update_points()

            # Lower duration
            self.duration -= 1

    def draw(self, win, scrolling):
        if self.duration > 0:
            for p in self.end_points:
                pg.draw.line(win, self.colour,
                             [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]],
                             [p[0] + scrolling[0], p[1] + scrolling[1]], width=4)

            # pg.draw.circle(win, (255, 0, 255),
            #                [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]],
            #                5)
            # pg.draw.arc(win, self.colour,
            #             [self.pos[0] + scrolling[0]- self.width//2, self.pos[1] + scrolling[1] -  self.height//2,
            #              self.width, self.height],
            #             math.radians(self.angle*-1 - self.angle_modifier + 180),
            #             math.radians(self.angle*-1 + self.angle_modifier + 180))

    def hit_wall(self, entities, level):
        pass

    def update_points(self):
        self.points_to_check = []
        self.end_points = []
        for i in range(self.radius):
            self.points_to_check.append(Fun.move_with_vel_angle(self.pos, i, self.angle + self.angle_modifier))
        self.end_points.append(self.points_to_check[-1])
        for i in range(self.radius):
            self.points_to_check.append(Fun.move_with_vel_angle(self.pos, i, self.angle - self.angle_modifier))
        self.end_points.append(self.points_to_check[-1])


class Gas(BasicBullet):
    def __init__(self, pos, angle, info, owner):
        BasicBullet.__init__(self, pos, angle, info, owner)
        self.wall_physics = melee_bullet_wall_hit

        self.fire = False
        self.explosion_primer = False
        self.explosion = False
        self.laser = False
        self.laser_based = False
        self.melee = False

        self.damage_type = "Physical"
        if "Damage type" in info[4]:
            self.damage_type = info[4]["Damage type"]

        self.secondary_explosion = {"Duration": 8, "Growth": 5, "Damage mod": 5}
        if "Secondary explosion" in info[4]:
            self.secondary_explosion = info[4]["Secondary explosion"]

        self.slowdown_rate = 0.05
        if "Slowdown rate" in info[4]:
            self.slowdown_rate = info[4]["Slowdown rate"]

        self.visual_effect = basic_visual
        # self.hit_sound = "Melee hit 1"

    def act(self, entities, level):
        if self.duration > 0:
            # Make the bullet move based on the angle
            self.pos[0] -= self.speed * math.cos(self.angle * math.pi / 180)
            self.pos[1] -= self.speed * math.sin(self.angle * math.pi / 180)
            bullet_slowdown(self)
            # Add a visual effect and noise for the parry, might add an "angle requirement"
                # checked_positions = []
            for b in entities["bullets"]:
                if not (b.fire or b.explosion):
                    continue
                if Fun.collision_circle_circle(self.pos, self.radius, b.pos, b.radius):

                    spawn_bullet(
                        self.owner, entities,
                        ExplosionSecondary,
                        self.pos,
                        self.angle,
                        [0, 5, self.radius, self.damage, self.secondary_explosion])
                    # Remove the gas
                    self.duration = 0
                    break

            # Check for collisions
            for collision in entities["entities"]:
                if Fun.collision_rect_circle(collision.collision_box.left, collision.collision_box.top,
                                             collision.collision_box.width, collision.collision_box.height,
                                             self.pos[0], self.pos[1], self.radius):
                    Fun.damage_calculation(collision, self.damage, self.damage_type, death_message="Smelled my farts")
                    self.on_hit_handler(collision, entities, level)
                    self.visual_effect(self, entities)
                    # self.duration = 0
                    # Fun.play_sound(self.hit_sound, "SFX")

            self.duration -= 1

    def draw(self, win, scrolling):
        if self.duration > 0:
            Fun.draw_transparent_circle(win, (self.pos[0] + scrolling[0],
                                              self.pos[1] + scrolling[1], self.radius), self.colour, 128)


# Probably gonna be used for when I put all the weapons into a JSON file
string_to_bullet_class = {
    "Bullet": Bullet,
    "Slowing": BulletSlowing,
    "Danmaku": BulletDanmaku,
    "Danmaku2": BulletDanmaku2,
    "Fire": Fire,
    "Napalm": Napalm,
    "Flare": Flare,
    "Boom - Delay/Contact": ExplosionPrimaryType1,
    "Boom - Contact": ExplosionPrimaryType2,
    "Grenade": GrenadeType1,
    "Flashbang": GrenadeType4,
    "GrenadeType7": GrenadeType7,
    "Missile": Missile,
    "Boom - Insta": ExplosionSecondary,
    "Laser": Laser,
    "Melee": Melee,
    # Skill related bullets
    "Electric": Electric,
    "Electric Homing": HomingElectric,
    "Electric Splitting": SplittingElectric,
    "Sword": Sword,
    "Homing Sword": HomingSword,
    "Razor Wind": RazorWind
}
