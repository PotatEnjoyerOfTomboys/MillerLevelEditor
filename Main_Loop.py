import pygame as pg

import Render
import Event
import Fun


def main_loop(WIN, CLOCK, entities, level, party_info, scrolling, scrolling_target_entities, end_with_main_player=True):
    Fun.stop_music()
    gaming = True
    time_passed = 0
    main_player = Event.ENEMY_NO_OWNER
    if end_with_main_player:
        main_player = entities["entities"][0]

    end_status = "Loss"

    mission_end_screen = True
    big_game_loop = True

    scrolling_mod = 1
    while gaming:
        # Get inputs
        mouse_key = pg.mouse.get_pressed(3)
        keys = pg.key.get_pressed()
        force_pause = Fun.needed_in_menu_and_game(WIN, keys)

        act_limit = 960 * Fun.FRAME_MAX_SIZE[0] / 630
        # |Entities|--------------------------------------------------------------------------------------------
        player = entities["entities"][0]
        for count, entity in enumerate(entities["entities"]):
            if Fun.distance_between([scrolling[0] * -1, scrolling[1] * -1],
                                    entity.pos) > act_limit:  # Saves a lot of performances
                continue
            if entity.health <= 0:
                entity.death(entities, level, scrolling_target_entities)
                if entity.health <= 0:  # Condor/Vincent's last stand skill forced me to do that
                    if entity.team == "Players" and "NO DEATH MESSAGE" not in entity.free_var:
                        party_info[entity.name]["Death message"] = entity.free_var["Death message"]
                        # print(party_info[entity.name]["Death message"])
                    entities["entities"].pop(count)
                    continue

            # Anti-shadow realm measure
            if entity.pos[0] < 48: entity.pos[0] = 96
            if entity.pos[1] < 48: entity.pos[1] = 128
            if entity.pos[0] > level["width height"][0] - 32: entity.pos[0] = level["width height"][0] - 48 - 32
            if entity.pos[1] > level["width height"][1] - 32: entity.pos[1] = level["width height"][1] - 48 - 32

            entity.get_input(entities, level)  # Get inputs
            entity.act(entities, level)  # Do stuff with input

        # Does people die?
        if level["level_finished"]:
            gaming = False
            end_status = "Win"
            if "Loss" in level["free var"]:
                end_status = "Loss"
            mission_end_screen = True
        elif main_player.health <= 0:
            # gaming = False
            mission_end_screen = True
            big_game_loop = True

            level["events"].append(Event.MissionEvent("Finishing", Event.trigger_constant, False, [Event.loss]))
            scrolling_mod = 0

            # |Handle items|----------------------------------------------------------------------------------------
        for count, item in enumerate(entities["items"]):
            if Fun.distance_between([scrolling[0] * -1, scrolling[1] * -1],
                                    item.pos) > act_limit:  # Saves a lot of performances
                continue
            item.act(entities, level)
            if not item.alive:
                entities["items"].pop(count)

        # |Bullet|----------------------------------------------------------------------------------------------
        for count, bullet_to_act in enumerate(entities["bullets"]):
            bullet_to_act.hit_wall(entities, level)
            # Make the bullets do their stuff
            bullet_to_act.act(entities, level)
            # Remove any dead bullets
            if bullet_to_act.duration <= 0:
                entities["bullets"].pop(count)

        # |Sounds|----------------------------------------------------------------------------------------------
        for sound in enumerate(entities["sounds"]):
            sound[1].go_down()
            if sound[1].duration <= 0:
                entities["sounds"].pop(sound[0])

        # |Mission events|--------------------------------------------------------------------------------------
        scrolling_target = Fun.find_scrolling_target(scrolling_target_entities)
        level["scrolling target"] = scrolling_target
        for mission_event in level["events"]:
            if mission_event.status != 0:
                mission_event.act(entities, {}, level, time_passed, WIN, CLOCK)
        scrolling_target = level["scrolling target"]

        # Scrolling target
        if entities["screen shake"]:
            screen_shake = entities["screen shake"]  # Duration, strength, direction, max duration
            vel = screen_shake[1] * Fun.SCREEN_SHAKE_MOD[0] * (screen_shake[0] / screen_shake[1])
            scrolling = Fun.move_with_vel_angle(scrolling, vel * [1, -1][screen_shake[0] % 2], screen_shake[2])
            if screen_shake[2] > 1: screen_shake[2] -= 0.1
            screen_shake[0] -= 1
            if screen_shake[0] <= 0: entities["screen shake"] = []

        # Draw function
        Render.draw(WIN, CLOCK, time_passed, scrolling, scrolling_target, level, entities, scrolling_mod)
        entities["scrolling"] = scrolling
        time_passed += 1

        particle_limiter = round(CLOCK.get_fps())
        for limited_particle in ["background particles", "particles"]:
            for count, particle in enumerate(entities[limited_particle]):
                if particle.duration <= 0:
                    entities[limited_particle].pop(count)
                if particle_limiter < 50 and not particle.survive_wipe:
                    particle.duration = 0
        for count, particle in enumerate(entities["UI particles"]):
            if particle.duration <= 0:
                entities["UI particles"].pop(count)

        pg.display.update()
        # |Pause menu|------------------------------------------------------------------------------------------
        if Fun.SYSTEM_CONTROLS_INPUT["Pause"] or force_pause:
            gaming = not Fun.settings_menu(WIN, CLOCK, also_pause=True)
            # Refresh controls in game
            for p in scrolling_target_entities:
                p.control = Fun.get_from_json("Key binds.json", "Keyboard")
                p.mouse_control = Fun.get_from_json("Key binds.json", "Mouse")
                p.controller_control = Fun.get_from_json("Controller binds.json", "Everything")
            ppp = Fun.get_from_json("Key binds.json", "System")
            for i in ppp:
                Fun.SYSTEM_CONTROLS[i] = ppp[i]

            big_game_loop = gaming

        CLOCK.tick(60)
    Fun.stop_music()
    return end_status, mission_end_screen, big_game_loop, party_info, time_passed
