import pygame as pg
import os
import random
import sys  # Cool video https://www.youtube.com/watch?v=2Yj5mmKWukw


pg.mixer.pre_init()
pg.init()
pg.joystick.init()
WIN_WIDTH, WIN_HEIGHT = 630, 450
ORIGINAL_WIDTH, ORIGINAL_HEIGHT = WIN_WIDTH, WIN_HEIGHT
WIN = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT), pg.RESIZABLE)
pg.display.set_icon(pg.image.load(os.path.join("Sprites/Icon.ico")))
pg.display.set_caption("THR-1's Assault")
import Fun  # General use functions
import Items   # Everything crashes if I remove that
import Event
import Render
import Entity
import Main_Loop

int(0.)
CLOCK = pg.time.Clock()
pg.mixer.set_num_channels(32)

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


# pygame_splash_screen(WIN, CLOCK)


import Fun  # General use functions
import MillierLevelEditor

if __name__ == "__main__":

    MillierLevelEditor.main(WIN, CLOCK)
    #