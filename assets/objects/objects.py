import sys
import math
import random
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

from utils.graphics import draw_filled_circle
from asset_maker.maker import draw_shadow_at, load_shapes, draw_stroke,draw_at

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


class Crocodile:
    """
    Moves up and down, jumps over platforms, and has a shadow effect.
    """
    def __init__(self, x=WINDOW_WIDTH/2, y=0, speed=100.0,
                 jumpDuration=1, jumpHeight=20.0, radius=20,shape=load_shapes("assets\objects\crocodile_shape.json"),
                 jump_detection_range=70, animDuration=0.25
                 ):  # Lookahead distance for jumps
        self.x = x
        self.y = y
        self.speed = speed
        self.vx = 0
        self.vy = speed
        self.radius = radius
        self.shape = shape

        # Jump state
        self.isJumping = False
        self.jumpTime = 0.0
        self.jumpDuration = jumpDuration
        self.jumpHeight = jumpHeight

        # Detection for early jumps
        self.jump_detection_range = jump_detection_range  # Distance ahead to detect platforms

        # Flag to remove the crocodile after finishing its cycle
        self.disappear = False
        
        # y flip
        self.flipx = False
        self.flipy= False
        
        # animation variable
        self.animTime=0;
        self.animSpeed=0.5;
        self.animDuration=animDuration;
        

    def get_jump_offset(self):
        """
        Returns a parabolic offset in Y during the jump animation.
        The parabola peaks at t = 0.5 * jumpDuration with jumpHeight offset.
        """
        if not self.isJumping:
            return 0.0
        t = self.jumpTime / self.jumpDuration  # Goes from 0 to 1
        return self.jumpHeight * 4.0 * t * (1.0 - t)

    def start_jump(self):
        """Initiate the jump animation."""
        if not self.isJumping:
            self.isJumping = True
            self.jumpTime = 0.0

    def update(self, dt, platforms):
        """
        Moves vertically, detects platforms early, and initiates jumps.
        """
        # ---------------------------
        # Handle jump timing
        # ---------------------------
        if self.isJumping:
            self.jumpTime += dt
            if self.jumpTime >= self.jumpDuration:
                self.isJumping = False
                self.jumpTime = 0.0
        
        # animation update
        self.animTime += dt
        if self.animTime >= self.animDuration:
            self.flipx= not self.flipx
            self.animTime = 0.0


        # ---------------------------
        # Check for platforms to jump EARLY
        # ---------------------------
        if not self.isJumping:
            for platform in platforms:
                # Check if crocodile's x is near the platform's x
                if (platform.x - platform.radius) <= self.x <= (platform.x + platform.radius):
                    # Look ahead by 'jump_detection_range' to anticipate a jump
                    future_y = self.y + (self.vy * dt) + self.jump_detection_range

                    # If moving downward and approaching platform
                    if self.vy > 0 and self.y < platform.y <= future_y:
                        self.start_jump()
                        break
                    # If moving upward and approaching platform
                    elif self.vy < 0 and self.y > platform.y >= (self.y - self.speed * dt - self.jump_detection_range):
                        self.start_jump()
                        break

        # ---------------------------
        # Update vertical position
        # ---------------------------
        self.y += self.vy * dt

        # ---------------------------
        # Reverse direction or remove
        # ---------------------------
        # If moving downward and we pass the bottom, reverse to go up
        if self.vy > 0 and self.y > WINDOW_HEIGHT:
            self.vy = -self.speed
            self.flipy= not self.flipy
        # If moving upward and we cross above the top, mark to disappear
        elif self.vy < 0 and self.y < 0:
            # self.disappear = True
            self.vy=self.speed
            self.flipy= not self.flipy

    def draw(self):
        """
        Draw the crocodile with a shadow and a parabolic jump effect.
        """
        # Calculate jump offset
        jumpOffset = self.get_jump_offset()
        croc_y = self.y - jumpOffset  # Apply jump effect

        # ---------------------------
        # Draw shadow (slightly below crocodile)
        # ---------------------------
        # glColor4f(0, 0, 0, 0.3)  # Black with transparency
        if(self.flipy==True):
            if(self.flipx==False):
                draw_shadow_at(self.shape, self.x-130, self.y-100,0.4)
                draw_at(self.shape, self.x-130, self.y-jumpOffset-100,0.4)
            else:
                draw_shadow_at(self.shape, self.x+145, self.y-100,-0.4,0.4)
                draw_at(self.shape, self.x+145, self.y-jumpOffset-100,-0.4,0.4)

        else:
            if(self.flipx==False):
                draw_shadow_at(self.shape, self.x-130, self.y+100,0.4,-0.4)
                draw_at(self.shape, self.x-130, self.y-jumpOffset+100,0.4,-0.4)
            
            else:
                draw_shadow_at(self.shape, self.x+145, self.y+100,-0.4,-0.4)
                draw_at(self.shape, self.x+145, self.y-jumpOffset+100,-0.4,-0.4)

        # draw_filled_circle(self.x, self.y, self.radius)  # Slightly bigger shadow

        # ---------------------------
        # Draw crocodile (light green)
        # ---------------------------
        # glColor3f(0.0, 1.0, 0.0)
        # draw_filled_circle(self.x, croc_y, self.radius)
        # glColor3f(0.0, 1.0, 0.0)
        # draw at
        


# -------------------------------------------------
# Player Class
# -------------------------------------------------
class Player:
    def __init__(self, x=LEFT_BANK_WIDTH/2
                 , y=WINDOW_HEIGHT/2,radious=12
                 ,speed=200.0,shape=load_shapes("assets\objects\player_shape.json"),
                 jumpDuration=0.5, jumpHeight=40.0, angularSpeed=2.0,health=100,lives=3
                 ):
        self.radius = radious
        self.x = x
        self.y = y
        self.speed = speed
        self.dx = 0
        self.dy = 0
        self.isJumping = False
        self.jumpTime = 0.0
        self.jumpDuration = jumpDuration  # seconds
        self.jumpHeight = jumpHeight
        self.attachedPlatform = None
        self.angle = 0.0
        self.angularSpeed = angularSpeed  # radians/sec
        self.player_shape = shape
        self.health = health
        self.lives = lives
        self.isDead = False
        self.damage_effect_time=0.0
        self.damage_effect_duration=1.5
        self.damage_effect_active=False

    def damage(self,damage):
        if(self.damage_effect_active):
            return False
        self.health -= damage
        self.damage_effect_active=True
        self.damage_effect_time=0.0
        if self.health <= 0:
            self.lives -= 1
            self.health = 100
            if self.lives <= 0:
                self.isDead = True
            print('LIFE LOST')
            return True
        
        return False




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
        if keys[K_LEFT] or keys[K_a]:
            self.dx = -self.speed
        if keys[K_RIGHT] or keys[K_d]:
            self.dx = self.speed
        if keys[K_UP] or keys[K_w]:
            self.dy = -self.speed
        if keys[K_DOWN] or keys[K_s]:
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

        # damage
        if(self.damage_effect_active):
            self.damage_effect_time += dt
            if(self.damage_effect_time >=self.damage_effect_duration):
                self.damage_effect_active=False
                self.damage_effect_time=0.0


    def draw(self):
        jumpOffset = self.get_jump_offset()
        # # Draw shadow
        glColor4f(0, 0, 0, 0.3)
        draw_filled_circle(self.x, self.y, self.radius)
        # Draw player with rotation
        glPushMatrix()
        # glTranslatef(self.x, self.y - jumpOffset, 0)
        # draw_shadow_at(self.player_shape, self.x-40, self.y-35,0.15)
        glRotatef(math.degrees(self.angle), 0, 0, 1)
        # red
        glColor3f(1.0, 0.0, 0.0)
        draw_filled_circle(0, 0, self.radius)
        glPopMatrix()
        # # draw_stroke(self.player_shape)
        # print(self.player_shape)
        # draw_at(self.player_shape, self.x, self.y)
        # for shape in self.player_shape:
        # draw_at(self.player_shape, self.x-40, self.y-35,0.15)
        # draw with jump offset

        if(self.damage_effect_active):
            # blink effect
            if(int(self.damage_effect_time*10)%2==0):
                return

        draw_at(self.player_shape, self.x-40, self.y-jumpOffset-35,0.15)

        