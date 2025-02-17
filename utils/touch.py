import json
import sys
import math
import random
import imgui
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from asset_maker.maker import load_shapes, draw_stroke, draw_at
from utils.graphics import draw_grass, load_texture, draw_animated_river, draw_river, textured_grass

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

# Define the D-pad center and offset for the directional buttons
DPAD_CENTER = (WINDOW_WIDTH / 6, 510)  # X remains as before; Y adjusted to allow for spacing
DPAD_OFFSET =45  # Distance from the center to each button

BUTTON_POSITIONS = {
    "up":    (DPAD_CENTER[0],         DPAD_CENTER[1] - DPAD_OFFSET, 30),
    "down":  (DPAD_CENTER[0],         DPAD_CENTER[1] + DPAD_OFFSET, 30),
    "left":  (DPAD_CENTER[0] - DPAD_OFFSET, DPAD_CENTER[1],            30),
    "right": (DPAD_CENTER[0] + DPAD_OFFSET, DPAD_CENTER[1],            30),
    "jump":  (WINDOW_WIDTH - 100,     WINDOW_HEIGHT - 75, 30),
    "pause": (WINDOW_WIDTH - 50,      50,                30),
}
def draw_all_touch_buttons():
    """Draws all the touch buttons on the screen."""
    for direction, (cx, cy, r) in BUTTON_POSITIONS.items():
        hover = is_mouse_over(direction)
        draw_button(cx, cy, r, direction, hover)

def draw_button(cx, cy, r, direction, hover=False):
    """
    Draws a button with a circle and an icon inside it.
    cx, cy - Center of the button.
    r - Radius of the circle.
    direction - One of: "UP", "DOWN", "LEFT", "RIGHT", "jump", "pause".
    hover - Boolean indicating if the mouse is over the button.
    """
    # Define base and hover colors (Steel blue shades)
    base_color  = (0.27, 0.51, 0.71)
    hover_color = (0.37, 0.61, 0.81)
    current_color = hover_color if hover else base_color

    # --- Draw Shadow ---
    shadow_offset = 3
    glColor4f(0.0, 0.0, 0.0, 0.3)  # Black shadow with 30% opacity
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(cx + shadow_offset, cy + shadow_offset)
    for i in range(51):
        angle = 2 * math.pi * i / 50
        x = cx + shadow_offset + r * math.cos(angle)
        y = cy + shadow_offset + r * math.sin(angle)
        glVertex2f(x, y)
    glEnd()

    # --- Draw Gradient Circle Button ---
    glBegin(GL_TRIANGLE_FAN)
    # Center vertex (brighter)
    glColor4f(current_color[0], current_color[1], current_color[2], 0.9)
    glVertex2f(cx, cy)
    # Outer vertices (more transparent)
    for i in range(51):
        angle = 2 * math.pi * i / 50
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        glColor4f(current_color[0], current_color[1], current_color[2], 0.5)
        glVertex2f(x, y)
    glEnd()

    # --- Draw Icon ---
    glColor4f(1.0, 1.0, 1.0, 0.8)  # White with 80% opacity
    tri_size = r * 0.8

    if direction.upper() == "UP":
        glBegin(GL_TRIANGLES)
        glVertex2f(cx, cy - tri_size / 2)
        glVertex2f(cx - tri_size / 2, cy + tri_size / 2)
        glVertex2f(cx + tri_size / 2, cy + tri_size / 2)
        glEnd()

    elif direction.upper() == "DOWN":
        glBegin(GL_TRIANGLES)
        glVertex2f(cx, cy + tri_size / 2)
        glVertex2f(cx - tri_size / 2, cy - tri_size / 2)
        glVertex2f(cx + tri_size / 2, cy - tri_size / 2)
        glEnd()

    elif direction.upper() == "LEFT":
        glBegin(GL_TRIANGLES)
        glVertex2f(cx - tri_size / 2, cy)
        glVertex2f(cx + tri_size / 2, cy - tri_size / 2)
        glVertex2f(cx + tri_size / 2, cy + tri_size / 2)
        glEnd()

    elif direction.upper() == "RIGHT":
        glBegin(GL_TRIANGLES)
        glVertex2f(cx + tri_size / 2, cy)
        glVertex2f(cx - tri_size / 2, cy - tri_size / 2)
        glVertex2f(cx - tri_size / 2, cy + tri_size / 2)
        glEnd()

    elif direction == "jump":
        # Draw a jump icon as a quadratic Bézier curve with an arrowhead.
        # Define control points for the curve.
        start = (cx - tri_size/2, cy + tri_size/4)
        control = (cx, cy - tri_size/2)
        end = (cx + tri_size/2, cy + tri_size/4)
        
        # Draw the curved line (using a line strip)
        glLineWidth(2)
        glBegin(GL_LINE_STRIP)
        for i in range(21):
            t = i / 20.0
            # Quadratic Bézier interpolation
            x = (1 - t)**2 * start[0] + 2*(1 - t)*t * control[0] + t**2 * end[0]
            y = (1 - t)**2 * start[1] + 2*(1 - t)*t * control[1] + t**2 * end[1]
            glVertex2f(x, y)
        glEnd()
        glLineWidth(1)
        
        # Draw the arrowhead at the end of the curve.
        # Compute the tangent at t=1 (approximation)
        dx = 2 * (end[0] - control[0])
        dy = 2 * (end[1] - control[1])
        length = math.sqrt(dx*dx + dy*dy)
        if length != 0:
            dx /= length
            dy /= length

        arrow_length = 8
        # Compute a perpendicular vector for the arrowhead width.
        perp_dx = -dy
        perp_dy = dx

        # Base point of the arrowhead (back from the tip)
        base = (end[0] - dx * arrow_length, end[1] - dy * arrow_length)
        # Compute two base corners for the arrowhead triangle.
        left_corner = (base[0] + perp_dx * (arrow_length/2), base[1] + perp_dy * (arrow_length/2))
        right_corner = (base[0] - perp_dx * (arrow_length/2), base[1] - perp_dy * (arrow_length/2))
        
        glBegin(GL_TRIANGLES)
        glVertex2f(end[0], end[1])           # Tip of the arrow
        glVertex2f(left_corner[0], left_corner[1])
        glVertex2f(right_corner[0], right_corner[1])
        glEnd()

    elif direction == "pause":
        # Draw two vertical rectangles for the pause icon.
        bar_width  = tri_size * 0.2
        bar_height = tri_size
        gap = 2  # Gap between bars
        # Left bar
        glBegin(GL_QUADS)
        glVertex2f(cx - gap - bar_width, cy - bar_height/2)
        glVertex2f(cx - gap,           cy - bar_height/2)
        glVertex2f(cx - gap,           cy + bar_height/2)
        glVertex2f(cx - gap - bar_width, cy + bar_height/2)
        glEnd()
        # Right bar
        glBegin(GL_QUADS)
        glVertex2f(cx + gap,           cy - bar_height/2)
        glVertex2f(cx + gap + bar_width, cy - bar_height/2)
        glVertex2f(cx + gap + bar_width, cy + bar_height/2)
        glVertex2f(cx + gap,           cy + bar_height/2)
        glEnd()

def is_inside_button(x, y, cx, cy, r):
    """
    Checks if the point (x, y) is inside a circle centered at (cx, cy) with radius r.
    
    Parameters:
      - x, y : The point to check (in OpenGL coordinate space)
      - cx, cy : Center of the button (circle)
      - r : Radius of the button
    
    Returns:
      - True if inside the circle, False otherwise.
    """
    return math.sqrt((x - cx) ** 2 + (y - cy) ** 2) <= r

def is_mouse_over(button):
    cx, cy, r = BUTTON_POSITIONS[button]
    mouse_x, mouse_y = pygame.mouse.get_pos()
    return is_inside_button(mouse_x, mouse_y, cx, cy, r)

def if_mouse_clicked(button):
    cx, cy, r = BUTTON_POSITIONS[button]
    mouse_x, mouse_y = pygame.mouse.get_pos()
    left, middle, right = pygame.mouse.get_pressed()
    if left and is_inside_button(mouse_x, mouse_y, cx, cy, r):
        return True
    return False
