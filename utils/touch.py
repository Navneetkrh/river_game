import json
import sys
import math
import random
import imgui
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from asset_maker.maker import load_shapes, draw_stroke,draw_at
from utils.graphics import draw_grass,load_texture,draw_animated_river,draw_river,textured_grass

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

LEFT_BANK_WIDTH = 100
RIGHT_BANK_WIDTH = 100
RIVER_START_X = LEFT_BANK_WIDTH
RIVER_END_X = WINDOW_WIDTH - RIGHT_BANK_WIDTH

NUM_COLUMNS = 6
CELL_WIDTH = (RIVER_END_X - RIVER_START_X) / NUM_COLUMNS
ROW_Y = [WINDOW_HEIGHT/3, WINDOW_HEIGHT/2, (2*WINDOW_HEIGHT)/3]


BUTTON_POSITIONS = {
    "up":(WINDOW_WIDTH/2,WINDOW_HEIGHT/2+100,50),
    "down":(WINDOW_WIDTH/2,WINDOW_HEIGHT/2-100,50),
    "left":(WINDOW_WIDTH/2-100,WINDOW_HEIGHT/2,50),
    "right":(WINDOW_WIDTH/2+100,WINDOW_HEIGHT/2,50),
    "jump":(WINDOW_WIDTH/2+400,WINDOW_HEIGHT/2,20),
    "pause":(WINDOW_WIDTH/2+200,WINDOW_HEIGHT/2,50),
}
def draw_all_touch_buttons():
    """Draws all the touch buttons on the screen."""
    for direction, (cx, cy,r) in BUTTON_POSITIONS.items():
        draw_button(cx, cy, r, direction)

def draw_button(cx, cy, r, direction):
    """
    Draws a button with a circle and a triangle inside it.
    cx, cy - Center of the button
    r - Radius of the circle
    direction - "UP", "DOWN", "LEFT", "RIGHT"
    """
    # # Draw Circle
    glColor3f(0.27, 0.51, 0.71)  # Steel blue color
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(cx, cy)  # Center
    for i in range(51):
        angle = 2 * math.pi * i / 50
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        glVertex2f(x, y)
    glEnd()

    # Draw Triangle inside the circle
    glColor3f(1.0, 0, 0)  # White triangle
    tri_size = r * 0.8  # Triangle size inside the circle
    glBegin(GL_TRIANGLES)

    if direction == "UP":
        glVertex2f(cx, cy + tri_size / 2)
        glVertex2f(cx - tri_size / 2, cy - tri_size / 2)
        glVertex2f(cx + tri_size / 2, cy - tri_size / 2)

    elif direction == "DOWN":
        glVertex2f(cx, cy - tri_size / 2)
        glVertex2f(cx - tri_size / 2, cy + tri_size / 2)
        glVertex2f(cx + tri_size / 2, cy + tri_size / 2)

    elif direction == "LEFT":
        glVertex2f(cx - tri_size / 2, cy)
        glVertex2f(cx + tri_size / 2, cy - tri_size / 2)
        glVertex2f(cx + tri_size / 2, cy + tri_size / 2)

    elif direction == "RIGHT":
        glVertex2f(cx + tri_size / 2, cy)
        glVertex2f(cx - tri_size / 2, cy - tri_size / 2)
        glVertex2f(cx - tri_size / 2, cy + tri_size / 2)

    glEnd()

def is_inside_button(x, y, cx, cy, r):
    """
    Checks if the point (x, y) is inside a circle centered at (cx, cy) with radius r.
    
    Parameters:
    - x, y : Point to check (in OpenGL coordinate space, -1 to 1)
    - cx, cy : Center of the button (circle)
    - r : Radius of the button
    
    Returns:
    - True if inside, False otherwise
    """
    return math.sqrt((x - cx) ** 2 + (y - cy) ** 2) <= r

def is_mouse_over(button):
    cx,cy,r=BUTTON_POSITIONS[button]
    mouse_x, mouse_y = pygame.mouse.get_pos()

    return is_inside_button(mouse_x, mouse_y, cx, cy, r)


def if_mouse_clicked(button):

    cx,cy,r=BUTTON_POSITIONS[button]
    mouse_x, mouse_y = pygame.mouse.get_pos()
    left, middle, right = pygame.mouse.get_pressed()
    if left:
        if is_inside_button(mouse_x, mouse_y, cx, cy, r):
            return True
    return False

