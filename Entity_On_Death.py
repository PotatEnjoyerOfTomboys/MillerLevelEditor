import random

import Particles
import Fun
import Event
import Bullets
import Items


def on_death_slime(self, entities, level):
    # Create 2 new slime with a smaller thiccness
    thick = self.thiccness * 0.75
    if thick >= 12:
        for x in range(2):
            Event.spawn_enemy(entities, "Slime", pos=[self.pos[0], self.pos[1]], angle=self.angle, team=self.team)
            entities["entities"][-1].thiccness = thick
            entities["entities"][-1].max_health = 90 * thick / 40
            entities["entities"][-1].health = 90 * thick / 40

            entities["entities"][-1].vel = Fun.move_with_vel_angle([0, 0], 2, 360 * random.random())
        Fun.play_sound("Slime split")

        Particles.random_particle_2_circle(entities, self.pos, random.uniform(4, 7), 20, 90,
                                     colour=(13, 101, 61), size=8 * thick / 40, angle_mod=random.randint(45, 90))
    else:
        Fun.play_sound("Slime death")


def on_death_snake(self, entities, bullets):
    Fun.play_sound("Snake split")
    self.name = "Dead"
    self.free_var["Pos history"] = []


def on_death_fish(self, entities, bullets):
    entities["particles"].append(
        Particles.FloatingText(self.pos, 18, f"{self.name} defeated", (255, 255, 255),
                         alpha_growth=10, alpha_ungrowth=10))


def on_death_kamikaze(self, entities, bullets):
    Fun.play_sound("Sardine Blows Up")
    Bullets.spawn_bullet(
        self, entities, Bullets.ExplosionSecondary,
        [self.pos[0], self.pos[1]], 0, [0, 5, 7, 10, {"Duration": 5, "Growth": 5, "Damage mod": 1}])


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
    level["events"].append(Event.MissionEvent("", Event.trigger_constant, True, [Event.loss_of_apc]))


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


def enforcer_on_death(self, entities, level):
    Bullets.spawn_bullet(
        self, entities, Bullets.ExplosionSecondary, self.pos,
        0, [0, 30, 0, 20, {"Damage mod": 1, "Growth": 2, "Duration": 30}]
    )


def armoured_shield_generator_on_death(self, entities, level):
    entities["UI particles"].append(
        Particles.ArmouredShieldGeneratorDeathParticle(self.pos, 300, self.free_var["Move angle"], self.aim_angle))


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


def aa_site_on_death_shield_generator(self, entities, level):
    aa_site_on_death(self, entities, level)
    if self.free_var["Shield Target"]:
        self.free_var["Shield Target"].armour = 0


def hover_tank_on_death(self, entities, level):
    entities["UI particles"].append(
        Particles.HoverTankDeathParticle(self.pos, 300, self.free_var["Move angle"], self.aim_angle, self.free_var["Machine Gun Angle"]))


def gilgamesh_on_death(self, entities, level):
    entities["UI particles"].append(
        Particles.GilgameshDeathParticle(self.pos, 300, self.angle, self.aim_angle, self.draw_angle, self.weapon, self.draw_rotated_dist, self.weapon_draw_dist))


def bloodhound_on_death(self, entities, level):
    entities["UI particles"].append(Particles.BloodHoundDeathParticle(self.pos, 1200, self.free_var["Mech"], self.free_var["Move angle"]))


def attack_helicopter_on_death(self, entities, level):
    Fun.play_sound("Attack Helicopter Death Scream", "Voice")
    entities["UI particles"].append(
        Particles.AttackHelicopterDeathParticle(self.pos, 300, self.aim_angle, self.time))


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
        Event.MissionEvent("Finishing", Event.trigger_on_for, False, [Event.change_scrolling_target], free_var={"Timer": 60 * 5, "Manual target": self.pos}))

