import math
import numpy as np
from pyrr import Vector3, matrix44
import platform
import subprocess
import pyglet
from pyglet.gl import *
from .RobotDisplay import RobotDisplay

ZOOM_IN_FACTOR = 1.2
ZOOM_OUT_FACTOR = 1/ZOOM_IN_FACTOR


def screen_scale():
    """Return 1 on normal screens, and 2 on mac for retina displays """
    # Not sure how to deal with a Mac that has a non-retina additional screen
    if platform.system() != 'Darwin':
        # This is not a Mac
        return 1
    output = subprocess.check_output('/usr/sbin/system_profiler SPDisplaysDataType', shell=True)
    output = output.decode('utf-8')
    for line in output.splitlines():
        if 'Retina' in line:
            return 2
    return 1


class InteractiveWindow(pyglet.window.Window):
    """The parent class of interactive windows"""

    def __init__(self, width=350, height=350, *args, **kwargs):
        conf = Config(sample_buffers=1, samples=4, depth_size=0, double_buffer=True)
        super().__init__(width, height, resizable=True, config=conf, *args, **kwargs)
        self.set_minimum_size(150, 150)
        self.zoom_level = 1.0
        self.left = -width / 2
        self.right = width / 2
        self.bottom = -height / 2
        self.top = height / 2
        self.drag_x = 0
        self.drag_y = 0

        # Initialize OpenGL parameters
        # https://www.w3schools.com/cssref/css_colors.asp
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_POLYGON_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        # Set alpha blending
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(1.0, 1.0, 1.0, 1.0)
        self.zoom_level = 6

        # The batch that displays the content of the window
        self.polar_batch = pyglet.graphics.Batch()
        self.background = pyglet.graphics.OrderedGroup(0)
        self.forefront = pyglet.graphics.OrderedGroup(5)
        self.screen_scale = screen_scale()

        # The batch that displays the robot
        self.robot_batch = pyglet.graphics.Batch()
        self.robot = RobotDisplay(self.robot_batch, self.background)
        self.robot_translate = np.array([0, 0, 0], dtype=float)
        self.robot_rotate = 0

        # The batch to animate the egocentric experiences
        self.egocentric_batch = pyglet.graphics.Batch()
        self.egocentric_rotate = 0
        self.egocentric_translate = np.array([0., 0., 0.])

        # The batch that displays the labels at the bottom of the view
        self.label_batch = pyglet.graphics.Batch()
        self.label1 = pyglet.text.Label('', font_name='Verdana', font_size=10, x=10, y=50)
        self.label1.color = (0, 0, 0, 255)
        self.label1.batch = self.label_batch
        self.label2 = pyglet.text.Label('', font_name='Verdana', font_size=10, x=10, y=30)
        self.label2.color = (0, 0, 0, 255)
        self.label2.batch = self.label_batch
        self.label3 = pyglet.text.Label('', font_name='Verdana', font_size=10, x=10, y=10)
        self.label3.color = (0, 0, 0, 255)
        self.label3.batch = self.label_batch

    def on_draw(self):
        """ Drawing the view """
        # The transformations are stacked, and applied backward to the vertices
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()

        # Stack the projection matrix. Fit the window corners.
        glOrtho(self.left, self.right, self.bottom, self.top, 1, -1)

        # Draw the polar layer
        self.polar_batch.draw()

        # Draw the robot
        glTranslatef(*self.robot_translate)
        glRotatef(self.robot_rotate, 0.0, 0.0, 1.0)
        self.robot_batch.draw()

        # Draw the egocentric layer
        glTranslatef(*self.egocentric_translate)
        glRotatef(self.egocentric_rotate, 0.0, 0.0, 1.0)
        self.egocentric_batch.draw()

        # Reset the projection to Identity to cancel the projection of the text
        glLoadIdentity()
        # Stack the projection of the text
        glOrtho(0, self.width, 0, self.height, -1, 1)

        # Draw the text in the bottom left corner
        self.label_batch.draw()

    def update_body_display(self, body_memory):
        """Updates the display of robot's head direction and emotion color"""
        self.robot.rotate_head(body_memory.head_direction_degree())
        self.robot.emotion_color(body_memory.emotion_code())

    def mouse_coordinates_to_point(self, x, y):
        """ Return the point in world reference frame from mouse x and y """
        point_x = (x - self.drag_x - self.width / 2) * self.zoom_level
        point_y = (y - self.drag_y - self.height / 2) * self.zoom_level
        return Vector3([point_x, point_y, 0], dtype=int)

    def window_to_ego_centric(self, x, y):
        """ Return the egocentric from mouse x and y """
        ego_point = self.mouse_coordinates_to_point(x, y) - self.robot_translate
        rotation_matrix = matrix44.create_from_z_rotation(math.radians(self.robot_rotate))
        return matrix44.apply_to_vector(rotation_matrix, ego_point).astype(int)

    # def mouse_to_ego_point(self, x, y, button, modifiers):
    #     """ Computing the position of the mouse click relative to the robot in mm and degrees """
    #     ego_point = self.mouse_coordinates_to_point(x, y)
    #     rotation_matrix = matrix44.create_from_z_rotation(math.radians(self.robot_rotate))
    #     ego_point = matrix44.apply_to_vector(rotation_matrix, ego_point).astype(int)
    #     ego_angle = math.degrees(math.atan2(ego_point[1], ego_point[0]))
    #     # Display the mouse click coordinates at the bottom of the view
    #     self.label3.text = f"Click: ({ego_point[0]:.0f}, {ego_point[1]:.0f}), angle: {ego_angle:.0f}°"
    #     # Return the click position to the controller
    #     return ego_point

    def on_resize(self, width, height):
        """ Adjusting the viewport when resizing the window """
        self.compute_corners()
        # The viewport has the dimension of the whole window for PC and twice the whole window for Mac retina display
        glViewport(0, 0, width * self.screen_scale, height * self.screen_scale)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        """Drag the world within the window"""
        # The total amount of drag
        self.drag_x += dx
        self.drag_y += dy
        self.compute_corners()

    def compute_corners(self):
        """Recompute the corners of the world window"""
        self.left = (-self.width / 2 - self.drag_x) * self.zoom_level
        self.right = (self.width / 2 - self.drag_x) * self.zoom_level
        self.bottom = (-self.height / 2 - self.drag_y) * self.zoom_level
        self.top = (self.height / 2 - self.drag_y) * self.zoom_level

    def on_mouse_scroll(self, x, y, dx, dy):
        """ Zoom the window from the center of the world"""
        self.zoom(dy)

    def save(self):
        """Save the view to file"""
        self.switch_to()  # Activates the OpenGL context of this window
        image = pyglet.image.get_buffer_manager().get_color_buffer().get_image_data()
        image.save(f"log/{self.caption}.png")

    def zoom(self, dy):
        """Zoom the view by the y scroll"""
        f = ZOOM_OUT_FACTOR if dy > 0 else ZOOM_IN_FACTOR if dy < 0 else 1
        if .6 < self.zoom_level * f < 8:
            self.zoom_level *= f
            self.left *= f
            self.right *= f
            self.bottom *= f
            self.top *= f
