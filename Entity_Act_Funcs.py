import pygame as pg
import random

import Fun
import Particles
import Skills
import Entity
from Entity import dodging, universal_pathfinding, pathfinding, start_up_lag_handler, entity_dodge_bullets
from Entity_Input_Funcs import APC_MOVE_TO_POINT


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

