import glfw
from OpenGL.GL import *
import imgui
from imgui.integrations.glfw import GlfwRenderer

class Window:
    def __init__(self, height, width):

        # Initialize glfw
        glfw.init()
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)
        
        # Create a window using glfw
        self.windowHeight = height
        self.windowWidth = width
        self.window = glfw.create_window(width, height,"Demo", None, None)

        if not self.window:
            glfw.terminate()
            print("Glfw window can't be created")
            exit()

        # Set initial position on the screen and activate it
        glfw.set_window_pos(self.window, 450, 30) 
        glfw.make_context_current(self.window)

        # Enable Depth and blending
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS) 


        # Set the viewport (Specifies which area to map the opengl co-ordinate system to)        
        glViewport(0, 0, self.windowWidth, self.windowHeight)

        # Delta time
        self.prevTime = glfw.get_time()

    def Close(self):
        glfw.terminate()
    
    def IsOpen(self):
        return not glfw.window_should_close(self.window)

    def StartFrame(self, c0, c1, c2, c3):
        currentTime = glfw.get_time()
        deltaTime = currentTime - self.prevTime
        self.prevTime = currentTime
        time = {"currentTime" : currentTime, "deltaTime" : deltaTime}

        glfw.poll_events()
        
        inputs = []
        if glfw.get_key(self.window, glfw.KEY_1) == glfw.PRESS:
            inputs.append("1")
        if glfw.get_key(self.window, glfw.KEY_2) == glfw.PRESS:
            inputs.append("2")
        if glfw.get_key(self.window, glfw.KEY_W) == glfw.PRESS:
            inputs.append("W")
        if glfw.get_key(self.window, glfw.KEY_A) == glfw.PRESS:
            inputs.append("A")
        if glfw.get_key(self.window, glfw.KEY_S) == glfw.PRESS:
            inputs.append("S")
        if glfw.get_key(self.window, glfw.KEY_D) == glfw.PRESS:
            inputs.append("D")
        if glfw.get_key(self.window, glfw.KEY_SPACE) == glfw.PRESS:
            inputs.append("SPACE")

        glClearColor(c0, c1, c2, c3)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        return inputs, time
    
    def EndFrame(self):
        glfw.swap_buffers(self.window) 
    
