import pygame as pg
import random
import math

import Bullets
import Weapons
import Fun
import Particles
from Entity import dodging, universal_pathfinding, pathfinding, start_up_lag_handler, entity_dodge_bullets



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


# |Component|-----------------------------------------------------------------------------------------------------------
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



# |Player inputs|-------------------------------------------------------------------------------------------------------
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


# |THR-1's Assault|-----------------------------------------------------------------------------------------------------
# |Enemy Input|---------------------------------------------------------------------------------------------------------
def enemy_input_thr_1s_assault_prototype(self, entities, level):
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
        #     true_target = move_target
        # if not true_target:
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

# |Bosses|--------------------------------------------------------------------------------------------------------------
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


def aa_site_input(self, entities, level):
    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    return target, target_angle


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


# |No Name TSS|---------------------------------------------------------------------------------------------------------
def enemy_input_commie_type_1(self, entities, level):
    # This version is used by all commie bots
    # Input functions are the IA for an enemy
    # better targeting system
    target, target_angle, wall_in = entity_target_detection(self, entities, level)

    self.input = Fun.get_default_inputs()
    if target:
        aim_target = self.target.pos.copy()
        self.angle = Fun.angle_between(aim_target, self.pos)

        self.input["Right"] = self.pos[0] < target[0]
        self.input["Left"] = self.pos[0] > target[0]
        self.input["Down"] = self.pos[1] < target[1]
        self.input["Up"] = self.pos[1] > target[1]

        # Just randomly attack
        if random.randint(0, self.weapon.fire_rate // 2) == 0:
            self.input["Shoot"] = True
        if not self.input["Shoot"]:
            if random.randint(0, self.weapon.fire_rate) == 0:
                self.input["Alt fire"] = True
        self.input["Reload"] = self.weapon.ammo == 0

    entity_spread_apart(self, entities)

    # Stunned status manager
    Fun.stunned_manager(self)
    return target, target_angle


def enemy_input_test(self, entities, level):
    # Input functions are the IA for an enemy
    target = False
    original_target = target
    target_angle = 0
    for p in entities["entities"]:
        if p.team == self.team: continue
        if Fun.check_point_in_circle(self.targeting_range, self.pos[0], self.pos[1], p.pos[0], p.pos[1]):
            target = p.pos
            original_target = target
            target_angle = p.angle

    # add way to make the target other ia

    self.input = Fun.get_default_inputs()

    if target:
        self.angle = Fun.angle_between(target, self.pos)
        # modify position of target for some ia types

        # Goes in front
        # target = [original_target[0] - self.weapon.range / 2 * math.cos(target_angle * math.pi / 180),
        #           original_target[1] - self.weapon.range / 2 * math.sin(target_angle * math.pi / 180)]
        # Goes behind
        target = [original_target[0] + self.weapon.range / 2 * math.cos(target_angle * math.pi / 180),
                  original_target[1] + self.weapon.range / 2 * math.sin(target_angle * math.pi / 180)]



        # Things to add to the movement if else
        # Make the AI stay a bit away from the target
        # and dist > self.weapon.range / 2:
        # Prevent the AI from going too far from the spawn point
        # and dist_from_start < self.targeting_range:

        if self.pos[0] < target[0]:
            self.input["Right"] = True
        elif self.pos[0] > target[0]:
            self.input["Left"] = True
        if self.pos[1] < target[1]:
            self.input["Down"] = True
        elif self.pos[1] > target[1]:
            self.input["Up"] = True

    # Check if something is in range
    if random.randint(0, self.weapon.fire_rate) == 0 and \
            Fun.check_point_in_circle(self.weapon.range, self.pos[0], self.pos[1], entities["entities"][0].pos[0],
                                      entities["entities"][0].pos[1]):
        self.input["Shoot"] = True

    self.input["Reload"] = self.weapon.ammo == 0
    # Stunned status manager
    Fun.stunned_manager(self)
    return target, target_angle


def enemy_input_fish(self, entities, level):
    # Input functions are the IA for an enemy
    target = False
    original_target = target
    target_angle = 0
    # for p in entities["players"]:
    #     if Fun.check_point_in_circle(self.targeting_range, self.pos[0], self.pos[1], p.pos[0], p.pos[1]):
    #         target = p.pos
    #         original_target = target
    #         target_angle = p.angle

    # add way to make the target other ia

    self.input = Fun.get_default_inputs()

    Fun.stunned_manager(self)
    return target, target_angle


def enemy_input_fish_2(self, entities, level):
    # Input functions are the IA for an enemy
    Fun.get_default_inputs()
    target = False
    original_target = target
    target_angle = 0
    # for p in entities["players"]:
    #     if Fun.check_point_in_circle(self.targeting_range, self.pos[0], self.pos[1], p.pos[0], p.pos[1]):
    #         target = p.pos
    #         original_target = target
    #         self.input["Shoot"] = True
    #     target_angle = p.angle

    Fun.stunned_manager(self)
    return target, target_angle


def enemy_input_shotgunner_type_1(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, original_target, target_angle = entity_target_detection(self, entities, level)
    original_target = target
    # target, target_angle, wall_in = entity_target_detection(self, entities, level)

    self.input = Fun.get_default_inputs()

    if target:
        self.angle = Fun.angle_between(target, self.pos)
        # modify position of target for some ia types

        # Goes behind
        target = [original_target[0] + self.weapon.range / 2 * math.cos(target_angle * math.pi / 180),
                  original_target[1] + self.weapon.range / 2 * math.sin(target_angle * math.pi / 180)]


        if self.pos[0] < target[0]:
            self.input["Right"] = True
        elif self.pos[0] > target[0]:
            self.input["Left"] = True
        if self.pos[1] < target[1]:
            self.input["Down"] = True
        elif self.pos[1] > target[1]:
            self.input["Up"] = True

        # Check if something is in range
        if random.randint(0, self.weapon.fire_rate) == 0 and \
                Fun.check_point_in_circle(self.weapon.range * 1.75, self.pos[0], self.pos[1],
                                          original_target[0],
                                          original_target[1]):
            self.input["Shoot"] = True
    self.input["Reload"] = self.weapon.ammo == 0
    # Stunned status manager
    Fun.stunned_manager(self)
    return target, target_angle


def enemy_input_shotgunner_type_2(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, original_target, target_angle = entity_target_detection(self, entities, level)
    original_target = target

    self.input = Fun.get_default_inputs()

    valid_enemies = {"enemies": []}
    for valid_enemy in entities["entities"]:
        if valid_enemy.team != self.team: continue
        if self.pos != valid_enemy.pos and valid_enemy.ai_type == "long range":
            valid_enemies["enemies"].append(valid_enemy)

    protected_target = Fun.find_closest_in_circle(self, valid_enemies, self.targeting_range, "enemies")
    if protected_target:
        protected_target_angle = Fun.angle_between(protected_target, self.pos)
        original_protected_target = [protected_target[0], protected_target[1]]
        # modify position of target for some ia types

        protected_target = [
            original_protected_target[0] - 40 * math.cos(self.angle * math.pi / 180),
            original_protected_target[1] - 40 * math.sin(self.angle * math.pi / 180)
        ]


        if self.pos[0] < protected_target[0]:
            self.input["Right"] = True
        elif self.pos[0] > protected_target[0]:
            self.input["Left"] = True
        if self.pos[1] < protected_target[1]:
            self.input["Down"] = True
        elif self.pos[1] > protected_target[1]:
            self.input["Up"] = True
    # Do stuff if the player gets close
    if target:
        self.angle = Fun.angle_between(target, self.pos)
        # modify position of target for some ia types

        # Goes behind
        if not protected_target:
            target = [original_target[0] + self.weapon.range / 2 * math.cos(target_angle * math.pi / 180),
                      original_target[1] + self.weapon.range / 2 * math.sin(target_angle * math.pi / 180)]


            if self.pos[0] < target[0]:
                self.input["Right"] = True
            elif self.pos[0] > target[0]:
                self.input["Left"] = True
            if self.pos[1] < target[1]:
                self.input["Down"] = True
            elif self.pos[1] > target[1]:
                self.input["Up"] = True

        # Check if something is in range
        if random.randint(0, self.weapon.fire_rate) == 0 and \
                Fun.check_point_in_circle(self.weapon.range * 1.75, self.pos[0], self.pos[1],
                                          original_target[0],
                                          original_target[1]):
            self.input["Shoot"] = True
    self.input["Reload"] = self.weapon.ammo == 0
    # Stunned status manager
    Fun.stunned_manager(self)
    return target, target_angle


def enemy_input_flamer_type_1(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, original_target, target_angle = entity_target_detection(self, entities, level)
    original_target = target

    Fun.get_default_inputs()

    if target:
        self.angle = Fun.angle_between(target, self.pos)
        # modify position of target for some ia types

        # Goes behind
        target = [original_target[0] + self.weapon.range / 2 * math.cos(target_angle * math.pi / 180),
                  original_target[1] + self.weapon.range / 2 * math.sin(target_angle * math.pi / 180)]


        if self.pos[0] < target[0]:
            self.input["Right"] = True
        elif self.pos[0] > target[0]:
            self.input["Left"] = True
        if self.pos[1] < target[1]:
            self.input["Down"] = True
        elif self.pos[1] > target[1]:
            self.input["Up"] = True

        # Check if something is in range
        if Fun.check_point_in_circle(self.weapon.range * 2, self.pos[0], self.pos[1],
                                     target[0],
                                     target[1]):
            self.input["Shoot"] = True
    self.input["Reload"] = self.weapon.ammo == 0
    # Stunned status manager
    Fun.stunned_manager(self)
    return target, target_angle


def enemy_input_buffer_type_1(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, original_target, target_angle = entity_target_detection(self, entities, level)
    original_target = target

    Fun.get_default_inputs()
    # go and find a target to stay close to
    valid_enemies = {"enemies": []}
    for valid_enemy in entities["entities"]:
        if valid_enemy.team != self.team: continue
        if self.pos != valid_enemy.pos:
            valid_enemies["enemies"].append(valid_enemy)


    buff_target = Fun.find_closest_in_circle(self, valid_enemies, self.targeting_range, "enemies")
    if buff_target:
        buff_target_angle = Fun.angle_between(buff_target, self.pos)
        original_buff_target = [buff_target[0], buff_target[1]]
        # modify position of target for some ia types

        buff_target = [original_buff_target[0] + 35 * math.cos(buff_target_angle * math.pi / 180),
                       original_buff_target[1] + 35 * math.sin(buff_target_angle * math.pi / 180)]


        if self.pos[0] < buff_target[0]:
            self.input["Right"] = True
        elif self.pos[0] > buff_target[0]:
            self.input["Left"] = True
        if self.pos[1] < buff_target[1]:
            self.input["Down"] = True
        elif self.pos[1] > buff_target[1]:
            self.input["Up"] = True
    # Do stuff if the player gets close
    if target:
        self.angle = Fun.angle_between(target, self.pos)
        # modify position of target for some ia types

        dist = math.hypot(target[0] - self.pos[0], target[1] - self.pos[1])
        if not buff_target:
            if self.pos[0] < target[0] and dist > self.weapon.range / 5 * 4:
                self.input["Right"] = True
            elif self.pos[0] > target[0] and dist > self.weapon.range / 5 * 4:
                self.input["Left"] = True
            if self.pos[1] < target[1] and dist > self.weapon.range / 5 * 4:
                self.input["Down"] = True
            elif self.pos[1] > target[1] and dist > self.weapon.range / 5 * 4:
                self.input["Up"] = True

        # Check if something is in range
        if random.randint(0, self.weapon.fire_rate) == 0 and \
                Fun.check_point_in_circle(self.weapon.range * 1.5, self.pos[0], self.pos[1],
                                          target[0],
                                          target[1]):
            self.input["Shoot"] = True
    self.input["Reload"] = self.weapon.ammo == 0
    # Stunned status manager
    Fun.stunned_manager(self)
    return target, target_angle


def enemy_input_grunt_type_1(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, original_target, target_angle = entity_target_detection(self, entities, level)
    original_target = target

    self.input = Fun.get_default_inputs()

    if target:
        self.angle = Fun.angle_between(target, self.pos)
        # modify position of target for some ia types

        # Goes in front
        target = [original_target[0] - self.weapon.range / 5 * math.cos(target_angle * math.pi / 180),
                  original_target[1] - self.weapon.range / 5 * math.sin(target_angle * math.pi / 180)]

        dist = math.hypot(target[0] - self.pos[0], target[1] - self.pos[1])

        if self.pos[0] < target[0] and dist > self.weapon.range / 5 * 4:
            self.input["Right"] = True
        elif self.pos[0] > target[0] and dist > self.weapon.range / 5 * 4:
            self.input["Left"] = True
        if self.pos[1] < target[1] and dist > self.weapon.range / 5 * 4:
            self.input["Down"] = True
        elif self.pos[1] > target[1] and dist > self.weapon.range / 5 * 4:
            self.input["Up"] = True

        # Check if something is in range
        if random.randint(0, self.weapon.fire_rate) == 0 and \
                Fun.check_point_in_circle(self.weapon.range, self.pos[0], self.pos[1],
                                          target[0],
                                          target[1]):
            self.input["Shoot"] = True
    self.input["Reload"] = self.weapon.ammo == 0
    # Stunned status manager
    Fun.stunned_manager(self)
    return target, target_angle


def enemy_input_sniper_type_1(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, original_target, target_angle = entity_target_detection(self, entities, level)
    original_target = target

    self.input = Fun.get_default_inputs()

    if target:
        dist = math.hypot(target[0] - self.pos[0], target[1] - self.pos[1])

        self.angle = Fun.angle_between(self.target.pos, self.pos)

        if dist > self.weapon.range / 5 * 4:
            self.input["Right"] = self.pos[0] < target[0]
            self.input["Left"] = self.pos[0] > target[0]
            self.input["Down"] = self.pos[1] < target[1]
            self.input["Up"] = self.pos[1] > target[1]

        # The AI will try to get away from the player if he gets too close
        if dist < self.weapon.range / 2:
            self.input = Fun.get_default_inputs()
            if self.pos[0] > target[0]:
                self.input["Right"] = True
            elif self.pos[0] < target[0]:
                self.input["Left"] = True
            if self.pos[1] > target[1]:
                self.input["Down"] = True
            elif self.pos[1] < target[1]:
                self.input["Up"] = True

        # Check if something is in range
        # random.randint(0, self.weapon.fire_rate) == 0 and \
        if self.weapon.ammo > 0 and \
                Fun.check_point_in_circle(self.weapon.range, self.pos[0], self.pos[1], target[0], target[1]) and \
                self.free_var['Startup lag'] == 0:
            self.free_var['Startup lag'] += 1
    self.input["Reload"] = self.weapon.ammo == 0
    self.draw_aim_line = False
    if self.free_var['Startup lag'] > 0:
        if start_up_lag_handler(self, self.free_var["Startup time"]):
            self.input["Shoot"] = True
        self.draw_aim_line = self.weapon.laser_sight

    # Stunned status manager
    Fun.stunned_manager(self)
    return target, target_angle


def enemy_input_sniper_type_2(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, original_target, target_angle = entity_target_detection(self, entities, level)
    original_target = target

    self.input = Fun.get_default_inputs()

    if target:
        self.angle = Fun.angle_between(target, self.pos)
        dist = math.hypot(target[0] - self.pos[0], target[1] - self.pos[1])

        if self.pos[0] < target[0] and dist > self.weapon.bullet_info[2] / 5 * 4:
            self.input["Right"] = True
        elif self.pos[0] > target[0] and dist > self.weapon.bullet_info[2] / 5 * 4:
            self.input["Left"] = True
        if self.pos[1] < target[1] and dist > self.weapon.bullet_info[2] / 5 * 4:
            self.input["Down"] = True
        elif self.pos[1] > target[1] and dist > self.weapon.bullet_info[2] / 5 * 4:
            self.input["Up"] = True

        # The AI will try to get away from the player if he gets too close
        if dist < self.weapon.bullet_info[2] * 0.95:
            self.input = Fun.get_default_inputs()
            if self.pos[0] > target[0]:
                self.input["Right"] = True
            elif self.pos[0] < target[0]:
                self.input["Left"] = True
            if self.pos[1] > target[1]:
                self.input["Down"] = True
            elif self.pos[1] < target[1]:
                self.input["Up"] = True

            # Check if something is in range
            if self.weapon.ammo > 0 and \
                    Fun.check_point_in_circle(self.weapon.range, self.pos[0], self.pos[1], target[0], target[1]) and \
                    self.free_var['Startup lag'] == 0:
                self.free_var['Startup lag'] += 1
    self.input["Reload"] = self.weapon.ammo == 0
    self.draw_aim_line = False
    if self.free_var['Startup lag'] > 0:
        if start_up_lag_handler(self, self.free_var["Startup time"]):
            self.input["Shoot"] = True
        self.draw_aim_line = self.weapon.laser_sight

    # Stunned status manager
    Fun.stunned_manager(self)
    return target, target_angle


def enemy_input_crazies_type_1(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, original_target, target_angle = entity_target_detection(self, entities, level)
    original_target = target

    self.input = Fun.get_default_inputs()

    if target:
        self.angle = Fun.angle_between(target, self.pos)
        # modify position of target for some ia types

        # Goes in front
        # testing = random.randint(2, 6)
        target = [original_target[0] - self.weapon.range / 1.25 * math.cos(target_angle * math.pi / 180),
                  original_target[1] - self.weapon.range / 1.25 * math.sin(target_angle * math.pi / 180)]

        dist = math.hypot(target[0] - self.pos[0], target[1] - self.pos[1])

        if self.pos[0] < target[0]:
            self.input["Right"] = True
        elif self.pos[0] > target[0]:
            self.input["Left"] = True
        if self.pos[1] < target[1]:
            self.input["Down"] = True
        elif self.pos[1] > target[1]:
            self.input["Up"] = True

        # Check if something is in range
        if Fun.check_point_in_circle(100, self.pos[0], self.pos[1],
                                     target[0],
                                     target[1]) \
                and random.randint(0, self.weapon.fire_rate // 2) == 0:
            self.input["Shoot"] = True
        if not self.input["Shoot"]:
            if Fun.check_point_in_circle(500, self.pos[0], self.pos[1],
                                         target[0],
                                         target[1]) \
                    and random.randint(0, self.weapon.fire_rate) == 0:
                self.input["Alt fire"] = True
    self.input["Reload"] = self.weapon.ammo == 0
    # Stunned status manager
    Fun.stunned_manager(self)
    return target, target_angle


# Nest AI
def nest_formation_manager(self, entities, level):
    # Parts of this can be reused to make the "snek" enemy once I have to make it
    # https://2img.net/h/i37.photobucket.com/albums/e59/besh-lo/Formations.jpg

    # This is gonna get funky real fast
    output = []
    if "Formation" not in self.free_var:
        return output
    if self.free_var["Formation"][0] == "None" or self.free_var["Formation"][1] == 0:
        return output

    # Get the position of whoever is the formation leader

    if self.input["Shoot"] and self.weapon.full_auto:
        self.input["Shoot"] = self.time % (self.weapon.fire_rate + 1) == 0
    if self.free_var["Formation"][0] in ["Line", "Line Left", "Line Right"]:
        leader_pos = []
        leader_angle = 0
        for e in entities["entities"]:
            if e.team != self.team: continue
            if "Formation" in e.free_var:
                if e.free_var["Formation"][0] != self.free_var["Formation"][0]:
                    continue

                if e.free_var["Formation"][1] == self.free_var["Formation"][1] - 1:
                    leader_pos = e.pos
                    leader_angle = e.angle
                    break
        if leader_pos:
            # Get the position to go to
            return {
                "Line": Fun.move_with_vel_angle(leader_pos, -32, leader_angle),
                "Line Right": Fun.move_with_vel_angle(leader_pos, 32, leader_angle + 95),
                "Line Left": Fun.move_with_vel_angle(leader_pos, 32, leader_angle - 95),
            }[self.free_var["Formation"][0]]
    if self.free_var["Formation"][0] in ["Web", "Spear", "Basic 1", "Basic 2", "Vee", "Diamond"]:
        true_leader_pos = []
        true_leader_angle = 0
        for e in entities["entities"]:
            if e.team != self.team: continue
            if "Formation" in e.free_var:
                if e.free_var["Formation"][0] != self.free_var["Formation"][0]:
                    continue
                if e.free_var["Formation"][1] == 0:
                    true_leader_pos = e.pos
                    true_leader_angle = e.angle
                    break

        if true_leader_pos:
            return {
                "Web": Fun.move_with_vel_angle(true_leader_pos, 64,
                                               [
                                                   true_leader_angle,
                                                   true_leader_angle + 30, true_leader_angle - 30,
                                                   true_leader_angle + 90, true_leader_angle - 90,
                                                   true_leader_angle + 150, true_leader_angle - 150,
                                               ][self.free_var["Formation"][1] % 7]),
                "Spear": Fun.move_with_vel_angle(true_leader_pos, 64,
                                                 [
                                                     true_leader_angle,
                                                     true_leader_angle,
                                                     true_leader_angle + 30, true_leader_angle - 30,
                                                     true_leader_angle + 180,
                                                 ][self.free_var["Formation"][1] % 5]),
                "Basic 1": Fun.move_with_vel_angle(true_leader_pos, 32 * self.free_var["Formation"][1],
                                                   [
                                                       true_leader_angle,
                                                       true_leader_angle + 135,
                                                       true_leader_angle - 135,
                                                       true_leader_angle + 135,
                                                   ][self.free_var["Formation"][1] % 4]),
                "Basic 2": Fun.move_with_vel_angle(true_leader_pos, 32 * self.free_var["Formation"][1],
                                                   [
                                                       true_leader_angle,
                                                       true_leader_angle - 135,
                                                       true_leader_angle + 135,
                                                       true_leader_angle - 135,
                                                   ][self.free_var["Formation"][1] % 4]),
                "Vee": Fun.move_with_vel_angle(true_leader_pos, 64,
                                               [
                                                   true_leader_angle,
                                                   true_leader_angle - 25,
                                                   true_leader_angle + 25,
                                                   true_leader_angle - 180,
                                               ][self.free_var["Formation"][1] % 4]),
                "Diamond": Fun.move_with_vel_angle(true_leader_pos, 32,
                                                   [
                                                       true_leader_angle,
                                                       true_leader_angle,
                                                       true_leader_angle + 90,
                                                       true_leader_angle - 90,
                                                       true_leader_angle - 180,
                                                   ][self.free_var["Formation"][1] % 5]),
            }[self.free_var["Formation"][0]]
    # This is a failsafe
    return output


def enemy_input_nest_trooper(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, original_target, target_angle = entity_target_detection(self, entities, level)
    original_target = target

    self.input = Fun.get_default_inputs()

    if target:
        self.angle = Fun.angle_between(target, self.pos)
        # modify position of target for some ia types

        # Goes in front
        target = [original_target[0] - self.weapon.range / 5 * math.cos(target_angle * math.pi / 180),
                  original_target[1] - self.weapon.range / 5 * math.sin(target_angle * math.pi / 180)]

        og_dist = Fun.distance_between(original_target, self.pos)
        range_target = og_dist > self.weapon.range * 0.65
        if range_target:
            self.input["Right"] = self.pos[0] < target[0]
            self.input["Left"] = self.pos[0] > target[0]
            self.input["Down"] = self.pos[1] < target[1]
            self.input["Up"] = self.pos[1] > target[1]

        if og_dist < self.weapon.range * 0.3:
            self.input = {"Up": self.pos[1] < target[1], "Right": self.pos[0] > target[0],
                          "Left": self.pos[0] < target[0], "Down": self.pos[1] > target[1], "Dash": False,
                          "Shoot": False, "Alt fire": False, "Reload": False,
            "Interact": False, "Skill 1": False, "Skill 2": False,
            "Order Hold": False, "Order Follow": False, "Order Attack": False, "Order Act Free": False}

        # Check if something is in range
        if random.randint(0, self.weapon.fire_rate) == 0 and Fun.check_point_in_circle(
                self.weapon.range * 0.8, self.pos[0], self.pos[1], original_target[0], original_target[1]):
            self.input["Shoot"] = True

        self.input["Alt fire"] = random.random() < 0.7 and self.weapon.ammo in [
            round(self.weapon.max_ammo * 0.25), round(self.weapon.max_ammo * 0.75)
        ]
    self.input["Reload"] = self.weapon.ammo == 0
    formation_target = nest_formation_manager(self, entities, level)

    if formation_target:
        self.input = {"Up": self.pos[1] > formation_target[1], "Right": self.pos[0] < formation_target[0],
                      "Left": self.pos[0] > formation_target[0], "Down": self.pos[1] < formation_target[1],
                      "Dash": False,
                      "Shoot": self.input["Shoot"],
                      "Alt fire": self.input["Alt fire"], "Reload": False,
            "Interact": False, "Skill 1": False, "Skill 2": False,
            "Order Hold": False, "Order Follow": False, "Order Attack": False, "Order Act Free": False}

    if not self.cutscene_mode:

        if dodging(self, entities, entities["bullets"], search_range=32, bullet_minimum=1, random_chance=(3, 0),
                   dodge_angles=(60, 120), dodge_vel=10, invulnerability_time=5):
            for x in range(3):
                entities["particles"].append(Particles.Smoke(Fun.random_point_in_circle(self.pos, 16)))
    # Stunned status manager
    Fun.stunned_manager(self)
    #

    return target, target_angle


def enemy_input_nest_sniper(self, entities,  level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, original_target, target_angle = entity_target_detection(self, entities, level)
    original_target = target

    self.input = Fun.get_default_inputs()

    if target:
        self.angle = Fun.angle_between(target, self.pos)
        # modify position of target for some ia types

        # Goes in front
        target = [original_target[0] - self.weapon.range / 5 * math.cos(target_angle * math.pi / 180),
                  original_target[1] - self.weapon.range / 5 * math.sin(target_angle * math.pi / 180)]

        # dist = math.hypot(target[0] - self.pos[0], target[1] - self.pos[1])
        dist = Fun.distance_between(original_target, self.pos)

        self.input["Right"] = self.pos[0] < target[0] and dist > self.weapon.range * 0.8
        self.input["Left"] = self.pos[0] > target[0] and dist > self.weapon.range * 0.8
        self.input["Down"] = self.pos[1] < target[1] and dist > self.weapon.range * 0.8
        self.input["Up"] = self.pos[1] > target[1] and dist > self.weapon.range * 0.8

        if dist < self.weapon.range * 0.4:
            self.input = Fun.get_default_inputs()
            if self.pos[0] > target[0]:
                self.input["Right"] = True
            elif self.pos[0] < target[0]:
                self.input["Left"] = True
            if self.pos[1] > target[1]:
                self.input["Down"] = True
            elif self.pos[1] < target[1]:
                self.input["Up"] = True

            # Check if something is in range
            if self.weapon.ammo > 0 and \
                    Fun.check_point_in_circle(self.weapon.range*1.1, self.pos[0], self.pos[1], target[0], target[1]) and \
                    self.free_var['Startup lag'] == 0:
                self.free_var['Startup lag'] += 1
    self.input["Reload"] = self.weapon.ammo == 0
    self.draw_aim_line = False
    if self.free_var['Startup lag'] > 0:
        self.draw_aim_line = self.weapon.laser_sight
        if start_up_lag_handler(self, self.free_var["Startup time"]):
            self.input["Shoot"] = True

    formation_target = nest_formation_manager(self, entities,  level)

    if formation_target:
        self.input = {"Up": False, "Right": False, "Left": False, "Down": False, "Dash": False,
                      "Shoot": self.input["Shoot"], "Alt fire": self.input["Alt fire"], "Reload": False,
            "Interact": False, "Skill 1": False, "Skill 2": False,
            "Order Hold": False, "Order Follow": False, "Order Attack": False, "Order Act Free": False}
        if self.pos[0] < formation_target[0]:
            self.input["Right"] = True
        elif self.pos[0] > formation_target[0]:
            self.input["Left"] = True
        if self.pos[1] < formation_target[1]:
            self.input["Down"] = True
        elif self.pos[1] > formation_target[1]:
            self.input["Up"] = True

    if not self.cutscene_mode:
        if dodging(self, entities, "bullets", search_range=32, bullet_minimum=1, random_chance=(3, 0),
                   dodge_angles=(60, 120), dodge_vel=10, invulnerability_time=5):
            for x in range(3):
                entities["particles"].append(Particles.Smoke(Fun.random_point_in_circle(self.pos, 32)))
    # Stunned status manager
    Fun.stunned_manager(self)


    return target, target_angle


def enemy_input_nest_shield(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, original_target, target_angle = entity_target_detection(self, entities, level)
    original_target = target

    self.input = Fun.get_default_inputs()

    if target:
        self.angle = Fun.angle_between(target, self.pos)
        # modify position of target for some ia types

        # Goes in front
        target = [original_target[0] - self.weapon.range / 5 * math.cos(target_angle * math.pi / 180),
                  original_target[1] - self.weapon.range / 5 * math.sin(target_angle * math.pi / 180)]

        # dist = math.hypot(target[0] - self.pos[0], target[1] - self.pos[1])
        og_dist = Fun.distance_between(original_target, self.pos)
        if self.pos[0] < target[0] and og_dist > self.weapon.range * 0.85:
            self.input["Right"] = True
        elif self.pos[0] > target[0] and og_dist > self.weapon.range * 0.85:
            self.input["Left"] = True
        if self.pos[1] < target[1] and og_dist > self.weapon.range * 0.85:
            self.input["Down"] = True
        elif self.pos[1] > target[1] and og_dist > self.weapon.range * 0.85:
            self.input["Up"] = True

        if og_dist < self.weapon.range * 0.3:
            self.input = {"Up": self.pos[1] < target[1],
                          "Right": self.pos[0] > target[0],
                          "Left": self.pos[0] < target[0],
                          "Down": self.pos[1] > target[1], "Dash": False,
                          "Shoot": False, "Alt fire": False, "Reload": False,
            "Interact": False, "Skill 1": False, "Skill 2": False,
            "Order Hold": False, "Order Follow": False, "Order Attack": False, "Order Act Free": False}

        # Check if something is in range
        if random.randint(0, self.weapon.fire_rate) == 0 and \
                Fun.check_point_in_circle(self.weapon.range * 0.8, self.pos[0], self.pos[1], target[0], target[1]):
            self.input["Shoot"] = True
    self.input["Reload"] = self.weapon.ammo == 0
    formation_target = nest_formation_manager(self, entities, level)

    if formation_target:
        self.input = {"Up": self.pos[1] > formation_target[1],
                      "Right": self.pos[0] < formation_target[0],
                      "Left": self.pos[0] > formation_target[0],
                      "Down": self.pos[1] < formation_target[1], "Dash": False,
                      "Shoot": self.input["Shoot"], "Alt fire": self.input["Alt fire"], "Reload": False,
            "Interact": False, "Skill 1": False, "Skill 2": False,
            "Order Hold": False, "Order Follow": False, "Order Attack": False, "Order Act Free": False}

    if not self.cutscene_mode:
        self.input["Alt fire"] = Fun.get_number_of_thing_in_a_damn_circle(
            entities, "bullets", 500, self.pos[0], self.pos[1]) > 1 or self.status["High friction"] > 0
    # Stunned status manager
    Fun.stunned_manager(self)

    return target, target_angle


def enemy_input_nest_commander(self, entities,  level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, original_target, target_angle = entity_target_detection(self, entities, level)
    original_target = target

    self.input = Fun.get_default_inputs()

    if target:
        self.angle = Fun.angle_between(target, self.pos)
        # modify position of target for some ia types

        # Goes in front
        target = [original_target[0] - self.weapon.range / 5 * math.cos(target_angle * math.pi / 180),
                  original_target[1] - self.weapon.range / 5 * math.sin(target_angle * math.pi / 180)]

        # dist = math.hypot(target[0] - self.pos[0], target[1] - self.pos[1])
        og_dist = Fun.distance_between(original_target, self.pos)
        range_target = og_dist > self.weapon.range * 1.1
        if range_target:
            self.input["Right"] = self.pos[0] < target[0]
            self.input["Left"] = self.pos[0] > target[0]
            self.input["Down"] = self.pos[1] < target[1]
            self.input["Up"] = self.pos[1] > target[1]

        if og_dist < self.weapon.range * 0.9:
            self.input = {"Up": self.pos[1] < target[1], "Right": self.pos[0] > target[0],
                          "Left": self.pos[0] < target[0], "Down": self.pos[1] > target[1], "Dash": False,
                          "Shoot": False, "Alt fire": False, "Reload": False,
            "Interact": False, "Skill 1": False, "Skill 2": False,
            "Order Hold": False, "Order Follow": False, "Order Attack": False, "Order Act Free": False}

        # Check if something is in range
        if random.randint(0, self.weapon.fire_rate) == 0 and \
                Fun.check_point_in_circle(self.weapon.range * 0.8, self.pos[0], self.pos[1], target[0], target[1]):
            self.input["Shoot"] = True
    self.input["Reload"] = self.weapon.ammo == 0
    #
    closest_commander = Fun.find_closest_in_circle_check_name(self, entities, 160, "Nest Commander")
    if closest_commander:
        self.input = {"Up": self.pos[1] < closest_commander[1], "Right": self.pos[0] > closest_commander[0],
                      "Left": self.pos[0] < closest_commander[0], "Down": self.pos[1] > closest_commander[1],
                       "Dash": False, "Shoot": False, "Alt fire": False, "Reload": False,
            "Interact": False, "Skill 1": False, "Skill 2": False,
            "Order Hold": False, "Order Follow": False, "Order Attack": False, "Order Act Free": False}

    # Handles formations
    formation_target = nest_formation_manager(self, entities,  level)
    if formation_target:
        self.input = {"Up": self.pos[1] > formation_target[1], "Right": self.pos[0] < formation_target[0],
                      "Left": self.pos[0] > formation_target[0], "Down": self.pos[1] < formation_target[1],
                       "Dash": False, "Shoot": self.input["Shoot"], "Alt fire": self.input["Alt fire"], "Reload": False,
            "Interact": False, "Skill 1": False, "Skill 2": False,
            "Order Hold": False, "Order Follow": False, "Order Attack": False, "Order Act Free": False}

    if not self.cutscene_mode:
        if dodging(self, entities, "bullets", search_range=32, bullet_minimum=1, random_chance=(3, 0),
                   dodge_angles=(60, 120), dodge_vel=10, invulnerability_time=5):
            for x in range(3):
                entities["particles"].append(Particles.Smoke(Fun.random_point_in_circle(self.pos, 32)))

    # Stunned status manager
    Fun.stunned_manager(self)


    return target, target_angle


def enemy_input_nest_cloaker(self, entities,  level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, original_target, target_angle = entity_target_detection(self, entities, level)
    original_target = target

    self.input = Fun.get_default_inputs()
    if target:
        self.angle = Fun.angle_between(target, self.pos)
        # modify position of target for some ia types

        # Goes in front
        target = [original_target[0], original_target[1]]

        og_dist = Fun.distance_between(original_target, self.pos)
        range_target = og_dist > self.weapon.range * 0.65
        if range_target:
            self.input["Right"] = self.pos[0] < target[0]
            self.input["Left"] = self.pos[0] > target[0]
            self.input["Down"] = self.pos[1] < target[1]
            self.input["Up"] = self.pos[1] > target[1]

        if og_dist < self.weapon.range * 0.3:
            self.input = {"Up": self.pos[1] < target[1], "Right": self.pos[0] > target[0],
                          "Left": self.pos[0] < target[0], "Down": self.pos[1] > target[1],
                           "Dash": False,
                          "Shoot": False, "Alt fire": False, "Reload": False,
            "Interact": False, "Skill 1": False, "Skill 2": False,
            "Order Hold": False, "Order Follow": False, "Order Attack": False, "Order Act Free": False}

        # Check if something is in range
        if og_dist <= self.weapon.range:
            self.input["Shoot"] = True
    self.input["Reload"] = self.weapon.ammo == 0
    # formation_target = nest_formation_manager(self, entities,  level)

    for e in entities["entities"]:
        if e.team != self.team: continue
        if 0 < Fun.distance_between(e.pos, self.pos) < 32:
            self.input["Right"] = self.pos[0] > e.pos[0]
            self.input["Left"] = self.pos[0] < e.pos[0]
            self.input["Down"] = self.pos[1] > e.pos[1]
            self.input["Up"] = self.pos[1] < e.pos[1]
            break

    if not self.cutscene_mode:
        if dodging(self, entities, "bullets", search_range=32, bullet_minimum=1, random_chance=(3, 0),
                   dodge_angles=(60, 120), dodge_vel=10, invulnerability_time=5):
            for x in range(3):
                entities["particles"].append(Particles.Smoke(Fun.random_point_in_circle(self.pos, 16)))
    # Stunned status manager
    Fun.stunned_manager(self)


    # The cloaker is invisible when you don't look at it
    hide = True
    for p in entities["entities"]:
        if p.team == self.team: continue
        if Fun.check_point_in_circle(450 * 0.25, p.pos[0], p.pos[1], self.pos[0], self.pos[1]) or \
                Fun.check_point_in_cone(self.targeting_range, p.pos[0], p.pos[1], self.pos[0], self.pos[1],
                                        p.angle, self.targeting_angle):
            hide = False
            break
    if hide:
        self.status["Stealth"] = 2

        # if 300 < self.time % 800 < 800:
        alpha = 128 + 128 * math.sin(self.time//16)
        entities["UI particles"].append(
            Particles.GrowingSquareTransparent((self.pos[0] - 2, self.pos[1] - 3, 1, 1), Fun.GREEN, [0, 0], 12, alpha))
        entities["UI particles"].append(
            Particles.GrowingSquareTransparent((self.pos[0] + 2, self.pos[1] - 3, 1, 1), Fun.GREEN, [0, 0], 12, alpha))
        # if random.random() < 0.01:
        #     for x in range(3):
        #         entities["particles"].append(Particles.Smoke(Fun.move_with_vel_angle(
        #             self.pos, random.random() * 16, random.random() * 360)))

    return target, target_angle


def enemy_input_nest_cloaker_sniper(self, entities,  level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, original_target, target_angle = entity_target_detection(self, entities, level)
    original_target = target

    self.input = Fun.get_default_inputs()
    if target:
        self.angle = Fun.angle_between(target, self.pos)
        # modify position of target for some ia types

        # Goes in front
        target = [original_target[0], original_target[1]]

        og_dist = Fun.distance_between(original_target, self.pos)
        range_target = og_dist > self.weapon.range * 0.65
        if range_target:
            self.input["Right"] = self.pos[0] < target[0]
            self.input["Left"] = self.pos[0] > target[0]
            self.input["Down"] = self.pos[1] < target[1]
            self.input["Up"] = self.pos[1] > target[1]

        if og_dist < self.weapon.range * 0.3:
            self.input = {"Up": self.pos[1] < target[1], "Right": self.pos[0] > target[0],
                          "Left": self.pos[0] < target[0], "Down": self.pos[1] > target[1],
                           "Dash": False,
                          "Shoot": False, "Alt fire": False, "Reload": False,
            "Interact": False, "Skill 1": False, "Skill 2": False,
            "Order Hold": False, "Order Follow": False, "Order Attack": False, "Order Act Free": False}

        # Check if something is in range
        if og_dist <= self.weapon.range and self.free_var['Startup lag'] == 0:
            self.free_var['Startup lag'] += 1
            # self.input["Shoot"] = True
    self.input["Reload"] = self.weapon.ammo == 0
    self.draw_aim_line = False
    if self.free_var['Startup lag'] > 0:
        self.draw_aim_line = self.weapon.laser_sight
        if start_up_lag_handler(self, self.free_var["Startup time"]):
            self.input["Shoot"] = True
    # formation_target = nest_formation_manager(self, entities,  level)

    for e in entities["entities"]:
        if e.team != self.team: continue
        if 0 < Fun.distance_between(e.pos, self.pos) < 32:
            self.input["Right"] = self.pos[0] > e.pos[0]
            self.input["Left"] = self.pos[0] < e.pos[0]
            self.input["Down"] = self.pos[1] > e.pos[1]
            self.input["Up"] = self.pos[1] < e.pos[1]
            break

    if not self.cutscene_mode:
        if dodging(self, entities, "bullets", search_range=32, bullet_minimum=1, random_chance=(3, 0),
                   dodge_angles=(60, 120), dodge_vel=10, invulnerability_time=5):
            for x in range(3):
                entities["particles"].append(Particles.Smoke(Fun.random_point_in_circle(self.pos, 16)))
    # Stunned status manager
    Fun.stunned_manager(self)


    # The cloaker is invisible when you don't look at it
    hide = True
    for p in entities["entities"]:
        if p.team == self.team: continue
        if Fun.check_point_in_circle(450 * 0.25, p.pos[0], p.pos[1], self.pos[0], self.pos[1]) or \
                Fun.check_point_in_cone(self.targeting_range, p.pos[0], p.pos[1], self.pos[0], self.pos[1],
                                        p.angle, self.targeting_angle):
            hide = False
            break
    if hide:
        self.status["Stealth"] = 2

        # if 300 < self.time % 800 < 800:
        alpha = 128 + 128 * math.sin(self.time//16)
        entities["UI particles"].append(
            Particles.GrowingSquareTransparent((self.pos[0] - 2, self.pos[1] - 3, 1, 1), Fun.GREEN, [0, 0], 12, alpha))
        entities["UI particles"].append(
            Particles.GrowingSquareTransparent((self.pos[0] + 2, self.pos[1] - 3, 1, 1), Fun.GREEN, [0, 0], 12, alpha))
        # if random.random() < 0.01:
        #     for x in range(3):
        #         entities["particles"].append(Particles.Smoke(Fun.move_with_vel_angle(
        #             self.pos, random.random() * 16, random.random() * 360)))

    return target, target_angle


def enemy_input_nest_flamer(self, entities,  level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, original_target, target_angle = entity_target_detection(self, entities, level)
    original_target = target

    self.input = Fun.get_default_inputs()

    if target:
        self.angle = Fun.angle_between(target, self.pos)
        # modify position of target for some ia types

        # Goes in front
        target = [original_target[0] - self.weapon.range / 5 * math.cos(target_angle * math.pi / 180),
                  original_target[1] - self.weapon.range / 5 * math.sin(target_angle * math.pi / 180)]

        og_dist = Fun.distance_between(original_target, self.pos)
        range_target = og_dist > self.weapon.range * 0.65
        if range_target:
            self.input["Right"] = self.pos[0] < target[0]
            self.input["Left"] = self.pos[0] > target[0]
            self.input["Down"] = self.pos[1] < target[1]
            self.input["Up"] = self.pos[1] > target[1]

        if og_dist < self.weapon.range * 0.3:
            self.input = {"Up": self.pos[1] < target[1], "Right": self.pos[0] > target[0],
                          "Left": self.pos[0] < target[0], "Down": self.pos[1] > target[1], "Dash": False,
                          "Shoot": False, "Alt fire": False, "Reload": False,
            "Interact": False, "Skill 1": False, "Skill 2": False,
            "Order Hold": False, "Order Follow": False, "Order Attack": False, "Order Act Free": False}

        # Check if something is in range
        if random.randint(0, self.weapon.fire_rate) == 0 and Fun.check_point_in_circle(
                self.weapon.range * 0.8, self.pos[0], self.pos[1], original_target[0], original_target[1]):
            self.input["Shoot"] = True

        # self.input["Alt fire"] = random.random() < 0.7 and self.weapon.ammo in [
        #     round(self.weapon.max_ammo * 0.25), round(self.weapon.max_ammo * 0.75)
        # ]
    self.input["Reload"] = self.weapon.ammo == 0
    formation_target = nest_formation_manager(self, entities,  level)

    if formation_target:
        self.input = {"Up": self.pos[1] > formation_target[1], "Right": self.pos[0] < formation_target[0],
                      "Left": self.pos[0] > formation_target[0], "Down": self.pos[1] < formation_target[1],
                      "Dash": False,
                      "Shoot": self.input["Shoot"],
                      "Alt fire": self.input["Alt fire"], "Reload": False,
            "Interact": False, "Skill 1": False, "Skill 2": False,
            "Order Hold": False, "Order Follow": False, "Order Attack": False, "Order Act Free": False}

    if not self.cutscene_mode:
        if dodging(self, entities, "bullets", search_range=32, bullet_minimum=1, random_chance=(3, 0),
                   dodge_angles=(60, 120), dodge_vel=10, invulnerability_time=5):
            for x in range(3):
                entities["particles"].append(Particles.Smoke(Fun.random_point_in_circle(self.pos, 16)))
    # Stunned status manager
    Fun.stunned_manager(self)


    return target, target_angle


def enemy_input_nest_demolisher(self, entities,  level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, original_target, target_angle = entity_target_detection(self, entities, level)
    original_target = target

    self.input = Fun.get_default_inputs()

    if target:
        self.angle = Fun.angle_between(target, self.pos)
        # modify position of target for some ia types

        # Goes in front
        target = [original_target[0] - self.weapon.range / 5 * math.cos(target_angle * math.pi / 180),
                  original_target[1] - self.weapon.range / 5 * math.sin(target_angle * math.pi / 180)]

        og_dist = Fun.distance_between(original_target, self.pos)
        range_target = og_dist > self.weapon.range * 0.65
        if range_target:
            self.input["Right"] = self.pos[0] < target[0]
            self.input["Left"] = self.pos[0] > target[0]
            self.input["Down"] = self.pos[1] < target[1]
            self.input["Up"] = self.pos[1] > target[1]

        if og_dist < self.weapon.range * 0.3:
            self.input = {"Up": self.pos[1] < target[1], "Right": self.pos[0] > target[0],
                          "Left": self.pos[0] < target[0], "Down": self.pos[1] > target[1], "Dash": False,
                          "Shoot": False, "Alt fire": False, "Reload": False,
            "Interact": False, "Skill 1": False, "Skill 2": False,
            "Order Hold": False, "Order Follow": False, "Order Attack": False, "Order Act Free": False}

        # Check if something is in range
        if random.randint(0, self.weapon.fire_rate) == 0 and Fun.check_point_in_circle(
                self.weapon.range * 0.8, self.pos[0], self.pos[1], original_target[0], original_target[1]):
            self.input["Shoot"] = True

        self.input["Alt fire"] = random.random() < 0.7 and self.weapon.ammo in [
            round(self.weapon.max_ammo * 0.25), round(self.weapon.max_ammo * 0.75)
        ]
    self.input["Reload"] = self.weapon.ammo == 0
    formation_target = nest_formation_manager(self, entities,  level)

    if formation_target:
        self.input = {"Up": self.pos[1] > formation_target[1], "Right": self.pos[0] < formation_target[0],
                      "Left": self.pos[0] > formation_target[0], "Down": self.pos[1] < formation_target[1],
                      "Dash": False,
                      "Shoot": self.input["Shoot"],
                      "Alt fire": self.input["Alt fire"], "Reload": False,
            "Interact": False, "Skill 1": False, "Skill 2": False,
            "Order Hold": False, "Order Follow": False, "Order Attack": False, "Order Act Free": False}

    if not self.cutscene_mode:
        if dodging(self, entities, "bullets", search_range=32, bullet_minimum=1, random_chance=(3, 0),
                   dodge_angles=(60, 120), dodge_vel=10, invulnerability_time=5):
            for x in range(3):
                entities["particles"].append(Particles.Smoke(Fun.random_point_in_circle(self.pos, 16)))
    # Stunned status manager
    Fun.stunned_manager(self)


    return target, target_angle


def enemy_input_nest_bunker(self, entities,  level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, original_target, target_angle = entity_target_detection(self, entities, level)
    original_target = target

    self.input = Fun.get_default_inputs()
    # valid_enemies = {"enemies": []}
    #     if self.pos != valid_enemy.pos:
    #         valid_enemies["enemies"].append(valid_enemy)
    # buff_target = Fun.find_closest_in_circle(self, valid_enemies, self.targeting_range, "enemies")
    buff_target = []
    for e in entities["entities"]:
        if e.team != self.team: continue
        if 0 < Fun.distance_between(e.pos, self.pos) < 32:
            self.input["Right"] = self.pos[0] > e.pos[0]
            self.input["Left"] = self.pos[0] < e.pos[0]
            self.input["Down"] = self.pos[1] > e.pos[1]
            self.input["Up"] = self.pos[1] < e.pos[1]
            break
    if target:
        self.angle = Fun.angle_between(target, self.pos)
        # modify position of target for some ia types

        # Goes in front
        target = [original_target[0] - self.weapon.range / 5 * math.cos(target_angle * math.pi / 180),
                  original_target[1] - self.weapon.range / 5 * math.sin(target_angle * math.pi / 180)]

        og_dist = Fun.distance_between(original_target, self.pos)
        # range_target = og_dist > self.weapon.range * 0.65
        # if range_target:
        #     self.input["Right"] = self.pos[0] < target[0]
        #     self.input["Left"] = self.pos[0] > target[0]
        #     self.input["Down"] = self.pos[1] < target[1]
        #     self.input["Up"] = self.pos[1] > target[1]

        if og_dist < self.weapon.range * 0.3:
            self.input = {"Up": self.pos[1] < target[1], "Right": self.pos[0] > target[0],
                          "Left": self.pos[0] < target[0], "Down": self.pos[1] > target[1], "Dash": False,
                          "Shoot": False, "Alt fire": False, "Reload": False,
            "Interact": False, "Skill 1": False, "Skill 2": False,
            "Order Hold": False, "Order Follow": False, "Order Attack": False, "Order Act Free": False}

        # Check if something is in range
        elif random.randint(0, self.weapon.fire_rate) == 0 and Fun.check_point_in_circle(
                self.weapon.range * 0.8, self.pos[0], self.pos[1], original_target[0], original_target[1]):
            self.input = {"Up": False, "Right": False,
                          "Left": False, "Down": False, "Dash": False,
                          "Shoot": True, "Alt fire": False, "Reload": False,
            "Interact": False, "Skill 1": False, "Skill 2": False,
            "Order Hold": False, "Order Follow": False, "Order Attack": False, "Order Act Free": False}

        # self.input["Alt fire"] = random.random() < 0.7 and self.weapon.ammo in [
        #     round(self.weapon.max_ammo * 0.25), round(self.weapon.max_ammo * 0.75)
        # ]
    self.input["Reload"] = self.weapon.ammo == 0
    # elif buff_target:
        # buff_target_angle = Fun.angle_between(buff_target, self.pos)
        # original_buff_target = [buff_target[0], buff_target[1]]
        # modify position of target for some ia types

        # self.input["Right"] = self.pos[0] < buff_target[0]
        # self.input["Left"] = self.pos[0] > buff_target[0]
        # self.input["Down"] = self.pos[1] < buff_target[1]
        # self.input["Up"] = self.pos[1] > buff_target[1]

    # formation_target = nest_formation_manager(self, entities,  level)

    # if formation_target:
    #     self.input = {"Up": self.pos[1] > formation_target[1], "Right": self.pos[0] < formation_target[0],
    #                   "Left": self.pos[0] > formation_target[0], "Down": self.pos[1] < formation_target[1],
    #                   "Dash": False,
    #                   "Shoot": self.input["Shoot"],
    #                   "Alt fire": self.input["Alt fire"]}

    # if not self.cutscene_mode:
    #     if dodging(self, entities, bullets, search_range=32, bullet_minimum=1, random_chance=(3, 0),
    #                dodge_angles=(60, 120), dodge_vel=10, invulnerability_time=5):
    #         for x in range(3):
    #             entities["particles"].append(Particles.Smoke(Fun.random_point_in_circle(self.pos, 16)))
    # Stunned status manager
    Fun.stunned_manager(self)


    return target, target_angle


# Anomalies
def enemy_input_monolith(self, entities,  level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, original_target, target_angle = entity_target_detection(self, entities, level)
    original_target = target

    self.input = Fun.get_default_inputs()

    if target:
        self.angle = Fun.angle_between(target, self.pos)

        # Check if something is in range
        self.input["Shoot"] = True
        self.status["Stealth"] = 2

    # Stunned status manager
    # Fun.stunned_manager(self)
    self.status["Stunned"] = 0


    return target, target_angle


def enemy_input_eye(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, original_target, target_angle = entity_target_detection(self, entities, level)
    original_target = target

    self.input = Fun.get_default_inputs()

    if target:
        self.angle = Fun.angle_between(target, self.pos)

        # Check if something is in range
        self.input["Shoot"] = True
        self.weapon.bullet_info = [2 + 3 * random.random(), 450, 5, 10, {"Colour": Fun.LIGHT_RED, "Bullet mod":
            [{"angle": "Player", "Interval": [25, 40, 70][random.randint(0, 2)]}]}]

    # Stunned status manager
    # Fun.stunned_manager(self)
    self.status["Stunned"] = 0


    return target, target_angle


def enemy_input_void(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, original_target, target_angle = entity_target_detection(self, entities, level)
    original_target = target

    self.input = Fun.get_default_inputs()

    if target:
        self.angle = Fun.angle_between(target, self.pos)

        # Check if something is in range
        self.input["Shoot"] = self.no_shoot_state == 0 and random.random() < 0.05

    # Stunned status manager
    # Fun.stunned_manager(self)
    self.status["Stunned"] = 0


    colours = [Fun.DARK_GREEN, Fun.DARK_GREEN_ALT, Fun.DARK, Fun.DARKER_GREEN]
    for x in range(2):
        pos = Fun.random_point_in_circle(self.pos, 12)
        colour = colours[random.randint(0, len(colours) - 1)]
        entities["particles"].append(Particles.FireParticle(pos, colour=colour))
    return target, target_angle


def enemy_input_slime(self, entities,level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, original_target, target_angle = entity_target_detection(self, entities, level)
    original_target = target

    self.input = Fun.get_default_inputs()

    if target:
        self.angle = Fun.angle_between(target, self.pos)
        # Make it move toward the player
        self.input["Right"] = self.pos[0] < target[0]
        self.input["Left"] = self.pos[0] > target[0]
        self.input["Down"] = self.pos[1] < target[1]
        self.input["Up"] = self.pos[1] > target[1]


    for e in entities["entities"]:
        if e.team != self.team: continue
        if 0 < Fun.distance_between(e.pos, self.pos) < 32:
            self.input["Right"] = self.pos[0] > e.pos[0]
            self.input["Left"] = self.pos[0] < e.pos[0]
            self.input["Down"] = self.pos[1] > e.pos[1]
            self.input["Up"] = self.pos[1] < e.pos[1]
            break

    for collision in entities["entities"]:
        if collision.team == self.team: continue
        if self.collision_box.colliderect(collision.collision_box):
            Fun.damage_calculation(collision, round(12 * self.thiccness / 40), "Melee")
    # Stunned status manager
    # Fun.stunned_manager(self)
    self.status["Stunned"] = 0


    return target, target_angle


def enemy_input_snake(self, entities, level):
    # Input functions are the IA for an enemy
    # better targeting system
    target, original_target, target_angle = entity_target_detection(self, entities, level)
    original_target = target

    self.input = Fun.get_default_inputs()

    self.free_var["Pos history"].append([self.pos[0], self.pos[1]])
    if len(self.free_var["Pos history"]) > 90:
        self.free_var["Pos history"].pop(0)

    if target:
        self.angle = Fun.angle_between(target, self.pos)
        # modify position of target for some ia types

        if self.time % 120 == (30 * self.free_var["Delay mod"]) % 120:     # if self.time % 120 == 0:
            self.free_var["Move Angle"] = self.angle

        # Check if something is in range
        if random.randint(0, self.weapon.fire_rate) == 0 and Fun.check_point_in_circle(
                self.weapon.range * 0.8, self.pos[0], self.pos[1], original_target[0], original_target[1]):
            self.input["Shoot"] = True

    angle = self.free_var["Move Angle"]
    follow_this_guy = self.free_var["Delay mod"] - 1
    following = False
    for e in entities["entities"]:
        if e.team != self.team: continue
        if "Delay mod" in e.free_var:
            if e.name == f"Snake {follow_this_guy}":
                pos = e.free_var["Pos history"][0]
                self.pos = [pos[0], pos[1]]
                following = True
                break

    if not following:
        self.vel = Fun.move_with_vel_angle([0, 0], self.speed, angle)

    # Stunned status manager
    Fun.stunned_manager(self)


    return target, target_angle


# |THR-1's Assault - Allies|--------------------------------------------------------------------------------------------
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


APC_MOVE_TO_POINT = { # Add something to choose between weapons later
    "Fortress": fortress_move_toward_point,
    "Sand Buggy": buggy_move_toward_point
}

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
