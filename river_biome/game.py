import json
import sys
import math
import random
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from asset_maker.test import load_shapes, draw_stroke,draw_at
from assets.objects.objects import Platform, Player,Crocodile
from utils.graphics import draw_grass,load_texture,draw_animated_river,draw_river,textured_grass

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
# Updated Levels Configuration (Speeds Multiplied by 60)
# -------------------------------------------------
LEVELS = [
    # Level 1
    {
        "level": 1,
        "platforms": [
            {"row": 1, "col": 1, "leftBound": 1, "rightBound": 3, "speed": 60.0},
            {"row": 2, "col": 2, "leftBound": 2, "rightBound": 4, "speed": 90.0},
            {"row": 3, "col": 3, "leftBound": 3, "rightBound": 5, "speed": 48.0},
            {"row": 2, "col": 4, "leftBound": 3, "rightBound": 5, "speed": 72.0},
            {"row": 3, "col": 5, "leftBound": 4, "rightBound": 6, "speed": 60.0},
            {"row": 2, "col": 6, "leftBound": 4, "rightBound": 6, "speed": 108.0}
        ]
        ,
        "enemy": [
            { "x":180,"y":500,"speed":100}
        ]
    },
    # Level 2
    {
        "level": 2,
        "platforms": [
            {"row": 1, "col": 1, "leftBound": 1, "rightBound": 3, "speed": 90.0},
            {"row": 2, "col": 2, "leftBound": 2, "rightBound": 4, "speed": 120.0},
            {"row": 3, "col": 3, "leftBound": 3, "rightBound": 5, "speed": 72.0},
            {"row": 2, "col": 4, "leftBound": 3, "rightBound": 5, "speed": 108.0},
            {"row": 3, "col": 5, "leftBound": 4, "rightBound": 6, "speed": 90.0},
            {"row": 2, "col": 6, "leftBound": 4, "rightBound": 6, "speed": 132.0}
        ],
        "enemy": [
            { "x":180,"y":600,"speed":120}
            
        ]
    }
]


# -------------------------------------------------
# RiverCrossingGame Class (Mirrors JS Logic)
# -------------------------------------------------


class RiverCrossingGame:
    def __init__(self):
        self.levels = LEVELS
        self.currentLevelIdx = 0
        self.shapes = load_shapes("shapes.json")
        # self.shapes = [flip_shape_horizontally(shape, WINDOW_WIDTH) for shape in self.shapes]
        self.load_level()
        self.gameOver = False
        self.win = False
        
        # self.river_textures = [if i<=9:load_texture(f"assets/textures/water/000{i}.png") else:load_texture(f"assets/textures/water/00{i}.png") for i in range(39)]
        # if i<=9:load_texture(f"assets/textures/water/000{i}.png") else:load_texture(f"assets/textures/water/00{i}.png")
        self.river_textures = [load_texture(f"assets/textures/water/000{i}.png") if i<=9 else load_texture(f"assets/textures/water/00{i}.png") for i in range(40)]
        self.grass_texture = load_texture("assets/textures/grass/Grass10.png")



    def load_level(self):
        self.player = Player()
        self.platforms = []
        levelData = self.levels[self.currentLevelIdx]
        for pd in levelData["platforms"]:
            p = Platform(
                pd["row"],
                pd["col"],
                pd["leftBound"],
                pd["rightBound"],
                pd["speed"]
            )
            self.platforms.append(p)

        self.enemies = []
        if "enemy" in levelData:
            for ed in levelData["enemy"]:
                e = Crocodile(
                    x=ed['x'],y=ed['y']
                )
                self.enemies.append(e)
        
        self.gameOver = False
        self.win = False

    def update(self, dt, keys):
        for p in self.platforms:
            p.update(dt)

        for crocodile in self.enemies:
            crocodile.update(dt,self.platforms)
        # Platform collisions: if two overlap, reverse their vx immediately.
        for i in range(len(self.platforms)):
            for j in range(i+1, len(self.platforms)):
                dx = self.platforms[i].x - self.platforms[j].x
                dy = self.platforms[i].y - self.platforms[j].y
                if math.hypot(dx, dy) < (self.platforms[i].radius + self.platforms[j].radius):
                    self.platforms[i].vx = -self.platforms[i].vx
                    self.platforms[j].vx = -self.platforms[j].vx

        self.player.update(dt, keys, self.platforms)

        # Strict death condition: if player is in the river and not attached.
        if (not self.player.isJumping and 
            self.player.x > RIVER_START_X and self.player.x < RIVER_END_X and 
            self.player.attachedPlatform is None):
            self.gameOver = True

        # Strict death condition: if player is not jumping and crocodile touches
        
        if (not self.player.isJumping ):
            for e in self.enemies:
                dx = self.player.x - e.x
                dy = self.player.y - e.y
                if math.hypot(dx, dy) < (self.player.radius + e.radius):  
                    self.gameOver = True
            
            







        if self.player.x >= RIVER_END_X:
            self.win = True

 

    def draw(self):
        # Draw left bank (grass)
        draw_grass(0, 0, RIVER_START_X, 0, RIVER_START_X, WINDOW_HEIGHT, 0, WINDOW_HEIGHT)
        textured_grass(0, 0, RIVER_START_X, 0, RIVER_START_X, WINDOW_HEIGHT, 0, WINDOW_HEIGHT, self.grass_texture)

        # Draw right bank (grass)
        draw_grass(RIVER_END_X, 0, WINDOW_WIDTH, 0, WINDOW_WIDTH, WINDOW_HEIGHT, RIVER_END_X, WINDOW_HEIGHT)
        textured_grass(RIVER_END_X, 0, WINDOW_WIDTH, 0, WINDOW_WIDTH, WINDOW_HEIGHT, RIVER_END_X, WINDOW_HEIGHT, self.grass_texture)

        # Draw river (blue water)
        # glColor3f(0.0, 0.4, 1.0)
        # glBegin(GL_QUADS)
        # glVertex2f(RIVER_START_X, 0)
        # glVertex2f(RIVER_END_X, 0)
        # glVertex2f(RIVER_END_X, WINDOW_HEIGHT)
        # glVertex2f(RIVER_START_X, WINDOW_HEIGHT)
        # glEnd()
        # draw_river(RIVER_START_X, 0, RIVER_END_X, 0, RIVER_END_X, WINDOW_HEIGHT, RIVER_START_X, WINDOW_HEIGHT)
        draw_animated_river(RIVER_START_X, 0, RIVER_END_X, 0, RIVER_END_X, WINDOW_HEIGHT, RIVER_START_X, WINDOW_HEIGHT, self.river_textures)

        # 2) Draw the shapes from test.py
        # for shape in self.shapes:
        #     draw_ST(shape, 0, 100)
        draw_at(self.shapes, 0, 100)
        # 3) Draw the platforms
        for p in self.platforms:
            p.draw()

        # 4) Draw the player
        self.player.draw()

        # 5) draw the enemies
        for crocodile in self.enemies:
            crocodile.draw()

        # Flush to finish drawing
        glFlush()


    def is_game_over(self):
        return self.gameOver

    def is_win(self):
        return self.win

    def next_level(self):
        self.currentLevelIdx += 1
        if self.currentLevelIdx >= len(self.levels):
            return False
        self.load_level()
        return True
        return self.gameOver

    def is_win(self):
        return self.win

    def next_level(self):
        self.currentLevelIdx += 1
        if self.currentLevelIdx >= len(self.levels):
            return False
        self.load_level()
        return True
    
    def game_loop(self):
        # pygame.init()
        # pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), DOUBLEBUF | OPENGL)
        # pygame.display.set_caption("River Crossing – PyOpenGL/Pygame (JS Logic)")
        clock = pygame.time.Clock()
        # self.init_opengl()

        running = True
        overlay_displayed = False

        while running:
            dt = clock.tick(FPS) / 1000.0
            keys = pygame.key.get_pressed()

            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    elif event.key == K_SPACE:
                        self.player.start_jump()

            if not overlay_displayed:
                self.update(dt, keys)
                if self.is_game_over():
                    overlay_displayed = True
                    print("Game Over!")
                elif self.is_win():
                    if not self.next_level():
                        print("Congratulations! You completed all levels!")
                        running = False
                    else:
                        print("Level Complete! Next level loaded.")
            glClear(GL_COLOR_BUFFER_BIT)
            self.draw()
            pygame.display.flip()

    

