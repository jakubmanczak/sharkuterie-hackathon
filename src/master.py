import pygame
import sys
from src.cutscene import CutsceneHandler
import src.intro as intro
import src.mainmenu as mainmenu
import src.levels as levels
from src.gamestate import gamestate
from src.cutscene import opening_cutscene_dialogue
from src.cutscene import final_cutscene_dialogue
from src.levels import make_lvl_1

def main():
    pygame.init()

    window_w, window_h = 256*4, 240*4
    window = pygame.display.set_mode((window_w, window_h), pygame.RESIZABLE)
    pygame.display.set_caption("Sharkuterie Board")

    pygame.key.set_repeat(96, 32)

    font = pygame.font.Font("./assets/Micro_Chat.ttf", 10)

    game_w, game_h = 256, 240
    game_surface = pygame.Surface((game_w, game_h))

    scaled_w, scaled_h = game_w, game_h
    pos_x, pos_y = 0, 0
    last_window_size = (0, 0)

    running = True
    clock = pygame.time.Clock()

    level = make_lvl_1()
    # level.add_player(1, 1)
    # level.init_camera(game_w, game_h)

    gamestate.screen = "introvideo"

    opening_cutscene = CutsceneHandler(opening_cutscene_dialogue)
    final_cutscene = CutsceneHandler(final_cutscene_dialogue)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                window_w, window_h = event.size
                window = pygame.display.set_mode((window_w, window_h), pygame.RESIZABLE)
                last_window_size = (0, 0)
            else:
                if gamestate.screen == "introvideo":
                    intro.handle_intro_events(event)
                elif gamestate.screen == "mainmenu":
                    mainmenu.handle_menu_events(event)
                elif gamestate.screen == "openingcutscene":
                    opening_cutscene.handle_events(event)
                elif gamestate.screen == "finalcutscene":
                    final_cutscene.handle_events(event)
                elif gamestate.screen == "ingame":
                    level.conductor.start() # this is a silly... and danger...
                    level.handle_player_movement(event)

        if gamestate.screen == "ingame":

            if level is None or getattr(level, 'level_number', -1) != gamestate.current_level:
                # Load new level based on current_level
                if gamestate.current_level == 1:
                    level = levels.make_lvl_1()
                    level.level_number = 1
                elif gamestate.current_level == 2:
                    level = levels.make_lvl_2()
                    level.level_number = 2
                elif gamestate.current_level == 3:
                    level = levels.make_lvl_3()
                    level.level_number = 3

                # Initialize level
                level.add_player(1, 1)
                level.init_camera(game_w, game_h)
                level.conductor.start()

            level.update()
            if level.check_level_completion():
                level.transition_to_next_level()


        # UPDATE CALLS
        # ---- ---- ---- ---- ---- ----
        # DRAW CALLS

        current_window_size = (window_w, window_h)
        if current_window_size != last_window_size:
            scale_w = window_w / game_w
            scale_h = window_h / game_h
            scale_factor = min(scale_w, scale_h)

            scaled_w = int(game_w * scale_factor)
            scaled_h = int(game_h * scale_factor)

            pos_x = (window_w - scaled_w) // 2
            pos_y = (window_h - scaled_h) // 2

            last_window_size = current_window_size

        game_surface.fill((0, 0, 0))

        if gamestate.screen == "introvideo":
            intro.handle_intro_drawing(game_surface)
        elif gamestate.screen == "mainmenu":
            mainmenu.handle_menu_drawing(game_surface)
        elif gamestate.screen == "openingcutscene":
            opening_cutscene.draw(game_surface)
        elif gamestate.screen == "finalcutscene":
            final_cutscene.draw(game_surface)
        elif gamestate.screen == "ingame":
            level.draw(game_surface, font)

        window.fill((0, 0, 0))
        scaled_surface = pygame.transform.scale(game_surface, (scaled_w, scaled_h))
        window.blit(scaled_surface, (pos_x, pos_y))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()
