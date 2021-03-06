import pyglet
from pyglet.gl import *
from ..Display.OsoyooCar import OsoyooCar
import json
import math
import threading
import time

# Zooming constants
ZOOM_IN_FACTOR = 1.2
ZOOM_OUT_FACTOR = 1 / ZOOM_IN_FACTOR


class EgoMemoryWindow(pyglet.window.Window):
    #  to draw a main window
    # set_caption: Set the window's caption, param: string(str)
    # set_minimum_size: resize window
    def __init__(self, *args, **kwargs):
        super().__init__(400, 400, resizable=True, *args, **kwargs)
        self.set_caption("Egocentric Memory")
        self.set_minimum_size(150, 150)
        glClearColor(1.0, 1.0, 1.0, 1.0)

        self.batch = pyglet.graphics.Batch()  # create a batch
        self.zoom_level = 1

        # draw the robot for display in the window using the batch parameter and used OsoyooCar's file
        self.robot = OsoyooCar(self.batch)
        self.azimuth = 0

    def on_draw(self):

        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()

        # The transformations are stacked, and applied backward to the vertices
        # Stack the projection matrix. Centered on (0,0). Fit the window size and zoom factor
        glOrtho(-self.width * self.zoom_level, self.width * self.zoom_level, -self.height * self.zoom_level,
                self.height * self.zoom_level, 1, -1)

        # Stack the rotation of the world so the robot's front is up
        glRotatef(90 - self.azimuth, 0.0, 0.0, 1.0)
        # Draw the robot and the phenomena
        self.batch.draw()

    def on_mouse_press(self,x, y, button, modifiers):
        # pass the event to any widgets within range of the mouse
        # the on mouse press event for mouse management
        # get the size of the window
        w, h = self.get_size()

        # mathematical formula to calculate the angle between a mouse click and the center of the window
        deltaX = x - (w/2)
        deltaY = y - (h/2)
        angleInDegrees = math.atan2(deltaY, deltaX) * 180 / math.pi
        print(int(angleInDegrees))

    def on_resize(self, width, height):
        # Display in the whole window
        glViewport(0, 0, width, height)

    def on_mouse_scroll(self, x, y, dx, dy):
        # Inspired from https://www.py4u.net/discuss/148957
        # Get scale factor
        f = ZOOM_IN_FACTOR if dy > 0 else ZOOM_OUT_FACTOR if dy < 0 else 1
        if .4 < self.zoom_level * f < 5:
            self.zoom_level *= f

    def actionLoop(self, frequence):
        """ Loop in the background to regularly ask the robot for information """
        # This function is not used in the final version
        def loop(obj: EgoMemoryWindow):
            while True:
                time.sleep(frequence)
                # print("Data requests")
                obj.outcome = obj.wifiInterface.enact({"action": "$"})
                # obj.windowRefresh('$', json.loads(outcome))

        thread = threading.Thread(target=loop, args=[self])
        thread.start()

    def actionLoopInterprete(self, dt):
        """ Loop executed by pyglet to use the actionLoop functions"""
        # This function is not used in the final version
        if self.outcome != "{}":
            # print(self.outcome)
            self.windowRefresh('$', json.loads(self.outcome))
            self.outcome = "{}"


# Testing the delete phenomena functionality
# The EgoMemoryWindow must be redrawn for the change to take effect
# python -m Python.OsoyooControllerBSN.Display.EgoMemoryWindow
if __name__ == "__main__":
    em_window = EgoMemoryWindow()

    # em_window.actionLoop(10)
    # clock.schedule_interval(em_window.actionLoopInterprete, 5)
    pyglet.app.run()