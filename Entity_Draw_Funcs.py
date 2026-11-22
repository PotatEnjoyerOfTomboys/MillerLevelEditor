import pygame as pg
import math
import Fun


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
                   drawing_pos, origin, 180 - self.aim_angle + angle_to_add + self.draw_angle + self.weapon_draw_angle)


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


def player_draw_advanced_movement(self, WIN, scrolling):
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
    self.draw_player_rotate(scrolling, WIN, player_direction, 360 * self.roll_time / self.roll_timer * 2)
    # Stamina bar
    x_pos = self.pos[0] - 16 + scrolling[0]
    y_pos = (self.pos[1] + 10) + self.thiccness // 2 + scrolling[1] - 4

    width = 32
    health_height = 4
    armour_height = 2

    # Draws the health bar
    col = Fun.ORANGE
    if self.stamina_recovery_time > 0:
        col = Fun.DARK_ORANGE
    pg.draw.rect(WIN, Fun.DARK, (x_pos, y_pos, width, health_height))
    pg.draw.rect(WIN, col, (x_pos, y_pos, width * (self.stamina / self.max_stamina), health_height))


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


def commie_bot_tank_draw(self, WIN, scrolling):
    # SPRITE_COMMIE_BOT_TANK_HULL = get_sprite_stack_list(get_image('Sprites/Vehicles/CommieBot.Tank - Hull.png'), 21)
    # SPRITE_COMMIE_BOT_TANK_TURRET
    Fun.draw_spritestack(WIN, Fun.SPRITE_COMMIE_BOT_TANK_HULL, [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]],
                         self.angle + 90, height_diff=0.5)
    # 226
    # angle = 226 + self.free_var["Move angle"]
    pos = [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1] - 4]
    pos = Fun.move_with_vel_angle(pos, 2, self.angle)
    Fun.draw_spritestack(WIN, Fun.SPRITE_COMMIE_BOT_TANK_TURRET, pos, self.aim_angle + 90, height_diff=0.5)


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


def enemy_draw_gang_moped(self, WIN, scrolling):
    # That one has animations
    if self.status["Stealth"] > 0:
        return
    # Draw the enemy

    WIN.blit(Fun.ENTITY_SHADOW, (self.pos[0]-16 + scrolling[0], self.pos[1] + 11 + scrolling[1]), special_flags=pg.BLEND_RGBA_SUB)
    frame_to_get = 0
    Fun.draw_spritestack(WIN, Fun.SPRITE_GANG_MOPED, [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]+10],
                         self.free_var["Move angle"] + 90, height_diff=0.75)

    # Draw the gun
    angle_to_add = 0
    if self.reloading:
        angle_to_add = (360 / self.weapon.reload_time) * self.no_shoot_state

    Fun.blitRotate(WIN, pg.transform.flip(self.weapon.sprite, True, -90 < self.aim_angle < 90),
                   Fun.move_with_vel_angle([self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]], 4,
                                           self.aim_angle),
                   [0, 0], 180 - self.aim_angle + angle_to_add)
    #


def enemy_draw_slime(self, WIN, scrolling):
    if self.status["Stealth"] > 0:
        return
    # Draw the enemy
    enemy_direction = Fun.get_entity_direction(self.angle)

    sprite_drawn = self.sprites[enemy_direction]["Walk"][0]
    sprite_drawn = pg.transform.scale(sprite_drawn, [self.thiccness, self.thiccness])
    WIN.blit(sprite_drawn, (self.pos[0] - sprite_drawn.get_width() // 2 + scrolling[0],
                            self.pos[1] - sprite_drawn.get_height() // 2 + scrolling[1]))


    if self.draw_targeting_range > 0:
        # Detection cone
        pg.draw.line(WIN, Fun.GREEN, [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]],
                     [self.pos[0] - self.targeting_range * math.cos(
                         (self.angle - self.targeting_angle) * math.pi / 180) +
                      scrolling[0],
                      self.pos[1] - self.targeting_range * math.sin(
                          (self.angle - self.targeting_angle) * math.pi / 180) +
                      scrolling[1]])
        pg.draw.line(WIN, Fun.GREEN, [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]],
                     [self.pos[0] - self.targeting_range * math.cos(
                         (self.angle + self.targeting_angle) * math.pi / 180) +
                      scrolling[0],
                      self.pos[1] - self.targeting_range * math.sin(
                          (self.angle + self.targeting_angle) * math.pi / 180) +
                      scrolling[1]])
        # Circle of detection
        pg.draw.circle(WIN, Fun.GREEN, [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]],
                       self.targeting_range // 10, 1)
        self.draw_targeting_range -= 1
    #


# Bosses

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



def hover_tank_draw(self, WIN, scrolling):
    h_mod = 0.75
    Fun.draw_spritestack(WIN, Fun.SPRITE_HOVER_TANK_CHASSIS, [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1]],
                         self.free_var["Move angle"] + 90, height_diff=h_mod)
    Fun.draw_spritestack(WIN, Fun.SPRITE_HOVER_TANK_TURRET, [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1] - 17 * h_mod],
                         self.aim_angle + 90, height_diff=h_mod)
    Fun.draw_spritestack(WIN, Fun.SPRITE_HOVER_TANK_GUN, [self.pos[0] + scrolling[0], self.pos[1] + scrolling[1] - 24 * h_mod],
                         self.free_var["Machine Gun Angle"] + 90, height_diff=h_mod)


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



RIGEL_SEGMENT = Fun.get_image('Sprites/Segment.png')
RIGEL_SEGMENT_WIDTH = RIGEL_SEGMENT.get_width()
RIGEL_SEGMENT_HEIGHT = RIGEL_SEGMENT.get_height()
RIGEL_SEGMENT_ORIGIN = [RIGEL_SEGMENT_WIDTH * 0.5, RIGEL_SEGMENT_HEIGHT * 0]