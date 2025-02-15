import sys
import math
import random
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import time
from PIL import Image
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

def load_texture(filename):
    # Open the image file
    image = Image.open(filename)
    image = image.convert("RGBA")  # Ensure we have an RGBA image
    width, height = image.size
    # Convert image data to bytes
    img_data = image.tobytes("raw", "RGBA", 0, -1)
    
    # Generate a texture ID and bind it
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    
    # Set texture parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    
    # Upload the texture data to the GPU
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    
    # Unbind the texture and return the texture ID
    glBindTexture(GL_TEXTURE_2D, 0)
    return texture_id


def draw_grass(x1, y1, x2, y2, x3, y3, x4, y4):
    """Draws a more visually appealing animated grass quad with swaying and variations."""

    time_factor = time.time() * 3  # Faster sway

    # Variations for individual blades
    blade_height = abs(y2 - y1)
    sway_factor = 0.03  # Increased sway amplitude
    sway_offset = x1 * 0.1  # Unique sway offset per blade
    sway = math.sin(time_factor + sway_offset) * sway_factor * blade_height  # Proportional sway

    # Gradient color for depth
    base_green = 1
    top_green = 1
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

def textured_grass(x1, y1, x2, y2, x3, y3, x4, y4, texture):
    """Draws a textured quad with grass texture."""
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture)

    glBegin(GL_QUADS)

    glTexCoord2f(0.0, 0.0)
    glVertex2f(x1, y1)

    glTexCoord2f(1.0, 0.0)
    glVertex2f(x2, y2)

    glTexCoord2f(1.0, 1.0)
    glVertex2f(x3, y3)

    glTexCoord2f(0.0, 1.0)
    glVertex2f(x4, y4)

    glEnd()

    glBindTexture(GL_TEXTURE_2D, 0)
    glDisable(GL_TEXTURE_2D)



def draw_animated_river(x1, y1, x2, y2, x3, y3, x4, y4, textures, frame_duration=0.1):
    """
    Draws a river quad with animated water texture.
    
    Parameters:
        x1, y1, ..., x4, y4: Coordinates of the quad's vertices.
        textures: A list of OpenGL texture IDs representing the animation frames.
        frame_duration: Duration (in seconds) that each frame is displayed.
    """
    # Determine the current frame based on time
    num_frames = len(textures)
    current_frame = int(time.time() / frame_duration) % num_frames
    current_texture = textures[current_frame]
    
    # Enable texturing and bind the current texture
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, current_texture)
    # water blue
    glColor3f(0, 0.7, 1)
    
    glBegin(GL_QUADS)
    
    # Define texture coordinates and corresponding vertices
    glTexCoord2f(0.0, 0.0)
    glVertex2f(x1, y1)
    
    glTexCoord2f(1.0, 0.0)
    glVertex2f(x2, y2)
    
    glTexCoord2f(1.0, 1.0)
    glVertex2f(x3, y3)
    
    glTexCoord2f(0.0, 1.0)
    glVertex2f(x4, y4)
    
    glEnd()
    
    # Unbind texture and disable texturing
    glBindTexture(GL_TEXTURE_2D, 0)
    glDisable(GL_TEXTURE_2D)

def draw_animated_space(x1, y1, x2, y2, x3, y3, x4, y4, textures, frame_duration=0.1):
    """
    Draws a river quad with animated water texture.
    
    Parameters:
        x1, y1, ..., x4, y4: Coordinates of the quad's vertices.
        textures: A list of OpenGL texture IDs representing the animation frames.
        frame_duration: Duration (in seconds) that each frame is displayed.
    """
    # Determine the current frame based on time
    num_frames = len(textures)
    current_frame = int(time.time() / frame_duration) % num_frames
    current_texture = textures[current_frame]
    
    # Enable texturing and bind the current texture
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, current_texture)
    # space black
    glColor3f(0.1,0.1,0,1)
    # glColor3f(0, 0.7, 1)
    
    glBegin(GL_QUADS)
    
    # Define texture coordinates and corresponding vertices
    glTexCoord2f(0.0, 0.0)
    glVertex2f(x1, y1)
    
    glTexCoord2f(1.0, 0.0)
    glVertex2f(x2, y2)
    
    glTexCoord2f(1.0, 1.0)
    glVertex2f(x3, y3)
    
    glTexCoord2f(0.0, 1.0)
    glVertex2f(x4, y4)
    
    glEnd()
    
    # Unbind texture and disable texturing
    glBindTexture(GL_TEXTURE_2D, 0)
    glDisable(GL_TEXTURE_2D)



def draw_river(x1, y1, x2, y2, x3, y3, x4, y4):
    glBegin(GL_QUADS)
    glColor3f(0.0, 0.4, 1.0)
    glVertex2f(x1, y1)
    glVertex2f(x2, y2)
    glVertex2f(x3, y3)
    glVertex2f(x4, y4)
    glEnd()

