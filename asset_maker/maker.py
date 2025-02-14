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
pygame.display.set_caption("Freehand Drawing, Shapes, Fill, Undo/Redo, and Save/Load")
pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)

# Set up an orthographic projection with (0,0) at the TOP-LEFT.
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
gluOrtho2D(0, WIDTH, HEIGHT, 0)  # Top-left is (0,0); y increases downward.
glMatrixMode(GL_MODELVIEW)
glLoadIdentity()
glClearColor(1.0, 1.0, 1.0, 1.0)  # White background

# -------------------------------------------------
# Global Drawing State
# -------------------------------------------------
current_color = (0.0, 0.0, 0.0)  # Default drawing color: black
drawing = False                  # True while dragging the mouse
current_stroke = None            # The stroke being created
strokes = []                     # List of finished strokes
undo_stack = []                  # Stack for undone strokes (for redo)

# Drawing mode: "freehand", "rectangle", "circle", "line", or "polygon"
draw_mode = "freehand"

# Used for rectangle/circle/line: store first click (start_x, start_y)
start_x, start_y = None, None

# Palette buttons (drawn in the top-left area)
palette_buttons = [
    # Black
    (10, 10, 30, 30, (0.0,  0.0,  0.0)),  
    # Red
    (50, 10, 30, 30, (1.0,  0.0,  0.0)), 
    # Green  
    (90, 10, 30, 30, (0.0,  1.0,  0.0)),
    # Blue   
    (130, 10, 30, 30, (0.0,  0.0,  1.0)),  
    # Yellow
    (170, 10, 30, 30, (1.0,  1.0,  0.0)),  
    # Magenta
    (210, 10, 30, 30, (1.0,  0.0,  1.0)), 
    # Wooden brown
    (250, 10, 30, 30, (1,  0.6,  0.2)), 
    # Orange
    (290, 10, 30, 30, (1,  0.5,  0.0)),
    # White
    (330, 10, 30, 30, (1.0,  1.0,  1.0)),
    # Extra colors (example duplicates adjusted for layout)
    (370, 10, 30, 30, (0.0,  0.5,  0.0)),  # Dark green
    (410, 10, 30, 30, (0.0,  0.5,  0.5)),  # Bluish green
]

# Threshold (in pixels) to consider a freehand stroke “closed” or to complete a polygon.
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
                shape_copy["points"] = [list(pt) for pt in value]
            elif key == "fixed_points":
                shape_copy["fixed_points"] = [list(pt) for pt in value]
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
        if "points" in shape:
            shape["points"] = [tuple(pt) for pt in shape["points"]]
        if "fixed_points" in shape:
            shape["fixed_points"] = [tuple(pt) for pt in shape["fixed_points"]]
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
# Shape/Point Utility Functions
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
    For non-freehand shapes (including finalized polygons), we assume they are closed.
    """
    if stroke["type"] != "freehand":
        return True

    pts = stroke["points"]
    if len(pts) < 3:
        return False
    x0, y0 = pts[0]
    x1, y1 = pts[-1]
    return math.hypot(x1 - x0, y1 - y0) <= CLOSE_THRESHOLD

def generate_rectangle_points(x1, y1, x2, y2):
    """
    Returns the four corners of the rectangle (x1,y1) to (x2,y2).
    The points form a closed polygon in counter-clockwise order.
    """
    return [
        (x1, y1),
        (x2, y1),
        (x2, y2),
        (x1, y2)
    ]

def generate_circle_points(cx, cy, radius, segments=36):
    """
    Returns a list of points approximating a circle centered at (cx, cy) with given radius.
    """
    pts = []
    for i in range(segments):
        theta = 2.0 * math.pi * (i / segments)
        x = cx + radius * math.cos(theta)
        y = cy + radius * math.sin(theta)
        pts.append((x, y))
    return pts

def generate_line_points(x1, y1, x2, y2):
    return [(x1, y1), (x2, y2)]

# -------------------------------------------------
# Drawing Functions
# -------------------------------------------------
def draw_stroke(stroke):
    """
    Draws a shape/stroke. If stroke is marked as filled, a filled polygon is drawn first;
    then the stroke outline is drawn on top.
    """
    if stroke["type"] == "polygon":
        # For polygon mode, only fill if the polygon is finalized.
        if stroke.get("finalized", False):
            pts = stroke["points"]
            if stroke.get("filled", False) and stroke.get("fill_color"):
                glColor3f(*stroke["fill_color"])
                glBegin(GL_POLYGON)
                for (x, y) in pts:
                    glVertex2f(x, y)
                glEnd()
            glColor3f(*stroke["line_color"])
            glLineWidth(2.0)
            glBegin(GL_LINE_LOOP)
            for (x, y) in pts:
                glVertex2f(x, y)
            glEnd()
        else:
            # Incomplete polygon: draw fixed points plus preview point if available.
            pts = stroke.get("fixed_points", [])
            if "preview" in stroke:
                pts = pts + [stroke["preview"]]
            if len(pts) < 2:
                return
            glColor3f(*stroke["line_color"])
            glLineWidth(2.0)
            glBegin(GL_LINE_STRIP)
            for (x, y) in pts:
                glVertex2f(x, y)
            glEnd()
        return

    pts = stroke["points"]
    if len(pts) < 2:
        return

    # Draw filled polygon if applicable
    if stroke.get("filled", False) and stroke.get("fill_color"):
        glColor3f(*stroke["fill_color"])
        glBegin(GL_POLYGON)
        for (x, y) in pts:
            glVertex2f(x, y)
        glEnd()

    # Draw stroke outline
    glColor3f(*stroke["line_color"])
    glLineWidth(2.0)
    glBegin(GL_LINE_LOOP if stroke["type"] != "freehand" else GL_LINE_STRIP)
    for (x, y) in pts:
        glVertex2f(x, y)
    glEnd()

def draw_at(shape=None, x=0, y=0, scalex=1.0, scaley=None):
    """
    Draws a shape (stroke) at the specified position (x, y) with a given scale.
    """
    if scaley is None:
        scaley = scalex

    if shape is None:
        return

    for stroke in shape:
        glPushMatrix()
        glTranslatef(x, y, 0.0)
        glScalef(scalex, scaley, 1.0)
        draw_stroke(stroke)
        glPopMatrix()

def draw_shadow_stroke(stroke, color=(0,0,0,0.3)):
    """
    Draws a shape/stroke as a semi-transparent shadow.
    """
    if not stroke or "points" not in stroke:
        return
    
    pts = stroke["points"]
    if len(pts) < 2:
        return

    glColor4f(*color)
    glBegin(GL_POLYGON if stroke.get("filled", False) else GL_LINE_LOOP)
    for (x, y) in pts:
        glVertex2f(x, y)
    glEnd()

def draw_shadow_at(shape=None, x=0, y=0, scalex=1.0, scaley=None, alpha=0.3, color=(0,0,0,0.3)):
    """
    Draws a shape (list of strokes) at the specified position (x, y) as a transparent black shadow.
    """
    if scaley is None:
        scaley = scalex

    if shape is None:
        return

    for stroke in shape:
        glPushMatrix()
        glTranslatef(x, y, 0.0)
        glScalef(scalex, scaley, 1.0)
        glColor4f(*color)
        draw_shadow_stroke(stroke, color=color)
        glPopMatrix()

def draw_palette():
    """
    Draws the color palette buttons in the top-left corner.
    """
    for (bx, by, bw, bh, color) in palette_buttons:
        glColor3f(*color)
        glBegin(GL_QUADS)
        glVertex2f(bx, by)
        glVertex2f(bx + bw, by)
        glVertex2f(bx + bw, by + bh)
        glVertex2f(bx, by + bh)
        glEnd()
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
    global drawing, current_stroke, strokes, undo_stack
    global current_color, draw_mode
    global start_x, start_y

    clock = pygame.time.Clock()

    while True:
        clock.tick(60)  # Limit to 60 FPS

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            # --- Mouse Events ---
            if event.type == MOUSEBUTTONDOWN:
                # Left mouse button: Possibly start drawing or add a polygon point
                if event.button == 1:
                    mx, my = event.pos

                    # Check palette click first
                    palette_clicked = False
                    for (bx, by, bw, bh, color) in palette_buttons:
                        if bx <= mx <= bx + bw and by <= my <= by + bh:
                            current_color = color
                            palette_clicked = True
                            break

                    if not palette_clicked:
                        if draw_mode == "freehand":
                            drawing = True
                            start_x, start_y = mx, my
                            current_stroke = {
                                "type": "freehand",
                                "points": [(mx, my)],
                                "line_color": current_color,
                                "filled": False,
                                "fill_color": None
                            }
                        elif draw_mode == "rectangle":
                            drawing = True
                            start_x, start_y = mx, my
                            current_stroke = {
                                "type": "rectangle",
                                "points": [],
                                "line_color": current_color,
                                "filled": False,
                                "fill_color": None
                            }
                        elif draw_mode == "circle":
                            drawing = True
                            start_x, start_y = mx, my
                            current_stroke = {
                                "type": "circle",
                                "points": [],
                                "line_color": current_color,
                                "filled": False,
                                "fill_color": None
                            }
                        elif draw_mode == "line":
                            drawing = True
                            start_x, start_y = mx, my
                            current_stroke = {
                                "type": "line",
                                "points": [(mx, my)],
                                "line_color": current_color,
                                "filled": False,
                                "fill_color": None
                            }
                        elif draw_mode == "polygon":
                            # In polygon mode, each left-click adds a point.
                            if current_stroke is None:
                                # Start a new polygon stroke.
                                current_stroke = {
                                    "type": "polygon",
                                    "fixed_points": [(mx, my)],
                                    "line_color": current_color,
                                    "filled": False,
                                    "fill_color": None,
                                    "finalized": False
                                }
                            else:
                                # Remove preview if present.
                                if "preview" in current_stroke:
                                    current_stroke.pop("preview")
                                # If the new point is near the first point and at least 3 points exist, finalize.
                                if (len(current_stroke["fixed_points"]) >= 3 and
                                    math.hypot(mx - current_stroke["fixed_points"][0][0],
                                               my - current_stroke["fixed_points"][0][1]) <= CLOSE_THRESHOLD):
                                    current_stroke["points"] = current_stroke["fixed_points"]
                                    current_stroke["finalized"] = True
                                    strokes.append(current_stroke)
                                    # Clear the redo stack when a new stroke is finalized.
                                    undo_stack.clear()  
                                    current_stroke = None
                                else:
                                    current_stroke["fixed_points"].append((mx, my))

                # Right mouse button: Attempt to fill a shape
                elif event.button == 3:
                    mx, my = event.pos
                    # Iterate in reverse order (topmost first)
                    for stroke in reversed(strokes):
                        # For polygon strokes, only fill if they are finalized.
                        if stroke["type"] == "polygon" and not stroke.get("finalized", False):
                            continue
                        if not stroke.get("filled", False) and is_closed(stroke):
                            # Use the stored "points" (for polygon, these exist only when finalized)
                            pts = stroke.get("points", [])
                            if pts and point_in_poly(mx, my, pts):
                                stroke["filled"] = True
                                stroke["fill_color"] = current_color
                                break

            elif event.type == MOUSEMOTION:
                mx, my = event.pos
                if drawing and current_stroke is not None:
                    if draw_mode == "freehand":
                        current_stroke["points"].append((mx, my))
                    elif draw_mode == "rectangle":
                        rect_pts = generate_rectangle_points(start_x, start_y, mx, my)
                        current_stroke["points"] = rect_pts
                    elif draw_mode == "circle":
                        radius = math.hypot(mx - start_x, my - start_y)
                        circle_pts = generate_circle_points(start_x, start_y, radius)
                        current_stroke["points"] = circle_pts
                    elif draw_mode == "line":
                        current_stroke["points"] = [(start_x, start_y), (mx, my)]
                elif draw_mode == "polygon" and current_stroke is not None:
                    # Update preview point for polygon mode
                    current_stroke["preview"] = (mx, my)

            elif event.type == MOUSEBUTTONUP:
                if event.button == 1 and drawing:
                    # For modes that use dragging (freehand, rectangle, circle, line)
                    if draw_mode in ["freehand", "rectangle", "circle", "line"]:
                        drawing = False
                        if current_stroke is not None and len(current_stroke.get("points", [])) > 1:
                            strokes.append(current_stroke)
                            # Clear the redo stack when a new stroke is finalized.
                            undo_stack.clear()  
                        current_stroke = None
                    # For polygon mode, we do not finalize on mouse button up.

            # --- Keyboard Shortcuts ---
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == K_c:
                    strokes.clear()
                    undo_stack.clear()
                # Save: ask for file path
                elif event.key == K_s:
                    file_path = input("Enter file path to save shapes: ")
                    if file_path:
                        save_shapes(file_path, strokes)
                # Load: ask for file path
                elif event.key == K_x:
                    file_path = input("Enter file path to load shapes: ")
                    if file_path:
                        strokes[:] = load_shapes(file_path)
                        undo_stack.clear()
                elif event.key == K_f:
                    draw_mode = "freehand"
                    print("Mode: Freehand")
                elif event.key == K_r:
                    draw_mode = "rectangle"
                    print("Mode: Rectangle")
                elif event.key == K_o:
                    draw_mode = "circle"
                    print("Mode: Circle")
                elif event.key == K_l:
                    draw_mode = "line"
                    print("Mode: Line")
                elif event.key == K_p:
                    draw_mode = "polygon"
                    print("Mode: Polygon")
                # Undo (press Z)
                elif event.key == K_z:
                    if strokes:
                        stroke_removed = strokes.pop()
                        undo_stack.append(stroke_removed)
                        print("Undo")
                # Redo (press Y)
                elif event.key == K_y:
                    if undo_stack:
                        stroke_restored = undo_stack.pop()
                        strokes.append(stroke_restored)
                        print("Redo")

        render()

if __name__ == '__main__':
    main()
