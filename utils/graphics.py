import sys
import math
import random
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import time

# -------------------------------------------------
# Helper Function: Draw a Filled Circle using GL_TRIANGLE_FAN
# -------------------------------------------------
def draw_filled_circle(cx, cy, r, segments=30):
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(cx, cy)
    for i in range(segments+1):
        angle = 2 * math.pi * i / segments
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        glVertex2f(x, y)
    glEnd()



def draw_grass(x1, y1, x2, y2, x3, y3, x4, y4):
    """Draws a more visually appealing animated grass quad with swaying and variations."""

    time_factor = time.time() * 3  # Faster sway

    # Variations for individual blades
    blade_height = abs(y2 - y1)
    sway_factor = 0.03  # Increased sway amplitude
    sway_offset = x1 * 0.1  # Unique sway offset per blade
    sway = math.sin(time_factor + sway_offset) * sway_factor * blade_height  # Proportional sway

    # Gradient color for depth
    base_green = 0.5
    top_green = 0.8
    color_diff = top_green - base_green

    glBegin(GL_QUADS)

    # Vertex 1 (bottom left)
    glColor3f(0, base_green, 0) # Darker green at the base
    glVertex2f(x1 + sway, y1)

    # Vertex 2 (top left)
    glColor3f(0, top_green, 0)  # Lighter green at the top
    glVertex2f(x2 + sway, y2)

    # Vertex 3 (top right)
    glColor3f(0, top_green, 0) # Lighter green at the top
    glVertex2f(x3 - sway, y3)

    # Vertex 4 (bottom right)
    glColor3f(0, base_green, 0) # Darker green at the base
    glVertex2f(x4 - sway, y4)


    glEnd()

def draw_patch(x, y, width, height, num_blades=10):
    """Draws a patch of grass with multiple blades."""
    blade_width = width / num_blades
    for i in range(num_blades):
        x_start = x + i * blade_width
        x_end = x_start + blade_width
        # Vary blade height slightly
        blade_height = height * (0.8 + 0.4 * math.sin(i*2 + time.time()*2)) # Vary height
        y_top = y + blade_height
        # Slight random variation in x positions for a more natural look
        x_variation = blade_width * 0.2 * (math.sin(i*3 + time.time()*3)) # Vary x
        draw_grass(x_start + x_variation, y, x_start + x_variation, y_top, x_end + x_variation, y_top, x_end + x_variation, y)


def draw_river(x1, y1, x2, y2, x3, y3, x4, y4):
    glColor3f(0.0, 0.4, 1.0)
    glBegin(GL_QUADS)
    glVertex2f(x1, y1)
    glVertex2f(x2, y2)
    glVertex2f(x3, y3)
    glVertex2f(x4, y4)
    glEnd()
