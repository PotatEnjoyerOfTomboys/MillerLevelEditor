import pygame as pg
import os


import Fun
import Event
import Items
import Entity
import Main

# To add:
#   Option to resize
#   Weather effects

#   Sprint Dash Roll movement system

#   Test level from editor

#   Add NEST Agent character
#   Add Detective Agency character

#   Import old enemies
#   Support for animated tiles
#   More props
#   Shaders? https://pygame-shaders.readthedocs.io/en/latest/surface_shaders.html


EMPTY_MAP_DATA = {"map": [],
                  "doors": [],
                  'door state': [],
                  "rendering": {"Segments": [], "Tile set": {}},
                  "pathfinding": [],
                  "spawn point": [[5, 5, 1, 1]],
                  "size": [80*8, 56*8]
                  }
EMPTY_EVENT_DATA = {
    "name": "Unnamed level",
    "events": {},
    "free var": {},
    "Characters": ["Curtis"]
}
EMPTY_FRAME = pg.Surface((630, 450), pg.SRCALPHA)
ALL_TRIGGER_FUNC = []
for f in dir(Event):
    if "trigger_check_" in f:
        ALL_TRIGGER_FUNC.append(f)
DEFAULT_EVENT_ACTION_INFO = {
    "spawn": {"Class": "Entity", "Pos": [0, 0, 1, 1], "Angle": 0, "ID": "", "Team": "Enemies"},
    "despawn": {"Method": "Soft", "Conditions": []},
    "door": {"Door ID": 0, "Door state": True},
    "sound": {"Action": "Play", "Audio": "Silence"},
    "level end": {"End level state": "win"},
    "cutscene": {},  # AAAAAAAAAAAAAAAAAAAA
    "radio": {},  # AAAAAAAAAAAAAAAAAAAA
    "teleport": {"Pos": [0, 0, 1, 1]},
    "character": {"Character": "Curtis", "Carry over health": True},
    "free var": {"Target free var": "", "Operation": "Addition", "Value": 0},
}
ALL_EVENT_ACTION_TYPE = [t for t in DEFAULT_EVENT_ACTION_INFO]

PLAYABLE_CHARACTERS = [
    "Curtis",           # Advanced Movement. Gunsmith.
    "Lawrence",         # Advanced Movement. Get a new mechanic with oil for his fire attacks.
                        # Fire attacks uses oil. Hitting with a gun attack restores oil. If a fire attacked used oil. It will ne stronger
    "Mark",
    "Vivianne",         # Advanced Movement. Gunsmith.

    "Lord",             #
    "Emperor",          # Advanced Movement.
    "Wizard",           #
    "Sovereign",        #
    "Duke",             # Advanced Movement.
    "Jester",           #
    "Condor",           #

    # NEST agent        # Advanced Movement.
    # Has spamable gas grenades
    # Skills
    # Cloak & night vision mode.
    # For a time, becomes invisible, gains night vision but become restricted to a knife. Knife deals lots of damage
    # <Skill 2>

    # Detective Agency  # Switch between John, Makoto and Flint. Each have a skill, an effect when they are switched too and at least 1 weapon.
                        # Health is shared between all 3
                            # John      WPN: Typewriter SMG  Skill:                                  Switch: .
                            # Makoto    WPN: Iguana's Tail   Skill: Lunges with claws. Big damage.   Switch: .
                            # Flint     WPN: Katana          Skill: Mag dumps pistol and throws it.  Switch: .

    # |Vertical movement version of all characters.|--------------------------------------------------------------------
    "Curtis (Vertical)"

]


def main(WIN, CLOCK):
    pg.display.message_box(title="Get Hacked Bitch!", message="We fucked yo hard drive")
    while True:
        # Get a list of available level directories
        valid_level_directories = []

        for x in os.listdir("Levels"):
            level_path = os.path.join("Levels", x)
            if not os.path.isfile(level_path):
                if "Level_data.json" in os.listdir(level_path):
                    valid_level_directories.append(x)

        # Let user choose a directory or make a new one
        level = {"map data": EMPTY_MAP_DATA.copy(),
                 "event data": EMPTY_EVENT_DATA.copy()
                 }

        options = []
        for po in valid_level_directories:
            options.append({"Name": po, "Value": po, "On select": "Return", "Render func": "Text only"})
        options.append({"Name": "New", "Value": ["This new"], "On select": "Return", "Render func": "Text only"})
        options.append({"Name": "Quit program", "Value": ["Quit"], "On select": "Return", "Render func": "Text only"})
        chosen_level = Fun.confirmation_popup(WIN, CLOCK, [100, 10], options, popup_width=500, op_width=6)

        if chosen_level == ["Quit"]:
            break

        if chosen_level == ["This new"]:
            # Generate new one if needed.
            # Use the save routine with default level values expect name
            while True:
                name = Fun.text_input_menu(WIN, CLOCK, WIN, [100, 60])
                allow_name = True
                for x in valid_level_directories:
                    if x == name:
                        allow_name = False
                if allow_name:
                    break

            level["event data"]["name"] = name
            save_level_info(WIN, CLOCK, level["map data"], level["event data"], name)

        else:
            level = {"map data": Fun.get_from_json(f"Levels/{chosen_level}/Map_data.json", "Everything"),
                     "event data": Fun.get_from_json(f"Levels/{chosen_level}/Level_data.json", "Everything")
                     }

        # Send selected directory to editor menu
        editor_menu(level, WIN, CLOCK)


# |Main editor menu|----------------------------------------------------------------------------------------------------
def editor_menu(level, WIN, CLOCK):
    map_data = level["map data"]
    event_data = level["event data"]

    # Check if something is missing

    # Action info
    for e in event_data["events"]:
        for a in event_data["events"][e][4]["Default Event Actions"]:
            for potential_missing_info in DEFAULT_EVENT_ACTION_INFO[a["Type"]]:
                if potential_missing_info not in a:
                    a.update({potential_missing_info: DEFAULT_EVENT_ACTION_INFO[a["Type"]][potential_missing_info]})

    # Fields in empty
    for field in EMPTY_MAP_DATA:
        if field not in map_data:
            map_data.update({field: EMPTY_MAP_DATA[field]})
    for field in EMPTY_EVENT_DATA:
        if field not in event_data:
            event_data.update({field: EMPTY_EVENT_DATA[field]})


    save_new_version = True
    options = [
        {"Name": "Map",             "Value": "Map",             "On select": "Return", "Render func": "Text only"},
        {"Name": "Events",          "Value": "Events",          "On select": "Return", "Render func": "Text only"},
        {"Name": "Free variable",   "Value": "Free variable",   "On select": "Return", "Render func": "Text only"},
        {"Name": "Metadata",        "Value": "Metadata",        "On select": "Return", "Render func": "Text only"},
        {"Name": "Save",            "Value": "Save",            "On select": "Return", "Render func": "Text only"},
        {"Name": "Test",            "Value": "Test",            "On select": "Return", "Render func": "Text only"},
        {"Name": "Exit", "Value": "Exit", "On select": "Return", "Render func": "Text only"},
    ]
    menu_logic = Fun.UniversalMenuLogic(options, use_mouse_inputs=True)
    draw = True

    editor_func = empty_func
    # Before leaving check if the player wants to save
    while True:
        # |Menu Logic|--------------------------------------------------------------------------------------------------
        do_shit = menu_logic.act(WIN, CLOCK)
        if do_shit and editor_func == empty_func:
            if do_shit == "Save":
                save_level_info(WIN, CLOCK, map_data, event_data, event_data["name"])
            elif do_shit == "Exit":
                break
            elif do_shit == "Test":
                save_level_info(WIN, CLOCK, map_data, event_data, "~")
                Main.custom_level(level_to_load="Ass Cheeks")
            else:
                editor_func = {

                    "Map": map_editor_func,
                    "Events": event_editor_func,
                    "Free variable": free_var_editor_func_main_menu_handler,
                    "Metadata": metadata_editor_func
                }[do_shit]
            menu_logic.cooldown()

        # Sub menus are handled in their own function
        # A sub menu can load another sub menu
        menu_frame, editor_func, map_data, event_data = editor_func(WIN, CLOCK, map_data, event_data)

        # |Draw|--------------------------------------------------------------------------------------------------------
        if draw:
            # width, height = WIN.get_size()
            width, height = 630, 450
            frame = pg.Surface((630, 450))
            surface_to_draw = frame
            WIN.fill(Fun.BLACK)

            surface_to_draw.fill(Fun.UI_COLOUR_BACKGROUND)

            # surface_to_draw.blit(temp_ui_font.render("", True, AMBER), (25 + x_mod, 25))
            menu_logic.draw(surface_to_draw, [5, 50])
            surface_to_draw.blit(menu_frame, [0, 0])

            # temp_ui_font = Fun.create_temp_font_1(height)

            Fun.scale_render(WIN, surface_to_draw, CLOCK)
            pg.display.flip()

        CLOCK.tick(60)

    if save_new_version:
        pass
    return


def save_level_info(WIN, CLOCK, map_data, event_data, level_name):
    # Check if directory for the level exists
    level_already_exists = False
    for x in os.listdir("Levels"):
        level_path = os.path.join("Levels", x)
        if not os.path.isfile(level_path):
            if "Level_data.json" in os.listdir(level_path) and x == level_name:
                level_already_exists = True

    Fun.make_directory(f"Levels/{level_name}")
    # if not ignore
    Fun.dict_to_json(f"Levels/{level_name}/Map_data.json", map_data)
    Fun.dict_to_json(f"Levels/{level_name}/Level_data.json", event_data)

    Fun.confirmation_popup(WIN, CLOCK, [100, 100],
                           [{"Name": "Okay", "Value": "You suck!", "On select": "Return", "Render func": "Text only"}],
                           text="Level Saved! You ")


# |Map editing|---------------------------------------------------------------------------------------------------------
def map_editor_func(WIN, CLOCK, map_data, event_data):
    # Handles mission editing
    # Geometry handles everything that the player character sees and interacts with

    options = [
        {"Name": "Draw walls", "Value": "Walls", "On select": "Return", "Render func": "Text only"},
        {"Name": "Draw doors", "Value": "Doors", "On select": "Return", "Render func": "Text only"},
        {"Name": "Set door state", "Value": "Door state", "On select": "Return", "Render func": "Text only"},
        {"Name": "Spawn point", "Value": "Spawn", "On select": "Return", "Render func": "Text only"},
        {"Name": "Pathfinding", "Value": "Pathfinding", "On select": "Return", "Render func": "Text only"},
        {"Name": "Rendering", "Value": "Rendering", "On select": "Return", "Render func": "Text only"},
        {"Name": "Resize", "Value": "Resize", "On select": "Return", "Render func": "Text only"},
        {"Name": "Exit", "Value": "Exit", "On select": "Return", "Render func": "Text only"},
    ]
    menu_logic = Fun.UniversalMenuLogic(options, use_mouse_inputs=True)
    frame = pg.Surface((630, 450))
    draw = True
    while True:
        # |Menu Logic|--------------------------------------------------------------------------------------------------
        do_shit = menu_logic.act(WIN, CLOCK)
        if do_shit:
            if do_shit == "Exit":
                break
            if do_shit == "Walls":
                map_data["map"] = map_draw_tool(WIN, CLOCK, map_data["size"], map_data["map"],
                                                rect_list_colour=Fun.WHITE,
                                                background_rect_lists=[map_data["doors"], map_data["spawn point"]],
                                                background_rect_lists_colours=[Fun.RED, Fun.MAGENTA]
                                                )
            if do_shit == "Doors":
                old_doors = map_data["doors"].copy()
                map_data["doors"] = map_draw_tool(WIN, CLOCK, map_data["size"], map_data["doors"],
                                                rect_list_colour=Fun.RED,
                                                background_rect_lists=[map_data["map"], map_data["spawn point"]],
                                                  background_rect_lists_colours=[Fun.WHITE, Fun.MAGENTA])
                if old_doors != map_data["doors"]:
                    map_data["door state"] = [False for x in map_data["doors"]]
            if do_shit == "Door state":
                state_options = []
                for count, state in enumerate(map_data["door state"]):
                    state_options.append({"Name": f"{count}", "Value": state, "On select": "Switch", "Render func": "Text only"})
                state_options.append({"Name": "Finish", "Value": "Exit", "On select": "Return", "Render func": "Text only"})

                door_states = door_status_menu(WIN, CLOCK, [315 - 128, 30], state_options, map_data,
                                               text="", popup_width=400, op_width=1)
                for count, x in enumerate(map_data["door state"]):
                    map_data["door state"][count] = door_states[count]["Value"]
            if do_shit == "Spawn":
                map_data["spawn point"] = map_draw_tool(WIN, CLOCK, map_data["size"], map_data["spawn point"], rect_list_colour=Fun.MAGENTA,
                                                        background_rect_lists=[map_data["map"], map_data["doors"]],
                                                        background_rect_lists_colours=[Fun.WHITE, Fun.RED],
                                                        point_selection_mode=True)
            if do_shit == "Pathfinding":
                map_data["pathfinding"] = map_draw_tool(WIN, CLOCK, map_data["size"], map_data["pathfinding"], rect_list_colour=Fun.YELLOW,
                                                        background_rect_lists=[map_data["map"], map_data["doors"], map_data["spawn point"]],
                                                        background_rect_lists_colours=[Fun.WHITE, Fun.RED, Fun.MAGENTA],
                                                        point_selection_mode=True, multi_point_selection=True)
            if do_shit == "Rendering":
                rendering_editor_menu(WIN, CLOCK, map_data)
            if do_shit == "Resize":
                # pick from list
                new_size = map_data["size"].copy()
                list_width = []
                list_height = []
                map_data["size"] = new_size
            menu_logic.cooldown()

        # |Draw|------------------------------------------------------------------------------------------------------------
        if draw:
            # width, height = WIN.get_size()
            width, height = 630, 450
            frame = pg.Surface((630, 450))
            surface_to_draw = frame
            WIN.fill(Fun.BLACK)

            surface_to_draw.fill(Fun.UI_COLOUR_BACKGROUND)

            # surface_to_draw.blit(temp_ui_font.render("", True, AMBER), (25 + x_mod, 25))
            menu_logic.draw(surface_to_draw, [5, 50])

            # temp_ui_font = Fun.create_temp_font_1(height)

            Fun.scale_render(WIN, surface_to_draw, CLOCK)
            pg.display.flip()
        CLOCK.tick(60)
    return frame, empty_func, map_data, event_data


def map_draw_tool(WIN, CLOCK, size, rect_list, rect_list_colour=Fun.WHITE, background_rect_lists=[], background_rect_lists_colours=[], point_selection_mode=False, multi_point_selection=False):
    # Rect list is the rectangles being drawn
    # size is the amount of 32px tiles in each direction
    canvas = pg.transform.scale(Fun.SPRITE_EMPTY, size)
    # canvas.convert_alpha()
    # canvas.fill((0, 0, 0, 0))
    draw_size = 8
    background_canvas = pg.transform.scale(Fun.SPRITE_EMPTY, size)
    background_canvas.set_alpha(128)

    for r in rect_list:
        pg.draw.rect(canvas, rect_list_colour, [d * draw_size for d in r])

    for count, background_list in enumerate(background_rect_lists):
        for r in background_list:
            pg.draw.rect(background_canvas, background_rect_lists_colours[count], [d * draw_size for d in r])

    scrolling = [0, 0]
    allow_scroll = True
    controller = Fun.PseudoPlayerMouseInput()
    draw = True
    spacing_control = lambda p : p - p % draw_size
    shape_first_point = False
    shape_type = "Point"
    # Create
    while True:
        keys = pg.key.get_pressed()
        mouse_keys = pg.mouse.get_pressed()
        Fun.needed_in_menu_and_game(WIN, keys)
        controller.get_input(keys, mouse_keys)
        # mouse_pos = pg.mouse.get_pos()
        mouse_pos = Fun.get_scaled_mouse_pos()
        if controller.input["Reload"]:
            break

        if allow_scroll:
            if controller.input["Up"]:
                scrolling[1] += draw_size
            if controller.input["Down"]:
                scrolling[1] -= draw_size
            if controller.input["Left"]:
                scrolling[0] += draw_size
            if controller.input["Right"]:
                scrolling[0] -= draw_size

        # Draw tool
        if not shape_first_point and not point_selection_mode:
            if controller.input["Skill 1"]:
                shape_first_point = [spacing_control(mouse_pos[0]), spacing_control(mouse_pos[1])]
                shape_type = "Rect"

            if controller.input["Skill 2"] and False: # Disabled for now, can't figure out how to make lines work
                shape_first_point = [spacing_control(mouse_pos[0]), spacing_control(mouse_pos[1])]
                shape_type = "Line"

        if controller.input["Shoot"]:
            if point_selection_mode and not multi_point_selection:
                canvas = pg.transform.scale(Fun.SPRITE_EMPTY, size)
            shape_type, shape_first_point = map_draw_tool_brushes(
                shape_type, canvas, rect_list_colour,
                [spacing_control(mouse_pos[0]), spacing_control(mouse_pos[1]),],
                shape_first_point, draw_size, scrolling, preview_only=False)
        if controller.input["Alt fire"] and (not point_selection_mode or multi_point_selection):
            shape_type, shape_first_point = map_draw_tool_brushes(
                shape_type, canvas, (0, 0, 0, 0),
                [spacing_control(mouse_pos[0]), spacing_control(mouse_pos[1]),],
                shape_first_point, draw_size, scrolling, preview_only=False)

        #
        if draw:
            # width, height = WIN.get_size()
            width, height = 630, 450
            frame = pg.Surface((630, 450))
            surface_to_draw = frame
            WIN.fill(Fun.BLACK)

            surface_to_draw.fill(Fun.UI_COLOUR_BACKGROUND)

            for y in range(canvas.get_height() // draw_size):
                for x in range(canvas.get_width() // draw_size):
                    pg.draw.rect(surface_to_draw,
                                 [
                                     [(10, 10, 10), (25, 25, 25)][y % 2],
                                     [(25, 25, 25), (10, 10, 10)][y % 2]
                                 ][x % 2],
                                 [x * draw_size + scrolling[0], y* draw_size + scrolling[1], draw_size, draw_size]
                                 )

            surface_to_draw.blit(background_canvas, scrolling)
            surface_to_draw.blit(canvas, scrolling)

            shape_type, shape_first_point = map_draw_tool_brushes(
                shape_type, surface_to_draw, Fun.GRAY,
                [spacing_control(mouse_pos[0]), spacing_control(mouse_pos[1]),],
                shape_first_point, draw_size, [0, 0], preview_only=True)

            # temp_ui_font = Fun.create_temp_font_1(height)
            Fun.scale_render(WIN, surface_to_draw, CLOCK)
            pg.display.flip()
        CLOCK.tick(60)

    # Convert image to rects for storage
    canvas = pg.transform.scale(canvas, [size[0]//draw_size, size[1]//draw_size])
    img = pg.Surface([size[0]//draw_size+2, size[1]//draw_size+2])
    img.blit(canvas, (1,1))
    map_geo = []
    for y in range(size[1]//draw_size+2):
        rank = []
        for x in range(size[0]//draw_size+2):
            rank.append(int(img.get_at((x, y)) == rect_list_colour))
        map_geo.append(rank)
    output = Fun.find_rects_giga_chad(map_geo, size[0]//draw_size+2, size[1]//draw_size+2)
    new_output = []
    for o in output:
        new_output.append([o[0]-1, o[1]-1, o[2], o[3]])

    if point_selection_mode and not multi_point_selection:
        new_point = new_output[0]
        return [[new_point[0], new_point[1], 1, 1]]
    return new_output


def map_draw_tool_brushes(shape_type, surface, colour, pos, shape_first_point, draw_size, scrolling, preview_only=False):
    if shape_type == "Point":
        pg.draw.rect(surface, colour,
                     [pos[0]-scrolling[0], pos[1]-scrolling[1], draw_size, draw_size])
    if shape_type == "Rect":
        p = [shape_first_point[0]-scrolling[0], shape_first_point[1]-scrolling[1]]
        # p = [shape_first_point[0], shape_first_point[1]]
        rect_x = p[0]
        rect_y = p[1]
        rect_width = pos[0]-scrolling[0] - p[0] + draw_size
        rect_height = pos[1]-scrolling[1] - p[1] + draw_size
        if rect_width < 0:
            rect_x = rect_x + rect_width - draw_size
            rect_width = abs(rect_width) + draw_size * 2
        if rect_height < 0:
            rect_y = rect_y + rect_height - draw_size
            rect_height = abs(rect_height) + draw_size * 2
        pg.draw.rect(surface, colour, [rect_x, rect_y, rect_width, rect_height])
        # Need way to handle
        if not preview_only:
            return "Point", []
    if shape_type == "Line":
        start_pos = [shape_first_point[0] - scrolling[0], shape_first_point[1] - scrolling[1]]
        end_pos = [pos[0] - scrolling[0], pos[1] - scrolling[1]]

        width = (start_pos[0] - end_pos[0])
        height = (start_pos[1] - end_pos[1])

        x_mod = 0
        if width < 0:
            x_mod = width
            width = abs(width)
        y_mod = 0
        if height < 0:
            y_mod = height
            height = abs(height)
        pos_s = [x_mod, y_mod]
        pos_e = [width, height]

        temp_surf = pg.Surface((width//draw_size+1, height//draw_size+1), pg.SRCALPHA)
        print(pos_s, pos_e, (width//draw_size+1, height//draw_size+1))

        pg.draw.line(temp_surf, colour, pos_s, pos_e)

        temp_pos = [end_pos[0] + x_mod, end_pos[1] + y_mod]
        surface.blit(pg.transform.scale_by(temp_surf, draw_size), temp_pos)

        # pg.draw.line(surface, colour, start_pos, end_pos, width=draw_size)
        if not preview_only:
            return "Point", []

    return shape_type, shape_first_point


def door_status_menu(WIN, CLOCK, pos, options, map_data, text="", popup_width=128, op_width=1):
    size = map_data["size"]

    canvas = pg.transform.scale(Fun.SPRITE_EMPTY, size)
    # canvas.convert_alpha()
    # canvas.fill((0, 0, 0, 0))
    draw_size = 8

    background_canvas = pg.transform.scale(Fun.SPRITE_EMPTY, size)
    background_canvas.set_alpha(128)
    scrolling = [0, 0]

    menu_logic = Fun.UniversalMenuLogic(
        options, use_mouse_inputs=True, width=op_width
    )
    menu_overlay = pg.image.load(os.path.join("Sprites/UI/Overlay.png")).convert_alpha()
    frame_1 = Fun.some_bullshit_for_transitions(WIN)
    draw = True
    text_lines = Fun.split_text(text, limit=80)
    while True:
        do_shit = menu_logic.act(WIN, CLOCK)
        if do_shit:
            output = menu_logic.options
            return output
        # |Draw|--------------------------------------------------------------------------------------------------------
        if draw:
            width, height = 630, 450
            # frame = pg.Surface((630, 450))
            frame = pg.Surface((630, 450))
            surface_to_draw = frame
            WIN.fill(Fun.BLACK)

            # Draw grid background
            for y in range(canvas.get_height() // draw_size):
                for x in range(canvas.get_width() // draw_size):
                    pg.draw.rect(surface_to_draw,
                                 [
                                     [(10, 10, 10), (25, 25, 25)][y % 2],
                                     [(25, 25, 25), (10, 10, 10)][y % 2]
                                 ][x % 2],
                                 [x * draw_size + scrolling[0], y* draw_size + scrolling[1], draw_size, draw_size]
                                 )
            for w in map_data["map"]:
                pg.draw.rect(background_canvas, Fun.WHITE, [s * draw_size for s in w])
            for count, d in enumerate(map_data["doors"]):
                col = [255, 0, 0]
                if not menu_logic.options[count]["Value"]:
                    col = [0, 255, 0]
                if menu_logic.selected_option != count:
                    col = [c * 0.4 for c in col]
                pg.draw.rect(canvas, col, [s * draw_size for s in d])

            temp_ui_font = Fun.create_temp_font_1(height)
            surface_to_draw.fill(Fun.UI_COLOUR_BACKGROUND)

            # surface_to_draw.blit(frame_1, (0, 0))

            surface_to_draw.blit(background_canvas, scrolling)
            surface_to_draw.blit(canvas, scrolling)

            height_mod = 0
            if text != "":
                #
                height_mod = 18 * len(text_lines)
            popup_height = 17 * len(menu_logic.options) + 30 + height_mod
            popup_uni = pg.Surface((popup_width, popup_height))
            popup_uni.fill(Fun.UI_COLOUR_NEW_BACKGROUND)
            menu_logic.draw(popup_uni, [0, height_mod])

            for count, x in enumerate(menu_logic.options):
                if x["Value"] in ["Exit"]:
                    continue
                pos = (80 + 24 * op_width, 30+ height_mod + 18 * count)
                popup_uni.blit(temp_ui_font.render(f"{x["Value"]}", True, Fun.AMBER), pos)

            # if text != "":
            #     # text_lines
            #     for count, text_line in enumerate(text_lines):
            #         rendered_text = temp_ui_font.render(text_line, True, AMBER)
            #         popup_uni.blit(rendered_text, [20, count * 18])

            popup_uni.set_alpha(192)
            surface_to_draw.blit(popup_uni, pos)
            pg.draw.rect(surface_to_draw, Fun.AMBER, (pos[0] - 2, pos[1] - 2, popup_width + 4, popup_height + 4), width=2)

            Fun.scale_render(WIN, surface_to_draw, CLOCK)
            pg.display.flip()
            CLOCK.tick(60)


def rendering_editor_menu(WIN, CLOCK, map_data):
    editor_colours =  [
        (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255), (255, 128, 128),
        (128, 255, 128), (128, 128, 255), (255, 255, 128), (255, 128, 255), (128, 255, 255)
    ]

    # "Segments": [{
    #   'Rect': pg.Rect,
    #   'Wall': [],
    #   'Floor': []}],
    # "Tile set": {"Wall": TILE_SET_IRON_MINES_WALL, "Floor": TILE_SET_IRON_MINES_FLOOR}

    # Check if rendering is empty, if empty make a basic one
    if not map_data["rendering"]["Segments"]:
        map_data["rendering"]["Tile set"] = {"Wall": 'Iron Mine Walls', "Floor": 'Iron Mine Floor'}
        # Generate the render

        render_map = pg.Surface([map_data["size"][0] / 8, map_data["size"][1] / 8])
        render_map.fill((0, 0, 0))
        for w in map_data["map"]:
            pg.draw.rect(render_map, Fun.WHITE, w)

        for y in range(render_map.get_height()):
            for x in range(render_map.get_width()):
                try:
                    if render_map.get_at([x, y +1]) == (0, 0, 0) and render_map.get_at([x, y]) == Fun.WHITE:
                        render_map.set_at([x, y], (0, 255, 255))
                except IndexError:
                    # We do not care
                    pass

        pg.image.save(render_map, "~AAA.png")
        old_render_map = render_map
        new_render_map = pg.Surface([map_data["size"][0]+2, map_data["size"][1] + 2])
        new_render_map.fill((255, 0, 128))
        new_render_map.blit(old_render_map, (1, 1))
        render_map = new_render_map

        map_data["rendering"]["Segments"] = render_segmenter(map_data, render_map)

    # Convert segments into usable wall lists
    tile_set_info = {
        # <Tile set name>: [<rect>, ...]
    }
    for t in map_data["rendering"]["Tile set"]:
        tile_set_info.update({t: []})
    for count, segment in enumerate(map_data["rendering"]["Segments"]):
        for s in segment:
            if s == "Rect":
                continue
            # if s == "Wall":
            #     print(segment[s])
            for w in segment[s]:
                tile_set_info[s].append(w)
        # print(count)

    # Give option to change or add a tile set
    options = [
    ]
    for tile_set in tile_set_info:
        options.append({"Name": tile_set, "Value": tile_set, "On select": "Return", "Render func": "Text only"})
    options.append({"Name": "Add", "Value": "Add", "On select": "Return", "Render func": "Text only"})
    options.append({"Name": "Reset", "Value": "Reset", "On select": "Return", "Render func": "Text only"})
    options.append({"Name": "Exit", "Value": "Exit", "On select": "Return", "Render func": "Text only"})

    menu_logic = Fun.UniversalMenuLogic(options, use_mouse_inputs=True)
    frame = pg.Surface((630, 450))
    draw = True
    while True:
        # |Menu Logic|--------------------------------------------------------------------------------------------------
        do_shit = menu_logic.act(WIN, CLOCK)
        if do_shit:
            if do_shit == "Exit":
                break
            elif do_shit == "Add":
                while True:
                    potential_name = Fun.text_input_menu(WIN, CLOCK, surface_to_draw, [100, 60])

                    allow_name = True
                    if potential_name in map_data["rendering"]["Tile set"]:
                        allow_name = False
                        Fun.confirmation_popup(WIN, CLOCK, [315 - 128, 300],
                        [{"Name": "Okay....", "Value": "You suck!", "On select": "Return", "Render func": "Text only"}],
                                           text="Name is already taken. Choose another")
                    if allow_name:
                        break

                # Pick a list for available tile set
                new_tiles = Fun.pick_from_list_popup(WIN, CLOCK, "Industrial Floor", [t for t in Event.TILES_DICT])
                tile_set_info.update({potential_name: []})
                map_data["rendering"]["Tile set"].update({potential_name: new_tiles})
            elif do_shit == "Reset":
                if Fun.confirmation_popup(WIN, CLOCK, [315 - 128, 300],
                                          [
                                              {"Name": "No!", "Value": "No", "On select": "Return",
                                               "Render func": "Text only"},
                                              {"Name": "YES!", "Value": "Yes", "On select": "Return",
                                               "Render func": "Text only"},
                                          ],
                                          text="Reset Rendering Data?") == "Yes":
                    map_data["rendering"] = {"Segments": [], "Tile set": {}}
                    tile_set_info = {}
                    menu_logic.selected_option = 0
            else:
                chosen_sub = Fun.confirmation_popup(WIN, CLOCK, [100, 90], [
                            {"Name": "Edit", "Value": "Edit", "On select": "Return", "Render func": "Text only"},
                            {"Name": "Change Tileset", "Value": "Change", "On select": "Return", "Render func": "Text only"},
                            {"Name": "Delete", "Value": "Delete", "On select": "Return", "Render func": "Text only"},
                            {"Name": "Return", "Value": "Nothing", "On select": "Return", "Render func": "Text only"}
                        ], popup_width=500)

                if chosen_sub == "Edit":
                    # Draw the tile set
                    background_rect_lists = [map_data['map']]
                    background_rect_lists_colours = [Fun.WHITE]
                    col = editor_colours[0]
                    for count, tile in enumerate(tile_set_info):
                        if tile == do_shit:
                            col = editor_colours[count]
                            continue
                        background_rect_lists.append(tile_set_info[tile])
                        background_rect_lists_colours.append(editor_colours[count])

                    tile_set_info[do_shit] = map_draw_tool(WIN, CLOCK, map_data['size'], tile_set_info[do_shit],
                                  rect_list_colour=col,
                                  background_rect_lists=background_rect_lists,
                                  background_rect_lists_colours=background_rect_lists_colours)
                elif chosen_sub == "Change":
                    map_data["rendering"]["Tile set"][do_shit] = Fun.pick_from_list_popup(
                        WIN, CLOCK, map_data["rendering"]["Tile set"][do_shit],
                        [ppp for ppp in Event.TILES_DICT],
                        choose_text="Tile set", pos=(100, 90),
                        text="")
                elif chosen_sub == "Delete":
                    if Fun.confirmation_popup(WIN, CLOCK, [315 - 128, 300],
                                              [
                                                  {"Name": "No!", "Value": "No", "On select": "Return",
                                                   "Render func": "Text only"},
                                                  {"Name": "YES!", "Value": "Yes", "On select": "Return",
                                                   "Render func": "Text only"},
                                              ],
                                              text="Delete event action?") == "Yes":
                        tile_set_info.pop(do_shit)

            menu_logic.cooldown()
            # Update options
            options = [
            ]
            for tile_set in tile_set_info:
                options.append({"Name": tile_set, "Value": tile_set, "On select": "Return", "Render func": "Text only"})
            options.append({"Name": "Add", "Value": "Add", "On select": "Return", "Render func": "Text only"})
            options.append({"Name": "Reset", "Value": "Reset", "On select": "Return", "Render func": "Text only"})
            options.append({"Name": "Exit", "Value": "Exit", "On select": "Return", "Render func": "Text only"})

            menu_logic.options = options

        # |Draw|------------------------------------------------------------------------------------------------------------
        if draw:
            # width, height = WIN.get_size()
            width, height = 630, 450
            frame = pg.Surface((630, 450))
            surface_to_draw = frame
            WIN.fill(Fun.BLACK)

            surface_to_draw.fill(Fun.UI_COLOUR_BACKGROUND)

            # surface_to_draw.blit(temp_ui_font.render("", True, AMBER), (25 + x_mod, 25))
            menu_logic.draw(surface_to_draw, [5, 50])

            # temp_ui_font = Fun.create_temp_font_1(height)

            Fun.scale_render(WIN, surface_to_draw, CLOCK)
            pg.display.flip()
        CLOCK.tick(60)

    # Redo render info to make it usable
    # tile_set_info
    # Draw on

    # for w in map_data["map"]:
    #     pg.draw.rect(output_map, Fun.WHITE, w)

    tile_dict = {}
    render_maps = []
    for count, tsss in enumerate(tile_set_info):
        output_map = pg.Surface(map_data["size"])
        output_map.fill((0, 0, 0))
        for w in tile_set_info[tsss]:
            # pg.draw.rect(output_map, editor_colours[count], w)
            pg.draw.rect(output_map, Fun.WHITE, w)
        # tile_dict.update({tsss: editor_colours[count]})
        tile_dict.update({tsss: Fun.WHITE})

        # pg.image.save(output_map, "~AAA.png")
        old_render_map = output_map
        new_render_map = pg.Surface([map_data["size"][0] + 2, map_data["size"][1] + 2])
        new_render_map.fill((255, 0, 128))
        new_render_map.blit(old_render_map, (1, 1))
        render_maps.append(new_render_map)

    map_data["rendering"]["Segments"] = []

    # Make the tile dict
    segment_list = []
    for layer, tile_layer in enumerate(tile_dict):
        segments_to_add = render_segmenter(map_data, render_maps[layer], tile_dict={tile_layer: Fun.WHITE})
        # Compile segments
        for x in segments_to_add:
            if not x[tile_layer]:
                continue
            append_to_segment_list = True
            for y in segment_list:
                if x["Rect"] == y["Rect"]:
                    append_to_segment_list = False
                    y.update({tile_layer: x[tile_layer]})
                    break
            if append_to_segment_list:
                segment_list.append(x)
    map_data["rendering"]["Segments"] = segment_list


def render_segmenter(map_data, render_map, tile_dict={'Wall': (0, 255, 255), 'Floor': (0, 0, 0)}):
    segment_size = [16, 16]
    convert_wall = lambda wall, p: [(wall[0] + p[0]) - 2, (wall[1] + p[1]) - 2, wall[2], wall[3]]
    segments_to_return = []

    for y in range(map_data["size"][1] // segment_size[1]):
        for x in range(map_data["size"][0] // segment_size[0]):  #
            pos = [(x * segment_size[0]) + 1,
                   (y * segment_size[1]) + 1]

            segment = pg.surface.Surface((segment_size[0] + 2, segment_size[1] + 2))
            segment.fill((255, 0, 128))
            segment.blit(render_map.subsurface(pos[0], pos[1], segment_size[0], segment_size[1]), (1, 1))
            new_dict = {
                'Rect': [pos[0], pos[1], segment_size[0], segment_size[1]],
            }
            for a in tile_dict:
                new_dict.update({
                    a: [convert_wall(wall, pos) for wall in Fun.advanced_image_to_map_geometry(segment, colours_to_check=[tile_dict[a]], size_mod=1)]
                })
            segments_to_return.append(new_dict)
    return segments_to_return


# |Event editing|-------------------------------------------------------------------------------------------------------
def event_editor_func(WIN, CLOCK, map_data, event_data):
    # Handles mission editing
    #  Event trigger zones
    options = []
    for e in event_data["events"]:
        options.append({"Name": e, "Value": e, "On select": "Return", "Render func": "Text only"})
    options.append({"Name": "New event", "Value": "New", "On select": "Return", "Render func": "Text only"})
    options.append({"Name": "Exit", "Value": "Exit", "On select": "Return", "Render func": "Text only"})

    menu_logic = Fun.UniversalMenuLogic(options, use_mouse_inputs=True)
    frame = pg.Surface((630, 450))
    draw = True
    while True:
        # |Menu Logic|--------------------------------------------------------------------------------------------------
        do_shit = menu_logic.act(WIN, CLOCK)
        if do_shit:
            if do_shit == "New":
                allow_new_event = True
                # Ask for event name/ID
                # new_event_name = input("Write event name: ") # Temporary measure
                new_event_name = Fun.text_input_menu(WIN, CLOCK, surface_to_draw, [100, 60])
                # Check if name/ID already exists
                if new_event_name in [n for n in event_data["events"]]:
                    allow_new_event = False
                # Add new event if allowed
                if allow_new_event:
                    event_data["events"].update({new_event_name: [new_event_name, {'rects': [], 'Conditions': 'trigger_check_constant'},
                                                                 True, ["generic_event"], {"Default Event Actions": []}]})
                    menu_logic.selected_option += 1

            elif do_shit == "Exit":
                break
            else:
                map_data, event_data = event_editor_settings_func(WIN, CLOCK, map_data, event_data, do_shit)

            # Update options, moved that there to handle event deletion
            options = [

            ]
            for e in event_data["events"]:
                options.append({"Name": e, "Value": e, "On select": "Return", "Render func": "Text only"})
            options.append({"Name": "New event", "Value": "New", "On select": "Return", "Render func": "Text only"})
            options.append({"Name": "Exit", "Value": "Exit", "On select": "Return", "Render func": "Text only"})

            menu_logic.options = options
            menu_logic.max_option = len(options) - 1

            menu_logic.cooldown()

        # |Draw|------------------------------------------------------------------------------------------------------------
        if draw:
            # width, height = WIN.get_size()
            width, height = 630, 450
            frame = pg.Surface((630, 450))
            surface_to_draw = frame
            WIN.fill(Fun.BLACK)

            surface_to_draw.fill(Fun.UI_COLOUR_BACKGROUND)

            # surface_to_draw.blit(temp_ui_font.render("", True, AMBER), (25 + x_mod, 25))
            menu_logic.draw(surface_to_draw, [5, 50])

            # temp_ui_font = Fun.create_temp_font_1(height)

            Fun.scale_render(WIN, surface_to_draw, CLOCK)
            pg.display.flip()

        CLOCK.tick(60)

    return frame, empty_func, map_data, event_data


def event_editor_settings_func(WIN, CLOCK, map_data, event_data, event_being_modified):
    # [new_event_name, {'rects': [], 'Conditions': 'trigger_check_constant'}, True, [], {}]})
    options = [
        {"Name": "Edit Trigger", "Value": "Trigger", "On select": "Return", "Render func": "Text only"},
    ]

    # Add options to edit options
    for count, a in enumerate(event_data["events"][event_being_modified][4]["Default Event Actions"]):
        action_name = a["Name"]
        visible_name = f"{action_name}_{count}"
        options.append({"Name": visible_name, "Value": count, "On select": "Return", "Render func": "Text only"})
    options.append({"Name": "New Action", "Value": "New Action", "On select": "Return", "Render func": "Text only"})

    toggle_name = ["Multi use event", "Single use event"][event_data["events"][event_being_modified][2]]
    options.append({"Name": toggle_name, "Value": "Toggle", "On select": "Return", "Render func": "Text only"})
    options.append({"Name": "Free var", "Value": "Free var", "On select": "Return", "Render func": "Text only"})
    options.append({"Name": "Delete", "Value": "Delete", "On select": "Return", "Render func": "Text only"})
    options.append({"Name": "Exit", "Value": "Exit", "On select": "Return", "Render func": "Text only"})

    # toggle between single use or not. (default is not)
    menu_logic = Fun.UniversalMenuLogic(options, use_mouse_inputs=True)
    frame = pg.Surface((630, 450))
    draw = True
    while True:
        # |Menu Logic|--------------------------------------------------------------------------------------------------
        do_shit = menu_logic.act(WIN, CLOCK)
        if do_shit or type(do_shit) != bool:
            if do_shit == "Toggle":
                event_data["events"][event_being_modified][2] = not event_data["events"][event_being_modified][2]
                toggle_name = ["Multi use event", "Single use event"][event_data["events"][event_being_modified][2]]
                menu_logic.options[-2] = {"Name": toggle_name, "Value": "Toggle", "On select": "Return", "Render func": "Text only"}
            elif do_shit == "Trigger":
                # Pick what to modify
                edit_trigger_attribute = Fun.confirmation_popup(WIN, CLOCK, [100, 10], [
                    {"Name": "Function", "Value": "Func", "On select": "Return", "Render func": "Text only"},
                    {"Name": "Trigger Area", "Value": "Area", "On select": "Return", "Render func": "Text only"},
                    {"Name": "Exit", "Value": "Exit", "On select": "Return", "Render func": "Text only"}
                ], popup_width=500)

                if edit_trigger_attribute == "Func":
                    default_value = 0
                    for count, dv in enumerate(ALL_TRIGGER_FUNC):
                        if dv == event_data["events"][event_being_modified][1]['Conditions']:
                            default_value = count
                            break
                    # , "Choose": {"List": sticks}
                    event_data["events"][event_being_modified][1]['Conditions'] =  ALL_TRIGGER_FUNC[
                        Fun.confirmation_popup(WIN, CLOCK, [100, 90], [
                            {"Name": "Function", "Value": default_value, "On select": "Choose", "Render func": "Choose",
                             "Choose": {"List": ALL_TRIGGER_FUNC}},
                            {"Name": "Finish", "Value": "Finish", "On select": "Return", "Render func": "Text only"}
                        ], popup_width=500, return_everything=True)[0]["Value"]
                    ]
                    trigger_func = event_data["events"][event_being_modified][1]['Conditions']

                    # Handle events that need special free var
                    # print(event_data["events"][event_being_modified][1]['Conditions'])
                    # event_data["events"][event_being_modified][4].update({"": ""})

                    # Add to function
                    # trigger_check_for_time                            missionEvent.free_var["Time target"]
                    if trigger_func in ["trigger_check_timer_on", "trigger_check_timer"]:
                        event_data["events"][event_being_modified][4].update({"Timer": 60})
                    # trigger_check_finished_encounter                  level["free var"][missionEvent.name]
                    if trigger_func == "trigger_check_encounter_waves":
                        # "E. num ref"          free var used to track waves
                        event_data["events"][event_being_modified][4].update({"E. num ref": ""})
                        # Add a level free_var named after the event as a default one

                        # "E. num stage"        number to trigger next stage # set to one
                        event_data["events"][event_being_modified][4].update({"E. num stage": 1})
                    if trigger_func in ["trigger_check_under_specified_amount_enemies", "trigger_check_encounter_waves"]:
                        # "Specified amount"    when enemy count reaches this value, trigger next stage
                        event_data["events"][event_being_modified][4].update({"Specified amount": 0})

                if edit_trigger_attribute == "Area":
                    event_data["events"][event_being_modified][1]['rects'] = map_draw_tool(
                        WIN, CLOCK, map_data["size"], event_data["events"][event_being_modified][1]['rects'], rect_list_colour=Fun.TEAL,
                        background_rect_lists=[map_data["map"], map_data["doors"], map_data["spawn point"]],
                        background_rect_lists_colours=[Fun.WHITE, Fun.RED, Fun.MAGENTA])
            elif do_shit == "New Action":
                # Ask event type
                while True:
                    potential_name = Fun.text_input_menu(WIN, CLOCK, surface_to_draw, [100, 60])

                    allow_name = True
                    if potential_name in event_data["events"][event_being_modified][4]["Default Event Actions"]:
                        allow_name = False
                        Fun.confirmation_popup(WIN, CLOCK, [315 - 128, 300],
                        [{"Name": "Okay....", "Value": "You suck!", "On select": "Return", "Render func": "Text only"}],
                                           text="Name is already taken. Choose another")

                    if allow_name:
                        break

                empty_action = {"Name": potential_name, "Type": ""}
                # Based on type, add default info

                # Add action in free vars
                event_data["events"][event_being_modified][4]["Default Event Actions"].append(empty_action)
            elif do_shit == "Delete":
                if Fun.confirmation_popup(WIN, CLOCK, [315 - 128, 300],
                        [
                            {"Name": "No!", "Value": "No", "On select": "Return", "Render func": "Text only"},
                            {"Name": "YES!", "Value": "Yes", "On select": "Return", "Render func": "Text only"},
                        ],
                                           text="Delete event?") == "Yes":
                    event_data["events"].pop(event_being_modified)
                    return map_data, event_data
            elif do_shit == "Free var":
                event_data["events"][event_being_modified][4] = free_var_editor_func(WIN, CLOCK, map_data, event_data, event_data["events"][event_being_modified][4])
            elif do_shit == "Exit":
                break
            else:
                # Get the event action
                event_action_modified = event_data["events"][event_being_modified][4]["Default Event Actions"][do_shit]
                change_event_type = event_action_modified["Type"] == ""

                # Pick an option
                if not change_event_type:
                    select_edit_option = Fun.confirmation_popup(WIN, CLOCK, [100, 90], [
                            {"Name": "Edit Info", "Value": "Edit", "On select": "Return", "Render func": "Text only"},
                            {"Name": "Change Type", "Value": "Change", "On select": "Return", "Render func": "Text only"},
                            {"Name": "Delete", "Value": "Delete", "On select": "Return", "Render func": "Text only"},
                            {"Name": "Return", "Value": "Nothing", "On select": "Return", "Render func": "Text only"}
                        ], popup_width=500)
                    if select_edit_option == "Change":
                        change_event_type = True
                    elif select_edit_option == "Delete":
                        if Fun.confirmation_popup(WIN, CLOCK, [315 - 128, 300],
                                                  [
                                                      {"Name": "No!", "Value": "No", "On select": "Return",
                                                       "Render func": "Text only"},
                                                      {"Name": "YES!", "Value": "Yes", "On select": "Return",
                                                       "Render func": "Text only"},
                                                  ],
                                                  text="Delete event action?") == "Yes":
                            event_data["events"][event_being_modified][4]["Default Event Actions"].pop(do_shit)
                    else:
                        func_map = {
                            "spawn": {"Class": ["Entity", "Item"], "Pos": [0, 0, 1, 1], "Angle": 0, "ID":
                                {"Entity": [e for e in Entity.unified_entity_repertory], "Item": [i for i in Items.editor_items]},
                                      "Team": "Enemies"
                                      # TODO: Add boss intro
                                      },
                            "despawn": {"Method": ["Soft", "Hard"], "Conditions": []},
                            "door": {"Door ID": [d for d, ignore in enumerate(map_data["doors"])], "Door state": True}, # Need a function to select doors visually
                            "sound": {"Action": ["Play", "Change", "Pause", "Stop"],
                                      "Audio": {"Sound": [s for s in Fun.sounds_dict], "Music": [s for s in Fun.music_dict]}},
                            "level end": {"End level state": ["win", " loss"]},
                            "cutscene": {},
                            "radio": {},
                            "teleport": {"Pos": [0, 0, 1, 1]},
                            "character": {"Character": PLAYABLE_CHARACTERS, "Carry over health": True},
                            "free var": {"Target free var": [fv for fv in event_data["free var"]], "Operation": ["Addition", "Subtraction", "Multiplication", "Division", "Set"], "Value": 0}
                        }
                        # print([d for d, ignore in enumerate(map_data["doors"])])

                        action_editor_func(WIN, CLOCK, event_action_modified, func_map=func_map[event_action_modified["Type"]], map_data=map_data)

                # Make sure the event action has a type assigned
                if change_event_type:
                    default_value = 0

                    for count, dv in enumerate(ALL_EVENT_ACTION_TYPE):
                        if dv == event_action_modified["Type"]:
                            default_value = count
                            break

                    action_types_to_pick = [a for a in  ALL_EVENT_ACTION_TYPE]
                    if not event_data["free var"]:
                        action_types_to_pick.pop(-1)

                    event_action_modified["Type"] = ALL_EVENT_ACTION_TYPE[
                        Fun.confirmation_popup(WIN, CLOCK, [100, 90], [
                            {"Name": "Action type", "Value": default_value, "On select": "Choose", "Render func": "Choose",  "Choose": {"List": action_types_to_pick}},
                            {"Name": "Finish", "Value": "Finish", "On select": "Return", "Render func": "Text only"}
                        ], popup_width=500, return_everything=True)[0]["Value"]
                    ]
                    event_data["events"][event_being_modified][4]["Default Event Actions"][do_shit] = {"Name": event_action_modified["Name"], "Type": event_action_modified["Type"]}
                    event_data["events"][event_being_modified][4]["Default Event Actions"][do_shit].update(
                        DEFAULT_EVENT_ACTION_INFO[event_data["events"][event_being_modified][4]["Default Event Actions"][do_shit]["Type"]]
                    )

            # Update options
            options = [
                {"Name": "Edit Trigger", "Value": "Trigger", "On select": "Return", "Render func": "Text only"},
            ]
            for count, a in enumerate(event_data["events"][event_being_modified][4]["Default Event Actions"]):
                action_name = a["Name"]
                visible_name = f"{action_name}_{count}"
                options.append({"Name": visible_name, "Value": count, "On select": "Return",
                                "Render func": "Text only"})
            options.append(
                {"Name": "New Action", "Value": "New Action", "On select": "Return", "Render func": "Text only"})
            toggle_name = ["Multi use event", "Single use event"][event_data["events"][event_being_modified][2]]
            options.append({"Name": toggle_name, "Value": "Toggle", "On select": "Return", "Render func": "Text only"})
            options.append({"Name": "Free var", "Value": "Free var", "On select": "Return", "Render func": "Text only"})
            options.append({"Name": "Delete", "Value": "Delete", "On select": "Return", "Render func": "Text only"})
            options.append({"Name": "Exit", "Value": "Exit", "On select": "Return", "Render func": "Text only"})

            menu_logic.options = options
            menu_logic.cooldown()

        # |Draw|------------------------------------------------------------------------------------------------------------
        if draw:
            # width, height = WIN.get_size()
            width, height = 630, 450
            frame = pg.Surface((630, 450))
            surface_to_draw = frame
            WIN.fill(Fun.BLACK)

            surface_to_draw.fill(Fun.UI_COLOUR_BACKGROUND)

            # surface_to_draw.blit(temp_ui_font.render("", True, AMBER), (25 + x_mod, 25))
            menu_logic.draw(surface_to_draw, [5, 50])

            # temp_ui_font = Fun.create_temp_font_1(height)

            Fun.scale_render(WIN, surface_to_draw, CLOCK)
            pg.display.flip()

        CLOCK.tick(60)

    return map_data, event_data


def action_editor_func(WIN, CLOCK, action_to_edit, func_map, map_data=False):
    options = []
    # Add options to edit options
    for count, field in enumerate(action_to_edit):
        if field in ["Name", "Type"]:
            continue
        options.append({"Name": field, "Value": field, "On select": "Return", "Render func": "Text only"})
    options.append({"Name": "Exit", "Value": "Exit", "On select": "Return", "Render func": "Text only"})

    # toggle between single use or not. (default is not)
    menu_logic = Fun.UniversalMenuLogic(options, use_mouse_inputs=True, width=3)
    draw = True
    while True:
        # |Menu Logic|--------------------------------------------------------------------------------------------------
        do_shit = menu_logic.act(WIN, CLOCK)
        if do_shit or type(do_shit) != bool:
            if do_shit == "Exit":
                break
            else:
                if type(func_map[do_shit]) == bool:
                    action_to_edit[do_shit] = not action_to_edit[do_shit]
                elif type(func_map[do_shit]) == list and do_shit == "Conditions":
                    # Need a special function
                    pass
                elif type(func_map[do_shit]) == list and do_shit == "Pos":
                    action_to_edit[do_shit] = map_draw_tool(WIN, CLOCK, map_data["size"], [action_to_edit[do_shit]],
                                                            rect_list_colour=(255, 85, 0),
                                                            background_rect_lists=[map_data["map"], map_data["doors"], map_data["spawn point"]],
                                                            background_rect_lists_colours=[Fun.WHITE, Fun.RED, Fun.MAGENTA],
                                                            point_selection_mode=True)[0]
                # Handle list options
                elif type(func_map[do_shit]) == list:
                    old_value = action_to_edit[do_shit]
                    action_to_edit[do_shit] = Fun.pick_from_list_popup(WIN, CLOCK, action_to_edit[do_shit], func_map[do_shit])

                    if do_shit == "Action" and action_to_edit["Type"] == "sound":
                        if old_value != action_to_edit[do_shit]:
                            if old_value == "Play" or (old_value in ["Change", "Pause", "Stop"] and action_to_edit[do_shit] not in ["Change", "Pause", "Stop"]):
                                action_to_edit["Audio"] = "Silence"
                elif type(func_map[do_shit]) == int:
                    action_to_edit[do_shit] = float(Fun.text_input_menu(WIN, CLOCK, surface_to_draw, [100, 60], text=action_to_edit[do_shit], nums_only=True))
                elif type(func_map[do_shit]) == str:
                    action_to_edit[do_shit] = Fun.text_input_menu(WIN, CLOCK, surface_to_draw, [100, 60], text=action_to_edit[do_shit], nums_only=False)
                elif type(func_map[do_shit]) == dict and do_shit == "Audio":
                    # "Action"
                    action_to_edit[do_shit] = Fun.pick_from_list_popup(WIN, CLOCK, action_to_edit[do_shit],
                                                                           func_map[do_shit][
                                                                               {"Play": "Sound",
                                                                                "Change": "Music",
                                                                                "Pause": "Music",
                                                                                "Stop": "Music"}[action_to_edit["Action"]]
                                                                           ])
                elif type(func_map[do_shit]) == dict:
                    action_to_edit[do_shit] = Fun.pick_from_list_popup(WIN, CLOCK, action_to_edit[do_shit],
                                                                           func_map[do_shit][action_to_edit["Class"]])

            menu_logic.cooldown()

        # |Draw|------------------------------------------------------------------------------------------------------------
        if draw:
            # width, height = WIN.get_size()
            width, height = 630, 450
            frame = pg.Surface((630, 450))
            temp_ui_font = Fun.create_temp_font_1(height)
            surface_to_draw = frame
            WIN.fill(Fun.BLACK)

            surface_to_draw.fill(Fun.UI_COLOUR_BACKGROUND)

            # surface_to_draw.blit(temp_ui_font.render("", True, AMBER), (25 + x_mod, 25))
            menu_logic.draw(surface_to_draw, [5, 50])
            for count, x in enumerate(menu_logic.options):
                if x["Value"] not in action_to_edit:
                    continue
                surface_to_draw.blit(temp_ui_font.render(f"{action_to_edit[x["Value"]]}", True, Fun.AMBER), (10 + 80 + 24 * 3, 80 + 18 * count))

            Fun.scale_render(WIN, surface_to_draw, CLOCK)
            pg.display.flip()

        CLOCK.tick(60)
    #   spawn       (need a pos for all)
    #       entity  (a boss intro can be selected for bosses,
    #                default team is "Enemy", can be set to "Players" to have allies)
    #       item    (no angle needed, extra info might be asked based on the item)
    #       bullets
    #   despawn     (set a series of condition to chooses who to despawn
    #                2 despawn method,
    #                   soft: the thing takes max damage that can't be reduced
    #                   hard: the entity is removed from the list (dangerous)
    #                conditions can be: name, team, pos)
    #                   example condition
    #                       var name, check type, check against
    #                       ["team", "equal", "enemies"]
    #                       ["name", "in", ["ass", "butt"]]
    #                       ["health", "less", 20]
    #   level end
    #       win condition
    #       loss condition
    #   cutscene
    #   radio transmission


def dict_editing_func(WIN, CLOCK, dictionary_to_edit, map_data=[], map_blueprint=False):
    # Get a map of all the dictionary's fields and their data types
    dict_type_map = {}

    if not map_blueprint:
        dict_type_map = make_dict_type_map(dictionary_to_edit, output={})
    else:
        dict_type_map = map_blueprint
    #
    # types to support,
    #   - int/float
    #   - string
    #   - pos, (allways a list)


def make_dict_type_map(dictionary_to_map, output):
    for x in dictionary_to_map:
        var_type = type(dictionary_to_map[x])
        if var_type == dict:
            output.update({x: make_dict_type_map(dictionary_to_map[x], output={})})
        else:
            output.update({x: f"{type(dictionary_to_map[x]).__name__}"})
    return output


def free_var_editor_func_main_menu_handler(WIN, CLOCK, map_data, event_data):
    event_data["free var"] = free_var_editor_func(WIN, CLOCK, map_data, event_data, event_data["free var"])
    return WIN, empty_func, map_data, event_data


def free_var_editor_func(WIN, CLOCK, map_data, event_data, free_var_to_edit):
    options = []
    for f in free_var_to_edit:
        options.append(
            {"Name": f, "Value": free_var_to_edit[f], "On select": "Return", "Render func": "Text only"})
    options.append({"Name": "New free var.", "Value": "New", "On select": "Return", "Render func": "Text only"})
    options.append({"Name": "Exit", "Value": "Exit", "On select": "Return", "Render func": "Text only"})
    menu_logic = Fun.UniversalMenuLogic(options, use_mouse_inputs=True)
    frame = pg.Surface((630, 450))
    draw = True
    while True:

        # |Menu Logic|--------------------------------------------------------------------------------------------------
        do_shit = menu_logic.act(WIN, CLOCK)
        if do_shit or type(do_shit) != bool:
            if do_shit == "Exit":
                break
            elif do_shit == "New":
                # Pick name
                # Check if name exists
                while True:
                    potential_name = Fun.text_input_menu(WIN, CLOCK, surface_to_draw, [100, 60])

                    allow_name = True
                    if potential_name in free_var_to_edit:
                        allow_name = False
                        Fun.confirmation_popup(WIN, CLOCK, [315 - 128, 300],
                        [{"Name": "Okay....", "Value": "You suck!", "On select": "Return", "Render func": "Text only"}],
                                           text="Name is already taken. Choose another")

                    if allow_name:
                        break
                # Pick data type, string or int for now
                default_value = Fun.pick_from_list_popup(WIN, CLOCK, "Number", ["Number", "String"])
                # Apply
                free_var_to_edit.update({potential_name: {"String": "Default", "Number": 0}[default_value]})
            # Add a way to delete
            else:
                data_type = type(menu_logic.options[menu_logic.selected_option]["Value"])
                nums_only = data_type in [int, float]

                free_var_to_edit[menu_logic.options[menu_logic.selected_option]["Name"]] = Fun.text_input_menu(WIN, CLOCK, surface_to_draw, [100, 60], text=menu_logic.options[menu_logic.selected_option]["Value"], nums_only=nums_only)
                if nums_only:
                    free_var_to_edit[menu_logic.options[menu_logic.selected_option]["Name"]] = data_type(free_var_to_edit[menu_logic.options[menu_logic.selected_option]["Name"]])

            menu_logic.cooldown()
            options = [
            ]
            for f in free_var_to_edit:
                options.append(
                    {"Name": f, "Value": free_var_to_edit[f], "On select": "Return", "Render func": "Text only"})
            options.append({"Name": "New free var.", "Value": "New", "On select": "Return", "Render func": "Text only"})
            options.append({"Name": "Exit", "Value": "Exit", "On select": "Return", "Render func": "Text only"})
            menu_logic.options = options

        # |Draw|------------------------------------------------------------------------------------------------------------
        if draw:
            # width, height = WIN.get_size()
            width, height = 630, 450
            frame = pg.Surface((630, 450))
            surface_to_draw = frame
            WIN.fill(Fun.BLACK)

            surface_to_draw.fill(Fun.UI_COLOUR_BACKGROUND)

            # surface_to_draw.blit(temp_ui_font.render("", True, AMBER), (25 + x_mod, 25))
            menu_logic.draw(surface_to_draw, [5, 50])

            # temp_ui_font = Fun.create_temp_font_1(height)

            Fun.scale_render(WIN, surface_to_draw, CLOCK)
            pg.display.flip()

        CLOCK.tick(60)

    return free_var_to_edit


def metadata_editor_func(WIN, CLOCK, map_data, event_data):
    # Handles mission editing
    # Could add weather effects here
    options = [
        {"Name": "Name", "Value": "Name", "On select": "Return", "Render func": "Text only"},
        {"Name": "Characters", "Value": "Characters", "On select": "Return", "Render func": "Text only"},
        {"Name": "Starting Track", "Value": "Track", "On select": "Return", "Render func": "Text only"},
        # Weather
        {"Name": "Exit", "Value": "Exit", "On select": "Return", "Render func": "Text only"},
    ]
    menu_logic = Fun.UniversalMenuLogic(options, use_mouse_inputs=True)
    frame = pg.Surface((630, 450))
    draw = True
    while True:
        # |Menu Logic|--------------------------------------------------------------------------------------------------
        do_shit = menu_logic.act(WIN, CLOCK)
        if do_shit:
            if do_shit == "Name":
                event_data["name"] = Fun.text_input_menu(WIN, CLOCK, surface_to_draw, [100, 60], text=event_data["name"])
            if do_shit == "Characters":
                #
                character_options = []
                for count, character in enumerate(PLAYABLE_CHARACTERS):
                    character_options.append(
                        {"Name": character, "Value": character in event_data["Characters"], "On select": "Switch", "Render func": "Text only"})
                character_options.append(
                    {"Name": "Finish", "Value": "Exit", "On select": "Return", "Render func": "Text only"})
                character_list = Fun.confirmation_popup(WIN, CLOCK, [100, 60], character_options, text="", return_everything=True, show_value=True)
                empty_list = []
                for c in character_list:
                    if c["Value"] and type(c["Value"]) != str:
                        empty_list.append(c["Name"])

                if not empty_list:
                    empty_list = [PLAYABLE_CHARACTERS[0]]
                event_data["Characters"] = empty_list

            # Weather
            # Add required free vars for weather
            # let user choose starting weather
            # add notice that events can be used to change the weather
            if do_shit == "Exit":
                break
            menu_logic.cooldown()

        # |Draw|------------------------------------------------------------------------------------------------------------
        if draw:
            # width, height = WIN.get_size()
            width, height = 630, 450
            frame = pg.Surface((630, 450))
            surface_to_draw = frame
            WIN.fill(Fun.BLACK)

            surface_to_draw.fill(Fun.UI_COLOUR_BACKGROUND)

            # surface_to_draw.blit(temp_ui_font.render("", True, AMBER), (25 + x_mod, 25))
            menu_logic.draw(surface_to_draw, [5, 50])

            # temp_ui_font = Fun.create_temp_font_1(height)
            Fun.scale_render(WIN, surface_to_draw, CLOCK)
            pg.display.flip()

        CLOCK.tick(60)
    return frame, empty_func, map_data, event_data


# |Test functions|------------------------------------------------------------------------------------------------------
def empty_func(WIN, CLOCK, map_data, event_data):
    return EMPTY_FRAME, empty_func, map_data, event_data


#  Features
# -Support custom events stored in a python file
