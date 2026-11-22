import pygame as pg
import random
import math

import Fun
import Particles
import Skills
import Event
import Entity
import Bullets
from Entity import dodging, universal_pathfinding, pathfinding, start_up_lag_handler, entity_dodge_bullets
from Entity_Input_Funcs import APC_MOVE_TO_POINT
import Entity_Boss_Attacks


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


def basic_gun_mechanics(self, entities, level):
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


# |THR-1's Assault|-----------------------------------------------------------------------------------------------------
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
    #


def player_act_advanced_movement(self, entities, level):
    # |Aim system|--------------------------------------------------------------------------------------------------
    Fun.aim_system(self, self.weapon)
    # |Movement Input|----------------------------------------------------------------------------------------------
    Fun.movement_player_advanced(self, entities, level)
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

    if self.armour_break:
        # Need a sound effect
        self.armour_break = False
        number_of_particle = 18
        for particles_to_add in range(360 // number_of_particle):
            entities["background particles"].append(Particles.RandomParticle2(
                [self.pos[0], self.pos[1]], Fun.GREEN, 2 * random.random(), random.randint(15, 45),
                                                        particles_to_add * number_of_particle,
                size=Fun.get_random_element_from_list([3, 4, 6])))
    #


def player_act_vertical(self, entities, level):
    # |Aim system|--------------------------------------------------------------------------------------------------
    Fun.aim_system(self, self.weapon)
    # |Movement Input|----------------------------------------------------------------------------------------------
    Fun.movement_player_vertical(self, entities, level)
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

    if self.armour_break:
        # Need a sound effect
        self.armour_break = False
        number_of_particle = 18
        for particles_to_add in range(360 // number_of_particle):
            entities["background particles"].append(Particles.RandomParticle2(
                [self.pos[0], self.pos[1]], Fun.GREEN, 2 * random.random(), random.randint(15, 45),
                                                        particles_to_add * number_of_particle,
                size=Fun.get_random_element_from_list([3, 4, 6])))


def nest_agent_act(self, entities, level):
    player_act_advanced_movement(self, entities, level)
    if self.no_shoot_state == 0:
        if self.input["Interact"]:
            speed = pg.math.clamp(Fun.distance_between(self.pos, self.mouse_pos) * 0.75 / 20, 1, 6.7)
            Bullets.spawn_bullet(self, entities, Bullets.GrenadeType8, Fun.move_with_vel_angle(self.pos, 16, self.aim_angle), self.aim_angle,
                                 [speed, 50, 4, 30,
                                  {"Incendiary": {
                                      "Amount of Bullets": 4,
                                      "Speed": 2,
                                      "Duration": 90,
                                      "Radius": 4,
                                      "Damage": 5,
                                      "Fire property": {"Particle allowed": True, "Burn chance": 1,
                                                        "Burn duration": 30, "Colour": Fun.FIRE,}}},
                                  {"Secondary explosion": {"Duration": 8, "Growth": 3.5, "Damage mod": 0.5}}])
            self.no_shoot_state = 25



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
                        selected_summon = Entity.player_repertory[Fun.get_random_element_from_list(valid_pool)]
                        entities["entities"].append(
                            Entity.Entity(
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
                "Buckshot": Entity_Boss_Attacks.curtis_buckshot,
                "Slug": Entity_Boss_Attacks.curtis_slug,
                "Burst Ricochet": Entity_Boss_Attacks.curtis_burst_ricochet,
                "Burst Long": Entity_Boss_Attacks.curtis_burst_long,
                "Flower Volley": Entity_Boss_Attacks.curtis_flower_volley,
                "Inverted Flower Volley": Entity_Boss_Attacks.curtis_inverted_flower_volley,
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


def moped_act(self, entities, level):
    angle = self.free_var["Move angle"] + 226 - 180

    # |Movement Input|----------------------------------------------------------------------------------------------
    self.running = False
    self.walking = False
    if self.time % 3 == 0:
        entities["particles"].append(Particles.Smoke(
                 Fun.move_with_vel_angle(self.pos, 8, self.free_var["Move angle"] - 180),
            colour=Fun.DARK_GRAY, duration=(5, 30)
        ))

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
        # self.free_var["Move angle"]
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
        self.free_var["Move angle"] = Fun.move_angle_toward_target_angle(self.free_var["Move angle"],
                                                                         self.free_var["Target Move angle"],
                                                                         turn_vel * mod)

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
                Fun.damage_calculation(e, round(abs(self.vel[0]) + abs(self.vel[1])) * 5, "Melee",
                                       death_message="Ran over")
            pass
    if self.draw_aim_line or self.weapon.laser_sight:
        pos = Fun.move_with_vel_angle(self.pos, -24, self.free_var["Move angle"])
        entities["background particles"].append(Particles.LineParticle(
            [pos[0], pos[1] - 14], Fun.BLUE, 1, self.weapon.range - 20,
            self.aim_angle, 2, 0))


# |Enemy Act|-----------------------------------------------------------------------------------------------------------
def enemy_act_type_1(self, entities, level):
    # Get the inputs

    Fun.aim_system(self, self.weapon)

    # Do shit
    Fun.movement_entity(self)

    basic_gun_mechanics(self, entities, level)

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



# |No Name TSS|---------------------------------------------------------------------------------------------------------

def enemy_act_type_1_no_name_tss(self, entities, level):
    # Get the inputs

    Fun.aim_system(self, self.weapon)

    # Do shit
    Fun.movement_entity(self)

    # I am placing the passive effects of enemies in the passive slot to not have to make more act functions
    basic_gun_mechanics(self, entities, level)


    # |Status effects|--------------------------------------------------------------------------------------------------
    # if self.status["No damage"] == 8:
    #     pass
    Fun.status_manager(self, entities)

    # |Movement output|-------------------------------------------------------------------------------------------------
    Fun.movement_output(self, level)

    # |Voice lines handler|---------------------------------------------------------------------------------------------
    # Handle Voice lines

    # laser sight
    if self.draw_aim_line:
        entities["particles"].append(Fun.LineParticle(
            Fun.move_with_vel_angle([self.pos[0], self.pos[1]], 10, self.aim_angle),
            (255, 50, 50), 1, self.weapon.range, self.aim_angle, width=2))
    #


def fish_act(self, entities, level):
    # Get the inputs

    Fun.aim_system(self, self.weapon)

    # Do shit
    Fun.movement_entity(self)

    # I am placing the passive effects of enemies in the passive slot to not have to make more act functions
    # self.weapon.passive(self, entities, bullets)
    # shooting(self, entities, bullets)

    # |Status effects|--------------------------------------------------------------------------------------------------
    # if self.status["No damage"] == 8:
    #     pass
    Fun.status_manager(self, entities)
    if self.damage_taken:
        if self.health < self.free_var["Health last frame"]:
            entities["particles"].append(
                Particles.FloatingTextType2([self.pos[0], self.pos[1] - 16], 18,
                                      f"{self.free_var['Health last frame'] - self.health}",
                                      Fun.WHITE, 30))

    # |Movement output|-------------------------------------------------------------------------------------------------
    Fun.movement_output(self, level)

    # |Voice lines handler|---------------------------------------------------------------------------------------------
    # Handle Voice lines

    # laser sight
    # if self.draw_aim_line:
    #     entities["particles"].append(Fun.LineParticle(
    #         Fun.move_with_vel_angle([self.pos[0], self.pos[1]], 10, self.aim_angle),
    #         (255, 50, 50), 1, self.weapon.range, self.aim_angle, width=2))
    self.free_var["Health last frame"] = self.health


def void_act(self, entities, level):
    # Get the inputs

    Fun.aim_system(self, self.weapon)

    # Do shit
    Fun.movement_entity(self)

    # I am placing the passive effects of enemies in the passive slot to not have to make more act functions
    basic_gun_mechanics(self, entities, level)
    if self.input["Shoot"]:
        player = entities["entities"][0]
        mod = random.randint(0, 45)
        self.no_shoot_state += mod
        self.pos = Fun.move_with_vel_angle(player.pos, 45 + mod * 2, player.angle + 180)

    # |Status effects|--------------------------------------------------------------------------------------------------
    # if self.status["No damage"] == 8:
    #     pass
    Fun.status_manager(self, entities)

    # |Movement output|-------------------------------------------------------------------------------------------------
    if self.status["High friction"] > 0:
        self.vel = [self.vel[0] * 0.25, self.vel[1] * 0.25]

    # This give the direction the entity moves towards,
    # when using it for anything you should check if the entity is even moving
    self.direction_angle = Fun.angle_between(self.vel, [0, 0])
    # Make the guy move
    self.pos[0] += self.vel[0]
    self.pos[1] += self.vel[1]
    self.collision_box = pg.Rect(self.pos[0] - self.thiccness / 2, self.pos[1] - self.thiccness / 2, self.thiccness, self.thiccness)
    friction_strength = self.friction
    if self.status["Forced Slide"]:  # Some enemies will slide
        friction_strength = 0.025
    if self.status["Low friction"] > 0:
        friction_strength = 0
    for i in range(2):
        if self.vel[i] != 0:
            if self.vel[i] > 0 + friction_strength:
                self.vel[i] -= friction_strength
            elif self.vel[i] < 0 - friction_strength:
                self.vel[i] += friction_strength
            else:
                self.vel[i] = 0

    #


def snake_act(self, entities, level):
    # Get the inputs

    Fun.aim_system(self, self.weapon)

    # Do shit
    Fun.movement_entity(self)

    # I am placing the passive effects of enemies in the passive slot to not have to make more act functions
    basic_gun_mechanics(self, entities, level)

    # |Status effects|--------------------------------------------------------------------------------------------------
    # if self.status["No damage"] == 8:
    #     pass
    Fun.status_manager(self, entities)

    # |Movement output|-------------------------------------------------------------------------------------------------
    # This give the direction the entity moves towards,
    # when using it for anything you should check if the entity is even moving
    self.direction_angle = Fun.angle_between(self.vel, [0, 0])
    # Make the guy move
    self.pos[0] += self.vel[0]
    self.pos[1] += self.vel[1]
    self.collision_box = pg.Rect(self.pos[0] - self.thiccness / 2, self.pos[1] - self.thiccness / 2, self.thiccness, self.thiccness)


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
            "Divorce Spiral": Entity_Boss_Attacks.gilgamesh_divorce_spiral,
            "Reverse Divorce Spiral": Entity_Boss_Attacks.gilgamesh_reverse_divorce_spiral,
            "Wall": Entity_Boss_Attacks.gilgamesh_wall,
            "Desert flower": Entity_Boss_Attacks.gilgamesh_desert_flower,
            "Desert dune": Entity_Boss_Attacks.gilgamesh_desert_dune,
        }[self.free_var["Current attack"]](self, entities, level)

    else:
        self.no_shoot_state -= 1
    {
        "Trishot": Entity_Boss_Attacks.gilgamesh_attack_1,
        "Dual shot": Entity_Boss_Attacks.gilgamesh_attack_2,
        "Hose": Entity_Boss_Attacks.gilgamesh_attack_3,
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
    Event.spawn_enemy(entities, "AA Laser", pos=pos[0], angle=random.randint(-180, 180), team=self.team)
    entities["entities"][-1].force_draw = True
    Event.spawn_enemy(entities, "Missile Battery", pos=pos[1], angle=random.randint(-180, 180), team=self.team)
    entities["entities"][-1].force_draw = True
    Event.spawn_enemy(entities, "Shield Generator", pos=pos[3], angle=random.randint(-180, 180), team=self.team)
    entities["entities"][-1].force_draw = True
    Event.spawn_enemy(entities, "Drone builder", pos=pos[2], angle=random.randint(-180, 180), team=self.team)
    entities["entities"][-1].force_draw = True
    self.func_act = aa_site_act_energy_generator


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
            Event.spawn_enemy("Drone", team=self.team, pos=pos, angle=random.randint(-180, 180))


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
    Entity_Boss_Attacks.bloodhound_boost(self, entities, level)
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
            "Missile": Entity_Boss_Attacks.bloodhound_hadean_missile,
            "Blade": Entity_Boss_Attacks.bloodhound_magma_blade,
            "Minigun": Entity_Boss_Attacks.bloodhound_lopolith_minigun,
            "Canon": Entity_Boss_Attacks.bloodhound_canon
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
    #


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
            "Shoulder Bash": Entity_Boss_Attacks.rigel_shoulder_bash,
            "Lance Swipe": Entity_Boss_Attacks.rigel_lance_swipe,
            "Giga Thrust": Entity_Boss_Attacks.rigel_giga_thrust,

            "Laser Barrage": Entity_Boss_Attacks.rigel_laser_barrage,
            "Plasma": Entity_Boss_Attacks.rigel_plasma,
            "Missile Circus": Entity_Boss_Attacks.rigel_missile_circus,
            "Raining Hell": Entity_Boss_Attacks.rigel_raining_hell
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

