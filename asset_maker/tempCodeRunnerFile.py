import sys
import math
import json
import time
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# -------------------------------------------------
# Window Setup
# -------------------------------------------------
WIDTH, HEIGHT = 800, 600

pygame.init()
pygame.display.set_caption("Freehand Drawing, Shape Fill, and Save/Load")
pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)

# Set up an orthographic projection: (0,0) at bottom-left, (WIDTH, HEIGHT) at top-right.
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
gluOrtho2D(0, WIDTH, 0, HEIGHT)
glMatrixMode(GL_MODELVIEW)
glLoadIdentity()
glClearColor(1.0, 1.0, 1.0, 1.0)  # White background

# -------------------------------------------------
# Global Drawing State
# -------------------------------------------------
current_color = (0.0, 0.0, 0.0)  # Default drawing color: black
drawing = False                  # True while freehand drawing is active
current_stroke = None            # The stroke being drawn
strokes = []                     # List of finished strokes

# Palette buttons (drawn in the top-left area)
# Each tuple: (x, y, width, height, (r, g, b))
palette_buttons = [
    (10, HEIGHT - 40, 30, 30, (0.0, 0.0, 0.0)),  # Black
    (50, HEIGHT - 40, 30, 30, (1.0, 0.0, 0.0)),   # Red
    (90, HEIGHT - 40, 30, 30, (0.0, 1.0, 0.0)),   # Green
    (130, HEIGHT - 40, 30, 30, (0.0, 0.0, 1.0)),  # Blue
    (170, HEIGHT - 40, 30, 30, (1.0, 1.0, 0.0)),  # Yellow
    (210, HEIGHT - 40, 30, 30, (1.0, 0.0, 1.0)),  # Magenta
]

# Threshold (in pixels) to consider a freehand stroke “closed”
CLOSE_THRESHOLD = 10

# -------------------------------------------------
# Helper Functions for Shape Saving/Loading
# -------------------------------------------------
def save_shapes(filename, shapes):
    """
    Saves the shapes (list of dictionaries) to a JSON file.
    Tuples (points and colors) are converted to lists for JSON serialization.
    """
    shapes_serializable = []
    for shape in shapes:
        shape_copy = {}
        for key, value in shape.items():
            if key == "points":
                # Convert each tuple to a list
                shape_copy["points"] = [list(pt) for pt in value]
            elif key in ("line_color", "fill_color"):
                shape_copy[key] = list(value) if value is not None else None
            else:
                shape_copy[key] = value
        shapes_serializable.append(shape_copy)
    with open(filename, "w") as f:
        json.dump(shapes_serializable, f)
    print(f"Saved {len(shapes)} shape(s) to '{filename}'.")


def load_shapes(filename):
    """
    Loads shapes from a JSON file.
    The data is converted back into the proper format (tuples for points and colors).
    """
    with open(filename, "r") as f:
        shapes_data = json.load(f)
    shapes_loaded = []
    for shape in shapes_data:
        shape["points"] = [tuple(pt) for pt in shape["points"]]
        shape["line_color"] = tuple(shape["line_color"])
        if "fill_color" in shape and shape["fill_color"] is not None:
            shape["fill_color"] = tuple(shape["fill_color"])
        shapes_loaded.append(shape)
    print(f"Loaded {len(shapes_loaded)} shape(s) from '{filename}'.")
    return shapes_loaded


def load_and_draw_shapes(filename):
    """
    Convenience function to load shapes from a file and draw them immediately.
    """
    loaded = load_shapes(filename)
    for shape in loaded:
        draw_stroke(shape)
    pygame.display.flip()

# -------------------------------------------------
# Drawing Helper Functions
# -------------------------------------------------
def point_in_poly(x, y, poly):
    """
    Determines if the point (x, y) is inside the polygon defined by a list of (x, y) tuples.
    Uses the ray-casting algorithm.
    """
    inside = False
    n = len(poly)
    if n < 3:
        return False  # Not enough points to form a polygon
    p1x, p1y = poly[0]
    for i in range(1, n + 1):
        p2x, p2y = poly[i % n]
        if (p1y > y) != (p2y > y):
            xinters = (y - p1y) * (p2x - p1x) / ((p2y - p1y) + 1e-12) + p1x
            if x < xinters:
                inside = not inside
        p1x, p1y = p2x, p2y
    return inside


def is_closed(stroke):
    """
    Check if a freehand stroke is “closed” by testing if the first and last points are close.
    """
    pts = stroke["points"]
    if len(pts) < 3:
        return False
    x0, y0 = pts[0]
    x1, y1 = pts[-1]
    return math.hypot(x1 - x0, y1 - y0) <= CLOSE_THRESHOLD


def draw_stroke(stroke):
    """
    Draws a stroke. If the stroke is marked as filled, a filled polygon is drawn first;
    then the stroke outline is drawn on top.
    """
    pts = stroke["points"]
    if len(pts) < 2:
        return

    # Draw the filled polygon if applicable
    if stroke.get("filled", False):
        glColor3f(*stroke["fill_color"])
        glBegin(GL_POLYGON)
        for (x, y) in pts:
            glVertex2f(x, y)
        glEnd()

    # Draw the stroke outline
    glColor3f(*stroke["line_color"])
    glLineWidth(2.0)
    glBegin(GL_LINE_STRIP)
    for (x, y) in pts:
        glVertex2f(x, y)
    glEnd()


def draw_palette():
    """
    Draws the color palette buttons in the top-left corner.
    """
    for (bx, by, bw, bh, color) in palette_buttons:
        # Draw filled rectangle for the palette button
        glColor3f(*color)
        glBegin(GL_QUADS)
        glVertex2f(bx, by)
        glVertex2f(bx + bw, by)
        glVertex2f(bx + bw, by + bh)
        glVertex2f(bx, by + bh)
        glEnd()
        # Draw a black border around the button
        glColor3f(0.0, 0.0, 0.0)
        glLineWidth(1.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(bx, by)
        glVertex2f(bx + bw, by)
        glVertex2f(bx + bw, by + bh)
        glVertex2f(bx, by + bh)
        glEnd()


def render():
    """
    Clears the screen, draws all strokes (finished and in-progress), and draws the palette.
    """
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()

    # Draw finished strokes
    for stroke in strokes:
        draw_stroke(stroke)

    # Draw the current (in-progress) stroke if any
    if current_stroke is not None:
        draw_stroke(current_stroke)

    # Draw the color palette on top
    draw_palette()

    pygame.display.flip()

# -------------------------------------------------
# Main Loop
# -------------------------------------------------
def main():
    global drawing, current_stroke, strokes, current_color
    clock = pygame.time.Clock()

    while True:
        clock.tick(60)  # Limit to 60 FPS

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            # --- Mouse Events ---
            if event.type == MOUSEBUTTONDOWN:
                # Left mouse button: Either select a palette color or begin drawing.
                if event.button == 1:
                    mx, my = event.pos
                    ogl_y = HEIGHT - my  # Convert Pygame coordinates to OpenGL coordinates

                    # Check if the click is on a palette button.
                    palette_clicked = False
                    for (bx, by, bw, bh, color) in palette_buttons:
                        if bx <= mx <= bx + bw and by <= ogl_y <= by + bh:
                            current_color = color
                            palette_clicked = True
                            break

                    # If not clicking a palette, start a freehand stroke.
                    if not palette_clicked:
                        drawing = True
                        current_stroke = {
                            "points": [(mx, ogl_y)],
                            "line_color": current_color,
                            "filled": False,    # Will be set to True if later filled
                            "fill_color": None
                        }

                # Right mouse button: Attempt to fill a closed stroke.
                elif event.button == 3:
                    mx, my = event.pos
                    ogl_y = HEIGHT - my
                    for stroke in strokes:
                        if not stroke.get("filled", False) and is_closed(stroke):
                            if point_in_poly(mx, ogl_y, stroke["points"]):
                                stroke["filled"] = True
                                stroke["fill_color"] = current_color
                                break

            elif event.type == MOUSEMOTION:
                if drawing and current_stroke is not None:
                    mx, my = event.pos
                    ogl_y = HEIGHT - my
                    current_stroke["points"].append((mx, ogl_y))

            elif event.type == MOUSEBUTTONUP:
                if event.button == 1 and drawing:
                    drawing = False
                    if current_stroke is not None:
                        strokes.append(current_stroke)
                        current_stroke = None

            # --- Keyboard Shortcuts ---
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == K_c:
                    strokes.clear()
                elif event.key == K_s:
                    # Save the current shapes to a JSON file.
                    save_shapes("shapes.json", strokes)
                elif event.key == K_l:
                    # Load shapes from the JSON file (this replaces the current strokes).
                    strokes = load_shapes("shapes.json")

        render()


if __name__ == '__main__':
    main()
