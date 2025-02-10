import imgui

class GuiUtils:
    def __init__(self, window_width, window_height, custom_colors=None):
        self.window_width = window_width
        self.window_height = window_height
        
        # Default colors (light theme)
        self.default_colors = {
            'window_bg': (0.95, 0.95, 0.95, 1.0),    # Light gray background
            'button': (0.8, 0.8, 0.8, 1.0),          # Light button color
            'button_hover': (0.7, 0.7, 0.7, 1.0),    # Button hover
            'button_active': (0.6, 0.6, 0.6, 1.0),   # Button when clicked
            'text': (0.0, 0.0, 0.0, 1.0),           # Black text
            'text_disabled': (0.6, 0.6, 0.6, 1.0),  # Gray text for disabled
        }
        
        # Update with any custom colors provided
        self.colors = self.default_colors.copy()
        if custom_colors:
            self.colors.update(custom_colors)

    def init_style(self):
        """Initialize ImGui style with current colors"""
        style = imgui.get_style()
        
        # Window styling
        style.window_padding = (20, 20)
        style.window_rounding = 2.0        # Slightly rounded corners
        style.frame_padding = (10, 5)
        style.frame_rounding = 4.0         # Rounded buttons
        style.item_spacing = (10, 10)
        style.item_inner_spacing = (5, 5)
        style.button_text_align = (0.5, 0.5)
        
        # Colors - using only valid ImGui color constants
        style.colors[imgui.COLOR_WINDOW_BACKGROUND] = self.colors['window_bg']
        style.colors[imgui.COLOR_TEXT] = self.colors['text']
        style.colors[imgui.COLOR_BUTTON] = self.colors['button']
        style.colors[imgui.COLOR_BUTTON_HOVERED] = self.colors['button_hover']
        style.colors[imgui.COLOR_BUTTON_ACTIVE] = self.colors['button_active']

    def draw_text(self, text, x=None, y=None, color=None):
        """Draw text at specific position with optional color"""
        if x is not None and y is not None:
            imgui.set_cursor_pos((x, y))
        
        if color:
            imgui.push_style_color(imgui.COLOR_TEXT, *color)
            
        imgui.text(text)
        
        if color:
            imgui.pop_style_color()

    def draw_text_centered(self, text, y=None, color=None):
        """Draw horizontally centered text at optional y position"""
        window_width = imgui.get_window_width()
        text_width = imgui.calc_text_size(text).x
        x = (window_width - text_width) * 0.5
        
        if y is not None:
            imgui.set_cursor_pos_y(y)
        
        self.draw_text(text, x, None, color)

    def draw_text_aligned(self, text, align="left", x_offset=0, y=None, color=None):
        """Draw text with specified alignment (left, center, right)"""
        window_width = imgui.get_window_width()
        text_width = imgui.calc_text_size(text).x
        
        if align == "center":
            x = (window_width - text_width) * 0.5 + x_offset
        elif align == "right":
            x = window_width - text_width - x_offset
        else:  # left
            x = x_offset
            
        if y is not None:
            imgui.set_cursor_pos_y(y)
            
        self.draw_text(text, x, None, color)

    def begin_centered_window(self, name,width, height,x=None,y=None, bg_color=None):
        """Create a centered window with optional background color"""
        if x is None:
            x = (self.window_width - width) / 2
        if y is None:
            y = (self.window_height - height) / 2
        
        imgui.set_next_window_position(x, y)
        imgui.set_next_window_size(width, height)
        
        if bg_color:
            imgui.push_style_color(imgui.COLOR_WINDOW_BACKGROUND, *bg_color)
            
        result = imgui.begin(name, flags=imgui.WINDOW_NO_TITLE_BAR | 
                                       imgui.WINDOW_NO_RESIZE | 
                                       imgui.WINDOW_NO_MOVE)
        
        if bg_color:
            imgui.pop_style_color()
            
        return result

    def draw_menu_button(self, label, width, height, enabled=True, color=None, hover_color=None):
        """Draw a button with optional custom colors"""
        if not enabled:
            imgui.push_style_color(imgui.COLOR_BUTTON, *self.colors['button'])
            imgui.push_style_color(imgui.COLOR_TEXT, *self.colors['text_disabled'])
        elif color:
            imgui.push_style_color(imgui.COLOR_BUTTON, *color)
            if hover_color:
                imgui.push_style_color(imgui.COLOR_BUTTON_HOVERED, *hover_color)
        
        clicked = imgui.button(label, width=width, height=height)
        
        if not enabled:
            imgui.pop_style_color(2)
        elif color:
            if hover_color:
                imgui.pop_style_color(2)
            else:
                imgui.pop_style_color()
            
        return clicked if enabled else False

    def draw_centered_button(self, label, width, height, enabled=True, color=None, hover_color=None):
        """Draw a centered button with optional custom colors"""
        window_width = imgui.get_window_width()
        imgui.set_cursor_pos_x((window_width - width) * 0.5)
        return self.draw_menu_button(label, width, height, enabled, color, hover_color)

    def add_spacing(self, height=10):
        """Add vertical space"""
        imgui.dummy(0, height)