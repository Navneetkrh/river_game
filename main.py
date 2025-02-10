import sys
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

from river_biome.game import RiverCrossingGame
from asset_maker.maker import load_shapes, draw_stroke,draw_at

# -------------------------------------------------
# Constants & Setup
# -------------------------------------------------
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
HOVER_COLOR = (255, 255, 0)  # Yellow for hover effect

pygame.init()
FONT = pygame.font.SysFont("Arial", 30)

# -------------------------------------------------
# OpenGL Setup
# -------------------------------------------------
BG=load_shapes("assets/shapes/menu_bg.json")
def init_opengl():
    """Initialize OpenGL context for the game."""
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, WINDOW_HEIGHT, 0)  # top-left origin
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glClearColor(0, 0, 0, 1)
    draw_at(BG,0,0) 
    glFlush()


# -------------------------------------------------
# Helper: Draw Text
# -------------------------------------------------
def draw_text(surface, text, x, y, color=WHITE):
    """Draws text onto a surface at (x, y)."""
    text_surf = FONT.render(text, True, color)
    surface.blit(text_surf, (x, y))

# -------------------------------------------------
# Button Helper Class
# -------------------------------------------------
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color

    def draw(self, screen, mouse_pos):
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(screen, color, self.rect)
        draw_text(screen, self.text, self.rect.x + 10, self.rect.y + 10)

    def is_clicked(self, mouse_pos, click):
        return self.rect.collidepoint(mouse_pos) and click

# -------------------------------------------------
# Main Menu
# -------------------------------------------------
def main_menu():
    """Main menu to select a biome."""
    
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Select Biome")
    clock = pygame.time.Clock()

    buttons = [
        Button(50, 100, 200, 50, "River Biome", GREEN, HOVER_COLOR),
        Button(50, 200, 200, 50, "Space Biome (N/A)", GRAY, GRAY),
        Button(50, 300, 200, 50, "Cloud Biome (N/A)", GRAY, GRAY),
    ]

    while True:
        # screen.fill(BLACK)
        draw_text(screen, "Select Biome", 20, 20)

        mouse_pos = pygame.mouse.get_pos()
        click = False

        for button in buttons:
            button.draw(screen, mouse_pos)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                click = True

        if buttons[0].is_clicked(mouse_pos, click):
            return "river"
        elif buttons[1].is_clicked(mouse_pos, click) or buttons[2].is_clicked(mouse_pos, click):
            print("This biome is not ready yet.")

        pygame.display.update()
        clock.tick(FPS)

# -------------------------------------------------
# River Biome Menu (Start Game / Back)
# -------------------------------------------------
def river_biome_menu():
    """Menu to Start River Biome or go Back."""
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("River Biome Menu")
    clock = pygame.time.Clock()

    buttons = [
        Button(50, 100, 200, 50, "Start Game", GREEN, HOVER_COLOR),
        Button(50, 200, 200, 50, "Back", RED, HOVER_COLOR),
    ]

    while True:
        screen.fill(BLACK)
        draw_text(screen, "River Biome", 20, 20)

        mouse_pos = pygame.mouse.get_pos()
        click = False

        for button in buttons:
            button.draw(screen, mouse_pos)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                click = True

        if buttons[0].is_clicked(mouse_pos, click):
            return "start"
        elif buttons[1].is_clicked(mouse_pos, click):
            return "back"

        pygame.display.update()
        clock.tick(FPS)

# -------------------------------------------------
# Launch Selected Biome
# -------------------------------------------------
def main():
    while True:
        selection = main_menu()
        
        if selection == "river":
            river_choice = river_biome_menu()

            if river_choice == "start":
                # Initialize OpenGL & Start River Biome
                pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL)
                pygame.display.set_caption("River Biome – PyOpenGL/Pygame")
                init_opengl()
                
                game = RiverCrossingGame()
                game.game_loop()
                
                pygame.quit()
                sys.exit()
            elif river_choice == "back":
                continue  # Return to main menu

if __name__ == "__main__":
    main()
