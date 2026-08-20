import pygame as pg
import os
# import sys


import Fun
import Event
import Items
import Entity
# To add:
#   Adding free variables
#   Rendering generation
#   Pathfinding graph generator


EMPTY_MAP_DATA = {"map": [],
                  "doors": [],
                  'door state': [],
                  "rendering": {
                      "Segments": [], # {Rect: [x, y, w, h], T: []}
                      "Tile set": {}
                  },
                  "pathfinding": None, # {'points': {},  # "<id>": [<x>, <y>]'connections': {}  # "<id>": [<id of connected points>]},
                  "spawn point": [[5, 5, 1, 1]],
                  "size": [80*8, 56*8]
                  }
EMPTY_EVENT_DATA = {"events": {},
                    # "ID": ['ID', {'rects': [], 'Conditions': 'trigger_check_constant'}, <single use or not>, [effects], {<free var for event>}]
                    "free var": {},
                    "name": "Unnamed level"
}
EMPTY_FRAME = pg.Surface((630, 450), pg.SRCALPHA)
ALL_TRIGGER_FUNC = []
for f in dir(Event):
    if "trigger_check_" in f:
        ALL_TRIGGER_FUNC.append(f)
ALL_EVENT_ACTION_TYPE = [
    "spawn",
    "despawn",
    "door",
    "sound",
    "level end",
    "cutscene",
    "radio",
    "free var"
]


def main(WIN, CLOCK):
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
    #   {
    #       "events": [],
    #       "pathfinding": None,  # {'points': {},  # "<id>": [<x>, <y>]'connections': {}  # "<id>": [<id of connected points>]},
    #       "free var": {}
    #   }

    save_new_version = True
    options = [
        {"Name": "Map",             "Value": "Map",             "On select": "Return", "Render func": "Text only"},
        {"Name": "Events",          "Value": "Events",          "On select": "Return", "Render func": "Text only"},
        {"Name": "Free variable",   "Value": "Free variable",   "On select": "Return", "Render func": "Text only"},
        {"Name": "Metadata",        "Value": "Metadata",        "On select": "Return", "Render func": "Text only"},
        {"Name": "Save",            "Value": "Save",            "On select": "Return", "Render func": "Text only"},

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
            else:
                editor_func = {
                    # "Red": red_func, "Green": green_func, "Blue": blue_func,

                    "Map": map_editor_func,
                    "Events": event_editor_func,
                    "Free variable": free_var_editor_func,
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
            pg.display.update()

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


# |Map editing|---------------------------------------------------------------------------------------------------------
def map_editor_func(WIN, CLOCK, map_data, event_data):
    # Handles mission editing
    # Geometry handles everything that the player character sees and interacts with
    #   Layer 4     Rendering               (give the option to use an auto renderer at the start)
    #                   Tile set generator

    #   {
    #       "map":
    #       "doors":
    #       "rendering": {
    #             "Segments": [
    #             {
    #                'Rect': pg.Rect,   (area covered by the segment, user shouldn't need to touch that)
    #                'Walls': [],
    #                'Floor': [],
    #              }
    #             ],
    #             "Tile set": {<ID>: <file path for tile>, ...}
    #         }
    #   }
    options = [
        # {"Name": "Events", "Value": "Events", "On select": "Return", "Render func": "Text only"},
        {"Name": "Draw walls", "Value": "Walls", "On select": "Return", "Render func": "Text only"},
        {"Name": "Draw doors", "Value": "Doors", "On select": "Return", "Render func": "Text only"},
        {"Name": "Set door state", "Value": "Door state", "On select": "Return", "Render func": "Text only"},
        {"Name": "Spawn point", "Value": "Spawn", "On select": "Return", "Render func": "Text only"},
        # Rendering
        # Pathfinding?
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

                # TODO: Add a way to identify doors when setting their states. Use map drawing tool as a base
                door_states = Fun.confirmation_popup(WIN, CLOCK, [315 - 128, 30],
                                       state_options,
                                       text="Set door state", return_everything=True, show_value=True, popup_width=400)
                for count, x in enumerate(map_data["door state"]):
                    map_data["door state"][count] = door_states[count]["Value"]

            if do_shit == "Spawn":
                map_data["spawn point"] = map_draw_tool(WIN, CLOCK, map_data["size"], map_data["spawn point"], rect_list_colour=Fun.MAGENTA,
                                                        background_rect_lists=[map_data["map"], map_data["doors"]],
                                                        background_rect_lists_colours=[Fun.WHITE, Fun.RED],
                                                        point_selection_mode=True)
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
            pg.display.update()
        CLOCK.tick(60)
    return frame, empty_func, map_data, event_data


def map_draw_tool(WIN, CLOCK, size, rect_list, rect_list_colour=Fun.WHITE, background_rect_lists=[], background_rect_lists_colours=[], point_selection_mode=False):
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
            if point_selection_mode:
                canvas = pg.transform.scale(Fun.SPRITE_EMPTY, size)
            shape_type, shape_first_point = map_draw_tool_brushes(
                shape_type, canvas, rect_list_colour,
                [spacing_control(mouse_pos[0]), spacing_control(mouse_pos[1]),],
                shape_first_point, draw_size, scrolling, preview_only=False)
        if controller.input["Alt fire"] and not point_selection_mode:
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
            pg.display.update()
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

    if point_selection_mode:
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


# |Event editing|-------------------------------------------------------------------------------------------------------
def event_editor_func(WIN, CLOCK, map_data, event_data):
    # Handles mission editing
    #  Event trigger zones
    options = [

    ]
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
            pg.display.update()

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

                    event_data["events"][event_being_modified][4].update({"": ""})

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
                # Get all event free vars
                # Make a popup to edit them
                pass
            elif do_shit == "Exit":
                break
            else:
                # Get the event action
                event_action_modified = event_data["events"][event_being_modified][4]["Default Event Actions"][do_shit]
                change_event_type = event_action_modified["Type"] == ""

                # Pick an option
                if not change_event_type:
                    # TODO: Move these in the action editor menu to remove the popup
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
                                {"Entity": [e for e in Entity.unified_entity_repertory], "Item": [i for i in Items.item_repertory]}
                                      # TODO: Add boss intro and
                                      },
                            "despawn": {"Method": ["Soft", "Hard"], "Conditions": []},
                            "door": {"Door ID": [d for d, ignore in enumerate(map_data["doors"])], "Door state": True}, # Need a function to select doors visually
                            "sound": {"Action": ["Play", "Change", "Pause", "Stop"],
                                      "Audio": {"Sound": [s for s in Fun.sounds_dict], "Music": [s for s in Fun.music_dict]}},
                            "level end": {"End level state": ["win", " loss"]},
                            "cutscene": {},
                            "radio": {},
                            "free var": {"Target free var": [fv for fv in event_data["free var"]], "Operation": ["Addition", "Subtraction", "Multiplication", "Division", "Set"], "Value": 0}
                        }
                        print([d for d, ignore in enumerate(map_data["doors"])])

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
                        {
                            "spawn": {"Class": "Entity", "Pos": [0, 0, 1, 1], "Angle": 0, "ID": ""},
                            "despawn": {"Method": "Soft", "Conditions": []},
                            "door": {"Door ID": 0, "Door state": True},
                            "sound": {"Action": "Play", "Audio": "Silence"},
                            "level end": {"End level state": "win"},
                            "cutscene": {},     # AAAAAAAAAAAAAAAAAAAA
                            "radio": {},        # AAAAAAAAAAAAAAAAAAAA
                            "free var": {"Target free var": "", "Operation": "Addition", "Value": 0}
                        }[event_data["events"][event_being_modified][4]["Default Event Actions"][do_shit]["Type"]]
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
            pg.display.update()

        CLOCK.tick(60)

    return map_data, event_data


def action_editor_func(WIN, CLOCK, action_to_edit, func_map, map_data=False):
    # TODO: Implement event action editor
    #   change action arguments

    options = [
    ]
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
            pg.display.update()

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
    #
    #   door        (pick a door and set state either in open or closed)
    #   sound
    #       change music
    #       pause music
    #       stop music
    #       play sound
    #   level end
    #       win condition
    #       loss condition
    #   cutscene
    #   radio transmission
    #   free var manipulation


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


# print(make_dict_type_map({"A": 1, "B": {"C": [], "D": "1", "Alpha": {"Bitches": Fun.RED}}, "E": False}, {}))


def free_var_editor_func(WIN, CLOCK, map_data, event_data):
    # Handles mission editing
    options = [
    ]
    for f in event_data["free var"]:
        options.append({"Name": f, "Value": event_data["free var"][f], "On select": "Return", "Render func": "Text only"})
    options.append({"Name": "New free var.", "Value": "New", "On select": "Return", "Render func": "Text only"})
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
            elif do_shit == "New":
                # Pick name
                # Check if name exists
                # Pick data type, string or int for now
                pass
            else:
                nums_only = type(menu_logic.options[menu_logic.selected_option]) in [int, float]
                menu_logic.options[menu_logic.selected_option]["Value"] = Fun.text_input_menu(WIN, CLOCK, surface_to_draw, [100, 60], text=menu_logic.options[menu_logic.selected_option]["Value"], nums_only=nums_only)
                if nums_only:
                    menu_logic.options[menu_logic.selected_option]["Value"] = float(menu_logic.options[menu_logic.selected_option]["Value"])

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
            pg.display.update()

        CLOCK.tick(60)

    return frame, empty_func, map_data, event_data


def metadata_editor_func(WIN, CLOCK, map_data, event_data):
    # Handles mission editing
    options = [
        {"Name": "Name", "Value": "Name", "On select": "Return", "Render func": "Text only"},
        {"Name": "Starting Track", "Value": "Track", "On select": "Return", "Render func": "Text only"},
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
            pg.display.update()

        CLOCK.tick(60)

    return frame, empty_func, map_data, event_data


# |Test functions|------------------------------------------------------------------------------------------------------
def empty_func(WIN, CLOCK, map_data, event_data):
    return EMPTY_FRAME, empty_func, map_data, event_data


def red_func(WIN, CLOCK, map_data, event_data):
    red_frame = pg.Surface((630, 450))
    red_frame.fill((255, 0, 0))
    return red_frame, empty_func, map_data, event_data


def green_func(WIN, CLOCK, map_data, event_data):
    red_frame = pg.Surface((630, 450))
    red_frame.fill((0, 255, 0))
    return red_frame, empty_func, map_data, event_data


def blue_func(WIN, CLOCK, map_data, event_data):
    red_frame = pg.Surface((630, 450))
    red_frame.fill((0, 0, 255))
    return red_frame, empty_func, map_data, event_data


#  Features
# -Add mission events to a level
# 	A dict is processed by a "Basic event class" to handle radio transmissions, entity spawns, doors
# -Generate render for the level
# 	Reuse THR-1's Assault chunk system for rendering
# -Support custom events stored in a python file

# File structure
# >Master Levels Directory
# 	>Level Directory
# 	Custom.py				stores special event functions for the level
# 	Map_data_#.json			contains the level geometry, multiple files can be made to have multiple parts to a level and reduce memory usage.
#                               rendering data is also stored in there
# 						    	needs a way to load a map outside the level directory
# 	level_data.json		    contains mission events, name of mission, track to use, character to use and meta data
