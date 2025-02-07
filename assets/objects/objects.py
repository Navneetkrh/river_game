import sys
import math
import random
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

from utils.graphics import draw_filled_circle

# -------------------------------------------------
# Constants & Setup
# -------------------------------------------------
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


# -------------------------------------------------
# Platform Class
# -------------------------------------------------
class Platform:
    def __init__(self, gridRow, gridCol, leftBound, rightBound, speed):
        self.row = gridRow
        self.col = gridCol
        self.radius = 25
        self.speed = speed
        # Compute initial x position from grid
        self.x = RIVER_START_X + (gridCol - 0.5) * CELL_WIDTH
        self.y = ROW_Y[gridRow - 1]
        # Compute actual horizontal bounds
        self.leftBoundX = RIVER_START_X + (leftBound - 0.5) * CELL_WIDTH
        self.rightBoundX = RIVER_START_X + (rightBound - 0.5) * CELL_WIDTH
        # Random initial direction
        self.vx = self.speed if random.random() < 0.5 else -self.speed

    def update(self, dt):
        self.x += self.vx * dt
        if self.x - self.radius < self.leftBoundX:
            self.x = self.leftBoundX + self.radius
            self.vx = abs(self.vx)
        if self.x + self.radius > self.rightBoundX:
            self.x = self.rightBoundX - self.radius
            self.vx = -abs(self.vx)

    def draw(self):
        # glColor3f(0.0, 1.0, 0.0)
        # light brown
        glColor3f(0.8, 0.6, 0.2)
        draw_filled_circle(self.x, self.y, self.radius)


# -------------------------------------------------
# Player Class
# -------------------------------------------------
class Player:
    def __init__(self):
        self.radius = 12
        self.x = LEFT_BANK_WIDTH / 2.0
        self.y = WINDOW_HEIGHT / 2.0
        self.speed = 200.0   # in px/sec
        self.dx = 0
        self.dy = 0
        self.isJumping = False
        self.jumpTime = 0.0
        self.jumpDuration = 0.5  # seconds
        self.jumpHeight = 40.0
        self.attachedPlatform = None
        self.angle = 0.0
        self.angularSpeed = 2.0  # radians/sec

    def start_jump(self):
        if not self.isJumping:
            self.isJumping = True
            self.jumpTime = 0.0
            self.attachedPlatform = None

    def try_attach(self, platforms):
        self.attachedPlatform = None
        for p in platforms:
            dist = math.hypot(self.x - p.x, self.y - p.y)
            if dist < (p.radius + self.radius):
                self.attachedPlatform = p
                break

    def get_jump_offset(self):
        if not self.isJumping:
            return 0.0
        t = self.jumpTime / self.jumpDuration
        return self.jumpHeight * 4.0 * t * (1.0 - t)

    def update(self, dt, keys, platforms):
        self.dx = 0
        self.dy = 0
        if keys[K_LEFT]:
            self.dx = -self.speed
        if keys[K_RIGHT]:
            self.dx = self.speed
        if keys[K_UP]:
            self.dy = -self.speed
        if keys[K_DOWN]:
            self.dy = self.speed

        if self.attachedPlatform and not self.isJumping:
            self.x += self.attachedPlatform.vx * dt

        self.x += self.dx * dt
        self.y += self.dy * dt

        if self.x - self.radius < 0:
            self.x = self.radius
        if self.x + self.radius > WINDOW_WIDTH:
            self.x = WINDOW_WIDTH - self.radius
        if self.y - self.radius < 0:
            self.y = self.radius
        if self.y + self.radius > WINDOW_HEIGHT:
            self.y = WINDOW_HEIGHT - self.radius

        self.angle += self.angularSpeed * dt
        if self.angle > 2 * math.pi:
            self.angle -= 2 * math.pi

        if self.isJumping:
            self.jumpTime += dt
            if self.jumpTime >= self.jumpDuration:
                self.isJumping = False
                self.try_attach(platforms)
        else:
            self.try_attach(platforms)

    def draw(self):
        jumpOffset = self.get_jump_offset()
        # Draw shadow
        glColor4f(0, 0, 0, 0.3)
        draw_filled_circle(self.x, self.y, self.radius)
        # Draw player with rotation
        glPushMatrix()
        glTranslatef(self.x, self.y - jumpOffset, 0)
        glRotatef(math.degrees(self.angle), 0, 0, 1)
        # red
        glColor3f(1.0, 0.0, 0.0)
        draw_filled_circle(0, 0, self.radius)
        glPopMatrix()
