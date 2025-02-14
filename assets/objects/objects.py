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
    def __init__(self, gridRow, gridCol, leftBound, rightBound, speed,coins=1,shape=load_shapes("assets\shapes\wood.json") or None,shape_x=-116,shape_y=-73,shape_size=0.3,coin_shape=load_shapes("assets\shapes\coin.json") or None):
        self.row = gridRow
        self.col = gridCol
        self.radius = 26
        self.leftBound=leftBound
        self.rightBound=rightBound
        self.speed = speed
        # Compute initial x position from grid
        self.x = RIVER_START_X + (gridCol - 0.5) * CELL_WIDTH
        self.y = ROW_Y[gridRow - 1]
        # Compute actual horizontal bounds
        self.leftBoundX = RIVER_START_X + (leftBound - 0.5) * CELL_WIDTH
        self.rightBoundX = RIVER_START_X + (rightBound - 0.5) * CELL_WIDTH
        # Random initial direction
        self.vx = self.speed if random.random() < 0.5 else -self.speed
        self.coins = coins

        self.shape=shape
        self.shape_x=shape_x
        self.shape_y=shape_y
        self.shape_size=shape_size
        self.coin_shape=coin_shape





    

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
        # glColor3f(0.8, 0.6, 0.2)
        # draw_filled_circle(self.x, self.y, self.radius)
        if(self.shape!=None):
            draw_at(self.shape, self.x+self.shape_x, self.y+self.shape_y,self.shape_size)
        else:
            glColor3f(0.8, 0.6, 0.2)
            draw_filled_circle(self.x, self.y, self.radius)
        
        if(self.coins>0 and self.shape!=None):
            draw_at(self.coin_shape, self.x-110,self.y-75,0.25)






class Crocodile:
    """
    Moves up and down, jumps over platforms, and has a shadow effect.
    """
    def __init__(self, x=WINDOW_WIDTH/2, y=0, speed=100.0,
                 jumpDuration=1, jumpHeight=20.0, radius=20,shape=load_shapes("assets\objects\crocodile_shape.json"),
                 jump_detection_range=70, animDuration=0.25,
                 inSpace=False,
                 inSquid=False,
                 ):  # Lookahead distance for jumps
        self.x = x
        self.y = y
        self.speed = speed
        self.vx = 0
        self.vy = speed
        self.radius = radius
        self.shape = shape

        # space shapes
        self.ufo1 = load_shapes("assets/shapes/ufo1.json")
        self.ufo2 = load_shapes("assets/shapes/ufo2.json")



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
        self.lightbulb=False
        self.bulbanimTime=0.0
        self.bulbanimDuration=0.4;
    
        # space 
        self.inSpace=inSpace
        # squid 
        self.inSquid=inSquid
        if(self.inSquid):
            self.shape=load_shapes("assets/shapes/bird.json")
    
        
    def hover_offset(self):
        """Returns a sine wave offset in Y for the hover effect."""
        # print(self.inSpace)
        if(self.inSpace):
            # return self.hover_height*math.sin(self.hover_time*10)*(1/10)+self.hover_offset
            return 20*math.sin(self.animTime*3)
        else:
            return 0.0
        

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
        self.bulbanimTime += dt
        if(not self.inSpace):
            if self.animTime >= self.animDuration:
                self.flipx= not self.flipx
                self.animTime = 0.0
        else:
            if self.bulbanimTime >= self.bulbanimDuration:
                self.lightbulb= not self.lightbulb
                self.bulbanimTime = 0.0




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
        spaceOffset = self.hover_offset()
        croc_y = self.y - jumpOffset  # Apply jump effect

        # ---------------------------
        # Draw shadow (slightly below crocodile)
        # ---------------------------
        # glColor4f(0, 0, 0, 0.3)  # Black with transparency
        if(self.inSpace==True):
            # draw_shadow_at(self.ufo1, self.x-130-spaceOffset, self.y-100,0.4)
            # draw_at(self.ufo1, self.x-130-spaceOffset, self.y-jumpOffset-100,0.4)
            if(self.lightbulb==False):
                draw_shadow_at(self.ufo1, self.x-130-spaceOffset, self.y-100,0.4)
                draw_at(self.ufo1, self.x-130-spaceOffset, self.y-jumpOffset-100,0.4)
                # print("ufo1")
            else:
                draw_shadow_at(self.ufo2, self.x-130-spaceOffset, self.y-100,0.4,0.4)
                draw_at(self.ufo2, self.x-130-spaceOffset, self.y-jumpOffset-100,0.4,0.4)
                # print("ufo2")
            return 

        if(self.inSquid==True):
            if(self.flipy==True):
              
                draw_shadow_at(self.shape, self.x-130-spaceOffset, self.y-100,0.3,color=(0.0, 0.0, 0.0, 0.1))
                draw_at(self.shape, self.x-130-spaceOffset, self.y-jumpOffset-90,0.3)
                
            

            else:
            
                draw_shadow_at(self.shape, self.x-130-spaceOffset, self.y+110,0.3,-0.3,color=(0.0, 0.0, 0.0, 0.1))
                draw_at(self.shape, self.x-130-spaceOffset, self.y-jumpOffset+90,0.3,-0.3)
            
                
            return
            
    
        if(self.flipy==True):
            if(self.flipx==False):
                print("ufo1")
                draw_shadow_at(self.shape, self.x-130-spaceOffset, self.y-100,0.4)
                draw_at(self.shape, self.x-130-spaceOffset, self.y-jumpOffset-100,0.4)
            else:
                print("ufo2")
                draw_shadow_at(self.shape, self.x+145-spaceOffset, self.y-100,-0.4,0.4)
                draw_at(self.shape, self.x+145-spaceOffset, self.y-jumpOffset-100,-0.4,0.4)

        else:
            if(self.flipx==False):
                draw_shadow_at(self.shape, self.x-130-spaceOffset, self.y+100,0.4,-0.4)
                draw_at(self.shape, self.x-130-spaceOffset, self.y-jumpOffset+100,0.4,-0.4)
            
            else:
                draw_shadow_at(self.shape, self.x+145-spaceOffset, self.y+100,-0.4,-0.4)
                draw_at(self.shape, self.x+145-spaceOffset, self.y-jumpOffset+100,-0.4,-0.4)

        # draw_filled_circle(self.x, self.y, self.radius)  # Slightly bigger shadow

        # ---------------------------
        # Draw crocodile (light green)
        # ---------------------------
        # glColor3f(0.0, 1.0, 0.0)
        # draw_filled_circle(self.x, croc_y, self.radius)
        # glColor3f(0.0, 1.0, 0.0)
        # draw at
        
class Doll:
    # on the right bank of the river
    def __init__(self, x=WINDOW_WIDTH-RIGHT_BANK_WIDTH/2, y=WINDOW_HEIGHT/2, speed=100,time_to_turn=2,radius=20,shapes=[load_shapes("assets\shapes\doll_green.json"),load_shapes("assets\shapes\doll_red.json")]):
        self.x = x
        self.y = y
     
        self.time_to_turn = time_to_turn
        self.facing_left = False
        self.current_time = 0.0

        self.cooldown = 1.0

        self.is_shooting = False
        self.shoot_duration = 0.3
        self.shoot_time = 0.0
        self.shooting_animation = False
        self.shapes=shapes
        self.shape = self.shapes[0]
    
    def update(self, delta_time):
        self.current_time += delta_time
        if self.current_time >= self.time_to_turn:
            self.facing_left = not self.facing_left
            self.current_time = 0.0
        
        if(self.shooting_animation):
            # straight line from the doll to the player
            

            self.shoot_time += delta_time
            if self.shoot_time >= self.shoot_duration:
                self.shooting_animation = False
                self.shoot_time = 0.0
                self.is_shooting = False
 


       
    def is_looking(self):
        return self.facing_left
    def shoot_player(self,player,damage):
        if(self.is_shooting==False):

            self.is_shooting = True
            self.shoot_time = 0.0
            # just the straight line from the doll to the player
            player.damage(damage)
            self.shooting_animation = True


        pass





    
    def draw(self,player):
        # if looking then red else green
        if self.is_looking():
              # draw the shape
            draw_at(self.shapes[1],self.x+60,self.y-70,-0.3,0.3)
            
            glColor3f(1.0, 0.0, 0.0)
            draw_filled_circle(self.x, self.y, 20)
            glColor3f(1.0, 1.0, 1.0)
            draw_filled_circle(self.x, self.y, 10)
          
        else:
            # draw the shape
            draw_at(self.shapes[0],self.x-170,self.y-70,0.3,0.3)
            # draw_at(self.shapes[0],self.x+60,self.y-70,-0.3,0.3)
            glColor3f(0.0, 0, 1.0)
            draw_filled_circle(self.x, self.y, 20)
            glColor3f(1.0, 1.0, 1.0)
            draw_filled_circle(self.x, self.y, 10)
            


        # draw a line from the doll to the player
        if(self.is_shooting):
            glColor3f(1.0, 0.0, 0.0)
            glLineWidth(5)
            glBegin(GL_LINES)
            glVertex2f(self.x, self.y)
            glVertex2f(player.x, player.y)
            glEnd()
            glLineWidth(1)

        # draw the shooting animation










# -------------------------------------------------
# Player Class
# -------------------------------------------------
class Player:
    def __init__(self, x=LEFT_BANK_WIDTH/2
                 , y=WINDOW_HEIGHT/2,radious=12
                 ,speed=200.0,shape=load_shapes("assets\objects\player_shape.json"),
                 jumpDuration=0.5, jumpHeight=40.0, angularSpeed=2.0,health=100,lives=3,
                 hover_fuel=100,hover_height=100,inspace=False
                 ):
        self.default_x=x
        self.default_y=y
        self.default_speed=speed
        self.player_shape = shape

        # space shapes

        self.space_man=load_shapes("assets/shapes/space_man.json")
        self.space_man_rocket=load_shapes("assets/shapes/space_man_rocket.json")
        if(inspace):
            self.player_shape=self.space_man



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
      
        self.health = health
        self.lives = lives
        self.isDead = False
        self.damage_effect_time=0.0
        self.damage_effect_duration=1.5
        self.damage_effect_active=False

        # velocity
        self.vx=0.0
        self.vy=0.0


        # coins
        self.coins = 0

        # hover
        self.hover_active=False
        self.hover_time=0.0
        
        self.defaul_hover_fuel=hover_fuel
        self.hover_fuel=hover_fuel
        self.hover_height=50
        self.fuel_depletion_rate=10
        self.fuel_regen_rate=10

        self.hover_time_duration=self.hover_fuel/self.fuel_depletion_rate

        # hover initial offset
        self.hover_offset=10
    
    
    def toggle_hover(self):
        self.player_shape=self.space_man_rocket if self.player_shape==self.space_man else self.space_man
        if(not self.hover_active):
            if(self.hover_fuel>0):
                self.hover_active=True
                self.hover_time=0.0
        else:
            self.hover_active=False
            self.hover_time=0.0
          
            
    def hover_update(self,dt):
        if(self.hover_active):
            self.hover_time+=dt
            self.hover_fuel-=self.fuel_depletion_rate*dt
            if(self.hover_fuel<=0):
                self.hover_active=False
                self.hover_time=0.0
                self.hover_fuel=0
        # regain fuel
        else:
            self.hover_fuel+=self.fuel_regen_rate*dt
            if(self.hover_fuel>self.defaul_hover_fuel):
                self.hover_fuel=self.defaul_hover_fuel
    
    def get_hover_offset(self):
        if(self.hover_active):
            return self.hover_height*math.sin(self.hover_time*10)*(1/10)+self.hover_offset
        else:
            return 0
        

            

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
            self.respawn()
            return True
        
        return False

    def respawn(self):
        self.x = self.default_x
        self.y = self.default_y
        self.speed = self.default_speed



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

                # take coin from platform if there
                if p.coins > 0:
                    self.coins += p.coins
                    p.coins = 0
                    print('COINS COLLECTED')
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

        if self.attachedPlatform and not self.isJumping and not self.hover_active:
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

        if self.isJumping :
            self.jumpTime += dt
            if self.jumpTime >= self.jumpDuration:
                self.isJumping = False
                self.try_attach(platforms)
        else:
            self.try_attach(platforms)
        
        self.hover_update(dt)

        if not self.hover_active:
            self.try_attach(platforms)

        

        # damage
        if(self.damage_effect_active):
            self.damage_effect_time += dt
            if(self.damage_effect_time >=self.damage_effect_duration):
                self.damage_effect_active=False
                self.damage_effect_time=0.0
    
    def space_update(self, dt, keys, platforms):
        acceleration = 800  # How fast the object accelerates
        friction = 0.85  # How much it slows down when no keys are pressed
        max_speed = 400  # Maximum movement speed

        # Apply acceleration based on key inputs
        if keys[K_LEFT] or keys[K_a]:
            self.vx -= acceleration * dt
        if keys[K_RIGHT] or keys[K_d]:
            self.vx += acceleration * dt
        if keys[K_UP] or keys[K_w]:
            self.vy -= acceleration * dt
        if keys[K_DOWN] or keys[K_s]:
            self.vy += acceleration * dt

        # Apply friction when no input is given
        self.vx *= friction
        self.vy *= friction

        # Limit speed
        self.vx = max(-max_speed, min(max_speed, self.vx))
        self.vy = max(-max_speed, min(max_speed, self.vy))

        # Move the object
        if self.attachedPlatform and not self.isJumping and not self.hover_active:
            self.x += self.attachedPlatform.vx * dt

        self.x += self.vx * dt
        self.y += self.vy * dt

        # Keep within screen bounds
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx = 0  # Stop movement at the edge
        if self.x + self.radius > WINDOW_WIDTH:
            self.x = WINDOW_WIDTH - self.radius
            self.vx = 0
        if self.y - self.radius < 0:
            self.y = self.radius
            self.vy = 0
        if self.y + self.radius > WINDOW_HEIGHT:
            self.y = WINDOW_HEIGHT - self.radius
            self.vy = 0

        # Rotation update
        self.angle += self.angularSpeed * dt
        if self.angle > 2 * math.pi:
            self.angle -= 2 * math.pi

        # Jump handling
        if self.isJumping:
            self.jumpTime += dt
            if self.jumpTime >= self.jumpDuration:
                self.isJumping = False
                self.try_attach(platforms)
        else:
            self.try_attach(platforms)

        self.hover_update(dt)

        if not self.hover_active:
            self.try_attach(platforms)

        # Damage effect timing
        if self.damage_effect_active:
            self.damage_effect_time += dt
            if self.damage_effect_time >= self.damage_effect_duration:
                self.damage_effect_active = False
                self.damage_effect_time = 0.0




    def draw(self):
        jumpOffset = self.get_jump_offset()
        hoverOffset = self.get_hover_offset() 

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

        draw_at(self.player_shape, self.x-40, self.y-jumpOffset-hoverOffset-35,0.15)

