from math import radians

import pygame as pg
import math

import Fun


# async might be usable for the render functions


# Render keeps all the draw functions used in normal gameplay
# Check out 60 30 10 rule

# |UI things|-----------------------------------------------------------------------------------------------------------
def new_draw_teammate_display(surface_to_draw, teammate, pos, w):
    font = Fun.FONTS["sma"]
    x, y, width, height = 2, 2, 630//4 * 0.9, 21.6 * 0.9

    surf = pg.Surface((width+4, height+4))
    surf.fill(Fun.UI_COLOUR_NEW_BACKDROP)
    pg.draw.rect(surf, Fun.UI_COLOUR_NEW_BACKGROUND, [2, 2, width, height])

    skill_width, skill_height = width * 0.125, height * 0.5

    y_mid = height // 2
    max_length = width * 0.75

    # Ammo
    text_colour = Fun.WHITE
    ammo_colour = Fun.AMBER
    if teammate.weapon.ammo <= teammate.weapon.max_ammo // 8:
        ammo_colour = Fun.RED
    elif teammate.weapon.ammo <= teammate.weapon.max_ammo // 2:
        ammo_colour = Fun.ORANGE

    # |Draws the health bar and armour|---------------------------------------------------------------------------------
    pg.draw.rect(surf, Fun.DARKER_RED, (x, y, width, skill_height))
    pg.draw.rect(surf, Fun.MED_RED, (x, y, teammate.health * width / teammate.max_health, skill_height))
    pg.draw.rect(surf, Fun.MED_GREEN, (x, y, teammate.armour * width / teammate.max_armour, skill_height//3))
    surf.blit(font.render(f"{teammate.name}", True, text_colour), (x, y))

    # Weapon stuff
    pg.draw.rect(surf, Fun.DARK, (x, y + y_mid, max_length, skill_height))
    pg.draw.rect(surf, ammo_colour, (x, y + y_mid, teammate.weapon.ammo * max_length / teammate.weapon.max_ammo,
                                                skill_height))
    margin = 1
    surf.blit(font.render(f"{teammate.weapon.ammo}", True, text_colour), (x, y + y_mid + margin))
    surf.blit(teammate.weapon.ammo_sprite, (x + 20, y + y_mid + margin))
    surf.blit(font.render(f"{teammate.weapon.ammo_pool}", True, text_colour), (x + 32 + teammate.weapon.ammo_sprite.get_width(), y + y_mid + margin))

    # Skill bar recharge
    for count, s in enumerate(teammate.skills):
        x_pos = x + width * 0.75 + count * skill_width
        height_charge = s.recharge * skill_height / s.recharge_max

        pg.draw.rect(surf, (0, 0, 255), (x_pos, y + y_mid, skill_width, height_charge))

    surface_to_draw.blit(pg.transform.scale_by(surf, w/width), pos)


def draw_bottom_health_bar(entity, surface_to_draw, round_scrolling):
    x_pos = entity.pos[0] - 16 + round_scrolling[0]
    y_pos = (entity.pos[1] + 10) + entity.thiccness // 2 + round_scrolling[1]

    width = 32
    health_height = 4
    armour_height = 2

    # Draws the health bar
    pg.draw.rect(surface_to_draw, Fun.RED, (x_pos, y_pos, width * (entity.health / entity.max_health), health_height))
    try:
        pg.draw.rect(surface_to_draw, Fun.GREEN, (x_pos, y_pos, width * (entity.armour / entity.max_armour), armour_height))
    except ZeroDivisionError:
        pass
    for count, skill in enumerate(entity.skills):
        val = pg.math.clamp(255 * skill.recharge / skill.recharge_max, 0, 255)
        mod = 0
        if skill.active:
            mod = val
        pg.draw.rect(surface_to_draw, (mod, mod, val),
                     (x_pos + 16 * count, y_pos+health_height, 16, 2))
    if entity.status["Stunned"] > 0:
        sprite = Fun.SPRITE_STUNNED[(entity.status["Stunned"] // 6) % 2]
        surface_to_draw.blit(sprite, [entity.pos[0] + round_scrolling[0] - sprite.get_width() / 2,
                                      entity.pos[1] - 15 + round_scrolling[1]])


# |General Draw Function|-----------------------------------------------------------------------------------------------
def draw(WIN, CLOCK, time_passed, scrolling, scrolling_target, level, entities, scrolling_mod=1):
    player = entities["entities"][0]
    # win_width, win_height = WIN.get_size()

    actual_win_width, actual_win_height = WIN.get_size()
    win_width, win_height = Fun.FRAME_MAX_SIZE
    camera_rect = pg.Rect(-scrolling[0], -scrolling[1], win_width, win_height)
    frame = pg.Surface(Fun.FRAME_MAX_SIZE)
    # surface_to_draw = WIN
    surface_to_draw = frame
    WIN.fill((0, 0, 0))
    temp_ui_font = Fun.create_temp_font_1(win_height, font_name="Sprites/JetBrainsMono-SemiBold.ttf")
    # Scrolling
    Fun.scrolling_manager(scrolling, scrolling_target, win_width, win_height, scrolling_speed=3.75*scrolling_mod)
    # Limit scrolling when needed
    # if "Limit scrolling" in level:
    #     if scrolling[0] > level["Limit scrolling"][0][1]:
    #         scrolling[0] = level["Limit scrolling"][0][1]
    #     elif scrolling[0] < level["Limit scrolling"][0][0]:
    #         scrolling[0] = level["Limit scrolling"][0][0]
    #     if scrolling[1] < level["Limit scrolling"][1][0]:
    #         scrolling[1] = level["Limit scrolling"][1][0]
    #     elif scrolling[1] > level["Limit scrolling"][1][1]:
    #         scrolling[1] = level["Limit scrolling"][1][1]

    round_scrolling = [round(scrolling[0]), round(scrolling[1])]
    # Draw level
    for wall in level["map"]:
        pg.draw.rect(surface_to_draw, Fun.WALL_COLOUR, [wall.left + round_scrolling[0],
                                                        wall.top + round_scrolling[1],
                                                        wall.width,
                                                        wall.height])
    # Draw map
    tiles = level["rendering"]["Tile set"] # = {"Wall": TILE_SET_SEWER_FLOOR, "Floor": TILE_SET_SEWER_WALL}

    for segment in level["rendering"]["Segments"]:
        if camera_rect.colliderect(segment["Rect"]):
            draw_multiple_rects(surface_to_draw, segment["Walls"], round_scrolling, tiles["Wall"], mode="All")
            draw_multiple_rects(surface_to_draw, segment["Floor"], round_scrolling, tiles["Floor"], mode="All")

    # Draw connections between waypoints
    # for w in level["pathfinding"]['connections']:
    #     p1 = level["pathfinding"]['points'][w]
    #     for c in level["pathfinding"]['connections'][w]:
    #         p2 = level["pathfinding"]['points'][c]
    #         pg.draw.line(surface_to_draw, Fun.YELLOW,
    #                      [p1[0] + round_scrolling[0], p1[1] + round_scrolling[1]],
    #                      [p2[0] + round_scrolling[0], p2[1] + round_scrolling[1]], 3)
    players = []
    for p_diddy in range(4):
        try:
            e  = entities["entities"][p_diddy]
        except IndexError:
            break

        if e.team == "Players":
            players.append(e)

    if 'APC path' in level['free var']:
        if level['free var']['APC path']:
            apc = None
            for p in players:
                if "IS AN APC" in p.free_var:
                    apc = p
                    break
            s_pos = apc.pos
            for p in level['free var']['APC path']:
                pg.draw.line(surface_to_draw, Fun.RED,
                              [s_pos[0] + round_scrolling[0], s_pos[1] + round_scrolling[1]],
                              [p[0] + round_scrolling[0], p[1] + round_scrolling[1]], 3)
                s_pos = p

    for particle in entities["background particles"]:
        particle.draw(surface_to_draw, round_scrolling)

    # Draw the entities
    # Only draw enemies when they are within targeting range for players

    # Won't DO: Optimize this pile of shit
    for e in entities["entities"]:
        # Skip checks if entity is a player or an enemy that has to be drawn no matter what
        if e in players or e.status["Visible"] > 0 or e.force_draw:
            e.draw(surface_to_draw, round_scrolling)
            draw_bottom_health_bar(e, surface_to_draw, round_scrolling)
            continue
        # Skip hidden enemies
        if e.status["Stealth"] > 0: continue
        # Only draw enemies who can be seen by a player
        for ee in players:
            # Get stealth range modifier
            detection_modifier = pg.math.clamp(e.stealth_mod * ee.stealth_counter, -20, 1)
            if not (Fun.distance_between(e.pos, ee.pos) < ee.targeting_range // 10 * detection_modifier or
                    Fun.check_point_in_cone(
                        ee.targeting_range * detection_modifier, ee.pos[0], ee.pos[1],
                        e.pos[0], e.pos[1],
                        ee.angle, ee.targeting_angle)):
                continue
            if Fun.wall_between(e.pos, ee.pos, level): continue
            e.draw(surface_to_draw, round_scrolling)
            draw_bottom_health_bar(e, surface_to_draw, round_scrolling)
            break

    # Draw the items
    for item_to_draw in entities["items"]:
        item_to_draw.draw(surface_to_draw, round_scrolling)

    # Draw the bullets
    for bullet_to_draw in entities["bullets"]:
        bullet_to_draw.draw(surface_to_draw, round_scrolling)

    # Handle particles
    for particle in entities["particles"]:
        particle.draw(surface_to_draw, round_scrolling)

    # Shadows
    background = Fun.BLACK
    light = Fun.WHITE
    surface_shadow = pg.Surface((win_width, win_height))
    surface_shadow.fill(background)
    for p_fov in players:
        pg.draw.circle(surface_shadow, light,
                       [p_fov.pos[0] + round_scrolling[0], p_fov.pos[1] + round_scrolling[1]],
                       p_fov.targeting_range / 10)

        angle_1 = radians(p_fov.angle * -1 - p_fov.targeting_angle + 180)  # rad
        angle_2 = radians(p_fov.angle * -1 + p_fov.targeting_angle + 180)
        half_range = p_fov.targeting_range / 2
        arc_rect = (p_fov.pos[0] - half_range + round_scrolling[0], p_fov.pos[1] - half_range + round_scrolling[1], p_fov.targeting_range, p_fov.targeting_range)
        pg.draw.arc(surface_shadow, light, arc_rect, angle_1, angle_2, 100000)

    img_copy = pg.Surface(surface_shadow.get_size())
    img_copy.fill(Fun.WHITE)
    surface_shadow.set_colorkey(Fun.WHITE)
    img_copy.blit(surface_shadow, (0, 0))
    surface_shadow = img_copy
    surface_shadow.set_colorkey(Fun.WHITE)
    surface_shadow.set_alpha(32)
    surface_to_draw.blit(surface_shadow, (0, 0))

    # |UI|--------------------------------------------------------------------------------------------------------------
    # Status bars
    # All of this is rendered below the player, allies and enemies
    boss_count = 0
    teammates_count = 0

    h = Fun.FRAME_MAX_SIZE[1] / 20.8
    w = Fun.FRAME_MAX_SIZE[0] // 4
    for p in players:
        # Health
        # [583, 416]
        h = Fun.FRAME_MAX_SIZE[1]/20.8
        w = Fun.FRAME_MAX_SIZE[0]//4   # 100
        # draw_teammate_display(
        #     surface_to_draw, p, [
         #         0 + w * teammates_count + 2 * teammates_count, 2, w, h
        #     ], temp_ui_font)
        new_draw_teammate_display(
            surface_to_draw, p, [
                0 + w * teammates_count + 2 * teammates_count, 2
            ], w)
        teammates_count += 1

        # Universal status bars
        pg.draw.rect(surface_to_draw, Fun.WHITE, (p.pos[0] - p.no_shoot_state // 4 + round_scrolling[0],
                                                      p.pos[1] + p.thiccness + 4 + round_scrolling[1],
                                                      p.no_shoot_state // 2, 2))
        mod = 6
        for status in p.status:
            if p.status[status] > 0:
                pg.draw.rect(surface_to_draw, Fun.STATUS_EFFECT_COLOUR[status],
                                 (p.pos[0] - p.status[status] // 4 + round_scrolling[0],
                                  p.pos[1] + p.thiccness + mod + round_scrolling[1],
                                  p.status[status] // 2, 2))
                mod += 2

    # Add an indicator that shows the enemies position
    # if "Is VIP" in e.free_var:
    for indicator in entities["entities"]:
            # Check if the enemy is far enough
        if math.hypot(indicator.pos[0] - player.pos[0], indicator.pos[1] - player.pos[1]) > win_height // 2:
            colour = Fun.RED
            if indicator.team == "Players":
                colour = Fun.BLUE
            elif "Is VIP" in indicator.free_var:
                colour = Fun.AMBER_LIGHT

                # Get angle
            indicator_angle = Fun.angle_between(indicator.pos, player.pos)
                # Draw a small rectangle
            pg.draw.rect(surface_to_draw, colour, (
                    (win_width / 2 - 2) - 150 * math.cos(indicator_angle * math.pi / 180),
                    (win_height / 2 - 2) - 150 * math.sin(indicator_angle * math.pi / 180),
                    4, 4)
                             )

    # Draw mini map
    map_surface = pg.Surface((64, 64))
    # pg.draw.rect(surface_to_draw, Fun.UI_COLOUR_NEW_BACKGROUND, [frame.get_width() - 112, 0, 112, 112])
    map_surface.fill(Fun.UI_COLOUR_NEW_BACKGROUND)
    z_mod = 16
    pos = scrolling_target
    for wall in level["map"]:
        pg.draw.rect(map_surface, Fun.UI_COLOUR_NEW_BACKDROP, [wall.left // z_mod + pos[0] // z_mod + 16,#  + x_mod,
                                                       wall.top // z_mod + pos[1] // z_mod  + 20,# + y_mod,
                                                     wall.width // z_mod,
                                                      wall.height // z_mod])
    pg.draw.rect(map_surface, Fun.AMBER_LIGHT, [32, 32, 2, 2])
    map_surface.set_alpha(196)
    surface_to_draw.blit(map_surface, [16, win_height-64-16])

    # Render any
    for particle in entities["UI particles"]:
        particle.draw(surface_to_draw, round_scrolling)

    # Scale the slide
    Fun.scale_render(WIN, surface_to_draw, CLOCK)


def draw_multiple_rects(WIN, rects, round_scrolling, tile_set, mode="All", modified_index=(1, 2, 3, 4, 0, 5, 6, 7, 8)):
    for t in rects:
        Fun.draw_environment_from_tile_set(WIN, (t[0], t[1]), t[2], t[3],
                                           round_scrolling, mode, tile_set=tile_set, modified_index=modified_index)


