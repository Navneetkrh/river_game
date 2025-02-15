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
from assets.objects.objects import Platform, Player,Crocodile
from gui_utils import GuiUtils
from utils.graphics import draw_animated_space, draw_grass,load_texture,textured_grass,draw_animated_river
import os
# -------------------------------------------------
# Constants & Setup
# -------------------------------------------------

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

LEFT_BANK_WIDTH = 100
RIGHT_BANK_WIDTH = 100
space_START_X = LEFT_BANK_WIDTH
space_END_X = WINDOW_WIDTH - RIGHT_BANK_WIDTH

NUM_COLUMNS = 6
CELL_WIDTH = (space_END_X - space_START_X) / NUM_COLUMNS
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
            { "x":250,"y":500,"speed":100},
            { "x":450,"y":100,"speed":100}
        ],
        "need_coins":4
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
            
        ],
        "need_coins":4
    }
]


# -------------------------------------------------
# spaceCrossingGame Class (Mirrors JS Logic)
# -------------------------------------------------


class SpaceCrossingGame:
    def __init__(self,gui:GuiUtils=None,impl=None):
        self.levels = LEVELS
        self.currentLevelIdx = 0
        self.need_coins=3
        self.shapes = load_shapes("shapes.json")
        self.space_rock_shape = load_shapes("assets/shapes/space_rock.json")
        self.ufo_shapes = [load_shapes("assets/shapes/ufo1.json"),load_shapes("assets/shapes/ufo2.json")]
        self.space_man_shape = load_shapes("assets/shapes/space_man.json")
        # self.shapes = [flip_shape_horizontally(shape, WINDOW_WIDTH) for shape in self.shapes]
        self.load_level()
        self.gameOver = False
        self.win = False
        
        # self.space_textures = [if i<=9:load_texture(f"assets/textures/water/000{i}.png") else:load_texture(f"assets/textures/water/00{i}.png") for i in range(39)]
        # if i<=9:load_texture(f"assets/textures/water/000{i}.png") else:load_texture(f"assets/textures/water/00{i}.png")
        self.space_textures = [load_texture(f"assets/textures/water/000{i}.png") if i<=9 else load_texture(f"assets/textures/water/00{i}.png") for i in range(40)]
        self.grass_texture = load_texture("assets/textures/grass/Grass10.png")

        self.space_bg = load_shapes("assets/shapes/starry_sky.json")
        self.space_bank = load_shapes("assets/shapes/space_bank.json")

       



        self.paused = False
        self.gui = gui
        self.impl = impl
        
        # make saves directory if it doesn't exist
      
        # if not os.path.exists('saves'):
        #     os.makedirs('saves')

        
        if not os.path.exists('saves/space'):
            os.makedirs('saves/space')

    def new_game(self):
        self.currentLevelIdx = 0
        self.load_level()
        self.gameOver = False
        self.win = False


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
            ,
        
        }
        
        try:
            with open('saves/space/game_save.json', 'w') as f:
                json.dump(game_state, f)
            return True
        except Exception as e:
            print(f"Error saving game state: {e}")
            return False



    def load_game_state(self):
        """Load the game state from a JSON file"""
        try:
            
            with open('saves/space/game_save.json', 'r') as f:
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
                           p_data['speed'],
                           shape=self.space_rock_shape
                           )
                p.x = p_data['x']
                p.y = p_data['y']
                p.vx = p_data['vx']
                self.platforms.append(p)
            
            # Restore enemies
            self.enemies = []
            for e_data in game_state['enemies']:
                e = Crocodile(x=e_data['x'], y=e_data['y'],inSpace=True
                               ,shape=self.ufo_shapes[random.randint(0,1)])
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
        # remarks="Game Paused"
        if not self.paused:
            return None
        
        
        choice = None
        if self.gui.begin_centered_window("Pause Menu", 300, 470, WINDOW_WIDTH//2-150, WINDOW_HEIGHT//2-200):
            if(self.is_win()):
                self.gui.draw_text_centered("Congratulations, You Win!", color=(1, 1, 0, 1))
                self.gui.add_spacing(20)
            elif(self.is_game_over()):
                self.gui.draw_text_centered("Game Over,you lose!", color=(1, 0, 0, 1))
                self.gui.add_spacing(20)
            else:
                self.gui.draw_text_centered("Game Paused",color= (1, 1, 1, 1))
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


    
    def hud(self,gui: GuiUtils):
        """Render the persistent game HUD"""
        
        # Create a window in the top-left corner with no title bar
        if gui.begin_centered_window("Game HUD", 400, 60, 10, 10):  # Adjust size and position as needed
            # Example HUD elements
            gui.draw_text(f"Health: {self.player.health} lives: {self.player.lives} coins: {self.player.coins}", 10, 10, (1, 0, 0, 1))
            # gui.add_spacing(5)
            # gui.draw_text(f"")
            # gui.add_spacing(5)
            # gui.draw_text("Time: 00:00")
            
            imgui.end()



    def draw_gui(self):
        self.hud(self.gui)
        
        return


    def load_level(self):
        self.player = Player(speed=100,shape=self.space_man_shape,inspace=True)
        self.platforms = []
        levelData = self.levels[self.currentLevelIdx]
        self.need_coins=levelData["need_coins"]
        for pd in levelData["platforms"]:
            p = Platform(
                pd["row"],
                pd["col"],
                pd["leftBound"],
                pd["rightBound"],
                pd["speed"],
                shape=self.space_rock_shape
                
            )
            self.platforms.append(p)

        self.enemies = []
        if "enemy" in levelData:
            for ed in levelData["enemy"]:
                e = Crocodile(
                    x=ed['x'],y=ed['y']
                    ,
                    inSpace=True,
                    shape=self.ufo_shapes[random.randint(0,1)]
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
            crocodile.update(dt,self.platforms)
        # Platform collisions: if two overlap, reverse their vx immediately.
        collision_padding = 0.5  # Small extra distance to prevent sticking

        for i in range(len(self.platforms)):
            for j in range(i + 1, len(self.platforms)):
                p1 = self.platforms[i]
                p2 = self.platforms[j]
                dx = p1.x - p2.x
                dy = p1.y - p2.y
                distance = math.hypot(dx, dy)
                min_distance = p1.radius + p2.radius + collision_padding

                # Only process collision if moving towards each other horizontally.
                if distance < min_distance:
                    # Reverse horizontal velocities only if they're moving towards one another.
                    if (p1.vx > 0 and p2.vx < 0) or (p1.vx < 0 and p2.vx > 0):
                        p1.vx = -p1.vx
                        p2.vx = -p2.vx

                    # Apply a gentle separation to reduce overlap:
                    if distance == 0:
                        # Prevent division by zero
                        distance = 0.1
                    overlap = (min_distance - distance)
                    # Calculate normalized displacement.
                    nx = dx / distance
                    ny = dy / distance
                    # Apply a fraction of the overlap to each platform.
                    correction_factor = 0.25  # Tune this factor as needed.
                    p1.x += nx * overlap * correction_factor
                    p1.y += ny * overlap * correction_factor
                    p2.x -= nx * overlap * correction_factor
                    p2.y -= ny * overlap * correction_factor
        self.player.space_update(dt, keys, self.platforms)

        # Strict death condition: if player is in the space and not attached.
        if (not self.player.isJumping and not self.player.hover_active and
            self.player.x > space_START_X and self.player.x < space_END_X and 
            self.player.attachedPlatform is None):
            # damage by health
            self.player.damage(self.player.health)
            
            # if(self.player.lives<=0):
            #     self.gameOver = True

        # condition: if player is not jumping and crocodile touches
        # then take 35 damage
        if (not self.player.isJumping ):
            for e in self.enemies:
                dx = self.player.x - e.x
                dy = self.player.y - e.y
                if math.hypot(dx, dy) < (self.player.radius + e.radius): 
                    self.player.damage(35) 
        
        if(self.player.isDead==True):
            self.gameOver = True
        
            







        if self.player.x >= WINDOW_WIDTH-40 and self.player.coins>=self.need_coins:
            print("coins ",self.player.coins," need coins ",self.need_coins)
            self.win = True

 

    def draw(self):
        draw_at(self.space_bg, -50, -90,1.2,1.2)
        # Draw left bank (grass)
        # draw_grass(0, 0, space_START_X, 0, space_START_X, WINDOW_HEIGHT, 0, WINDOW_HEIGHT)
        # glColor3f(1,1,1)
        draw_at(self.space_bank, -260, -100, 0.8, 1.2)
        # draw_grass(0, 0, space_START_X, 0, space_START_X, WINDOW_HEIGHT, 0, WINDOW_HEIGHT)
        # draw_
        # textured_grass(0, 0, space_START_X, 0, space_START_X, WINDOW_HEIGHT, 0, WINDOW_HEIGHT, self.grass_texture)

        # Draw right bank (grass)
      
        # draw_grass(space_END_X, 0, WINDOW_WIDTH, 0, WINDOW_WIDTH, WINDOW_HEIGHT, space_END_X, WINDOW_HEIGHT)
        draw_at(self.space_bank, 1060, -100, -0.8, 1.2)
        # textured_grass(space_END_X, 0, WINDOW_WIDTH, 0, WINDOW_WIDTH, WINDOW_HEIGHT, space_END_X, WINDOW_HEIGHT, self.grass_texture)

        # Draw space (blue water)
        glColor3f(0.3, 0.2, 0.3)
        # glBegin(GL_QUADS)
        # glVertex2f(space_START_X, 0)
        # glVertex2f(space_END_X, 0)
        # glVertex2f(space_END_X, WINDOW_HEIGHT)
        # glVertex2f(space_START_X, WINDOW_HEIGHT)
        # glEnd()
        # draw_space(space_START_X, 0, space_END_X, 0, space_END_X, WINDOW_HEIGHT, space_START_X, WINDOW_HEIGHT)
        # draw_animated_space(space_START_X, 0, space_END_X, 0, space_END_X, WINDOW_HEIGHT, space_START_X, WINDOW_HEIGHT, self.space_textures)

        # 2) Draw the shapes from test.py
        # for shape in self.shapes:
        #     draw_ST(shape, 0, 100)
        # draw_at(self.shapes, 0, 100)
        
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
    
    def game_loop(self):
        impl=self.impl
        # pygame.init()
        # pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), DOUBLEBUF | OPENGL)
        # pygame.display.set_caption("space Crossing – PyOpenGL/Pygame (JS Logic)")
        clock = pygame.time.Clock()
        # self.init_opengl()

        running = True
        overlay_displayed = False
        first_time = True
       
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
                    # if event.key == K_ESCAPE:
                    #     running = False
                    # if event.key == K_SPACE:
                    #     if not self.paused:
                    #         self.player.start_jump()
                    if event.key == K_LSHIFT or event.key == K_SPACE:
                        self.player.toggle_hover()
                elif event.type == KEYUP:
                    if event.key == K_LSHIFT or event.key == K_SPACE:
                        self.player.toggle_hover()



            # if not overlay_displayed:
            #     self.update(dt, keys)
            #     if self.is_game_over():
            #         overlay_displayed = True
            #         print("Game Over!")
            #     elif self.is_win():
            #         if not self.next_level():
            #             print("Congratulations! You completed all levels!")
            #             running = False
            #         else:
            #             print("Level Complete! Next level loaded.")
            imgui.new_frame()
            # Handle pause menu
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
            if not self.paused and not overlay_displayed:
                self.update(dt, keys)
                if self.is_game_over():
                    # overlay_displayed = True
                    print("Game Over!")
                    self.paused = True
                    # return
                elif self.is_win():
                    if not self.next_level():
                        print("Congratulations! You completed all levels!")
                        self.paused = True

                        # running = False
                    else:
                        print("Level Complete! Next level loaded.")

            self.draw_gui()

               # Render
            
            glClear(GL_COLOR_BUFFER_BIT)
            
            self.draw()
                
            imgui.render()
            impl.render(imgui.get_draw_data())
            pygame.display.flip()

    

