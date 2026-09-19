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


# |General Draw Function|-----------------------------------------------------------------------------------------------
def draw(WIN, CLOCK, time_passed, scrolling, scrolling_target, level, entities, scrolling_mod=1):

    player = entities["entities"][0]
    win_width, win_height = Fun.FRAME_MAX_SIZE
    camera_rect = pg.Rect(-scrolling[0], -scrolling[1], win_width, win_height)
    frame = pg.Surface(Fun.FRAME_MAX_SIZE)
    surface_to_draw = frame


    WIN.fill((0, 0, 0))

    # temp_ui_font = Fun.create_temp_font_1(win_height, font_name="Sprites/JetBrainsMono-SemiBold.ttf")
    # Scrolling
    Fun.scrolling_manager(scrolling, scrolling_target, win_width, win_height, scrolling_speed=3.75*scrolling_mod)
    round_scrolling = [round(scrolling[0]), round(scrolling[1])]

    # TODO: Implement scrolling limiter
    # if "Limit scrolling" in level:
    #     if scrolling[0] > level["Limit scrolling"][0][1]:
    #         scrolling[0] = level["Limit scrolling"][0][1]
    #     elif scrolling[0] < level["Limit scrolling"][0][0]:
    #         scrolling[0] = level["Limit scrolling"][0][0]
    #     if scrolling[1] < level["Limit scrolling"][1][0]:
    #         scrolling[1] = level["Limit scrolling"][1][0]
    #     elif scrolling[1] > level["Limit scrolling"][1][1]:
    #         scrolling[1] = level["Limit scrolling"][1][1]

    # Draw level
    for wall in level["map"]:
        pg.draw.rect(surface_to_draw, Fun.WALL_COLOUR, [wall.left + round_scrolling[0], wall.top + round_scrolling[1],
                                                        wall.width, wall.height])
    # Draw map
    tiles = level["rendering"]["Tile set"] # = {"Wall": TILE_SET_SEWER_FLOOR, "Floor": TILE_SET_SEWER_WALL}

    for segment in level["rendering"]["Segments"]:
        if camera_rect.colliderect(segment["Rect"]):
            for t in level["rendering"]["Tile set"]:
                if t not in segment:
                    continue
                draw_multiple_rects(surface_to_draw, segment[t], round_scrolling, tiles[t])

    for count, door in enumerate(level['door state']):
        if door:
            wall = level["map"][count]
            Fun.draw_transparent_rect(surface_to_draw, [wall.left + round_scrolling[0], wall.top + round_scrolling[1],
                                                        wall.width, wall.height], (255, 0, 255), 128)

    players = []
    for p_diddy in range(4):
        try:
            e  = entities["entities"][p_diddy]
        except IndexError:
            break

        if e.team == "Players":
            players.append(e)

    for particle in entities["background particles"]:
        particle.draw(surface_to_draw, round_scrolling)

    # Draw the entities and items
    render_list = entities["entities"] + entities["items"]
    for e in sorted(render_list, key=lambda  x: x.z):   # sorted makes sure that the ones with lowest y value goes first
        e.draw(surface_to_draw, round_scrolling, players, level)

    # Draw the bullets
    for bullet_to_draw in entities["bullets"]:
        bullet_to_draw.draw(surface_to_draw, round_scrolling)

    # Handle particles
    for particle in entities["particles"]:
        particle.draw(surface_to_draw, round_scrolling)

    # Shadows
    # Re-implement the old shadow system

    # FOV
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
    # All of this is rendered below the entities
    teammates_count = 0
    w = Fun.FRAME_MAX_SIZE[0] // 4
    for p in players:
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
                    4, 4))

    # Render any
    for particle in entities["UI particles"]:
        particle.draw(surface_to_draw, round_scrolling)

    # Scale the slide
    Fun.scale_render(WIN, surface_to_draw, CLOCK)


def draw_multiple_rects(WIN, rects, round_scrolling, tile_set, modified_index=(1, 2, 3, 4, 0, 5, 6, 7, 8)):
    for t in rects:
        draw_environment_from_tile_set(WIN, (t[0], t[1]), t[2], t[3], round_scrolling,
                                       tile_set=tile_set, modified_index=modified_index)


def draw_environment_from_tile_set(WIN, top_left_corner, width, height, scrolling,
                                   tile_set=Fun.TILE_SET_INDUSTRIAL_FLOOR, modified_index=(1, 2, 3, 4, 0, 5, 6, 7, 8)):
    # This function uses a tile set to render a rectangular area
    internal_width = round((width - Fun.TILES_SIZE * 2) // Fun.TILES_SIZE)

    if height > Fun.TILES_SIZE:
        # Draw the top layer
        # Draw the left corner
        WIN.blit(tile_set[modified_index[0]],
                     [top_left_corner[0] + scrolling[0],
                      top_left_corner[1] + scrolling[1]])
        # Draw the middle
        for x in range(internal_width):
            WIN.blit(tile_set[modified_index[1]],
                         [top_left_corner[0] + Fun.TILES_SIZE + (x * Fun.TILES_SIZE) + scrolling[0],
                          top_left_corner[1] + scrolling[1]])
        # Draw the right corner
        WIN.blit(tile_set[modified_index[2]],
                     [top_left_corner[0] + width - Fun.TILES_SIZE + scrolling[0],
                      top_left_corner[1] + scrolling[1]])

        # Draw the middle layers
        for y in range(round((height - Fun.TILES_SIZE * 2) // Fun.TILES_SIZE)):
            # Draw the left side
            WIN.blit(tile_set[modified_index[3]],
                         [top_left_corner[0] + scrolling[0],
                          top_left_corner[1] + Fun.TILES_SIZE + (y * Fun.TILES_SIZE) + scrolling[1]])
            # Draw the middle
            for x in range(internal_width):
                WIN.blit(tile_set[modified_index[4]],
                             [top_left_corner[0] + Fun.TILES_SIZE + (x * Fun.TILES_SIZE) + scrolling[0],
                              top_left_corner[1] + Fun.TILES_SIZE + (y * Fun.TILES_SIZE) + scrolling[1]])
            # Draw the right side
            WIN.blit(tile_set[modified_index[5]],
                         [top_left_corner[0] + width - Fun.TILES_SIZE + scrolling[0],
                          top_left_corner[1] + Fun.TILES_SIZE + (y * Fun.TILES_SIZE) + scrolling[1]])

    # Draws the bottom layer
    for x in range(internal_width):
        WIN.blit(tile_set[modified_index[7]],
                     [top_left_corner[0] + Fun.TILES_SIZE + (x * Fun.TILES_SIZE) + scrolling[0],
                      top_left_corner[1] + height - Fun.TILES_SIZE + scrolling[1]])
    # Draw the sides
    WIN.blit(tile_set[modified_index[6]],
                 [top_left_corner[0] + scrolling[0],
                  top_left_corner[1] + height - Fun.TILES_SIZE + scrolling[1]])
    WIN.blit(tile_set[modified_index[8]],
                 [top_left_corner[0] + width - Fun.TILES_SIZE + scrolling[0],
                  top_left_corner[1] + height - Fun.TILES_SIZE + scrolling[1]])

