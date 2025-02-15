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
from assets.objects.objects import Platform, Player, Crocodile, Doll
from gui_utils import GuiUtils
from utils.graphics import draw_grass, load_texture, textured_grass, draw_animated_river
import os

# -------------------------------------------------
# Constants & Setup
# -------------------------------------------------

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

LEFT_BANK_WIDTH = 100
RIGHT_BANK_WIDTH = 100
SQUID_START_X = LEFT_BANK_WIDTH
SQUID_END_X = WINDOW_WIDTH - RIGHT_BANK_WIDTH

NUM_COLUMNS = 6
CELL_WIDTH = (SQUID_END_X - SQUID_START_X) / NUM_COLUMNS
ROW_Y = [WINDOW_HEIGHT / 3, WINDOW_HEIGHT / 2, (2 * WINDOW_HEIGHT) / 3]

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
        ],
        "enemy": [
            {"x": 250, "y": 500, "speed": 50},
            {"x": 450, "y": 100, "speed": 50}
        ],
        "need_coins": 4
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
            {"x": 250, "y": 500, "speed": 100},
            {"x": 450, "y": 100, "speed": 100}

        ],
        "need_coins": 6
    }
]

# -------------------------------------------------
# SquidCrossingGame Class 
# -------------------------------------------------

class SquidCrossingGame:
    def __init__(self, gui: GuiUtils = None, impl=None):
        self.levels = LEVELS
        self.currentLevelIdx = 0
        self.need_coins = 3
        self.shapes = load_shapes("shapes.json")
        self.player_shape = load_shapes("assets/shapes/squid_player.json")
        self.squid_sky = load_shapes("assets/shapes/sky.json")
        self.squid_bank = load_shapes("assets/shapes/squid_bank.json")
        self.squid_shape = load_shapes("assets/shapes/squid_bg.json")
        self.load_level()
        self.gameOver = False
        self.win = False

        self.squid_textures = [load_texture(f"assets/textures/water/000{i}.png") if i <= 9 else load_texture(f"assets/textures/water/00{i}.png") for i in range(40)]
        self.grass_texture = load_texture("assets/textures/grass/Grass10.png")

        self.paused = False
        self.gui = gui
        self.impl = impl

        self.first_time_coins=True
        self.all_stories = {
                "start": {
                    "title": "The Final Portal",
                    "lines": [
                        "You jump through the last portal and land in a desolate arena.",
                        "The ground is scattered with moving platforms.",
                        "A giant doll stands in the distance, its lifeless eyes scanning the area.",
                        "They say this doll has already taken down 100 players before you.",
                        "Strange birds peck at the ground, indifferent to what’s coming.",
                        "The rules are simple: Move at the wrong time, and you won’t make it out."
                    ]
                },
                "level2": {
                    "title": "Level 1 Complete: The Doll Watches",
                    "lines": [
                        "You made it across, but the doll isn’t done.",
                        "Its head turns slowly, searching for movement.",
                        "The 100 before you didn’t stand a chance.",
                        "Stay on the platforms—they seem to be safe.",
                        "The birds keep eating, oblivious to the danger."
                    ]
                },
                "level3": {
                    "title": "Level 2 Complete: The Final Test",
                    "lines": [
                        "You're getting closer to the exit.",
                        "The doll is watching for the slightest mistake.",
                        "The platforms shift unpredictably beneath your feet.",
                        "One last challenge, and you might be the first to survive."
                    ]
                },
                "coins": {
                    "title": "Not Enough Coins",
                    "lines": [
                        "You need more coins to continue.",
                        "Try collecting more before moving forward."
                    ],
                    "button_label": "Got It"
                }
            }

        
        self.story_shown = False
        self.current_story_data = self.all_stories["start"]

        if not os.path.exists('saves/squid'):
            os.makedirs('saves/squid')

    def new_game(self):
        self.currentLevelIdx = 0
        self.load_level()
        self.gameOver = False
        self.win = False
        self.story_shown = False
        self.current_story_data = self.all_stories["start"]

    def save_game_state(self):
        """Save the current game state to a JSON file"""
        game_state = {
            'player': {
                'x': self.player.x,
                'y': self.player.y,
                'health': self.player.health,
                'lives': self.player.lives,
                'coins': self.player.coins,
                'isJumping': self.player.isJumping,
            },
            'level': self.currentLevelIdx,
            'platforms': [
                {
                    'x': p.x,
                    'y': p.y,
                    'vx': p.vx,
                    'row': p.row,
                    'col': p.col,
                    'leftBound': p.leftBound,
                    'rightBound': p.rightBound,
                    'speed': p.speed
                } for p in self.platforms
            ],
            'enemies': [
                {
                    'x': e.x,
                    'y': e.y,
                    'speed': e.speed
                } for e in self.enemies
            ]
        }

        try:
            with open('saves/squid/game_save.json', 'w') as f:
                json.dump(game_state, f)
            return True
        except Exception as e:
            print(f"Error saving game state: {e}")
            return False

    def load_game_state(self):
        """Load the game state from a JSON file"""
        try:
            with open('saves/squid/game_save.json', 'r') as f:
                game_state = json.load(f)

            # Restore player state
            self.player.x = game_state['player']['x']
            self.player.y = game_state['player']['y']
            self.player.health = game_state['player']['health']
            self.player.lives = game_state['player']['lives']
            self.player.coins = game_state['player']['coins']
            self.player.isJumping = game_state['player']['isJumping']

            # Restore level
            self.currentLevelIdx = game_state['level']

            # Restore platforms
            self.platforms = []
            for p_data in game_state['platforms']:
                p = Platform(p_data['row'], p_data['col'],
                             p_data['leftBound'], p_data['rightBound'],
                             p_data['speed'], issquid=True)
                p.x = p_data['x']
                p.y = p_data['y']
                p.vx = p_data['vx']
                self.platforms.append(p)

            # Restore enemies
            self.enemies = []
            for e_data in game_state['enemies']:
                e = Crocodile(x=e_data['x'], y=e_data['y'], inSquid=True)
                e.speed = e_data['speed']
                self.enemies.append(e)

            return True
        except FileNotFoundError:
            print("No saved game found")
            return False
        except Exception as e:
            print(f"Error loading game state: {e}")
            return False

    def render_pause_menu(self):
        """Render the pause menu"""
        if not self.paused:
            return None

        choice = None
        if self.gui.begin_centered_window("Pause Menu", 300, 470, WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 - 200):
            if self.is_win():
                self.gui.draw_text_centered("Congratulations, You Win!", color=(1, 1, 0, 1))
                self.gui.add_spacing(20)
            elif self.is_game_over():
                self.gui.draw_text_centered("Game Over, you lose!", color=(1, 0, 0, 1))
                self.gui.add_spacing(20)
            else:
                self.gui.draw_text_centered("Game Paused", color=(1, 1, 1, 1))
                self.gui.add_spacing(20)
                if self.gui.draw_centered_button("Resume", 260, 50):
                    choice = "resume"

            self.gui.add_spacing(10)

            if self.gui.draw_centered_button("New Game", 260, 50):
                choice = "New Game"
            self.gui.add_spacing(10)

            if self.gui.draw_centered_button("Save Game", 260, 50):
                choice = "save"

            self.gui.add_spacing(10)

            if self.gui.draw_centered_button("Load Game", 260, 50):
                choice = "load"

            self.gui.add_spacing(10)

            if self.gui.draw_centered_button("Exit to Main Menu", 260, 50):
                choice = "exit"

            imgui.end()

        return choice

    def hud(self, gui: GuiUtils):
        """Render the persistent game HUD"""
        if gui.begin_centered_window("Game HUD", 400, 60, 10, 10):
            gui.draw_text(f"Health: {int(self.player.health)} lives: {self.player.lives} coins: {self.player.coins}/{self.need_coins} level: {self.currentLevelIdx + 1}", 10, 10, (1, 0, 0, 1))
            gui.draw_text(f"watch the doll,she shoots when she catches you moving", 10, 25, (1, 0, 1, 1))
            imgui.end()

    def gui_story(self):
        """
        Unified function to display any story overlay.
        Uses self.all_stories for text. If no current story is set
        and the starting story hasn't been dismissed, it uses the 'start' story.
        """
        if self.current_story_data is None:
            return

        if self.gui.begin_centered_window("Story", 500, 300, WINDOW_WIDTH // 2 - 250, WINDOW_HEIGHT // 2 - 150, bg_color=(0.4, 0.4, 0.9, 0.8)):
            self.gui.draw_text_centered(self.current_story_data.get("title", "Story"), color=(1, 1, 0, 1))
            self.gui.add_spacing(10)
            y_offset = 60
            for line in self.current_story_data.get("lines", []):
                self.gui.draw_text(line, 20, y_offset, color=(1, 1, 1, 1))
                y_offset += 20
            self.gui.add_spacing(20)
            button_label = self.current_story_data.get("button_label", "Continue")
            if self.gui.draw_centered_button(button_label, 300, 50):
                if not self.story_shown:
                    self.story_shown = True
                self.current_story_data = None
            imgui.end()

    def draw_gui(self):
        if self.paused == False and self.story_shown == False:
            self.gui_story()
        self.hud(self.gui)

    def load_level(self):
        self.player = Player(speed=100, shape=self.player_shape)
        self.doll = Doll()
        self.platforms = []
        levelData = self.levels[self.currentLevelIdx]
        self.need_coins = levelData["need_coins"]
        for pd in levelData["platforms"]:
            p = Platform(
                pd["row"],
                pd["col"],
                pd["leftBound"],
                pd["rightBound"],
                pd["speed"],
                issquid=True
            )
            self.platforms.append(p)

        self.enemies = []
        if "enemy" in levelData:
            for ed in levelData["enemy"]:
                e = Crocodile(
                    x=ed['x'], y=ed['y'],
                    inSquid=True,
                )
                self.enemies.append(e)

        self.gameOver = False
        self.win = False

    def update(self, dt, keys):
        if keys[pygame.K_ESCAPE]:
            self.paused = not self.paused
            return

        if self.paused:
            return

        for p in self.platforms:
            p.update(dt)

        for crocodile in self.enemies:
            crocodile.update(dt, self.platforms)

        collision_padding = 0.5

        for i in range(len(self.platforms)):
            for j in range(i + 1, len(self.platforms)):
                p1 = self.platforms[i]
                p2 = self.platforms[j]
                dx = p1.x - p2.x
                dy = p1.y - p2.y
                distance = math.hypot(dx, dy)
                min_distance = p1.radius + p2.radius + collision_padding

                if distance < min_distance:
                    if (p1.vx > 0 and p2.vx < 0) or (p1.vx < 0 and p2.vx > 0):
                        p1.vx = -p1.vx
                        p2.vx = -p2.vx

                    if distance == 0:
                        distance = 0.1
                    overlap = (min_distance - distance)
                    nx = dx / distance
                    ny = dy / distance
                    correction_factor = 0.25
                    p1.x += nx * overlap * correction_factor
                    p1.y += ny * overlap * correction_factor
                    p2.x -= nx * overlap * correction_factor
                    p2.y -= ny * overlap * correction_factor

        self.player.space_update(dt, keys, self.platforms)
        self.doll.update(dt)

        if (not self.player.isJumping and not self.player.hover_active and
                self.player.x > SQUID_START_X and self.player.x < SQUID_END_X and
                self.player.attachedPlatform is None and self.doll.is_looking() and (abs(self.player.vx) >= 0.15 or abs(self.player.vy) >= 0.2)):
            self.doll.shoot_player(self.player, 10 + self.player.health / 3)

        if not self.player.isJumping:
            for e in self.enemies:
                dx = self.player.x - e.x
                dy = self.player.y - e.y
                if math.hypot(dx, dy) < (self.player.radius + e.radius):
                    self.player.damage(10)
                    pass

        if self.player.isDead:
            self.gameOver = True
        
        if(self.player.x >= WINDOW_WIDTH - 40 and self.player.coins <self.need_coins and self.first_time_coins):
            self.story_shown=False
            self.current_story_data = self.all_stories.get("coins", None)
            self.first_time_coins=False

        if self.player.x >= WINDOW_WIDTH - 40 and self.player.coins >= self.need_coins:
            self.win = True

    def draw(self):
        draw_at(self.squid_shape, -220, -180, 1.5, 1.5)
        draw_at(self.squid_sky, -200, -180, 1.5, 1.2)
        draw_at(self.squid_bank, -320, -200, 1, 1.5)
        draw_at(self.squid_bank, 1120, -200, -1, 1.5)

        for p in self.platforms:
            p.draw()

        self.player.draw()

        for crocodile in self.enemies:
            crocodile.draw()

        self.doll.draw(self.player)

        glFlush()

    def is_game_over(self):
        return self.gameOver

    def is_win(self):
        return self.win

    def next_level(self):
        self.currentLevelIdx += 1
        try:
            self.current_story_data = self.all_stories.get(f"level{self.currentLevelIdx + 1}", None)
            if self.current_story_data is not None:
                self.story_shown = False
        except:
            print("Error in getting story data, no story data to show")

        if self.currentLevelIdx >= len(self.levels):
            return False

        self.load_level()
        return True

    def game_loop(self):
        impl = self.impl
        clock = pygame.time.Clock()

        running = True
        overlay_displayed = False

        while running:
            dt = clock.tick(FPS) / 1000.0
            keys = pygame.key.get_pressed()

            for event in pygame.event.get():
                impl.process_event(event)
                if event.type == QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN:
                    pass

            imgui.new_frame()
            pause_choice = self.render_pause_menu()
            if pause_choice:
                if pause_choice == "New Game":
                    self.paused = False
                    self.new_game()
                elif pause_choice == "resume":
                    self.paused = False
                elif pause_choice == "save":
                    if self.save_game_state():
                        print("Game saved successfully!")
                elif pause_choice == "load":
                    if self.load_game_state():
                        print("Game loaded successfully!")
                        self.paused = False
                elif pause_choice == "exit":
                    print("main menu...")
                    return True
                    running = False

            if not self.paused and not overlay_displayed and self.story_shown == True:
                self.update(dt, keys)
                if self.is_game_over():
                    print("Game Over!")
                    self.paused = True
                elif self.is_win():
                    if not self.next_level():
                        if self.story_shown == True:
                            print("Congratulations! You completed all levels!")
                            self.paused = True
                    else:
                        print("Level Complete! Next level loaded.")

            self.draw_gui()

            glClear(GL_COLOR_BUFFER_BIT)
            self.draw()

            imgui.render()
            impl.render(imgui.get_draw_data())
            pygame.display.flip()
