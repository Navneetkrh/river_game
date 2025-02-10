import sys
import math
import random
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

from river_biome.game import RiverCrossingGame
from utils.graphics import draw_filled_circle



# -------------------------------------------------
# Constants & Setup
# -------------------------------------------------
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60



# -------------------------------------------------
# OpenGL Setup
# -------------------------------------------------
def init_opengl():
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, WINDOW_HEIGHT, 0)  # top-left origin
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glClearColor(0, 0, 0, 1)


# -------------------------------------------------
# Main Loop
# -------------------------------------------------
def main():
    pygame.init()
    pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("River Crossing – PyOpenGL/Pygame (JS Logic)")
    clock = pygame.time.Clock()
    init_opengl()

    game = RiverCrossingGame()
    game.game_loop()

    # running = True
    # overlay_displayed = False

    # while running:
    #     dt = clock.tick(FPS) / 1000.0
    #     keys = pygame.key.get_pressed()

    #     for event in pygame.event.get():
    #         if event.type == QUIT:
    #             running = False
    #         elif event.type == KEYDOWN:
    #             if event.key == K_ESCAPE:
    #                 running = False
    #             elif event.key == K_SPACE:
    #                 game.player.start_jump()

    #     if not overlay_displayed:
    #         game.update(dt, keys)
    #         if game.is_game_over():
    #             overlay_displayed = True
    #             print("Game Over!")
    #         elif game.is_win():
    #             if not game.next_level():
    #                 print("Congratulations! You completed all levels!")
    #                 running = False
    #             else:
    #                 print("Level Complete! Next level loaded.")
    #     glClear(GL_COLOR_BUFFER_BIT)
    #     game.draw()
    #     pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
