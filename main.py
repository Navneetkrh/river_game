import sys
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import imgui
from imgui.integrations.pygame import PygameRenderer
from river_biome.game import RiverCrossingGame
from space_biome.game import SpaceCrossingGame
from squid_biome.game import SquidCrossingGame
from asset_maker.maker import load_shapes, draw_stroke, draw_at
from gui_utils import GuiUtils

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

mixer=pygame.mixer
mixer.init()
mixer.music.load("assets/sounds/bg.mp3")
mixer.music.play(-1)
mixer.music.set_volume(1)

# Colors for light theme
COLORS = {
    'window_bg': (0.95, 0.95, 0.95, 0.3),    
    'button': (0.8, 0.8, 0.8, 1.0),          
    'button_hover': (0.7, 0.7, 0.7, 1.0),    
    'button_active': (0.6, 0.6, 0.6, 1.0),   
    'text': (0.2, 0.2, 0.2, 1.0),           
    'text_disabled': (0.5, 0.5, 0.5, 1.0)    
}

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), 
                               pygame.DOUBLEBUF | pygame.OPENGL)
pygame.display.set_caption("Biome Selection")

# Load background
try:
    BG = load_shapes("assets/shapes/menu_bg.json")
    print("Background loaded successfully")
except Exception as e:
    print(f"Error loading background: {e}")
    BG = None

def init_opengl():
    """Initialize OpenGL settings"""
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, WINDOW_HEIGHT, 0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glClearColor(0.1, 0.1, 0.1, 1.0)

def init_imgui():
    """Initialize ImGui with proper display size"""
    imgui.create_context()
    impl = PygameRenderer()
    io = imgui.get_io()
    io.display_size = WINDOW_WIDTH, WINDOW_HEIGHT
    
    

    return impl

def draw_background():
    """Draw the background"""
    if BG is not None:
        glPushMatrix()
        glLoadIdentity()
        draw_at(BG, -128, -145,1.27,1.45)
        glPopMatrix()

def render_main_menu(gui: GuiUtils):
    """Render the main menu"""
    selection = None
    
    if gui.begin_centered_window("Main Menu", 340, 370,205,90):
        gui.draw_text_centered("Select Biome")
        gui.add_spacing(10)
        
        if gui.draw_centered_button("River Biome", 260, 50):
            mixer.music.load("assets/sounds/river.mp3")
            mixer.music.play(-1)
            mixer.music.set_volume(1)
            
            selection = "river"
        
        gui.add_spacing(5)
        
        # Disabled buttons
        if gui.draw_centered_button("Space Biome", 260, 50):
            mixer.music.load("assets/sounds/space.mp3")
            mixer.music.play(-1)
            mixer.music.set_volume(1)
            
            selection = "space"
        gui.add_spacing(10)
        if gui.draw_centered_button("Squid Biome ", 260, 50):
            mixer.music.load("assets/sounds/rock.mp3")
            mixer.music.play(-1)
            mixer.music.set_volume(1)
            
            selection = "squid"
        gui.add_spacing(10)
        
        # gui.add_spacing(5)
        
        if gui.draw_centered_button("Quit", 260, 40):
            pygame.quit()
            sys.exit()
        
        imgui.end()
    
    return selection

def render_river_menu(gui: GuiUtils):
    """Render the river biome menu"""
    choice = None
    
    if gui.begin_centered_window("River Menu", 340, 370,205,90):
        gui.draw_text_centered("River Biome")
        gui.add_spacing(20)
        
        if gui.draw_centered_button("Start Game", 260, 50):
            choice = "start"
        
        gui.add_spacing(10)
        
        if gui.draw_centered_button("Back to Main Menu", 260, 50):
            choice = "back"
        
        imgui.end()
    
    return choice

# def hud(gui: GuiUtils):
#     """Render the HUD for the river biome game"""
#     gui.begin_window("HUD", 200, 100, 10, 10)
#     gui.draw_text("Score: ")
#     gui.draw_text("Lives: ")
#     gui.end_window()


def main():
    """Main game loop"""
    clock = pygame.time.Clock()
    
    # Initialize OpenGL first
    init_opengl()
    
    # Initialize ImGui with proper display size
    impl = init_imgui()
    
    # Initialize GUI utils after ImGui
    gui = GuiUtils(WINDOW_WIDTH, WINDOW_HEIGHT, COLORS)
    gui.init_style()
    
    current_menu = "main"
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            impl.process_event(event)
        
        # Clear and draw background
        glClear(GL_COLOR_BUFFER_BIT)
        draw_background()
        
        # Start new frame
        imgui.new_frame()
        
        # Handle menu states
        if current_menu == "main":
            selection = render_main_menu(gui)
            if selection == "river":
                current_menu = "river"
            elif selection == "space":
                current_menu = "space"

            elif selection == "squid":
                current_menu = "squid"

                
        elif current_menu == "river":
            # choice = render_river_menu(gui)
            # if choice == "start":
            try:
                imgui.render()
                impl.render(imgui.get_draw_data())
                game = RiverCrossingGame(gui,impl)
                game.paused=True
                status=game.game_loop()
                if(status==True):
                    current_menu = "main"
            except Exception as e:
                print(f"Error starting game: {e}")
                # finally:
                #     pygame.quit()
                #     sys.exit()
            # elif choice == "back":
            #     current_menu = "main"
        elif current_menu == "space":
            # choice = render_space_menu(gui)
            # if choice == "start":
            try:
                imgui.render()
                impl.render(imgui.get_draw_data())
                game = SpaceCrossingGame(gui,impl)
                game.paused=True
                status=game.game_loop()
                if(status==True):
                    current_menu = "main"
            except Exception as e:
                print(f"Error starting game: {e}")
        elif current_menu == "squid":
            # choice = render_squid_menu(gui)
            # if choice == "start":
            try:
                imgui.render()
                impl.render(imgui.get_draw_data())

                game = SquidCrossingGame(gui,impl)
                game.paused=True
                
                status=game.game_loop()
                if(status==True):
                    current_menu = "main"
            except Exception as e:
                print(f"Error starting game: {e}")

        
        # Render
        imgui.render()
        impl.render(imgui.get_draw_data())
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Fatal error: {e}")
        pygame.quit()
        sys.exit(1)