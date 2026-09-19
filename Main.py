import pygame as pg
import os
import random
import sys  # Cool video https://www.youtube.com/watch?v=2Yj5mmKWukw


pg.mixer.pre_init()
pg.init()
pg.joystick.init()


WIN_WIDTH, WIN_HEIGHT = 630, 450
ORIGINAL_WIDTH, ORIGINAL_HEIGHT = WIN_WIDTH, WIN_HEIGHT
WIN = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT), pg.RESIZABLE, pg.OPENGL | pg.DOUBLEBUF)
pg.display.set_icon(pg.image.load(os.path.join("Sprites/Icon.ico")))
pg.display.set_caption("THR-1's Assault")

CLOCK = pg.time.Clock()
pg.mixer.set_num_channels(32)



# Moved that here so that you don't start on a black screen
def pygame_splash_screen(WIN, CLOCK):
    width, height = 630, 450
    stage = 100
    sprite = pg.image.load(os.path.join("Sprites/pygame_ce_tiny.png")).convert_alpha()
    colour = [170, 238, 187]
    text_colour = [40, 40, 40]
    draw = True
    font = pg.font.SysFont("Sprites/JetBrainsMono-SemiBold.ttf", 25)
    while colour != [12, 12, 12] and stage > 0:
        # Handle events
        for event in pg.event.get():
            if event.type not in [pg.QUIT, pg.JOYDEVICEADDED, pg.JOYDEVICEREMOVED, pg.WINDOWFOCUSLOST, pg.VIDEORESIZE]:
                continue
            elif event.type == pg.QUIT:
                sys.exit()
            elif event.type == pg.VIDEORESIZE:
                width_e, height_e = event.size
                if width_e < 630:
                    width_e = 630
                if height_e < 450:
                    height_e = 450

                WIN = pg.display.set_mode((width_e, height_e), pg.RESIZABLE)
            elif event.type == pg.WINDOWFOCUSLOST:
                return True

        if colour == [12, 12, 12]:
            stage -= 1
        for x in range(3):
            if colour[x] > 12:
                colour[x] -= 2

                if colour[x] < 12:
                    colour[x] = 12

                if text_colour[x] < 255:
                    text_colour[x] += 2

                    if text_colour[x] > 255:
                        text_colour[x] = 255

        # |Draw|--------------------------------------------------------------------------------------------------------
        if draw:
            frame = pg.Surface((width, height))
            surface_to_draw = frame
            WIN.fill((0, 0, 0))
            surface_to_draw.fill(colour)
            surface_to_draw.blit(sprite, [315 - sprite.get_width() // 2, 225 - sprite.get_height() // 2])
            text = font.render(f"Made with", True, text_colour)
            surface_to_draw.blit(text, [315 - text.get_width() // 2, 110])


            width_s, height_s = WIN.get_size()
            slide_width, slide_height = [630, 450]  # 1.4

            # Get the smallest of the 2 dimensions
            if width_s != slide_width or height_s != slide_height:
                if width_s > height_s * 1.4:
                    slide_width = slide_width * height_s / slide_height
                    slide_height = height_s
                elif width_s < height_s:
                    slide_height = slide_height * width_s / slide_width
                    slide_width = width_s
                if width_s < height_s * 1.4:
                    slide_width = slide_width * height_s / slide_height
                    slide_height = height_s
                elif width_s > height_s:
                    slide_height = slide_height * width_s / slide_width
                    slide_width = width_s

            # This was added to handle the render zoom
            if slide_width > width_s or slide_height > height_s:
                if width_s > height_s * 1.4:
                    slide_width = slide_width * height_s / slide_height
                    slide_height = height_s
                elif width_s < height_s * 1.4:
                    slide_height = slide_height * width_s / slide_width
                    slide_width = width_s

            # Draw the stuff
            surface_to_draw = pg.transform.scale(surface_to_draw, (slide_width, slide_height))
            WIN.blit(surface_to_draw, (width_s // 2 - slide_width // 2, height_s // 2 - slide_height // 2))
            pg.display.flip()
            CLOCK.tick(60)


pygame_splash_screen(WIN, CLOCK)


import Fun  # General use functions
import Items   # Everything crashes if I remove that
import Event
import Render
import Entity
import Entity_Input_Funcs
import Main_Loop


def main_game(party_info):
    big_game_loop = True
    party_being_used = "THR-1"
    if "Curtis" in party_info:
        party_being_used = "Zoar"
    current_mission = 1
    run_info = {
        "Player party": player_party,
        "Missions completed": 0,
        "Time spend in mission": 0,
        "Mission historic": [],
        "Funds": 0,
        "Upgrades": [],
        "Available upgrades": [],
        "Upgrade pool": []
    }

    names = [name for name in party_info]
    for upgrade in Fun.UPGRADE_INFO:
        if Fun.UPGRADE_INFO[upgrade]["Tier"] != 1:
            continue
        if Fun.UPGRADE_INFO[upgrade]["Owner"] not in names and not Fun.UPGRADE_INFO[upgrade]["Owner"] == "Party":
            continue
        run_info["Upgrade pool"].append(upgrade)
    Fun.update_available_upgrades(run_info)
    # add upgrades to the upgrade pool
    end_status = "Loss"

    # Meta game loop
    level = {"name": "Shitass"}
    Fun.story_event(WIN, CLOCK, party_being_used, "Start")

    Fun.weapons_menu(WIN, CLOCK, party_info, run_info)
    while big_game_loop and current_mission <= 15:
        Fun.loading_screen(WIN, CLOCK)
        gaming = True
        load_level = True

        possible_levels = []
        # Check if it's a boss mission
        if current_mission in [5, 10]:
            boss_mission = [0, 1, 2]
            boss_mission.pop(Fun.get_random_element_from_list(boss_mission))
            for possible_level in boss_mission:
                l, ex = Fun.level_generator(possible_levels, party_info, run_info, current_mission=current_mission,
                                            faction=possible_level)
                possible_levels.append({"name": f"{possible_level}", "level": l, "extra info": ex})
        elif current_mission == 15:
            l, ex = Fun.level_generator(possible_levels, party_info, run_info, current_mission=current_mission)
            possible_levels.append({"name": f"{0}", "level": l, "extra info": ex})
        else:
            for possible_level in range(3):
                l, ex = Fun.level_generator(possible_levels, party_info, run_info, current_mission=current_mission,
                                            faction=possible_level)
                possible_levels.append({"name": f"{possible_level}", "level": l, "extra info": ex})

        # Add a menu to choose_weapons
        level, extra_info, party_info, out_party, give_up = Fun.mission_menu(WIN, CLOCK, possible_levels, party_info,
                                                                             run_info)
        if give_up:
            big_game_loop = False
            load_level = False
            # Fun.confirmation_popup(
            #         WIN, CLOCK, [350, 100],
            #         [
            #             {"Name": "OH SHIT", "Value": "Yes", "On select": "Return", "Render func": "Text only"}
            #         ],
            #     text="Game is about to crash out"
            # )
        if load_level:
            level.update({"Player party": player_party})
            entities = {"entities": [], "items": [], "sounds": [], "bullets": [],
                        "background particles": [], "particles": [], "UI particles": [], "screen shake": [],
                        "cutscene stage": 0, "shadows": [], "scrolling": [], "scrolling target": []}

            scrolling_target_entities = []  # Use that
            # Load up the party
            player_count = 0
            for count, player_to_add in enumerate(out_party):
                name = player_to_add[0]
                input_method = player_to_add[1]
                info = party_info[name]["Info"].copy()

                # Check if the character drives the APC
                if player_to_add[2]:
                    apc_info = Entity.player_repertory[
                        {"THR-1": "Fortress", "Zoar Colonists": "Sand Buggy"}[player_party]
                    ].copy()
                    for i in [
                        "health", "armour", "damage resistances", "thickness", "vel max", "speed", "friction",
                        "dash", "weapon", "skills", "func input", "func act", "func draw", "on death",
                        "targeting range", "targeting angle", "stealth mod", "stealth counter", "wall hack",
                        "free var"
                    ]:
                        info[i] = apc_info[i]
                    info["name"] = "APC"

                # Add default outline
                info["free var"].update({"Outline": Fun.OUTLINE_TEAL})

                # Manage input functions, default is AI
                if input_method == "Keyboard & Mouse":
                    info["func input"] = Entity.player_input_keyboard
                    info["free var"].update({"Outline": Fun.PLAYER_OUTLINE_COLOUR[player_count]})

                    player_count += 1
                elif input_method in ["Controller 1", "Controller 2", "Controller 3", "Controller 4"]:
                    info["func input"] = {
                        "Controller 1": Entity.player_input_controller_1,
                        "Controller 2": Entity.player_input_controller_2,
                        "Controller 3": Entity.player_input_controller_3,
                        "Controller 4": Entity.player_input_controller_4
                    }[input_method]
                    info["Input mode"] = "Controller"
                    info["free var"].update({"Outline": Fun.PLAYER_OUTLINE_COLOUR[player_count]})
                    player_count += 1

                # Add players in
                entities["entities"].append(Entity.Entity(info))
                last_added_entity = entities["entities"][-1]
                if input_method != "COM":
                    scrolling_target_entities.append(last_added_entity)
                    last_added_entity.is_player = True

                # Handle spawn points
                if count > 0:
                    mc = entities["entities"][0]
                    last_added_entity.pos = Fun.random_point_in_circle(mc.pos, 16)
                    last_added_entity.free_var["Ally waypoint"] = mc
                else:
                    last_added_entity.pos = extra_info["Spawn"].copy()

                # Change health
                if not player_to_add[2]:
                    last_added_entity.health = party_info[last_added_entity.name]["Health"]
                # Apply upgrades
                # Go though all bought upgrades
                # print(last_added_entity)
                for character_upgrade in run_info["Upgrades"]:
                    # print(character_upgrade)
                    upgrade_info = Fun.UPGRADE_INFO[character_upgrade]
                    # Apply them if the character can use them.


                # Reset the name to the correct one
                last_added_entity.name = name

            # Heal benched team members
            for team_member in party_info:
                member_benched = True
                for deployed_team_member in entities["entities"]:
                    if team_member == deployed_team_member.name:
                        member_benched = False
                        break
                if member_benched and (party_info[team_member]["Health"] > 0 or current_mission in [5, 10]):
                    party_info[team_member]["Health"] = Entity.player_repertory[team_member]["health"]

            # Load events
            new_events = []
            for events_to_load in level["events"]:
                event_name = events_to_load[0]
                event_trigger = Event.get_event_trigger(events_to_load[1])
                # event_functions = Event.get_event_function(events_to_load[3])
                event_functions = []
                for funcs in events_to_load[3]:
                    event_functions.append(getattr(Event, funcs))
                    # "Name", Event.relevant trigger, single use, Event.effects
                free_var = {}
                if len(events_to_load) == 5:
                    free_var = events_to_load[4]

                new_events.append(
                    Event.MissionEvent(event_name, event_trigger, events_to_load[2], event_functions,
                                       free_var=free_var))
            level["events"] = new_events

            # Spawn enemies
            for p in extra_info["Enemy spawns"]:
                Event.spawn_enemy(entities, p["Type"], Fun.random_point_in_circle(p["Pos"], 16), 360 * random.random())
                enemy = entities["entities"][-1]
                enemy.vel = Fun.move_with_vel_angle([0, 0], 6 + 2 * random.random(), enemy.angle)

            # Scrolling
            scrolling_target = Fun.find_scrolling_target(scrolling_target_entities)
            scrolling = scrolling_target
            entities["scrolling"] = scrolling
            # end_status = "Loss"
            # |Main game loop|------------------------------------------------------------------------------------------
            go_to_hub = False,  # mission_end_screen = False, True
            frame_2 = WIN.copy()
            Render.draw(WIN, CLOCK, 0, scrolling, scrolling_target, level, entities, 1)
            Fun.menu_transition_doom_screen_melt(WIN, CLOCK, WIN.copy(), frame_2)

            checked_time = False
            end_status, mission_end_screen, big_game_loop, party_info, time_spent = Main_Loop.main_loop(WIN, CLOCK, entities, level,
                                                                                            party_info, scrolling,
                                                                                            scrolling_target_entities)
            run_info["Time spend in mission"] += time_spent

            pg.mixer.music.fadeout(60)
            # |Mission end screen|----------------------------------------------------------------------------------
            if big_game_loop:
                # Save health to party info
                # For each member in the party
                deployed_team = []
                surviving_deployed_team = []
                for p in out_party:
                    deployed_team.append(p[0])
                    if p[2]:
                        surviving_deployed_team.append(p[0])
                        continue
                    # Assume death
                    party_info[p[0]]["Health"] = 0
                    # See if alive
                    for e in entities["entities"]:
                        if e.team == "Players":
                            # Add
                            # If Alive unmark death
                            if p[0] == e.name:
                                surviving_deployed_team.append(p[0])
                                party_info[e.name]["Health"] = e.health
                if end_status == "Win":
                    run_info["Funds"] += extra_info["Mission Reward"]
                    Fun.end_mission_menu(WIN, CLOCK, party_info, end_status, run_info, level, extra_info, deployed_team, surviving_deployed_team, entities, time_spent)
                    run_info["Missions completed"] += 1
                    run_info["Mission historic"].append({
                        "Name": level["name"], "Mission": current_mission, "Faction": level["faction"],
                        "Deployed team": deployed_team, "Surviving deployed team": surviving_deployed_team, "Objective": level["objective"]
                    })

                    if current_mission == 5:
                        Fun.story_event(WIN, CLOCK, party_being_used, "Event 1")
                    if current_mission == 10:
                        Fun.story_event(WIN, CLOCK, party_being_used, "Event 2")
                    current_mission += 1
                if end_status == "Loss":
                    big_game_loop = False

    # Run end screen
    Fun.end_run_menu(WIN, CLOCK, run_info, party_info, end_status)

    # Check if an ending should be played
    if current_mission >= 15 and end_status != "Loss":
        if level["name"] == Fun.write_textline("Finale 1"):
            Fun.story_event(WIN, CLOCK, party_being_used, "Ending Win")
        else:
            Fun.story_event(WIN, CLOCK, party_being_used, "Ending Loss")

    # Unlock stuff here
    # Check through the run history
    save_data = Fun.get_from_json("Save.json", "Everything")
    unlocked_weapons = save_data["Character weapons unlocked"]
    for m in run_info["Mission historic"]:
        # {'Player party': 'THR-1', 'Missions completed': 0, 'Mission historic': [], 'Funds': 0, 'Upgrades': [], 'Available upgrades': []}
        # {
        #                         "Name": level["name"], "Mission": current_mission, "Faction": level["faction"],
        #                         "Deployed team": deployed_team, "Surviving deployed team": surviving_deployed_team
        #                     }
        save_data["Faction mission count"][m["Faction"]] += 1
        # Unlock weapons
        if m["Mission"] == 5:
            for p in m["Surviving deployed team"]:
                if 1 not in unlocked_weapons[p]:
                    unlocked_weapons[p].append(1)
                    # Confirmation pop up
                    Fun.confirmation_popup(
                        WIN, CLOCK, [350, 100],
                        [{"Name": "Continue", "Value": "No", "On select": "Return", "Render func": "Text only"}],
                        text=f"New weapon unlocked - {Fun.weapon_ownership_table[p][1]}"
                    )
                Fun.weapon_entry_unlock({
                        "Lord": "GMG-04B",
                        "Emperor": "Corrine's Old Rifle",
                        "Wizard": "Custom Mk18 Laser cutter",
                        "Sovereign": "St-Laurent Gen 1",
                        "Duke": "Hook Swords",
                        "Jester": "Nihilist Stretcher",
                        "Condor": "Type 23 Shotgun",
                        "Curtis": "War and Peace",
                        "Lawrence": "Captain's Axe & Blunderbuss",
                        "Mark": "Type 30 Rifle",
                        "Vivianne": "Vivianne's Shotgun"
                }[p], save_data, WIN, CLOCK)
                if p == "Sovereign":
                    Fun.weapon_entry_unlock("Corrine's Hands", save_data, WIN, CLOCK)

            # unlock boss entries
            boss = [
                "Armed Shield Generator",
                "Hover Tank",
                "Fire Support Mech"][m["Faction"]]
            Fun.boss_entry_unlock(boss, m["Faction"], save_data, WIN, CLOCK)
        if m["Mission"] == 10:
            for p in m["Surviving deployed team"]:
                if 2 not in unlocked_weapons[p]:
                    unlocked_weapons[p].append(2)
                    # Confirmation pop up
                    Fun.confirmation_popup(
                        WIN, CLOCK, [350, 100],
                        [{"Name": "Continue", "Value": "No", "On select": "Return", "Render func": "Text only"}],
                        text=f"New weapon unlocked - {Fun.weapon_ownership_table[p][2]}"
                    )
                Fun.weapon_entry_unlock({
                        "Lord": "Big Iron",
                        "Emperor": "Oversized stun baton",
                        "Wizard": "Crippled Laddie FCS Radio",
                        "Sovereign": "Mk16 Flare Mortar",
                        "Duke": "Gun and Ballistic Knife",
                        "Jester": "Stoic Shield generator",
                        "Condor": "Type 47 Rifle",
                        "Curtis": "Hunk of Steel",
                        "Lawrence": "Musket .360",
                        "Mark": "C4",
                        "Vivianne": "Vivianne's Leg"
                }[p], save_data, WIN, CLOCK)
            # unlock boss entries
            boss = [
			"AA Site",
			"Gilgamesh",
			"Attack Helicopter"][m["Faction"]]
            Fun.boss_entry_unlock(boss, m["Faction"], save_data, WIN, CLOCK)
        # Unlock final bosses entries
        if m["Mission"] == 15:
            boss = "Rigel"
            if not run_info["Time spend in mission"] / 60 / 60 < 20:
                if "Curtis" not in party_info:
                    boss = "Curtis"
                else:
                    boss = "THR-1 (Throne)"
            Fun.boss_entry_unlock(boss, 3, save_data, WIN, CLOCK)
        # Unlock encyclopedia entries
        if m["Objective"] == "Eliminate Commander":
            Fun.enemy_entry_unlock("VIP", m["Faction"], save_data, WIN, CLOCK)

    # Unlock enemy entries
    for x in range(3):
        if save_data["Faction mission count"][x] >= 3:
            Fun.enemy_entry_unlock("Grunt", x, save_data, WIN, CLOCK)
        if save_data["Faction mission count"][x] >= 9:
            Fun.enemy_entry_unlock("Shock", x, save_data, WIN, CLOCK)
        if save_data["Faction mission count"][x] >= 18:
            Fun.enemy_entry_unlock("Support", x, save_data, WIN, CLOCK)
        if save_data["Faction mission count"][x] >= 27:
            Fun.enemy_entry_unlock("Specialist 1", x, save_data, WIN, CLOCK)
        if save_data["Faction mission count"][x] >= 36:
            Fun.enemy_entry_unlock("Specialist 2", x, save_data, WIN, CLOCK)
        if save_data["Faction mission count"][x] >= 45:
            Fun.enemy_entry_unlock("Elite", x, save_data, WIN, CLOCK)

    # unlock Zoar
    if current_mission == 15:
        if not save_data["Zoar unlocked"]:
            save_data["Zoar unlocked"] = True
            Fun.confirmation_popup(
                        WIN, CLOCK, Fun.UNLOCK_POPUP_POS,
                        [{"Name": "Continue", "Value": "No", "On select": "Return", "Render func": "Text only"}],
                        text=f"Zoar has been unlocked!", popup_width=Fun.UNLOCK_POPUP_WIDTH
                    )
        # unlock Zoar default weapons
        for gun in ["Standard Shotgun", "Cowboy's Repeater", "Lawrence's Cutlass & Flintlock", "Mark's Rifle", "Vivianne's Rifle"]:
            Fun.weapon_entry_unlock(gun, save_data, WIN, CLOCK)
        if "NEST" not in save_data["Databank entries unlocked"]:
            try:
                if level['name'] == Fun.write_textline("Finale 1"):
                    save_data["Databank entries unlocked"].append("NEST")
                    Fun.confirmation_popup(
                                WIN, CLOCK, Fun.UNLOCK_POPUP_POS,
                                [{"Name": "Continue", "Value": "No", "On select": "Return", "Render func": "Text only"}],
                                text=f"Entry 'NEST' added to Databank in 'Root\Organizations\Armed groups'", popup_width=Fun.UNLOCK_POPUP_WIDTH
                            )
            except NameError:
                pass
    save_data["Character weapons unlocked"] = unlocked_weapons
    Fun.dict_to_json("Save.json", save_data)


def versus_mode(party_info):
    while True:
        # Menus

        Fun.loading_screen(WIN, CLOCK)
        gaming = True
        load_level = True

        possible_levels = []
        for p in os.listdir(f'Maps/Versus mode'):
            if os.path.splitext(f'Maps/Versus mode/{p}')[1] in [".png"]:
                l, ex = Fun.versus_level_generator(possible_levels, party_info, p)
                possible_levels.append({"name": f"{p}", "level": l, "extra info": ex})

        # Modified mission selection menu to let choose between versus maps
        level, extra_info, party_info, out_party, give_up = Fun.versus_arena_menu(WIN, CLOCK, possible_levels, party_info)

        if give_up:
            return

        # Load level
        entities = {"entities": [], "items": [], "sounds": [], "bullets": [],
                    "background particles": [], "particles": [], "UI particles": [], "screen shake": [],
                    "cutscene stage": 0, "shadows": [], "scrolling": [], "scrolling target": []}

        scrolling_target_entities = []  # Use that
        # Load up the party
        player_count = 0
        for count, player_to_add in enumerate(out_party):
            name = player_to_add[0]
            input_method = player_to_add[1]
            info = party_info[name]["Info"].copy()

            # Manage input functions, default is AI
            if input_method == "Keyboard & Mouse":
                info["func input"] = Entity.player_input_keyboard

            elif input_method in ["Controller 1", "Controller 2", "Controller 3", "Controller 4"]:
                info["func input"] = {
                    "Controller 1": Entity.player_input_controller_1,
                    "Controller 2": Entity.player_input_controller_2,
                    "Controller 3": Entity.player_input_controller_3,
                    "Controller 4": Entity.player_input_controller_4
                }[input_method]
                info["Input mode"] = "Controller"

            # Change weapons
            info["weapon"] = player_to_add[2]

            # Add outline based on position number and players in
            info["free var"].update({"Outline": Fun.PLAYER_OUTLINE_COLOUR[player_count]})
            entities["entities"].append(Entity.Entity(info))
            last_added_entity = entities["entities"][-1]
            scrolling_target_entities.append(last_added_entity)

            player_count += 1
            last_added_entity.team = f"Player {player_count}"

            if input_method != "COM":
                # New AI for COM?
                last_added_entity.is_player = True

            # Handle spawn points
            num = random.randint(0, len(extra_info["Spawn"])-1)
            last_added_entity.pos = extra_info["Spawn"][num]
            extra_info["Spawn"].pop(num)

            # Reset the name to the correct one
            last_added_entity.name = name
            last_added_entity.ai_state = "Attack"
            last_added_entity.force_draw = True
            last_added_entity.max_health *= 5
            last_added_entity.health *= 5
            last_added_entity.max_armour *= 5
            last_added_entity.armour *= 5
            last_added_entity.armour *= 5
            last_added_entity.targeting_angle = 180
            last_added_entity.targeting_range = 1280
            last_added_entity.free_var.update({"IS VERSUS": True})

        # Load events
        new_events = []
        for events_to_load in level["events"]:
            event_name = events_to_load[0]
            event_trigger = Event.get_event_trigger(events_to_load[1])
            # event_functions = Event.get_event_function(events_to_load[3])
            event_functions = []
            for funcs in events_to_load[3]:
                event_functions.append(getattr(Event, funcs))
                # "Name", Event.relevant trigger, single use, Event.effects
            free_var = {}
            if len(events_to_load) == 5:
                free_var = events_to_load[4]

            new_events.append(
                Event.MissionEvent(event_name, event_trigger, events_to_load[2], event_functions,
                                   free_var=free_var))
        level["events"] = new_events

        # Scrolling
        scrolling_target = Fun.find_scrolling_target(scrolling_target_entities)
        scrolling = scrolling_target
        entities["scrolling"] = scrolling

        # |Main game loop|------------------------------------------------------------------------------------------
        go_to_hub = False,  # mission_end_screen = False, True

        frame_2 = WIN.copy()
        Render.draw(WIN, CLOCK, 0, scrolling, scrolling_target, level, entities, 1)
        Fun.menu_transition_doom_screen_melt(WIN, CLOCK, WIN.copy(), frame_2)

        checked_time = False
        end_status, mission_end_screen, big_game_loop, party_info, time_spent = Main_Loop.main_loop(WIN, CLOCK, entities, level,
                                                                                        party_info, scrolling,
                                                                                        scrolling_target_entities,
                                                                                        end_with_main_player=False)
        pg.mixer.music.fadeout(60)
        # |Mission end screen|----------------------------------------------------------------------------------
        if big_game_loop:

            Fun.versus_end_menu(WIN, CLOCK, party_info, end_status)


def custom_level(level_to_load="Ass Cheeks"):
    big_game_loop = True

    while big_game_loop:
        Fun.loading_screen(WIN, CLOCK)
        load_level = True
        # Choose level here

        if load_level:
            # Get event from JSON
            level = Event.load_level(level_to_load)

            # Set up the rests
            entities = {"entities": [], "items": [], "sounds": [], "bullets": [],
                        "background particles": [], "particles": [], "UI particles": [], "screen shake": [],
                        "cutscene stage": 0, "shadows": [], "scrolling": [], "scrolling target": [], "WIN": WIN}

            scrolling_target_entities = []  # Use that
            # Load up the party
            player_count = 0

            player_character = level["characters"][0]
            if len(level["characters"]) != 1:
                character_options = []
                for character in level["characters"]:
                    character_options.append({"Name": character, "Value": character, "On select": "Return", "Render func": "Text only"})
                player_character  = Fun.confirmation_popup(WIN, CLOCK, [100, 60], character_options, text="")

            out_party = [[player_character, "Keyboard & Mouse"]]
            for count, player_to_add in enumerate(out_party):
                name = player_to_add[0]
                input_method = player_to_add[1]
                info = Entity.player_repertory[name]

                # Add default outline
                info["free var"].update({"Outline": Fun.OUTLINE_TEAL})

                # Manage input functions, default is AI
                if input_method == "Keyboard & Mouse":
                    info["func input"] = Entity_Input_Funcs.player_input_keyboard
                    info["free var"].update({"Outline": Fun.PLAYER_OUTLINE_COLOUR[player_count]})

                    player_count += 1
                elif input_method in ["Controller 1", "Controller 2", "Controller 3", "Controller 4"]:
                    info["func input"] = {
                        "Controller 1": Entity_Input_Funcs.player_input_controller_1,
                        "Controller 2": Entity_Input_Funcs.player_input_controller_2,
                        "Controller 3": Entity_Input_Funcs.player_input_controller_3,
                        "Controller 4": Entity_Input_Funcs.player_input_controller_4
                    }[input_method]
                    info["Input mode"] = "Controller"
                    info["free var"].update({"Outline": Fun.PLAYER_OUTLINE_COLOUR[player_count]})
                    player_count += 1

                # Add players in
                entities["entities"].append(Entity.Entity(info))
                last_added_entity = entities["entities"][-1]
                if input_method != "COM":
                    scrolling_target_entities.append(last_added_entity)
                    last_added_entity.is_player = True

                # Handle spawn points
                if count > 0:
                    mc = entities["entities"][0]
                    last_added_entity.pos = Fun.random_point_in_circle(mc.pos, 16)
                    last_added_entity.free_var["Ally waypoint"] = mc
                else:
                    last_added_entity.pos = level["spawn point"].copy()

                # Reset the name to the correct one
                last_added_entity.name = name

            # Load events
            new_events = []
            for events_to_load in level["events"]:
                event_name = events_to_load[0]
                event_trigger = Event.get_event_trigger(events_to_load[1])
                # event_functions = Event.get_event_function(events_to_load[3])
                event_functions = []
                for funcs in events_to_load[3]:
                    event_functions.append(getattr(Event, funcs))
                    # "Name", Event.relevant trigger, single use, Event.effects
                free_var = {}
                if len(events_to_load) == 5:
                    free_var = events_to_load[4]

                new_events.append(
                    Event.MissionEvent(event_name, event_trigger, events_to_load[2], event_functions,
                                       free_var=free_var))
            level["events"] = new_events

            # Scrolling
            scrolling_target = Fun.find_scrolling_target(scrolling_target_entities)
            scrolling = scrolling_target
            entities["scrolling"] = scrolling

            # |Main game loop|------------------------------------------------------------------------------------------
            frame_2 = WIN.copy()
            Render.draw(WIN, CLOCK, 0, scrolling, scrolling_target, level, entities, 1)
            Fun.menu_transition_doom_screen_melt(WIN, CLOCK, WIN.copy(), frame_2)

            end_status, mission_end_screen, big_game_loop, time_spent = Main_Loop.main_loop_no_party(
                WIN, CLOCK, entities, level, scrolling, scrolling_target_entities
            )

            pg.mixer.music.fadeout(60)
            # |Mission end screen|----------------------------------------------------------------------------------


if __name__ == "__main__":
    # |Load controls and save|------------------------------------------------------------------------------------------
    try:
        save_data = Fun.get_from_json("Save.json", "Everything")
        # Convert data file if needed
        for field_to_check in Fun.EMPTY_SAVE_FILE:
            if field_to_check not in save_data:
                Fun.print_to_error_stream(f"Whoops, someone doesn't have '{field_to_check}' in his save file")
                save_data.update({field_to_check: Fun.EMPTY_SAVE_FILE[field_to_check]})
                save_data.update({"Version": Fun.VERSION})
                Fun.dict_to_json("Save.json", save_data)
                Fun.print_to_error_stream("Fixed!")
        # Fun.weapon_entry_unlock("Big Iron", save_data, WIN, CLOCK)
    except FileNotFoundError:
        Fun.print_to_error_stream("Save.json not found, creating new one")
        Fun.dict_to_json("Save.json", Fun.EMPTY_SAVE_FILE)

    save_data =  Fun.get_from_json("Save.json", "Everything")
    # Load control
    try:
        controls = Fun.PseudoPlayer().control
        Fun.SYSTEM_CONTROLS = Fun.get_from_json("Key binds.json", "System")
    except FileNotFoundError:
        Fun.print_to_error_stream("Key binds.json not found, creating new one")
        Fun.dict_to_json("Key binds.json", Fun.DEFAULT_KEY_BINDS)
        controls = Fun.PseudoPlayer().control

    Fun.my_own_shit(WIN, CLOCK)
    Fun.title_screen(WIN, CLOCK, controls)

    while True:
        player_party = Fun.main_menu(WIN, CLOCK)
        if player_party == "Custom Levels":
            custom_level()
        else:
            create_char_party_info = lambda char_name: {
                "Name": char_name,
                "Health": Entity.player_repertory[char_name]["health"],
                "Death message": "",
                "Info": Entity.player_repertory[char_name].copy(),
            }

            party_info = {
                "THR-1": {
                    "Lord": create_char_party_info("Lord"),
                    "Emperor": create_char_party_info("Emperor"),
                    "Wizard": create_char_party_info("Wizard"),
                    "Sovereign": create_char_party_info("Sovereign"),
                    "Duke": create_char_party_info("Duke"),
                    "Jester": create_char_party_info("Jester"),
                    "Condor": create_char_party_info("Condor"),
                },
                "Zoar Colonists": {
                    "Curtis": create_char_party_info("Curtis"),
                    "Lawrence": create_char_party_info("Lawrence"),
                    "Vivianne": create_char_party_info("Vivianne"),
                    "Mark": create_char_party_info("Mark"),
                },
                "Versus": {
                    "Lord": create_char_party_info("Lord"),
                    "Emperor": create_char_party_info("Emperor"),
                    "Wizard": create_char_party_info("Wizard"),
                    "Sovereign": create_char_party_info("Sovereign"),
                    "Duke":create_char_party_info("Duke"),
                    "Jester": create_char_party_info("Jester"),
                    "Condor": create_char_party_info("Condor"),

                    "Curtis": create_char_party_info("Curtis"),
                    "Lawrence": create_char_party_info("Lawrence"),
                    "Vivianne": create_char_party_info("Vivianne"),
                    "Mark": create_char_party_info("Mark"),
                }
            }[player_party].copy()

            if player_party == "Versus":
                versus_mode(party_info)
            else:
                main_game(party_info)
        #
    #