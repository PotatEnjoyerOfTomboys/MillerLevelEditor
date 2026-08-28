import pygame as pg
import sys
import random

import Bullets
import Items
import Particles
import Fun


TILES_DICT = {
    "Industrial Floor": Fun.TILE_SET_INDUSTRIAL_FLOOR,
    "Industrial Walls": Fun.TILE_SET_INDUSTRIAL_WALL,

    "Entry Gate Floor": Fun.TILE_SET_ENTRY_GATE_FLOOR,
    "Entry Gate Walls": Fun.TILE_SET_ENTRY_GATE_WALL,

    "Red Desert Floor": Fun.TILE_SET_RED_DESERT_FLOOR,
    "Red Desert Walls": Fun.TILE_SET_RED_DESERT_WALL,

    "Sand Cave Floor":  Fun.TILE_SET_SAND_CAVES_FLOOR,
    "Sand Cave Walls":  Fun.TILE_SET_SAND_CAVES_WALL,

    "Iron Mine Floor":  Fun.TILE_SET_IRON_MINES_FLOOR,
    "Iron Mine Walls":  Fun.TILE_SET_IRON_MINES_WALL,

    "Salt Flats Floor": Fun.TILE_SET_SALT_FLATS_FLOOR,
    "Salt Flats Walls": Fun.TILE_SET_SALT_FLATS_WALL,

    "Paved Road":       Fun.TILE_SET_PAVED_ROAD,
    "Interior Tiles":   Fun.TILE_SET_INTERIOR_TILES,

    "Sewers Bars":      Fun.TILE_SET_SEWERS_BARS,
    "Sewers Walls":     Fun.TILE_SET_SEWERS_WALL,
    "Sewers Floor":     Fun.TILE_SET_SEWERS_FLOOR
}


def cutscene_reset(entities):
    entities["cutscene stage"], Fun.CUTSCENE_SKIP_TIMER[0] = 0, 0


class MissionEvent:
    def __init__(self, name, trigger, single_use, effect, free_var={}):
        self.name = name
        self.status = 1

        # Trigger system
        # Triggers are used to start a mission event handles lots of things like
        # Enemy spawn, win/loss conditions, warp

        self.trigger_rects = trigger["rects"]  # List of rectangle used to trigger the event in some situations
        self.trigger = trigger["Conditions"]  # What causes the event to start, it's a function
        # conditions types
        #   box, uses the rectangles to check if an entity has collided with the trigger to start it
        #   time,

        self.single_use = single_use  # Make the event stop working if has been activated once

        self.effect = effect  # List of functions that made the event do stuff

        self.free_var = free_var.copy()  # This would probably allow me to let people make custom levels

    def act(self, entities, bullets, level, time_passed, screen, CLOCK):
        if self.trigger(self, entities, bullets, level, time_passed):
            for effects in self.effect:
                effects(self, entities, bullets, level, time_passed, screen, CLOCK)

            if self.single_use:
                self.status = 0


def weather_handler(self, entities, bullets, level, time_passed, screen, CLOCK):
    player = entities["players"][0]
    if not level["free var"]["Is inside"]:
        if level["free var"]["Weather"] == "Rainy":
            Particles.rain_fall(entities, player.pos, 630)
        elif level["free var"]["Weather"] == "Windy":
            if len(entities["particles"]) <= 5000 and random.randint(0, 1) == 0:
                true_pos = Fun.random_point_in_circle(player.pos, 630)

                duration = random.randint(60, 120)

                if time_passed % 500 > 425:
                    entities["particles"].append(Particles.Leaf([true_pos[0], true_pos[1] - 100],
                                                          x_speed=random.uniform(0.25, 3)))
                elif random.random() < 0.125:
                    entities["particles"].append(Particles.RandomParticle2(true_pos, Fun.ORANGE, random.uniform(2, 6),
                                                                     duration, 180, size=random.randint(2, 5)))
                else:
                    entities["particles"].append(Particles.RandomParticle3(true_pos, Fun.WHITE, random.uniform(2, 6),
                                                                     duration, 180, (-120 + duration) * 0.0125,
                                                                     size=2))

        elif level["free var"]["Weather"] == "Sandstorm":
            if len(entities["particles"]) <= 5000:
                true_pos = Fun.random_point_in_circle(player.pos, 630 * 0.75)
                duration = random.randint(60, 120)

                entities["particles"].append(Particles.RandomParticle2(true_pos, Fun.ORANGE, random.uniform(2, 6),
                                                                 duration, 180, size=random.randint(2, 5)))

                if time_passed % 4500 > 4000:
                    for x in range(3):
                        true_pos = Fun.random_point_in_circle(player.pos, 630 * 0.5)
                        true_pos[0] -= screen.get_size()[0] * 0.5
                        duration = random.randint(60, 120) * 3
                        entities["particles"].append(Particles.RandomParticle2(true_pos, Fun.ORANGE, random.uniform(2, 6),
                                                                         duration, 180, size=random.randint(2, 5)))


def radio_handler(entities, transmission, cooldown=3):
    # This is just way better
    for x in entities["UI particles"]:
        if type(x) == Particles.RadioTransmission:
            for t in transmission:
                x.extra_parts.append(t)
            return
    entities["UI particles"].append(Particles.RadioTransmission(Fun.SPRITE_RADIO_VIVIANNE[4], [], Fun.WHITE, 0,
                                                          extra_parts=transmission, cooldown=3))


# |Enemy Spawn Function|------------------------------------------------------------------------------------------------
def spawn_enemy(entities, enemy: str, pos: [int, int], angle: float, team="Enemies"):
    # entities  :
    # enemy     : name of the enemy/boss you want to spawn (use the name present in the repertory)
    # pos       : x and y coordinates [x, y]
    # angle     : which direction the enemy will look toward,
    #               0 is left,
    #               90 is top,
    #               180 is right,
    #               -90 is bottom
    #             You can use any number between -180 and 180, if you use any other the game might crash
    # temp_repertory = Fun.get_from_json('Game asset.json', )
    if type(enemy) != str:
        Fun.print_to_error_stream(f"Error, I need a string brother")
        Fun.print_to_error_stream(f"You gave me this: {enemy}")
        return
    if enemy in Entity.enemy_repertory:
        # entities["entities"].append(Enemies.Enemy(Enemies.enemy_repertory[enemy], pos, angle))
        info = Entity.enemy_repertory[enemy]

        info["free var"].update({"Outline": {
            "FAC-1": Fun.OUTLINE_ENEMIES_FACTION_1,
            "FAC-2": Fun.OUTLINE_ENEMIES_FACTION_2,
            "FAC-3": Fun.OUTLINE_ENEMIES_FACTION_3,

            "Pirate": Fun.OUTLINE_ENEMIES_FACTION_1,
            "Street Gang": Fun.OUTLINE_ENEMIES_FACTION_2,
            "CommieBot": Fun.OUTLINE_ENEMIES_FACTION_3,
            "Nest": Fun.OUTLINE_ENEMIES_FACTION_2,

            "Test": (0, 0, 0),
            "Anomalies": (0, 0, 0),

            "Zoar Colonists": (0, 0, 0),
            "THR-1": (0, 0, 0),
        }[info["faction"]]
        })

        entities["entities"].append(Entity.Entity(info, team=team, pos=pos, start_angle=angle))
        if info["faction"] == 'THR-1':
            entities["entities"][-1].ai_state = "Attack"
        return

    Fun.print_to_error_stream(f"Error {enemy} does not exist")


def spawn_ally(entities, ally: str, pos: [int, int], angle: int):
    # entities  :
    # enemy     : name of the ally you want to spawn (use the name present in the repertory)
    # pos       : x and y coordinates [x, y]
    # angle     : which direction the enemy will look toward,
    #               0 is left,
    #               90 is top,
    #               180 is right,
    #               -90 is bottom
    #             You can use any number between -180 and 180, if you use any other the game might crash

    if ally in Entity.player_repertory:
        entities["entities"].append(Entity.Entity(Entity.player_repertory[ally], pos=pos, start_angle=angle))
        # info, team="Players", pos=[0, 0], start_angle=0
        return
    Fun.print_to_error_stream(f"Error {ally} does not exist")


# The event system work by using triggers to check if the event should happen and effects that are what the event cause
# |Generic trigger functions|-------------------------------------------------------------------------------------------
def get_event_trigger(trigger_to_load):
    new_trigger = {"rects": [], "Conditions": False}
    # Load rects
    for rect in trigger_to_load["rects"]:
        new_trigger["rects"].append(pg.Rect(rect[0], rect[1], rect[2], rect[3]))
    # Load the trigger function
    new_trigger["Conditions"] = getattr(sys.modules[__name__], trigger_to_load["Conditions"])
    return new_trigger


def trigger_check_constant(self, entities, bullets, level, time_passed):
    return True


def trigger_check_rect(self, entities, bullets, level, time_passed):
    for rect in self.trigger_rects:
        if rect.colliderect(entities["entities"][0].collision_box):
            return True


def trigger_check_rect_everyone(self, entities, bullets, level, time_passed):
    for rect in self.trigger_rects:
        for e in entities["entities"]:
            if rect.colliderect(e.collision_box):
                return True


def trigger_check_mission_start(self, entities, bullets, level, time_passed):
    return time_passed == 0


def trigger_check_mission_end(self, entities, bullets, level, time_passed):
    return level["level_finished"]


def trigger_check_mission_game_over(self, entities, bullets, level, time_passed):
    return entities["players"][0].health <= 0


# General enemy checks
def trigger_check_zero_enemies(self, entities, bullets, level, time_passed):
    for e in entities["entities"]:
        if e.team != "Players":
            return False
    return True


def trigger_check_zero_vip(self, entities, bullets, level, time_passed):
    for e in entities["entities"]:
        if "Is VIP" in e.free_var:
            return False
    return True


def trigger_check_zero_boss(self, entities, bullets, level, time_passed):
    for e in entities["entities"]:
        if "IS BOSS" in e.free_var:
            return False
    return True


def trigger_check_boss_alive(self, entities, bullets, level, time_passed):
    for e in entities["entities"]:
        if "IS BOSS" in e.free_var:
            return True
    return False


def trigger_check_under_specified_amount_enemies(self, entities, bullets, level, time_passed):
    l = []
    for e in entities["entities"]:
        if e.team == "Players": continue
        l.append(e)
    return len(l) <= self.free_var["Specified amount"]


def trigger_check_no_enemies_in_rect(self, entities, bullets, level, time_passed):
    for rect in self.trigger_rects:
        for enemy in entities["enemies"]:
            if rect.colliderect(enemy.collision_box):
                return False
    return True


def trigger_check_enemies_in_rect(self, entities, bullets, level, time_passed):
    for rect in self.trigger_rects:
        for enemy in entities["enemies"]:
            if rect.colliderect(enemy.collision_box):
                return True
    return False


def trigger_check_finished_encounter(self, entities, bullets, level, time_passed):
    if level["free var"][self.name] == 1:
        return trigger_check_zero_enemies(self, entities, bullets, level, time_passed)


def trigger_check_timer(self, entities, bullets, level, time_passed):
    self.free_var["Timer"] -= 1
    return self.free_var["Timer"] == 0


def trigger_check_timer_on(self, entities, bullets, level, time_passed):
    self.free_var["Timer"] -= 1
    return self.free_var["Timer"] >= 0


# Cutscene related
def trigger_check_cutscene_done(self, entities, bullets, level, time_passed):
    for t in ["players", "enemies"]:
        for e in entities[t]:
            if e.cutscene_mode:
                return False
    return True


def trigger_check_for_time(self, entities, bullets, level, time_passed):
    if time_passed >= self.free_var["Time target"]:
        return True
    return False


# def trigger_check_m6e_end(self, entities, bullets, level, time_passed): old name for the function
def trigger_check_encounter_waves(self, entities, bullets, level, time_passed):
    # I love this function
    # "Specified amount" "E. num stage" "E. num ref"
    if int(level["free var"][self.free_var["E. num ref"]]) == int(self.free_var["E. num stage"]):
        value = trigger_check_under_specified_amount_enemies(self, entities, bullets, level, time_passed)
        if value:
            level["free var"][self.free_var["E. num ref"]] += 1
        return value


# |Triggers|------------------------------------------------------------------------------------------------------------
trigger_mission_start = {"rects": [], "Conditions": trigger_check_mission_start}
trigger_timer = {"rects": [], "Conditions": trigger_check_timer}
trigger_on_for = {"rects": [], "Conditions": trigger_check_timer_on}
trigger_mission_end = {"rects": [], "Conditions": trigger_check_mission_end}
trigger_mission_game_over = {"rects": [], "Conditions": trigger_check_mission_game_over}
trigger_no_enemies = {"rects": [], "Conditions": trigger_check_zero_enemies}
trigger_yes_boss = {"rects": [], "Conditions": trigger_check_boss_alive}
trigger_constant = {"rects": [], "Conditions": trigger_check_constant}
trigger_e_finished = {"rects": [], "Conditions": trigger_check_finished_encounter}


def generic_event(self, entities, bullets, level, time_passed, screen, CLOCK):
    # Do shit with generic events
    for a in self.free_var["Default Event Actions"]:
        # print(a["Name"])
            #   level end
            #       win condition
            #       loss condition
            #   cutscene
            #   radio transmission
        try:

            {
                "spawn": generic_event_spawn,
                "despawn": generic_event_despawn,
                "door": generic_event_door,
                "sound": generic_event_sound,
                "level end": generic_event_level_end,
                "cutscene": generic_event_cutscene,
                "radio": generic_event_radio,
                "free var": generic_event_free_var
             }[a["Type"]](self, entities, bullets, level, time_passed, a)
            #                             "level end": {"End level state": "win"},
            #                             "cutscene": {},     # AAAAAAAAAAAAAAAAAAAA
            #                             "radio": {},        # AAAAAAAAAAAAAAAAAAAA
        except Exception as e:
            Fun.print_to_error_stream(f"Event: {self.name}, Action: {a['Name']}")
            Fun.print_to_error_stream(f"{a}")
            Fun.print_to_error_stream(f"An error occurred: {e}")



def generic_event_spawn(self, entities, bullets, level, time_passed, info):
    #       entity  (a boss intro can be selected for bosses,
    #                default team is "Enemy", can be set to "Players" to have allies)
    #       item    (no angle needed, extra info might be asked based on the item)
    #       bullets
    #                             "spawn": {"Class": "Entity", "Pos": [0, 0, 1, 1], "Angle": 0, "ID": ""},
    if info["Class"] == "Item":
        Items.spawn_item(entities, info["ID"], info["Pos"])
    if info["Class"] == "Entity":
        spawn_enemy(entities, info["ID"], info["Pos"], float(info["Angle"]))


def generic_event_despawn(self, entities, bullets, level, time_passed, info):
    #   despawn     (set a series of condition to chooses who to despawn
    #                2 despawn method,
    #                   soft: the thing takes max damage that can't be reduced
    #                   hard: the entity is removed from the list
    #                conditions can be: name, team, pos)
    #                             "despawn": {"Method": "Soft", "Conditions": []},
    pass


def generic_event_door(self, entities, bullets, level, time_passed, info):
    # door        (pick a door and set state either in open or closed)
    #                             "door": {"Door ID": 0, "Door state": True},
    # level["door state"].append({"State": map_data["door state"][count], "Rect": pg.Rect([s * 32 for s in d])})
    door_id = info["Door ID"]
    level["door state"][door_id]["State"] = info["Door state"]

    # Set wall collisions
    if level["door state"][door_id]["State"]:
        level["map"][door_id] = level["door state"][door_id]["Rect"]
    else:
        level["map"][door_id] = pg.Rect([0, 0, 0, 0])


def generic_event_sound(self, entities, bullets, level, time_passed, info):
    #                             "sound": {"Action": "Play", "Audio": "Silence"},
    if info["Action"] == "Play":
        Fun.play_sound(info["Audio"])
    if info["Action"] == "Change":
        Fun.play_music(info["Audio"])
    if info["Action"] == "Pause":
        if pg.mixer.music.get_busy():
            pg.mixer.music.pause()
        else:
            pg.mixer.music.unpause()
    if info["Action"] == "Stop":
        pg.mixer.music.stop()


def generic_event_level_end(self, entities, bullets, level, time_passed, info):
    #                             "level end": {"End level state": "win"},
    time_till_end = 60 * 5
    level["events"].append(MissionEvent("Finishing", trigger_timer, False, [finish_mission], free_var={"Timer": time_till_end}))
    for e in entities["entities"]:
        if e.team == "Players":
            e.status["No damage"] = time_till_end

    if info["End level state"] != "win":
        Fun.stop_music()
        level["free var"].update({"Loss": True})


def generic_event_cutscene(self, entities, bullets, level, time_passed, info):
    #                             "cutscene": {},     # AAAAAAAAAAAAAAAAAAAA
    pass


def generic_event_radio(self, entities, bullets, level, time_passed, info):
    #                             "radio": {},        # AAAAAAAAAAAAAAAAAAAA
    pass


def generic_event_change_character(self, entities, bullets, level, time_passed, info):
    #   change_character
    pass


def generic_event_free_var(self, entities, bullets, level, time_passed, info):
    #                             "free var": {"Target free var": "", "Operation": "Addition", "Value": 0}

    # "Addition", "Subtraction", "Multiplication", "Division", "Set"

    if info["Operation"] == "Addition":
        level["free var"][info["Target free var"]] += info["Value"]
    if info["Operation"] == "Subtraction":
        level["free var"][info["Target free var"]] -= info["Value"]
    if info["Operation"] == "Multiplication":
        level["free var"][info["Target free var"]] *= info["Value"]
    if info["Operation"] == "Division":
        level["free var"][info["Target free var"]] /= info["Value"]
    if info["Operation"] == "Set":
        level["free var"][info["Target free var"]] = info["Value"]


# |Mission events|------------------------------------------------------------------------------------------------------
def mission_start(self, entities, bullets, level, time_passed, screen, CLOCK):

    track_to_play = "Mission 1"
    if level['objective'] != "Defeat Elite Unit":
        allies = []
        for e in entities["entities"]:
            if e.team != "Players": break
            allies.append(e.name)

        #
        a = allies[0]
        sprite = {
                "Lord": Fun.SPRITE_RADIO_LORD,
                "Emperor": Fun.SPRITE_RADIO_EMPEROR,
                "Wizard": Fun.SPRITE_RADIO_WIZARD,
                "Sovereign": Fun.SPRITE_RADIO_SOVEREIGN,
                "Duke": Fun.SPRITE_RADIO_DUKE,
                "Jester": Fun.SPRITE_RADIO_JESTER,
                "Condor": Fun.SPRITE_RADIO_CONDOR,
                "Curtis": Fun.SPRITE_RADIO_CURTIS,
                "Lawrence": Fun.SPRITE_RADIO_LAWRENCE,
                "Mark": Fun.SPRITE_RADIO_MARK,
                "Vivianne": Fun.SPRITE_RADIO_VIVIANNE
            }[a]
        radio_handler(entities, [
            [sprite[0], f"RADIO-START-{a}-{level['objective']}", Fun.AMBER, 240]
            ])
        if level['objective'] == "Escort":
            radio_handler(entities,
                          {
                              "THR-1": [[Fun.SPRITE_RADIO_EMPLOYER[0], "Follow the red line", Fun.AMBER, 300]],
                              "Zoar Colonists": [[Fun.SPRITE_RADIO_MAKOTO[0], "", Fun.AMBER, 300]],
                          }[level["Player party"]]
                          )
        # Get music to play
        if level["mission number"] > 5:
            track_to_play = "Mission 2"
        if level["mission number"] > 10:
            track_to_play = "Mission 3"
        Fun.play_music(track_to_play)
        return
    # BossIntro
    boss_name = "BOSS-NAME-UNKNOWN"

    track_to_play = {"THR-1": "Boss - THR-1", "Zoar Colonists": "Boss - Curtis"}[level["Player party"]]

    if level["mission number"] == 5:
        boss_name = [
            "BOSS-NAME-ARMED-SHIELD-GENERATOR",
            "BOSS-NAME-HOVER-TANK",
            "BOSS-NAME-FIRE-SUPPORT-MECH"
        ][level['faction']]
    if level["mission number"] == 10:
        boss_name = [
            "BOSS-NAME-AA-SITE",
            "BOSS-NAME-GILGAMESH",
            "BOSS-NAME-ATTACK-HELICOPTER"
        ][level['faction']]
    if level["mission number"] == 15:
        # Fun.play_music("Dracula")
        # Additional stuff for final boss
        track_to_play = {"THR-1": "Boss - Curtis", "Zoar Colonists": "Boss - THR-1"}[level["Player party"]]
        if level['name'] == Fun.write_textline("Finale 1"):
            track_to_play = "Boss - Rigel"
        if level['name'] == Fun.write_textline("Finale 2"):
            boss_name = "BOSS-NAME-CURTIS"
        if level['name'] == Fun.write_textline("Finale 3"):
            boss_name = "BOSS-NAME-THR-1"
            for e in entities["entities"]:
                if e.team == "Player":
                    continue
                e.weapon.fire_rate *= 2
                e.vel_max *= 0.8
                e.pos = Fun.random_point_in_circle(e.pos, 32)
                e.free_var.update({"IS VERSUS": True})
                if e.name == "Lord":
                    e.weapon.bullet_info[0] = 6
                    e.weapon.bullet_info[3] = round(e.weapon.bullet_info[3] * 0.5)
                    e.weapon.bullet_info[4]["Manoeuvrability"] = 1
            level["events"].append(
                MissionEvent('Ambush', {"rects": [], "Conditions": trigger_check_under_specified_amount_enemies}, True, [thr_1],
                 free_var={"Specified amount": 3})
            )
    for e in entities["entities"]:
        if e.team == "Player":
            continue
        e.force_draw = True

    # Intro manager
    if level['name'] != Fun.write_textline("Finale 2"):

        entities["UI particles"].append(Particles.BossIntro(boss_name=Fun.write_textline(boss_name)))
    else:
        entities["UI particles"].append(Particles.MissionTitleCard(Fun.write_textline(boss_name), ""))

    level["events"].append(
        MissionEvent("Finishing", trigger_on_for, False, [change_scrolling_target], free_var={"Timer": 60 * 5}))

    # Play music track
    Fun.play_music(track_to_play)


def win(self, entities, bullets, level, time_passed, screen, CLOCK):
    time_till_end = 60 * 5
    level["events"].append(MissionEvent("Finishing", trigger_timer, False, [finish_mission], free_var={"Timer": time_till_end}))
    for e in entities["entities"]:
        if e.team == "Players":
            e.status["No damage"] = time_till_end
    #


def loss(self, entities, bullets, level, time_passed, screen, CLOCK):
    Fun.stop_music()
    level["events"].append(MissionEvent("Finishing", trigger_timer, False, [finish_mission], free_var={"Timer": 60 * 5}))
    for e in entities["entities"]:
        if e.team != "Players":
            e.status["No damage"] = 300
    level["free var"].update({"Loss": True})
    #


def skip_mission(self, entities, bullets, level, time_passed, screen, CLOCK):
    level["events"].append(MissionEvent("Finishing", trigger_timer, False, [finish_mission], free_var={"Timer": 60 * 5}))

    for e in entities["entities"]:
        if e.team == "Players":
            e.status["No damage"] = 300
            e.health = e.max_health
            # print(e.health)
    #


def loss_of_apc(self, entities, bullets, level, time_passed, screen, CLOCK):
    Fun.stop_music()
    level["events"].append(MissionEvent("Finishing", trigger_timer, False, [finish_mission], free_var={"Timer": 60 * 5}))
    radio_handler(entities,
                  {
                      "THR-1": [[Fun.SPRITE_RADIO_EMPLOYER[0], "You lost the APC. Mission failed.", Fun.AMBER, 300]],
                      "Zoar Colonists": [[Fun.SPRITE_RADIO_MAKOTO[0], "We just finished paying it off... come back to the colony.", Fun.AMBER, 300]],
                  }[level["Player party"]])
    level["free var"].update({"Loss": True})
    #


def finish_mission(self, entities, bullets, level, time_passed, screen, CLOCK):
    level["level_finished"] = True


def change_scrolling_target(self, entities, bullets, level, time_passed, screen, CLOCK):
    scrolling_target_entities = []
    for e in entities["entities"]:
        if "IS BOSS" in e.free_var:
            scrolling_target_entities.append(e)
    if "Manual target" in self.free_var:
        ENEMY_NO_OWNER.pos = self.free_var["Manual target"]
        scrolling_target_entities.append(ENEMY_NO_OWNER)
    level["scrolling target"] = Fun.find_scrolling_target(scrolling_target_entities)

    if self.free_var["Timer"] == 1:
        level["events"].append(MissionEvent("Finishing", trigger_yes_boss, False, [handle_boss_scrolling]))


def handle_boss_scrolling(self, entities, bullets, level, time_passed, screen, CLOCK):
    boss = False
    for e in entities["entities"]:
        if "IS BOSS" in e.free_var:
            boss = e.pos
    if boss:
        width = Fun.FRAME_MAX_SIZE[0] / 2
        height = Fun.FRAME_MAX_SIZE[1] / 2


        point = [boss[0] * -1 + width, boss[1] * -1 + height]
        level["scrolling target"] = Fun.midpoint_between(level["scrolling target"], point)

        num = Fun.distance_between(level["scrolling target"], point) * 0.005
        if num < 0.9:
            num = 0.9
        if num > 1.41:
            num = 1.41
        Fun.update_render_zoom(num)


def spawn_enemy_squad(entities, level, pos, dist_mod=1):
    # Find waypoint
    # 'points': {},  # "<id>": [<x>, <y>]
    #             # 'connections': {}  # "<id>": [<id of connected points>]
    point = ""
    for p in level["pathfinding"]["points"]:
        if Fun.distance_between(level["pathfinding"]["points"][p], pos) < 64 * dist_mod:
            point = p
    # Error control
    if point == "":
        Fun.print_to_error_stream("Didn't find matching pathfinding waypoint. Aborting")
        return
    # Get a waypoint 2 waypoint away from the start one
    no_go_points = [point]
    for x in range(1):
        waypoint_candidate = []
        for c in level["pathfinding"]["connections"][no_go_points[-1]]:
            if c in no_go_points:
                continue
            waypoint_candidate.append(c)
        no_go_points.append(waypoint_candidate[random.randint(0, len(waypoint_candidate)-1)])
    chosen_waypoint = level["pathfinding"]["points"][no_go_points[-1]]

    angle = Fun.angle_between(pos, chosen_waypoint)
    # Spawn enemies at the chosen way point
    squad, budget = Fun.enemy_squad_generator(level['mission number'], level['faction'])
    for e in squad:
        spawn_enemy(entities, e, Fun.random_point_in_donut(chosen_waypoint, (16, 32)), angle)


def spawn_enemy_squad_defense(entities, level, pos):
    # Find waypoint
    # 'points': {},  # "<id>": [<x>, <y>]
    #             # 'connections': {}  # "<id>": [<id of connected points>]
    searching_point = True
    chosen_waypoint = [0, 0]
    while searching_point:
        chosen_waypoint = level["pathfinding"]["points"][f'{random.randint(0, len(level["pathfinding"]["points"]) - 1)}']
        searching_point = False
        for w in level["map"]:
            if Fun.distance_between(pos, chosen_waypoint) < 256:
                searching_point = True
                break
            if w.collidepoint(chosen_waypoint[0], chosen_waypoint[1]):
                searching_point = True
                break

    angle = Fun.angle_between(pos, chosen_waypoint)
    # Spawn enemies at the chosen way point
    squad, budget = Fun.enemy_squad_generator(level['mission number'], level['faction'])
    for e in squad:
        spawn_enemy(entities, e, chosen_waypoint.copy(), angle)


# Capture
def capture_zone(self, entities, bullets, level, time_passed, screen, CLOCK):
    # Cap points {"Pos": [x, y], "Cap gauge": 0, "Captured": False}
    cap_points = level["free var"]["Cap points"]
    radius = 80
    all_points_captured = True
    players = []
    for e in entities["entities"]:
        if e.team == "Players":
            players.append(e)
    enemies = []
    for e in entities["entities"]:
        if e.team != "Players":
            enemies.append(e)

    main_player = players[0]
    x, y = [], []
    length = 0
    for titties in entities["entities"]:
        if "Outline" not in titties.free_var: continue
        x.append(titties.pos[0])
        y.append(titties.pos[1])
        length += 1
        if length >= 4: break
    centroid = [(sum(x)) / length, (sum(y)) / length]

    # For all points
    for i, point in enumerate(cap_points):
        dist = Fun.distance_between(point["Pos"], main_player.pos)
        if time_passed % 18 == 0:
            num_increase = 0
            # Check if any players are in one of the point to capture
            for p in players:
                if Fun.check_point_in_circle(radius, point["Pos"][0], point["Pos"][1], p.pos[0], p.pos[1]):
                    num_increase += 1.5
                    # Check if there's enemies on the point, if true, stop the capture, else increase cap gauge
                    for e in enemies:
                        if Fun.check_point_in_circle(radius, point["Pos"][0], point["Pos"][1], e.pos[0], e.pos[1]):
                            num_increase = 0
                            break
                    break
            # If cap gauge over 100, set point to captured
            if not point["Captured"]:
                if point["Cap gauge"] >= 0:
                    point["Cap gauge"] += num_increase
                    # Everytime the cap gauge reaches a multiple of 20 while raising, raise agro and make enemies go toward the point
                    if point["Cap gauge"] > 100:
                        for count, op in enumerate(level['objective points']):
                            if op == point["Pos"]:
                                level['objective points'].pop(count)
                                break
                        point["Captured"] = True
                        radio_handler(entities, {
                      "THR-1": [
                            [Fun.SPRITE_RADIO_EMPLOYER[0], f"Point {Fun.PHONETIC_ALPHABET[i % 26]} captured", Fun.AMBER, 300],
                            [Fun.SPRITE_RADIO_EMPLOYER[0], "Move to the next one.", Fun.AMBER, 180]
                        ],
                      "Zoar Colonists": [
                            [Fun.SPRITE_RADIO_MAKOTO[0], f"Point {Fun.JUST_THE_ALPHABET[i % 26]} is under our control", Fun.AMBER, 300],
                            [Fun.SPRITE_RADIO_MAKOTO[0], "Get the next one", Fun.AMBER, 180]
                        ],
                  }[level["Player party"]]
                                      )
                    elif point["Cap gauge"] % 20 == 0 and num_increase > 0:
                        spawn_enemy_squad(entities, level, point["Pos"])
                if point["Cap gauge"] < 0:
                    point["Cap gauge"] = 0

        # Draw
        colour = Fun.AMBER_LIGHT
        if point["Captured"]:
            # Switch colour when captured
            colour = Fun.UI_COLOUR_CONTRAST
        else:
            all_points_captured = False
        # If too far, draw indicator to show direction, else draw a circle showing the area used by the point
        if dist > 512:
            if not point["Captured"]:
                pos = Fun.move_with_vel_angle(centroid, 128, Fun.angle_between(point["Pos"], centroid))
                entities["UI particles"].append(Particles.GrowingCircle(pos, colour, 0, 1, 4, 0))
        else:
            entities["background particles"].append(Particles.GrowingCircle(point["Pos"], colour, 0, 1, radius, 3))
        if not point["Captured"]:
            rect_left, rect_top = point["Pos"][0]-50, point["Pos"][1]-5
            entities["background particles"].append(Particles.GrowingSquare(
                [rect_left, rect_top, 100, 10], Fun.UI_COLOUR_NEW_BACKGROUND, [0, 0], 1))
            entities["background particles"].append(Particles.GrowingSquare(
                [rect_left, rect_top, point["Cap gauge"], 10], colour, [0, 0], 1))
        # If Cap gauge over 0

    # if all points are captured, cause win
    if all_points_captured:
        win(self, entities, bullets, level, time_passed, screen, CLOCK)


# Escort. Apc moves on its own, event to make enemies attack the APC
# Defense. Event to handle waves
def defense_mission(self, entities, bullets, level, time_passed, screen, CLOCK):
    # Trigger is when there under 5 enemies
    # trigger_check_under_specified_amount_enemies(self, entities, bullets, level, time_passed):
    #  <= self.free_var["Specified amount"]
    # Defense info {"Current wave": 0, "Wave count": Int}
    defense_info = level["free var"]["Defense info"]
    if defense_info["Current wave"] == defense_info["Wave count"]:
        win(self, entities, bullets, level, time_passed, screen, CLOCK)
        return

    if defense_info["Current wave"] < defense_info["Wave count"]:
        # Spawn enemies
        pos = entities["entities"][0].pos
        print(f'Wave {defense_info["Current wave"]} finished')
        defense_info["Current wave"] += 1
        mod = 1
        if "Lessen presence" in level['modifiers']:
            mod -= 0.33
        if "Increased presence" in level['modifiers']:
            mod += 0.25
        for x in range(round((defense_info["Current wave"] + random.randint(3, 6)) * mod)):
            spawn_enemy_squad_defense(entities, level, pos)
        # print(f'Wave {defense_info["Current wave"]} started')


def artillery_strike(self, entities, bullets, level, time_passed, screen, CLOCK):
    if time_passed % 320 == 319:
        Fun.play_sound("Artillery 1")
        Bullets.spawn_bullet(
                ENEMY_NO_OWNER, entities, Bullets.Artillery,
            Fun.move_with_vel_angle(
                entities["entities"][0].pos, 128, 360 * random.random()), 0,
                [0, 60, 64,
                 50, {"Secondary explosion": {"Duration": 20}, "Colour": Fun.RED, "Slowdown rate": 0.05}])


def sandstorm(self, entities, bullets, level, time_passed, screen, CLOCK):
    for e in entities["entities"]:
        e.targeting_range = e.og_info["targeting range"] * 0.55
    player = entities["entities"][0]
    if len(entities["particles"]) <= 5000:
        true_pos = Fun.random_point_in_circle(player.pos, 630 * 0.75)
        duration = random.randint(60, 120)

        for x in range(2):
            entities["particles"].append(Particles.RandomParticle2(true_pos, Fun.ORANGE, random.uniform(2, 6),
                                                             duration, 180, size=random.randint(2, 5)))


def landmines(self, entities, bullets, level, time_passed, screen, CLOCK):
    for p in level["pathfinding"]['points']:
        if random.random() < 0.33:
            continue
        for x in range(random.randint(3, 10)):
            point = Fun.random_point_in_circle(level["pathfinding"]['points'][p].copy(), 64)
            allow = True
            for wall in level["map"]:
                if wall.collidepoint(point[0], point[1]):
                    allow = False
                    break
            if allow:
                Items.spawn_item(entities, "Landmine", point)
    # "Landmine"
    #


def ambush(self, entities, bullets, level, time_passed, screen, CLOCK):
    for x in range(3):
        spawn_enemy_squad(entities, level, entities["entities"][0].pos, dist_mod=5)
        # print([entities["scrolling"][0] * -1, entities["scrolling"][1] * -1])


def thr_1(self, entities, bullets, level, time_passed, screen, CLOCK):
    # , "Sovereign", "Duke", "Condor
    pos = entities["entities"][0].pos
    dist_mod = 5
        # print([entities["scrolling"][0] * -1, entities["scrolling"][1] * -1])
    point = ""
    for p in level["pathfinding"]["points"]:
        if Fun.distance_between(level["pathfinding"]["points"][p], pos) < 64 * dist_mod:
            point = p
    # Error control
    if point == "":
        Fun.print_to_error_stream("Didn't find matching pathfinding waypoint. Aborting")
        return
    # Get a waypoint 2 waypoint away from the start one
    no_go_points = [point]
    for x in range(1):
        waypoint_candidate = []
        for c in level["pathfinding"]["connections"][no_go_points[-1]]:
            if c in no_go_points:
                continue
            waypoint_candidate.append(c)
        no_go_points.append(waypoint_candidate[random.randint(0, len(waypoint_candidate)-1)])
    chosen_waypoint = level["pathfinding"]["points"][no_go_points[-1]]

    angle = Fun.angle_between(pos, chosen_waypoint)
    # Spawn enemies at the chosen way point
    for e in ["Sovereign", "Duke", "Condor"]:
        spawn_enemy(entities, e, Fun.random_point_in_donut(chosen_waypoint, (16, 32)), angle)
        entities["entities"][-1].weapon.fire_rate *= 2
        entities["entities"][-1].vel_max *= 0.8
        # entities["entities"][-1].pos = Fun.random_point_in_circle(e.pos, 32)
        entities["entities"][-1].free_var.update({"IS VERSUS": True})


# Versus
def versus_every_frame(self, entities, bullets, level, time_passed, screen, CLOCK):
    if time_passed == 0:
        track_to_play = f"Mission {random.randint(1, 3)}"
        Fun.play_music(track_to_play)
        t = 20
        mod = 1.5
        radio_handler(entities, [
            [Fun.SPRITE_RADIO_EMPLOYER[0], f"3", Fun.AMBER, t],
            [Fun.SPRITE_RADIO_EMPLOYER[0], f"2", Fun.AMBER, t],
            [Fun.SPRITE_RADIO_EMPLOYER[0], f"1", Fun.AMBER, t],
            [Fun.SPRITE_RADIO_EMPLOYER[0], f"FIGHT", Fun.AMBER, round(t * mod)],
        ])
        for e in entities["entities"]:
            e.status["Stunned"] = t * 3 + round(t * mod)
    # Handle end condition
    if len(entities["entities"]) <= 1:
        radio_handler(entities, [
            [Fun.SPRITE_RADIO_EMPLOYER[0], f"{entities['entities'][0].name} won the match", Fun.AMBER, 300]
        ])
        level["events"].append(MissionEvent("Finishing", trigger_timer, False, [finish_mission], free_var={"Timer": 60 * 5}))


#
def convert_pos(dict_to_convert, list_mode=False):
    for count, e in enumerate(dict_to_convert):
        index = e
        if list_mode:
            index = count
        if type(dict_to_convert[index]) == dict:
            dict_to_convert[index] = convert_pos(dict_to_convert[index])
        elif e == "Pos":
            dict_to_convert[index] = [dict_to_convert[index][0] * 32 + 16, dict_to_convert[index][1] * 32 + 16]
        elif type(dict_to_convert[index]) == list:
            dict_to_convert[index] = convert_pos(dict_to_convert[index], list_mode=True)

    return dict_to_convert


def load_level(level_to_load):
    map_data = Fun.get_from_json(f"Levels/{level_to_load}/Map_data.json", "Everything")
    event_data = Fun.get_from_json(f"Levels/{level_to_load}/Level_data.json", "Everything")

    level = {
        'name': event_data["name"],
        'map': [],
        'door state': [],
        'events': [],
        'level_finished': False,
        'pathfinding': {'points': {'0': [0, 0], '1': [1, 0]}, 'connections': {'0': ['1'], '1': ['0']}},
        "width height": [map_data["size"][0] * 32, map_data["size"][1] * 32],
        'rendering': {
            "Segments": [],
            "Tile set": {}
        },
        "spawn point": [
            map_data["spawn point"][0][0] * 32 + 16, map_data["spawn point"][0][1] * 32 + 16
        ],
        'free var': event_data["free var"],
    }
    # Convert level geometry
    for count, d in enumerate(map_data["doors"]):
        level["door state"].append({"State": map_data["door state"][count], "Rect": pg.Rect([s * 32 for s in d])})
        if map_data["door state"][count]:
            level["map"].append(pg.Rect([s * 32 for s in d]))
        else:
            level["map"].append(pg.Rect([0, 0, 0, 0]))

    # Pathfinding
    level_map = pg.Surface([level["width height"][0]/32, level["width height"][1]/32]).convert_alpha()
    for w in map_data["map"]:
        level["map"].append(pg.Rect([s * 32 for s in w]))
        pg.draw.rect(level_map, Fun.WHITE, w)

    for p in map_data["pathfinding"]:
        pg.draw.rect(level_map, (255, 255, 0), p)

    # Fun.screenshot(level_map)
    level['pathfinding'] = Fun.waypoint_connection_pathfinding_creator(level_map)

    # Convert rendering info
    for tile_set in map_data["rendering"]["Tile set"]:
        level['rendering']['Tile set'].update({tile_set: TILES_DICT[map_data["rendering"]["Tile set"][tile_set]]})

    for segment in map_data["rendering"]["Segments"]:
        empty_segment = {
            "Rect": pg.Rect([segment["Rect"][0] * 32 - 32, segment["Rect"][1] * 32 - 32,
                             segment["Rect"][2] * 32 + 64, segment["Rect"][3] * 32 + 64])
        }
        for tiles in level['rendering']['Tile set']:
            empty_part_list = []
            if tiles not in segment:
                continue
            for w in segment[tiles]:
                empty_part_list.append([y * 32 for y in w])
            empty_segment.update({tiles: empty_part_list})
        level['rendering']['Segments'].append(empty_segment)

    # Convert events
    for e in event_data["events"]:

        event_info = event_data["events"]

        trigger = {'rects': [], 'Conditions': event_info[e][1]["Conditions"]}

        for r in event_info[e][1]["rects"]:
            trigger["rects"].append([ass * 32 for ass in r])

        free_var = convert_pos(event_info[e][4])

        event = [event_info[e][0], trigger, event_info[e][2],
                 ["generic_event"], # Will need to update that for custom functions
                 free_var]

        level["events"].append(event)

    return level

import Entity
from Entity import ENEMY_NO_OWNER

