import math
import random
import sys

import Bullets
import Entity
import Fun
import Items
import Particles


def handle_skill_normal(self, skill_id, skill_input):
    self.skills[skill_id].first_active_frame = False
    if skill_input and self.skills[skill_id].recharge >= self.skills[skill_id].recharge_max:
        # self.skills[skill_id].active = True
        self.skills[skill_id].recharge = 0
    # Deactivate Skills
    # if self.skills[skill_id].active:
    #     self.skills[skill_id].active = False
        self.skills[skill_id].first_active_frame = True
        return True
    return False


def handle_skill_hold(self, skill_id, skill_input):
    if skill_input and self.skills[skill_id].recharge >= self.skills[skill_id].recharge_max:
            self.skills[skill_id].active = True
            self.skills[skill_id].recharge -= self.skills[skill_id].depletion_rate
    # Deactivate Skills
    if self.skills[skill_id].active:
        # deplete the recharge
        self.skills[skill_id].recharge -= self.skills[skill_id].depletion_rate
        # end skill if recharge at 0
        if self.skills[skill_id].recharge <= 0:
            self.skills[skill_id].recharge = 0
            self.skills[skill_id].active = False
        # end skill if the button isn't pressed
        if not skill_input:
            self.skills[skill_id].active = False
        return True
    return False


def handle_skill_switch(self, skill_id, skill_input):
    if skill_input and self.skills[skill_id].recharge >= self.skills[skill_id].recharge_max:

        self.skills[skill_id].active = True
        self.skills[skill_id].recharge -= self.skills[skill_id].depletion_rate

    # Deactivate Skills
    if self.skills[skill_id].active:
        self.skills[skill_id].first_active_frame = False
        if self.skills[skill_id].recharge >= self.skills[skill_id].recharge_max:
            self.skills[skill_id].first_active_frame = True
        # deplete the recharge
        self.skills[skill_id].recharge -= self.skills[skill_id].depletion_rate
        # end skill if recharge at 0
        if self.skills[skill_id].recharge <= 0:
            self.skills[skill_id].recharge = 0
            self.skills[skill_id].active = False

        # end skill if the button is pressed again
        if skill_input and self.skills[skill_id].recharge < 75:
            self.skills[skill_id].active = False
        self.skills[skill_id].last_active_frame = not self.skills[skill_id].active
        return True
    return False


def handle_skill_switch_no_cancel(self, skill_id, skill_input):
    if skill_input and self.skills[skill_id].recharge >= self.skills[skill_id].recharge_max:

        self.skills[skill_id].active = True
        # self.skills[skill_id].recharge -= self.skills[skill_id].depletion_rate

    # Deactivate Skills
    if self.skills[skill_id].active:
        self.skills[skill_id].first_active_frame = False
        self.skills[skill_id].last_active_frame = False
        if self.skills[skill_id].recharge >= self.skills[skill_id].recharge_max:
            self.skills[skill_id].first_active_frame = True
        # deplete the recharge
        self.skills[skill_id].recharge -= self.skills[skill_id].depletion_rate
        # end skill if recharge at 0
        if self.skills[skill_id].recharge <= 0:
            self.skills[skill_id].recharge = 0
            self.skills[skill_id].active = False
        if not self.skills[skill_id].active:
            self.skills[skill_id].last_active_frame = True

        return True
    return False


def skills_manager(self, entities, level):
    skill_inputs = ["Skill 1", "Skill 2"]
    for j in range(len(self.skills)):
        skill_input = self.input[skill_inputs[j]]
        # Recharge Skills
        if self.skills[j].recharge <= self.skills[j].recharge_max and not self.skills[j].active:
            self.skills[j].recharge += self.skills[j].recharge_rate

        if {
            "normal": handle_skill_normal,
            "hold": handle_skill_hold,
            "switch": handle_skill_switch,
            "switch no cancel": handle_skill_switch_no_cancel,
        }[self.skills[j].activation_mode](self, j, skill_input):

            self.skills[j].func(self, self.skills[j], entities, level)


class Skill:
    def __init__(self, skill):
        self.name = skill["name"]
        self.skill_class = skill["class"]
        self.description = skill["description"]

        self.func = skill["func"]
        if type(self.func) == str:
            self.func = getattr(sys.modules[__name__], self.func)
        self.activation_mode = skill["activation mode"]
        self.active = False

        self.recharge = 0
        self.recharge_max = 100
        self.recharge_rate = 1
        self.depletion_rate = 1
        if "recharge max" in skill: self.recharge_max = skill["recharge max"]
        if "recharge rate" in skill: self.recharge_rate = skill["recharge rate"]
        if "depletion rate" in skill: self.depletion_rate = skill["depletion rate"]

        self.free_var = skill["free variables"]
        self.sprite = False
        self.first_active_frame = False
        self.last_active_frame = False


# |THR-1|---------------------------------------------------------------------------------------------------------------
# |Lord|----------------------------------------------------------------------------------------------------------------
def leopold_gauntlet_punch(self, skill, entities, level):
    self.no_shoot_state += 1
    self.status["Slowness"] += 1
    # Visual warning
    corner_1 = Fun.move_with_vel_angle(self.pos, 32, self.angle + 90)
    corner_2 = Fun.move_with_vel_angle(corner_1, 128, self.angle)
    corner_3 = Fun.move_with_vel_angle(corner_2, 64, self.angle - 90)
    corner_4 = Fun.move_with_vel_angle(corner_3, 128, self.angle + 180)
    points = [self.pos, corner_1, corner_2, corner_3, corner_4]

    entities["background particles"].append(Particles.TransparentPolygon(points, Fun.DARK_RED, 1, 96))
    mod = 1 - skill.recharge / skill.recharge_max
    corner_1_p2 = Fun.move_with_vel_angle(self.pos, 32, self.angle + 90)
    corner_2_p2 = Fun.move_with_vel_angle(corner_1_p2, 128 * mod, self.angle)
    corner_3_p2 = Fun.move_with_vel_angle(corner_2_p2, 64, self.angle - 90)
    corner_4_p2 = Fun.move_with_vel_angle(corner_3_p2, 128 * mod, self.angle + 180)
    points_p2 = [self.pos, corner_1_p2, corner_2_p2, corner_3_p2, corner_4_p2]
    entities["background particles"].append(Particles.TransparentPolygon(points_p2, Fun.DARK_RED, 1, 96))

    if mod == 1:
        damage = 150
        if "IS VERSUS" in self.free_var:
            damage = 80
        entities["screen shake"] = [20, 5, self.aim_angle, 20]

        if "Taunt" in self.free_var:
            self.agro *= 1.5
            Particles.random_particle_2_circle(entities, self.pos, 4, 45, 36, colour=Fun.RED, angle_mod=180 * random.random())
        knockback = 7
        if "Giga ton Punch" in self.free_var:
            knockback = 14
        self.agro += 10
        # hits = False
        for e in entities["entities"]:
            if e.team == self.team:
                # Check if
                # if "Taunt" in self.free_var:
                if "Giga ton Punch" in self.free_var:
                    if Fun.check_point_in_rotated_rectangle([corner_1, corner_2, corner_3, corner_4], e.pos):
                        e.vel = Fun.move_with_vel_angle([0, 0], knockback, self.angle)
                        for x in range(12):
                            num = x % 2
                            entities["particles"].append(Particles.RandomParticle2(
                                e.pos.copy(), Fun.YELLOW, 4 * [1, 1.75][num], 15,
                                self.angle + [-90, 90][num] + random.uniform(-15, 15), size=4 * [1, 2][num]))
                continue
            #
            if Fun.distance_between(e.pos, self.pos) < 160:
                e.target = self
            if Fun.check_point_in_rotated_rectangle([corner_1, corner_2, corner_3, corner_4], e.pos):
                entities["background particles"].append(Particles.GrowingCircle(e.pos, Fun.DARK_RED, 4, 16, 1, 2))
                Fun.damage_calculation(e, damage, "Melee", death_message="Punched by Lord")
                e.vel = Fun.move_with_vel_angle([0, 0], knockback, self.angle)
                if "IS BOSS" in e.free_var:
                    e.status["Stunned"] += 90
                    if "Startup lag" in e.free_var:
                        e.free_var["Startup lag"] = 0
                for x in range(12):
                    num = x % 2
                    entities["particles"].append(Particles.RandomParticle2(
                        e.pos.copy(), Fun.DARK_RED, 4 * [1, 1.75][num], 15,
                        self.angle + [-90, 90][num] + random.uniform(-15, 15), size=4 * [1, 2][num]))
                if self.weapon.name == "Big Iron":
                    self.weapon.ammo += 1
                    if self.weapon.ammo > self.weapon.max_ammo:
                        self.weapon.ammo = self.weapon.max_ammo
        Fun.play_sound("Hitting 3")
        entities["particles"].append(Particles.AfterImageRotated(
            Fun.move_with_vel_angle(self.pos, 64, self.angle), Fun.SPRITE_LORD_GAUNTLET, 30, self.angle))

        return

    if self.time % 5 == 0:
        Fun.play_sound("Charge")

    entities["particles"].append(Particles.AfterImageRotated(
        Fun.move_with_vel_angle(self.pos, 16 * mod * -1, self.angle),
        Fun.SPRITE_LORD_GAUNTLET, 1, self.angle))
    #sd


def leopold_beast_mode(self, skill, entities, level):
    if self.weapon.ammo == 0:
        if self.weapon.ammo_pool > 0:
            self.weapon.ammo += 1
            self.weapon.ammo_pool -= 1
    self.agro += 1
    mod = 1
    if 'Super Duper Ultimate Death Defying Plus Ultra Supreme Heavenly Beast Mode DELUXE' in self.free_var:
        # Lord gets max agro
        self.agro = 100
        # Can't use weapons for 5 sec after the effect ends
        if skill.last_active_frame:
            self.no_shoot_state = 300
        mod = 2

    self.did_agro_raise = 60 * 3
    # Particle effect should be always moving toward the user
    if skill.first_active_frame:
        Fun.play_sound("Beast Mode")
        entities["particles"].append(Particles.GrowingCircle(self.pos, Fun.WHITE, 4, 16, 0, 16))
        entities["background particles"].append(Particles.BeastModeParticle(self.pos, 5*60* mod, Fun.ORANGE))


# |Emperor|-------------------------------------------------------------------------------------------------------------
def kai_kick(self, skill, entities, level):
    amount = 90
    if "IS VERSUS" in self.free_var:
        amount = 45
    point = Fun.move_with_vel_angle(self.pos, -16, self.angle)
    for e in entities["entities"]:
        if e.team == self.team:
            continue
        if Fun.check_point_in_cone(128, point[0], point[1], e.pos[0], e.pos[1], self.angle, 45):
            e.status["Stunned"] += amount
            self.free_var["Kicked"] += 1
            if "Startup lag" in e.free_var:
                e.free_var["Startup lag"] = 0
            if "Kick to the Balls" in self.free_var:
                e.status["Low res"] += 5 * 60
            if "Kick and Run" in self.free_var:
                self.status["Double speed"] = 1 * 60

    # self.free_var["Kicked"]
    if "Skilled" in self.free_var:
        if "Duke" in self.free_var:
            for b in entities["bullets"]:
                if b.laser_based:
                    continue
                if Fun.check_point_in_cone(96, self.pos[0], self.pos[1], b.pos[0], b.pos[1], self.angle, 30):
                    b.team = self.team
                    b.angle = self.angle
                    b.owner = self
                    b.speed *= 1.5
                    b.radius *= 1.75
                    b.duration = b.og_info[1]
            # Nearby bullets get parried

    # Visual effects
    for y in range(3):
        for x in range(7):
            angle = self.aim_angle - 5 * 3 + 5 * x + random.uniform(-30, 30)
            num = int(random.random() > 0.7)
            entities["particles"].append(Particles.RandomParticle2(
                Fun.move_with_vel_angle(self.pos, 6, angle),
                [Fun.WHITE, Fun.YELLOW][num], 4 * [1, 1.75][num], 15, angle, size=4 * [1, 2][num]))

    Fun.play_sound("Hitting 1", "SFX")


def kai_mega_buff(self, skill, entities, level):
    duration = 600
    if "Omega Buff" in self.free_var:
        duration = 1000

    lord, duke = None, None
    for e in entities["entities"]:
        if e.team == self.team:
            if e.name == "Lord":
                lord = e
                continue
            if e.name == "Duke":
                duke = e
                continue
    if lord is not None and duke is not None:
        lord.status["Dash recovery up"] += duration
        duke.status["Fuller auto"] += duration
        for p in [lord, duke]:
            Particles.random_particle_2_circle(entities, p.pos, 2, 20, 18, colour=Fun.WHITE,
                                         angle_mod=180 * random.random())
            Particles.random_particle_2_circle(entities, p.pos, 1, 45, 16, colour=Fun.WHITE, size=5,
                                         angle_mod=180 * random.random())

    if "Skilled" in self.free_var:
        if "Wizard" in self.free_var:
            # Reloads current weapon
            self.weapon.ammo = self.weapon.max_ammo
            self.weapon.ammo_pool += self.weapon.max_ammo*2
            if self.weapon.ammo_pool > self.weapon.max_ammo_pool:
                self.weapon.ammo_pool = self.weapon.max_ammo_pool

            for x in range(5):
                pos = Fun.random_point_in_circle(self.pos, 16)
                entities["particles"].append(
                    Particles.RandomParticle1(pos, Fun.RED, -2, round(10 + 10 * random.random()),
                                        size=(2, 4))
                )
        if "Sovereign" in self.free_var:
            # Nearby enemies receive the Visible effect
            for e in entities["entities"]:
                if e.team == self.team:
                    continue
                if Fun.distance_between(self.pos, e.pos) < self.targeting_range:
                    self.status["Visible"] += duration // 2

                    entities["particles"].append(Particles.GrowingCircleEntityBound(e, Fun.DARK_GREEN, "Visible", 2))
        if "Jester" in self.free_var:
            # Gives some armour to either Emperor or Allies
            targets = []
            for e in entities["entities"]:
                if e.team != self.team:
                    break
                if e == self:
                    continue
                if Fun.distance_between(e.pos, self.pos) < 96:
                    targets.append(e)
            if targets:
                num = len(targets) -1
                for t in targets:
                    t.armour += [60, 90, 120][num]
                    if t.armour > t.max_armour:
                        t.armour = t.max_armour
                    for x in range(5):
                        pos = Fun.random_point_in_circle(t.pos, 16)
                        entities["particles"].append(
                            Particles.RandomParticle1(pos, Fun.GREEN, -2, round(10 + 10 * random.random()), size=(2, 4))
                        )
            else:
                self.armour += 120
                if self.armour > self.max_armour:
                    self.armour = self.max_armour

                for x in range(5):
                    pos = Fun.random_point_in_circle(self.pos, 16)
                    entities["particles"].append(
                        Particles.RandomParticle1(pos, Fun.GREEN, -2, round(10 + 10 * random.random()), size=(2, 4))
                    )

    if "Alpha Buff" in self.free_var:
        # Set HP to one
        self.health = 1
        self.max_health = 1
        self.resistances = {"Physical": 0.2,  "Fire": 0.2, "Explosion": 0.2, "Energy": 0.2, "Melee": 0.2, "Healing": -1}

        # Can detect anything near him
        self.targeting_angle = 360
        self.stealth_counter = 10
        self.thiccness = 8

        # Faster and better dashes
        self.vel_max = 5.75
        self.dash_speed = 17
        self.dash_iframes = 24
        self.dash_charge_time = 30

        center = self.pos
        Particles.random_particle_2_circle(entities, self.pos, 4, 45, 36, colour=Fun.WHITE, angle_mod=180 * random.random())
        Particles.random_particle_2_circle(entities, self.pos, 2, 90, 36, colour=Fun.LIGHT_BLUE, size=5,
                                     angle_mod=180 * random.random())
        for x in range(4):
            for particles_to_add in range(10):
                entities["background particles"].append(
                    Particles.RandomParticle2([center[0], center[1]], Fun.RED, 1 + particles_to_add * 0.66, 90,
                                        particles_to_add * 10 + 90 * x))

        return
    self.status["Dash recovery up"] += duration
    self.status["Fuller auto"] += duration
    Particles.random_particle_2_circle(entities, self.pos, 4, 45, 36, colour=Fun.WHITE, angle_mod=180 * random.random())
    Particles.random_particle_2_circle(entities, self.pos, 2, 90, 36, colour=Fun.LIGHT_BLUE, size=5, angle_mod=180 * random.random())
    Fun.play_sound("Sword launch")


# |Wizard|--------------------------------------------------------------------------------------------------------------
def jeanne_building(self, skill, entities, level):
    place = self.input["Interact"]
    self.no_shoot_state += 1

    pos = [
        [Fun.move_with_vel_angle(self.pos, 48, self.angle)],        # Turret
        [Fun.move_with_vel_angle(self.pos, 48.5, self.angle - 35),  # Cover
         Fun.move_with_vel_angle(self.pos, 48.5, self.angle),
         Fun.move_with_vel_angle(self.pos, 48.5, self.angle + 35)],
        [Fun.move_with_vel_angle(self.pos, 48, self.angle)]         # Demolition Charge
    ][skill.free_var["Chosen building"]]

    building = ["Jeanne Turret", "Jeanne Cover", "Jeanne Demolition Charge"][skill.free_var["Chosen building"]]

    if skill.free_var["Switch cooldown"] > 0:
        skill.free_var["Switch cooldown"] -= 1
    elif self.input["Shoot"] and skill.free_var["Switch cooldown"] == 0:
        skill.free_var["Chosen building"] = (skill.free_var["Chosen building"] + 1) % 3
        skill.free_var["Switch cooldown"] = 30
    # Place the building
    if place:
        for p in pos:
            Items.spawn_item(entities, building, p, self=self)
            if "Health" in entities["items"][-1].free_var:

                if "Wrench Wench" in self.free_var:
                    entities["items"][-1].free_var.update({"Wrench Wench": True})
                if "Special Coating" in self.free_var:
                    entities["items"][-1].free_var.update({"Special Coating": True})
                if "Sturdy Building" in self.free_var:
                    for x in range(5):
                        pos = Fun.random_point_in_circle(p, 16)
                        entities["particles"].append(
                            Particles.RandomParticle1(pos, Fun.GREEN, -2, round(10 + 10 * random.random()),
                                                size=(2, 4))
                        )
                    entities["items"][-1].free_var["Health"] *= 2
        if building == "Jeanne Turret":
            entities["items"][-1].free_var["Angle"] = self.angle
            if "Overclocked" in self.free_var:
                for x in range(5):
                    pos = Fun.random_point_in_circle(p, 16)
                    entities["particles"].append(
                        Particles.RandomParticle1(pos, Fun.RED, -2, round(10 + 10 * random.random()),
                                            size=(2, 4))
                    )
                entities["items"][-1].free_var["Fire rate"] = 10
        if "Self Destruct" in self.free_var:
            entities["items"][-1].free_var.update({"Self Destruct": True})
        if "Busting Blue Balls" in self.free_var:
            entities["items"][-1].free_var.update({"Busting Blue Balls": True})

        skill.recharge = 0
        skill.active = False
        if "Field Repair" in self.free_var:
            for e in entities["entities"]:
                if e.team != self.team:
                    break
                if e.name != "Jester":
                    continue
                if Fun.distance_between(self.pos, e.pos) < 64:
                    e.armour += round(e.max_armour * 0.25)
                    if e.armour > e.max_armour:
                        e.armour = e.max_armour
                    for x in range(5):
                        pos = Fun.random_point_in_circle(e.pos, 16)
                        entities["particles"].append(
                            Particles.RandomParticle1(pos, Fun.GREEN, -2, round(10 + 10 * random.random()),
                                                size=(2, 4))
                        )
                    break
        Fun.play_sound("Jeanne Building")
        return

    # Build Preview
    img = Fun.get_image(f'Sprites/Items/{building}.png')
    img.set_alpha(196)
    if building == "Jeanne Turret":
        img_1 = img.subsurface((96, 00, 16, 16))
        img_2 = img.subsurface((00, 00, 16, 16))
        for p in pos:
            entities["particles"].append(Particles.AfterImage(p, img_1, 1))
            entities["particles"].append(Particles.AfterImage([p[0], p[1]-4], img_2, 1))
        return

    for p in pos:
        entities["particles"].append(Particles.AfterImage(p, img, 1))


def jeanne_guns_blazing(self, skill, entities, level):
    # Increases fire rate and give 75% of magazine back (rounded up). Makes Lord invincible for 5 sec.
    for e in entities["entities"]:
        if e.team != self.team:
            break
            # continue
        magazine_ammo_back = round(e.weapon.max_ammo * 0.75)
        over_magazine = e.weapon.ammo + magazine_ammo_back > e.weapon.max_ammo
        if over_magazine:
            diff = e.weapon.ammo + magazine_ammo_back - e.weapon.max_ammo

            if "Resupply" in self.free_var:
                e.weapon.ammo_pool += diff
            magazine_ammo_back -= diff

        e.weapon.ammo += magazine_ammo_back
        e.status["Fuller auto"] += 5 * 60

        Particles.random_particle_2_circle(entities, e.pos, 4, 15, 36, colour=Fun.RED, angle_mod=180 * random.random())
        Particles.random_particle_2_circle(entities, self.pos, 4, 15, 36, colour=Fun.RED, angle_mod=180 * random.random())
        if e.name == "Lord":
            Particles.random_particle_2_circle(entities, e.pos, 2, 60, 36, colour=Fun.YELLOW, size=5,
                                         angle_mod=180 * random.random())
            e.weapon.ammo_pool += 100
            e.status["No damage"] += 5 * 60
    if "Resupply" in self.free_var:
        for i in entities["items"]:
            if i.name == "Jeanne Turret":
                Particles.random_particle_2_circle(entities, i.pos, 4, 15, 36, colour=Fun.RED,
                                             angle_mod=180 * random.random())
                self.free_var["Ammo"] = 25
    Fun.play_sound("Jeanne Buff")


# |Sovereign|-----------------------------------------------------------------------------------------------------------
def corrine_cardboard_box(self, skill, entities, level):
    # Puts Corrine in a state where she can't move but her stealth mod is increased.
    if skill.first_active_frame:
        skill.free_var["Draw angle"] = self.aim_angle
        self.func_draw = Entity.cardboard_box_draw
    #   Stun Kick can move her around.
    self.shot_allowed = False
    if self.dash_cooldown <= 0:
        self.dash_cooldown = 2
    self.vel = [0, 0]
    if self.status["Stealth"] <= 1:
        self.status["Stealth"] = 2
    if "Safety Corner" in self.free_var:
        if self.status["No damage"] <= 1:
            self.status["No damage"] = 2

    if skill.last_active_frame:
        self.func_draw = Entity.player_draw
        if self.team != "Players":
            self.func_draw = Entity.enemy_draw_basic


def corrine_detect_targets(self, skill, entities, level):
    # Counters stealth. Lets Corrine find targets behind walls
    # Highlights targets for a short time
    duration = self.free_var["Detect Targets Duration"]
    for e in entities["entities"]:
        if e.team == self.team:
            continue
        if Fun.check_point_in_circle(self.targeting_range, self.pos[0], self.pos[1], e.pos[0], e.pos[1]):
            entities["particles"].append(Particles.GrowingCircleEntityBound(e, Fun.DARK_GREEN, "Visible", 2))
            e.status["Visible"] += duration

    entities["background particles"].append(Particles.GrowingCircle(self.pos, Fun.DARK_GREEN, 4, 64, 1, 4))
    Fun.play_sound("Corrine Ping")


# |Duke|----------------------------------------------------------------------------------------------------------------
def zander_tail_swipe(self, skill, entities, level):
    # Parry bullets around him
    for b in entities["bullets"]:
        if b.laser_based or b.owner == self:
            continue
        if Fun.check_point_in_circle(64, self.pos[0], self.pos[1], b.pos[0], b.pos[1]):
            if "Tail & Blue Balls" in self.free_var:
                Bullets.spawn_blue_balls(
                    self, entities,
                    b.pos.copy(),
                    self.angle,
                    [b.og_info[0] * 1.5, b.og_info[1], b.radius, b.damage, {"Colour": Fun.DARK_BLUE}])
                b.duration = 0
                continue
            b.team = self.team
            b.angle = self.angle
            b.owner = self
            b.speed *= 1.5
            b.duration = b.og_info[1]

    # Visual effects
    Items.spawn_item(entities, "Zan'dr speen", [0, 0], self=self)
    Fun.play_sound("Hitting 1", "SFX")


def zander_smoke_screen(self, skill, entities, level):
    self.status["Stealth"] += 60 * 2.5
    # Creates a smoke grenade in front
    for x in range(32):
        pos = Fun.random_point_in_cone(self.pos, 64, self.angle, 60)
        entities["particles"].append(Particles.Smoke(
            pos,
            # duration=(self.free_var["Duration"] // 4, self.free_var["Duration"] // 3)
        ))
    # Stun enemies in the aoe of the grenade
    for e in entities["entities"]:
        if e.team == self.team:
            continue
        if e.target == self:
            e.target = False
        if Fun.check_point_in_cone(64 * 1.5, self.pos[0], self.pos[1], e.pos[0], e.pos[1], self.angle, 60):
            e.status["Stunned"] += 60
            e.status["Visible"] += 60

    # Lowers agro to a -10
    if self.agro > -10:
        self.agro = -10
    Fun.play_sound("Zander Smoke")


# |Jester|--------------------------------------------------------------------------------------------------------------
def m3d1c_discharge(self, skill, entities, level):
    # Stuns everybody around user and the user
    dist = 128
    amount = 120
    if "IS VERSUS" in self.free_var:
        amount = 80
    for e in entities["entities"]:
        if Fun.distance_between(self.pos, e.pos) < dist:
            if "Power Boost" in self.free_var and e.team == self.team:
                sk_1 = e.skills[0]
                sk_2 = e.skills[1]
                sk_1.recharge += sk_1.recharge_rate * 3
                if sk_1.recharge > sk_1.recharge_max:
                    sk_1.recharge = sk_1.recharge_max
                sk_2.recharge += sk_2.recharge_rate * 3
                if sk_2.recharge > sk_2.recharge_max:
                    sk_2.recharge = sk_2.recharge_max
            else:
                e.status["Stunned"] += amount
            if "Startup lag" in e.free_var:
                e.free_var["Startup lag"] = 0
    if "Surge Protection" in self.free_var:
        self.status["Stunned"] = 0

    # Remove IFF from missiles
    target = "None"
    if "Electronic Swearfare" in self.free_var:
        target = self.team
    for b in entities["bullets"]:
        if b.team == self.team:
            continue
        if type(b) != Bullets.Missile: continue
        if Fun.distance_between(self.pos, b.pos) < dist:
            b.team = target
            b.owner = self
    Fun.play_sound("Electricity 1")
    number_of_particle = 18
    for particles_to_add in range(360 // number_of_particle):
        entities["particles"].append(Particles.RandomParticle2(
            [self.pos[0], self.pos[1]], Particles.YELLOW, 1 + 3 * random.random(), random.randint(45, 90),
            particles_to_add * number_of_particle, size=Fun.get_random_element_from_list([3, 4 ,6])))
    duration = 9
    entities["particles"].append(Particles.GrowingCircleTransparent(
        self.pos, Fun.WHITE, dist/duration, duration, 0, 4, alpha=62))


def m3d1c_robot_fuck_off(self, skill, entities, level):
    dist = 128
    damage = 10
    if "S41-Lor Firmware" in self.free_var:
        dist = 160 + 16
    if "Profanity Update" in self.free_var:
        damage = 20
        for b in entities["bullets"]:
            if b.team == self.team:
                continue
            if Fun.collision_circle_circle(self.pos, dist, b.pos, b.radius):
                b.duration = 0

    for e in entities["entities"]:
        if e.team == self.team:
            continue
        e_dist = Fun.distance_between(self.pos, e.pos)
        if e_dist < dist:
            Fun.damage_calculation(e, damage, "Melee", death_message="Insulted to death")
            e.vel = Fun.move_with_vel_angle([0,0], (dist-e_dist)*0.4, Fun.angle_between(e.pos, self.pos))
    Fun.play_sound("Electricity 2")

    duration = 9
    entities["particles"].append(Particles.GrowingCircleTransparent(
        self.pos, Fun.WHITE, dist/duration, duration, 0, 4, alpha=62))


# |Condor|--------------------------------------------------------------------------------------------------------------
def vincent_armour_breaker(self, skill, entities, level):
    point = Fun.move_with_vel_angle(self.pos, -16, self.angle)
    amount = 60
    if "IS VERSUS" in self.free_var:
        amount = 30
    for e in entities["entities"]:
        if e.team == self.team:
            continue
        if not Fun.check_point_in_cone(128, point[0], point[1], e.pos[0], e.pos[1], self.angle, 45):
            continue
        # Alternate effect for those with no armour
        if e.armour <= 0:
            continue
        e.armour -= e.max_armour // 3
        if e.armour < 0:
            stun_time = abs(e.armour) * amount
            if stun_time > 240:
                stun_time = 240
            e.status["Stunned"] += stun_time
            if "Startup lag" in e.free_var:
                e.free_var["Startup lag"] = 0
            e.armour = 0

        # Visual
        number_of_particle = 9
        for particles_to_add in range(360 // number_of_particle):
            entities["background particles"].append(Particles.RandomParticle2(
                [e.pos[0], e.pos[1]], Fun.GREEN, 2 * random.random(), random.randint(15, 45),
                                                       particles_to_add * number_of_particle,
                size=Fun.get_random_element_from_list([3, 4, 6])))

    # Visual effects
    for y in range(3):
        for x in range(7):
            angle = self.aim_angle - 5 * 3 + 5 * x + random.uniform(-30, 30)
            num = int(random.random() > 0.7)
            entities["particles"].append(Particles.RandomParticle2(
                Fun.move_with_vel_angle(self.pos, 6, angle),
                [Fun.LIGHT_GREEN, Fun.DARK_GREEN][num], 4 * [1, 1.75][num], 15, angle, size=4 * [1, 2][num]))

    Fun.play_sound("Vincent Armour Break")


def vincent_last_stand(self, skill, entities, level):
    # This just add the condition for last stand to take effect and add visuals
    self.status["Last Stand"] = 60 * 5

    number_of_particle = 18
    for particles_to_add in range(360 // number_of_particle):
        angle = particles_to_add * number_of_particle
        speed = 1 + 3 * random.random()
        time = random.randint(45, 90)
        dist = speed * time
        entities["particles"].append(Particles.RandomParticle2(
            Fun.move_with_vel_angle(self.pos, dist, angle), Fun.DARK_RED, speed, time, angle - 180,
            size=Fun.get_random_element_from_list([3, 4 ,6])))
    Fun.play_sound("Skill 3")


# |Fortress APC|--------------------------------------------------------------------------------------------------------
def fortress_mortar(self, skill, entities, level):
    angle = self.free_var["Move angle"] + 226 - 180
    for p in range(16):
        entities["particles"].append(Particles.Smoke(
            Fun.move_with_vel_angle(Fun.move_with_vel_angle(self.pos, 22.6274, angle), p * 7 * random.random()+ 32, self.angle + random.uniform(-8, 8))))

    Bullets.spawn_bullet(
            self, entities, Bullets.Artillery, self.mouse_pos, self.angle,
            [2, 60, 64,
             50, {"Secondary explosion":{"Duration": 20, "Strength": 120, "Radius":64}, "Colour": Fun.DARK_BLUE, "Slowdown rate": 0.05}])

    entities["sounds"].append(Fun.Sound(
        Fun.move_with_vel_angle(self.pos, 20, self.aim_angle), 60, 175, source=self.team, strength=2))
    Fun.play_sound("Vulture Armour")


def fortress_repair(self, skill, entities, level):
    if self.damage_taken:
        skill.recharge = 0
        return

    if skill.first_active_frame or skill.recharge % 60 == 0:
        self.armour += 10

    if self.armour > self.max_armour:
        self.armour = self.max_armour


# |Zoar Colonists|------------------------------------------------------------------------------------------------------
# |Curtis|--------------------------------------------------------------------------------------------------------------
def curtis_kick(self, skill, entities, level):
    extra_effects = False
    for b in entities["bullets"]:
        if b.team == self.team:
            continue
        if b.laser_based:
            continue
        if Fun.check_point_in_cone(96, self.pos[0], self.pos[1], b.pos[0], b.pos[1], self.angle, 30):
            extra_effects = True
            Bullets.spawn_blue_balls(
                self, entities,
                b.pos.copy(),
                self.angle,
                [b.og_info[0] * 1.5, b.og_info[1], b.radius * 1.75, b.damage, {"Colour": Fun.DARK_BLUE}])
    if "III, L'Impératrice" in self.free_var:
        for e in entities["entities"]:
            if e.team == self.team:
                continue
            if Fun.check_point_in_cone(128, self.pos[0], self.pos[1], e.pos[0], e.pos[1], self.angle, 30):
                extra_effects = True
                e.status["Low friction"] += 30
                e.vel = Fun.move_with_vel_angle(self.vel, 4, self.angle)

                for x in range(5):
                    pos = Fun.random_point_in_circle(e.pos, 16)
                    entities["particles"].append(
                        Particles.RandomParticle1(pos, Fun.LIGHT_BLUE, 2, round(10 + 10 * random.random()), size=(4, 2))
                    )

    if extra_effects:
        if "X, La Roue de Fortune" in self.free_var:
            self.status[Fun.get_random_element_from_list(Fun.BUFFS_NAMES)] += 180
    # Visual effects
    for y in range(3):
        for x in range(7):
            angle = self.aim_angle - 5 * 3 + 5 * x + random.uniform(-30, 30)
            entities["particles"].append(Particles.RandomParticle2(
                Fun.move_with_vel_angle(self.pos, 6, angle),
                Fun.WHITE, 4, 15, angle, size=3))

    Fun.play_sound("Hitting 1", "SFX")


def curtis_kick_boss(self, skill, entities, level):
    for b in entities["bullets"]:
        if b.team == self.team:
            continue
        if b.laser_based:
            continue
        if Fun.check_point_in_cone(96, self.pos[0], self.pos[1], b.pos[0], b.pos[1], self.angle, 30):
            Bullets.spawn_blue_balls(
                self, entities,
                b.pos.copy(),
                self.angle,
                [b.og_info[0], b.og_info[1], b.radius * 1.75, b.damage, {"Colour": Fun.DARK_BLUE}])

    # Visual effects
    for y in range(3):
        for x in range(7):
            angle = self.aim_angle - 5 * 3 + 5 * x + random.uniform(-30, 30)
            entities["particles"].append(Particles.RandomParticle2(
                Fun.move_with_vel_angle(self.pos, 6, angle),
                Fun.DARK_GRAY, 4, 15, angle, size=3))

    Fun.play_sound("Hitting 1", "SFX")


def curtis_fool(self, skill, entities, level):
    sound_allowed = False
    for b in entities["bullets"]:
        if b.owner != self:
            continue
        if "Redirect" not in b.free_var:
            b.speed = 0
            b.duration = 1200
            sound_allowed = True
            for particles_to_add in range(360 // 36):
                entities["particles"].append(Particles.RandomParticle2(
                    [b.pos[0] - 30 * math.cos(particles_to_add * 36 * math.pi / 180),
                     b.pos[1] - 30 * math.sin(particles_to_add * 36 * math.pi / 180)],
                    Fun.LIGHT_BLUE, -2, 15, particles_to_add * 36, size=3))
            b.free_var.update({"Redirect": True})
            if "VIII, La Justice" in self.free_var:
                Items.spawn_item(entities, "Justice", b.pos, self.owner)
                entities["items"][-1].free_var["Bullet"] = b
            continue
        # Redirect
        b.duration = round(b.og_info[1] * 2)
        b.angle = Fun.angle_between(self.mouse_pos, b.pos)
        for x in range(3):
            entities["particles"].append(Particles.RandomParticle2(
                [b.pos[0], b.pos[1]],
                Fun.AMBER, b.speed // 2, 14,
                                   b.angle + 180 + random.uniform(-4, 4)))
        b.speed = 8
        sound_allowed = True
    if sound_allowed:
        Fun.play_sound("Bullet bending", "SFX")
        return
    skill.recharge = skill.recharge_max


# |Lawrence|------------------------------------------------------------------------------------------------------------
def lawrence_flame_canyon(self, skill, entities, level):
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

    for x in range(14):
        Bullets.spawn_bullet(
            self, entities,
            Bullets.Napalm,
            Fun.move_with_vel_angle(self.pos, 20, self.angle),
            self.angle + random.uniform(-2, 2),
            [random.uniform(4, 16), 180, random.uniform(4, 7),
             20 * mod * fire_mod, {"Particle allowed": True,
                  "Burn chance": 0.8,
                  "Burn duration": 30 * duration_mod,
                  "Colour": self.weapon.free_var["Colour"], "On hit": on_hit_list
                  }])
    Fun.play_sound("Son slash", "SFX")


def lawrence_flame_burst(self, skill, entities, level):
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

    for x in range(14 * 5):
        Bullets.spawn_bullet(
            self, entities,
            Bullets.Napalm,
            Fun.move_with_vel_angle(self.pos, 20, self.angle),
            360 * random.random(),
            [random.uniform(2, 6), 180, random.uniform(4, 7),
             20 * mod * fire_mod, {"Particle allowed": True,
                  "Burn chance": 0.8,
                  "Burn duration": 30 * duration_mod,
                  "Colour": self.weapon.free_var["Colour"], "On hit": on_hit_list
                  }])
    Fun.play_sound("Son slash", "SFX")


# |Mark|----------------------------------------------------------------------------------------------------------------
def mark_target_locator(self, skill, entities, level):
    for e in entities["entities"]:
        if e.team == self.team:
            continue
        if Fun.check_point_in_cone(self.targeting_range, self.pos[0], self.pos[1], e.pos[0], e.pos[1], self.angle, self.targeting_angle):
            entities["particles"].append(Particles.GrowingCircle(e.pos, Fun.DARK_GREEN, 0, 1, 18, 2))
            if "Helping mark" in self.free_var:
                if "Mark's helping mark" not in e.free_var:
                    Items.spawn_item(entities, "Mark", e.pos, self.owner)
                    e.free_var.update({"Mark's helping mark": True})
                    entities["items"][-1].free_var["Victim"] = e
                    entities["items"][-1].free_var["Colour"] = Fun.GREEN
                    entities["items"][-1].thiccness = e.thiccness * 1.2
                    entities["items"][-1].free_var["Payload"] = Items.payload_helping


def mark_smoke_grenade(self, skill, entities, level):
    Items.spawn_item(entities, "Smoke Grenade", self.pos.copy(), self=self)
    # Lower agro
    self.agro -= 75
    # Force reset
    for e in entities["entities"]:
        if e.target == self:
            e.target = []
        if "Disable weapon mark" in self.free_var:
            if random.random() < 0.33:
                Items.spawn_item(entities, "Mark", e.pos, self.owner)
                entities["items"][-1].free_var["Victim"] = e
                entities["items"][-1].free_var["Colour"] = Fun.DARK_GREEN_ALT
                entities["items"][-1].thiccness = e.thiccness * 1.2
                entities["items"][-1].free_var["Payload"] = Items.payload_disable


# |Vivianne|------------------------------------------------------------------------------------------------------------
def vivianne_rat_shot(self, skill, entities, level):
    for e in entities["entities"]:
        if e.team != self.team:
            continue
        e.status["Bullet x3"] += 320
        e.status["Low Aim"] += 320
        e.status["No Recoil"] += 320
    self.skills[1].recharge = 0


def vivianne_reaper_rounds(self, skill, entities, level):
    for e in entities["entities"]:
        if e.team != self.team:
            continue
        e.status["Bullet speed up"] += 320
        e.status["Bullet duration down"] += 320
        e.status["Perfect Aim"] += 320
    self.skills[0].recharge = 0


# |Sand Buggy|----------------------------------------------------------------------------------------------------------
def sand_buggy_drift(self, skill, entities, level):
    self.status["Low friction"] = 2
    mod = 0.7

    smoke_colour_pool = [Fun.WHITE, Fun.GRAY, Fun.LIGHT_GRAY]
    if level["mission number"] > 5:
        smoke_colour_pool = [Fun.ORANGE, Fun.ORANGE, Fun.LIGHT_GRAY]
    if level["mission number"] > 10:
        smoke_colour_pool = [Fun.WHITE, Fun.GRAY, Fun.LIGHT_GRAY]
    entities["background particles"].append(Particles.Smoke(Fun.random_point_in_circle(
        Fun.move_with_vel_angle(self.pos, 12, self.free_var["Move angle"] -180), 16),
        colour=smoke_colour_pool[random.randint(0, 2)]
                                           ))


def sand_buggy_burst_rocket(self, skill, entities, level):
    for a in [-15, 0, 15]:
        for b in range(7):
            if b in [0, 1]: continue
            # Hot.

            Bullets.spawn_bullet(
                self, entities, Bullets.ExplosionPrimaryType1,
                Fun.move_with_vel_angle(self.pos, 32, self.free_var["Move angle"]+a),
                self.free_var["Move angle"] + random.uniform(-4, 4)+a,
                [5 * b, 10, 4, 50, {"Secondary explosion": {"Duration": 8,
                                                            "Growth": 6,
                                                            "Damage mod": 1}}])
    Fun.play_sound("Hitting 3", "SFX")


# |Skill repertory|-----------------------------------------------------------------------------------------------------
# Offense   : Purely damaging skills
# Support   : Give you bonuses and don't affect the others much
# Movement  : Manipulate movement
# Tactical  : Does a lot of stuff, often not related to making damage
skill_repertory = {
    # |THR-1|-----------------------------------------------------------------------------------------------------------
    # Lord
    "Gauntlet Punch":
        {"name": "Gauntlet Punch",
         "class": "Offense",
         "description": "",
         "func": "leopold_gauntlet_punch",
         "activation mode": "switch no cancel",
         "depletion rate": 5,
         "recharge max": 5 * 60,
         "free variables": {}
         },
    "Beast Mode":
        {"name": "Beast Mode",
         "class": "Offense",
         "description": "",
         "func": "leopold_beast_mode",
         "activation mode": "switch no cancel",
         "depletion rate": 4,
         "recharge max": 20 * 60,
         "free variables": {}
         },
    # Emperor
    "Stun Kick":
        {"name": "Stun Kick",
         "class": "Offense",
         "description": "",
         "func": "kai_kick",
         "activation mode": "normal",
         "recharge max": 1.75 * 60,
         "free variables": {}
         },
    "Mega Buff":
        {"name": "Mega Buff",
         "class": "Offense",
         "description": "",
         "func": "kai_mega_buff",
         "activation mode": "normal",
         "recharge max": 15 * 60,
         "free variables": {}
         },
    # Wizard
    "Building":
        {"name": "Building",
         "class": "Offense",
         "description": "",
         "func": "jeanne_building",
         "activation mode": "hold",
         "recharge rate": 0.25,
         "depletion rate": 0,
         "free variables": {
             "Chosen building": 0,
             "Switch cooldown": 0
         }
         },
    "All Guns Blazing":
        {"name": "All Guns Blazing",
         "class": "Offense",
         "description": "",
         "func": "jeanne_guns_blazing",
         "activation mode": "normal",
         "recharge max": 15 * 60,
         "free variables": {}
         },
    # Sovereign
    "Cardboard box":
        {"name": "Cardboard box",
         "class": "Offense",
         "description": "",
         "func": "corrine_cardboard_box",
         "activation mode": "switch",
         "recharge rate": 5,
         "depletion rate": 1,
         "recharge max": 5 * 60,
         "free variables": {"Draw angle": 0}
         },
    "Detect Targets":
        {"name": "Detect Targets",
         "class": "Offense",
         "description": "",
         "func": "corrine_detect_targets",
         "activation mode": "normal",
         "recharge max": 7 * 60,
         "free variables": {}
         },
    # Duke
    "Tail Swipe":
        {"name": "Tail Swipe",
         "class": "Offense",
         "description": "",
         "func": "zander_tail_swipe",
         "activation mode": "normal",
         "recharge max": 2.5 * 60,
         "free variables": {}
         },
    "Smoke Screen":
        {"name": "Smoke Screen",
         "class": "Offensive",
         "description": "",
         "func": "zander_smoke_screen",
         "activation mode": "normal",
         "recharge max": 8 * 60,
         "free variables": {}
         },

    # Jester
    "Discharge":
        {"name": "Discharge",
         "class": "Offense",
         "description": "",
         "func": "m3d1c_discharge",
         "activation mode": "normal",
         "recharge max": 5 * 60,
         "free variables": {}
         },
    "Robot Fuck Off":
        {"name": "Discharge",
         "class": "Offensive",
         "description": "",
         "func": "m3d1c_robot_fuck_off",
         "activation mode": "normal",
         "recharge max": 12 * 60,
         "free variables": {}
         },
    # Condor
    "Armour Breaker":
        {"name": "Armour Breaker",
         "class": "Offense",
         "description": "",
         "func": "vincent_armour_breaker",
         "activation mode": "normal",
         "recharge max": 4 * 60,
         "free variables": {}
         },

    "Last Stand":
        {"name": "Last Stand",
         "class": "Offense",
         "description": "",
         "func": "vincent_last_stand",
         "activation mode": "normal",
         "recharge max": 30 * 60,
         "free variables": {}
         },
    # Fortress
    "Mortar":
        {"name": "Mortar",
         "class": "Offense",
         "description": "",
         "func": "fortress_mortar",
         "activation mode": "normal",
         "recharge max": 4 * 60,
         "free variables": {}
         },
    "Repairs":
        {"name": "Repairs",
         "class": "Offense",
         "description": "",
         "func": "fortress_repair",
         "activation mode": "switch no cancel",
         "depletion rate": 1,
         "recharge max": 20 * 60,
         "free variables": {}
         },
    # |Zoar Colonists|--------------------------------------------------------------------------------------------------
    # Curtis
    "Kick":
        {"name": "Kick",
         "class": "Offense",
         "description": "",
         "func": "curtis_kick",
         "activation mode": "normal",
         "recharge rate": 2,
         "depletion rate": 0,
         "free variables": {}
         },
    "Kick Boss":
        {"name": "Kick Boss",
         "class": "Offense",
         "description": "",
         "func": "curtis_kick_boss",
         "activation mode": "normal",
         "recharge rate": 1.2,
         "depletion rate": 0,
         "free variables": {}
         },
    "Le Mat":
        {"name": "Le Mat",
         "class": "Offense",
         "description": "",
         "func": "curtis_fool",
         "activation mode": "normal",
         "recharge rate": 0.25,
         "depletion rate": 0,
         "free variables": {}
         },
    # Lawrence
    "Flame Canyon":
        {"name": "Flame Canyon",
         "class": "Offense",
         "description": "",
         "func": "lawrence_flame_canyon",
         "activation mode": "normal",
         "recharge rate": 0.25,
         "depletion rate": 0,
         "free variables": {}
         },
    "Flame Burst":
        {"name": "Flame Burst",
         "class": "Offense",
         "description": "",
         "func": "lawrence_flame_burst",
         "activation mode": "normal",
         "recharge rate": 0.125,
         "depletion rate": 0,
         "free variables": {}
         },
    # Mark
    "Target Locator":
        {"name": "Target Locator",
         "class": "Offense",
         "description": "",
         "func": "mark_target_locator",
         "activation mode": "hold",
         "recharge rate": 1,
         "depletion rate": 0.75,
         "free variables": {}
         },
    "Smoke Grenade":
        {"name": "Smoke Grenade",
         "class": "Offense",
         "description": "",
         "func": "mark_smoke_grenade",
         "activation mode": "normal",
         "recharge rate": 0.125,
         "depletion rate": 0,
         "free variables": {}
         },
    # Vivianne
    "Rat Shot":
        {"name": "Rat Shot",
         "class": "Offense",
         "description": "",
         "func": "vivianne_rat_shot",
         "activation mode": "normal",
         "recharge rate": 0.125,
         "depletion rate": 0,
         "free variables": {}
         },
    "Reaper Rounds":
        {"name": "Reaper Rounds",
         "class": "Offense",
         "description": "",
         "func": "vivianne_reaper_rounds",
         "activation mode": "normal",
         "recharge rate": 0.125,
         "depletion rate": 0,
         "free variables": {}
         },
    # Sand Buggy
    # sand_buggy_drift
    "Drift":
        {"name": "Drift",
         "class": "Offense",
         "description": "",
         "func": "sand_buggy_drift",
         "activation mode": "normal",
         "recharge rate": 1,
         "depletion rate": 0,
         "recharge max": 1,
         "free variables": {}
         },
    "Rocket Burst":
        {"name": "Rocket Burst",
         "class": "Offense",
         "description": "",
         "func": "sand_buggy_burst_rocket",
         "activation mode": "normal",
         "recharge rate": 1,
         "depletion rate": 0,
         "recharge max": 240,
         "free variables": {}
         },
}
