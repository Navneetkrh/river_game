import sys
import math
import random
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import pygame_gui

from river_biome.game import RiverCrossingGame
from utils.graphics import draw_filled_circle



# -------------------------------------------------
# Constants & Setup
# -------------------------------------------------
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Define game states
STATE_MAIN_MENU = 0
STATE_BIOME_MENU = 1
STATE_GAME = 2

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

    # game = RiverCrossingGame()
    # game.game_loop()

    # Create the Pygame window/surface
    window_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Biome Selection – Pygame GUI")

    # Create the GUI manager
    manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT), 
                                   "theme.json")  # optional theme

    # We'll keep track of our current 'app state' to switch between menus & game
    app_state = STATE_MAIN_MENU

    # --- Create the main menu UI elements ---
    main_menu_panel = pygame_gui.elements.UIPanel(
        relative_rect=pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT),
        starting_layer_height=0,
        manager=manager
    )
    title_label = pygame_gui.elements.UITextBox(
        html_text="<h2>Select Biome</h2>",
        relative_rect=pygame.Rect(WINDOW_WIDTH//2 - 100, 50, 200, 50),
        manager=manager,
        container=main_menu_panel
    )
    # Biome Buttons
    river_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(WINDOW_WIDTH//2 - 75, 150, 150, 50),
        text="River Biome",
        manager=manager,
        container=main_menu_panel
    )
    space_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(WINDOW_WIDTH//2 - 75, 220, 150, 50),
        text="Space Biome",
        manager=manager,
        container=main_menu_panel
    )
    cloud_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(WINDOW_WIDTH//2 - 75, 290, 150, 50),
        text="Cloud Biome",
        manager=manager,
        container=main_menu_panel
    )
    quit_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(WINDOW_WIDTH//2 - 75, 380, 150, 50),
        text="Quit",
        manager=manager,
        container=main_menu_panel
    )

    # We'll also create a second "biome menu" panel that shows “Start / Back”
    # specifically for River biome
    biome_menu_panel = pygame_gui.elements.UIPanel(
        relative_rect=pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT),
        starting_layer_height=1,
        manager=manager,
        visible=False  # Initially hidden
    )
    biome_title = pygame_gui.elements.UITextBox(
        html_text="<h2>River Biome</h2>",
        relative_rect=pygame.Rect(WINDOW_WIDTH//2 - 100, 50, 200, 50),
        manager=manager,
        container=biome_menu_panel
    )
    start_game_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(WINDOW_WIDTH//2 - 75, 200, 150, 50),
        text="Start Game",
        manager=manager,
        container=biome_menu_panel
    )
    back_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(WINDOW_WIDTH//2 - 75, 280, 150, 50),
        text="Back",
        manager=manager,
        container=biome_menu_panel
    )

    # We'll create a reference to the RiverCrossingGame, but only initialize
    # it once the user chooses "Start Game"
    river_game = None

    # We can also create a small UI label for in-game UI to display Health & Lives
    # We'll show/hide it when in GAME state
    in_game_ui_panel = pygame_gui.elements.UIPanel(
        relative_rect=pygame.Rect(0, 0, WINDOW_WIDTH, 50),
        starting_layer_height=2,
        manager=manager,
        visible=False
    )
    health_lives_label = pygame_gui.elements.UITextBox(
        html_text="Health: N/A | Lives: N/A",
        relative_rect=pygame.Rect(10, 10, 200, 30),
        manager=manager,
        container=in_game_ui_panel
    )
    # Optionally, an in-game "Exit" button to return to main menu
    exit_to_menu_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(WINDOW_WIDTH - 110, 10, 100, 30),
        text="Exit",
        manager=manager,
        container=in_game_ui_panel
    )

    running = True

    while running:
        time_delta = clock.tick(FPS) / 1000.0

        # Handle events
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            # Let Pygame GUI process its events
            manager.process_events(event)

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                # MAIN MENU logic
                if app_state == STATE_MAIN_MENU:
                    if event.ui_element == river_button:
                        # Hide main_menu_panel, show biome_menu_panel
                        main_menu_panel.hide()
                        biome_menu_panel.show()
                        app_state = STATE_BIOME_MENU

                    elif event.ui_element == space_button:
                        # Not ready yet
                        print("Space Biome not implemented yet.")
                    elif event.ui_element == cloud_button:
                        # Not ready yet
                        print("Cloud Biome not implemented yet.")
                    elif event.ui_element == quit_button:
                        running = False

                # BIOME MENU logic (River)
                elif app_state == STATE_BIOME_MENU:
                    if event.ui_element == start_game_button:
                        # Start the river game
                        biome_menu_panel.hide()
                        in_game_ui_panel.show()
                        app_state = STATE_GAME

                        # Initialize the RiverCrossingGame
                        river_game = RiverCrossingGame()

                    elif event.ui_element == back_button:
                        # Return to main menu
                        biome_menu_panel.hide()
                        main_menu_panel.show()
                        app_state = STATE_MAIN_MENU

                # IN-GAME UI logic
                elif app_state == STATE_GAME:
                    if event.ui_element == exit_to_menu_button:
                        # Exit to main menu
                        in_game_ui_panel.hide()
                        main_menu_panel.show()
                        app_state = STATE_MAIN_MENU

                        # If you want to forcibly end the game, or re-init next time
                        # river_game = None

            # Additional keydown checks, e.g. SPACE to jump in game
            if event.type == KEYDOWN:
                if app_state == STATE_GAME and river_game is not None:
                    if event.key == K_SPACE:
                        river_game.player.start_jump()

        # Update the UI manager
        manager.update(time_delta)

        # Clear the screen
        window_surface.fill((0, 0, 0))

        # If in GAME state, update and draw the RiverCrossingGame
        if app_state == STATE_GAME and river_game is not None:
            # Update game logic
            keys = pygame.key.get_pressed()
            river_game.update(time_delta, keys)
            if river_game.is_game_over():
                # The player lost all lives? Return to menu or let them re-try
                # For example:
                in_game_ui_panel.hide()
                main_menu_panel.show()
                app_state = STATE_MAIN_MENU
                print("Game Over. Returning to menu.")

            elif river_game.is_win():
                # If you want to handle next level or next biome
                pass

            # Draw the game
            glClear(GL_COLOR_BUFFER_BIT)  # Clear the GL buffer
            river_game.draw()
            pygame.display.flip()

            # Update the in-game UI text for Health & Lives
            if river_game.player is not None:
                new_text = f"Health: {river_game.player.health} | Lives: {river_game.player.lives}"
                health_lives_label.set_text(new_text)

        else:
            # If in MENU state, just draw the GUI
            manager.draw_ui(window_surface)
            pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()